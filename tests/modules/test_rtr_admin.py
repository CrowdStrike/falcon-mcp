"""
Tests for the RTR Admin module.
"""

import inspect

from falcon_mcp.common.api_scopes import get_required_scopes
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr_admin import RTR_ADMIN_EXECUTION_ANNOTATIONS, RTRAdminModule
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
            "falcon_get_rtr_admin_script_details",
            "falcon_search_rtr_falcon_scripts",
            "falcon_get_rtr_falcon_script_details",
            "falcon_search_rtr_put_files",
            "falcon_get_rtr_put_file_details",
            "falcon_check_rtr_admin_command_status",
            "falcon_classify_rtr_admin_command",
            "falcon_preview_rtr_admin_command",
            "falcon_execute_rtr_admin_command",
        ]
        self.assert_tools_registered(expected_tools)
        self.assertFalse(hasattr(self.module, "batch_execute_admin_command"))

    def test_tool_annotations(self):
        """Test tool annotations are correctly set."""
        self.module.register_tools(self.mock_server)

        for tool_name in [
            "falcon_search_rtr_admin_scripts",
            "falcon_get_rtr_admin_script_details",
            "falcon_search_rtr_falcon_scripts",
            "falcon_get_rtr_falcon_script_details",
            "falcon_search_rtr_put_files",
            "falcon_get_rtr_put_file_details",
            "falcon_check_rtr_admin_command_status",
            "falcon_classify_rtr_admin_command",
            "falcon_preview_rtr_admin_command",
        ]:
            self.assert_tool_annotations(tool_name, READ_ONLY_ANNOTATIONS)

        self.assert_tool_annotations(
            "falcon_execute_rtr_admin_command",
            RTR_ADMIN_EXECUTION_ANNOTATIONS,
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_rtr_admin_scripts_fql_guide",
            "falcon_search_rtr_falcon_scripts_fql_guide",
            "falcon_search_rtr_put_files_fql_guide",
            "falcon_rtr_admin_tool_use_guide",
            "falcon_rtr_admin_runscript_raw_guide",
        ]
        self.assert_resources_registered(expected_resources)

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

    def test_api_scope_mappings(self):
        """Test RTR Admin operations have explicit scope mappings."""
        for operation in [
            "RTR_ListScripts",
            "RTR_GetScriptsV2",
            "RTR_ListFalconScripts",
            "RTR_GetFalconScripts",
            "RTR_ListPut_Files",
            "RTR_GetPut_FilesV2",
            "RTR_CheckAdminCommandStatus",
            "RTR_ExecuteAdminCommand",
        ]:
            self.assertEqual(
                get_required_scopes(operation),
                ["Real time response (admin):write"],
            )

    def test_inventory_limits_match_falconpy_contract(self):
        """Test search tool limits match the pinned FalconPy endpoint metadata."""
        self.assertEqual(self._limit_le("search_scripts"), 5000)
        self.assertEqual(self._limit_le("search_falcon_scripts"), 100)
        self.assertEqual(self._limit_le("search_put_files"), 5000)

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

        result = self.module.search_scripts(
            filter="platform:'windows'",
            limit=25,
            offset=5,
            sort="created_at|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListScripts")
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform:'windows'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 5)
        self.assertEqual(first_call[1]["parameters"]["sort"], "created_at|desc")

        self.assertEqual(second_call[0][0], "RTR_GetScriptsV2")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["script-1", "script-2"])
        self.assertEqual(result[0]["name"], "collect-a")

    def test_search_falcon_scripts_returns_full_details(self):
        """Test Falcon script search fetches details after IDs are returned."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["falcon-script-1"]}},
            {
                "status_code": 200,
                "body": {"resources": [{"id": "falcon-script-1", "name": "triage"}]},
            },
        ]

        result = self.module.search_falcon_scripts(
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

        result = self.module.search_put_files(
            filter="name:~'collector'",
            limit=50,
            offset=0,
            sort="created_at|desc",
        )

        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListPut_Files")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(second_call[0][0], "RTR_GetPut_FilesV2")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["file-1"])
        self.assertEqual(result[0]["name"], "collector.exe")

    def test_get_details_empty_ids_return_without_api_call(self):
        """Test detail helpers return early for empty ID lists."""
        self.assertEqual(self.module.get_script_details(ids=[]), [])
        self.assertEqual(self.module.get_falcon_script_details(ids=[]), [])
        self.assertEqual(self.module.get_put_file_details(ids=[]), [])
        self.mock_client.command.assert_not_called()

    def test_get_script_details_uses_query_parameters(self):
        """Test custom script details use query parameters for IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "script-1"}]},
        }

        result = self.module.get_script_details(ids=["script-1"])

        self.mock_client.command.assert_called_once_with(
            "RTR_GetScriptsV2",
            parameters={"ids": ["script-1"]},
        )
        self.assertEqual(result[0]["id"], "script-1")

    def test_search_error_returns_fql_guide(self):
        """Test search errors include the relevant FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_scripts(
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

        result = self.module.search_put_files(
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

        result = self.module.check_admin_command_status(
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
        missing_request = self.module.check_admin_command_status(
            cloud_request_id=" ",
            sequence_id=0,
        )
        invalid_sequence = self.module.check_admin_command_status(
            cloud_request_id="req-123",
            sequence_id=-1,
        )

        self.assertIn("error", missing_request)
        self.assertIn("error", invalid_sequence)
        self.mock_client.command.assert_not_called()

    def test_classify_read_only_command(self):
        """Test read-only commands are classified as low risk."""
        result = self.module.classify_admin_command(base_command="ps")

        self.assertEqual(result["category"], "read_only")
        self.assertEqual(result["risk"], "low")
        self.assertTrue(result["allowed_for_execution"])
        self.assertIn("safety_disclaimer", result)
        self.assertIsNone(result["blocked_reason"])
        self.mock_client.command.assert_not_called()

    def test_classify_registry_query_only(self):
        """Test only read-only registry queries are allowed."""
        allowed = self.module.classify_admin_command(
            base_command="reg",
            command_string=r"reg query HKLM\Software\Microsoft",
        )
        blocked = self.module.classify_admin_command(
            base_command="reg",
            command_string=r"reg delete HKLM\Software\Test",
        )

        self.assertEqual(allowed["category"], "read_only")
        self.assertTrue(allowed["allowed_for_execution"])
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
                result = self.module.classify_admin_command(
                    base_command="update",
                    command_string=command_string,
                )

                self.assertEqual(result["category"], "read_only")
                self.assertEqual(result["risk"], "low")
                self.assertTrue(result["allowed_for_execution"])

        install = self.module.classify_admin_command(
            base_command="update",
            command_string="update install",
        )
        self.assertEqual(install["category"], "high_impact")
        self.assertFalse(install["allowed_for_execution"])
        self.assertTrue(install["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_unsupported_rtr_commands_as_unknown(self):
        """Test non-documented RTR Admin commands are not treated as low risk."""
        for base_command in ["csrutil", "ifconfig", "users"]:
            with self.subTest(base_command=base_command):
                result = self.module.classify_admin_command(base_command=base_command)

                self.assertEqual(result["category"], "unknown")
                self.assertFalse(result["allowed_for_execution"])
                self.assertFalse(result["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_destructive_and_unknown_commands_are_blocked(self):
        """Test destructive and unknown commands are blocked."""
        destructive = self.module.classify_admin_command(base_command="rm")
        unknown = self.module.classify_admin_command(base_command="not-a-command")

        self.assertEqual(destructive["risk"], "critical")
        self.assertFalse(destructive["allowed_for_execution"])
        self.assertTrue(destructive["requires_approval"])
        self.assertIsNotNone(destructive["blocked_reason"])
        self.assertEqual(unknown["category"], "unknown")
        self.assertFalse(unknown["allowed_for_execution"])
        self.assertFalse(unknown["requires_approval"])
        self.mock_client.command.assert_not_called()

    def test_classify_empty_base_command_returns_error(self):
        """Test empty base command validation."""
        result = self.module.classify_admin_command(base_command=" ")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_preview_admin_command_does_not_call_falcon(self):
        """Test command preview returns a payload shape without executing."""
        result = self.module.preview_admin_command(
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
        self.assertTrue(result["policy_allows_future_execution"])
        self.assertTrue(result["classification_enforced"])
        self.assertFalse(result["approval_gate"]["approval_required"])
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
        preview = self.module.preview_admin_command(
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

        result = self.module.execute_admin_command(
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

    def test_preview_admin_command_reports_missing_context(self):
        """Test command preview calls out missing audit context."""
        result = self.module.preview_admin_command(
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
        self.assertRegex(result["approval_gate"]["approval_phrase"], r"^APPROVE_RTR_ADMIN_[0-9A-F]{16}$")
        self.assertEqual(
            result["command_guidance"]["resource"],
            "falcon://rtr-admin/commands/runscript-guide",
        )
        self.mock_client.command.assert_not_called()

    def test_preview_admin_command_missing_required_fields_returns_error(self):
        """Test command preview rejects missing required command fields."""
        result = self.module.preview_admin_command(
            session_id=" ",
            base_command="ps",
            command_string=" ",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["missing_required"], ["session_id", "command_string"])
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_submits_low_risk_single_host_body(self):
        """Test low-risk single-host RTR Admin execution submits the expected body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_admin_command(
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
        result = self.module.execute_admin_command(
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
        self.assertIn("approval required", result["error"].lower())
        self.assertTrue(result["details"]["approval_gate"]["approval_required"])
        self.assertRegex(
            result["details"]["approval_gate"]["approval_phrase"],
            r"^APPROVE_RTR_ADMIN_[0-9A-F]{16}$",
        )
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_submits_high_impact_after_exact_approval(self):
        """Test high-impact single-host execution submits only after exact approval."""
        blocked = self.module.execute_admin_command(
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
        approval_phrase = blocked["details"]["approval_gate"]["approval_phrase"]
        self.mock_client.command.assert_not_called()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_admin_command(
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

        result = self.module.execute_admin_command(
            session_id="session-1",
            base_command="runscript",
            command_string="runscript -Raw=```Get-Process```",
        )

        self.assertIn("error", result)
        self.assertIn("approval required", result["error"].lower())
        self.assertTrue(result["details"]["approval_gate"]["approval_required"])
        self.mock_client.command.assert_not_called()
        self.assertTrue(
            result["details"]["approval_gate"]["approval_phrase"].startswith(
                "APPROVE_RTR_ADMIN_"
            )
        )
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
        result = self.module.execute_admin_command(
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
        result = self.module.execute_admin_command(
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
        )

        self.assertIn("error", result)
        self.assertEqual(result["details"]["missing_required"], ["session_id"])
        self.mock_client.command.assert_not_called()

    def test_execute_admin_command_wraps_api_error(self):
        """Test single-host RTR Admin execution includes context on API errors."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.execute_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="ps",
            command_string="ps",
        )

        self.assertFalse(result["submitted"])
        self.assertIn("error", result["result"])
        self.assertEqual(result["missing_context"], ["reason", "ticket", "expected_effect"])

    def _limit_le(self, method_name: str) -> int:
        """Return the Pydantic upper-bound metadata for a search limit parameter."""
        signature = inspect.signature(getattr(self.module, method_name))
        limit_field = signature.parameters["limit"].default
        for item in limit_field.metadata:
            le = getattr(item, "le", None)
            if le is not None:
                return le
        raise AssertionError(f"No upper limit metadata found for {method_name}")
