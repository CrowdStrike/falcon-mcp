"""
Falcon MCP Server - Main entry point

This module provides the main server class for the Falcon MCP server
and serves as the entry point for the application.
"""

import argparse
import os
import sys
from typing import TYPE_CHECKING, Any, Literal

import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from falcon_mcp import registry
from falcon_mcp.client import FalconClient, get_version
from falcon_mcp.common.auth import (
    ASGIApp,
    auth_middleware,
    normalize_content_type_middleware,
    strip_trailing_slash_middleware,
)
from falcon_mcp.common.fql import FQL_FILTER_HINT_SUFFIX
from falcon_mcp.common.logging import configure_logging, get_logger
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS, offload_to_thread
from falcon_mcp.tool_filter import Resolution, ToolPolicy, ToolRecord

if TYPE_CHECKING:
    from falcon_mcp.dynamic import DynamicMode

logger = get_logger(__name__)

# Type alias for transport options
TransportType = Literal["stdio", "sse", "streamable-http"]

# Hosts that keep the server reachable only from the local machine. Binding to
# anything else exposes it on the network, where an unauthenticated endpoint is a risk.
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

BASE_INSTRUCTIONS = (
    "This server provides access to CrowdStrike Falcon capabilities.\n\n"
    f"Composing filters: {FQL_FILTER_HINT_SUFFIX} When a tool's filter parameter names "
    "a falcon:// guide resource, read it before composing a filter: it lists the fields "
    "and operators that endpoint actually accepts, and an unsupported field returns an "
    "empty result rather than an error, which is indistinguishable from a genuine "
    "no-match.\n\n"
    "Changing state: readOnlyHint=false marks a tool that changes tenant state, and "
    "destructiveHint=true marks one whose effect cannot be undone. Confirm the user's "
    "intent before calling either."
)


class FalconMCPServer:
    """Main server class for the Falcon MCP server."""

    def __init__(
        self,
        base_url: str | None = None,
        debug: bool = False,
        enabled_modules: set[str] | None = None,
        user_agent_comment: str | None = None,
        stateless_http: bool = False,
        client_id: str | None = None,
        client_secret: str | None = None,
        api_key: str | None = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        member_cid: str | None = None,
        proxy: str | None = None,
        dynamic: bool = False,
        read_only: bool = False,
        allowed_tools: set[str] | None = None,
        excluded_tools: set[str] | None = None,
    ):
        """Initialize the Falcon MCP server.

        Args:
            base_url: Falcon API base URL
            debug: Enable debug logging
            enabled_modules: Set of module names to enable (defaults to all modules)
            user_agent_comment: Additional information to include in the User-Agent comment section
            stateless_http: Enable stateless HTTP mode (creates new transport per request)
            client_id: Falcon API Client ID (defaults to FALCON_CLIENT_ID env var)
            client_secret: Falcon API Client Secret (defaults to FALCON_CLIENT_SECRET env var)
            api_key: API key for HTTP transport authentication (x-api-key header)
            host: Host to bind to for HTTP transports (default: 127.0.0.1)
            port: Port to listen on for HTTP transports (default: 8000)
            member_cid: Child CID for Flight Control (MSSP) support (defaults to FALCON_MEMBER_CID env var)
            proxy: HTTP/HTTPS proxy URL for outbound Falcon API connections (defaults to FALCON_PROXY_URL env var)
            dynamic: Enable dynamic mode (discovery meta-tools instead of the full surface)
            read_only: Register only read-only tools, overriding allowed_tools
            allowed_tools: Additive allow-list of prefixed tool names.
            excluded_tools: Deny-list of prefixed tool names; wins over allowed_tools

        Raises:
            ValueError: If allowed_tools or excluded_tools name unknown tools
        """
        # Store configuration
        self.base_url = base_url
        self.debug = debug
        self.user_agent_comment = user_agent_comment
        self.stateless_http = stateless_http
        self.api_key = api_key
        self.host = host
        self.port = port
        self.dynamic = dynamic

        allowed_tools = allowed_tools or set()
        excluded_tools = excluded_tools or set()

        tool_module_map = (
            registry.get_tool_module_map() if (allowed_tools or excluded_tools) else {}
        )
        self._validate_filter_tool_names(allowed_tools, excluded_tools, tool_module_map)

        # Resolve which modules to load. The allow-list is additive: it pulls in the
        # modules owning the tools it names, gated so they contribute only those
        # tools.
        if enabled_modules:
            self.enabled_modules = set(enabled_modules)
        elif allowed_tools:
            # --tools alone supplies the whole surface, so start from no modules.
            self.enabled_modules = set()
        else:
            self.enabled_modules = set(registry.get_module_names())

        allow_list_modules = {
            tool_module_map[name] for name in allowed_tools if name in tool_module_map
        }
        # Modules pulled in solely for the allow-list get loaded but not reported as
        # enabled: they contribute only their named tools.
        self.loaded_modules = self.enabled_modules | allow_list_modules

        self.tool_policy = ToolPolicy(
            read_only=read_only,
            allowed=allowed_tools,
            excluded=excluded_tools,
            enabled_modules=self.enabled_modules,
        )

        # Configure logging
        configure_logging(debug=self.debug)
        logger.info("Initializing Falcon MCP Server")

        # Initialize the Falcon client
        self.falcon_client = FalconClient(
            base_url=self.base_url,
            debug=self.debug,
            user_agent_comment=self.user_agent_comment,
            client_id=client_id,
            client_secret=client_secret,
            member_cid=member_cid,
            proxy=proxy,
        )

        # Authenticate with the Falcon API
        if not self.falcon_client.authenticate():
            msg = self.falcon_client.auth_failure_message()
            logger.error(msg)
            raise RuntimeError(msg)

        # Initialize the MCP server
        self.server = FastMCP(
            name="Falcon MCP Server",
            instructions=self._instructions(),
            debug=self.debug,
            log_level="DEBUG" if self.debug else "INFO",
            stateless_http=self.stateless_http,
            host=self.host,
            port=self.port,
        )

        # Set the server version in MCP protocol metadata (returned in initialize handshake)
        self.server._mcp_server.version = get_version()

        # Initialize and register modules
        self.modules = {}
        # Set before _register_tools so list_enabled_tools can tell the two catalog
        # sources apart.
        self._dynamic_mode: DynamicMode | None = None
        available_modules = registry.get_available_modules()
        for module_name in self.loaded_modules:
            if module_name in available_modules:
                module_class = available_modules[module_name]
                self.modules[module_name] = module_class(self.falcon_client)
                logger.debug("Initialized module: %s", module_name)

        # Register tools and resources from modules
        tool_count = self._register_tools()
        tool_word = "tool" if tool_count == 1 else "tools"

        resource_count = self._register_resources()
        resource_word = "resource" if resource_count == 1 else "resources"

        # Count modules and tools with proper grammar
        module_count = len(self.enabled_modules & set(self.modules))
        module_word = "module" if module_count == 1 else "modules"

        logger.info(
            "Falcon MCP v%s — %d %s, %d %s, %d %s%s",
            get_version(),
            module_count,
            module_word,
            tool_count,
            tool_word,
            resource_count,
            resource_word,
            " (dynamic mode)" if self.dynamic else "",
        )

        if self.tool_policy.active:
            # Counts only what the operator asked to remove. Run with --debug to
            # see the names.
            withheld = len(self._resolution.withheld_by_rule)
            logger.info(
                "Tool policy active (%s) — %d %s withheld",
                self.tool_policy.describe(),
                withheld,
                "tool" if withheld == 1 else "tools",
            )

    def _instructions(self) -> str:
        """Describe the server, and in dynamic mode the loop for reaching a tool.

        Both modes inherit BASE_INSTRUCTIONS, which carries the cross-cutting guidance
        no single tool description owns.
        """
        if not self.dynamic:
            return BASE_INSTRUCTIONS
        return (
            f"{BASE_INSTRUCTIONS}\n\nThis server is running in dynamic mode: the "
            "Falcon tools are not individually registered, and are reached through "
            "three tools instead — falcon_search_tools and falcon_execute_tool for "
            "discovery, plus the always-on falcon_list_enabled_tools inventory.\n\n"
            "1. falcon_search_tools with a keyword query, or a module name, lists "
            "candidate tools ordered by likely relevance. These entries carry each "
            "tool's name, description, and read_only / destructive flags, but no "
            "parameters. The order is a keyword match, not a judgement of intent, so "
            "read the descriptions and flags and pick the tool that fits.\n"
            "2. falcon_search_tools again with tool_names=[chosen name] returns the "
            "full parameter schema for those tools, including filter syntax hints. "
            "Name more than one to compare candidates.\n"
            "3. falcon_execute_tool runs the tool with those parameters.\n\n"
            "falcon_list_enabled_tools gives the full inventory of Falcon tools "
            "available here, grouped by the module each belongs to. A capability "
            "absent from that list is not available on this server, whether because "
            "its module is off or a filter withholds it — report that rather than "
            "searching repeatedly."
        )

    def _validate_filter_tool_names(
        self,
        allowed: set[str],
        excluded: set[str],
        tool_module_map: dict[str, str],
    ) -> None:
        """Reject allow/deny-list entries that name no known tool.

        Runs before authentication so a typo costs no Falcon round-trip. Matters most
        for the deny-list, where an ignored name would leave a tool exposed.

        Args:
            allowed: Allow-list names supplied by the operator.
            excluded: Deny-list names supplied by the operator.
            tool_module_map: Every known tool name mapped to its module.

        Raises:
            ValueError: If any named tool is unrecognized.
        """
        named = allowed | excluded
        if not named:
            return

        unknown = sorted(named - set(tool_module_map))
        if unknown:
            raise ValueError(
                f"Unrecognized tool names: {', '.join(unknown)}. "
                "Names must be the falcon_-prefixed names clients see "
                "(e.g. falcon_search_hosts)."
            )

    def _register_tools(self) -> int:
        """Register tools from all modules, then subtract the ones policy withholds.

        Registration runs first so the policy resolves against the tools the server
        actually holds — module ownership and annotations are then facts, not
        something to predict ahead of time.

        Returns:
            int: Number of tools left registered
        """
        # falcon_list_enabled_tools is always registered: it is the cheap way to see
        # every tool available, and dynamic mode's zero-hit hint points here.
        # Meta-tools are exempt from the policy — withholding them leaves the server
        # undiscoverable.
        self.server.add_tool(
            offload_to_thread(self.list_enabled_tools),
            name="falcon_list_enabled_tools",
            annotations=READ_ONLY_ANNOTATIONS,
            structured_output=False,
        )

        if self.dynamic:
            # Dynamic mode: expose only the discovery/execution meta-tools plus
            # falcon_list_enabled_tools above (3 tools total) so the context window
            # stays minimal. The catalog applies the policy while building, so a
            # withheld tool is absent from search and 404s in the executor.
            from falcon_mcp.dynamic import DynamicMode

            self._dynamic_mode = DynamicMode(self.modules, self.server, self.tool_policy)
            self._dynamic_mode.register()
            self._resolution = self._dynamic_mode.catalog.resolution
        else:
            # Normal mode: register the other two core tools and then each module's tools.
            self.server.add_tool(
                offload_to_thread(self.falcon_check_connectivity),
                name="falcon_check_connectivity",
                annotations=READ_ONLY_ANNOTATIONS,
                structured_output=False,
            )

            self.server.add_tool(
                offload_to_thread(self.list_enabled_modules),
                name="falcon_list_enabled_modules",
                annotations=READ_ONLY_ANNOTATIONS,
                structured_output=False,
            )

            for module in self.modules.values():
                module.register_tools(self.server)

            self._resolution = self._apply_policy()

        # Count what the tool manager holds; arithmetic would overcount when the
        # policy withholds a tool.
        return len(self.server._tool_manager._tools)

    def _apply_policy(self) -> Resolution:
        """Remove the tools the policy withholds from the already-registered surface.

        Returns:
            The policy's keep/removed partition of this server's module tools.
        """
        registered = self.server._tool_manager._tools
        catalog = {
            name: ToolRecord(module=module_name, annotations=tool.annotations)
            for module_name, module in self.modules.items()
            for name in module.tools
            if (tool := registered.get(name)) is not None
        }
        resolution = self.tool_policy.resolve(catalog)

        for name in resolution.removed:
            # remove_tool raises on an unknown name, and ToolManager.add_tool skips
            # duplicates silently, so a repeated registration pass reaches here with
            # the tool already gone.
            if name in registered:
                self.server.remove_tool(name)
                logger.debug("Withheld tool: %s", name)

        # Keep module.tools mirroring what is registered.
        for module in self.modules.values():
            module.tools = [name for name in module.tools if name not in resolution.removed]

        return resolution

    def _register_resources(self) -> int:
        """Register resources from all modules.

        Returns:
            int: Number of resources registered
        """
        # Deliberately not gated by the tool policy: tool descriptions name their
        # guide by URI, so dropping one strands a live tool. See
        # TestGuideReferencesResolve.
        for module in self.modules.values():
            if hasattr(module, "register_resources") and callable(module.register_resources):
                module.register_resources(self.server)

        return len(self.server._resource_manager._resources)

    def falcon_check_connectivity(self) -> dict[str, bool]:
        """Check connectivity to the Falcon API."""
        try:
            # Deliberately bypasses FalconClient._token_lock: this is a stateless
            # probe (stateful=False) that never mutates the shared token, so it
            # cannot corrupt a concurrent refresh. It may fire its own throwaway
            # /oauth2/token POST alongside a real refresh, which is acceptable for
            # a diagnostic tool — the lock guards the shared-state refresh path,
            # not every possible token request.
            result = self.falcon_client.client._login_handler(stateful=False)
            return {"connected": result.get("status_code") == 201}
        except Exception:
            logger.warning("Connectivity probe failed", exc_info=True)
            return {"connected": False}

    def list_enabled_modules(self) -> dict[str, list[str]]:
        """Lists enabled modules in the falcon-mcp server.

        These modules are determined by the --modules flag when starting the server.
        If no modules are specified, all available modules are enabled.
        """
        return {"modules": sorted(self.enabled_modules & set(self.modules))}

    def list_enabled_tools(self) -> dict[str, Any]:
        """Lists the Falcon tools available on this server.

        Call this to see the full inventory before hunting for a capability: a name
        absent from this list is not available here, whether because its module is not
        enabled or because a tool filter withholds it. Returns the sorted tool names,
        their count, and a by_module mapping grouping each tool under the module it
        belongs to — the names listed under a module are the only ones available from
        it, and are the exact spellings falcon_search_tools accepts as module=.
        filters_active names the filter rules whenever any are configured. Excludes
        this server's own meta-tools, which are always present in tools/list.
        """
        if self._dynamic_mode is not None:
            # Building the catalog clears module.tools, so it is the only record of
            # what falcon_execute_tool accepts.
            entries = self._dynamic_mode.catalog.entries
            names = set(entries)
            by_module: dict[str, list[str]] = {}
            for name, entry in entries.items():
                by_module.setdefault(entry.module, []).append(name)
        else:
            # _apply_policy() prunes module.tools to what stayed registered.
            by_module = {
                module_name: sorted(module.tools)
                for module_name, module in self.modules.items()
                if module.tools
            }
            names = {name for tools in by_module.values() for name in tools}
        result: dict[str, Any] = {
            "tools": sorted(names),
            "total": len(names),
            # Same catalog the search dispatches from, so the published vocabulary
            # cannot drift from what module= accepts.
            "by_module": {mod: sorted(by_module[mod]) for mod in sorted(by_module)},
        }
        # Only present when a filter narrowed the list, so an unfiltered server's
        # response is unchanged and the key's presence is itself the signal.
        if self.tool_policy.active:
            result["filters_active"] = self.tool_policy.describe()
        return result

    def _run_http_transport(self, app: ASGIApp) -> None:
        """Apply middleware and start uvicorn for an HTTP transport.

        Args:
            app: The ASGI application from FastMCP
        """
        app = strip_trailing_slash_middleware(app)
        app = normalize_content_type_middleware(app)
        if self.api_key:
            app = auth_middleware(app, self.api_key)
            logger.info("API key authentication enabled")
        elif self.host not in _LOOPBACK_HOSTS:
            logger.warning(
                "Server is binding to %s:%d without --api-key: the endpoint is reachable "
                "on the network and has no authentication. Set --api-key "
                "(or FALCON_MCP_API_KEY) when binding beyond loopback.",
                self.host,
                self.port,
            )
        uvicorn.run(
            app,
            host=self.host,
            port=self.port,
            log_level="debug" if self.debug else "info",
        )

    def run(self, transport: TransportType = "stdio") -> None:
        """Run the MCP server.

        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
        """
        if transport in ("streamable-http", "sse"):
            logger.info("Starting %s server on %s:%d", transport, self.host, self.port)
            app_method = (
                self.server.streamable_http_app
                if transport == "streamable-http"
                else self.server.sse_app
            )
            self._run_http_transport(app_method())
        else:
            self.server.run(transport)


def parse_modules_list(modules_string: str) -> list[str]:
    """Parse and validate comma-separated module list.

    Args:
        modules_string: Comma-separated string of module names

    Returns:
        List of validated module names, empty if the string is empty

    Raises:
        argparse.ArgumentTypeError: If any module names are invalid
    """
    # Get available modules
    available_modules = registry.get_module_names()

    # Split by comma and clean up whitespace
    modules = [m.strip() for m in modules_string.split(",") if m.strip()]

    # Validate against available modules
    invalid_modules = [m for m in modules if m not in available_modules]
    if invalid_modules:
        raise argparse.ArgumentTypeError(
            f"Invalid modules: {', '.join(invalid_modules)}. "
            f"Available modules: {', '.join(available_modules)}"
        )

    return modules


def parse_tools_list(tools_string: str) -> list[str]:
    """Parse a comma-separated tool-name list.

    Names are not validated here: the set of valid tool names is only known after
    module registration, so FalconMCPServer rejects unknown names at startup.

    Args:
        tools_string: Comma-separated string of prefixed tool names

    Returns:
        List of tool names, empty if the string is empty
    """
    return [t.strip() for t in tools_string.split(",") if t.strip()]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Falcon MCP Server")

    # Version
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {get_version()}",
    )

    # Transport options
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse", "streamable-http"],
        default=os.environ.get("FALCON_MCP_TRANSPORT", "stdio"),
        help="Transport protocol to use (default: stdio, env: FALCON_MCP_TRANSPORT)",
    )

    # Module selection
    available_modules = registry.get_module_names()

    parser.add_argument(
        "--modules",
        "-m",
        type=parse_modules_list,
        default=parse_modules_list(os.environ.get("FALCON_MCP_MODULES", "")),
        metavar="MODULE1,MODULE2,...",
        help=f"Comma-separated list of modules to enable. Available: [{', '.join(available_modules)}] "
        f"(default: all modules, env: FALCON_MCP_MODULES)",
    )

    # Debug mode
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=os.environ.get("FALCON_MCP_DEBUG", "").lower() == "true",
        help="Enable debug logging (env: FALCON_MCP_DEBUG)",
    )

    # API base URL
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FALCON_BASE_URL"),
        help="Falcon API base URL (env: FALCON_BASE_URL)",
    )

    # HTTP transport configuration
    parser.add_argument(
        "--host",
        default=os.environ.get("FALCON_MCP_HOST", "127.0.0.1"),
        help="Host to bind to for HTTP transports (default: 127.0.0.1, env: FALCON_MCP_HOST)",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.environ.get("FALCON_MCP_PORT", "8000")),
        help="Port to listen on for HTTP transports (default: 8000, env: FALCON_MCP_PORT)",
    )

    parser.add_argument(
        "--user-agent-comment",
        default=os.environ.get("FALCON_MCP_USER_AGENT_COMMENT"),
        help="Additional information to include in the User-Agent comment section (env: FALCON_MCP_USER_AGENT_COMMENT)",
    )

    # Stateless HTTP mode (creates new transport per request for horizontal scaling)
    parser.add_argument(
        "--stateless-http",
        action="store_true",
        default=os.environ.get("FALCON_MCP_STATELESS_HTTP", "").lower() == "true",
        help="Enable stateless HTTP mode for scalable deployments (env: FALCON_MCP_STATELESS_HTTP)",
    )

    # API key authentication for HTTP transports
    parser.add_argument(
        "--api-key",
        default=os.environ.get("FALCON_MCP_API_KEY"),
        help="API key for HTTP transport authentication (x-api-key header, env: FALCON_MCP_API_KEY)",
    )

    # Flight Control (MSSP) support
    parser.add_argument(
        "--member-cid",
        default=os.environ.get("FALCON_MEMBER_CID"),
        help="Child CID for Flight Control (MSSP) support (env: FALCON_MEMBER_CID)",
    )

    # Proxy configuration
    parser.add_argument(
        "--proxy",
        default=os.environ.get("FALCON_PROXY_URL"),
        help="HTTP/HTTPS proxy URL for outbound Falcon API connections (env: FALCON_PROXY_URL). "
        "Example: http://proxy.corp.example.com:8080",
    )

    # Dynamic mode
    parser.add_argument(
        "--dynamic",
        action="store_true",
        default=os.environ.get("FALCON_MCP_DYNAMIC", "").lower() == "true",
        help="Enable dynamic mode: exposes 3 tools (list-enabled-tools + search + execute) "
        "instead of all module tools (env: FALCON_MCP_DYNAMIC)",
    )

    # Blast-radius controls. These compose with --modules and with each other;
    # --read-only and --exclude-tools both override --tools.
    parser.add_argument(
        "--read-only",
        action="store_true",
        default=os.environ.get("FALCON_MCP_READ_ONLY", "").lower() == "true",
        help="Register only read-only tools, disabling every tool that mutates tenant state. "
        "Takes precedence over --tools (env: FALCON_MCP_READ_ONLY)",
    )

    parser.add_argument(
        "--tools",
        type=parse_tools_list,
        default=parse_tools_list(os.environ.get("FALCON_MCP_TOOLS", "")),
        metavar="TOOL1,TOOL2,...",
        help="Comma-separated allow-list of tool names to register (e.g. "
        "falcon_search_hosts,falcon_search_detections). Additive: added to the tools from "
        "--modules, and may name tools from modules that are not enabled. Set alone, only "
        "these tools load. Unknown names abort startup (env: FALCON_MCP_TOOLS)",
    )

    parser.add_argument(
        "--exclude-tools",
        type=parse_tools_list,
        default=parse_tools_list(os.environ.get("FALCON_MCP_EXCLUDE_TOOLS", "")),
        metavar="TOOL1,TOOL2,...",
        help="Comma-separated deny-list of tool names to withhold. Overrides --tools. "
        "Unknown names abort startup (env: FALCON_MCP_EXCLUDE_TOOLS)",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the Falcon MCP server."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments (includes environment variable defaults)
    args = parse_args()

    try:
        # Create and run the server
        server = FalconMCPServer(
            base_url=args.base_url,
            debug=args.debug,
            enabled_modules=set(args.modules),
            user_agent_comment=args.user_agent_comment,
            stateless_http=args.stateless_http,
            api_key=args.api_key,
            host=args.host,
            port=args.port,
            member_cid=args.member_cid,
            proxy=args.proxy,
            dynamic=args.dynamic,
            read_only=args.read_only,
            allowed_tools=set(args.tools),
            excluded_tools=set(args.exclude_tools),
        )
        logger.info("Starting server with %s transport", args.transport)
        server.run(args.transport)
    except RuntimeError as e:
        logger.error("Runtime error: %s", e)
        sys.exit(1)
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        # Catch any other exceptions to ensure graceful shutdown
        logger.error("Unexpected error running server: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
