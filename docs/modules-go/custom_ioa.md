# Custom Ioa

Search, create, update, and delete Custom IOA behavioral rule groups and rules in CrowdStrike Falcon.

## Tools

### `falcon_create_ioa_rule`

**Type:** mutating

Create a new Custom IOA behavioral detection rule within a rule group. Use falcon_get_ioa_rule_types first to discover rule type IDs, required fields, and valid disposition IDs. The field_values parameter defines the behavioral criteria the rule matches against (process names, file paths, command line regex). Returns the created rule on success.

### `falcon_create_ioa_rule_group`

**Type:** mutating

Create a new Custom IOA rule group. Rule groups are containers for behavioral detection rules scoped to a platform. Use falcon_get_ioa_platforms to see valid platform values. After creating a group, use falcon_create_ioa_rule to add detection rules to it. Returns the created rule group on success.

### `falcon_delete_ioa_rule_groups`

**Type:** destructive

Delete Custom IOA rule groups by ID. Permanently removes the rule groups and all rules within them. Use falcon_search_ioa_rule_groups to find rule group IDs. Returns an empty list on success.

### `falcon_delete_ioa_rules`

**Type:** destructive

Delete Custom IOA behavioral detection rules from a rule group. Use falcon_search_ioa_rule_groups to find the rule group ID and individual rule instance IDs to delete. Returns an empty list on success.

### `falcon_get_ioa_platforms`

**Type:** read-only

Get all available platforms for Custom IOA rule groups. Use this to discover valid platform values (windows, mac, linux) before creating a rule group. Returns platform details.

### `falcon_get_ioa_rule_types`

**Type:** read-only

Get all available Custom IOA rule types. Use this to discover valid rule type IDs, required fields, and disposition IDs before creating a behavioral detection rule. Returns rule type details including platform, fields, and supported actions.

### `falcon_search_ioa_rule_groups`

**Type:** read-only

Search Custom IOA rule groups and return full details including their rules. Use this to find rule groups by platform, name, or enabled state. Consult falcon://custom-ioa/rule-groups/fql-guide before constructing filter expressions. Returns rule group objects with their contained behavioral detection rules.

### `falcon_update_ioa_rule`

**Type:** mutating

Update an existing Custom IOA behavioral detection rule. Requires rulegroup_version for optimistic locking. Get the current version and instance_id from falcon_search_ioa_rule_groups. Returns the updated rule on success.

### `falcon_update_ioa_rule_group`

**Type:** mutating

Update an existing Custom IOA rule group. Modify name, description, or enabled state. Requires rulegroup_version for optimistic locking — get it from falcon_search_ioa_rule_groups. Returns the updated rule group on success.

## Resources

- `falcon://custom-ioa/rule-groups/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_ioa_rule_groups` tool.

