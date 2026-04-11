"""
Contains ODS resources.
"""

from falcon_mcp.common.utils import generate_md_table


def _build_embedded_fql_syntax(title: str, common_fields: list[str], examples: list[str]) -> str:
    common_fields_text = "\n".join(f"- {field}" for field in common_fields)
    examples_text = "\n".join(f"- {example}" for example in examples)
    return f"""FQL filter string for querying {title}.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (status:'done',status:'running')+description:'weekly*'

COMMON FIELDS:
{common_fields_text}

EXAMPLES:
{examples_text}
"""


SEARCH_ODS_SCANS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "ODS scan ID. Example: id:'scan-123'"),
    ("status", "String", "Scan status. Example: status:'done'"),
    ("description", "String", "Scan description. Example: description:'weekly scan'"),
    ("initiated_from", "String", "Request origin label. Example: initiated_from:'falcon-mcp'"),
    ("created_on", "Timestamp", "Creation timestamp. Example: created_on:>'2026-03-01T00:00:00Z'"),
]

SEARCH_ODS_SCAN_HOSTS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Scan-host metadata ID. Example: id:'host-meta-123'"),
    ("scan_id", "String", "Parent scan ID. Example: scan_id:'scan-123'"),
    ("host_id", "String", "Host device ID. Example: host_id:'aid-123'"),
    ("status", "String", "Scan-host status. Example: status:'complete'"),
    ("last_updated", "Timestamp", "Last update timestamp. Example: last_updated:>'2026-03-01T00:00:00Z'"),
]

SEARCH_ODS_SCHEDULED_SCANS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Scheduled scan ID. Example: id:'sched-123'"),
    ("status", "String", "Scheduled scan status. Example: status:'enabled'"),
    ("description", "String", "Schedule description. Example: description:'daily scan'"),
    (
        "schedule.start_timestamp",
        "Timestamp",
        "First scheduled run timestamp. Example: schedule.start_timestamp:>'2026-03-01T00:00:00Z'",
    ),
]

SEARCH_ODS_MALICIOUS_FILES_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "ODS malicious file ID. Example: id:'mf-123'"),
    ("scan_id", "String", "Parent scan ID. Example: scan_id:'scan-123'"),
    ("hash", "String", "Malicious file hash. Example: hash:'a1b2c3...'"),
    ("filename", "String", "Malicious file name. Example: filename:'sample.exe'"),
    ("last_updated", "Timestamp", "Last update timestamp. Example: last_updated:>'2026-03-01T00:00:00Z'"),
]

SEARCH_ODS_SCANS_EMBEDDED_FQL_SYNTAX = _build_embedded_fql_syntax(
    "ODS scans",
    common_fields=["id: Scan ID", "status: Scan status", "description: Scan description", "created_on: Creation timestamp"],
    examples=["Completed scans: status:'done'", "Recent weekly scans: description:'weekly*'+created_on:>'2026-03-01T00:00:00Z'"],
)

SEARCH_ODS_SCAN_HOSTS_EMBEDDED_FQL_SYNTAX = _build_embedded_fql_syntax(
    "ODS scan-host metadata",
    common_fields=["id: Scan-host metadata ID", "scan_id: Parent scan ID", "host_id: Host device ID", "status: Host scan status"],
    examples=["Host records for a scan: scan_id:'scan-123'", "Recently updated host scans: last_updated:>'2026-03-01T00:00:00Z'"],
)

SEARCH_ODS_SCHEDULED_SCANS_EMBEDDED_FQL_SYNTAX = _build_embedded_fql_syntax(
    "scheduled ODS scans",
    common_fields=["id: Scheduled scan ID", "status: Schedule status", "description: Schedule description", "schedule.start_timestamp: First run timestamp"],
    examples=["Enabled schedules: status:'enabled'", "Schedules starting soon: schedule.start_timestamp:>'2026-03-01T00:00:00Z'"],
)

SEARCH_ODS_MALICIOUS_FILES_EMBEDDED_FQL_SYNTAX = _build_embedded_fql_syntax(
    "ODS malicious files",
    common_fields=["id: Malicious file ID", "scan_id: Parent scan ID", "hash: Malicious file hash", "filename: Malicious file name"],
    examples=["Files for a scan: scan_id:'scan-123'", "Specific filename pattern: filename:'sample*'"],
)

SEARCH_ODS_SCANS_FQL_DOCUMENTATION = f"""ODS Scans FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_ods_scans`.

{generate_md_table(SEARCH_ODS_SCANS_FQL_FILTERS)}
"""

SEARCH_ODS_SCAN_HOSTS_FQL_DOCUMENTATION = f"""ODS Scan Hosts FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_ods_scan_hosts`.

{generate_md_table(SEARCH_ODS_SCAN_HOSTS_FQL_FILTERS)}
"""

SEARCH_ODS_SCHEDULED_SCANS_FQL_DOCUMENTATION = f"""ODS Scheduled Scans FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_ods_scheduled_scans`
and `falcon_delete_ods_scheduled_scans` when selecting schedules by query.

{generate_md_table(SEARCH_ODS_SCHEDULED_SCANS_FQL_FILTERS)}
"""

SEARCH_ODS_MALICIOUS_FILES_FQL_DOCUMENTATION = f"""ODS Malicious Files FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_ods_malicious_files`.

{generate_md_table(SEARCH_ODS_MALICIOUS_FILES_FQL_FILTERS)}
"""
