"""
Contains Cloud resources.
"""

FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Hosts Guide

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

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['value1', 'value2'] for multiple distinct values
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format). Also referred as Timestamps
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for multiple string values: ['value 1', 'value 2']
• Use wildcard operator to determine if a property contains or not a substring: property:*'*sub*', property:!*'*sub*'
• Date and timestamp format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""

SEARCH_KUBERNETES_CONTAINERS_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_kubernetes_containers FQL filter options ===

+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| Name                       | Type                      | Supported Operators   | Description                                            |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| agent_id                   | String                    | equal                 | The sensor agent ID running in the container.          |
|                            |                           | not equal             | Ex: 3c1ca4a114504ca89af51fd126991efd                   |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| agent_type                 | String                    | equal                 | The sensor agent type running in the container.        |
|                            |                           | not equal             | Ex: Falcon sensor for linux.                           |
|                            |                           | wildcard              |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cloud_account_id           | String                    | equal                 | The cloud provider account ID.                         |
|                            |                           | not equal             | Ex: 171998889118                                       |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cloud_name                 | String                    | equal                 | The cloud provider name.                               |
|                            |                           | not equal             | Ex: AWS                                                |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cloud_region               | String                    | equal                 | The cloud region.                                      |
|                            |                           | not equal             | Ex: us-1                                               |
|                            |                           | wildcard              |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cluster_name               | String                    | equal                 | The kubernetes cluster that manages the container.     |
|                            |                           | not equal             | Ex: prod-cluster                                       |
|                            |                           | wildcard              |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| container_name             | String                    | equal                 | The kubernetes container name.                         |
|                            |                           | not equal             | Ex: prod-cluster                                       |
|                            |                           | wildcard              |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cve_id                     | String                    | equal                 | The CVE ID found in the container image.               |
|                            |                           | not equal             | Ex: CVE-2025-1234                                      |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| first_seen                 | Timestamp                 | less than             | Timestamp when the kubernetes container was first seen |
|                            |                           | less than or equal    | in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").           |
|                            |                           | greater than          | Ex: 2025-01-19T11:14:15Z                               |
|                            |                           | greater than or equal |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| last_seen                  | Timestamp                 | less than             | Timestamp when the kubernetes container was last seen  |
|                            |                           | less than or equal    | in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").           |
|                            |                           | greater than          | Ex: 2025-01-19T11:14:15Z                               |
|                            |                           | greater than or equal |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| image_vulnerability_count  | Number                    | less than             | Number of image vulnerabilities found                  |
|                            |                           | less than or equal    | in the container image.                                |
|                            |                           | greater than          | Ex: 1                                                  |
|                            |                           | greater than or equal |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| namespace                  | String                    | equal                 | The kubernetes namespace name.                         |
|                            |                           | not equal             | Ex: default                                            |
|                            |                           | wildcard              |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| privileged                 | Boolean                   | equal                 | Tells whether the container is running with elevated   |
|                            |                           | not equal             | privileges.                                            |
|                            |                           |                       | Ex: false                                              |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| running_status             | Boolean                   | equal                 | Tells whether the container is running.                |
|                            |                           | not equal             |                                                        |
|                            |                           |                       | Ex: true                                               |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+

=== falcon_search_kubernetes_containers FQL filter examples ===

# Find kubernetes containers that are running and have 1 or more image vulnerabilities
falcon_search_kubernetes_containers(filter="image_vulnerability_count:>0+running_status:true", limit=5)

# Find kubernetes containers seen in the last 7 days and by the CVE ID found in their container images
falcon_search_kubernetes_containers(filter="cve_id:'CVE-2025-1234'+last_seen:>'2025-03-15T00:00:00Z'", limit=10)

# Find kubernetes containers whose cloud provider are AWS or Azure
falcon_search_kubernetes_containers(filter="cloud_name:['AWS', 'Azure']", limit=100)

# Find kubernetes containers whose names starts with "app-"
falcon_search_kubernetes_containers(filter="container_name:*'app-*'", limit=100)

# Find kubernetes containers whose cluster or namespace name is "prod"
falcon_search_kubernetes_containers(filter="cluster_name:'prod',namespace:'prod'", limit=10)

=== falcon_count_kubernetes_containers FQL filter examples ===

# Count kubernetes containers by cluster name
falcon_search_kubernetes_containers(filter="cluster_name:'staging'")

# Count kubernetes containers by agent type
falcon_search_kubernetes_containers(filter="agent_type:'Kubernetes'")
"""
)

SEARCH_IMAGES_VULNERABILITIES_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_kubernetes_containers FQL filter options ===

+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| Name                       | Type                      | Supported Operators   | Description                                            |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| container_id               | String                    | equal                 | The kubernetes container id in which the image         |
|                            |                           | not equal             | vulnerability was detected.                            |
|                            |                           |                       | Ex: 515f976c43eaa3edf51590e7217ac8191a7e50c59          |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| container_running_status   | Boolean                   | equal                 | The running status of the kubernetes container         |
|                            |                           | not equal             | in which the image vulnerability was detected.         |
|                            |                           |                       | Ex: true                                               |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cps_rating                 | String                    | equal                 | The CSP rating of the image vulnerability.             |
|                            |                           | not equal             | Possible values: Low, Medium, High, Critical           |
|                            |                           |                       | Ex: Critical                                           |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cve_id                     | String                    | equal                 | The CVE ID of the image vulnerability.                 |
|                            |                           | not equal             |                                                        |
|                            |                           | wildcard              | Ex: Critical                                           |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| cvss_score                 | Number                    | less than             | The CVSS Score of the image vulnerability. The value   |
|                            |                           |                       | must be between 0 and 10.                              |
|                            |                           | less than or equal    | Ex: 8                                                  |
|                            |                           | greater than          |                                                        |
|                            |                           | greater than or equal |                                                        |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| registry                   | String                    | equal                 | The image registry of the image in which the           |
|                            |                           | not equal             | vulnerability was detected.                            |
|                            |                           | wildcard              | Ex: docker.io                                          |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| repository                 | String                    | equal                 | The image repository of the image in which the         |
|                            |                           | not equal             | vulnerability was detected.                            |
|                            |                           | wildcard              | Ex: my-app                                             |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+
| tag                        | String                    | equal                 | The image tag of the image in which the                |
|                            |                           | not equal             | vulnerability was detected.                            |
|                            |                           | wildcard              | Ex: v1.0.0                                             |
+----------------------------+---------------------------+-----------------------+--------------------------------------------------------+

=== falcon_search_vulnerabilities FQL filter examples ===

# Find images vulnerabilities by container ID
falcon_search_images_vulnerabilities(filter="container_id:'12341223', limit=1)

# Find images vulnerabilities by a list of container IDs
falcon_search_images_vulnerabilities(filter="container_id:['12341223', '199929292', '1000101']", limit=100)

# Find images vulnerabilities by CVSS score and container is running
falcon_search_images_vulnerabilities(filter="cvss_score:>5+container_running_status:true", limit=100)

# Find images vulnerabilities by image registry using wildcard
falcon_search_images_vulnerabilities(filter="registry:*'*docker*'", limit=100)
"""
)
