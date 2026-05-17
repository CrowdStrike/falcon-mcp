---
title: Case Management
description: Managing CrowdStrike cases, including searching, creating, updating, and managing evidence and tags
sidebar:
  order: 10
---

Managing CrowdStrike cases, including searching, creating, updating, and managing evidence and tags

## API Scopes

- `Case Templates:read`
- `Cases:read`
- `Cases:write`

## Tools

### `falcon_add_case_alert_evidence`

:::note
This tool modifies data.
:::

**Required scopes:** `Cases:write`

Attach alert evidence to an existing case.

Provide alert composite_id values from the Alerts v2 API (e.g. from
falcon_search_detections). Each case supports a maximum of 100 combined
evidence items. Returns the updated case record.

**Example prompts:**

- "Attach these detection alerts to the open case"

### `falcon_add_case_event_evidence`

:::note
This tool modifies data.
:::

**Required scopes:** `Cases:write`

Attach LogScale event evidence to an existing case.

Provide event IDs obtained from falcon_search_ngsiem or the Falcon
console. Each case supports a maximum of 100 combined evidence items.
Returns the updated case record.

**Example prompts:**

- "Add these NGSIEM event IDs to the case as evidence"

### `falcon_create_case`

:::note
This tool modifies data.
:::

**Required scopes:** `Cases:write`

Create a new case in CrowdStrike.

Provide a name and severity at minimum. Optionally attach alert or event
evidence, assign a user, apply a template, and set tags. Returns the
created case record.

**Example prompts:**

- "Create a high-severity case for the suspicious lateral movement investigation"
- "Open a new case and attach these alert IDs as evidence"

### `falcon_get_cases`

**Required scopes:** `Cases:read`

Retrieve details for case IDs you already have.

Use when you have specific case IDs from search results or external
references. For discovering cases by criteria, use falcon_search_cases
instead. Returns full case records.

**Example prompts:**

- "Get details for this case ID"

### `falcon_list_case_templates`

**Required scopes:** `Case Templates:read`

List available case templates.

Use to discover templates that can be applied when creating or updating
cases. Returns template details including name, custom fields, and SLA
configuration.

**Example prompts:**

- "Show me the available case templates"

### `falcon_manage_case_tags`

:::note
This tool modifies data.
:::

**Required scopes:** `Cases:write`

Add or remove tags on a case.

Set action to 'add' to attach new tags, or 'remove' to delete existing
tags. Returns the updated case record.

**Example prompts:**

- "Tag this case with 'ransomware' and 'priority'"
- "Remove the 'false-positive' tag from this case"

### `falcon_search_cases`

**Required scopes:** `Cases:read`

Find cases by criteria and return their complete details.

Use this to discover cases by status, severity, assignee, time range, or
evidence attributes. Consult falcon://cases/search/fql-guide before
constructing filter expressions. Returns full case records including
status, severity, evidence, assigned user, and analysis results.

**Example prompts:**

- "Show me all open high-severity cases"
- "Find cases assigned to me that are in progress"

### `falcon_update_case`

:::note
This tool modifies data.
:::

**Required scopes:** `Cases:write`

Update an existing case's fields.

Provide the case ID and any fields to change. Use expected_version for
optimistic concurrency control to prevent conflicting updates. Returns the
updated case record with incremented version.

**Example prompts:**

- "Close case ABC-1234"
- "Assign this case to the SOC analyst and set severity to critical"

## Resources

- **`falcon://cases/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cases` tool.
