"""
Sensor Usage module for Falcon MCP Server

This module provides tools for accessing CrowdStrike Falcon sensor usage data.
"""

from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.sensor_usage import SEARCH_SENSOR_USAGE_FQL_DOCUMENTATION

logger = get_logger(__name__)


class SensorUsageModule(BaseModule):
    """Module for accessing CrowdStrike Falcon sensor usage data."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server=server,
            method=self.search_sensor_usage,
            name="search_sensor_usage",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_sensor_usage_fql_resource = TextResource(
            uri=AnyUrl("falcon://sensor-usage/weekly/fql-guide"),
            name="falcon_search_sensor_usage_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_sensor_usage` tool.",
            text=SEARCH_SENSOR_USAGE_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_sensor_usage_fql_resource,
        )

    def search_sensor_usage(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://sensor-usage/weekly/fql-guide` resource when building this filter parameter.",
            examples={"event_date:'2024-06-11'", "period:'30'"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for sensor usage data in your CrowdStrike environment.

        IMPORTANT: You must use the `falcon://sensor-usage/weekly/fql-guide` resource when you need to use the `filter` parameter. This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_sensor_usage` tool.

        Returns:
            List of sensor usage details
        """
        # Prepare parameters for GetSensorUsageWeekly
        params = prepare_api_parameters(
            {
                "filter": filter,
            }
        )

        # Define the operation name
        operation = "GetSensorUsageWeekly"

        logger.debug("Searching sensor usage with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get the results
        results = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search sensor usage",
            default_result=[],
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(results):
            return [results]

        return results
