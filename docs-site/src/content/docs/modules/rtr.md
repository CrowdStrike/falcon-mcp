---
title: Real Time Response
description: Initiating and inspecting RTR sessions and executing read-only RTR commands during host investigations
sidebar:
  order: 24
---

Initiating and inspecting RTR sessions and executing read-only RTR commands during host investigations

## API Scopes

- `Real time response:read`
- `real-time-response-audit:read`
- `Real time response:write`

## Tools

### `falcon_aggregate_rtr_sessions`

**Required scopes:** `Real time response:read`

Summarize RTR session activity with Falcon aggregation buckets.

Use this before detailed searches when the user asks which hosts,
users, origins, commands, or time windows account for RTR activity.
This is read-only summary visibility; it does not open sessions, run
commands, or return every session record.

**Example prompts:**

- "Summarize RTR sessions by command for the last 30 days"
- "Which hosts have the most RTR activity this week?"

### `falcon_check_rtr_command_status`

**Required scopes:** `Real time response:read`

Get the status and output for an RTR command execution.

Poll this after falcon_execute_rtr_read_only_command to retrieve command
output. Use sequence_id to paginate through large output chunks.

**Example prompts:**

- "Check the status of RTR command request abc123"

### `falcon_delete_rtr_session`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Real time response:read`

Close an RTR session and release the host connection.

Use this when investigation is complete to free up session resources.

**Example prompts:**

- "End the RTR session abc123"

### `falcon_execute_rtr_read_only_command`

:::note
This tool modifies data.
:::

**Required scopes:** `Real time response:read`

Execute a read-only RTR command on a single host.

Limited to read-only commands (ls, ps, cat, filehash, reg) for hunt and triage
workflows. Does not expose admin or remediation commands. Returns command records
containing a cloud_request_id for polling output via falcon_check_rtr_command_status.

**Example prompts:**

- "Run 'ps' on this host via RTR"
- "List running processes on host xyz"

### `falcon_get_rtr_session_details`

**Required scopes:** `Real time response:read`

Retrieve detailed metadata for one or more RTR sessions.

Use when you already have session IDs from search results. For discovering
sessions by criteria, use falcon_search_rtr_sessions instead. Returns full
session records.

**Example prompts:**

- "Get details for RTR session abc123"

### `falcon_init_rtr_session`

:::note
This tool modifies data.
:::

**Required scopes:** `Real time response:read`

Initialize or reuse an RTR session for a single host.

Opens a live connection to the specified device for executing RTR commands.
Use queue_offline=True if the host may be offline. Returns session records
containing the session_id needed for subsequent commands.

**Example prompts:**

- "Start an RTR session on host xyz"

### `falcon_list_rtr_session_files`

**Required scopes:** `Real time response:write`

List files extracted during an RTR session.

Returns file metadata for artifacts captured during the session, such as
files pulled with the `get` command.

**Example prompts:**

- "List files extracted during RTR session abc123"

### `falcon_pulse_rtr_session`

:::note
This tool modifies data.
:::

**Required scopes:** `Real time response:read`

Refresh an RTR session timeout for a single host.

Keeps an existing session alive by resetting its inactivity timer. Use this
to prevent session expiration during long investigations.

**Example prompts:**

- "Refresh the RTR session to keep it alive"

### `falcon_run_rtr_read_only_command_and_wait`

:::note
This tool modifies data.
:::

**Required scopes:** `Real time response:read`

Execute a read-only RTR command and poll until completion.

Use this for simple, focused RTR evidence collection when the user
wants the command output directly and does not need to manually manage
a cloud request ID. This polls command status until completion or
timeout, accumulating output chunks into one result. It still executes
an RTR command and creates RTR command activity, but it does not expose
RTR Admin or remediation APIs.

**Example prompts:**

- "Run 'ps' via RTR and return the output when it completes"
- "Check C:\Windows\win.ini on this RTR session and wait for the result"

### `falcon_search_rtr_audit_sessions`

**Required scopes:** `real-time-response-audit:read`

Search RTR audit sessions for accountability and timeline evidence.

Use this when you need to understand who used RTR, when they used it,
which host was targeted, or which command activity Falcon recorded.
This is read-only audit visibility; it does not open sessions or run
commands. Consult falcon://rtr/audit/sessions/search/fql-guide before
constructing filter expressions.

**Example prompts:**

- "Show me RTR audit activity from the last 7 days"
- "Who used RTR against host EXAMPLE-WIN-22?"

### `falcon_search_rtr_sessions`

**Required scopes:** `Real time response:read`

Search RTR sessions and return full session details.

Use this to find sessions by hostname, agent ID, user, or creation time. Consult
falcon://rtr/sessions/search/fql-guide before constructing filter expressions.
Returns session metadata including host info, commands executed, and status.

**Example prompts:**

- "Find all active RTR sessions"
- "Show me RTR sessions for host abc123"

## Resources

- **`falcon://rtr/sessions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool.
- **`falcon://rtr/audit/sessions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_rtr_audit_sessions` tool.
- **`falcon://rtr/sessions/aggregate-guide`**: Explains how to summarize RTR session activity with the `falcon_aggregate_rtr_sessions` tool.
- **`falcon://rtr/workflows/investigation-guide`**: Provides a safe read-only RTR workflow for endpoint investigation tools.
