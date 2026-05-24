"""
Triage module for Falcon MCP Server

Composite investigation tools that combine multiple API calls into single,
token-optimized operations for common SOC workflows.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from pydantic import Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.field_presets import HOST_SUMMARY_FIELDS
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import (
    filter_fields,
    format_response,
    prepare_api_parameters,
)
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class TriageModule(BaseModule):
    """Composite investigation tools for common SOC triage workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register triage tools with the MCP server."""
        self._add_tool(server, self.get_host_triage_context, "get_host_triage_context")

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
    ) -> dict[str, Any]:
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
                "limit": 0,
            }),
        )

        recent_count = 0
        if detection_result.get("status_code") == 200:
            resources = detection_result.get("body", {}).get("resources", [])
            recent_count = len(resources) if resources else 0

        filtered_host["recent_detection_count"] = recent_count

        return format_response(filtered_host, format)
