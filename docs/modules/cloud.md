<!-- meta:title Cloud Security -->
<!-- meta:description Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, IOM Findings, CSPM Suppression Rules, Cloud Risks, Cloud Groups, and Cloud Insights -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, IOM Findings, CSPM Suppression Rules, Cloud Risks, Cloud Groups, and Cloud Insights

## API Scopes

- `Cloud Groups V2:read`
- `Cloud Security API Assets:read`
- `Cloud Security API Detections:read`
- `Cloud Security API Risks:read`
- `Cloud Security Policies:read`
- `Falcon Container Image:read`
- `Cloud Security Policies:write`

## Tools

### `falcon_search_cloud_insights`

> [!NOTE]
> Not available on CrowdStrike's hosted Falcon MCP. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

**Required scopes:** `Cloud Security API Assets:read`, `Cloud Security Policies:read`

Search for cloud security insights using FQL.

Returns asset records — one per asset — each with asset context and a nested
`insights` array of insight facts. Omit `filter` to return all assets that have
any insight; pass `insights.id:['id1','id2']` to scope by insight type. Use
`falcon_get_cloud_asset_insights` for the full per-asset detail. Consult
falcon://cloud/cloud-insights/fql-guide for filter syntax and field reference.
Responses include `pagination.total` and `pagination.next` for cursor-based paging.

**Example prompts:**

- "What is internet-exposed in my cloud accounts?"
- "Which IAM identities have admin and are actually unused?"
- "Which exposed storage might hold sensitive data?"
- "Which access keys are stale or unrotated?"

### `falcon_get_cloud_asset_insights`

> [!NOTE]
> Not available on CrowdStrike's hosted Falcon MCP. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

**Required scopes:** `Cloud Security API Assets:read`

Retrieve the full insight detail for one or more cloud ASSET IDs.

Takes cloud asset IDs (not insight-definition IDs) and returns each asset's
complete `cloud_context.insights` — both the `external[]` insight instances and
the richer `details{}` map (per-insight value, context, and calculatedAt) — plus
asset context. Use this to drill into why an asset is flagged after finding it with
falcon_search_cloud_insights or falcon_search_cspm_assets. Returns one record per
requested asset that has insight data.

**Example prompts:**

- "Show me all the insight facts and context for cloud asset abc-123"
- "Why is this asset flagged — give me its full insight detail"

### `falcon_list_cloud_insight_definitions`

> [!NOTE]
> Not available on CrowdStrike's hosted Falcon MCP. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

**Required scopes:** `Cloud Security Policies:read`

Return all available cloud insight definitions, deduplicated by insight_id.

Each entry represents one unique insight type with aggregated providers,
resource_types, and (when non-empty) compliance framework controls. Call this
first to discover valid insight_ids before filtering with falcon_search_cloud_insights.
Returns the standard pagination envelope; `pagination.total` is an exact count
rather than an estimate, because the catalog is assembled and counted locally
rather than server-paged. When `categories` is supplied it counts the matching
entries, not the whole catalog.

**Example prompts:**

- "What cloud security insights are available for Identity?"
- "List all insight definitions across all categories"
- "Which compliance controls map to cloud network insights?"

### `falcon_search_cspm_assets`

**Required scopes:** `Cloud Security API Assets:read`

Search for cloud assets in your CrowdStrike CSPM inventory.

Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region,
resource type, or tags. Consult falcon://cloud/cspm-assets/fql-guide before
constructing filter expressions. Returns slimmed asset details with security
posture context (IOM/IOA counts, exposure, severity).
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions. For cursor-based paging, use `pagination.next` as the `after` parameter on the next call.

**Example prompts:**

- "Find all AWS EC2 instances in my cloud inventory"

### `falcon_search_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Search for Kubernetes containers in your CrowdStrike container inventory.

Use this to find containers by cluster, namespace, image, or cloud provider.
Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter
expressions. Returns full container details including image, status, and vulnerabilities.

**Example prompts:**

- "Find all containers running in AWS clusters"
- "Show me containers in the prod cluster"

### `falcon_count_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Count Kubernetes containers matching filter criteria.

Use this for aggregate counts without returning full container details. Consult
falcon://cloud/kubernetes-containers/fql-guide before constructing filter
expressions. Returns the matching container count as an integer.

**Example prompts:**

- "How many containers are running in Azure?"

### `falcon_search_images_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for container image vulnerabilities in CrowdStrike Image Assessments.

Use this to find CVEs affecting container images by severity, CVSS score, or
CVE ID. Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing
filter expressions. Returns vulnerability details including CVE IDs, scores, and
impacted image counts.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Find image vulnerabilities with CVSS score above 7"

### `falcon_search_iom_findings`

**Required scopes:** `Cloud Security API Detections:read`

Search for CSPM Indicators of Misconfiguration (IOM) findings.

Use this to find specific compliance rule failures on individual cloud resources —
each IOM is a single rule-against-resource violation (e.g. "S3 bucket ACL allows
public write" on a named bucket). For aggregated risk posture combining multiple
IOMs and IOAs across assets, use falcon_search_cloud_risks instead. For runtime
behavioral threats, use falcon_search_detections. Consult
falcon://cloud/cspm-iom-findings/fql-guide before constructing filter expressions.
Returns IOM entities with cloud context, evaluation details, and resource information.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me critical open CSPM misconfiguration findings in AWS"
- "Find IOM findings for S3 buckets with public access"
- "What CSPM IOM findings are suppressed as accepted risk?"

### `falcon_search_cspm_suppression_rules`

**Required scopes:** `Cloud Security Policies:read`

Search for CSPM IOM suppression rules.

Use this to review existing suppressions before creating new ones. Returns
suppression rule objects including scope, reason, and expiration details.
Returns an empty list if no rules exist.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "List all CSPM IOM suppression rules and their reasons"
- "Show me which CSPM findings are being suppressed and why"

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

### `falcon_search_cloud_risks`

**Required scopes:** `Cloud Security API Risks:read`

Search for cloud risks in your CrowdStrike environment.

Use this to find risks by severity, status, cloud provider, account, asset, rule,
or threat actor. Cloud risks aggregate IOM and IOA findings into per-asset risk
records and include threat intelligence attribution. For individual compliance rule
violations on specific resources, use falcon_search_iom_findings instead.

For the underlying per-asset security facts that risks are computed from, use
falcon_search_cloud_insights instead — that covers all insight categories:
Identity (MFA status, admin privileges, credential rotation, unused accounts),
Network (internet exposure, public IPs, access ranges),
Vulnerabilities (reachable CVEs, RCE, sensor presence),
Data (secrets, sensitive data, encryption, logging),
AI (LLM model usage, MCP server exposure),
Application (third-party vendor compliance, excessive permissions).

Consult falcon://cloud/cloud-risks/fql-guide before constructing filter expressions.
Returns full risk details including severity, lifecycle status, asset context, and
threat intelligence attribution.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me all open critical cloud risks in AWS"
- "Which account has the most unresolved critical risks?"
- "What new cloud risks appeared in the last 7 days?"
- "Show me risks for the production cloud group"
- "What cloud risks have been suppressed and why?"

### `falcon_search_cloud_groups`

**Required scopes:** `Cloud Groups V2:read`

List cloud groups in your CrowdStrike environment.

Use this to discover available cloud groups before filtering risks by
`cloud_group` or `groups.*` FQL fields in `falcon_search_cloud_risks`.
Returns full group details including name, selectors, and tags.

**Example prompts:**

- "What cloud groups are configured in my environment?"
- "List all cloud groups tagged as production"

### `falcon_get_cloud_groups`

**Required scopes:** `Cloud Groups V2:read`

Get detailed information for cloud groups by ID.

Use when you already have specific cloud group IDs — for example, the `cloud_groups`
field returned by `falcon_search_cloud_risks`. Returns full group details including
name, selectors, business impact, and environment tags.

**Example prompts:**

- "Get the details for cloud group abc-123"

## Resources

- **`falcon://cloud/cloud-insights/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cloud_insights` tool.
- **`falcon://cloud/cspm-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
- **`falcon://cloud/kubernetes-containers/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- **`falcon://cloud/images-vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- **`falcon://cloud/cspm-iom-findings/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.
- **`falcon://cloud/cloud-risks/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cloud_risks` tool.
