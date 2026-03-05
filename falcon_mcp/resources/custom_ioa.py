"""
Contains Custom IOA resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_IOA_RULE_GROUPS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "enabled",
        "Boolean",
        "Whether the rule group is enabled. Example: enabled:true",
    ),
    (
        "platform",
        "String",
        "Platform for the rule group. Allowed values: windows, mac, linux. Example: platform:'windows'",
    ),
    (
        "name",
        "String",
        "Name of the rule group. Example: name:'Suspicious Process Creation'",
    ),
    (
        "description",
        "String",
        "Description of the rule group. Example: description:'*lateral movement*'",
    ),
    (
        "rules.action_label",
        "String",
        "Action label for rules within the group. Example: rules.action_label:'Detect'",
    ),
    (
        "rules.name",
        "String",
        "Name of rules within the group. Example: rules.name:'Block cmd.exe'",
    ),
    (
        "rules.description",
        "String",
        "Description of rules within the group.",
    ),
    (
        "rules.pattern_severity",
        "String",
        "Severity of rules. Allowed values: critical, high, medium, low, informational. Example: rules.pattern_severity:'high'",
    ),
    (
        "rules.ruletype_name",
        "String",
        "Rule type name for rules. Example: rules.ruletype_name:'Process Creation'",
    ),
    (
        "rules.enabled",
        "Boolean",
        "Whether rules in the group are enabled. Example: rules.enabled:true",
    ),
    (
        "created_on",
        "Timestamp",
        "Creation timestamp. Example: created_on:>'2024-01-01T00:00:00Z'",
    ),
    (
        "modified_on",
        "Timestamp",
        "Last modification timestamp. Example: modified_on:>'2024-06-01T00:00:00Z'",
    ),
]

_SORT_FIELDS = """
**Sort fields:** created_by, created_on, enabled, modified_by, modified_on, name, description

**Sort formats:** `field.asc`, `field.desc`, `field|asc`, `field|desc`

**Example:** `modified_on.desc`
"""

_FQL_OPERATORS = """
**FQL Operators:**
- Equality: `field:'value'`
- Wildcard: `field:*'partial*'`
- Range: `field:>'value'`, `field:<'value'`
- Boolean: `field:true` or `field:false`
- AND: `+` (e.g., `platform:'windows'+enabled:true`)
- OR: `,` (e.g., `platform:'windows',platform:'mac'`)
"""

SEARCH_IOA_RULE_GROUPS_FQL_DOCUMENTATION = f"""
# Custom IOA Rule Groups FQL Filter Guide

Use FQL (Falcon Query Language) to filter rule groups returned by `falcon_search_ioa_rule_groups`.

## Filter Fields

{generate_md_table(SEARCH_IOA_RULE_GROUPS_FQL_FILTERS)}

## Operators & Syntax
{_FQL_OPERATORS}

## Sort Options
{_SORT_FIELDS}

## Examples

Search for enabled Windows rule groups:
```
platform:'windows'+enabled:true
```

Search for rule groups with high-severity rules:
```
rules.pattern_severity:'high'
```

Search for rule groups modified recently:
```
modified_on:>'2024-01-01T00:00:00Z'
```

Search for rule groups by name pattern:
```
name:*'Suspicious*'
```
"""
