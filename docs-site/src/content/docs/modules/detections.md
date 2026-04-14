---
title: Detections
description: Accessing and analyzing CrowdStrike Falcon detections
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon detections

## API Scopes

- `Alerts:read`

## Tools

### `falcon_get_detection_details`

**Required scopes:** `Alerts:read`

Retrieve details for detection IDs you already have.

Use ONLY when you have specific composite detection ID(s). To find detections
by criteria (severity, status, hostname, etc.), use `falcon_search_detections`.

**Example prompts:**

- "Get me the details for this detection"

### `falcon_search_detections`

**Required scopes:** `Alerts:read`

Find detections by criteria and return their complete details.

Use this tool to discover detections - filter by severity, status, hostname,
time range, etc. Returns full detection information including behaviors,
device context, and threat details.

**Example prompts:**

- "Show me new high severity detections from the last 7 days"
- "Find all unassigned critical detections"

## Resources

- **`falcon://detections/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_detections` tool.
