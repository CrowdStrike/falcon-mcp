"""
Contains Quarantine resources.
"""

from falcon_mcp.common.utils import generate_md_table

EMBEDDED_FQL_SYNTAX = """FQL filter string for querying quarantined files.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (status:'released',status:'quarantined')+device.hostname:'DC*'

COMMON FIELDS:
- id: Quarantine record ID
- status: Quarantine state
- sha256: File SHA256
- date_updated: Record update timestamp
- device.hostname: Host name
- device.device_id: Host agent ID
- behaviors.username: User tied to the quarantined behavior

EXAMPLES:
- Files quarantined on a host: device.hostname:'BRR-WB-LIB-22'
- Recently updated records: date_updated:>'2026-03-01T00:00:00Z'
- Files for a user: behaviors.username:'alice'
"""

SEARCH_QUARANTINED_FILES_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        "Quarantine file record ID. Example: id:'1234567890abcdef'",
    ),
    (
        "status",
        "String",
        "Quarantine state such as quarantined or released. Example: status:'quarantined'",
    ),
    (
        "sha256",
        "String",
        "SHA256 hash of the quarantined file. Example: sha256:'a1b2c3...'",
    ),
    (
        "date_updated",
        "Timestamp",
        "Last update timestamp. Example: date_updated:>'2026-03-01T00:00:00Z'",
    ),
    (
        "device.hostname",
        "String",
        "Host name tied to the quarantine event. Example: device.hostname:'BRR-WB-LIB-22'",
    ),
    (
        "device.device_id",
        "String",
        "Falcon device ID for the affected host. Example: device.device_id:'aid-123'",
    ),
    (
        "behaviors.username",
        "String",
        "Username associated with the quarantined behavior. Example: behaviors.username:'alice'",
    ),
    (
        "behaviors.ioc_value",
        "String",
        "IOC value associated with the quarantined behavior. Example: behaviors.ioc_value:'Shift - Print_d3lsk.exe'",
    ),
]

SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION = f"""Quarantine Files FQL Filter Guide

Use this guide when building the `filter` parameter for `falcon_search_quarantined_files`,
`falcon_preview_quarantine_action_counts`, `falcon_update_quarantined_files_by_filter`,
or `falcon_delete_quarantined_files_by_filter`.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value'
• >, >=, <, <=: field_name:>'2026-03-01T00:00:00Z'
• ~: field_name:~'partial'
• !~: field_name:!~'exclude'
• *: field_name:'prefix*' or field_name:'*suffix*'

=== COMBINING ===
• + = AND
• , = OR
• () = GROUPING

=== AVAILABLE FIELDS ===

{generate_md_table(SEARCH_QUARANTINED_FILES_FQL_FILTERS)}

=== EXAMPLES ===

# Quarantined files for a host
device.hostname:'BRR-WB-LIB-22'

# Records updated recently
date_updated:>'2026-03-01T00:00:00Z'

# Released files for a user
status:'released'+behaviors.username:'alice'

# File hash on a specific host
sha256:'a1b2c3*'+device.hostname:'DC*'
"""
