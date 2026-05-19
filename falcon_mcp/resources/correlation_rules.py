"""
Contains Correlation Rules resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_CORRELATION_RULES_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        "Name of the rule. Example: name:'Suspicious PowerShell'",
    ),
    (
        "status",
        "String",
        "Rule status. Allowed values: enabled, disabled. Example: status:'enabled'",
    ),
    (
        "severity",
        "Integer",
        "Rule severity (0-100). Example: severity:>50",
    ),
    (
        "tactic",
        "String",
        "MITRE ATT&CK tactic. Example: tactic:'Execution'",
    ),
    (
        "technique",
        "String",
        "MITRE ATT&CK technique. Example: technique:'T1059'",
    ),
    (
        "created_on",
        "Timestamp",
        "Creation timestamp. Example: created_on:>'2024-01-01T00:00:00Z'",
    ),
    (
        "last_updated_on",
        "Timestamp",
        "Last modification timestamp. Example: last_updated_on:>'2024-06-01T00:00:00Z'",
    ),
    (
        "customer_id",
        "String",
        "CID of the tenant. Example: customer_id:'abc123'",
    ),
    (
        "user_id",
        "String",
        "ID of the user who created or owns the rule.",
    ),
    (
        "user_uuid",
        "String",
        "UUID of the user who created or owns the rule.",
    ),
]

_SORT_FIELDS = """
**Sort fields:** name, status, severity, created_on, last_updated_on

**Sort formats:** `field.asc`, `field.desc`, `field|asc`, `field|desc`

**Example:** `last_updated_on.desc`
"""

_FQL_OPERATORS = """
**FQL Operators:**
- Equality: `field:'value'`
- Wildcard: `field:*'partial*'`
- Range: `field:>'value'`, `field:<'value'`
- Integer range: `field:>50`
- Boolean: `field:true` or `field:false`
- AND: `+` (e.g., `status:'enabled'+severity:>50`)
- OR: `,` (e.g., `tactic:'Execution',tactic:'Persistence'`)
"""

SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION = f"""
# NG-SIEM Correlation Rules FQL Filter Guide

Use FQL (Falcon Query Language) to filter rules returned by `falcon_search_correlation_rules`.

## Filter Fields

{generate_md_table(SEARCH_CORRELATION_RULES_FQL_FILTERS)}

## Operators & Syntax
{_FQL_OPERATORS}

## Sort Options
{_SORT_FIELDS}

## Examples

Search for enabled rules:
```
status:'enabled'
```

Search for high-severity rules with a MITRE tactic:
```
severity:>75+tactic:'Execution'
```

Search for rules updated recently:
```
last_updated_on:>'2024-01-01T00:00:00Z'
```

Search for rules by name pattern:
```
name:*'PowerShell*'
```

Search for rules covering a specific technique:
```
technique:'T1059'
```
"""
