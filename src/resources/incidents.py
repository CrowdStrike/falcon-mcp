"""
Contains Incidents resources.
"""

# TODO: verify filter
CROWD_SCORE_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - CrowdScore Guide

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
• !~ = does not text match
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_show_crowd_score FQL filter options ===
• id
• cid
• timestamp
• score
• adjusted_score
• modified_timestamp

=== EXAMPLE USAGE ===

• score:>50
• timestamp:>'2023-01-01T00:00:00Z'
• modified_timestamp:>'2023-01-01T00:00:00Z'+score:>70

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""

# TODO: verify filter and provide valid examples
SEARCH_INCIDENTS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Incidents Guide

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
• !~ = does not text match
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_incidents FQL filter options ===

+----------------------+---------------------------+----------+------------------------------------------------------------------+
| Name                 | Type                      | Operators| Description                                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| host_ids             | String                    | No       | The device IDs of all the hosts on which the incident occurred.  |
|                      |                           |          | Ex: 9a07d39f8c9f430eb3e474d1a0c16ce9                             |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| lm_host_ids          | String                    | No       | If lateral movement has occurred, this field shows the remote    |
|                      |                           |          | device IDs of the hosts on which the lateral movement occurred.  |
|                      |                           |          | Ex: c4e9e4643999495da6958ea9f21ee597                             |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| lm_hosts_capped      | Boolean                   | No       | Indicates that the list of lateral movement hosts has been       |
|                      |                           |          | truncated. The limit is 15 hosts.                                |
|                      |                           |          | Ex: True                                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| name                 | String                    | Yes      | The name of the incident. Initially the name is assigned by      |
|                      |                           |          | CrowdScore, but it can be updated through the API.               |
|                      |                           |          | Ex: Incident on DESKTOP-27LTE3R at 2019-12-20T19:56:16Z          |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| description          | String                    | Yes      | The description of the incident. Initially the description is    |
|                      |                           |          | assigned by CrowdScore, but it can be updated through the API.   |
|                      |                           |          | Ex: Objectives in this incident: Keep Access.                    |
|                      |                           |          |     Techniques: Masquerading.                                    |
|                      |                           |          |     Involved hosts and end users: DESKTOP-27LTE3R.               |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| users                | String                    | Yes      | The usernames of the accounts associated with the incident.      |
|                      |                           |          | Ex: someuser                                                     |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| tags                 | String                    | Yes      | Tags associated with the incident. CrowdScore will assign an     |
|                      |                           |          | initial set of tags, but tags can be added or removed through    |
|                      |                           |          | the API.                                                         |
|                      |                           |          | Ex: Objective/Keep Access                                        |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| final_score          | Number                    | Yes      | The incident score. Divide the integer by 10 to match the        |
|                      |                           |          | displayed score for the incident.                                |
|                      |                           |          | Ex: 56                                                           |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| start                | Timestamp                 | Yes      | The recorded time of the earliest behavior.                      |
|                      |                           |          | Ex: 2017-01-31T22:36:11Z                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| end                  | Timestamp                 | Yes      | The recorded time of the latest behavior.                        |
|                      |                           |          | Ex: 2017-01-31T22:36:11Z                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| assigned_to_name     | String                    | Yes      | The name of the user the incident is assigned to.                |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| state                | String                    | No       | The incident state: "open" or "closed"                           |
|                      |                           |          | Ex: open                                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| status               | Number                    | No       | The incident status as a number:                                 |
|                      |                           |          | - 20: New                                                        |
|                      |                           |          | - 25: Reopened                                                   |
|                      |                           |          | - 30: In Progress                                                |
|                      |                           |          | - 40: Closed                                                     |
|                      |                           |          | Ex: 20                                                           |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| modified_timestamp   | Timestamp                 | Yes      | The most recent time a user has updated the incident.            |
|                      |                           |          | Ex: 2021-02-04T05:57:04Z                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+

=== EXAMPLE USAGE ===

• state:'open'
• status:'20'
• final_score:>50
• tags:'Objective/Keep Access'
• modified_timestamp:>'2023-01-01T00:00:00Z'
• state:'open'+final_score:>50

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Status values: 20: New, 25: Reopened, 30: In Progress, 40: Closed
"""

# TODO: verify filter and provide valid examples
SEARCH_BEHAVIORS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Behaviors Guide

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
• !~ = does not text match
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_behaviors FQL filter options ===
• aid: Agent ID
• behavior_id: Behavior ID
• incident_id: Incident ID
• tactic: MITRE ATT&CK tactic
• technique: MITRE ATT&CK technique
• objective: Attack objective
• timestamp: When the behavior occurred

=== EXAMPLE USAGE ===

• tactic:'Defense Evasion'
• technique:'Masquerading'
• timestamp:>'2023-01-01T00:00:00Z'
• tactic:'Persistence'+confidence:>80
• objective:'Keep Access'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""
