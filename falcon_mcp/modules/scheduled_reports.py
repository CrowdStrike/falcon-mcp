"""
Scheduled Reports module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon
scheduled reports and scheduled searches.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.scheduled_reports import (
    SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
    SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
)


class ScheduledReportsModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon scheduled reports and searches."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register entity tools
        self._add_tool(
            server=server,
            method=self.search_scheduled_reports,
            name="search_scheduled_reports",
        )

        self._add_tool(
            server=server,
            method=self.launch_scheduled_report,
            name="launch_scheduled_report",
        )

        # Register execution tools
        self._add_tool(
            server=server,
            method=self.search_report_executions,
            name="search_report_executions",
        )

        self._add_tool(
            server=server,
            method=self.download_report_execution,
            name="download_report_execution",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_scheduled_reports_fql_resource = TextResource(
            uri=AnyUrl("falcon://scheduled-reports/search/fql-guide"),
            name="falcon_search_scheduled_reports_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_scheduled_reports` tool.",
            text=SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
        )

        search_report_executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://scheduled-reports/executions/search/fql-guide"),
            name="falcon_search_report_executions_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_report_executions` tool.",
            text=SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_scheduled_reports_fql_resource,
        )
        self._add_resource(
            server,
            search_report_executions_fql_resource,
        )

    def search_scheduled_reports(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit results. Use id:'<id>' to get specific reports. IMPORTANT: use the `falcon://scheduled-reports/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of records to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Property to sort by. Ex: created_on.asc, last_updated_on.desc, next_execution_on.desc",
        ),
        q: str | None = Field(
            default=None,
            description="Free-text search for terms in id, name, description, type, status fields",
        ),
    ) -> list[dict[str, Any]]:
        """Search for scheduled reports and searches in your CrowdStrike environment.

        Returns full details for matching scheduled report/search entities. Use the filter
        parameter to narrow results or retrieve specific entities by ID.

        IMPORTANT: You must use the `falcon://scheduled-reports/search/fql-guide` resource
        when you need to use the `filter` parameter.

        Common use cases:
        - Get specific report by ID: filter=id:'<report-id>'
        - Get multiple reports by ID: filter=id:['id1','id2']
        - Find active reports: filter=status:'ACTIVE'
        - Find scheduled searches: filter=type:'event_search'
        - Find by creator: filter=user_id:'user@email.com'

        Examples:
        - filter=status:'ACTIVE'+type:'event_search' - Active scheduled searches
        - filter=created_on:>'2023-01-01' - Created after date
        - filter=id:'45c59557ded4413cafb8ff81e7640456' - Specific report by ID
        """
        report_ids = self._base_search_api_call(
            operation="scheduled_reports_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search for scheduled reports",
            default_result=[],
        )

        if self._is_error(report_ids):
            return [report_ids]

        # If we have report IDs, get the full details for each one
        if report_ids:
            details = self._base_get_by_ids(
                operation="scheduled_reports_get",
                ids=report_ids,
                use_params=True,
            )

            if self._is_error(details):
                return [details]

            return details

        return []

    def launch_scheduled_report(
        self,
        id: str = Field(description="Scheduled report/search entity ID to execute."),
    ) -> list[dict[str, Any]]:
        """Launch a scheduled report on demand.

        Execute a scheduled report or search immediately, outside of its recurring schedule.
        This creates a new execution instance that can be tracked and downloaded.

        Returns the execution details including the execution ID which can be used with:
        - falcon_search_report_executions to check status (filter=id:'<execution-id>')
        - falcon_download_report_execution to download results when ready

        Note: The report will run with the same parameters as defined in the entity configuration.
        """
        result = self._base_query_api_call(
            operation="scheduled_reports_launch",
            body_params={"id": id},
            error_message="Failed to launch scheduled report",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_report_executions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit results. Use id:'<id>' to get specific executions. IMPORTANT: use the `falcon://scheduled-reports/executions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of records to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Property to sort by. Ex: created_on.asc, last_updated_on.desc",
        ),
    ) -> list[dict[str, Any]]:
        """Search for scheduled report/search executions in your CrowdStrike environment.

        Returns full details for matching executions. Use the filter parameter to narrow
        results or retrieve specific executions by ID.

        IMPORTANT: You must use the `falcon://scheduled-reports/executions/search/fql-guide`
        resource when you need to use the `filter` parameter.

        Common use cases:
        - Get specific execution by ID: filter=id:'<execution-id>'
        - Get all executions for a report: filter=scheduled_report_id:'<report-id>'
        - Find completed executions: filter=status:'DONE'
        - Find failed executions: filter=status:'FAILED'

        Examples:
        - filter=status:'DONE'+created_on:>'2023-01-01' - Successful runs after date
        - filter=scheduled_report_id:'abc123' - All executions for report abc123
        - filter=id:'f1984ff006a94980b352f18ee79aed77' - Specific execution by ID
        """
        execution_ids = self._base_search_api_call(
            operation="report_executions_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search for report executions",
            default_result=[],
        )

        if self._is_error(execution_ids):
            return [execution_ids]

        # If we have execution IDs, get the full details for each one
        if execution_ids:
            details = self._base_get_by_ids(
                operation="report_executions_get",
                ids=execution_ids,
                use_params=True,
            )

            if self._is_error(details):
                return [details]

            return details

        return []

    def download_report_execution(
        self,
        id: str = Field(description="Report execution ID to download."),
    ) -> str | list[dict[str, Any]] | dict[str, Any]:
        """Download generated report results.

        Download the report results for a completed execution. Only works for executions
        with status='DONE'.

        The return format depends on how the scheduled report was configured:
        - CSV format reports: Returns string containing CSV data
        - JSON format reports: Returns list of result records
        - PDF format reports: Not supported (returns error - use CSV/JSON instead)

        Note: Check execution status first using falcon_search_report_executions with
        filter=id:'<execution-id>' to ensure the execution is complete (status='DONE')
        before attempting to download.
        """
        prepared_params = prepare_api_parameters({"ids": id})
        response = self.client.command(
            "report_executions_download_get",
            parameters=prepared_params,
        )

        # CSV format: FalconPy returns raw bytes
        if isinstance(response, bytes):
            # Check if it's a PDF (starts with %PDF magic bytes)
            if response[:4] == b"%PDF":
                return {
                    "error": "PDF format not supported for LLM consumption. "
                    "Please configure the scheduled report to use CSV or JSON format instead."
                }
            # Decode CSV/text content
            return response.decode("utf-8")

        # JSON format: FalconPy returns dict with body.resources
        if isinstance(response, dict):
            status_code = response.get("status_code")
            if status_code != 200:
                return handle_api_response(
                    response,
                    operation="report_executions_download_get",
                    error_message="Failed to download report execution",
                    default_result=[],
                )
            # Extract resources list from JSON format response
            return response.get("body", {}).get("resources", [])

        # Unexpected response type
        return {"error": f"Unexpected response type: {type(response).__name__}"}
