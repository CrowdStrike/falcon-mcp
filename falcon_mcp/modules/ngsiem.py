"""
NGSIEM module for Falcon MCP Server

This module provides tools for running search queries against CrowdStrike's
Next-Gen SIEM (LogScale-based) via the asynchronous job-based search API.
"""

import time
from datetime import datetime
from typing import Any

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)

POLL_INTERVAL_SECONDS = 5
TIMEOUT_SECONDS = 300


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

    def search_ngsiem(
        self,
        query_string: str = Field(
            description=(
                "CQL query string to execute against Next-Gen SIEM. "
                "This is the CrowdStrike Query Language expression. "
                'Examples: "aid=abc123", "#event_simpleName=ProcessRollup2", "ComputerName=DC*"'
            ),
        ),
        start: str = Field(
            description=(
                "Search start time as an ISO 8601 timestamp. "
                'Example: "2025-01-01T00:00:00Z"'
            ),
        ),
        repository: str = Field(
            default="search-all",
            description=(
                "Repository to search. Valid options: "
                "search-all (all event data from CrowdStrike and third-party sources), "
                "investigate_view (endpoint event data and sensor events - requires Falcon Insight XDR), "
                "third-party (event data from third-party sources - requires Falcon LogScale), "
                "falcon_for_it_view (data collected by Falcon for IT), "
                "forensics_view (triage data from Falcon Forensics)"
            ),
        ),
        end: str | None = Field(
            default=None,
            description=(
                "Search end time as an ISO 8601 timestamp. "
                "If not provided, defaults to the current time. "
                'Example: "2025-02-06T00:00:00Z"'
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search CrowdStrike Next-Gen SIEM (LogScale) for events.

        Executes a CQL (CrowdStrike Query Language) query against the NGSIEM search API.
        This tool starts an asynchronous search job, polls for completion, and returns
        the matching events.

        The search is asynchronous and job-based: it starts a search job, polls until
        the job completes, then returns the events found.

        Common use cases:
        - Search for events by agent ID: query_string="aid=abc123"
        - Search for process events: query_string="#event_simpleName=ProcessRollup2"
        - Search by hostname pattern: query_string="ComputerName=DC*"
        - Search third-party logs: repository="third-party"
        """
        # Step 1: Start the search job
        # Note: FalconPy uber class passes body unchanged; API expects camelCase keys
        # and Unix epoch milliseconds for timestamps
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
            return {
                "error": "Failed to start NGSIEM search: no job ID returned",
                "details": start_response.get("body", {}),
            }

        logger.debug("NGSIEM search job started: %s", job_id)

        # Step 2: Poll for completion
        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            time.sleep(POLL_INTERVAL_SECONDS)
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

        return {
            "error": f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds",
            "hint": (
                "The search did not complete within the timeout period. "
                "Try narrowing your query or reducing the time range."
            ),
            "job_id": job_id,
        }
