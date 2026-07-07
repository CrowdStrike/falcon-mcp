=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal to
• > = greater than
• >= = greater than or equal
• < = less than
• <= = less than or equal
• ~ = text match (ignores case, spaces, punctuation)
• * = wildcard matching (not supported on all fields — see endpoint-specific notes below)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) or relative: 'now-7d', 'now-24h' (lowercase, single-quoted)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition (e.g., platform_name:'Windows'+status:'normal')
• , = OR condition (e.g., severity_name:'Critical',severity_name:'High')
• ( ) = Group expressions

IMPORTANT: Use + for AND and , for OR — do NOT use the words AND/OR.
Values must be single-quoted. Relative dates must be lowercase ('now-7d' not 'NOW-7d').
=== falcon_search_kubernetes_containers FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|agent_id|String|The sensor agent ID running in the container. Ex: agent_id:'3c1ca4a114504ca89af51fd126991efd'|
|agent_type|String|The sensor agent type running in the container. Ex: agent_type:'Falcon sensor for linux'|
|ai_related|Boolean|Determines if the container hosts AI related packages. Ex: ai_related:true|
|cloud_account_id|String|The cloud provider account ID. Ex: cloud_account_id:'171998889118'|
|cloud_name|String|The cloud provider name. Ex: cloud_name:'AWS'|
|cloud_region|String|The cloud region. Ex: cloud_region:'us-1'|
|cluster_id|String|The kubernetes cluster ID of the container. Ex: cluster_id:'6055bde7-acfe-48ae-9ee0-0ac1a60d8eac'|
|cluster_name|String|The kubernetes cluster that manages the container. Ex: cluster_name:'prod-cluster'|
|container_id|String|The kubernetes container ID. Ex: container_id:'c30c45f9-4702-4663-bce8-cca9f2237d1d'|
|container_name|String|The kubernetes container name. Ex: container_name:'prod-cluster'|
|cve_id|String|The CVE ID found in the container image. Ex: cve_id:'CVE-2025-1234'|
|detection_name|String|The name of the detection found in the container image. Ex: detection_name:'RunningAsRootContainer'|
|first_seen|Timestamp|Timestamp when the kubernetes container was first seen in UTC date format ("YYYY-MM-DDTHH:MM:SSZ"). Ex: first_seen:'2025-01-19T11:14:15Z'|
|image_detection_count|Number|Number of images detections found in the container image. Ex: image_detection_count:5|
|image_digest|String|The digest of the container image. Ex: image_digest:'sha256:a08d3ee8ee68ebd8a78525a710c6479270692259e'|
|image_has_been_assessed|Boolean|Tells whether the container image has been assessed. Ex: image_has_been_assessed:true|
|image_id|String|The ID of the container image. Ex: image_id:'a90f484d134848af858cd409801e213e'|
|image_registry|String|The registry of the container image.|
|image_repository|String|The repository of the container image. Ex: image_repository:'my-app'|
|image_tag|String|The tag of the container image. Ex: image_tag:'v1.0.0'|
|image_vulnerability_count|Number|Number of image vulnerabilities found in the container image. Ex: image_vulnerability_count:1|
|insecure_mount_source|String|File path of the insecure mount in the container. Ex: insecure_mount_source:'/var/data'|
|insecure_mount_type|String|Type of the insecure mount in the container. Ex: insecure_mount_type:'hostPath'|
|insecure_propagation_mode|Boolean|Tells whether the container has an insecure mount propagation mode. Ex: insecure_propagation_mode:false|
|interactive_mode|Boolean|Tells whether the container is running in interactive mode. Ex: interactive_mode:true|
|ipv4|String|The IPv4 of the container. Ex: ipv4:'10.10.1.5'|
|ipv6|String|The IPv6 of the container. Ex: ipv6:'2001:db8::ff00:42:8329'|
|last_seen|Timestamp|Timestamp when the kubernetes container was last seen in UTC date format ("YYYY-MM-DDTHH:MM:SSZ"). Ex: last_seen:'2025-01-19T11:14:15Z'|
|namespace|String|The kubernetes namespace name. Ex: namespace:'default'|
|node_name|String|The name of the kubernetes node. Ex: node_name:'k8s-pool'|
|node_uid|String|The kubernetes node UID of the container. Ex: node_uid:'79f1741e7db542bdaaecac11a7f7b7ae'|
|pod_id|String|The kubernetes pod ID of the container. Ex: pod_id:'6ab0fffa-2662-440b-8e95-2be93e11da3c'|
|pod_name|String|The kubernetes pod name of the container.|
|port|String|The port that the container exposes.|
|privileged|Boolean|Tells whether the container is running with elevated privileges. Ex: privileged:false|
|root_write_access|Boolean|Tells whether the container has root write access. Ex: root_write_access:false|
|run_as_root_group|Boolean|Tells whether the container is running as root group.|
|run_as_root_user|Boolean|Tells whether the container is running as root user.|
|running_status|Boolean|Tells whether the container is running. Ex: running_status:true|

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
