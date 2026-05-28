---
title: Data Protection (DLP)
description: Provides read-only access to DLP configuration data — classifications, policies, and content patterns — so an LLM can reason about why a DLP detection fired
sidebar:
  order: 10
---

Provides read-only access to DLP configuration data — classifications, policies, and content patterns — so an LLM can reason about why a DLP detection fired

## API Scopes

- `Data Protection:read`

## Tools

### `falcon_search_dlp_classifications`

**Required scopes:** `Data Protection:read`

Search for DLP classifications in your CrowdStrike environment.

Use this to find classification rules that define what sensitive data
patterns to detect. Consult falcon://dlp/classifications/fql-guide before
constructing filter expressions. Returns full classification details
including content pattern references and rule configuration.

**Example prompts:**

- "What DLP classifications are configured in my environment?"
- "Show me the classification rules that detect credit card data"

### `falcon_search_dlp_content_patterns`

**Required scopes:** `Data Protection:read`

Search for DLP content patterns in your CrowdStrike environment.

Use this to find regex-based content detection patterns by type, category,
or region. Consult falcon://dlp/content-patterns/fql-guide before
constructing filter expressions. Returns full pattern details including
regex definitions and match thresholds.

**Example prompts:**

- "What predefined content patterns are available for DLP?"
- "Show me custom DLP regex patterns in the Financial category"

### `falcon_search_dlp_policies`

**Required scopes:** `Data Protection:read`

Search for DLP policies in your CrowdStrike environment.

Use this to find data protection policies by platform, enablement status,
or precedence. Requires a platform_name ('win' or 'mac'). Consult
falcon://dlp/policies/fql-guide before constructing filter expressions.
Returns full policy details including host groups and classification
assignments.

**Example prompts:**

- "List all enabled Windows DLP policies"
- "Show me the Mac DLP policies and their precedence order"

## Resources

- **`falcon://dlp/classifications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_dlp_classifications` tool.
- **`falcon://dlp/policies/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_dlp_policies` tool.
- **`falcon://dlp/content-patterns/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_dlp_content_patterns` tool.
