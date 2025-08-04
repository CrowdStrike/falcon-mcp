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
        "Type",
        "Description"
    ),
    (
        "id",
        "String",
        """
        The indicator ID. It follows the format: {type}_{indicator}
        """
    ),
    (
        "created_date",
        "Timestamp",
        """
        Timestamp in standard Unix time, UTC when the indicator was created.

        Ex: 1753022288
        """
    ),
    (
        "deleted",
        "Boolean",
        """
        If true, include only published indicators.
        If false, include only deleted indicators.

        Ex: false
        """
    ),
    (
        "domain_types",
        "String",
        """
        The domain type of domain indicators.

        Possible values include:
        - ActorControlled
        - DGA
        - DynamicDNS
        - KnownGood
        - LegitimateCompromised
        - PhishingDomain
        - Sinkholed
        - StrategicWebCompromise
        - Unregistered
        """
    ),
    (
        "indicator",
        "String",
        """
        The indicator that was queried.

        Ex: "all-deutsch.gl.at.ply.gg"
        """
    ),
    (
        "ip_address_types",
        "String",
        """
        The address type of ip_address indicators.

        Possible values include:
        - HtranDestinationNode
        - HtranProxy
        - LegitimateCompromised
        - Parking
        - PopularSite
        - SharedWebHost
        - Sinkhole
        - TorProxy
        """
    ),
    (
        "kill_chains",
        "String",
        """
        The point in the kill chain at which an indicator is associated.

        Possible values include:
        - reconnaissance
        - weaponization
        - delivery
        - exploitation
        - installation
        - c2 (Command and Control)
        - actionOnObjectives

        Ex: "delivery"
        """
    ),
    (
        "last_updated",
        "Timestamp",
        """
        Timestamp in standard Unix time, UTC when the indicator was last updated in the internal database.

        Ex: 1753027269
        """
    ),
    (
        "malicious_confidence",
        "String",
        """
        Indicates a confidence level by which an indicator is considered to be malicious.

        Possible values:
        - high: If indicator is an IP or domain, it has been associated with malicious activity within the last 60 days.
        - medium: If indicator is an IP or domain, it has been associated with malicious activity within the last 60-120 days.
        - low: If indicator is an IP or domain, it has been associated with malicious activity exceeding 120 days.
        - unverified: This indicator has not been verified by a CrowdStrike Intelligence analyst or an automated system.

        Ex: "high"
        """
    ),
    (
        "malware_families",
        "String",
        """
        Indicates the malware family an indicator has been associated with. An indicator might be associated with more than one malware family.

        Ex: "Xworm", "njRATLime"
        """
    ),
    (
        "published_date",
        "Timestamp",
        """
        Timestamp in standard Unix time, UTC when the indicator was first published to the API.

        Ex: 1753022288
        """
    ),
    (
        "reports",
        "String",
        """
        The report ID that the indicator is associated with (such as CSIT-XXXX or CSIR-XXXX).
        The report list is also represented under the labels list in the JSON data structure.
        """
    ),
    (
        "targets",
        "String",
        """
        The indicators targeted industries.

        Possible values include sectors like:
        - Aerospace
        - Agricultural
        - Chemical
        - Defense
        - Dissident
        - Energy
        - Financial
        - Government
        - Healthcare
        - Technology
        """
    ),
    (
        "threat_types",
        "String",
        """
        Types of threats.

        Ex: "ddos", "mineware", "banking"
        """
    ),
    (
        "type",
        "String",
        """
        Possible indicator types include:
        - binary_string
        - compile_time
        - device_name
        - domain
        - email_address
        - email_subject
        - event_name
        - file_mapping
        - file_name
        - file_path
        - hash_ion
        - hash_md5
        - hash_sha256
        - ip_address
        - ip_address_block
        - mutex_name
        - password
        - persona_name
        - phone_number
        - port
        - registry
        - semaphore_name
        - service_name
        - url
        - user_agent
        - username
        - x509_seria
        - x509_subject

        Ex: "domain"
        """
    ),
    (
        "vulnerabilities",
        "String",
        """
        Associated vulnerabilities (CVEs).

        Ex: "CVE-2023-1234"
        """
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
        "Type",
        "Description",
    ),
    (
        "id",
        "Number",
        """
        The report's ID.

        Ex: 2583
        """
    ),
    (
        "actors",
        "String",
        """
        Names of adversaries included in a report.

        Ex: "FANCY BEAR"
        """
    ),
    (
        "created_date",
        "Timestamp",
        """
        Timestamp in Unix epoch format when the report was created.

        Ex: 1754075803
        """
    ),
    (
        "description",
        "String",
        """
        A detailed description of the report.

        Ex: "In mid-July 2025, CrowdStrike Intelligence identified infrastructure..."
        """
    ),
    (
        "last_modified_date",
        "Timestamp",
        """
        Timestamp in Unix epoch format when the report was last modified.

        Ex: 1754076191
        """
    ),
    (
        "motivations.value",
        "String",
        """
        Motivations included in the report.

        Ex: "Criminal", "State-Sponsored"
        """
    ),
    (
        "name",
        "String",
        """
        The report's name.

        Ex: "CSA-250861 Newly Identified HAYWIRE KITTEN Infrastructure Associated with Microsoft Phishing Campaign"
        """
    ),
    (
        "type",
        "String",
        """
        The type of report.

        Ex: "notice", "tipper", "periodic-report"
        """
    ),
    (
        "short_description",
        "String",
        """
        A truncated version of the report's description.

        Ex: "Adversary: HAYWIRE KITTEN || Target Industry: Technology, Renewable Energy..."
        """
    ),
    (
        "slug",
        "String",
        """
        The URL-friendly identifier of the report.

        Ex: "csa-250861", "csit-25151"
        """
    ),
    (
        "sub_type",
        "String",
        """
        The subtype of the report.

        Ex: "daily", "yara"
        """
    ),
    (
        "tags",
        "String",
        """
        The report's tags.

        Ex: "ransomware", "espionage", "vulnerabilities"
        """
    ),
    (
        "target_countries",
        "String",
        """
        Targeted countries included in the report.

        Ex: "United States", "Taiwan", "Western Europe"
        """
    ),
    (
        "target_industries",
        "String",
        """
        Targeted industries included in the report.

        Ex: "Technology", "Government", "Healthcare"
        """
    ),
    (
        "url",
        "String",
        """
        The URL to the report's page.

        Ex: "https://falcon.crowdstrike.com/intelligence/reports/csa-250861"
        """
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
