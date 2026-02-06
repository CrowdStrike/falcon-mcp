"""Integration tests for the NGSIEM module."""

from datetime import datetime, timedelta, timezone

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
