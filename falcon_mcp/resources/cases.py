"""
Contains Cases resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_CASES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        "System-level case identifier (opaque base64 string).",
    ),
    (
        "reference_id",
        "String",
        "Human-readable case ID (e.g. ABC-1234). Case-sensitive, full match required.",
    ),
    (
        "status",
        "String",
        """
        Case status. Values:
        - new: Newly created case
        - in_progress: Under investigation
        - closed: Investigation completed
        - reopened: Previously closed, now active again
        Ex: new
        """,
    ),
    (
        "severity",
        "Integer",
        """
        Numeric severity (1-100).
        Informational=1, Low~25, Medium~50, High~75, Critical=100.
        Ex: 70
        """,
    ),
    (
        "name",
        "String",
        "Case name. Ex: Suspicious lateral movement",
    ),
    (
        "description",
        "String",
        "Case description text.",
    ),
    (
        "all_text",
        "String",
        "Full-text search across all searchable case fields.",
    ),
    (
        "created_timestamp",
        "Timestamp",
        "Case creation time in ISO 8601 UTC. Ex: 2025-01-01T00:00:00Z",
    ),
    (
        "updated_timestamp",
        "Timestamp",
        "Last modification time in ISO 8601 UTC. Ex: 2025-06-01T00:00:00Z",
    ),
    (
        "assigned_to_uuid",
        "String",
        "UUID of assigned user.",
    ),
    (
        "assigned_to_name",
        "String",
        "Display name of assigned user.",
    ),
    (
        "created_by",
        "String",
        "Creator email or API client ID.",
    ),
    (
        "modified_by",
        "String",
        "Last modifier email or API client ID.",
    ),
    (
        "tags",
        "String",
        "Tags applied to the case.",
    ),
    (
        "cid",
        "String",
        "Customer ID (Flight Control multi-CID scenarios).",
    ),
    (
        "alerts",
        "String",
        "Alert IDs attached as evidence.",
    ),
    (
        "events",
        "String",
        "LogScale event details in evidence.",
    ),
    (
        "data_domains",
        "String",
        "Data domains from evidence (e.g. Endpoint, Identity, Cloud).",
    ),
    (
        "source_vendors",
        "String",
        "Source vendors from evidence.",
    ),
    (
        "source_products",
        "String",
        "Source products from evidence.",
    ),
    (
        "tactic_ids",
        "String",
        "MITRE ATT&CK tactic IDs from evidence. Ex: TA0006",
    ),
    (
        "tactics",
        "String",
        "MITRE ATT&CK tactic names from evidence. Ex: Credential Access",
    ),
    (
        "technique_ids",
        "String",
        "MITRE ATT&CK technique IDs from evidence. Ex: T1003",
    ),
    (
        "techniques",
        "String",
        "MITRE ATT&CK technique names from evidence.",
    ),
    (
        "aids",
        "String",
        "Agent IDs from evidence.",
    ),
    (
        "hostnames",
        "String",
        "Hostnames from evidence.",
    ),
    (
        "ips",
        "String",
        "IP addresses from evidence.",
    ),
    (
        "email_addresses",
        "String",
        "Email addresses from evidence.",
    ),
    (
        "sha256s",
        "String",
        "SHA-256 hashes from evidence.",
    ),
    (
        "md5s",
        "String",
        "MD5 hashes from evidence.",
    ),
    (
        "usernames",
        "String",
        "Usernames from evidence.",
    ),
    (
        "command_lines",
        "String",
        "Command lines from evidence.",
    ),
    (
        "file_names",
        "String",
        "File names from evidence.",
    ),
    (
        "image_file_names",
        "String",
        "Image file names from evidence.",
    ),
    (
        "cloud_providers",
        "String",
        "Cloud provider. Values: aws, azure, gcp",
    ),
    (
        "cloud_account_ids",
        "String",
        "Cloud account IDs from evidence.",
    ),
    (
        "cloud_regions",
        "String",
        "Cloud regions from evidence. Ex: eu-west-2",
    ),
    (
        "cloud_instance_ids",
        "String",
        "Cloud instance IDs from evidence.",
    ),
    (
        "cloud_availability_zones",
        "String",
        "Cloud availability zones from evidence.",
    ),
    (
        "cloud_service_names",
        "String",
        "Cloud service names from evidence.",
    ),
    (
        "case_template_id",
        "String",
        "Template ID applied to the case.",
    ),
    (
        "case_template_name",
        "String",
        "Template name applied to the case.",
    ),
    (
        "sla_name",
        "String",
        "SLA name from the case template.",
    ),
    (
        "sla_active_timer.status",
        "String",
        "SLA timer status. Values: pending, in_progress, paused, achieved, missed",
    ),
    (
        "sla_active_timer_time_due",
        "String",
        "SLA deadline as epoch timestamp.",
    ),
]

SEARCH_CASES_FQL_DOCUMENTATION = r"""Falcon Query Language (FQL) - Search Cases Guide

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

""" + generate_md_table(SEARCH_CASES_FQL_FILTERS) + """

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
"""


# The four /casemgmt/aggregates/* endpoints share one filterable field set, except
# access-tags, which accepts only id, cid, and key (live-validated 2026-07-28).
AGGREGATE_CASE_CONFIG_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        """
        Display name of the SLA, template, or notification group.
        Not available on access tags. Exact match or `:*` substring.
        Ex: 'BarelyTea Corp SLA'
        """,
    ),
    (
        "key",
        "String",
        """
        Access tag key. Access tags only.
        Ex: 'ANALYST1'
        """,
    ),
    (
        "id",
        "String",
        "Unique identifier of the record.",
    ),
    (
        "cid",
        "String",
        "Customer ID owning the record.",
    ),
    (
        "created_by_name",
        "String",
        """
        Username that created the record. Not available on access tags.
        Ex: 'analyst@example.com'
        """,
    ),
    (
        "updated_by_name",
        "String",
        """
        Username that last updated the record. Not available on access tags.
        Ex: 'analyst@example.com'
        """,
    ),
    (
        "created_timestamp",
        "Timestamp",
        """
        Creation time (UTC). Not available on access tags.
        Ex: >'now-30d' or >'2026-01-01T00:00:00Z'
        """,
    ),
    (
        "updated_timestamp",
        "Timestamp",
        """
        Last update time (UTC). Not available on access tags.
        Ex: >'now-7d'
        """,
    ),
]

AGGREGATE_CASE_CONFIG_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Case Configuration Aggregates Guide

Filters the records counted by falcon_aggregate_case_slas,
falcon_aggregate_case_templates, falcon_aggregate_case_access_tags, and
falcon_aggregate_case_notification_groups. These endpoints aggregate case
*configuration* objects, not cases themselves — to filter cases, see
falcon://cases/search/fql-guide.

=== OPERATORS (live-validated) ===

Exact match:      name:'BarelyTea Corp SLA'
Substring match:  name:*'*Corp*'
Comparison:       created_timestamp:>'now-30d'
AND:              name:*'*SLA*'+created_timestamp:>'now-90d'
OR:               name:'Analyst 1',name:'Analyst 2'

`~` (contains) and a trailing wildcard inside quotes ('Corp*') return no results on
these endpoints — use `:*` for substring matching.

An unsupported filter field returns an error naming the problem rather than an empty
result, so a failed filter is visible rather than silent.

=== AVAILABLE FIELDS ===

"""
    + generate_md_table(AGGREGATE_CASE_CONFIG_FQL_FILTERS)
    + r"""
Access tags accept only `id`, `cid`, and `key`. The other endpoints accept every
field except `key`.

=== EXAMPLES ===

# Templates created in the last 30 days
created_timestamp:>'now-30d'

# Notification groups whose name mentions an analyst
name:*'*Analyst*'

# Records created by a specific user
created_by_name:'analyst@example.com'

# Access tags for a given key
key:'ANALYST1'
"""
)


AGGREGATE_CASE_FILE_DETAILS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        """
        File name of the attachment, including extension.
        Ex: *'*.png'
        """,
    ),
    (
        "case_id",
        "String",
        """
        ID of the case the file is attached to. Prefer the case_ids parameter,
        which builds this filter for you.
        Ex: '019f449a-558e-71ea-ba8f-106d7b265036'
        """,
    ),
    (
        "id",
        "String",
        "Unique identifier of the file itself.",
    ),
    (
        "cid",
        "String",
        "Customer ID owning the file.",
    ),
    (
        "file_size",
        "String",
        """
        Human-readable file size, not a number — compare it as a string.
        Ex: '114.8 KB'
        """,
    ),
]

AGGREGATE_CASE_FILE_DETAILS_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Case File Aggregates Guide

Filters the files counted by falcon_aggregate_case_file_details. This aggregates
files uploaded to cases, not the cases themselves — to filter cases, see
falcon://cases/search/fql-guide.

These are uploaded attachments. They are distinct from a case record's
`analysis_results.files`, which lists forensic artifacts (malware paths and
hashes) observed in detections; that field is empty for cases that do have
attachments, so it cannot be used to answer questions about them.

=== OPERATORS (live-validated) ===

Exact match:      name:'report.pdf'
Substring match:  name:*'*.png'
AND:              case_id:'019f449a-558e-71ea-ba8f-106d7b265036'+name:*'*.png'
OR:               name:*'*.png',name:*'*.jpg'

`~` (contains) returns no results here — use `:*` for substring matching.

=== AVAILABLE FIELDS ===

"""
    + generate_md_table(AGGREGATE_CASE_FILE_DETAILS_FQL_FILTERS)
    + r"""
=== EXAMPLES ===

# Screenshots attached to any case
name:*'*.png'

# Files on one specific case
case_id:'019f449a-558e-71ea-ba8f-106d7b265036'

# PDFs or Word documents
name:*'*.pdf',name:*'*.docx'
"""
)
