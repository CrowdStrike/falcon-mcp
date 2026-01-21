"""Integration tests for the Serverless module."""

import pytest

from falcon_mcp.modules.serverless import ServerlessModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestServerlessIntegration(BaseIntegrationTest):
    """Integration tests for Serverless module with real API calls.

    Validates:
    - Correct FalconPy operation name (GetCombinedVulnerabilitiesSARIF)
    - Combined query endpoint returns vulnerability data in SARIF format
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the serverless module with a real client."""
        self.module = ServerlessModule(falcon_client)

    def test_search_serverless_vulnerabilities_returns_data(self):
        """Test that search_serverless_vulnerabilities returns vulnerability data.

        Validates the GetCombinedVulnerabilitiesSARIF operation name is correct.
        Note: filter is required for this endpoint.
        """
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="cloud_provider:'aws'",
            limit=5,
        )

        self.assert_no_error(result, context="search_serverless_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_serverless_vulnerabilities")

    def test_search_serverless_vulnerabilities_with_severity_filter(self):
        """Test search_serverless_vulnerabilities with severity filter."""
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="severity:'HIGH'",
            limit=3,
        )

        self.assert_no_error(result, context="search_serverless_vulnerabilities with severity filter")
        self.assert_valid_list_response(result, min_length=0, context="search_serverless_vulnerabilities with severity filter")

    def test_search_serverless_vulnerabilities_with_sort(self):
        """Test search_serverless_vulnerabilities with sort parameter."""
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="cloud_provider:'aws'",
            sort="severity",
            limit=3,
        )

        self.assert_no_error(result, context="search_serverless_vulnerabilities with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_serverless_vulnerabilities with sort")

    def test_search_serverless_vulnerabilities_with_offset(self):
        """Test search_serverless_vulnerabilities with offset parameter."""
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="cloud_provider:'aws'",
            offset=0,
            limit=3,
        )

        self.assert_no_error(result, context="search_serverless_vulnerabilities with offset")
        self.assert_valid_list_response(result, min_length=0, context="search_serverless_vulnerabilities with offset")

    def test_search_serverless_vulnerabilities_response_structure(self):
        """Test that search_serverless_vulnerabilities returns SARIF-format data.

        SARIF (Static Analysis Results Interchange Format) typically has 'runs' field.
        """
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="cloud_provider:'aws'",
            limit=5,
        )

        self.assert_no_error(result, context="search_serverless_vulnerabilities structure")

        # Result should be a list (extracted from runs)
        assert isinstance(result, list), f"Expected list (from SARIF runs), got {type(result)}"

    def test_operation_name_is_correct(self):
        """Validate that FalconPy operation name is correct.

        If operation name is wrong, the API call will fail with an error.
        """
        result = self.call_method(
            self.module.search_serverless_vulnerabilities,
            filter="cloud_provider:'aws'",
            limit=1,
        )
        self.assert_no_error(result, context="GetCombinedVulnerabilitiesSARIF operation name")
