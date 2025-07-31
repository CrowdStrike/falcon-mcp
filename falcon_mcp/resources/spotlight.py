"""
Contains Spotlight Vulnerabilities resources.
"""

from falcon_mcp.common.utils import generate_table

# List of tuples containing filter options data: (name, type, operators, description)
SEARCH_VULNERABILITIES_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    ("aid", "String", "No", "Unique agent identifier (AID) of the sensor where the vulnerability was found. For assets without a Falcon sensor installed, this field matches the asset ID field.\nEx: aid:'abcde6b9a3427d8c4a1af416424d6231'"),
    ("apps.remediation.ids", "String", "Yes", "Unique identifier of a remediation. Supports multiple values and negation.\nEx: apps.remediation.ids:'7bba2e543744a92962be7afeb6484858'\nEx: apps.remediation.ids:['ID1','ID2','ID3']"),
    ("cid", "String", "No", "Unique system-generated customer identifier (CID) of the account. In multi-CID environments, you can filter by both parent and child CIDs.\nEx: cid:'0123456789ABCDEFGHIJKLMNOPQRSTUV'"),
    ("closed_timestamp", "Timestamp", "Yes", "Date and time a vulnerability was set to a status of CLOSED.\nEx: closed_timestamp:>'2021-06-25T10:32'\nEx: closed_timestamp:<'2021-10-18'"),
    ("confidence", "String", "Yes", "Whether or not the vulnerability has been confirmed.\nValues: confirmed, potential\nEx: confidence:'potential'"),
    ("created_timestamp", "Timestamp", "Yes", "Date and time when this vulnerability was found in your environment. Use this to get vulnerabilities created after the timestamp you last pulled data on.\nEx: created_timestamp:<'2021-09-25T13:22'\nEx: created_timestamp:>'2021-02-12'"),
    ("cve.base_score", "Number", "Yes", "CVE base score.\nEx: cve.base_score:>5.0"),
    ("cve.cwes", "String", "Yes", "Unique identifier for a vulnerability from the Common Weakness Enumeration (CWE) list.\nEx: cve.cwes:['CWE-787','CWE-699']"),
    ("cve.exploit_status", "String", "Yes", "Numeric value of the most severe known exploit. Supports multiple values and negation.\nValues: 0=Unproven, 30=Available, 60=Easily accessible, 90=Actively used\nEx: cve.exploit_status:'60'\nEx: cve.exploit_status:!'0'"),
    ("cve.exprt_rating", "String", "Yes", "ExPRT rating assigned by CrowdStrike's predictive AI rating system. Value must be in all caps. Supports multiple values and negation.\nValues: UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL\nEx: cve.exprt_rating:'HIGH'\nEx: cve.exprt_rating:['HIGH','CRITICAL']"),
    ("cve.id", "String", "Yes", "Unique identifier for a vulnerability as cataloged in the National Vulnerability Database (NVD). Supports multiple values and negation. For case-insensitive filtering, add .insensitive to the field name.\nNote: All values must be enclosed in brackets.\nEx: cve.id:['CVE-2022-1234']\nEx: cve.id:['CVE-2022-1234','CVE-2023-1234']"),
    ("cve.is_cisa_kev", "Boolean", "Yes", "Filter for vulnerabilities that are in the CISA Known Exploited Vulnerabilities (KEV) catalog. Supports negation.\nEx: cve.is_cisa_kev:true"),
    ("cve.remediation_level", "String", "Yes", "CVSS remediation level of the vulnerability. Supports multiple values and negation.\nEx: cve.remediation_level:'O' (official fix)\nEx: cve.remediation_level:'U' (no available fix)"),
    ("cve.severity", "String", "Yes", "CVSS severity rating of the vulnerability. Value must be in all caps. Supports multiple values and negation.\nValues: UNKNOWN, NONE, LOW, MEDIUM, HIGH, CRITICAL\nEx: cve.severity:'LOW'\nEx: cve.severity:!'UNKNOWN'"),
    ("cve.types", "String", "Yes", "Vulnerability type.\nValues: Vulnerability, Misconfiguration, Unsupported software\nEx: cve.types:!'Misconfiguration'"),
    ("data_providers.ports", "String", "Yes", "Ports on the host where the vulnerability was found by the third-party provider.\nEx: data_providers.ports:'53'\nEx: data_providers.ports:!'0' (any port)"),
    ("data_providers.provider", "String", "No", "Name of the data provider.\nEx: data_providers.provider:'{provider name}'"),
    ("data_providers.rating", "String", "Yes", "Third-party provider rating.\nValues: UNKNOWN, NONE, LOW, MEDIUM, HIGH, CRITICAL\nEx: data_providers.rating:'CRITICAL'"),
    ("data_providers.scan_time", "Timestamp", "Yes", "UTC date and time when the vulnerability was most recently identified by the third-party provider.\nEx: data_providers.scan_time:>'2023-08-03'"),
    ("data_providers.scanner_id", "String", "No", "ID of the third-party scanner that identified the vulnerability.\nEx: data_providers.scanner_id:'{scanner id}'"),
    ("host_info.asset_criticality", "String", "Yes", "Assigned criticality level of the asset.\nValues: Critical, High, Noncritical, Unassigned\nEx: host_info.asset_criticality:['Critical','High']\nEx: host_info.asset_criticality:!'Unassigned'"),
    ("host_info.groups", "String", "Yes", "Unique system-assigned ID of a host group. Supports multiple values and negation. All values must be enclosed in brackets.\nEx: host_info.groups:['03f0b54af2692e99c4cec945818fbef7']\nEx: host_info.groups:!['03f0b54af2692e99c4cec945818fbef7']"),
    ("host_info.has_run_container", "Boolean", "No", "Whether or not the host is running Kubernetes containers.\nEx: host_info.has_run_container:true"),
    ("host_info.internet_exposure", "String", "No", "Whether or not the asset is internet-facing.\nValues: Yes, No, Pending\nEx: host_info.internet_exposure:'Yes'"),
    ("host_info.managed_by", "String", "Yes", "Indicates if the asset has the Falcon sensor installed.\nValues: Falcon sensor, Unmanaged\nSupports multiple values and negation.\nEx: host_info.managed_by:'Unmanaged'"),
    ("host_info.platform_name", "String", "Yes", "Operating system platform. Supports negation.\nValues: Windows, Mac, Linux\nEx: host_info.platform_name:'Windows'\nEx: host_info.platform_name:!'Linux'"),
    ("host_info.product_type_desc", "String", "Yes", "Type of host a sensor is running on. Supports multiple values and negation. For case-insensitive filtering, add .insensitive to the field name. Enter values with first letter capitalized.\nValues: Workstation, Server, Domain Controller\nEx: host_info.product_type_desc:'Workstation'\nEx: host_info.product_type_desc:!'Workstation'"),
    ("host_info.tags", "String", "Yes", "Name of a tag assigned to a host. Supports multiple values and negation. All values must be enclosed in brackets.\nEx: host_info.tags:['ephemeral']\nEx: host_info.tags:!['search','ephemeral']"),
    ("host_info.third_party_asset_ids", "String", "Yes", "Asset IDs assigned to the host by third-party providers in the format: {data_provider}: {data_provider_asset_id}\nSupports multiple values and negation.\nEx: host_info.third_party_asset_ids:'{provider}: {asset_id}'"),
    ("last_seen_within", "Number", "No", "Filter for vulnerabilities based on the number of days since a host last connected to Falcon. Enter a numeric value from 3 to 45 to indicate the number of days to look back.\nEx: last_seen_within:'10'"),
    ("services.port", "String", "No", "Port on the host where a vulnerability was found by Falcon EASM or a third-party provider.\nEx: services.port:'443'"),
    ("services.protocol", "String", "No", "Network protocols recognized by Falcon EASM.\nEx: services.protocol:'pop3'"),
    ("services.transport", "String", "No", "Transport methods recognized by Falcon EASM.\nEx: services.transport:'tcp'"),
    ("status", "String", "Yes", "Status of a vulnerability. Value must be in all lowercase letters. Supports multiple values and negation.\nValues: open, closed, reopen, expired\nEx: status:'open'\nEx: status:!'closed'\nEx: status:['open','reopen']"),
    ("suppression_info.is_suppressed", "Boolean", "No", "Indicates if the vulnerability is suppressed by a suppression rule or not.\nEx: suppression_info.is_suppressed:true"),
    ("suppression_info.reason", "String", "Yes", "Attribute assigned to a suppression rule. Supports multiple values and negation. All values must be enclosed in brackets.\nValues: ACCEPT_RISK, COMPENSATING_CONTROL, FALSE_POSITIVE\nEx: suppression_info.reason:['ACCEPT_RISK']\nEx: suppression_info.reason:!['FALSE_POSITIVE']"),
    ("updated_timestamp", "Timestamp", "Yes", "UTC date and time of the last update made on a vulnerability.\nEx: updated_timestamp:<'2021-10-20T22:36'\nEx: updated_timestamp:>'2021-09-15'"),
    ("vulnerability_id", "String", "Yes", "CVE ID of the vulnerability. If there's no CVE ID, this is the CrowdStrike or third-party ID of the vulnerability.\nFor case-insensitive filtering, add .insensitive to the field name. Supports multiple values and negation.\nEx: vulnerability_id:['CVE-2022-1234']\nEx: vulnerability_id:['CVE-2022-1234','CVE-2023-4321']"),
]

SEARCH_VULNERABILITIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Vulnerabilities Guide

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
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== falcon_search_vulnerabilities FQL filter options ===

""" + generate_table(SEARCH_VULNERABILITIES_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches and multiple values: ['value1','value2']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• For case-insensitive filtering, add .insensitive to field names
• Boolean values: true or false (no quotes)
• Wildcards (*) are unsupported in this API
• Some fields require specific capitalization (check individual field descriptions)

=== COMMON FILTER EXAMPLES ===
• High severity vulnerabilities: cve.severity:'HIGH'
• Recent vulnerabilities: created_timestamp:>'2024-01-01'
• Windows vulnerabilities: host_info.platform_name:'Windows'
• Open vulnerabilities with exploits: status:'open'+cve.exploit_status:!'0'
• Critical ExPRT rated vulnerabilities: cve.exprt_rating:'CRITICAL'
• CISA KEV vulnerabilities: cve.is_cisa_kev:true
"""
