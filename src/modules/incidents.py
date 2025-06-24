# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Incidents module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon incidents.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
from .base import BaseModule


class IncidentsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon incidents."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.crowd_score,
            name="show_crowd_score"
        )

        self._add_tool(
            server,
            self.get_incidents,
            name="get_incident_details"
        )

        self._add_tool(
            server,
            self.query_incidents,
            name="search_incidents"
        )

        self._add_tool(
            server,
            self.get_behaviors,
            name="get_behavior_details"
        )

        self._add_tool(
            server,
            self.query_behaviors,
            name="search_behaviors"
        )

    def crowd_score(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results."),
        limit: Optional[int] = Field(default=100, ge=1, le=2500, description="Maximum number of records to return. (Max: 2500)"),
        offset: Optional[int] = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="TThe property to sort by. (Ex: modified_timestamp.desc)", examples={"modified_timestamp.desc"}),
    ) -> Dict[str, Any]:
        """Query environment wide CrowdScore and return the entity data.

        Args:
            filter: FQL Syntax formatted string used to limit the results.
            limit: Maximum number of records to return. (Max: 2500)
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: modified_timestamp.desc)

        Returns:
            Tool returns the CrowdScore entity data.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Define the operation name (used for error handling)
        operation = "CrowdScore"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        api_response = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )

        # Check if we received an error response
        if isinstance(api_response, dict) and "error" in api_response:
            # Return the error response as is
            return api_response

        # Initialize result with all scores
        result = {
            "average_score": 0,
            "average_adjusted_score": 0,
            "scores": api_response  # Include all the scores in the result
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

    def get_incidents(
        self,
        ids: List[str] = Field(description="Incident ID(s) to retrieve."),
    ) -> Dict[str, Any]:
        """Get details on incidents by providing incident IDs.

        Args:
            ids: Incident ID(s) to retrieve.

        Returns:
            Tool returns the CrowdScore entity data.
        """
        return self._base_get_by_ids(
            operation="GetIncidents",
            ids=ids,
        )

    def query_incidents(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results. Review the following table for a complete list of available filters."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum number of records to return. (Max: 500)"),
        offset: int = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="The property to sort by. FQL syntax. Ex: state.asc, name.desc"),
    ) -> Dict[str, Any]:
        """Search for incidents by providing a FQL filter, sorting, and paging details.

        Args:
            filter: FQL Syntax formatted string used to limit the results. Review the following table for a complete list of available filters.
            limit: Maximum number of records to return. (Max: 500)
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: modified_timestamp.desc)

        For more detail regarding filters and their usage, please review the Falcon Query Language documentation.

        Available filters:
            host_ids: The device IDs of all the hosts on which the incident occurred. Example: `9a07d39f8c9f430eb3e474d1a0c16ce9`
            lm_host_ids: If lateral movement has occurred, this field shows the remote device IDs of the hosts on which the lateral movement occurred. Example: `c4e9e4643999495da6958ea9f21ee597`
            lm_hosts_capped: Indicates that the list of lateral movement hosts has been truncated. The limit is 15 hosts. Example: `True`
            name: The name of the incident. Initially the name is assigned by CrowdScore, but it can be updated through the API. Example: `Incident on DESKTOP-27LTE3R at 2019-12-20T19:56:16Z`
            description: The description of the incident. Initially the description is assigned by CrowdScore, but it can be updated through the API. Example: `Objectives in this incident: Keep Access. Techniques: Masquerading. Involved hosts and end users: DESKTOP-27LTE3R, DESKTOP-27LTE3R$.`
            users: The usernames of the accounts associated with the incident. Example: `someuser`
            tags: Tags associated with the incident. CrowdScore will assign an initial set of tags, but tags can be added or removed through the API. Example: `Objective/Keep Access`
            final_score: The incident score. Divide the integer by 10 to match the displayed score for the incident. Example: `56`
            start: The recorded time of the earliest behavior. Example: 2017-01-31T22:36:11Z
            end: The recorded time of the latest behavior. Example: 2017-01-31T22:36:11Z
            assigned_to_name: The name of the user the incident is assigned to.
            state: The incident state: "open" or "closed". Example: `open`
            status: The incident status as a number: 20: New, 25: Reopened, 30: In Progress, 40: Closed. Example: `20`
            modified_timestamp: The most recent time a user has updated the incident. Example: `2021-02-04T05:57:04Z`

        Returns:
            Tool returns CrowdStrike incidents.
        """
        return self._base_query(
            operation="QueryIncidents",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_behaviors(
        self,
        ids: List[str] = Field(description="Behavior ID(s) to retrieve."),
    ) -> Dict[str, Any]:
        """Get details on behaviors by providing behavior IDs.

        Args:
            ids: Behavior ID(s) to retrieve.

        Returns:
            Tool returns the CrowdScore behaviors by ID.
        """
        return self._base_get_by_ids(
            operation="GetBehaviors",
            ids=ids,
        )


    def query_behaviors(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum number of records to return. (Max: 500)"),
        offset: int = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="The property to sort by. (Ex: modified_timestamp.desc)"),
    ) -> Dict[str, Any]:
        """Search for behaviors by providing a FQL filter, sorting, and paging details.

        Args:
            filter: FQL Syntax formatted string used to limit the results.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: modified_timestamp.desc)


        Returns:
            Tool returns CrowdStrike behaviors.
        """
        return self._base_query(
            operation="QueryBehaviors",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def _base_query(
        self, operation: str, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )
