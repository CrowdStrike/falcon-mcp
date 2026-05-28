"""
Contains Data Protection (DLP) resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Classification FQL filters
SEARCH_CLASSIFICATIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Classification name. Supports text match (~) for case-insensitive search.

        Ex: name:~'credit'
        Ex: name:'My Classification'
        """,
    ),
    (
        "created_at",
        "Timestamp",
        "Yes",
        """
        Date the classification was created.

        Ex: created_at:>'2024-01-01'
        Ex: created_at:<'2025-06-01'
        """,
    ),
    (
        "modified_at",
        "Timestamp",
        "Yes",
        """
        Date the classification was last modified.

        Ex: modified_at:>'2024-01-01'
        """,
    ),
    (
        "created_by",
        "String",
        "Yes",
        """
        Email of the user who created the classification. Use ~ for partial match.

        Ex: created_by:~'admin'
        """,
    ),
    (
        "modified_by",
        "String",
        "Yes",
        """
        Email of the user who last modified the classification.

        Ex: modified_by:~'admin'
        """,
    ),
]

SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search DLP Classifications Guide

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
• !~ = does not text match

=== DATA TYPES & SYNTAX ===
• Strings: 'value' (use ~ for case-insensitive matching)
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== falcon_search_dlp_classifications FQL filter options ===

""" + generate_md_table(SEARCH_CLASSIFICATIONS_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• name:~'credit' - Classifications with "credit" in the name (case-insensitive)
• created_at:>'2024-01-01' - Created after a date
• modified_at:>'2024-06-01' - Recently modified

=== SORTING ===

Supported sort fields: name.asc, name.desc, created_at.asc, created_at.desc, modified_at.desc

=== IMPORTANT NOTES ===
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""

# Policy FQL filters
SEARCH_POLICIES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Policy name. Supports text match (~) for case-insensitive search.

        Ex: name:~'production'
        Ex: name:'Default Policy'
        """,
    ),
    (
        "is_enabled",
        "Boolean",
        "No",
        """
        Whether the policy is enabled.

        Ex: is_enabled:true
        Ex: is_enabled:false
        """,
    ),
    (
        "is_default",
        "Boolean",
        "No",
        """
        Whether this is the default policy.

        Ex: is_default:true
        """,
    ),
    (
        "created_at",
        "Timestamp",
        "Yes",
        """
        Date the policy was created.

        Ex: created_at:>'2024-01-01'
        """,
    ),
    (
        "description",
        "String",
        "Yes",
        """
        Policy description text. Supports text match (~).

        Ex: description:~'compliance'
        """,
    ),
    (
        "precedence",
        "Integer",
        "Yes",
        """
        Policy precedence (evaluation order). Lower = higher priority.

        Ex: precedence:>0
        Ex: precedence:0
        """,
    ),
    (
        "modified_by",
        "String",
        "Yes",
        """
        Email of the user who last modified the policy.

        Ex: modified_by:~'admin'
        """,
    ),
]

SEARCH_POLICIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search DLP Policies Guide

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
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== IMPORTANT: platform_name parameter ===

The falcon_search_dlp_policies tool requires a platform_name parameter ('win' or 'mac')
which is separate from the FQL filter. The filter applies within the selected platform.

=== falcon_search_dlp_policies FQL filter options ===

""" + generate_md_table(SEARCH_POLICIES_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• is_enabled:true - All enabled policies
• is_default:true - Default policy only
• is_enabled:true+precedence:>0 - Enabled non-default policies
• name:~'production' - Policies with "production" in the name
• created_at:>'2024-01-01' - Recently created policies

=== SORTING ===

Supported sort fields: name.asc, name.desc, precedence.asc, created_at.desc

=== IMPORTANT NOTES ===
• platform_name ('win' or 'mac') is required and is not an FQL filter
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Boolean values have no quotes: is_enabled:true
"""

# Content Pattern FQL filters
SEARCH_CONTENT_PATTERNS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Content pattern name. Supports text match (~) for case-insensitive search.

        Ex: name:~'credit card'
        Ex: name:'SSN Pattern'
        """,
    ),
    (
        "type",
        "String",
        "Yes",
        """
        Pattern type. Values: custom, predefined.

        Ex: type:'custom'
        Ex: type:'predefined'
        """,
    ),
    (
        "category",
        "String",
        "Yes",
        """
        Pattern category. Values include: Custom, Financial, PII, Healthcare.

        Ex: category:'Custom'
        Ex: category:'Financial'
        """,
    ),
    (
        "region",
        "String",
        "Yes",
        """
        Geographic region the pattern applies to. Ex: ALL, US, EU.

        Ex: region:'ALL'
        Ex: region:'US'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the content pattern has been deleted.

        Ex: deleted:false
        Ex: deleted:true
        """,
    ),
    (
        "example",
        "String",
        "Yes",
        """
        Example text for the content pattern.

        Ex: example:~'4111'
        """,
    ),
]

SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search DLP Content Patterns Guide

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

=== falcon_search_dlp_content_patterns FQL filter options ===

""" + generate_md_table(SEARCH_CONTENT_PATTERNS_FQL_FILTERS) + """

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
"""
