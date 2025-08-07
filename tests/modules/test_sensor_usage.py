"""
Tests for the Sensor Usage module.
"""

import unittest

from falcon_mcp.modules.sensor_usage import SensorUsageModule
from tests.modules.utils.test_modules import TestModules


class TestSensorUsageModule(TestModules):
    """Test cases for the Sensor Usage module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SensorUsageModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_sensor_usage",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_sensor_usage_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_sensor_usage_success(self):
        """Test searching sensor usage with successful response."""
        # Setup mock response with sample sensor usage data
        mock_response = {
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
        }
        self.mock_client.command.return_value = mock_response

        # Call search_sensor_usage with test parameters
        result = self.module.search_sensor_usage(filter="event_date:'2025-08-02'")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetSensorUsageWeekly",
            parameters={
                "filter": "event_date:'2025-08-02'",
            },
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date"], "2025-08-02")
        self.assertEqual(result[0]["containers"], 42.5)
        self.assertEqual(result[0]["workstations"], 42.75)
        self.assertEqual(result[0]["mobile"], 42.75)

    def test_search_sensor_usage_no_filter(self):
        """Test searching sensor usage with no filter parameter."""
        # Setup mock response with sample sensor usage data
        mock_response = {
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
        }
        self.mock_client.command.return_value = mock_response

        # Call search_sensor_usage with no filter
        result = self.module.search_sensor_usage()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSensorUsageWeekly")

        # Verify result contains expected values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date"], "2025-08-02")

    def test_search_sensor_usage_empty_response(self):
        """Test searching sensor usage with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call search_sensor_usage
        result = self.module.search_sensor_usage(filter="event_date:'2025-08-02'")

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSensorUsageWeekly")

        # Verify result is an empty list
        self.assertEqual(result, [])

    def test_search_sensor_usage_error(self):
        """Test searching sensor usage with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid query"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_sensor_usage
        results = self.module.search_sensor_usage(filter="invalid query")
        result = results[0]

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(result["error"].startswith("Failed to search sensor usage"))


if __name__ == "__main__":
    unittest.main()
