<!-- meta:title Custom IOA -->
<!-- meta:description Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints

## API Scopes

- `Custom IOA Rules:read`
- `Custom IOA Rules:write`

## Tools

### `falcon_create_ioa_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Custom IOA Rules:write`

Create a new Custom IOA behavioral detection rule within a rule group.

Use falcon_get_ioa_rule_types first to discover rule type IDs, required fields,
and valid disposition IDs. The field_values parameter defines the behavioral
criteria the rule matches against (process names, file paths, command line regex).

**Example prompts:**

- "Add a process creation rule to IOA group abc123 that detects cmd.exe spawned from Word"

### `falcon_create_ioa_rule_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Custom IOA Rules:write`

Create a new Custom IOA rule group.

Rule groups are containers for behavioral detection rules scoped to a platform.
Use falcon_get_ioa_platforms to see valid platform values. After creating a
group, use falcon_create_ioa_rule to add detection rules to it.

**Example prompts:**

- "Create a Windows IOA rule group named 'Suspicious PowerShell Activity'"

### `falcon_delete_ioa_rule_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Custom IOA Rules:write`

Delete Custom IOA rule groups by ID.

Permanently removes the rule groups and all rules within them. Use
falcon_search_ioa_rule_groups to find rule group IDs.

**Example prompts:**

- "Delete Custom IOA rule groups abc123 and def456"

### `falcon_delete_ioa_rules`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Custom IOA Rules:write`

Delete Custom IOA behavioral detection rules from a rule group.

Use falcon_search_ioa_rule_groups to find the rule group ID and individual
rule instance IDs to delete.

**Example prompts:**

- "Delete rules from IOA group abc123"

### `falcon_get_ioa_platforms`

**Required scopes:** `Custom IOA Rules:read`

Get all available platforms for Custom IOA rule groups.

Use this to discover valid platform values (windows, mac, linux) before
creating a rule group. Returns platform details.

**Example prompts:**

- "What platforms are available for Custom IOA rule groups?"

### `falcon_get_ioa_rule_types`

**Required scopes:** `Custom IOA Rules:read`

Get all available Custom IOA rule types.

Use this to discover valid rule type IDs, required fields, and disposition IDs
before creating a behavioral detection rule. Returns rule type details including
platform, fields, and supported actions.

**Example prompts:**

- "What Custom IOA rule types are available?"

### `falcon_search_ioa_rule_groups`

**Required scopes:** `Custom IOA Rules:read`

Search Custom IOA rule groups and return full details including their rules.

Use this to find rule groups by platform, name, or enabled state. Consult
falcon://custom-ioa/rule-groups/fql-guide before constructing filter expressions.
Returns rule group objects with their contained behavioral detection rules.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Find enabled Windows Custom IOA rule groups"

### `falcon_update_ioa_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Custom IOA Rules:write`

Update an existing Custom IOA behavioral detection rule.

Requires rulegroup_version for optimistic locking. Get the current version
and instance_id from falcon_search_ioa_rule_groups.

**Example prompts:**

- "Enable IOA rule instance abc in group xyz"

### `falcon_update_ioa_rule_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Custom IOA Rules:write`

Update an existing Custom IOA rule group.

Modify name, description, or enabled state. Requires rulegroup_version for
optimistic locking — get it from falcon_search_ioa_rule_groups.

**Example prompts:**

- "Disable IOA rule group abc123"

## Resources

- **`falcon://custom-ioa/rule-groups/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_ioa_rule_groups` tool.
