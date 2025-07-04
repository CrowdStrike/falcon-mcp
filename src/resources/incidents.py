"""
Contains Incidents resources.
"""

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
• host_ids: The device IDs of all the hosts on which the incident occurred
• lm_host_ids: If lateral movement has occurred, this field shows the remote device IDs of the hosts on which the lateral movement occurred
• lm_hosts_capped: Indicates that the list of lateral movement hosts has been truncated
• name: The name of the incident
• description: The description of the incident
• users: The usernames of the accounts associated with the incident
• tags: Tags associated with the incident
• final_score: The incident score
• start: The recorded time of the earliest behavior
• end: The recorded time of the latest behavior
• assigned_to_name: The name of the user the incident is assigned to
• state: The incident state: "open" or "closed"
• status: The incident status as a number: 20: New, 25: Reopened, 30: In Progress, 40: Closed
• modified_timestamp: The most recent time a user has updated the incident

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

        Available filters:
            host_ids: The device IDs of all the hosts on which the incident occurred. Example: `9a07d39f8c9f430eb3e474d1a0c16ce9`
            lm_host_ids: If lateral movement has occurred, this field shows the remote device IDs of the hosts on which the lateral movement occurred. Example: `c4e9e4643999495da6958ea9f21ee597`
            lm_hosts_capped: Indicates that the list of lateral movement hosts has been truncated. The limit is 15 hosts. Example: `True`
            name: The name of the incident. Initially the name is assigned by CrowdScore, but it can be updated through the API. Example: `Incident on DESKTOP-27LTE3R at 2019-12-20T19:56:16Z`
            description: The description of the incident. Initially the description is assigned by CrowdScore, but it can be updated through the API. Example: `Objectives in this incident: Keep Access. Techniques: Masquerading. Involved hosts and end users: DESKTOP-27LTE3R, DESKTOP-27LTE3R$.`
            users: The usernames of the accounts associated with the incident. Example: `someuser`
            tags: Tags associated with the incident. CrowdScore will assign an initial set of tags, but tags can be added or removed through the API. Example: `Objective/Keep Access`
            final_score: The incident score. Divide the integer by 10 to match the displayed score for the incident. Example: `56`
            start: The recorded time of the earliest behavior. Example: 2017-01-31T22:36:11Z
            end: The recorded time of the latest behavior. Example: 2017-01-31T22:36:11Z
            assigned_to_name: The name of the user the incident is assigned to.
            state: The incident state: "open" or "closed". Example: `open`
            status: The incident status as a number: 20: New, 25: Reopened, 30: In Progress, 40: Closed. Example: `20`
            modified_timestamp: The most recent time a user has updated the incident. Example: `2021-02-04T05:57:04Z`
"""

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
• confidence: Confidence level (1-100)
• severity: Severity level
• scenario: Behavior scenario
• timestamp: When the behavior occurred
• filename: Associated filename
• filepath: Associated filepath
• cmdline: Associated command line
• username: Associated username
• hostname: Host name where behavior occurred
• ioc_type: Indicator of compromise type
• ioc_value: Indicator of compromise value
• alert_ids: Associated alert IDs

=== EXAMPLE USAGE ===

• tactic:'Persistence'
• technique:'T1055'
• confidence:>80
• severity:'high'
• timestamp:>'2023-01-01T00:00:00Z'
• tactic:'Persistence'+confidence:>80

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""
