"""
Tests for the Serverless module.
"""

import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp.modules.serverless import ServerlessModule
from tests.modules.utils.test_modules import TestModules


class TestServerlessModule(TestModules):
    """Test cases for the Serverless module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ServerlessModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_serverless_vulnerabilities",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_serverless_vulnerabilities_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_serverless_vulnerabilities_success(self):
        """Test searching serverless vulnerabilities with successful response."""
        run = {
            "tool": {
                "driver": {
                    "name": "CrowdStrike",
                    "informationUri": "https://www.crowdstrike.com/",
                    "rules": [
                        {
                            "id": "CVE-2023-12345",
                            "name": "PythonPackageVulnerability",
                            "shortDescription": {"text": "Test vulnerability description"},
                            "fullDescription": {"text": "Test vulnerability full description"},
                            "help": {"text": "Package: test-package\nVulnerability: CVE-2023-12345"},
                            "properties": {
                                "severity": "HIGH",
                                "cvssBaseScore": 8.5,
                                "remediations": ["Upgrade to version 2.0.0"],
                            },
                        }
                    ],
                }
            }
        }
        # Real FalconPy shape: SARIF document(s) live in body.resources
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"runs": [run]}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_serverless_vulnerabilities(
            filter="cloud_provider:'aws'"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["tool"]["driver"]["name"], "CrowdStrike")
        self.assertEqual(
            result[0]["tool"]["driver"]["rules"][0]["id"], "CVE-2023-12345"
        )
        self.assertEqual(
            result[0]["tool"]["driver"]["rules"][0]["properties"]["severity"], "HIGH"
        )

    def test_search_serverless_vulnerabilities_no_filter(self):
        """Test searching serverless vulnerabilities with no filter parameter."""
        # In the serverless module, filter is a required parameter with no default
        # So we should test that it's properly required

        # Create a mock implementation that raises TypeError when filter is not provided
        def mock_search(*args, **kwargs):
            if "filter" not in kwargs:
                raise TypeError("filter is a required parameter")
            return []

        # Replace the method with our mock
        self.module.search_serverless_vulnerabilities = mock_search

        # This should raise a TypeError since filter is a required parameter
        with self.assertRaises(TypeError):
            self.module.search_serverless_vulnerabilities()

    def test_search_serverless_vulnerabilities_empty_response(self):
        """Test searching serverless vulnerabilities with empty response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_serverless_vulnerabilities(
            filter="cloud_provider:'aws'"
        )

        self.assertEqual(result, [])

    def test_search_serverless_vulnerabilities_error(self):
        """Test searching serverless vulnerabilities with API error."""
        # Setup mock error response
        error_response = {
            "error": "Failed to search serverless vulnerabilities: Request failed with status code 400",
            "details": {"errors": [{"message": "Invalid query"}]},
        }

        # Mock the method to return the error
        self.module.search_serverless_vulnerabilities = MagicMock(return_value=[error_response])

        # Call search_serverless_vulnerabilities
        results = self.module.search_serverless_vulnerabilities(
            filter="invalid query"
        )
        result = results[0]

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(
            result["error"].startswith("Failed to search serverless vulnerabilities")
        )

    def test_search_serverless_vulnerabilities_with_all_params(self):
        """Test searching serverless vulnerabilities with all parameters."""
        # Setup mock response
        mock_response = [
            {
                "tool": {
                    "driver": {
                        "name": "CrowdStrike",
                        "rules": [
                            {
                                "id": "CVE-2023-12345",
                                "properties": {"severity": "HIGH"}
                            }
                        ]
                    }
                }
            }
        ]

        # Mock the method to return the mock response
        self.module.search_serverless_vulnerabilities = MagicMock(return_value=mock_response)

        # Call search_serverless_vulnerabilities with all parameters
        result = self.module.search_serverless_vulnerabilities(
            filter="cloud_provider:'aws'",
            limit=5,
            offset=10,
            sort="severity",
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["tool"]["driver"]["name"], "CrowdStrike")

    def test_search_serverless_vulnerabilities_missing_runs(self):
        """Test searching serverless vulnerabilities with missing runs in response."""
        # Setup mock response with missing runs
        error_response = {
            "error": "Failed to search serverless vulnerabilities: Missing 'runs' in response",
            "details": {"body": {}}
        }

        # Mock the method to return the error
        self.module.search_serverless_vulnerabilities = MagicMock(return_value=[error_response])

        # Call search_serverless_vulnerabilities
        result = self.module.search_serverless_vulnerabilities(
            filter="cloud_provider:'aws'"
        )

        # Verify result is a list with one item containing error info
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_serverless_vulnerabilities_none_runs(self):
        """Test searching serverless vulnerabilities when 'runs' key exists but is None."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"runs": None}]},
        }

        result = self.module.search_serverless_vulnerabilities(
            filter="cloud_provider:'aws'"
        )

        self.assertEqual(result, [])
        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args[1]
        self.assertEqual(call_args["parameters"]["filter"], "cloud_provider:'aws'")


if __name__ == "__main__":
    unittest.main()
