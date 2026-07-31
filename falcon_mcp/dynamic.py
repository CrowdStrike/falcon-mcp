"""
Dynamic mode for Falcon MCP Server.

Wraps the full tool surface behind 3 tools (falcon_list_enabled_tools +
falcon_search_tools + falcon_execute_tool) to reduce context window consumption
while keeping all functionality accessible on-demand.
"""

from dataclasses import dataclass, field
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from falcon_mcp.common.fql import FQL_FILTER_HINT_SUFFIX
from falcon_mcp.common.logging import get_logger
from falcon_mcp.filter_hints import FILTER_HINTS, QUERY_STRING_HINTS
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS, BaseModule
from falcon_mcp.tool_filter import Resolution, ToolPolicy, ToolRecord

logger = get_logger(__name__)


@dataclass
class ToolEntry:
    """Catalog entry for a single tool."""

    tool: Tool
    module: str
    search_corpus: str = field(init=False)

    def __post_init__(self) -> None:
        param_names = " ".join(self.tool.parameters.get("properties", {}).keys())
        self.search_corpus = (
            f"{self.tool.name} {self.tool.description or ''} {self.module} {param_names}"
        ).lower()


class DynamicToolCatalog:
    """Builds a searchable catalog of tools from modules via a scratch FastMCP instance."""

    def __init__(
        self, modules: dict[str, BaseModule], policy: ToolPolicy | None = None
    ) -> None:
        self._entries: dict[str, ToolEntry] = {}
        self._policy = policy or ToolPolicy()
        self.resolution = Resolution(
            keep=frozenset(), removed=frozenset(), withheld_by_rule=frozenset()
        )
        self._build(modules)

    def _build(self, modules: dict[str, BaseModule]) -> None:
        scratch = FastMCP("scratch")

        for module_name, module in modules.items():
            module.register_tools(scratch)

        all_tools: dict[str, Tool] = scratch._tool_manager._tools

        module_tool_names: dict[str, str] = {}
        for module_name, module in modules.items():
            for tool_name in module.tools:
                module_tool_names[tool_name] = module_name

        self.resolution = self._policy.resolve(
            {
                tool_name: ToolRecord(
                    module=module_tool_names.get(tool_name, "unknown"),
                    annotations=tool_obj.annotations,
                )
                for tool_name, tool_obj in all_tools.items()
            }
        )

        for tool_name, tool_obj in all_tools.items():
            # Omitting a withheld tool here is the whole enforcement: it is then
            # absent from falcon_search_tools and 404s in falcon_execute_tool, so the
            # executor is not a bypass.
            if tool_name in self.resolution.removed:
                # Named here because this path never calls server.remove_tool, so
                # --debug would otherwise report a count with no names behind it.
                logger.debug("Withheld tool: %s", tool_name)
                continue
            module_name = module_tool_names.get(tool_name, "unknown")
            self._entries[tool_name] = ToolEntry(tool=tool_obj, module=module_name)

        for module in modules.values():
            module.tools.clear()

        logger.debug("Dynamic catalog built with %d tools", len(self._entries))

    @property
    def entries(self) -> dict[str, ToolEntry]:
        return self._entries

    def get(self, tool_name: str) -> ToolEntry | None:
        return self._entries.get(tool_name)

    def search(
        self,
        query: str = "",
        module: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        return [self._format_entry(e) for e in self._matches(query, module)[:limit]]

    def count_matches(self, query: str = "", module: str | None = None) -> int:
        """Count every matching entry, ignoring the result limit.

        Shares _matches with search() so the reported total cannot drift from the
        results returned.
        """
        return len(self._matches(query, module))

    def _matches(self, query: str, module: str | None) -> list[ToolEntry]:
        candidates: list[ToolEntry] = list(self._entries.values())

        if module:
            candidates = [e for e in candidates if e.module == module]

        if query:
            tokens = query.lower().split()
            candidates = [
                e for e in candidates if all(t in e.search_corpus for t in tokens)
            ]

        return candidates

    def _format_entry(self, entry: ToolEntry) -> dict[str, Any]:
        params_summary = {}
        properties = entry.tool.parameters.get("properties", {})
        required = entry.tool.parameters.get("required", [])

        for name, schema in properties.items():
            param_info: dict[str, Any] = {
                "type": schema.get("type", "any"),
                "required": name in required,
                "description": schema.get("description", ""),
            }
            examples = schema.get("examples")
            if examples:
                param_info["examples"] = examples
            params_summary[name] = param_info

        hint = FILTER_HINTS.get(entry.tool.name)
        if hint and "filter" in params_summary:
            desc = params_summary["filter"]["description"]
            separator = " " if desc.endswith(".") else ". "
            params_summary["filter"]["description"] = desc + separator + hint

        if "filter" in params_summary:
            desc = params_summary["filter"]["description"]
            separator = " " if desc.endswith(".") else ". "
            params_summary["filter"]["description"] = desc + separator + FQL_FILTER_HINT_SUFFIX

        # CQL tools use a `query_string` param instead of an FQL `filter`; inject the
        # curated CQL hint there so dynamic mode reaches the model the same way.
        cql_hint = QUERY_STRING_HINTS.get(entry.tool.name)
        if cql_hint and "query_string" in params_summary:
            desc = params_summary["query_string"]["description"]
            separator = " " if desc.endswith(".") else ". "
            params_summary["query_string"]["description"] = desc + separator + cql_hint

        annotations = entry.tool.annotations
        return {
            "name": entry.tool.name,
            "module": entry.module,
            "description": entry.tool.description or "",
            "parameters": params_summary,
            "read_only": annotations.readOnlyHint if annotations else True,
            "destructive": annotations.destructiveHint if annotations else False,
        }

    @staticmethod
    def summarize_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
        summary = {}
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        for name, schema in properties.items():
            summary[name] = {
                "type": schema.get("type", "any"),
                "required": name in required,
                "description": schema.get("description", ""),
            }
        return summary


class DynamicMode:
    """Registers the 2 discovery meta-tools (falcon_search_tools + falcon_execute_tool).

    falcon_list_enabled_tools is registered separately by the server, giving dynamic
    mode 3 tools total in the client-visible surface.
    """

    def __init__(
        self,
        modules: dict[str, BaseModule],
        server: FastMCP,
        policy: ToolPolicy | None = None,
    ) -> None:
        self.server = server
        self.catalog = DynamicToolCatalog(modules, policy)

    def register(self) -> None:
        self.server.add_tool(
            self._search_tools,
            name="falcon_search_tools",
            annotations=READ_ONLY_ANNOTATIONS,
            structured_output=False,
        )
        self.server.add_tool(
            self._execute_tool,
            name="falcon_execute_tool",
            annotations=None,
            structured_output=False,
        )

    async def _search_tools(
        self,
        query: str = Field(
            default="",
            description="Keywords to search across tool names, descriptions, module names, and parameter names.",
        ),
        module: str | None = Field(
            default=None,
            description="Filter results to a specific module (e.g., 'hosts', 'detections').",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of results to return (default: 20).",
        ),
    ) -> dict[str, Any]:
        """Look up full parameter schemas for tools matching a keyword.

        Call falcon_list_enabled_tools first when you need the complete inventory of
        what this server serves; use this to get a tool's parameters before calling
        falcon_execute_tool. Returns matching tools with full schemas, plus total and
        truncated so you can tell when results were capped.
        """
        results = self.catalog.search(query=query, module=module, limit=limit)
        total = self.catalog.count_matches(query=query, module=module)
        truncated = total > len(results)

        if not results:
            return {
                "results": [],
                "total": 0,
                "truncated": False,
                "hint": f"No tool matching '{query}' is served by this server. Call "
                "falcon_list_enabled_tools for the full inventory. If the capability "
                "you need is genuinely absent, it was not enabled on this server — "
                "tell the user rather than trying more searches.",
            }

        envelope: dict[str, Any] = {
            "results": results,
            "total": total,
            "truncated": truncated,
        }
        if truncated:
            envelope["hint"] = (
                f"Showing {len(results)} of {total}. Call falcon_list_enabled_tools "
                "for all names, or narrow with query."
            )
        return envelope

    async def _execute_tool(
        self,
        tool_name: str = Field(
            description="Exact tool name to execute (from falcon_search_tools results).",
        ),
        parameters: dict[str, Any] = Field(
            default_factory=dict,
            description="Tool parameters as a JSON object.",
        ),
    ) -> Any:
        """Execute a Falcon tool by name with the given parameters.

        Use falcon_search_tools first to discover tool names, parameter schemas,
        and mutation risk (read_only / destructive fields). Do not execute destructive
        tools without confirming the user's intent.
        Results are returned in full — use each tool's own limit parameter to control
        response volume. Empty result sets return a dict with results, pagination, and
        hint keys rather than a bare empty list.
        """
        entry = self.catalog.get(tool_name)
        if not entry:
            return {
                "error": f"Unknown tool: '{tool_name}'. Use falcon_search_tools to discover valid names."
            }

        try:
            result = await entry.tool.run(parameters)
        except Exception as e:
            error_type = type(e).__name__
            if "validation" in error_type.lower() or "valid" in str(e).lower():
                return {
                    "error": f"Parameter validation failed: {e}",
                    "tool": tool_name,
                    "expected_parameters": self.catalog.summarize_parameters(
                        entry.tool.parameters
                    ),
                }
            return {"error": f"Execution failed: {e}", "tool": tool_name}

        return self._normalize_empty(result)

    def _normalize_empty(self, result: Any) -> Any:
        """Return a helpful hint when a tool produces an empty result set."""
        if isinstance(result, list) and len(result) == 0:
            return {
                "results": [],
                "pagination": {"total": 0, "next": None},
                "hint": "No records returned. Use falcon_search_tools to review the tool parameters if this is unexpected.",
            }
        return result
