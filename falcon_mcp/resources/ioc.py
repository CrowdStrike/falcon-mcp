"""
Contains IOC resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_IOCS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "action",
        "String",
        "IOC action. Example: action:'detect'",
    ),
    (
        "applied_globally",
        "Boolean",
        "Whether the IOC is applied globally. Example: applied_globally:true",
    ),
    (
        "created_by",
        "String",
        "Username or identifier that created the IOC.",
    ),
    (
        "created_on",
        "Timestamp",
        "IOC creation timestamp.",
    ),
    (
        "expiration",
        "Timestamp",
        "IOC expiration time.",
    ),
    (
        "expired",
        "Boolean",
        "Whether the IOC is already expired.",
    ),
    (
        "metadata.filename.raw",
        "String",
        "Filename metadata (when provided).",
    ),
    (
        "modified_by",
        "String",
        "Username or identifier that last modified the IOC.",
    ),
    (
        "modified_on",
        "Timestamp",
        "IOC last modified timestamp.",
    ),
    (
        "severity_number",
        "Number",
        "Numeric severity value.",
    ),
    (
        "source",
        "String",
        "IOC source label. Example: source:'mcp'",
    ),
    (
        "type",
        "String",
        "Indicator type. Examples: domain, ipv4, ipv6, md5, sha256",
    ),
    (
        "value",
        "String",
        "Indicator value. Example: value:'malicious.example'",
    ),
]

SEARCH_IOCS_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("action", "Sort by action"),
    ("applied_globally", "Sort by global scope"),
    ("created_on", "Sort by creation timestamp"),
    ("expiration", "Sort by expiration timestamp"),
    ("modified_on", "Sort by last modification timestamp"),
    ("severity_number", "Sort by severity"),
    ("source", "Sort by source"),
    ("type", "Sort by IOC type"),
    ("value", "Sort by IOC value"),
]

SEARCH_IOCS_FQL_DOCUMENTATION = f"""
# IOC Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_iocs`.
This module uses Falcon IOC Service Collection endpoints (`indicator_*_v1`).

## Filter Fields

{generate_md_table(SEARCH_IOCS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_IOCS_SORT_FIELDS)}

## Examples

- Active domain IOCs:
  - `filter="type:'domain'+expired:false"`
- High severity IOCs first:
  - `sort="severity_number.desc"`
- IOC values containing a string:
  - `filter="value:*example*"`

## Notes

- Validate filters in a test environment before production use.
- If no results are returned, start with a broad filter and then refine.
"""

