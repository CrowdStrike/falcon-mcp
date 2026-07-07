# Scheduled Reports

Access CrowdStrike Falcon scheduled reports and their executions.

## Tools

### `falcon_download_report_execution`

**Type:** read-only

Download the content of a completed report execution by ID. Returns the report content as text. Get execution IDs from falcon_search_report_executions; the execution must be in a completed state to download.

### `falcon_launch_scheduled_report`

**Type:** mutating

Launch a scheduled report or search on demand. Executes the report immediately outside its recurring schedule. Returns execution records containing an execution ID that can be tracked with falcon_search_report_executions and downloaded with falcon_download_report_execution when complete.

### `falcon_search_report_executions`

**Type:** read-only

Search for report/search execution history. Consult falcon://scheduled-reports/executions/search/fql-guide before constructing filter expressions. Returns full execution details including status and download availability.

### `falcon_search_scheduled_reports`

**Type:** read-only

Search for scheduled reports in your CrowdStrike environment. Consult falcon://scheduled-reports/search/fql-guide before constructing filter expressions. Returns full scheduled-report details.

## Resources

- `falcon://scheduled-reports/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_scheduled_reports` tool.
- `falcon://scheduled-reports/executions/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_report_executions` tool.

