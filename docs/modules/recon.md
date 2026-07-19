<!-- meta:title Recon -->
<!-- meta:description Searching Falcon Intelligence Recon notifications, monitoring rules, and exposed-data records -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching Falcon Intelligence Recon notifications, monitoring rules, and exposed-data records

## API Scopes

- `Monitoring rules (Falcon Intelligence Recon):read`

## Tools

### `falcon_search_recon_exposed_data_records`

**Required scopes:** `Monitoring rules (Falcon Intelligence Recon):read`

Search Falcon Intelligence Recon exposed-data records and return their full details.

Use this to find leaked credential and PII rows associated with recon notifications —
emails, login IDs, password hashes, domains, and breach metadata. Consult
`falcon://recon/exposed-data-records/search/fql-guide` before constructing filter
expressions. These records are part of the external cyber risk monitoring capability of
CrowdStrike Counter Adversary Operations (CAO). Returns full records including credential
fields, location data, and associated notification context.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Find exposed credentials for example.com"
- "Show leaked credentials from the past 7 days"
- "Find exposed data records for a specific notification"

### `falcon_search_recon_notifications`

**Required scopes:** `Monitoring rules (Falcon Intelligence Recon):read`

Search Falcon Intelligence Recon notifications (also called recon alerts)
and return their full details.

Use this for dark web matches, leaked credentials, typosquatting matches, and breach
summaries triggered by your monitoring rules. Consult
`falcon://recon/notifications/search/fql-guide` before constructing filter expressions.
This serves the external cyber risk monitoring capability of CrowdStrike Counter Adversary
Operations (CAO). For endpoint, XDR, or NG-SIEM alerts, use `falcon_search_detections`
instead. Returns full notification records with a nested `notification` object
containing status, rule metadata, breach_summary, and item details.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me recon alerts from the past 7 days"
- "Show me new recon alerts with high priority"
- "Find recon notifications for domain monitoring rules"
- "Show typosquatting recon alerts"
- "Find leaked credential notifications from stealer logs"

### `falcon_search_recon_rules`

**Required scopes:** `Monitoring rules (Falcon Intelligence Recon):read`

Search Falcon Intelligence Recon monitoring rules and return their full details.

Use this to list the rules that generate your recon notifications — find rules by
topic (domain, email, typosquatting, brand), priority, status, or whether breach
monitoring is enabled. Consult `falcon://recon/rules/search/fql-guide` before
constructing filter expressions. These monitoring rules power the external cyber risk
monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full
rule definitions including topic, priority, filter expressions, and notification settings.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "List all active Recon monitoring rules"
- "Show typosquatting monitoring rules"
- "Find Recon rules with breach monitoring enabled"
- "List high priority domain monitoring rules"

## Resources

- **`falcon://recon/notifications/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_recon_notifications` tool.
- **`falcon://recon/rules/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_recon_rules` tool.
- **`falcon://recon/exposed-data-records/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_recon_exposed_data_records` tool.
