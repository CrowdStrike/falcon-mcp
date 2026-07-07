# Correlation Rules

Manage CrowdStrike Falcon NG-SIEM Correlation Rules.

## Tools

### `falcon_create_correlation_rule`

**Type:** mutating

Create a new NG-SIEM Correlation Rule. Wraps a user-provided CQL query as a scheduled detection rule. The caller must supply the CQL query — use falcon_search_ngsiem to test queries before creating rules. Returns the created rule record on success.

### `falcon_delete_correlation_rules`

**Type:** destructive

Permanently delete NG-SIEM Correlation Rules by rule ID. Removes the specified rules and all their versions. This action cannot be undone — use falcon_search_correlation_rules to confirm IDs before deleting. Returns an empty list on success.

### `falcon_search_correlation_rules`

**Type:** read-only

Search NG-SIEM Correlation Rules and return full rule details. Use this to find detection rules by name, status, severity, or MITRE tactic/technique. Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions. Returns full rule objects; use the `rule_id` field when passing results to update or delete tools. Filter with state:'published' to get one result per rule.

### `falcon_update_correlation_rule`

**Type:** mutating

Update an existing NG-SIEM Correlation Rule. Modifies fields on the rule and auto-publishes a new version — no separate publish step needed. To enable/disable a rule, set status to 'active' or 'inactive'. Only provided fields are changed; omitted fields retain current values.

## Resources

- `falcon://correlation-rules/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.

