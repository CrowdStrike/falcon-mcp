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

    def _base_search_api_call(
        self,
        operation: str,
        search_params: Dict[str, Any],
        error_message: str = "Search operation failed",
        default_result: Any = None,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Standardized API call for search operations with parameters.

        This method consolidates the common pattern of:
        1. Preparing parameters
        2. Making API request with parameters
        3. Handling the response
        4. Error checking

        Args:
            operation: The API operation name (e.g., "QueryDevicesByFilter")
            search_params: Dictionary of search parameters (filter, limit, offset, sort, etc.)
            error_message: Custom error message for failed operations
            default_result: Default value to return if no results found

        Returns:
            API response data or error dict
        """
        # Prepare parameters for the API request
        prepared_params = prepare_api_parameters(search_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        # Make the API request
        response = self.client.command(operation, parameters=prepared_params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result if default_result is not None else [],
        )

    def _base_query_api_call(
        self,
        operation: str,
        query_params: Dict[str, Any] = None,
        body_params: Dict[str, Any] = None,
        error_message: str = "Query operation failed",
        default_result: Any = None,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Standardized API call for operations that can use both parameters and body.

        Args:
            operation: The API operation name
            query_params: Dictionary of query parameters (for parameters= argument)
            body_params: Dictionary of body parameters (for body= argument)
            error_message: Custom error message for failed operations
            default_result: Default value to return if no results found

        Returns:
            API response data or error dict
        """
        # Prepare the API call arguments
        call_args = {}

        if query_params:
            call_args["parameters"] = prepare_api_parameters(query_params)

        if body_params:
            call_args["body"] = prepare_api_parameters(body_params)

        logger.debug("Executing %s with args: %s", operation, call_args)

        # Make the API request
        response = self.client.command(operation, **call_args)

        # Handle GraphQL operations differently - they don't use "resources" structure
        if operation == "api_preempt_proxy_post_graphql":
            # For GraphQL, check status and return the full body on success
            if response.get("status_code") == 200:
                return response.get("body", {})
            else:
                # Use standard error handling for failed GraphQL requests
                return handle_api_response(
                    response,
                    operation=operation,
                    error_message=error_message,
                    default_result=default_result if default_result is not None else {},
                )

        # Handle the response using standard resource extraction
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result if default_result is not None else [],
        )

    def _is_error(self, response: Any) -> bool:
        return isinstance(response, dict) and "error" in response
