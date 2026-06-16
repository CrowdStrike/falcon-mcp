"""
Contains Cloud resources.
"""

from falcon_mcp.common.fql import FQL_BASE_OPERATORS
from falcon_mcp.common.utils import generate_md_table

FQL_DOCUMENTATION = FQL_BASE_OPERATORS

# List of tuples containing filter options data: (name, type, description)
KUBERNETES_CONTAINERS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description"
    ),
    (
        "agent_id",
        "String",
        """
        The sensor agent ID running in the container.

        Ex: agent_id:'3c1ca4a114504ca89af51fd126991efd'
        """
    ),
    (
        "agent_type",
        "String",
        """
        The sensor agent type running in the container.

        Ex: agent_type:'Falcon sensor for linux'
        """
    ),
    (
        "ai_related",
        "Boolean",
        """
        Determines if the container hosts AI related packages.

        Ex: ai_related:true
        """
    ),
    (
        "cloud_account_id",
        "String",
        """
        The cloud provider account ID.

        Ex: cloud_account_id:'171998889118'
        """
    ),
    (
        "cloud_name",
        "String",
        """
        The cloud provider name.

        Ex: cloud_name:'AWS'
        """
    ),
    (
        "cloud_region",
        "String",
        """
        The cloud region.

        Ex: cloud_region:'us-1'
        """
    ),
    (
        "cluster_id",
        "String",
        """
        The kubernetes cluster ID of the container.

        Ex: cluster_id:'6055bde7-acfe-48ae-9ee0-0ac1a60d8eac'
        """
    ),
    (
        "cluster_name",
        "String",
        """
        The kubernetes cluster that manages the container.

        Ex: cluster_name:'prod-cluster'
        """
    ),
    (
        "container_id",
        "String",
        """
        The kubernetes container ID.

        Ex: container_id:'c30c45f9-4702-4663-bce8-cca9f2237d1d'
        """
    ),
    (
        "container_name",
        "String",
        """
        The kubernetes container name.

        Ex: container_name:'prod-cluster'
        """
    ),
    (
        "cve_id",
        "String",
        """
        The CVE ID found in the container image.

        Ex: cve_id:'CVE-2025-1234'
        """
    ),
    (
        "detection_name",
        "String",
        """
        The name of the detection found in the container image.

        Ex: detection_name:'RunningAsRootContainer'
        """
    ),
    (
        "first_seen",
        "Timestamp",
        """
        Timestamp when the kubernetes container was first seen in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").

        Ex: first_seen:'2025-01-19T11:14:15Z'
        """
    ),
    (
        "image_detection_count",
        "Number",
        """
        Number of images detections found in the container image.

        Ex: image_detection_count:5
        """
    ),
    (
        "image_digest",
        "String",
        """
        The digest of the container image.

        Ex: image_digest:'sha256:a08d3ee8ee68ebd8a78525a710c6479270692259e'
        """
    ),
    (
        "image_has_been_assessed",
        "Boolean",
        """
        Tells whether the container image has been assessed.

        Ex: image_has_been_assessed:true
        """
    ),
    (
        "image_id",
        "String",
        """
        The ID of the container image.

        Ex: image_id:'a90f484d134848af858cd409801e213e'
        """
    ),
    (
        "image_registry",
        "String",
        """
        The registry of the container image.
        """
    ),
    (
        "image_repository",
        "String",
        """
        The repository of the container image.

        Ex: image_repository:'my-app'
        """
    ),
    (
        "image_tag",
        "String",
        """
        The tag of the container image.

        Ex: image_tag:'v1.0.0'
        """
    ),
    (
        "image_vulnerability_count",
        "Number",
        """
        Number of image vulnerabilities found in the container image.

        Ex: image_vulnerability_count:1
        """
    ),
    (
        "insecure_mount_source",
        "String",
        """
        File path of the insecure mount in the container.

        Ex: insecure_mount_source:'/var/data'
        """
    ),
    (
        "insecure_mount_type",
        "String",
        """
        Type of the insecure mount in the container.

        Ex: insecure_mount_type:'hostPath'
        """
    ),
    (
        "insecure_propagation_mode",
        "Boolean",
        """
        Tells whether the container has an insecure mount propagation mode.

        Ex: insecure_propagation_mode:false
        """
    ),
    (
        "interactive_mode",
        "Boolean",
        """
        Tells whether the container is running in interactive mode.

        Ex: interactive_mode:true
        """
    ),
    (
        "ipv4",
        "String",
        """
        The IPv4 of the container.

        Ex: ipv4:'10.10.1.5'
        """
    ),
    (
        "ipv6",
        "String",
        """
        The IPv6 of the container.

        Ex: ipv6:'2001:db8::ff00:42:8329'
        """
    ),
    (
        "last_seen",
        "Timestamp",
        """
        Timestamp when the kubernetes container was last seen in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").

        Ex: last_seen:'2025-01-19T11:14:15Z'
        """
    ),
    (
        "namespace",
        "String",
        """
        The kubernetes namespace name.

        Ex: namespace:'default'
        """
    ),
    (
        "node_name",
        "String",
        """
        The name of the kubernetes node.

        Ex: node_name:'k8s-pool'
        """
    ),
    (
        "node_uid",
        "String",
        """
        The kubernetes node UID of the container.

        Ex: node_uid:'79f1741e7db542bdaaecac11a7f7b7ae'
        """
    ),
    (
        "pod_id",
        "String",
        """
        The kubernetes pod ID of the container.

        Ex: pod_id:'6ab0fffa-2662-440b-8e95-2be93e11da3c'
        """
    ),
    (
        "pod_name",
        "String",
        """
        The kubernetes pod name of the container.
        """
    ),
    (
        "port",
        "String",
        """
        The port that the container exposes.
        """
    ),
    (
        "privileged",
        "Boolean",
        """
        Tells whether the container is running with elevated privileges.

        Ex: privileged:false
        """
    ),
    (
        "root_write_access",
        "Boolean",
        """
        Tells whether the container has root write access.

        Ex: root_write_access:false
        """
    ),
    (
        "run_as_root_group",
        "Boolean",
        """
        Tells whether the container is running as root group.
        """
    ),
    (
        "run_as_root_user",
        "Boolean",
        """
        Tells whether the container is running as root user.
        """
    ),
    (
        "running_status",
        "Boolean",
        """
        Tells whether the container is running.

        Ex: running_status:true
        """
    ),
]

KUBERNETES_CONTAINERS_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_kubernetes_containers FQL filter available fields ===

""" + generate_md_table(KUBERNETES_CONTAINERS_FQL_FILTERS) + """

=== falcon_search_kubernetes_containers FQL filter examples ===

# Find kubernetes containers that are running and have 1 or more image vulnerabilities
image_vulnerability_count:>0+running_status:true

# Find kubernetes containers seen in the last 7 days and by the CVE ID found in their container images
cve_id:'CVE-2025-1234'+last_seen:>'2025-03-15T00:00:00Z'

# Find kubernetes containers whose cloud_name is in a list
cloud_name:['AWS', 'Azure']

# Find kubernetes containers whose names starts with "app-"
container_name:*'app-*'

# Find kubernetes containers whose cluster or namespace name is "prod"
cluster_name:'prod',namespace:'prod'

=== falcon_count_kubernetes_containers FQL filter examples ===

# Count kubernetes containers by cluster name
cluster_name:'staging'

# Count kubernetes containers by agent type
agent_type:'Kubernetes'
"""
)

# List of tuples containing filter options data: (name, type, description)
IMAGES_VULNERABILITIES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description"
    ),
    (
        "ai_related",
        "Boolean",
        """
        Tells whether the image has AI related packages.

        Ex: ai_related:true
        """
    ),
    (
        "base_os",
        "String",
        """
        The base operating system of the image.

        Ex: base_os:'ubuntu'
        """
    ),
    (
        "container_id",
        "String",
        """
        The kubernetes container id in which the image vulnerability was detected.

        Ex: container_id:'515f976c43eaa3edf51590e7217ac8191a7e50c59'
        """
    ),
    (
        "container_running_status",
        "Boolean",
        """
        The running status of the kubernetes container in which the image vulnerability was detected.

        Ex: container_running_status:true
        """
    ),
    (
        "cps_rating",
        "String",
        """
        The CSP rating of the image vulnerability.
        Possible values: Low, Medium, High, Critical

        Ex: cps_rating:'Critical'
        """
    ),
    (
        "cve_id",
        "String",
        """
        The CVE ID of the image vulnerability.

        Ex: cve_id:'CVE-2025-1234'
        """
    ),
    (
        "cvss_score",
        "Number",
        """
        The CVSS Score of the image vulnerability. The value must be between 0 and 10.

        Ex: cvss_score:8
        """
    ),
    (
        "image_digest",
        "String",
        """
        The digest of the image.

        Ex: image_digest:'sha256:a08d3ee8ee68ebd8a78525a710c6479270692259e'
        """
    ),
    (
        "image_id",
        "String",
        """
        The ID of the image.

        Ex: image_id:'a90f484d134848af858cd409801e213e'
        """
    ),
    (
        "registry",
        "String",
        """
        The image registry of the image in which the vulnerability was detected.

        Ex: registry:'docker.io'
        """
    ),
    (
        "repository",
        "String",
        """
        The image repository of the image in which the vulnerability was detected.

        Ex: repository:'my-app'
        """
    ),
    (
        "severity",
        "String",
        """
        The severity of the vulnerability.
        Available values: Low, Medium, High, Critical.

        Ex: severity:'High'
        """
    ),
    (
        "tag",
        "String",
        """
        The image tag of the image in which the vulnerability was detected.

        Ex: tag:'v1.0.0'
        """
    ),
]

IMAGES_VULNERABILITIES_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_images_vulnerabilities FQL filter options ===

""" + generate_md_table(IMAGES_VULNERABILITIES_FQL_FILTERS) + """

=== falcon_search_images_vulnerabilities FQL filter examples ===

# Find images vulnerabilities by container ID
container_id:'12341223'

# Find images vulnerabilities by a list of container IDs
container_id:['12341223', '199929292', '1000101']

# Find images vulnerabilities by CVSS score and container with running status true
cvss_score:>5+container_running_status:true

# Find images vulnerabilities by image registry using wildcard
registry:*'*docker*'
"""
)

# List of tuples containing filter options data: (name, type, description)
SEARCH_CSPM_ASSETS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description"
    ),
    (
        "account_id",
        "String",
        """
        The cloud provider account ID.

        Ex: account_id:'123456789012'
        """
    ),
    (
        "account_name",
        "String",
        """
        The cloud provider account name.

        Ex: account_name:'production-account'
        """
    ),
    (
        "cloud_provider",
        "String",
        """
        The cloud provider hosting the resource.
        Values: AWS, Azure, GCP (case-sensitive).

        Ex: cloud_provider:'AWS'
        Ex: cloud_provider:['AWS', 'Azure']
        """
    ),
    (
        "resource_type",
        "String",
        """
        The cloud resource type in ARN format or short format.
        Examples: AWS::EC2::Instance, ec2-instance, AWS::S3::Bucket.

        Ex: resource_type:'AWS::EC2::Instance'
        Ex: resource_type:'ec2-instance'
        Ex: resource_type:*'*S3*'
        """
    ),
    (
        "resource_id",
        "String",
        """
        The unique identifier of the cloud resource.

        Ex: resource_id:'//ec2.amazonaws.com/i-1234567890abcdef0'
        """
    ),
    (
        "region",
        "String",
        """
        The cloud region where the resource is deployed.

        Ex: region:'us-east-1'
        Ex: region:['us-east-1', 'us-west-2']
        """
    ),
    (
        "tag_key",
        "String",
        """
        Filter by cloud resource tag key name.

        Ex: tag_key:'Environment'
        Ex: tag_key:'CostCenter'
        """
    ),
    (
        "tag_value",
        "String",
        """
        Filter by cloud resource tag value.

        Ex: tag_value:'Production'
        Ex: tag_value:'*web*'
        """
    ),
    (
        "tags",
        "String",
        """
        Filter by tag in key:value format.

        Ex: tags:'Environment:Production'
        Ex: tags:'CostCenter:12345'
        """
    ),
    (
        "tags_string",
        "String",
        """
        Filter by tag string representation. Supports wildcards.

        Ex: tags_string:'*Production*'
        Ex: tags_string:'*Environment*'
        """
    ),
    (
        "creation_time",
        "Timestamp",
        """
        Timestamp when the cloud resource was created in UTC format.

        Ex: creation_time:>'2025-01-01T00:00:00Z'
        Ex: creation_time:<='2024-12-31T23:59:59Z'
        """
    ),
    (
        "updated_at",
        "Timestamp",
        """
        Timestamp when the asset was last updated in CrowdStrike in UTC format.

        Ex: updated_at:>'2025-03-01T00:00:00Z'
        """
    ),
    (
        "active",
        "Boolean",
        """
        Indicates if the asset is currently active.

        Ex: active:true
        """
    ),
    (
        "service",
        "String",
        """
        The cloud service category.
        Examples: EC2, S3, API Gateway, Lambda, VPC.

        Ex: service:'EC2'
        Ex: service:*'*Gateway*'
        """
    ),
    (
        "service_category",
        "String",
        """
        The broader service category.
        Examples: Compute, Storage, Networking, Database.

        Ex: service_category:'Compute'
        """
    ),
    (
        "location",
        "String",
        """
        The geographic location of the resource (may differ from region).

        Ex: location:'us-central1'
        Ex: location:'global'
        """
    ),
    (
        "highest_severity",
        "String",
        """
        Highest severity finding associated with the asset.
        Values: critical, high, medium, informational.

        Ex: highest_severity:'critical'
        Ex: highest_severity:['critical', 'high']
        """
    ),
    (
        "publicly_exposed",
        "Boolean",
        """
        Whether the resource is publicly exposed.

        Ex: publicly_exposed:true
        """
    ),
    (
        "status",
        "String",
        """
        Asset lifecycle status.
        Values: ResourceDiscovered, ResourceUpdated, ResourceDeleted.

        Ex: status:'ResourceDiscovered'
        """
    ),
    (
        "instance_state",
        "String",
        """
        Instance state for compute resources.

        Ex: instance_state:'running'
        Ex: instance_state:'stopped'
        """
    ),
    (
        "managed_by",
        "String",
        """
        How the asset is managed by CrowdStrike.
        Values: Sensor, Snapshot, Unmanaged.

        Ex: managed_by:'Sensor'
        Ex: managed_by:'Unmanaged'
        """
    ),
    (
        "instance_id",
        "String",
        """
        Cloud instance identifier.

        Ex: instance_id:'i-0abc123def456'
        """
    ),
    (
        "platform_name",
        "String",
        """
        OS platform name.

        Ex: platform_name:'Linux'
        Ex: platform_name:'Windows'
        """
    ),
    (
        "ioa_count",
        "Number",
        """
        Count of Indicators of Attack associated with the asset.

        Ex: ioa_count:>0
        Ex: ioa_count:>=5
        """
    ),
    (
        "iom_count",
        "Number",
        """
        Count of Indicators of Misconfiguration associated with the asset.

        Ex: iom_count:>0
        Ex: iom_count:>=10
        """
    ),
]

CSPM_IOM_FINDINGS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description"
    ),
    (
        "account_id",
        "String",
        """
        The cloud provider account ID.

        Ex: account_id:'123456789012'
        """
    ),
    (
        "account_name",
        "String",
        """
        The cloud provider account name.

        Ex: account_name:'production-account'
        """
    ),
    (
        "cloud_provider",
        "String",
        """
        The cloud provider. Values: aws, azure, gcp.

        Ex: cloud_provider:'aws'
        Ex: cloud_provider:['aws', 'azure']
        """
    ),
    (
        "severity",
        "String",
        """
        The severity of the misconfiguration finding.
        Values: critical, high, medium, low, informational.

        Ex: severity:'critical'
        Ex: severity:['critical', 'high']
        """
    ),
    (
        "status",
        "String",
        """
        The status of the finding.
        Values: open, suppressed, pass.

        Ex: status:'open'
        """
    ),
    (
        "service",
        "String",
        """
        The cloud service (e.g., EC2, S3, IAM, KeyVault, Compute Engine).

        Ex: service:'S3'
        Ex: service:'IAM'
        """
    ),
    (
        "service_category",
        "String",
        """
        Broader service category.
        Examples: Compute, Storage, Networking, Identity.

        Ex: service_category:'Identity'
        """
    ),
    (
        "region",
        "String",
        """
        The cloud region where the finding was detected.

        Ex: region:'us-east-1'
        Ex: region:['us-east-1', 'eu-west-1']
        """
    ),
    (
        "resource_id",
        "String",
        """
        The unique identifier of the affected resource.

        Ex: resource_id:'arn:aws:s3:::my-bucket'
        """
    ),
    (
        "resource_type",
        "String",
        """
        The type of cloud resource affected.

        Ex: resource_type:'AWS::S3::Bucket'
        Ex: resource_type:*'*EC2*'
        """
    ),
    (
        "resource_type_name",
        "String",
        """
        Human-readable resource type name.

        Ex: resource_type_name:'S3 Bucket'
        """
    ),
    (
        "rule_name",
        "String",
        """
        The name of the misconfiguration rule that triggered the finding.

        Ex: rule_name:*'*encryption*'
        Ex: rule_name:*'*public*'
        """
    ),
    (
        "rule_id",
        "String",
        """
        The unique rule identifier.

        Ex: rule_id:'CS-001'
        """
    ),
    (
        "policy_name",
        "String",
        """
        The policy name containing the rule.

        Ex: policy_name:*'*CIS*'
        """
    ),
    (
        "policy_id",
        "String",
        """
        The policy identifier.

        Ex: policy_id:'123'
        """
    ),
    (
        "benchmark_name",
        "String",
        """
        Compliance benchmark name (e.g., CIS, NIST, SOC2).

        Ex: benchmark_name:*'*CIS*'
        """
    ),
    (
        "framework",
        "String",
        """
        Compliance framework the finding maps to.

        Ex: framework:'CIS'
        """
    ),
    (
        "attack_type",
        "String",
        """
        MITRE ATT&CK attack type classification.

        Ex: attack_type:*'*credential*'
        """
    ),
    (
        "tactic_name",
        "String",
        """
        MITRE ATT&CK tactic name.

        Ex: tactic_name:'Credential Access'
        """
    ),
    (
        "technique_name",
        "String",
        """
        MITRE ATT&CK technique name.

        Ex: technique_name:*'*Brute Force*'
        """
    ),
    (
        "first_detected",
        "Timestamp",
        """
        When the finding was first detected in UTC format.

        Ex: first_detected:>'2025-01-01T00:00:00Z'
        """
    ),
    (
        "last_detected",
        "Timestamp",
        """
        When the finding was last detected in UTC format.

        Ex: last_detected:>'2025-04-01T00:00:00Z'
        """
    ),
    (
        "suppressed_by",
        "String",
        """
        The user or rule that suppressed this finding.

        Ex: suppressed_by:*'*admin*'
        """
    ),
    (
        "suppression_reason",
        "String",
        """
        The reason the finding was suppressed.
        Values: accept-risk, compensating-control, false-positive.

        Ex: suppression_reason:'accept-risk'
        """
    ),
    (
        "tag_key",
        "String",
        """
        Cloud resource tag key.

        Ex: tag_key:'Environment'
        """
    ),
    (
        "tag_value",
        "String",
        """
        Cloud resource tag value.

        Ex: tag_value:'Production'
        """
    ),
    (
        "cloud_group",
        "String",
        """
        Cloud group identifier for organizational grouping.

        Ex: cloud_group:'prod-group'
        """
    ),
]

CSPM_IOM_FINDINGS_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_iom_findings FQL filter available fields ===

""" + generate_md_table(CSPM_IOM_FINDINGS_FQL_FILTERS) + """

=== falcon_search_iom_findings FQL filter examples ===

# Find critical and high severity open findings
severity:['critical', 'high']+status:'open'

# Find open findings in AWS for a specific service
cloud_provider:'aws'+service:'S3'+status:'open'

# Find findings detected in the last 7 days
first_detected:>'2025-05-05T00:00:00Z'+status:'open'

# Find IAM-related misconfigurations across all clouds
service_category:'Identity'+severity:['critical', 'high']

# Find findings for a specific rule by name
rule_name:*'*encryption*'+status:'open'

# Find suppressed findings with a specific reason
status:'suppressed'+suppression_reason:'accept-risk'

# Find findings mapped to CIS benchmark
benchmark_name:*'*CIS*'+severity:'critical'

# Find findings for specific cloud accounts
account_id:['123456789012', '987654321098']+status:'open'

# Find findings by MITRE ATT&CK tactic
tactic_name:'Credential Access'+severity:['critical', 'high']

# Find findings in specific regions
region:['us-east-1', 'eu-west-1']+cloud_provider:'aws'+status:'open'

# Find findings by resource tag
tag_key:'Environment'+tag_value:'Production'+severity:'critical'
"""
)

SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_cspm_assets FQL filter available fields ===

""" + generate_md_table(SEARCH_CSPM_ASSETS_FQL_FILTERS) + """

=== falcon_search_cspm_assets FQL filter examples ===

# Find AWS production assets by tag
tag_key:'Environment'+tag_value:'Production'+cloud_provider:'AWS'

# Find EC2 instances
resource_type:'AWS::EC2::Instance'

# Find assets by multiple tags (AND condition)
tag_key:'Owner'+tag_value:'CloudOps'

# Find assets using combined tag format
tags:'Environment:Production'

# Find assets by cloud provider and region
cloud_provider:'AWS'+region:['us-east-1', 'us-west-2']

# Find assets created in the last 30 days
creation_time:>'2025-02-16T00:00:00Z'

# Find assets by service category and active status
service_category:'Compute'+active:true

# Find assets with wildcard on resource type
resource_type:*'*S3*'

# Find assets by account and service
account_name:'production-account'+service:'Lambda'

# Find publicly exposed critical-severity assets
publicly_exposed:true+highest_severity:'critical'

# Find running instances managed by Sensor
instance_state:'running'+managed_by:'Sensor'

# Find assets with active misconfigurations
iom_count:>0+cloud_provider:'AWS'

=== Cloud Resource Tag Filtering Syntax ===

Cloud resource tags (AWS/Azure/GCP) use separate filter fields for keys and values.

AVAILABLE TAG FIELDS:
• tag_key — Filter by tag key name: tag_key:'Environment'
• tag_value — Filter by tag value: tag_value:'Production'
• tags — Filter by key:value pair: tags:'Environment:Production'
• tags_string — Filter by tag string with wildcards: tags_string:'*Production*'

EXAMPLES:
tag_key:'Environment'+tag_value:'Production'   # Key + value match
tags:'Environment:Production'                  # Combined key:value format
tags_string:'*Production*'                     # Wildcard tag search
tag_key:'CostCenter'                           # Any asset with this tag key
tag_key:'Env'+tag_value:'Prod'+cloud_provider:'AWS'  # Tags + provider

=== Common Use Cases ===

# Compliance: Find production assets for audit
tag_key:'Environment'+tag_value:'Production'+tag_key:'Compliance'+tag_value:'PCI'

# Cost Management: Find resources by cost center
tags:'CostCenter:12345'+active:true

# Security: Find publicly exposed compute resources
service_category:'Compute'+publicly_exposed:true+cloud_provider:'AWS'

# Security: Find assets with critical findings
highest_severity:'critical'+managed_by:'Sensor'

# Multi-region inventory
cloud_provider:'AWS'+region:['us-east-1', 'eu-west-1']

# Recent changes: Assets updated in last 7 days
updated_at:>'2025-03-11T00:00:00Z'

# Find unmanaged assets with IOAs
managed_by:'Unmanaged'+ioa_count:>0
"""
)
