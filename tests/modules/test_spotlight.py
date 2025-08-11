"""
Tests for the Spotlight module.
"""

import unittest

from falcon_mcp.modules.spotlight import SpotlightModule
from tests.modules.utils.test_modules import TestModules


class TestSpotlightModule(TestModules):
    """Test cases for the Spotlight module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SpotlightModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_vulnerabilities",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_vulnerabilities_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_vulnerabilities_success(self):
        """Test searching vulnerabilities with successful response."""
        # Setup mock response with sample vulnerability data
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "cve_id": "CVE-2023-12345",
                        "status": "open",
                        "severity": "HIGH",
                        "cvss_base_score": 8.5,
                        "created_timestamp": "2023-08-01T12:00:00Z",
                        "updated_timestamp": "2023-08-02T14:30:00Z",
                        "host_info": {
                            "hostname": "test-server",
                            "os_version": "Ubuntu 22.04"
                        }
                    }
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call search_vulnerabilities with test parameters
        result = self.module.search_vulnerabilities(filter="status:'open'")

        # Verify client command was called correctly
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "combinedQueryVulnerabilities")
        
        # Check that the parameters dictionary contains the expected filter
        params = call_args[1]["parameters"]
        self.assertEqual(params["filter"], "status:'open'")

        # Verify result contains expected values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cve_id"], "CVE-2023-12345")
        self.assertEqual(result[0]["severity"], "HIGH")
        self.assertEqual(result[0]["status"], "open")
        self.assertEqual(result[0]["cvss_base_score"], 8.5)

    def test_search_vulnerabilities_no_filter(self):
        """Test searching vulnerabilities with no filter parameter."""
        # Setup mock response with sample vulnerability data
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "cve_id": "CVE-2023-12345",
                        "status": "open",
                        "severity": "HIGH"
                    }
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call search_vulnerabilities with no filter
        result = self.module.search_vulnerabilities()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "combinedQueryVulnerabilities")

        # Verify result contains expected values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cve_id"], "CVE-2023-12345")

    def test_search_vulnerabilities_empty_response(self):
        """Test searching vulnerabilities with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call search_vulnerabilities
        result = self.module.search_vulnerabilities(filter="status:'closed'")

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "combinedQueryVulnerabilities")

        # Verify result is an empty list
        self.assertEqual(result, [])

    def test_search_vulnerabilities_error(self):
        """Test searching vulnerabilities with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid query"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_vulnerabilities
        results = self.module.search_vulnerabilities(filter="invalid query")
        result = results[0]

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(result["error"].startswith("Failed to search vulnerabilities"))


if __name__ == "__main__":
    unittest.main()
