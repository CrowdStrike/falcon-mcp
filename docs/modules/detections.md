<!-- meta:title Detections -->
<!-- meta:description Accessing and analyzing CrowdStrike Falcon detections -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and analyzing CrowdStrike Falcon detections

## API Scopes

- `Alerts:read`
- `Alerts:write`

## Tools

### `falcon_get_detection_details`

**Required scopes:** `Alerts:read`

Retrieve details for detection IDs you already have.

Use when you have specific composite detection ID(s). For discovering detections
by criteria (severity, status, hostname, etc.), use falcon_search_detections
instead. Returns full detection records.

**Example prompts:**

- "Get me the details for this detection"

### `falcon_search_detections`

**Required scopes:** `Alerts:read`

Find detections by criteria and return their complete details.

Use this to discover detections by severity, status, hostname, time range, or
other attributes. Consult falcon://detections/search/fql-guide before constructing
filter expressions. Returns full alert records including process context, device
info, tactic/technique details, and threat classification.

**Example prompts:**

- "Show me new high severity detections from the last 7 days"
- "Find all unassigned critical detections"

### `falcon_update_detections`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Alerts:write`

Update the status, assignment, visibility, or verdict of one or more detections.

Use to change status (new, in_progress, reopened, closed), assign to a user by
UUID, email address, or full name, append a comment, unassign, hide/show
detections in the UI, or set a verdict (true_positive, false_positive, ignored).
At least one update parameter must be provided. Returns `[]` (empty list) on success; returns an error dict on failure.

**Example prompts:**

- "Mark detection abc123 as in_progress"
- "Assign detection abc123 to analyst@example.com"
- "Close these detections and add a comment: resolved via playbook"

## Resources

- **`falcon://detections/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_detections` tool.
