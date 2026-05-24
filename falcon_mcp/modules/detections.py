"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""

from textwrap import dedent
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.field_presets import DETECTION_SUMMARY_FIELDS
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import filter_records, format_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.detections import (
    SEARCH_DETECTIONS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class DetectionsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon detections."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_detections,
            name="search_detections",
        )

        self._add_tool(
            server=server,
            method=self.get_detection_details,
            name="get_detection_details",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_detections_fql_resource = TextResource(
            uri=AnyUrl("falcon://detections/search/fql-guide"),
            name="falcon_search_detections_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_detections` tool.",
            text=SEARCH_DETECTIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_detections_fql_resource,
        )

    def search_detections(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://detections/search/fql-guide` for syntax.",
            examples=["status:'new'+severity_name:'High'", "device.hostname:'DC*'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=9999,
            description="The maximum number of detections to return in this response (default: 10; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: int | None = Field(
            default=None,
            description="The first detection to return, where 0 is the latest detection. Use with the offset parameter to manage pagination of results.",
        ),
        q: str | None = Field(
            default=None,
            description="Search all detection metadata for the provided string",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort detections using these options:

                timestamp: Timestamp when the detection occurred
                created_timestamp: When the detection was created
                updated_timestamp: When the detection was last modified
                severity: Severity level of the detection (1-100, recommended when filtering by severity)
                confidence: Confidence level of the detection (1-100)
                agent_id: Agent ID associated with the detection

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'severity.desc' or 'severity|desc'

                When searching for high severity detections, use 'severity.desc' to get the highest severity detections first.
                For chronological ordering, use 'timestamp.desc' for most recent detections first.

                Examples: 'severity.desc', 'timestamp.desc'
            """).strip(),
            examples=["severity.desc", "timestamp.desc"],
        ),
        include_hidden: bool = Field(default=True),
        view: Literal["summary", "full"] = Field(
            default="summary",
            description="'summary' returns investigation-essential fields only (default). 'full' returns the complete API response.",
        ),
        fields: list[str] | None = Field(
            default=None,
            description="Override: explicit list of fields to return. Takes precedence over view.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Find detections by criteria and return their complete details.

        Use this to discover detections by severity, status, hostname, time range, or
        other attributes. Consult falcon://detections/search/fql-guide before constructing
        filter expressions. Returns full alert records including process context, device
        info, tactic/technique details, and threat classification.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(view, FieldInfo):
            view = view.default
        if isinstance(fields, FieldInfo):
            fields = fields.default
        if isinstance(format, FieldInfo):
            format = format.default

        detection_ids = self._base_search_api_call(
            operation="GetQueriesAlertsV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "q": q,
                "sort": sort,
            },
            error_message="Failed to search detections",
        )

        # Handle search error - return with FQL guide
        if self._is_error(detection_ids):
            return self._format_fql_error_response(
                [detection_ids], filter, SEARCH_DETECTIONS_FQL_DOCUMENTATION
            )

        # Handle empty results - return with FQL guide
        if not detection_ids:
            return self._format_fql_error_response([], filter, SEARCH_DETECTIONS_FQL_DOCUMENTATION)

        # Get detection details - past FQL concerns, normal API flow
        details = self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=detection_ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )

        if self._is_error(details):
            return [details]

        if isinstance(details, list):
            if fields:
                details = filter_records(details, fields)
            elif view == "summary":
                details = filter_records(details, DETECTION_SUMMARY_FIELDS)
            return format_response(details, format)

        return details

    def get_detection_details(
        self,
        ids: list[str] = Field(
            description="Composite ID(s) to retrieve detection details for.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.",
        ),
        view: Literal["summary", "full"] = Field(
            default="summary",
            description="'summary' returns investigation-essential fields only (default). 'full' returns the complete API response.",
        ),
        fields: list[str] | None = Field(
            default=None,
            description="Override: explicit list of fields to return. Takes precedence over view.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Retrieve details for detection IDs you already have.

        Use when you have specific composite detection ID(s). For discovering detections
        by criteria (severity, status, hostname, etc.), use falcon_search_detections
        instead. Returns full detection records.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(view, FieldInfo):
            view = view.default
        if isinstance(fields, FieldInfo):
            fields = fields.default
        if isinstance(format, FieldInfo):
            format = format.default

        logger.debug("Getting detection details for ID(s): %s", ids)

        result = self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )

        if self._is_error(result):
            return result

        if isinstance(result, list):
            if fields:
                result = filter_records(result, fields)
            elif view == "summary":
                result = filter_records(result, DETECTION_SUMMARY_FIELDS)
            return format_response(result, format)

        return result
