"""
Tests for the Falcon API client.
"""
import unittest
import sys
import platform
from unittest.mock import MagicMock, patch

from falcon_mcp.client import FalconClient


class TestFalconClient(unittest.TestCase):
    """Test cases for the Falcon API client."""

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_client_initialization(self, mock_apiharness, mock_environ_get):
        """Test client initialization with base URL."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Create client with base URL
        _client = FalconClient(
            base_url="https://api.test.crowdstrike.com",
            debug=True
        )

        # Verify APIHarnessV2 was initialized correctly with config values
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "test-client-id")
        self.assertEqual(call_args["client_secret"], "test-client-secret")
        self.assertEqual(call_args["base_url"], "https://api.test.crowdstrike.com")
        self.assertTrue(call_args["debug"])

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_client_initialization_with_env_vars(self, mock_apiharness, mock_environ_get):
        """Test client initialization with environment variables."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "env-client-id",
            "FALCON_CLIENT_SECRET": "env-client-secret",
            "FALCON_BASE_URL": "https://api.env.crowdstrike.com"
        }.get(key, default)

        # Create client with environment variables
        _client = FalconClient()

        # Verify APIHarnessV2 was initialized correctly
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "env-client-id")
        self.assertEqual(call_args["client_secret"], "env-client-secret")
        self.assertEqual(call_args["base_url"], "https://api.env.crowdstrike.com")
        self.assertFalse(call_args["debug"])

    @patch('falcon_mcp.client.os.environ.get')
    def test_client_initialization_missing_credentials(self, mock_environ_get):
        """Test client initialization with missing credentials."""
        # Setup mock environment variables (missing credentials)
        mock_environ_get.return_value = None

        # Verify ValueError is raised when credentials are missing
        with self.assertRaises(ValueError):
            FalconClient()

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_authenticate(self, mock_apiharness, mock_environ_get):
        """Test authenticate method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.login.return_value = True
        mock_apiharness.return_value = mock_instance

        # Create client and authenticate
        client = FalconClient()
        result = client.authenticate()

        # Verify login was called and result is correct
        mock_instance.login.assert_called_once()
        self.assertTrue(result)

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_is_authenticated(self, mock_apiharness, mock_environ_get):
        """Test is_authenticated method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.token_valid = True
        mock_apiharness.return_value = mock_instance

        # Create client and check authentication status
        client = FalconClient()
        result = client.is_authenticated()

        # Verify result is correct
        self.assertTrue(result)

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_get_headers(self, mock_apiharness, mock_environ_get):
        """Test get_headers method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.auth_headers = {"Authorization": "Bearer test-token"}
        mock_apiharness.return_value = mock_instance

        # Create client and get headers
        client = FalconClient()
        headers = client.get_headers()

        # Verify headers are correct
        self.assertEqual(headers, {"Authorization": "Bearer test-token"})

    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_command(self, mock_apiharness, mock_environ_get):
        """Test command method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.command.return_value = {"status_code": 200, "body": {"resources": [{"id": "test"}]}}
        mock_apiharness.return_value = mock_instance

        # Create client and execute command
        client = FalconClient()
        response = client.command("TestOperation", parameters={"filter": "test"})

        # Verify command was called with correct arguments
        mock_instance.command.assert_called_once_with("TestOperation", parameters={"filter": "test"})

        # Verify response is correct
        self.assertEqual(response["status_code"], 200)
        self.assertEqual(response["body"]["resources"][0]["id"], "test")

    @patch('falcon_mcp.client.version')
    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_get_user_agent_best_case_scenario(self, mock_apiharness, mock_environ_get, mock_version):
        """Test get_user_agent method in the best case scenario with all packages installed."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock version calls for best case scenario
        def version_side_effect(package_name):
            if package_name == "falcon-mcp":
                return "1.2.3"
            if package_name == "crowdstrike-falconpy":
                return "1.3.4"
            raise ValueError(f"Unexpected package: {package_name}")

        mock_version.side_effect = version_side_effect
        mock_apiharness.return_value = MagicMock()

        # Create client and get user agent
        client = FalconClient()
        user_agent = client.get_user_agent()

        # Verify user agent format and content
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = f"{platform.system()}/{platform.release()}"
        expected = f"falcon-mcp/1.2.3 (falconpy/1.3.4; Python/{python_version}; {platform_info})"

        self.assertEqual(user_agent, expected)

        # Verify user agent is properly used in APIHarnessV2 initialization
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["user_agent"], expected)

        # Verify format components
        self.assertTrue(user_agent.startswith("falcon-mcp/1.2.3"))
        self.assertIn(f"Python/{python_version}", user_agent)
        self.assertIn(platform_info, user_agent)
        self.assertIn("falconpy/1.3.4", user_agent)

    @patch('falcon_mcp.client.version')
    @patch('falcon_mcp.client.os.environ.get')
    @patch('falcon_mcp.client.APIHarnessV2')
    def test_get_user_agent_with_custom_user_agent(self, mock_apiharness, mock_environ_get, mock_version):
        """Test get_user_agent method with a custom user agent."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret"
        }.get(key, default)

        # Setup mock version calls
        def version_side_effect(package_name):
            if package_name == "falcon-mcp":
                return "1.2.3"
            if package_name == "crowdstrike-falconpy":
                return "1.3.4"
            raise ValueError(f"Unexpected package: {package_name}")

        mock_version.side_effect = version_side_effect
        mock_apiharness.return_value = MagicMock()

        # Create client with custom user agent
        client = FalconClient(custom_user_agent="CustomApp/1.0")
        user_agent = client.get_user_agent()

        # Verify user agent format and content
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = f"{platform.system()}/{platform.release()}"
        expected = f"falcon-mcp/1.2.3 (falconpy/1.3.4; Python/{python_version}; {platform_info}; CustomApp/1.0)"

        self.assertEqual(user_agent, expected)

        # Verify user agent is properly used in APIHarnessV2 initialization
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["user_agent"], expected)


if __name__ == '__main__':
    unittest.main()
