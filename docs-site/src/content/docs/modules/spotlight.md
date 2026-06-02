---
title: Spotlight
description: Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities
sidebar:
  order: 30
---

Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities

## API Scopes

- `Vulnerabilities:read`

## Tools

### `falcon_search_vulnerabilities`

**Required scopes:** `Vulnerabilities:read`

Search for vulnerabilities in your CrowdStrike environment.

Use this to find vulnerabilities by CVE severity, status, host, or remediation
state. Consult falcon://spotlight/vulnerabilities/fql-guide before constructing
filter expressions. Returns vulnerability details including CVE info, host context,
and remediation guidance (based on facet selection).

**Example prompts:**

- "Show me open HIGH severity vulnerabilities"
- "Find vulnerabilities on host xyz"

## Resources

- **`falcon://spotlight/vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_vulnerabilities` tool.
