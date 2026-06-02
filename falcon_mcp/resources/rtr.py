"""
Contains RTR (Real Time Response) resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Concise FQL syntax for embedding in tool parameter descriptions
EMBEDDED_FQL_SYNTAX = """FQL filter string for querying RTR sessions.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (field1:'v1',field1:'v2')+field2:'v3'

COMMON FIELDS:
- aid: Host agent ID
- hostname: Host name
- user_id: API user who created the session ('@me' for current user)
- origin: Session origin label (e.g., 'falcon-mcp')
- created_at: Session creation timestamp (ISO 8601)
- updated_at: Last update timestamp (ISO 8601)
- base_command: RTR command name (e.g., 'ls', 'ps', 'cat')
- command_string: Full command line executed
- offline_queued: Whether session was queued offline (true/false)

LOOKUP NOTES:
- Direct session id and cloud_request_id filters can be environment/API-shape dependent.
- For command history, prefer aid or hostname plus a bounded created_at window and optional base_command.
- Inspect returned session command logs client-side for exact session IDs and cloud request IDs.

EXAMPLES:
- Sessions for a host: hostname:'EXAMPLE-WIN-22'
- Sessions by agent ID: aid:'2c5c4e7738004deaa9dfcdb86f633f3e'
- Current user sessions: user_id:'@me'
- Offline-queued sessions: offline_queued:true+hostname:'DC*'
"""

AUDIT_RTR_SESSIONS_EMBEDDED_FQL_SYNTAX = """FQL filter string for querying RTR audit sessions.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>'2025-01-01T00:00:00Z'
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMMON STARTING POINTS:
- Use created_at or updated_at filters to keep audit searches time-bound.
- Set with_command_info=true when you need command IDs and command log context.
- If a field is rejected by Falcon, reduce to a timestamp-bounded search and inspect returned fields.
- Direct cloud_request_id filters can be environment/API-shape dependent; if they return no rows,
  search by aid or hostname plus a bounded created_at window and inspect command logs client-side.

EXAMPLES:
- Recent RTR audit sessions: created_at:>'now-7d'
- RTR audit sessions for a host pattern: hostname:'DC*'+created_at:>'now-7d'
- RTR audit sessions for current API user: user_id:'@me'+created_at:>'now-7d'
"""

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
        RTR session ID. Live testing showed exact ID filtering can be
        API-shape dependent; if no rows return, fall back to aid/hostname plus
        bounded created_at and inspect returned session IDs client-side.
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
        Ex: EXAMPLE-WIN-22
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
        Cloud request ID associated with a command execution. Live testing
        showed exact filtering can be API-shape dependent; if no rows return,
        fall back to aid/hostname plus bounded created_at and inspect returned
        command logs client-side.
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
]

SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "created_at",
        "Timestamp",
        """
        When the audited RTR session was created. Use this to keep audit
        searches bounded.
        Ex: 2025-03-15T10:30:00Z
        """,
    ),
    (
        "updated_at",
        "Timestamp",
        """
        When the audited RTR session was last updated.
        Ex: 2025-03-15T11:00:00Z
        """,
    ),
    (
        "deleted_at",
        "Timestamp",
        """
        When the audited RTR session was deleted.
        Ex: 2025-03-15T12:00:00Z
        """,
    ),
    (
        "aid",
        "String",
        """
        Host agent ID associated with the audited RTR activity.
        Ex: 2c5c4e7738004deaa9dfcdb86f633f3e
        """,
    ),
    (
        "hostname",
        "String",
        """
        Hostname associated with the audited RTR activity.
        Ex: EXAMPLE-WIN-22
        """,
    ),
    (
        "user_id",
        "String",
        """
        Falcon user or API client associated with the RTR session.
        Some Falcon environments support '@me' for the current user.
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
        Cloud request ID associated with command execution. This is most
        useful when with_command_info=true is enabled. Live testing showed
        exact filtering can be API-shape dependent; if no rows return, fall
        back to aid/hostname plus bounded created_at and inspect returned
        command logs client-side.
        Ex: a1b2c3d4-5678-90ab-cdef-1234567890ab
        """,
    ),
    (
        "base_command",
        "String",
        """
        RTR base command name. This is most useful when with_command_info=true
        is enabled, but exact command filters can be API-shape dependent on the
        audit endpoint. If no rows return, fall back to aid/hostname plus
        bounded created_at and inspect returned command logs client-side.
        Ex: ps
        """,
    ),
    (
        "command_string",
        "String",
        """
        Full RTR command line string. This is most useful when
        with_command_info=true is enabled, but exact command filters can be
        API-shape dependent on the audit endpoint. If no rows return, fall back
        to aid/hostname plus bounded created_at and inspect returned command
        logs client-side.
        Ex: cat C:\\Windows\\win.ini
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
hostname:'EXAMPLE-WIN-22'

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

# Recent offline-queued sessions
offline_queued:true+created_at:>'2025-03-10T00:00:00Z'

# Deleted sessions after a timestamp for an agent
deleted_at:>'2025-03-10T00:00:00Z'+aid:'2c5c4e7738004deaa9dfcdb86f633f3e'
"""

SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION = r"""Falcon Query Language (FQL) - Search RTR Audit Sessions Guide

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
Direct cloud_request_id filters can be environment/API-shape dependent. If an
exact lookup returns no rows, search by aid or hostname plus a bounded created_at
window and inspect returned command logs client-side.

=== falcon_search_rtr_audit_sessions FQL filter fields ===

""" + generate_md_table(SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS) + """

=== EXAMPLES ===

# Recent RTR audit sessions
created_at:>'now-7d'

# RTR audit sessions for a host pattern
hostname:'DC*'+created_at:>'now-7d'

# Current user's RTR audit sessions
user_id:'@me'+created_at:>'now-7d'

# Command-focused audit search
aid:'2c5c4e7738004deaa9dfcdb86f633f3e'+created_at:>'now-7d'

# Then inspect returned command logs for cloud_request_id, base_command, and command_string.
"""

AGGREGATE_RTR_SESSIONS_GUIDE = """RTR Session Aggregation Guide

Use falcon_aggregate_rtr_sessions to summarize RTR session activity without pulling every
individual session record.

Recommended aggregation fields:
- hostname: Which hosts have the most RTR activity
- aid: Which host agent IDs have RTR activity
- user_id: Which Falcon users or API clients created sessions
- origin: Which integration or source created sessions
- base_command: Which RTR commands are most common
- created_at: Time-based activity buckets with aggregate_type=date_range

Recommended filters:
- created_at:>'now-7d'
- user_id:'@me'
- hostname:'DC*'
- offline_queued:true

Example terms aggregation:
- aggregate_type: terms
- field: base_command
- filter: created_at:>'now-7d'
- size: 10

Example date range aggregation:
- aggregate_type: date_range
- field: created_at
- date_ranges: [{"from": "now-7d", "to": "now"}]

Use this before detailed searches when the user asks "how much", "which hosts", "which users",
or "what commands" across many RTR sessions.
"""

READ_ONLY_RTR_INVESTIGATION_GUIDE = """Read-only RTR Investigation Guide

This guide helps agents use RTR safely for endpoint triage. The current RTR MCP module exposes
the read-only RTR command endpoint for host investigation. It does not expose RTR Admin,
Active Responder, remediation, or arbitrary script execution.

Recommended sequence:
1. Use Falcon detections, incidents, hosts, or NGSIEM to identify the host AID.
2. Use falcon_init_rtr_session to open or reuse a single-host RTR session.
3. Use falcon_run_rtr_read_only_command_and_wait for simple focused evidence collection.
4. Use falcon_execute_rtr_read_only_command plus falcon_check_rtr_command_status when you
   need manual control over request IDs, polling, or output sequence chunks.
5. Use falcon_search_rtr_audit_sessions when accountability or session history matters.
6. Use falcon_delete_rtr_session when the session is no longer needed.

Useful read-only command patterns:
- Processes: base_command=ps, command_string="ps"
- Directory listing: base_command=ls, command_string="ls C:\\Path"
- File hash: base_command=filehash, command_string="filehash C:\\Path\\file.exe"
- File preview: base_command=cat, command_string="cat C:\\Path\\file.txt"
- Registry query: base_command=reg, command_string="reg query HKLM\\Software\\..."
- Network state: base_command=netstat, command_string="netstat"
- Event log review: base_command=eventlog, command_string="eventlog view Security 50"

Model behavior guidance:
- Prefer one host and one question at a time.
- Keep commands narrow and explain what evidence each command is collecting.
- Use audit and aggregation tools before broad RTR activity conclusions.
- Treat offline or queued behavior as a telemetry state, not proof the host is powered off.
- Do not attempt remediation, deletion, script execution, or active-response behavior through
  the read-only RTR tool.
"""
