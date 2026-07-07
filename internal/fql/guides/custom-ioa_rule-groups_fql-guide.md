
# Custom IOA Rule Groups FQL Filter Guide

Use FQL (Falcon Query Language) to filter rule groups returned by `falcon_search_ioa_rule_groups`.

## Filter Fields

|Field|Type|Description|
|-|-|-|
|enabled|Boolean|Whether the rule group is enabled. Example: enabled:true|
|platform|String|Platform for the rule group. Allowed values: windows, mac, linux. Example: platform:'windows'|
|name|String|Name of the rule group. Example: name:'Suspicious Process Creation'|
|description|String|Description of the rule group. Example: description:'*lateral movement*'|
|rules.action_label|String|Action label for rules within the group. Example: rules.action_label:'Detect'|
|rules.name|String|Name of rules within the group. Example: rules.name:'Block cmd.exe'|
|rules.description|String|Description of rules within the group.|
|rules.pattern_severity|String|Severity of rules. Allowed values: critical, high, medium, low, informational. Example: rules.pattern_severity:'high'|
|rules.ruletype_name|String|Rule type name for rules. Example: rules.ruletype_name:'Process Creation'|
|rules.enabled|Boolean|Whether rules in the group are enabled. Example: rules.enabled:true|
|created_on|Timestamp|Creation timestamp. Example: created_on:>'2024-01-01T00:00:00Z'|
|modified_on|Timestamp|Last modification timestamp. Example: modified_on:>'2024-06-01T00:00:00Z'|

## Operators & Syntax
=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal to
• > = greater than
• >= = greater than or equal
• < = less than
• <= = less than or equal
• ~ = text match (ignores case, spaces, punctuation)
• * = wildcard matching (not supported on all fields — see endpoint-specific notes below)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) or relative: 'now-7d', 'now-24h' (lowercase, single-quoted)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition (e.g., platform_name:'Windows'+status:'normal')
• , = OR condition (e.g., severity_name:'Critical',severity_name:'High')
• ( ) = Group expressions

IMPORTANT: Use + for AND and , for OR — do NOT use the words AND/OR.
Values must be single-quoted. Relative dates must be lowercase ('now-7d' not 'NOW-7d').

## Sort Options

**Sort fields:** created_by, created_on, enabled, modified_by, modified_on, name, description

**Sort formats:** `field.asc`, `field.desc`, `field|asc`, `field|desc`

**Example:** `modified_on.desc`


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
