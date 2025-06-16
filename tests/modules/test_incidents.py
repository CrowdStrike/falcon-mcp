import unittest
from unittest.mock import MagicMock, patch

from mcp.server import FastMCP

from src.client import FalconClient
from src.modules.incidents import IncidentsModule


class TestIncidentsModule(unittest.TestCase):
    """Test cases for the YourModule module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock client
        self.mock_client = MagicMock(spec=FalconClient)

        # Create the module
        self.module = IncidentsModule(self.mock_client)

        # Create a mock server
        self.mock_server = MagicMock(spec=FastMCP)

    def test_register_tools(self):
        """Test registering tools with the server."""
        # Call register_tools
        self.module.register_tools(self.mock_server)

        # Verify that add_tool was called for each tool
        self.assertEqual(self.mock_server.add_tool.call_count, 3)  # Adjust based on number of tools

        # Get the tool names that were registered
        registered_tools = [
            call.kwargs['name']
            for call in self.mock_server.add_tool.call_args_list
        ]

        # Verify that all expected tools were registered
        expected_tools = [
            "incidents_crowd_score",
            "incidents_get_incidents",
            "incidents_query_incidents",
        ]
        for tool in expected_tools:
            self.assertIn(tool, registered_tools)

    # def test_your_tool_method(self):
    #     """Test your tool method."""
    #     # Setup mock response
    #     mock_response = {
    #         "status_code": 200,
    #         "body": {
    #             "resources": [{"id": "test", "name": "Test Resource"}]
    #         }
    #     }
    #     self.mock_client.command.return_value = mock_response

    #     # Call your tool method
    #     result = self.module.your_tool_method("test_param", 123)

    #     # Verify client command was called correctly
    #     self.mock_client.command.assert_called_once_with(
    #         "YourFalconAPIOperation",
    #         parameters={"param1": "test_param", "param2": 123}
    #     )

    #     # Verify result
    #     expected_result = [{"id": "test", "name": "Test Resource"}]
    #     self.assertEqual(result, expected_result)

    # def test_your_tool_method_error(self):
    #     """Test your tool method with API error."""
    #     # Setup mock response with error
    #     mock_response = {
    #         "status_code": 403,
    #         "body": {
    #             "errors": [{"message": "Access denied"}]
    #         }
    #     }
    #     self.mock_client.command.return_value = mock_response

    #     # Call your tool method
    #     result = self.module.your_tool_method("test_param")

    #     # Verify result contains error
    #     self.assertIn("error", result)
    #     self.assertIn("details", result)
