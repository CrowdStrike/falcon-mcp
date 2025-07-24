# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Incidents module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon incidents.
"""

from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.incidents import (
    CROWD_SCORE_FQL_DOCUMENTATION,
    SEARCH_BEHAVIORS_FQL_DOCUMENTATION,
    SEARCH_INCIDENTS_FQL_DOCUMENTATION,
)


class IncidentsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon incidents."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(server, self.show_crowd_score, name="show_crowd_score")

        self._add_tool(server, self.search_incidents, name="search_incidents")

        self._add_tool(server, self.get_incident_details, name="get_incident_details")

        self._add_tool(server, self.search_behaviors, name="search_behaviors")

        self._add_tool(server, self.get_behavior_details, name="get_behavior_details")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        crowd_score_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/crowd-score/fql-guide"),
            name="falcon_show_crowd_score_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_show_crowd_score` tool.",
            text=CROWD_SCORE_FQL_DOCUMENTATION,
        )

        search_incidents_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/search/fql-guide"),
            name="falcon_search_incidents_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_incidents` tool.",
            text=SEARCH_INCIDENTS_FQL_DOCUMENTATION,
        )

        search_behaviors_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/behaviors/fql-guide"),
            name="falcon_search_behaviors_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_behaviors` tool.",
            text=SEARCH_BEHAVIORS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, crowd_score_fql_resource)
        self._add_resource(server, search_incidents_fql_resource)
        self._add_resource(server, search_behaviors_fql_resource)

    def show_crowd_score(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/crowd-score/fql-guide` resource when building this filter parameter.",
        ),
        limit: Optional[int] = Field(
            default=100,
            ge=1,
            le=2500,
            description="Maximum number of records to return. (Max: 2500)",
        ),
        offset: Optional[int] = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description="TThe property to sort by. (Ex: modified_timestamp.desc)",
            examples={"modified_timestamp.desc"},
        ),
    ) -> Dict[str, Any]:
        """View calculated CrowdScores and security posture metrics for your environment.

        IMPORTANT: You must use the `falcon://incidents/crowd-score/fql-guide` resource when you need to use the `filter` parameter. This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_show_crowd_score` tool.

        Returns:
            Tool returns the CrowdScore entity data.
        """
        # Prepare parameters
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Define the operation name (used for error handling)
        operation = "CrowdScore"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        api_response = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

        # Check if we received an error response
        if self._is_error(api_response):
            # Return the error response as is
            return api_response

        # Initialize result with all scores
        result = {
            "average_score": 0,
            "average_adjusted_score": 0,
            "scores": api_response,  # Include all the scores in the result
        }

        if api_response:  # If we have scores (list of score objects)
            score_sum = 0
            adjusted_score_sum = 0
            count = len(api_response)

            for item in api_response:
                score_sum += item.get("score", 0)
                adjusted_score_sum += item.get("adjusted_score", 0)

            if count > 0:
                # Round to ensure integer output
                result["average_score"] = round(score_sum / count)
                result["average_adjusted_score"] = round(adjusted_score_sum / count)

        return result

    def search_incidents(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of records to return. (Max: 500)",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description="The property to sort by. FQL syntax. Ex: state.asc, name.desc",
        ),
    ) -> List[Dict[str, Any]]:
        """Find and analyze security incidents to understand coordinated activity in your environment.

        IMPORTANT: You must use the `falcon://incidents/search/fql-guide` resource when you need to use the `filter` parameter. This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_incidents` tool.

        Returns:
            Tool returns CrowdStrike incidents.
        """
        incident_ids = self._base_query(
            operation="QueryIncidents",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(incident_ids):
            return [incident_ids]

        # If we have incident IDs, get the details for each one
        if incident_ids:
            return self.get_incident_details(incident_ids)

        return []

    def get_incident_details(
        self,
        ids: List[str] = Field(description="Incident ID(s) to retrieve."),
    ) -> List[Dict[str, Any]]:
        """Get comprehensive incident details to understand attack patterns and coordinated activities.

        This tool returns comprehensive incident details for one or more incident IDs.
        Use this when you already have specific incident IDs and need their full details.
        For searching/discovering incidents, use the `falcon_search_incidents` tool instead.

        Returns:
            List of incident details with comprehensive information including hosts,
            scores, behaviors, timeline, and associated metadata
        """
        incidents = self._base_get_by_ids(
            operation="GetIncidents",
            ids=ids,
        )

        if self._is_error(incidents):
            return [incidents]

        return incidents

    def search_behaviors(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/behaviors/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of records to return. (Max: 500)",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description="The property to sort by. (Ex: modified_timestamp.desc)",
        ),
    ) -> List[Dict[str, Any]]:
        """Find and analyze behaviors to understand suspicious activity in your environment.

        Use this when you need to find behaviors matching certain criteria rather than retrieving specific behaviors by ID.
        For retrieving details of known behavior IDs, use falcon_get_behavior_details instead.

        IMPORTANT: You must use the `falcon://incidents/behaviors/fql-guide` resource when you need to use the `filter` parameter. This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_behaviors` tool.

        Returns:
            Tool returns CrowdStrike behaviors.
        """
        behavior_ids = self._base_query(
            operation="QueryBehaviors",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(behavior_ids):
            return [behavior_ids]

        # If we have behavior IDs, get the details for each one
        if behavior_ids:
            return self.get_behavior_details(behavior_ids)

        return []

    def get_behavior_details(
        self,
        ids: List[str] = Field(description="Behavior ID(s) to retrieve."),
    ) -> List[Dict[str, Any]]:
        """Get detailed behavior information to understand attack techniques and tactics.

        Use this when you already know the specific behavior ID(s) and need to retrieve their details.
        For searching behaviors based on criteria, use the `falcon_search_behaviors` tool instead.

        Returns:
            List of behavior details with comprehensive information including techniques,
            tactics, severity, confidence levels, and associated metadata
        """
        behaviors = self._base_get_by_ids(
            operation="GetBehaviors",
            ids=ids,
        )

        if self._is_error(behaviors):
            return [behaviors]

        return behaviors

    def _base_query(
        self,
        operation: str,
        filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> List[str] | Dict[str, Any]:
        # Prepare parameters
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )
