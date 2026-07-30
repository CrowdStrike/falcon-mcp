<!-- meta:title Hosts -->
<!-- meta:description Accessing and managing CrowdStrike Falcon hosts/devices -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon hosts/devices

## API Scopes

- `Hosts:read`
- `Hosts:write`

## Tools

### `falcon_get_host_details`

**Required scopes:** `Hosts:read`

Retrieve detailed information for one or more host device IDs.

Use when you already have specific device IDs from search results, the Falcon
console, or the Streaming API. For discovering hosts by criteria, use
falcon_search_hosts instead. Returns comprehensive host details.

**Example prompts:**

- "Get the full details for host device abc123"

### `falcon_manage_host_grouping_tags`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Hosts:write`

Add or remove Falcon Grouping Tags on one or more hosts.

Set action to 'add' to attach tags, or 'remove' to detach them, on every device
in `ids`. Grouping tags can drive dynamic host group assignment and therefore
policy assignment, so changing them may change a host's security posture.
Adding a tag a host already has, or removing one it lacks, is a no-op. Returns
one record per device, each with `device_id` and `updated`.

### `falcon_search_hosts`

**Required scopes:** `Hosts:read`

Search for hosts in your CrowdStrike environment.

Use this to find devices by hostname, platform, IP, sensor version, or other
attributes. Consult falcon://hosts/search/fql-guide before constructing filter
expressions. Returns full host details including device info, OS, and network
context.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Find all Windows hosts in my environment"
- "Show me hosts last seen in the past 24 hours"

## Resources

- **`falcon://hosts/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_hosts` tool.
