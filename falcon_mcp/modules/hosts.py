"""
Hosts module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon hosts/devices.
"""

from textwrap import dedent
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.field_presets import HOST_SUMMARY_FIELDS
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import filter_records, format_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.hosts import SEARCH_HOSTS_FQL_DOCUMENTATION

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
            server=server,
            method=self.search_hosts,
            name="search_hosts",
        )

        self._add_tool(
            server=server,
            method=self.get_host_details,
            name="get_host_details",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_hosts_fql_resource = TextResource(
            uri=AnyUrl("falcon://hosts/search/fql-guide"),
            name="falcon_search_hosts_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_hosts` tool.",
            text=SEARCH_HOSTS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_hosts_fql_resource,
        )

    def search_hosts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://hosts/search/fql-guide` for syntax.",
            examples={"platform_name:'Windows'", "hostname:'PC*'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="The maximum records to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str | None = Field(
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
            examples={"hostname.asc", "last_seen.desc"},
        ),
        view: Literal["summary", "full"] = Field(
            default="summary",
            description="'summary' returns investigation-essential fields only (default). 'full' returns the complete API response.",
        ),
        fields: list[str] | None = Field(
            default=None,
            description="Override: explicit list of fields to return. Takes precedence over view.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> list[dict[str, Any]] | str:
        """Search for hosts in your CrowdStrike environment.

        Use this to find devices by hostname, platform, IP, sensor version, or other
        attributes. Consult falcon://hosts/search/fql-guide before constructing filter
        expressions. Returns full host details including device info, OS, and network
        context.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(view, FieldInfo):
            view = view.default
        if isinstance(fields, FieldInfo):
            fields = fields.default
        if isinstance(format, FieldInfo):
            format = format.default

        device_ids = self._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search hosts",
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(device_ids):
            return [device_ids]

        # If we have device IDs, get the details for each one
        if device_ids:
            details = self._base_get_by_ids(
                operation="PostDeviceDetailsV2",
                ids=device_ids,
                id_key="ids",
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if self._is_error(details):
                return [details]

            if fields:
                details = filter_records(details, fields)
            elif view == "summary":
                details = filter_records(details, HOST_SUMMARY_FIELDS)

            return format_response(details, format)

        return []

    def get_host_details(
        self,
        ids: list[str] = Field(
            description="Host device IDs to retrieve details for. You can get device IDs from the search_hosts operation, the Falcon console, or the Streaming API. Maximum: 5000 IDs per request."
        ),
        view: Literal["summary", "full"] = Field(
            default="summary",
            description="'summary' returns investigation-essential fields only (default). 'full' returns the complete API response.",
        ),
        fields: list[str] | None = Field(
            default=None,
            description="Override: explicit list of fields to return. Takes precedence over view.",
        ),
        format: Literal["json", "toon"] = Field(
            default="json",
            description="Response format. 'toon' uses compact tabular encoding for token efficiency.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Retrieve detailed information for one or more host device IDs.

        Use when you already have specific device IDs from search results, the Falcon
        console, or the Streaming API. For discovering hosts by criteria, use
        falcon_search_hosts instead. Returns comprehensive host details.
        """
        # Resolve FieldInfo defaults for direct calls (e.g., from tests)
        if isinstance(view, FieldInfo):
            view = view.default
        if isinstance(fields, FieldInfo):
            fields = fields.default
        if isinstance(format, FieldInfo):
            format = format.default

        logger.debug("Getting host details for IDs: %s", ids)

        # Handle empty list case - return empty list without making API call
        if not ids:
            return []

        result = self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=ids,
            id_key="ids",
        )

        if self._is_error(result):
            return result

        if isinstance(result, list):
            if fields:
                result = filter_records(result, fields)
            elif view == "summary":
                result = filter_records(result, HOST_SUMMARY_FIELDS)
            return format_response(result, format)

        return result
