"""
Common utility functions for Falcon MCP Server

This module provides common utility functions for the Falcon MCP server.
"""

import re
from typing import Any, Dict, List, Optional

from .errors import _format_error_response, is_success_response
from .logging import get_logger

logger = get_logger(__name__)


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from a dictionary.

    Args:
        data: Dictionary to filter

    Returns:
        Dict[str, Any]: Filtered dictionary
    """
    return {k: v for k, v in data.items() if v is not None}


def prepare_api_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare parameters for Falcon API requests.

    Args:
        params: Raw parameters

    Returns:
        Dict[str, Any]: Prepared parameters
    """
    # Remove None values
    filtered = filter_none_values(params)

    # Handle special parameter formatting if needed
    if "filter" in filtered and isinstance(filtered["filter"], dict):
        # Convert filter dict to FQL string if needed
        pass

    return filtered


def extract_resources(
    response: Dict[str, Any],
    default: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Extract resources from an API response.

    Args:
        response: API response dictionary
        default: Default value if no resources are found

    Returns:
        List[Dict[str, Any]]: Extracted resources
    """
    if not is_success_response(response):
        return default if default is not None else []

    resources = response.get("body", {}).get("resources", [])
    return resources if resources else (default if default is not None else [])


def extract_first_resource(
    response: Dict[str, Any],
    operation: str,
    not_found_error: str = "Resource not found",
) -> Dict[str, Any]:
    """Extract the first resource from an API response.

    Args:
        response: API response dictionary
        operation: The API operation that was performed
        not_found_error: Error message if no resources are found

    Returns:
        Dict[str, Any]: First resource or error response
    """
    resources = extract_resources(response)

    if not resources:
        return _format_error_response(not_found_error, operation=operation)

    return resources[0]


def sanitize_input(input_str: str) -> str:
    """Sanitize input string.

    Args:
        input_str: Input string to sanitize

    Returns:
        Sanitized string with dangerous characters removed
    """
    if not isinstance(input_str, str):
        return str(input_str)

    # Remove backslashes, quotes, and control characters that could be used for injection
    sanitized = re.sub(r'[\\"\'\n\r\t]', "", input_str)

    # Additional safety: limit length to prevent excessively long inputs
    return sanitized[:255]
