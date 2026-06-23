<!-- meta:title Cloud Security -->
<!-- meta:description Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets

## API Scopes

- `Cloud Security API Assets:read`
- `Cloud Security API Detections:read`
- `Cloud Security API Groups:read`
- `Cloud Security API Risks:read`
- `Cloud Security Policies:read`
- `Falcon Container Image:read`
- `Cloud Security Policies:write`

## Tools

### `falcon_count_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Count Kubernetes containers matching filter criteria.

Use this for aggregate counts without returning full container details. Consult
falcon://cloud/kubernetes-containers/fql-guide before constructing filter
expressions. Returns the matching container count as an integer.

**Example prompts:**

- "How many containers are running in Azure?"

### `falcon_create_cspm_suppression_rule`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Cloud Security Policies:read`, `Cloud Security Policies:write`

Create a CSPM IOM suppression rule to hide matching findings.

Suppressed findings are still assessed but not surfaced in compliance scores.
Requires at least one rule selection (rule_ids, rule_names, or rule_severities)
and a suppression reason. Setting an expiration_date is strongly recommended to
avoid permanent suppressions. Returns the created suppression rule object.

**Example prompts:**

- "Create a CSPM suppression rule for the S3 encryption finding in the dev account as accepted risk"
- "Suppress the IAM password policy IOM finding as a false positive, expiring in 30 days"

### `falcon_delete_cspm_suppression_rules`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Cloud Security Policies:write`

Delete CSPM IOM suppression rules by ID.

Deleting a suppression rule re-activates all findings that were previously
suppressed by it. Use falcon_search_cspm_suppression_rules to find rule IDs
first. Returns a confirmation response.

**Example prompts:**

- "Delete CSPM suppression rule abc-123"
- "Remove the CSPM IOM suppression rule for the S3 public access finding"

### `falcon_get_cloud_groups`

**Required scopes:** `Cloud Security API Groups:read`

Get detailed information for cloud groups by ID.

Use when you already have specific cloud group IDs from `falcon_search_cloud_groups`
results. Returns full group details including name, selectors, business impact,
and environment tags.

**Example prompts:**

- "Get the details for cloud group abc-123"

### `falcon_search_cloud_groups`

**Required scopes:** `Cloud Security API Groups:read`

List cloud groups in your CrowdStrike environment.

Use this to discover available cloud groups before filtering risks by
`cloud_group` or `groups.*` FQL fields in `falcon_search_cloud_risks`.
Returns full group details including name, selectors, and tags.

**Example prompts:**

- "What cloud groups are configured in my environment?"
- "List all cloud groups tagged as production"

### `falcon_search_cloud_risks`

**Required scopes:** `Cloud Security API Risks:read`

Search for cloud risks in your CrowdStrike environment.

Use this to find risks by severity, status, cloud provider, account, asset, rule,
or threat actor. Consult falcon://cloud/cloud-risks/fql-guide before constructing
filter expressions. Returns full risk details including severity, lifecycle status,
asset context, and threat intelligence attribution.

**Example prompts:**

- "Show me all open critical cloud risks in AWS"
- "Which account has the most unresolved critical risks?"
- "What new cloud risks appeared in the last 7 days?"
- "Show me risks for the production cloud group"
- "What cloud risks have been suppressed and why?"

### `falcon_search_cspm_assets`

**Required scopes:** `Cloud Security API Assets:read`

Search for cloud assets in your CrowdStrike CSPM inventory.

Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region,
resource type, or tags. Consult falcon://cloud/cspm-assets/fql-guide before
constructing filter expressions. Returns slimmed asset details with security
posture context (IOM/IOA counts, exposure, severity).

**Example prompts:**

- "Find all AWS EC2 instances in my cloud inventory"

### `falcon_search_cspm_suppression_rules`

**Required scopes:** `Cloud Security Policies:read`

Search for CSPM IOM suppression rules.

Use this to review existing suppressions before creating new ones. Returns
suppression rule objects including scope, reason, and expiration details.
Returns an empty list if no rules exist.

**Example prompts:**

- "List all CSPM IOM suppression rules and their reasons"
- "Show me which CSPM findings are being suppressed and why"

### `falcon_search_images_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for container image vulnerabilities in CrowdStrike Image Assessments.

Use this to find CVEs affecting container images by severity, CVSS score, or
CVE ID. Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing
filter expressions. Returns vulnerability details including CVE IDs, scores, and
impacted image counts.

**Example prompts:**

- "Find image vulnerabilities with CVSS score above 7"

### `falcon_search_iom_findings`

**Required scopes:** `Cloud Security API Detections:read`

Search for CSPM Indicators of Misconfiguration (IOM) findings.

Use this to find cloud misconfigurations by severity, provider, service, or
suppression state. Consult falcon://cloud/cspm-iom-findings/fql-guide before
constructing filter expressions. Returns IOM entities with cloud context,
evaluation details, and resource information.

**Example prompts:**

- "Show me critical open CSPM misconfiguration findings in AWS"
- "Find IOM findings for S3 buckets with public access"
- "What CSPM IOM findings are suppressed as accepted risk?"

### `falcon_search_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Search for Kubernetes containers in your CrowdStrike container inventory.

Use this to find containers by cluster, namespace, image, or cloud provider.
Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter
expressions. Returns full container details including image, status, and vulnerabilities.

**Example prompts:**

- "Find all containers running in AWS clusters"
- "Show me containers in the prod cluster"

## Resources

- **`falcon://cloud/kubernetes-containers/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- **`falcon://cloud/images-vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- **`falcon://cloud/cspm-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
- **`falcon://cloud/cspm-iom-findings/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.
- **`falcon://cloud/cloud-risks/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cloud_risks` tool.
