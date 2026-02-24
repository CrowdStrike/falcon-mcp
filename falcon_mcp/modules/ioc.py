"""
IOC module for Falcon MCP Server.

This module provides tools for searching, creating, and deleting custom IOCs
using Falcon IOC Service Collection endpoints.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ioc import SEARCH_IOCS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class IOCModule(BaseModule):
    """Module for managing custom IOCs."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_iocs,
            name="search_iocs",
        )

        self._add_tool(
            server=server,
            method=self.add_ioc,
            name="add_ioc",
        )

        self._add_tool(
            server=server,
            method=self.remove_iocs,
            name="remove_iocs",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_iocs_fql_resource = TextResource(
            uri=AnyUrl("falcon://ioc/search/fql-guide"),
            name="falcon_search_iocs_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_iocs` tool.",
            text=SEARCH_IOCS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_iocs_fql_resource,
        )

    def search_iocs(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit IOC search results. IMPORTANT: use the `falcon://ioc/search/fql-guide` resource when building this filter parameter.",
            examples={"type:'domain'+expired:false", "source:'mcp'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of IOC IDs to return from search. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort IOCs using FQL sort syntax.

                Common fields include:
                action, applied_globally, created_on, expiration, modified_on,
                severity_number, source, type, value

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'modified_on.desc', 'severity_number|desc'
            """).strip(),
            examples={"modified_on.desc", "severity_number|desc"},
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token for large result sets. Use the `after` value returned by the previous search call.",
        ),
        from_parent: bool | None = Field(
            default=None,
            description="Return indicators from the MSSP parent when applicable.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search custom IOCs and return full IOC details.

        IMPORTANT: You must use the `falcon://ioc/search/fql-guide` resource
        when you need to use the `filter` parameter.
        """
        filter = self._normalize_field_value(filter)
        limit = self._normalize_field_value(limit)
        offset = self._normalize_field_value(offset)
        sort = self._normalize_field_value(sort)
        after = self._normalize_field_value(after)
        from_parent = self._normalize_field_value(from_parent)

        indicator_ids = self._base_search_api_call(
            operation="indicator_search_v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
                "from_parent": from_parent,
            },
            error_message="Failed to search IOCs",
        )

        if self._is_error(indicator_ids):
            return self._format_fql_error_response(
                [indicator_ids], filter, SEARCH_IOCS_FQL_DOCUMENTATION
            )

        if not indicator_ids:
            return self._format_fql_error_response([], filter, SEARCH_IOCS_FQL_DOCUMENTATION)

        details = self._base_get_by_ids(
            operation="indicator_get_v1",
            ids=indicator_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def add_ioc(
        self,
        type: str | None = Field(
            default=None,
            description="IOC type for single IOC creation. Common values: domain, ipv4, ipv6, md5, sha256. Required when `indicators` is not provided.",
        ),
        value: str | None = Field(
            default=None,
            description="IOC value for single IOC creation. Required when `indicators` is not provided.",
        ),
        action: str = Field(
            default="detect",
            description="Action for single IOC creation. Example values: detect, prevent, no_action.",
        ),
        source: str = Field(
            default="mcp",
            description="Source label for the IOC.",
        ),
        severity: str | None = Field(
            default=None,
            description="Severity label for single IOC creation.",
        ),
        description: str | None = Field(
            default=None,
            description="Description text for single IOC creation.",
        ),
        expiration: str | None = Field(
            default=None,
            description="Expiration timestamp in UTC (ISO 8601). Example: 2026-12-31T23:59:59Z",
        ),
        applied_globally: bool | None = Field(
            default=None,
            description="Whether the IOC is applied globally.",
        ),
        mobile_action: str | None = Field(
            default=None,
            description="Action to apply on mobile platforms.",
        ),
        platforms: list[str] | None = Field(
            default=None,
            description="Platform list for single IOC creation.",
        ),
        host_groups: list[str] | None = Field(
            default=None,
            description="Host groups for scoped IOC application.",
        ),
        tags: list[str] | None = Field(
            default=None,
            description="Falcon grouping tags to attach to the IOC.",
        ),
        metadata: dict[str, Any] | None = Field(
            default=None,
            description="Metadata dictionary for the IOC. Example: {'filename': 'evil.exe'}",
        ),
        filename: str | None = Field(
            default=None,
            description="Convenience shortcut for metadata filename. Merged into `metadata`.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment for IOC creation.",
        ),
        indicators: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional bulk IOC payload. If provided, single IOC fields are ignored.",
        ),
        ignore_warnings: bool = Field(
            default=False,
            description="Set to true to ignore warnings and create all submitted IOCs.",
        ),
        retrodetects: bool | None = Field(
            default=None,
            description="Whether to submit IOCs to retrodetect processing.",
        ),
    ) -> list[dict[str, Any]]:
        """Create one or more custom IOCs."""
        type = self._normalize_field_value(type)
        value = self._normalize_field_value(value)
        action = self._normalize_field_value(action)
        source = self._normalize_field_value(source)
        severity = self._normalize_field_value(severity)
        description = self._normalize_field_value(description)
        expiration = self._normalize_field_value(expiration)
        applied_globally = self._normalize_field_value(applied_globally)
        mobile_action = self._normalize_field_value(mobile_action)
        platforms = self._normalize_field_value(platforms)
        host_groups = self._normalize_field_value(host_groups)
        tags = self._normalize_field_value(tags)
        metadata = self._normalize_field_value(metadata)
        filename = self._normalize_field_value(filename)
        comment = self._normalize_field_value(comment)
        indicators = self._normalize_field_value(indicators)
        ignore_warnings = self._normalize_field_value(ignore_warnings)
        retrodetects = self._normalize_field_value(retrodetects)

        payload_or_error = self._build_add_ioc_payload(
            type=type,
            value=value,
            action=action,
            source=source,
            severity=severity,
            description=description,
            expiration=expiration,
            applied_globally=applied_globally,
            mobile_action=mobile_action,
            platforms=platforms,
            host_groups=host_groups,
            tags=tags,
            metadata=metadata,
            filename=filename,
            comment=comment,
            indicators=indicators,
        )

        if self._is_error(payload_or_error):
            return [payload_or_error]

        result = self._base_query_api_call(
            operation="indicator_create_v1",
            query_params={
                "ignore_warnings": ignore_warnings,
                "retrodetects": retrodetects,
            },
            body_params=payload_or_error,
            error_message="Failed to add IOC",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def remove_iocs(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="IOC IDs to remove. Use this when deleting specific IOCs.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL expression for bulk IOC removal. If both `filter` and `ids` are provided, `filter` takes precedence.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment describing why these IOCs are being removed.",
        ),
        from_parent: bool | None = Field(
            default=None,
            description="Limit action to IOCs originating from the MSSP parent.",
        ),
    ) -> list[dict[str, Any]]:
        """Remove custom IOCs by IDs or FQL filter."""
        ids = self._normalize_field_value(ids)
        filter = self._normalize_field_value(filter)
        comment = self._normalize_field_value(comment)
        from_parent = self._normalize_field_value(from_parent)

        if not ids and not filter:
            return [
                _format_error_response(
                    "Either `ids` or `filter` must be provided to remove IOCs.",
                    operation="indicator_delete_v1",
                )
            ]

        result = self._base_query_api_call(
            operation="indicator_delete_v1",
            query_params={
                "ids": ids,
                "filter": filter,
                "comment": comment,
                "from_parent": from_parent,
            },
            error_message="Failed to remove IOCs",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _build_add_ioc_payload(
        self,
        type: str | None,
        value: str | None,
        action: str,
        source: str,
        severity: str | None,
        description: str | None,
        expiration: str | None,
        applied_globally: bool | None,
        mobile_action: str | None,
        platforms: list[str] | None,
        host_groups: list[str] | None,
        tags: list[str] | None,
        metadata: dict[str, Any] | None,
        filename: str | None,
        comment: str | None,
        indicators: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        """Build IOC create payload or return a validation error payload."""
        if indicators:
            payload: dict[str, Any] = {"indicators": indicators}
            if comment:
                payload["comment"] = comment
            return payload

        if not type or not value:
            return _format_error_response(
                "`type` and `value` are required when `indicators` is not provided.",
                operation="indicator_create_v1",
            )

        indicator: dict[str, Any] = {
            "type": type,
            "value": value,
            "action": action,
            "source": source,
        }

        optional_values = {
            "severity": severity,
            "description": description,
            "expiration": expiration,
            "applied_globally": applied_globally,
            "mobile_action": mobile_action,
            "platforms": platforms,
            "host_groups": host_groups,
            "tags": tags,
        }
        for key, value_ in optional_values.items():
            if value_ is not None:
                indicator[key] = value_

        if metadata:
            indicator["metadata"] = metadata
        if filename:
            existing_metadata = indicator.get("metadata", {})
            if not isinstance(existing_metadata, dict):
                existing_metadata = {}
            existing_metadata["filename"] = filename
            indicator["metadata"] = existing_metadata

        payload = {"indicators": [indicator]}
        if comment:
            payload["comment"] = comment

        return payload

    @staticmethod
    def _normalize_field_value(value: Any) -> Any:
        """Normalize direct function-call defaults produced by pydantic Field()."""
        if isinstance(value, FieldInfo):
            return value.default
        return value
