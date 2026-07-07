
# Firewall Management FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_firewall_rules`
- `falcon_search_firewall_rule_groups`

## Filter Fields

|Field|Type|Description|
|-|-|-|
|enabled|Boolean|Filter by rule enabled state. Example: enabled:true|
|platform|String|Filter by platform. Example: platform:'windows'|
|name|String|Rule or rule group name. Example: name:'Block*'|
|description|String|Rule or rule group description text search.|
|created_on|Timestamp|Entity creation timestamp.|
|modified_on|Timestamp|Entity last modified timestamp.|

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

|Field|Description|
|-|-|
|name|Sort by name|
|platform|Sort by platform|
|created_on|Sort by creation time|
|modified_on|Sort by last modified time|
|enabled|Sort by enabled flag|

## Examples

- Enabled rules:
  - `filter="enabled:true"`
- Windows rule groups:
  - `filter="platform:'windows'"`
- Recently modified entities:
  - `sort="modified_on.desc"`

## Notes

- For policy-specific searches, use `falcon_search_firewall_policy_rules` with `policy_id`.
- Start broad, then refine your filter if results are empty.
