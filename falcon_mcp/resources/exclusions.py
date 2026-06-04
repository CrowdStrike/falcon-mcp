"""
Contains Exclusions FQL documentation resources.

One unified guide for the `falcon_search_exclusions` tool with four labeled
sections — IOA, Machine Learning, Sensor Visibility, and Certificate-Based —
because the supported FQL fields differ by exclusion type.
"""

from falcon_mcp.common.utils import generate_md_table

IOA_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies to all hosts. Ex: applied_globally:true"),
    ("created_by", "String", "User who created the exclusion."),
    ("created_on", "Timestamp", "Creation time. Ex: created_on:>'now-7d'"),
    ("last_modified", "Timestamp", "Last modification time."),
    ("modified_by", "String", "User who last modified the exclusion."),
    ("name", "String", "Exclusion name. Ex: name:'my-exclusion'"),
    ("value", "String", "Exclusion value."),
    ("pattern_id", "String", "IOA rule pattern ID the exclusion targets. Ex: pattern_id:'569'"),
    ("pattern_name", "String", "IOA rule pattern name."),
]

ML_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies to all hosts. Ex: applied_globally:true"),
    ("created_by", "String", "User who created the exclusion."),
    ("created_on", "Timestamp", "Creation time. Ex: created_on:>'now-7d'"),
    ("last_modified", "Timestamp", "Last modification time."),
    ("modified_by", "String", "User who last modified the exclusion."),
    ("value", "String", "Excluded path/value. Ex: value:'/tmp/*'"),
]

SENSOR_VISIBILITY_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies to all hosts. Ex: applied_globally:true"),
    ("created_by", "String", "User who created the exclusion."),
    ("created_on", "Timestamp", "Creation time. Ex: created_on:>'now-7d'"),
    ("last_modified", "Timestamp", "Last modification time."),
    ("modified_by", "String", "User who last modified the exclusion."),
    ("value", "String", "Excluded path/value. Ex: value:'C:\\\\Temp\\\\*'"),
]

CERTIFICATE_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies to all hosts. Ex: applied_globally:true"),
    ("created_by", "String", "User who created the exclusion."),
    ("created_on", "Timestamp", "Creation time. Ex: created_on:>'now-7d'"),
    ("modified_by", "String", "User who last modified the exclusion."),
    ("modified_on", "Timestamp", "Last modification time (certificate uses modified_on, not last_modified)."),
    ("name", "String", "Exclusion name. Ex: name:'trusted-signer'"),
    ("value", "String", "Exclusion value."),
]

SEARCH_EXCLUSIONS_FQL_DOCUMENTATION = (
    """# Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_exclusions`.
The supported fields depend on the `exclusion_type` you are searching. Pick the
matching section below.

## Sort and limit notes

- Sortable fields differ from filterable fields and vary by type — use only the
  fields listed under each section's "Sortable fields" below. Sorting by an
  unlisted field returns a 400 "Unknown sort value" error.
- For `ioa`, `ml`, and `sensor_visibility`, a sort direction suffix is recommended
  (e.g. `last_modified.desc`). Bare field names may be rejected by these APIs, so
  the tool appends `.desc` when you omit a direction.
- `certificate` accepts either a bare field (`created_on`) or a suffixed one
  (`created_on.desc`).
- The `certificate` query caps `limit` at 100; the other types allow up to 500.

## IOA Exclusions (`exclusion_type="ioa"`)

"""
    + generate_md_table(IOA_EXCLUSIONS_FQL_FILTERS)
    + """

Sortable fields: `last_modified`, `name`, `created_by`, `modified_by`,
`pattern_id`, `pattern_name`. Note: IOA does NOT support sorting by `created_on`
— use `last_modified.desc` to surface the most recently changed exclusions.

Examples:
- Recently created: `filter="created_on:>'now-7d'"`
- By rule pattern: `filter="pattern_id:'569'"`
- Globally applied: `filter="applied_globally:true"`
- Most recent first: `sort="last_modified.desc"`

## Machine Learning Exclusions (`exclusion_type="ml"`)

"""
    + generate_md_table(ML_EXCLUSIONS_FQL_FILTERS)
    + """

Sortable fields: `created_on`, `last_modified`, `value`, `applied_globally`.

Examples:
- Recently modified: `filter="last_modified:>'now-24h'"`
- By value: `filter="value:'/tmp/*'"`
- Created by a user: `filter="created_by:'analyst@example.com'"`
- Most recent first: `sort="created_on.desc"`

## Sensor Visibility Exclusions (`exclusion_type="sensor_visibility"`)

"""
    + generate_md_table(SENSOR_VISIBILITY_EXCLUSIONS_FQL_FILTERS)
    + """

Sortable fields: `created_on`, `last_modified`, `value`, `applied_globally`,
`created_by`, `modified_by`.

Examples:
- Recently created: `filter="created_on:>'now-7d'"`
- Globally applied: `filter="applied_globally:true"`
- By value: `filter="value:'*\\\\Temp\\\\*'"`
- Most recent first: `sort="created_on.desc"`

## Certificate-Based Exclusions (`exclusion_type="certificate"`)

"""
    + generate_md_table(CERTIFICATE_EXCLUSIONS_FQL_FILTERS)
    + """

Sortable fields: `created_on`, `modified_on`, `name`, `created_by`,
`modified_by`.

Examples:
- Recently modified: `filter="modified_on:>'now-7d'"`
- By name: `filter="name:'trusted-signer'"`
- Globally applied: `filter="applied_globally:true"`
- Most recent first: `sort="created_on.desc"`

## Notes

- Timestamps support relative values such as `now-7d` or `now-24h` (lowercase, quoted).
- If no results are returned, start with a broad filter and then refine.
"""
)
