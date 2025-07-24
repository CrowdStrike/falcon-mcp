# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Spotlight module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon Spotlight vulnerabilities.
"""

from textwrap import dedent
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.spotlight import SEARCH_VULNERABILITIES_FQL_DOCUMENTATION

logger = get_logger(__name__)


class SpotlightModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon Spotlight vulnerabilities."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server, self.search_vulnerabilities, name="search_vulnerabilities"
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_vulnerabilities_fql_resource = TextResource(
            uri=AnyUrl("falcon://spotlight/vulnerabilities/fql-guide"),
            name="falcon_search_vulnerabilities_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_vulnerabilities` tool.",
            text=SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_vulnerabilities_fql_resource)

    def search_vulnerabilities(
        self,
        filter: str = Field(
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://spotlight/vulnerabilities/fql-guide` resource when building this filter parameter.",
            examples={"status:'open'", "cve.severity:'HIGH'"},
        ),
        limit: Optional[int] = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of results to return. (Max: 5000, Default: 100)",
        ),
        offset: Optional[int] = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return results.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description=dedent("""
                Sort vulnerabilities using FQL syntax.

                Supported sorting fields:
                • created_timestamp: When the vulnerability was found
                • closed_timestamp: When the vulnerability was closed
                • updated_timestamp: When the vulnerability was last updated

                Sort either asc (ascending) or desc (descending).
                Format: 'field|direction'

                Examples: 'created_timestamp|desc', 'updated_timestamp|desc', 'closed_timestamp|asc'
            """).strip(),
            examples={
                "created_timestamp|desc",
                "updated_timestamp|desc",
                "closed_timestamp|asc",
            },
        ),
        after: Optional[str] = Field(
            default=None,
            description="A pagination token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that place in the results.",
        ),
        facet: Optional[str] = Field(
            default=None,
            description=dedent("""
                Important: Use only one value!

                Select various detail blocks to be returned for each vulnerability.

                Supported values:
                • host_info: Include host/asset information and context
                • remediation: Include remediation and fix information
                • cve: Include CVE details, scoring, and metadata
                • evaluation_logic: Include vulnerability assessment methodology

                Use host_info when you need asset context, remediation for fix information,
                cve for detailed vulnerability scoring, and evaluation_logic for assessment details.

                Examples: 'host_info', 'cve', 'remediation'
            """).strip(),
            examples={"host_info", "cve", "remediation", "evaluation_logic"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for vulnerabilities in your CrowdStrike environment.

        IMPORTANT: You must use the `falcon://spotlight/vulnerabilities/fql-guide` resource when you need to use the `filter` parameter. This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_vulnerabilities` tool.

        Returns:
            List of vulnerability details with comprehensive information including CVE data,
            host information, remediation details, and security assessments
        """
        # Prepare parameters for combinedQueryVulnerabilities
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
                "facet": facet,
            }
        )

        # Define the operation name
        operation = "combinedQueryVulnerabilities"

        logger.debug("Searching vulnerabilities with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get vulnerability data
        vulnerabilities = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search vulnerabilities",
            default_result=[],
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(vulnerabilities):
            return [vulnerabilities]

        return vulnerabilities
