# Detections

Access and manage CrowdStrike Falcon detections (alerts).

## Tools

### `falcon_get_detection_details`

**Type:** read-only

Retrieve details for detection IDs you already have. Use when you have specific composite detection ID(s). For discovering detections by criteria (severity, status, hostname, etc.), use falcon_search_detections instead. Returns full detection records.

### `falcon_search_detections`

**Type:** read-only

Find detections (also called alerts) by criteria and return their complete details. Use this to discover detections by severity, status, hostname, time range, or other attributes — this is the tool for general alert and detection queries. Covers alerts across all Falcon products: endpoint (EPP), identity (IDP), XDR, OverWatch, and NG-SIEM. Consult falcon://detections/search/fql-guide before constructing filter expressions. Returns full alert records including process context, device info, tactic/technique details, and threat classification.

### `falcon_update_detections`

**Type:** mutating

Update the status, assignment, visibility, comments, and tags of one or more detections. Use to change status (new, in_progress, reopened, closed), assign to a user by UUID, email address, or full name, unassign, append a comment, hide/show detections in the UI, or add/remove tags. Resolution is tag-based: applying the conventional tags true_positive, false_positive, or ignored is what populates the console's Resolution view. At least one update parameter must be provided. Returns `[]` (empty list) on success, or `{"result": [], "hint": "..."}` when closing without adding a resolution tag in this call; returns an error dict on failure.

## Resources

- `falcon://detections/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_detections` tool.

