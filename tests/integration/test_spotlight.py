"""Integration tests for the Spotlight module."""

import pytest

from falcon_mcp.modules.spotlight import SpotlightModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSpotlightIntegration(BaseIntegrationTest):
    """Integration tests for Spotlight module with real API calls.

    Validates:
    - Correct FalconPy operation name (combinedQueryVulnerabilities)
    - Combined query endpoint returns full vulnerability details
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the spotlight module with a real client."""
        self.module = SpotlightModule(falcon_client)

    def test_search_vulnerabilities_returns_details(self):
        """Test that search_vulnerabilities returns full vulnerability details.

        Validates the combinedQueryVulnerabilities operation name is correct.
        """
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            limit=5,
        )

        self.assert_no_error(result, context="search_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_vulnerabilities")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "status"],
                context="search_vulnerabilities",
            )

    def test_search_vulnerabilities_with_filter(self):
        """Test search_vulnerabilities with FQL filter."""
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            limit=3,
        )

        self.assert_no_error(result, context="search_vulnerabilities with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_vulnerabilities with filter")

    def test_search_vulnerabilities_with_sort(self):
        """Test search_vulnerabilities with sort parameter."""
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            sort="created_timestamp|desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_vulnerabilities with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_vulnerabilities with sort")

    def test_search_vulnerabilities_with_facet(self):
        """Test search_vulnerabilities with facet parameter for additional details."""
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            facet="cve",
            limit=3,
        )

        self.assert_no_error(result, context="search_vulnerabilities with facet")
        self.assert_valid_list_response(result, min_length=0, context="search_vulnerabilities with facet")

    def test_operation_name_is_correct(self):
        """Validate that FalconPy operation name is correct.

        If operation name is wrong, the API call will fail with an error.
        """
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            limit=1,
        )
        self.assert_no_error(result, context="combinedQueryVulnerabilities operation name")
