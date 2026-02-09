"""Integration tests for the NGSIEM module."""

from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest

from falcon_mcp.modules.ngsiem import NGSIEMModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestNGSIEMIntegration(BaseIntegrationTest):
    """Integration tests for NGSIEM module with real API calls.

    Validates:
    - Correct FalconPy operation names (StartSearchV1, GetSearchStatusV1)
    - Asynchronous search job workflow (start, poll, return events)
    - Parameter passing (repository, query_string, start, end)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the NGSIEM module with a real client."""
        self.module = NGSIEMModule(falcon_client)

    def test_search_ngsiem_returns_events(self):
        """Test that search_ngsiem returns an events list without errors.

        Runs a simple wildcard query over the last hour.
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        result = self.call_method(
            self.module.search_ngsiem,
            query_string="*",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        self.assert_no_error(result, context="search_ngsiem")

        # Result should be a list (events)
        assert isinstance(result, list), f"Expected list of events, got {type(result)}"

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names work against real API.

        If operation names are wrong, the API call will fail with an error.
        This test uses a short time range to execute quickly.
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        result = self.call_method(
            self.module.search_ngsiem,
            query_string="*",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        self.assert_no_error(result, context="StartSearchV1/GetSearchStatusV1 operation names")

    def test_search_ngsiem_invalid_cql_returns_error(self):
        """Test that an invalid CQL query returns an error response."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        # Intentionally malformed CQL - unclosed bracket
        result = self.call_method(
            self.module.search_ngsiem,
            query_string="[invalid_syntax",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        # API should return error dict, not raise exception
        assert isinstance(result, dict), f"Expected error dict, got {type(result)}"
        assert "error" in result, "Expected 'error' key in response for invalid CQL"

    def test_search_ngsiem_no_matches_returns_empty_list(self):
        """Test that a query with no matches returns an empty list."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=5)

        # Query for non-existent aid - should return empty, not error
        result = self.call_method(
            self.module.search_ngsiem,
            query_string="aid=nonexistent_aid_12345",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        self.assert_no_error(result, context="search with no matches")
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    def test_search_ngsiem_with_repository_parameter(self):
        """Test search with explicit repository parameter."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        result = self.call_method(
            self.module.search_ngsiem,
            query_string="*",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            repository="investigate_view",
        )

        # May return events or empty list depending on environment
        self.assert_no_error(result, context="search with investigate_view repository")
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    def test_search_ngsiem_invalid_repository_returns_error(self):
        """Test that an invalid repository value returns an error."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        result = self.call_method(
            self.module.search_ngsiem,
            query_string="*",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            repository="nonexistent_repo",
        )

        assert isinstance(result, dict), f"Expected error dict, got {type(result)}"
        assert "error" in result, "Expected 'error' key for invalid repository"

    def test_search_ngsiem_event_structure(self):
        """Test that returned events have expected structure when data exists."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        result = self.call_method(
            self.module.search_ngsiem,
            query_string="*",
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        self.assert_no_error(result, context="search_ngsiem event structure")
        assert isinstance(result, list), f"Expected list, got {type(result)}"

        # Only validate structure if events exist
        if len(result) > 0:
            first_event = result[0]
            assert isinstance(first_event, dict), f"Expected event dict, got {type(first_event)}"
            # Events should have at least a timestamp field
            assert "@timestamp" in first_event or "timestamp" in first_event, (
                f"Expected timestamp field in event. Available fields: {list(first_event.keys())}"
            )

    def test_search_ngsiem_special_characters_in_query(self):
        """Test that special characters in query are handled correctly."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        # Query with special characters
        result = self.call_method(
            self.module.search_ngsiem,
            query_string='#event_simpleName="ProcessRollup2"',
            start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        self.assert_no_error(result, context="search with special characters")
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    def test_search_ngsiem_timeout_returns_error(self):
        """Test that a search exceeding the timeout returns a timeout error.

        Uses a zero timeout to force immediate timeout condition.
        The module should return an error dict with timeout message.
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        # Patch the module constants to use zero timeout (immediate timeout)
        with (
            mock.patch("falcon_mcp.modules.ngsiem.TIMEOUT_SECONDS", 0),
            mock.patch("falcon_mcp.modules.ngsiem.POLL_INTERVAL_SECONDS", 1),
        ):
            result = self.call_method(
                self.module.search_ngsiem,
                query_string="*",
                start=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                end=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        # Should return error dict with timeout message
        assert isinstance(result, dict), f"Expected error dict, got {type(result)}"
        assert "error" in result, "Expected 'error' key for timeout"
        assert "timed out" in result["error"].lower(), (
            f"Expected timeout message, got: {result['error']}"
        )
