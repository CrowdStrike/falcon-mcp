"""
Real Time Response Admin module for Falcon MCP Server.

This module exposes RTR Admin inventory, command status, command preview, and
admin command execution helpers. It does not manage script / put-file uploads,
updates, or deletes.
"""

import hashlib
import json
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.utils import prepare_api_parameters, unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr_admin import (
    EMBEDDED_FALCON_SCRIPT_FQL_SYNTAX,
    EMBEDDED_PUT_FILE_FQL_SYNTAX,
    EMBEDDED_SCRIPT_FQL_SYNTAX,
    RTR_ADMIN_RUNSCRIPT_RAW_GUIDE,
    RTR_ADMIN_TOOL_USE_GUIDE,
    SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION,
    SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION,
    SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION,
)

READ_ONLY_ADMIN_COMMANDS = {
    "cat",
    "cd",
    "clear",
    "env",
    "eventlog",
    "filehash",
    "getsid",
    "help",
    "history",
    "ipconfig",
    "ls",
    "mount",
    "netstat",
    "ps",
}

EVIDENCE_COLLECTION_COMMANDS = {"get"}
SENSITIVE_COLLECTION_COMMANDS = {"memdump", "xmemdump"}
BLOCKED_ADMIN_COMMANDS = {
    "cp",
    "encrypt",
    "kill",
    "map",
    "mkdir",
    "mv",
    "put",
    "put-and-run",
    "restart",
    "rm",
    "run",
    "shutdown",
    "unmap",
    "zip",
}
READ_ONLY_UPDATE_SUBCOMMANDS = {"history", "list", "query"}

RTR_ADMIN_SAFETY_DISCLAIMER = (
    "RTR Admin can affect live endpoints. This module can execute admin "
    "commands when explicitly invoked, but automated tests must stay mocked, "
    "smoke-only, or read-only. Any live endpoint-changing test must target "
    "only a PC chosen by the operator."
)

RTR_ADMIN_EXECUTION_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


def _normalize_field_value(value: Any) -> Any:
    """Unwrap direct-call Pydantic Field defaults into plain Python values."""
    return unwrap_field_default(value)


class RTRAdminModule(BaseModule):
    """Module for RTR Admin inventory and pre-execution safety checks."""

    MODULE_NAME = "rtr_admin"

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_scripts,
            name="search_rtr_admin_scripts",
        )
        self._add_tool(
            server=server,
            method=self.get_script_details,
            name="get_rtr_admin_script_details",
        )
        self._add_tool(
            server=server,
            method=self.search_falcon_scripts,
            name="search_rtr_falcon_scripts",
        )
        self._add_tool(
            server=server,
            method=self.get_falcon_script_details,
            name="get_rtr_falcon_script_details",
        )
        self._add_tool(
            server=server,
            method=self.search_put_files,
            name="search_rtr_put_files",
        )
        self._add_tool(
            server=server,
            method=self.get_put_file_details,
            name="get_rtr_put_file_details",
        )
        self._add_tool(
            server=server,
            method=self.check_admin_command_status,
            name="check_rtr_admin_command_status",
        )
        self._add_tool(
            server=server,
            method=self.classify_admin_command,
            name="classify_rtr_admin_command",
        )
        self._add_tool(
            server=server,
            method=self.preview_admin_command,
            name="preview_rtr_admin_command",
        )
        self._add_tool(
            server=server,
            method=self.execute_admin_command,
            name="execute_rtr_admin_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        resources = [
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/scripts/search/fql-guide"),
                name="falcon_search_rtr_admin_scripts_fql_guide",
                description="Contains the guide for the `filter` param of the custom RTR script search tool.",
                text=SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/falcon-scripts/search/fql-guide"),
                name="falcon_search_rtr_falcon_scripts_fql_guide",
                description="Contains the guide for the `filter` param of the Falcon script search tool.",
                text=SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/put-files/search/fql-guide"),
                name="falcon_search_rtr_put_files_fql_guide",
                description="Contains the guide for the `filter` param of the RTR put-file search tool.",
                text=SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/workflows/admin-guide"),
                name="falcon_rtr_admin_tool_use_guide",
                description="Contains RTR Admin inventory, preview, execution, and polling guidance.",
                text=RTR_ADMIN_TOOL_USE_GUIDE,
            ),
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/commands/runscript-guide"),
                name="falcon_rtr_admin_runscript_raw_guide",
                description="Contains RTR Admin runscript raw command construction guidance.",
                text=RTR_ADMIN_RUNSCRIPT_RAW_GUIDE,
            ),
        ]

        for resource in resources:
            self._add_resource(server, resource)

    def search_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description=EMBEDDED_SCRIPT_FQL_SYNTAX,
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of custom script IDs to return. Max: 5000.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort custom scripts by a supported field such as `created_at|desc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR custom scripts and return full metadata records.

        Use this to find reusable custom RTR scripts by name, platform, or
        permission type. Consult falcon://rtr-admin/scripts/search/fql-guide
        before constructing filter expressions.
        """
        return self._search_and_get_details(
            search_operation="RTR_ListScripts",
            get_operation="RTR_GetScriptsV2",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            fql_documentation=SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION,
        )

    def get_script_details(
        self,
        ids: list[str] = Field(description="Custom RTR script IDs to retrieve."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve custom RTR script metadata and content by script ID."""
        return self._get_details("RTR_GetScriptsV2", ids)

    def search_falcon_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description=EMBEDDED_FALCON_SCRIPT_FQL_SYNTAX,
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=100,
            description="Maximum number of Falcon script IDs to return. Max: 100.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort Falcon scripts by a supported field such as `name|asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search CrowdStrike-provided Falcon scripts and return full records.

        Use this to find CrowdStrike-provided RTR scripts by name or platform.
        Consult falcon://rtr-admin/falcon-scripts/search/fql-guide before
        constructing filter expressions.
        """
        return self._search_and_get_details(
            search_operation="RTR_ListFalconScripts",
            get_operation="RTR_GetFalconScripts",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            fql_documentation=SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION,
        )

    def get_falcon_script_details(
        self,
        ids: list[str] = Field(description="Falcon script IDs to retrieve."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve CrowdStrike-provided Falcon script metadata and content by ID."""
        return self._get_details("RTR_GetFalconScripts", ids)

    def search_put_files(
        self,
        filter: str | None = Field(
            default=None,
            description=EMBEDDED_PUT_FILE_FQL_SYNTAX,
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of put-file IDs to return. Max: 5000.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort put-files by a supported field such as `created_at|desc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR put-files and return full metadata records.

        Use this to review put-file inventory before considering an admin
        command that references staged content. Consult
        falcon://rtr-admin/put-files/search/fql-guide before constructing
        filter expressions.
        """
        return self._search_and_get_details(
            search_operation="RTR_ListPut_Files",
            get_operation="RTR_GetPut_FilesV2",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            fql_documentation=SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION,
        )

    def get_put_file_details(
        self,
        ids: list[str] = Field(description="RTR put-file IDs to retrieve."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve RTR put-file metadata by ID.

        This tool intentionally returns metadata only. It does not expose
        put-file content retrieval in the first RTR Admin slice.
        """
        return self._get_details("RTR_GetPut_FilesV2", ids)

    def check_admin_command_status(
        self,
        cloud_request_id: str = Field(
            description="Cloud request ID returned from a prior RTR Admin command.",
        ),
        sequence_id: int = Field(
            default=0,
            ge=0,
            description="Sequence chunk to retrieve for command output. Starts at 0.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve status and output for a prior RTR Admin command.

        This is a read-only status lookup. It cannot start a new command.
        """
        cloud_request_id = _normalize_field_value(cloud_request_id)
        sequence_id = _normalize_field_value(sequence_id)

        if not isinstance(cloud_request_id, str) or not cloud_request_id.strip():
            return _format_error_response(
                "cloud_request_id is required to check RTR Admin command status. "
                "No Falcon call was made."
            )

        if not isinstance(sequence_id, int) or sequence_id < 0:
            return _format_error_response(
                "sequence_id must be a non-negative integer. No Falcon call was made."
            )

        return self._base_query_api_call(
            operation="RTR_CheckAdminCommandStatus",
            query_params={
                "cloud_request_id": cloud_request_id,
                "sequence_id": sequence_id,
            },
            error_message="Failed to check RTR Admin command status",
        )

    def classify_admin_command(
        self,
        base_command: str = Field(
            description="RTR Admin base command to classify, such as `get`, `runscript`, `rm`, or `reg`.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Optional full command line for subcommand-sensitive checks, such as `reg query ...`.",
        ),
    ) -> dict[str, Any]:
        """Classify an RTR Admin command without executing it.

        Use this before designing or approving any RTR Admin execution flow.
        This policy helper is intentionally local and does not call Falcon.
        """
        base_command = _normalize_field_value(base_command)
        command_string = _normalize_field_value(command_string)

        if not isinstance(base_command, str) or not base_command.strip():
            return _format_error_response(
                "base_command is required. Provide an RTR Admin base command such "
                "as `ps`, `get`, `reg`, `runscript`, or `rm`. No Falcon call was made."
            )

        normalized = base_command.strip().lower()
        command_text = command_string.strip() if isinstance(command_string, str) else ""
        command_lower = command_text.lower()

        if normalized in READ_ONLY_ADMIN_COMMANDS:
            return self._classification(
                normalized,
                "read_only",
                "low",
                True,
                "Command is normally read-only in RTR Admin.",
            )

        if normalized == "reg":
            if command_lower.split()[:2] == ["reg", "query"]:
                return self._classification(
                    normalized,
                    "read_only",
                    "low",
                    True,
                    "`reg query` is read-only; other registry subcommands are blocked.",
                )
            return self._classification(
                normalized,
                "high_impact",
                "critical",
                False,
                "Registry writes, loads, unloads, and deletes require explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
            )

        if normalized == "update":
            update_tokens = command_lower.split()
            if len(update_tokens) >= 2 and update_tokens[1] in READ_ONLY_UPDATE_SUBCOMMANDS:
                return self._classification(
                    normalized,
                    "read_only",
                    "low",
                    True,
                    "`update history`, `update list`, and `update query` are read-only; "
                    "update installs are blocked.",
                )
            return self._classification(
                normalized,
                "high_impact",
                "critical",
                False,
                "Sensor update install actions require explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
            )

        if normalized in EVIDENCE_COLLECTION_COMMANDS:
            return self._classification(
                normalized,
                "evidence_collection",
                "medium",
                True,
                "Command can collect files from a chosen host and needs explicit target review.",
            )

        if normalized == "runscript":
            return self._classification(
                normalized,
                "script_execution",
                "critical",
                False,
                "Script execution is high risk and requires explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
            )

        if normalized in SENSITIVE_COLLECTION_COMMANDS:
            return self._classification(
                normalized,
                "sensitive_collection",
                "high",
                False,
                "Memory dump commands can collect sensitive data and require explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
            )

        if normalized in BLOCKED_ADMIN_COMMANDS:
            return self._classification(
                normalized,
                "high_impact",
                "critical",
                False,
                "Command can write, delete, execute, disrupt, or stage material on a host and requires explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
            )

        return self._classification(
            normalized,
            "unknown",
            "unknown",
            False,
            "Unknown RTR Admin command. It is blocked until reviewed and explicitly allowlisted.",
        )

    def preview_admin_command(
        self,
        session_id: str = Field(description="RTR session ID that would receive the command."),
        device_id: str | None = Field(
            default=None,
            description="Optional host agent ID included in the preview target and Falcon body when supplied.",
        ),
        base_command: str = Field(description="RTR Admin base command to preview."),
        command_string: str = Field(description="Full RTR Admin command string to preview."),
        command_id: int | None = Field(
            default=None,
            ge=0,
            description="Optional command sequence ID that would be sent as `id` in the Falcon body.",
        ),
        target_hostname: str | None = Field(
            default=None,
            description="Optional hostname for human review of the selected target.",
        ),
        reason: str | None = Field(
            default=None,
            description="Why this command is being considered.",
        ),
        ticket: str | None = Field(
            default=None,
            description="Ticket, case, or incident identifier for audit context.",
        ),
        expected_effect: str | None = Field(
            default=None,
            description="Expected endpoint effect if this command were executed later.",
        ),
        persist: bool = Field(
            default=False,
            description="Whether the command would be persisted. Defaults false.",
        ),
    ) -> dict[str, Any]:
        """Preview an RTR Admin command payload without executing it.

        This tool returns the exact Falcon operation and body shape that a later
        execution tool would use, plus local policy classification. It never
        calls Falcon and cannot execute the command.
        """
        session_id = _normalize_field_value(session_id)
        device_id = _normalize_field_value(device_id)
        base_command = _normalize_field_value(base_command)
        command_string = _normalize_field_value(command_string)
        command_id = _normalize_field_value(command_id)
        target_hostname = _normalize_field_value(target_hostname)
        reason = _normalize_field_value(reason)
        ticket = _normalize_field_value(ticket)
        expected_effect = _normalize_field_value(expected_effect)
        persist = _normalize_field_value(persist)

        missing_required = []
        if not isinstance(session_id, str) or not session_id.strip():
            missing_required.append("session_id")
        if not isinstance(base_command, str) or not base_command.strip():
            missing_required.append("base_command")
        if not isinstance(command_string, str) or not command_string.strip():
            missing_required.append("command_string")

        if missing_required:
            return _format_error_response(
                "RTR Admin command preview requires non-empty session_id, "
                "base_command, and command_string. No Falcon call was made.",
                details={"missing_required": missing_required},
            )

        classification = self.classify_admin_command(base_command, command_string)
        if self._is_error(classification):
            return classification

        body = self._execute_admin_command_body(
            base_command=base_command,
            command_string=command_string,
            session_id=session_id,
            device_id=device_id,
            command_id=command_id,
            persist=bool(persist),
        )
        approval_gate = self._approval_gate(
            operation="RTR_ExecuteAdminCommand",
            classification=classification,
            payload={"body": prepare_api_parameters(body)},
            target={
                "session_id": session_id,
                "device_id": device_id,
                "hostname": target_hostname,
            },
        )

        required_context = {
            "reason": reason,
            "ticket": ticket,
            "expected_effect": expected_effect,
        }
        missing_context = [key for key, value in required_context.items() if not value]

        return {
            "execution_available": True,
            "execution_tool": "falcon_execute_rtr_admin_command",
            "policy_allows_future_execution": classification["allowed_for_execution"],
            "policy_note": (
                "Classification is enforced before Falcon calls. High-impact "
                "commands require the exact operator approval phrase returned "
                "by this preview or by a blocked execution attempt."
            ),
            "classification_enforced": True,
            "classification": classification,
            "safety_disclaimer": RTR_ADMIN_SAFETY_DISCLAIMER,
            "command_guidance": self._command_guidance(base_command, command_string),
            "missing_context": missing_context,
            "required_context": list(required_context.keys()),
            "target": {
                "session_id": session_id,
                "device_id": device_id,
                "hostname": target_hostname,
            },
            "operation": "RTR_ExecuteAdminCommand",
            "payload_preview": {
                "body": prepare_api_parameters(body),
            },
            "review_note": (
                "This preview does not call Falcon. Use the execution tool only "
                "after reviewing the target and expected endpoint effect."
            ),
            "approval_gate": approval_gate,
        }

    def execute_admin_command(
        self,
        base_command: str = Field(description="RTR Admin base command to execute."),
        command_string: str = Field(description="Full RTR Admin command string to execute."),
        session_id: str | None = Field(
            default=None,
            description="RTR session ID to execute the command against.",
        ),
        device_id: str | None = Field(
            default=None,
            description="Optional device AID for human review. Falcon execution requires session_id.",
        ),
        command_id: int | None = Field(
            default=None,
            ge=0,
            description="Optional command sequence ID sent as `id` in the Falcon body.",
        ),
        persist: bool = Field(
            default=False,
            description="Execute when the host returns to service. Defaults false.",
        ),
        target_hostname: str | None = Field(
            default=None,
            description="Optional hostname for human review. Not sent to Falcon.",
        ),
        reason: str | None = Field(
            default=None,
            description="Why this command is being executed.",
        ),
        ticket: str | None = Field(
            default=None,
            description="Ticket, case, or incident identifier for audit context.",
        ),
        expected_effect: str | None = Field(
            default=None,
            description="Expected endpoint effect of the command.",
        ),
        operator_approval: str | None = Field(
            default=None,
            description=(
                "Exact approval phrase required for high-impact RTR Admin commands. "
                "Get it from preview or from the approval-required response after "
                "human review."
            ),
        ),
    ) -> dict[str, Any]:
        """Execute an RTR Admin command on a single host.

        High-impact commands are blocked before the Falcon API call unless the
        exact operator approval phrase for this payload is supplied.
        """
        base_command = _normalize_field_value(base_command)
        command_string = _normalize_field_value(command_string)
        session_id = _normalize_field_value(session_id)
        device_id = _normalize_field_value(device_id)
        command_id = _normalize_field_value(command_id)
        persist = _normalize_field_value(persist)
        target_hostname = _normalize_field_value(target_hostname)
        reason = _normalize_field_value(reason)
        ticket = _normalize_field_value(ticket)
        expected_effect = _normalize_field_value(expected_effect)
        operator_approval = _normalize_field_value(operator_approval)

        missing_required = []
        if not isinstance(base_command, str) or not base_command.strip():
            missing_required.append("base_command")
        if not isinstance(command_string, str) or not command_string.strip():
            missing_required.append("command_string")
        if not self._has_text(session_id):
            missing_required.append("session_id")

        if missing_required:
            return _format_error_response(
                "RTR Admin command execution requires base_command, command_string, "
                "and session_id. No Falcon call was made.",
                details={"missing_required": missing_required},
            )

        classification = self.classify_admin_command(base_command, command_string)
        if self._is_error(classification):
            return classification

        body = self._execute_admin_command_body(
            base_command=base_command,
            command_string=command_string,
            session_id=session_id,
            device_id=device_id,
            command_id=command_id,
            persist=bool(persist),
        )
        payload = {"body": prepare_api_parameters(body)}
        target = {
            "session_id": session_id,
            "device_id": device_id,
            "hostname": target_hostname,
        }
        approval_gate = self._approval_gate(
            operation="RTR_ExecuteAdminCommand",
            classification=classification,
            payload=payload,
            target=target,
        )
        policy_error = self._enforce_admin_command_policy(
            classification=classification,
            approval_gate=approval_gate,
            operator_approval=operator_approval,
            target=target,
            payload=payload,
        )
        if policy_error:
            return policy_error

        result = self._base_query_api_call(
            operation="RTR_ExecuteAdminCommand",
            body_params=body,
            error_message="Failed to execute RTR Admin command",
        )

        return self._execution_response(
            operation="RTR_ExecuteAdminCommand",
            result=result,
            classification=classification,
            approval_gate=approval_gate,
            target=target,
            missing_context=self._missing_audit_context(reason, ticket, expected_effect),
            payload=payload,
        )

    def _search_and_get_details(
        self,
        search_operation: str,
        get_operation: str,
        filter: str | None,
        limit: int,
        offset: int | None,
        sort: str | None,
        fql_documentation: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        ids = self._base_search_api_call(
            operation=search_operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message=f"Failed to search RTR Admin resources with {search_operation}",
        )

        if self._is_error(ids):
            return self._format_fql_error_response([ids], filter, fql_documentation)

        if not ids:
            return self._format_fql_error_response([], filter, fql_documentation)

        details = self._base_get_by_ids(
            operation=get_operation,
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def _get_details(
        self,
        operation: str,
        ids: list[str],
    ) -> list[dict[str, Any]] | dict[str, Any]:
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation=operation,
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def _classification(
        self,
        base_command: str,
        category: str,
        risk: str,
        allowed_for_execution: bool,
        explanation: str,
        requires_approval: bool = False,
        can_execute_with_approval: bool = False,
    ) -> dict[str, Any]:
        return {
            "base_command": base_command,
            "category": category,
            "risk": risk,
            "allowed_for_execution": allowed_for_execution,
            "requires_approval": requires_approval,
            "can_execute_with_approval": can_execute_with_approval,
            "explanation": explanation,
            "blocked_reason": None if allowed_for_execution else explanation,
            "requires_explicit_target": allowed_for_execution,
            "safety_disclaimer": RTR_ADMIN_SAFETY_DISCLAIMER,
        }

    def _execute_admin_command_body(
        self,
        base_command: str,
        command_string: str,
        session_id: str | None,
        device_id: str | None,
        command_id: int | None,
        persist: bool,
    ) -> dict[str, Any]:
        return {
            "base_command": base_command,
            "command_string": command_string,
            "device_id": device_id,
            "session_id": session_id,
            "id": command_id,
            "persist": persist,
        }

    def _execution_response(
        self,
        operation: str,
        result: list[dict[str, Any]] | dict[str, Any],
        classification: dict[str, Any],
        approval_gate: dict[str, Any],
        target: dict[str, Any],
        missing_context: list[str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        response: dict[str, Any] = {
            "operation": operation,
            "submitted": not self._is_error(result),
            "result": result,
            "classification": classification,
            "classification_enforced": True,
            "approval_gate": approval_gate | {"approved": True},
            "safety_disclaimer": RTR_ADMIN_SAFETY_DISCLAIMER,
            "command_guidance": self._command_guidance(
                payload.get("body", {}).get("base_command"),
                payload.get("body", {}).get("command_string"),
            ),
            "missing_context": missing_context,
            "target": target,
            "payload": payload,
            "next_step": (
                "Use `falcon_check_rtr_admin_command_status` with the returned "
                "cloud_request_id to retrieve command output."
            ),
        }

        if payload.get("body", {}).get("persist"):
            response["persist_warning"] = (
                "Persisted RTR Admin commands may run when offline hosts return "
                "to service."
            )

        if missing_context:
            response["context_warning"] = (
                "Audit context is incomplete. Consider providing reason, ticket, "
                "and expected_effect before live use."
            )

        return response

    def _enforce_admin_command_policy(
        self,
        classification: dict[str, Any],
        approval_gate: dict[str, Any],
        operator_approval: str | None,
        target: dict[str, Any],
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if classification.get("allowed_for_execution"):
            return None

        if not classification.get("requires_approval"):
            return _format_error_response(
                "RTR Admin command is blocked by local policy. No Falcon call was made.",
                details={
                    "classification": classification,
                    "target": prepare_api_parameters(target),
                    "payload_preview": payload,
                    "approval_gate": approval_gate,
                },
            )

        if operator_approval == approval_gate["approval_phrase"]:
            return None

        return _format_error_response(
            "RTR Admin high-impact approval required before Falcon call. No Falcon call was made.",
            details={
                "classification": classification,
                "target": prepare_api_parameters(target),
                "payload_preview": payload,
                "approval_gate": approval_gate,
            },
        )

    def _approval_gate(
        self,
        operation: str,
        classification: dict[str, Any],
        payload: dict[str, Any],
        target: dict[str, Any],
    ) -> dict[str, Any]:
        if not classification.get("requires_approval"):
            return {
                "approval_required": False,
                "approved_by_default": True,
                "reason": "Command classification does not require high-impact approval.",
            }

        approval_hash = self._approval_hash(
            operation=operation,
            classification=classification,
            payload=payload,
            target=target,
        )
        return {
            "approval_required": True,
            "approved_by_default": False,
            "approval_phrase": f"APPROVE_RTR_ADMIN_{approval_hash}",
            "approval_hash": approval_hash,
            "reason": classification.get("blocked_reason") or classification.get("explanation"),
            "instruction": (
                "Ask the operator to review the exact target, command, expected effect, "
                "and payload hash. Re-submit with operator_approval set to the exact "
                "approval_phrase only after approval."
            ),
        }

    def _approval_hash(
        self,
        operation: str,
        classification: dict[str, Any],
        payload: dict[str, Any],
        target: dict[str, Any],
    ) -> str:
        material = {
            "operation": operation,
            "base_command": classification.get("base_command"),
            "category": classification.get("category"),
            "risk": classification.get("risk"),
            "target": prepare_api_parameters(target),
            "payload": payload,
        }
        serialized = json.dumps(material, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16].upper()

    def _missing_audit_context(
        self,
        reason: str | None,
        ticket: str | None,
        expected_effect: str | None,
    ) -> list[str]:
        required_context = {
            "reason": reason,
            "ticket": ticket,
            "expected_effect": expected_effect,
        }
        return [key for key, value in required_context.items() if not self._has_text(value)]

    def _has_text(self, value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def _command_guidance(
        self,
        base_command: Any,
        command_string: Any,
    ) -> dict[str, Any] | None:
        if not isinstance(base_command, str):
            return None

        if base_command.strip().lower() != "runscript":
            return None

        warnings = [
            "`runscript -Raw` is not an interactive terminal; submit one command and poll status.",
            "Do not place RTR controller commands such as `get`, `put`, or status polling inside raw script bodies.",
            "Use `falcon_check_rtr_admin_command_status` with the returned cloud_request_id.",
        ]

        if isinstance(command_string, str) and "-raw" in command_string.lower():
            warnings.append(
                "Raw script bodies are quoting-sensitive; avoid unescaped triple backticks."
            )

        return {
            "resource": "falcon://rtr-admin/commands/runscript-guide",
            "shape": "runscript -Raw=```<target-side script>```",
            "cloud_file_shape": 'runscript -CloudFile="ScriptName" -CommandLine="<arguments>"',
            "warnings": warnings,
        }
