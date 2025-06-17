"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_first_resource
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
            name="detects_query_detects"
        )

        self._add_tool(
            server,
            self.get_detection_details,
            name="detects_get_detect_summaries"
        )

        self._add_tool(
            server,
            self.get_detection_count,
            name="get_detection_count"
        )

    def search_detections(
        self,
        filter: Optional[str] = Field(default=None, description="Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results."), 
        limit: Optional[int] = Field(default=100, min=1, max=9999, description="The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results."),
        offset: Optional[int] = Field(default=0, min=0, description="The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results."),
        q: Optional[str] = Field(default=None, description="Search all detection metadata for the provided string."), 
        sort: Optional[str] = Field(default=None, description="""Sort detections using these options:

    first_behavior: Timestamp of the first behavior associated with this detection last_behavior: Timestamp of the last behavior associated with this detection
    max_severity: Highest severity of the behaviors associated with this detection
    max_confidence: Highest confidence of the behaviors associated with this detection
    adversary_id: ID of the adversary associated with this detection, if any
    devices.hostname: Hostname of the host where this detection was detected
    Sort either asc (ascending) or desc (descending).

    For example: last_behavior|asc""", examples={"last_behavior|asc"}),
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        Args:
            filter: Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results.
            limit: The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.
            offset: The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results.
            q: Search all detection metadata for the provided string.
            sort: Sort detections using these options:
                first_behavior: Timestamp of the first behavior associated with this detection last_behavior: Timestamp of the last behavior associated with this detection
                max_severity: Highest severity of the behaviors associated with this detection
                max_confidence: Highest confidence of the behaviors associated with this detection
                adversary_id: ID of the adversary associated with this detection, if any
                devices.hostname: Hostname of the host where this detection was detected
                Sort either asc (ascending) or desc (descending).

                For example: last_behavior|asc

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
        operation = "QueryDetects"

        logger.debug("Searching detections with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get detection IDs
        detection_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search detections",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if isinstance(detection_ids, dict) and "error" in detection_ids:
            return [detection_ids]

        # If we have detection IDs, get the details for each one
        if detection_ids:
            details_operation = "GetDetectSummaries"
            details_response = self.client.command(
                details_operation,
                body={"ids": detection_ids}
            )

            # Use handle_api_response for the details response
            details = handle_api_response(
                details_response,
                operation=details_operation,
                error_message="Failed to get detection details",
                default_result=[]
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if isinstance(details, dict) and "error" in details:
                return [details]

            return details

        return []

    def get_detection_details(
        self,
        ids: List[str] = Field(description="ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the QueryDetects operation, the Falcon console, or the Streaming API."),
    ) -> Dict[str, Any]:
        """View information about detections. Gets detailed information about a specific detection.

        Args:
            ids: ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the QueryDetects operation, the Falcon console, or the Streaming API.

        Returns:
            Detection details
        """
        # Define the operation name
        operation = "GetDetectSummaries"

        logger.debug("Getting detection details for ID: %s", ids)

        return self._base_get_by_ids(
            operation=operation,
            ids=ids,
        )
