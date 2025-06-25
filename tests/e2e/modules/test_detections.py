"""
E2E tests for the Detections module.
"""
import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestDetectionsModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Detections Module.
    """

    def test_get_top_3_high_severity_detections(self):
        """Verify the agent can retrieve the top 3 high-severity detections."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDetects",
                    "validator": lambda kwargs: "high" in kwargs.get('parameters', {}).get('filter', '').lower() or "max_severity:5" in kwargs.get('parameters', {}).get('filter', '').lower(),
                    "response": {"status_code": 200, "body": {"resources": ["detection-1", "detection-2", "detection-3"]}}
                },
                {
                    "operation": "GetDetectSummaries",
                    "validator": lambda kwargs: "detection-1" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {"id": "detection-1", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                                {"id": "detection-2", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                                {"id": "detection-3", "status": "new", "severity": "high", "description": "A test detection for E2E."}
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Give me the details of the top 3 high severity detections, return only detection id and descriptions"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_detections")
            self.assertIn("high", json.dumps(used_tool['input']['tool_input']).lower())
            self.assertIn("detection-1", used_tool['output'])
            self.assertIn("detection-2", used_tool['output'])
            self.assertIn("detection-3", used_tool['output'])

            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("high", api_call_1_params.get('filter').lower())
            self.assertEqual(api_call_1_params.get('limit'), 3)
            self.assertIn('max_severity.desc', api_call_1_params.get('sort', ''))
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-1", "detection-2", "detection-3"])

            self.assertIn("detection-1", result)
            self.assertIn("detection-2", result)
            self.assertIn("detection-3", result)

        self.run_test_with_retries(
            "test_get_top_3_high_severity_detections",
            test_logic,
            assertions
        )

    def test_get_highest_detection_for_ip(self):
        """Verify the agent can find the highest-severity detection for a specific IP."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDetects",
                    "validator": lambda kwargs: "10.0.0.1" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {"status_code": 200, "body": {"resources": ["detection-4"]}}
                },
                {
                    "operation": "GetDetectSummaries",
                    "validator": lambda kwargs: "detection-4" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [{
                                "id": "detection-4",
                                "status": "new",
                                "severity": "critical",
                                "description": "A critical detection on a specific IP."
                            }]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "What is the highest detection for the device with local_ip 10.0.0.1? Return the detection id as well"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, f"Expected 1 tool call, but got {len(tools)}")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_detections")
            self.assertIn("10.0.0.1", json.dumps(used_tool['input']['tool_input']))
            self.assertIn("detection-4", used_tool['output'])

            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("10.0.0.1", api_call_1_params.get('filter'))
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-4"])

            self.assertIn("detection-4", result)
            self.assertNotIn("detection-1", result)

        self.run_test_with_retries(
            "test_get_highest_detection_for_ip",
            test_logic,
            assertions
        )

if __name__ == '__main__':
    unittest.main()
