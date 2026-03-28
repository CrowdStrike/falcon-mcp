"""
Quarantine module for Falcon MCP Server.

This module provides tools for investigating quarantined files and applying
quarantine actions during triage and remediation workflows.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.utils import normalize_field_value
from falcon_mcp.modules.base import BaseModule

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class QuarantineModule(BaseModule):
    """Module for investigating and managing Falcon quarantine records."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_quarantined_files, name="search_quarantined_files")
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

    def search_quarantined_files(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for quarantined files. Common fields include status, device.hostname, device.device_id, behaviors.username, and behaviors.ioc_value.",
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
    ) -> list[dict[str, Any]]:
        """Search quarantined files and return full quarantine metadata."""
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
            return [file_ids]

        if not file_ids:
            return []

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
        """Retrieve detailed metadata for specific quarantined files."""
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
            description="FQL filter used to estimate how many quarantined files would be affected by each action. Use `*` for all files.",
        ),
    ) -> list[dict[str, Any]]:
        """Preview how many quarantined files would be affected by each action."""
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
        """Apply a quarantine action to specific quarantined files by ID."""
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
            description="FQL filter used to select quarantined files.",
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
        """Apply a quarantine action to quarantined files selected by query."""
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
