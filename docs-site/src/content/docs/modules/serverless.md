---
title: Serverless
description: Accessing and managing CrowdStrike Falcon Serverless Vulnerabilities
sidebar:
  order: 10
---

Accessing and managing CrowdStrike Falcon Serverless Vulnerabilities

## API Scopes

- `Falcon Container Image:read`

## Tools

### `falcon_search_serverless_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for vulnerabilities in your serverless functions across all cloud service providers.

This endpoint provides security information in SARIF format, including:
- CVE IDs for identified vulnerabilities
- Severity levels
- Vulnerability descriptions
- Additional relevant details

**Example prompts:**

- "Find HIGH severity vulnerabilities in AWS Lambda functions"

## Resources

- **`falcon://serverless/vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_serverless_vulnerabilities` tool.
