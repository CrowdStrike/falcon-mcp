"""
Contains Sensor Usage resources.
"""

from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, operators, description)
SEARCH_SENSOR_USAGE_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "event_date",
        "Date",
        "Yes",
        """
        The final date of the results to be returned in ISO 8601 format (YYYY-MM-DD).
        Data is available for retrieval starting with the current date minus 2 days
        and going back 395 days.

        Data is not available for the current date or the current date minus 1 day.

        Default: the current date minus 2 days

        Ex: event_date:'2024-06-11'
        """
    ),
    (
        "period",
        "String",
        "Yes",
        """
        The number of days of data to return. Even though this looks like a number, make sure to always use quotes for period for example '3' instead of 3.

        Minimum: 1
        Maximum: 395
        Default: 28

        Ex: period:'30'
        """
    ),
    (
        "selected_cids",
        "String",
        "No",
        """
        A comma-separated list of up to 100 CID IDs to return data for.
        This filter is available to Falcon Flight Control parent CIDs and to CIDs
        in multi-CID deployments with the access-account-billing-data feature flag enabled.

        Note: This field is case-sensitive and requires the correct input of capital and lowercase letters.

        Ex: selected_cids:'cid_1,cid_2,cid_3'
        """
    ),
]

SEARCH_SENSOR_USAGE_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Sensor Usage Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===

✅ **WORKING OPERATORS:**
• No operator = equals (default) - ALL FIELDS
• ! = not equal to - ALL FIELDS
• > = greater than - DATE AND INTEGER FIELDS
• >= = greater than or equal - DATE AND INTEGER FIELDS
• < = less than - DATE AND INTEGER FIELDS
• <= = less than or equal - DATE AND INTEGER FIELDS

=== DATA TYPES & SYNTAX ===
• Dates: 'YYYY-MM-DD' (ISO 8601 format)
• Integers: 30 (without quotes)
• Strings: 'value' or ['exact_value'] for exact match

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_sensor_usage FQL filter options ===

""" + generate_md_table(SEARCH_SENSOR_USAGE_FQL_FILTERS) + """

=== ✅ WORKING PATTERNS ===

**Basic Equality:**
• event_date:'2024-06-11'
• period:'30'
• selected_cids:'cid_1,cid_2,cid_3'

**Combined Conditions:**
• event_date:'2024-06-11'+period:'30'
• event_date:'2024-06-11'+selected_cids:'cid_1,cid_2'

**Date Comparisons:**
• event_date:>'2024-01-01'
• event_date:<='2024-06-11'

**Period Comparisons:**
• period:>='14'
• period:<='60'

=== 💡 SYNTAX RULES ===
• Use single quotes around values: 'value'
• Date format must be ISO 8601: 'YYYY-MM-DD'
• Combine conditions with + (AND) or , (OR)
• Use parentheses for grouping: (condition1,condition2)+condition3
"""
