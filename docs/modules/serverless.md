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

Search for vulnerabilities in serverless functions across all cloud providers.

Use this to find CVEs in Lambda/Cloud Functions/Azure Functions by severity,
provider, or runtime. Consult falcon://serverless/vulnerabilities/fql-guide before
constructing filter expressions. Returns vulnerability data in SARIF format
including CVE IDs, severity levels, and descriptions.

**Example prompts:**

- "Find HIGH severity vulnerabilities in AWS Lambda functions"

## Resources

- **`falcon://serverless/vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_serverless_vulnerabilities` tool.
