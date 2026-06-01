<!-- meta:title Host Groups -->
<!-- meta:description Searching, creating, updating, and deleting CrowdStrike Falcon host groups, as well as managing group membership -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, creating, updating, and deleting CrowdStrike Falcon host groups, as well as managing group membership

## API Scopes

- `Host Groups:read`
- `Host Groups:write`

## Tools

### `falcon_create_host_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Create a host group.

Provide a name and group_type. 'dynamic' groups take an assignment_rule (host
FQL) that automatically includes matching hosts. 'static' and 'staticByID' groups
are created empty (no assignment_rule) and populated afterwards via
falcon_perform_host_group_action. Returns the created host group record on success.

**Example prompts:**

- "Create a static host group called 'Critical Servers'"
- "Create a dynamic host group for all Windows hosts"

### `falcon_delete_host_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Host Groups:write`

Delete one or more host groups.

Provide the host group `ids` to delete. This permanently removes the groups.
Returns an empty list on success.

**Example prompts:**

- "Delete host group abc123"

### `falcon_perform_host_group_action`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Add or remove hosts from one or more host groups.

Set action_name to 'add-hosts' or 'remove-hosts', provide the target group
`ids`, and a host FQL filter selecting which hosts to act on. Applies only to
static groups. Returns the updated host group records on success.

**Example prompts:**

- "Add the hosts matching platform_name Windows to group abc123"
- "Remove host device xyz from host group abc123"

### `falcon_search_host_group_members`

**Required scopes:** `Host Groups:read`

Search for the host members of a specific host group.

Use this to list the devices that belong to a host group. Requires the group
`id` and filters on HOST attributes (platform, hostname, etc.) — consult
falcon://hosts/search/fql-guide for the filter syntax. Returns full host device
entities including device_id, hostname, platform, and network context.

**Example prompts:**

- "List the Windows hosts in host group abc123"
- "Show me the members of the Production Servers group"

### `falcon_search_host_groups`

**Required scopes:** `Host Groups:read`

Search for host groups in your CrowdStrike environment.

Use this to find host groups by name, type, creator, or timestamps. Consult
falcon://host-groups/search/fql-guide before constructing filter expressions.
Returns full host group details including id, name, group_type, description,
and audit metadata in a single call.

**Example prompts:**

- "Show me all static host groups"
- "Find host groups created in the last 30 days"

### `falcon_update_host_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Update an existing host group.

Provide the group `id` and any fields to change. name and description are safe
for any group type; only set assignment_rule on 'dynamic' groups. Unspecified
fields are left unchanged. Returns the updated host group record on success.

**Example prompts:**

- "Rename host group abc123 to 'Decommissioned'"
- "Update the assignment rule for the dynamic Windows group"

## Resources

- **`falcon://host-groups/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_host_groups` tool.
