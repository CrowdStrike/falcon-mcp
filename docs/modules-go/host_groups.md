# Host Groups

Search, create, update, and delete CrowdStrike Falcon host groups, and manage group membership.

## Tools

### `falcon_create_host_group`

**Type:** mutating

Create a host group. Provide a name and group_type. 'dynamic' groups take an assignment_rule (host FQL) that automatically includes matching hosts. 'static' and 'staticByID' groups are created empty (no assignment_rule) and populated afterwards via falcon_perform_host_group_action. Returns the created host group record on success.

### `falcon_delete_host_groups`

**Type:** destructive

Delete one or more host groups. Provide the host group `ids` to delete. This permanently removes the groups. Returns an empty list on success.

### `falcon_perform_host_group_action`

**Type:** mutating

Add or remove hosts from one or more host groups. Set action_name to 'add-hosts' or 'remove-hosts', provide the target group `ids`, and a host FQL filter selecting which hosts to act on. Applies only to static groups. Returns the updated host group records on success.

### `falcon_search_host_group_members`

**Type:** read-only

Search for the host members of a specific host group. Use this to list the devices that belong to a host group. Requires the group `id` and filters on HOST attributes (platform, hostname, etc.) — consult falcon://hosts/search/fql-guide for the filter syntax. Returns full host device entities including device_id, hostname, platform, and network context.

### `falcon_search_host_groups`

**Type:** read-only

Search for host groups in your CrowdStrike environment. Use this to find host groups by name, type, creator, or timestamps. Consult falcon://host-groups/search/fql-guide before constructing filter expressions. Returns full host group details including id, name, group_type, description, and audit metadata in a single call.

### `falcon_update_host_group`

**Type:** mutating

Update an existing host group. Provide the group `id` and any fields to change. name and description are safe for any group type; only set assignment_rule on 'dynamic' groups. Unspecified fields are left unchanged. Returns the updated host group record on success.

## Resources

- `falcon://host-groups/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_host_groups` tool.

