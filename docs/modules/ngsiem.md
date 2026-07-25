<!-- meta:title NGSIEM -->
<!-- meta:description Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API

## API Scopes

- `NGSIEM:read`
- `NGSIEM:write`

## Tools

### `falcon_search_ngsiem`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Execute a CQL (CrowdStrike Query Language) query against CrowdStrike Next-Gen SIEM.

Use this to search security events, logs, and telemetry. CQL is a pipe-based
language (`filter | command | command`); build the query from the LogScale
references cited in the query_string parameter. Start from a tag or field
filter (e.g. `#event_simpleName=ProcessRollup2`, `UserName=*`) and keep the
time range tight before adding pipes like `groupBy([...], function=count())`
or `sort()`. Returns matching event records, or an error dict if the job fails
or times out. Note: the API does not return detailed CQL parser diagnostics on
a malformed query, so get the query structure right from the references rather
than relying on error feedback. Search times out after FALCON_MCP_NGSIEM_TIMEOUT
seconds (default: 300).

**Example prompts:**

- "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2"
- "Search NGSIEM for DNS events from January 2025"
