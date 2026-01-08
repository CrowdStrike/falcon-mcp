"""
E2E tests for the NGSIEM module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest, ensure_dict


@pytest.mark.e2e
class TestNGSIEMModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server NGSIEM Module.
    """

    def test_execute_simple_query(self):
        """Verify the agent can execute a simple NGSIEM query."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        "#event_simpleName=ProcessRollup2" in kwargs.get("body", {}).get("queryString", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "search-123"}
                    },
                },
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: kwargs.get("id") == "search-123",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "done": True,
                            "events": [
                                {
                                    "event": "ProcessRollup2",
                                    "ComputerName": "WIN-TEST01",
                                    "UserName": "testuser",
                                    "CommandLine": "notepad.exe",
                                    "timestamp": "2024-01-01T12:00:00Z"
                                },
                                {
                                    "event": "ProcessRollup2",
                                    "ComputerName": "WIN-TEST02",
                                    "UserName": "admin",
                                    "CommandLine": "powershell.exe",
                                    "timestamp": "2024-01-01T12:05:00Z"
                                }
                            ]
                        }
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Execute this NGSIEM query: #event_simpleName=ProcessRollup2 | tail(2)"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_execute_ngsiem_query")

            # Verify the tool input contains the query
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("ProcessRollup2", tool_input.get("query", ""))

            # Verify StartSearchV1 API call was made
            start_search_calls = [
                call for call in self._mock_api_instance.command.call_args_list
                if call[0][0] == "StartSearchV1"
            ]
            self.assertGreaterEqual(len(start_search_calls), 1, "Expected StartSearchV1 API call")

            # Verify GetSearchStatusV1 API call was made
            status_calls = [
                call for call in self._mock_api_instance.command.call_args_list
                if call[0][0] == "GetSearchStatusV1"
            ]
            self.assertGreaterEqual(len(status_calls), 1, "Expected GetSearchStatusV1 API call")

            # Verify result contains search results
            self.assertIn("ProcessRollup2", result)
            self.assertIn("WIN-TEST01", result)
            self.assertIn("notepad.exe", result)

        self.run_test_with_retries(
            "test_execute_simple_query", test_logic, assertions
        )

    def test_execute_query_with_time_range(self):
        """Verify the agent can execute a query with a specific time range."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        "#event_simpleName=ProcessRollup2" in kwargs.get("body", {}).get("queryString", "") and
                        "15m" in kwargs.get("body", {}).get("start", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "search-456"}
                    },
                },
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: kwargs.get("id") == "search-456",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "done": True,
                            "events": [
                                {
                                    "event": "ProcessRollup2",
                                    "ComputerName": "WIN-PROD01",
                                    "UserName": "svcaccount",
                                    "CommandLine": "svchost.exe",
                                    "timestamp": "2024-01-01T11:45:00Z"
                                }
                            ]
                        }
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Execute this NGSIEM query for the last 15 minutes: #event_simpleName=ProcessRollup2"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_execute_ngsiem_query")

            # Verify the tool input contains the query and time range
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("ProcessRollup2", tool_input.get("query", ""))
            self.assertIn("15m", tool_input.get("time_range", ""))

            # Verify API calls were made
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                2,  # StartSearchV1 and GetSearchStatusV1
                "Expected at least 2 API calls"
            )

            # Verify result contains search results
            self.assertIn("ProcessRollup2", result)
            self.assertIn("WIN-PROD01", result)
            self.assertIn("svchost.exe", result)

        self.run_test_with_retries(
            "test_execute_query_with_time_range", test_logic, assertions
        )

    def test_execute_query_with_different_repository(self):
        """Verify the agent can execute a query in a specific repository."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        kwargs.get("repository") == "detections" and
                        "#event_simpleName=DetectionSummaryEvent" in kwargs.get("body", {}).get("queryString", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "search-789"}
                    },
                },
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: (
                        kwargs.get("id") == "search-789" and
                        kwargs.get("repository") == "detections"
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "done": True,
                            "events": [
                                {
                                    "event": "DetectionSummaryEvent",
                                    "DetectName": "Suspicious PowerShell Activity",
                                    "Severity": "Medium",
                                    "ComputerName": "WIN-WS01",
                                    "timestamp": "2024-01-01T10:30:00Z"
                                }
                            ]
                        }
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Execute this NGSIEM query in the detections repository: #event_simpleName=DetectionSummaryEvent"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_execute_ngsiem_query")

            # Verify the tool input contains the query and repository
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("DetectionSummaryEvent", tool_input.get("query", ""))
            self.assertEqual("detections", tool_input.get("repository", ""))

            # Verify result contains detection information
            self.assertIn("DetectionSummaryEvent", result)
            self.assertIn("Suspicious PowerShell Activity", result)
            self.assertIn("WIN-WS01", result)

        self.run_test_with_retries(
            "test_execute_query_with_different_repository", test_logic, assertions
        )

    def test_long_running_query_status_feedback(self):
        """Verify the agent handles long-running queries with status feedback."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        "#event_simpleName=ProcessRollup2" in kwargs.get("body", {}).get("queryString", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "search-long-running"}
                    },
                },
                # First few status checks return not done
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: kwargs.get("id") == "search-long-running",
                    "response": {
                        "status_code": 200,
                        "body": {"done": False}
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Execute this complex NGSIEM query: #event_simpleName=ProcessRollup2 | eval hours=strftime(\"%H\", @timestamp) | stats count by hours"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_execute_ngsiem_query")

            # For long-running queries, we expect status feedback rather than full results
            # The result should indicate the query is still running
            self.assertTrue(
                any(phrase in result.lower() for phrase in [
                    "processing", "running", "complex query", "large result", "wait"
                ]),
                f"Expected status feedback in result: {result}"
            )

        self.run_test_with_retries(
            "test_long_running_query_status_feedback", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()