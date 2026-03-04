"""
Tests for the Firewall module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.firewall import FirewallModule
from tests.modules.utils.test_modules import TestModules


class TestFirewallModule(TestModules):
    """Test cases for the Firewall module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(FirewallModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_firewall_rules",
            "falcon_search_firewall_rule_groups",
            "falcon_search_firewall_policy_rules",
            "falcon_create_firewall_rule_group",
            "falcon_delete_firewall_rule_groups",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_firewall_rules_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_firewall_rules", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_create_firewall_rule_group",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_firewall_rule_groups",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_search_firewall_rules_success(self):
        """Test searching firewall rules and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule-id-1", "rule-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule-id-1", "name": "Rule 1", "platform": "windows"},
                    {"id": "rule-id-2", "name": "Rule 2", "platform": "windows"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_firewall_rules(
            filter="enabled:true",
            limit=20,
            offset=0,
            sort="modified_on.desc",
            q=None,
            after=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "query_rules")
        self.assertEqual(first_call[1]["parameters"]["filter"], "enabled:true")
        self.assertEqual(first_call[1]["parameters"]["limit"], 20)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "modified_on.desc")

        self.assertEqual(second_call[0][0], "get_rules")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["rule-id-1", "rule-id-2"])
        self.assertEqual(len(result), 2)

    def test_search_firewall_rules_empty_with_filter(self):
        """Test rule search empty results with filter returns FQL guide wrapper."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_firewall_rules(
            filter="name:'DoesNotExist*'",
            limit=10,
            offset=None,
            sort=None,
            q=None,
            after=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_firewall_rule_groups_success(self):
        """Test searching firewall rule groups and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["group-id-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "group-id-1", "name": "Default Group", "platform": "windows"}
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_firewall_rule_groups(
            filter="enabled:true",
            limit=10,
            offset=0,
            sort="modified_on.desc",
            q=None,
            after=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "query_rule_groups")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "get_rule_groups")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-id-1")

    def test_search_firewall_policy_rules_success(self):
        """Test searching policy rules and fetching full rule details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule-id-10"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule-id-10", "name": "Policy Rule", "platform": "windows"}
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_firewall_policy_rules(
            policy_id="policy-1",
            filter="enabled:true",
            limit=10,
            offset=0,
            sort="modified_on.desc",
            q=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "query_policy_rules")
        self.assertEqual(first_call[1]["parameters"]["id"], "policy-1")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "get_rules")
        self.assertEqual(len(result), 1)

    def test_create_firewall_rule_group_success(self):
        """Test creating a firewall rule group with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {
                "resources": [
                    {"id": "group-id-1", "name": "Test Group", "platform": "windows"}
                ]
            },
        }

        result = self.module.create_firewall_rule_group(
            name="Test Group",
            platform="windows",
            rules=[{"name": "Rule 1", "action": "ALLOW"}],
            description="Test firewall group",
            enabled=True,
            clone_id=None,
            library=None,
            comment="Create for tests",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "create_rule_group",
            parameters={"comment": "Create for tests"},
            body={
                "name": "Test Group",
                "platform": "windows",
                "enabled": True,
                "description": "Test firewall group",
                "rules": [{"name": "Rule 1", "action": "ALLOW"}],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-id-1")

    def test_create_firewall_rule_group_validation_missing_name_platform(self):
        """Test create validation when name/platform are missing."""
        result = self.module.create_firewall_rule_group(
            name=None,
            platform=None,
            rules=None,
            description=None,
            enabled=True,
            clone_id=None,
            library=None,
            comment=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_firewall_rule_group_validation_missing_rules_and_clone(self):
        """Test create validation when neither rules nor clone_id is provided."""
        result = self.module.create_firewall_rule_group(
            name="Test Group",
            platform="windows",
            rules=None,
            description=None,
            enabled=True,
            clone_id=None,
            library=None,
            comment=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_firewall_rule_groups_success(self):
        """Test deleting firewall rule groups by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-id-1"}]},
        }

        result = self.module.delete_firewall_rule_groups(
            ids=["group-id-1"],
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "delete_rule_groups",
            parameters={"ids": ["group-id-1"], "comment": "cleanup"},
        )
        self.assertEqual(len(result), 1)

    def test_delete_firewall_rule_groups_validation(self):
        """Test delete validation when ids are missing."""
        result = self.module.delete_firewall_rule_groups(ids=None, comment=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()

