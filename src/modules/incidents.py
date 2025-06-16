"""
Incidents module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon incidents.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_first_resource
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
            name="incidents_crowd_score",
            description="Query environment wide CrowdScore and return the entity data."
        )

        self._add_tool(
            server,
            self.get_incidents,
            name="incidents_get_incidents",
            description="Get details on incidents by providing incident IDs."
        )

        self._add_tool(
            server,
            self.query_incidents,
            name="incidents_query_incidents",
            description="Search for incidents by providing a FQL filter, sorting, and paging details."
        )

        self._add_tool(
            server,
            self.get_behaviors,
            name="incidents_get_behaviors",
            description="Get details on behaviors by providing behavior IDs."
        )

        self._add_tool(
            server,
            self.query_behaviors,
            name="incidents_query_behaviors",
            description="Search for behaviors by providing a FQL filter, sorting, and paging details."
        )


    def crowd_score(self, query: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None) -> Dict[str, Any]:
        """Query environment wide CrowdScore and return the entity data.

        Args:
            query: FQL Syntax formatted string used to limit the results.
            limit: Maximum number of records to return. Max 2500.
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: modified_timestamp.desc)

        Returns:
            Tool returns the CrowdScore entity data.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "query": query,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Define the operation name (used for error handling)
        operation = "CrowdScore"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )


    def get_incidents(self, ids: List[str]) -> Dict[str, Any]:
        """Get details on incidents by providing incident IDs.

        Args:
            ids: Incident ID(s) to retrieve.

        Returns:
            Tool returns the CrowdScore entity data.
        """
        self._base_get(
            operation="GetIncidents",
            ids=ids,
        )

    def query_incidents(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for incidents by providing a FQL filter, sorting, and paging details.

        Args:
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. FQL syntax. Ex: state.asc, name.desc
                    Available sort fields:
                    assigned_to                 sort_score
                    assigned_to_name            start
                    end                         state
                    modified_timestamp          status
                    name

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
        self._base_query(
            operation="QueryIncidents",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_behaviors(self, ids: List[str]) -> Dict[str, Any]:
        """Get details on behaviors by providing behavior IDs.

        Args:
            ids: Behavior ID(s) to retrieve.

        Returns:
            Tool returns the CrowdScore behaviors by ID.
        """
        self._base_get(
            operation="GetBehaviors",
            ids=ids,
        )


    def query_behaviors(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for behaviors by providing a FQL filter, sorting, and paging details.

        Args:
            filter: FQL Syntax formatted string used to limit the results.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. (Ex: modified_timestamp.desc)


        Returns:
            Tool returns CrowdStrike behaviors.
        """
        self._base_query(
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


    def _base_get(
        self, operation: str, ids: List[str],
    ) -> Dict[str, Any]:
        body = prepare_api_parameters({
            "ids": ids
        })

        # Make the API request
        response = self.client.command(operation, body=body)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )
