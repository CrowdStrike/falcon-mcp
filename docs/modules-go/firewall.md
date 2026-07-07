# Firewall

Search and manage CrowdStrike Falcon Firewall Management rules, rule groups, and policies.

## Tools

### `falcon_create_firewall_rule_group`

**Type:** mutating

Create a firewall rule group. Provide a name, platform, and either rules or a clone_id. Returns a list containing the created rule group object.

### `falcon_delete_firewall_rule_groups`

**Type:** destructive

Delete firewall rule groups by ID. Permanently removes the specified rule groups and all rules within them. Returns a success summary with deleted rule group IDs.

### `falcon_search_firewall_policy_rules`

**Type:** read-only

Search firewall rules within a specific policy container. Use this when you need rules scoped to a particular policy. Consult falcon://firewall/rules/fql-guide before constructing filter expressions. Returns full rule details for the specified policy.

### `falcon_search_firewall_rule_groups`

**Type:** read-only

Search firewall rule groups and return full rule group details. Use this to find rule groups by name, platform, or enabled state. Consult falcon://firewall/rules/fql-guide before constructing filter expressions. Returns rule group objects including their contained rules.

### `falcon_search_firewall_rules`

**Type:** read-only

Search firewall rules and return full rule details. Use this to find firewall rules by name, platform, or enabled state. Consult falcon://firewall/rules/fql-guide before constructing filter expressions. Returns complete rule objects including conditions and actions.

## Resources

- `falcon://firewall/rules/fql-guide` — Contains the guide for the `filter` param of firewall search tools.

