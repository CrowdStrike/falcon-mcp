"""
Contains Data Connectors resources.
"""

from falcon_mcp.common.utils import generate_md_table

# FQL filter fields for searching data connections
SEARCH_DATA_CONNECTIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        r"""
        Connection name. Supports exact match or case-insensitive glob with * wildcard.
        Note: ~* is NOT supported for this field; use * for wildcard matching.
        Ex (exact): name:'My Okta Connection'
        Ex (wildcard): name:*'*okta*'
        """,
    ),
    (
        "status",
        "String",
        """
        Connection status. Values are title-case — lowercase will be rejected by the API.
        Possible values: Active, Idle, Disconnected, Paused, Pending, Error
        Ex: status:'Active'
        """,
    ),
    (
        "vendor_name",
        "String",
        """
        Vendor or provider name. Exact match only (case-sensitive). Wildcard is NOT supported.
        Ex: vendor_name:'Microsoft'
        """,
    ),
    (
        "vendor_product_name",
        "String",
        """
        Vendor product name. Exact match only (case-sensitive).
        Ex: vendor_product_name:'Okta Identity'
        """,
    ),
]

SEARCH_DATA_CONNECTIONS_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Data Connections Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value' (exact match, case-sensitive)
• *: field_name:*'*term*' (glob/wildcard match, case-insensitive) — supported on name only
• !: field_name:!'value' (not equal)

NOTE: ~* (case-insensitive glob) is NOT supported by this endpoint. Use * instead for name.

=== COMBINING ===
• + = AND: status:'Active'+vendor_name:'Microsoft'
• , = OR: status:'Active',status:'Idle'

=== CONNECTION STATUS VALUES (title-case required) ===
• Active: Receiving data with no errors in the last hour
• Idle: No data received in the last hour
• Disconnected: Connection is down
• Paused: Connection is paused
• Pending: Configuration not yet completed
• Error: Encountered errors in the last hour

=== falcon_search_data_connections FQL filter available fields ===

"""
    + generate_md_table(SEARCH_DATA_CONNECTIONS_FQL_FILTERS)
    + r"""

=== FILTER EXAMPLES ===

# All active connections
status:'Active'

# Connections with errors or disconnected
status:'Error',status:'Disconnected'

# Connections from a specific vendor (exact match required)
vendor_name:'Microsoft'

# Find connections by name keyword (wildcard)
name:*'*okta*'

# Active connections from Microsoft
status:'Active'+vendor_name:'Microsoft'
"""
)

# FQL filter fields for searching available data connectors (catalog)
SEARCH_DATA_CONNECTORS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        """
        Connector name. Use ~* with * wildcards for case-insensitive substring matching.
        Ex: name:~*'*aws*'
        """,
    ),
    (
        "vendor",
        "String",
        """
        Vendor or provider name.
        Ex: vendor:~*'*microsoft*'
        """,
    ),
    (
        "connector_type",
        "String",
        """
        Ingestion type. Possible values: push, pull.
        Ex: connector_type:'pull'
        """,
    ),
]

SEARCH_DATA_CONNECTORS_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Available Data Connectors Guide

=== PURPOSE ===
Use this to discover what data connector types are available in the Falcon catalog.
These are the connector templates, not active connections.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value' (exact match, case-sensitive)
• ~*: field_name:~*'*term*' (glob/wildcard match, case-insensitive)

=== COMBINING ===
• + = AND: vendor:~*'*aws*'+connector_type:'pull'
• , = OR: vendor:~*'*microsoft*',vendor:~*'*google*'

=== falcon_search_data_connectors FQL filter available fields ===

"""
    + generate_md_table(SEARCH_DATA_CONNECTORS_FQL_FILTERS)
    + """

=== FILTER EXAMPLES ===

# All AWS connectors
vendor:~*'*aws*'

# All push-based connectors
connector_type:'push'

# Microsoft connectors
vendor:~*'*microsoft*'

# Find connector by name
name:~*'*cloudtrail*'
"""
)

# Data source mapping guide — cross-module intelligence
DATA_SOURCE_MAPPING_GUIDE = r"""Data Source Mapping Guide — Correlation Rules & Data Connectors

=== PURPOSE ===
Use this guide to cross-reference correlation rule templates with data connectors
to answer questions like:
  - "What correlation rules can I enable with my current data?"
  - "What data do I need to onboard for this correlation rule to work?"

=== KEY CONCEPT: THE VENDORS FIELD ===
Every correlation rule template has a `vendors` field listing which data sources
it needs. This is the JOIN KEY between templates and data connectors.

  Template vendors field  ↔  Connector/Connection vendor_name

=== FALCON SENSOR DATA IS ALWAYS AVAILABLE ===
Templates with vendors: ['CrowdStrike'] use native Falcon sensor data.
NO data connector is needed — this data is always present in every Falcon deployment.

Falcon native data repos in CQL queries:
  • #repo="base_sensor" — EDR telemetry (ProcessRollup2, NetworkConnect, DnsRequest,
    FileWrite, RegistryOperations, UserLogon, etc.)
  • #repo="aidr" — CrowdStrike AI/ML detection events (AIDR prompt analysis,
    anomaly detection, secret exposure)
  • #repo="detections" — Falcon detection alerts
  • #repo="xdr_indicatorsrepo" — XDR indicator matches

CQL vendor tag: #Vendor="crowdstrike" also indicates native Falcon data.

=== THIRD-PARTY DATA REQUIRES A CONNECTOR ===
Any vendor in the template's vendors list OTHER THAN "CrowdStrike" requires an
active data connector. Common examples:
  • vendors: ['Microsoft'] — needs a Microsoft connector (Entra ID, Defender XDR, etc.)
  • vendors: ['Okta'] — needs the Okta Identity connector
  • vendors: ['Zscaler'] — needs a Zscaler connector (ZIA, ZPA)
  • vendors: ['Microsoft', 'Zscaler'] — needs BOTH vendors connected

The CQL #Vendor= tag in the rule's query maps to the connector's vendor_name:
  • #Vendor="microsoft" → vendor_name contains "Microsoft"
  • #Vendor="okta" → vendor_name contains "Okta"
  • #Vendor="zscaler" → vendor_name contains "Zscaler"
  • #Vendor="aws" → vendor_name contains "AmazonWebServices"
  • #Vendor="google" → vendor_name contains "Google"
  • #Vendor="paloalto" → vendor_name contains "Palo Alto Networks"
  • #Vendor="fortinet" → vendor_name contains "Fortinet"
  • #Vendor="cisco" → vendor_name contains "Cisco"

=== WORKFLOW: "What rules can I enable with my current data?" ===
1. Call falcon_search_data_connections to list active connections
2. Collect the vendor_name values from results (these are your available vendors)
3. Add "CrowdStrike" to the set (always available)
4. Call falcon_search_correlation_rule_templates
5. For each template: check if ALL entries in its vendors list are in your
   available vendor set. If yes → you can enable it.
6. Templates with vendors: ['CrowdStrike'] are ALWAYS enableable.

=== WORKFLOW: "What data do I need for this rule?" ===
1. Get the correlation rule template — read its vendors field
2. Remove "CrowdStrike" from the list (already available)
3. Remaining vendors = connectors you need to onboard
4. For each needed vendor: call falcon_search_data_connectors with
   vendor:~*'*<vendor_name>*' to find the right connector to set up
5. If no vendors remain after removing CrowdStrike → the rule works out of
   the box with native Falcon sensor data

=== TEMPLATE VENDOR DISTRIBUTION (for context) ===
Across ~1600+ available templates:
  • ~220 use CrowdStrike-only data (native sensor, always available)
  • ~1370 require one or more third-party data connectors
  • ~36 use a mix of CrowdStrike + third-party data
"""

# Troubleshooting guide resource
DATA_CONNECTORS_TROUBLESHOOTING_GUIDE = r"""Data Connectors Troubleshooting Guide

=== CONNECTION STATUS MEANINGS ===

• Active: Receiving data with no errors (received data within the last hour)
• Idle: No data received in the last hour based on event timestamp
• Disconnected: Connection is down, data is not being ingested
• Paused: Connection paused by user — cannot ingest or receive data
• Pending: Configuration still in progress / not completed
• Error: Encountered an error in the last hour — must successfully ingest
  without errors for an hour to return to Active

=== COMMON ISSUES ===

1. Status: Error
   - Check error history using falcon_get_data_connection to review details
   - Common causes:
     * Invalid credentials or permissions on the third-party system
     * API key expired or revoked
     * Third-party system configuration changed
   - For push connectors: verify API key is correct, regenerate if needed
   - For pull connectors: verify data source configuration credentials

2. Status: Idle (no data in 24h)
   - The connector is configured but no events are flowing
   - Check if the third-party system is generating events
   - For push connectors: verify the data shipper is running and configured
     with the correct API URL and key
   - For pull connectors: check that the source has data in the lookback period

3. Status: Disconnected
   - Connection is fully down
   - Re-check all connection settings and third-party credentials
   - Consider deleting and re-creating the connection

4. Push connector HTTP errors:
   - 400: Invalid data format or no data in payload
   - 401: Invalid API key — regenerate using falcon_regenerate_data_connection_token
   - 403: Authorization token incorrect, connection deleted/paused, or invalid ID
   - 413: Payload exceeds size limit (32MB for most endpoints, 999KB for Humio Raw)
   - 429: Rate limited — wait and retry

=== PUSH CONNECTOR BEST PRACTICES ===
• Batch multiple events per request (up to 32MB payload)
• Use gzip or Deflate compression
• Set request timeout to 35 seconds
• Add Uncompressed-Content-Length header to fail fast on oversized payloads

=== INVESTIGATION WORKFLOW ===
1. List connections: falcon_search_data_connections (filter by status:'Error')
2. Get details: falcon_get_data_connection with the connection ID
3. For push connectors with auth issues: falcon_regenerate_data_connection_token
4. For persistent issues: review connection configuration and third-party settings
"""
