"""
Tests for the Host Groups module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.host_groups import HostGroupsModule
from tests.modules.utils.test_modules import TestModules


class TestHostGroupsModule(TestModules):
    """Test cases for the Host Groups module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(HostGroupsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_host_groups",
            "falcon_search_host_group_members",
            "falcon_create_host_group",
            "falcon_update_host_group",
            "falcon_delete_host_groups",
            "falcon_perform_host_group_action",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_host_groups_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_host_groups_success(self):
        """Test searching host groups returns full details in a single call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "group-1",
                        "name": "Production Servers",
                        "group_type": "static",
                    },
                    {
                        "id": "group-2",
                        "name": "Windows Dynamic",
                        "group_type": "dynamic",
                    },
                ]
            },
        }

        result = self.module.search_host_groups(
            filter="group_type:'static'",
            limit=100,
            offset=0,
            sort="name.asc",
        )

        # Combined search is a SINGLE command call (no two-step query->get)
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "queryCombinedHostGroups")
        self.assertEqual(call_args[1]["parameters"]["filter"], "group_type:'static'")
        self.assertEqual(call_args[1]["parameters"]["sort"], "name.asc")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "group-1")

    def test_search_host_groups_empty_results_returns_fql_guide(self):
        """Test host group search empty results return clean empty response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_host_groups(filter="name:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["filter_used"], "name:'nonexistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_host_groups_error_returns_fql_guide(self):
        """Test host group search errors include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_host_groups(filter="bad filter")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)

    def test_search_host_group_members_success(self):
        """Test searching host group members returns full host details."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device-1", "hostname": "PC-1"},
                    {"device_id": "device-2", "hostname": "PC-2"},
                ]
            },
        }

        result = self.module.search_host_group_members(
            id="group-1",
            filter="platform_name:'Windows'",
            limit=100,
            offset=0,
            sort="hostname.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "queryCombinedGroupMembers")
        self.assertEqual(call_args[1]["parameters"]["id"], "group-1")
        self.assertEqual(
            call_args[1]["parameters"]["filter"], "platform_name:'Windows'"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["device_id"], "device-1")

    def test_search_host_group_members_error(self):
        """Test member search error returns wrapped error."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "Group not found"}]},
        }

        result = self.module.search_host_group_members(
            id="bad-group", filter=None, limit=100, offset=None, sort=None
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_create_host_group_static_success(self):
        """Test creating a static host group."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {
                "resources": [
                    {"id": "group-1", "name": "Critical Servers", "group_type": "static"}
                ]
            },
        }

        result = self.module.create_host_group(
            name="Critical Servers",
            group_type="static",
            description="Important hosts",
            assignment_rule=None,
        )

        self.mock_client.command.assert_called_once_with(
            "createHostGroups",
            body={
                "resources": [
                    {
                        "name": "Critical Servers",
                        "group_type": "static",
                        "description": "Important hosts",
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-1")

    def test_create_host_group_dynamic_with_assignment_rule(self):
        """Test creating a dynamic host group includes assignment_rule."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "group-2", "group_type": "dynamic"}]},
        }

        self.module.create_host_group(
            name="Windows Dynamic",
            group_type="dynamic",
            description=None,
            assignment_rule="platform_name:'Windows'",
        )

        call_args = self.mock_client.command.call_args
        resource = call_args[1]["body"]["resources"][0]
        self.assertEqual(resource["assignment_rule"], "platform_name:'Windows'")
        self.assertNotIn("description", resource)

    def test_update_host_group_success(self):
        """Test updating a host group."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1", "name": "Renamed"}]},
        }

        result = self.module.update_host_group(
            id="group-1",
            name="Renamed",
            description=None,
            assignment_rule=None,
        )

        self.mock_client.command.assert_called_once_with(
            "updateHostGroups",
            body={"resources": [{"id": "group-1", "name": "Renamed"}]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Renamed")

    def test_delete_host_groups_success(self):
        """Test deleting host groups sends IDs as query params."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["group-1"]},
        }

        result = self.module.delete_host_groups(ids=["group-1", "group-2"])

        self.mock_client.command.assert_called_once_with(
            "deleteHostGroups",
            parameters={"ids": ["group-1", "group-2"]},
        )
        self.assertIsInstance(result, list)

    def test_delete_host_groups_validation_error(self):
        """Test delete_host_groups requires ids."""
        result = self.module.delete_host_groups(ids=[])

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_host_group_action_add_hosts(self):
        """Test adding hosts to a group sends action_name and body correctly."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1"}]},
        }

        result = self.module.perform_host_group_action(
            action_name="add-hosts",
            ids=["group-1"],
            filter="platform_name:'Windows'",
        )

        self.mock_client.command.assert_called_once_with(
            "performGroupAction",
            parameters={"action_name": "add-hosts"},
            body={
                "ids": ["group-1"],
                "action_parameters": [
                    {"name": "filter", "value": "platform_name:'Windows'"}
                ],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-1")

    def test_perform_host_group_action_remove_hosts(self):
        """Test removing hosts from a group passes remove-hosts action."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1"}]},
        }

        self.module.perform_host_group_action(
            action_name="remove-hosts",
            ids=["group-1"],
            filter="device_id:['dev-1']",
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["action_name"], "remove-hosts")

    # Security validation tests

    def test_search_host_groups_with_special_characters_in_filter(self):
        """Test that special characters in filter are passed through safely."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "name:*';DROP TABLE--*"
        self.module.search_host_groups(filter=filter_with_special)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_create_host_group_permission_error(self):
        """Test create_host_group with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.create_host_group(
            name="Test",
            group_type="static",
            description=None,
            assignment_rule=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_delete_host_groups_permission_error(self):
        """Test delete_host_groups with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.delete_host_groups(ids=["group-1"])

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # Annotation tests

    def test_search_tools_have_read_only_annotations(self):
        """Test that search tools are registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_host_groups", READ_ONLY_ANNOTATIONS
        )
        self.assert_tool_annotations(
            "falcon_search_host_group_members", READ_ONLY_ANNOTATIONS
        )

    def test_mutating_tools_have_correct_annotations(self):
        """Test that mutating tools carry the correct annotations."""
        self.module.register_tools(self.mock_server)

        non_destructive = ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
        self.assert_tool_annotations("falcon_create_host_group", non_destructive)
        self.assert_tool_annotations("falcon_update_host_group", non_destructive)
        self.assert_tool_annotations(
            "falcon_perform_host_group_action", non_destructive
        )

        self.assert_tool_annotations(
            "falcon_delete_host_groups",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
