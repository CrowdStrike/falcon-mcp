"""
Base module for Falcon MCP Server

This module provides the base class for all Falcon MCP server modules.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from mcp.server import FastMCP

from src.common.errors import handle_api_response
from src.common.utils import prepare_api_parameters

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

    def _add_tool(self, server: FastMCP, method: Callable, name: str) -> None:
        """Add a tool to the MCP server and track it.

        Args:
            server: MCP server instance
            method: Method to register
            name: Tool name
        """
        prefixed_name = f"falcon_{name}"
        server.add_tool(method, name=prefixed_name)
        self.tools.append(prefixed_name)
        logger.debug("Added tool: %s", prefixed_name)

    def _base_get_by_ids(
        self, operation: str, ids: List[str],
    ) -> Dict[str, Any]:
        body = prepare_api_parameters({
            "ids": ids
        })

        # Make the API request
        response = self.client.command(operation, body=body)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )
