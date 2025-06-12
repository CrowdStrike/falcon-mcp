"""
Base module for Falcon MCP Server

This module provides the base class for all Falcon MCP server modules.
"""
from abc import ABC, abstractmethod
from typing import Callable

from mcp.server import FastMCP

from ..client import FalconClient
from ..common.logging import get_logger

logger = get_logger(__name__)


class BaseModule(ABC):
    """Base class for all Falcon MCP server modules."""

    def __init__(self, client: FalconClient):
        """Initialize the module.

        Args:
            client: Falcon API client
        """
        self.client = client
        self.tools = []  # List to track registered tools

    @abstractmethod
    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """

    def _add_tool(self, server: FastMCP, method: Callable, name: str, description: str) -> None:
        """Add a tool to the MCP server and track it.

        Args:
            server: MCP server instance
            method: Method to register
            name: Tool name
            description: Tool description
        """
        server.add_tool(method, name=name, description=description)
        self.tools.append(name)
        logger.debug("Added tool: %s", name)
