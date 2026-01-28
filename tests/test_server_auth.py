"""
Tests for server-level API key authentication integration.

These tests verify that the FalconMCPServer correctly stores and applies
API key authentication for HTTP transports.
"""

from unittest.mock import MagicMock, patch


class TestServerAPIKeyStorage:
    """Test that FalconMCPServer correctly stores API key configuration."""

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    def test_server_stores_api_key(self, mock_registry, mock_client_class):
        """Test that FalconMCPServer stores the api_key parameter."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        server = FalconMCPServer(api_key="test-api-key")

        assert server.api_key == "test-api-key"

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    def test_api_key_defaults_to_none(self, mock_registry, mock_client_class):
        """Test that api_key defaults to None when not provided."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        server = FalconMCPServer()

        assert server.api_key is None


class TestMiddlewareApplication:
    """Test that auth middleware is correctly applied to transports."""

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.auth_middleware")
    @patch("falcon_mcp.server.uvicorn")
    def test_middleware_applied_to_streamable_http(
        self, mock_uvicorn, mock_auth_middleware, mock_registry, mock_client_class
    ):
        """Test that auth middleware wraps streamable-http app when api_key is set."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        mock_wrapped_app = MagicMock()
        mock_auth_middleware.return_value = mock_wrapped_app

        server = FalconMCPServer(api_key="test-key")
        server.run(transport="streamable-http")

        # Verify auth_middleware was called with the app and api_key
        mock_auth_middleware.assert_called_once()
        call_args = mock_auth_middleware.call_args
        # auth_middleware(app, api_key) - positional args
        assert call_args[0][1] == "test-key"

        # Verify uvicorn.run was called with the wrapped app
        mock_uvicorn.run.assert_called_once()
        uvicorn_call_args = mock_uvicorn.run.call_args
        assert uvicorn_call_args[0][0] == mock_wrapped_app

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.auth_middleware")
    @patch("falcon_mcp.server.uvicorn")
    def test_middleware_applied_to_sse(
        self, _mock_uvicorn, mock_auth_middleware, mock_registry, mock_client_class
    ):
        """Test that auth middleware wraps SSE app when api_key is set."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        mock_wrapped_app = MagicMock()
        mock_auth_middleware.return_value = mock_wrapped_app

        server = FalconMCPServer(api_key="test-key")
        server.run(transport="sse")

        # Verify auth_middleware was called
        mock_auth_middleware.assert_called_once()
        call_args = mock_auth_middleware.call_args
        # auth_middleware(app, api_key) - positional args
        assert call_args[0][1] == "test-key"

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.auth_middleware")
    def test_middleware_not_applied_to_stdio(
        self, mock_auth_middleware, mock_registry, mock_client_class
    ):
        """Test that auth middleware is NOT applied for stdio transport."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        server = FalconMCPServer(api_key="test-key")

        # Mock the internal FastMCP server's run method
        server.server.run = MagicMock()

        server.run(transport="stdio")

        # Verify auth_middleware was NOT called for stdio
        mock_auth_middleware.assert_not_called()

        # Verify FastMCP run was called with stdio
        server.server.run.assert_called_once_with("stdio")

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.auth_middleware")
    @patch("falcon_mcp.server.uvicorn")
    def test_no_middleware_when_api_key_none(
        self, _mock_uvicorn, mock_auth_middleware, mock_registry, mock_client_class
    ):
        """Test that auth middleware is NOT applied when api_key is None."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        server = FalconMCPServer()  # No api_key
        server.run(transport="streamable-http")

        # Verify auth_middleware was NOT called
        mock_auth_middleware.assert_not_called()


class TestLogging:
    """Test that API key authentication status is logged."""

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.uvicorn")
    @patch("falcon_mcp.server.logger")
    def test_log_message_when_enabled(
        self, mock_logger, _mock_uvicorn, mock_registry, mock_client_class
    ):
        """Test that 'API key authentication enabled' is logged when api_key is set."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        server = FalconMCPServer(api_key="test-key")
        server.run(transport="streamable-http")

        # Find the log call with "API key authentication enabled"
        info_calls = [call for call in mock_logger.info.call_args_list]
        auth_log_found = any(
            "API key authentication enabled" in str(call) for call in info_calls
        )
        assert auth_log_found, f"Expected 'API key authentication enabled' log, got: {info_calls}"

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.registry")
    @patch("falcon_mcp.server.uvicorn")
    @patch("falcon_mcp.server.logger")
    def test_no_auth_log_when_disabled(
        self, mock_logger, _mock_uvicorn, mock_registry, mock_client_class
    ):
        """Test that auth log is NOT present when api_key is None."""
        from falcon_mcp.server import FalconMCPServer

        # Setup mocks
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        mock_registry.get_module_names.return_value = []
        mock_registry.get_available_modules.return_value = {}

        # Reset mock to clear any calls from initialization
        mock_logger.reset_mock()

        server = FalconMCPServer()  # No api_key
        mock_logger.reset_mock()  # Clear init logs
        server.run(transport="streamable-http")

        # Verify NO log call mentions "API key authentication enabled"
        info_calls = [call for call in mock_logger.info.call_args_list]
        auth_log_found = any(
            "API key authentication enabled" in str(call) for call in info_calls
        )
        assert not auth_log_found, f"Unexpected auth log found: {info_calls}"
