"""
Tests for the Falcon MCP server.
"""

import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp import registry
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
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
            base_url="https://api.test.crowdstrike.com",
            debug=True,
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
            stateless_http=False,
            host="127.0.0.1",
            port=8000,
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
    def test_list_enabled_modules(self, mock_client):
        """Test listing enabled modules."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        # Create server
        server = FalconMCPServer()

        # Call list_enabled_modules
        result = server.list_enabled_modules()

        # Get the actual module names from the registry
        expected_modules = registry.get_module_names()

        # Verify result matches registry (since all modules are enabled by default)
        self.assertEqual(set(result["modules"]), set(expected_modules))

    @patch("falcon_mcp.server.FalconClient")
    def test_list_enabled_modules_with_limited_modules(self, mock_client):
        """Test listing enabled modules with limited module set."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        # Create server with only specific modules
        server = FalconMCPServer(enabled_modules={"detections", "cloud"})

        # Call list_enabled_modules
        result = server.list_enabled_modules()

        # Should only return enabled modules
        self.assertEqual(set(result["modules"]), {"detections", "cloud"})

        # Verify return type is correct
        self.assertIsInstance(result["modules"], list)

        # Verify each module name is a string
        for module_name in result["modules"]:
            self.assertIsInstance(module_name, str)

    @patch("falcon_mcp.server.FalconClient")
    def test_list_modules(self, mock_client):
        """Test listing all available modules."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        # Create server with limited modules
        server = FalconMCPServer(enabled_modules={"detections", "cloud"})

        # Call list_modules
        result = server.list_modules()

        # Should return ALL modules from registry regardless of what's enabled
        expected_modules = registry.get_module_names()
        self.assertEqual(set(result["modules"]), set(expected_modules))

        # Verify return type is correct
        self.assertIsInstance(result["modules"], list)

        # Verify each module name is a string
        for module_name in result["modules"]:
            self.assertIsInstance(module_name, str)

    @patch("falcon_mcp.server.FalconClient")
    def test_list_modules_consistency(self, mock_client):
        """Test that list_modules always returns the same result."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        # Create two servers with different enabled modules
        server1 = FalconMCPServer(enabled_modules={"detections"})
        server2 = FalconMCPServer(enabled_modules={"cloud", "intel"})

        # Both should return the same available modules
        result1 = server1.list_modules()
        result2 = server2.list_modules()

        self.assertEqual(set(result1["modules"]), set(result2["modules"]))

        # And both should match the registry
        expected_modules = registry.get_module_names()
        self.assertEqual(set(result1["modules"]), set(expected_modules))

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_with_stateless_http_enabled(self, mock_fastmcp, mock_client):
        """Test server initialization with stateless_http enabled."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with stateless_http enabled
        server = FalconMCPServer(stateless_http=True)

        # Verify stateless_http is stored
        self.assertTrue(server.stateless_http)

        # Verify FastMCP was initialized with stateless_http
        mock_fastmcp.assert_called_once_with(
            name="Falcon MCP Server",
            instructions="This server provides access to CrowdStrike Falcon capabilities.",
            debug=False,
            log_level="INFO",
            stateless_http=True,
            host="127.0.0.1",
            port=8000,
        )

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_with_stateless_http_disabled_by_default(self, mock_fastmcp, mock_client):
        """Test server initialization with stateless_http disabled by default."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server without specifying stateless_http
        server = FalconMCPServer()

        # Verify stateless_http defaults to False
        self.assertFalse(server.stateless_http)

        # Verify FastMCP was initialized with stateless_http=False
        mock_fastmcp.assert_called_once_with(
            name="Falcon MCP Server",
            instructions="This server provides access to CrowdStrike Falcon capabilities.",
            debug=False,
            log_level="INFO",
            stateless_http=False,
            host="127.0.0.1",
            port=8000,
        )

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_with_direct_credentials(self, mock_fastmcp, mock_client):
        """Test server initialization with direct credentials passed to client."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with direct credentials
        _server = FalconMCPServer(
            client_id="direct-client-id",
            client_secret="direct-client-secret",
        )

        # Verify FalconClient was initialized with direct credentials
        mock_client.assert_called_once()
        call_args = mock_client.call_args[1]
        self.assertEqual(call_args["client_id"], "direct-client-id")
        self.assertEqual(call_args["client_secret"], "direct-client-secret")

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_with_all_options_and_credentials(self, mock_fastmcp, mock_client):
        """Test server initialization with all options including credentials."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with all options
        _server = FalconMCPServer(
            base_url="https://api.test.crowdstrike.com",
            debug=True,
            client_id="direct-client-id",
            client_secret="direct-client-secret",
        )

        # Verify FalconClient was initialized with all options
        call_args = mock_client.call_args[1]
        self.assertEqual(call_args["base_url"], "https://api.test.crowdstrike.com")
        self.assertTrue(call_args["debug"])
        self.assertEqual(call_args["client_id"], "direct-client-id")
        self.assertEqual(call_args["client_secret"], "direct-client-secret")


    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_passes_non_localhost_host_to_fastmcp(self, mock_fastmcp, mock_client):
        """Test that non-localhost host is passed to FastMCP to avoid DNS rebinding protection."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with 0.0.0.0 host (containerized deployment)
        server = FalconMCPServer(host="0.0.0.0", port=9090)

        # Verify host and port are stored
        self.assertEqual(server.host, "0.0.0.0")
        self.assertEqual(server.port, 9090)

        # Verify FastMCP receives the non-localhost host
        mock_fastmcp.assert_called_once_with(
            name="Falcon MCP Server",
            instructions="This server provides access to CrowdStrike Falcon capabilities.",
            debug=False,
            log_level="INFO",
            stateless_http=False,
            host="0.0.0.0",
            port=9090,
        )

    @patch("falcon_mcp.server.uvicorn")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_run_streamable_http_uses_instance_host_port(
        self, mock_fastmcp, mock_client, mock_uvicorn
    ):
        """Test that run() uses host/port from the server instance for uvicorn."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with custom host/port
        server = FalconMCPServer(host="0.0.0.0", port=9090)

        # Run with streamable-http transport
        server.run("streamable-http")

        # Verify uvicorn was called with instance host/port
        mock_uvicorn.run.assert_called_once()
        call_kwargs = mock_uvicorn.run.call_args[1]
        self.assertEqual(call_kwargs["host"], "0.0.0.0")
        self.assertEqual(call_kwargs["port"], 9090)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_core_tools_have_read_only_annotations(self, mock_fastmcp, mock_client):
        """Test that all 3 core server tools are registered with read-only annotations."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server (registers tools during __init__)
        FalconMCPServer(enabled_modules=set())

        # Collect core tool registrations (the first 3 add_tool calls)
        core_tool_names = [
            "falcon_check_connectivity",
            "falcon_list_enabled_modules",
            "falcon_list_modules",
        ]
        for call in mock_server_instance.add_tool.call_args_list:
            name = call.kwargs.get("name")
            if name in core_tool_names:
                self.assertEqual(
                    call.kwargs.get("annotations"),
                    READ_ONLY_ANNOTATIONS,
                    f"Tool {name} should have READ_ONLY_ANNOTATIONS",
                )


    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_all_tools_have_annotations(self, mock_fastmcp, mock_client):
        """Test that every registered tool has non-None annotations."""
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with ALL modules to register every tool
        FalconMCPServer()

        for call in mock_server_instance.add_tool.call_args_list:
            name = call.kwargs.get("name", "<unknown>")
            annotations = call.kwargs.get("annotations")
            self.assertIsNotNone(
                annotations,
                f"Tool '{name}' was registered without annotations. "
                f"Use _add_tool() for automatic READ_ONLY_ANNOTATIONS, "
                f"or pass explicit annotations for mutating tools.",
            )

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_initialization_with_member_cid(self, mock_fastmcp, mock_client):
        """Test server initialization with member_cid parameter."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server with member_cid
        _server = FalconMCPServer(member_cid="abc123-child-cid-xyz")

        # Verify FalconClient was initialized with member_cid
        mock_client.assert_called_once()
        call_args = mock_client.call_args[1]
        self.assertEqual(call_args["member_cid"], "abc123-child-cid-xyz")

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_server_initialization_without_member_cid(self, mock_fastmcp, mock_client):
        """Test server initialization without member_cid (parent CID mode)."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server without member_cid
        _server = FalconMCPServer()

        # Verify FalconClient was initialized without member_cid
        mock_client.assert_called_once()
        call_args = mock_client.call_args[1]
        # Should be None (the default)
        self.assertIsNone(call_args["member_cid"])


if __name__ == "__main__":
    unittest.main()
