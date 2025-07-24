"""
Base module for Falcon MCP Server

This module provides the base class for all Falcon MCP server modules.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from mcp import Resource
from mcp.server import FastMCP

from falcon_mcp.client import FalconClient
from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters

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
        self.resources = []  # List to track registered resources

    @abstractmethod
    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP Server.

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

    def _add_resource(self, server: FastMCP, resource: Resource) -> None:
        """Add a resource to the MCP server and track it.

        Args:
            server: MCP server instance
            resource: Resource object
        """
        server.add_resource(resource=resource)

        resource_uri = resource.uri
        self.resources.append(resource_uri)
        logger.debug("Added resource: %s", resource_uri)

    def _base_get_by_ids(
        self,
        operation: str,
        ids: List[str],
        id_key: str = "ids",
        **additional_params,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Helper method for API operations that retrieve entities by IDs.

        Args:
            operation: The API operation name
            ids: List of entity IDs
            id_key: The key name for IDs in the request body (default: "ids")
            **additional_params: Additional parameters to include in the request body

        Returns:
            List of entity details or error dict
        """
        # Build the request body with dynamic ID key and additional parameters
        body_params = {id_key: ids}
        body_params.update(additional_params)

        body = prepare_api_parameters(body_params)

        # Make the API request
        response = self.client.command(operation, body=body)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def _is_error(self, response: Any) -> bool:
        return isinstance(response, dict) and "error" in response
