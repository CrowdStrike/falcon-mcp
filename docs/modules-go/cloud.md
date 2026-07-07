# Cloud

Access and analyze CrowdStrike Falcon cloud resources: Kubernetes containers, container image vulnerabilities, CSPM assets, IOM findings, and suppression rules.

## Tools

### `falcon_count_kubernetes_containers`

**Type:** read-only

Count Kubernetes containers matching filter criteria. Use this for aggregate counts without returning full container details. Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter expressions. Returns the matching container count as an integer.

### `falcon_create_cspm_suppression_rule`

**Type:** mutating

Create a CSPM IOM suppression rule to hide matching findings. Suppressed findings are still assessed but not surfaced in compliance scores. Requires at least one rule selection (rule_ids, rule_names, or rule_severities) and a suppression reason. Setting an expiration_date is strongly recommended to avoid permanent suppressions. Returns the created suppression rule object.

### `falcon_delete_cspm_suppression_rules`

**Type:** destructive

Delete CSPM IOM suppression rules by ID. Deleting a suppression rule re-activates all findings that were previously suppressed by it. Use falcon_search_cspm_suppression_rules to find rule IDs first. Returns a confirmation response.

### `falcon_search_cspm_assets`

**Type:** read-only

Search for cloud assets in your CrowdStrike CSPM inventory. Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region, resource type, or tags. Consult falcon://cloud/cspm-assets/fql-guide before constructing filter expressions. Returns slimmed asset details with security posture context (IOM/IOA counts, exposure, severity).

### `falcon_search_cspm_suppression_rules`

**Type:** read-only

Search for CSPM IOM suppression rules. Use this to review existing suppressions before creating new ones. Returns suppression rule objects including scope, reason, and expiration details. Returns an empty list if no rules exist.

### `falcon_search_images_vulnerabilities`

**Type:** read-only

Search for container image vulnerabilities in CrowdStrike Image Assessments. Use this to find CVEs affecting container images by severity, CVSS score, or CVE ID. Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing filter expressions. Returns vulnerability details including CVE IDs, scores, and impacted image counts.

### `falcon_search_iom_findings`

**Type:** read-only

Search for CSPM Indicators of Misconfiguration (IOM) findings. Use this to find cloud misconfigurations by severity, provider, service, or suppression state. Consult falcon://cloud/cspm-iom-findings/fql-guide before constructing filter expressions. Returns IOM entities with cloud context, evaluation details, and resource information.

### `falcon_search_kubernetes_containers`

**Type:** read-only

Search for Kubernetes containers in your CrowdStrike container inventory. Use this to find containers by cluster, namespace, image, or cloud provider. Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter expressions. Returns full container details including image, status, and vulnerabilities.

## Resources

- `falcon://cloud/kubernetes-containers/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- `falcon://cloud/images-vulnerabilities/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- `falcon://cloud/cspm-assets/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
- `falcon://cloud/cspm-iom-findings/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.

