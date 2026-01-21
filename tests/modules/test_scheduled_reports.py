"""
Tests for the Scheduled Reports module.
"""

import unittest

from falcon_mcp.modules.scheduled_reports import ScheduledReportsModule
from tests.modules.utils.test_modules import TestModules


class TestScheduledReportsModule(TestModules):
    """Test cases for the Scheduled Reports module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ScheduledReportsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_scheduled_reports",
            "falcon_launch_scheduled_report",
            "falcon_search_report_executions",
            "falcon_download_report_execution",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_scheduled_reports_fql_guide",
            "falcon_search_report_executions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_scheduled_reports_success(self):
        """Test searching scheduled reports with successful response."""
        # Setup mock responses: first for query (returns IDs), then for get (returns details)
        query_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    "report-id-1",
                    "report-id-2",
                ]
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "report-id-1",
                        "name": "Weekly Host Report",
                        "status": "ACTIVE",
                    },
                    {
                        "id": "report-id-2",
                        "name": "Daily Vulnerability Scan",
                        "status": "ACTIVE",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        # Call search_scheduled_reports with test parameters
        result = self.module.search_scheduled_reports(
            filter="status:'ACTIVE'",
            limit=100,
            offset=0,
            sort="created_on.desc",
            q="test",
        )

        # Verify client command was called twice (query then get)
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Verify first call was the query
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "scheduled_reports_query")
        self.assertEqual(
            first_call[1]["parameters"],
            {
                "filter": "status:'ACTIVE'",
                "limit": 100,
                "offset": 0,
                "sort": "created_on.desc",
                "q": "test",
            },
        )

        # Verify second call was the get with IDs (uses parameters for GET request)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "scheduled_reports_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], ["report-id-1", "report-id-2"]
        )

        # Verify result contains full details
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "report-id-1")
        self.assertEqual(result[0]["name"], "Weekly Host Report")
        self.assertEqual(result[1]["id"], "report-id-2")
        self.assertEqual(result[1]["name"], "Daily Vulnerability Scan")

    def test_search_scheduled_reports_empty(self):
        """Test searching scheduled reports with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call search_scheduled_reports
        result = self.module.search_scheduled_reports()

        # Verify result is empty list
        self.assertEqual(result, [])

    def test_search_scheduled_reports_error(self):
        """Test searching scheduled reports with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_scheduled_reports
        result = self.module.search_scheduled_reports(filter="invalid")

        # Verify result contains error (wrapped in list for consistent return type)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertTrue(result[0]["error"].startswith("Failed to search for scheduled reports"))

    def test_launch_scheduled_report_success(self):
        """Test launching scheduled report with successful response."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "execution-id-1",
                        "scheduled_report_id": "report-id-1",
                        "status": "PENDING",
                    }
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call launch_scheduled_report
        result = self.module.launch_scheduled_report(id="report-id-1")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "scheduled_reports_launch",
            body={"id": "report-id-1"},
        )

        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "execution-id-1")
        self.assertEqual(result[0]["status"], "PENDING")

    def test_search_report_executions_success(self):
        """Test searching report executions with successful response."""
        # Setup mock responses: first for query (returns IDs), then for get (returns details)
        query_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    "execution-id-1",
                    "execution-id-2",
                ]
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "execution-id-1",
                        "scheduled_report_id": "report-id-1",
                        "status": "DONE",
                    },
                    {
                        "id": "execution-id-2",
                        "scheduled_report_id": "report-id-2",
                        "status": "PENDING",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        # Call search_report_executions
        result = self.module.search_report_executions(
            filter="status:'DONE'",
            limit=50,
            offset=10,
            sort="created_on.desc",
        )

        # Verify client command was called twice (query then get)
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Verify first call was the query
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "report_executions_query")
        self.assertEqual(
            first_call[1]["parameters"],
            {
                "filter": "status:'DONE'",
                "limit": 50,
                "offset": 10,
                "sort": "created_on.desc",
            },
        )

        # Verify second call was the get with IDs (uses parameters for GET request)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "report_executions_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], ["execution-id-1", "execution-id-2"]
        )

        # Verify result contains full details
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "execution-id-1")
        self.assertEqual(result[0]["status"], "DONE")

    def test_download_report_execution_csv_format(self):
        """Test downloading CSV format report returns decoded string content.

        When the scheduled report is configured with format=csv,
        FalconPy returns raw bytes containing CSV data.
        """
        # Setup mock response - raw CSV bytes
        mock_response = b"@timestamp,@timestamp.nanos,text\n1.768962407987e+12,0,sntest\n"
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="execution-id-1")

        # Verify client command was called with 'ids' parameter
        self.mock_client.command.assert_called_once_with(
            "report_executions_download_get",
            parameters={"ids": "execution-id-1"},
        )

        # Verify result is the decoded string content
        self.assertIsInstance(result, str)
        self.assertIn("@timestamp", result)
        self.assertIn("sntest", result)

    def test_download_report_execution_json_format(self):
        """Test downloading JSON format report returns list of resources.

        When the scheduled report is configured with format=json,
        FalconPy returns a dict with body.resources containing the results.
        """
        # Setup mock response - dict with resources (JSON format)
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"event_id": "1", "hostname": "host1", "severity": "high"},
                    {"event_id": "2", "hostname": "host2", "severity": "medium"},
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="execution-id-1")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "report_executions_download_get",
            parameters={"ids": "execution-id-1"},
        )

        # Verify result is a list of resources
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["event_id"], "1")
        self.assertEqual(result[1]["hostname"], "host2")

    def test_download_report_execution_pdf_format_returns_error(self):
        """Test downloading PDF format report returns error.

        PDF format is not supported for LLM consumption. When FalconPy returns
        bytes starting with %PDF magic bytes, return an error message.
        """
        # Setup mock response - PDF bytes (starts with %PDF)
        mock_response = b"%PDF-1.4\n%more binary content here..."
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="execution-id-1")

        # Verify result is an error dict
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("PDF format not supported", result["error"])
        self.assertIn("CSV or JSON format", result["error"])

    def test_download_report_execution_api_error(self):
        """Test downloading report execution with API error."""
        # Setup mock response with error (execution not ready)
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Execution not complete"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="execution-id-1")

        # Verify result contains error
        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Failed to download report execution"))

    # Security validation tests

    def test_search_scheduled_reports_with_special_characters_in_filter(self):
        """Test that special characters in filter are passed through safely."""
        # Setup mock response
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Test with filter containing special characters (FQL syntax)
        filter_with_special = "status:'ACTIVE'+type:'event_search'"
        self.module.search_scheduled_reports(filter=filter_with_special)

        # Verify the filter was passed through unchanged
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_launch_scheduled_report_with_invalid_id(self):
        """Test launching report with invalid ID returns error from API."""
        # Setup mock response with 404 error
        mock_response = {
            "status_code": 404,
            "body": {"errors": [{"message": "Scheduled report not found"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call with invalid ID
        result = self.module.launch_scheduled_report(id="nonexistent-id")

        # Verify error is returned (wrapped in list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_report_executions_error(self):
        """Test searching report executions with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter syntax"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_report_executions
        result = self.module.search_report_executions(filter="invalid[syntax")

        # Verify error is returned (wrapped in list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertTrue(result[0]["error"].startswith("Failed to search for report executions"))

    def test_download_report_execution_not_complete(self):
        """Test downloading report when execution is not complete (PENDING status)."""
        # Setup mock response for trying to download a PENDING execution
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Cannot download report: execution status is PENDING"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="pending-execution-id")

        # Verify error is returned
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to download report execution", result["error"])

    def test_download_report_execution_json_empty_resources(self):
        """Test downloading JSON format report with empty resources."""
        # Setup mock response - dict with empty resources (JSON format with no results)
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call download_report_execution
        result = self.module.download_report_execution(id="execution-id-1")

        # Verify result is an empty list
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
