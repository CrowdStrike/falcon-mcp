---
title: Intel
description: Accessing and analyzing CrowdStrike Falcon intelligence data
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon intelligence data

## API Scopes

- `Actors (Falcon Intelligence):read`
- `Indicators (Falcon Intelligence):read`
- `Reports (Falcon Intelligence):read`

## Tools

### `falcon_get_mitre_report`

**Required scopes:** `Actors (Falcon Intelligence):read`

Generate MITRE ATT&CK report for a given threat actor.

Provides detailed MITRE ATT&CK tactics, techniques, and procedures (TTPs)
report associated with a specific threat actor tracked.

Args:
    actor: Pass the actor name (string) or numeric actor ID (string).
    format: Report format. Accepted options: 'csv' or 'json'. Defaults to 'json'.

**Example prompts:**

- "Generate MITRE ATT&CK report for FANCY BEAR"

### `falcon_query_actor_entities`

**Required scopes:** `Actors (Falcon Intelligence):read`

Research threat actors and adversary groups tracked by CrowdStrike intelligence.

### `falcon_query_indicator_entities`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Search for threat indicators and indicators of compromise (IOCs) from CrowdStrike intelligence.

### `falcon_query_report_entities`

**Required scopes:** `Reports (Falcon Intelligence):read`

Access CrowdStrike intelligence publications and threat reports.

This tool returns comprehensive intelligence report details based on your search criteria.
Use this when you need to find CrowdStrike intelligence publications matching specific conditions.
For guidance on building FQL filters, use the `falcon://intel/reports/fql-guide` resource.

## Resources

- **`falcon://intel/actors/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_actors` tool.
- **`falcon://intel/indicators/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_indicators` tool.
- **`falcon://intel/reports/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_reports` tool.
