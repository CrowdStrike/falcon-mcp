"""
Real Time Response module for Falcon MCP Server.

This module provides tools for initiating and inspecting RTR sessions and for
executing read-only RTR commands during host investigations.
"""

import time
from textwrap import dedent
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr import (
    AGGREGATE_RTR_SESSIONS_GUIDE,
    AUDIT_RTR_SESSIONS_EMBEDDED_FQL_SYNTAX,
    EMBEDDED_FQL_SYNTAX,
    READ_ONLY_RTR_INVESTIGATION_GUIDE,
    SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION,
    SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class RTRModule(BaseModule):
    """Module for Real Time Response hunt and triage workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_sessions,
            name="search_rtr_sessions",
        )

        self._add_tool(
            server=server,
            method=self.search_audit_sessions,
            name="search_rtr_audit_sessions",
        )

        self._add_tool(
            server=server,
            method=self.aggregate_sessions,
            name="aggregate_rtr_sessions",
        )

        self._add_tool(
            server=server,
            method=self.get_session_details,
            name="get_rtr_session_details",
        )

        self._add_tool(
            server=server,
            method=self.init_session,
            name="init_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.pulse_session,
            name="pulse_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.execute_read_only_command,
            name="execute_rtr_read_only_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.run_read_only_command_and_wait,
            name="run_rtr_read_only_command_and_wait",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.check_command_status,
            name="check_rtr_command_status",
        )

        self._add_tool(
            server=server,
            method=self.list_session_files,
            name="list_rtr_session_files",
        )

        self._add_tool(
            server=server,
            method=self.delete_session,
            name="delete_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_rtr_sessions_fql_resource = TextResource(
            uri=AnyUrl("falcon://rtr/sessions/search/fql-guide"),
            name="falcon_search_rtr_sessions_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool.",
            text=SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_rtr_sessions_fql_resource,
        )

        search_rtr_audit_sessions_fql_resource = TextResource(
            uri=AnyUrl("falcon://rtr/audit/sessions/search/fql-guide"),
            name="falcon_search_rtr_audit_sessions_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_rtr_audit_sessions` tool.",
            text=SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_rtr_audit_sessions_fql_resource,
        )

        aggregate_rtr_sessions_resource = TextResource(
            uri=AnyUrl("falcon://rtr/sessions/aggregate-guide"),
            name="falcon_aggregate_rtr_sessions_guide",
            description="Explains how to summarize RTR session activity with the `falcon_aggregate_rtr_sessions` tool.",
            text=AGGREGATE_RTR_SESSIONS_GUIDE,
        )

        self._add_resource(
            server,
            aggregate_rtr_sessions_resource,
        )

        read_only_rtr_investigation_resource = TextResource(
            uri=AnyUrl("falcon://rtr/workflows/investigation-guide"),
            name="falcon_rtr_read_only_investigation_guide",
            description="Provides a safe read-only RTR workflow for endpoint investigation tools.",
            text=READ_ONLY_RTR_INVESTIGATION_GUIDE,
        )

        self._add_resource(
            server,
            read_only_rtr_investigation_resource,
        )

    def search_sessions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://rtr/sessions/search/fql-guide` for syntax.",
            examples=["hostname:'BRR-WB-LIB-22'", "aid:'2c5c4e7738...'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of RTR session IDs to return. Max: 5000.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR sessions by a supported session property such as:
                `created_at.asc`, `updated_at.desc`, or `hostname.asc`.
            """).strip(),
            examples=["created_at.desc", "hostname.asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR sessions and return full session details.

        Use this to find sessions by hostname, agent ID, user, or creation time. Consult
        falcon://rtr/sessions/search/fql-guide before constructing filter expressions.
        Returns session metadata including host info, commands executed, and status.
        """
        session_ids = self._base_search_api_call(
            operation="RTR_ListAllSessions",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR sessions",
        )

        if self._is_error(session_ids):
            return self._format_fql_error_response(
                [session_ids], filter, SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION
            )

        if not session_ids:
            return self._format_empty_response(filter)

        details = self._base_get_by_ids(
            operation="RTR_ListSessions",
            ids=session_ids,
            id_key="ids",
            use_params=False,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_audit_sessions(
        self,
        filter: str | None = Field(
            default=None,
            description=AUDIT_RTR_SESSIONS_EMBEDDED_FQL_SYNTAX,
            examples=["created_at:>'now-7d'", "hostname:'BRR-WB-LIB-22'+created_at:>'now-7d'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum number of RTR audit session records to return. Max: 1000.",
        ),
        offset: int | None = Field(
            default=None,
            ge=0,
            description="Starting index of the audit result set.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR audit sessions by a supported audit property using pipe syntax:
                `created_at|desc`, `updated_at|asc`, or `deleted_at|desc`.
            """).strip(),
            examples=["created_at|desc", "updated_at|asc"],
        ),
        with_command_info: bool = Field(
            default=False,
            description="Include command IDs and command log fields in the audit response.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR audit sessions for accountability and timeline evidence.

        Use this when you need to understand who used RTR, when they used it,
        which host was targeted, or which command activity Falcon recorded.
        This is read-only audit visibility; it does not open sessions or run
        commands. Consult falcon://rtr/audit/sessions/search/fql-guide before
        constructing filter expressions.
        """
        audit_sessions = self._base_search_api_call(
            operation="RTRAuditSessions",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "with_command_info": with_command_info,
            },
            error_message="Failed to search RTR audit sessions",
        )

        if self._is_error(audit_sessions):
            return self._format_fql_error_response(
                [audit_sessions], filter, SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION
            )

        if not audit_sessions:
            return self._format_empty_response(filter)

        return audit_sessions

    def aggregate_sessions(
        self,
        field: str = Field(
            description="RTR session field to aggregate, such as `hostname`, `user_id`, `origin`, `base_command`, or `created_at`.",
            examples=["base_command", "hostname", "user_id", "created_at"],
        ),
        aggregate_type: Literal["terms", "date_range"] = Field(
            default="terms",
            description="Aggregation type to run. Use `terms` for top values and `date_range` for time buckets.",
        ),
        name: str = Field(
            default="rtr_session_aggregation",
            description="Friendly name for the aggregation returned by Falcon.",
        ),
        filter: str | None = Field(
            default=None,
            description=EMBEDDED_FQL_SYNTAX,
            examples=["created_at:>'now-7d'", "hostname:'DC*'"],
        ),
        size: int | None = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum buckets to return for terms aggregations.",
        ),
        interval: str | None = Field(
            default=None,
            description="Optional interval for date range aggregations, such as `day` or `hour`.",
            examples=["day", "hour"],
        ),
        date_ranges: list[dict[str, str]] | None = Field(
            default=None,
            description="Date ranges for date_range aggregations, for example `[{'from': 'now-7d', 'to': 'now'}]`.",
            examples=[[{"from": "now-7d", "to": "now"}]],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Summarize RTR session activity with Falcon aggregation buckets.

        Use this before detailed searches when the user asks which hosts,
        users, origins, commands, or time windows account for RTR activity.
        This is read-only summary visibility; it does not open sessions, run
        commands, or return every session record.
        """
        operation = "RTR_AggregateSessions"
        body_params = {
            "date_ranges": date_ranges,
            "field": field,
            "filter": filter,
            "interval": interval,
            "name": name,
            "size": size,
            "type": aggregate_type,
        }
        prepared_body = prepare_api_parameters(body_params)

        logger.debug("Executing %s with body: %s", operation, prepared_body)
        response = self.client.command(operation, body=[prepared_body])

        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to aggregate RTR sessions",
            default_result=[],
        )

    def get_session_details(
        self,
        ids: list[str] = Field(
            description="RTR session IDs to retrieve details for.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve detailed metadata for one or more RTR sessions.

        Use when you already have session IDs from search results. For discovering
        sessions by criteria, use falcon_search_rtr_sessions instead. Returns full
        session records.
        """
        logger.debug("Getting RTR session details for IDs: %s", ids)

        if not ids:
            return []

        return self._base_get_by_ids(
            operation="RTR_ListSessions",
            ids=ids,
            id_key="ids",
            use_params=False,
        )

    def init_session(
        self,
        device_id: str = Field(
            description="The host agent ID (AID) to open or reuse an RTR session for.",
        ),
        origin: str = Field(
            default="falcon-mcp",
            description="Origin label for the RTR request.",
        ),
        queue_offline: bool = Field(
            default=False,
            description="Queue the request if the host is currently offline.",
        ),
        timeout: int | None = Field(
            default=None,
            ge=1,
            le=600,
            description="How long to wait for the request in seconds. Max: 600.",
        ),
        timeout_duration: str | None = Field(
            default=None,
            description="Alternate duration syntax such as `30s`, `2m`, or `1h`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Initialize or reuse an RTR session for a single host.

        Opens a live connection to the specified device for executing RTR commands.
        Use queue_offline=True if the host may be offline. Returns session records
        containing the session_id needed for subsequent commands.
        """
        return self._base_query_api_call(
            operation="RTR_InitSession",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
            },
            body_params={
                "device_id": device_id,
                "origin": origin,
                "queue_offline": queue_offline,
            },
            error_message="Failed to initialize RTR session",
        )

    def pulse_session(
        self,
        device_id: str = Field(
            description="The host agent ID (AID) whose RTR session timeout should be refreshed.",
        ),
        origin: str = Field(
            default="falcon-mcp",
            description="Origin label for the RTR request.",
        ),
        queue_offline: bool = Field(
            default=False,
            description="Queue the pulse if the host is currently offline.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Refresh an RTR session timeout for a single host.

        Keeps an existing session alive by resetting its inactivity timer. Use this
        to prevent session expiration during long investigations.
        """
        return self._base_query_api_call(
            operation="RTR_PulseSession",
            body_params={
                "device_id": device_id,
                "origin": origin,
                "queue_offline": queue_offline,
            },
            error_message="Failed to pulse RTR session",
        )

    def execute_read_only_command(
        self,
        session_id: str = Field(
            description="RTR session ID returned from falcon_init_rtr_session or falcon_search_rtr_sessions.",
        ),
        base_command: str = Field(
            description="Read-only RTR base command to execute, such as `ls`, `ps`, `cat`, `filehash`, or `reg`.",
            examples=["ls", "ps", "filehash"],
        ),
        command_string: str | None = Field(
            default=None,
            description="Optional full command line to execute. Example: `cat C:\\Windows\\win.ini`.",
        ),
        persist: bool = Field(
            default=False,
            description="Persist the read-only command in the RTR session history.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Execute a read-only RTR command on a single host.

        Limited to read-only commands (ls, ps, cat, filehash, reg) for hunt and triage
        workflows. Does not expose admin or remediation commands. Returns command records
        containing a cloud_request_id for polling output via falcon_check_rtr_command_status.
        """
        return self._base_query_api_call(
            operation="RTR_ExecuteCommand",
            body_params={
                "session_id": session_id,
                "base_command": base_command,
                "command_string": command_string,
                "persist": persist,
            },
            error_message="Failed to execute RTR read-only command",
        )

    def check_command_status(
        self,
        cloud_request_id: str = Field(
            description="Cloud request ID returned from falcon_execute_rtr_read_only_command.",
        ),
        sequence_id: int = Field(
            default=0,
            ge=0,
            description="Sequence chunk to retrieve for command output. Starts at 0.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get the status and output for an RTR command execution.

        Poll this after falcon_execute_rtr_read_only_command to retrieve command
        output. Use sequence_id to paginate through large output chunks.
        """
        return self._base_query_api_call(
            operation="RTR_CheckCommandStatus",
            query_params={
                "cloud_request_id": cloud_request_id,
                "sequence_id": sequence_id,
            },
            error_message="Failed to check RTR command status",
        )

    def run_read_only_command_and_wait(
        self,
        session_id: str = Field(
            description="RTR session ID returned from falcon_init_rtr_session or falcon_search_rtr_sessions.",
        ),
        base_command: str = Field(
            description="Read-only RTR base command to execute, such as `ls`, `ps`, `cat`, `filehash`, or `reg`.",
            examples=["ls", "ps", "filehash"],
        ),
        command_string: str | None = Field(
            default=None,
            description="Optional full command line to execute. Example: `cat C:\\Windows\\win.ini`.",
        ),
        persist: bool = Field(
            default=False,
            description="Persist the read-only command in the RTR session history.",
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
            description="Seconds to wait between command status checks.",
        ),
    ) -> dict[str, Any]:
        """Execute a read-only RTR command and poll until completion.

        Use this for simple, focused RTR evidence collection when the user
        wants the command output directly and does not need to manually manage
        a cloud request ID. This polls command status until completion or
        timeout, accumulating output chunks into one result. It still executes
        an RTR command and creates RTR command activity, but it does not expose
        RTR Admin or remediation APIs.
        """
        execute_result = self._base_query_api_call(
            operation="RTR_ExecuteCommand",
            body_params={
                "session_id": session_id,
                "base_command": base_command,
                "command_string": command_string,
                "persist": persist,
            },
            error_message="Failed to execute RTR read-only command",
        )

        if self._is_error(execute_result):
            execute_result["phase"] = "execute"
            return execute_result

        if not isinstance(execute_result, list) or not execute_result:
            return {
                "error": "RTR command execution did not return a command request.",
                "phase": "execute",
                "results": execute_result,
            }

        command_request = execute_result[0]
        if not isinstance(command_request, dict):
            return {
                "error": "RTR command execution returned an unexpected response shape.",
                "phase": "execute",
                "results": execute_result,
            }

        cloud_request_id = command_request.get("cloud_request_id")
        if not cloud_request_id:
            return {
                "error": "RTR command execution did not return a cloud_request_id.",
                "phase": "execute",
                "execution": command_request,
            }

        deadline = time.monotonic() + timeout_seconds
        status_chunks: list[dict[str, Any]] = []
        sequence_id = 0

        while True:
            status_result = self._base_query_api_call(
                operation="RTR_CheckCommandStatus",
                query_params={
                    "cloud_request_id": cloud_request_id,
                    "sequence_id": sequence_id,
                },
                error_message="Failed to check RTR command status",
            )

            if self._is_error(status_result):
                status_result["phase"] = "status"
                status_result["cloud_request_id"] = cloud_request_id
                return status_result

            if isinstance(status_result, list):
                status_chunks.extend(
                    chunk for chunk in status_result if isinstance(chunk, dict)
                )

            complete = any(chunk.get("complete") is True for chunk in status_chunks)
            if complete:
                return self._format_wait_result(
                    cloud_request_id=cloud_request_id,
                    command_request=command_request,
                    status_chunks=status_chunks,
                    complete=True,
                    timed_out=False,
                )

            if time.monotonic() >= deadline:
                return self._format_wait_result(
                    cloud_request_id=cloud_request_id,
                    command_request=command_request,
                    status_chunks=status_chunks,
                    complete=False,
                    timed_out=True,
                )

            if status_chunks:
                sequence_id = status_chunks[-1].get("sequence_id", sequence_id)
            time.sleep(poll_interval_seconds)

    def list_session_files(
        self,
        session_id: str = Field(
            description="RTR session ID to retrieve extracted session files for.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List files extracted during an RTR session.

        Returns file metadata for artifacts captured during the session, such as
        files pulled with the `get` command.
        """
        return self._base_query_api_call(
            operation="RTR_ListFilesV2",
            query_params={"session_id": session_id},
            error_message="Failed to list RTR session files",
        )

    def delete_session(
        self,
        session_id: str = Field(
            description="RTR session ID to close.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Close an RTR session and release the host connection.

        Use this when investigation is complete to free up session resources.
        """
        return self._base_query_api_call(
            operation="RTR_DeleteSession",
            query_params={"session_id": session_id},
            error_message="Failed to delete RTR session",
        )

    def _format_wait_result(
        self,
        cloud_request_id: str,
        command_request: dict[str, Any],
        status_chunks: list[dict[str, Any]],
        complete: bool,
        timed_out: bool,
    ) -> dict[str, Any]:
        """Format command-and-wait output for model-friendly consumption."""
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
            "status": status_chunks,
            "stdout": stdout,
            "stderr": stderr,
        }

        if timed_out:
            result["warning"] = "Timed out waiting for RTR command completion."

        return result
