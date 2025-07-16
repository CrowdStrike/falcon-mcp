import unittest
from unittest.mock import call, MagicMock

from mcp.server import FastMCP

from falcon_mcp.client import FalconClient


class TestModules(unittest.TestCase):
    def setup_module(self, module_class):
        """
        Set up test fixtures with the specified module class.

        Args:
            module_class: The module class to instantiate
        """
        # Create a mock client
        self.mock_client = MagicMock(spec=FalconClient)

        # Create a mock server
        self.mock_server = MagicMock(spec=FastMCP)

        # Create the module
        self.module = module_class(self.mock_client)

    def assert_tools_registered(self, expected_tools):
        """
        Helper method to verify that a module correctly registers its tools.

        Args:
            expected_tools: List of tool names that should be registered
        """
        # Call register_tools
        self.module.register_tools(self.mock_server)

        # Verify that add_tool was called for each tool
        self.assertEqual(self.mock_server.add_tool.call_count, len(expected_tools))

        # Get the tool names that were registered
        registered_tools = [
            call.kwargs["name"] for call in self.mock_server.add_tool.call_args_list
        ]

        # Verify that all expected tools were registered
        for tool in expected_tools:
            self.assertIn(tool, registered_tools)

    def assert_resources_registered(self, expected_resources):
        """
        Helper method to verify that a module correctly registers its resources.

        Args:
            expected_tools: List of resources names that should be registered
        """
        # Call register_tools
        self.module.register_resources(self.mock_server)

        # Verify that add_resource was called for each resource
        self.assertEqual(self.mock_server.add_resource.call_count, len(expected_resources))

        # Get the tool names that were registered
        registered_resources = [
            call.kwargs["resource"].name for call in self.mock_server.add_resource.call_args_list
        ]

        # Verify that all expected tools were registered
        for tool in expected_resources:
            self.assertIn(tool, registered_resources)
