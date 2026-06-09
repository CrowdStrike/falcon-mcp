<!-- meta:title Policies -->
<!-- meta:description This module provides a unified set of tools for managing CrowdStrike host-based policies across all six policy types — prevention, sensor_update, firewall, device_control, response, and content_update — behind a single `policy_type` discriminator -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides a unified set of tools for managing CrowdStrike host-based policies across all six policy types — prevention, sensor_update, firewall, device_control, response, and content_update — behind a single `policy_type` discriminator

## API Scopes

- `Content Update Policies:read`
- `Device Control Policies:read`
- `Firewall Management:read`
- `Prevention Policies:read`
- `Response Policies:read`
- `Sensor Update Policies:read`
- `Content Update Policies:write`
- `Device Control Policies:write`
- `Firewall Management:write`
- `Prevention Policies:write`
- `Response Policies:write`
- `Sensor Update Policies:write`

## Tools

### `falcon_create_policy`

> [!NOTE]
> This tool modifies data.

Create a host-based policy of the given type.

Provide a name and (for every type except content_update) a platform_name.
Detailed per-type settings construction is out of scope for v1 — the
typical flow is to clone an existing policy with clone_id and then adjust
it via falcon_update_policy, or pass an opaque settings object. New
policies are created disabled. Returns the created policy record.

**Example prompts:**

- "Create a disabled firewall policy named 'Test FW' for Windows"

### `falcon_delete_policies`

> [!CAUTION]
> This tool performs destructive operations.

Delete one or more host-based policies of the given type.

Provide the policy_type and a non-empty list of policy `ids`. A policy
usually must be DISABLED before it can be deleted — an enabled policy
returns an HTTP 400. Disable it first with
falcon_perform_policy_action(action_name="disable"); this tool does not
auto-disable. The Default policy of each type cannot be deleted. Returns
the API response for the deletion.

**Example prompts:**

- "Delete firewall policy 1a2b3c"

### `falcon_perform_policy_action`

> [!NOTE]
> This tool modifies data.

Perform an action on one or more policies of the given type.

Use this to enable/disable policies or attach/detach host groups and rule
groups (and, for content_update, content overrides). action_name is
validated against the actions valid for that policy_type. The
add/remove-host-group and add/remove-rule-group actions require a group_id.
Returns the updated policy records.

**Example prompts:**

- "Disable prevention policy 1a2b3c"
- "Add host group 9z8y7x to sensor update policy 1a2b3c"

### `falcon_search_policies`

Search host-based policies of a given type and return full policy records.

Use this to find prevention, sensor update, firewall, device control,
response, or content update policies by name, platform, enabled state, or
timestamp — the `policy_type` parameter selects which policy API is
queried. Consult falcon://policies/search/fql-guide before constructing
filter expressions; the `name` match operator differs per type. Returns
full policy records including id, name, platform_name, enabled, settings,
and assigned host groups.

**Example prompts:**

- "List all firewall policies"
- "Show enabled sensor update policies for Windows"
- "Find prevention policies whose name contains 'default'"

### `falcon_search_policy_members`

Search for the host members governed by a specific policy.

Use this to list the devices a policy is applied to — answering "which
machines does this policy govern?". This differs from falcon_search_policies
(which returns the policy object, whose groups[] lists host GROUPS, not
resolved hosts) and from falcon_search_host_group_members (which lists one
group's hosts; a policy may target several groups or apply globally).
Requires the policy `id`; filters on HOST attributes — consult
falcon://hosts/search/fql-guide for the filter syntax. Returns full host
device entities including device_id, hostname, platform_name, and network
context.

**Example prompts:**

- "What hosts are assigned to firewall policy 1a2b3c?"

### `falcon_set_policy_precedence`

> [!NOTE]
> This tool modifies data.

Set the precedence (evaluation order) of policies for a platform.

The `ids` list must be the COMPLETE ordered set of non-Default policies for
the given platform — the first id is highest precedence. Partial lists are
rejected by the API. platform_name is required for every type except
content_update. Returns the API response.

**Example prompts:**

- "Set the precedence order of these Windows prevention policies: 1a2b3c, 4d5e6f, 7g8h9i"

### `falcon_update_policy`

> [!NOTE]
> This tool modifies data.

Update an existing host-based policy of the given type.

Provide the policy `id` plus any fields to change (name, description,
settings). platform_name is not updatable after creation. Uses HTTP PATCH
semantics — unspecified fields are left unchanged. Returns the updated
policy record.

**Example prompts:**

- "Rename prevention policy 1a2b3c to 'Servers - Strict'"

## Resources

- **`falcon://policies/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_policies` tool.
