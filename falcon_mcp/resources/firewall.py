"""
Contains Firewall Management resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_FIREWALL_RULES_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "enabled",
        "Boolean",
        "Filter by rule enabled state. Example: enabled:true",
    ),
    (
        "platform",
        "String",
        "Filter by platform: windows, mac, linux. Rule groups only — on "
        "`falcon_search_firewall_rules` and `falcon_search_firewall_policy_rules` "
        "this is an unknown property and the request fails. "
        "Example: platform:'windows'",
    ),
    (
        "name",
        "String",
        "Rule or rule group name. For substring matching use the contains operator, "
        "name:~'value'. Example: name:~'Block'",
    ),
    (
        "description",
        "String",
        "Rule or rule group description text search.",
    ),
    (
        "created_on",
        "Timestamp",
        "Entity creation timestamp.",
    ),
    (
        "modified_on",
        "Timestamp",
        "Entity last modified timestamp.",
    ),
]

SEARCH_FIREWALL_RULES_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("name", "Sort by name"),
    ("platform", "Sort by platform. Rule groups only"),
    ("created_on", "Sort by creation time"),
    ("modified_on", "Sort by last modified time"),
    ("enabled", "Sort by enabled flag"),
]

SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION = f"""
# Firewall Management FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_firewall_rules`
- `falcon_search_firewall_rule_groups`
- `falcon_search_firewall_policy_rules`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_RULES_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_RULES_FQL_SORT_FIELDS)}

## Examples

- Enabled rules:
  - `filter="enabled:true"`
- Windows rule groups (`platform` works on rule groups only):
  - `filter="platform:'windows'"`
- Rules whose name contains a word:
  - `filter="name:~'Block'"`
- Recently modified entities:
  - `sort="modified_on.desc"`

## Notes

- For name matching, use the contains operator `name:~'value'` (case-insensitive,
  matches whole words). A `name:'value*'` glob is treated literally — the `*` is a
  literal character, so the query silently returns nothing. For an arbitrary
  substring (not a whole word), use the wildcard form `name:*'*value*'`. A plain
  `name:'value'` exact match also works when you know the full name.
- `falcon_search_firewall_policy_rules` requires `rule_group.policy_ids` in the
  filter itself; any other filter without it fails. Pass the same value as
  `policy_id`.
- Start broad, then refine your filter if results are empty.
"""

