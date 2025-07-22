"""
Contains Detections resources.
"""

SEARCH_DETECTIONS_FQL_DOCUMENTATION = r"""Falcon Query Language (FQL) - Search Detections/Alerts Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: field_name:>50 (comparison)
• ~: field_name:~'partial' (text match, case insensitive)
• !~: field_name:!~'exclude' (not text match)
• *: field_name:'prefix*' or field_name:'*suffix*' (wildcards)

=== DATA TYPES ===
• String: 'value'
• Number: 123 (no quotes)
• Boolean: true/false (no quotes)
• Timestamp: 'YYYY-MM-DDTHH:MM:SSZ'
• Array: ['value1', 'value2']

=== WILDCARDS ===
✅ **String & Number fields**: field_name:'pattern*' (prefix), field_name:'*pattern' (suffix), field_name:'*pattern*' (contains)
❌ **Timestamp fields**: Not supported (causes errors)
⚠️ **Number wildcards**: Require quotes: pattern_id:'123*'

=== COMBINING ===
• + = AND: status:'new'+severity:>=70
• , = OR: product:'epp',product:'xdr'

=== COMMON PATTERNS ===

🔍 ESSENTIAL FILTERS:
• Status: status:'new' | status:'in_progress' | status:'closed' | status:'reopened'
• Severity: severity:>=90 (critical) | severity:>=70 (high+) | severity:>=50 (medium+) | severity:>=20 (low+)
• Product: product:'epp' | product:'idp' | product:'xdr' | product:'overwatch' (see field table for all)
• Assignment: assigned_to_name:!* (unassigned) | assigned_to_name:* (assigned) | assigned_to_name:'user.name'
• Timestamps: created_timestamp:>'2025-01-01T00:00:00Z' | created_timestamp:>='date1'+created_timestamp:<='date2'
• Wildcards: name:'EICAR*' | description:'*credential*' | agent_id:'77d11725*' | pattern_id:'301*'
• Combinations: status:'new'+severity:>=70+product:'epp' | product:'epp',product:'xdr' | status:'new',status:'reopened'

🔍 EPP-SPECIFIC PATTERNS:
• Device targeting: product:'epp'+device.hostname:'DC*' | product:'epp'+device.external_ip:'192.168.*'
• Process analysis: product:'epp'+filename:'*cmd*'+cmdline:'*password*' | product:'epp'+filepath:'*system32*'
• Hash investigation: product:'epp'+sha256:'abc123...' | product:'epp'+md5:'def456...'
• Incident correlation: product:'epp'+incident.id:'inc_12345' | product:'epp'+incident.score:>=80
• User activity: product:'epp'+user_name:'admin*' | product:'epp'+logon_domain:'CORP'
• Nested queries: product:'epp'+device.agent_version:'7.*' | product:'epp'+parent_details.filename:'*explorer*'

=== falcon_search_detections FQL filter available fields ===

+----------------------------+---------------------------+--------------------------------------------------------+
| Name                       | Type                      | Description                                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| **CORE IDENTIFICATION**                                                                                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| agent_id                   | String                    | Agent ID associated with the alert.                   |
|                            |                           | Ex: 77d11725xxxxxxxxxxxxxxxxxxxxc48ca19               |
+----------------------------+---------------------------+--------------------------------------------------------+
| aggregate_id               | String                    | Unique identifier linking multiple related alerts      |
|                            |                           | that represent a logical grouping (like legacy        |
|                            |                           | detection_id). Use this to correlate related alerts.  |
|                            |                           | Ex: aggind:77d1172532c8xxxxxxxxxxxxxxxxxxxx49030016385|
+----------------------------+---------------------------+--------------------------------------------------------+
| composite_id               | String                    | Global unique identifier for the individual alert.     |
|                            |                           | This replaces the legacy detection_id for individual  |
|                            |                           | alerts in the new Alerts API.                         |
|                            |                           | Ex: d615:ind:77d1172xxxxxxxxxxxxxxxxx6c48ca19         |
+----------------------------+---------------------------+--------------------------------------------------------+
| cid                        | String                    | Customer ID.                                           |
|                            |                           | Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158                |
+----------------------------+---------------------------+--------------------------------------------------------+
| pattern_id                 | Number                    | Detection pattern identifier.                          |
|                            |                           | Ex: 67                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| **ASSIGNMENT & WORKFLOW**                                                                                       |
+----------------------------+---------------------------+--------------------------------------------------------+
| assigned_to_name           | String                    | Name of assigned Falcon user.                         |
|                            |                           | Ex: Alice Anderson                                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| assigned_to_uid            | String                    | User ID of assigned Falcon user.                      |
|                            |                           | Ex: alice.anderson@example.com                        |
+----------------------------+---------------------------+--------------------------------------------------------+
| assigned_to_uuid           | String                    | UUID of assigned Falcon user.                         |
|                            |                           | Ex: dc54xxxxxxxxxxxxxxxx1658                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| status                     | String                    | Alert status. Possible values:                         |
|                            |                           | - new: Newly detected, needs triage                   |
|                            |                           | - in_progress: Being investigated                      |
|                            |                           | - closed: Investigation completed                      |
|                            |                           | - reopened: Previously closed, now active again       |
|                            |                           | Ex: new                                                |
+----------------------------+---------------------------+--------------------------------------------------------+
| **TIMESTAMPS**                                                                                                   |
+----------------------------+---------------------------+--------------------------------------------------------+
| created_timestamp          | Timestamp                 | When alert was created in UTC format.                 |
|                            |                           | Ex: 2024-02-22T14:16:04.973070837Z                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| updated_timestamp          | Timestamp                 | Last modification time in UTC format.                  |
|                            |                           | Ex: 2024-02-22T15:15:05.637481021Z                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| timestamp                  | Timestamp                 | Alert occurrence timestamp in UTC format.             |
|                            |                           | Ex: 2024-02-22T14:15:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| crawled_timestamp          | Timestamp                 | Internal timestamp for processing in UTC format.      |
|                            |                           | Ex: 2024-02-22T15:15:05.637684718Z                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| **THREAT ASSESSMENT**                                                                                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| confidence                 | Number                    | Confidence level (1-100). Higher values indicate      |
|                            |                           | greater confidence in the detection.                   |
|                            |                           | Ex: 80                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| severity                   | Number                    | Security risk level (1-100). Use numeric values:      |
|                            |                           | - Critical: severity:>=90                              |
|                            |                           | - High: severity:>=70                                 |
|                            |                           | - Medium: severity:>=50                               |
|                            |                           | - Low: severity:>=20                                  |
|                            |                           | Ex: 90                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| tactic                     | String                    | MITRE ATT&CK tactic name.                              |
|                            |                           | Ex: Credential Access                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| tactic_id                  | String                    | MITRE ATT&CK tactic identifier.                        |
|                            |                           | Ex: TA0006                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| technique                  | String                    | MITRE ATT&CK technique name.                           |
|                            |                           | Ex: OS Credential Dumping                              |
+----------------------------+---------------------------+--------------------------------------------------------+
| technique_id               | String                    | MITRE ATT&CK technique identifier.                     |
|                            |                           | Ex: T1003                                              |
+----------------------------+---------------------------+--------------------------------------------------------+
| objective                  | String                    | Attack objective description.                          |
|                            |                           | Ex: Gain Access                                        |
+----------------------------+---------------------------+--------------------------------------------------------+
| scenario                   | String                    | Detection scenario classification.                     |
|                            |                           | Ex: credential_theft                                   |
+----------------------------+---------------------------+--------------------------------------------------------+
| **PRODUCT & PLATFORM**                                                                                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| product                    | String                    | Source Falcon product. Possible values:               |
|                            |                           | - epp: Endpoint Protection Platform                    |
|                            |                           | - idp: Identity Protection                             |
|                            |                           | - mobile: Mobile Device Protection                     |
|                            |                           | - xdr: Extended Detection and Response                 |
|                            |                           | - overwatch: Managed Threat Hunting                   |
|                            |                           | - cwpp: Cloud Workload Protection                     |
|                            |                           | - ngsiem: Next-Gen SIEM                               |
|                            |                           | - thirdparty: Third-party integrations                |
|                            |                           | - data-protection: Data Loss Prevention               |
|                            |                           | Ex: epp                                                |
+----------------------------+---------------------------+--------------------------------------------------------+
| platform                   | String                    | Operating system platform.                            |
|                            |                           | Ex: Windows, Linux, Mac                                |
+----------------------------+---------------------------+--------------------------------------------------------+
| data_domains               | Array                     | Domain to which this alert belongs to. Possible       |
|                            |                           | values: Endpoint, Identity, Cloud, Email, Web,        |
|                            |                           | Network (array field).                                |
|                            |                           | Ex: ["Endpoint"]                                      |
+----------------------------+---------------------------+--------------------------------------------------------+
| source_products            | Array                     | Products associated with the source of this alert     |
|                            |                           | (array field).                                        |
|                            |                           | Ex: ["Falcon Insight"]                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| source_vendors             | Array                     | Vendors associated with the source of this alert      |
|                            |                           | (array field).                                        |
|                            |                           | Ex: ["CrowdStrike"]                                   |
+----------------------------+---------------------------+--------------------------------------------------------+
| **DETECTION METADATA**                                                                                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| name                       | String                    | Detection pattern name.                                |
|                            |                           | Ex: NtdsFileAccessedViaVss                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| display_name               | String                    | Human-readable detection name.                         |
|                            |                           | Ex: NtdsFileAccessedViaVss                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| description                | String                    | Detection description.                                 |
|                            |                           | Ex: Process accessed credential-containing NTDS.dit   |
|                            |                           | in a Volume Shadow Snapshot                           |
+----------------------------+---------------------------+--------------------------------------------------------+
| type                       | String                    | Detection type classification. Possible values:       |
|                            |                           | - ldt: Legacy Detection Technology                     |
|                            |                           | - ods: On-sensor Detection System                     |
|                            |                           | - xdr: Extended Detection and Response                |
|                            |                           | - ofp: Offline Protection                             |
|                            |                           | - ssd: Suspicious Script Detection                    |
|                            |                           | - windows_legacy: Windows Legacy Detection            |
|                            |                           | Ex: ldt                                                |
+----------------------------+---------------------------+--------------------------------------------------------+
| **UI & WORKFLOW**                                                                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| show_in_ui                 | Boolean                   | Whether detection appears in UI.                      |
|                            |                           | Ex: true                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| email_sent                 | Boolean                   | Whether email was sent for this detection.            |
|                            |                           | Ex: true                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| seconds_to_resolved        | Number                    | Time in seconds to move from new to closed status.    |
|                            |                           | Ex: 3600                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| seconds_to_triaged         | Number                    | Time in seconds to move from new to in_progress.      |
|                            |                           | Ex: 1800                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| **COMMENTS & TAGS**                                                                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| comments.value             | String                    | A single term in an alert comment. Matching is        |
|                            |                           | case sensitive. Partial match and wildcard search     |
|                            |                           | are not supported.                                     |
|                            |                           | Ex: suspicious                                         |
+----------------------------+---------------------------+--------------------------------------------------------+
| tags                       | Array                     | Contains a separated list of FalconGroupingTags       |
|                            |                           | and SensorGroupingTags (array field).                 |
|                            |                           | Ex: ["fc/offering/falcon_complete",                   |
|                            |                           | "fc/exclusion/pre-epp-migration", "fc/exclusion/nonlive"]|
+----------------------------+---------------------------+--------------------------------------------------------+
| **PROCESS & EXECUTION** (EPP-specific fields)                                                                   |
+----------------------------+---------------------------+--------------------------------------------------------+
| alleged_filetype           | String                    | The alleged file type of the executable.              |
|                            |                           | Ex: exe                                                |
+----------------------------+---------------------------+--------------------------------------------------------+
| cmdline                    | String                    | Command line arguments used to start the process.     |
|                            |                           | Ex: powershell.exe -ExecutionPolicy Bypass           |
+----------------------------+---------------------------+--------------------------------------------------------+
| filename                   | String                    | Process filename without path.                        |
|                            |                           | Ex: powershell.exe                                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| filepath                   | String                    | Full file path of the executable.                     |
|                            |                           | Ex: C:\Windows\System32\WindowsPowerShell\v1.0\      |
|                            |                           | powershell.exe                                        |
+----------------------------+---------------------------+--------------------------------------------------------+
| process_id                 | String                    | Process identifier.                                    |
|                            |                           | Ex: pid:12345:abcdef                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| parent_process_id          | String                    | Parent process identifier.                             |
|                            |                           | Ex: pid:12344:ghijkl                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| local_process_id           | Number                    | Local process ID number.                               |
|                            |                           | Ex: 12345                                              |
+----------------------------+---------------------------+--------------------------------------------------------+
| process_start_time         | Number                    | Process start timestamp (epoch).                      |
|                            |                           | Ex: 1724347200                                         |
+----------------------------+---------------------------+--------------------------------------------------------+
| process_end_time           | Number                    | Process end timestamp (epoch).                        |
|                            |                           | Ex: 1724347800                                         |
+----------------------------+---------------------------+--------------------------------------------------------+
| tree_id                    | String                    | Process tree identifier.                               |
|                            |                           | Ex: tree:77d11725:abcd1234                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| tree_root                  | String                    | Process tree root identifier.                          |
|                            |                           | Ex: root:77d11725:efgh5678                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| **DEVICE INFORMATION** (EPP-specific nested fields)                                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.agent_load_flags    | String                    | Agent load flags configuration.                        |
|                            |                           | Ex: 0x00000001                                        |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.agent_local_time    | Timestamp                 | Agent local timestamp in UTC format.                  |
|                            |                           | Ex: 2024-02-22T14:15:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.agent_version       | String                    | CrowdStrike Falcon agent version.                     |
|                            |                           | Ex: 7.10.19103.0                                      |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.bios_manufacturer   | String                    | System BIOS manufacturer name.                         |
|                            |                           | Ex: Dell Inc.                                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.bios_version        | String                    | System BIOS version information.                       |
|                            |                           | Ex: 2.18.0                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.config_id_base      | String                    | Base configuration identifier.                         |
|                            |                           | Ex: 65994753                                           |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.config_id_build     | String                    | Build configuration identifier.                        |
|                            |                           | Ex: 19103                                              |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.config_id_platform  | String                    | Platform configuration identifier.                     |
|                            |                           | Ex: 3                                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.device_id           | String                    | Unique device identifier.                              |
|                            |                           | Ex: 77d11725xxxxxxxxxxxxxxxxxxxxc48ca19               |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.external_ip         | String                    | Device external/public IP address.                     |
|                            |                           | Ex: 203.0.113.5                                       |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.first_seen          | Timestamp                 | First time device was seen in UTC format.             |
|                            |                           | Ex: 2024-01-15T10:30:00.000Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.hostname            | String                    | Device hostname or computer name.                      |
|                            |                           | Ex: DESKTOP-ABC123                                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.last_seen           | Timestamp                 | Last time device was seen in UTC format.              |
|                            |                           | Ex: 2024-02-22T14:15:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.local_ip            | String                    | Device local/private IP address.                       |
|                            |                           | Ex: 192.168.1.100                                     |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.major_version       | String                    | Operating system major version.                        |
|                            |                           | Ex: 10                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.minor_version       | String                    | Operating system minor version.                        |
|                            |                           | Ex: 0                                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.modified_timestamp  | Timestamp                 | Device record last modified timestamp in UTC format.   |
|                            |                           | Ex: 2024-02-22T15:15:05.637Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.os_version          | String                    | Complete operating system version string.             |
|                            |                           | Ex: Windows 10                                         |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.ou                  | String                    | Organizational unit or domain path.                    |
|                            |                           | Ex: OU=Computers,DC=example,DC=com                    |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.platform_id         | String                    | Platform identifier code.                              |
|                            |                           | Ex: 0                                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.platform_name       | String                    | Operating system platform name.                       |
|                            |                           | Ex: Windows                                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.product_type        | String                    | Product type identifier.                               |
|                            |                           | Ex: 1                                                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.product_type_desc   | String                    | Product type description.                              |
|                            |                           | Ex: Workstation                                       |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.status              | String                    | Device connection status.                              |
|                            |                           | Ex: normal                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.system_manufacturer | String                    | System hardware manufacturer.                          |
|                            |                           | Ex: Dell Inc.                                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| device.system_product_name | String                    | System product model name.                             |
|                            |                           | Ex: OptiPlex 7090                                     |
+----------------------------+---------------------------+--------------------------------------------------------+
| **HASH & PREVALENCE** (EPP-specific fields)                                                                     |
+----------------------------+---------------------------+--------------------------------------------------------+
| md5                        | String                    | MD5 hash of the file.                                 |
|                            |                           | Ex: 5d41402abc4b2a76b9719d911017c592                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| sha1                       | String                    | SHA1 hash of the file.                                |
|                            |                           | Ex: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d          |
+----------------------------+---------------------------+--------------------------------------------------------+
| sha256                     | String                    | SHA256 hash of the file.                              |
|                            |                           | Ex: 2cf24dba4f21d4288094c19329d73459e4449065644a8   |
|                            |                           | 9ed6534746b7d2cbe0e9a4c8e8e8bf7                      |
+----------------------------+---------------------------+--------------------------------------------------------+
| global_prevalence          | String                    | Global prevalence rating of the file.                 |
|                            |                           | Ex: rare                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| local_prevalence           | String                    | Local prevalence rating within the organization.       |
|                            |                           | Ex: common                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| **INCIDENT & TRIAGE** (EPP-specific nested fields)                                                              |
+----------------------------+---------------------------+--------------------------------------------------------+
| charlotte.can_triage       | Boolean                   | Whether alert can be triaged automatically.           |
|                            |                           | Ex: true                                               |
+----------------------------+---------------------------+--------------------------------------------------------+
| charlotte.triage_status    | String                    | Automated triage status.                              |
|                            |                           | Ex: triaged                                            |
+----------------------------+---------------------------+--------------------------------------------------------+
| incident.created           | Timestamp                 | Incident creation timestamp in UTC format.            |
|                            |                           | Ex: 2024-02-22T14:15:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| incident.end               | Timestamp                 | Incident end timestamp in UTC format.                 |
|                            |                           | Ex: 2024-02-22T14:45:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| incident.id                | String                    | Unique incident identifier.                            |
|                            |                           | Ex: inc_12345abcdef                                   |
+----------------------------+---------------------------+--------------------------------------------------------+
| incident.score             | Number                    | Incident severity score (1-100).                      |
|                            |                           | Ex: 85                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| incident.start             | Timestamp                 | Incident start timestamp in UTC format.               |
|                            |                           | Ex: 2024-02-22T14:15:03.112Z                          |
+----------------------------+---------------------------+--------------------------------------------------------+
| indicator_id               | String                    | Threat indicator identifier.                           |
|                            |                           | Ex: ind_67890wxyz                                     |
+----------------------------+---------------------------+--------------------------------------------------------+
| **PROCESS LINEAGE** (EPP-specific nested object fields)                                                         |
+----------------------------+---------------------------+--------------------------------------------------------+
| parent_details.*           | Object                    | Parent process information object. Use dot notation    |
|                            |                           | for specific fields like parent_details.cmdline,      |
|                            |                           | parent_details.filename, parent_details.filepath,     |
|                            |                           | parent_details.process_id, etc.                       |
|                            |                           | Ex: parent_details.filename:'explorer.exe'            |
+----------------------------+---------------------------+--------------------------------------------------------+
| grandparent_details.*      | Object                    | Grandparent process information object. Use dot       |
|                            |                           | notation for specific fields like                     |
|                            |                           | grandparent_details.cmdline,                          |
|                            |                           | grandparent_details.filename, etc.                    |
|                            |                           | Ex: grandparent_details.filepath:'*winlogon*'         |
+----------------------------+---------------------------+--------------------------------------------------------+
| child_process_ids          | Array                     | List of child process identifiers spawned by this     |
|                            |                           | process (array field).                                |
|                            |                           | Ex: ["pid:12346:abcdef", "pid:12347:ghijkl"]         |
+----------------------------+---------------------------+--------------------------------------------------------+
| triggering_process_graph_id| String                    | Process graph identifier for the triggering process   |
|                            |                           | in the attack chain.                                   |
|                            |                           | Ex: graph:77d11725:trigger123                        |
+----------------------------+---------------------------+--------------------------------------------------------+
| **IOC & INDICATORS** (EPP-specific fields)                                                                      |
+----------------------------+---------------------------+--------------------------------------------------------+
| ioc_context                | Array                     | IOC context information and metadata (array field).   |
|                            |                           | Ex: ["malware_family", "apt_group"]                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| ioc_values                 | Array                     | IOC values associated with the alert (array field).   |
|                            |                           | Ex: ["192.168.1.100", "malicious.exe"]               |
+----------------------------+---------------------------+--------------------------------------------------------+
| falcon_host_link           | String                    | Direct link to Falcon console for this host.         |
|                            |                           | Ex: https://falcon.crowdstrike.com/hosts/detail/     |
|                            |                           | 77d11725xxxxxxxxxxxxxxxxxxxxc48ca19                  |
+----------------------------+---------------------------+--------------------------------------------------------+
| **USER & AUTHENTICATION** (EPP-specific fields)                                                                 |
+----------------------------+---------------------------+--------------------------------------------------------+
| user_id                    | String                    | User identifier associated with the process.          |
|                            |                           | Ex: S-1-5-21-1234567890-987654321-1122334455-1001    |
+----------------------------+---------------------------+--------------------------------------------------------+
| user_name                  | String                    | Username associated with the process.                  |
|                            |                           | Ex: administrator                                      |
+----------------------------+---------------------------+--------------------------------------------------------+
| logon_domain               | String                    | Logon domain name for the user.                       |
|                            |                           | Ex: CORP                                               |
+----------------------------+---------------------------+--------------------------------------------------------+

=== COMPLEX FILTER EXAMPLES ===

# New high-severity endpoint alerts
status:'new'+severity:>=70+product:'epp'

# Unassigned critical alerts from last 24 hours
assigned_to_name:!*+severity:>=90+created_timestamp:>'2025-01-19T00:00:00Z'

# OverWatch alerts with credential access tactics
product:'overwatch'+tactic:'Credential Access'

# XDR alerts with high confidence from specific technique
product:'xdr'+confidence:>=80+technique_id:'T1003'

# Find alerts by aggregate_id (related alerts)
aggregate_id:'aggind:77d1172532c8xxxxxxxxxxxxxxxxxxxx49030016385'

# Find alerts from multiple products
product:['epp', 'xdr', 'overwatch']

# Recently updated alerts assigned to specific analyst
assigned_to_name:'alice.anderson'+updated_timestamp:>'2025-01-18T12:00:00Z'

# Find alerts with specific MITRE ATT&CK tactics
tactic:['Credential Access', 'Persistence', 'Privilege Escalation']

# Closed alerts resolved quickly (under 1 hour)
status:'closed'+seconds_to_resolved:<3600

# Date range with multiple products and severity
created_timestamp:>='2025-01-15T00:00:00Z'+created_timestamp:<='2025-01-20T00:00:00Z'+product:'epp',product:'xdr'+severity:>=70
"""
