---
title: Spotlight
description: Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities
sidebar:
  order: 10
---

Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities

## API Scopes

- `Vulnerabilities:read`

## Tools

### `falcon_search_vulnerabilities`

**Required scopes:** `Vulnerabilities:read`

Search for vulnerabilities in your CrowdStrike environment.

**Example prompts:**

- "Show me open HIGH severity vulnerabilities"
- "Find vulnerabilities on host xyz"

## Resources

- **`falcon://spotlight/vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_vulnerabilities` tool.
