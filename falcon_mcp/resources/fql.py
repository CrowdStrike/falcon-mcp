"""
Contains Falcon Query Language resources.
"""

FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Hosts Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal
• > = greater than
• >= = greater than or equal
• < = less than
• <= = less than or equal
• ~ = text match (ignores case, spaces, punctuation)
• !~ = not text match
• * = wildcard (one or more characters)
• !* = not wildcard (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['value1', 'value2'] for multiple distinct values
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format). Also referred as Timestamps
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for multiple string values: ['value 1', 'value 2']
• Use wildcard operator to determine if a property contains or not a substring: property:*'*sub*', property:!*'*sub*'
• Date and timestamp format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""
