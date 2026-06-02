"""
Tests for the RTR module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr import RTRModule
from tests.modules.utils.test_modules import TestModules


class TestRTRModule(TestModules):
    """Test cases for the RTR module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(RTRModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_rtr_sessions",
            "falcon_search_rtr_audit_sessions",
            "falcon_aggregate_rtr_sessions",
            "falcon_get_rtr_session_details",
            "falcon_init_rtr_session",
            "falcon_pulse_rtr_session",
            "falcon_execute_rtr_read_only_command",
            "falcon_run_rtr_read_only_command_and_wait",
            "falcon_check_rtr_command_status",
            "falcon_list_rtr_session_files",
            "falcon_delete_rtr_session",
        ]
        self.assert_tools_registered(expected_tools)

    def test_tool_annotations(self):
        """Test tool annotations are correctly set."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_rtr_audit_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_aggregate_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_rtr_session_details", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_init_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_pulse_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_execute_rtr_read_only_command",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_run_rtr_read_only_command_and_wait",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations("falcon_check_rtr_command_status", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_list_rtr_session_files", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_rtr_sessions_fql_guide",
            "falcon_search_rtr_audit_sessions_fql_guide",
            "falcon_aggregate_rtr_sessions_guide",
            "falcon_rtr_read_only_investigation_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_sessions_returns_full_details(self):
        """Test searching RTR sessions fetches details after IDs are returned."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["session-1", "session-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "session-1", "aid": "aid-1"},
                    {"id": "session-2", "aid": "aid-2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_sessions(
            filter="hostname:'EXAMPLE-WIN-22'",
            limit=25,
            offset=0,
            sort="created_at.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListAllSessions")
        self.assertEqual(first_call[1]["parameters"]["filter"], "hostname:'EXAMPLE-WIN-22'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "created_at.desc")

        self.assertEqual(second_call[0][0], "RTR_ListSessions")
        self.assertEqual(second_call[1]["body"]["ids"], ["session-1", "session-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "session-1")

    def test_search_audit_sessions(self):
        """Test searching RTR audit sessions."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "audit-session-1",
                        "hostname": "EXAMPLE-WIN-22",
                        "user_id": "user@example.com",
                    }
                ]
            },
        }

        result = self.module.search_audit_sessions(
            filter="created_at:>'now-7d'",
            limit=25,
            offset=0,
            sort="created_at|desc",
            with_command_info=True,
        )

        self.mock_client.command.assert_called_once_with(
            "RTRAuditSessions",
            parameters={
                "filter": "created_at:>'now-7d'",
                "limit": 25,
                "offset": 0,
                "sort": "created_at|desc",
                "with_command_info": True,
            },
        )
        self.assertEqual(result[0]["id"], "audit-session-1")

    def test_search_audit_sessions_error_returns_fql_guide(self):
        """Test audit search with API error returns the RTR audit FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_audit_sessions(
            filter="invalid:::filter",
            limit=10,
            offset=None,
            sort=None,
            with_command_info=False,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("RTR Audit Sessions", result["fql_guide"])
        self.assertIn("Filter error occurred", result["hint"])

    def test_search_audit_sessions_empty_returns_fql_guide(self):
        """Test audit search with no results returns the RTR audit FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_audit_sessions(
            filter="created_at:>'2099-01-01T00:00:00Z'",
            limit=10,
            offset=None,
            sort=None,
            with_command_info=False,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_aggregate_sessions_terms(self):
        """Test RTR session terms aggregation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "commands",
                        "buckets": [{"key": "ps", "count": 5}],
                    }
                ]
            },
        }

        result = self.module.aggregate_sessions(
            field="base_command",
            aggregate_type="terms",
            name="commands",
            filter="created_at:>'now-7d'",
            size=5,
            interval=None,
            date_ranges=None,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_AggregateSessions",
            body=[
                {
                    "field": "base_command",
                    "filter": "created_at:>'now-7d'",
                    "name": "commands",
                    "size": 5,
                    "type": "terms",
                }
            ],
        )
        self.assertEqual(result[0]["name"], "commands")

    def test_aggregate_sessions_date_range(self):
        """Test RTR session date range aggregation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "activity_by_day",
                        "buckets": [{"key": "now-7d_now", "count": 3}],
                    }
                ]
            },
        }

        result = self.module.aggregate_sessions(
            field="created_at",
            aggregate_type="date_range",
            name="activity_by_day",
            filter=None,
            size=None,
            interval="day",
            date_ranges=[{"from": "now-7d", "to": "now"}],
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_AggregateSessions",
            body=[
                {
                    "date_ranges": [{"from": "now-7d", "to": "now"}],
                    "field": "created_at",
                    "interval": "day",
                    "name": "activity_by_day",
                    "type": "date_range",
                }
            ],
        )
        self.assertEqual(result[0]["name"], "activity_by_day")

    def test_get_session_details_empty_ids(self):
        """Test get_session_details returns early for empty input."""
        result = self.module.get_session_details(ids=[])

        self.assertEqual(result, [])
        self.mock_client.command.assert_not_called()

    def test_init_session(self):
        """Test RTR session initialization."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1"}]},
        }

        result = self.module.init_session(
            device_id="aid-123",
            origin="falcon-mcp",
            queue_offline=True,
            timeout=30,
            timeout_duration="30s",
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_InitSession",
            parameters={
                "timeout": 30,
                "timeout_duration": "30s",
            },
            body={
                "device_id": "aid-123",
                "origin": "falcon-mcp",
                "queue_offline": True,
            },
        )
        self.assertEqual(result[0]["session_id"], "session-1")

    def test_execute_read_only_command(self):
        """Test RTR read-only command execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_read_only_command(
            session_id="session-1",
            base_command="cat",
            command_string=r"cat C:\Windows\win.ini",
            persist=False,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteCommand",
            body={
                "session_id": "session-1",
                "base_command": "cat",
                "command_string": r"cat C:\Windows\win.ini",
                "persist": False,
            },
        )
        self.assertEqual(result[0]["cloud_request_id"], "req-123")

    def test_run_read_only_command_and_wait(self):
        """Test RTR read-only command execution with status polling."""
        execute_response = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123", "session_id": "session-1"}]},
        }
        status_response = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "ok"}]},
        }
        self.mock_client.command.side_effect = [execute_response, status_response]

        result = self.module.run_read_only_command_and_wait(
            session_id="session-1",
            base_command="cat",
            command_string=r"cat C:\Windows\win.ini",
            persist=False,
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "RTR_ExecuteCommand",
            body={
                "session_id": "session-1",
                "base_command": "cat",
                "command_string": r"cat C:\Windows\win.ini",
                "persist": False,
            },
        )
        self.mock_client.command.assert_any_call(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 0},
        )
        self.assertEqual(result["cloud_request_id"], "req-123")
        self.assertTrue(result["complete"])
        self.assertFalse(result["timed_out"])
        self.assertEqual(result["stdout"], "ok")

    def test_run_read_only_command_and_wait_advances_sequence_chunks(self):
        """Test command-and-wait reads sequence_id from response for next poll."""
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

        result = self.module.run_read_only_command_and_wait(
            session_id="session-1",
            base_command="cat",
            command_string=r"cat C:\Windows\win.ini",
            persist=False,
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.mock_client.command.assert_any_call(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 0},
        )
        self.mock_client.command.assert_any_call(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 3},
        )
        self.assertEqual(result["stdout"], "part1part2")
        self.assertTrue(result["complete"])

    def test_run_read_only_command_and_wait_execute_error(self):
        """Test command-and-wait returns execute phase on execute failure."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Session ID is invalid"}]},
        }

        result = self.module.run_read_only_command_and_wait(
            session_id="not-a-real-session",
            base_command="ps",
            command_string="ps",
            persist=False,
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["phase"], "execute")

    def test_run_read_only_command_and_wait_timeout(self):
        """Test command-and-wait returns partial status on timeout."""
        execute_response = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123", "session_id": "session-1"}]},
        }
        status_response = {
            "status_code": 200,
            "body": {"resources": [{"complete": False, "stdout": ""}]},
        }
        self.mock_client.command.side_effect = [execute_response, status_response]

        result = self.module.run_read_only_command_and_wait(
            session_id="session-1",
            base_command="ps",
            command_string="ps",
            persist=False,
            timeout_seconds=0,
            poll_interval_seconds=0,
        )

        self.assertEqual(result["cloud_request_id"], "req-123")
        self.assertFalse(result["complete"])
        self.assertTrue(result["timed_out"])
        self.assertIn("warning", result)

    def test_check_command_status(self):
        """Test retrieving RTR command status."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "ok"}]},
        }

        result = self.module.check_command_status(
            cloud_request_id="req-123",
            sequence_id=1,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 1},
        )
        self.assertTrue(result[0]["complete"])

    def test_list_session_files(self):
        """Test listing RTR session files."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "abc"}]},
        }

        result = self.module.list_session_files(session_id="session-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_ListFilesV2",
            parameters={"session_id": "session-1"},
        )
        self.assertEqual(result[0]["sha256"], "abc")

    def test_delete_session(self):
        """Test deleting an RTR session."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1", "deleted": True}]},
        }

        result = self.module.delete_session(session_id="session-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteSession",
            parameters={"session_id": "session-1"},
        )
        self.assertTrue(result[0]["deleted"])

    def test_search_sessions_error_returns_fql_guide(self):
        """Test searching RTR sessions with API error returns FQL guide."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_sessions(
            filter="invalid:::filter",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertIn("Filter error occurred", result["hint"])

    def test_search_sessions_empty_returns_fql_guide(self):
        """Test searching RTR sessions with no results returns FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_sessions(
            filter="hostname:'nonexistent'",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertIn("No results matched", result["hint"])

    def test_search_sessions_with_special_characters_in_filter(self):
        """Test that special characters in filter are passed through safely."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "hostname:'test';DROP TABLE--"
        self.module.search_sessions(
            filter=filter_with_special,
            limit=10,
            offset=None,
            sort=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_search_sessions_with_long_filter_value(self):
        """Test that extremely long filter values are passed through to the API."""
        long_value = "a" * 10000
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_sessions(
            filter=f"hostname:'{long_value}'",
            limit=10,
            offset=None,
            sort=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertIn(long_value, call_args[1]["parameters"]["filter"])

    def test_execute_command_with_malformed_session_id(self):
        """Test execute_read_only_command with malformed session ID returns API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Session ID is invalid"}]},
        }

        result = self.module.execute_read_only_command(
            session_id="not-a-real-session-!!!",
            base_command="ps",
            command_string=None,
            persist=False,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_check_command_status_with_malformed_request_id(self):
        """Test check_command_status with malformed cloud_request_id returns API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "cloud_request_id must be a uuid string"}]},
        }

        result = self.module.check_command_status(
            cloud_request_id="not-a-uuid-!!!",
            sequence_id=0,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_delete_session_with_malformed_session_id(self):
        """Test delete_session with malformed session ID returns API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Session ID is invalid"}]},
        }

        result = self.module.delete_session(session_id="not-a-real-session-!!!")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_init_session_permission_error(self):
        """Test init_session with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.init_session(
            device_id="aid-123",
            origin="falcon-mcp",
            queue_offline=False,
            timeout=None,
            timeout_duration=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
