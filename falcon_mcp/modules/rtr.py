"""
Real Time Response module for Falcon MCP Server.

This module provides tools for initiating and inspecting RTR sessions and for
executing read-only RTR commands during host investigations.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr import (
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
            return self._format_fql_error_response(
                [], filter, SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="RTR_ListSessions",
            ids=session_ids,
            id_key="ids",
            use_params=False,
        )

        if self._is_error(details):
            return [details]

        return details

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
