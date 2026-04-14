---
title: Scheduled Reports
description: Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches
sidebar:
  order: 10
---

Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches

## API Scopes

- `Scheduled Reports:read`

## Tools

### `falcon_download_report_execution`

**Required scopes:** `Scheduled Reports:read`

Download generated report results.

Download the report results for a completed execution. Only works for executions
with status='DONE'.

The return format depends on how the scheduled report was configured:
- CSV format reports: Returns string containing CSV data
- JSON format reports: Returns list of result records
- PDF format reports: Not supported (returns error - use CSV/JSON instead)

Note: Check execution status first using falcon_search_report_executions with
filter=id:'<execution-id>' to ensure the execution is complete (status='DONE')
before attempting to download.

**Example prompts:**

- "Download the results for report execution abc123"

### `falcon_launch_scheduled_report`

:::note
This tool modifies data.
:::

**Required scopes:** `Scheduled Reports:read`

Launch a scheduled report on demand.

Execute a scheduled report or search immediately, outside of its recurring schedule.
This creates a new execution instance that can be tracked and downloaded.

Returns the execution details including the execution ID which can be used with:
- falcon_search_report_executions to check status (filter=id:'<execution-id>')
- falcon_download_report_execution to download results when ready

Note: The report will run with the same parameters as defined in the entity configuration.

**Example prompts:**

- "Run scheduled report abc123 now"

### `falcon_search_report_executions`

**Required scopes:** `Scheduled Reports:read`

Search for scheduled report/search executions in your CrowdStrike environment.

Returns full details for matching executions. Use the filter parameter to narrow
results or retrieve specific executions by ID.

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

**Example prompts:**

- "Show me completed executions for report abc123"

### `falcon_search_scheduled_reports`

**Required scopes:** `Scheduled Reports:read`

Search for scheduled reports and searches in your CrowdStrike environment.

Returns full details for matching scheduled report/search entities. Use the filter
parameter to narrow results or retrieve specific entities by ID.

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

**Example prompts:**

- "Show me all active scheduled reports"

## Resources

- **`falcon://scheduled-reports/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_scheduled_reports` tool.
- **`falcon://scheduled-reports/executions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_report_executions` tool.
