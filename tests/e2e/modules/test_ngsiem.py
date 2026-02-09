"""
E2E tests for the NGSIEM module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestNGSIEMModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server NGSIEM Module.
    """

    def test_search_ngsiem_with_user_provided_query(self):
        """Verify the agent passes user-provided CQL query without modification."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        kwargs.get("repository") == "search-all"
                        and kwargs.get("body", {}).get("queryString")
                        == "#event_simpleName=ProcessRollup2"
                        and "start" in kwargs.get("body", {})
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "job-12345"},
                    },
                },
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: kwargs.get("search_id") == "job-12345",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "done": True,
                            "events": [
                                {
                                    "aid": "agent-001",
                                    "event_simpleName": "ProcessRollup2",
                                    "CommandLine": "powershell.exe -enc ...",
                                    "timestamp": "2025-02-05T10:00:00Z",
                                },
                                {
                                    "aid": "agent-002",
                                    "event_simpleName": "ProcessRollup2",
                                    "CommandLine": "cmd.exe /c whoami",
                                    "timestamp": "2025-02-05T09:30:00Z",
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = (
                "Search NGSIEM for events using this CQL query: #event_simpleName=ProcessRollup2 "
                "from the last 24 hours"
            )
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Validate tool was called
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertIn(
                "falcon_search_ngsiem",
                tool_names,
                f"Expected falcon_search_ngsiem in tool calls. Got: {tool_names}",
            )

            # Find StartSearchV1 call
            start_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "StartSearchV1":
                    start_call = call
                    break

            self.assertIsNotNone(start_call, "Expected StartSearchV1 API call")

            # Validate CQL query passed exactly as user provided
            body = start_call[1].get("body", {})
            self.assertEqual(
                body.get("queryString"),
                "#event_simpleName=ProcessRollup2",
                "CQL query should be passed exactly as user provided",
            )

            # Validate timestamps are in epoch milliseconds
            self.assertIn("start", body, "Expected start timestamp in body")
            self.assertIsInstance(body["start"], int, "Start should be epoch milliseconds")

            # Validate events in result
            self.assertIn("ProcessRollup2", result, "Expected event data in result")

        self.run_test_with_retries(
            "test_search_ngsiem_with_user_provided_query",
            test_logic,
            assertions,
        )

    def test_search_ngsiem_with_specific_repository(self):
        """Verify the agent uses the correct repository when specified."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "StartSearchV1",
                    "validator": lambda kwargs: (
                        kwargs.get("repository") == "third-party"
                        and kwargs.get("body", {}).get("queryString") == "source=firewall"
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"id": "job-67890"},
                    },
                },
                {
                    "operation": "GetSearchStatusV1",
                    "validator": lambda kwargs: kwargs.get("search_id") == "job-67890",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "done": True,
                            "events": [
                                {
                                    "source": "firewall",
                                    "action": "blocked",
                                    "src_ip": "192.168.1.100",
                                    "dst_ip": "10.0.0.1",
                                    "timestamp": "2025-02-05T08:00:00Z",
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = (
                "Search the third-party repository in NGSIEM using this CQL query: source=firewall "
                "for events from yesterday"
            )
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Validate tool was called
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertIn(
                "falcon_search_ngsiem",
                tool_names,
                f"Expected falcon_search_ngsiem in tool calls. Got: {tool_names}",
            )

            # Find StartSearchV1 call with third-party repository
            start_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "StartSearchV1":
                    if call[1].get("repository") == "third-party":
                        start_call = call
                        break

            self.assertIsNotNone(
                start_call, "Expected StartSearchV1 call with third-party repository"
            )

            # Validate repository parameter
            self.assertEqual(
                start_call[1].get("repository"),
                "third-party",
                "Expected third-party repository",
            )

            # Validate CQL query
            body = start_call[1].get("body", {})
            self.assertEqual(
                body.get("queryString"),
                "source=firewall",
                "CQL query should match user-provided query",
            )

            # Validate result contains firewall event
            self.assertIn("firewall", result, "Expected firewall event in result")

        self.run_test_with_retries(
            "test_search_ngsiem_with_specific_repository",
            test_logic,
            assertions,
        )


if __name__ == "__main__":
    unittest.main()
