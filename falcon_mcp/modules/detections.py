"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""

from textwrap import dedent
from typing import Any, Dict, List

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.common.constants import SearchLimits
from falcon_mcp.resources.detections import SEARCH_DETECTIONS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class DetectionsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon detections."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
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
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://detections/search/fql-guide` resource when building this filter parameter.",
            examples={"agent_id:'77d11725xxxxxxxxxxxxxxxxxxxxc48ca19'", "status:'new'"},
        ),
        limit: int = Field(
            default=SearchLimits.DEFAULT,
            ge=1,
            le=SearchLimits.MAX_DETECTIONS,
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
            examples={"severity.desc", "timestamp.desc"},
        ),
        include_hidden: bool = Field(default=True),
    ) -> List[Dict[str, Any]]:
        """Find and analyze detections to understand malicious activity in your environment.

        IMPORTANT: You must use the `falcon://detections/search/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_detections` tool.
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

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(detection_ids):
            return [detection_ids]

        # If we have detection IDs, get the details for each one
        if detection_ids:
            details = self._base_get_by_ids(
                operation="PostEntitiesAlertsV2",
                ids=detection_ids,
                id_key="composite_ids",
                include_hidden=include_hidden,
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if self._is_error(details):
                return [details]

            return details

        return []

    def get_detection_details(
        self,
        ids: List[str] = Field(
            description="Composite ID(s) to retrieve detection details for.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.",
        ),
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Get detection details for specific detection IDs to understand security threats.

        Use this when you already have specific detection IDs and need their full details.
        For searching/discovering detections, use the `falcon_search_detections` tool instead.
        """
        logger.debug("Getting detection details for ID(s): %s", ids)

        return self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )
