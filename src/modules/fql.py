"""
FQL module for Falcon MCP Server

This module provides resources for FQL.
"""
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from ..common.logging import get_logger
from .base import BaseModule

logger = get_logger(__name__)


asdasd = """Falcon Query Language (FQL)

Many of the CrowdStrike Falcon API endpoints support the use of Falcon Query Language (FQL) syntax to select and sort records or filter results.

Standard FQL expression syntax follows the pattern: `<property>:[operator]<value>` when filtering or selecting records.

Standard syntax for a FQL sort expression is: `sort:<property>.<direction>`.

> **WARNING**
>
> `client_id` and `client_secret` are keyword arguments that contain your CrowdStrike API credentials. Please note that all examples below do not hard code these values. (These values are ingested as strings.)
>
> CrowdStrike does ***NOT*** recommend hard coding API credentials or customer identifiers within source code.

## Properties

Properties are the elements within CrowdStrike Falcon data that you use to filter, select and sort.
Properties always contain only alphanumeric characters or underscores (`_`).
The first character in a property is always a letter, and properties are always considered lowercase.
(Uppercase submissions are accepted and converted.)
Some names for complex properties are separated by periods, such as `author.name` or `posts.count`.

## Data types and restrictions

FQL syntax is typically case sensitive for both property keys and values.
Most properties allowed within a FQL statement are either `boolean`, `integer`, `string` or `null` data types.
A FQL statement can have a maximum of 20 properties defined.

## Operators

By default, an expression passed within a FQL statement's operator is **equal to**.
As an example, `platform_name:'windows'` would filter on hosts where the attribute *platform_name* is
equal to *windows*.

FQL supports the following operators, although not all may make sense to the query you are trying to perform.

> Note: Available FQL filters and their syntax may vary between API service collection.

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

🚨 DETECTION PROPERTIES (Complete List):

=== IDENTIFICATION & CORE ===
• composite_id: Unique detection identifier
• aggregate_id: Related detection group identifier
• cid: Customer ID
• agent_id: Falcon agent identifier
• pattern_id: Detection pattern identifier

=== ASSIGNMENT & WORKFLOW ===
• assigned_to_name: Person assigned to this detection
• assigned_to_uid: Assigned user identifier
• assigned_to_uuid: Assigned user UUID
• status: Detection status (new, in_progress, closed, reopened)

=== TIMESTAMPS ===
• created_timestamp: When detection was created
• updated_timestamp: Last modification time
• timestamp: Detection occurrence timestamp

=== THREAT INTELLIGENCE ===
• confidence: Confidence level (1-100)
• severity: Detection severity level
• tactic: MITRE ATT&CK tactic
• tactic_id: MITRE ATT&CK tactic ID
• technique: MITRE ATT&CK technique
• technique_id: MITRE ATT&CK technique ID
• objective: Attack objective description

=== DETECTION METADATA ===
• name: Detection name/title
• display_name: Human-readable detection name
• description: Detection description
• type: Detection type classification
• scenario: Detection scenario

=== SYSTEM & PLATFORM ===
• platform: Operating system platform
• show_in_ui: Whether detection appears in UI (true/false)
• data_domains: Data classification domains

=== PRODUCT FILTERING ===
• product: Source Falcon product
    - 'epp' (Endpoint Protection)
    - 'idp' (Identity Protection)
    - 'mobile' (Falcon for Mobile)
    - 'xdr' (Falcon XDR)
    - 'overwatch' (OverWatch)
    - 'cwpp' (Cloud Workload Protection)
    - 'ngsiem' (Next-Gen SIEM)
    - 'thirdparty' (Third party data)
    - 'data-protection' (Data Protection)

=== SOURCE INFORMATION ===
• source_products: Products that generated this detection
• source_vendors: Vendor sources for the detection

=== TAGS & CLASSIFICATION ===
• tags: Detection classification tags

💡 PRACTICAL DETECTION SEARCH EXAMPLES:

=== STATUS-BASED SEARCHES ===
Find new detections:
status:'new'

Find detections in progress:
status:'in_progress'

Find closed detections:
status:'closed'

Find reopened detections:
status:'reopened'

=== PRODUCT-SPECIFIC SEARCHES ===
Find endpoint protection detections:
product:'epp'

Find identity protection detections:
product:'idp'

Find XDR detections:
product:'xdr'

Find OverWatch detections:
product:'overwatch'

=== SEVERITY & CONFIDENCE SEARCHES ===
Find high confidence detections:
confidence:>80

Find medium to high confidence:
confidence:>=50

🔥 SEVERITY NUMERIC MAPPING (Critical for Proper Filtering):
Based on CrowdStrike Falcon API data:
• Critical: severity:>=90 (or severity:90 exactly)
• High: severity:>=70 (or severity:70 exactly)
• Medium: severity:>=50 (or severity:50 exactly)
• Low: severity:>=20 (covers range 20-40)
• Informational: severity:<=10 (covers range 2-5)

Find critical severity detections only:
severity:>=90

Find high severity detections (includes critical):
severity:>=70

Find medium severity and above (includes high & critical):
severity:>=50

Find high severity detections only (excludes critical):
severity:70

Find informational detections:
severity:<=10

=== ASSIGNMENT SEARCHES ===
Find unassigned detections:
assigned_to_name:!*

Find detections assigned to specific analyst:
assigned_to_name:'john.doe'

=== TIME-BASED SEARCHES ===
Find recent detections (last 24 hours):
created_timestamp:>'2024-01-20T00:00:00Z'

Find detections from specific date range:
created_timestamp:>='2024-01-15T00:00:00Z'+created_timestamp:<='2024-01-20T00:00:00Z'

Find recently updated detections:
updated_timestamp:>'2024-01-19T00:00:00Z'

=== THREAT INTELLIGENCE SEARCHES ===
Find detections with specific tactic:
tactic:'Persistence'

Find detections with technique ID:
technique_id:'T1055'

Find detections with specific objective:
objective:'*credential*'

=== ADVANCED COMBINED SEARCHES ===
Find new high-confidence endpoint detections:
status:'new'+confidence:>75+product:'epp'

Find assigned XDR detections that are in progress:
product:'xdr'+status:'in_progress'+assigned_to_name:*

Find recent high-severity unassigned detections:
created_timestamp:>'2024-01-18T00:00:00Z'+assigned_to_name:!*+confidence:>80

Find OverWatch detections with persistence tactics:
product:'overwatch'+tactic:'Persistence'

=== BULK FILTERING SEARCHES ===
Find detections from multiple products:
(product:'epp'),(product:'xdr'),(product:'idp')

Find detections in various active states:
(status:'new'),(status:'in_progress')

Find detections needing attention (new or reopened):
(status:'new'),(status:'reopened')

=== INVESTIGATION-FOCUSED SEARCHES ===
Find detections with specific pattern:
pattern_id:'12345'

Find related detections by aggregate:
aggregate_id:'agg-67890'

Find detections with specific tags:
tags:'malware'

Find detections that show in UI:
show_in_ui:true

🚀 USAGE EXAMPLES:

# Find new endpoint protection detections sorted by severity
search_detections("status:'new'+product:'epp'", limit=50, sort="severity.desc")

# Find high-confidence XDR detections from last week
search_detections("product:'xdr'+confidence:>80+created_timestamp:>'2024-01-15T00:00:00Z'", limit=25)

# Find unassigned detections across all products
search_detections("assigned_to_name:!*", limit=100, sort="timestamp.desc")

# Find OverWatch detections with specific tactics
search_detections("product:'overwatch'+tactic:'Initial Access'", limit=50)

# Find detections that need immediate attention
search_detections("(status:'new'),(status:'reopened')+confidence:>75", sort="timestamp.desc")

⚠️ IMPORTANT NOTES:
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Status values are: new, in_progress, closed, reopened
• Product filtering enables product-specific detection analysis
• Confidence values range from 1-100
• Complex queries may take longer to execute
• include_hidden parameter shows previously hidden detections

Returns:
    List of detection details
"""


class FqlModule(BaseModule):
    """This module provides resources for FQL."""

    def register_tools(self, server: FastMCP) -> None:
        pass

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.
        Args:
            server: MCP server instance
        """

        basic_resource = TextResource(
            uri=AnyUrl("resource://fql_syntax"),
            name="fql_syntax",
            description=asdasd,
            text=asdasd,
        )

        self._add_resource(server, basic_resource)
