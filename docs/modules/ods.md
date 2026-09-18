<!-- meta:title On-Demand Scan -->
<!-- meta:description Search ODS results, launch and cancel scans, and manage scheduled scans. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Search ODS results, launch and cancel scans, and manage scheduled scans.

## API Scopes

- `On-demand scans (ODS):read`
- `On-demand scans (ODS):write`

## Tools

### `falcon_search_ods_scans`

**Required scopes:** `On-demand scans (ODS):read`

Search ODS scans and return full scan entities with pagination.

**Example prompts:**

- "Show completed ODS scans that found malicious files"

### `falcon_search_ods_scan_hosts`

**Required scopes:** `On-demand scans (ODS):read`

Search per-host ODS scan results and return full metadata.

**Example prompts:**

- "Which hosts in scan scan-123 found malicious files?"

### `falcon_search_ods_malicious_files`

**Required scopes:** `On-demand scans (ODS):read`

Search malicious files found by ODS and return full file records.

**Example prompts:**

- "List quarantined files found by scan scan-123"

### `falcon_search_ods_scheduled_scans`

**Required scopes:** `On-demand scans (ODS):read`

Search scheduled ODS scans and return full schedule definitions.

**Example prompts:**

- "Show active scheduled ODS scans"

### `falcon_launch_ods_scan`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `On-demand scans (ODS):write`

Start an ODS scan against explicit hosts or host groups.

**Example prompts:**

- "Scan C:\Temp on host aid-123 without quarantining files"

### `falcon_cancel_ods_scans`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `On-demand scans (ODS):write`

Cancel active ODS scans by explicit scan ID.

**Example prompts:**

- "Cancel ODS scan scan-123"

### `falcon_schedule_ods_scan`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `On-demand scans (ODS):write`

Create a recurring or future ODS scan schedule.

**Example prompts:**

- "Schedule a daily scan of /tmp on this Linux host"

### `falcon_delete_ods_scheduled_scans`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `On-demand scans (ODS):write`

Delete ODS schedules by explicit IDs.

**Example prompts:**

- "Delete scheduled ODS scan schedule-123"

## Resources

- **`falcon://ods/scans/fql-guide`**: FQL guide for the falcon_search_ods_scans tool.
- **`falcon://ods/scan-hosts/fql-guide`**: FQL guide for the falcon_search_ods_scan_hosts tool.
- **`falcon://ods/malicious-files/fql-guide`**: FQL guide for the falcon_search_ods_malicious_files tool.
- **`falcon://ods/scheduled-scans/fql-guide`**: FQL guide for the falcon_search_ods_scheduled_scans tool.
