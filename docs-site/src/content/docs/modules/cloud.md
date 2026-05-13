---
title: Cloud Security
description: Accessing and analyzing CrowdStrike Falcon cloud resources including Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, CSPM Findings, and Suppression Rules
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon cloud resources including Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, CSPM Findings, and Suppression Rules

## API Scopes

- `Cloud Security API Assets:read`
- `Cloud Security API Detections:read`
- `Cloud Security Policies:read`
- `Cloud Security Policies:write`
- `CSPM Registration:read`
- `Falcon Container Image:read`

## Tools

### `falcon_count_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Count kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "How many containers are running in Azure?"

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

### `falcon_search_iom_findings`

**Required scopes:** `Cloud Security API Detections:read`

Search for CSPM Indicators of Misconfiguration (IOM) findings. Retrieves cloud security
posture findings that identify misconfigurations in your cloud environment (AWS, Azure, GCP).
Findings map to compliance frameworks (CIS, NIST, SOC2) and MITRE ATT&CK techniques.

Supports filtering by suppression state to view which findings have been accepted as risk,
marked as false positives, or have compensating controls.

Returns IOM finding entities with nested structure: `id`, `cloud` (account, provider, region),
`evaluation` (severity, status, rule, attack_types), `resource` (resource_id, type, service).

**Example prompts:**

- "Show me critical open CSPM findings in AWS"
- "Find misconfiguration findings for S3 buckets"
- "What IOM findings are suppressed as accepted risk?"
- "Show me high severity findings detected in the last week"

### `falcon_search_ioa_findings`

**Required scopes:** `CSPM Registration:read`

Search for CSPM Indicators of Attack (IOA) behavior detections. Retrieves cloud security
behavior detections that identify active attack patterns in your cloud environment. IOAs
detect runtime threats like unauthorized API calls, suspicious credential usage, and
lateral movement.

This tool uses direct parameter filtering, not FQL. Pass parameters directly rather than
building a filter query string.

**Example prompts:**

- "Show me IOA events in AWS from the last 24 hours"
- "Are there any critical IOA detections in Azure?"
- "Find IOA events related to IAM in AWS"

### `falcon_search_cspm_suppression_rules`

**Required scopes:** `Cloud Security Policies:read`

Lists suppression rules that control which IOM findings are suppressed. Suppression rules
define which rules and assets are excluded from generating active findings, along with the
reason and optional expiration date.

Returns suppression rule objects containing: id, name, domain, subdomain, rule_selection_type,
scope_type, suppression_reason, created_at, created_by.

**Example prompts:**

- "Show me all CSPM suppression rules"
- "What findings are being suppressed and why?"

### `falcon_create_cspm_suppression_rule`

**Required scopes:** `Cloud Security Policies:write`

Create a CSPM IOM suppression rule to suppress matching findings. This creates a rule that
hides matching IOM findings from compliance scores and active finding views. Suppressed
findings are still assessed but not surfaced.

A suppression rule defines:
- **WHICH rules** to suppress (by ID, name, or severity)
- **WHICH assets** to suppress them for (by cloud provider, account, region, resource)
- **WHY** (accept-risk, compensating-control, false-positive)
- **WHEN** it expires (strongly recommended)

:::caution
This is a destructive operation. Creating a suppression rule will hide matching findings
from compliance visibility. Requires the modern "Cloud Security Posture Rules" mode.
:::

**Example prompts:**

- "Suppress that S3 encryption finding in the dev account as accepted risk"
- "Create a suppression rule for the IAM password policy finding as a false positive, expires in 30 days"

### `falcon_delete_cspm_suppression_rules`

**Required scopes:** `Cloud Security Policies:write`

Delete CSPM IOM suppression rules by ID. Deleting a suppression rule will re-activate all
findings that were previously suppressed by that rule.

:::caution
This is a destructive operation. Deleted suppression rules will cause previously suppressed
findings to reappear as open findings.
:::

**Example prompts:**

- "Delete the suppression rule we just created"
- "Remove suppression rule abc-123"

### `falcon_search_images_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for images vulnerabilities in your CrowdStrike Image Assessments

**Example prompts:**

- "Find image vulnerabilities with CVSS score above 7"

### `falcon_search_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Search for kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "Find all containers running in AWS clusters"
- "Show me containers in the prod cluster"

## Resources

- **`falcon://cloud/cspm-iom-findings/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.
- **`falcon://cloud/kubernetes-containers/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- **`falcon://cloud/images-vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- **`falcon://cloud/cspm-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
