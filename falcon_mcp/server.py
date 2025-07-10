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

from falcon_mcp.client import FalconClient
from falcon_mcp.common.logging import configure_logging, get_logger
from falcon_mcp import registry

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

        self.enabled_modules = enabled_modules or set(registry.get_module_names())

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
        available_modules = registry.get_available_modules()
        for module_name in self.enabled_modules:
            if module_name in available_modules:
                module_class = available_modules[module_name]
                self.modules[module_name] = module_class(self.falcon_client)
                logger.debug("Initialized module: %s", module_name)

        # Register tools and resources from modules
        self._register_tools()
        self._register_resources()

        # Count modules and tools with proper grammar
        module_count = len(self.modules)
        module_word = "module" if module_count == 1 else "modules"

        # Simple count of tools (handles modules without tools attribute)
        tool_count = sum(len(getattr(m, 'tools', [])) for m in self.modules.values())
        tool_word = "tool" if tool_count == 1 else "tools"

        # Simple count of resources (handles modules without resources attribute)
        resource_count = sum(len(getattr(m, 'resources', [])) for m in self.modules.values())
        resource_word = "resource" if resource_count == 1 else "resources"

        logger.info(
            "Initialized %d %s with %d %s and %d %s",
            module_count, module_word, tool_count, tool_word, resource_count, resource_word
        )

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

    def _register_resources(self):
        """Register resources from all modules."""
        # Register resources from modules
        for module in self.modules.values():
            # Check if the module has a register_resources method
            if hasattr(module, 'register_resources') and callable(module.register_resources):
                module.register_resources(self.server)

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


def parse_modules_list(modules_string):
    """Parse and validate comma-separated module list.

    Args:
        modules_string: Comma-separated string of module names

    Returns:
        List of validated module names

    Raises:
        argparse.ArgumentTypeError: If any module names are invalid
    """
    if not modules_string:
        return []

    # Split by comma and clean up whitespace
    modules = [m.strip() for m in modules_string.split(',') if m.strip()]

    # Validate against available modules
    available_modules = registry.get_module_names()
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
        "--transport", "-t",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )

    # Module selection
    available_modules = registry.get_module_names()
    parser.add_argument(
        "--modules", "-m",
        type=parse_modules_list,
        metavar="MODULE1,MODULE2,...",
        help=f"Comma-separated list of modules to enable. Available: {', '.join(available_modules)}. "
             f"Can also be set via FALCON_MODULES environment variable (default: all modules)"
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

    # Determine which modules to enable with proper precedence
    enabled_modules = None

    # 1. Command-line arguments take precedence
    if args.modules is not None:
        enabled_modules = set(args.modules)
        logger.debug("Using modules from command line: %s", ', '.join(args.modules))

    # 2. Fall back to FALCON_MODULES environment variable
    elif os.environ.get("FALCON_MODULES"):
        try:
            env_modules = parse_modules_list(os.environ.get("FALCON_MODULES"))
            enabled_modules = set(env_modules)
            logger.debug("Using modules from FALCON_MODULES environment variable: %s", ', '.join(env_modules))
        except argparse.ArgumentTypeError as e:
            logger.error("Invalid FALCON_MODULES environment variable: %s", e)
            sys.exit(1)

    # 3. Default to all modules if none specified
    if enabled_modules is None:
        all_modules = registry.get_module_names()
        enabled_modules = set(all_modules)
        logger.debug("Using all available modules: %s", ', '.join(all_modules))

    try:
        # Create and run the server
        server = FalconMCPServer(
            base_url=args.base_url,
            debug=debug,
            enabled_modules=enabled_modules
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
