#!/usr/bin/env python3
"""Main entry point for the CrowdStrike Falcon MCP Server.

This module provides a convenient way to run the Falcon MCP server
during development or from the command line.
"""

import sys
from pathlib import Path

# Add src directory to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.api.server import main

if __name__ == "__main__":
    main() 