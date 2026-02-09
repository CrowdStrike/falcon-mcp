"""
NGSIEM module for Falcon MCP Server

This module provides tools for running search queries against CrowdStrike's
Next-Gen SIEM via the asynchronous job-based search API.
"""

import asyncio
import os
from datetime import datetime
from typing import Any

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)

# Configurable polling settings
POLL_INTERVAL_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
TIMEOUT_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))


def _iso_to_epoch_ms(iso_timestamp: str) -> int:
    """Convert ISO 8601 timestamp to Unix epoch milliseconds.

    Args:
        iso_timestamp: ISO 8601 formatted timestamp (e.g., "2025-01-01T00:00:00Z")

    Returns:
        Unix epoch time in milliseconds
    """
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


class NGSIEMModule(BaseModule):
    """Module for running search queries against CrowdStrike Next-Gen SIEM."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_ngsiem,
            name="search_ngsiem",
        )

    async def search_ngsiem(
        self,
        query_string: str = Field(
            description=(
                "The CQL query string to execute. "
                "This tool executes pre-written CQL queries - it does NOT help construct queries. "
                "Users must provide a complete, valid CQL query. "
                "Example: '#event_simpleName=ProcessRollup2' or 'source=firewall | count()'"
            ),
        ),
        start: str = Field(
            description=(
                "Search start time as an ISO 8601 timestamp (REQUIRED format). "
                "Example: start='2025-01-01T00:00:00Z'"
            ),
            examples={"2025-01-01T00:00:00Z"},
        ),
        repository: str = Field(
            default="search-all",
            description=(
                "Repository to search. Valid options: "
                "search-all (default - all event data), "
                "investigate_view (endpoint events), "
                "third-party (third-party source events), "
                "falcon_for_it_view (Falcon for IT data), "
                "forensics_view (Falcon Forensics triage data)"
            ),
        ),
        end: str | None = Field(
            default=None,
            description=(
                "Search end time as an ISO 8601 timestamp. "
                "If not provided, defaults to the current time. "
                "Example: end='2025-02-06T00:00:00Z'"
            ),
            examples={"2025-01-01T00:00:00Z"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Execute a CQL query against CrowdStrike Next-Gen SIEM.

        This tool executes pre-written CQL queries provided by the user. It does NOT
        assist with query construction - users must supply complete, valid CQL syntax.

        The tool starts an asynchronous search job, polls for completion (up to the
        configured timeout), and returns matching events.

        Note: Search times out after FALCON_MCP_NGSIEM_TIMEOUT seconds (default: 300).
        Polling interval is controlled by FALCON_MCP_NGSIEM_POLL_INTERVAL (default: 5).

        Args:
            query_string (required): The CQL query to execute. Example: '#event_simpleName=ProcessRollup2'
            start (required): ISO 8601 timestamp for search start. Example: '2025-01-01T00:00:00Z'
            repository (optional): Repository to search. Default: 'search-all'.
                Options: search-all, investigate_view, third-party, falcon_for_it_view, forensics_view
            end (optional): ISO 8601 timestamp for search end. Defaults to current time.
        """
        # Step 1: Start the search job
        # Note: FalconPy uber class passes body unchanged; API expects camelCase keys
        body_params: dict[str, Any] = {
            "queryString": query_string,
            "start": _iso_to_epoch_ms(start),
        }
        if isinstance(end, str):
            body_params["end"] = _iso_to_epoch_ms(end)

        logger.debug("Starting NGSIEM search with query: %s", query_string)

        start_response = self.client.command(
            operation="StartSearchV1",
            repository=repository,
            body=body_params,
        )

        start_status = start_response.get("status_code")
        if start_status != 200:
            return handle_api_response(
                start_response,
                operation="StartSearchV1",
                error_message="Failed to start NGSIEM search",
                default_result=[],
            )

        job_id = start_response.get("body", {}).get("id")
        if not job_id:
            return _format_error_response(
                message="Failed to start NGSIEM search: no job ID returned",
                details=start_response.get("body", {}),
                operation="StartSearchV1",
            )

        logger.debug("NGSIEM search job started: %s", job_id)

        # Step 2: Poll for completion
        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            poll_response = self.client.command(
                operation="GetSearchStatusV1",
                repository=repository,
                search_id=job_id,
            )

            poll_status = poll_response.get("status_code")
            if poll_status != 200:
                return handle_api_response(
                    poll_response,
                    operation="GetSearchStatusV1",
                    error_message="Failed to poll NGSIEM search status",
                    default_result=[],
                )

            body = poll_response.get("body", {})
            if body.get("done"):
                logger.debug("NGSIEM search job completed: %s", job_id)
                return body.get("events", [])

        # Step 3: Timeout — attempt cleanup
        logger.warning("NGSIEM search job timed out: %s", job_id)
        self.client.command(
            operation="StopSearchV1",
            repository=repository,
            id=job_id,
        )

        return _format_error_response(
            message=f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds. "
            "Try narrowing your query or reducing the time range.",
            details={"job_id": job_id, "timeout_seconds": TIMEOUT_SECONDS},
            operation="GetSearchStatusV1",
        )
