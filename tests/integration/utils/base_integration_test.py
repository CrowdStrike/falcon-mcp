"""Base class for integration tests with real API calls."""

import inspect
import warnings
from typing import Any, Callable, Dict, List, Optional

import pytest
from pydantic.fields import FieldInfo


def resolve_field_defaults(method: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve Pydantic Field defaults for method parameters.

    When calling module methods directly (not through FastMCP), Field()
    default values are not resolved automatically. This helper inspects
    the method signature and resolves any Field() defaults for parameters
    not explicitly provided.

    Args:
        method: The method to call
        kwargs: The keyword arguments provided

    Returns:
        Updated kwargs with Field defaults resolved
    """
    sig = inspect.signature(method)
    resolved_kwargs = dict(kwargs)

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Skip if already provided
        if param_name in resolved_kwargs:
            continue

        # Check if default is a Pydantic FieldInfo
        if isinstance(param.default, FieldInfo):
            resolved_kwargs[param_name] = param.default.default
        elif param.default is not inspect.Parameter.empty:
            resolved_kwargs[param_name] = param.default

    return resolved_kwargs


class BaseIntegrationTest:
    """Base class providing common assertions for integration tests.

    Integration tests validate that modules work correctly against the real
    CrowdStrike Falcon API, catching issues that mocked tests cannot detect:
    - Incorrect FalconPy operation names (typos)
    - HTTP method mismatches (POST body vs GET query parameters)
    - Two-step search patterns not returning full details
    - API response schema changes
    """

    def assert_no_error(
        self,
        result: Any,
        context: str = "",
    ) -> None:
        """Assert that the result is not an API error response.

        Args:
            result: The API response to check
            context: Optional context string for the error message
        """
        error_msg = f"API error{f' ({context})' if context else ''}: {result}"

        # Check for error dict format
        if isinstance(result, dict):
            assert "error" not in result, error_msg
            assert result.get("status_code", 200) < 400, error_msg

        # Check for list containing error dict
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict):
                assert "error" not in first_item, error_msg

    def assert_valid_list_response(
        self,
        result: Any,
        min_length: int = 0,
        context: str = "",
    ) -> None:
        """Assert that the result is a valid list response.

        Args:
            result: The API response to check
            min_length: Minimum expected length of the list
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""
        assert isinstance(result, list), f"Expected list response{ctx}, got {type(result)}"
        assert (
            len(result) >= min_length
        ), f"Expected at least {min_length} items{ctx}, got {len(result)}"

    def assert_search_returns_details(
        self,
        result: List[Dict[str, Any]],
        expected_fields: List[str],
        context: str = "",
    ) -> None:
        """Assert that search results contain full entity details, not just IDs.

        This validates the two-step search pattern:
        1. Search returns entity IDs
        2. Get details returns full entity objects

        Args:
            result: The search results to check
            expected_fields: List of field names expected in each result
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""

        assert isinstance(result, list), f"Expected list of results{ctx}"
        assert len(result) > 0, f"Expected at least one result to validate{ctx}"

        first_item = result[0]
        assert isinstance(first_item, dict), (
            f"Expected dict items (full details), got {type(first_item)}{ctx}. "
            "This may indicate the search is returning IDs only instead of full details."
        )

        for field in expected_fields:
            assert field in first_item, (
                f"Expected field '{field}' in result{ctx}. "
                f"Available fields: {list(first_item.keys())}"
            )

    def assert_result_has_id(
        self,
        result: List[Dict[str, Any]],
        id_field: str = "id",
        context: str = "",
    ) -> None:
        """Assert that each result item has an ID field.

        Args:
            result: The results to check
            id_field: The name of the ID field to check for
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""

        assert isinstance(result, list), f"Expected list of results{ctx}"

        for i, item in enumerate(result):
            assert isinstance(item, dict), f"Expected dict at index {i}{ctx}"
            assert id_field in item, f"Missing '{id_field}' field at index {i}{ctx}"

    def get_first_id(
        self,
        result: List[Dict[str, Any]],
        id_field: str = "id",
    ) -> Optional[str]:
        """Extract the first ID from a list of results.

        Args:
            result: The results to extract from
            id_field: The name of the ID field

        Returns:
            The first ID value, or None if not found
        """
        if not result or not isinstance(result, list):
            return None

        first_item = result[0]
        if isinstance(first_item, dict):
            return first_item.get(id_field)

        return None

    def call_method(self, method: Callable[..., Any], **kwargs: Any) -> Any:
        """Call a module method with resolved Pydantic Field defaults.

        When calling module methods directly (not through FastMCP), Field()
        default values are not resolved automatically. This helper ensures
        Field defaults are properly resolved before calling the method.

        Args:
            method: The module method to call
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The result of calling the method
        """
        resolved_kwargs = resolve_field_defaults(method, kwargs)
        return method(**resolved_kwargs)

    def skip_with_warning(self, reason: str, context: str = "") -> None:
        """Skip a test with a warning to make it visible in CI output.

        This method emits a warning before skipping to ensure skipped tests
        are visible in CI logs and test reports. Silent skips can mask issues
        where tests never actually run.

        Args:
            reason: The reason for skipping the test
            context: Optional context about the test being skipped
        """
        full_reason = f"{reason}" if not context else f"{reason} ({context})"
        warnings.warn(f"INTEGRATION TEST SKIPPED: {full_reason}", stacklevel=2)
        pytest.skip(full_reason)
