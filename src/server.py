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

from .client import FalconClient
from .common.logging import configure_logging, get_logger
from . import registry

logger = get_logger(__name__)


class FalconMCPServer:
    """Main server class for the Falcon MCP server."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
        enabled_modules: Optional[Set[str]] = None,
    ):
        """Initialize the Falcon MCP server.

        Args:
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var)
            debug: Enable debug logging
            enabled_modules: Set of module names to enable (defaults to all modules)
        """
        # Store configuration
        self.base_url = base_url
        self.debug = debug

        self.enabled_modules = enabled_modules or set(registry.AVAILABLE_MODULES.keys())

        # Configure logging
        configure_logging(debug=self.debug)
        logger.info("Initializing Falcon MCP Server")

        # Initialize the Falcon client
        self.falcon_client = FalconClient(
            base_url=self.base_url,
            debug=self.debug
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
            log_level="DEBUG" if self.debug else "INFO"
        )

        # Initialize and register modules
        self.modules = {}
        for module_name in self.enabled_modules:
            if module_name in registry.AVAILABLE_MODULES:
                module_class = registry.AVAILABLE_MODULES[module_name]
                self.modules[module_name] = module_class(self.falcon_client)
                logger.debug("Initialized module: %s", module_name)

        # Register tools from modules
        self._register_tools()

        # Count modules and tools with proper grammar
        module_count = len(self.modules)
        module_word = "module" if module_count == 1 else "modules"

        # Simple count of tools (handles modules without tools attribute)
        tool_count = sum(len(getattr(m, 'tools', [])) for m in self.modules.values())
        tool_word = "tool" if tool_count == 1 else "tools"

        logger.info("Initialized %d %s with %d %s", module_count, module_word, tool_count, tool_word)

    def _register_tools(self):
        """Register tools from all modules."""
        # Register core tools directly
        self.server.add_tool(
            self.falcon_check_connectivity,
            name="falcon_check_connectivity",
            description="Check connectivity to the Falcon API."
        )

        self.server.add_tool(
            self.get_available_modules,
            name="falcon_get_available_modules",
            description="Get information about available modules."
        )

        # Register tools from modules
        for module in self.modules.values():
            module.register_tools(self.server)

    def falcon_check_connectivity(self) -> Dict[str, bool]:
        """Check connectivity to the Falcon API.

        Returns:
            Dict[str, bool]: Connectivity status
        """
        return {"connected": self.falcon_client.is_authenticated()}

    def get_available_modules(self) -> Dict[str, List[str]]:
        """Get information about available modules.

        Returns:
            Dict[str, List[str]]: Available modules
        """
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
            uvicorn.run(app, host=host, port=port, log_level="info" if not self.debug else "debug")
        elif transport == "sse":
            # For sse, use uvicorn directly for custom host/port (same pattern as streamable-http)
            logger.info("Starting sse server on %s:%d", host, port)

            # Get the ASGI app from FastMCP
            app = self.server.sse_app()

            # Run with uvicorn for custom host/port configuration
            uvicorn.run(app, host=host, port=port, log_level="info" if not self.debug else "debug")
        else:
            # For stdio, use the default FastMCP run method (no host/port needed)
            self.server.run(transport)


def parse_args():
    """Parse command line arguments."""
    # Ensure modules are discovered before creating the parser
    registry.discover_modules()

    parser = argparse.ArgumentParser(description="Falcon MCP Server")

    # Transport options
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )

    # Module selection
    available_modules = list(registry.AVAILABLE_MODULES.keys())
    parser.add_argument(
        "--modules", "-m",
        nargs="+",
        choices=available_modules,
        default=available_modules,
        metavar="MODULE",
        help=f"Modules to enable. Available: {', '.join(available_modules)} (default: {','.join(available_modules)})"
    )

    # Debug mode
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )

    # API base URL
    parser.add_argument(
        "--base-url",
        help="Falcon API base URL (defaults to FALCON_BASE_URL env var)"
    )

    # HTTP transport configuration
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transports (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to listen on for HTTP transports (default: 8000)"
    )


    return parser.parse_args()


def main():
    """Main entry point for the Falcon MCP server."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Get debug setting
    debug = args.debug or os.environ.get("DEBUG", "").lower() == "true"

    try:
        # Create and run the server
        server = FalconMCPServer(
            base_url=args.base_url,
            debug=debug,
            enabled_modules=set(args.modules)
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
    except Exception as e:  # pylint: disable=broad-except
        # Catch any other exceptions to ensure graceful shutdown
        logger.error("Unexpected error running server: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
