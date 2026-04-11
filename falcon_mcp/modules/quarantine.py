"""
Quarantine module for Falcon MCP Server.

This module provides tools for investigating quarantined files and applying
quarantine actions during triage and remediation workflows.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.utils import normalize_field_value
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.quarantine import (
    EMBEDDED_FQL_SYNTAX,
    SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION,
)

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

VALID_QUARANTINE_ACTIONS = {"release", "unrelease", "delete"}


class QuarantineModule(BaseModule):
    """Module for investigating and managing Falcon quarantine records."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_quarantined_files,
            name="search_quarantined_files",
        )
        self._add_tool(
            server=server,
            method=self.get_quarantined_file_details,
            name="get_quarantined_file_details",
        )
        self._add_tool(
            server=server,
            method=self.preview_quarantine_action_counts,
            name="preview_quarantine_action_counts",
        )
        self._add_tool(
            server=server,
            method=self.update_quarantined_files_by_ids,
            name="update_quarantined_files_by_ids",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_quarantined_files_by_filter,
            name="update_quarantined_files_by_filter",
            annotations=MUTATING_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_quarantined_files_fql_resource = TextResource(
            uri=AnyUrl("falcon://quarantine/files/search/fql-guide"),
            name="falcon_search_quarantined_files_fql_guide",
            description="Contains the guide for the `filter` param of quarantine search and filter-based action tools.",
            text=SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_quarantined_files_fql_resource,
        )

    def search_quarantined_files(
        self,
        filter: str | None = Field(
            default=None,
            description=EMBEDDED_FQL_SYNTAX,
        ),
        q: str | None = Field(
            default=None,
            description="Free-text search across common quarantine fields such as sha256, hostname, username, and paths.path.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of quarantine file IDs to return. Max: 500.",
        ),
        offset: str | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort quarantined files using FQL syntax such as `date_updated|desc` or `hostname|asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search quarantined files and return full quarantine metadata.

        IMPORTANT: You must use the `falcon://quarantine/files/search/fql-guide`
        resource when building the `filter` parameter for this tool.

        Use this tool to discover quarantine records by host, hash, user, or
        status. If matching record IDs are found, the tool retrieves the full
        quarantine details before returning them. Empty results and filter errors
        include the FQL guide to help refine the query.
        """
        file_ids = self._base_search_api_call(
            operation="QueryQuarantineFiles",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search quarantined files",
            default_result=[],
        )

        if self._is_error(file_ids):
            return self._format_fql_error_response(
                [file_ids], filter, SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION
            )

        if not file_ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="GetQuarantineFiles",
            ids=file_ids,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_quarantined_file_details(
        self,
        ids: list[str] = Field(description="Quarantine file ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve quarantine record details for IDs you already know.

        Use this tool only when you already have specific quarantine file IDs.
        To discover records by host, hash, user, or status, use
        `falcon_search_quarantined_files`.
        """
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="GetQuarantineFiles",
            ids=ids,
        )

        if self._is_error(details):
            return [details]

        return details

    def preview_quarantine_action_counts(
        self,
        filter: str = Field(
            description="FQL filter used to estimate how many quarantined files would be affected by each action. Use `*` for all files. IMPORTANT: use the `falcon://quarantine/files/search/fql-guide` resource when building this filter parameter.",
        ),
    ) -> list[dict[str, Any]]:
        """Estimate how many quarantine records each action would affect.

        Use this read-only tool before calling a mutating quarantine action when
        you want to understand the blast radius of a `release`, `unrelease`, or
        `delete` request.
        """
        result = self._base_query_api_call(
            operation="ActionUpdateCount",
            query_params={"filter": filter},
            error_message="Failed to preview quarantine action counts",
        )

        if self._is_error(result):
            return [result]

        return result

    def update_quarantined_files_by_ids(
        self,
        ids: list[str] = Field(description="Quarantine file ID(s) to update."),
        action: str = Field(
            description="Action to apply. Supported values are `release`, `unrelease`, and `delete`.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment describing why the action is being taken.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply a quarantine action to specific records by ID.

        Use this tool when you already know the quarantine file IDs to update.
        The `action` value is case-insensitive and must be one of `release`,
        `unrelease`, or `delete`.
        """
        action = self._normalize_action(action)
        if self._is_error(action):
            return [action]

        result = self._base_query_api_call(
            operation="UpdateQuarantinedDetectsByIds",
            body_params={
                "ids": ids,
                "action": action,
                "comment": comment,
            },
            error_message="Failed to update quarantined files by IDs",
        )

        if self._is_error(result):
            return [result]

        return result

    def update_quarantined_files_by_filter(
        self,
        action: str = Field(
            description="Action to apply. Supported values are `release`, `unrelease`, and `delete`.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter used to select quarantined files. IMPORTANT: use the `falcon://quarantine/files/search/fql-guide` resource when building this filter parameter.",
        ),
        q: str | None = Field(
            default=None,
            description="Optional free-text search used to further narrow the update target set.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment describing why the action is being taken.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply a quarantine action to records selected by query.

        Use this tool when you want Falcon to select the target quarantine
        records using `filter` or `q` instead of explicit IDs. The `action`
        value is case-insensitive and must be one of `release`, `unrelease`, or
        `delete`.
        """
        action = self._normalize_action(action)
        if self._is_error(action):
            return [action]

        filter = normalize_field_value(filter)
        q = normalize_field_value(q)

        if not filter and not q:
            return [
                _format_error_response(
                    "Provide at least one of `filter` or `q` when updating quarantined files by query."
                )
            ]

        result = self._base_query_api_call(
            operation="UpdateQfByQuery",
            body_params={
                "action": action,
                "filter": filter,
                "q": q,
                "comment": comment,
            },
            error_message="Failed to update quarantined files by query",
        )

        if self._is_error(result):
            return [result]

        return result

    def _normalize_action(self, action: str | None) -> str | dict[str, Any]:
        """Normalize and validate quarantine action names."""
        normalized = normalize_field_value(action)
        if not isinstance(normalized, str):
            return _format_error_response(
                "Provide a quarantine `action` value of `release`, `unrelease`, or `delete`."
            )

        lowered = normalized.strip().lower()
        if lowered not in VALID_QUARANTINE_ACTIONS:
            return _format_error_response(
                "Unsupported quarantine `action`. Use `release`, `unrelease`, or `delete`."
            )

        return lowered
