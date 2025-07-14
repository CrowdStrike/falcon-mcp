"""
Contains Spotlight Vulnerabilities resources.
"""

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

+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| Name                             | Type                      | Operators| Description                                                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| aid                              | String                    | No       | Unique agent identifier (AID) of the sensor where the           |
|                                  |                           |          | vulnerability was found. For assets without a Falcon sensor     |
|                                  |                           |          | installed, this field matches the asset ID field.               |
|                                  |                           |          | Ex: aid:'abcde6b9a3427d8c4a1af416424d6231'                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| apps.remediation.ids             | String                    | Yes      | Unique identifier of a remediation. Supports multiple values     |
|                                  |                           |          | and negation.                                                    |
|                                  |                           |          | Ex: apps.remediation.ids:'7bba2e543744a92962be7afeb6484858'      |
|                                  |                           |          | Ex: apps.remediation.ids:['ID1','ID2','ID3']                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cid                              | String                    | No       | Unique system-generated customer identifier (CID) of the        |
|                                  |                           |          | account. In multi-CID environments, you can filter by both      |
|                                  |                           |          | parent and child CIDs.                                           |
|                                  |                           |          | Ex: cid:'0123456789ABCDEFGHIJKLMNOPQRSTUV'                       |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| closed_timestamp                 | Timestamp                 | Yes      | Date and time a vulnerability was set to a status of CLOSED.    |
|                                  |                           |          | Ex: closed_timestamp:>'2021-06-25T10:32'                        |
|                                  |                           |          | Ex: closed_timestamp:<'2021-10-18'                              |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| confidence                       | String                    | Yes      | Whether or not the vulnerability has been confirmed.             |
|                                  |                           |          | Values: confirmed, potential                                     |
|                                  |                           |          | Ex: confidence:'potential'                                       |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| created_timestamp                | Timestamp                 | Yes      | Date and time when this vulnerability was found in your          |
|                                  |                           |          | environment. Use this to get vulnerabilities created after      |
|                                  |                           |          | the timestamp you last pulled data on.                          |
|                                  |                           |          | Ex: created_timestamp:<'2021-09-25T13:22'                       |
|                                  |                           |          | Ex: created_timestamp:>'2021-02-12'                             |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.base_score                   | Number                    | Yes      | CVE base score.                                                  |
|                                  |                           |          | Ex: cve.base_score:>5.0                                          |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.cwes                         | String                    | Yes      | Unique identifier for a vulnerability from the Common            |
|                                  |                           |          | Weakness Enumeration (CWE) list.                                |
|                                  |                           |          | Ex: cve.cwes:['CWE-787','CWE-699']                               |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.exploit_status               | String                    | Yes      | Numeric value of the most severe known exploit. Supports        |
|                                  |                           |          | multiple values and negation.                                    |
|                                  |                           |          | Values: 0=Unproven, 30=Available, 60=Easily accessible,        |
|                                  |                           |          | 90=Actively used                                                 |
|                                  |                           |          | Ex: cve.exploit_status:'60'                                      |
|                                  |                           |          | Ex: cve.exploit_status:!'0'                                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.exprt_rating                 | String                    | Yes      | ExPRT rating assigned by CrowdStrike's predictive AI rating     |
|                                  |                           |          | system. Value must be in all caps. Supports multiple values     |
|                                  |                           |          | and negation.                                                    |
|                                  |                           |          | Values: UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL                    |
|                                  |                           |          | Ex: cve.exprt_rating:'HIGH'                                      |
|                                  |                           |          | Ex: cve.exprt_rating:['HIGH','CRITICAL']                        |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.id                           | String                    | Yes      | Unique identifier for a vulnerability as cataloged in the       |
|                                  |                           |          | National Vulnerability Database (NVD). Supports multiple        |
|                                  |                           |          | values and negation. For case-insensitive filtering, add        |
|                                  |                           |          | .insensitive to the field name.                                 |
|                                  |                           |          | Note: All values must be enclosed in brackets.                  |
|                                  |                           |          | Ex: cve.id:['CVE-2022-1234']                                    |
|                                  |                           |          | Ex: cve.id:['CVE-2022-1234','CVE-2023-1234']                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.is_cisa_kev                  | Boolean                   | Yes      | Filter for vulnerabilities that are in the CISA Known          |
|                                  |                           |          | Exploited Vulnerabilities (KEV) catalog. Supports negation.     |
|                                  |                           |          | Ex: cve.is_cisa_kev:true                                         |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.remediation_level            | String                    | Yes      | CVSS remediation level of the vulnerability. Supports           |
|                                  |                           |          | multiple values and negation.                                    |
|                                  |                           |          | Ex: cve.remediation_level:'O' (official fix)                    |
|                                  |                           |          | Ex: cve.remediation_level:'U' (no available fix)                |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.severity                     | String                    | Yes      | CVSS severity rating of the vulnerability. Value must be in     |
|                                  |                           |          | all caps. Supports multiple values and negation.                |
|                                  |                           |          | Values: UNKNOWN, NONE, LOW, MEDIUM, HIGH, CRITICAL              |
|                                  |                           |          | Ex: cve.severity:'LOW'                                           |
|                                  |                           |          | Ex: cve.severity:!'UNKNOWN'                                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| cve.types                        | String                    | Yes      | Vulnerability type.                                              |
|                                  |                           |          | Values: Vulnerability, Misconfiguration, Unsupported software   |
|                                  |                           |          | Ex: cve.types:!'Misconfiguration'                               |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| data_providers.ports             | String                    | Yes      | Ports on the host where the vulnerability was found by the      |
|                                  |                           |          | third-party provider.                                            |
|                                  |                           |          | Ex: data_providers.ports:'53'                                    |
|                                  |                           |          | Ex: data_providers.ports:!'0' (any port)                        |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| data_providers.provider          | String                    | No       | Name of the data provider.                                       |
|                                  |                           |          | Ex: data_providers.provider:'{provider name}'                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| data_providers.rating            | String                    | Yes      | Third-party provider rating.                                     |
|                                  |                           |          | Values: UNKNOWN, NONE, LOW, MEDIUM, HIGH, CRITICAL              |
|                                  |                           |          | Ex: data_providers.rating:'CRITICAL'                            |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| data_providers.scan_time         | Timestamp                 | Yes      | UTC date and time when the vulnerability was most recently      |
|                                  |                           |          | identified by the third-party provider.                         |
|                                  |                           |          | Ex: data_providers.scan_time:>'2023-08-03'                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| data_providers.scanner_id        | String                    | No       | ID of the third-party scanner that identified the               |
|                                  |                           |          | vulnerability.                                                   |
|                                  |                           |          | Ex: data_providers.scanner_id:'{scanner id}'                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.asset_criticality      | String                    | Yes      | Assigned criticality level of the asset.                        |
|                                  |                           |          | Values: Critical, High, Noncritical, Unassigned                 |
|                                  |                           |          | Ex: host_info.asset_criticality:['Critical','High']             |
|                                  |                           |          | Ex: host_info.asset_criticality:!'Unassigned'                   |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.groups                 | String                    | Yes      | Unique system-assigned ID of a host group. Supports multiple    |
|                                  |                           |          | values and negation. All values must be enclosed in brackets.   |
|                                  |                           |          | Ex: host_info.groups:['03f0b54af2692e99c4cec945818fbef7']        |
|                                  |                           |          | Ex: host_info.groups:!['03f0b54af2692e99c4cec945818fbef7']       |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.has_run_container      | Boolean                   | No       | Whether or not the host is running Kubernetes containers.       |
|                                  |                           |          | Ex: host_info.has_run_container:true                             |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.internet_exposure      | String                    | No       | Whether or not the asset is internet-facing.                    |
|                                  |                           |          | Values: Yes, No, Pending                                         |
|                                  |                           |          | Ex: host_info.internet_exposure:'Yes'                           |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.managed_by             | String                    | Yes      | Indicates if the asset has the Falcon sensor installed.         |
|                                  |                           |          | Values: Falcon sensor, Unmanaged                                |
|                                  |                           |          | Supports multiple values and negation.                          |
|                                  |                           |          | Ex: host_info.managed_by:'Unmanaged'                            |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.platform_name          | String                    | Yes      | Operating system platform. Supports negation.                   |
|                                  |                           |          | Values: Windows, Mac, Linux                                      |
|                                  |                           |          | Ex: host_info.platform_name:'Windows'                           |
|                                  |                           |          | Ex: host_info.platform_name:!'Linux'                            |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.product_type_desc      | String                    | Yes      | Type of host a sensor is running on. Supports multiple values   |
|                                  |                           |          | and negation. For case-insensitive filtering, add .insensitive  |
|                                  |                           |          | to the field name. Enter values with first letter capitalized.  |
|                                  |                           |          | Values: Workstation, Server, Domain Controller                   |
|                                  |                           |          | Ex: host_info.product_type_desc:'Workstation'                   |
|                                  |                           |          | Ex: host_info.product_type_desc:!'Workstation'                  |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.tags                   | String                    | Yes      | Name of a tag assigned to a host. Supports multiple values      |
|                                  |                           |          | and negation. All values must be enclosed in brackets.          |
|                                  |                           |          | Ex: host_info.tags:['ephemeral']                                |
|                                  |                           |          | Ex: host_info.tags:!['search','ephemeral']                      |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| host_info.third_party_asset_ids  | String                    | Yes      | Asset IDs assigned to the host by third-party providers in      |
|                                  |                           |          | the format: {data_provider}: {data_provider_asset_id}           |
|                                  |                           |          | Supports multiple values and negation.                          |
|                                  |                           |          | Ex: host_info.third_party_asset_ids:'{provider}: {asset_id}'    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| last_seen_within                 | Number                    | No       | Filter for vulnerabilities based on the number of days since    |
|                                  |                           |          | a host last connected to Falcon. Enter a numeric value from     |
|                                  |                           |          | 3 to 45 to indicate the number of days to look back.            |
|                                  |                           |          | Ex: last_seen_within:'10'                                       |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| services.port                    | String                    | No       | Port on the host where a vulnerability was found by Falcon      |
|                                  |                           |          | EASM or a third-party provider.                                 |
|                                  |                           |          | Ex: services.port:'443'                                         |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| services.protocol                | String                    | No       | Network protocols recognized by Falcon EASM.                    |
|                                  |                           |          | Ex: services.protocol:'pop3'                                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| services.transport               | String                    | No       | Transport methods recognized by Falcon EASM.                    |
|                                  |                           |          | Ex: services.transport:'tcp'                                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| status                           | String                    | Yes      | Status of a vulnerability. Value must be in all lowercase       |
|                                  |                           |          | letters. Supports multiple values and negation.                 |
|                                  |                           |          | Values: open, closed, reopen, expired                           |
|                                  |                           |          | Ex: status:'open'                                               |
|                                  |                           |          | Ex: status:!'closed'                                            |
|                                  |                           |          | Ex: status:['open','reopen']                                    |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| suppression_info.is_suppressed   | Boolean                   | No       | Indicates if the vulnerability is suppressed by a suppression   |
|                                  |                           |          | rule or not.                                                     |
|                                  |                           |          | Ex: suppression_info.is_suppressed:true                         |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| suppression_info.reason          | String                    | Yes      | Attribute assigned to a suppression rule. Supports multiple     |
|                                  |                           |          | values and negation. All values must be enclosed in brackets.   |
|                                  |                           |          | Values: ACCEPT_RISK, COMPENSATING_CONTROL, FALSE_POSITIVE       |
|                                  |                           |          | Ex: suppression_info.reason:['ACCEPT_RISK']                     |
|                                  |                           |          | Ex: suppression_info.reason:!['FALSE_POSITIVE']                 |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| updated_timestamp                | Timestamp                 | Yes      | UTC date and time of the last update made on a vulnerability.   |
|                                  |                           |          | Ex: updated_timestamp:<'2021-10-20T22:36'                       |
|                                  |                           |          | Ex: updated_timestamp:>'2021-09-15'                             |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+
| vulnerability_id                 | String                    | Yes      | CVE ID of the vulnerability. If there's no CVE ID, this is      |
|                                  |                           |          | the CrowdStrike or third-party ID of the vulnerability.         |
|                                  |                           |          | For case-insensitive filtering, add .insensitive to the field   |
|                                  |                           |          | name. Supports multiple values and negation.                    |
|                                  |                           |          | Ex: vulnerability_id:['CVE-2022-1234']                          |
|                                  |                           |          | Ex: vulnerability_id:['CVE-2022-1234','CVE-2023-4321']          |
+----------------------------------+---------------------------+----------+------------------------------------------------------------------+

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
