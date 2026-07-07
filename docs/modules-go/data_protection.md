# Data Protection

Read-only access to CrowdStrike Falcon Data Protection classifications, policies, and content patterns.

## Tools

### `falcon_search_data_protection_classifications`

**Type:** read-only

Search for Data Protection classifications in your CrowdStrike environment. Use this to find classification rules that define what sensitive data patterns to detect. Consult falcon://data-protection/classifications/fql-guide before constructing filter expressions. Returns full classification details including content pattern references and rule configuration.

### `falcon_search_data_protection_content_patterns`

**Type:** read-only

Search for Data Protection content patterns in your CrowdStrike environment. Use this to find regex-based content detection patterns by type, category, or region. Consult falcon://data-protection/content-patterns/fql-guide before constructing filter expressions. Returns full pattern details including regex definitions and match thresholds.

### `falcon_search_data_protection_policies`

**Type:** read-only

Search for Data Protection policies in your CrowdStrike environment. Use this to find data protection policies by platform, enablement status, or precedence. Requires a platform_name ('win' or 'mac'). Consult falcon://data-protection/policies/fql-guide before constructing filter expressions. Returns full policy details including host groups and classification assignments.

## Resources

- `falcon://data-protection/classifications/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_data_protection_classifications` tool.
- `falcon://data-protection/policies/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_data_protection_policies` tool.
- `falcon://data-protection/content-patterns/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_data_protection_content_patterns` tool.

