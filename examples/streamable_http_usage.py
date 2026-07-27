#!/usr/bin/env python3
"""
Streamable HTTP transport example for Falcon MCP Server.

This script demonstrates how to initialize and run the Falcon MCP server
with streamable-http transport for custom integrations and web-based deployments.
"""

import os

from dotenv import load_dotenv

from falcon_mcp.server import FalconMCPServer


def main() -> None:
    """Run the Falcon MCP server with streamable-http transport."""
    # Load environment variables from .env file
    load_dotenv()

    # Example 1: Default settings (port 8000, localhost)
    # server = FalconMCPServer(
    #     debug=os.environ.get("DEBUG", "").lower() == "true",
    # )
    # server.run("streamable-http")
    #   -> http://127.0.0.1:8000/mcp

    # Example 2: Custom host/port for external access.
    # Binding to 0.0.0.0 exposes the server on the network with no auth by default,
    # so set api_key (any secure string you choose) to require callers to send a
    # matching x-api-key header. Prefer the FALCON_MCP_API_KEY env var over hardcoding.
    server = FalconMCPServer(
        # You can override the base URL if needed
        # base_url="https://api.us-2.crowdstrike.com",
        debug=os.environ.get("DEBUG", "").lower() == "true",
        host="0.0.0.0",
        port=8080,
        api_key=os.environ.get("FALCON_MCP_API_KEY"),
    )
    server.run("streamable-http")


if __name__ == "__main__":
    main()
