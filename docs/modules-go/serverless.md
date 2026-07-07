# Serverless

Access and manage CrowdStrike Falcon Serverless Vulnerabilities.

## Tools

### `falcon_search_serverless_vulnerabilities`

**Type:** read-only

Search for vulnerabilities in serverless functions across all cloud providers. Use this to find CVEs in Lambda/Cloud Functions/Azure Functions by severity, provider, or runtime. Consult falcon://serverless/vulnerabilities/fql-guide before constructing filter expressions. Returns vulnerability data in SARIF format including CVE IDs, severity levels, and descriptions.

## Resources

- `falcon://serverless/vulnerabilities/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_serverless_vulnerabilities` tool.

