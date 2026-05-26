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
    - Read-only count path works with a valid quarantine FQL filter
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Quarantine module with a real client."""
        self.module = QuarantineModule(falcon_client)

    def test_search_quarantined_files_returns_details(self):
        """Test that quarantine search returns full quarantine details."""
        result = self.call_method(self.module.search_quarantined_files, limit=5)

        self.assert_no_error(result, context="search_quarantined_files")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_quarantined_files",
            )
        if isinstance(result, list) and len(result) > 0:
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
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_quarantined_files with sort",
            )

    def test_preview_quarantine_actions_with_filter(self):
        """Test the read-only quarantine action count with a valid FQL filter."""
        result = self.call_method(
            self.module.preview_quarantine_actions,
            filter="state:'quarantined'",
        )

        self.assert_no_error(result, context="preview_quarantine_actions")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="preview_quarantine_actions",
        )
        if result:
            assert isinstance(result[0], dict), (
                "Expected dict payload from preview_quarantine_actions"
            )
            assert "buckets" in result[0], (
                "Expected buckets in preview_quarantine_actions response"
            )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        search_quarantined_files exercises both QueryQuarantineFiles and
        GetQuarantineFiles via the two-step search pattern.
        """
        result = self.call_method(self.module.search_quarantined_files, limit=1)
        self.assert_no_error(result, context="QueryQuarantineFiles + GetQuarantineFiles operation names")
