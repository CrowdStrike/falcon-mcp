<!-- meta:title Firewall Management -->
<!-- meta:description Searching and managing firewall rules and rule groups -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching and managing firewall rules and rule groups

## API Scopes

- `Firewall Management:read`
- `Firewall Management:write`

## Tools

### `falcon_create_firewall_rule_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Create a firewall rule group.

Provide a name, platform, and either rules or a clone_id. Returns a list
containing the created rule group object.

**Example prompts:**

- "Create a Windows firewall rule group named 'Prod Outbound'"

### `falcon_delete_firewall_rule_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Firewall Management:write`

Delete firewall rule groups by ID.

Permanently removes the specified rule groups and all rules within them.
Returns an empty list on success.

**Example prompts:**

- "Delete firewall rule group abc123"

### `falcon_search_firewall_policy_rules`

**Required scopes:** `Firewall Management:read`

Search firewall rules within a specific policy container.

Use this when you need rules scoped to a particular policy. Consult
falcon://firewall/rules/fql-guide before constructing filter expressions.
Returns full rule details for the specified policy.

**Example prompts:**

- "Show me all rules in firewall policy abc123"

### `falcon_search_firewall_rule_groups`

**Required scopes:** `Firewall Management:read`

Search firewall rule groups and return full rule group details.

Use this to find rule groups by name, platform, or enabled state. Consult
falcon://firewall/rules/fql-guide before constructing filter expressions.
Returns rule group objects including their contained rules.

**Example prompts:**

- "Find all enabled firewall rule groups for Windows"

### `falcon_search_firewall_rules`

**Required scopes:** `Firewall Management:read`

Search firewall rules and return full rule details.

Use this to find firewall rules by name, platform, or enabled state. Consult
falcon://firewall/rules/fql-guide before constructing filter expressions.
Returns complete rule objects including conditions and actions.

**Example prompts:**

- "Show me all enabled Windows firewall rules"
- "Find firewall rules matching 'outbound'"

## Resources

- **`falcon://firewall/rules/fql-guide`**: Contains the guide for the `filter` param of firewall search tools.
