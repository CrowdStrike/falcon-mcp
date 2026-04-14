---
title: NGSIEM
description: Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API
sidebar:
  order: 10
---

Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API

## API Scopes

- `NGSIEM:read`
- `NGSIEM:write`

## Tools

### `falcon_search_ngsiem`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Execute a CQL query against CrowdStrike Next-Gen SIEM.

This tool executes pre-written CQL queries provided by the user. It does NOT
assist with query construction - users must supply complete, valid CQL syntax.

The tool starts an asynchronous search job, polls for completion (up to the
configured timeout), and returns matching events.

Note: Search times out after FALCON_MCP_NGSIEM_TIMEOUT seconds (default: 300).
Polling interval is controlled by FALCON_MCP_NGSIEM_POLL_INTERVAL (default: 5).

Args:
    query_string (required): The CQL query to execute. Example: '#event_simpleName=ProcessRollup2'
    start (required): ISO 8601 timestamp for search start. Example: '2025-01-01T00:00:00Z'
    repository (optional): Repository to search. Default: 'search-all'.
        Options: search-all, investigate_view, third-party, falcon_for_it_view, forensics_view
    end (optional): ISO 8601 timestamp for search end. Defaults to current time.

**Example prompts:**

- "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2"
- "Search NGSIEM for DNS events from January 2025"
