---
title: Data Protection
description: Provides read-only access to Data Protection configuration data — classifications, policies, and content patterns — so an LLM can reason about why a Data Protection detection fired
sidebar:
  order: 14
---

Provides read-only access to Data Protection configuration data — classifications, policies, and content patterns — so an LLM can reason about why a Data Protection detection fired

## API Scopes

- `Data Protection:read`

## Tools

### `falcon_search_data_protection_classifications`

**Required scopes:** `Data Protection:read`

Search for Data Protection classifications in your CrowdStrike environment.

Use this to find classification rules that define what sensitive data
patterns to detect. Consult
falcon://data-protection/classifications/fql-guide before constructing
filter expressions. Returns full classification details including content
pattern references and rule configuration.

**Example prompts:**

- "What Data Protection classifications are configured in my environment?"
- "Show me the classification rules that detect credit card data"

### `falcon_search_data_protection_content_patterns`

**Required scopes:** `Data Protection:read`

Search for Data Protection content patterns in your CrowdStrike environment.

Use this to find regex-based content detection patterns by type, category,
or region. Consult falcon://data-protection/content-patterns/fql-guide
before constructing filter expressions. Returns full pattern details
including regex definitions and match thresholds.

**Example prompts:**

- "What predefined content patterns are available for Data Protection?"
- "Show me custom Data Protection regex patterns in the Financial category"

### `falcon_search_data_protection_policies`

**Required scopes:** `Data Protection:read`

Search for Data Protection policies in your CrowdStrike environment.

Use this to find data protection policies by platform, enablement status,
or precedence. Requires a platform_name ('win' or 'mac'). Consult
falcon://data-protection/policies/fql-guide before constructing filter
expressions. Returns full policy details including host groups and
classification assignments.

**Example prompts:**

- "List all enabled Windows Data Protection policies"
- "Show me the Mac Data Protection policies and their precedence order"

## Resources

- **`falcon://data-protection/classifications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_protection_classifications` tool.
- **`falcon://data-protection/policies/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_protection_policies` tool.
- **`falcon://data-protection/content-patterns/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_protection_content_patterns` tool.
