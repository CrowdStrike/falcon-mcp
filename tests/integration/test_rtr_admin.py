"""Integration tests for the RTR Admin module."""

import pytest

from falcon_mcp.modules.rtr_admin import RTRAdminModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestRTRAdminIntegration(BaseIntegrationTest):
    """Integration tests for RTR Admin inventory and local policy helpers.

    Validates:
    - Correct FalconPy operation names for RTR Admin inventory APIs
    - GET query parameter usage for script and put-file detail lookups
    - Put-file content and command-and-wait helpers fail closed locally when unsafe
    - Sort expressions accepted by the current API contract
    - Preview and classification helpers stay local and do not require a live endpoint
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR Admin module with a real client."""
        self.module = RTRAdminModule(falcon_client)

    def _skip_if_admin_scope_error(self, result, context: str) -> None:
        """Skip gracefully when the API client lacks RTR Admin scope."""
        error_text = ""
        if isinstance(result, dict) and "error" in result:
            error_text = str(result)
        elif isinstance(result, list) and result and isinstance(result[0], dict):
            if "error" in result[0]:
                error_text = str(result[0])

        if not error_text:
            return

        scope_markers = ["403", "permission", "scope", "authorization", "access denied"]
        if any(marker in error_text.lower() for marker in scope_markers):
            self.skip_with_warning(
                f"{context} requires Real time response (admin):write; API returned {error_text}",
                context=context,
            )

    def test_search_custom_scripts_operation_name(self):
        """Validate RTR_ListScripts and RTR_GetScriptsV2 operation usage."""
        result = self.call_method(self.module.search_rtr_admin_scripts, limit=1)

        self._skip_if_admin_scope_error(result, "search_rtr_admin_scripts")
        self.assert_no_error(result, context="search_rtr_admin_scripts")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_rtr_admin_scripts",
            )

    def test_search_custom_scripts_with_sort(self):
        """Validate custom script search accepts documented pipe sort syntax."""
        result = self.call_method(
            self.module.search_rtr_admin_scripts,
            sort="created_timestamp|desc",
            limit=1,
        )

        self._skip_if_admin_scope_error(result, "search_rtr_admin_scripts sort")
        self.assert_no_error(result, context="search_rtr_admin_scripts sort")

    def test_search_falcon_scripts_operation_name(self):
        """Validate RTR_ListFalconScripts and RTR_GetFalconScripts operation usage."""
        result = self.call_method(self.module.search_rtr_falcon_scripts, limit=1)

        self._skip_if_admin_scope_error(result, "search_rtr_falcon_scripts")
        self.assert_no_error(result, context="search_rtr_falcon_scripts")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_rtr_falcon_scripts",
            )

    def test_search_falcon_scripts_with_sort(self):
        """Validate Falcon script search accepts a documented sort field."""
        result = self.call_method(
            self.module.search_rtr_falcon_scripts,
            sort="name|asc",
            limit=1,
        )

        self._skip_if_admin_scope_error(result, "search_rtr_falcon_scripts sort")
        self.assert_no_error(result, context="search_rtr_falcon_scripts sort")

    def test_search_put_files_operation_name(self):
        """Validate RTR_ListPut_Files and RTR_GetPut_FilesV2 operation usage."""
        result = self.call_method(self.module.search_rtr_put_files, limit=1)

        self._skip_if_admin_scope_error(result, "search_rtr_put_files")
        self.assert_no_error(result, context="search_rtr_put_files")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result,
                min_length=0,
                context="search_rtr_put_files",
            )

    def test_preview_high_impact_command_is_local(self):
        """Validate high-impact preview returns approval guidance without a Falcon call."""
        result = self.module.preview_rtr_admin_command(
            session_id="session-1",
            device_id="aid-1",
            base_command="runscript",
            command_string="runscript -Raw=```Get-Process```",
            target_hostname="HOST-1",
            reason="integration local policy check",
            ticket="TEST-LOCAL",
            expected_effect="no live Falcon call",
        )

        assert result["operation"] == "RTR_ExecuteAdminCommand"
        assert result["approval_gate"]["approval_required"] is True
        assert result["payload_preview"]["body"]["device_id"] == "aid-1"
        assert result["target"]["device_id"] == "aid-1"

    def test_put_file_contents_requires_id_locally(self):
        """Validate put-file content retrieval fails closed without a file ID."""
        result = self.module.get_rtr_put_file_contents(file_id=" ")

        assert "error" in result

    def test_run_admin_command_and_wait_requires_approval_locally(self):
        """Validate command-and-wait does not bypass high-impact approval."""
        result = self.module.run_rtr_admin_command_and_wait(
            session_id="session-1",
            device_id="aid-1",
            base_command="rm",
            command_string=r"rm C:\Temp\old.bin",
            target_hostname="HOST-1",
            reason="integration local policy check",
            ticket="TEST-LOCAL",
            expected_effect="no live Falcon call",
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        assert "error" in result
        assert result["phase"] == "execute"
