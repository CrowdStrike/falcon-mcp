---
title: Intel
description: Accessing and analyzing CrowdStrike Falcon intelligence data
sidebar:
  order: 20
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
parsed list of dicts; CSV format returns raw CSV text.

**Example prompts:**

- "Generate MITRE ATT&CK report for FANCY BEAR"

### `falcon_search_actors`

**Required scopes:** `Actors (Falcon Intelligence):read`

Research threat actors and adversary groups tracked by CrowdStrike intelligence.

Use this to search actors by name, target countries/industries, or activity dates.
Consult falcon://intel/actors/fql-guide before constructing filter expressions.
Returns full actor profiles including aliases, motivations, and targeting details.

**Example prompts:**

- "Find threat actors targeting financial services"
- "Search for BEAR adversary groups"

### `falcon_search_indicators`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Search for threat indicators and IOCs from CrowdStrike intelligence.

Use this to find indicators by type, publish date, malware family, or threat actor
association. Consult falcon://intel/indicators/fql-guide before constructing filter
expressions. Returns full indicator details including labels, relations, and kill chain stage.

**Example prompts:**

- "Find intelligence IOCs of type domain published this year"

### `falcon_search_reports`

**Required scopes:** `Reports (Falcon Intelligence):read`

Search CrowdStrike intelligence publications and threat reports.

Use this to find reports by name, target industry, threat type, or publication date.
Consult falcon://intel/reports/fql-guide before constructing filter expressions.
Returns full report metadata including title, description, and target details.

**Example prompts:**

- "Find intelligence reports published in the last 30 days"

## Resources

- **`falcon://intel/actors/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_actors` tool.
- **`falcon://intel/indicators/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_indicators` tool.
- **`falcon://intel/reports/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_reports` tool.
