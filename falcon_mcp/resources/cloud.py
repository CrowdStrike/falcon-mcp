"""
Contains Cloud resources.
"""

from falcon_mcp.common.utils import generate_md_table

FQL_DOCUMENTATION = """Falcon Query Language (FQL)

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal
• > = greater than
• >= = greater than or equal
• < = less than
• <= = less than or equal
• ~ = text match (ignores case, spaces, punctuation)
• !~ = not text match
• * = wildcard (one or more characters)
• !* = not wildcard (one or more characters)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== DATA TYPES & SUPPORTED OPERATORS ===
• String: equal, not equal, wildcard.
• Date, Timestamp: equal, not equal, less than, less than or equal, greater than, greater than or equal.
• Boolean: equal, not equal.
• Number: equal, not equal, less than, less than or equal, greater than, greater than or equal.

=== DATA TYPES & SYNTAX ===
• String: 'value' or ['value1', 'value2'] for a list of values. Wildcards: 'partial*' or '*partial' or '*partial*'.
• Date, Timestamp: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format).
• Boolean: true or false (no quotes).
• Number: 123 (no quotes).

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for list of string values: ['value 1', 'value 2']
• Use wildcard operator to determine if a property contains or not a substring. Ex: `property:*'*sub*'`, `property:!*'*sub*'`
• Dates and timestamps format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""

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
