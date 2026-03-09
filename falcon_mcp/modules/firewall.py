"""
Firewall Management module for Falcon MCP Server.

This module provides tools for searching and managing firewall rules and rule groups.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.firewall import SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION


class FirewallModule(BaseModule):
    """Module for Firewall Management operations via FalconPy."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_firewall_rules,
            name="search_firewall_rules",
        )

        self._add_tool(
            server=server,
            method=self.search_firewall_rule_groups,
            name="search_firewall_rule_groups",
        )

        self._add_tool(
            server=server,
            method=self.search_firewall_policy_rules,
            name="search_firewall_policy_rules",
        )

        self._add_tool(
            server=server,
            method=self.create_firewall_rule_group,
            name="create_firewall_rule_group",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_firewall_rule_groups,
            name="delete_firewall_rule_groups",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_firewall_rules_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall/rules/fql-guide"),
            name="falcon_search_firewall_rules_fql_guide",
            description="Contains the guide for the `filter` param of firewall search tools.",
            text=SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_firewall_rules_fql_resource)

    def search_firewall_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule search. IMPORTANT: use the `falcon://firewall/rules/fql-guide` resource when building this filter parameter.",
            examples=["enabled:true", "platform:'windows'+name:'Block*'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of rule IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort firewall rules using FQL syntax.

                Supported examples: name.asc, modified_on.desc, platform|asc
            """).strip(),
            examples=["modified_on.desc", "name|asc"],
        ),
        q: str | None = Field(
            default=None,
            description="Free-text query string across rule fields.",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from a previous query response.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search firewall rules and return full rule details."""
        rule_ids = self._base_search_api_call(
            operation="query_rules",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to search firewall rules",
        )

        if self._is_error(rule_ids):
            if filter:
                return self._format_fql_error_response(
                    [rule_ids], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION
                )
            return [rule_ids]

        if not rule_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="get_rules",
            ids=rule_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_firewall_rule_groups(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule group search. IMPORTANT: use the `falcon://firewall/rules/fql-guide` resource when building this filter parameter.",
            examples=["enabled:true", "platform:'windows'+name:'Default*'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of rule group IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in FQL syntax (e.g., modified_on.desc).",
        ),
        q: str | None = Field(
            default=None,
            description="Free-text query string across rule group fields.",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from a previous query response.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search firewall rule groups and return full rule group details."""
        rule_group_ids = self._base_search_api_call(
            operation="query_rule_groups",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to search firewall rule groups",
        )

        if self._is_error(rule_group_ids):
            if filter:
                return self._format_fql_error_response(
                    [rule_group_ids], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION
                )
            return [rule_group_ids]

        if not rule_group_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="get_rule_groups",
            ids=rule_group_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_firewall_policy_rules(
        self,
        policy_id: str = Field(
            description="Policy container ID to query rules within.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for policy rule search. IMPORTANT: use the `falcon://firewall/rules/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of policy rule IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in FQL syntax (e.g., modified_on.desc).",
        ),
        q: str | None = Field(
            default=None,
            description="Free-text query string across policy rule fields.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search firewall rules in a specific policy container and return full rule details."""
        policy_rule_ids = self._base_search_api_call(
            operation="query_policy_rules",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search firewall policy rules",
        )

        if self._is_error(policy_rule_ids):
            if filter:
                return self._format_fql_error_response(
                    [policy_rule_ids], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION
                )
            return [policy_rule_ids]

        if not policy_rule_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="get_rules",
            ids=policy_rule_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def create_firewall_rule_group(
        self,
        name: str | None = Field(
            default=None,
            description="Rule group name. Required when `body` is not provided.",
        ),
        platform: str | None = Field(
            default=None,
            description="Target platform (for example: windows, mac, linux). Required when `body` is not provided.",
        ),
        rules: list[dict[str, Any]] | None = Field(
            default=None,
            description="Rule definitions. Required when `body` is not provided and `clone_id` is not set.",
        ),
        description: str | None = Field(
            default=None,
            description="Rule group description.",
        ),
        enabled: bool = Field(
            default=True,
            description="Whether this rule group is enabled.",
        ),
        clone_id: str | None = Field(
            default=None,
            description="Rule group ID to clone from.",
        ),
        library: bool | None = Field(
            default=None,
            description="Set true when cloning from the CrowdStrike rule group library.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit log comment for this action.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a firewall rule group."""
        request_body = body
        if request_body is None:
            if not name or not platform:
                return [
                    _format_error_response(
                        "`name` and `platform` are required when `body` is not provided.",
                        operation="create_rule_group",
                    )
                ]
            if not rules and not clone_id:
                return [
                    _format_error_response(
                        "Provide `rules` or `clone_id` when creating a firewall rule group.",
                        operation="create_rule_group",
                    )
                ]

            request_body = {
                "name": name,
                "platform": platform,
                "enabled": enabled,
            }
            if description:
                request_body["description"] = description
            if rules:
                request_body["rules"] = rules

        result = self._base_query_api_call(
            operation="create_rule_group",
            query_params={
                "clone_id": clone_id,
                "library": library,
                "comment": comment,
            },
            body_params=request_body,
            error_message="Failed to create firewall rule group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_firewall_rule_groups(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Rule group IDs to delete.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit log comment for this action.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete firewall rule groups by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required when deleting firewall rule groups.",
                    operation="delete_rule_groups",
                )
            ]

        result = self._base_query_api_call(
            operation="delete_rule_groups",
            query_params={
                "ids": ids,
                "comment": comment,
            },
            error_message="Failed to delete firewall rule groups",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

