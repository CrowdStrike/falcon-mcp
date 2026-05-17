---
title: Real Time Response
description: Initiating and inspecting RTR sessions and for executing read-only RTR commands during host investigations
sidebar:
  order: 10
---

Initiating and inspecting RTR sessions and for executing read-only RTR commands during host investigations

## API Scopes

- `Real time response:read`
- `Real time response:write`

## Tools

### `falcon_check_command_status`

**Required scopes:** `Real time response:read`

Get the status and output for an RTR command execution.

Poll this after falcon_execute_rtr_read_only_command to retrieve command
output. Use sequence_id to paginate through large output chunks.

### `falcon_delete_session`

**Required scopes:** `Real time response:read`

Close an RTR session and release the host connection.

Use this when investigation is complete to free up session resources.

### `falcon_execute_read_only_command`

**Required scopes:** `Real time response:read`

Execute a read-only RTR command on a single host.

Limited to read-only commands (ls, ps, cat, filehash, reg) for hunt and triage
workflows. Does not expose admin or remediation commands. Returns command records
containing a cloud_request_id for polling output via falcon_check_rtr_command_status.

### `falcon_get_session_details`

**Required scopes:** `Real time response:read`

Retrieve detailed metadata for one or more RTR sessions.

Use when you already have session IDs from search results. For discovering
sessions by criteria, use falcon_search_rtr_sessions instead. Returns full
session records.

### `falcon_init_session`

**Required scopes:** `Real time response:read`

Initialize or reuse an RTR session for a single host.

Opens a live connection to the specified device for executing RTR commands.
Use queue_offline=True if the host may be offline. Returns session records
containing the session_id needed for subsequent commands.

### `falcon_list_session_files`

**Required scopes:** `Real time response:write`

List files extracted during an RTR session.

Returns file metadata for artifacts captured during the session, such as
files pulled with the `get` command.

### `falcon_pulse_session`

**Required scopes:** `Real time response:read`

Refresh an RTR session timeout for a single host.

Keeps an existing session alive by resetting its inactivity timer. Use this
to prevent session expiration during long investigations.

### `falcon_search_sessions`

**Required scopes:** `Real time response:read`

Search RTR sessions and return full session details.

Use this to find sessions by hostname, agent ID, user, or creation time. Consult
falcon://rtr/sessions/search/fql-guide before constructing filter expressions.
Returns session metadata including host info, commands executed, and status.

## Resources

- **`falcon://rtr/sessions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool.
