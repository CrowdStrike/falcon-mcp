Falcon Query Language (FQL) - Search Host Groups Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===

**WORKING OPERATORS:**
• No operator = equals (default) - ALL FIELDS
• ! = not equal to - ALL FIELDS
• > = greater than - TIMESTAMP FIELDS ONLY
• >= = greater than or equal - TIMESTAMP FIELDS ONLY
• < = less than - TIMESTAMP FIELDS ONLY
• <= = less than or equal - TIMESTAMP FIELDS ONLY
• ~ = text match (case insensitive) - TEXT FIELDS ONLY
• * = wildcard matching - LIMITED SUPPORT (see examples below)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_host_groups FQL filter options ===

|Name|Type|Operators|Description|
|-|-|-|-|
|name|String|Yes|The name of the host group. LIMITED wildcard support: name:'Servers*' (prefix) works. Ex: name:'Windows Servers'|
|group_type|String|No|The method by which the group is managed. Possible values: static, staticByID, dynamic. Ex: group_type:'dynamic'|
|created_by|String|No|The email of the user which created the group. Ex: created_by:'user@example.com'|
|created_timestamp|Timestamp|Yes|Group creation timestamp (UTC). Ex: created_timestamp:>'2024-01-01T00:00:00Z'|
|modified_by|String|No|The email of the user which last modified the group. Ex: modified_by:'user@example.com'|
|modified_timestamp|Timestamp|Yes|Last record update timestamp (UTC). Ex: modified_timestamp:<'2024-12-31T23:59:59Z'|

=== WORKING PATTERNS ===

**Basic Equality:**
• group_type:'static', group_type:'dynamic', group_type:'staticByID'
• name:'Production Servers'
• created_by:'admin@example.com'

**Combined Conditions:**
• group_type:'dynamic'+created_by:'admin@example.com'
• (group_type:'static',group_type:'staticByID')+name:'PCI*'

**Timestamp Comparisons:**
• created_timestamp:>'2024-01-01T00:00:00Z'
• modified_timestamp:>='2024-06-01T00:00:00Z'
• modified_timestamp:<='2024-12-31T23:59:59Z'

**Inequality Filters:**
• group_type:!'dynamic' (non-dynamic groups)

**Name Wildcards (Limited):**
• name:'Servers*' (prefix)
• name:'*-prod' (suffix)

**Text Match:**
• name:~'server'
• created_by:~'admin'

=== PATTERNS TO AVOID ===
• Simple wildcards: name:*, created_by:*
• Contains wildcards: name:'*server*'

=== SYNTAX RULES ===
• Use single quotes around string values: 'value'
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Combine conditions with + (AND) or , (OR)
• Use parentheses for grouping: (condition1,condition2)+condition3

=== NOTE ON MEMBER SEARCH ===
This guide applies to searching host GROUPS (falcon_search_host_groups). To
search the member DEVICES of a group (falcon_search_host_group_members) or to
select hosts for falcon_perform_host_group_action, the filter operates on
HOST/DEVICE attributes (platform_name, hostname, etc.) — see the hosts FQL
guide (falcon://hosts/search/fql-guide) instead.
