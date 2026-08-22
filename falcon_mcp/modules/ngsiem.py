"""
NGSIEM module for Falcon MCP Server

This module provides tools for running search queries against CrowdStrike's
Next-Gen SIEM via the asynchronous job-based search API.
"""

import asyncio
import os
from datetime import datetime, timezone
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
# The API demotes unrecognized CQL words to free-text stages instead of erroring, so
# `job.parsed_query` (its own normalization of what ran) is the only misparse signal.
_CQL_CONFIRMED_ZERO_HINT = (
    "No rows matched, and the job scanned {processed_events:,} events — a real "
    "negative. Report it as such rather than retrying. If you expected rows, check "
    "`job.parsed_query` against the query you sent."
)

# A correct filter over an empty partition and a misparsed query both scan nothing.
_CQL_UNSCANNED_ZERO_HINT = (
    "No rows, and `job.processed_events` does not show a completed scan, so this alone "
    "is not a confirmed negative. Compare `job.parsed_query` to the query you sent: "
    "unrecognized words become free-text stages instead of an error. If it matches your "
    "intent the negative is real; if not, correct the syntax using the guide above."
)

# Configurable polling settings
POLL_INTERVAL_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
TIMEOUT_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))

# `repository` is the only caller-supplied value in this server that reaches a URL
# path variable (/humio/api/v1/repositories/{repository}/queryjobs). FalconPy
# interpolates it into the route and `requests` normalizes the path before sending,
# so a separator or a bare dot-segment retargets the request at a route the calling
# operation never selected. A separator is what makes traversal possible, so once
# those are rejected only a whole-value dot-segment can still alter the path —
# `a..b` is inert and stays allowed.
_UNSAFE_REPOSITORY_CHARS = ("/", "\\", "%")
_DOT_SEGMENTS = (".", "..")


def _validate_repository(repository: Any) -> dict[str, Any] | None:
    """Reject a repository value that would change which route is called.

    Returns an error response to hand straight back to the caller, or None when the
    value is safe to interpolate.

    A non-str value is an unresolved Pydantic `Field` default, which happens only when
    the tool method is called directly instead of through FastMCP — the same reason
    `end` is guarded with `isinstance` below. FastMCP validates against the `str`
    annotation before dispatch, and the declared default is safe, so let it through.

    Args:
        repository: The caller-supplied repository or view name

    Returns:
        An error response dict, or None if the value is acceptable
    """
    if not isinstance(repository, str):
        return None

    if not repository.strip():
        return _format_error_response(
            "Invalid repository: must be a non-empty repository or view name, "
            "for example 'search-all'.",
            operation="StartSearchV1",
        )

    if any(char in repository for char in _UNSAFE_REPOSITORY_CHARS) or repository in _DOT_SEGMENTS:
        return _format_error_response(
            f"Invalid repository {repository!r}: must not contain '/', '\\', or '%', "
            "or be '.' or '..'. Pass a plain repository or view name, "
            "for example 'search-all'.",
            operation="StartSearchV1",
        )

    return None


def _iso_to_epoch_ms(iso_timestamp: str) -> int:
    """Convert ISO 8601 timestamp to Unix epoch milliseconds.

    Args:
        iso_timestamp: ISO 8601 formatted timestamp (e.g., "2025-01-01T00:00:00Z")

    Returns:
        Unix epoch time in milliseconds
    """
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def _epoch_ms_to_iso(epoch_ms: Any) -> str | None:
    """Convert Unix epoch milliseconds to an ISO 8601 UTC timestamp.

    Args:
        epoch_ms: Unix epoch time in milliseconds

    Returns:
        ISO 8601 timestamp string, or None if the value is not a usable number
    """
    if isinstance(epoch_ms, bool) or not isinstance(epoch_ms, (int, float)):
        return None
    try:
        return (
            datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except (OSError, OverflowError, ValueError):
        return None


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

    @staticmethod
    def _extract_job_metadata(
        body: dict[str, Any],
        repository: str,
        job_id: str,
    ) -> dict[str, Any]:
        """Map a search-status body onto the `job` block of the response envelope.

        Fields the response omits are reported as None, never defaulted to 0.

        Args:
            body: The `body` of a 200 GetSearchStatusV1 response
            repository: The repository the job ran against
            job_id: The search job ID

        Returns:
            Dict of job metadata suitable for the `job` key of the response envelope
        """
        meta = body.get("metaData") or {}
        filter_query = meta.get("filterQuery") or {}
        # Job-level and query-level warnings are scoped separately; callers want both.
        warnings = [*(body.get("warnings") or []), *(meta.get("warnings") or [])]

        return {
            "job_id": job_id,
            "repository": repository,
            "event_count": meta.get("eventCount"),
            "processed_events": meta.get("processedEvents"),
            "processed_bytes": meta.get("processedBytes"),
            "parsed_query": filter_query.get("queryString"),
            "search_start": _epoch_ms_to_iso(meta.get("queryStart")),
            "search_end": _epoch_ms_to_iso(meta.get("queryEnd")),
            "duration_ms": meta.get("timeMillis"),
            "is_aggregate": meta.get("isAggregate"),
            "cancelled": body.get("cancelled"),
            "warnings": warnings,
        }

    def _build_job_envelope(
        self,
        events: list[dict[str, Any]],
        job: dict[str, Any],
        query_string: str,
    ) -> dict[str, Any]:
        """Assemble the response envelope, identical in shape for any row count.

        NG-SIEM jobs carry no `meta.pagination`, so this keeps the house `results` key
        and swaps the pagination block for a `job` block. Zero rows also get the CQL
        guide and a hint chosen from `job.processed_events`.

        Args:
            events: The event records returned by the job
            job: Job metadata from `_extract_job_metadata`
            query_string: The CQL query as submitted

        Returns:
            Dict with `results`, `query_used`, `job`, and on zero rows also
            `cql_guide` and `hint`
        """
        envelope: dict[str, Any] = {
            "results": events,
            "query_used": query_string,
            "job": job,
        }

        if events:
            return envelope

        processed = job.get("processed_events")
        if isinstance(processed, int) and not isinstance(processed, bool) and processed > 0:
            hint = _CQL_CONFIRMED_ZERO_HINT.format(processed_events=processed)
        else:
            hint = _CQL_UNSCANNED_ZERO_HINT

        envelope["cql_guide"] = SEARCH_NGSIEM_CQL_DOCUMENTATION
        envelope["hint"] = hint
        return envelope

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
                "Custom and other built-in repositories/views can also be passed by name. "
                "Pass the bare name only: values containing '/', '\\', or '%' are rejected."
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
    ) -> dict[str, Any]:
        """Execute a CQL (CrowdStrike Query Language) query against CrowdStrike Next-Gen SIEM.

        Use this to search security events, logs, and telemetry with CQL. CQL is a
        pipe-based language (`filter | command | command`): start from a tag or field
        filter (e.g. `#event_simpleName=ProcessRollup2`, `UserName=*`) and pipe into
        commands like `groupBy([...], function=count())` and `sort()`; keep the time
        range tight. Consult `falcon://ngsiem/search/cql-guide` to construct the query —
        it has the pipe model, core commands, and working examples (distinct count, time
        bucketing, regex match, filtering on an aggregate). Returns
        `{results, query_used, job}`, where `job` carries the row count, events scanned,
        the window searched, and `job.parsed_query` — the API's own normalization of the
        query it ran. Check `job.parsed_query` against your intent: unrecognized words
        become free-text stages instead of an error, so `| limit 5` runs as `| limit | 5`
        and returns the wrong rows silently. On zero rows a hint says whether the job
        scanned events (a real negative) or scanned none (unresolved). Search times out
        after FALCON_MCP_NGSIEM_TIMEOUT seconds (default: 300).
        """
        # `repository` is interpolated into the request path, so validate it before it
        # can reach any of the three calls below.
        repository_error = _validate_repository(repository)
        if repository_error is not None:
            return repository_error

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
        last_job_meta: dict[str, Any] | None = None
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
            last_job_meta = self._extract_job_metadata(body, repository, job_id)
            if body.get("done"):
                logger.debug("NGSIEM search job completed: %s", job_id)
                return self._build_job_envelope(
                    body.get("events") or [],
                    last_job_meta,
                    query_string,
                )

        # Step 3: Timeout — attempt cleanup
        logger.warning("NGSIEM search job timed out: %s", job_id)
        stop_response = await self.client.command_async(
            operation="StopSearchV1",
            repository=repository,
            id=job_id,
        )

        # How far the job got, and whether cleanup actually stopped it.
        details: dict[str, Any] = {
            "job_id": job_id,
            "timeout_seconds": TIMEOUT_SECONDS,
            "stop_status_code": stop_response.get("status_code"),
        }
        if last_job_meta is not None:
            details["last_job_status"] = last_job_meta

        error_response = _format_error_response(
            message=f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds. "
            "Try narrowing your query or reducing the time range.",
            details=details,
            operation="GetSearchStatusV1",
        )
        return self._format_cql_error_response(error_response, query_string)
