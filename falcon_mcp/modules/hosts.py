# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Hosts module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon hosts/devices.
"""
from typing import Dict, List, Optional, Any
from textwrap import dedent

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.resources.hosts import SEARCH_HOSTS_FQL_DOCUMENTATION
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class HostsModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon hosts/devices."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.search_hosts,
            name="search_hosts"
        )

        self._add_tool(
            server,
            self.search_hosts_fql_filter_guide,
            name="search_hosts_fql_filter_guide"
        )

        self._add_tool(
            server,
            self.get_host_details,
            name="get_host_details"
        )

    def search_hosts(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_search_hosts_fql_filter_guide` tool when building this filter parameter.", examples={"platform_name:'Windows'", "hostname:'PC*'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=5000, description="The maximum records to return. [1-5000]"),
        offset: Optional[int] = Field(default=0, ge=0, description="The offset to start retrieving records from."),
        sort: Optional[str] = Field(
            default=None,
            description=dedent("""
                Sort hosts using these options:

                hostname: Host name/computer name
                last_seen: Timestamp when the host was last seen
                first_seen: Timestamp when the host was first seen
                modified_timestamp: When the host record was last modified
                platform_name: Operating system platform
                agent_version: CrowdStrike agent version
                os_version: Operating system version
                external_ip: External IP address

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'hostname.desc' or 'hostname|desc'

                Examples: 'hostname.asc', 'last_seen.desc', 'platform_name.asc'
            """).strip(),
            examples={"hostname.asc", "last_seen.desc"}
        ),
    ) -> List[Dict[str, Any]]:
        """Search for hosts in your CrowdStrike environment.

        IMPORTANT: You must use the tool `falcon_search_hosts_fql_filter_guide` whenever you want to use the `filter` parameter. This tool contains the guide on how to build the FQL `filter` parameter for `search_hosts` tool.

        Returns:
            List of host details
        """
        # Prepare parameters for QueryDevicesByFilter
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Define the operation name
        operation = "QueryDevicesByFilter"

        logger.debug("Searching hosts with params: %s", params)

        # Make the API request to get device IDs
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get device IDs
        device_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search hosts",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(device_ids):
            return [device_ids]

        # If we have device IDs, get the details for each one
        if device_ids:
            # Use the base method to get device details
            details = self._base_get_by_ids(
                operation="PostDeviceDetailsV2",
                ids=device_ids,
                id_key="ids"
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if self._is_error(details):
                return [details]

            return details

        return []

    def search_hosts_fql_filter_guide(self) -> str:
        """
        Returns the guide for the `filter` param of the `falcon_search_hosts` tool.

        IMPORTANT: Before running `falcon_search_hosts`, always call this tool to get information about how to build the FQL for the filter.
        """
        return SEARCH_HOSTS_FQL_DOCUMENTATION

    def get_host_details(
        self,
        ids: List[str] = Field(description="Host device IDs to retrieve details for. You can get device IDs from the search_hosts operation, the Falcon console, or the Streaming API. Maximum: 5000 IDs per request."),
    ) -> List[Dict[str, Any]]|Dict[str, Any]:
        """Retrieve detailed information for specified host device IDs.

        This tool returns comprehensive host details for one or more device IDs.
        Use this when you already have specific device IDs and need their full details.
        For searching/discovering hosts, use the `falcon_search_hosts` tool instead.

        Returns:
            List of host details with comprehensive information including system specs,
            agent information, network details, and security status
        """
        logger.debug("Getting host details for IDs: %s", ids)

        # Handle empty list case - return empty list without making API call
        if not ids:
            return []

        # Use the base method to get device details
        return self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=ids,
            id_key="ids"
        )
