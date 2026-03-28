"""Integration tests for the Quarantine module."""

import pytest

from falcon_mcp.modules.quarantine import QuarantineModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestQuarantineIntegration(BaseIntegrationTest):
    """Integration tests for the Quarantine module with real API calls.

    Validates:
    - Correct FalconPy operation names for quarantine search and detail lookups
    - Two-step search pattern returns full quarantine details, not just IDs
    - Read-only preview path works with a valid quarantine filter
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Quarantine module with a real client."""
        self.module = QuarantineModule(falcon_client)

    def test_search_quarantined_files_returns_details(self):
        """Test that quarantine search returns full quarantine details."""
        result = self.call_method(self.module.search_quarantined_files, limit=5)

        self.assert_no_error(result, context="search_quarantined_files")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_quarantined_files",
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "sha256", "hostname"],
                context="search_quarantined_files",
            )

    def test_search_quarantined_files_with_sort(self):
        """Test quarantine search with a supported sort expression."""
        result = self.call_method(
            self.module.search_quarantined_files,
            sort="date_updated|desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_quarantined_files with sort")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_quarantined_files with sort",
        )

    def test_get_quarantined_file_details_with_valid_id(self):
        """Test quarantine detail lookup using a valid file ID."""
        search_result = self.call_method(self.module.search_quarantined_files, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No quarantined files available to test get_quarantined_file_details",
                context="test_get_quarantined_file_details_with_valid_id",
            )

        quarantine_id = self.get_first_id(search_result)
        if not quarantine_id:
            self.skip_with_warning(
                "Could not extract quarantine ID from search results",
                context="test_get_quarantined_file_details_with_valid_id",
            )

        result = self.call_method(self.module.get_quarantined_file_details, ids=[quarantine_id])

        self.assert_no_error(result, context="get_quarantined_file_details")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_quarantined_file_details",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "sha256", "hostname"],
            context="get_quarantined_file_details",
        )

    def test_preview_quarantine_action_counts_with_valid_filter(self):
        """Test the read-only quarantine action preview against a real ID filter."""
        search_result = self.call_method(self.module.search_quarantined_files, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No quarantined files available to test preview_quarantine_action_counts",
                context="test_preview_quarantine_action_counts_with_valid_filter",
            )

        quarantine_id = self.get_first_id(search_result)
        if not quarantine_id:
            self.skip_with_warning(
                "Could not extract quarantine ID from search results",
                context="test_preview_quarantine_action_counts_with_valid_filter",
            )

        result = self.call_method(
            self.module.preview_quarantine_action_counts,
            filter=f"id:'{quarantine_id}'",
        )

        self.assert_no_error(result, context="preview_quarantine_action_counts")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="preview_quarantine_action_counts",
        )
        assert isinstance(result[0], dict), "Expected dict bucket payload from preview_quarantine_action_counts"
        assert "buckets" in result[0], "Expected buckets in preview_quarantine_action_counts response"
