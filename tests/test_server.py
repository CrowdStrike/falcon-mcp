"""
Tests for the Falcon MCP server.
"""

import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp import registry
from falcon_mcp.server import FalconMCPServer


class TestFalconMCPServer(unittest.TestCase):
    """Test cases for the Falcon MCP server."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Ensure modules are discovered before each test
        registry.discover_modules()

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_initialization(self, mock_fastmcp, mock_client):
        """Test server initialization with default settings."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server
        server = FalconMCPServer(
            base_url="https://api.test.crowdstrike.com", debug=True
        )

        # Verify client initialization with direct parameters
        mock_client.assert_called_once()
        # Extract the arguments
        call_args = mock_client.call_args[1]
        self.assertEqual(call_args["base_url"], "https://api.test.crowdstrike.com")
        self.assertTrue(call_args["debug"])

        # Verify authentication
        mock_client_instance.authenticate.assert_called_once()

        # Verify server initialization
        mock_fastmcp.assert_called_once_with(
            name="Falcon MCP Server",
            instructions="This server provides access to CrowdStrike Falcon capabilities.",
            debug=True,
            log_level="DEBUG",
        )

        # Verify modules initialization
        available_module_names = registry.get_module_names()
        self.assertEqual(len(server.modules), len(available_module_names))
        for module_name in available_module_names:
            self.assertIn(module_name, server.modules)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_with_specific_modules(self, mock_fastmcp, mock_client):
        """Test server initialization with specific modules."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with only the detections module
        server = FalconMCPServer(enabled_modules={"detections"})

        # Verify modules initialization
        self.assertEqual(len(server.modules), 1)
        self.assertIn("detections", server.modules)

    @patch("falcon_mcp.server.FalconClient")
    def test_authentication_failure(self, mock_client):
        """Test server initialization with authentication failure."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = False
        mock_client.return_value = mock_client_instance

        # Verify authentication failure raises RuntimeError
        with self.assertRaises(RuntimeError):
            FalconMCPServer()

    @patch("falcon_mcp.server.FalconClient")
    def test_falcon_check_connectivity(self, mock_client):
        """Test checking Falcon API connectivity."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.is_authenticated.return_value = True
        mock_client.return_value = mock_client_instance
        mock_client_instance.authenticate.return_value = True

        # Create server with mock client
        server = FalconMCPServer()

        # Call falcon_check_connectivity
        result = server.falcon_check_connectivity()

        # Verify client method was called
        mock_client_instance.is_authenticated.assert_called_once()

        # Verify result
        expected_result = {"connected": True}
        self.assertEqual(result, expected_result)

    @patch("falcon_mcp.server.FalconClient")
    def test_get_available_modules(self, mock_client):
        """Test getting available modules."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        # Create server
        server = FalconMCPServer()

        # Call get_available_modules
        result = server.get_available_modules()

        # Get the actual module names from the registry
        expected_modules = registry.get_module_names()

        # Verify result matches registry
        self.assertEqual(set(result["modules"]), set(expected_modules))


if __name__ == "__main__":
    unittest.main()
