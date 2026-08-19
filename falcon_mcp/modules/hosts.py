"""
Hosts module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon hosts/devices.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.hosts import SEARCH_HOSTS_FQL_DOCUMENTATION

logger = get_logger(__name__)

# A host's `tags` array mixes two namespaces that are not interchangeable:
# FalconGroupingTags are set cloud-side and are what UpdateDeviceTags edits;
# SensorGroupingTags are baked in by the sensor installer and are read-only.
GROUPING_PREFIX = "FalconGroupingTags/"
SENSOR_PREFIX = "SensorGroupingTags/"

VALID_TAG_ACTIONS = ("add", "remove")

# Caps the API enforces, checked here because it reports neither cleanly
MAX_TAG_DEVICE_IDS = 5000
MAX_TAGS_PER_REQUEST = 50


def _tag_error(message: str) -> list[dict[str, Any]]:
    """Wrap a tag validation failure in the module's standard error shape."""
    return [_format_error_response(message, operation="UpdateDeviceTags")]


def _has_prefix(tag: str, prefix: str) -> bool:
    """Check for a namespace prefix without regard to how the caller cased it.

    The API compares the prefix exactly, so a miscased one is not a prefix to it:
    `falcongroupingtags/x` is rejected outright, and blindly prepending the
    canonical prefix would instead build the real-but-meaningless
    `FalconGroupingTags/falcongroupingtags/x`. Recognizing prefixes
    case-insensitively lets the caller's intent be honored either way.
    """
    return tag.casefold().startswith(prefix.casefold())


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

        self._add_tool(
            server=server,
            method=self.manage_host_grouping_tags,
            name="manage_host_grouping_tags",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
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

                Sort either asc (ascending) or desc (descending). Use the dot
                separator ('hostname.desc'), which is supported on every Falcon
                sort endpoint. The pipe form ('hostname|desc') is accepted here
                but rejected by some endpoints, so prefer the dot form.

                Examples: 'hostname.asc', 'last_seen.desc', 'platform_name.asc'
            """).strip(),
            examples={"hostname.asc", "last_seen.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search hosts and their sensor state: filter by hostname, platform, IP, sensor version, containment (network-quarantine) status, assigned policies, or grouping tags.

        Use this to find devices and check their protection state - whether a host is
        contained, what sensor version it runs, which policies apply. For drive encryption,
        disk/memory/CPU, OS security settings, or internet exposure, use
        `falcon_search_managed_assets`. See `falcon://hosts/search/fql-guide` for filters;
        returns full host details.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        device_ids, pagination = self._base_search_with_meta(
            operation="QueryDevicesByFilter",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search hosts",
        )

        if self._is_error(device_ids):
            return self._format_fql_error_response(
                [device_ids], filter, SEARCH_HOSTS_FQL_DOCUMENTATION
            )

        if not device_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=device_ids,
            id_key="ids",
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order in case the details endpoint
        # returns entities in a different order (validated field: device_id).
        details = self._reorder_by_ids(device_ids, details, id_field="device_id")
        return self._build_pagination_envelope(details, pagination, filter)

    def get_host_details(
        self,
        ids: list[str] = Field(
            description="Host device IDs to retrieve details for. You can get device IDs from the search_hosts operation, the Falcon console, or the Streaming API. Maximum: 5000 IDs per request."
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve detailed information for one or more host device IDs.

        Use when you already have specific device IDs from search results, the Falcon
        console, or the Streaming API. For discovering hosts by criteria, use
        falcon_search_hosts instead. Returns comprehensive host details.
        """
        logger.debug("Getting host details for IDs: %s", ids)

        # Handle empty list case - return empty list without making API call
        if not ids:
            return []

        return self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=ids,
            id_key="ids",
        )

    def manage_host_grouping_tags(
        self,
        ids: list[str] = Field(
            description=(
                "Host device IDs (AIDs) to tag. You can get device IDs from the "
                "falcon_search_hosts operation, the Falcon console, or the Streaming API. "
                "Maximum: 5000 IDs per request."
            ),
        ),
        action: str = Field(
            description="Action to perform. Values: 'add' or 'remove'.",
        ),
        tags: list[str] = Field(
            description=(
                "Falcon Grouping Tags to add or remove. The 'FalconGroupingTags/' "
                "prefix is optional and is added automatically. Sensor grouping tags "
                "('SensorGroupingTags/') are applied by the sensor installer and "
                "cannot be changed through this API. Maximum: 50 tags per request."
            ),
        ),
    ) -> list[dict[str, Any]]:
        """Add or remove Falcon Grouping Tags on one or more hosts.

        Set action to 'add' to attach tags, or 'remove' to detach them, on every device
        in `ids`. Grouping tags can drive dynamic host group assignment and therefore
        policy assignment, so changing them may change a host's security posture.
        Adding a tag a host already has, or removing one it lacks, is a no-op. Returns
        one record per device, each with `device_id`, `updated`, and `code`. Tag names
        are case-sensitive, so removing a tag requires the exact casing it was created
        with.
        """
        if action not in VALID_TAG_ACTIONS:
            return _tag_error(f"Invalid action {action!r}. Must be 'add' or 'remove'.")

        if not ids:
            return _tag_error("`ids` must be provided to manage host grouping tags.")

        if len(ids) > MAX_TAG_DEVICE_IDS:
            return _tag_error(
                f"Too many device IDs: {len(ids)}. The API accepts at most "
                f"{MAX_TAG_DEVICE_IDS} per request."
            )

        if not tags:
            return _tag_error("`tags` must be provided to manage host grouping tags.")

        if len(tags) > MAX_TAGS_PER_REQUEST:
            return _tag_error(
                f"Too many tags: {len(tags)}. The API accepts at most "
                f"{MAX_TAGS_PER_REQUEST} per request and fails the whole call above that."
            )

        normalized_tags: list[str] = []
        for tag in tags:
            # Trim before prefixing: ' Quarantined' would otherwise become the
            # distinct (and real) tag 'FalconGroupingTags/ Quarantined'.
            stripped = tag.strip()

            if not stripped:
                return _tag_error("Tag values cannot be empty.")

            # Reject before prefixing. Prefixing a sensor tag would build a real but
            # meaningless 'FalconGroupingTags/SensorGroupingTags/...' tag rather than
            # failing, so the guard has to come first.
            if _has_prefix(stripped, SENSOR_PREFIX):
                return _tag_error(
                    f"{stripped!r} is a sensor grouping tag. Those are applied by "
                    "the sensor installer and cannot be changed through the API."
                )

            if _has_prefix(stripped, GROUPING_PREFIX):
                # Re-apply the canonical prefix so a miscased one still lands on the
                # tag the caller meant, rather than being rejected by the API.
                normalized_tags.append(GROUPING_PREFIX + stripped[len(GROUPING_PREFIX):])
            else:
                normalized_tags.append(GROUPING_PREFIX + stripped)

        logger.debug(
            "Performing tag %s on %d host(s): %s", action, len(ids), normalized_tags
        )

        result = self._base_query_api_call(
            operation="UpdateDeviceTags",
            # The Uber class (APIHarnessV2) takes the raw swagger body, so these are
            # `action`/`device_ids` — not the `action_name`/`ids` keyword names used
            # by FalconPy's Hosts.update_device_tags() service-class method.
            body_params={
                "action": action,
                "device_ids": ids,
                "tags": normalized_tags,
            },
            error_message="Failed to manage host grouping tags",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
