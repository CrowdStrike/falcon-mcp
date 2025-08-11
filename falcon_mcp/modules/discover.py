"""
Discover module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon Discover applications.
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
from falcon_mcp.resources.discover import SEARCH_APPLICATIONS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class DiscoverModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon Discover applications."""

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

        self._add_resource(
            server,
            search_applications_fql_resource,
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
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of items to return: 1-1000. Default is 100. Use with the after parameter to manage pagination of results.",
        ),
        after: str | None = Field(
            default=None,
            description="Token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that place in the results. Tokens expire 120 seconds after a call is made.",
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
                "after": after,
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
