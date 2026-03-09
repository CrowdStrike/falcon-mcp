"""
Tests for the Custom IOA module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.custom_ioa import CustomIOAModule
from tests.modules.utils.test_modules import TestModules


class TestCustomIOAModule(TestModules):
    """Test cases for the Custom IOA module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CustomIOAModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_ioa_rule_groups",
            "falcon_get_ioa_platforms",
            "falcon_get_ioa_rule_types",
            "falcon_create_ioa_rule_group",
            "falcon_update_ioa_rule_group",
            "falcon_delete_ioa_rule_groups",
            "falcon_create_ioa_rule",
            "falcon_update_ioa_rule",
            "falcon_delete_ioa_rules",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_ioa_rule_groups_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # --- search_ioa_rule_groups ---

    def test_search_ioa_rule_groups_success(self):
        """Test searching rule groups returns full group data."""
        rule_groups = [
            {
                "id": "rg-001",
                "name": "Windows Rules",
                "platform": "windows",
                "enabled": True,
                "version": 1,
                "rules": [],
            },
            {
                "id": "rg-002",
                "name": "Mac Rules",
                "platform": "mac",
                "enabled": True,
                "version": 2,
                "rules": [],
            },
        ]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": rule_groups},
        }

        result = self.module.search_ioa_rule_groups(
            filter="platform:'windows'",
            limit=25,
            offset=None,
            sort=None,
            q=None,
        )

        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "query_rule_groups_full")
        self.assertEqual(call_args[1]["parameters"]["filter"], "platform:'windows'")
        self.assertEqual(call_args[1]["parameters"]["limit"], 25)
        self.assertNotIn("offset", call_args[1]["parameters"])
        self.assertNotIn("sort", call_args[1]["parameters"])
        self.assertNotIn("q", call_args[1]["parameters"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "rg-001")

    def test_search_ioa_rule_groups_empty_returns_fql_guide(self):
        """Test that empty results return FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_ioa_rule_groups(filter="name:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_search_ioa_rule_groups_error_returns_fql_guide(self):
        """Test that errors return FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter syntax"}]},
        }

        result = self.module.search_ioa_rule_groups(filter="bad filter syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error", result["hint"])

    def test_search_ioa_rule_groups_no_filter(self):
        """Test searching without filter omits filter param."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-001"}]},
        }

        self.module.search_ioa_rule_groups(
            filter=None,
            offset=None,
            sort=None,
            q=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertNotIn("filter", call_args[1]["parameters"])

    # --- get_ioa_platforms ---

    def test_get_ioa_platforms_success(self):
        """Test getting available platforms returns platform details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["windows", "mac", "linux"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "windows", "name": "Windows"},
                    {"id": "mac", "name": "Mac"},
                    {"id": "linux", "name": "Linux"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.get_ioa_platforms()

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(first_call[0][0], "query_platformsMixin0")
        self.assertEqual(second_call[0][0], "get_platformsMixin0")
        self.assertEqual(len(result), 3)

    def test_get_ioa_platforms_empty(self):
        """Test getting platforms when none available returns empty list."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_ioa_platforms()

        self.mock_client.command.assert_called_once()
        self.assertEqual(result, [])

    def test_get_ioa_platforms_query_error(self):
        """Test that query errors are surfaced correctly."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.get_ioa_platforms()

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # --- get_ioa_rule_types ---

    def test_get_ioa_rule_types_success(self):
        """Test getting rule types returns type details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rt-001", "rt-002"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rt-001", "name": "Process Creation", "platform": "windows"},
                    {"id": "rt-002", "name": "Network Connection", "platform": "windows"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.get_ioa_rule_types(limit=50)

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(first_call[0][0], "query_rule_types")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.assertEqual(second_call[0][0], "get_rule_types")
        self.assertEqual(len(result), 2)

    def test_get_ioa_rule_types_empty(self):
        """Test getting rule types when none exist returns empty list."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_ioa_rule_types()

        self.mock_client.command.assert_called_once()
        self.assertEqual(result, [])

    # --- create_ioa_rule_group ---

    def test_create_ioa_rule_group_success(self):
        """Test creating a rule group with all fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"id": "rg-001", "name": "Windows IOA Rules", "platform": "windows"}]
            },
        }

        result = self.module.create_ioa_rule_group(
            name="Windows IOA Rules",
            platform="windows",
            description="Rules for detecting suspicious Windows activity",
            comment="Created for testing",
        )

        self.mock_client.command.assert_called_once_with(
            "create_rule_groupMixin0",
            body={
                "name": "Windows IOA Rules",
                "platform": "windows",
                "description": "Rules for detecting suspicious Windows activity",
                "comment": "Created for testing",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "rg-001")

    def test_create_ioa_rule_group_minimal(self):
        """Test creating a rule group with only required fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-002", "name": "Mac Rules", "platform": "mac"}]},
        }

        result = self.module.create_ioa_rule_group(
            name="Mac Rules",
            platform="mac",
            description=None,
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["body"]["name"], "Mac Rules")
        self.assertEqual(call_args[1]["body"]["platform"], "mac")
        self.assertNotIn("description", call_args[1]["body"])
        self.assertNotIn("comment", call_args[1]["body"])
        self.assertEqual(len(result), 1)

    def test_create_ioa_rule_group_error(self):
        """Test create rule group error is returned correctly."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid platform"}]},
        }

        result = self.module.create_ioa_rule_group(
            name="Test Group",
            platform="invalid_platform",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # --- update_ioa_rule_group ---

    def test_update_ioa_rule_group_enable(self):
        """Test enabling a rule group."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-001", "enabled": True}]},
        }

        result = self.module.update_ioa_rule_group(
            id="rg-001",
            rulegroup_version=3,
            name=None,
            description=None,
            enabled=True,
            comment="Enabling for production",
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "update_rule_groupMixin0")
        self.assertEqual(call_args[1]["body"]["id"], "rg-001")
        self.assertEqual(call_args[1]["body"]["rulegroup_version"], 3)
        self.assertEqual(call_args[1]["body"]["enabled"], True)
        self.assertEqual(call_args[1]["body"]["comment"], "Enabling for production")
        self.assertNotIn("name", call_args[1]["body"])
        self.assertEqual(len(result), 1)

    def test_update_ioa_rule_group_rename(self):
        """Test renaming a rule group."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-001", "name": "New Name"}]},
        }

        result = self.module.update_ioa_rule_group(
            id="rg-001",
            rulegroup_version=2,
            name="New Name",
            description=None,
            enabled=None,
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["body"]["name"], "New Name")
        self.assertNotIn("enabled", call_args[1]["body"])
        self.assertEqual(len(result), 1)

    # --- delete_ioa_rule_groups ---

    def test_delete_ioa_rule_groups_success(self):
        """Test deleting rule groups by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-001"}]},
        }

        result = self.module.delete_ioa_rule_groups(
            ids=["rg-001"],
            comment="Cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "delete_rule_groupsMixin0",
            parameters={"ids": ["rg-001"], "comment": "Cleanup"},
        )
        self.assertEqual(len(result), 1)

    def test_delete_ioa_rule_groups_multiple(self):
        """Test deleting multiple rule groups."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rg-001"}, {"id": "rg-002"}]},
        }

        result = self.module.delete_ioa_rule_groups(
            ids=["rg-001", "rg-002"],
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["ids"], ["rg-001", "rg-002"])
        self.assertNotIn("comment", call_args[1]["parameters"])
        self.assertEqual(len(result), 2)

    def test_delete_ioa_rule_groups_validation_error(self):
        """Test delete requires at least one ID."""
        result = self.module.delete_ioa_rule_groups(ids=[])

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # --- create_ioa_rule ---

    def test_create_ioa_rule_success(self):
        """Test creating a behavioral rule within a rule group."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "instance_id": "rule-001",
                        "name": "Block cmd.exe from Office",
                        "rulegroup_id": "rg-001",
                    }
                ]
            },
        }

        field_values = [
            {
                "name": "GrandparentImageFilename",
                "value": ".*\\\\winword\\.exe",
                "label": "Grand Parent Image Filename",
            }
        ]

        result = self.module.create_ioa_rule(
            rulegroup_id="rg-001",
            name="Block cmd.exe from Office",
            ruletype_id="rt-001",
            disposition_id=10,
            pattern_severity="high",
            field_values=field_values,
            description="Detects cmd.exe spawned from Office applications",
            comment="New rule for lateral movement detection",
        )

        self.mock_client.command.assert_called_once_with(
            "create_rule",
            body={
                "rulegroup_id": "rg-001",
                "name": "Block cmd.exe from Office",
                "ruletype_id": "rt-001",
                "disposition_id": 10,
                "pattern_severity": "high",
                "field_values": field_values,
                "description": "Detects cmd.exe spawned from Office applications",
                "comment": "New rule for lateral movement detection",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["instance_id"], "rule-001")

    def test_create_ioa_rule_minimal(self):
        """Test creating a rule with only required fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"instance_id": "rule-002"}]},
        }

        result = self.module.create_ioa_rule(
            rulegroup_id="rg-001",
            name="Test Rule",
            ruletype_id="rt-001",
            disposition_id=20,
            pattern_severity="medium",
            field_values=[],
            description=None,
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertNotIn("description", call_args[1]["body"])
        self.assertNotIn("comment", call_args[1]["body"])
        self.assertEqual(len(result), 1)

    def test_create_ioa_rule_error(self):
        """Test create rule error is returned."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid ruletype_id"}]},
        }

        result = self.module.create_ioa_rule(
            rulegroup_id="rg-001",
            name="Bad Rule",
            ruletype_id="invalid-id",
            disposition_id=10,
            pattern_severity="high",
            field_values=[],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # --- update_ioa_rule ---

    def test_update_ioa_rule_enable(self):
        """Test enabling a rule."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"instance_id": "rule-001", "enabled": True}]},
        }

        result = self.module.update_ioa_rule(
            rulegroup_id="rg-001",
            rulegroup_version=5,
            instance_id="rule-001",
            enabled=True,
            comment="Enabling rule",
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "update_rules_v2")
        body = call_args[1]["body"]
        self.assertEqual(body["rulegroup_id"], "rg-001")
        self.assertEqual(body["rulegroup_version"], 5)
        self.assertEqual(body["comment"], "Enabling rule")
        self.assertEqual(len(body["rule_updates"]), 1)
        self.assertEqual(body["rule_updates"][0]["instance_id"], "rule-001")
        self.assertEqual(body["rule_updates"][0]["enabled"], True)
        self.assertEqual(len(result), 1)

    def test_update_ioa_rule_change_severity(self):
        """Test changing a rule's severity."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"instance_id": "rule-001", "pattern_severity": "critical"}]},
        }

        result = self.module.update_ioa_rule(
            rulegroup_id="rg-001",
            rulegroup_version=3,
            instance_id="rule-001",
            name=None,
            description=None,
            enabled=None,
            pattern_severity="critical",
            disposition_id=None,
            field_values=None,
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        rule_update = call_args[1]["body"]["rule_updates"][0]
        self.assertEqual(rule_update["pattern_severity"], "critical")
        self.assertNotIn("enabled", rule_update)
        self.assertNotIn("name", rule_update)
        self.assertEqual(len(result), 1)

    def test_update_ioa_rule_with_field_values(self):
        """Test updating a rule's field values."""
        new_field_values = [{"name": "ImageFilename", "value": ".*\\\\malware\\.exe"}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"instance_id": "rule-001"}]},
        }

        self.module.update_ioa_rule(
            rulegroup_id="rg-001",
            rulegroup_version=2,
            instance_id="rule-001",
            field_values=new_field_values,
        )

        call_args = self.mock_client.command.call_args
        rule_update = call_args[1]["body"]["rule_updates"][0]
        self.assertEqual(rule_update["field_values"], new_field_values)

    # --- delete_ioa_rules ---

    def test_delete_ioa_rules_success(self):
        """Test deleting rules from a rule group."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule-001"}]},
        }

        result = self.module.delete_ioa_rules(
            rule_group_id="rg-001",
            ids=["rule-001"],
            comment="Cleanup old rule",
        )

        self.mock_client.command.assert_called_once_with(
            "delete_rules",
            parameters={
                "rule_group_id": "rg-001",
                "ids": ["rule-001"],
                "comment": "Cleanup old rule",
            },
        )
        self.assertEqual(len(result), 1)

    def test_delete_ioa_rules_multiple(self):
        """Test deleting multiple rules."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule-001"}, {"id": "rule-002"}]},
        }

        result = self.module.delete_ioa_rules(
            rule_group_id="rg-001",
            ids=["rule-001", "rule-002"],
            comment=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["ids"], ["rule-001", "rule-002"])
        self.assertNotIn("comment", call_args[1]["parameters"])
        self.assertEqual(len(result), 2)

    def test_delete_ioa_rules_validation_error(self):
        """Test delete rules requires at least one ID."""
        result = self.module.delete_ioa_rules(
            rule_group_id="rg-001",
            ids=[],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # --- Tool annotation tests ---

    def test_search_ioa_rule_groups_has_read_only_annotations(self):
        """Test that search_ioa_rule_groups is registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_ioa_rule_groups", READ_ONLY_ANNOTATIONS)

    def test_get_ioa_platforms_has_read_only_annotations(self):
        """Test that get_ioa_platforms is registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_ioa_platforms", READ_ONLY_ANNOTATIONS)

    def test_get_ioa_rule_types_has_read_only_annotations(self):
        """Test that get_ioa_rule_types is registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_ioa_rule_types", READ_ONLY_ANNOTATIONS)

    def test_create_ioa_rule_group_has_mutating_annotations(self):
        """Test that create_ioa_rule_group is registered with non-destructive write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_ioa_rule_group",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_ioa_rule_group_has_mutating_annotations(self):
        """Test that update_ioa_rule_group is registered with non-destructive idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_ioa_rule_group",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_delete_ioa_rule_groups_has_destructive_annotations(self):
        """Test that delete_ioa_rule_groups is registered with destructive annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_ioa_rule_groups",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_create_ioa_rule_has_mutating_annotations(self):
        """Test that create_ioa_rule is registered with non-destructive write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_ioa_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_ioa_rule_has_mutating_annotations(self):
        """Test that update_ioa_rule is registered with idempotent write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_ioa_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_delete_ioa_rules_has_destructive_annotations(self):
        """Test that delete_ioa_rules is registered with destructive annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_ioa_rules",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    # --- Permission / error handling tests ---

    def test_search_rule_groups_permission_error(self):
        """Test that permission errors are surfaced correctly."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.search_ioa_rule_groups()

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("error", result["results"][0])

    def test_create_rule_group_permission_error(self):
        """Test create rule group 403 error is surfaced."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.create_ioa_rule_group(
            name="Test",
            platform="windows",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_create_rule_permission_error(self):
        """Test create rule 403 error is surfaced."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.create_ioa_rule(
            rulegroup_id="rg-001",
            name="Test Rule",
            ruletype_id="rt-001",
            disposition_id=10,
            pattern_severity="high",
            field_values=[],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_delete_rule_groups_permission_error(self):
        """Test delete rule groups 403 error is surfaced."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.delete_ioa_rule_groups(ids=["rg-001"])

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
