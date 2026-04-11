"""
Falcon Sandbox module for Falcon MCP Server.

This module provides tools for sample submission, sandbox report search, and
submission/report status review.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import (
    normalize_field_value,
    prepare_api_parameters,
    resolve_binary_upload_input,
)
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.sandbox import (
    SEARCH_SANDBOX_REPORTS_EMBEDDED_FQL_SYNTAX,
    SEARCH_SANDBOX_REPORTS_FQL_DOCUMENTATION,
    SEARCH_SANDBOX_SUBMISSIONS_EMBEDDED_FQL_SYNTAX,
    SEARCH_SANDBOX_SUBMISSIONS_FQL_DOCUMENTATION,
)

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class SandboxModule(BaseModule):
    """Module for Falcon Sandbox submission and report workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.upload_sandbox_sample,
            name="upload_sandbox_sample",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.check_sandbox_samples,
            name="check_sandbox_samples",
        )
        self._add_tool(
            server=server,
            method=self.submit_sandbox_analysis,
            name="submit_sandbox_analysis",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_sandbox_submissions,
            name="search_sandbox_submissions",
        )
        self._add_tool(
            server=server,
            method=self.get_sandbox_submission_details,
            name="get_sandbox_submission_details",
        )
        self._add_tool(
            server=server,
            method=self.search_sandbox_reports,
            name="search_sandbox_reports",
        )
        self._add_tool(
            server=server,
            method=self.get_sandbox_report_summaries,
            name="get_sandbox_report_summaries",
        )
        self._add_tool(
            server=server,
            method=self.get_sandbox_report_details,
            name="get_sandbox_report_details",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        resources = [
            TextResource(
                uri=AnyUrl("falcon://sandbox/submissions/search/fql-guide"),
                name="falcon_search_sandbox_submissions_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_sandbox_submissions` tool.",
                text=SEARCH_SANDBOX_SUBMISSIONS_FQL_DOCUMENTATION,
            ),
            TextResource(
                uri=AnyUrl("falcon://sandbox/reports/search/fql-guide"),
                name="falcon_search_sandbox_reports_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_sandbox_reports` tool.",
                text=SEARCH_SANDBOX_REPORTS_FQL_DOCUMENTATION,
            ),
        ]

        for resource in resources:
            self._add_resource(server, resource)

    def upload_sandbox_sample(
        self,
        file_name: str | None = Field(
            default=None,
            description="Name of the sample file. Required when using `file_base64`. Optional when `file_path` is provided.",
        ),
        file_path: str | None = Field(
            default=None,
            description="Absolute or relative path to a local file to upload for Falcon Sandbox.",
        ),
        file_base64: str | None = Field(
            default=None,
            description="Base64-encoded sample content. Provide this instead of `file_path` when the file is already in memory.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional analyst comment stored with the uploaded sample.",
        ),
        is_confidential: bool | None = Field(
            default=True,
            description="Whether the uploaded sample should remain visible only to your tenant.",
        ),
    ) -> list[dict[str, Any]]:
        """Upload a local file or base64 payload directly to Falcon Sandbox.

        Provide exactly one of `file_path` or `file_base64`. Use this tool when
        you need a sample available in Sandbox storage before checking existing
        hashes or creating a detonation request.
        """
        try:
            sample_bytes, upload_name = resolve_binary_upload_input(
                file_path=file_path,
                file_base64=file_base64,
                file_name=file_name,
            )
        except ValueError as exc:
            return [_format_error_response(str(exc))]

        response = self.client.command(
            "UploadSampleV2",
            files=[("sample", (upload_name, sample_bytes))],
            data=prepare_api_parameters(
                {
                    "file_name": upload_name,
                    "comment": comment,
                    "is_confidential": is_confidential,
                }
            ),
        )

        result = handle_api_response(
            response,
            operation="UploadSampleV2",
            error_message="Failed to upload Falcon Sandbox sample",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def check_sandbox_samples(
        self,
        sha256s: list[str] = Field(description="SHA256 value(s) to check for Sandbox sample availability."),
    ) -> list[dict[str, Any]]:
        """Check which SHA256 hashes already exist in Falcon Sandbox storage."""
        result = self._base_query_api_call(
            operation="QuerySampleV1",
            body_params={"sha256s": sha256s},
            error_message="Failed to query Falcon Sandbox samples",
        )

        if self._is_error(result):
            return [result]

        return result

    def submit_sandbox_analysis(
        self,
        sha256: str | None = Field(
            default=None,
            description="Uploaded sample SHA256 to analyze. Use this or `url`, but not both.",
        ),
        url: str | None = Field(
            default=None,
            description="URL to analyze. Use this or `sha256`, but not both.",
        ),
        submit_name: str | None = Field(
            default=None,
            description="Optional display name used for file type detection and analysis.",
        ),
        environment_id: int | None = Field(
            default=None,
            description="Sandbox environment ID. Common values include 140 (Windows 11), 160 (Windows 10), and 310 (Linux Ubuntu 20).",
        ),
        network_settings: str | None = Field(
            default=None,
            description="Network profile for the analysis. Examples: `default`, `tor`, `simulated`, `offline`.",
        ),
        action_script: str | None = Field(
            default=None,
            description="Optional Falcon Sandbox action script such as `default` or `default_maxantievasion`.",
        ),
        command_line: str | None = Field(
            default=None,
            description="Optional command line to pass at runtime.",
        ),
        document_password: str | None = Field(
            default=None,
            description="Optional document password for Office or PDF submissions.",
        ),
        system_date: str | None = Field(
            default=None,
            description="Optional yyyy-MM-dd date to set inside the sandbox.",
        ),
        system_time: str | None = Field(
            default=None,
            description="Optional HH:mm time to set inside the sandbox.",
        ),
        user_tags: list[str] | None = Field(
            default=None,
            description="Optional analyst-defined tags stored with the submission.",
        ),
        send_email_notification: bool | None = Field(
            default=None,
            description="Whether Falcon should send an email notification when analysis completes.",
        ),
        aid: str | None = Field(
            default=None,
            description="Optional Falcon agent ID associated with the sample or URL.",
        ),
    ) -> list[dict[str, Any]]:
        """Submit a URL or uploaded SHA256 for Falcon Sandbox analysis.

        Provide exactly one of `sha256` or `url`. Use this tool after uploading
        a sample or when detonating a URL directly, and optionally tune the
        environment, networking, and analyst metadata for the detonation.
        """
        sha256 = normalize_field_value(sha256)
        url = normalize_field_value(url)

        if bool(sha256) == bool(url):
            return [_format_error_response("Provide exactly one of `sha256` or `url` when submitting Sandbox analysis.")]

        submission = prepare_api_parameters(
            {
                "sha256": sha256,
                "url": url,
                "submit_name": submit_name,
                "environment_id": environment_id,
                "network_settings": network_settings,
                "action_script": action_script,
                "command_line": command_line,
                "document_password": document_password,
                "system_date": system_date,
                "system_time": system_time,
            }
        )

        result = self._base_query_api_call(
            operation="Submit",
            query_params={"aid": aid},
            body_params={
                "sandbox": [submission],
                "user_tags": user_tags,
                "send_email_notification": send_email_notification,
            },
            error_message="Failed to submit Falcon Sandbox analysis",
        )

        if self._is_error(result):
            return [result]

        return result

    def search_sandbox_submissions(
        self,
        filter: str | None = Field(
            default=None,
            description=SEARCH_SANDBOX_SUBMISSIONS_EMBEDDED_FQL_SYNTAX,
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of submission IDs to return."),
        offset: str | None = Field(default=None, description="Starting offset for submission search results."),
        sort: str | None = Field(default=None, description="Sort direction or FQL sort expression supported by Falcon Sandbox."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Sandbox submissions and return full submission details.

        IMPORTANT: You must use the `falcon://sandbox/submissions/search/fql-guide`
        resource when building the `filter` parameter for this tool.

        Use this tool to discover Sandbox submissions by state, hash, or time
        range. If matching submission IDs are found, the tool retrieves the full
        submission details before returning them. Empty results and filter
        errors include the FQL guide.
        """
        submission_ids = self._base_search_api_call(
            operation="QuerySubmissions",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Falcon Sandbox submissions",
            default_result=[],
        )

        if self._is_error(submission_ids):
            return self._format_fql_error_response(
                [submission_ids], filter, SEARCH_SANDBOX_SUBMISSIONS_FQL_DOCUMENTATION
            )

        if not submission_ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_SANDBOX_SUBMISSIONS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="GetSubmissions",
            ids=submission_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_sandbox_submission_details(
        self,
        ids: list[str] = Field(description="Falcon Sandbox submission ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve submission details for IDs you already know.

        Use this tool only when you already have submission IDs. To discover
        submissions by hash, state, or time range, use
        `falcon_search_sandbox_submissions`.
        """
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="GetSubmissions",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_sandbox_reports(
        self,
        filter: str | None = Field(
            default=None,
            description=SEARCH_SANDBOX_REPORTS_EMBEDDED_FQL_SYNTAX,
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of report IDs to return."),
        offset: str | None = Field(default=None, description="Starting offset for report search results."),
        sort: str | None = Field(default=None, description="Sort direction or FQL sort expression supported by Falcon Sandbox."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Sandbox reports and return summary report data.

        IMPORTANT: You must use the `falcon://sandbox/reports/search/fql-guide`
        resource when building the `filter` parameter for this tool.

        Use this tool to discover Sandbox reports by verdict, hash, or time
        range. If matching report IDs are found, the tool retrieves the summary
        report data before returning it. Empty results and filter errors include
        the FQL guide.
        """
        report_ids = self._base_search_api_call(
            operation="QueryReports",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Falcon Sandbox reports",
            default_result=[],
        )

        if self._is_error(report_ids):
            return self._format_fql_error_response(
                [report_ids], filter, SEARCH_SANDBOX_REPORTS_FQL_DOCUMENTATION
            )

        if not report_ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_SANDBOX_REPORTS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation="GetSummaryReports",
            ids=report_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_sandbox_report_summaries(
        self,
        ids: list[str] = Field(description="Falcon Sandbox report ID(s) to summarize."),
    ) -> list[dict[str, Any]]:
        """Retrieve summary report data for IDs you already know.

        Use this tool only when you already have report IDs. To discover reports
        by verdict, hash, or time range, use `falcon_search_sandbox_reports`.
        """
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="GetSummaryReports",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_sandbox_report_details(
        self,
        ids: list[str] = Field(description="Falcon Sandbox report ID(s) to retrieve in full."),
    ) -> list[dict[str, Any]]:
        """Retrieve full Falcon Sandbox reports for one or more report IDs.

        Use this tool only when you already have report IDs and need the full
        report body rather than the lighter summary data returned by
        `falcon_get_sandbox_report_summaries`.
        """
        if not ids:
            return []

        details = self._base_get_by_ids(
            operation="GetReports",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details
