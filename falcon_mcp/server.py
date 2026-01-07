"""
Falcon MCP Server - Main entry point

This module provides the main server class for the Falcon MCP server
and serves as the entry point for the application.
"""

import argparse
import os
import sys
from typing import Dict, List, Optional, Set

import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from falcon_mcp import registry
from falcon_mcp.client import FalconClient
from falcon_mcp.common.logging import configure_logging, get_logger

logger = get_logger(__name__)


class FalconMCPServer:
    """Main server class for the Falcon MCP server."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
        enabled_modules: Optional[Set[str]] = None,
        user_agent_comment: Optional[str] = None,
        stateless_http: bool = False,
    ):
        """Initialize the Falcon MCP server.

        Args:
            base_url: Falcon API base URL
            debug: Enable debug logging
            enabled_modules: Set of module names to enable (defaults to all modules)
            user_agent_comment: Additional information to include in the User-Agent comment section
            stateless_http: Enable stateless HTTP mode (creates new transport per request)
        """
        # Store configuration
        self.base_url = base_url
        self.debug = debug
        self.user_agent_comment = user_agent_comment
        self.stateless_http = stateless_http

        self.enabled_modules = enabled_modules or set(registry.get_module_names())

        # Configure logging
        configure_logging(debug=self.debug)
        logger.info("Initializing Falcon MCP Server")

        # Initialize the Falcon client
        self.falcon_client = FalconClient(
            base_url=self.base_url,
            debug=self.debug,
            user_agent_comment=self.user_agent_comment,
        )

        # Authenticate with the Falcon API
        if not self.falcon_client.authenticate():
            logger.error("Failed to authenticate with the Falcon API")
            raise RuntimeError("Failed to authenticate with the Falcon API")

        # Initialize the MCP server
        self.server = FastMCP(
            name="Falcon MCP Server",
            instructions="This server provides access to CrowdStrike Falcon capabilities.",
            debug=self.debug,
            log_level="DEBUG" if self.debug else "INFO",
            stateless_http=self.stateless_http,
        )

        # Initialize and register modules
        self.modules = {}
        available_modules = registry.get_available_modules()
        for module_name in self.enabled_modules:
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
        module_count = len(self.modules)
        module_word = "module" if module_count == 1 else "modules"

        logger.info(
            "Initialized %d %s with %d %s and %d %s",
            module_count,
            module_word,
            tool_count,
            tool_word,
            resource_count,
            resource_word,
        )

    def _register_tools(self) -> int:
        """Register tools from all modules.

        Returns:
            int: Number of tools registered
        """
        # Register core tools directly
        self.server.add_tool(
            self.falcon_check_connectivity,
            name="falcon_check_connectivity",
        )

        self.server.add_tool(
            self.list_enabled_modules,
            name="falcon_list_enabled_modules",
        )

        self.server.add_tool(
            self.list_modules,
            name="falcon_list_modules",
        )

        tool_count = 3  # the tools added above

        # Register tools from modules
        for module in self.modules.values():
            module.register_tools(self.server)

        tool_count += sum(len(getattr(m, "tools", [])) for m in self.modules.values())

        return tool_count

    def _register_resources(self) -> int:
        """Register resources from all modules.

        Returns:
            int: Number of resources registered
        """
        # Register resources from modules
        for module in self.modules.values():
            # Check if the module has a register_resources method
            if hasattr(module, "register_resources") and callable(module.register_resources):
                module.register_resources(self.server)

        return sum(len(getattr(m, "resources", [])) for m in self.modules.values())

    def falcon_check_connectivity(self) -> Dict[str, bool]:
        """Check connectivity to the Falcon API."""
        return {"connected": self.falcon_client.is_authenticated()}

    def list_enabled_modules(self) -> Dict[str, List[str]]:
        """Lists enabled modules in the falcon-mcp server.

        These modules are determined by the --modules flag when starting the server.
        If no modules are specified, all available modules are enabled.
        """
        return {"modules": list(self.modules.keys())}

    def list_modules(self) -> Dict[str, List[str]]:
        """Lists all available modules in the falcon-mcp server."""
        return {"modules": registry.get_module_names()}

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000):
        """Run the MCP server.

        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
            host: Host to bind to for HTTP transports (default: 127.0.0.1)
            port: Port to listen on for HTTP transports (default: 8000)
        """
        if transport == "streamable-http":
            # For streamable-http, use uvicorn directly for custom host/port
            logger.info("Starting streamable-http server on %s:%d", host, port)

            # Get the ASGI app from FastMCP (handles /mcp path automatically)
            app = self.server.streamable_http_app()

            # Run with uvicorn for custom host/port configuration
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info" if not self.debug else "debug",
            )
        elif transport == "sse":
            # For sse, use uvicorn directly for custom host/port (same pattern as streamable-http)
            logger.info("Starting sse server on %s:%d", host, port)

            # Get the ASGI app from FastMCP
            app = self.server.sse_app()

            # Run with uvicorn for custom host/port configuration
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info" if not self.debug else "debug",
            )
        else:
            # For stdio, use the default FastMCP run method (no host/port needed)
            self.server.run(transport)


def parse_modules_list(modules_string):
    """Parse and validate comma-separated module list.

    Args:
        modules_string: Comma-separated string of module names

    Returns:
        List of validated module names (returns all available modules if empty string)

    Raises:
        argparse.ArgumentTypeError: If any module names are invalid
    """
    # Get available modules
    available_modules = registry.get_module_names()

    # If empty string, return all available modules (default behavior)
    if not modules_string:
        return available_modules

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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Falcon MCP Server")

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

    return parser.parse_args()


def main():
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
        )
        logger.info("Starting server with %s transport", args.transport)
        server.run(args.transport, host=args.host, port=args.port)
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
