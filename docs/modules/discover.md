<!-- meta:title Discover -->
<!-- meta:description Accessing and managing CrowdStrike Falcon Discover applications, managed assets, and unmanaged assets -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon Discover applications, managed assets, and unmanaged assets

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

### `falcon_search_managed_assets`

> [!NOTE]
> Not available on CrowdStrike's hosted Falcon MCP. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

**Required scopes:** `Assets:read`

Search hosts by asset and configuration posture: drive encryption status, encrypted/unencrypted drives, OS security settings (Secure Boot, Credential Guard, IOMMU), disk/memory/CPU usage, asset criticality, and internet exposure.

Use this when the question is about a device's storage, hardware, or security
configuration rather than its sensor state. For containment status, sensor version,
or policy assignment, use `falcon_search_hosts`. See
`falcon://discover/managed-assets/fql-guide` for filters; returns full asset details.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Which managed Windows hosts are unencrypted?"
- "List critical assets that don't have Credential Guard enabled"

## Resources

- **`falcon://discover/applications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_applications` tool.
- **`falcon://discover/hosts/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.
- **`falcon://discover/managed-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_managed_assets` tool.
