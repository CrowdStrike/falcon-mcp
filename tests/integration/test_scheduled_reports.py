"""Integration tests for the Scheduled Reports module."""

import pytest

from falcon_mcp.modules.scheduled_reports import ScheduledReportsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestScheduledReportsIntegration(BaseIntegrationTest):
    """Integration tests for Scheduled Reports module with real API calls.

    Validates:
    - Correct FalconPy operation names (scheduled_reports_query, scheduled_reports_get,
      report_executions_query, report_executions_get)
    - Two-step search pattern returns full details, not just IDs
    - GET with params usage for get_by_ids (use_params=True)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the scheduled reports module with a real client."""
        self.module = ScheduledReportsModule(falcon_client)

    def test_search_scheduled_reports_returns_details(self):
        """Test that search_scheduled_reports returns full report details.

        This validates the two-step search pattern:
        1. scheduled_reports_query returns report IDs
        2. scheduled_reports_get returns full details (using GET with params)
        """
        result = self.call_method(self.module.search_scheduled_reports, limit=5)

        self.assert_no_error(result, context="search_scheduled_reports")
        self.assert_valid_list_response(result, min_length=0, context="search_scheduled_reports")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "type"],
                context="search_scheduled_reports",
            )

    def test_search_scheduled_reports_with_filter(self):
        """Test search_scheduled_reports with FQL filter."""
        result = self.call_method(
            self.module.search_scheduled_reports,
            filter="status:'ACTIVE'",
            limit=3,
        )

        self.assert_no_error(result, context="search_scheduled_reports with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_scheduled_reports with filter")

    def test_search_scheduled_reports_with_sort(self):
        """Test search_scheduled_reports with sort parameter."""
        result = self.call_method(
            self.module.search_scheduled_reports,
            sort="created_on.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_scheduled_reports with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_scheduled_reports with sort")

    def test_search_scheduled_reports_with_free_text(self):
        """Test search_scheduled_reports with free-text search."""
        result = self.call_method(
            self.module.search_scheduled_reports,
            q="report",
            limit=5,
        )

        self.assert_no_error(result, context="search_scheduled_reports with q param")
        self.assert_valid_list_response(result, min_length=0, context="search_scheduled_reports with q param")

    def test_search_report_executions_returns_details(self):
        """Test that search_report_executions returns full execution details.

        This validates the two-step search pattern:
        1. report_executions_query returns execution IDs
        2. report_executions_get returns full details (using GET with params)
        """
        result = self.call_method(self.module.search_report_executions, limit=5)

        self.assert_no_error(result, context="search_report_executions")
        self.assert_valid_list_response(result, min_length=0, context="search_report_executions")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "status"],
                context="search_report_executions",
            )

    def test_search_report_executions_with_filter(self):
        """Test search_report_executions with FQL filter."""
        result = self.call_method(
            self.module.search_report_executions,
            filter="status:'DONE'",
            limit=3,
        )

        self.assert_no_error(result, context="search_report_executions with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_report_executions with filter")

    def test_search_report_executions_with_sort(self):
        """Test search_report_executions with sort parameter."""
        result = self.call_method(
            self.module.search_report_executions,
            sort="created_on.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_report_executions with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_report_executions with sort")

    def test_download_csv_format_execution(self):
        """Test download_report_execution with a CSV format execution.

        CSV format executions return raw bytes that are decoded to string.
        Most scheduled reports use CSV format by default.
        """
        # Search for completed executions - prefer CSV format (most common)
        search_result = self.call_method(
            self.module.search_report_executions,
            filter="status:'DONE'",
            limit=20,
            sort="created_on.desc",
        )

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No completed executions available",
                context="test_download_csv_format_execution",
            )

        # Find an execution with results that uses CSV format
        # Look for executions where report_params.format is 'csv' (or not json/pdf)
        execution_id = None
        execution_type = None
        report_format = None
        for execution in search_result:
            result_count = execution.get("result_metadata", {}).get("result_count", 0)
            fmt = execution.get("report_params", {}).get("format", "csv")
            if result_count > 0 and fmt == "csv":
                execution_id = execution.get("id")
                execution_type = execution.get("type")
                report_format = fmt
                break

        if not execution_id:
            self.skip_with_warning(
                "No CSV format executions with results found",
                context="test_download_csv_format_execution",
            )

        print(f"\nDownloading CSV format execution: {execution_id} (type={execution_type}, format={report_format})")

        # Download that execution
        result = self.call_method(self.module.download_report_execution, id=execution_id)

        print(f"Result type: {type(result)}")
        if isinstance(result, str):
            print(f"String content (first 200 chars): {result[:200]}")

        # CSV format should return a decoded string
        if isinstance(result, dict) and "error" in result:
            pytest.fail(f"Download failed with error: {result.get('error')}")

        assert isinstance(result, str), f"Expected string for CSV format, got {type(result)}"
        assert len(result) > 0, "Expected non-empty CSV content"

    def test_download_json_format_execution(self):
        """Test download_report_execution with a JSON format execution.

        JSON format executions return dict with body.resources containing results.
        These are typically scheduled searches (type=event_search).
        """
        # Search for completed executions with JSON format
        search_result = self.call_method(
            self.module.search_report_executions,
            filter="status:'DONE'",
            limit=30,
            sort="created_on.desc",
        )

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No completed executions available",
                context="test_download_json_format_execution",
            )

        # Find an execution with results that uses JSON format
        execution_id = None
        execution_type = None
        report_format = None
        for execution in search_result:
            result_count = execution.get("result_metadata", {}).get("result_count", 0)
            fmt = execution.get("report_params", {}).get("format", "csv")
            if result_count > 0 and fmt == "json":
                execution_id = execution.get("id")
                execution_type = execution.get("type")
                report_format = fmt
                break

        if not execution_id:
            self.skip_with_warning(
                "No JSON format executions with results found",
                context="test_download_json_format_execution",
            )

        print(f"\nDownloading JSON format execution: {execution_id} (type={execution_type}, format={report_format})")

        # Download that execution
        result = self.call_method(self.module.download_report_execution, id=execution_id)

        print(f"Result type: {type(result)}")
        if isinstance(result, list) and len(result) > 0:
            print(f"First result keys: {result[0].keys() if isinstance(result[0], dict) else 'N/A'}")
            print(f"Result count: {len(result)}")

        # JSON format should return a list of resources
        if isinstance(result, dict) and "error" in result:
            pytest.fail(f"Download failed with error: {result.get('error')}")

        assert isinstance(result, list), f"Expected list for JSON format, got {type(result)}"
        assert len(result) > 0, "Expected non-empty results list"

        # Verify each result is a dict
        for item in result[:3]:
            assert isinstance(item, dict), f"Expected dict item, got {type(item)}"

    def test_download_pdf_format_execution_returns_error(self):
        """Test download_report_execution with a PDF format execution returns error.

        PDF format is not supported for LLM consumption. The implementation
        should detect PDF bytes and return an error recommending CSV/JSON format.
        """
        # Search for completed executions with PDF format
        search_result = self.call_method(
            self.module.search_report_executions,
            filter="status:'DONE'",
            limit=100,
            sort="created_on.desc",
        )

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No completed executions available",
                context="test_download_pdf_format_execution_returns_error",
            )

        # Find an execution with results that uses PDF format
        execution_id = None
        execution_type = None
        report_format = None
        for execution in search_result:
            result_count = execution.get("result_metadata", {}).get("result_count", 0)
            fmt = execution.get("report_params", {}).get("format", "csv")
            if result_count > 0 and fmt == "pdf":
                execution_id = execution.get("id")
                execution_type = execution.get("type")
                report_format = fmt
                break

        if not execution_id:
            self.skip_with_warning(
                "No PDF format executions with results found",
                context="test_download_pdf_format_execution_returns_error",
            )

        print(f"\nDownloading PDF format execution: {execution_id} (type={execution_type}, format={report_format})")

        # Download that execution - should return error
        result = self.call_method(self.module.download_report_execution, id=execution_id)

        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Dict content: {result}")

        # PDF format should return an error dict
        assert isinstance(result, dict), f"Expected error dict for PDF format, got {type(result)}"
        assert "error" in result, "Expected error key in result"
        assert "PDF format not supported" in result["error"], f"Unexpected error message: {result['error']}"

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test scheduled_reports_query and scheduled_reports_get (via search)
        result = self.call_method(self.module.search_scheduled_reports, limit=1)
        self.assert_no_error(result, context="scheduled_reports_query/get operation names")

        # Test report_executions_query and report_executions_get (via search)
        result = self.call_method(self.module.search_report_executions, limit=1)
        self.assert_no_error(result, context="report_executions_query/get operation names")
