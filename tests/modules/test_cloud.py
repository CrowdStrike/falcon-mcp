"""
Tests for the Cloud module.
"""

import unittest

from falcon_mcp.modules.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudModule(TestModules):
    """Test cases for the Cloud module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CloudModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_kubernetes_containers_fql_filter_guide",
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
            "falcon_images_vulnerabilities_fql_filter_guide",
            "falcon_search_images_vulnerabilities",
        ]
        self.assert_tools_registered(expected_tools)

    def test_search_kubernetes_containers(self):
        """Test searching for kubernetes containers."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": ["container_1", "container_2"]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(
            filter="cloud_name:'AWS'", limit=1
        )

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCombined")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_name:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertEqual(result, ["container_1", "container_2"])

    def test_search_kubernetes_containers_errors(self):
        """Test searching for kubernetes containers with API error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(filter="invalid_filter")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_count_kubernetes_containers(self):
        """Test count for kubernetes containers."""
        mock_response = {"status_code": 200, "body": {"resources": [500]}}
        self.mock_client.command.return_value = mock_response

        result = self.module.count_kubernetes_containers(filter="cloud_region:'us-1'")

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCount")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_region:'us-1'")
        self.assertEqual(result, [500])

    def test_count_kubernetes_containers_errors(self):
        """Test count for kubernetes containers with API error."""
        mock_response = {
            "status_code": 500,
            "body": {"errors": [{"message": "internal error"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(filter="invalid_filter")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_search_images_vulnerabilities(self):
        """Test search for images vulnerabilities."""
        mock_response = {"status_code": 200, "body": {"resources": ["cve_id_1"]}}
        self.mock_client.command.return_value = mock_response

        result = self.module.search_images_vulnerabilities(
            filter="cvss_score:>5", limit=1
        )

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadCombinedVulnerabilities")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cvss_score:>5")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertEqual(result, ["cve_id_1"])

    def test_search_images_vulnerabilities_errors(self):
        """Test search for images vulnerabilities with API error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid sort"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(sort="1|1")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)


if __name__ == "__main__":
    unittest.main()
