# Policies

Manage CrowdStrike Falcon host-based policies across prevention, sensor update, firewall, device control, response, and content update policy types.

## Tools

### `falcon_create_policy`

**Type:** mutating

Create a host-based policy of the given type. Provide a name and (for every type except content_update) a platform_name. New policies are created disabled. Clone an existing policy with clone_id to inherit its settings, then adjust with falcon_update_policy. Returns the created policy record.

### `falcon_delete_policies`

**Type:** destructive

Delete one or more host-based policies of the given type. A policy usually must be DISABLED before it can be deleted — an enabled policy returns HTTP 400. Disable it first with falcon_perform_policy_action(action_name='disable'). The Default policy of each type cannot be deleted. Returns an empty list on success.

### `falcon_perform_policy_action`

**Type:** mutating

Perform an action on one or more policies of the given type. Use this to enable/disable policies or attach/detach host groups and rule groups. action_name is validated against the actions valid for that policy_type. The add/remove-host-group and add/remove-rule-group actions require a group_id. Returns the updated policy records.

### `falcon_search_policies`

**Type:** read-only

Search host-based policies of a given type and return full policy records. Use this to find prevention, sensor update, firewall, device control, response, or content update policies by name, platform, enabled state, or timestamp — the policy_type parameter selects which policy API is queried. Consult falcon://policies/search/fql-guide before constructing filter expressions; the name match operator differs per type. Returns full policy records including id, name, platform_name, enabled, settings, and assigned host groups. WARNING: Do NOT sort by platform_name — it returns HTTP 500 on every policy type.

### `falcon_search_policy_members`

**Type:** read-only

Search for the host members governed by a specific policy. Use this to list the devices a policy is applied to. Requires the policy id; filters on HOST attributes — consult falcon://hosts/search/fql-guide for filter syntax. Returns full host device entities including device_id, hostname, platform_name, and network context.

### `falcon_set_policy_precedence`

**Type:** mutating

Set the precedence (evaluation order) of policies for a platform. The ids list must be the COMPLETE ordered set of non-Default policies for the given platform — the first id is highest precedence. Partial lists are rejected by the API. platform_name is required for every type except content_update. Returns the API response.

### `falcon_update_policy`

**Type:** mutating

Update an existing host-based policy of the given type. Provide the policy id plus any fields to change (name, description). platform_name is not updatable after creation. Unspecified fields are left unchanged. Returns the updated policy record.

## Resources

- `falcon://policies/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_policies` tool.

