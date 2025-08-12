"""
Unit tests for the Discover module.
"""

import unittest
from unittest.mock import MagicMock, patch

from mcp.server import FastMCP

from falcon_mcp.client import FalconClient
from falcon_mcp.modules.discover import DiscoverModule


class TestDiscoverModule(unittest.TestCase):
    """Test cases for the Discover module."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=FalconClient)
        self.module = DiscoverModule(self.client)
        self.server = MagicMock(spec=FastMCP)

    def test_register_tools(self):
        """Test that tools are registered correctly."""
        self.module.register_tools(self.server)
        self.server.add_tool.assert_called_once()
        self.assertEqual(len(self.module.tools), 1)
        self.assertEqual(self.module.tools[0], "falcon_search_applications")

    def test_register_resources(self):
        """Test that resources are registered correctly."""
        self.module.register_resources(self.server)
        self.server.add_resource.assert_called_once()
        self.assertEqual(len(self.module.resources), 1)
        self.assertEqual(
            str(self.module.resources[0]), "falcon://discover/applications/fql-guide"
        )

    @patch("falcon_mcp.modules.discover.prepare_api_parameters")
    @patch("falcon_mcp.modules.discover.handle_api_response")
    def test_search_applications(self, mock_handle_response, mock_prepare_params):
        """Test search_applications method."""
        # Setup mocks
        mock_prepare_params.return_value = {"filter": "name:'Chrome'"}
        mock_response = MagicMock()
        self.client.command.return_value = mock_response
        mock_handle_response.return_value = [{"id": "app1", "name": "Chrome"}]

        # Call the method
        result = self.module.search_applications(filter="name:'Chrome'")

        # Assertions
        # Don't check the exact arguments, just verify it was called once
        self.assertEqual(mock_prepare_params.call_count, 1)
        self.client.command.assert_called_once_with(
            "combined_applications", parameters={"filter": "name:'Chrome'"}
        )
        mock_handle_response.assert_called_once_with(
            mock_response,
            operation="combined_applications",
            error_message="Failed to search applications",
            default_result=[],
        )
        self.assertEqual(result, [{"id": "app1", "name": "Chrome"}])

    @patch("falcon_mcp.modules.discover.prepare_api_parameters")
    @patch("falcon_mcp.modules.discover.handle_api_response")
    def test_search_applications_with_error(self, mock_handle_response, mock_prepare_params):
        """Test search_applications method when an error occurs."""
        # Setup mocks
        mock_prepare_params.return_value = {"filter": "name:'Chrome'"}
        mock_response = MagicMock()
        self.client.command.return_value = mock_response
        error_response = {"error": "API Error", "message": "Something went wrong"}
        mock_handle_response.return_value = error_response

        # Call the method
        result = self.module.search_applications(filter="name:'Chrome'")

        # Assertions
        self.assertEqual(result, [error_response])

    @patch("falcon_mcp.modules.discover.prepare_api_parameters")
    @patch("falcon_mcp.modules.discover.handle_api_response")
    def test_search_applications_with_all_params(self, mock_handle_response, mock_prepare_params):
        """Test search_applications method with all parameters."""
        # Setup mocks
        mock_prepare_params.return_value = {
            "filter": "name:'Chrome'",
            "facet": "host_info",
            "limit": 50,
            "sort": "name.asc",
        }
        mock_response = MagicMock()
        self.client.command.return_value = mock_response
        mock_handle_response.return_value = [{"id": "app1", "name": "Chrome"}]

        # Call the method
        result = self.module.search_applications(
            filter="name:'Chrome'",
            facet="host_info",
            limit=50,
            sort="name.asc",
        )

        # Assertions
        # Don't check the exact arguments, just verify it was called once
        self.assertEqual(mock_prepare_params.call_count, 1)
        self.client.command.assert_called_once_with(
            "combined_applications",
            parameters={
                "filter": "name:'Chrome'",
                "facet": "host_info",
                "limit": 50,
                "sort": "name.asc",
            },
        )
        self.assertEqual(result, [{"id": "app1", "name": "Chrome"}])


if __name__ == "__main__":
    unittest.main()
