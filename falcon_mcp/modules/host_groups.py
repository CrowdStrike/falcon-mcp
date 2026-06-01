"""
Host Groups module for Falcon MCP Server

This module provides tools for searching, creating, updating, and deleting
CrowdStrike Falcon host groups, as well as managing group membership.
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
from falcon_mcp.resources.host_groups import SEARCH_HOST_GROUPS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class HostGroupsModule(BaseModule):
    """Module for managing CrowdStrike Falcon host groups and their membership."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_host_groups,
            name="search_host_groups",
        )

        self._add_tool(
            server=server,
            method=self.search_host_group_members,
            name="search_host_group_members",
        )

        self._add_tool(
            server=server,
            method=self.create_host_group,
            name="create_host_group",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_host_group,
            name="update_host_group",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_host_groups,
            name="delete_host_groups",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.perform_host_group_action,
            name="perform_host_group_action",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_host_groups_fql_resource = TextResource(
            uri=AnyUrl("falcon://host-groups/search/fql-guide"),
            name="falcon_search_host_groups_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_host_groups` tool.",
            text=SEARCH_HOST_GROUPS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_host_groups_fql_resource,
        )

    def search_host_groups(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://host-groups/search/fql-guide` for syntax.",
            examples={"group_type:'static'", "name:'Production Servers'"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="The maximum records to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str = Field(
            default="name.asc",
            description=dedent("""
                Sort host groups using these options:

                name: Host group name
                group_type: Host group type (static/dynamic)
                created_by: User who created the group
                created_timestamp: When the group was created
                modified_by: User who last modified the group
                modified_timestamp: When the group was last modified

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'name.desc' or 'name|desc'

                Examples: 'name.asc', 'created_timestamp.desc'
            """).strip(),
            examples={"name.asc", "created_timestamp.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for host groups in your CrowdStrike environment.

        Use this to find host groups by name, type, creator, or timestamps. Consult
        falcon://host-groups/search/fql-guide before constructing filter expressions.
        Returns full host group details including id, name, group_type, description,
        and audit metadata in a single call.
        """
        host_groups = self._base_search_api_call(
            operation="queryCombinedHostGroups",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search host groups",
        )

        if self._is_error(host_groups):
            return self._format_fql_error_response(
                [host_groups], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION
            )

        if not host_groups:
            return self._format_fql_error_response(
                [], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION
            )

        return host_groups

    def search_host_group_members(
        self,
        id: str = Field(
            description="The host group ID whose members should be retrieved. If you don't already have it, use falcon_search_host_groups to look it up.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression on HOST attributes. See `falcon://hosts/search/fql-guide` for syntax.",
            examples={"platform_name:'Windows'", "hostname:'PC*'"},
        ),
        limit: int = Field(
            default=100,
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
            description="Sort members using host FQL sort syntax (e.g. 'hostname.asc', 'last_seen.desc').",
            examples={"hostname.asc", "last_seen.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for the host members of a specific host group.

        Use this to list the devices that belong to a host group. Requires the group
        `id` and filters on HOST attributes (platform, hostname, etc.) — consult
        falcon://hosts/search/fql-guide for the filter syntax. Returns full host device
        entities including device_id, hostname, platform, and network context.
        """
        members = self._base_search_api_call(
            operation="queryCombinedGroupMembers",
            search_params={
                "id": id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search host group members",
        )

        if self._is_error(members):
            return [members]

        return members

    def create_host_group(
        self,
        name: str = Field(
            description="Name for the new host group.",
        ),
        group_type: str = Field(
            description="Type of host group. One of: 'static' (hosts added manually by ID via falcon_perform_host_group_action), 'staticByID' (same, populated after creation), or 'dynamic' (hosts matched automatically by an assignment_rule).",
        ),
        description: str | None = Field(
            default=None,
            description="Description for the host group.",
        ),
        assignment_rule: str | None = Field(
            default=None,
            description="FQL assignment rule for dynamic groups (e.g. \"platform_name:'Windows'\"). Required for 'dynamic' groups; the API rejects it for 'static'/'staticByID' groups.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a host group.

        Provide a name and group_type. 'dynamic' groups take an assignment_rule (host
        FQL) that automatically includes matching hosts. 'static' and 'staticByID' groups
        are created empty (no assignment_rule) and populated afterwards via
        falcon_perform_host_group_action. Returns the created host group record on success.
        """
        resource: dict[str, Any] = {
            "name": name,
            "group_type": group_type,
        }
        if description is not None:
            resource["description"] = description
        if assignment_rule is not None:
            resource["assignment_rule"] = assignment_rule

        result = self._base_query_api_call(
            operation="createHostGroups",
            body_params={"resources": [resource]},
            error_message="Failed to create host group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_host_group(
        self,
        id: str = Field(
            description="The host group ID to update. If you don't already have it, use falcon_search_host_groups to look it up.",
        ),
        name: str | None = Field(
            default=None,
            description="New name for the host group.",
        ),
        description: str | None = Field(
            default=None,
            description="New description for the host group.",
        ),
        assignment_rule: str | None = Field(
            default=None,
            description="New FQL assignment rule (e.g. \"platform_name:'Windows'\"). Only set this for 'dynamic' groups. The API does not block setting it on 'static'/'staticByID' groups, but doing so leaves the group in an inconsistent state and should be avoided.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an existing host group.

        Provide the group `id` and any fields to change. name and description are safe
        for any group type; only set assignment_rule on 'dynamic' groups. Unspecified
        fields are left unchanged. Returns the updated host group record on success.
        """
        resource: dict[str, Any] = {"id": id}
        if name is not None:
            resource["name"] = name
        if description is not None:
            resource["description"] = description
        if assignment_rule is not None:
            resource["assignment_rule"] = assignment_rule

        result = self._base_query_api_call(
            operation="updateHostGroups",
            body_params={"resources": [resource]},
            error_message="Failed to update host group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_host_groups(
        self,
        ids: list[str] = Field(
            description="Host group IDs to delete. If you don't already have them, use falcon_search_host_groups to look them up.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete one or more host groups.

        Provide the host group `ids` to delete. This permanently removes the groups.
        Returns an empty list on success.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to delete host groups.",
                    operation="deleteHostGroups",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteHostGroups",
            query_params={"ids": ids},
            error_message="Failed to delete host groups",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_host_group_action(
        self,
        action_name: str = Field(
            description="The membership action to perform. Either 'add-hosts' or 'remove-hosts'.",
        ),
        ids: list[str] = Field(
            description="Host group IDs to add hosts to or remove hosts from. If you don't already have them, use falcon_search_host_groups to look them up.",
        ),
        filter: str = Field(
            description="Host FQL expression selecting which hosts to add or remove (e.g. \"device_id:['id1','id2']\" or \"platform_name:'Windows'\"). See `falcon://hosts/search/fql-guide` for syntax.",
        ),
    ) -> list[dict[str, Any]]:
        """Add or remove hosts from one or more host groups.

        Set action_name to 'add-hosts' or 'remove-hosts', provide the target group
        `ids`, and a host FQL filter selecting which hosts to act on. Applies only to
        static groups. Returns the updated host group records on success.
        """
        result = self._base_query_api_call(
            operation="performGroupAction",
            query_params={"action_name": action_name},
            body_params={
                "ids": ids,
                "action_parameters": [{"name": "filter", "value": filter}],
            },
            error_message="Failed to perform host group action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
