---
title: NGSIEM
description: Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API
sidebar:
  order: 22
---

Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API

## API Scopes

- `NGSIEM:read`
- `NGSIEM:write`

## Tools

### `falcon_search_ngsiem`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Execute a CQL query against CrowdStrike Next-Gen SIEM.

Use this to search security events, logs, and telemetry; callers must supply
a complete, valid CQL query — this tool does not assist with query construction.
Returns matching event records, or an error dict if the job fails or times out.
Search times out after FALCON_MCP_NGSIEM_TIMEOUT seconds (default: 300).

**Example prompts:**

- "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2"
- "Search NGSIEM for DNS events from January 2025"
