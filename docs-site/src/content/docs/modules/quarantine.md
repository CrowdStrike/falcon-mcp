---
title: Quarantine
description: Investigating quarantined files and applying quarantine actions during triage and remediation workflows
sidebar:
  order: 10
---

Investigating quarantined files and applying quarantine actions during triage and remediation workflows

## API Scopes

- `Quarantined Files:read`
- `Quarantined Files:write`

## Tools

### `falcon_delete_quarantined_files`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Quarantined Files:write`

Delete quarantine records selected by IDs or filter.

This tool is destructive and should be used only when quarantine records
should be removed rather than released. Provide `ids` for specific records,
or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide
before constructing filter expressions. Returns an empty list on success.

**Example prompts:**

- "Delete quarantine records for host SE-DAO-WIN10-CO"
- "Delete quarantine record abc123"

### `falcon_preview_quarantine_actions`

**Required scopes:** `Quarantined Files:read`

Estimate how many quarantine records each action would affect for a given filter.

Use this read-only tool before calling a mutating quarantine action to
understand the blast radius of a release, unrelease, or delete request.
Consult falcon://quarantine/files/search/fql-guide before constructing
filter expressions. Returns a list of action counts keyed by action name.

**Example prompts:**

- "Preview how many quarantined files can be released vs deleted"
- "Preview quarantine action impact for state quarantined on host SE-DAO-WIN10-CO"

### `falcon_search_quarantined_files`

**Required scopes:** `Quarantined Files:read`

Search quarantined files and return full quarantine metadata.

Use this to discover quarantine records by host, hash, user, or state.
Consult falcon://quarantine/files/search/fql-guide before constructing
filter expressions. Returns full quarantine details including hostname,
sha256, paths, state, and associated alert and detection IDs.

**Example prompts:**

- "Show me quarantined files on host SE-DAO-WIN10-CO"
- "Find quarantined files for user badguy updated in the last 7 days"
- "Search for quarantined files with SHA256 starting with 3dd9"

### `falcon_update_quarantined_files`

:::note
This tool modifies data.
:::

**Required scopes:** `Quarantined Files:write`

Apply a reversible quarantine action to records selected by IDs or filter.

Use this to release or unrelease quarantined files. Provide `ids` for
specific records, or `filter` to select by query. Consult
falcon://quarantine/files/search/fql-guide before constructing filter
expressions. Returns an empty list on success.

**Example prompts:**

- "Release quarantine record abc123"
- "Release all quarantined files for user badguy"

## Resources

- **`falcon://quarantine/files/search/fql-guide`**: Contains the guide for the `filter` param of quarantine search and filter-based action tools.
