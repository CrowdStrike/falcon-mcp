"""
Tests for the IOC module.
"""

import unittest

from falcon_mcp.modules.ioc import IOCModule
from tests.modules.utils.test_modules import TestModules


class TestIOCModule(TestModules):
    """Test cases for the IOC module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IOCModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_iocs",
            "falcon_add_ioc",
            "falcon_remove_iocs",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_iocs_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_iocs_success(self):
        """Test searching IOCs and fetching full details."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["ioc-id-1", "ioc-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "ioc-id-1", "type": "domain", "value": "bad.example"},
                    {"id": "ioc-id-2", "type": "ipv4", "value": "1.2.3.4"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_iocs(
            filter="type:'domain'",
            limit=25,
            offset=0,
            sort="modified_on.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "indicator_search_v1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "type:'domain'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "modified_on.desc")

        self.assertEqual(second_call[0][0], "indicator_get_v1")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["ioc-id-1", "ioc-id-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "ioc-id-1")

    def test_search_iocs_empty_results_returns_fql_guide(self):
        """Test IOC search empty results include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_iocs(filter="value:'nothing-here'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_search_iocs_error_returns_fql_guide(self):
        """Test IOC search errors include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_iocs(filter="bad filter")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)

    def test_add_ioc_success(self):
        """Test adding a single IOC."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "ioc-id-1", "type": "domain", "value": "bad.example"}
                ]
            },
        }

        result = self.module.add_ioc(
            type="domain",
            value="bad.example",
            action="detect",
            source="mcp-tests",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=["tag1"],
            metadata=None,
            filename=None,
            comment="Create IOC for testing",
            indicators=None,
            ignore_warnings=False,
            retrodetects=None,
        )

        self.mock_client.command.assert_called_once_with(
            "indicator_create_v1",
            parameters={"ignore_warnings": False},
            body={
                "comment": "Create IOC for testing",
                "indicators": [
                    {
                        "type": "domain",
                        "value": "bad.example",
                        "action": "detect",
                        "source": "mcp-tests",
                        "tags": ["tag1"],
                    }
                ],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ioc-id-1")

    def test_add_ioc_with_retrodetects(self):
        """Test that retrodetects parameter is passed through to the API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "ioc-id-1", "type": "domain", "value": "bad.example"}
                ]
            },
        }

        self.module.add_ioc(
            type="domain",
            value="bad.example",
            action="detect",
            source="mcp",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=None,
            metadata=None,
            filename=None,
            comment=None,
            indicators=None,
            ignore_warnings=False,
            retrodetects=True,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["retrodetects"], True)

    def test_add_ioc_bulk_indicators(self):
        """Test adding IOCs via bulk indicators payload."""
        bulk_indicators = [
            {"type": "domain", "value": "evil1.example", "action": "detect", "source": "mcp"},
            {"type": "ipv4", "value": "10.0.0.1", "action": "prevent", "source": "mcp"},
        ]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "ioc-id-1", "type": "domain", "value": "evil1.example"},
                    {"id": "ioc-id-2", "type": "ipv4", "value": "10.0.0.1"},
                ]
            },
        }

        result = self.module.add_ioc(
            type=None,
            value=None,
            action="detect",
            source="mcp",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=None,
            metadata=None,
            filename=None,
            indicators=bulk_indicators,
            comment="Bulk import",
            ignore_warnings=False,
            retrodetects=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["body"]["indicators"], bulk_indicators)
        self.assertEqual(call_args[1]["body"]["comment"], "Bulk import")
        self.assertEqual(len(result), 2)

    def test_add_ioc_validation_error(self):
        """Test add_ioc requires type/value when indicators are not provided."""
        result = self.module.add_ioc(
            type=None,
            value=None,
            action="detect",
            source="mcp",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=None,
            metadata=None,
            filename=None,
            comment=None,
            indicators=None,
            ignore_warnings=False,
            retrodetects=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_remove_iocs_by_ids_success(self):
        """Test removing IOCs by explicit IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioc-id-1"}]},
        }

        result = self.module.remove_iocs(
            ids=["ioc-id-1"], filter=None, comment="cleanup", from_parent=None
        )

        self.mock_client.command.assert_called_once_with(
            "indicator_delete_v1",
            parameters={"ids": ["ioc-id-1"], "comment": "cleanup"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ioc-id-1")

    def test_remove_iocs_by_filter(self):
        """Test removing IOCs by FQL filter."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioc-id-1"}, {"id": "ioc-id-2"}]},
        }

        result = self.module.remove_iocs(
            ids=None,
            filter="source:'mcp'+expired:true",
            comment="cleanup expired IOCs",
            from_parent=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "indicator_delete_v1")
        self.assertEqual(
            call_args[1]["parameters"]["filter"], "source:'mcp'+expired:true"
        )
        self.assertEqual(call_args[1]["parameters"]["comment"], "cleanup expired IOCs")
        self.assertEqual(len(result), 2)

    def test_remove_iocs_validation_error(self):
        """Test remove_iocs requires either ids or filter."""
        result = self.module.remove_iocs(
            ids=None, filter=None, comment=None, from_parent=None
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # Security validation tests

    def test_search_iocs_with_special_characters_in_filter(self):
        """Test that special characters in filter are passed through safely."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "type:'domain'+value:*';DROP TABLE--*"
        self.module.search_iocs(filter=filter_with_special)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_remove_iocs_with_invalid_ids(self):
        """Test removing IOCs with malformed IDs returns API error."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "IOC not found"}]},
        }

        result = self.module.remove_iocs(
            ids=["not-a-real-id-!!!"], filter=None, comment=None, from_parent=None
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_add_ioc_permission_error(self):
        """Test add_ioc with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.add_ioc(
            type="domain",
            value="bad.example",
            action="detect",
            source="mcp",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=None,
            metadata=None,
            filename=None,
            comment=None,
            indicators=None,
            ignore_warnings=False,
            retrodetects=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_remove_iocs_permission_error(self):
        """Test remove_iocs with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.remove_iocs(
            ids=["ioc-id-1"], filter=None, comment=None, from_parent=None
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_add_ioc_malformed_indicators_list(self):
        """Test add_ioc with empty indicators list triggers validation error."""
        result = self.module.add_ioc(
            type=None,
            value=None,
            action="detect",
            source="mcp",
            severity=None,
            description=None,
            expiration=None,
            applied_globally=None,
            mobile_action=None,
            platforms=None,
            host_groups=None,
            tags=None,
            metadata=None,
            filename=None,
            comment=None,
            indicators=[],
            ignore_warnings=False,
            retrodetects=None,
        )

        # Empty list is falsy, so it falls through to single-IOC validation
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_iocs_with_long_filter_value(self):
        """Test that extremely long filter values are passed through to the API."""
        long_value = "a" * 10000
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_iocs(filter=f"value:'{long_value}'")

        call_args = self.mock_client.command.call_args
        self.assertIn(long_value, call_args[1]["parameters"]["filter"])


if __name__ == "__main__":
    unittest.main()


