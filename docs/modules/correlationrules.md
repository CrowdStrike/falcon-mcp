<!-- meta:title Correlation Rules -->
<!-- meta:description Search, create, update, and delete NG-SIEM correlation rules, and discover and deploy pre-built rule templates. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Search, create, update, and delete NG-SIEM correlation rules, and discover and deploy pre-built rule templates.

## API Scopes

- `Correlation Rules:read`
- `Correlation Rules:write`

## Tools

### `falcon_search_correlation_rules`

**Required scopes:** `Correlation Rules:read`

Search NG-SIEM Correlation Rules and return summary rule details.

Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions.
Returns summary rule objects (id, rule_id, name, description, severity, status, state, mitre_attack, template_id, user_id, created_on, last_updated_on); use the `rule_id` field when passing results to update or
delete tools. Filter with state:'published' to get one result per rule.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
Use falcon_get_correlation_rule to retrieve the full rule object including the CQL query, schedule, execution history, and notification config.

> [!IMPORTANT]
> This tool only returns rules that have already been deployed in the tenant.
> When results are empty or the user asks what rules they *can* or *should*
> enable, always follow up with `falcon_search_correlation_rule_templates` to
> surface pre-built detection templates that can be deployed. Templates
> represent the full catalog of available detections — a tenant with zero
> matching rules may still have many relevant templates ready to deploy.

Severity mapping — use integers in API/FQL calls, show only the name when presenting to the user:
10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.

**Example prompts:**

- "Show me all active high-severity correlation rules"
- "Find correlation rules covering lateral movement tactics"

### `falcon_get_correlation_rule`

**Required scopes:** `Correlation Rules:read`

Get full details for a single NG-SIEM Correlation Rule.

Returns the complete rule object including the CQL query, schedule, execution
history, notification config, and all metadata. Use this to inspect a rule
before modifying it or to troubleshoot execution details.

**Example prompts:**

- "Show me the full details of this correlation rule"
- "What CQL query does this rule use?"

### `falcon_create_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Correlation Rules:write`

Create a new NG-SIEM Correlation Rule.

Wraps a user-provided CQL query as a scheduled detection rule. The caller must
supply the CQL query — use falcon_search_ngsiem to test queries before creating rules.
Returns the created rule record on success.

The `customer_id` parameter falls back to the `FALCON_CID` environment variable when
not provided explicitly. See [Configuration](/falcon-mcp/getting-started/configuration/)
for details.

**Example prompts:**

- "Create a correlation rule using this CQL query: #event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*"

### `falcon_update_correlation_rule`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Correlation Rules:write`

Update an existing NG-SIEM Correlation Rule.

Modifies fields on the rule and auto-publishes a new version — no separate publish
step needed. To enable/disable a rule, set status to 'active' or 'inactive'.
Only provided fields are changed; omitted fields retain current values.

**Example prompts:**

- "Disable the correlation rule — set its status to inactive"
- "Update the rule severity to critical (90)"

### `falcon_delete_correlation_rules`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Correlation Rules:write`

Permanently delete one or more NG-SIEM Correlation Rules by rule IDs.

Removes the specified rules and all their versions. This action cannot be undone —
use falcon_search_correlation_rules to confirm IDs before deleting. Returns an
empty list on success.

**Example prompts:**

- "Delete the test correlation rule we created"

### `falcon_search_correlation_rule_templates`

**Required scopes:** `Correlation Rules:read`

Search pre-built Correlation Rule templates and return summary template details.

Use this to discover detection rule templates that can be deployed as live correlation
rules. Describe what you want to detect — lateral movement, credential theft, ransomware,
phishing, etc. — and consult falcon://correlation-rule-templates/search/fql-guide for
MITRE ATT&CK tactic/technique ID mappings and natural-language search strategies.
Returns summary template objects (id, name, description, severity, vendors, mitre_attack, author, created_on, last_updated_on); use the `id` field when passing results to the deploy tool.
Responses include `pagination.total` (the total number of records matching the filter,
or null when the API does not report a count) — use it to answer "how many" questions.
Use falcon_get_correlation_rule_template to retrieve the full template including the CQL query, schedule, lookback, and trigger configuration.

Each template has a `vendors` field listing which data sources it requires.
Templates with vendors: ['CrowdStrike'] use native Falcon sensor data and need no
data connector. Other vendors require an active data connector. To check what data
is available or what connectors are needed, see
falcon://data-connectors/data-sources/mapping-guide.

Severity mapping — use integers in API/FQL calls, show only the name when presenting to the user:
10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.

**Example prompts:**

- "Find correlation rule templates for detecting lateral movement"
- "Show me templates related to ransomware or credential theft"
- "What templates can I deploy using only native Falcon sensor data?"

### `falcon_get_correlation_rule_template`

**Required scopes:** `Correlation Rules:read`

Get full details for a single Correlation Rule template.

Returns the complete template object including the CQL query, schedule, lookback,
trigger configuration, and license details. Use this to inspect a template's
detection logic before deploying it.

**Example prompts:**

- "Show me the full detection logic for this template"
- "What does this template's CQL query look for?"

### `falcon_deploy_correlation_rule_template`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Correlation Rules:write`

Deploy a Correlation Rule template as a live detection rule.

First fetches the template to get its defaults (CQL query, schedule, severity,
MITRE mappings, etc.), then checks whether a rule with the same name already
exists. If a duplicate is found, returns a structured response with the existing
rule's details instead of creating a duplicate — the caller should ask the user
whether to update the existing rule via `falcon_update_correlation_rule`.

Only `template_id` and `customer_id` are required — all other fields except
`status` use the template's built-in values when omitted. The `status` parameter
defaults to `"active"` when not provided (it does not inherit from the template).

The `customer_id` parameter falls back to the `FALCON_CID` environment variable when
not provided explicitly. See [Configuration](/falcon-mcp/getting-started/configuration/)
for details.

Typical workflow:
1. Use `falcon_search_correlation_rule_templates` to find a template
2. Pass the template's `id` here along with your `customer_id`
3. Optionally override name, severity, status, schedule, etc.

Returns the created rule record on success, or a `duplicate_found` response
when a rule with the same name already exists.

**Example prompts:**

- "Deploy the lateral movement template as an active rule"
- "Deploy this template but set severity to critical and status to inactive"

## Resources

- **`falcon://correlation-rules/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.
- **`falcon://correlation-rule-templates/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_correlation_rule_templates` tool, including MITRE ATT&CK tactic/technique ID mappings and natural-language search strategies.
