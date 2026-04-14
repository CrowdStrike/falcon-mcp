---
title: Incidents
description: Accessing and analyzing CrowdStrike Falcon incidents
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon incidents

## API Scopes

- `Incidents:read`

## Tools

### `falcon_get_behavior_details`

**Required scopes:** `Incidents:read`

Get detailed behavior information to understand attack techniques and tactics.

Use this when you already know the specific behavior ID(s) and need to retrieve their details.
For searching behaviors based on criteria, use the `falcon_search_behaviors` tool instead.

**Example prompts:**

- "Get details for behavior behav:abc123"

### `falcon_get_incident_details`

**Required scopes:** `Incidents:read`

Get comprehensive incident details to understand attack patterns and coordinated activities.

This tool returns comprehensive incident details for one or more incident IDs.
Use this when you already have specific incident IDs and need their full details.
For searching/discovering incidents, use the `falcon_search_incidents` tool instead.

**Example prompts:**

- "Get details for incident inc:abc123"

### `falcon_search_behaviors`

**Required scopes:** `Incidents:read`

Find and analyze behaviors to understand suspicious activity in your environment.

Use this when you need to find behaviors matching certain criteria rather than retrieving specific behaviors by ID.
For retrieving details of known behavior IDs, use falcon_get_behavior_details instead.

**Example prompts:**

- "Find behaviors associated with lateral movement"

### `falcon_search_incidents`

**Required scopes:** `Incidents:read`

Find and analyze security incidents to understand coordinated activity in your environment.

**Example prompts:**

- "Find all open high-severity incidents"
- "Show me incidents from the past week"

### `falcon_show_crowd_score`

**Required scopes:** `Incidents:read`

View calculated CrowdScores and security posture metrics for your environment.

**Example prompts:**

- "Show me the current CrowdScore for my environment"

## Resources

- **`falcon://incidents/crowd-score/fql-guide`**: Contains the guide for the `filter` param of the `falcon_show_crowd_score` tool.
- **`falcon://incidents/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_incidents` tool.
- **`falcon://incidents/behaviors/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_behaviors` tool.
