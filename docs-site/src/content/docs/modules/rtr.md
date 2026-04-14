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

Get the status and output chunk for an RTR command.

### `falcon_delete_session`

**Required scopes:** `Real time response:read`

Delete an RTR session.

### `falcon_execute_read_only_command`

**Required scopes:** `Real time response:read`

Execute a read-only RTR command on a single host.

This tool is intentionally limited to the read-only RTR endpoint for
hunt and triage workflows. It does not expose admin or remediation
command APIs.

### `falcon_get_session_details`

**Required scopes:** `Real time response:read`

Retrieve detailed metadata for one or more RTR sessions.

### `falcon_init_session`

**Required scopes:** `Real time response:read`

Initialize or reuse an RTR session for a single host.

### `falcon_list_session_files`

**Required scopes:** `Real time response:write`

List files currently associated with an RTR session.

### `falcon_pulse_session`

**Required scopes:** `Real time response:read`

Refresh an RTR session timeout for a single host.

### `falcon_search_sessions`

**Required scopes:** `Real time response:read`

Search RTR sessions and return full session details.

## Resources

- **`falcon://rtr/sessions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool.
