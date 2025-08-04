"""
Common utility functions for Falcon MCP Server

This module provides common utility functions for the Falcon MCP server.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

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


def generate_md_table(data: List[Tuple]) -> str:
    """Generate a Markdown table from a list of tuples.

    This function creates a compact Markdown table with the provided data.
    It's designed to minimize token usage while maintaining readability.
    The first row of data is used as the header row.

    Args:
        data: List of tuples where the first tuple contains the headers
              and the remaining tuples contain the table data

    Returns:
        str: Formatted Markdown table as a string

    Raises:
        TypeError: If the first row (headers) contains non-string values
        TypeError: If there are not at least 2 items (header and a value row)
        ValueError: If the header row is empty
        ValueError: If a row has more items than headers
    """
    if not data or len(data) < 2:
        raise TypeError("Need at least 2 items. The header and a value row")

    # Extract headers from the first row
    headers = data[0]
    
    # Check that the header row is not empty
    if len(headers) == 0:
        raise ValueError("Header row cannot be empty")
    
    # Check that all headers are strings
    for header in headers:
        if not isinstance(header, str):
            raise TypeError(f"Header values must be strings, got {type(header).__name__}")

    # Use the remaining rows as data
    rows = data[1:]

    # Create the table header, stripping spaces from header values
    header_parts = []
    for h in headers:
        # Strip spaces from header values
        header_parts.append(str(h).strip())

    header_row = "|" + "|".join(header_parts) + "|"

    # Create the separator row with the exact expected format
    separator = "|-" * len(headers) + "|"

    # Build the table
    table = [header_row, separator]

    for idx, row in enumerate(rows):
        # Check if row has more items than headers
        if len(row) > len(headers):
            raise ValueError(f"Row {idx+1} has {len(row)} items, which is more than the {len(headers)} headers")

        # Convert row values to strings and handle special cases
        row_values = []
        for i, value in enumerate(row):
            if i < len(headers):
                if value is None:
                    row_values.append("")
                elif isinstance(value, bool):
                    row_values.append(str(value).lower())
                elif isinstance(value, (int, float)):
                    row_values.append(str(value))
                else:
                    # Process multi-line text to create a clean, single-line representation

                    text = str(value)
                    # Split text into lines, strip whitespace, and filter out empty lines
                    non_empty_lines = [line.strip() for line in text.split('\n') if line.strip()]
                    # Join the non-empty lines with a single space
                    formatted_text = " ".join(non_empty_lines).strip()
                    row_values.append(formatted_text)

        # Pad the row if it's shorter than headers
        while len(row_values) < len(headers):
            row_values.append("")

        # Add the row to the table
        table.append("|" + "|".join(row_values) + "|")

    return "\n".join(table)
