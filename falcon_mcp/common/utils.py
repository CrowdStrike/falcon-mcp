"""
Common utility functions for Falcon MCP Server

This module provides common utility functions for the Falcon MCP server.
"""

import re
from typing import Any, Optional

from .errors import _format_error_response, is_success_response
from .logging import get_logger

logger = get_logger(__name__)


def unwrap_field_default(value: Any) -> Any:
    """Resolve a Pydantic FieldInfo object to its actual default value."""
    return value.default if hasattr(value, "default") else value


def filter_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from a dictionary.

    Args:
        data: Dictionary to filter

    Returns:
        Dict[str, Any]: Filtered dictionary
    """
    return {k: v for k, v in data.items() if v is not None}


def filter_fields(record: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Keep only listed fields from a record.
    Supports dot notation for nested extraction:
    'device.hostname' extracts {"device": {"hostname": value}}.
    Unknown fields are silently ignored.
    """
    result: dict[str, Any] = {}
    for field in fields:
        parts = field.split(".")
        source = record
        valid = True
        for part in parts:
            if isinstance(source, dict) and part in source:
                source = source[part]
            else:
                valid = False
                break
        if not valid:
            continue
        target = result
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = source
    return result


def filter_records(records: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    """Apply filter_fields to each record in a list."""
    return [filter_fields(record, fields) for record in records]


def truncate_string_fields(record: dict[str, Any], max_length: int) -> dict[str, Any]:
    """Truncate string values exceeding max_length, preserving non-string types.
    Appends ' [truncated, full_len=N]' marker to truncated values.
    Recurses into nested dicts.
    """
    result: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, str) and len(value) > max_length:
            result[key] = value[:max_length] + f" [truncated, full_len={len(value)}]"
        elif isinstance(value, dict):
            result[key] = truncate_string_fields(value, max_length)
        else:
            result[key] = value
    return result


def format_response(
    results: list[dict[str, Any]] | dict[str, Any], fmt: str
) -> list[dict[str, Any]] | dict[str, Any] | str:
    """Apply output format to results.
    Returns original data for 'json'. For 'toon', converts lists with 2+ records
    to TOON encoding; single records and non-lists pass through unchanged.
    """
    if fmt == "toon" and isinstance(results, list) and len(results) > 1:
        from toon_format import encode
        return encode(results)
    return results


def prepare_api_parameters(params: dict[str, Any]) -> dict[str, Any]:
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
    response: dict[str, Any],
    default: Optional[list[dict[str, Any]]] = None,
) -> list[dict[str, Any]]:
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
    response: dict[str, Any],
    operation: str,
    not_found_error: str = "Resource not found",
) -> dict[str, Any]:
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


def generate_md_table(data: list[tuple]) -> str:
    """Generate a Markdown table from a list of tuples.

    This function creates a compact Markdown table with the provided data.
    It's designed to minimize token usage while maintaining readability.
    The first tuple contains headers, remaining tuples contain data rows.

    Args:
        data: List of tuples where the first tuple contains the headers
              and the remaining tuples contain the table data

    Returns:
        str: Formatted Markdown table as a string

    Raises:
        TypeError: If the first row (headers) contains non-string values
        TypeError: If there are not at least 2 items (header and a value row)
        ValueError: If the header row is empty
    """
    # Basic validation
    if not data or len(data) < 2:
        raise TypeError("Need at least 2 items. The header and a value row")

    # Extract and validate headers
    headers = data[0]
    if len(headers) == 0:
        raise ValueError("Header row cannot be empty")

    # Validate header types and clean them
    clean_headers = []
    for header in headers:
        if not isinstance(header, str):
            raise TypeError(f"Header values must be strings, got {type(header).__name__}")
        clean_headers.append(header.strip())

    # Build table structure
    lines = [
        "|" + "|".join(clean_headers) + "|",
        "|" + "|".join(["-"] * len(clean_headers)) + "|"
    ]

    # Process data rows
    for row in data[1:]:
        # Convert values to strings with consistent formatting
        row_values = []
        for value in row[:len(clean_headers)]:  # Truncate to header count
            if value is None:
                row_values.append("")
            elif isinstance(value, bool):
                row_values.append(str(value).lower())
            elif isinstance(value, (int, float)):
                row_values.append(str(value))
            else:
                # Handle multi-line strings by collapsing to single line
                text = str(value)
                clean_text = " ".join(line.strip() for line in text.split('\n') if line.strip())
                row_values.append(clean_text)

        # Pad row to match header count
        while len(row_values) < len(clean_headers):
            row_values.append("")

        lines.append("|" + "|".join(row_values) + "|")

    return "\n".join(lines)
