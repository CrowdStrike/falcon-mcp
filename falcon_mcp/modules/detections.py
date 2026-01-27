"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.detections import (
    EMBEDDED_FQL_SYNTAX,
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
            description=EMBEDDED_FQL_SYNTAX,
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
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Find detections by criteria and return their complete details.

        Use this tool to discover detections - filter by severity, status, hostname,
        time range, etc. Returns full detection information including behaviors,
        device context, and threat details.

        Returns FQL syntax guide on error or empty results to help refine queries.
        """
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
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve details for detection IDs you already have.

        Use ONLY when you have specific composite detection ID(s). To find detections
        by criteria (severity, status, hostname, etc.), use `falcon_search_detections`.
        """
        logger.debug("Getting detection details for ID(s): %s", ids)

        return self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )
