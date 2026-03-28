"""
On-Demand Scans module for Falcon MCP Server.

This module provides tools for ODS hunt, scan orchestration, and malicious file
review workflows.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.utils import normalize_field_value, prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class ODSModule(BaseModule):
    """Module for on-demand scan investigation and orchestration workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_ods_scans, name="search_ods_scans")
        self._add_tool(server=server, method=self.get_ods_scan_details, name="get_ods_scan_details")
        self._add_tool(server=server, method=self.search_ods_scan_hosts, name="search_ods_scan_hosts")
        self._add_tool(server=server, method=self.get_ods_scan_host_details, name="get_ods_scan_host_details")
        self._add_tool(
            server=server,
            method=self.launch_ods_scan,
            name="launch_ods_scan",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.cancel_ods_scans,
            name="cancel_ods_scans",
            annotations=DESTRUCTIVE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_ods_scheduled_scans,
            name="search_ods_scheduled_scans",
        )
        self._add_tool(
            server=server,
            method=self.get_ods_scheduled_scan_details,
            name="get_ods_scheduled_scan_details",
        )
        self._add_tool(
            server=server,
            method=self.schedule_ods_scan,
            name="schedule_ods_scan",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_ods_scheduled_scans,
            name="delete_ods_scheduled_scans",
            annotations=DESTRUCTIVE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_ods_malicious_files,
            name="search_ods_malicious_files",
        )
        self._add_tool(
            server=server,
            method=self.get_ods_malicious_file_details,
            name="get_ods_malicious_file_details",
        )

    def search_ods_scans(
        self,
        filter: str | None = Field(default=None, description="FQL filter for ODS scans."),
        limit: int = Field(default=10, ge=1, le=500, description="Maximum number of scan IDs to return."),
        offset: int | None = Field(default=None, description="Starting index of overall result set from which to return IDs."),
        sort: str | None = Field(default=None, description="FQL sort for ODS scans, such as `created_on|desc`."),
    ) -> list[dict[str, Any]]:
        """Search ODS scans and return full scan details."""
        scan_ids = self._base_search_api_call(
            operation="query_scans",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search ODS scans",
            default_result=[],
        )

        if self._is_error(scan_ids):
            return [scan_ids]

        if not scan_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scans_by_scan_ids_v2",
            ids=scan_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_ods_scan_details(
        self,
        ids: list[str] = Field(description="ODS scan ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get full details for one or more ODS scans."""
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scans_by_scan_ids_v2",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_ods_scan_hosts(
        self,
        filter: str | None = Field(default=None, description="FQL filter for ODS scan-host metadata."),
        limit: int = Field(default=10, ge=1, le=500, description="Maximum number of scan-host IDs to return."),
        offset: int | None = Field(default=None, description="Starting index of overall result set from which to return IDs."),
        sort: str | None = Field(default=None, description="FQL sort for ODS scan hosts, such as `last_updated|desc`."),
    ) -> list[dict[str, Any]]:
        """Search ODS scan-host records and return full details."""
        scan_host_ids = self._base_search_api_call(
            operation="query_scan_host_metadata",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search ODS scan hosts",
            default_result=[],
        )

        if self._is_error(scan_host_ids):
            return [scan_host_ids]

        if not scan_host_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scan_host_metadata_by_ids",
            ids=scan_host_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_ods_scan_host_details(
        self,
        ids: list[str] = Field(description="ODS scan-host metadata ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get full details for one or more ODS scan-host records."""
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scan_host_metadata_by_ids",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def launch_ods_scan(
        self,
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full ODS scan creation payload. If omitted, one is built from the individual parameters below.",
        ),
        hosts: list[str] | None = Field(default=None, description="Host AID(s) to scan."),
        host_groups: list[str] | None = Field(default=None, description="Host group ID(s) to scan."),
        file_paths: list[str] | None = Field(default=None, description="Optional file paths to target during the scan."),
        description: str | None = Field(default=None, description="Human-readable scan description."),
        initiated_from: str | None = Field(default=None, description="Source label for the scan request."),
        quarantine: bool | None = Field(default=None, description="Quarantine malicious files found by the scan."),
        endpoint_notification: bool | None = Field(default=None, description="Whether the endpoint should display a scan notification."),
        scan_exclusions: list[str] | None = Field(default=None, description="File path globs to exclude from the scan."),
        max_duration: int | None = Field(default=None, description="Maximum scan duration in seconds."),
        max_file_size: int | None = Field(default=None, description="Maximum file size to scan in bytes."),
        cpu_priority: int | None = Field(default=None, description="CPU priority for the scan job."),
        pause_duration: int | None = Field(default=None, description="Pause duration in seconds during the scan."),
        start_timestamp: str | None = Field(default=None, description="Optional ISO 8601 timestamp to delay scan start."),
        interval: int | None = Field(default=None, description="Optional interval override in seconds for create-scan payloads."),
        ignored_by_channelfile: bool | None = Field(default=None, description="Whether the scan should be ignored by Channel File logic."),
        sensor_ml_level_detection: int | None = Field(default=None, description="Sensor ML detection level."),
        sensor_ml_level_prevention: int | None = Field(default=None, description="Sensor ML prevention level."),
        cloud_ml_level_detection: int | None = Field(default=None, description="Cloud ML detection level."),
        cloud_ml_level_prevention: int | None = Field(default=None, description="Cloud ML prevention level."),
    ) -> list[dict[str, Any]]:
        """Create and start an on-demand scan."""
        body = normalize_field_value(body)
        payload = body or self._build_scan_payload(
            scheduled=False,
            hosts=hosts,
            host_groups=host_groups,
            file_paths=file_paths,
            description=description,
            initiated_from=initiated_from,
            quarantine=quarantine,
            endpoint_notification=endpoint_notification,
            scan_exclusions=scan_exclusions,
            scan_inclusions=None,
            max_duration=max_duration,
            max_file_size=max_file_size,
            cpu_priority=cpu_priority,
            pause_duration=pause_duration,
            start_timestamp=start_timestamp,
            interval=interval,
            ignored_by_channelfile=ignored_by_channelfile,
            sensor_ml_level_detection=sensor_ml_level_detection,
            sensor_ml_level_prevention=sensor_ml_level_prevention,
            cloud_ml_level_detection=cloud_ml_level_detection,
            cloud_ml_level_prevention=cloud_ml_level_prevention,
        )

        result = self._base_query_api_call(
            operation="create_scan",
            body_params=payload,
            error_message="Failed to launch ODS scan",
        )

        if self._is_error(result):
            return [result]

        return result

    def cancel_ods_scans(
        self,
        ids: list[str] = Field(description="ODS scan ID(s) to cancel."),
    ) -> list[dict[str, Any]]:
        """Cancel one or more running ODS scans."""
        result = self._base_query_api_call(
            operation="cancel_scans",
            body_params={"ids": ids},
            error_message="Failed to cancel ODS scans",
        )

        if self._is_error(result):
            return [result]

        return result

    def search_ods_scheduled_scans(
        self,
        filter: str | None = Field(default=None, description="FQL filter for scheduled ODS scans."),
        limit: int = Field(default=10, ge=1, le=500, description="Maximum number of scheduled scan IDs to return."),
        offset: int | None = Field(default=None, description="Starting index of overall result set from which to return IDs."),
        sort: str | None = Field(default=None, description="FQL sort for scheduled scans, such as `schedule.start_timestamp|desc`."),
    ) -> list[dict[str, Any]]:
        """Search scheduled ODS scans and return full schedule details."""
        scan_ids = self._base_search_api_call(
            operation="query_scheduled_scans",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search scheduled ODS scans",
            default_result=[],
        )

        if self._is_error(scan_ids):
            return [scan_ids]

        if not scan_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scheduled_scans_by_scan_ids",
            ids=scan_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_ods_scheduled_scan_details(
        self,
        ids: list[str] = Field(description="Scheduled ODS scan ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get full details for one or more scheduled ODS scans."""
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="get_scheduled_scans_by_scan_ids",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def schedule_ods_scan(
        self,
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full scheduled ODS scan payload. If omitted, one is built from the individual parameters below.",
        ),
        hosts: list[str] | None = Field(default=None, description="Optional host AID(s) to include if your tenant supports direct host scheduling."),
        host_groups: list[str] | None = Field(default=None, description="Host group ID(s) to scan."),
        file_paths: list[str] | None = Field(default=None, description="Optional file paths to target during the scan."),
        description: str | None = Field(default=None, description="Human-readable scheduled scan description."),
        initiated_from: str | None = Field(default=None, description="Source label for the scheduled scan request."),
        quarantine: bool | None = Field(default=None, description="Quarantine malicious files found by the scan."),
        endpoint_notification: bool | None = Field(default=None, description="Whether the endpoint should display a scan notification."),
        scan_exclusions: list[str] | None = Field(default=None, description="File path globs to exclude from the scan."),
        scan_inclusions: list[str] | None = Field(default=None, description="File path globs to explicitly include in the scan."),
        max_duration: int | None = Field(default=None, description="Maximum scan duration in seconds."),
        max_file_size: int | None = Field(default=None, description="Maximum file size to scan in bytes."),
        cpu_priority: int | None = Field(default=None, description="CPU priority for the scan job."),
        pause_duration: int | None = Field(default=None, description="Pause duration in seconds during the scan."),
        start_timestamp: str | None = Field(default=None, description="ISO 8601 timestamp for the first scheduled run."),
        interval: int | None = Field(default=None, description="Schedule interval in seconds."),
        ignored_by_channelfile: bool | None = Field(default=None, description="Whether the scheduled scan should be ignored by Channel File logic."),
        sensor_ml_level_detection: int | None = Field(default=None, description="Sensor ML detection level."),
        sensor_ml_level_prevention: int | None = Field(default=None, description="Sensor ML prevention level."),
        cloud_ml_level_detection: int | None = Field(default=None, description="Cloud ML detection level."),
        cloud_ml_level_prevention: int | None = Field(default=None, description="Cloud ML prevention level."),
    ) -> list[dict[str, Any]]:
        """Create or update a scheduled on-demand scan definition."""
        body = normalize_field_value(body)
        payload = body or self._build_scan_payload(
            scheduled=True,
            hosts=hosts,
            host_groups=host_groups,
            file_paths=file_paths,
            description=description,
            initiated_from=initiated_from,
            quarantine=quarantine,
            endpoint_notification=endpoint_notification,
            scan_exclusions=scan_exclusions,
            scan_inclusions=scan_inclusions,
            max_duration=max_duration,
            max_file_size=max_file_size,
            cpu_priority=cpu_priority,
            pause_duration=pause_duration,
            start_timestamp=start_timestamp,
            interval=interval,
            ignored_by_channelfile=ignored_by_channelfile,
            sensor_ml_level_detection=sensor_ml_level_detection,
            sensor_ml_level_prevention=sensor_ml_level_prevention,
            cloud_ml_level_detection=cloud_ml_level_detection,
            cloud_ml_level_prevention=cloud_ml_level_prevention,
        )

        result = self._base_query_api_call(
            operation="schedule_scan",
            body_params=payload,
            error_message="Failed to schedule ODS scan",
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_ods_scheduled_scans(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Scheduled scan ID(s) to delete.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter to delete scheduled scans by query instead of IDs.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete scheduled ODS scan definitions by ID or filter."""
        ids = normalize_field_value(ids)
        filter = normalize_field_value(filter)

        if not ids and not filter:
            return [
                _format_error_response(
                    "Provide at least one of `ids` or `filter` when deleting scheduled ODS scans."
                )
            ]

        result = self._base_query_api_call(
            operation="delete_scheduled_scans",
            query_params={
                "ids": ids,
                "filter": filter,
            },
            error_message="Failed to delete scheduled ODS scans",
        )

        if self._is_error(result):
            return [result]

        return result

    def search_ods_malicious_files(
        self,
        filter: str | None = Field(default=None, description="FQL filter for malicious files found by ODS."),
        limit: int = Field(default=10, ge=1, le=500, description="Maximum number of malicious file IDs to return."),
        offset: int | None = Field(default=None, description="Starting index of overall result set from which to return IDs."),
        sort: str | None = Field(default=None, description="FQL sort for malicious files, such as `last_updated|desc`."),
    ) -> list[dict[str, Any]]:
        """Search malicious files found by ODS and return full details."""
        file_ids = self._base_search_api_call(
            operation="query_malicious_files",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search ODS malicious files",
            default_result=[],
        )

        if self._is_error(file_ids):
            return [file_ids]

        if not file_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_malicious_files_by_ids",
            ids=file_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_ods_malicious_file_details(
        self,
        ids: list[str] = Field(description="ODS malicious file ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get full details for one or more malicious files found by ODS."""
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="get_malicious_files_by_ids",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def _build_scan_payload(
        self,
        *,
        scheduled: bool,
        hosts: list[str] | None,
        host_groups: list[str] | None,
        file_paths: list[str] | None,
        description: str | None,
        initiated_from: str | None,
        quarantine: bool | None,
        endpoint_notification: bool | None,
        scan_exclusions: list[str] | None,
        scan_inclusions: list[str] | None,
        max_duration: int | None,
        max_file_size: int | None,
        cpu_priority: int | None,
        pause_duration: int | None,
        start_timestamp: str | None,
        interval: int | None,
        ignored_by_channelfile: bool | None,
        sensor_ml_level_detection: int | None,
        sensor_ml_level_prevention: int | None,
        cloud_ml_level_detection: int | None,
        cloud_ml_level_prevention: int | None,
    ) -> dict[str, Any]:
        payload = prepare_api_parameters(
            {
                "hosts": hosts,
                "host_groups": host_groups,
                "file_paths": file_paths,
                "description": description,
                "initiated_from": initiated_from,
                "quarantine": quarantine,
                "endpoint_notification": endpoint_notification,
                "scan_exclusions": scan_exclusions,
                "scan_inclusions": scan_inclusions if scheduled else None,
                "max_duration": max_duration,
                "max_file_size": max_file_size,
                "cpu_priority": cpu_priority,
                "pause_duration": pause_duration,
                "sensor_ml_level_detection": sensor_ml_level_detection,
                "sensor_ml_level_prevention": sensor_ml_level_prevention,
                "cloud_ml_level_detection": cloud_ml_level_detection,
                "cloud_ml_level_prevention": cloud_ml_level_prevention,
            }
        )

        schedule_fields = prepare_api_parameters(
            {
                "start_timestamp": start_timestamp,
                "interval": interval,
                "ignored_by_channelfile": ignored_by_channelfile,
            }
        )

        if scheduled:
            if schedule_fields:
                payload["schedule"] = schedule_fields
        else:
            payload.update(schedule_fields)

        return payload
