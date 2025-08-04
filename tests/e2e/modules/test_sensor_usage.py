"""
E2E tests for the Sensor Usage module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest, ensure_dict


@pytest.mark.e2e
class TestSensorUsageModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Sensor Usage Module.
    """

    def test_search_sensor_usage(self):
        """Verify the agent can show sensor usage for a specific event_date"""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetSensorUsageWeekly",
                    "validator": lambda kwargs: "event_date:'2025-08-02'" in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "containers": 42.5,
                                    "public_cloud_with_containers": 42,
                                    "public_cloud_without_containers": 42.75,
                                    "servers_with_containers": 42.25,
                                    "servers_without_containers": 42.75,
                                    "workstations": 42.75,
                                    "mobile": 42.75,
                                    "lumos": 42.25,
                                    "chrome_os": 0,
                                    "date": "2025-08-02"
                                }
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Show me sensor usage on 2025-08-02"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            self.assertIn("falcon_search_sensor_usage_fql_guide", tool_names_called)
            self.assertIn("falcon_search_sensor_usage", tool_names_called)

            used_tool = tools[len(tools) - 1]

            # Verify the tool input contains the filter parameter with proper FQL syntax
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("filter", tool_input, "Tool input should contain a 'filter' parameter")
            self.assertIn("event_date:'2025-08-02", tool_input.get("filter", ""), "Filter should contain event_date:'2025-08-02' in FQL syntax")

            # # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertIn("event_date:'2025-08-02'", api_call_params.get("filter", ""))

        self.run_test_with_retries(
            "test_search_sensor_usage", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
