# Shield

Falcon Shield (SaaS Security): query posture checks, alerts, user/device/app inventory, data shares, integrations, and audit logs for connected SaaS applications.

## Tools

### `falcon_dismiss_shield_check`

**Type:** destructive

Dismiss a Falcon Shield (SaaS Security) posture check to suppress it from the failed checks list. Use this only when a check is intentionally accepted as a known risk; omit entities to dismiss the entire check for all entities, or provide specific entity names to dismiss only those. This action is permanent and cannot be undone from the API — the dismissal reason is recorded in audit logs.

### `falcon_get_shield_activity_monitor`

**Type:** read-only

Get events from the Falcon Shield (SaaS Security) activity monitor; data is retained for 180 days. Use this to investigate user activity, threats, or IoC events across connected SaaS platforms; when filtering by integration_id, category, or actor, the date range must be within 24 hours. Returns activity event objects including timestamp, event name, actor identity, integration, category, and location details.

### `falcon_get_shield_app_users`

**Type:** read-only

Retrieve the users who have authorized or are associated with a specific third-party app in Falcon Shield. Use this after falcon_search_shield_apps to drill into a specific app's user population. Returns user objects including email, display name, and granted permissions.

### `falcon_get_shield_check_affected_entities`

**Type:** read-only

Retrieve the specific entities (users, apps, or devices) that are violating a given Falcon Shield posture check. Use this after falcon_search_shield_checks to drill into which entities are failing a specific check. Returns entity objects with entity name, type, and relevant security details.

### `falcon_get_shield_check_compliance`

**Type:** read-only

Retrieve the compliance framework mappings for a specific Falcon Shield posture check. Use this after falcon_search_shield_checks to understand the regulatory impact of a failing check. Returns compliance objects identifying the framework (e.g., SOC 2, CIS, NIST, PCI DSS), control ID, and control description that the check satisfies.

### `falcon_get_shield_integrations`

**Type:** read-only

List all SaaS integrations connected to Falcon Shield and their current connection status. Call this first when starting a Shield investigation to discover available integration IDs, which are required as input to most other Shield tools. Returns integration objects containing integration_id, SaaS platform name, connection health, and last sync time.

### `falcon_get_shield_posture_metrics`

**Type:** read-only

Get aggregated Falcon Shield (SaaS Security) posture metrics for a dashboard or summary view. Use this for a high-level overview of your SaaS security posture; for individual check records with remediation details, use falcon_search_shield_checks instead. Returns total check counts, overall score percentage, and a breakdown of checks by status across connected SaaS applications.

### `falcon_get_shield_supported_saas`

**Type:** read-only

List SaaS platforms supported by Falcon Shield for integration. Use this to discover which SaaS applications can be connected before setting up new integrations. Returns supported SaaS platform objects including platform name and ID.

### `falcon_get_shield_system_logs`

**Type:** read-only

Retrieve Falcon Shield (SaaS Security) system audit logs; data is retained for 90 days. Use date range filters to narrow results, covering events such as integration creates, check dismissals, and data syncs. Returns log objects containing timestamp, event type, actor, and details.

### `falcon_get_shield_system_users`

**Type:** read-only

List Falcon Shield (SaaS Security) platform administrators. Use this to audit console-level admin accounts; for end-users of connected SaaS applications, use falcon_search_shield_users instead. Returns system-level user objects including email, role, and MFA status.

### `falcon_search_shield_alerts`

**Type:** read-only

Search Falcon Shield (SaaS Security) alerts for monitored SaaS applications. Use this to find configuration drift, degraded checks, integration failures, or active threats; use last_id from the last result for cursor-based pagination or offset for offset-based pagination. Returns alert objects containing id, type, integration details, timestamp, and severity.

### `falcon_search_shield_apps`

**Type:** read-only

List third-party applications (OAuth apps, API tokens, browser extensions, service principals) with access to Falcon Shield (SaaS Security) monitored platforms. Use this to audit app access across your SaaS estate; use the item_id from results with falcon_get_shield_app_users to see who authorized a specific app. Returns app objects containing item_id, name, type, status, access_level, granted scopes, and user count.

### `falcon_search_shield_checks`

**Type:** read-only

Search individual Falcon Shield (SaaS Security) posture checks with filtering. Use this to find specific failing checks by status, impact, integration, or type; consult falcon://shield/search/query-guide for valid filter values. Returns check records containing id, name, status, impact level, affected entity count, and remediation plan.

### `falcon_search_shield_data_shares`

**Type:** read-only

List files and resources shared externally across Falcon Shield (SaaS Security) monitored applications. Use this to identify overshared or externally exposed files such as Google Drive documents shared outside the organization. Returns resource objects containing resource name, type, owner, sharing access level, password protection status, and last access/modification timestamps.

### `falcon_search_shield_devices`

**Type:** read-only

List devices registered to users in Falcon Shield (SaaS Security) connected SaaS applications. Use this to identify unmanaged or unassociated devices in your SaaS estate; note that this returns devices from SaaS provider records, not Falcon sensor inventory — use falcon_search_hosts for that. Returns device objects containing device name, owner email, compliance posture, and management status.

### `falcon_search_shield_users`

**Type:** read-only

List end-users discovered across Falcon Shield (SaaS Security) connected SaaS applications. Use this to audit user access across your SaaS estate or identify over-privileged or stale accounts; for Shield platform administrators instead of SaaS app end-users, use falcon_get_shield_system_users. Returns user objects containing email, display name, connected application details, privilege status, and exposure metrics.

## Resources

- `falcon://shield/search/query-guide` — Query parameter guide for Falcon Shield (SaaS Security) tools.

