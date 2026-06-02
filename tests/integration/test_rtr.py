"""Integration tests for the RTR module."""

import warnings

import pytest

from falcon_mcp.modules.hosts import HostsModule
from falcon_mcp.modules.rtr import RTRModule
from tests.integration.utils.base_integration_test import (
    BaseIntegrationTest,
    resolve_field_defaults,
)


@pytest.mark.integration
class TestRTRIntegration(BaseIntegrationTest):
    """Integration tests for the RTR module with real API calls.

    Validates:
    - Correct FalconPy operation names for RTR session search and details
    - Two-step search pattern returns full session details, not just IDs
    - POST body usage for session detail lookups
    - FQL filter field names are accepted by the API
    - FQL examples from documentation are syntactically valid
    - Sort expressions work correctly
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR module with a real client."""
        self.module = RTRModule(falcon_client)

    def _assert_fql_field_accepted(self, field_filter: str, context: str) -> None:
        """Assert that an FQL filter expression is accepted by the API.

        Calls search_sessions with the filter and checks that the API did not
        reject the field name with a 400 error.  The method returns either a
        list (results found) or a dict (FQL guide response on empty/error).

        For dict responses we inspect the ``hint`` value:
        - "No results matched" → field was accepted, just no data
        - "Filter error occurred" → field was rejected (HTTP 400)
        """
        result = self.call_method(self.module.search_sessions, filter=field_filter, limit=1)
        self.assert_no_error(result, context=context)

        if isinstance(result, dict):
            hint = result.get("hint", "")
            assert "Filter error occurred" not in hint, (
                f"FQL field rejected by API ({context}): filter={field_filter!r}, hint={hint}"
            )

    def _skip_if_scope_error(self, result, scope_hint: str, context: str) -> None:
        """Skip gracefully when the tenant API client lacks an optional RTR scope."""
        error_text = ""
        if isinstance(result, dict) and "error" in result:
            error_text = str(result)
        elif isinstance(result, list) and result and isinstance(result[0], dict):
            if "error" in result[0]:
                error_text = str(result[0])

        if not error_text:
            return

        scope_error_markers = ["403", "permission", "scope", "authorization", "access denied"]
        if any(marker in error_text.lower() for marker in scope_error_markers):
            self.skip_with_warning(
                f"{context} requires {scope_hint}; API client returned {error_text}",
                context=context,
            )

    # ------------------------------------------------------------------
    # Existing tests
    # ------------------------------------------------------------------

    def test_search_rtr_sessions_returns_details(self):
        """Test that RTR session search returns full session details."""
        result = self.call_method(self.module.search_sessions, limit=5)

        self.assert_no_error(result, context="search_rtr_sessions")

        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_rtr_sessions")
            if len(result) > 0:
                self.assert_search_returns_details(
                    result,
                    expected_fields=["id", "device_id", "hostname"],
                    context="search_rtr_sessions",
                )

    def test_search_rtr_sessions_with_sort(self):
        """Test RTR session search with a supported sort expression."""
        result = self.call_method(
            self.module.search_sessions,
            sort="created_at.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_rtr_sessions with sort")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_rtr_sessions with sort",
            )

    def test_get_rtr_session_details_with_valid_id(self):
        """Test session detail lookup using a valid session ID."""
        search_result = self.call_method(self.module.search_sessions, limit=1)

        if not isinstance(search_result, list) or len(search_result) == 0:
            self.skip_with_warning(
                "No RTR sessions available to test get_rtr_session_details",
                context="test_get_rtr_session_details_with_valid_id",
            )

        session_id = self.get_first_id(search_result)
        if not session_id:
            self.skip_with_warning(
                "Could not extract session ID from RTR search results",
                context="test_get_rtr_session_details_with_valid_id",
            )

        result = self.call_method(self.module.get_session_details, ids=[session_id])

        self.assert_no_error(result, context="get_rtr_session_details")
        self.assert_valid_list_response(result, min_length=1, context="get_rtr_session_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "device_id", "hostname"],
            context="get_rtr_session_details",
        )

    def test_operation_names_are_correct(self):
        """Validate that the RTR FalconPy operation names are correct."""
        result = self.call_method(self.module.search_sessions, limit=1)
        self.assert_no_error(result, context="RTR operation name validation")

    def test_search_rtr_audit_sessions(self):
        """Validate the RTR audit search operation and parameter shape."""
        result = self.call_method(
            self.module.search_audit_sessions,
            limit=1,
            sort="created_at|desc",
            with_command_info=False,
        )

        self._skip_if_scope_error(
            result,
            "real-time-response-audit:read",
            "search_rtr_audit_sessions",
        )
        self.assert_no_error(result, context="search_rtr_audit_sessions")

        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_rtr_audit_sessions",
            )

    def test_aggregate_rtr_sessions(self):
        """Validate RTR session aggregation operation and request body shape."""
        result = self.call_method(
            self.module.aggregate_sessions,
            field="base_command",
            aggregate_type="terms",
            name="commands",
            filter="created_at:>'now-30d'",
            size=5,
        )

        self._skip_if_scope_error(
            result,
            "Real time response:read",
            "aggregate_rtr_sessions",
        )
        self.assert_no_error(result, context="aggregate_rtr_sessions")

        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="aggregate_rtr_sessions",
            )

    # ------------------------------------------------------------------
    # FQL filter tests
    # ------------------------------------------------------------------

    def test_search_rtr_sessions_with_filter(self):
        """Test search_sessions with a basic FQL filter."""
        result = self.call_method(
            self.module.search_sessions,
            filter="hostname:'NONEXISTENT_HOST_XYZZY12345'",
            limit=1,
        )

        self.assert_no_error(result, context="search_rtr_sessions with filter")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_rtr_sessions with filter"
            )

    def test_fql_string_fields_are_accepted(self):
        """Validate that all documented string FQL fields are accepted."""
        string_fields = [
            "id",
            "aid",
            "hostname",
            "user_id",
            "origin",
            "cloud_request_id",
            "command_string",
            "base_command",
        ]
        for field in string_fields:
            self._assert_fql_field_accepted(
                f"{field}:'NONEXISTENT_VALUE_XYZZY12345'",
                context=f"string field {field}",
            )

    def test_fql_boolean_fields_are_accepted(self):
        """Validate that all documented boolean FQL fields are accepted."""
        boolean_fields = ["offline_queued"]
        for field in boolean_fields:
            self._assert_fql_field_accepted(
                f"{field}:true",
                context=f"boolean field {field}",
            )

    def test_fql_timestamp_fields_are_accepted(self):
        """Validate that all documented timestamp FQL fields are accepted."""
        timestamp_fields = ["created_at", "updated_at", "deleted_at"]
        for field in timestamp_fields:
            self._assert_fql_field_accepted(
                f"{field}:>'2099-01-01T00:00:00Z'",
                context=f"timestamp field {field}",
            )

    # ------------------------------------------------------------------
    # FQL example validation
    # ------------------------------------------------------------------

    def test_fql_example_user_id_at_me(self):
        """Validate the @me special token is accepted."""
        self._assert_fql_field_accepted(
            "user_id:'@me'",
            context="user_id @me special token",
        )

    def test_fql_example_deleted_at_future_timestamp(self):
        """Validate deleted_at timestamp comparison syntax."""
        self._assert_fql_field_accepted(
            "deleted_at:>'2099-01-01T00:00:00Z'",
            context="deleted_at future timestamp",
        )

    def test_fql_example_compound_filter(self):
        """Validate compound AND filter with wildcard."""
        self._assert_fql_field_accepted(
            "offline_queued:true+hostname:'NONEXISTENT_XYZZY12345*'",
            context="compound AND filter with wildcard",
        )

    # ------------------------------------------------------------------
    # Sort expression tests
    # ------------------------------------------------------------------

    def test_sort_additional_fields(self):
        """Validate additional sort expressions beyond created_at.desc."""
        sort_expressions = ["updated_at.asc", "hostname.asc"]
        for sort_expr in sort_expressions:
            result = self.call_method(
                self.module.search_sessions,
                sort=sort_expr,
                limit=1,
            )
            self.assert_no_error(result, context=f"sort {sort_expr}")


@pytest.mark.integration
class TestRTRLifecycleIntegration(BaseIntegrationTest):
    """Integration tests for RTR session lifecycle (mutating operations).

    Validates:
    - Correct FalconPy operation names for RTR_InitSession, RTR_PulseSession,
      RTR_ExecuteCommand, RTR_CheckCommandStatus, RTR_ListFilesV2, RTR_DeleteSession
    - Parameter shapes accepted by the real API
    - Response schemas match expectations

    Requires:
    - At least one host in the Falcon environment
    - API key with Real time response:read scope
    - Real time response:write scope for list_session_files (skipped if missing)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR module with a real client."""
        self.module = RTRModule(falcon_client)

    @pytest.fixture(autouse=True, scope="class")
    def init_rtr_session(self, falcon_client):
        """Initialize an RTR session for the class and clean up after all tests.

        Looks up a real host AID via HostsModule, then opens an RTR session
        with queue_offline=True so the API accepts immediately even if the
        host is offline.
        """
        hosts_module = HostsModule(falcon_client)
        rtr_module = RTRModule(falcon_client)

        # Find a real host (last seen within the past hour)
        host_kwargs = resolve_field_defaults(
            hosts_module.search_hosts,
            {
                "filter": "last_seen:>='now-1h'",
                "limit": 1,
            },
        )
        hosts_result = hosts_module.search_hosts(**host_kwargs)

        if not isinstance(hosts_result, list) or len(hosts_result) == 0:
            pytest.skip("No hosts found in environment")

        first_host = hosts_result[0]
        if isinstance(first_host, dict) and "error" in first_host:
            pytest.skip(f"Host search failed (check Hosts:read scope): {first_host}")

        device_id = first_host.get("device_id") if isinstance(first_host, dict) else None
        if not device_id:
            pytest.skip("Could not extract device_id from host search results")

        # Init RTR session with queue_offline=True for safety
        init_kwargs = resolve_field_defaults(
            rtr_module.init_session,
            {
                "device_id": device_id,
                "queue_offline": True,
                "origin": "falcon-mcp-integration-test",
            },
        )
        result = rtr_module.init_session(**init_kwargs)

        # Check for error (e.g. missing RTR read scope)
        if isinstance(result, dict) and "error" in result:
            pytest.skip(f"Cannot init RTR session (check Real time response:read scope): {result}")
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                pytest.skip(
                    f"Cannot init RTR session (check Real time response:read scope): {first}"
                )

        # Extract session_id from response
        session_id = None
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict):
                session_id = first.get("session_id")
        elif isinstance(result, dict):
            session_id = result.get("session_id")

        if not session_id:
            pytest.skip(f"Could not extract session_id from init response: {result}")

        self.__class__._session_id = session_id
        self.__class__._device_id = device_id
        self.__class__._init_result = result
        self.__class__._cloud_request_id = None  # sentinel for cascade-skip

        yield

        # Teardown: delete the session (idempotent)
        try:
            delete_kwargs = resolve_field_defaults(
                rtr_module.delete_session,
                {
                    "session_id": session_id,
                },
            )
            rtr_module.delete_session(**delete_kwargs)
        except Exception as e:
            warnings.warn(
                f"Failed to clean up RTR session {session_id}: {e}",
                stacklevel=2,
            )

    # ------------------------------------------------------------------
    # Test methods
    # ------------------------------------------------------------------

    def test_init_session_response_shape(self):
        """Validate that RTR_InitSession returned a dict with a session_id.

        Uses the stored fixture result — no extra API call needed.
        """
        result = self.__class__._init_result

        # Result is either a single dict or a list wrapping one
        if isinstance(result, list):
            assert len(result) > 0, "init_session returned empty list"
            session = result[0]
        else:
            session = result

        assert isinstance(session, dict), (
            f"Expected dict for init_session response, got {type(session)}"
        )
        assert "session_id" in session, (
            f"Expected 'session_id' in init response. Available fields: {list(session.keys())}"
        )
        assert isinstance(session["session_id"], str) and len(session["session_id"]) > 0, (
            f"Expected non-empty session_id string, got {session['session_id']!r}"
        )

    def test_pulse_session(self):
        """Validate RTR_PulseSession accepts the correct parameter shape."""
        result = self.call_method(
            self.module.pulse_session,
            device_id=self.__class__._device_id,
            queue_offline=True,
        )

        self.assert_no_error(result, context="pulse_session")

        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="pulse_session")

    def test_execute_read_only_command(self):
        """Validate RTR_ExecuteCommand with a simple `ls` command.

        If the host is offline the API returns an error — store None for
        cloud_request_id and downstream tests will cascade-skip.

        Note: the RTR API requires `command_string` to contain the full
        command line; `base_command` alone is not sufficient.
        """
        result = self.call_method(
            self.module.execute_read_only_command,
            session_id=self.__class__._session_id,
            base_command="ls",
            command_string="ls C:\\",
        )

        # Host may be offline — treat error as a graceful skip
        if isinstance(result, dict) and "error" in result:
            self.__class__._cloud_request_id = None
            self.skip_with_warning(
                "execute_read_only_command returned error (host likely offline)",
                context="test_execute_read_only_command",
            )

        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                self.__class__._cloud_request_id = None
                self.skip_with_warning(
                    "execute_read_only_command returned error (host likely offline)",
                    context="test_execute_read_only_command",
                )

        self.assert_no_error(result, context="execute_read_only_command")

        # Extract cloud_request_id
        cloud_request_id = None
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict):
                cloud_request_id = first.get("cloud_request_id")
        elif isinstance(result, dict):
            cloud_request_id = result.get("cloud_request_id")

        assert cloud_request_id, f"Expected cloud_request_id in execute response. Got: {result}"
        self.__class__._cloud_request_id = cloud_request_id

    def test_run_read_only_command_and_wait(self):
        """Validate the command-and-wait helper against a real RTR session."""
        result = self.call_method(
            self.module.run_read_only_command_and_wait,
            session_id=self.__class__._session_id,
            base_command="pwd",
            command_string="pwd",
            timeout_seconds=30,
            poll_interval_seconds=2,
        )

        if isinstance(result, dict) and "error" in result:
            self.skip_with_warning(
                "run_read_only_command_and_wait returned error (host likely offline)",
                context="test_run_read_only_command_and_wait",
            )

        self.assert_no_error(result, context="run_read_only_command_and_wait")

        assert isinstance(result, dict), (
            f"Expected dict response from run_read_only_command_and_wait, got {type(result)}"
        )
        assert result.get("cloud_request_id"), (
            f"Expected cloud_request_id in command-and-wait response. Got: {result}"
        )
        assert "complete" in result, (
            f"Expected complete flag in command-and-wait response. Got: {result}"
        )
        assert "timed_out" in result, (
            f"Expected timed_out flag in command-and-wait response. Got: {result}"
        )

        if result.get("timed_out"):
            self.skip_with_warning(
                "RTR command did not complete before the helper timeout",
                context="test_run_read_only_command_and_wait",
            )

    def test_check_command_status(self):
        """Validate RTR_CheckCommandStatus returns output for a known request."""
        if self.__class__._cloud_request_id is None:
            self.skip_with_warning(
                "No cloud_request_id available (execute command was skipped or failed)",
                context="test_check_command_status",
            )

        result = self.call_method(
            self.module.check_command_status,
            cloud_request_id=self.__class__._cloud_request_id,
            sequence_id=0,
        )

        self.assert_no_error(result, context="check_command_status")

        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="check_command_status")
            if len(result) > 0:
                first = result[0]
                if isinstance(first, dict):
                    assert "complete" in first, (
                        f"Expected 'complete' field in command status. "
                        f"Available fields: {list(first.keys())}"
                    )
                    assert "stdout" in first, (
                        f"Expected 'stdout' field in command status. "
                        f"Available fields: {list(first.keys())}"
                    )

    def test_list_session_files(self):
        """Validate RTR_ListFilesV2 against a real session.

        This operation requires Real time response:write scope. If the API
        returns a 403 error, skip gracefully with a scope hint.
        """
        if self.__class__._cloud_request_id is None:
            self.skip_with_warning(
                "No cloud_request_id available (execute command was skipped or failed)",
                context="test_list_session_files",
            )

        result = self.call_method(
            self.module.list_session_files,
            session_id=self.__class__._session_id,
        )

        # Handle 403 from missing :write scope
        if isinstance(result, dict) and "error" in result:
            error_str = str(result.get("error", ""))
            if "403" in error_str or "Forbidden" in error_str:
                self.skip_with_warning(
                    "list_session_files returned 403 (check Real time response:write scope)",
                    context="test_list_session_files",
                )
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                error_str = str(first.get("error", ""))
                if "403" in error_str or "Forbidden" in error_str:
                    self.skip_with_warning(
                        "list_session_files returned 403 (check Real time response:write scope)",
                        context="test_list_session_files",
                    )

        self.assert_no_error(result, context="list_session_files")

        if isinstance(result, list):
            # Empty is valid — ls doesn't extract files
            self.assert_valid_list_response(result, min_length=0, context="list_session_files")

    def test_delete_session(self):
        """Validate RTR_DeleteSession by creating and deleting a disposable session.

        Does NOT delete the shared fixture's session — creates a fresh
        disposable session with queue_offline=True and immediately deletes it.
        """
        # Create a disposable session
        init_result = self.call_method(
            self.module.init_session,
            device_id=self.__class__._device_id,
            queue_offline=True,
            origin="falcon-mcp-integration-test-delete",
        )

        # Extract session_id from disposable session
        disposable_session_id = None
        if isinstance(init_result, list) and len(init_result) > 0:
            first = init_result[0]
            if isinstance(first, dict):
                if "error" in first:
                    self.skip_with_warning(
                        f"Could not create disposable session: {first}",
                        context="test_delete_session",
                    )
                disposable_session_id = first.get("session_id")
        elif isinstance(init_result, dict):
            if "error" in init_result:
                self.skip_with_warning(
                    f"Could not create disposable session: {init_result}",
                    context="test_delete_session",
                )
            disposable_session_id = init_result.get("session_id")

        if not disposable_session_id:
            self.skip_with_warning(
                f"Could not extract session_id from disposable init response: {init_result}",
                context="test_delete_session",
            )

        # Delete it
        delete_result = self.call_method(
            self.module.delete_session,
            session_id=disposable_session_id,
        )

        self.assert_no_error(delete_result, context="delete_session")
