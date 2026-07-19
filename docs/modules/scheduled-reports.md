<!-- meta:title Scheduled Reports -->
<!-- meta:description Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches

## API Scopes

- `Scheduled Reports:read`

## Tools

### `falcon_download_report_execution`

**Required scopes:** `Scheduled Reports:read`

Download the results of a completed report execution.

Only works for executions with status='DONE'. Check status first using
falcon_search_report_executions. Returns CSV string or JSON records depending
on the report's configured format. PDF format is not supported.

**Example prompts:**

- "Download the results for report execution abc123"

### `falcon_launch_scheduled_report`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Scheduled Reports:read`

Launch a scheduled report or search on demand.

Executes the report immediately outside its recurring schedule. Returns
execution records containing an execution ID that can be tracked with
falcon_search_report_executions and downloaded with
falcon_download_report_execution when complete.

**Example prompts:**

- "Run scheduled report abc123 now"

### `falcon_search_report_executions`

**Required scopes:** `Scheduled Reports:read`

Search for report/search execution history.

Use this to find executions by status, report ID, or completion date. Consult
falcon://scheduled-reports/executions/search/fql-guide before constructing filter
expressions. Returns full execution details including status and timestamps.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me completed executions for report abc123"

### `falcon_search_scheduled_reports`

**Required scopes:** `Scheduled Reports:read`

Search for scheduled reports and searches in your CrowdStrike environment.

Use this to find reports by status, type, creator, or creation date. Consult
falcon://scheduled-reports/search/fql-guide before constructing filter expressions.
Returns full report/search entity details including schedule configuration.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me all active scheduled reports"

## Resources

- **`falcon://scheduled-reports/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_scheduled_reports` tool.
- **`falcon://scheduled-reports/executions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_report_executions` tool.
