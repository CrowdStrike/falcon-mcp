# Ngsiem

Execute CQL search queries against CrowdStrike Next-Gen SIEM.

## Tools

### `falcon_search_ngsiem`

**Type:** read-only

Execute a CQL query against CrowdStrike Next-Gen SIEM. Use this to search security events, logs, and telemetry. Callers must supply a complete, valid CQL query — this tool does not assist with query construction. Returns matching event records, or an error dict if the job fails or times out.

