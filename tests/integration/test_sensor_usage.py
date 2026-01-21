"""Integration tests for the Sensor Usage module."""

import pytest

from falcon_mcp.modules.sensor_usage import SensorUsageModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSensorUsageIntegration(BaseIntegrationTest):
    """Integration tests for Sensor Usage module with real API calls.

    Validates:
    - Correct FalconPy operation name (GetSensorUsageWeekly)
    - API response returns sensor usage data
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the sensor usage module with a real client."""
        self.module = SensorUsageModule(falcon_client)

    def test_search_sensor_usage_returns_data(self):
        """Test that search_sensor_usage returns usage data.

        Validates the GetSensorUsageWeekly operation name is correct.
        """
        result = self.call_method(self.module.search_sensor_usage)

        self.assert_no_error(result, context="search_sensor_usage")
        self.assert_valid_list_response(result, min_length=0, context="search_sensor_usage")

    def test_search_sensor_usage_with_filter(self):
        """Test search_sensor_usage with FQL filter."""
        result = self.call_method(
            self.module.search_sensor_usage,
            filter="period:'30'",
        )

        self.assert_no_error(result, context="search_sensor_usage with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_sensor_usage with filter")

    def test_search_sensor_usage_response_structure(self):
        """Test that search_sensor_usage returns expected data structure."""
        result = self.call_method(self.module.search_sensor_usage)

        self.assert_no_error(result, context="search_sensor_usage structure")

        if len(result) > 0:
            # Check for expected fields in sensor usage data
            first_item = result[0]
            assert isinstance(first_item, dict), f"Expected dict items, got {type(first_item)}"

    def test_operation_name_is_correct(self):
        """Validate that FalconPy operation name is correct.

        If operation name is wrong, the API call will fail with an error.
        """
        result = self.call_method(self.module.search_sensor_usage)
        self.assert_no_error(result, context="GetSensorUsageWeekly operation name")
