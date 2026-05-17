<!-- meta:title Hosts -->
<!-- meta:description Accessing and managing CrowdStrike Falcon hosts/devices -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon hosts/devices

## API Scopes

- `Hosts:read`

## Tools

### `falcon_get_host_details`

**Required scopes:** `Hosts:read`

Retrieve detailed information for one or more host device IDs.

Use when you already have specific device IDs from search results, the Falcon
console, or the Streaming API. For discovering hosts by criteria, use
falcon_search_hosts instead. Returns comprehensive host details.

**Example prompts:**

- "Get the full details for host device abc123"

### `falcon_search_hosts`

**Required scopes:** `Hosts:read`

Search for hosts in your CrowdStrike environment.

Use this to find devices by hostname, platform, IP, sensor version, or other
attributes. Consult falcon://hosts/search/fql-guide before constructing filter
expressions. Returns full host details including device info, OS, and network
context.

**Example prompts:**

- "Find all Windows hosts in my environment"
- "Show me hosts last seen in the past 24 hours"

## Resources

- **`falcon://hosts/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_hosts` tool.
