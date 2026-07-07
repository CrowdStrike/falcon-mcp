Falcon Query Language (FQL) - Search Host Groups Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal to
• > = greater than (timestamp fields)
• >= = greater than or equal (timestamp fields)
• < = less than (timestamp fields)
• <= = less than or equal (timestamp fields)
• ~ = text match (case insensitive)

=== DATA TYPES & SYNTAX ===
• Strings: 'value'
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) or relative like 'now-30d'
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_host_groups FQL filter options ===

|Name|Type|Description|
|-|-|-|
|name|String|The name of the host group. Ex: name:'Production Servers'|
|group_type|String|The type of host group. Possible values: - static (members assigned by hostname) - staticByID (members assigned by device ID) - dynamic (members matched by an FQL assignment rule) Ex: group_type:'static'|
|created_by|String|The user who created the host group. Ex: created_by:'user@example.com'|
|created_timestamp|Timestamp|The timestamp when the host group was created (UTC). Ex: created_timestamp:>'2024-01-01T00:00:00Z' Ex: created_timestamp:>'now-30d'|
|modified_by|String|The user who last modified the host group. Ex: modified_by:'user@example.com'|
|modified_timestamp|Timestamp|The timestamp when the host group was last modified (UTC). Ex: modified_timestamp:>'2024-01-01T00:00:00Z' Ex: modified_timestamp:>'now-7d'|

=== EXAMPLE QUERIES ===

**By name:**
• name:'Production Servers'

**By type:**
• group_type:'static'
• group_type:'staticByID'
• group_type:'dynamic'

**By creator:**
• created_by:'user@example.com'

**Recently created:**
• created_timestamp:>'now-30d'
• created_timestamp:>'2024-01-01T00:00:00Z'

**Recently modified:**
• modified_timestamp:>'now-7d'

**Combined Conditions:**
• group_type:'static'+created_by:'user@example.com'
• (group_type:'static',group_type:'staticByID')+modified_timestamp:>'now-30d'

=== 💡 SYNTAX RULES ===
• Use single quotes around string values: 'value'
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Relative dates use lowercase quoted syntax: 'now-7d', 'now-30d'
• Combine conditions with + (AND) or , (OR)

=== NOTE ON MEMBER SEARCH ===
The falcon_search_host_group_members tool filters on HOST (device) attributes,
not host group attributes. Consult falcon://hosts/search/fql-guide for the
filter syntax of that tool.
