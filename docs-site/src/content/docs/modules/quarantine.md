---
title: Quarantine
description: Searching quarantine records, previewing action counts, and applying release, unrelease, or delete actions
sidebar:
  order: 10
---

Searching quarantine records, previewing action counts, and applying release, unrelease, or delete actions

## API Scopes

- `Quarantined Files:read`
- `Quarantined Files:write`

## Tools

### `falcon_search_quarantined_files`

**Required scopes:** `Quarantined Files:read`

Search quarantined files and return full quarantine metadata.

### `falcon_get_quarantined_file_details`

**Required scopes:** `Quarantined Files:read`

Retrieve quarantine record details for IDs you already know.

### `falcon_preview_quarantine_action_counts`

**Required scopes:** `Quarantined Files:read`

Estimate how many quarantine records each action would affect.

### `falcon_update_quarantined_files_by_ids`

**Required scopes:** `Quarantined Files:write`

Apply the reversible `release` or `unrelease` action to specific records by ID.

### `falcon_update_quarantined_files_by_filter`

**Required scopes:** `Quarantined Files:write`

Apply the reversible `release` or `unrelease` action to records selected by query.

### `falcon_delete_quarantined_files_by_ids`

**Required scopes:** `Quarantined Files:write`

Delete specific quarantine records by ID.

### `falcon_delete_quarantined_files_by_filter`

**Required scopes:** `Quarantined Files:write`

Delete quarantine records selected by filter or free-text query.

## Resources

- **`falcon://quarantine/files/search/fql-guide`**: Contains the guide for the `filter` param of quarantine search, preview, update, and delete-by-filter tools.
