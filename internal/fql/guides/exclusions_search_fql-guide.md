# Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_exclusions`.
The supported fields depend on the `exclusion_type` you are searching. Pick the
matching section below.

## Filtering caveats

Read these before searching — they explain two non-obvious API behaviors that
otherwise lead to silent empty results:

1. **Unsupported filter fields return an empty result, not an error.** These
   query APIs do not validate filter fields — filtering on a field that is not
   listed in the matching section's table silently returns zero matches instead
   of a 400. An empty result therefore does NOT prove nothing exists; if a search
   comes back empty, re-check every field against the table below before
   concluding there are no matches.
2. **`value`/`name` matching depends on the operator.** The plain `:` operator is
   an exact, full-string match — `value:'/usr/local'` matches only an entry whose
   value is exactly `/usr/local`, and any `*` inside the quotes is treated as a
   literal character, not a wildcard. For partial-path or substring matching, use
   the `:*` wildcard operator with a glob pattern: `value:*'*/usr/local*'` matches
   any value containing `/usr/local`, and `name:*'*Signer*'` matches any name
   containing `Signer`. The `~` (tilde/contains) operator is NOT supported on these
   fields and silently returns nothing.

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

|Field|Type|Description|
|-|-|-|
|applied_globally|Boolean|Whether the exclusion applies to all hosts. Ex: applied_globally:true|
|created_on|Timestamp|Creation time. Ex: created_on:>'now-7d'|
|last_modified|Timestamp|Last modification time. Ex: last_modified:>'now-24h'|
|pattern_id|String|IOA rule pattern ID the exclusion targets. Exact match only. Ex: pattern_id:'569'|

Sortable fields: `last_modified`, `name`, `created_by`, `modified_by`,
`pattern_id`, `pattern_name`. Note: IOA does NOT support sorting by `created_on`
— use `last_modified.desc` to surface the most recently changed exclusions.

Examples:
- Recently created: `filter="created_on:>'now-7d'"`
- By rule pattern: `filter="pattern_id:'569'"`
- Globally applied: `filter="applied_globally:true"`
- Most recent first: `sort="last_modified.desc"`

## Machine Learning Exclusions (`exclusion_type="ml"`)

|Field|Type|Description|
|-|-|-|
|applied_globally|Boolean|Whether the exclusion applies to all hosts. Ex: applied_globally:true|
|created_on|Timestamp|Creation time. Ex: created_on:>'now-7d'|
|last_modified|Timestamp|Last modification time. Ex: last_modified:>'now-24h'|
|value|String|Excluded path/value. Plain `:` is exact match (`*` is literal); use the `:*` wildcard operator for substrings. Ex: value:*'*/usr/local*'|

Sortable fields: `created_on`, `last_modified`, `value`, `applied_globally`.

Examples:
- Recently modified: `filter="last_modified:>'now-24h'"`
- Recently created: `filter="created_on:>'now-7d'"`
- Value contains a substring: `filter="value:*'*/usr/local*'"` (use the `:*` wildcard operator)
- Exact value: `filter="value:'/usr/local/bin/app'"` (plain `:`; `*` would be literal)
- Globally applied: `filter="applied_globally:true"`
- Most recent first: `sort="created_on.desc"`

## Sensor Visibility Exclusions (`exclusion_type="sensor_visibility"`)

|Field|Type|Description|
|-|-|-|
|applied_globally|Boolean|Whether the exclusion applies to all hosts. Ex: applied_globally:true|
|created_on|Timestamp|Creation time. Ex: created_on:>'now-7d'|
|last_modified|Timestamp|Last modification time. Ex: last_modified:>'now-24h'|
|value|String|Excluded path/value. Plain `:` is exact match (`*` is literal); use the `:*` wildcard operator for substrings. Ex: value:*'*\\System32\\*'|

Sortable fields: `created_on`, `last_modified`, `value`, `applied_globally`,
`created_by`, `modified_by`.

Examples:
- Recently created: `filter="created_on:>'now-7d'"`
- Globally applied: `filter="applied_globally:true"`
- Value contains a substring: `filter="value:*'*\System32\*'"` (use the `:*` wildcard operator)
- Exact value: `filter="value:'C:\Windows\System32\app.exe'"` (plain `:`; `*` would be literal)
- Most recent first: `sort="created_on.desc"`

## Certificate-Based Exclusions (`exclusion_type="certificate"`)

|Field|Type|Description|
|-|-|-|
|applied_globally|Boolean|Whether the exclusion applies to all hosts. Ex: applied_globally:true|
|created_by|String|User who created the exclusion. Exact match only. Ex: created_by:'analyst@example.com'|
|created_on|Timestamp|Creation time. Ex: created_on:>'now-7d'|
|modified_by|String|User who last modified the exclusion. Exact match only. Ex: modified_by:'analyst@example.com'|
|modified_on|Timestamp|Last modification time (certificate uses modified_on, not last_modified). Ex: modified_on:>'now-7d'|
|name|String|Exclusion name. Plain `:` is exact match; use the `:*` wildcard operator for substrings. Ex: name:*'*Signer*'|

Sortable fields: `created_on`, `modified_on`, `name`, `created_by`,
`modified_by`.

Examples:
- Recently modified: `filter="modified_on:>'now-7d'"`
- Name contains a substring: `filter="name:*'*Signer*'"` (use the `:*` wildcard operator)
- Exact name: `filter="name:'TrustedSigner'"` (plain `:`)
- Created by a user: `filter="created_by:'analyst@example.com'"`
- Globally applied: `filter="applied_globally:true"`
- Most recent first: `sort="created_on.desc"`

## Notes

- Timestamps support relative values such as `now-7d` or `now-24h` (lowercase, quoted).
- If no results are returned, start with a broad filter and then refine.
