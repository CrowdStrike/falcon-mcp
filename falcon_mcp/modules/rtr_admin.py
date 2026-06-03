"""
Real Time Response Admin module for Falcon MCP Server.

This module exposes RTR Admin inventory, command status, command preview, and
admin command execution helpers. It does not manage script / put-file uploads,
updates, or deletes.
"""

import hashlib
import json
import time
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters, unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr_admin import (
    RTR_ADMIN_APPROVAL_PACKET_TEMPLATE,
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
    "csrutil",
    "env",
    "eventlog",
    "filehash",
    "getsid",
    "help",
    "history",
    "ifconfig",
    "ipconfig",
    "ls",
    "mount",
    "netstat",
    "ps",
    "pwd",
    "users",
}

EVIDENCE_COLLECTION_COMMANDS = {"get"}
SENSITIVE_COLLECTION_COMMANDS = {"memdump", "xmemdump"}
BLOCKED_ADMIN_COMMANDS = {
    "cp",
    "cswindiag",
    "encrypt",
    "falconscript",
    "kill",
    "map",
    "mkdir",
    "mv",
    "put",
    "put-and-run",
    "restart",
    "rm",
    "rmdir",
    "run",
    "shutdown",
    "tar",
    "umount",
    "unmount",
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


class RTRAdminModule(BaseModule):
    """Module for RTR Admin inventory and pre-execution safety checks."""

    MODULE_NAME = "rtr_admin"

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_rtr_admin_scripts,
            name="search_rtr_admin_scripts",
        )
        self._add_tool(
            server=server,
            method=self.search_rtr_falcon_scripts,
            name="search_rtr_falcon_scripts",
        )
        self._add_tool(
            server=server,
            method=self.search_rtr_put_files,
            name="search_rtr_put_files",
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_put_file_contents,
            name="get_rtr_put_file_contents",
        )
        self._add_tool(
            server=server,
            method=self.check_rtr_admin_command_status,
            name="check_rtr_admin_command_status",
        )
        self._add_tool(
            server=server,
            method=self.classify_rtr_admin_command,
            name="classify_rtr_admin_command",
        )
        self._add_tool(
            server=server,
            method=self.preview_rtr_admin_command,
            name="preview_rtr_admin_command",
        )
        self._add_tool(
            server=server,
            method=self.execute_rtr_admin_command,
            name="execute_rtr_admin_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.run_rtr_admin_command_and_wait,
            name="run_rtr_admin_command_and_wait",
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
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/policy/command-guide"),
                name="falcon_rtr_admin_command_policy_guide",
                description="Contains RTR Admin command classification policy and command categories.",
                text=self._command_policy_guide(),
            ),
            TextResource(
                uri=AnyUrl("falcon://rtr-admin/approval/packet-guide"),
                name="falcon_rtr_admin_approval_packet_template",
                description="Contains the approval packet template for high-impact RTR Admin commands.",
                text=RTR_ADMIN_APPROVAL_PACKET_TEMPLATE,
            ),
        ]

        for resource in resources:
            self._add_resource(server, resource)

    def register_prompts(self, server: FastMCP) -> None:
        """Register prompts with the MCP server."""
        self._add_prompt(
            server=server,
            method=self.plan_rtr_admin_action,
            name="plan_rtr_admin_action",
            title="Plan RTR Admin Action",
            description="Plan a safe RTR Admin workflow before using execution tools.",
        )
        self._add_prompt(
            server=server,
            method=self.build_rtr_admin_approval_packet,
            name="build_rtr_admin_approval_packet",
            title="Build RTR Admin Approval Packet",
            description="Create an operator approval packet for a high-impact RTR Admin command.",
        )
        self._add_prompt(
            server=server,
            method=self.review_rtr_admin_runscript,
            name="review_rtr_admin_runscript",
            title="Review RTR Admin Runscript",
            description="Review an RTR Admin runscript command string for safety and quoting risks.",
        )
        self._add_prompt(
            server=server,
            method=self.interpret_rtr_admin_status,
            name="interpret_rtr_admin_status",
            title="Interpret RTR Admin Status",
            description="Interpret RTR Admin command status output and suggest next safe steps.",
        )

    def plan_rtr_admin_action(
        self,
        objective: str = Field(description="Operator objective for the RTR Admin workflow."),
        target_hostname: str | None = Field(
            default=None,
            description="Optional hostname under review.",
        ),
        session_id: str | None = Field(
            default=None,
            description="Optional RTR session ID if one is already known.",
        ),
        device_id: str | None = Field(
            default=None,
            description="Optional Falcon device AID if one is already known.",
        ),
        ticket: str | None = Field(
            default=None,
            description="Optional ticket, case, or incident identifier.",
        ),
    ) -> str:
        """Plan a safe RTR Admin action before calling execution tools."""
        return "\n".join(
            [
                "Plan an RTR Admin action using the existing RTR Admin MCP surface.",
                "",
                "Context:",
                *self._prompt_context_lines(
                    objective=objective,
                    target_hostname=target_hostname,
                    session_id=session_id,
                    device_id=device_id,
                    ticket=ticket,
                ),
                "",
                "Workflow:",
                "1. Use inventory/search tools only if reusable scripts or put-files need review.",
                "   Use `falcon_get_rtr_put_file_contents` only after selecting a specific put-file ID.",
                "2. Use `falcon_classify_rtr_admin_command` before any execution planning.",
                "3. Use `falcon_preview_rtr_admin_command` to inspect payload, target, policy, and approval gate.",
                "4. For high-impact commands, build an approval packet and wait for explicit operator approval.",
                "5. Use `falcon_run_rtr_admin_command_and_wait` for focused single-host commands when direct output is needed.",
                "6. Use `falcon_execute_rtr_admin_command` plus `falcon_check_rtr_admin_command_status` when manual polling is better.",
                "",
                "Do not invent new tools, bypass the approval phrase, or place RTR controller actions inside raw scripts.",
            ]
        )

    def build_rtr_admin_approval_packet(
        self,
        base_command: str = Field(description="RTR Admin base command under review."),
        command_string: str = Field(description="Exact RTR Admin command string under review."),
        session_id: str = Field(description="RTR session ID that would receive the command."),
        device_id: str | None = Field(default=None, description="Optional Falcon device AID."),
        target_hostname: str | None = Field(default=None, description="Optional hostname."),
        reason: str | None = Field(default=None, description="Reason for considering the command."),
        ticket: str | None = Field(default=None, description="Ticket, case, or incident identifier."),
        expected_effect: str | None = Field(
            default=None,
            description="Expected endpoint effect if the command is executed.",
        ),
        persist: bool = Field(default=False, description="Whether the command would persist offline."),
    ) -> str:
        """Create an approval-packet prompt for a high-impact RTR Admin command."""
        return "\n".join(
            [
                "Build an RTR Admin approval packet for operator review.",
                "",
                "Command under review:",
                f"- base_command: {base_command}",
                f"- command_string: {command_string}",
                f"- persist: {bool(persist)}",
                "",
                "Target:",
                *self._prompt_context_lines(
                    target_hostname=target_hostname,
                    session_id=session_id,
                    device_id=device_id,
                    ticket=ticket,
                    reason=reason,
                    expected_effect=expected_effect,
                ),
                "",
                "Required steps:",
                "1. Confirm `base_command` matches the first token of `command_string`.",
                "2. Use `falcon_classify_rtr_admin_command` to get category, risk, and approval requirements.",
                "3. Use `falcon_preview_rtr_admin_command` with reason, ticket, and expected_effect.",
                "4. Copy the preview `approval_gate.approval_phrase` only after operator approval.",
                "5. Execute once with `falcon_run_rtr_admin_command_and_wait`, or use `falcon_execute_rtr_admin_command` then poll status.",
                "",
                "Approval template resource: falcon://rtr-admin/approval/packet-guide",
            ]
        )

    def review_rtr_admin_runscript(
        self,
        command_string: str = Field(description="RTR Admin runscript command string to review."),
        target_platform: str | None = Field(
            default=None,
            description="Optional target platform such as windows, linux, or mac.",
        ),
        objective: str | None = Field(
            default=None,
            description="Optional operator objective for the script.",
        ),
    ) -> str:
        """Review a runscript command string for safety and quoting risks."""
        return "\n".join(
            [
                "Review this RTR Admin runscript command before preview or execution.",
                "",
                f"- command_string: {command_string}",
                f"- target_platform: {target_platform or 'not provided'}",
                f"- objective: {objective or 'not provided'}",
                "",
                "Checklist:",
                "1. Confirm the command starts with `runscript` and uses the intended `-Raw` or `-CloudFile` shape.",
                "2. Do not include RTR controller commands such as `get`, `put`, `cd`, or status polling inside raw script bodies.",
                "3. Check quoting around triple backticks, shell quotes, and command-line arguments.",
                "4. Prefer approved cloud scripts for reusable or multiline logic.",
                "5. Use `falcon_preview_rtr_admin_command` before execution and require high-impact approval.",
                "6. Prefer `falcon_run_rtr_admin_command_and_wait` only for focused commands where immediate output is needed.",
                "",
                "Reference resource: falcon://rtr-admin/commands/runscript-guide",
            ]
        )

    def interpret_rtr_admin_status(
        self,
        command_status: str = Field(
            description="RTR Admin command status result or summarized stdout/stderr to interpret.",
        ),
        base_command: str | None = Field(default=None, description="Optional base command."),
        expected_effect: str | None = Field(
            default=None,
            description="Optional expected endpoint effect that was approved.",
        ),
    ) -> str:
        """Interpret RTR Admin status output and suggest next safe steps."""
        return "\n".join(
            [
                "Interpret RTR Admin command status output.",
                "",
                f"- base_command: {base_command or 'not provided'}",
                f"- expected_effect: {expected_effect or 'not provided'}",
                "",
                "Status material:",
                command_status,
                "",
                "Return:",
                "1. Completion state and whether more `falcon_check_rtr_admin_command_status` polling is needed.",
                "2. stdout/stderr findings tied to the approved command and expected effect.",
                "3. Any evidence gaps or follow-up read-only checks.",
                "4. Any warning that the output suggests unexpected endpoint impact.",
                "",
                "Do not suggest a second high-impact action without a fresh preview and approval packet.",
            ]
        )

    def search_rtr_admin_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://rtr-admin/scripts/search/fql-guide` for syntax.",
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
            description="Sort custom scripts by a supported field such as `created_timestamp|desc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR custom scripts and return full metadata records.

        Use this to find reusable custom RTR scripts by name, platform, or
        permission type. Consult falcon://rtr-admin/scripts/search/fql-guide
        before constructing filter expressions. Returns full script records,
        including script content; treat the response as sensitive operational
        material.
        """
        filter = unwrap_field_default(filter)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)
        sort = unwrap_field_default(sort)

        ids = self._base_search_api_call(
            operation="RTR_ListScripts",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR Admin scripts",
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="RTR_GetScriptsV2",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return self._order_details_by_ids(ids, details)

    def search_rtr_falcon_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://rtr-admin/falcon-scripts/search/fql-guide` for syntax.",
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

        Use this to find CrowdStrike-provided RTR scripts by name or platform,
        or to look up known script IDs with an `id` filter. Consult
        falcon://rtr-admin/falcon-scripts/search/fql-guide before constructing
        filter expressions. Returns full script records; treat any returned
        script content as sensitive operational material.
        """
        filter = unwrap_field_default(filter)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)
        sort = unwrap_field_default(sort)

        ids = self._base_search_api_call(
            operation="RTR_ListFalconScripts",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR Falcon scripts",
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="RTR_GetFalconScripts",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return self._order_details_by_ids(ids, details)

    def search_rtr_put_files(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://rtr-admin/put-files/search/fql-guide` for syntax.",
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
            description="Sort put-files by a supported field such as `created_timestamp|desc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR put-files and return full metadata records.

        Use this to review put-file inventory before considering an admin
        command that references staged content. Consult
        falcon://rtr-admin/put-files/search/fql-guide before constructing
        filter expressions. Returns full put-file metadata records.
        """
        filter = unwrap_field_default(filter)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)
        sort = unwrap_field_default(sort)

        ids = self._base_search_api_call(
            operation="RTR_ListPut_Files",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR put-files",
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="RTR_GetPut_FilesV2",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return self._order_details_by_ids(ids, details)

    def get_rtr_put_file_contents(
        self,
        file_id: str = Field(
            description="RTR put-file ID whose stored contents should be retrieved.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve the stored contents of one RTR put-file by ID.

        Use this only after selecting a specific put-file from
        falcon_search_rtr_put_files. This is a read-only Falcon call, but the
        returned content can be sensitive because put-files may contain scripts,
        binaries, or operational payloads staged for RTR `put` workflows.
        Text content is returned for model review; binary content returns size
        metadata and a safe error instead of raw bytes. Treat retrieval results
        as sensitive regardless of inventory `file_type`; binary-tagged
        inventory can still retrieve text content.
        """
        file_id = unwrap_field_default(file_id)

        if not isinstance(file_id, str) or not file_id.strip():
            return _format_error_response(
                "file_id is required to retrieve RTR put-file contents. "
                "No Falcon call was made."
            )

        prepared_params = prepare_api_parameters({"id": file_id})
        response = self.client.command(
            "RTR_GetPutFileContents",
            parameters=prepared_params,
        )

        if isinstance(response, bytes):
            try:
                return {
                    "id": file_id,
                    "content": response.decode("utf-8"),
                    "content_format": "text",
                    "sensitivity_warning": self._put_file_content_warning(),
                }
            except UnicodeDecodeError:
                return {
                    "error": (
                        "RTR put-file content is binary and cannot be returned "
                        "as safe text for model consumption."
                    ),
                    "id": file_id,
                    "content_format": "binary",
                    "size_bytes": len(response),
                }

        if isinstance(response, dict):
            status_code = response.get("status_code")
            if status_code is None or status_code >= 300:
                return handle_api_response(
                    response,
                    operation="RTR_GetPutFileContents",
                    error_message="Failed to retrieve RTR put-file contents",
                    default_result=[],
                )

            body = response.get("body", {})
            if isinstance(body, dict) and "resources" in body:
                resources = body.get("resources", [])
                if isinstance(resources, list):
                    return [
                        self._annotate_put_file_content(resource)
                        if isinstance(resource, dict)
                        else resource
                        for resource in resources
                    ]
                return resources
            if body:
                return self._annotate_put_file_content({"id": file_id, "body": body})
            return []

        return {"error": f"Unexpected response type: {type(response).__name__}"}

    def check_rtr_admin_command_status(
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

        Use this to poll for command completion after execution. This is a
        read-only status lookup that cannot start a new command. Returns
        completion status, stdout, stderr, and sequence information.
        """
        cloud_request_id = unwrap_field_default(cloud_request_id)
        sequence_id = unwrap_field_default(sequence_id)

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

    def classify_rtr_admin_command(
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
        Returns category, risk level, approval requirements, and explanation.
        """
        base_command = unwrap_field_default(base_command)
        command_string = unwrap_field_default(command_string)

        if not isinstance(base_command, str) or not base_command.strip():
            return _format_error_response(
                "base_command is required. Provide an RTR Admin base command such "
                "as `ps`, `get`, `reg`, `runscript`, or `rm`. No Falcon call was made."
            )

        normalized = base_command.strip().lower()
        command_text = command_string.strip() if isinstance(command_string, str) else ""
        command_lower = command_text.lower()
        command_base = command_lower.split(maxsplit=1)[0] if command_lower else None
        command_warnings = self._command_shape_warnings(normalized, command_text)

        if command_base and command_base != normalized:
            return _format_error_response(
                "base_command must match the first token of command_string. "
                "No Falcon call was made.",
                details={
                    "base_command": normalized,
                    "command_string_base": command_base,
                },
            )

        if normalized in READ_ONLY_ADMIN_COMMANDS:
            return self._classification(
                normalized,
                "read_only",
                "low",
                True,
                "Command is normally read-only in RTR Admin.",
                command_warnings=command_warnings,
            )

        if normalized == "reg":
            if command_lower.split()[:2] == ["reg", "query"]:
                return self._classification(
                    normalized,
                    "read_only",
                    "low",
                    True,
                    "`reg query` is read-only; other registry subcommands are blocked.",
                    command_warnings=command_warnings,
                )
            return self._classification(
                normalized,
                "high_impact",
                "critical",
                False,
                "Registry writes, loads, unloads, and deletes require explicit operator approval.",
                requires_approval=True,
                can_execute_with_approval=True,
                command_warnings=command_warnings,
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
                command_warnings=command_warnings,
            )

        if normalized in EVIDENCE_COLLECTION_COMMANDS:
            return self._classification(
                normalized,
                "evidence_collection",
                "high",
                False,
                "File exfiltration command requires explicit operator approval before execution.",
                requires_approval=True,
                can_execute_with_approval=True,
                command_warnings=command_warnings,
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
                command_warnings=command_warnings,
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
                command_warnings=command_warnings,
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
            command_warnings=command_warnings,
        )

    def preview_rtr_admin_command(
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
        session_id = unwrap_field_default(session_id)
        device_id = unwrap_field_default(device_id)
        base_command = unwrap_field_default(base_command)
        command_string = unwrap_field_default(command_string)
        command_id = unwrap_field_default(command_id)
        target_hostname = unwrap_field_default(target_hostname)
        reason = unwrap_field_default(reason)
        ticket = unwrap_field_default(ticket)
        expected_effect = unwrap_field_default(expected_effect)
        persist = unwrap_field_default(persist)

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

        classification = self.classify_rtr_admin_command(base_command, command_string)
        if self._is_error(classification):
            return classification

        audit_context = self._audit_context(reason, ticket, expected_effect)
        missing_context = self._missing_audit_context(reason, ticket, expected_effect)

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
            audit_context=audit_context,
        )

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
            "required_context": list(audit_context.keys()),
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

    def execute_rtr_admin_command(
        self,
        base_command: str = Field(description="RTR Admin base command to execute."),
        command_string: str = Field(description="Full RTR Admin command string to execute."),
        session_id: str = Field(
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

        Use after previewing and classifying the command. High-impact commands
        are blocked unless the exact operator approval phrase is supplied.
        Returns submission status, cloud_request_id for polling, and
        classification enforcement details.
        """
        base_command = unwrap_field_default(base_command)
        command_string = unwrap_field_default(command_string)
        session_id = unwrap_field_default(session_id)
        device_id = unwrap_field_default(device_id)
        command_id = unwrap_field_default(command_id)
        persist = unwrap_field_default(persist)
        target_hostname = unwrap_field_default(target_hostname)
        reason = unwrap_field_default(reason)
        ticket = unwrap_field_default(ticket)
        expected_effect = unwrap_field_default(expected_effect)
        operator_approval = unwrap_field_default(operator_approval)

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

        classification = self.classify_rtr_admin_command(base_command, command_string)
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
        audit_context = self._audit_context(reason, ticket, expected_effect)
        missing_context = self._missing_audit_context(reason, ticket, expected_effect)
        approval_gate = self._approval_gate(
            operation="RTR_ExecuteAdminCommand",
            classification=classification,
            payload=payload,
            target=target,
            audit_context=audit_context,
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
            missing_context=missing_context,
            payload=payload,
        )

    def run_rtr_admin_command_and_wait(
        self,
        base_command: str = Field(description="RTR Admin base command to execute."),
        command_string: str = Field(description="Full RTR Admin command string to execute."),
        session_id: str = Field(
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
        timeout_seconds: int = Field(
            default=60,
            ge=1,
            le=600,
            description="Maximum time to wait for command completion. Max: 600 seconds.",
        ),
        poll_interval_seconds: float = Field(
            default=2.0,
            ge=0.5,
            le=30.0,
            description="Seconds to wait between admin command status checks.",
        ),
    ) -> dict[str, Any]:
        """Execute an RTR Admin command and poll until completion or timeout.

        This is a convenience workflow for single-host admin commands. It uses
        the same local classification and approval gate as
        falcon_execute_rtr_admin_command, then polls
        falcon_check_rtr_admin_command_status with the returned cloud_request_id.
        """
        timeout_seconds = unwrap_field_default(timeout_seconds)
        poll_interval_seconds = unwrap_field_default(poll_interval_seconds)

        execute_response = self.execute_rtr_admin_command(
            base_command=base_command,
            command_string=command_string,
            session_id=session_id,
            device_id=device_id,
            command_id=command_id,
            persist=persist,
            target_hostname=target_hostname,
            reason=reason,
            ticket=ticket,
            expected_effect=expected_effect,
            operator_approval=operator_approval,
        )

        if self._is_error(execute_response):
            execute_response["phase"] = "execute"
            return execute_response

        if not execute_response.get("submitted"):
            execute_response["phase"] = "execute"
            return execute_response

        execute_result = execute_response.get("result")
        if not isinstance(execute_result, list) or not execute_result:
            return {
                "error": "RTR Admin command execution did not return a command request.",
                "phase": "execute",
                "execution_response": execute_response,
            }

        command_request = execute_result[0]
        if not isinstance(command_request, dict):
            return {
                "error": "RTR Admin command execution returned an unexpected response shape.",
                "phase": "execute",
                "execution_response": execute_response,
            }

        cloud_request_id = command_request.get("cloud_request_id")
        if not cloud_request_id:
            return {
                "error": "RTR Admin command execution did not return a cloud_request_id.",
                "phase": "execute",
                "execution_response": execute_response,
            }

        deadline = time.monotonic() + timeout_seconds
        status_chunks: list[dict[str, Any]] = []
        sequence_id = 0

        while True:
            status_result = self._base_query_api_call(
                operation="RTR_CheckAdminCommandStatus",
                query_params={
                    "cloud_request_id": cloud_request_id,
                    "sequence_id": sequence_id,
                },
                error_message="Failed to check RTR Admin command status",
            )

            if self._is_error(status_result):
                status_result["phase"] = "status"
                status_result["cloud_request_id"] = cloud_request_id
                status_result["execution_response"] = execute_response
                return status_result

            if isinstance(status_result, list):
                status_chunks.extend(
                    chunk for chunk in status_result if isinstance(chunk, dict)
                )

            complete = any(chunk.get("complete") is True for chunk in status_chunks)
            if complete:
                return self._format_admin_wait_result(
                    cloud_request_id=cloud_request_id,
                    command_request=command_request,
                    execute_response=execute_response,
                    status_chunks=status_chunks,
                    complete=True,
                    timed_out=False,
                )

            if time.monotonic() >= deadline:
                return self._format_admin_wait_result(
                    cloud_request_id=cloud_request_id,
                    command_request=command_request,
                    execute_response=execute_response,
                    status_chunks=status_chunks,
                    complete=False,
                    timed_out=True,
                )

            if status_chunks:
                sequence_id = status_chunks[-1].get("sequence_id", sequence_id)
            time.sleep(poll_interval_seconds)

    def _prompt_context_lines(self, **values: Any) -> list[str]:
        lines = []
        for key, value in values.items():
            if isinstance(value, str) and value.strip():
                lines.append(f"- {key}: {value.strip()}")
            elif value is not None and not isinstance(value, str):
                lines.append(f"- {key}: {value}")
            else:
                lines.append(f"- {key}: not provided")
        return lines

    def _command_policy_guide(self) -> str:
        return "\n".join(
            [
                "RTR Admin Command Policy Guide",
                "",
                "This resource summarizes local RTR Admin command classification.",
                "The execution tool enforces this policy before any Falcon call.",
                "",
                f"Read-only commands: {', '.join(sorted(READ_ONLY_ADMIN_COMMANDS))}",
                f"Evidence collection commands: {', '.join(sorted(EVIDENCE_COLLECTION_COMMANDS))}",
                f"Sensitive collection commands: {', '.join(sorted(SENSITIVE_COLLECTION_COMMANDS))}",
                f"High-impact commands: {', '.join(sorted(BLOCKED_ADMIN_COMMANDS))}",
                f"Read-only update subcommands: {', '.join(sorted(READ_ONLY_UPDATE_SUBCOMMANDS))}",
                "",
                "`reg query` is read-only; other registry subcommands require approval.",
                "`reg query` accepts only a small argument shape in Falcon RTR; keep key/value arguments minimal and preview warnings before live use.",
                "Use `rm <directory> -force` for directory cleanup and verify stderr/stdout before assuming deletion succeeded.",
                "`runscript` is always high impact and requires approval.",
                "Unknown commands are blocked until reviewed and explicitly allowlisted.",
                "For execution, `base_command` must match the first token of `command_string`.",
            ]
        )

    def _classification(
        self,
        base_command: str,
        category: str,
        risk: str,
        allowed_for_execution: bool,
        explanation: str,
        requires_approval: bool = False,
        can_execute_with_approval: bool = False,
        command_warnings: list[str] | None = None,
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
            "requires_explicit_target": allowed_for_execution or can_execute_with_approval,
            "safety_disclaimer": RTR_ADMIN_SAFETY_DISCLAIMER,
            "command_warnings": command_warnings or [],
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

    def _format_admin_wait_result(
        self,
        cloud_request_id: str,
        command_request: dict[str, Any],
        execute_response: dict[str, Any],
        status_chunks: list[dict[str, Any]],
        complete: bool,
        timed_out: bool,
    ) -> dict[str, Any]:
        """Format admin command-and-wait output for model-friendly consumption."""
        stdout = "".join(
            str(chunk.get("stdout", "")) for chunk in status_chunks if chunk.get("stdout")
        )
        stderr = "".join(
            str(chunk.get("stderr", "")) for chunk in status_chunks if chunk.get("stderr")
        )

        result: dict[str, Any] = {
            "cloud_request_id": cloud_request_id,
            "complete": complete,
            "timed_out": timed_out,
            "execution": command_request,
            "execution_response": execute_response,
            "status": status_chunks,
            "stdout": stdout,
            "stderr": stderr,
            "classification": execute_response.get("classification"),
            "approval_gate": execute_response.get("approval_gate"),
            "safety_disclaimer": RTR_ADMIN_SAFETY_DISCLAIMER,
        }

        if timed_out:
            result["warning"] = "Timed out waiting for RTR Admin command completion."

        if execute_response.get("context_warning"):
            result["context_warning"] = execute_response["context_warning"]
        if execute_response.get("missing_context"):
            result["missing_context"] = execute_response["missing_context"]

        return result

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

        if not approval_gate.get("approval_ready", True):
            return _format_error_response(
                "RTR Admin approval context is incomplete. No Falcon call was made.",
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
        audit_context: dict[str, Any],
    ) -> dict[str, Any]:
        if not classification.get("requires_approval"):
            return {
                "approval_required": False,
                "approved_by_default": True,
                "reason": "Command classification does not require high-impact approval.",
            }

        missing_approval_context = self._missing_approval_context(
            audit_context=audit_context,
            target=target,
        )
        if missing_approval_context:
            return {
                "approval_required": True,
                "approved_by_default": False,
                "approval_ready": False,
                "missing_approval_context": missing_approval_context,
                "reason": classification.get("blocked_reason") or classification.get("explanation"),
                "instruction": (
                    "Provide device_id, reason, ticket, and expected_effect before "
                    "requesting high-impact approval. No approval phrase is issued "
                    "until the approval packet can bind target, payload, and audit context."
                ),
            }

        approval_hash = self._approval_hash(
            operation=operation,
            classification=classification,
            payload=payload,
            target=target,
            audit_context=audit_context,
        )
        return {
            "approval_required": True,
            "approved_by_default": False,
            "approval_ready": True,
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
        audit_context: dict[str, Any],
    ) -> str:
        hash_target = {
            k: v for k, v in target.items() if k in ("session_id", "device_id")
        }
        material = {
            "operation": operation,
            "base_command": classification.get("base_command"),
            "category": classification.get("category"),
            "risk": classification.get("risk"),
            "target": prepare_api_parameters(hash_target),
            "audit_context": prepare_api_parameters(audit_context),
            "payload": payload,
        }
        serialized = json.dumps(material, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16].upper()

    def _audit_context(
        self,
        reason: str | None,
        ticket: str | None,
        expected_effect: str | None,
    ) -> dict[str, Any]:
        return {
            "reason": reason.strip() if isinstance(reason, str) else reason,
            "ticket": ticket.strip() if isinstance(ticket, str) else ticket,
            "expected_effect": (
                expected_effect.strip()
                if isinstance(expected_effect, str)
                else expected_effect
            ),
        }

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

    def _missing_approval_context(
        self,
        audit_context: dict[str, Any],
        target: dict[str, Any],
    ) -> list[str]:
        missing = [
            key for key, value in audit_context.items() if not self._has_text(value)
        ]
        if not self._has_text(target.get("device_id")):
            missing.append("device_id")
        return missing

    def _put_file_content_warning(self) -> str:
        return (
            "RTR put-file content retrieval is sensitive regardless of inventory "
            "file_type. Put-file metadata can say binary while retrieval returns "
            "text content."
        )

    def _annotate_put_file_content(self, item: dict[str, Any]) -> dict[str, Any]:
        content_format = item.get("content_format")
        has_text_content = "content" in item or (
            isinstance(item.get("body"), dict) and "content" in item["body"]
        )
        if content_format == "binary":
            return item
        if has_text_content:
            return item | {"sensitivity_warning": self._put_file_content_warning()}
        return item

    def _order_details_by_ids(
        self,
        ids: list[str],
        details: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Preserve query/list result order after Falcon detail lookups."""
        order = {entity_id: index for index, entity_id in enumerate(ids)}
        return sorted(
            details,
            key=lambda item: order.get(str(item.get("id")), len(order)),
        )

    def _command_shape_warnings(
        self,
        base_command: str,
        command_string: str,
    ) -> list[str]:
        if base_command != "reg":
            return []

        tokens = command_string.split()
        if len(tokens) > 3 and [token.lower() for token in tokens[:2]] == ["reg", "query"]:
            return [
                "`reg query` can return Falcon HTTP 400 when more than two "
                "arguments follow `reg`. Keep the query shape to "
                "`reg query <key>` or quote paths with spaces before live use."
            ]
        return []

    def _command_guidance(
        self,
        base_command: Any,
        command_string: Any,
    ) -> dict[str, Any] | None:
        if not isinstance(base_command, str):
            return None

        normalized = base_command.strip().lower()
        shape_warnings = self._command_shape_warnings(
            normalized,
            command_string if isinstance(command_string, str) else "",
        )

        if normalized == "reg" and shape_warnings:
            return {
                "warnings": shape_warnings,
            }

        if normalized != "runscript":
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
        warnings.extend(shape_warnings)

        return {
            "resource": "falcon://rtr-admin/commands/runscript-guide",
            "shape": "runscript -Raw=```<target-side script>```",
            "cloud_file_shape": 'runscript -CloudFile="ScriptName" -CommandLine="<arguments>"',
            "warnings": warnings,
        }
