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
=== falcon_search_images_vulnerabilities FQL filter options ===

|Name|Type|Description|
|-|-|-|
|ai_related|Boolean|Tells whether the image has AI related packages. Ex: ai_related:true|
|base_os|String|The base operating system of the image. Ex: base_os:'ubuntu'|
|container_id|String|The kubernetes container id in which the image vulnerability was detected. Ex: container_id:'515f976c43eaa3edf51590e7217ac8191a7e50c59'|
|container_running_status|Boolean|The running status of the kubernetes container in which the image vulnerability was detected. Ex: container_running_status:true|
|cps_rating|String|The CSP rating of the image vulnerability. Possible values: Low, Medium, High, Critical Ex: cps_rating:'Critical'|
|cve_id|String|The CVE ID of the image vulnerability. Ex: cve_id:'CVE-2025-1234'|
|cvss_score|Number|The CVSS Score of the image vulnerability. The value must be between 0 and 10. Ex: cvss_score:8|
|image_digest|String|The digest of the image. Ex: image_digest:'sha256:a08d3ee8ee68ebd8a78525a710c6479270692259e'|
|image_id|String|The ID of the image. Ex: image_id:'a90f484d134848af858cd409801e213e'|
|registry|String|The image registry of the image in which the vulnerability was detected. Ex: registry:'docker.io'|
|repository|String|The image repository of the image in which the vulnerability was detected. Ex: repository:'my-app'|
|severity|String|The severity of the vulnerability. Available values: Low, Medium, High, Critical. Ex: severity:'High'|
|tag|String|The image tag of the image in which the vulnerability was detected. Ex: tag:'v1.0.0'|

=== falcon_search_images_vulnerabilities FQL filter examples ===

# Find images vulnerabilities by container ID
container_id:'12341223'

# Find images vulnerabilities by a list of container IDs
container_id:['12341223', '199929292', '1000101']

# Find images vulnerabilities by CVSS score and container with running status true
cvss_score:>5+container_running_status:true

# Find images vulnerabilities by image registry using wildcard
registry:*'*docker*'
