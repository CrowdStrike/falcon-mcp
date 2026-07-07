# Recon

Access Falcon Intelligence Recon notifications, monitoring rules, and exposed-data records.

## Tools

### `falcon_search_recon_exposed_data_records`

**Type:** read-only

Search Falcon Intelligence Recon exposed-data records and return their full details. Use this to find leaked credential and PII rows associated with recon notifications — emails, login IDs, password hashes, domains, and breach metadata. Consult falcon://recon/exposed-data-records/search/fql-guide before constructing filter expressions. These records are part of the external cyber risk monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full records including credential fields, location data, and associated notification context.

### `falcon_search_recon_notifications`

**Type:** read-only

Search Falcon Intelligence Recon notifications (also called recon alerts) and return their full details. Use this for dark web matches, leaked credentials, typosquatting matches, and breach summaries triggered by your monitoring rules. Consult falcon://recon/notifications/search/fql-guide before constructing filter expressions. This serves the external cyber risk monitoring capability of CrowdStrike Counter Adversary Operations (CAO). For endpoint, XDR, or NG-SIEM alerts, use falcon_search_detections instead. Returns full notification records with a nested `notification` object containing status, rule metadata, breach_summary, and item details.

### `falcon_search_recon_rules`

**Type:** read-only

Search Falcon Intelligence Recon monitoring rules and return their full details. Use this to list the rules that generate your recon notifications — find rules by topic (domain, email, typosquatting, brand), priority, status, or whether breach monitoring is enabled. Consult falcon://recon/rules/search/fql-guide before constructing filter expressions. These monitoring rules power the external cyber risk monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full rule definitions including topic, priority, filter expressions, and notification settings.

## Resources

- `falcon://recon/notifications/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_recon_notifications` tool.
- `falcon://recon/rules/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_recon_rules` tool.
- `falcon://recon/exposed-data-records/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_recon_exposed_data_records` tool.

