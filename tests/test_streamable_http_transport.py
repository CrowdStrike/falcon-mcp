"""
Tests for streamable-http transport functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp.server import FalconMCPServer


class TestStreamableHttpTransport(unittest.TestCase):
    """Test cases for streamable-http transport."""

    @patch("falcon_mcp.server.create_no_redirect_app")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_transport_initialization(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
        mock_create_no_redirect_app,
    ):
        """Test streamable-http transport initialization."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_mcp_app
        mock_fastmcp.return_value = mock_server_instance

        mock_wrapped_app = MagicMock()
        mock_create_no_redirect_app.return_value = mock_wrapped_app

        # Create server
        server = FalconMCPServer(debug=True)

        # Test streamable-http transport
        server.run("streamable-http", host="0.0.0.0", port=8080)

        # Verify streamable_http_app was called
        mock_server_instance.streamable_http_app.assert_called_once()

        # Verify create_no_redirect_app was called with the MCP app
        mock_create_no_redirect_app.assert_called_once_with(mock_mcp_app)

        # Verify uvicorn was called with the wrapped app
        mock_uvicorn.run.assert_called_once_with(mock_wrapped_app, host="0.0.0.0", port=8080, log_level="debug")

    @patch("falcon_mcp.server.create_no_redirect_app")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_default_parameters(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
        mock_create_no_redirect_app,
    ):
        """Test streamable-http transport with default parameters."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_mcp_app
        mock_fastmcp.return_value = mock_server_instance

        mock_wrapped_app = MagicMock()
        mock_create_no_redirect_app.return_value = mock_wrapped_app

        # Create server
        server = FalconMCPServer(debug=False)

        # Test streamable-http transport with defaults
        server.run("streamable-http")

        # Verify uvicorn was called with default parameters and wrapped app
        mock_uvicorn.run.assert_called_once_with(
            mock_wrapped_app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_non_streamable_http_transport_unchanged(
        self,
        mock_fastmcp,
        mock_client,
    ):
        """Test that non-streamable-http transports use the original method."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        # Create server
        server = FalconMCPServer()

        # Test stdio transport (should use original method)
        server.run("stdio")

        # Verify the original run method was called
        mock_server_instance.run.assert_called_once_with("stdio")

        # Verify streamable_http_app was NOT called
        mock_server_instance.streamable_http_app.assert_not_called()

    @patch("falcon_mcp.server.create_no_redirect_app")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_custom_parameters(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
        mock_create_no_redirect_app,
    ):
        """Test streamable-http transport with custom parameters."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_mcp_app
        mock_fastmcp.return_value = mock_server_instance

        mock_wrapped_app = MagicMock()
        mock_create_no_redirect_app.return_value = mock_wrapped_app

        # Create server
        server = FalconMCPServer(debug=True)

        # Test streamable-http transport with custom parameters
        server.run("streamable-http", host="192.168.1.100", port=9000)

        # Verify uvicorn was called with custom parameters and wrapped app
        mock_uvicorn.run.assert_called_once_with(
            mock_wrapped_app,
            host="192.168.1.100",
            port=9000,
            log_level="debug",
        )

    @patch("falcon_mcp.server.create_no_redirect_app")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_logging_levels(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
        mock_create_no_redirect_app,
    ):
        """Test streamable-http transport logging level configuration."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_mcp_app
        mock_fastmcp.return_value = mock_server_instance

        mock_wrapped_app = MagicMock()
        mock_create_no_redirect_app.return_value = mock_wrapped_app

        # Test with debug=True
        server_debug = FalconMCPServer(debug=True)
        server_debug.run("streamable-http")

        # Verify debug log level
        mock_uvicorn.run.assert_called_with(
            mock_wrapped_app,
            host="127.0.0.1",
            port=8000,
            log_level="debug",
        )

        # Reset mock
        mock_uvicorn.reset_mock()

        # Test with debug=False
        server_info = FalconMCPServer(debug=False)
        server_info.run("streamable-http")

        # Verify info log level
        mock_uvicorn.run.assert_called_with(
            mock_wrapped_app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )

    @patch("falcon_mcp.server.create_no_redirect_app")
    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_sse_transport_uses_no_redirect_wrapper(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
        mock_create_no_redirect_app,
    ):
        """Test that SSE transport also uses the no-redirect wrapper."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_server_instance.sse_app.return_value = mock_mcp_app
        mock_fastmcp.return_value = mock_server_instance

        mock_wrapped_app = MagicMock()
        mock_create_no_redirect_app.return_value = mock_wrapped_app

        # Create server
        server = FalconMCPServer(debug=False)

        # Test SSE transport
        server.run("sse", host="0.0.0.0", port=8080)

        # Verify sse_app was called
        mock_server_instance.sse_app.assert_called_once()

        # Verify create_no_redirect_app was called with the MCP app and /sse mount path
        mock_create_no_redirect_app.assert_called_once_with(mock_mcp_app, mount_path="/sse")

        # Verify uvicorn was called with the wrapped app
        mock_uvicorn.run.assert_called_once_with(mock_wrapped_app, host="0.0.0.0", port=8080, log_level="info")


class TestCreateNoRedirectApp(unittest.TestCase):
    """Test cases for the create_no_redirect_app function."""

    def test_create_no_redirect_app_returns_router(self):
        """Test that create_no_redirect_app returns a Starlette Router."""
        from starlette.routing import Router

        from falcon_mcp.server import create_no_redirect_app

        mock_app = MagicMock()
        result = create_no_redirect_app(mock_app)

        # Verify it returns a Router instance
        self.assertIsInstance(result, Router)

    def test_create_no_redirect_app_default_mount_path(self):
        """Test that create_no_redirect_app uses /mcp as default mount path."""
        from starlette.routing import Mount

        from falcon_mcp.server import create_no_redirect_app

        mock_app = MagicMock()
        router = create_no_redirect_app(mock_app)

        # Verify the mount path
        self.assertEqual(len(router.routes), 1)
        self.assertIsInstance(router.routes[0], Mount)
        self.assertEqual(router.routes[0].path, "/mcp")

    def test_create_no_redirect_app_custom_mount_path(self):
        """Test that create_no_redirect_app accepts custom mount path."""
        from starlette.routing import Mount

        from falcon_mcp.server import create_no_redirect_app

        mock_app = MagicMock()
        router = create_no_redirect_app(mock_app, mount_path="/sse")

        # Verify the custom mount path
        self.assertEqual(len(router.routes), 1)
        self.assertIsInstance(router.routes[0], Mount)
        self.assertEqual(router.routes[0].path, "/sse")

    def test_create_no_redirect_app_redirect_slashes_disabled(self):
        """Test that the router has redirect_slashes disabled."""
        from falcon_mcp.server import create_no_redirect_app

        mock_app = MagicMock()
        router = create_no_redirect_app(mock_app)

        # Verify redirect_slashes is False
        self.assertFalse(router.redirect_slashes)


if __name__ == "__main__":
    unittest.main()
