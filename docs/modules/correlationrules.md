<!-- meta:title Correlation Rules -->
<!-- meta:description Correlation Rules module for CrowdStrike Falcon. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Correlation Rules module for CrowdStrike Falcon.

## API Scopes

- `Correlation Rules:read`
- `Correlation Rules:write`

## Tools

### `falcon_create_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Correlation Rules:write`

Create a new NG-SIEM Correlation Rule.

Wraps a user-provided CQL query as a scheduled detection rule. The caller must
supply the CQL query — use falcon_search_ngsiem to test queries before creating rules.
Returns the created rule record on success.

**Example prompts:**

- "Create a correlation rule using this CQL query: #event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*"

### `falcon_delete_correlation_rules`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Correlation Rules:write`

Permanently delete NG-SIEM Correlation Rules by rule ID.

Removes the specified rules and all their versions. This action cannot be undone —
use falcon_search_correlation_rules to confirm IDs before deleting. Returns an
empty list on success.

**Example prompts:**

- "Delete the test correlation rule we created"

### `falcon_search_correlation_rules`

**Required scopes:** `Correlation Rules:read`

Search NG-SIEM Correlation Rules and return full rule details.

Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions.
Returns full rule objects; use the `rule_id` field when passing results to update or
delete tools. Filter with state:'published' to get one result per rule.

**Example prompts:**

- "Show me all active high-severity correlation rules"
- "Find correlation rules covering lateral movement tactics"

### `falcon_update_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Correlation Rules:write`

Update an existing NG-SIEM Correlation Rule.

Modifies fields on the rule and auto-publishes a new version — no separate publish
step needed. To enable/disable a rule, set status to 'active' or 'inactive'.
Only provided fields are changed; omitted fields retain current values.

**Example prompts:**

- "Disable the correlation rule — set its status to inactive"
- "Update the rule severity to critical (90)"

## Resources

- **`falcon://correlation-rules/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.
