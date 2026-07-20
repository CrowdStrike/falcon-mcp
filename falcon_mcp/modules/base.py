"""
Base module for Falcon MCP Server

This module provides the base class for all Falcon MCP server modules.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from mcp import Resource
from mcp.server import FastMCP
from mcp.types import ToolAnnotations

from falcon_mcp.client import FalconClient
from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters

logger = get_logger(__name__)

# Default: read-only tool that talks to an external API
READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


class BaseModule(ABC):
    """Base class for all Falcon MCP server modules."""

    def __init__(self, client: FalconClient):
        """Initialize the module.

        Args:
            client: Falcon API client
        """
        self.client = client
        self.tools: list[str] = []  # List to track registered tools
        self.resources: list[str] = []  # List to track registered resources

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

    def _add_tool(
        self,
        server: FastMCP,
        method: Callable[..., Any],
        name: str,
        annotations: ToolAnnotations | None = None,
    ) -> None:
        """Add a tool to the MCP server and track it.

        Args:
            server: MCP server instance
            method: Method to register
            name: Tool name
            annotations: MCP tool annotations. Defaults to READ_ONLY_ANNOTATIONS.
        """
        prefixed_name = f"falcon_{name}"
        server.add_tool(
            method,
            name=prefixed_name,
            annotations=annotations or READ_ONLY_ANNOTATIONS,
            structured_output=False,
        )
        self.tools.append(prefixed_name)
        logger.debug("Added tool: %s", prefixed_name)

    def _add_resource(self, server: FastMCP, resource: Resource) -> None:
        """Add a resource to the MCP server and track it.

        Args:
            server: MCP server instance
            resource: Resource object
        """
        # FastMCP expects its own Resource type, cast accordingly
        server.add_resource(resource=resource)  # type: ignore[arg-type]

        resource_uri = resource.uri
        self.resources.append(str(resource_uri))
        logger.debug("Added resource: %s", resource_uri)

    def _base_get_by_ids(
        self,
        operation: str,
        ids: list[str],
        id_key: str = "ids",
        use_params: bool = False,
        **additional_params: Any,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Helper method for API operations that retrieve entities by IDs.

        Args:
            operation: The API operation name
            ids: List of entity IDs
            id_key: The key name for IDs in the request (default: "ids")
            use_params: If True, send IDs as query parameters (GET).
                       If False, send as request body (POST). Default: False
            **additional_params: Additional parameters to include in the request

        Returns:
            List of entity details or error dict
        """
        # Build the request params with dynamic ID key and additional parameters
        request_params = {id_key: ids}
        request_params.update(additional_params)

        prepared = prepare_api_parameters(request_params)

        # Make the API request using either parameters (GET) or body (POST)
        if use_params:
            response = self.client.command(operation, parameters=prepared)
        else:
            response = self.client.command(operation, body=prepared)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def _reorder_by_ids(
        self,
        ordered_ids: list[str],
        entities: list[dict[str, Any]],
        id_field: str,
    ) -> list[dict[str, Any]]:
        """Reorder hydrated entities to match the sorted ID order from the query step.

        Search tools query entity IDs first (honoring the requested sort) and then
        hydrate full details by ID. Some "get entities by IDs" endpoints return
        resources in arbitrary order, discarding the sort. This restores the order
        of ``ordered_ids``. It is a no-op for endpoints that already preserve order.

        Entities whose ID is not in ``ordered_ids`` are appended in their original
        order (never dropped); IDs with no matching entity are skipped.

        Args:
            ordered_ids: Entity IDs from the query step, in the desired order.
            entities: Hydrated entity dicts from the get-by-IDs step.
            id_field: The key inside each entity dict that holds its ID.

        Returns:
            The entities reordered to match ordered_ids.
        """
        by_id = {str(entity.get(id_field, "")): entity for entity in entities}

        result: list[dict[str, Any]] = []
        placed: set[str] = set()
        for entity_id in ordered_ids:
            key = str(entity_id)
            if key in by_id and key not in placed:
                result.append(by_id[key])
                placed.add(key)

        # Preserve entities not referenced by ordered_ids rather than dropping them
        result.extend(
            entity for entity in entities
            if str(entity.get(id_field, "")) not in placed
        )

        return result

    def _base_search_api_call(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str = "Search operation failed",
        default_result: Any = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
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
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
        error_message: str = "Query operation failed",
        default_result: Any = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
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
                body: dict[str, Any] = response.get("body", {})
                return body
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

    def _base_get_api_call(
        self,
        operation: str,
        api_params: dict[str, Any],
        error_message: str = "GET operation failed",
        decode_binary: bool = True,
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Standardized API call for GET operations with optional binary response handling.

        This method handles various GET operations that may return:
        - Standard JSON responses (handled by handle_api_response)
        - Binary responses that need UTF-8 decoding (like MITRE reports)

        Args:
            operation: The API operation name (e.g., "GetMitreReport", "GetReportPdf")
            api_params: Dictionary of API parameters
            error_message: Custom error message for failed operations
            decode_binary: Whether to decode binary responses as UTF-8 (default: True)

        Returns:
            - For successful operations with binary responses: decoded string content
            - For successful operations with JSON responses: standard API response
            - For failed operations: error dict
        """
        # Prepare parameters for the API request
        prepared_params = prepare_api_parameters(api_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        # Make the API request
        command_response = self.client.command(operation, parameters=prepared_params)

        # FalconPy returns raw bytes for binary download endpoints (e.g., GetMitreReport)
        if isinstance(command_response, bytes):
            if decode_binary:
                return command_response.decode('utf-8')
            return command_response

        # Dict response - check status code and use standard error handling
        status_code = command_response.get("status_code")

        if status_code != 200:
            return handle_api_response(
                command_response,
                operation=operation,
                error_message=error_message,
                default_result=[],
            )

        # Standard response handling for dict responses
        return handle_api_response(
            command_response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

    def _base_search_with_meta(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str = "Search operation failed",
    ) -> tuple[list[dict[str, Any]] | dict[str, Any], dict[str, Any] | None]:
        """Like _base_search_api_call but also returns the response's pagination metadata.

        Hydration (fetching full entity details by ID) discards `body.meta.pagination`
        from the query-step response, so callers that need `total`/`after` must capture
        it here, before calling `_base_get_by_ids`.

        Args:
            operation: The API operation name (e.g., "QueryDevicesByFilter")
            search_params: Dictionary of search parameters (filter, limit, offset, sort, etc.)
            error_message: Custom error message for failed operations

        Returns:
            Tuple of (resources or error dict, pagination dict or None)
        """
        prepared_params = prepare_api_parameters(search_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        response = self.client.command(operation, parameters=prepared_params)

        result = handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

        if self._is_error(result):
            return result, None

        pagination = self._extract_pagination(response)
        return result, pagination

    @staticmethod
    def _extract_pagination(response: dict[str, Any]) -> dict[str, Any] | None:
        """Pull `body.meta.pagination` out of a raw API response, if present."""
        return ((response.get("body") or {}).get("meta") or {}).get("pagination")

    def _build_pagination_envelope(
        self,
        results: list[dict[str, Any]],
        pagination: dict[str, Any] | None,
        filter_used: str | None = None,
    ) -> dict[str, Any]:
        """Assemble the standard search-tool response envelope.

        Args:
            results: The full entity details to return to the caller
            pagination: The raw `body.meta.pagination` dict from the API response, if any
            filter_used: The FQL filter string that was used, if applicable

        Returns:
            Dict with `results`, `pagination` (total/offset/limit/next), and
            optionally `filter_used`
        """
        pag: dict[str, Any] = {}
        if pagination:
            # `total` may be absent (some endpoints omit it) — report None rather
            # than inventing a count, so a caller can tell "unknown" from a real total.
            pag["total"] = pagination.get("total")
            if "offset" in pagination:
                pag["offset"] = pagination["offset"]
            if "limit" in pagination:
                pag["limit"] = pagination["limit"]
            pag["next"] = pagination.get("after") or None
        else:
            # No pagination metadata: the API gave us no count, so report None rather
            # than synthesizing one. A non-null `total` always means the API returned it.
            pag = {"total": None, "next": None}

        envelope: dict[str, Any] = {"results": results, "pagination": pag}
        if filter_used is not None:
            envelope["filter_used"] = filter_used
        return envelope

    def _is_error(self, response: Any) -> bool:
        return isinstance(response, dict) and "error" in response

    def _format_fql_error_response(
        self,
        errors: list[dict[str, Any]],
        filter_used: str | None,
        fql_documentation: str,
    ) -> dict[str, Any]:
        """Format response with FQL guide for API errors indicating filter problems.

        Use ONLY when the API returned an error (400+) that suggests the FQL
        filter syntax is incorrect. Do NOT use for empty results (200 with 0
        resources) — empty results use the standard pagination envelope, not
        this FQL-error shape.

        Args:
            errors: List containing the error dict from the API
            filter_used: The FQL filter string that was used (can be None)
            fql_documentation: Module-specific FQL documentation constant

        Returns:
            Dict with results, filter_used, fql_guide, and contextual hint
        """
        return {
            "results": errors,
            "filter_used": filter_used,
            "fql_guide": fql_documentation,
            "hint": "Filter error occurred. Review the FQL guide above to correct your query syntax.",
        }
