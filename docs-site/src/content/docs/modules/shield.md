---
title: Shield
description: Shield module for CrowdStrike Falcon.
sidebar:
  order: 29
---

Shield module for CrowdStrike Falcon.

## API Scopes

- `SaaS Security:read`
- `SaaS Security:write`

## Tools

### `falcon_dismiss_shield_check`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `SaaS Security:write`

Dismiss a Falcon Shield (SaaS Security) posture check to suppress it from the failed checks list.

Use this only when a check is intentionally accepted as a known risk; omit entities to dismiss
the entire check for all entities, or provide specific entity names to dismiss only those.
This action is permanent and cannot be undone from the API — the dismissal reason is recorded
in audit logs.

**Example prompts:**

- "Dismiss a low-impact Shield check entity with reason 'No longer applicable'"

### `falcon_get_shield_activity_monitor`

**Required scopes:** `SaaS Security:read`

Get events from the Falcon Shield (SaaS Security) activity monitor; data is retained for 180 days.

Use this to investigate user activity, threats, or IoC events across connected SaaS platforms;
when filtering by integration_id, category, or actor, the date range must be within 24 hours.
Returns activity event objects including timestamp, event name, actor identity, integration,
category, and location details.

**Example prompts:**

- "Show me Shield activity events from the last 24 hours"

### `falcon_get_shield_app_users`

**Required scopes:** `SaaS Security:read`

Retrieve the users who have authorized or are associated with a specific third-party app in Falcon Shield.

Use this after `search_shield_apps` to drill into a specific app's user population.
Returns user objects including email, display name, and granted permissions.

**Example prompts:**

- "Show me which users have authorized Shield app abc123"

### `falcon_get_shield_check_affected_entities`

**Required scopes:** `SaaS Security:read`

Retrieve the specific entities (users, apps, or devices) that are violating a given Falcon Shield posture check.

Use this after `search_shield_checks` to drill into which entities are failing a specific check. Returns entity
objects with entity name, type, and relevant security details.

**Example prompts:**

- "Show me the entities affected by a failed Shield check"

### `falcon_get_shield_check_compliance`

**Required scopes:** `SaaS Security:read`

Retrieve the compliance framework mappings for a specific Falcon Shield posture check.

Use this after `search_shield_checks` to understand the regulatory impact of a failing check.
Returns compliance objects identifying the framework (e.g., SOC 2, CIS, NIST, PCI DSS),
control ID, and control description that the check satisfies.

**Example prompts:**

- "Find a Shield check with compliance framework mappings"

### `falcon_get_shield_integrations`

**Required scopes:** `SaaS Security:read`

List all SaaS integrations connected to Falcon Shield and their current connection status.

Call this first when starting a Shield investigation to discover available integration IDs,
which are required as input to most other Shield tools. Returns integration objects containing
integration_id, SaaS platform name, connection health, and last sync time.

**Example prompts:**

- "List all connected SaaS integrations in Falcon Shield"

### `falcon_get_shield_posture_metrics`

**Required scopes:** `SaaS Security:read`

Get aggregated Falcon Shield (SaaS Security) posture metrics for a dashboard or summary view.

Use this for a high-level overview of your SaaS security posture; for individual check records
with remediation details, use `search_shield_checks` instead. Returns total check counts, overall
score percentage, and a breakdown of checks by status across connected SaaS applications.

**Example prompts:**

- "Show me my overall Falcon Shield posture metrics"

### `falcon_get_shield_supported_saas`

**Required scopes:** `SaaS Security:read`

List SaaS platforms supported by Falcon Shield for integration.

Use this to discover which SaaS applications can be connected before setting up new integrations.
Returns supported SaaS platform objects including platform name and ID.

**Example prompts:**

- "List all SaaS platforms supported by Falcon Shield"

### `falcon_get_shield_system_logs`

**Required scopes:** `SaaS Security:read`

Retrieve Falcon Shield (SaaS Security) system audit logs; data is retained for 90 days.

Use date range filters to narrow results, covering events such as integration creates, check
dismissals, and data syncs. Returns log objects containing timestamp, event type, actor, and details.

**Example prompts:**

- "Show me the last 10 Falcon Shield system audit logs"

### `falcon_get_shield_system_users`

**Required scopes:** `SaaS Security:read`

List Falcon Shield (SaaS Security) platform administrators.

Use this to audit console-level admin accounts; for end-users of connected SaaS applications,
use `search_shield_users` instead. Returns system-level user objects including email, role,
and MFA status.

**Example prompts:**

- "Show me the Falcon Shield platform administrators and their MFA status"

### `falcon_search_shield_alerts`

**Required scopes:** `SaaS Security:read`

Search Falcon Shield (SaaS Security) alerts for monitored SaaS applications.

Use this to find configuration drift, degraded checks, integration failures, or active threats;
use last_id from the last result for cursor-based pagination or offset for offset-based pagination.
Returns alert objects containing id, type, integration details, timestamp, and severity.

**Example prompts:**

- "Show me Shield alerts of type Threat"
- "Show me the 5 oldest Shield alerts sorted by date"

### `falcon_search_shield_apps`

**Required scopes:** `SaaS Security:read`

List third-party applications (OAuth apps, API tokens, browser extensions, service principals)
with access to Falcon Shield (SaaS Security) monitored platforms.

Use this to audit app access across your SaaS estate; use the item_id from results with
`get_shield_app_users` to see who authorized a specific app. Returns app objects containing
item_id, name, type, status, access_level, granted scopes, and user count.

**Example prompts:**

- "Find OAuth apps in Shield that haven't been active in 90 days"
- "List all Shield apps with status 'in review'"

### `falcon_search_shield_checks`

**Required scopes:** `SaaS Security:read`

Search individual Falcon Shield (SaaS Security) posture checks with filtering.

Use this to find specific failing checks by status, impact, integration, or type; consult
falcon://shield/search/query-guide for valid filter values. Returns check records containing
id, name, status, impact level, affected entity count, and remediation plan.

**Example prompts:**

- "Show me the failed Shield security checks"
- "Search for high impact Shield checks related to devices"

### `falcon_search_shield_data_shares`

**Required scopes:** `SaaS Security:read`

List files and resources shared externally across Falcon Shield (SaaS Security) monitored applications.

Use this to identify overshared or externally exposed files such as Google Drive documents shared
outside the organization. Returns resource objects containing resource name, type, owner, sharing
access level, password protection status, and last access/modification timestamps.

**Example prompts:**

- "Find files shared via public link in Shield"

### `falcon_search_shield_devices`

**Required scopes:** `SaaS Security:read`

List devices registered to users in Falcon Shield (SaaS Security) connected SaaS applications.

Use this to identify unmanaged or unassociated devices in your SaaS estate; note that this returns
devices from SaaS provider records, not Falcon sensor inventory — use `search_hosts` for that.
Returns device objects containing device name, owner email, compliance posture, and management status.

**Example prompts:**

- "Show me devices in Shield not associated with any known user"

### `falcon_search_shield_users`

**Required scopes:** `SaaS Security:read`

List end-users discovered across Falcon Shield (SaaS Security) connected SaaS applications.

Use this to audit user access across your SaaS estate or identify over-privileged or stale accounts;
for Shield platform administrators instead of SaaS app end-users, use `get_shield_system_users`.
Returns user objects containing email, display name, connected application details, privilege status,
and exposure metrics.

**Example prompts:**

- "List privileged users across my connected SaaS apps in Shield"

## Resources

- **`falcon://shield/search/query-guide`**: Query parameter guide for Falcon Shield (SaaS Security) tools.
