"""
Dynamic mode for Falcon MCP Server.

Wraps the full tool surface behind 3 tools (falcon_list_enabled_tools +
falcon_search_tools + falcon_execute_tool) to reduce context window consumption
while keeping all functionality accessible on-demand.
"""

import re
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

_TOOL_PREFIX = "falcon_"
_NON_ALNUM = re.compile(r"[^a-z0-9]+")

# Relative weights only: a name match must outrank any number of description
# matches, so the gap between tiers exceeds the most tokens a query realistically
# carries.
_SCORE_EXACT_NAME = 1000
_SCORE_NAME_WORD = 10
_SCORE_NAME_SUBSTRING = 5
_SCORE_MODULE_WORD = 3
_SCORE_MODULE_SUBSTRING = 2
_SCORE_DESCRIPTION = 1


def _words(text: str) -> frozenset[str]:
    """Split text into lowercase alphanumeric words."""
    return frozenset(w for w in _NON_ALNUM.split(text.lower()) if w)


def normalize_identifier(name: str) -> str:
    """Reduce a name to lowercase alphanumerics, dropping separators.

    Makes 'Host_Groups', 'host-groups', and 'hostgroups' the same key.
    """
    return _NON_ALNUM.sub("", name.lower())


@dataclass
class ToolEntry:
    """Catalog entry for a single tool."""

    tool: Tool
    module: str
    search_corpus: str = field(init=False)
    name_words: frozenset[str] = field(init=False)
    unprefixed_name: str = field(init=False)
    name_key: frozenset[str] = field(init=False)
    module_words: frozenset[str] = field(init=False)
    module_key: str = field(init=False)

    def __post_init__(self) -> None:
        param_names = " ".join(self.tool.parameters.get("properties", {}).keys())
        self.search_corpus = (
            f"{self.tool.name} {self.tool.description or ''} {self.module} {param_names}"
        ).lower()

        name = self.tool.name.lower()
        self.unprefixed_name = name.removeprefix(_TOOL_PREFIX)
        self.name_words = _words(self.unprefixed_name)
        # Both spellings are accepted as an exact hit so a query can name the tool
        # with or without the server's prefix.
        self.name_key = frozenset(
            {normalize_identifier(name), normalize_identifier(self.unprefixed_name)}
        )
        self.module_words = _words(self.module)
        self.module_key = normalize_identifier(self.module)

    def score(self, tokens: list[str], query_key: str) -> int:
        """Rank this entry against a tokenized query; higher sorts earlier.

        Each token scores once, at the strongest field it hits, so a tool named
        for the query outranks one that only mentions it in prose.
        """
        if query_key and query_key in self.name_key:
            return _SCORE_EXACT_NAME

        total = 0
        for token in tokens:
            if token in self.name_words:
                total += _SCORE_NAME_WORD
            elif token in self.unprefixed_name:
                total += _SCORE_NAME_SUBSTRING
            elif token in self.module_words:
                total += _SCORE_MODULE_WORD
            elif token in self.module_key:
                total += _SCORE_MODULE_SUBSTRING
            else:
                total += _SCORE_DESCRIPTION
        return total


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

    def withholding_rule(self, tool_name: str) -> str | None:
        """Name the rule that withholds this tool, or None if no rule did."""
        return self.resolution.reasons.get(tool_name)

    def describe_policy(self) -> str:
        """Summarize every filtering rule the server has enabled."""
        return self._policy.describe()

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

    def relaxed(self, query: str = "", module: str | None = None) -> bool:
        """True when the results came from the any-token fallback."""
        return self._match_set(query, module)[1]

    def _match_set(
        self, query: str, module: str | None
    ) -> tuple[list[ToolEntry], bool]:
        """Select matching entries; the flag reports whether the fallback ran.

        Requiring every token narrows well when the query is already tool-shaped,
        but a phrase carrying one word the catalog does not use matches nothing at
        all. Falling back to any-token keeps such a query answerable; ranking is
        what makes the wider set usable.
        """
        candidates: list[ToolEntry] = list(self._entries.values())

        if module:
            module_key = normalize_identifier(module)
            candidates = [e for e in candidates if e.module_key == module_key]

        if not query:
            return candidates, False

        tokens = query.lower().split()
        strict = [e for e in candidates if all(t in e.search_corpus for t in tokens)]
        if strict:
            return strict, False
        return [e for e in candidates if any(t in e.search_corpus for t in tokens)], True

    def _matches(self, query: str, module: str | None) -> list[ToolEntry]:
        candidates, _ = self._match_set(query, module)

        if not query:
            # Browsing has no relevance signal, so order by name to stay stable
            # across processes.
            return sorted(candidates, key=lambda e: e.tool.name)

        tokens = query.lower().split()
        query_key = normalize_identifier(query)
        # Ties break toward the least-qualified name, then alphabetically: a tool
        # carrying no extra words beyond the query is the more direct answer, and
        # catalog insertion order follows a set of module names, so it is not
        # stable across processes.
        return sorted(
            candidates,
            key=lambda e: (-e.score(tokens, query_key), len(e.name_words), e.tool.name),
        )

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
    """Registers the 2 discovery meta-tools (falcon_search_tools + falcon_execute_tool)."""

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

    def _entries_remain(self) -> bool:
        """True if the catalog still serves at least one capability tool.

        Filtering can withhold every tool (``--tools <mutator> --read-only``), which
        changes what is honest to tell a model about looking elsewhere.
        """
        return bool(self.catalog.entries)

    async def _search_tools(
        self,
        query: str = Field(
            default="",
            description="Keywords to search across tool names, descriptions, module names, and parameter names.",
        ),
        module: str | None = Field(
            default=None,
            description=(
                "Restrict results to one module (e.g., 'hosts', 'detections'). Case "
                "and separators are ignored, so 'Host_Groups' and 'hostgroups' both "
                "work. Call falcon_list_enabled_tools for the exact module names this "
                "server serves. Pass it with no query to browse everything that "
                "module serves."
            ),
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of results to return (default: 20, max: 500).",
        ),
    ) -> dict[str, Any]:
        """Get a Falcon tool's parameters so you can call it with falcon_execute_tool.

        This is the entry point in dynamic mode: search by keyword, or pass a module
        name (or no query at all) to browse. Results are ordered by relevance, best
        fit first, so prefer the top results. Each result carries the tool's name,
        module, description, a summary of every parameter (type, required, description,
        examples, and filter-syntax hints where the tool takes a filter), and
        read_only/destructive flags — check those before executing anything that
        mutates. Read total and truncated to tell a capped list from a complete one,
        and hint for whether the match had to be loosened.
        """
        results = self.catalog.search(query=query, module=module, limit=limit)
        total = self.catalog.count_matches(query=query, module=module)
        truncated = total > len(results)

        if not results:
            # Quoting an empty query back reads as a failed lookup for "".
            subject = f"No tool matching '{query}' is" if query else "No tool is"
            if not self._entries_remain():
                hint = (
                    "This server serves no capability tools: its configuration "
                    f"({self.catalog.describe_policy()}) withholds all of them. Tell the "
                    "user the server is configured with no tools available rather than "
                    "searching again."
                )
            elif self.catalog.resolution.withheld_by_rule:
                hint = (
                    f"{subject} served by this server, which is "
                    f"running with a tool filter ({self.catalog.describe_policy()}). "
                    "Call falcon_list_enabled_tools for what it does serve. The "
                    "capability may exist but be withheld by configuration — tell the "
                    "user that rather than trying more searches."
                )
            else:
                hint = (
                    f"{subject} served by this server. Call "
                    "falcon_list_enabled_tools for the full inventory. If the capability "
                    "you need is genuinely absent, it was not enabled on this server — "
                    "tell the user rather than trying more searches."
                )
            return {
                "results": [],
                "total": 0,
                "truncated": False,
                "hint": hint,
            }

        envelope: dict[str, Any] = {
            "results": results,
            "total": total,
            "truncated": truncated,
        }
        hints: list[str] = []
        if self.catalog.relaxed(query=query, module=module):
            hints.append(
                "No tool matched every word, so these match at least one of them and "
                "are ordered by relevance — the best fit is first. Check the top few "
                "rather than assuming the capability is missing."
            )
        if truncated:
            hints.append(
                f"Showing {len(results)} of {total}. Call falcon_list_enabled_tools "
                "for all names, or narrow with query."
            )
        if hints:
            envelope["hint"] = " ".join(hints)
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
            # A tool the policy withheld is absent from the catalog exactly like one
            # that never existed. Say which it is, or the model reports an operator
            # config choice to the user as a missing product capability.
            rule = self.catalog.withholding_rule(tool_name)
            if rule is not None:
                # Promising other tools on an empty surface sends the model hunting.
                remainder = (
                    "Do not try to achieve the same effect through a different tool, "
                    "though other tools remain available for other work."
                    if self._entries_remain()
                    else "This server currently serves no capability tools at all, so "
                    "do not look for an alternative."
                )
                return {
                    "error": f"'{tool_name}' exists on this server but its configuration "
                    f"withholds it ({rule}). The capability is not missing — tell the user "
                    f"it is disabled by this server's configuration. {remainder}",
                    "tool": tool_name,
                }
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
