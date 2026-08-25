"""
Contains Policies FQL documentation resources.

One unified guide for the `falcon_search_policies` tool covering all six
host-based policy types behind the `policy_type` discriminator — prevention,
sensor_update, firewall, device_control, response, and content_update. The
supported FQL fields are largely common, but the `name` match operator and a few
audit fields differ by type, so per-type notes are documented inline.

Only fields with a confirmed non-empty live hit (validated 2026-06-06) are
documented here.
"""

from falcon_mcp.common.utils import generate_md_table

# Common filterable fields shared across all six policy types. Per-type operator
# differences (notably `name`) are documented in the prose below the table.
COMMON_POLICIES_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    (
        "platform_name",
        "String",
        "Operating system platform. Exact match with `:`. Ex: platform_name:'Windows'. "
        "For content_update the only value is 'all'.",
    ),
    ("enabled", "Boolean", "Whether the policy is enabled. Ex: enabled:true"),
    (
        "created_timestamp",
        "Timestamp",
        "Creation time. Range operators and relative dates supported. Ex: created_timestamp:>'now-7d'",
    ),
    (
        "modified_timestamp",
        "Timestamp",
        "Last modification time. Range operators and relative dates supported. Ex: modified_timestamp:>'now-24h'",
    ),
]

SEARCH_POLICIES_FQL_DOCUMENTATION = (
    """# Policies Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_policies`. One
unified set of filterable fields covers all six policy types selected by
`policy_type` (prevention, sensor_update, firewall, device_control, response,
content_update), but the `name` match operator differs per type — read the
per-type notes below before filtering on `name`.

## Filtering caveats

Read these before searching — they explain two non-obvious API behaviors that
otherwise lead to silent empty results:

1. **Unsupported filter fields return an empty result, not an error.** These
   query APIs do not validate filter fields — filtering on a field that is not
   listed below (or with the wrong operator for the type) silently returns zero
   matches instead of a 400. An empty result therefore does NOT prove nothing
   exists; re-check every field and operator against this guide before concluding
   there are no matches.
2. **`name` matching depends on the operator and differs per policy type.** Using
   the wrong operator for the type silently returns nothing rather than erroring
   (see the per-type note below).

## Common filterable fields (all types)

"""
    + generate_md_table(COMMON_POLICIES_FQL_FILTERS)
    + """

## Per-type `name` operator (read before filtering on name)

The `name` field is matched differently depending on `policy_type`:

- **prevention, response, firewall, device_control**: use the tilde (contains)
  operator — `name:~'value'` (case-insensitive substring). Do NOT use a glob like
  `name:'*value*'`: the `*` is treated as a literal character and silently returns
  nothing. A plain `name:'value'` exact match is also unreliable — it matches a few
  built-in policies (e.g. the Default policy, internally named `platform_default`)
  but silently returns empty for most custom-named policies. Always prefer `~`.
- **sensor_update, content_update**: `name` is NOT filterable — omit it (filtering
  on it silently returns empty).

## Other per-type notes

- **created_by / modified_by**: unreliable across types and not recommended for
  filtering. prevention matches `created_by`/`modified_by` with `~`; firewall
  matches only short exact values (emails containing `@` fail); response,
  sensor_update, and device_control do not reliably support `modified_by`. Prefer
  filtering by timestamp instead.
- **precedence**: accepted in FQL filters but NOT returned in entity bodies (or
  returned null). Do not read `entity['precedence']` from search results; use
  `falcon_set_policy_precedence` to manage ordering.
- **content_update**: `platform_name` is always `'all'` (platform-agnostic) and
  `name` is not filterable.

## Sort and limit notes

Safe sort fields: `name`, `created_timestamp`, `modified_timestamp`, `enabled`,
`created_by`, `modified_by`, `precedence`.

**Use the dot direction separator only.** `created_timestamp.desc` works;
`created_timestamp|desc` is rejected with HTTP 400 on all six policy types, so the
tool rejects the pipe form up front.

**Do NOT sort by `platform_name`.** Sorting by `platform_name` in either
direction returns an HTTP 500 error on every policy type — it is not a valid sort
field even though it is a valid filter field. Use one of the safe sort fields
above instead.

**`device_control` has two extra sort restrictions** (live-validated; they do not
apply to the other five types):

- `created_by` and `modified_by` return HTTP 500. The tool rejects both up front
  for this type.
- `created_timestamp` and `modified_timestamp` ignore the requested direction and
  return the same ascending order for `.asc` and `.desc`. Do not rely on
  `created_timestamp.desc` to surface the newest device_control policies — sort on
  `precedence` or `enabled`, or order the results yourself.

## Example queries (each confirmed to return data)

- Enabled policies: `filter="enabled:true"`
- By platform: `filter="platform_name:'Windows'"`
- Recently created: `filter="created_timestamp:>'now-7d'"`
- Name contains (prevention/response/firewall/device_control): `filter="name:~'default'"`
- Most recently modified first: `sort="modified_timestamp.desc"`

## Notes

- Timestamps support relative values such as `now-7d` or `now-24h` (lowercase, quoted).
- If no results are returned, start with a broad filter (e.g. `enabled:true`) and
  then refine.
"""
)
