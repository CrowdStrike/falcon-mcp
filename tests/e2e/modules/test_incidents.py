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

    def test_crowd_score_default_parameters(self):
        """Verify the agent can retrieve CrowdScore with default parameters."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "CrowdScore",
                    "validator": lambda kwargs: kwargs.get('parameters', {}).get('limit') == 100,
                    "response": {
                        "status_code": 200, 
                        "body": [
                            {"id": "score-1", "score": 50, "adjusted_score": 60},
                            {"id": "score-2", "score": 70, "adjusted_score": 80},
                            {"id": "score-3", "score": 40, "adjusted_score": 50}
                        ]
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "What is our current CrowdScore?"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "show_crowd_score")
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


if __name__ == '__main__':
    unittest.main()
