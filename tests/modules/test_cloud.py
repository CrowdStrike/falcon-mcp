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
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_kubernetes_containers_fql_filter_guide",
            "falcon_images_vulnerabilities_fql_filter_guide",
            "falcon_search_cspm_assets_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

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

    def test_search_cspm_assets_success(self):
        """Test searching for CSPM assets with two-step pattern."""
        # Mock query response (returns IDs)
        query_response = {
            "status_code": 200,
            "body": {"resources": ["asset_1", "asset_2", "asset_3"]},
        }
        # Mock get response (returns full details)
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "asset_1", "cloud_provider": "AWS", "resource_type": "ec2-instance"},
                    {"id": "asset_2", "cloud_provider": "AWS", "resource_type": "s3-bucket"},
                    {"id": "asset_3", "cloud_provider": "Azure", "resource_type": "vm"},
                ]
            },
        }

        # Configure side_effect to return query then get
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_assets(
            filter="cloud_provider:'AWS'", limit=10
        )

        # Verify 2 API calls made
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Verify first call (query)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "cloud_security_assets_queries")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_provider:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        # Verify second call (get details)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], ["asset_1", "asset_2", "asset_3"]
        )

        # Verify result is full details, not just IDs
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("cloud_provider", result[0])
        self.assertIn("resource_type", result[0])

    def test_search_cspm_assets_batching(self):
        """Test CSPM assets search handles >100 IDs with batching."""
        # Mock 250 IDs
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}

        # Mock 3 batches (100 + 100 + 50)
        batch1_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(100)
        ]
        batch2_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(100, 200)
        ]
        batch3_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(200, 250)
        ]

        batch1 = {"status_code": 200, "body": {"resources": batch1_assets}}
        batch2 = {"status_code": 200, "body": {"resources": batch2_assets}}
        batch3 = {"status_code": 200, "body": {"resources": batch3_assets}}

        self.mock_client.command.side_effect = [
            query_response,
            batch1,
            batch2,
            batch3,
        ]

        result = self.module.search_cspm_assets(limit=1000)

        # Verify 4 calls: 1 query + 3 get batches
        self.assertEqual(self.mock_client.command.call_count, 4)

        # Verify batching calls - validate both length and content
        # Second call should contain IDs 0-99
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100)]
        )

        # Third call should contain IDs 100-199
        third_call = self.mock_client.command.call_args_list[2]
        self.assertEqual(third_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            third_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100, 200)]
        )

        # Fourth call should contain IDs 200-249
        fourth_call = self.mock_client.command.call_args_list[3]
        self.assertEqual(fourth_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            fourth_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(200, 250)]
        )

        # Verify all 250 assets returned
        self.assertEqual(len(result), 250)

    def test_search_cspm_assets_error_returns_fql_guide(self):
        """Test CSPM assets search returns FQL guide on error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_cspm_assets(filter="invalid::syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertIn("hint", result)
        self.assertIn("tag_key", result["fql_guide"])

    def test_search_cspm_assets_empty_returns_fql_guide(self):
        """Test CSPM assets search returns FQL guide on empty results."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = query_response

        result = self.module.search_cspm_assets(filter="cloud_provider:'NonExistent'")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertEqual(result["results"], [])
        self.assertIn("Cloud Resource Tag Filtering", result["fql_guide"])

    def test_search_cspm_assets_batch_error_fails_fast(self):
        """Test CSPM assets batching fails fast on batch error."""
        # Mock 250 IDs
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}

        # First batch succeeds, second batch fails
        batch1 = {
            "status_code": 200,
            "body": {"resources": [{"id": f"asset_{i}"} for i in range(100)]},
        }
        batch2_error = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }

        self.mock_client.command.side_effect = [
            query_response,
            batch1,
            batch2_error,
        ]

        result = self.module.search_cspm_assets(limit=1000)

        # Verify only 3 calls (query + batch1 + batch2 error)
        self.assertEqual(self.mock_client.command.call_count, 3)

        # Verify error returned (not partial results)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_cspm_assets_uses_params_true(self):
        """Test CSPM assets get request uses use_params=True for GET method."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["asset_1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "asset_1"}]},
        }

        self.mock_client.command.side_effect = [query_response, get_response]

        self.module.search_cspm_assets(limit=1)

        # Verify second call uses parameters (not body)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])


if __name__ == "__main__":
    unittest.main()

