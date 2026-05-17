---
title: IOC
description: Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints
sidebar:
  order: 10
---

Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints

## API Scopes

- `IOC Management:read`
- `IOC Management:write`

## Tools

### `falcon_add_ioc`

:::note
This tool modifies data.
:::

**Required scopes:** `IOC Management:write`

Create one or more custom IOCs.

Provide type/value/action for a single IOC, or pass a bulk indicators array.
Returns the created indicator records on success.

**Example prompts:**

- "Block the domain evil.example.com"
- "Add a SHA256 hash IOC with prevent action"

### `falcon_remove_iocs`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `IOC Management:write`

Remove custom IOCs by IDs or FQL filter.

Provide either specific IDs or an FQL filter for bulk removal. If both are
given, filter takes precedence. Returns an empty list on success.

**Example prompts:**

- "Delete IOC with ID abc123"
- "Remove all expired IOCs"

### `falcon_search_iocs`

**Required scopes:** `IOC Management:read`

Search custom IOCs and return full IOC details.

Use this to find IOCs by type, value, action, severity, or expiration status.
Consult falcon://ioc/search/fql-guide before constructing filter expressions.
Returns full indicator records including metadata, platforms, and host groups.

**Example prompts:**

- "Find all active domain IOCs"
- "Show me SHA256 hash IOCs with prevent action"

## Resources

- **`falcon://ioc/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iocs` tool.
