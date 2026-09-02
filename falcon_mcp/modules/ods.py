"""On-Demand Scan module for Falcon MCP Server.

This module searches ODS results and manages immediate and scheduled scans.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ods import (
    SEARCH_ODS_MALICIOUS_FILES_FQL_DOCUMENTATION,
    SEARCH_ODS_SCAN_HOSTS_FQL_DOCUMENTATION,
    SEARCH_ODS_SCANS_FQL_DOCUMENTATION,
    SEARCH_ODS_SCHEDULED_SCANS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class ODSModule(BaseModule):
    """Module for searching and managing Falcon On-Demand Scans."""

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(server=server, method=self.search_ods_scans, name="search_ods_scans")
        self._add_tool(server=server, method=self.search_ods_scan_hosts, name="search_ods_scan_hosts")
        self._add_tool(server=server, method=self.search_ods_malicious_files, name="search_ods_malicious_files")
        self._add_tool(server=server, method=self.search_ods_scheduled_scans, name="search_ods_scheduled_scans")
        self._add_tool(
            server=server,
            method=self.launch_ods_scan,
            name="launch_ods_scan",
            annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True),
        )
        self._add_tool(
            server=server,
            method=self.cancel_ods_scans,
            name="cancel_ods_scans",
            annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True),
        )
        self._add_tool(
            server=server,
            method=self.schedule_ods_scan,
            name="schedule_ods_scan",
            annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True),
        )
        self._add_tool(
            server=server,
            method=self.delete_ods_scheduled_scans,
            name="delete_ods_scheduled_scans",
            annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True),
        )

    def register_resources(self, server: FastMCP) -> None:
        resources = [
            TextResource(
                uri=AnyUrl("falcon://ods/scans/fql-guide"),
                name="falcon_search_ods_scans_fql_guide",
                description="FQL guide for the falcon_search_ods_scans tool.",
                text=SEARCH_ODS_SCANS_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://ods/scan-hosts/fql-guide"),
                name="falcon_search_ods_scan_hosts_fql_guide",
                description="FQL guide for the falcon_search_ods_scan_hosts tool.",
                text=SEARCH_ODS_SCAN_HOSTS_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://ods/malicious-files/fql-guide"),
                name="falcon_search_ods_malicious_files_fql_guide",
                description="FQL guide for the falcon_search_ods_malicious_files tool.",
                text=SEARCH_ODS_MALICIOUS_FILES_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://ods/scheduled-scans/fql-guide"),
                name="falcon_search_ods_scheduled_scans_fql_guide",
                description="FQL guide for the falcon_search_ods_scheduled_scans tool.",
                text=SEARCH_ODS_SCHEDULED_SCANS_FQL_DOCUMENTATION,
            ),
        ]
        for resource in resources:
            self._add_resource(server=server, resource=resource)

    def _search_and_hydrate(
        self,
        query_operation: str,
        get_operation: str,
        filter: str | None,
        limit: int,
        offset: int | None,
        sort: str | None,
        guide: str,
        label: str,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        ids, pagination = self._base_search_with_meta(
            operation=query_operation,
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message=f"Failed to search {label}",
        )
        if self._is_error(ids):
            return self._format_fql_error_response([ids], filter, guide)
        if not ids:
            return self._build_pagination_envelope([], pagination, filter)
        details = self._base_get_by_ids(get_operation, ids, use_params=True)
        if self._is_error(details):
            return [details]
        details = self._reorder_by_ids(ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def search_ods_scans(
        self,
        filter: str | None = Field(default=None, description="FQL filter. See `falcon://ods/scans/fql-guide`."),
        limit: int = Field(default=10, ge=1, le=500),
        offset: int | None = Field(default=None, ge=0),
        sort: str | None = Field(default="created_on|desc"),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Search ODS scans and return full scan entities with pagination."""
        return self._search_and_hydrate(
            query_operation="query_scans",
            get_operation="get_scans_by_scan_ids_v2",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            guide=SEARCH_ODS_SCANS_FQL_DOCUMENTATION,
            label="ODS scans",
        )

    def search_ods_scan_hosts(
        self,
        filter: str | None = Field(default=None, description="FQL filter. See `falcon://ods/scan-hosts/fql-guide`."),
        limit: int = Field(default=10, ge=1, le=500),
        offset: int | None = Field(default=None, ge=0),
        sort: str | None = Field(default="last_updated|desc"),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Search per-host ODS scan results and return full metadata."""
        return self._search_and_hydrate(
            query_operation="query_scan_host_metadata",
            get_operation="get_scan_host_metadata_by_ids",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            guide=SEARCH_ODS_SCAN_HOSTS_FQL_DOCUMENTATION,
            label="ODS scan hosts",
        )

    def search_ods_malicious_files(
        self,
        filter: str | None = Field(default=None, description="FQL filter. See `falcon://ods/malicious-files/fql-guide`."),
        limit: int = Field(default=10, ge=1, le=500),
        offset: int | None = Field(default=None, ge=0),
        sort: str | None = Field(default="last_updated|desc"),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Search malicious files found by ODS and return full file records."""
        return self._search_and_hydrate(
            query_operation="query_malicious_files",
            get_operation="get_malicious_files_by_ids",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            guide=SEARCH_ODS_MALICIOUS_FILES_FQL_DOCUMENTATION,
            label="ODS malicious files",
        )

    def search_ods_scheduled_scans(
        self,
        filter: str | None = Field(default=None, description="FQL filter. See `falcon://ods/scheduled-scans/fql-guide`."),
        limit: int = Field(default=10, ge=1, le=500),
        offset: int | None = Field(default=None, ge=0),
        sort: str | None = Field(default="schedule.start_timestamp|desc"),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Search scheduled ODS scans and return full schedule definitions."""
        return self._search_and_hydrate(
            query_operation="query_scheduled_scans",
            get_operation="get_scheduled_scans_by_scan_ids",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            guide=SEARCH_ODS_SCHEDULED_SCANS_FQL_DOCUMENTATION,
            label="ODS scheduled scans",
        )

    @staticmethod
    def _scan_body(
        hosts: list[str] | None,
        host_groups: list[str] | None,
        file_paths: list[str],
        description: str | None,
        quarantine: bool,
        cpu_priority: int | None,
        endpoint_notification: bool | None,
        max_duration: int | None,
        max_file_size: int | None,
        pause_duration: int | None,
        scan_inclusions: list[str] | None,
        scan_exclusions: list[str] | None,
    ) -> dict[str, Any] | None:
        if not hosts and not host_groups:
            return None
        if not file_paths:
            return None
        return prepare_api_parameters({
            "hosts": hosts,
            "host_groups": host_groups,
            "file_paths": file_paths,
            "description": description,
            "quarantine": quarantine,
            "cpu_priority": cpu_priority,
            "endpoint_notification": endpoint_notification,
            "max_duration": max_duration,
            "max_file_size": max_file_size,
            "pause_duration": pause_duration,
            "scan_inclusions": scan_inclusions,
            "scan_exclusions": scan_exclusions,
            "initiated_from": "falcon-mcp",
        })

    def launch_ods_scan(
        self,
        file_paths: list[str] = Field(description="Absolute endpoint paths to scan."),
        hosts: list[str] | None = Field(default=None, description="Host AIDs to scan."),
        host_groups: list[str] | None = Field(default=None, description="Host-group IDs to scan."),
        description: str | None = None,
        quarantine: bool = Field(default=False, description="Quarantine detected malicious files."),
        cpu_priority: int | None = None,
        endpoint_notification: bool | None = None,
        max_duration: int | None = Field(default=None, ge=1),
        max_file_size: int | None = Field(default=None, ge=1),
        pause_duration: int | None = Field(default=None, ge=0),
        scan_inclusions: list[str] | None = None,
        scan_exclusions: list[str] | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Start an ODS scan against explicit hosts or host groups."""
        body = self._scan_body(hosts, host_groups, file_paths, description, quarantine, cpu_priority, endpoint_notification, max_duration, max_file_size, pause_duration, scan_inclusions, scan_exclusions)
        if body is None:
            return _format_error_response("Provide at least one host or host group and at least one file path.")
        response = self.client.command("create_scan", body=body)
        return handle_api_response(response, operation="create_scan", error_message="Failed to launch ODS scan", default_result=[])

    def cancel_ods_scans(self, ids: list[str] = Field(min_length=1, description="Scan IDs to cancel.")) -> list[dict[str, Any]] | dict[str, Any]:
        """Cancel active ODS scans by explicit scan ID."""
        response = self.client.command("cancel_scans", body={"ids": ids})
        return handle_api_response(response, operation="cancel_scans", error_message="Failed to cancel ODS scans", default_result=[])

    def schedule_ods_scan(
        self,
        file_paths: list[str] = Field(description="Absolute endpoint paths to scan."),
        schedule: dict[str, Any] = Field(description="Schedule with start_timestamp, interval, and optional ignored_by_channelfile."),
        hosts: list[str] | None = None,
        host_groups: list[str] | None = None,
        description: str | None = None,
        quarantine: bool = False,
        cpu_priority: int | None = None,
        endpoint_notification: bool | None = None,
        max_duration: int | None = Field(default=None, ge=1),
        max_file_size: int | None = Field(default=None, ge=1),
        pause_duration: int | None = Field(default=None, ge=0),
        scan_inclusions: list[str] | None = None,
        scan_exclusions: list[str] | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a recurring or future ODS scan schedule."""
        if not schedule.get("start_timestamp") or schedule.get("interval") is None:
            return _format_error_response("Schedule requires `start_timestamp` and `interval`.")
        body = self._scan_body(hosts, host_groups, file_paths, description, quarantine, cpu_priority, endpoint_notification, max_duration, max_file_size, pause_duration, scan_inclusions, scan_exclusions)
        if body is None:
            return _format_error_response("Provide at least one host or host group and at least one file path.")
        body["schedule"] = schedule
        response = self.client.command("schedule_scan", body=body)
        return handle_api_response(response, operation="schedule_scan", error_message="Failed to schedule ODS scan", default_result=[])

    def delete_ods_scheduled_scans(self, ids: list[str] = Field(min_length=1, description="Scheduled-scan IDs to delete.")) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete ODS schedules by explicit IDs."""
        response = self.client.command("delete_scheduled_scans", parameters={"ids": ids})
        return handle_api_response(response, operation="delete_scheduled_scans", error_message="Failed to delete ODS schedules", default_result=[])
