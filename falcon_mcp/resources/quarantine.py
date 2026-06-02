"""
Contains Quarantine resources.
"""

from falcon_mcp.common.utils import generate_md_table

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
        "state",
        "String",
        "Quarantine state (response field). Also queryable as `status` in FQL. Example: state:'quarantined' or status:'released'",
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
        "hostname",
        "String",
        "Host name tied to the quarantine event (top-level field). Example: hostname:'EXAMPLE-WIN-22'",
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
`falcon_count_quarantine_actions`, `falcon_update_quarantined_files`,
or `falcon_delete_quarantined_files`.

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

=== NOTES ===

• The response entity uses `state` for the quarantine status field.
• Both `state` and `status` work as FQL filter fields.

=== EXAMPLES ===

# Quarantined files for a host
hostname:'EXAMPLE-WIN-22'

# Records updated recently
date_updated:>'2026-03-01T00:00:00Z'

# Released files for a user
status:'released'+behaviors.username:'alice'

# File hash on a specific host
sha256:'a1b2c3*'+hostname:'DC*'
"""
