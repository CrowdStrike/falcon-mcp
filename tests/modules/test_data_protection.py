"""
Tests for the Data Protection module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.data_protection import DataProtectionModule
from tests.modules.utils.test_modules import TestModules


class TestDataProtectionModule(TestModules):
    """Test cases for the Data Protection module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DataProtectionModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_data_protection_classifications",
            "falcon_search_data_protection_policies",
            "falcon_search_data_protection_content_patterns",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_data_protection_classifications_fql_guide",
            "falcon_search_data_protection_policies_fql_guide",
            "falcon_search_data_protection_content_patterns_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_all_tools_are_read_only(self):
        """Verify all Data Protection tools have read-only annotations."""
        self.module.register_tools(self.mock_server)
        for call in self.mock_server.add_tool.call_args_list:
            self.assertEqual(
                call.kwargs.get("annotations"),
                READ_ONLY_ANNOTATIONS,
                f"Tool {call.kwargs.get('name')} should be read-only",
            )

    # --- Classifications ---

    def test_search_classifications_success(self):
        """Test searching classifications with successful two-step response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cls-id-1", "cls-id-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "cls-id-1",
                        "name": "Credit Card Detection",
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                    {
                        "id": "cls-id-2",
                        "name": "SSN Detection",
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_classifications(
            filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Credit Card Detection")

    def test_search_classifications_reorders_to_match_sorted_ids(self):
        """When the get step returns classifications out of order, the result is
        reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cls-id-b", "cls-id-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "cls-id-a", "name": "Classification A"},
                    {"id": "cls-id-b", "name": "Classification B"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_classifications(
            filter=None, limit=100, offset=0, sort="created_at.desc"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "cls-id-b")
        self.assertEqual(result[1]["id"], "cls-id-a")

    def test_search_classifications_empty_results(self):
        """Test that empty search returns clean empty response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_data_protection_classifications(
            filter="name:~'nonexistent'", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["filter_used"], "name:~'nonexistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_classifications_error_response(self):
        """Test that an API error returns FQL guide with error hint."""
        error_response = {
            "status_code": 400,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "invalid filter key: foo"}],
            },
        }
        self.mock_client.command.side_effect = [error_response]

        result = self.module.search_data_protection_classifications(
            filter="foo:'bar'", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])

    # --- Policies ---

    def test_search_policies_success(self):
        """Test searching policies with platform_name and two-step response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["pol-id-1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "pol-id-1",
                        "name": "Windows Data Protection Policy",
                        "platform_name": "win",
                        "is_enabled": True,
                    }
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_policies(
            platform_name="win", filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["platform_name"], "win")

    def test_search_policies_reorders_to_match_sorted_ids(self):
        """When the get step returns policies out of order, the result is
        reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["pol-id-b", "pol-id-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "pol-id-a", "name": "Policy A", "platform_name": "win"},
                    {"id": "pol-id-b", "name": "Policy B", "platform_name": "win"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_policies(
            platform_name="win", filter=None, limit=100, offset=0, sort="created_at.desc"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "pol-id-b")
        self.assertEqual(result[1]["id"], "pol-id-a")

    def test_search_policies_passes_platform_name(self):
        """Test that platform_name is sent to the query API."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        self.module.search_data_protection_policies(
            platform_name="mac", filter=None, limit=100, offset=0, sort=None
        )

        call_args = self.mock_client.command.call_args
        params = call_args.kwargs.get("parameters") or call_args[1].get("parameters", {})
        self.assertEqual(params.get("platform_name"), "mac")

    def test_search_policies_empty_results(self):
        """Test that empty policy search returns clean empty response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_data_protection_policies(
            platform_name="win", filter="is_enabled:false", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertNotIn("fql_guide", result)

    def test_search_policies_error_response(self):
        """Test that policy error returns FQL guide."""
        error_response = {
            "status_code": 400,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "platform_name must be 'win' or 'mac'"}],
            },
        }
        self.mock_client.command.side_effect = [error_response]

        result = self.module.search_data_protection_policies(
            platform_name="invalid", filter=None, limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])

    # --- Content Patterns ---

    def test_search_content_patterns_success(self):
        """Test searching content patterns with successful two-step response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cp-id-1", "cp-id-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "cp-id-1",
                        "name": "Credit Card Regex",
                        "type": "predefined",
                        "category": "Financial",
                    },
                    {
                        "id": "cp-id-2",
                        "name": "Custom SSN Pattern",
                        "type": "custom",
                        "category": "Custom",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_content_patterns(
            filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "predefined")

    def test_search_content_patterns_reorders_to_match_sorted_ids(self):
        """When the get step returns content patterns out of order, the result is
        reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cp-id-b", "cp-id-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "cp-id-a", "name": "Pattern A", "type": "predefined"},
                    {"id": "cp-id-b", "name": "Pattern B", "type": "custom"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_protection_content_patterns(
            filter=None, limit=100, offset=0, sort="created_at.desc"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "cp-id-b")
        self.assertEqual(result[1]["id"], "cp-id-a")

    def test_search_content_patterns_empty_results(self):
        """Test that empty content pattern search returns clean empty response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_data_protection_content_patterns(
            filter="type:'nonexistent'", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertNotIn("fql_guide", result)

    def test_search_content_patterns_error_response(self):
        """Test that content pattern error returns FQL guide."""
        error_response = {
            "status_code": 400,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "invalid fql filter properties: [bad]"}],
            },
        }
        self.mock_client.command.side_effect = [error_response]

        result = self.module.search_data_protection_content_patterns(
            filter="bad:'val'", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])


if __name__ == "__main__":
    unittest.main()
