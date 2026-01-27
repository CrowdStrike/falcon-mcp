"""
Intel module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon intelligence data.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.intel import (
    QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION,
    QUERY_INDICATOR_ENTITIES_FQL_DOCUMENTATION,
    QUERY_REPORT_ENTITIES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class IntelModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon intelligence data."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server=server,
            method=self.query_actor_entities,
            name="search_actors",
        )

        self._add_tool(
            server=server,
            method=self.query_indicator_entities,
            name="search_indicators",
        )

        self._add_tool(
            server=server,
            method=self.query_report_entities,
            name="search_reports",
        )

        self._add_tool(
            server=server,
            method=self.get_mitre_report,
            name="get_mitre_report",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_actors_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/actors/fql-guide"),
            name="falcon_search_actors_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_actors` tool.",
            text=QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION,
        )

        search_indicators_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/indicators/fql-guide"),
            name="falcon_search_indicators_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_indicators` tool.",
            text=QUERY_INDICATOR_ENTITIES_FQL_DOCUMENTATION,
        )

        search_reports_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/reports/fql-guide"),
            name="falcon_search_reports_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_reports` tool.",
            text=QUERY_REPORT_ENTITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_actors_fql_resource,
        )
        self._add_resource(
            server,
            search_indicators_fql_resource,
        )
        self._add_resource(
            server,
            search_reports_fql_resource,
        )

    def query_actor_entities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression that should be used to limit the results. IMPORTANT: use the `falcon://intel/actors/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of records to return. Max 5000",
            examples={10, 20, 100},
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
            examples=[0, 10],
        ),
        sort: str | None = Field(
            default=None,
            description="The field and direction to sort results on. The format is {field}|{asc/desc}. Valid values include: name, target_countries, target_industries, type, created_date, last_activity_date and last_modified_date. Ex: created_date|desc",
            examples={"created_date|desc"},
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all indexed fields.",
            examples={"BEAR"},
        ),
    ) -> list[dict[str, Any]]:
        """Research threat actors and adversary groups tracked by CrowdStrike intelligence.

        IMPORTANT: You must use the `falcon://intel/actors/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_actors` tool.
        """
        api_response = self._base_search_api_call(
            operation="QueryIntelActorEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search actors",
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def query_indicator_entities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression that should be used to limit the results. IMPORTANT: use the `falcon://intel/indicators/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of records to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: str | None = Field(
            default=None,
            description="The field and direction to sort results on. The format is {field}|{asc/desc}. Valid values are: id, indicator, type, published_date, last_updated, and _marker. Ex: published_date|desc",
            examples={"published_date|desc"},
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all indexed fields.",
        ),
        include_deleted: bool = Field(
            default=False,
            description="Flag indicating if both published and deleted indicators should be returned.",
        ),
        include_relations: bool = Field(
            default=False,
            description="Flag indicating if related indicators should be returned.",
        ),
    ) -> list[dict[str, Any]]:
        """Search for threat indicators and indicators of compromise (IOCs) from CrowdStrike intelligence.

        IMPORTANT: You must use the `falcon://intel/indicators/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_indicators` tool.
        """
        api_response = self._base_search_api_call(
            operation="QueryIntelIndicatorEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "include_deleted": include_deleted,
                "include_relations": include_relations,
            },
            error_message="Failed to search indicators",
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def query_report_entities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression that should be used to limit the results. IMPORTANT: use the `falcon://intel/reports/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of records to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: str | None = Field(
            default=None,
            description="The field and direction to sort results on in the format of: {field}.{asc}or {field}.{desc}. Valid values include: name, target_countries, target_industries, type, created_date, last_modified_date. Ex: created_date|desc",
            examples={"created_date|desc"},
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all indexed fields.",
        ),
    ) -> list[dict[str, Any]]:
        """Access CrowdStrike intelligence publications and threat reports.

        This tool returns comprehensive intelligence report details based on your search criteria.
        Use this when you need to find CrowdStrike intelligence publications matching specific conditions.
        For guidance on building FQL filters, use the `falcon://intel/reports/fql-guide` resource.

        IMPORTANT: You must use the `falcon://intel/reports/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_reports` tool.
        """
        api_response = self._base_search_api_call(
            operation="QueryIntelReportEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search reports",
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(api_response):
            return [api_response]

        return api_response

    def get_mitre_report(
        self,
        actor: str = Field(
            ...,
            description="Threat actor name or ID",
            examples={"WARP PANDA", "234987", "revenant spider"},
        ),
        format: str = Field(
            default="json",
            description="Report format. Accepted options: 'csv' or 'json'.",
            examples={"json", "csv"},
        ),
    ) -> list[dict[str, Any]] | str:
        """Generate MITRE ATT&CK report for a given threat actor.

        Provides detailed MITRE ATT&CK tactics, techniques, and procedures (TTPs)
        report associated with a specific threat actor tracked.

        Args:
            actor: Pass the actor name (string) or numeric actor ID (string).
            format: Report format. Accepted options: 'csv' or 'json'. Defaults to 'json'.
        """

        # Check if the actor parameter looks like an ID (numeric) or a name
        actor_id = actor.strip()

        # If it's not a numeric ID, search for the actor first
        if not actor_id.isdigit():
            logger.debug("Searching for actor: %s", actor)

            # Search for actors using the provided name with FQL filter
            search_results = self._base_search_api_call(
                operation="QueryIntelActorEntities",
                search_params={
                    "filter": f"name:'{actor}'",
                    "limit": 1,
                },
                error_message="Failed to search for actor by name",
            )

            # Check if search returned an error
            if self._is_error(search_results):
                return [search_results]

            # Check if we got any results - must be a list at this point
            if not search_results or not isinstance(search_results, list):
                return [{
                    "error": "Actor not found",
                    "message": f"No actor found with name: {actor}",
                }]

            # Get the first (and should be only) result
            selected_actor = search_results[0]

            # Extract the numeric ID
            actor_id = str(selected_actor.get('id', ''))
            if not actor_id or actor_id == 'None':
                return [{
                    "error": "Invalid actor data",
                    "message": f"Found actor '{selected_actor.get('name', 'Unknown')}' but missing ID field",
                    "actor_data": selected_actor
                }]

            logger.debug("Resolved actor '%s' to ID: %s", actor, actor_id)

        # Use the base GET API call method with binary decoding
        api_response = self._base_get_api_call(
            operation="GetMitreReport",
            api_params={
                "actor_id": actor_id,
                "format": format,
            },
            error_message="Failed to get MITRE report",
            decode_binary=True,
        )

        # If it's an error, wrap in list for consistency
        if self._is_error(api_response):
            logger.debug("API response is an error, wrapping in list")
            return [api_response]

        return api_response

