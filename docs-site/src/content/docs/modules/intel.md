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

Generate a MITRE ATT&CK report for a given threat actor.

Accepts an actor name (e.g., 'WARP PANDA') or numeric ID. Returns MITRE ATT&CK
tactics, techniques, and procedures (TTPs) for the actor. JSON format returns a
decoded string; CSV format returns CSV text.

**Example prompts:**

- "Generate MITRE ATT&CK report for FANCY BEAR"

### `falcon_query_actor_entities`

**Required scopes:** `Actors (Falcon Intelligence):read`

Research threat actors and adversary groups tracked by CrowdStrike intelligence.

Use this to search actors by name, target countries/industries, or activity dates.
Consult falcon://intel/actors/fql-guide before constructing filter expressions.
Returns full actor profiles including aliases, motivations, and targeting details.

### `falcon_query_indicator_entities`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Search for threat indicators and IOCs from CrowdStrike intelligence.

Use this to find indicators by type, publish date, malware family, or threat actor
association. Consult falcon://intel/indicators/fql-guide before constructing filter
expressions. Returns full indicator details including labels, relations, and kill chain stage.

### `falcon_query_report_entities`

**Required scopes:** `Reports (Falcon Intelligence):read`

Search CrowdStrike intelligence publications and threat reports.

Use this to find reports by name, target industry, threat type, or publication date.
Consult falcon://intel/reports/fql-guide before constructing filter expressions.
Returns full report metadata including title, description, and target details.

## Resources

- **`falcon://intel/actors/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_actors` tool.
- **`falcon://intel/indicators/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_indicators` tool.
- **`falcon://intel/reports/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_reports` tool.
