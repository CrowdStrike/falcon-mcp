<!-- meta:title Fusion SOAR -->
<!-- meta:description Searching Fusion SOAR workflow definitions and executions, reading what an execution produced, and running an on-demand workflow -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching Fusion SOAR workflow definitions and executions, reading what an execution produced, and running an on-demand workflow

> [!NOTE]
> This module is not available on CrowdStrike's hosted Falcon MCP; it is only available when self-hosting this server. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

## API Scopes

- `Workflows:read`
- `Workflows:write`

## Tools

### `falcon_search_workflow_definitions`

**Required scopes:** `Workflows:read`

Search Fusion SOAR workflow definitions in your CrowdStrike environment.

Use this to find a workflow to run or inspect, filtering on name, enabled
state, trigger type, version, or last-modified time. Consult
falcon://fusion/workflow-definitions/fql-guide before constructing filter
expressions — matching a name needs `name.raw`, because `name` is analyzed
and returns zero rows for an exact match. Returns full definition records
including `id`, `name`, `enabled`, `version`, and the `trigger` block whose
`parameters` field is the JSON Schema for that workflow's execute input.
Records are large (a definition embeds its whole action configuration), so
narrow the filter rather than raising the limit; one definition can appear
as several rows, one per version, so a result set may hold more rows than
the limit.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "What Fusion SOAR workflows can I trigger on demand?"
- "Find the Fusion workflow called 'Adversary Exposure Mitigation'"
- "Which Fusion workflows are currently disabled?"

### `falcon_search_workflow_executions`

**Required scopes:** `Workflows:read`

Search Fusion SOAR workflow execution history in your CrowdStrike environment.

Use this to see whether a workflow ran and how it finished, filtering on
definition, status, or start/finish time. Consult
falcon://fusion/workflow-executions/fql-guide before constructing filter
expressions — several fields are named differently in the filter than in
the response (`id` vs `execution_id`, `started_timestamp` vs
`start_timestamp`), and status must be filtered via `ui_status`, since
`status` uses a separate internal vocabulary. Returns full execution
records including `execution_id`, `definition_id`, `status`, timestamps,
and per-activity state. Records are large (an execution embeds the whole
triggering event), so narrow the filter rather than raising the limit, and
note `pagination.total` saturates at 10000, so exactly 10000 means "at
least 10000" rather than an exact count.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me workflow executions that completed"
- "Which Fusion workflows failed in the last 7 days?"
- "Are any workflow runs waiting on someone to approve them?"

### `falcon_get_workflow_execution_results`

**Required scopes:** `Workflows:read`

Read what one or more Fusion SOAR workflow executions produced.

Use this to look up executions directly by ID — up to 500 at once, with no
filter to construct — and to read each activity's own `result` payload:
ticket numbers, script output, API responses. This is the step after
falcon_execute_workflow, which returns only an execution ID. Returns the
full execution records including `status` and every activity's result;
`skip_fields` trims the largest sections when the records are too big. A run
still going reports `status` 'In progress': report that state back rather
than re-polling in a tight loop. 'Completed' and 'Failed' are terminal;
'Action required' means the run is waiting on a human, so polling will never
finish it.

**Example prompts:**

- "What did workflow execution 714511d8 actually do?"
- "Show me the ticket number the incident workflow created"

### `falcon_execute_workflow`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Workflows:write`

Start a Fusion SOAR workflow by definition ID.

Use this to run a workflow a team has already built and reviewed — notifying
a channel, opening a ticket, or running a containment sequence. What this
tool does depends entirely on the workflow you name and cannot be known from
this tool's name: a workflow may contain a host, disable an identity, or
notify third parties. Confirm the definition with
falcon_search_workflow_definitions and check its `trigger.parameters`,
`enabled` and `version` first; prefer a `trigger.type` of 'On demand', and
note the API refuses a disabled definition or a 'Signal'-triggered one with
a 412 whose message says which. Match `parameters` to `trigger.parameters`
exactly — a missing required field is rejected and starts nothing, but a
wrong type or malformed value is accepted and starts a real run. Returns
`[{"execution_id": "<id>"}]`; the run is asynchronous, so read the outcome
with falcon_get_workflow_execution_results.

**Example prompts:**

- "Run the 'Notify SOC Channel' workflow"
- "Start workflow 2617e3fc with the hash abc123"

## Resources

- **`falcon://fusion/workflow-definitions/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_workflow_definitions` tool.
- **`falcon://fusion/workflow-executions/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_workflow_executions` tool.
