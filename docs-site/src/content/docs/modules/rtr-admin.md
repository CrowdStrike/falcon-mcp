---
title: Real Time Response Admin
description: Inspect RTR Admin assets, classify command risk, preview payloads, and execute approved single-host admin workflows.
sidebar:
  order: 25
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

### `falcon_get_rtr_put_file_contents`

**Required scopes:** `Real time response (admin):write`

Retrieve the stored contents of one RTR put-file by ID.

Use this only after selecting a specific put-file from
falcon_search_rtr_put_files. This is a read-only Falcon call, but the
returned content can be sensitive because put-files may contain scripts,
binaries, or operational payloads staged for RTR `put` workflows.
Text content is returned for model review; binary content returns size
metadata and a safe error instead of raw bytes. Treat retrieval results
as sensitive regardless of inventory `file_type`; binary-tagged
inventory can still retrieve text content.

**Example prompts:**

- "Retrieve the contents for RTR put-file ID abc123"

### `falcon_preview_rtr_admin_command`

**Required scopes:** `Real time response (admin):write`

Preview an RTR Admin command payload without executing it.

This tool returns the exact Falcon operation and body shape that a later
execution tool would use, plus local policy classification. It never
calls Falcon and cannot execute the command.

**Example prompts:**

- "Preview the exact RTR Admin payload for this command before running it"

### `falcon_run_rtr_admin_command_and_wait`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Real time response (admin):write`

Execute an RTR Admin command and poll until completion or timeout.

This is a convenience workflow for single-host admin commands. It uses
the same local classification and approval gate as
falcon_execute_rtr_admin_command, then polls
falcon_check_rtr_admin_command_status with the returned cloud_request_id.

**Example prompts:**

- "Run this approved RTR Admin command and wait for stdout and stderr"

### `falcon_search_rtr_admin_scripts`

**Required scopes:** `Real time response (admin):write`

Search RTR custom scripts and return full metadata records.

Use this to find reusable custom RTR scripts by name, platform, or
permission type. Consult falcon://rtr-admin/scripts/search/fql-guide
before constructing filter expressions. Returns full script records,
including script content; treat the response as sensitive operational
material.

**Example prompts:**

- "Find Windows RTR Admin scripts with triage in the name"
- "Show me private custom RTR scripts I could review for this host"
- "Look up RTR Admin script ID abc123 with an id filter"

### `falcon_search_rtr_falcon_scripts`

**Required scopes:** `Real time response (admin):write`

Search CrowdStrike-provided Falcon scripts and return full records.

Use this to find CrowdStrike-provided RTR scripts by name or platform,
or to look up known script IDs with an `id` filter. Consult
falcon://rtr-admin/falcon-scripts/search/fql-guide before constructing
filter expressions. Returns full script records; treat any returned
script content as sensitive operational material.

**Example prompts:**

- "Find CrowdStrike-provided Falcon scripts for Windows collection"
- "Look up Falcon script ID abc123 with an id filter"

### `falcon_search_rtr_put_files`

**Required scopes:** `Real time response (admin):write`

Search RTR put-files and return full metadata records.

Use this to review put-file inventory before considering an admin
command that references staged content. Consult
falcon://rtr-admin/put-files/search/fql-guide before constructing
filter expressions. Returns full put-file metadata records.

**Example prompts:**

- "Search RTR put-files with collector in the name"
- "Look up RTR put-file ID abc123 with an id filter"

## Resources

- **`falcon://rtr-admin/scripts/search/fql-guide`**: Contains the guide for the `filter` param of the custom RTR script search tool.
- **`falcon://rtr-admin/falcon-scripts/search/fql-guide`**: Contains the guide for the `filter` param of the Falcon script search tool.
- **`falcon://rtr-admin/put-files/search/fql-guide`**: Contains the guide for the `filter` param of the RTR put-file search tool.
- **`falcon://rtr-admin/workflows/admin-guide`**: Contains RTR Admin inventory, preview, execution, and polling guidance.
- **`falcon://rtr-admin/commands/runscript-guide`**: Contains RTR Admin runscript raw command construction guidance.
- **`falcon://rtr-admin/policy/command-guide`**: Contains RTR Admin command classification policy and command categories.
- **`falcon://rtr-admin/approval/packet-guide`**: Contains the approval packet template for high-impact RTR Admin commands.

## Prompts

### `falcon_plan_rtr_admin_action`

**Title:** Plan RTR Admin Action

Plan a safe RTR Admin workflow before using execution tools.

### `falcon_build_rtr_admin_approval_packet`

**Title:** Build RTR Admin Approval Packet

Create an operator approval packet for a high-impact RTR Admin command.

### `falcon_review_rtr_admin_runscript`

**Title:** Review RTR Admin Runscript

Review an RTR Admin runscript command string for safety and quoting risks.

### `falcon_interpret_rtr_admin_status`

**Title:** Interpret RTR Admin Status

Interpret RTR Admin command status output and suggest next safe steps.
