# Rtr

Real Time Response session lifecycle for CrowdStrike Falcon: search, init, execute read-only commands, and manage RTR sessions.

## Tools

### `falcon_aggregate_rtr_sessions`

**Type:** read-only

Summarize RTR session activity with Falcon aggregation buckets. Use this before detailed searches when the user asks which hosts, users, origins, commands, or time windows account for RTR activity. Consult falcon://rtr/sessions/aggregate-guide for examples. This is read-only summary visibility; it does not open sessions or run commands.

### `falcon_check_rtr_command_status`

**Type:** read-only

Get the status and output for an RTR command execution. Poll this after falcon_execute_rtr_read_only_command to retrieve command output. Use sequence_id to paginate through large output chunks.

### `falcon_delete_rtr_session`

**Type:** destructive

Close an RTR session and release the host connection. Use this when investigation is complete to free up session resources.

### `falcon_execute_rtr_read_only_command`

**Type:** mutating

Execute a read-only RTR command on a single host. Limited to read-only commands (cat, cd, clear, env, eventlog, filehash, getsid, help, history, ipconfig, ls, mount, netstat, ps, reg) for hunt and triage workflows. Returns command records containing a cloud_request_id for polling output via falcon_check_rtr_command_status.

### `falcon_get_rtr_session_details`

**Type:** read-only

Retrieve detailed metadata for one or more RTR sessions by ID. Use when you already have session IDs from search results. For discovering sessions by criteria, use falcon_search_rtr_sessions instead. Returns full session records.

### `falcon_init_rtr_session`

**Type:** mutating

Initialize or reuse an RTR session for a single host. Opens a live connection to the specified device for executing RTR commands. Use queue_offline=true if the host may be offline. Returns session records containing the session_id needed for subsequent commands.

### `falcon_list_rtr_session_files`

**Type:** read-only

List files extracted during an RTR session. Returns file metadata for artifacts captured during the session, such as files pulled with the get command.

### `falcon_pulse_rtr_session`

**Type:** mutating

Refresh an RTR session timeout for a single host. Keeps an existing session alive by resetting its inactivity timer. Use this to prevent session expiration during long investigations.

### `falcon_run_rtr_read_only_command_and_wait`

**Type:** mutating

Execute a read-only RTR command and poll until completion. Use this for simple, focused RTR evidence collection when you want the command output directly without manually managing a cloud_request_id. Limited to the same read-only command set as falcon_execute_rtr_read_only_command. Polls command status until completion or timeout, accumulating output chunks into one result.

### `falcon_search_rtr_audit_sessions`

**Type:** read-only

Search RTR audit sessions for accountability and timeline evidence. Use this when you need to understand who used RTR, when they used it, which host was targeted, or which command activity Falcon recorded. Consult falcon://rtr/audit/sessions/search/fql-guide before constructing filter expressions. This is read-only audit visibility; it does not open sessions or run commands.

### `falcon_search_rtr_sessions`

**Type:** read-only

Search RTR sessions and return full session details. Use this to find sessions by hostname, agent ID, user, or creation time. Consult falcon://rtr/sessions/search/fql-guide before constructing filter expressions. Returns session metadata including host info, commands executed, and status.

## Resources

- `falcon://rtr/sessions/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool.
- `falcon://rtr/audit/sessions/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_rtr_audit_sessions` tool.
- `falcon://rtr/sessions/aggregate-guide` — Explains how to summarize RTR session activity with the `falcon_aggregate_rtr_sessions` tool.
- `falcon://rtr/workflows/investigation-guide` — Provides a safe read-only RTR workflow for endpoint investigation tools.

