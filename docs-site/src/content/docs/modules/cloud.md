---
title: Cloud Security
description: Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets

## API Scopes

- `Cloud Security API Assets:read`
- `Cloud Security API Detections:read`
- `Cloud Security Policies:read`
- `Falcon Container Image:read`
- `Cloud Security Policies:write`

## Tools

### `falcon_count_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Count kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "How many containers are running in Azure?"

### `falcon_create_cspm_suppression_rule`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Cloud Security Policies:write`

Create a CSPM IOM suppression rule to suppress matching findings.

WARNING: This creates a suppression rule that will hide matching IOM findings
from compliance scores and active finding views. Suppressed findings are still
assessed but not surfaced. Use carefully and prefer narrow scope.

A suppression rule defines:
- WHICH rules to suppress (by ID, name, or severity)
- WHICH assets to suppress them for (by cloud provider, account, region, resource)
- WHY (accept-risk, compensating-control, false-positive)
- WHEN it expires (strongly recommended)

Requires the modern 'Cloud Security Posture Rules' mode (not legacy policies).

Returns the created suppression rule object on success, or an error dict
with details on failure.

**Example prompts:**

- "Create a CSPM suppression rule for the S3 encryption finding in the dev account as accepted risk"
- "Suppress the IAM password policy IOM finding as a false positive, expiring in 30 days"

### `falcon_delete_cspm_suppression_rules`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Cloud Security Policies:write`

Delete CSPM IOM suppression rules by ID.

WARNING: Deleting a suppression rule will re-activate all findings that were
previously suppressed by that rule. They will appear as open findings again.

Use falcon_search_cspm_suppression_rules first to identify which rules to delete.

Returns a confirmation response on success, or an error dict on failure.

**Example prompts:**

- "Delete CSPM suppression rule abc-123"
- "Remove the CSPM IOM suppression rule for the S3 public access finding"

### `falcon_search_cspm_assets`

**Required scopes:** `Cloud Security API Assets:read`

Search for cloud assets in your CrowdStrike CSPM Asset Inventory.

This tool queries cloud resources (EC2 instances, VPCs, subnets, load balancers, etc.)
managed by CrowdStrike CSPM. Supports comprehensive FQL filtering including:
- Cloud provider and resource type filtering
- Tag-based filtering (AWS/Azure/GCP tags)
- Security posture (publicly exposed, severity, IOM/IOA counts)
- Compliance status and benchmarks
- Temporal filtering (creation time, last updated)

**Example prompts:**

- "Find all AWS EC2 instances in my cloud inventory"

### `falcon_search_cspm_suppression_rules`

**Required scopes:** `Cloud Security Policies:read`

Search for CSPM IOM suppression rules.

Lists suppression rules that control which IOM findings are suppressed.
Suppression rules define which rules and assets are excluded from generating
active findings, along with the reason and optional expiration date.

Use this to review existing suppressions before creating new ones.

Returns a list of suppression rule objects containing: id, name, domain,
subdomain, disabled, rule_selection_type, scope_type, suppression_reason,
created_at, created_by. Returns an empty list if no rules exist.

**Example prompts:**

- "List all CSPM IOM suppression rules and their reasons"
- "Show me which CSPM findings are being suppressed and why"

### `falcon_search_images_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for images vulnerabilities in your CrowdStrike Image Assessments

**Example prompts:**

- "Find image vulnerabilities with CVSS score above 7"

### `falcon_search_iom_findings`

**Required scopes:** `Cloud Security API Detections:read`

Search for CSPM Indicators of Misconfiguration (IOM) findings.

Retrieves cloud security posture findings that identify misconfigurations
in your cloud environment (AWS, Azure, GCP). Findings map to compliance
frameworks (CIS, NIST, SOC2) and MITRE ATT&CK techniques.

Supports filtering by suppression state to view which findings have been
accepted as risk, marked as false positives, or have compensating controls.

Returns a list of IOM finding entities with nested structure:
- id: Unique finding identifier
- cloud: {account_id, account_name, provider, region}
- evaluation: {severity, status, attack_types, rule, created, url}
- resource: {resource_id, resource_type, service, service_category}

**Example prompts:**

- "Show me critical open CSPM misconfiguration findings in AWS"
- "Find IOM findings for S3 buckets with public access"
- "What CSPM IOM findings are suppressed as accepted risk?"

### `falcon_search_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Search for kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "Find all containers running in AWS clusters"
- "Show me containers in the prod cluster"

## Resources

- **`falcon://cloud/kubernetes-containers/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- **`falcon://cloud/images-vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- **`falcon://cloud/cspm-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
- **`falcon://cloud/cspm-iom-findings/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.
