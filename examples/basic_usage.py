#!/usr/bin/env python3
"""
Basic usage example for Falcon MCP Server.

This script demonstrates how to initialize and run the Falcon MCP server.
"""

import os

from dotenv import load_dotenv

from falcon_mcp.server import FalconMCPServer


def main():
    """Run the Falcon MCP server with default settings."""
    # Load environment variables from .env file
    load_dotenv()

    # Create and run the server with stdio transport
    server = FalconMCPServer(
        # You can override the base URL if needed
        # base_url="https://api.us-2.crowdstrike.com",
        debug=os.environ.get("DEBUG", "").lower() == "true",
    )

    # Run the server with stdio transport (default)
    server.run()


if __name__ == "__main__":
    main()
