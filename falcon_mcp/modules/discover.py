"""
Discover module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets.
"""

from textwrap import dedent
from typing import Any, Dict, List

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.common.constants import SearchLimits
from falcon_mcp.resources.discover import (
    SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
    SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class DiscoverModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server=server,
            method=self.search_applications,
            name="search_applications",
        )

        self._add_tool(
            server=server,
            method=self.search_unmanaged_assets,
            name="search_unmanaged_assets",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_applications_fql_resource = TextResource(
            uri=AnyUrl("falcon://discover/applications/fql-guide"),
            name="falcon_search_applications_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_applications` tool.",
            text=SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
        )

        search_unmanaged_assets_fql_resource = TextResource(
            uri=AnyUrl("falcon://discover/hosts/fql-guide"),
            name="falcon_search_unmanaged_assets_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.",
            text=SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_applications_fql_resource,
        )

        self._add_resource(
            server,
            search_unmanaged_assets_fql_resource,
        )

    def search_applications(
        self,
        filter: str = Field(
            description="FQL filter expression used to limit the results. IMPORTANT: use the `falcon://discover/applications/fql-guide` resource when building this filter parameter.",
            examples={"name:'Chrome'", "vendor:'Microsoft Corporation'"},
        ),
        facet: str | None = Field(
            default=None,
            description=dedent("""
                Type of data to be returned for each application entity. The facet filter allows you to limit the response to just the information you want.

                Possible values:
                • browser_extension
                • host_info
                • install_usage

                Note: Requests that do not include the host_info or browser_extension facets still return host.ID, browser_extension.ID, and browser_extension.enabled in the response.
            """).strip(),
            examples={"browser_extension", "host_info", "install_usage"},
        ),
        limit: int = Field(
            default=SearchLimits.DEFAULT_DISCOVER,
            ge=1,
            le=SearchLimits.MAX_DISCOVER_APPS,
            description="Maximum number of items to return: 1-1000. Default is 100.",
        ),
        sort: str | None = Field(
            default=None,
            description="Property used to sort the results. All properties can be used to sort unless otherwise noted in their property descriptions.",
            examples={"name.asc", "vendor.desc", "last_updated_timestamp.desc"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for applications in your CrowdStrike environment.

        IMPORTANT: You must use the `falcon://discover/applications/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_applications` tool.
        """
        # Prepare parameters for combined_applications
        params = prepare_api_parameters(
            {
                "filter": filter,
                "facet": facet,
                "limit": limit,
                "sort": sort,
            }
        )

        # Define the operation name
        operation = "combined_applications"

        logger.debug("Searching applications with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get application data
        applications = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search applications",
            default_result=[],
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(applications):
            return [applications]

        return applications

    def search_unmanaged_assets(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit the results. IMPORTANT: use the `falcon://discover/hosts/fql-guide` resource when building this filter parameter. Note: entity_type:'unmanaged' is automatically applied.",
            examples={"platform_name:'Windows'", "criticality:'Critical'"},
        ),
        limit: int = Field(
            default=SearchLimits.DEFAULT_DISCOVER,
            ge=1,
            le=SearchLimits.MAX_HOSTS,
            description="Maximum number of items to return: 1-5000. Default is 100.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return results.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort unmanaged assets using these options:

                hostname: Host name/computer name
                last_seen_timestamp: Timestamp when the asset was last seen
                first_seen_timestamp: Timestamp when the asset was first seen
                platform_name: Operating system platform
                os_version: Operating system version
                external_ip: External IP address
                country: Country location
                criticality: Criticality level

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'hostname.desc' or 'hostname|desc'

                Examples: 'hostname.asc', 'last_seen_timestamp.desc', 'criticality.desc'
            """).strip(),
            examples={"hostname.asc", "last_seen_timestamp.desc", "criticality.desc"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for unmanaged assets (hosts) in your CrowdStrike environment.

        These are systems that do not have the Falcon sensor installed but have been
        discovered by systems that do have a Falcon sensor installed.

        IMPORTANT: You must use the `falcon://discover/hosts/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_unmanaged_assets` tool.

        The tool automatically filters for unmanaged assets only by adding entity_type:'unmanaged' to all queries.
        You do not need to (and cannot) specify entity_type in your filter - it is always set to 'unmanaged'.
        """
        # Always enforce entity_type:'unmanaged' filter
        base_filter = "entity_type:'unmanaged'"

        # Combine with user filter if provided
        if filter:
            combined_filter = f"{base_filter}+{filter}"
        else:
            combined_filter = base_filter

        # Prepare parameters for combined_hosts
        params = prepare_api_parameters(
            {
                "filter": combined_filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Define the operation name
        operation = "combined_hosts"

        logger.debug("Searching unmanaged assets with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get unmanaged asset data
        assets = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search unmanaged assets",
            default_result=[],
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(assets):
            return [assets]

        return assets
