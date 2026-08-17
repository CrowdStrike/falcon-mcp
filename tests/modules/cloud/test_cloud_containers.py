"""
Tests for cloud containers tools (part of CloudModule).
"""

import unittest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudContainersTools(TestModules):
    """Test cases for the cloud containers tools within CloudModule."""

    def setUp(self):
        self.setup_module(CloudModule)

    def test_search_kubernetes_containers(self):
        """Test searching for kubernetes containers."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 1, "total": 2}},
                "resources": ["container_1", "container_2"],
            },
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(filter="cloud_name:'AWS'", limit=1)

        self.assertEqual(self.mock_client.command.call_count, 1)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCombined")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_name:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertIn("results", result)
        self.assertEqual(result["results"], ["container_1", "container_2"])
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_kubernetes_containers_error(self):
        """Test searching for kubernetes containers with API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        result = self.module.search_kubernetes_containers(filter="invalid_filter")
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_count_kubernetes_containers(self):
        """Test count for kubernetes containers returns an int."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"count": 500}]},
        }
        result = self.module.count_kubernetes_containers(filter="cloud_region:'us-1'")

        self.assertEqual(self.mock_client.command.call_count, 1)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCount")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_region:'us-1'")
        self.assertEqual(result, 500)
        self.assertIsInstance(result, int)

    def test_count_kubernetes_containers_error(self):
        """Test count for kubernetes containers with API error."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "internal error"}]},
        }
        result = self.module.count_kubernetes_containers(filter="invalid_filter")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_search_images_vulnerabilities(self):
        """Test search for images vulnerabilities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 1, "total": 1}},
                "resources": ["cve_id_1"],
            },
        }
        result = self.module.search_images_vulnerabilities(filter="cvss_score:>5", limit=1)

        self.assertEqual(self.mock_client.command.call_count, 1)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadCombinedVulnerabilities")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cvss_score:>5")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertIn("results", result)
        self.assertEqual(result["results"], ["cve_id_1"])
        self.assertEqual(result["pagination"]["total"], 1)

    def test_search_images_vulnerabilities_error(self):
        """Test search for images vulnerabilities with API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid sort"}]},
        }
        result = self.module.search_images_vulnerabilities(sort="1|1")
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
