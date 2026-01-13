"""
E2E tests for the Scheduled Reports module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestScheduledReportsModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Scheduled Reports Module.
    """

    def test_query_active_scheduled_reports(self):
        """Verify the agent can query for active scheduled reports."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "scheduled_reports_query",
                    "validator": lambda kwargs: "ACTIVE"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                "report-id-001",
                                "report-id-002",
                            ]
                        },
                    },
                },
                {
                    "operation": "scheduled_reports_get",
                    "validator": lambda kwargs: True,
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "report-id-001",
                                    "name": "Weekly Host Report",
                                    "description": "Weekly summary of host activity",
                                    "status": "ACTIVE",
                                    "type": "hosts",
                                    "user_id": "admin@company.com",
                                    "created_on": "2024-01-01T00:00:00Z",
                                    "next_execution_on": "2024-01-22T08:00:00Z",
                                    "schedule": {
                                        "definition": "0 8 * * 1",
                                        "display": "Every Monday at 8:00 AM",
                                    },
                                    "last_execution": {
                                        "id": "exec-001",
                                        "status": "DONE",
                                        "last_updated_on": "2024-01-15T08:05:00Z",
                                    },
                                },
                                {
                                    "id": "report-id-002",
                                    "name": "Daily Vulnerability Scan",
                                    "description": "Daily spotlight vulnerabilities report",
                                    "status": "ACTIVE",
                                    "type": "spotlight_vulnerabilities",
                                    "user_id": "security@company.com",
                                    "created_on": "2024-01-05T00:00:00Z",
                                    "next_execution_on": "2024-01-21T06:00:00Z",
                                    "schedule": {
                                        "definition": "0 6 * * *",
                                        "display": "Daily at 6:00 AM",
                                    },
                                    "last_execution": {
                                        "id": "exec-002",
                                        "status": "DONE",
                                        "last_updated_on": "2024-01-20T06:03:00Z",
                                    },
                                },
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Show me all active scheduled reports and their details"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Check that query tool was called
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertTrue(
                any("scheduled_reports" in name for name in tool_names),
                f"Expected scheduled reports tool to be called, got: {tool_names}",
            )

            # Verify API calls were made
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )

            # Verify result contains expected report information
            self.assertIn("Weekly Host Report", result)
            self.assertIn("Daily Vulnerability Scan", result)
            self.assertIn("ACTIVE", result)

        self.run_test_with_retries(
            "test_query_active_scheduled_reports", test_logic, assertions
        )

    def test_query_scheduled_searches(self):
        """Verify the agent can query for scheduled searches (event_search type)."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "scheduled_reports_query",
                    "validator": lambda kwargs: "event_search"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                "search-id-001",
                            ]
                        },
                    },
                },
                {
                    "operation": "scheduled_reports_get",
                    "validator": lambda kwargs: True,
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "search-id-001",
                                    "name": "Suspicious Process Search",
                                    "description": "Search for suspicious process executions",
                                    "status": "ACTIVE",
                                    "type": "event_search",
                                    "user_id": "analyst@company.com",
                                    "created_on": "2024-01-10T00:00:00Z",
                                    "next_execution_on": "2024-01-21T12:00:00Z",
                                    "schedule": {
                                        "definition": "0 */4 * * *",
                                        "display": "Every 4 hours",
                                    },
                                    "last_execution": {
                                        "id": "exec-search-001",
                                        "status": "DONE",
                                        "last_updated_on": "2024-01-20T16:02:00Z",
                                        "result_metadata": {
                                            "result_count": 15,
                                            "execution_duration": 3500,
                                        },
                                    },
                                },
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Search for all scheduled searches in the system"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Verify result contains scheduled search information
            self.assertIn("Suspicious Process Search", result)
            self.assertIn("event_search", result.lower())

        self.run_test_with_retries(
            "test_query_scheduled_searches", test_logic, assertions
        )

    def test_query_report_executions(self):
        """Verify the agent can query for report executions."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "report_executions_query",
                    "validator": lambda kwargs: True,
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                "exec-001",
                                "exec-002",
                            ]
                        },
                    },
                },
                {
                    "operation": "report_executions_get",
                    "validator": lambda kwargs: True,
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "exec-001",
                                    "scheduled_report_id": "report-id-001",
                                    "status": "DONE",
                                    "type": "hosts",
                                    "created_on": "2024-01-20T08:00:00Z",
                                    "last_updated_on": "2024-01-20T08:05:00Z",
                                    "expiration_on": "2024-02-19T08:05:00Z",
                                    "result_metadata": {
                                        "result_count": 150,
                                        "execution_duration": 5000,
                                        "report_file_name": "weekly_host_report_20240120.csv",
                                    },
                                },
                                {
                                    "id": "exec-002",
                                    "scheduled_report_id": "report-id-002",
                                    "status": "FAILED",
                                    "type": "spotlight_vulnerabilities",
                                    "created_on": "2024-01-20T06:00:00Z",
                                    "last_updated_on": "2024-01-20T06:10:00Z",
                                    "status_msg": "Timeout while processing data",
                                },
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Show me recent report executions and their status"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Check that execution query tool was called
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertTrue(
                any("execution" in name.lower() for name in tool_names),
                f"Expected report execution tool to be called, got: {tool_names}",
            )

            # Verify result contains execution information
            self.assertIn("DONE", result)
            # Check for either FAILED status or timeout message
            self.assertTrue(
                "FAILED" in result or "Timeout" in result,
                "Expected FAILED status or timeout message in result",
            )

        self.run_test_with_retries(
            "test_query_report_executions", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
