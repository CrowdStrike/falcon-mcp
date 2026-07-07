# Discover

Access and manage CrowdStrike Falcon Discover applications and unmanaged assets.

## Tools

### `falcon_search_applications`

**Type:** read-only

Search for applications discovered in your CrowdStrike environment. Use this to find applications by name, vendor, or installation details. Consult falcon://discover/applications/fql-guide before constructing filter expressions. Returns application entities with optional host info and usage data (based on facet).

### `falcon_search_unmanaged_assets`

**Type:** read-only

Search for unmanaged assets (hosts without Falcon sensor) in your environment. Finds systems discovered by Falcon-managed hosts that lack a sensor themselves. Consult falcon://discover/hosts/fql-guide before constructing filter expressions. The tool automatically adds entity_type:'unmanaged' to all queries. Returns full asset details including platform, network, and criticality information.

## Resources

- `falcon://discover/applications/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_applications` tool.
- `falcon://discover/hosts/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.

