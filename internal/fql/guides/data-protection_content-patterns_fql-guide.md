Falcon Query Language (FQL) - Search Data Protection Content Patterns Guide

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

=== DATA TYPES & SYNTAX ===
• Strings: 'value' (use ~ for case-insensitive matching)
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== falcon_search_data_protection_content_patterns FQL filter options ===

|Name|Type|Operators|Description|
|-|-|-|-|
|name|String|Yes|Content pattern name. Supports text match (~) for case-insensitive search. Ex: name:~'credit card' Ex: name:'SSN Pattern'|
|type|String|Yes|Pattern type. Values: custom, predefined. Ex: type:'custom' Ex: type:'predefined'|
|category|String|Yes|Pattern category. Values include: Custom, Financial, PII, Healthcare. Ex: category:'Custom' Ex: category:'Financial'|
|region|String|Yes|Geographic region the pattern applies to. Ex: ALL, US, EU. Ex: region:'ALL' Ex: region:'US'|
|deleted|Boolean|No|Whether the content pattern has been deleted. Ex: deleted:false Ex: deleted:true|
|example|String|Yes|Example text for the content pattern. Ex: example:~'4111'|

=== EXAMPLE USAGE ===

• type:'custom' - Custom patterns only
• type:'predefined' - CrowdStrike-provided patterns
• category:'Financial' - Financial data patterns
• deleted:false - Active (non-deleted) patterns
• region:'US'+type:'predefined' - US-specific predefined patterns
• name:~'credit' - Patterns with "credit" in the name

=== SORTING ===

Supported sort fields: name.asc, name.desc, category.asc, region.asc

=== IMPORTANT NOTES ===
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Boolean values have no quotes: deleted:false
• type values are lowercase: 'custom', 'predefined'
