# Spotlight

Access and manage CrowdStrike Falcon Spotlight vulnerability findings.

## Tools

### `falcon_search_vulnerabilities`

**Type:** read-only

Search for vulnerabilities in your CrowdStrike environment. Use this to find vulnerabilities by CVE severity, status, host, or remediation state. Consult falcon://spotlight/vulnerabilities/fql-guide before constructing filter expressions. Returns vulnerability details including CVE info, host context, and remediation guidance (based on facet selection).

## Resources

- `falcon://spotlight/vulnerabilities/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_vulnerabilities` tool.

