"""
Tests for the RTR Admin module.
"""

import asyncio
import inspect

from mcp.types import ToolAnnotations

from falcon_mcp.common.api_scopes import get_required_scopes
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr_admin import RTRAdminModule
from tests.modules.utils.test_modules import TestModules


class TestRTRAdminModule(TestModules):
    """Test cases for the RTR Admin module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(RTRAdminModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_rtr_admin_scripts",
            "falcon_search_rtr_falcon_scripts",
            "falcon_search_rtr_put_files",
            "falcon_get_rtr_put_file_contents",
            "falcon_check_rtr_admin_command_status",
            "falcon_classify_rtr_admin_command",
            "falcon_preview_rtr_admin_command",
            "falcon_execute_rtr_admin_command",
            "falcon_run_rtr_admin_command_and_wait",
        ]
        self.assert_tools_registered(expected_tools)
        self.assertFalse(hasattr(self.module, "batch_execute_admin_command"))

    def test_tool_annotations(self):
        """Test tool annotations are correctly set."""
        self.module.register_tools(self.mock_server)

        for tool_name in [
            "falcon_search_rtr_admin_scripts",
            "falcon_search_rtr_falcon_scripts",
            "falcon_search_rtr_put_files",
            "falcon_get_rtr_put_file_contents",
            "falcon_check_rtr_admin_command_status",
            "falcon_classify_rtr_admin_command",
            "falcon_preview_rtr_admin_command",
        ]:
            self.assert_tool_annotations(tool_name, READ_ONLY_ANNOTATIONS)

        self.assert_tool_annotations(
            "falcon_execute_rtr_admin_command",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_run_rtr_admin_command_and_wait",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_rtr_admin_scripts_fql_guide",
            "falcon_search_rtr_falcon_scripts_fql_guide",
            "falcon_search_rtr_put_files_fql_guide",
            "falcon_rtr_admin_tool_use_guide",
            "falcon_rtr_admin_runscript_raw_guide",
            "falcon_rtr_admin_command_policy_guide",
            "falcon_rtr_admin_approval_packet_template",
        ]
        self.assert_resources_registered(expected_resources)

    def test_register_prompts(self):
        """Test registering RTR Admin workflow prompts with the server."""
        expected_prompts = [
            "falcon_plan_rtr_admin_action",
            "falcon_build_rtr_admin_approval_packet",
            "falcon_review_rtr_admin_runscript",
            "falcon_interpret_rtr_admin_status",
        ]
        self.assert_prompts_registered(expected_prompts)

    def test_register_resources_includes_admin_tool_use_guide(self):
        """Test RTR Admin workflow guidance is exposed as a resource."""
        self.module.register_resources(self.mock_server)

        resources = {
            call.kwargs["resource"].name: call.kwargs["resource"]
            for call in self.mock_server.add_resource.call_args_list
        }

        guide = resources["falcon_rtr_admin_tool_use_guide"]
        self.assertEqual(str(guide.uri), "falcon://rtr-admin/workflows/admin-guide")
        self.assertIn("Recommended workflow", guide.text)
        self.assertIn("falcon_preview_rtr_admin_command", guide.text)
        self.assertIn("classification is enforced", guide.text.lower())
        self.assertIn("returned sequence_id", guide.text)
        self.assertNotIn("then increment", guide.text)

    def test_register_resources_include_policy_and_approval_guides(self):
        """Test RTR Admin policy and approval context are exposed as resources."""
        self.module.register_resources(self.mock_server)

        resources = {
            call.kwargs["resource"].name: call.kwargs["resource"]
            for call in self.mock_server.add_resource.call_args_list
        }

        policy = resources["falcon_rtr_admin_command_policy_guide"]
        approval = resources["falcon_rtr_admin_approval_packet_template"]

        self.assertEqual(str(policy.uri), "falcon://rtr-admin/policy/command-guide")
        self.assertIn("Read-only commands", policy.text)
        self.assertIn("ps", policy.text)
        self.assertIn("rm", policy.text)
        self.assertIn("runscript", policy.text)
        self.assertIn("Unknown commands", policy.text)

        self.assertEqual(str(approval.uri), "falcon://rtr-admin/approval/packet-guide")
        self.assertIn("Approval Packet", approval.text)
        self.assertIn("approval phrase", approval.text.lower())

    def test_prompt_methods_are_local_workflow_guides(self):
        """Test RTR Admin prompts render workflow text without Falcon calls."""
        plan = self.module.plan_rtr_admin_action(
            objective="collect triage evidence",
            target_hostname="HOST-1",
            ticket="INC-123",
        )
        packet = self.module.build_rtr_admin_approval_packet(
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            session_id="session-1",
            reason="cleanup selected test file",
            ticket="INC-123",
            expected_effect="remove one file",
        )
        runscript = self.module.review_rtr_admin_runscript(
            command_string="runscript -Raw=```Get-Process```",
            target_platform="windows",
        )
        status = self.module.interpret_rtr_admin_status(
            command_status="complete=true stdout=ok stderr=",
            base_command="ps",
        )

        self.assertIn("falcon_classify_rtr_admin_command", plan)
        self.assertIn("falcon_preview_rtr_admin_command", packet)
        self.assertIn("approval_gate.approval_phrase", packet)
        self.assertIn("triple backticks", runscript)
        self.assertIn("falcon_check_rtr_admin_command_status", status)
        self.mock_client.command.assert_not_called()

    def test_registered_prompt_renders_workflow_text(self):
        """Test registered MCP prompt renders with runtime arguments."""
        self.module.register_prompts(self.mock_server)
        prompts = {
            call.args[0].name: call.args[0]
            for call in self.mock_server.add_prompt.call_args_list
        }

        messages = asyncio.run(
            prompts["falcon_plan_rtr_admin_action"].render(
                {
                    "objective": "collect triage evidence",
                    "target_hostname": "HOST-1",
                }
            )
        )

        self.assertEqual(len(messages), 1)
        rendered = messages[0].content.text
        self.assertIn("collect triage evidence", rendered)
        self.assertIn("HOST-1", rendered)
        self.assertIn("falcon_classify_rtr_admin_command", rendered)
        self.assertIn("falcon_preview_rtr_admin_command", rendered)
        self.mock_client.command.assert_not_called()

    def test_api_scope_mappings(self):
        """Test RTR Admin operations have explicit scope mappings."""
        for operation in [
            "RTR_ListScripts",
            "RTR_GetScriptsV2",
            "RTR_ListFalconScripts",
            "RTR_GetFalconScripts",
            "RTR_ListPut_Files",
            "RTR_GetPut_FilesV2",
            "RTR_GetPutFileContents",
            "RTR_CheckAdminCommandStatus",
            "RTR_ExecuteAdminCommand",
        ]:
            self.assertEqual(
                get_required_scopes(operation),
                ["Real time response (admin):write"],
            )

    def test_inventory_limits_match_falconpy_contract(self):
        """Test search tool limits match the pinned FalconPy endpoint metadata."""
        self.assertEqual(self._limit_le("search_rtr_admin_scripts"), 5000)
        self.assertEqual(self._limit_le("search_rtr_falcon_scripts"), 100)
        self.assertEqual(self._limit_le("search_rtr_put_files"), 5000)

    def test_search_scripts_returns_full_details(self):
        """Test custom script search fetches details after IDs are returned."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["script-1", "script-2"]}},
            {
                "status_code": 200,
                "body": {
                    "resources": [
                        {"id": "script-1", "name": "collect-a"},
                        {"id": "script-2", "name": "collect-b"},
                    ]
                },
            },
        ]

        result = self.module.search_rtr_admin_scripts(
            filter="platform:'windows'",
            limit=25,
            offset=5,
            sort="created_timestamp|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListScripts")
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform:'windows'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 5)
        self.assertEqual(first_call[1]["parameters"]["sort"], "created_timestamp|desc")

        self.assertEqual(second_call[0][0], "RTR_GetScriptsV2")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["script-1", "script-2"])
        self.assertEqual(result[0]["name"], "collect-a")

    def test_search_scripts_preserves_query_id_order_after_detail_fetch(self):
        """Test detail responses are returned in the original search ID order."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["script-2", "script-1"]}},
            {
                "status_code": 200,
                "body": {
                    "resources": [
                        {"id": "script-1", "name": "older"},
                        {"id": "script-2", "name": "newer"},
                    ]
                },
            },
        ]

        result = self.module.search_rtr_admin_scripts(sort="created_timestamp|desc")

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(
            first_call[1]["parameters"],
            {"limit": 10, "sort": "created_timestamp|desc"},
        )
        self.assertEqual([item["id"] for item in result], ["script-2", "script-1"])

    def test_search_put_files_defaults_do_not_send_fieldinfo_values(self):
        """Test omitted optional search params are not sent as FieldInfo objects."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["file-1"]}},
            {
                "status_code": 200,
                "body": {"resources": [{"id": "file-1", "name": "collector.exe"}]},
            },
        ]

        result = self.module.search_rtr_put_files(sort="created_timestamp|desc")

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(
            first_call[1]["parameters"],
            {"limit": 10, "sort": "created_timestamp|desc"},
        )
        self.assertEqual(result[0]["id"], "file-1")

    def test_search_falcon_scripts_returns_full_details(self):
        """Test Falcon script search fetches details after IDs are returned."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["falcon-script-1"]}},
            {
                "status_code": 200,
                "body": {"resources": [{"id": "falcon-script-1", "name": "triage"}]},
            },
        ]

        result = self.module.search_rtr_falcon_scripts(
            filter="name:~'triage'",
            limit=10,
            offset=None,
            sort="name|asc",
        )

        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListFalconScripts")
        self.assertEqual(first_call[1]["parameters"]["filter"], "name:~'triage'")
        self.assertNotIn("offset", first_call[1]["parameters"])
        self.assertEqual(second_call[0][0], "RTR_GetFalconScripts")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["falcon-script-1"])
        self.assertEqual(result[0]["id"], "falcon-script-1")

    def test_search_put_files_returns_full_details(self):
        """Test put-file search fetches details after IDs are returned."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["file-1"]}},
            {
                "status_code": 200,
                "body": {"resources": [{"id": "file-1", "name": "collector.exe"}]},
            },
        ]

        result = self.module.search_rtr_put_files(
            filter="name:~'collector'",
            limit=50,
            offset=0,
            sort="created_timestamp|desc",
        )

        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListPut_Files")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(second_call[0][0], "RTR_GetPut_FilesV2")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["file-1"])
        self.assertEqual(result[0]["name"], "collector.exe")

    def test_get_put_file_contents_uses_id_query_parameter(self):
        """Test retrieving put-file contents uses FalconPy's id query shape."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "file-1", "content": "payload"}]},
        }

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_GetPutFileContents",
            parameters={"id": "file-1"},
        )
        self.assertEqual(result[0]["content"], "payload")

    def test_get_put_file_contents_returns_direct_body_payload(self):
        """Test put-file contents can return a direct body payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"content": "payload", "encoding": "utf-8"},
        }

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_GetPutFileContents",
            parameters={"id": "file-1"},
        )
        self.assertEqual(result["id"], "file-1")
        self.assertEqual(result["body"]["content"], "payload")

    def test_get_put_file_contents_warns_when_binary_metadata_returns_text(self):
        """Test text retrieval is sensitive even when inventory metadata says binary."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "file-1",
                        "file_type": "binary",
                        "content_format": "text",
                        "content": "script payload",
                    }
                ]
            },
        }

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.assertEqual(result[0]["content_format"], "text")
        self.assertEqual(result[0]["file_type"], "binary")
        self.assertIn("sensitivity_warning", result[0])

    def test_get_put_file_contents_decodes_text_bytes(self):
        """Test text byte content is decoded into a model-safe response."""
        self.mock_client.command.return_value = b"echo hello"

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.assertEqual(result["id"], "file-1")
        self.assertEqual(result["content"], "echo hello")
        self.assertEqual(result["content_format"], "text")

    def test_get_put_file_contents_rejects_binary_bytes(self):
        """Test binary put-file bytes return a safe error with size metadata."""
        self.mock_client.command.return_value = b"\xff\xfe\x00\x00"

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.assertIn("error", result)
        self.assertEqual(result["content_format"], "binary")
        self.assertEqual(result["size_bytes"], 4)

    def test_get_put_file_contents_wraps_api_error(self):
        """Test put-file content API errors include operation scope context."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.get_rtr_put_file_contents(file_id="file-1")

        self.assertIn("error", result)
        self.assertEqual(result["details"]["status_code"], 403)
        self.assertEqual(result["required_scopes"], ["Real time response (admin):write"])

    def test_get_put_file_contents_validates_file_id(self):
        """Test put-file content retrieval fails locally without an ID."""
        result = self.module.get_rtr_put_file_contents(file_id=" ")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_search_by_id_filter_round_trips_query_and_get(self):
        """Test ID lookups go through the search query→get round-trip."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["script-1"]}},
            {
                "status_code": 200,
                "body": {"resources": [{"id": "script-1", "name": "collect-a"}]},
            },
        ]

        result = self.module.search_rtr_admin_scripts(
            filter="id:'script-1'",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListScripts")
        self.assertEqual(first_call[1]["parameters"]["filter"], "id:'script-1'")
        self.assertEqual(second_call[0][0], "RTR_GetScriptsV2")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["script-1"])
        self.assertEqual(result[0]["name"], "collect-a")

    def test_search_error_returns_fql_guide(self):
        """Test search errors include the relevant FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_rtr_admin_scripts(
            filter="invalid:::filter",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])

    def test_empty_search_returns_fql_guide(self):
        """Test empty search results include the relevant FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_rtr_put_files(
            filter="name:'not-real'",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_check_admin_command_status(self):
        """Test retrieving RTR Admin command status."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "ok"}]},
        }

        result = self.module.check_rtr_admin_command_status(
            cloud_request_id="req-123",
            sequence_id=1,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_CheckAdminCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 1},
        )
        self.assertTrue(result[0]["complete"])

    def test_check_admin_command_status_validates_required_fields(self):
        """Test command status lookup fails locally for invalid inputs."""
        missing_request = self.module.check_rtr_admin_command_status(
            cloud_request_id=" ",
            sequence_id=0,
        )
        invalid_sequence = self.module.check_rtr_admin_command_status(
            cloud_request_id="req-123",
            sequence_id=-1,
        )

        self.assertIn("error", missing_request)
        self.assertIn("error", invalid_sequence)
        self.mock_client.command.assert_not_called()

    def test_classify_read_only_command(self):
        """Test read-only commands are classified as low risk."""
        result = self.module.classify_rtr_admin_command(base_command="ps")

        self.assertEqual(result["category"], "read_only")
        self.assertEqual(result["risk"], "low")
        self.assertTrue(result["allowed_for_execution"])
        self.assertIn("safety_disclaimer", result)
        self.assertIsNone(result["blocked_reason"])
        self.mock_client.command.assert_not_called()

    def test_classify_registry_query_only(self):
        """Test only read-only registry queries are allowed."""
        allowed = self.module.classify_rtr_admin_command(
            base_command="reg",
            command_string=r"reg query HKLM\Software\Microsoft",
        )
        warned = self.module.classify_rtr_admin_command(
            base_command="reg",
            command_string=r"reg query HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion ProductName",
        )
        blocked = self.module.classify_rtr_admin_command(
            base_command="reg",
            command_string=r"reg delete HKLM\Software\Test",
        )

        self.assertEqual(allowed["category"], "read_only")
        self.assertTrue(allowed["allowed_for_execution"])
        self.assertEqual(allowed["command_warnings"], [])
        self.assertEqual(warned["category"], "read_only")
        self.assertTrue(warned["command_warnings"])
        self.assertEqual(blocked["category"], "high_impact")
        self.assertFalse(blocked["allowed_for_execution"])
        self.assertTrue(blocked["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_update_read_only_subcommands(self):
        """Test documented read-only update subcommands are not blocked as installs."""
        for command_string in [
            "update history",
            "update list",
            "update query",
        ]:
            with self.subTest(command_string=command_string):
                result = self.module.classify_rtr_admin_command(
                    base_command="update",
                    command_string=command_string,
                )

                self.assertEqual(result["category"], "read_only")
                self.assertEqual(result["risk"], "low")
                self.assertTrue(result["allowed_for_execution"])

        install = self.module.classify_rtr_admin_command(
            base_command="update",
            command_string="update install",
        )
        self.assertEqual(install["category"], "high_impact")
        self.assertFalse(install["allowed_for_execution"])
        self.assertTrue(install["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_unsupported_rtr_commands_as_unknown(self):
        """Test non-documented RTR Admin commands are not treated as low risk."""
        for base_command in ["totally-fake", "notacommand"]:
            with self.subTest(base_command=base_command):
                result = self.module.classify_rtr_admin_command(base_command=base_command)

                self.assertEqual(result["category"], "unknown")
                self.assertFalse(result["allowed_for_execution"])
                self.assertFalse(result["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_newly_added_read_only_commands(self):
        """Test csrutil, ifconfig, users, pwd are classified as read-only."""
        for base_command in ["csrutil", "ifconfig", "users", "pwd"]:
            with self.subTest(base_command=base_command):
                result = self.module.classify_rtr_admin_command(base_command=base_command)

                self.assertEqual(result["category"], "read_only")
                self.assertEqual(result["risk"], "low")
                self.assertTrue(result["allowed_for_execution"])
        self.mock_client.command.assert_not_called()

    def test_classify_newly_added_blocked_commands(self):
        """Test documented high-impact commands are blocked with approval."""
        for base_command in [
            "tar",
            "umount",
            "unmount",
            "rmdir",
            "cswindiag",
            "falconscript",
        ]:
            with self.subTest(base_command=base_command):
                result = self.module.classify_rtr_admin_command(base_command=base_command)

                self.assertEqual(result["category"], "high_impact")
                self.assertEqual(result["risk"], "critical")
                self.assertFalse(result["allowed_for_execution"])
                self.assertTrue(result["requires_approval"])
                self.assertTrue(result["can_execute_with_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_destructive_and_unknown_commands_are_blocked(self):
        """Test destructive and unknown commands are blocked."""
        destructive = self.module.classify_rtr_admin_command(base_command="rm")
        unknown = self.module.classify_rtr_admin_command(base_command="not-a-command")

        self.assertEqual(destructive["risk"], "critical")
        self.assertFalse(destructive["allowed_for_execution"])
        self.assertTrue(destructive["requires_approval"])
        self.assertTrue(destructive["requires_explicit_target"])
        self.assertIsNotNone(destructive["blocked_reason"])
        self.assertEqual(unknown["category"], "unknown")
        self.assertFalse(unknown["allowed_for_execution"])
        self.assertFalse(unknown["requires_approval"])
        self.assertFalse(unknown["requires_explicit_target"])
        self.mock_client.command.assert_not_called()

    def test_classify_empty_base_command_returns_error(self):
        """Test empty base command validation."""
        result = self.module.classify_rtr_admin_command(base_command=" ")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_classify_rejects_base_command_mismatch(self):
        """Test command strings cannot hide a different base command."""
        result = self.module.classify_rtr_admin_command(
            base_command="ps",
            command_string=r"rm C:\Temp\old.bin",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["base_command"], "ps")
        self.assertEqual(result["details"]["command_string_base"], "rm")
        self.mock_client.command.assert_not_called()

    def test_preview_admin_command_does_not_call_falcon(self):
        """Test command preview returns a payload shape without executing."""
        result = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="get",
            command_string=r"get C:\Temp\sample.bin",
            command_id=7,
            target_hostname="HOST-1",
            reason="collect sample",
            ticket="INC-123",
            expected_effect="retrieve one file for analysis",
            persist=False,
        )

        self.assertTrue(result["execution_available"])
        self.assertEqual(result["execution_tool"], "falcon_execute_rtr_admin_command")
        self.assertFalse(result["policy_allows_future_execution"])
        self.assertTrue(result["classification_enforced"])
        self.assertTrue(result["approval_gate"]["approval_required"])
        self.assertIn("safety_disclaimer", result)
        self.assertEqual(result["operation"], "RTR_ExecuteAdminCommand")
        self.assertEqual(result["missing_context"], [])
        self.assertEqual(result["required_context"], ["reason", "ticket", "expected_effect"])
        self.assertEqual(result["target"]["device_id"], "aid-1")
        self.assertEqual(result["target"]["hostname"], "HOST-1")
        self.assertEqual(result["payload_preview"]["body"]["device_id"], "aid-1")
        self.assertEqual(result["payload_preview"]["body"]["session_id"], "session-1")
        self.assertEqual(result["payload_preview"]["body"]["id"], 7)
        self.mock_client.command.assert_not_called()

    def test_preview_approval_phrase_matches_execution_payload_with_device_id(self):
        """Test preview and execution approval use the same target and payload material."""
        preview = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            persist=True,
        )
        approval_phrase = preview["approval_gate"]["approval_phrase"]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            operator_approval=approval_phrase,
        )

        self.assertTrue(result["submitted"])
        self.assertTrue(result["approval_gate"]["approved"])
        self.mock_client.command.assert_called_once()

    def test_approval_hash_binds_expected_effect(self):
        """Test changed audit context changes the high-impact approval phrase."""
        first = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
        )
        second = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected directory",
        )

        self.assertNotEqual(
            first["approval_gate"]["approval_phrase"],
            second["approval_gate"]["approval_phrase"],
        )

    def test_approval_hash_independent_of_hostname(self):
        """Test that hostname differences do not break approval phrase matching."""
        preview = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            persist=True,
        )
        approval_phrase = preview["approval_gate"]["approval_phrase"]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="DIFFERENT-HOST",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            operator_approval=approval_phrase,
        )

        self.assertTrue(result["submitted"])
        self.assertTrue(result["approval_gate"]["approved"])
        self.mock_client.command.assert_called_once()

    def test_preview_admin_command_reports_missing_context(self):
        """Test command preview calls out missing audit context."""
        result = self.module.preview_rtr_admin_command(
            session_id="session-1",
            base_command="runscript",
            command_string="runscript -Raw=```Get-Process```",
            target_hostname=None,
            reason=None,
            ticket=None,
            expected_effect=None,
            persist=False,
        )

        self.assertTrue(result["execution_available"])
        self.assertEqual(result["missing_context"], ["reason", "ticket", "expected_effect"])
        self.assertTrue(result["approval_gate"]["approval_required"])
        self.assertFalse(result["approval_gate"]["approval_ready"])
        self.assertNotIn("approval_phrase", result["approval_gate"])
        self.assertEqual(
            result["approval_gate"]["missing_approval_context"],
            ["reason", "ticket", "expected_effect", "device_id"],
        )
        self.assertEqual(
            result["command_guidance"]["resource"],
            "falcon://rtr-admin/commands/runscript-guide",
        )
        self.mock_client.command.assert_not_called()

    def test_preview_admin_command_missing_required_fields_returns_error(self):
        """Test command preview rejects missing required command fields."""
        result = self.module.preview_rtr_admin_command(
            session_id=" ",
            base_command="ps",
            command_string=" ",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["missing_required"], ["session_id", "command_string"])
        self.mock_client.command.assert_not_called()

    def test_preview_admin_command_rejects_base_command_mismatch(self):
        """Test preview stops locally when command string and base command disagree."""
        result = self.module.preview_rtr_admin_command(
            session_id="session-1",
            base_command="ps",
            command_string=r"rm C:\Temp\old.bin",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["base_command"], "ps")
        self.assertEqual(result["details"]["command_string_base"], "rm")
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_submits_low_risk_single_host_body(self):
        """Test low-risk single-host RTR Admin execution submits the expected body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
            command_id=7,
            persist=False,
            target_hostname="HOST-1",
            reason="process review",
            ticket="INC-123",
            expected_effect="list processes",
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteAdminCommand",
            body={
                "base_command": "ps",
                "command_string": "ps",
                "device_id": "aid-1",
                "session_id": "session-1",
                "id": 7,
                "persist": False,
            },
        )
        self.assertTrue(result["submitted"])
        self.assertTrue(result["classification_enforced"])
        self.assertFalse(result["approval_gate"]["approval_required"])
        self.assertTrue(result["approval_gate"]["approved"])
        self.assertEqual(result["operation"], "RTR_ExecuteAdminCommand")
        self.assertEqual(result["result"][0]["cloud_request_id"], "req-123")
        self.assertNotIn("persist_warning", result)

    def test_execute_admin_command_requires_approval_for_high_impact_command(self):
        """Test high-impact single-host execution stops before the Falcon call."""
        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
        )

        self.assertIn("error", result)
        self.assertIn("approval required", result["error"].lower())
        self.assertTrue(result["details"]["approval_gate"]["approval_required"])
        self.assertTrue(result["details"]["approval_gate"]["approval_ready"])
        self.assertRegex(
            result["details"]["approval_gate"]["approval_phrase"],
            r"^APPROVE_RTR_ADMIN_[0-9A-F]{16}$",
        )
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_requires_device_id_for_high_impact_approval(self):
        """Test high-impact approval is not issued without a device ID."""
        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id=None,
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
        )

        self.assertIn("error", result)
        self.assertIn("approval context is incomplete", result["error"])
        self.assertFalse(result["details"]["approval_gate"]["approval_ready"])
        self.assertEqual(
            result["details"]["approval_gate"]["missing_approval_context"],
            ["device_id"],
        )
        self.assertNotIn("approval_phrase", result["details"]["approval_gate"])
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_submits_high_impact_after_exact_approval(self):
        """Test high-impact single-host execution submits only after exact approval."""
        blocked = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
        )
        approval_phrase = blocked["details"]["approval_gate"]["approval_phrase"]
        self.mock_client.command.assert_not_called()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            command_id=7,
            persist=True,
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            operator_approval=approval_phrase,
        )

        self.assertTrue(result["submitted"])
        self.assertTrue(result["classification_enforced"])
        self.assertTrue(result["approval_gate"]["approval_required"])
        self.assertTrue(result["approval_gate"]["approved"])
        self.assertIn("persist_warning", result)
        self.mock_client.command.assert_called_once()

    def test_execute_admin_command_returns_runscript_raw_guidance(self):
        """Test raw runscript execution includes controller guidance."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-raw"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            base_command="runscript",
            command_string="runscript -Raw=```Get-Process```",
        )

        self.assertIn("error", result)
        self.assertIn("approval context is incomplete", result["error"])
        self.assertTrue(result["details"]["approval_gate"]["approval_required"])
        self.assertFalse(result["details"]["approval_gate"]["approval_ready"])
        self.mock_client.command.assert_not_called()
        self.assertNotIn("approval_phrase", result["details"]["approval_gate"])
        self.assertEqual(
            result["details"]["payload_preview"]["body"]["command_string"],
            "runscript -Raw=```Get-Process```",
        )
        self.assertEqual(
            self.module._command_guidance("runscript", "runscript -Raw=```Get-Process```")[
                "shape"
            ],
            "runscript -Raw=```<target-side script>```",
        )

    def test_execute_admin_command_requires_target_and_command(self):
        """Test single-host RTR Admin execution validates minimum fields locally."""
        result = self.module.execute_rtr_admin_command(
            session_id=None,
            device_id=None,
            base_command=" ",
            command_string=" ",
        )

        self.assertIn("error", result)
        self.assertEqual(
            result["details"]["missing_required"],
            ["base_command", "command_string", "session_id"],
        )
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_rejects_device_only_target(self):
        """Test single-host RTR Admin execution requires an existing RTR session."""
        result = self.module.execute_rtr_admin_command(
            session_id=" ",
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["missing_required"], ["session_id"])
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_rejects_base_command_mismatch(self):
        """Test execution stops locally when command string and base command disagree."""
        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="ps",
            command_string=r"rm C:\Temp\old.bin",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["base_command"], "ps")
        self.assertEqual(result["details"]["command_string_base"], "rm")
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_wraps_api_error(self):
        """Test single-host RTR Admin execution includes context on API errors."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.execute_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
        )

        self.assertFalse(result["submitted"])
        self.assertIn("error", result["result"])
        self.assertEqual(result["missing_context"], ["reason", "ticket", "expected_effect"])

    def test_run_admin_command_and_wait_submits_and_polls(self):
        """Test RTR Admin command-and-wait submits once and polls status."""
        execute_response = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123", "session_id": "session-1"}]},
        }
        status_response = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "ok"}]},
        }
        self.mock_client.command.side_effect = [execute_response, status_response]

        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
            command_id=7,
            persist=False,
            target_hostname="HOST-1",
            reason="process review",
            ticket="INC-123",
            expected_effect="list processes",
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "RTR_ExecuteAdminCommand",
            body={
                "base_command": "ps",
                "command_string": "ps",
                "device_id": "aid-1",
                "session_id": "session-1",
                "id": 7,
                "persist": False,
            },
        )
        self.mock_client.command.assert_any_call(
            "RTR_CheckAdminCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 0},
        )
        self.assertEqual(result["cloud_request_id"], "req-123")
        self.assertTrue(result["complete"])
        self.assertFalse(result["timed_out"])
        self.assertEqual(result["stdout"], "ok")
        self.assertEqual(result["classification"]["category"], "read_only")
        self.assertFalse(result["approval_gate"]["approval_required"])

    def test_run_admin_command_and_wait_advances_sequence_chunks(self):
        """Test RTR Admin command-and-wait reads sequence_id from status chunks."""
        execute_response = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123", "session_id": "session-1"}]},
        }
        first_chunk_response = {
            "status_code": 200,
            "body": {"resources": [{"complete": False, "stdout": "part1", "sequence_id": 3}]},
        }
        second_chunk_response = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "part2"}]},
        }
        self.mock_client.command.side_effect = [
            execute_response,
            first_chunk_response,
            second_chunk_response,
        ]

        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            base_command="ps",
            command_string="ps",
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.mock_client.command.assert_any_call(
            "RTR_CheckAdminCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 0},
        )
        self.mock_client.command.assert_any_call(
            "RTR_CheckAdminCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 3},
        )
        self.assertEqual(result["stdout"], "part1part2")
        self.assertTrue(result["complete"])
        self.assertIn("context_warning", result)
        self.assertEqual(result["missing_context"], ["reason", "ticket", "expected_effect"])

    def test_run_admin_command_and_wait_requires_approval_before_falcon_call(self):
        """Test RTR Admin command-and-wait does not bypass high-impact approval."""
        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertIn("error", result)
        self.assertEqual(result["phase"], "execute")
        self.assertIn("approval required", result["error"].lower())
        self.mock_client.command.assert_not_called()

    def test_run_admin_command_and_wait_high_impact_after_exact_approval(self):
        """Test high-impact command-and-wait runs only after exact approval."""
        preview = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            persist=True,
        )
        approval_phrase = preview["approval_gate"]["approval_phrase"]
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {"resources": [{"cloud_request_id": "req-123"}]},
            },
            {
                "status_code": 200,
                "body": {"resources": [{"complete": True, "stderr": ""}]},
            },
        ]

        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="cleanup test file",
            ticket="INC-123",
            expected_effect="remove selected file",
            persist=True,
            operator_approval=approval_phrase,
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertTrue(result["complete"])
        self.assertTrue(result["approval_gate"]["approval_required"])
        self.assertTrue(result["approval_gate"]["approved"])
        self.assertEqual(result["classification"]["category"], "high_impact")
        self.assertEqual(self.mock_client.command.call_count, 2)

    def test_run_admin_command_and_wait_timeout(self):
        """Test RTR Admin command-and-wait returns partial status on timeout."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {"resources": [{"cloud_request_id": "req-123"}]},
            },
            {
                "status_code": 200,
                "body": {"resources": [{"complete": False, "stdout": "partial"}]},
            },
        ]

        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            base_command="ps",
            command_string="ps",
            timeout_seconds=0,
            poll_interval_seconds=0,
        )

        self.assertEqual(result["cloud_request_id"], "req-123")
        self.assertFalse(result["complete"])
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["stdout"], "partial")
        self.assertIn("warning", result)

    def _limit_le(self, method_name: str) -> int:
        """Return the Pydantic upper-bound metadata for a search limit parameter."""
        signature = inspect.signature(getattr(self.module, method_name))
        limit_field = signature.parameters["limit"].default
        for item in limit_field.metadata:
            le = getattr(item, "le", None)
            if le is not None:
                return le
        raise AssertionError(f"No upper limit metadata found for {method_name}")
