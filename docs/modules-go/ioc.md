# Ioc

Search, create, and remove custom IOCs in CrowdStrike Falcon.

## Tools

### `falcon_add_ioc`

**Type:** mutating

Create one or more custom IOCs. Provide type/value/action for a single IOC, or pass a bulk indicators array. Returns the created indicator records on success.

### `falcon_remove_iocs`

**Type:** destructive

Remove custom IOCs by IDs or FQL filter. Provide either specific IDs or an FQL filter for bulk removal. If both are given, filter takes precedence. Returns a success summary with deleted IOC IDs.

### `falcon_search_iocs`

**Type:** read-only

Search custom IOCs and return full IOC details. Use this to find IOCs by type, value, action, severity, or expiration status. Consult falcon://ioc/search/fql-guide before constructing filter expressions. Returns full indicator records including metadata, platforms, and host groups.

## Resources

- `falcon://ioc/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_iocs` tool.

