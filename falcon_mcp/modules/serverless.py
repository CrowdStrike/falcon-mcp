"""
Serverless Vulnerabilities module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon Serverless Vulnerabilities.
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
from falcon_mcp.resources.serverless import SERVERLESS_VULNERABILITIES_FQL_DOCUMENTATION

logger = get_logger(__name__)


class ServerlessModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon Serverless Vulnerabilities."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server=server,
            method=self.search_serverless_vulnerabilities,
            name="search_serverless_vulnerabilities",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        serverless_vulnerabilities_fql_resource = TextResource(
            uri=AnyUrl("falcon://serverless/vulnerabilities/fql-guide"),
            name="falcon_serverless_vulnerabilities_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_serverless_vulnerabilities` tool.",
            text=SERVERLESS_VULNERABILITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            serverless_vulnerabilities_fql_resource,
        )

    def search_serverless_vulnerabilities(
        self,
        filter: str = Field(
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://serverless/vulnerabilities/fql-guide` resource when building this filter parameter.",
            examples={"cloud_provider:'AWS'", "severity:'HIGH'"},
        ),
        limit: int | None = Field(
            default=10,
            ge=1,
            description="The upper-bound on the number of records to retrieve. (Default: 10)",
        ),
        offset: int | None = Field(
            default=0,
            description="The offset from where to begin.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort serverless vulnerabilities using FQL syntax.

                Supported sorting fields:
                • application_name: Name of the application
                • application_name_version: Version of the application
                • cid: Customer ID
                • cloud_account_id: Cloud account ID
                • cloud_account_name: Cloud account name
                • cloud_provider: Cloud provider
                • cve_id: CVE ID
                • cvss_base_score: CVSS base score
                • exprt_rating: ExPRT rating
                • first_seen_timestamp: When the vulnerability was first seen
                • function_resource_id: Function resource ID
                • is_supported: Whether the function is supported
                • layer: Layer where the vulnerability was found
                • region: Cloud region
                • runtime: Runtime environment
                • severity: Severity level
                • timestamp: When the vulnerability was last updated
                • type: Type of vulnerability

                Format: 'field'

                Examples: 'severity', 'cloud_provider', 'first_seen_timestamp'
            """).strip(),
            examples={
                "severity",
                "cloud_provider",
                "first_seen_timestamp",
            },
        ),
    ) -> List[Dict[str, Any]]:
        """Search for vulnerabilities in your serverless functions across all cloud service providers.

        This endpoint provides security information in SARIF format, including:
        - CVE IDs for identified vulnerabilities
        - Severity levels
        - Vulnerability descriptions
        - Additional relevant details

        IMPORTANT: You must use the `falcon://serverless/vulnerabilities/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_serverless_vulnerabilities` tool.
        """
        # Prepare parameters for GetCombinedVulnerabilitiesSARIF
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Define the operation name
        operation = "GetCombinedVulnerabilitiesSARIF"

        logger.debug("Searching serverless vulnerabilities with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get vulnerability data
        vulnerabilities = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search serverless vulnerabilities",
            default_result=[],
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(vulnerabilities) or ("runs" not in vulnerabilities):
            return [vulnerabilities]

        return vulnerabilities["runs"] or []
