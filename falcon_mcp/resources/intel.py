"""
Contains Intel resources.
"""

from falcon_mcp.common.utils import generate_md_table

QUERY_ACTOR_ENTITIES_FQL_FILTERS = [
    (
        "Name",
    ),
    (
        "actors",
    ),
    (
        "actors.id",
    ),
    (
        "actors.name",
    ),
    (
        "actors.slug",
    ),
    (
        "actors.url",
    ),
    (
        "animal_classifier",
    ),
    (
        "created_date",
    ),
    (
        "description",
    ),
    (
        "id",
    ),
    (
        "last_modified_date",
    ),
    (
        "motivations",
    ),
    (
        "motivations.id",
    ),
    (
        "motivations.slug",
    ),
    (
        "motivations.value",
    ),
    (
        "name",
    ),
    (
        "name.raw",
    ),
    (
        "origins",
    ),
    (
        "short_description",
    ),
    (
        "slug",
    ),
    (
        "sub_type",
    ),
    (
        "sub_type.id",
    ),
    (
        "sub_type.name",
    ),
    (
        "sub_type.slug",
    ),
    (
        "tags",
    ),
    (
        "tags.id",
    ),
    (
        "tags.slug",
    ),
    (
        "tags.value",
    ),
    (
        "target_countries",
    ),
    (
        "target_countries.id",
    ),
    (
        "target_countries.slug",
    ),
    (
        "target_countries.value",
    ),
    (
        "target_industries",
    ),
    (
        "target_industries.id",
    ),
    (
        "target_industries.slug",
    ),
    (
        "target_industries.value",
    ),
    (
        "type",
    ),
    (
        "type.id",
    ),
    (
        "type.name",
    ),
    (
        "type.slug",
    ),
    (
        "url",
    ),
]

QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Intel Query Actor Entities Guide

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
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '_partial_'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_actors FQL filter options ===

""" + generate_md_table(QUERY_ACTOR_ENTITIES_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• animal_classifier:'BEAR'
• name:'FANCY BEAR'
• animal_classifier:'BEAR',animal_classifier:'SPIDER'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""

QUERY_INDICATOR_ENTITIES_FQL_FILTERS = [
    (
        "Name",
    ),
    (
        "created_date",
    ),
    (
        "deleted",
    ),
    (
        "domain_types",
    ),
    (
        "id",
    ),
    (
        "indicator",
    ),
    (
        "ip_address_types",
    ),
    (
        "kill_chains",
    ),
    (
        "labels",
    ),
    (
        "last_updated",
    ),
    (
        "malicious_confidence",
    ),
    (
        "malware_families",
    ),
    (
        "published_date",
    ),
    (
        "reports",
    ),
    (
        "source",
    ),
    (
        "targets",
    ),
    (
        "threat_types",
    ),
    (
        "type",
    ),
    (
        "vulnerabilities",
    ),
]

QUERY_INDICATOR_ENTITIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Intel Query Indicator Entities Guide

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
• * = wildcard matching (one or more characters)

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

=== falcon_search_indicators FQL filter options ===

""" + generate_md_table(QUERY_INDICATOR_ENTITIES_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• type:'domain'
• malicious_confidence:'high'
• type:'hash_md5'+malicious_confidence:'high'
• created_date:>'2023-01-01T00:00:00Z'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""


QUERY_REPORT_ENTITIES_FQL_FILTERS = [
    (
        "Name",
    ),
    (
        "actors",
    ),
    (
        "created_date",
    ),
    (
        "description",
    ),
    (
        "id",
    ),
    (
        "last_modified_date",
    ),
    (
        "name",
    ),
    (
        "report_type",
    ),
    (
        "short_description",
    ),
    (
        "slug",
    ),
    (
        "tags",
    ),
    (
        "target_countries",
    ),
    (
        "target_industries",
    ),
    (
        "url",
    ),
]

QUERY_REPORT_ENTITIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Intel Query Report Entities Guide

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
• * = wildcard matching (one or more characters)

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

=== falcon_search_reports FQL filter options ===

""" + generate_md_table(QUERY_REPORT_ENTITIES_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• report_type:'malware'
• name:'*ransomware*'
• created_date:>'2023-01-01T00:00:00Z'
• target_industries:'healthcare'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""
