# Hosts

Access and manage CrowdStrike Falcon hosts/devices.

## Tools

### `falcon_get_host_details`

**Type:** read-only

Retrieve detailed information for one or more host device IDs. Use when you already have specific device IDs from search results, the Falcon console, or the Streaming API. For discovering hosts by criteria, use falcon_search_hosts instead.

### `falcon_search_hosts`

**Type:** read-only

Search for hosts in your CrowdStrike environment. Use this to find devices by hostname, platform, IP, sensor version, or other attributes. Consult falcon://hosts/search/fql-guide before constructing filter expressions. Returns full host details including device info, OS, and network context.

## Resources

- `falcon://hosts/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_hosts` tool.

