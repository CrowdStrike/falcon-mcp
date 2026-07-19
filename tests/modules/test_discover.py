"""
Unit tests for the Discover module.
"""

import unittest
from unittest.mock import MagicMock

from mcp.server import FastMCP

from falcon_mcp.client import FalconClient
from falcon_mcp.modules.discover import DiscoverModule


class TestDiscoverModule(unittest.TestCase):
    """Test cases for the Discover module."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=FalconClient)
        self.module = DiscoverModule(self.client)
        self.server = MagicMock(spec=FastMCP)

    def test_register_tools(self):
        """Test that tools are registered correctly."""
        self.module.register_tools(self.server)
        self.assertEqual(self.server.add_tool.call_count, 2)
        self.assertEqual(len(self.module.tools), 2)
        self.assertEqual(self.module.tools[0], "falcon_search_applications")
        self.assertEqual(self.module.tools[1], "falcon_search_unmanaged_assets")

    def test_register_resources(self):
        """Test that resources are registered correctly."""
        self.module.register_resources(self.server)
        self.assertEqual(self.server.add_resource.call_count, 2)
        self.assertEqual(len(self.module.resources), 2)
        self.assertEqual(
            str(self.module.resources[0]), "falcon://discover/applications/fql-guide"
        )
        self.assertEqual(
            str(self.module.resources[1]), "falcon://discover/hosts/fql-guide"
        )

    def test_search_applications(self):
        """Test search_applications method."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
                "resources": [{"id": "app1", "name": "Chrome"}],
            },
        }
        self.client.command.return_value = mock_response

        result = self.module.search_applications(filter="name:'Chrome'")

        first_call = self.client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "combined_applications")
        self.assertEqual(first_call[1]["parameters"]["filter"], "name:'Chrome'")
        self.assertEqual(result["results"], [{"id": "app1", "name": "Chrome"}])
        self.assertEqual(result["pagination"]["total"], 1)
        self.assertEqual(result["filter_used"], "name:'Chrome'")

    def test_search_applications_with_error(self):
        """Test search_applications method when an error occurs."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Something went wrong"}]},
        }
        self.client.command.return_value = mock_response

        result = self.module.search_applications(filter="name:'Chrome'")

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_search_applications_with_all_params(self):
        """Test search_applications method with all parameters."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 50, "total": 1}},
                "resources": [{"id": "app1", "name": "Chrome"}],
            },
        }
        self.client.command.return_value = mock_response

        result = self.module.search_applications(
            filter="name:'Chrome'",
            facet="host_info",
            limit=50,
            sort="name.asc",
        )

        first_call = self.client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "combined_applications")
        params = first_call[1]["parameters"]
        self.assertEqual(params["filter"], "name:'Chrome'")
        self.assertEqual(params["facet"], "host_info")
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["sort"], "name.asc")
        self.assertEqual(result["results"], [{"id": "app1", "name": "Chrome"}])

    def test_search_unmanaged_assets(self):
        """Test search_unmanaged_assets method."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
                "resources": [{"device_id": "host1", "hostname": "PC-001"}],
            },
        }
        self.client.command.return_value = mock_response

        result = self.module.search_unmanaged_assets(filter="platform_name:'Windows'")

        first_call = self.client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "combined_hosts")
        self.assertEqual(
            first_call[1]["parameters"]["filter"],
            "entity_type:'unmanaged'+platform_name:'Windows'",
        )
        self.assertEqual(
            result["results"], [{"device_id": "host1", "hostname": "PC-001"}]
        )

    def test_search_unmanaged_assets_without_filter(self):
        """Test search_unmanaged_assets method without user filter."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
                "resources": [{"device_id": "host1", "hostname": "PC-001"}],
            },
        }
        self.client.command.return_value = mock_response

        result = self.module.search_unmanaged_assets(filter=None)

        first_call = self.client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "combined_hosts")
        self.assertEqual(
            first_call[1]["parameters"]["filter"], "entity_type:'unmanaged'"
        )
        self.assertEqual(
            result["results"], [{"device_id": "host1", "hostname": "PC-001"}]
        )

    def test_search_unmanaged_assets_with_error(self):
        """Test search_unmanaged_assets method when an error occurs."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Something went wrong"}]},
        }
        self.client.command.return_value = mock_response

        result = self.module.search_unmanaged_assets(filter="platform_name:'Windows'")

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_search_unmanaged_assets_with_all_params(self):
        """Test search_unmanaged_assets method with all parameters."""
        mock_response = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 10, "limit": 50, "total": 1}},
                "resources": [{"device_id": "host1", "hostname": "PC-001"}],
            },
        }
        self.client.command.return_value = mock_response

        result = self.module.search_unmanaged_assets(
            filter="criticality:'Critical'",
            limit=50,
            offset=10,
            sort="hostname.asc",
        )

        first_call = self.client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "combined_hosts")
        params = first_call[1]["parameters"]
        self.assertEqual(
            params["filter"], "entity_type:'unmanaged'+criticality:'Critical'"
        )
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["offset"], 10)
        self.assertEqual(params["sort"], "hostname.asc")
        self.assertEqual(
            result["results"], [{"device_id": "host1", "hostname": "PC-001"}]
        )


if __name__ == "__main__":
    unittest.main()
