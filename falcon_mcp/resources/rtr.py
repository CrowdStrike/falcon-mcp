"""
Contains RTR (Real Time Response) resources.
"""

from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, description)
SEARCH_RTR_SESSIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        """
        RTR session ID.
        Ex: 9f3c5e7a-1234-5678-abcd-ef0123456789
        """,
    ),
    (
        "created_at",
        "Timestamp",
        """
        When the RTR session was created (ISO 8601).
        Ex: 2025-03-15T10:30:00Z
        """,
    ),
    (
        "updated_at",
        "Timestamp",
        """
        When the RTR session was last updated (ISO 8601).
        Ex: 2025-03-15T11:00:00Z
        """,
    ),
    (
        "deleted_at",
        "Timestamp",
        """
        When the RTR session was deleted (ISO 8601).
        Ex: 2025-03-15T12:00:00Z
        """,
    ),
    (
        "aid",
        "String",
        """
        Host agent ID the session is connected to.
        Ex: 2c5c4e7738004deaa9dfcdb86f633f3e
        """,
    ),
    (
        "hostname",
        "String",
        """
        Hostname of the connected host.
        Ex: BRR-WB-LIB-22
        """,
    ),
    (
        "user_id",
        "String",
        """
        API user who created the session. Use '@me' to
        restrict results to the current API user.
        Ex: user@example.com
        """,
    ),
    (
        "origin",
        "String",
        """
        Origin label for the RTR session.
        Ex: falcon-mcp
        """,
    ),
    (
        "cloud_request_id",
        "String",
        """
        Cloud request ID associated with a command execution.
        Ex: a1b2c3d4-5678-90ab-cdef-1234567890ab
        """,
    ),
    (
        "command_string",
        "String",
        """
        Full command line string that was executed.
        Ex: cat C:\\Windows\\win.ini
        """,
    ),
    (
        "base_command",
        "String",
        """
        RTR base command name. Common values: ls, ps, cat,
        filehash, reg, netstat, ifconfig, mount, users.
        Ex: ps
        """,
    ),
    (
        "offline_queued",
        "Boolean",
        """
        Whether the session was queued for offline execution.
        Ex: true
        """,
    ),
    (
        "commands_queued",
        "Boolean",
        """
        Whether commands are queued in the session.
        Ex: true
        """,
    ),
]

SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION = r"""Falcon Query Language (FQL) - Search RTR Sessions Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: field_name:>'2025-01-01T00:00:00Z' (comparison)
• ~: field_name:~'partial' (text match, case insensitive)
• !~: field_name:!~'exclude' (not text match)
• *: field_name:'prefix*' or field_name:'*suffix*' (wildcards)

=== DATA TYPES ===
• String: 'value'
• Number: 123 (no quotes)
• Boolean: true/false (no quotes)
• Timestamp: 'YYYY-MM-DDTHH:MM:SSZ'

=== WILDCARDS ===
✅ **String fields**: field_name:'pattern*' (prefix), field_name:'*pattern' (suffix), field_name:'*pattern*' (contains)
❌ **Timestamp fields**: Not supported (causes errors)

=== COMBINING ===
• + = AND: hostname:'DC*'+user_id:'@me'
• , = OR: base_command:'ls',base_command:'ps'
• () = GROUPING: (base_command:'ls',base_command:'ps')+hostname:'DC*'

=== SORT OPTIONS ===
• created_at: When the session was created
• updated_at: When the session was last updated
• hostname: Hostname of the connected host

Sort either asc (ascending) or desc (descending).
Examples: 'created_at.desc', 'hostname.asc'

=== falcon_search_rtr_sessions FQL filter available fields ===

""" + generate_md_table(SEARCH_RTR_SESSIONS_FQL_FILTERS) + """

=== COMPLEX FILTER EXAMPLES ===

# Sessions for a specific host
hostname:'BRR-WB-LIB-22'

# Sessions by agent ID
aid:'2c5c4e7738004deaa9dfcdb86f633f3e'

# Current user's sessions only
user_id:'@me'

# Sessions created after a specific date
created_at:>'2025-03-01T00:00:00Z'

# Offline-queued sessions for a hostname pattern
offline_queued:true+hostname:'DC*'

# Sessions that ran specific commands
base_command:'ps'+hostname:'PROD*'

# Sessions with a specific origin label
origin:'falcon-mcp'+user_id:'@me'

# Sessions matching multiple commands
(base_command:'ls',base_command:'cat',base_command:'filehash')+hostname:'WEB*'

# Recent sessions for a host with queued commands
commands_queued:true+created_at:>'2025-03-10T00:00:00Z'

# Exclude deleted sessions for an agent
deleted_at:!'*'+aid:'2c5c4e7738004deaa9dfcdb86f633f3e'
"""
