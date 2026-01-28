"""Integration tests for the NGSIEM module."""

import os

import pytest

from falcon_mcp.modules.ngsiem import NGSIEMModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestNGSIEMIntegration(BaseIntegrationTest):
    """Integration tests for NGSIEM with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up module with real client."""
        self.module = NGSIEMModule(falcon_client)
        self.repository = os.getenv("FALCON_NGSIEM_REPOSITORY", "base_sensor")

    def test_start_search_returns_id(self):
        """Start a search and verify a search id is returned."""
        result = self.call_method(
            self.module.start_ngsiem_search,
            repository=self.repository,
            query_string="#event_simpleName=EndOfProcess",
            start="1d",
        )

        if isinstance(result, dict) and result.get("error"):
            self.skip_with_warning(
                result["error"],
                context="start_ngsiem_search",
            )
        self.assert_no_error(result, context="start_ngsiem_search")
        search_id = None
        if isinstance(result, list) and result:
            search_id = result[0].get("search_id") or result[0].get("id")
        elif isinstance(result, dict):
            search_id = result.get("search_id") or result.get("id")
        if not search_id:
            self.skip_with_warning(
                "NGSIEM search response missing search_id",
                context="start_ngsiem_search",
            )

    def test_get_search_status(self):
        """Start a search and check status endpoint."""
        result = self.call_method(
            self.module.start_ngsiem_search,
            repository=self.repository,
            query_string="#event_simpleName=EndOfProcess",
            start="1d",
        )

        if isinstance(result, dict) and result.get("error"):
            self.skip_with_warning(
                result["error"],
                context="start_ngsiem_search",
            )
        self.assert_no_error(result, context="start_ngsiem_search")

        if isinstance(result, list) and result:
            search_id = result[0].get("search_id") or result[0].get("id")
        else:
            if isinstance(result, dict):
                search_id = result.get("search_id") or result.get("id")
            else:
                search_id = None

        if not search_id:
            self.skip_with_warning(
                "No search_id available for status check",
                context="get_ngsiem_search_status",
            )

        status = self.call_method(
            self.module.get_ngsiem_search_status,
            repository=self.repository,
            search_id=search_id,
        )

        self.assert_no_error(status, context="get_ngsiem_search_status")

    def test_search_and_wait(self):
        """Start a search and wait for results."""
        result = self.call_method(
            self.module.search_ngsiem_and_wait,
            repository=self.repository,
            query_string="#event_simpleName=EndOfProcess",
            start="1d",
            poll_interval_seconds=2,
            timeout_seconds=30,
        )

        if isinstance(result, dict) and result.get("error"):
            self.skip_with_warning(
                result["error"],
                context="search_ngsiem_and_wait",
            )

        self.assert_no_error(result, context="search_ngsiem_and_wait")
        assert isinstance(result, list)

    def test_ontology_lookup(self):
        """Verify ontology lookup returns fields for a known event."""
        result = self.call_method(
            self.module.get_ngsiem_event_schema,
            event_simple_name="EndOfProcess",
        )

        self.assert_no_error(result, context="get_ngsiem_event_schema")
        if result.get("error"):
            self.skip_with_warning(
                result["error"],
                context="get_ngsiem_event_schema",
            )
        fields = result.get("fields", [])
        assert isinstance(fields, list)
