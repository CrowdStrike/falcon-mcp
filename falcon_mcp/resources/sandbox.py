"""
Contains Sandbox resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_SANDBOX_SUBMISSIONS_EMBEDDED_FQL_SYNTAX = """FQL filter string for querying Falcon Sandbox submissions.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (state:'in_progress',state:'success')+sha256:'a1b2*'

COMMON FIELDS:
- id: Submission ID
- sha256: Uploaded sample hash
- state: Submission processing state
- created_on: Submission creation timestamp

EXAMPLES:
- Submission by sample hash: sha256:'a1b2c3*'
- Completed submissions: state:'success'
"""

SEARCH_SANDBOX_REPORTS_EMBEDDED_FQL_SYNTAX = """FQL filter string for querying Falcon Sandbox reports.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (verdict:'malicious',verdict:'suspicious')+sha256:'a1b2*'

COMMON FIELDS:
- id: Report ID
- sha256: Uploaded sample hash
- verdict: Sandbox verdict
- created_on: Report creation timestamp

EXAMPLES:
- Malicious reports: verdict:'malicious'
- Reports by sample hash: sha256:'a1b2c3*'
"""

SEARCH_SANDBOX_SUBMISSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Submission ID. Example: id:'sub-123'"),
    ("sha256", "String", "Uploaded sample SHA256. Example: sha256:'a1b2c3...'"),
    ("state", "String", "Submission state. Example: state:'success'"),
    ("created_on", "Timestamp", "Submission creation time. Example: created_on:>'2026-03-01T00:00:00Z'"),
]

SEARCH_SANDBOX_REPORTS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Report ID. Example: id:'report-123'"),
    ("sha256", "String", "Uploaded sample SHA256. Example: sha256:'a1b2c3...'"),
    ("verdict", "String", "Sandbox verdict. Example: verdict:'malicious'"),
    ("created_on", "Timestamp", "Report creation time. Example: created_on:>'2026-03-01T00:00:00Z'"),
]

SEARCH_SANDBOX_SUBMISSIONS_FQL_DOCUMENTATION = f"""Falcon Sandbox Submissions FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_sandbox_submissions`.

{generate_md_table(SEARCH_SANDBOX_SUBMISSIONS_FQL_FILTERS)}
"""

SEARCH_SANDBOX_REPORTS_FQL_DOCUMENTATION = f"""Falcon Sandbox Reports FQL Filter Guide

Use this guide for the `filter` parameter of `falcon_search_sandbox_reports`.

{generate_md_table(SEARCH_SANDBOX_REPORTS_FQL_FILTERS)}
"""
