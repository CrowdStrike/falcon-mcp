Falcon Query Language (FQL) - Search Cases Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
- = (default): field_name:'value'
- !: field_name:!'value' (not equal)
- >, >=, <, <=: field_name:>50 (comparison)
- *: field_name:'prefix*' (wildcard)

=== DATA TYPES ===
- String: 'value'
- Integer: 123 (no quotes)
- Timestamp: 'YYYY-MM-DDTHH:MM:SSZ'

=== COMBINING ===
- + = AND: status:'new'+severity:>50
- , = OR: status:'new',status:'in_progress'

=== SORT OPTIONS ===
Valid sort fields: id, created_timestamp, updated_timestamp, severity, status, name, reference_id

Sort formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
Examples: 'created_timestamp.desc', 'severity|desc'

=== falcon_search_cases FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|id|String|System-level case identifier (opaque base64 string).|
|reference_id|String|Human-readable case ID (e.g. ABC-1234). Case-sensitive, full match required.|
|status|String|Case status. Values: - new: Newly created case - in_progress: Under investigation - closed: Investigation completed - reopened: Previously closed, now active again Ex: new|
|severity|Integer|Numeric severity (1-100). Informational=1, Low~25, Medium~50, High~75, Critical=100. Ex: 70|
|name|String|Case name. Ex: Suspicious lateral movement|
|description|String|Case description text.|
|all_text|String|Full-text search across all searchable case fields.|
|created_timestamp|Timestamp|Case creation time in ISO 8601 UTC. Ex: 2025-01-01T00:00:00Z|
|updated_timestamp|Timestamp|Last modification time in ISO 8601 UTC. Ex: 2025-06-01T00:00:00Z|
|assigned_to_uuid|String|UUID of assigned user.|
|assigned_to_name|String|Display name of assigned user.|
|created_by|String|Creator email or API client ID.|
|modified_by|String|Last modifier email or API client ID.|
|tags|String|Tags applied to the case.|
|cid|String|Customer ID (Flight Control multi-CID scenarios).|
|alerts|String|Alert IDs attached as evidence.|
|events|String|LogScale event details in evidence.|
|data_domains|String|Data domains from evidence (e.g. Endpoint, Identity, Cloud).|
|source_vendors|String|Source vendors from evidence.|
|source_products|String|Source products from evidence.|
|tactic_ids|String|MITRE ATT&CK tactic IDs from evidence. Ex: TA0006|
|tactics|String|MITRE ATT&CK tactic names from evidence. Ex: Credential Access|
|technique_ids|String|MITRE ATT&CK technique IDs from evidence. Ex: T1003|
|techniques|String|MITRE ATT&CK technique names from evidence.|
|aids|String|Agent IDs from evidence.|
|hostnames|String|Hostnames from evidence.|
|ips|String|IP addresses from evidence.|
|email_addresses|String|Email addresses from evidence.|
|sha256s|String|SHA-256 hashes from evidence.|
|md5s|String|MD5 hashes from evidence.|
|usernames|String|Usernames from evidence.|
|command_lines|String|Command lines from evidence.|
|file_names|String|File names from evidence.|
|image_file_names|String|Image file names from evidence.|
|cloud_providers|String|Cloud provider. Values: aws, azure, gcp|
|cloud_account_ids|String|Cloud account IDs from evidence.|
|cloud_regions|String|Cloud regions from evidence. Ex: eu-west-2|
|cloud_instance_ids|String|Cloud instance IDs from evidence.|
|cloud_availability_zones|String|Cloud availability zones from evidence.|
|cloud_service_names|String|Cloud service names from evidence.|
|case_template_id|String|Template ID applied to the case.|
|case_template_name|String|Template name applied to the case.|
|sla_name|String|SLA name from the case template.|
|sla_active_timer.status|String|SLA timer status. Values: pending, in_progress, paused, achieved, missed|
|sla_active_timer_time_due|String|SLA deadline as epoch timestamp.|

=== COMPLEX FILTER EXAMPLES ===

# Open high-severity cases
status:'new'+severity:>70

# Cases in progress or reopened
status:'in_progress',status:'reopened'

# Cases created in the last week
created_timestamp:>'2025-05-10T00:00:00Z'+status:'new'

# Cases with specific MITRE tactic
tactic_ids:'TA0006'+severity:>50

# Cases assigned to a user
assigned_to_name:'Alice Anderson'+status:'in_progress'

# Cases by reference ID
reference_id:'ABC-1234'

# Unassigned high-severity cases
assigned_to_uuid:!'*'+severity:>70

# Cases with cloud evidence
cloud_providers:'aws'+status:'new'
