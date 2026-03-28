"""Integration tests for the Sandbox module."""

import pytest

from falcon_mcp.modules.sandbox import SandboxModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSandboxIntegration(BaseIntegrationTest):
    """Integration tests for the Sandbox module with real API calls.

    Validates:
    - Correct FalconPy operation names for sample checks and report lookups
    - Two-step search patterns return full submission and report details
    - GET-with-params detail retrieval for Sandbox entities
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Sandbox module with a real client."""
        self.module = SandboxModule(falcon_client)

    def test_check_sandbox_samples_returns_list(self):
        """Test checking sandbox sample availability with a harmless fake SHA."""
        result = self.call_method(
            self.module.check_sandbox_samples,
            sha256s=["0" * 64],
        )

        self.assert_no_error(result, context="check_sandbox_samples")
        self.assert_valid_list_response(result, min_length=0, context="check_sandbox_samples")

    def test_search_sandbox_submissions_returns_details(self):
        """Test that sandbox submission search returns full submission details."""
        result = self.call_method(self.module.search_sandbox_submissions, limit=5)

        self.assert_no_error(result, context="search_sandbox_submissions")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_sandbox_submissions",
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "state", "sandbox"],
                context="search_sandbox_submissions",
            )

    def test_get_sandbox_submission_details_with_valid_id(self):
        """Test sandbox submission detail lookup using a valid submission ID."""
        search_result = self.call_method(self.module.search_sandbox_submissions, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No sandbox submissions available to test get_sandbox_submission_details",
                context="test_get_sandbox_submission_details_with_valid_id",
            )

        submission_id = self.get_first_id(search_result)
        if not submission_id:
            self.skip_with_warning(
                "Could not extract sandbox submission ID from search results",
                context="test_get_sandbox_submission_details_with_valid_id",
            )

        result = self.call_method(self.module.get_sandbox_submission_details, ids=[submission_id])

        self.assert_no_error(result, context="get_sandbox_submission_details")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_sandbox_submission_details",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "state", "sandbox"],
            context="get_sandbox_submission_details",
        )

    def test_search_sandbox_reports_returns_details(self):
        """Test that sandbox report search returns summary report details."""
        result = self.call_method(self.module.search_sandbox_reports, limit=5)

        self.assert_no_error(result, context="search_sandbox_reports")
        self.assert_valid_list_response(result, min_length=0, context="search_sandbox_reports")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "verdict", "sandbox"],
                context="search_sandbox_reports",
            )

    def test_get_sandbox_report_summaries_with_valid_id(self):
        """Test sandbox report summary lookup using a valid report ID."""
        search_result = self.call_method(self.module.search_sandbox_reports, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No sandbox reports available to test get_sandbox_report_summaries",
                context="test_get_sandbox_report_summaries_with_valid_id",
            )

        report_id = self.get_first_id(search_result)
        if not report_id:
            self.skip_with_warning(
                "Could not extract sandbox report ID from search results",
                context="test_get_sandbox_report_summaries_with_valid_id",
            )

        result = self.call_method(self.module.get_sandbox_report_summaries, ids=[report_id])

        self.assert_no_error(result, context="get_sandbox_report_summaries")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_sandbox_report_summaries",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "verdict", "sandbox"],
            context="get_sandbox_report_summaries",
        )
