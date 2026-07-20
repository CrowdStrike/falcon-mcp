"""
Spotlight module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon Spotlight vulnerabilities.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
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
            server=server,
            method=self.search_vulnerabilities,
            name="search_vulnerabilities",
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

        self._add_resource(
            server,
            search_vulnerabilities_fql_resource,
        )

    def search_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://spotlight/vulnerabilities/fql-guide` for syntax.",
            examples=["status:'open'", "cve.severity:'HIGH'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of results to return. (Max: 5000, Default: 10)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return results.",
        ),
        sort: str | None = Field(
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
            examples=[
                "created_timestamp|desc",
                "updated_timestamp|desc",
                "closed_timestamp|asc",
            ],
        ),
        after: str | None = Field(
            default=None,
            description="A pagination token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that place in the results.",
        ),
        facet: str | list[str] | None = Field(
            default=None,
            description=dedent("""
                Select one or more detail blocks to be returned for each vulnerability.

                Accepts a single value (e.g. 'cve') or a list of values
                (e.g. ['cve', 'host_info', 'remediation']) to retrieve multiple
                detail blocks in a single request.

                Supported values:
                • host_info: Include host/asset information and context
                • remediation: Include remediation and fix information
                • cve: Include CVE details, scoring, and metadata
                • evaluation_logic: Include vulnerability assessment methodology

                Use host_info when you need asset context, remediation for fix information,
                cve for detailed vulnerability scoring, and evaluation_logic for assessment details.

                Examples: 'cve', ['cve', 'host_info'], ['cve', 'host_info', 'remediation', 'evaluation_logic']
            """).strip(),
            examples=["cve", ["cve", "host_info"], ["cve", "host_info", "remediation", "evaluation_logic"]],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for vulnerabilities in your CrowdStrike environment.

        Use this to find vulnerabilities by CVE severity, status, host, or remediation
        state. Consult falcon://spotlight/vulnerabilities/fql-guide before constructing
        filter expressions. Returns vulnerability details including CVE info, host context,
        and remediation guidance (based on facet selection).
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions. For cursor-based paging, use `pagination.next` as the `after` parameter on the next call.
        """
        vulnerabilities, pagination = self._base_search_with_meta(
            operation="combinedQueryVulnerabilities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
                "facet": facet,
            },
            error_message="Failed to search vulnerabilities",
        )

        if self._is_error(vulnerabilities):
            return [vulnerabilities]

        return self._build_pagination_envelope(vulnerabilities or [], pagination, filter)
