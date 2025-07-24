#!/usr/bin/env python3
"""
SSE transport example for Falcon MCP Server.

This script demonstrates how to initialize and run the Falcon MCP server with SSE transport.
"""
import os

from dotenv import load_dotenv

from falcon_mcp.server import FalconMCPServer


def main():
    """Run the Falcon MCP server with SSE transport."""
    # Load environment variables from .env file
    load_dotenv()

    # Create and run the server with SSE transport
    server = FalconMCPServer(
        # You can override the base URL if needed
        # base_url="https://api.us-2.crowdstrike.com",
        debug=os.environ.get("DEBUG", "").lower() == "true"
    )

    # Run the server with SSE transport
    server.run("sse")


if __name__ == "__main__":
    main()
