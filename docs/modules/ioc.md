<!-- meta:title IOC -->
<!-- meta:description Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints

## API Scopes

- `IOC Management:read`
- `IOC Management:write`

## Tools

### `falcon_add_ioc`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IOC Management:write`

Create one or more custom IOCs.

Provide type/value/action for a single IOC, or pass a bulk indicators array.
Returns the created indicator records on success.

**Example prompts:**

- "Block the domain evil.example.com"
- "Add a SHA256 hash IOC with prevent action"

### `falcon_remove_iocs`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IOC Management:write`

Remove custom IOCs by IDs or FQL filter.

Provide either specific IDs or an FQL filter for bulk removal. If both are
given, filter takes precedence. Returns a success summary with deleted IOC IDs.

**Example prompts:**

- "Delete IOC with ID abc123"
- "Remove all expired IOCs"

### `falcon_search_iocs`

**Required scopes:** `IOC Management:read`

Search custom IOCs and return full IOC details.

Use this to find IOCs by type, value, action, severity, or expiration status.
Consult falcon://ioc/search/fql-guide before constructing filter expressions.
Returns full indicator records including metadata, platforms, and host groups.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions. For cursor-based paging, use `pagination.next` as the `after` parameter on the next call.

**Example prompts:**

- "Find all active domain IOCs"
- "Show me SHA256 hash IOCs with prevent action"

## Resources

- **`falcon://ioc/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iocs` tool.
