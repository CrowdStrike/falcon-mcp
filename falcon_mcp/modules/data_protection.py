"""
Data Protection module for Falcon MCP Server.

Provides read-only access to Data Protection configuration data —
classifications, policies, and content patterns — so an LLM can reason about why
a Data Protection detection fired.

For Data Protection detections, use falcon_search_detections with
product:'data-protection'. For EDD scan results, use falcon_search_ngsiem with
#event_simpleName=Event_DataProtectionClassifiedFileEvent.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.data_protection import (
    SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION,
    SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION,
    SEARCH_POLICIES_FQL_DOCUMENTATION,
)


class DataProtectionModule(BaseModule):
    """CrowdStrike Data Protection configuration module.

    Read-only access to Data Protection rule definitions — classifications,
    policies, and content patterns.

    Required API Scopes:
    - Data Protection:read
    """

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_data_protection_classifications,
            name="search_data_protection_classifications",
        )
        self._add_tool(
            server=server,
            method=self.search_data_protection_policies,
            name="search_data_protection_policies",
        )
        self._add_tool(
            server=server,
            method=self.search_data_protection_content_patterns,
            name="search_data_protection_content_patterns",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        classifications_fql_resource = TextResource(
            uri=AnyUrl("falcon://data-protection/classifications/fql-guide"),
            name="falcon_search_data_protection_classifications_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_data_protection_classifications` tool.",
            text=SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION,
        )
        policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://data-protection/policies/fql-guide"),
            name="falcon_search_data_protection_policies_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_data_protection_policies` tool.",
            text=SEARCH_POLICIES_FQL_DOCUMENTATION,
        )
        content_patterns_fql_resource = TextResource(
            uri=AnyUrl("falcon://data-protection/content-patterns/fql-guide"),
            name="falcon_search_data_protection_content_patterns_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_data_protection_content_patterns` tool.",
            text=SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, classifications_fql_resource)
        self._add_resource(server, policies_fql_resource)
        self._add_resource(server, content_patterns_fql_resource)

    def search_data_protection_classifications(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://data-protection/classifications/fql-guide` for syntax.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of records to return.",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Pagination offset.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort order. Ex: name.asc, created_at.desc, modified_at.desc",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for Data Protection classifications in your CrowdStrike environment.

        Use this to find classification rules that define what sensitive data
        patterns to detect. Consult
        falcon://data-protection/classifications/fql-guide before constructing
        filter expressions. Returns full classification details including content
        pattern references and rule configuration.
        """
        ids = self._base_search_api_call(
            operation="queries_classification_get_v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Data Protection classifications",
            default_result=[],
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_empty_response(filter)

        return self._base_get_by_ids(
            "entities_classification_get_v2", ids, use_params=True
        )

    def search_data_protection_policies(
        self,
        platform_name: str = Field(
            description="Required. Platform to query: 'win' or 'mac'.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://data-protection/policies/fql-guide` for syntax.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of records to return.",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Pagination offset.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort order. Ex: name.asc, precedence.asc, created_at.desc",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for Data Protection policies in your CrowdStrike environment.

        Use this to find data protection policies by platform, enablement status,
        or precedence. Requires a platform_name ('win' or 'mac'). Consult
        falcon://data-protection/policies/fql-guide before constructing filter
        expressions. Returns full policy details including host groups and
        classification assignments.
        """
        ids = self._base_search_api_call(
            operation="queries_policy_get_v2",
            search_params={
                "platform_name": platform_name,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Data Protection policies",
            default_result=[],
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_POLICIES_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_empty_response(filter)

        return self._base_get_by_ids("entities_policy_get_v2", ids, use_params=True)

    def search_data_protection_content_patterns(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://data-protection/content-patterns/fql-guide` for syntax.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of records to return.",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Pagination offset.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort order. Ex: name.asc, category.asc, region.asc",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for Data Protection content patterns in your CrowdStrike environment.

        Use this to find regex-based content detection patterns by type, category,
        or region. Consult falcon://data-protection/content-patterns/fql-guide
        before constructing filter expressions. Returns full pattern details
        including regex definitions and match thresholds.
        """
        ids = self._base_search_api_call(
            operation="queries_content_pattern_get_v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Data Protection content patterns",
            default_result=[],
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_empty_response(filter)

        return self._base_get_by_ids("entities_content_pattern_get", ids, use_params=True)
