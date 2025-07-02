# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Intel module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon intelligence data.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
from ..resources.intel import QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION
from .base import BaseModule

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
            server,
            self.query_actor_entities,
            name="search_actors"
        )

        self._add_tool(
            server,
            self.query_indicator_entities,
            name="search_indicators"
        )

        self._add_tool(
            server,
            self.query_report_entities,
            name="search_reports"
        )

    def register_resources(self, server) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """

        query_actor_entities_resource = TextResource(
            uri=AnyUrl("falcon://intel/query_actor_entities/fql-guide"),
            name="falcon_query_actor_entities_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_actors` tool.",
            text=QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION
        )

        self._add_resource(
            server,
            query_actor_entities_resource
        )

    def query_actor_entities(
        self,
        filter: Optional[str] = Field(default=None, description="FQL query expression that should be used to limit the results. IMPORTANT: use the 'falcon://query_actor_entities_fql_documentation' resource when building this parameter."),
        limit: Optional[int] = Field(default=100, ge=1, le=5000, description="Maximum number of records to return. Max 5000", examples={10, 20, 100}),
        offset: Optional[int] = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids.", examples={0,10}),
        sort: Optional[str] = Field(default=None, description="The property to sort by. Example: 'created_date|desc'", examples={"created_date|desc"}),
        q: Optional[str] = Field(default=None, description="Free text search across all indexed fields.", examples={"BEAR"}),
    ) -> List[Dict[str, Any]]:
        """Get info about actors that match provided FQL filters. Use this when you need to query for actor entities matching certain criteria.

        IMPORTANT: You must call the FQL Guide for Intel Query Actor Entities (falcon://intel/query_actor_entities/fql-guide) resource first

        Returns:
            Information about actors that match the provided filters.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "q": q,
        })

        # Define the operation name
        operation = "QueryIntelActorEntities"

        logger.debug("Searching actors with params: %s", params)

        # Make the API request
        command_response = self.client.command(operation, parameters=params)

        # Handle the response
        api_response = handle_api_response(
            command_response,
            operation=operation,
            error_message="Failed to search actors",
            default_result=[]
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def query_indicator_entities(
        self,
        filter: Optional[str] = Field(default=None, description="FQL query expression that should be used to limit the results."),
        limit: Optional[int] = Field(default=100, ge=1, le=5000, description="Maximum number of records to return. (Max: 5000)"),
        offset: Optional[int] = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="The property to sort by. (Ex: created_date|desc)"),
        q: Optional[str] = Field(default=None, description="Free text search across all indexed fields."),
        include_deleted: Optional[bool] = Field(default=False, description="Flag indicating if both published and deleted indicators should be returned."),
        include_relations: Optional[bool] = Field(default=False, description="Flag indicating if related indicators should be returned."),
    ) -> List[Dict[str, Any]]:
        """Get info about indicators that match provided FQL filters.

        Args:
            filter: FQL query expression that should be used to limit the results.
            limit: Maximum number of records to return. (Max: 5000)
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: created_date|desc)
            q: Free text search across all indexed fields.
            include_deleted: Flag indicating if both published and deleted indicators should be returned.
            include_relations: Flag indicating if related indicators should be returned.

        Returns:
            List of indicators that match the provided filters.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "q": q,
            "include_deleted": include_deleted,
            "include_relations": include_relations,
        })

        # Define the operation name
        operation = "QueryIntelIndicatorEntities"

        logger.debug("Searching indicators with params: %s", params)

        # Make the API request
        command_response = self.client.command(operation, parameters=params)

        # Handle the response
        api_response = handle_api_response(
            command_response,
            operation=operation,
            error_message="Failed to search indicators",
            default_result=[]
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def query_report_entities(
        self,
        filter: Optional[str] = Field(default=None, description="FQL query expression that should be used to limit the results."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of records to return. (Max: 5000)"),
        offset: int = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="The property to sort by. (Ex: created_date|desc)"),
        q: Optional[str] = Field(default=None, description="Free text search across all indexed fields."),
    ) -> List[Dict[str, Any]]:
        """Get info about reports that match provided FQL filters.

        Args:
            filter: FQL query expression that should be used to limit the results. Review the following table for a complete list of available filters.
            limit: Maximum number of records to return. (Max: 5000)
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: created_date|desc)
            q: Free text search across all indexed fields.
            fields: The fields to return, or a predefined set of fields in the form of the collection name surrounded by two underscores.

        Returns:
            List of reports that match the provided filters.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "q": q,
        })

        # Define the operation name
        operation = "QueryIntelReportEntities"

        logger.debug("Searching reports with params: %s", params)

        # Make the API request
        command_response = self.client.command(operation, parameters=params)

        # Handle the response
        api_response = handle_api_response(
            command_response,
            operation=operation,
            error_message="Failed to search reports",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(api_response):
            return [api_response]

        return api_response
