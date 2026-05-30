---
title: Real Time Response Admin
description: Inspect RTR Admin assets, classify command risk, preview payloads, and execute approved single-host admin workflows.
sidebar:
  order: 10
---

Inspect RTR Admin assets, classify command risk, preview payloads, and execute approved single-host admin workflows.

## API Scopes

- `Real time response (admin):write`

## Tools

### `falcon_check_rtr_admin_command_status`

**Required scopes:** `Real time response (admin):write`

Retrieve status and output for a prior RTR Admin command.

Use this to poll for command completion after execution. This is a
read-only status lookup that cannot start a new command. Returns
completion status, stdout, stderr, and sequence information.

**Example prompts:**

- "Check the output for this RTR Admin cloud request ID"

### `falcon_classify_rtr_admin_command`

Classify an RTR Admin command without executing it.

Use this before designing or approving any RTR Admin execution flow.
This policy helper is intentionally local and does not call Falcon.
Returns category, risk level, approval requirements, and explanation.

**Example prompts:**

- "Classify this RTR Admin command before I decide whether to run it"

### `falcon_execute_rtr_admin_command`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Real time response (admin):write`

Execute an RTR Admin command on a single host.

Use after previewing and classifying the command. High-impact commands
are blocked unless the exact operator approval phrase is supplied.
Returns submission status, cloud_request_id for polling, and
classification enforcement details.

**Example prompts:**

- "Run this approved RTR Admin command against the existing RTR session"

### `falcon_preview_rtr_admin_command`

**Required scopes:** `Real time response (admin):write`

Preview an RTR Admin command payload without executing it.

This tool returns the exact Falcon operation and body shape that a later
execution tool would use, plus local policy classification. It never
calls Falcon and cannot execute the command.

**Example prompts:**

- "Preview the exact RTR Admin payload for this command before running it"

### `falcon_search_rtr_admin_scripts`

**Required scopes:** `Real time response (admin):write`

Search RTR custom scripts and return full metadata records.

Use this to find reusable custom RTR scripts by name, platform, or
permission type, or to look up known script IDs with an `id` filter.
Consult falcon://rtr-admin/scripts/search/fql-guide before constructing
filter expressions. Returns full script records including name, content,
platform, and permission details.

**Example prompts:**

- "Find Windows RTR Admin scripts with triage in the name"
- "Show me private custom RTR scripts I could review for this host"

### `falcon_search_rtr_falcon_scripts`

**Required scopes:** `Real time response (admin):write`

Search CrowdStrike-provided Falcon scripts and return full records.

Use this to find CrowdStrike-provided RTR scripts by name or platform,
or to look up known script IDs with an `id` filter. Consult
falcon://rtr-admin/falcon-scripts/search/fql-guide before constructing
filter expressions. Returns full script records including name,
description, and platform.

**Example prompts:**

- "Find CrowdStrike-provided Falcon scripts for Windows collection"

### `falcon_search_rtr_put_files`

**Required scopes:** `Real time response (admin):write`

Search RTR put-files and return full metadata records.

Use this to review put-file inventory before considering an admin
command that references staged content, or to look up known put-file IDs
with an `id` filter. Consult falcon://rtr-admin/put-files/search/fql-guide
before constructing filter expressions. Returns full put-file metadata
records.

**Example prompts:**

- "Search RTR put-files with collector in the name"

## Resources

- **`falcon://rtr-admin/scripts/search/fql-guide`**: Contains the guide for the `filter` param of the custom RTR script search tool.
- **`falcon://rtr-admin/falcon-scripts/search/fql-guide`**: Contains the guide for the `filter` param of the Falcon script search tool.
- **`falcon://rtr-admin/put-files/search/fql-guide`**: Contains the guide for the `filter` param of the RTR put-file search tool.
- **`falcon://rtr-admin/workflows/admin-guide`**: Contains RTR Admin inventory, preview, execution, and polling guidance.
- **`falcon://rtr-admin/commands/runscript-guide`**: Contains RTR Admin runscript raw command construction guidance.
