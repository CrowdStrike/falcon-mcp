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
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ngsiem import SEARCH_NGSIEM_CQL_DOCUMENTATION

logger = get_logger(__name__)

# Hint appended to error/empty responses steering the model to the CQL guide.
_CQL_ERROR_HINT = (
    "Review the CQL guide above and correct your query. CQL is a pipe-based "
    "language (filter | command | command) — not SQL or Splunk SPL. Consult "
    "`falcon://ngsiem/search/cql-guide` for the syntax and working examples."
)
_CQL_EMPTY_HINT = (
    "0 events returned. This can mean no data matched, but it is also how the API "
    "reports an invalid query (it free-text-matches malformed CQL rather than "
    "erroring). If this is unexpected, review the CQL guide above and verify your "
    "query syntax and field names. Consult `falcon://ngsiem/search/cql-guide`."
)

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

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_ngsiem_cql_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/search/cql-guide"),
            name="falcon_search_ngsiem_cql_guide",
            description="Contains the CQL authoring guide for the `query_string` param of the `falcon_search_ngsiem` tool.",
            text=SEARCH_NGSIEM_CQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_ngsiem_cql_resource,
        )

    def _format_cql_error_response(
        self,
        error_response: dict[str, Any],
        query_string: str,
    ) -> dict[str, Any]:
        """Augment an error response with the CQL guide and a repair hint.

        Reaches the model with the full CQL authoring guide exactly when its query
        failed, so it can correct the syntax and retry. Mirrors
        `_format_fql_error_response` but for CQL (the API returns no CQL parser
        diagnostics, so the guide is the only actionable signal).

        Args:
            error_response: The error dict produced by the shared error handlers
            query_string: The CQL query that was attempted

        Returns:
            The error dict with `cql_guide`, `hint`, and `query_used` added
        """
        error_response["query_used"] = query_string
        error_response["cql_guide"] = SEARCH_NGSIEM_CQL_DOCUMENTATION
        error_response["hint"] = _CQL_ERROR_HINT
        return error_response

    async def search_ngsiem(
        self,
        query_string: str = Field(
            description=(
                "The CQL (CrowdStrike Query Language) query to execute. "
                "Consult `falcon://ngsiem/search/cql-guide` to construct this query. "
                "CQL is pipe-based: `filter | command | command` — not SQL or Splunk "
                "SPL (do not use SELECT/WHERE/stats/`| limit`). Build a query by "
                "starting from a tag or field filter and piping into commands. "
                "Common building blocks: tag filter `#event_simpleName=ProcessRollup2`; "
                "field match `UserName=*`; aggregate `groupBy([ComputerName], function=count())`; "
                "order `sort(_count, order=desc)`; limit raw events `head(5)`. "
                "Examples: '#event_simpleName=ProcessRollup2 | head(5)' and "
                "'#event_simpleName=ProcessRollup2 | groupBy([ComputerName], function=count()) "
                "| sort(_count, order=desc)'. "
                "For anything beyond these building blocks (distinct count, time "
                "bucketing, regex/contains match, filtering on an aggregate), read "
                "`falcon://ngsiem/search/cql-guide` — it has working examples."
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
                "Repository (or view) to search. Defaults to search-all (all event "
                "data). Which repositories exist depends on the users tenant and its "
                "configuration, so this is not a closed list. Common repositories/views: "
                "search-all (all event data), "
                "investigate_view (endpoint events), "
                "xdr (XDR data), "
                "third-party (third-party source events), "
                "falcon_for_it_view (Falcon for IT data), "
                "forensics_view (Falcon Forensics triage data). "
                "Custom and other built-in repositories/views can also be passed by name."
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
        """Execute a CQL (CrowdStrike Query Language) query against CrowdStrike Next-Gen SIEM.

        Use this to search security events, logs, and telemetry with CQL. CQL is a
        pipe-based language (`filter | command | command`): start from a tag or field
        filter (e.g. `#event_simpleName=ProcessRollup2`, `UserName=*`) and pipe into
        commands like `groupBy([...], function=count())` and `sort()`; keep the time
        range tight. Consult `falcon://ngsiem/search/cql-guide` to construct the query —
        it has the pipe model, core commands, and working examples (distinct count, time
        bucketing, regex match, filtering on an aggregate). Returns matching event
        records, or an error/empty dict carrying the CQL guide when the job fails,
        times out, or returns no rows. Note: the API does not return detailed CQL parser
        diagnostics — a malformed query may error or silently return unexpected/empty
        results rather than a helpful message, so a result is not proof the query parsed
        as intended. Search times out after FALCON_MCP_NGSIEM_TIMEOUT seconds
        (default: 300).
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

        start_response = await self.client.command_async(
            operation="StartSearchV1",
            repository=repository,
            body=body_params,
        )

        start_status = start_response.get("status_code")
        if start_status != 200:
            error_response = handle_api_response(
                start_response,
                operation="StartSearchV1",
                error_message="Failed to start NGSIEM search",
                default_result=[],
            )
            return self._format_cql_error_response(error_response, query_string)

        job_id = start_response.get("body", {}).get("id")
        if not job_id:
            error_response = _format_error_response(
                message="Failed to start NGSIEM search: no job ID returned",
                details=start_response.get("body", {}),
                operation="StartSearchV1",
            )
            return self._format_cql_error_response(error_response, query_string)

        logger.debug("NGSIEM search job started: %s", job_id)

        # Step 2: Poll for completion
        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            poll_response = await self.client.command_async(
                operation="GetSearchStatusV1",
                repository=repository,
                search_id=job_id,
            )

            poll_status = poll_response.get("status_code")
            if poll_status != 200:
                error_response = handle_api_response(
                    poll_response,
                    operation="GetSearchStatusV1",
                    error_message="Failed to poll NGSIEM search status",
                    default_result=[],
                )
                return self._format_cql_error_response(error_response, query_string)

            body = poll_response.get("body", {})
            if body.get("done"):
                logger.debug("NGSIEM search job completed: %s", job_id)
                events = body.get("events", [])
                if not events:
                    # The API free-text-matches invalid CQL and returns 200 with an
                    # empty list, so an empty result is the most common silent-failure
                    # signal. Return the guide + hint so the model can self-correct.
                    return {
                        "results": [],
                        "query_used": query_string,
                        "cql_guide": SEARCH_NGSIEM_CQL_DOCUMENTATION,
                        "hint": _CQL_EMPTY_HINT,
                    }
                return events

        # Step 3: Timeout — attempt cleanup
        logger.warning("NGSIEM search job timed out: %s", job_id)
        await self.client.command_async(
            operation="StopSearchV1",
            repository=repository,
            id=job_id,
        )

        error_response = _format_error_response(
            message=f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds. "
            "Try narrowing your query or reducing the time range.",
            details={"job_id": job_id, "timeout_seconds": TIMEOUT_SECONDS},
            operation="GetSearchStatusV1",
        )
        return self._format_cql_error_response(error_response, query_string)
