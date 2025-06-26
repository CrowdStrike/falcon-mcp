# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Intel module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon intelligence data.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
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
            self.search_actors,
            name="search_actors"
        )

    def search_actors(
        self,
        filter: Optional[str] = Field(default=None, description="FQL query expression that should be used to limit the results."),
        limit: Optional[int] = Field(default=100, ge=1, le=5000, description="Maximum number of records to return. (Max: 5000)"),
        offset: Optional[int] = Field(default=0, ge=0, description="Starting index of overall result set from which to return ids."),
        sort: Optional[str] = Field(default=None, description="The property to sort by. (Ex: created_date|desc)"),
        q: Optional[str] = Field(default=None, description="Free text search across all indexed fields."),
    ) -> Dict[str, Any]:
        """Get info about actors that match provided FQL filters.

        Args:
            filter: FQL query expression that should be used to limit the results.
            limit: Maximum number of records to return. (Max: 5000)
            offset: Starting index of overall result set from which to return ids.
            sort: The property to sort by. (Ex: created_date|desc)
            q: Free text search across all indexed fields.

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
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search actors",
            default_result=[]
        )
