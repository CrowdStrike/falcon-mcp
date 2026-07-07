# Cases

Manage CrowdStrike Falcon cases: search, create, update, attach evidence, manage tags, and list templates.

## Tools

### `falcon_add_case_alert_evidence`

**Type:** mutating

Attach alert evidence to an existing case. Provide alert composite_id values from the Alerts v2 API (e.g. from falcon_search_detections). Each case supports a maximum of 100 combined evidence items. Returns the updated case record.

### `falcon_add_case_event_evidence`

**Type:** mutating

Attach LogScale event evidence to an existing case. Provide event IDs obtained from falcon_search_ngsiem or the Falcon console. Each case supports a maximum of 100 combined evidence items. Returns the updated case record.

### `falcon_create_case`

**Type:** mutating

Create a new case in CrowdStrike. Provide a name and severity at minimum. Optionally attach alert or event evidence, assign a user, apply a template, and set tags. Returns the created case record.

### `falcon_get_cases`

**Type:** read-only

Retrieve details for case IDs you already have. Use when you have specific case IDs from search results or external references. For discovering cases by criteria, use falcon_search_cases instead. Returns full case records.

### `falcon_list_case_templates`

**Type:** read-only

List available case templates. Use to discover templates that can be applied when creating or updating cases. Returns template details including name, custom fields, and SLA configuration.

### `falcon_manage_case_tags`

**Type:** mutating

Add or remove tags on a case. Set action to 'add' to attach new tags, or 'remove' to delete existing tags. Returns the updated case record.

### `falcon_search_cases`

**Type:** read-only

Find cases by criteria and return their complete details. Use this to discover cases by status, severity, assignee, time range, or evidence attributes. Consult falcon://cases/search/fql-guide before constructing filter expressions. Returns full case records including status, severity, evidence, assigned user, and analysis results.

### `falcon_update_case`

**Type:** mutating

Update an existing case's fields. Provide the case ID and any fields to change. Use expected_version for optimistic concurrency control to prevent conflicting updates. Returns the updated case record with incremented version.

## Resources

- `falcon://cases/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_cases` tool.

