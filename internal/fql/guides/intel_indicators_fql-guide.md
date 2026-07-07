Falcon Query Language (FQL) - Intel Query Indicator Entities Guide

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
• * = wildcard matching (not supported on all fields — see endpoint-specific notes below)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) or relative: 'now-7d', 'now-24h' (lowercase, single-quoted)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition (e.g., platform_name:'Windows'+status:'normal')
• , = OR condition (e.g., severity_name:'Critical',severity_name:'High')
• ( ) = Group expressions

IMPORTANT: Use + for AND and , for OR — do NOT use the words AND/OR.
Values must be single-quoted. Relative dates must be lowercase ('now-7d' not 'NOW-7d').

=== falcon_search_indicators FQL filter options ===

|Name|Type|Description|
|-|-|-|
|id|String|The indicator ID. It follows the format: {type}_{indicator}|
|created_date|Timestamp|Timestamp in standard Unix time, UTC when the indicator was created. Ex: 1753022288|
|deleted|Boolean|If true, include only published indicators. If false, include only deleted indicators. Ex: false|
|domain_types|String|The domain type of domain indicators. Possible values include: - ActorControlled - DGA - DynamicDNS - KnownGood - LegitimateCompromised - PhishingDomain - Sinkholed - StrategicWebCompromise - Unregistered|
|indicator|String|The indicator that was queried. Ex: "all-deutsch.gl.at.ply.gg"|
|ip_address_types|String|The address type of ip_address indicators. Possible values include: - HtranDestinationNode - HtranProxy - LegitimateCompromised - Parking - PopularSite - SharedWebHost - Sinkhole - TorProxy|
|kill_chains|String|The point in the kill chain at which an indicator is associated. Possible values include: - reconnaissance - weaponization - delivery - exploitation - installation - c2 (Command and Control) - actionOnObjectives Ex: "delivery"|
|last_updated|Timestamp|Timestamp in standard Unix time, UTC when the indicator was last updated in the internal database. Ex: 1753027269|
|malicious_confidence|String|Indicates a confidence level by which an indicator is considered to be malicious. Possible values: - high: If indicator is an IP or domain, it has been associated with malicious activity within the last 60 days. - medium: If indicator is an IP or domain, it has been associated with malicious activity within the last 60-120 days. - low: If indicator is an IP or domain, it has been associated with malicious activity exceeding 120 days. - unverified: This indicator has not been verified by a CrowdStrike Intelligence analyst or an automated system. Ex: "high"|
|malware_families|String|Indicates the malware family an indicator has been associated with. An indicator might be associated with more than one malware family. Ex: "Xworm", "njRATLime"|
|published_date|Timestamp|Timestamp in standard Unix time, UTC when the indicator was first published to the API. Ex: 1753022288|
|reports|String|The report ID that the indicator is associated with (such as CSIT-XXXX or CSIR-XXXX). The report list is also represented under the labels list in the JSON data structure.|
|targets|String|The indicators targeted industries. Possible values include sectors like: - Aerospace - Agricultural - Chemical - Defense - Dissident - Energy - Financial - Government - Healthcare - Technology|
|threat_types|String|Types of threats. Ex: "ddos", "mineware", "banking"|
|type|String|Possible indicator types include: - binary_string - compile_time - device_name - domain - email_address - email_subject - event_name - file_mapping - file_name - file_path - hash_ion - hash_md5 - hash_sha256 - ip_address - ip_address_block - mutex_name - password - persona_name - phone_number - port - registry - semaphore_name - service_name - url - user_agent - username - x509_seria - x509_subject Ex: "domain"|
|vulnerabilities|String|Associated vulnerabilities (CVEs). Ex: "CVE-2023-1234"|

=== EXAMPLE USAGE ===

• type:'domain'
• malicious_confidence:'high'
• type:'hash_md5'+malicious_confidence:'high'
• malicious_confidence:'high'+published_date:>'now-7d'
• published_date:>'now-30d'

Relative dates supported: published_date:>'now-7d' | published_date:>'now-30d' (lowercase 'now', quoted)

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date fields accept relative syntax ('now-Nd', 'now-Nh') or Unix epoch integers
