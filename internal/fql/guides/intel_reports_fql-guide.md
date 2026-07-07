Falcon Query Language (FQL) - Intel Query Report Entities Guide

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

=== falcon_search_reports FQL filter options ===

|Name|Type|Description|
|-|-|-|
|id|Number|The report's ID. Ex: 2583|
|actors|String|Names of adversaries included in a report. Ex: "FANCY BEAR"|
|created_date|Timestamp|Timestamp in Unix epoch format when the report was created. Ex: 1754075803|
|description|String|A detailed description of the report. Ex: "In mid-July 2025, CrowdStrike Intelligence identified infrastructure..."|
|last_modified_date|Timestamp|Timestamp in Unix epoch format when the report was last modified. Ex: 1754076191|
|motivations.value|String|Motivations included in the report. Ex: "Criminal", "State-Sponsored"|
|name|String|The report's name. Ex: "CSA-250861 Newly Identified HAYWIRE KITTEN Infrastructure Associated with Microsoft Phishing Campaign"|
|type|String|The type of report. Ex: "notice", "tipper", "periodic-report"|
|short_description|String|A truncated version of the report's description. Ex: "Adversary: HAYWIRE KITTEN || Target Industry: Technology, Renewable Energy..."|
|slug|String|The URL-friendly identifier of the report. Ex: "csa-250861", "csit-25151"|
|sub_type|String|The subtype of the report. Ex: "daily", "yara"|
|tags|String|The report's tags. Ex: "ransomware", "espionage", "vulnerabilities"|
|target_countries|String|Targeted countries included in the report. Ex: "United States", "Taiwan", "Western Europe"|
|target_industries|String|Targeted industries included in the report. Ex: "Technology", "Government", "Healthcare"|
|url|String|The URL to the report's page. Ex: "https://falcon.crowdstrike.com/intelligence/reports/csa-250861"|

=== EXAMPLE USAGE ===

• report_type:'malware'
• name:'*ransomware*'
• created_date:>'2023-01-01T00:00:00Z'
• target_industries:'healthcare'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
