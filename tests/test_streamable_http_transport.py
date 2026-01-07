"""
Tests for streamable-http transport functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp.server import FalconMCPServer


class TestStreamableHttpTransport(unittest.TestCase):
    """Test cases for streamable-http transport."""

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_transport_initialization(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport initialization."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server
        server = FalconMCPServer(debug=True)

        # Test streamable-http transport
        server.run("streamable-http", host="0.0.0.0", port=8080)

        # Verify uvicorn was called with correct parameters
        mock_uvicorn.run.assert_called_once_with(
            mock_app, host="0.0.0.0", port=8080, log_level="debug"
        )

        # Verify streamable_http_app was called
        mock_server_instance.streamable_http_app.assert_called_once()

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_with_stateless_http_enabled(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport with stateless_http enabled."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server with stateless_http enabled
        server = FalconMCPServer(stateless_http=True)

        # Test streamable-http transport
        server.run("streamable-http")

        # Verify streamable_http_app was called with stateless_http=True
        mock_server_instance.streamable_http_app.assert_called_once_with(stateless_http=True)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_with_stateless_http_disabled(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport with stateless_http disabled (default)."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server without stateless_http (defaults to False)
        server = FalconMCPServer()

        # Test streamable-http transport
        server.run("streamable-http")

        # Verify streamable_http_app was called with stateless_http=False
        mock_server_instance.streamable_http_app.assert_called_once_with(stateless_http=False)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_sse_transport_with_stateless_http_enabled(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test sse transport with stateless_http enabled."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.sse_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server with stateless_http enabled
        server = FalconMCPServer(stateless_http=True)

        # Test sse transport
        server.run("sse")

        # Verify sse_app was called with stateless_http=True
        mock_server_instance.sse_app.assert_called_once_with(stateless_http=True)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_sse_transport_with_stateless_http_disabled(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test sse transport with stateless_http disabled (default)."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.sse_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server without stateless_http (defaults to False)
        server = FalconMCPServer()

        # Test sse transport
        server.run("sse")

        # Verify sse_app was called with stateless_http=False
        mock_server_instance.sse_app.assert_called_once_with(stateless_http=False)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_default_parameters(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport with default parameters."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server
        server = FalconMCPServer(debug=False)

        # Test streamable-http transport with defaults
        server.run("streamable-http")

        # Verify uvicorn was called with default parameters
        mock_uvicorn.run.assert_called_once_with(
            mock_app,
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

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_custom_parameters(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport with custom parameters."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Create server
        server = FalconMCPServer(debug=True)

        # Test streamable-http transport with custom parameters
        server.run("streamable-http", host="192.168.1.100", port=9000)

        # Verify uvicorn was called with custom parameters
        mock_uvicorn.run.assert_called_once_with(
            mock_app,
            host="192.168.1.100",
            port=9000,
            log_level="debug",
        )

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    @patch("falcon_mcp.server.uvicorn")
    def test_streamable_http_logging_levels(
        self,
        mock_uvicorn,
        mock_fastmcp,
        mock_client,
    ):
        """Test streamable-http transport logging level configuration."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_app = MagicMock()
        mock_server_instance.streamable_http_app.return_value = mock_app
        mock_fastmcp.return_value = mock_server_instance

        # Test with debug=True
        server_debug = FalconMCPServer(debug=True)
        server_debug.run("streamable-http")

        # Verify debug log level
        mock_uvicorn.run.assert_called_with(
            mock_app,
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
            mock_app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )


if __name__ == "__main__":
    unittest.main()
