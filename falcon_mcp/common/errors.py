"""
Error handling utilities for Falcon MCP Server

This module provides error handling utilities for the Falcon MCP server.
"""

from typing import Any, Dict, Optional

from .api_scopes import get_required_scopes
from .logging import get_logger

logger = get_logger(__name__)

# Common error codes and their meanings
ERROR_CODE_DESCRIPTIONS = {
    403: "Permission denied. The API credentials don't have the required access.",
    401: "Authentication failed. The API credentials are invalid or expired.",
    404: "Resource not found. The requested resource does not exist.",
    429: "Rate limit exceeded. Too many requests in a short period.",
    500: "Server error. An unexpected error occurred on the server.",
    503: "Service unavailable. The service is temporarily unavailable.",
}


class FalconError(Exception):
    """Base exception for all Falcon MCP server errors."""


class AuthenticationError(FalconError):
    """Raised when authentication with the Falcon API fails."""


class APIError(FalconError):
    """Raised when a Falcon API request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        body: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
    ):
        self.status_code = status_code
        self.body = body
        self.operation = operation
        super().__init__(message)


def is_success_response(response: Dict[str, Any]) -> bool:
    """Check if an API response indicates success.

    Args:
        response: The API response dictionary

    Returns:
        bool: True if the response indicates success (status code 200)
    """
    return response.get("status_code") == 200


def _format_error_response(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    operation: Optional[str] = None,
) -> Dict[str, Any]:
    """Format an error as a standardized response.

    Args:
        message: The error message
        details: Additional error details
        operation: The API operation that failed (used for permission errors)

    Returns:
        Dict[str, Any]: Formatted error response
    """
    response: Dict[str, Any] = {"error": message}

    # Add details if provided
    if details:
        response["details"] = details

        # Special handling for permission errors (403)
        if details.get("status_code") == 403 and operation:
            required_scopes = get_required_scopes(operation)
            if required_scopes:
                response["required_scopes"] = required_scopes
                scopes_list = ", ".join(required_scopes)
                response["resolution"] = (
                    f"This operation requires the following API scopes: {scopes_list}. "
                    "Please ensure your API client has been granted these scopes in the "
                    "CrowdStrike Falcon console."
                )

    # Log the error
    logger.error("Error: %s", message)

    return response


def handle_api_response(
    response: Dict[str, Any],
    operation: str,
    error_message: str = "API request failed",
    default_result: Any = None,
) -> Dict[str, Any] | Any:
    """Handle an API response, returning either the result or an error.

    Args:
        response: The API response dictionary
        operation: The API operation that was performed
        error_message: The error message to use if the request failed
        default_result: The default result to return if the response is empty

    Returns:
        Dict[str, Any]|Any: The result or an error response
    """
    status_code = response.get("status_code")

    # If no status_code is present, assume success (200) for responses with data
    # This handles cases like NGSIEM query results that don't include status_code
    if status_code is None:
        # Check if response contains actual data (successful response)
        if any(key in response for key in ["results", "search_id", "body", "resources"]):
            status_code = 200
        else:
            # Empty response without status_code - treat as error
            status_code = 500

    if status_code != 200:
        # Get a more descriptive error message based on status code
        status_message = ERROR_CODE_DESCRIPTIONS.get(
            status_code, f"Request failed with status code {status_code}"
        )

        # For permission errors, add more context
        if status_code == 403:
            required_scopes = get_required_scopes(operation)
            if required_scopes:
                status_message += f" Required scopes: {', '.join(required_scopes)}"

        # Log the error
        logger.error("Error: %s: %s", error_message, status_message)

        return _format_error_response(
            f"{error_message}: {status_message}", details=response, operation=operation
        )

    # Handle NGSIEM query responses - they have different structure than standard API responses
    if ("search_id" in response and "results" in response) or (operation and "NG-SIEM Query" in operation):
        return response

    # Extract resources from the response body for standard API responses
    resources = response.get("body", {}).get("resources", [])

    if not resources and default_result is not None:
        return default_result

    # For standard API responses, return resources list/dict as expected
    return resources
