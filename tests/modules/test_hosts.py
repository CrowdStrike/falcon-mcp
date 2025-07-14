"""
Tests for the Hosts module.
"""
import unittest

from falcon_mcp.modules.hosts import HostsModule
from tests.modules.utils.test_modules import TestModules


class TestHostsModule(TestModules):
    """Test cases for the Hosts module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(HostsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_hosts",
            "falcon_get_host_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_search_hosts(self):
        """Test searching for hosts."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["device1", "device2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": []  # Empty resources for PostDeviceDetailsV2
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'", limit=50)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to QueryDevicesByFilter with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryDevicesByFilter")
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Windows'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.mock_client.command.assert_any_call(
            "PostDeviceDetailsV2",
            body={"ids": ["device1", "device2"]}
        )

        # Verify result
        self.assertEqual(result, [])  # Empty list because PostDeviceDetailsV2 returned empty resources

    def test_search_hosts_with_details(self):
        """Test searching for hosts with details."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["device1", "device2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"},
                    {"device_id": "device2", "hostname": "TEST-HOST-2", "platform_name": "Linux"}
                ]
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'", limit=50)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to QueryDevicesByFilter with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryDevicesByFilter")
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Windows'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.mock_client.command.assert_any_call(
            "PostDeviceDetailsV2",
            body={"ids": ["device1", "device2"]}
        )

        # Verify result
        expected_result = [
            {"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"},
            {"device_id": "device2", "hostname": "TEST-HOST-2", "platform_name": "Linux"}
        ]
        self.assertEqual(result, expected_result)

    def test_search_hosts_error(self):
        """Test searching for hosts with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid filter"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="invalid_filter")

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("details", result[0])

    def test_search_hosts_no_results(self):
        """Test searching for hosts with no results."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="hostname:'NONEXISTENT'")

        # Verify result is empty list
        self.assertEqual(result, [])
        # Only one API call should be made (QueryDevicesByFilter)
        self.assertEqual(self.mock_client.command.call_count, 1)


    def test_search_hosts_with_all_parameters(self):
        """Test searching for hosts with all parameters."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_hosts with all parameters
        result = self.module.search_hosts(
            filter="platform_name:'Linux'",
            limit=25,
            offset=10,
            sort="hostname.desc"
        )

        # Verify API call with all parameters
        self.mock_client.command.assert_called_once_with(
            "QueryDevicesByFilter",
            parameters={
                "filter": "platform_name:'Linux'",
                "limit": 25,
                "offset": 10,
                "sort": "hostname.desc"
            }
        )

        # Verify result
        self.assertEqual(result, [])

    def test_get_host_details(self):
        """Test getting host details."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["device1"])

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostDeviceDetailsV2",
            body={"ids": ["device1"]}
        )

        # Verify result
        expected_result = [{"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"}]
        self.assertEqual(result, expected_result)

    def test_get_host_details_multiple_ids(self):
        """Test getting host details for multiple IDs."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"},
                    {"device_id": "device2", "hostname": "TEST-HOST-2", "platform_name": "Linux"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["device1", "device2"])

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostDeviceDetailsV2",
            body={"ids": ["device1", "device2"]}
        )

        # Verify result
        expected_result = [
            {"device_id": "device1", "hostname": "TEST-HOST-1", "platform_name": "Windows"},
            {"device_id": "device2", "hostname": "TEST-HOST-2", "platform_name": "Linux"}
        ]
        self.assertEqual(result, expected_result)

    def test_get_host_details_not_found(self):
        """Test getting host details for non-existent host."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["nonexistent"])

        # For empty resources, handle_api_response returns the default_result (empty list)
        self.assertEqual(result, [])

    def test_get_host_details_error(self):
        """Test getting host details with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 404,
            "body": {
                "errors": [{"message": "Device not found"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["invalid-id"])

        # Verify result contains error
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_get_host_details_empty_list(self):
        """Test getting host details with empty ID list."""
        # Call get_host_details with empty list
        result = self.module.get_host_details([])

        # Should return empty list without making API call
        self.assertEqual(result, [])
        self.mock_client.command.assert_not_called()

    def test_search_hosts_windows_platform(self):
        """Test searching for Windows hosts."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["win-host-1", "win-host-2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "win-host-1", "platform_name": "Windows", "hostname": "WIN-01"},
                    {"device_id": "win-host-2", "platform_name": "Windows", "hostname": "WIN-02"}
                ]
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'")

        # Verify result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["platform_name"], "Windows")
        self.assertEqual(result[1]["platform_name"], "Windows")

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Windows'")

    def test_search_hosts_linux_platform(self):
        """Test searching for Linux hosts."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["linux-host-1"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "linux-host-1", "platform_name": "Linux", "hostname": "LINUX-01"}
                ]
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Linux'")

        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["platform_name"], "Linux")

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Linux'")

    def test_search_hosts_mac_platform_no_results(self):
        """Test searching for Mac hosts with no results."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Mac'")

        # Verify result
        self.assertEqual(len(result), 0)

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Mac'")


if __name__ == '__main__':
    unittest.main()
