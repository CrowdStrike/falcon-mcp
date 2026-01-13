"""
Scheduled Reports module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon
scheduled reports and scheduled searches.
"""

from typing import Any, List

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

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
    ) -> List[dict[str, Any]]:
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
        result = self._base_search_api_call(
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

        if self._is_error(result):
            return [result]

        return result

    def launch_scheduled_report(
        self,
        id: str = Field(description="Scheduled report/search entity ID to execute."),
    ) -> List[dict[str, Any]]:
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
    ) -> List[dict[str, Any]]:
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
        result = self._base_search_api_call(
            operation="reports_executions_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search for report executions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def download_report_execution(
        self,
        id: str = Field(description="Report execution ID to download."),
    ) -> str:
        """Download generated report file.

        Download the report file for a completed execution. Only works for executions
        with status='DONE'. The report is returned as a decoded string.

        Returns:
            The report content as a decoded UTF-8 string.

        Note: Check execution status first using falcon_search_report_executions with
        filter=id:'<execution-id>' to ensure the execution is complete (status='DONE')
        before attempting to download.
        """
        return self._base_get_api_call(
            operation="report_executions_download_get",
            api_params={"id": id},
            error_message="Failed to download report execution",
            decode_binary=True,
        )
