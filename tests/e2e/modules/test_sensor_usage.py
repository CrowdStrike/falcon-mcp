"""
E2E tests for the Sensor Usage module.
"""

import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestSensorUsageModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Sensor Usage Module.
    """

    def test_get_weekly_sensor_usage(self):
        """Verify the agent can retrieve weekly sensor usage data."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetSensorUsageWeekly",
                    "validator": lambda kwargs: "event_date"
                    in kwargs.get("parameters", {}).get("filter", ""),
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
                                },
                                {
                                    "containers": 41,
                                    "public_cloud_with_containers": 41.25,
                                    "public_cloud_without_containers": 41.5,
                                    "servers_with_containers": 41.75,
                                    "servers_without_containers": 41.5,
                                    "workstations": 41.75,
                                    "mobile": 41.5,
                                    "lumos": 41.25,
                                    "chrome_os": 0,
                                    "date": "2025-08-01"
                                },
                                {
                                    "containers": 40,
                                    "public_cloud_with_containers": 40,
                                    "public_cloud_without_containers": 40.5,
                                    "servers_with_containers": 40,
                                    "servers_without_containers": 40.75,
                                    "workstations": 40.75,
                                    "mobile": 40,
                                    "lumos": 40.25,
                                    "chrome_os": 0,
                                    "date": "2025-07-31"
                                },
                                {
                                    "containers": 39,
                                    "public_cloud_with_containers": 39.5,
                                    "public_cloud_without_containers": 39.5,
                                    "servers_with_containers": 39.5,
                                    "servers_without_containers": 39,
                                    "workstations": 39.5,
                                    "mobile": 39.5,
                                    "lumos": 39.25,
                                    "chrome_os": 0,
                                    "date": "2025-07-30"
                                },
                                {
                                    "containers": 38,
                                    "public_cloud_with_containers": 38,
                                    "public_cloud_without_containers": 38,
                                    "servers_with_containers": 38,
                                    "servers_without_containers": 38,
                                    "workstations": 38.75,
                                    "mobile": 38,
                                    "lumos": 38.25,
                                    "chrome_os": 0,
                                    "date": "2025-07-29"
                                },
                                {
                                    "containers": 37,
                                    "public_cloud_with_containers": 37.25,
                                    "public_cloud_without_containers": 37,
                                    "servers_with_containers": 37,
                                    "servers_without_containers": 37.75,
                                    "workstations": 37.25,
                                    "mobile": 37.25,
                                    "lumos": 37,
                                    "chrome_os": 0,
                                    "date": "2025-07-28"
                                },
                                {
                                    "containers": 36,
                                    "public_cloud_with_containers": 36.75,
                                    "public_cloud_without_containers": 36.75,
                                    "servers_with_containers": 36.5,
                                    "servers_without_containers": 36.75,
                                    "workstations": 36.5,
                                    "mobile": 36,
                                    "lumos": 36.75,
                                    "chrome_os": 0,
                                    "date": "2025-07-27"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Show me the weekly sensor usage data for the past week"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_sensor_usage")

            # Check for event_date in filter
            tool_input = used_tool["input"]["tool_input"]
            filter_str = tool_input.get("filter", "")
            self.assertIn("event_date", filter_str)

            # Verify sensor usage data is in the output
            self.assertIn("2025-08-02", used_tool["output"])
            self.assertIn("containers", used_tool["output"].lower())
            self.assertIn("workstations", used_tool["output"].lower())

            # Verify API call was made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (GetSensorUsageWeekly)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertIn("event_date", api_call_params.get("filter", ""))

            # Verify result contains expected information
            self.assertIn("2025-08-02", result)
            self.assertIn("containers", result.lower())
            self.assertIn("workstations", result.lower())

        self.run_test_with_retries("test_get_weekly_sensor_usage", test_logic, assertions)


if __name__ == "__main__":
    unittest.main()
