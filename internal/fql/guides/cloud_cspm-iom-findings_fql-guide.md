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
=== falcon_search_iom_findings FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|account_id|String|The cloud provider account ID. Ex: account_id:'123456789012'|
|account_name|String|The cloud provider account name. Ex: account_name:'production-account'|
|cloud_provider|String|The cloud provider. Values: aws, azure, gcp. Ex: cloud_provider:'aws' Ex: cloud_provider:['aws', 'azure']|
|severity|String|The severity of the misconfiguration finding. Values: critical, high, medium, low, informational. Ex: severity:'critical' Ex: severity:['critical', 'high']|
|status|String|The status of the finding. Values: open, suppressed, pass. Ex: status:'open'|
|service|String|The cloud service (e.g., EC2, S3, IAM, KeyVault, Compute Engine). Ex: service:'S3' Ex: service:'IAM'|
|service_category|String|Broader service category. Examples: Compute, Storage, Networking, Identity. Ex: service_category:'Identity'|
|region|String|The cloud region where the finding was detected. Ex: region:'us-east-1' Ex: region:['us-east-1', 'eu-west-1']|
|resource_id|String|The unique identifier of the affected resource. Ex: resource_id:'arn:aws:s3:::my-bucket'|
|resource_type|String|The type of cloud resource affected. Ex: resource_type:'AWS::S3::Bucket' Ex: resource_type:*'*EC2*'|
|resource_type_name|String|Human-readable resource type name. Ex: resource_type_name:'S3 Bucket'|
|rule_name|String|The name of the misconfiguration rule that triggered the finding. Ex: rule_name:*'*encryption*' Ex: rule_name:*'*public*'|
|rule_id|String|The unique rule identifier. Ex: rule_id:'CS-001'|
|policy_name|String|The policy name containing the rule. Ex: policy_name:*'*CIS*'|
|policy_id|String|The policy identifier. Ex: policy_id:'123'|
|benchmark_name|String|Compliance benchmark name (e.g., CIS, NIST, SOC2). Ex: benchmark_name:*'*CIS*'|
|framework|String|Compliance framework the finding maps to. Ex: framework:'CIS'|
|attack_type|String|MITRE ATT&CK attack type classification. Ex: attack_type:*'*credential*'|
|tactic_name|String|MITRE ATT&CK tactic name. Ex: tactic_name:'Credential Access'|
|technique_name|String|MITRE ATT&CK technique name. Ex: technique_name:*'*Brute Force*'|
|first_detected|Timestamp|When the finding was first detected in UTC format. Ex: first_detected:>'2025-01-01T00:00:00Z'|
|last_detected|Timestamp|When the finding was last detected in UTC format. Ex: last_detected:>'2025-04-01T00:00:00Z'|
|suppressed_by|String|The user or rule that suppressed this finding. Ex: suppressed_by:*'*admin*'|
|suppression_reason|String|The reason the finding was suppressed. Values: accept-risk, compensating-control, false-positive. Ex: suppression_reason:'accept-risk'|
|tag_key|String|Cloud resource tag key. Ex: tag_key:'Environment'|
|tag_value|String|Cloud resource tag value. Ex: tag_value:'Production'|
|cloud_group|String|Cloud group identifier for organizational grouping. Ex: cloud_group:'prod-group'|

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
