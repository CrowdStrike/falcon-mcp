# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
from ..resources.detections import SEARCH_DETECTIONS_FQL_DOCUMENTATION
from .base import BaseModule

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
            server,
            self.search_detections,
            name="search_detections"
        )

        self._add_tool(
            server,
            self.search_detections_fql_filter_guide,
            name="search_detections_fql_filter_guide"
        )

        self._add_tool(
            server,
            self.get_detection_details,
            name="get_detection_details"
        )

    def search_detections(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_search_detections_fql_filter_guide` tool when building this filter parameter.", examples={"agent_id:'77d11725xxxxxxxxxxxxxxxxxxxxc48ca19'", "status:'new'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=9999, description="The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results."),
        offset: Optional[int] = Field(default=0, ge=0, description="The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results."),
        q: Optional[str] = Field(default=None, description="Search all detection metadata for the provided string"),
        sort: Optional[str] = Field(default=None, description="""Sort detections using these options:

    timestamp: Timestamp when the alert occurred
    created_timestamp: When the alert was created
    updated_timestamp: When the alert was last modified
    severity: Severity level of the alert (1-100, recommended when filtering by severity)
    confidence: Confidence level of the alert (1-100)
    agent_id: Agent ID associated with the alert

    Sort either asc (ascending) or desc (descending).
    Both formats are supported: 'severity.desc' or 'severity|desc'

    When searching for high severity alerts, use 'severity.desc' to get the highest severity alerts first.
    For chronological ordering, use 'timestamp.desc' for most recent alerts first.

    Examples: 'severity.desc', 'timestamp.desc'
""", examples={"severity.desc", "timestamp.desc"}),
        include_hidden: Optional[bool] = Field(default=True),
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        IMPORTANT: You must use the tool `falcon_search_detections_fql_filter_guide` whenever you want to use the `filter` parameter. This tool contains the guide on how to build the FQL `filter` parameter for `search_detections` tool.

        Returns:
            List of detection details
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "q": q,
            "sort": sort,
        })

        # Define the operation name
        operation = "GetQueriesAlertsV2"

        logger.debug("Searching detections with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get detection IDs (now composite_ids)
        detection_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search detections",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(detection_ids):
            return [detection_ids]

        # If we have detection IDs, get the details for each one
        if detection_ids:
            # Use the enhanced base method with composite_ids and include_hidden
            details = self._base_get_by_ids(
                operation="PostEntitiesAlertsV2",
                ids=detection_ids,
                id_key="composite_ids",
                include_hidden=include_hidden
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if self._is_error(details):
                return [details]

            return details

        return []

    def search_detections_fql_filter_guide(self) -> str:
        """
        Returns the guide for the `filter` param of the `falcon_search_detections` tool.

        IMPORTANT: Before running `falcon_search_detections`, always call this tool to get information about how to build the FQL for the filter.
        """
        return SEARCH_DETECTIONS_FQL_DOCUMENTATION

    def get_detection_details(
        self,
        ids: List[str] = Field(),
        include_hidden: Optional[bool] = Field(default=True),
    ) -> List[Dict[str, Any]]|Dict[str, Any]:
        """View information about detections. Gets detailed information about a specific detection.

        Args:
            ids: ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the search_detections operation, the Falcon console, or the Streaming API.
            include_hidden: Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.

        Returns:
            Detection details
        """
        logger.debug("Getting detection details for ID: %s", ids)

        # Use the enhanced base method - composite_ids parameter matches ids for backward compatibility
        return self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )
