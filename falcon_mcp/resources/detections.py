"""
Contains Detections resources.
"""

SEARCH_DETECTIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Detections/Alerts Guide

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
| **INTERNAL FIELDS**                                                                                             |
+----------------------------+---------------------------+--------------------------------------------------------+
| external                   | Boolean                   | A field reserved for internal use.                    |
|                            |                           | Ex: false                                              |
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
