"""
Contains Intel resources.
"""

from falcon_mcp.common.utils import generate_md_table

QUERY_ACTOR_ENTITIES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "Number",
        """
        The adversary's ID.

        Ex: 2583
        """
    ),
    (
        "actor_type",
        "String",
        """
        The type of adversary.

        Ex: "targeted"
        """
    ),
    (
        "actors.id",
        "Number",
        """
        The ID of an associated actor.

        Ex: 1823
        """
    ),
    (
        "actors.name",
        "String",
        """
        The name of an associated actor.

        Ex: "VENOMOUS BEAR"
        """
    ),
    (
        "actors.slug",
        "String",
        """
        The URL-friendly identifier of an associated actor.

        Ex: "venomous-bear"
        """
    ),
    (
        "actors.url",
        "String",
        """
        The URL to the actor's profile page.

        Ex: "https://falcon.crowdstrike.com/intelligence/actors/venomous-bear/"
        """
    ),
    (
        "animal_classifier",
        "String",
        """
        The animal classification assigned to the adversary.

        Ex: "BEAR"
        """
    ),
    (
        "capability.value",
        "String",
        """
        The adversary's capability.

        Ex: "average"
        """
    ),
    (
        "created_date",
        "Timestamp",
        """
        Timestamp when the actor entity was created.

        Ex: 1441729727
        """
    ),
    (
        "description",
        "String",
        """
        A detailed description of the adversary.

        Ex: "VENOMOUS BEAR is a sophisticated Russia-based adversary..."
        """
    ),
    (
        "first_activity_date",
        "Timestamp",
        """
        First activity date.

        Ex: 1094660880
        """
    ),
    (
        "known_as",
        "String",
        """
        The adversary's alias.

        Ex: "dridex"
        """
    ),
    (
        "last_activity_date",
        "Timestamp",
        """
        Last activity date.

        Ex: 1749427200
        """
    ),
    (
        "last_modified_date",
        "Timestamp",
        """
        Timestamp when the actor entity was last modified.

        Ex: 1754320661
        """
    ),
    (
        "motivations.id",
        "Number",
        """
        The ID of a motivation associated with the adversary.

        Ex: 1001485
        """
    ),
    (
        "motivations.slug",
        "String",
        """
        The URL-friendly identifier of a motivation.

        Ex: "state-sponsored"
        """
    ),
    (
        "motivations.value",
        "String",
        """
        The display name of a motivation.

        Ex: "State-Sponsored"
        """
    ),
    (
        "name",
        "String",
        """
        The adversary's name.

        Ex: "FANCY BEAR"
        """
    ),
    (
        "origins.slug",
        "String",
        """
        The adversary's country of origin slug.

        Ex: "ru"
        """
    ),
    (
        "origins.value",
        "String",
        """
        The adversary's country of origin.

        Ex: "Afghanistan"
        """
    ),
    (
        "short_description",
        "String",
        """
        A truncated version of the adversary's description.

        Ex: "VENOMOUS BEAR is a sophisticated Russia-based adversary..."
        """
    ),
    (
        "slug",
        "String",
        """
        The URL-friendly identifier of the adversary.

        Ex: "fancy-bear"
        """
    ),
    (
        "target_countries.id",
        "Number",
        """
        The ID of a target country.

        Ex: 1
        """
    ),
    (
        "target_countries.slug",
        "String",
        """
        The URL-friendly identifier of a target country.

        Ex: "us"
        """
    ),
    (
        "target_countries.value",
        "String",
        """
        The display name of a target country.

        Ex: "United States"
        """
    ),
    (
        "target_industries.id",
        "Number",
        """
        The ID of a target industry.

        Ex: 344
        """
    ),
    (
        "target_industries.slug",
        "String",
        """
        The URL-friendly identifier of a target industry.

        Ex: "government"
        """
    ),
    (
        "target_industries.value",
        "String",
        """
        The display name of a target industry.

        Ex: "Government"
        """
    ),
    (
        "url",
        "String",
        """
        The URL to the adversary's profile page.

        Ex: "https://falcon.crowdstrike.com/intelligence/actors/fancy-bear/"
        """
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
