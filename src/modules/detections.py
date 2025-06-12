"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

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
            name="search_detections",
            description="Search for detections in your CrowdStrike environment."
        )

        self._add_tool(
            server,
            self.get_detection_details,
            name="get_detection_details",
            description="Get detailed information about a specific detection."
        )

        self._add_tool(
            server,
            self.get_detection_count,
            name="get_detection_count",
            description="Get the count of detections matching a query."
        )

    def search_detections(
        self, query: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        Args:
            query: FQL query string to filter detections
            limit: Maximum number of results to return

        Returns:
            List of detection details
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": query,
            "limit": limit
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

    def get_detection_details(self, detection_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific detection.

        Args:
            detection_id: The ID of the detection to retrieve

        Returns:
            Detection details
        """
        # Define the operation name
        operation = "GetDetectSummaries"

        logger.debug("Getting detection details for ID: %s", detection_id)

        # Make the API request
        response = self.client.command(
            operation,
            body={"ids": [detection_id]}
        )

        # Extract the first resource
        return extract_first_resource(
            response,
            operation=operation,
            not_found_error="Detection not found"
        )

    def get_detection_count(self, query: Optional[str] = None) -> Dict[str, int]:
        """Get the count of detections matching a query.

        Args:
            query: FQL query string to filter detections

        Returns:
            Dictionary with detection count
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": query
        })

        # Define the operation name
        operation = "QueryDetects"

        logger.debug("Getting detection count with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get detection IDs
        detection_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to get detection count",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it with a count of 0
        if isinstance(detection_ids, dict) and "error" in detection_ids:
            return {"count": 0, **detection_ids}

        return {"count": len(detection_ids)}
