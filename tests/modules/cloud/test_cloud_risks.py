"""
Tests for cloud risks and cloud groups tools (part of CloudModule).
"""

import unittest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudRisksTools(TestModules):
    """Test cases for the cloud risks and cloud groups tools within CloudModule."""

    def setUp(self):
        self.setup_module(CloudModule)

    def test_search_cloud_risks_success(self):
        """Test search_cloud_risks returns entities on success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "risk-1", "severity": "critical", "status": "open"},
                    {"id": "risk-2", "severity": "high", "status": "open"},
                ]
            },
        }
        result = self.module.search_cloud_risks(
            filter="severity:'critical'", limit=10, offset=None, sort=None
        )
        self.assertEqual(self.mock_client.command.call_args[0][0], "combined_cloud_risks")
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "risk-1")

    def test_search_cloud_risks_empty(self):
        """Test search_cloud_risks returns empty list when no results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_cloud_risks(filter=None, limit=100, offset=None, sort=None)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 0)

    def test_search_cloud_risks_api_error(self):
        """Test search_cloud_risks returns error dict on API failure."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        result = self.module.search_cloud_risks(filter="invalid!", limit=10, offset=None, sort=None)
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_search_cloud_risks_passes_all_params(self):
        """Test search_cloud_risks passes filter, sort, limit, offset to API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.search_cloud_risks(
            filter="cloud_provider:'aws'",
            limit=50,
            offset=100,
            sort="severity|desc",
        )
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["filter"], "cloud_provider:'aws'")
        self.assertEqual(call_params["limit"], 50)
        self.assertEqual(call_params["offset"], 100)
        self.assertEqual(call_params["sort"], "severity|desc")

    def test_search_cloud_groups_success(self):
        """Test search_cloud_groups returns entities on success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "grp-1", "name": "prod-group", "environment": "production"},
                ]
            },
        }
        result = self.module.search_cloud_groups(filter=None, limit=100, offset=None, sort=None)
        self.mock_client.command.assert_called_once_with(
            "ListCloudGroupsExternal",
            parameters={"limit": 100},
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"][0]["id"], "grp-1")

    def test_search_cloud_groups_with_filter(self):
        """Test search_cloud_groups passes filter param."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.search_cloud_groups(
            filter="environment:'production'", limit=10, offset=None, sort=None
        )
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["filter"], "environment:'production'")

    def test_search_cloud_groups_api_error(self):
        """Test search_cloud_groups returns error dict on API failure."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }
        result = self.module.search_cloud_groups(filter=None, limit=100, offset=None, sort=None)
        self.assertIsInstance(result, (dict, list))
        if isinstance(result, list):
            self.assertIn("error", result[0])
        else:
            self.assertIn("error", result)

    def test_get_cloud_groups_success(self):
        """Test get_cloud_groups fetches entities by ID."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "grp-1", "name": "prod-group"}]},
        }
        result = self.module.get_cloud_groups(ids=["grp-1"])
        self.mock_client.command.assert_called_once_with(
            "ListCloudGroupsByIDExternal",
            parameters={"ids": ["grp-1"]},
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], "grp-1")

    def test_get_cloud_groups_multiple_ids(self):
        """Test get_cloud_groups accepts multiple IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.get_cloud_groups(ids=["grp-1", "grp-2"])
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["ids"], ["grp-1", "grp-2"])


if __name__ == "__main__":
    unittest.main()
