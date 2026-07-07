Falcon Query Language (FQL) - Search RTR Audit Sessions Guide

=== PURPOSE ===
Use falcon_search_rtr_audit_sessions when you need accountability and timeline evidence:
who used RTR, when, against which host, and optionally which command activity is recorded.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: field_name:>'2025-01-01T00:00:00Z' (comparison)
• ~: field_name:~'partial' (text match, case insensitive)
• !~: field_name:!~'exclude' (not text match)
• *: field_name:'prefix*' or field_name:'*suffix*' (wildcards)

=== SORT OPTIONS ===
Available audit sort fields: created_at, updated_at, deleted_at.

The RTR audit API uses pipe-style sort examples such as:
• created_at|desc
• updated_at|asc
• deleted_at|desc

=== COMMAND INFO ===
Set with_command_info=true when the investigation needs cloud request IDs and command log fields.
Leave it false for lighter timeline searches.

=== falcon_search_rtr_audit_sessions FQL filter fields ===

|Name|Type|Description|
|-|-|-|
|created_at|Timestamp|When the audited RTR session was created. Use this to keep audit searches bounded. Ex: 2025-03-15T10:30:00Z|
|updated_at|Timestamp|When the audited RTR session was last updated. Ex: 2025-03-15T11:00:00Z|
|deleted_at|Timestamp|When the audited RTR session was deleted. Ex: 2025-03-15T12:00:00Z|
|aid|String|Host agent ID associated with the audited RTR activity. Ex: 2c5c4e7738004deaa9dfcdb86f633f3e|
|hostname|String|Hostname associated with the audited RTR activity. Ex: BRR-WB-LIB-22|
|user_id|String|Falcon user or API client associated with the RTR session. Some Falcon environments support '@me' for the current user. Ex: user@example.com|
|origin|String|Origin label for the RTR session. Ex: falcon-mcp|
|cloud_request_id|String|Cloud request ID associated with command execution. This is most useful when with_command_info=true is enabled. Ex: a1b2c3d4-5678-90ab-cdef-1234567890ab|
|base_command|String|RTR base command name. This is most useful when with_command_info=true is enabled. Ex: ps|
|command_string|String|Full RTR command line string. This is most useful when with_command_info=true is enabled. Ex: cat C:\Windows\win.ini|

=== EXAMPLES ===

# Recent RTR audit sessions
created_at:>'now-7d'

# RTR audit sessions for a host pattern
hostname:'DC*'+created_at:>'now-7d'

# Current user's RTR audit sessions
user_id:'@me'+created_at:>'now-7d'

# Command-focused audit search
base_command:'ps'+created_at:>'now-7d'

# Audit search for a command request
cloud_request_id:'a1b2c3d4-5678-90ab-cdef-1234567890ab'
