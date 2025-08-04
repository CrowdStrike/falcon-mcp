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


if __name__ == "__main__":
    unittest.main()
