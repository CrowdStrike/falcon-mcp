<!-- meta:title Discover -->
<!-- meta:description Accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets

## API Scopes

- `Assets:read`

## Tools

### `falcon_search_applications`

**Required scopes:** `Assets:read`

Search for applications discovered in your CrowdStrike environment.

Use this to find applications by name, vendor, or installation details. Consult
falcon://discover/applications/fql-guide before constructing filter expressions.
Returns application entities with optional host info and usage data (based on facet).
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Find all Chrome installations across my environment"

### `falcon_search_unmanaged_assets`

**Required scopes:** `Assets:read`

Search for unmanaged assets (hosts without Falcon sensor) in your environment.

Finds systems discovered by Falcon-managed hosts that lack a sensor themselves.
Consult falcon://discover/hosts/fql-guide before constructing filter expressions.
The tool automatically adds entity_type:'unmanaged' to all queries. Returns full
asset details including platform, network, and criticality information.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me unmanaged Windows devices on the network"

## Resources

- **`falcon://discover/applications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_applications` tool.
- **`falcon://discover/hosts/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.
