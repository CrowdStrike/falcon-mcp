"""
Triage module for Falcon MCP Server

Composite investigation tools that combine multiple API calls into single,
token-optimized operations for common SOC workflows.
"""

import asyncio
import os
from typing import Any, Literal

from mcp.server import FastMCP
from pydantic import Field
from pydantic.fields import FieldInfo

from falcon_mcp import registry
from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.field_presets import (
    DETECTION_SUMMARY_FIELDS,
    HOST_SUMMARY_FIELDS,
    PROCESS_TELEMETRY_FIELDS,
)
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import (
    filter_fields,
    filter_records,
    format_response,
    prepare_api_parameters,
    truncate_string_fields,
)
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)

# Reuse NGSIEM polling settings
POLL_INTERVAL_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
TIMEOUT_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))


class TriageModule(BaseModule):
    """Composite investigation tools for common SOC triage workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register triage tools with the MCP server."""
        self._add_tool(server, self.get_host_triage_context, "get_host_triage_context")
        self._add_tool(server, self.get_detection_triage, "get_detection_triage")
        if "ngsiem" in registry.get_module_names():
            self._add_tool(server, self.get_process_verdict_context, "get_process_verdict_context")

    def get_host_triage_context(
        self,
        hostname: str | None = Field(
            default=None,
            description="Hostname to look up. Provide at least one of hostname or device_id.",
        ),
        device_id: str | None = Field(
            default=None,
            description="CrowdStrike device ID. Provide at least one of hostname or device_id.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> dict[str, Any] | str:
        """Get host context plus recent detection count in a single call.

        Resolves hostname to device_id if needed, fetches host details filtered to
        investigation-essential fields, and appends the 7-day detection count.
        Use this as a first step when triaging an alert to understand the host posture.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(hostname, FieldInfo):
            hostname = hostname.default
        if isinstance(device_id, FieldInfo):
            device_id = device_id.default
        if isinstance(format, FieldInfo):
            format = format.default

        # Validate: at least one identifier required
        if not hostname and not device_id:
            return {"error": "At least one of hostname or device_id is required."}

        # Step 1: Resolve hostname -> device_id if needed
        if not device_id:
            ids = self._base_search_api_call(
                operation="QueryDevicesByFilter",
                search_params={"filter": f"hostname:'{hostname}'", "limit": 1},
                error_message="Failed to resolve hostname",
            )
            if self._is_error(ids):
                return ids
            if not ids:
                return _format_error_response(
                    message=f"No device found for hostname '{hostname}'.",
                    operation="QueryDevicesByFilter",
                )
            device_id = ids[0]

        # Step 2: Fetch host details
        details = self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=[device_id],
            id_key="ids",
        )
        if self._is_error(details):
            return details

        host = details[0] if isinstance(details, list) and details else details
        filtered_host = filter_fields(host, HOST_SUMMARY_FIELDS)

        # Step 3: Fetch recent detection count (7 days)
        detection_result = self.client.command(
            "GetQueriesAlertsV2",
            parameters=prepare_api_parameters({
                "filter": f"device.device_id:'{device_id}'+created_timestamp:>='now-7d'",
                "limit": 1,
            }),
        )

        recent_count = (
            detection_result.get("body", {})
            .get("meta", {})
            .get("pagination", {})
            .get("total", 0)
        )

        filtered_host["recent_detection_count"] = recent_count

        return format_response(filtered_host, format)

    def get_detection_triage(
        self,
        detection_id: str = Field(
            description="Composite detection ID to retrieve triage details for.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> dict[str, Any] | str:
        """Get a single detection filtered to investigation-essential fields.

        Fetches the detection by composite ID and returns only the fields needed
        for triage decisions: severity, confidence, MITRE mapping, process chain,
        and device context.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(format, FieldInfo):
            format = format.default

        result = self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=[detection_id],
            id_key="composite_ids",
            include_hidden=True,
        )

        if self._is_error(result):
            return result

        detection = result[0] if isinstance(result, list) and result else result
        filtered = filter_fields(detection, DETECTION_SUMMARY_FIELDS)

        return format_response(filtered, format)

    async def get_process_verdict_context(
        self,
        device_id: str = Field(
            description="CrowdStrike device ID (aid) to search process telemetry for.",
        ),
        process_name: str | None = Field(
            default=None,
            description="Process file name to search for. Provide at least one of process_name or pid.",
        ),
        pid: str | None = Field(
            default=None,
            description="Target process ID. Provide at least one of process_name or pid.",
        ),
        start: str = Field(
            description="Search start time as ISO 8601 timestamp. Example: '2025-01-01T00:00:00Z'",
        ),
        end: str | None = Field(
            default=None,
            description="Search end time as ISO 8601 timestamp. Defaults to now if omitted.",
        ),
        max_field_length: int = Field(
            default=2048,
            description="Auto-truncate string fields longer than this value.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Search ProcessRollup2 telemetry for a specific process on a device.

        Queries NGSIEM for process execution events matching the given device and
        process name or PID within the time window. Returns telemetry filtered to
        verdict-relevant fields: hashes, signatures, command line, parent chain.
        Requires the NGSIEM module to be enabled.
        """
        from falcon_mcp.modules.ngsiem import _iso_to_epoch_ms

        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(device_id, FieldInfo):
            device_id = device_id.default
        if isinstance(process_name, FieldInfo):
            process_name = process_name.default
        if isinstance(pid, FieldInfo):
            pid = pid.default
        if isinstance(end, FieldInfo):
            end = end.default
        if isinstance(max_field_length, FieldInfo):
            max_field_length = max_field_length.default
        if isinstance(format, FieldInfo):
            format = format.default

        # Validate inputs
        if not device_id:
            return {"error": "device_id is required."}

        if not process_name and not pid:
            return {"error": "At least one of process_name or pid is required."}

        # Build CQL query
        cql_parts = [f'#event_simpleName="ProcessRollup2"', f'aid="{device_id}"']
        if process_name:
            cql_parts.append(f'FileName="{process_name}"')
        if pid:
            cql_parts.append(f'TargetProcessId="{pid}"')
        query_string = " ".join(cql_parts)

        # Start NGSIEM search
        body_params: dict[str, Any] = {
            "queryString": query_string,
            "start": _iso_to_epoch_ms(start),
        }
        if isinstance(end, str):
            body_params["end"] = _iso_to_epoch_ms(end)

        logger.debug("Starting process verdict search: %s", query_string)

        start_response = self.client.command(
            operation="StartSearchV1",
            repository="search-all",
            body=body_params,
        )

        start_status = start_response.get("status_code")
        if start_status != 200:
            return handle_api_response(
                start_response,
                operation="StartSearchV1",
                error_message="Failed to start process verdict search",
                default_result=[],
            )

        job_id = start_response.get("body", {}).get("id")
        if not job_id:
            return _format_error_response(
                message="Failed to start process verdict search: no job ID returned",
                details=start_response.get("body", {}),
                operation="StartSearchV1",
            )

        # Poll for completion
        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            poll_response = self.client.command(
                operation="GetSearchStatusV1",
                repository="search-all",
                search_id=job_id,
            )

            poll_status = poll_response.get("status_code")
            if poll_status != 200:
                return handle_api_response(
                    poll_response,
                    operation="GetSearchStatusV1",
                    error_message="Failed to poll process verdict search status",
                    default_result=[],
                )

            body = poll_response.get("body", {})
            if body.get("done"):
                events = body.get("events", [])
                events = [truncate_string_fields(e, max_field_length) for e in events]
                events = filter_records(events, PROCESS_TELEMETRY_FIELDS)
                return format_response(events, format)

        # Timeout — attempt cleanup
        logger.warning("Process verdict search timed out: %s", job_id)
        self.client.command(
            operation="StopSearchV1",
            repository="search-all",
            id=job_id,
        )

        return _format_error_response(
            message=f"Process verdict search timed out after {TIMEOUT_SECONDS} seconds.",
            details={"job_id": job_id, "timeout_seconds": TIMEOUT_SECONDS},
            operation="GetSearchStatusV1",
        )
