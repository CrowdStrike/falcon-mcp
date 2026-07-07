Falcon Query Language (FQL) - Search Unmanaged Assets Guide

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

=== AUTOMATIC FILTERING ===
This tool automatically filters for unmanaged assets only by adding entity_type:'unmanaged' to all queries.
You do not need to (and cannot) specify entity_type in your filter - it is always set to 'unmanaged'.

=== falcon_search_unmanaged_assets FQL filter options ===

|Name|Type|Operators|Description|
|-|-|-|-|
|platform_name|String|Yes|Operating system platform of the unmanaged asset. Ex: platform_name:'Windows' Ex: platform_name:'Linux' Ex: platform_name:'Mac' Ex: platform_name:['Windows','Linux']|
|os_version|String|Yes|Operating system version of the unmanaged asset. Ex: os_version:'Windows 10' Ex: os_version:'Ubuntu 20.04' Ex: os_version:'macOS 12.3' Ex: os_version:*'Windows*'|
|hostname|String|Yes|Hostname of the unmanaged asset. Ex: hostname:'PC-001' Ex: hostname:*'PC-*' Ex: hostname:['PC-001','PC-002']|
|country|String|Yes|Country where the unmanaged asset is located. Ex: country:'United States of America' Ex: country:'Germany' Ex: country:['United States of America','Canada']|
|city|String|Yes|City where the unmanaged asset is located. Ex: city:'New York' Ex: city:'London' Ex: city:['New York','Los Angeles']|
|product_type_desc|String|Yes|Product type description of the unmanaged asset. Ex: product_type_desc:'Workstation' Ex: product_type_desc:'Server' Ex: product_type_desc:'Domain Controller' Ex: product_type_desc:['Workstation','Server']|
|external_ip|String|Yes|External IP address of the unmanaged asset. Ex: external_ip:'192.0.2.1' Ex: external_ip:'192.0.2.0/24' Ex: external_ip:['192.0.2.1','203.0.113.1']|
|local_ip_addresses|String|Yes|Local IP addresses of the unmanaged asset. Ex: local_ip_addresses:'10.0.1.100' Ex: local_ip_addresses:'192.168.1.0/24' Ex: local_ip_addresses:['10.0.1.100','192.168.1.50']|
|mac_addresses|String|Yes|MAC addresses of the unmanaged asset. Ex: mac_addresses:'AA-BB-CC-DD-EE-FF' Ex: mac_addresses:*'AA-BB-CC*' Ex: mac_addresses:['AA-BB-CC-DD-EE-FF','11-22-33-44-55-66']|
|first_seen_timestamp|Timestamp|Yes|Date and time when the unmanaged asset was first discovered. Ex: first_seen_timestamp:'2024-01-01T00:00:00Z' Ex: first_seen_timestamp:>'2024-01-01T00:00:00Z' Ex: first_seen_timestamp:>'now-7d'|
|last_seen_timestamp|Timestamp|Yes|Date and time when the unmanaged asset was last seen. Ex: last_seen_timestamp:'2024-06-15T12:00:00Z' Ex: last_seen_timestamp:>'now-24h' Ex: last_seen_timestamp:<'now-30d'|
|kernel_version|String|Yes|Kernel version of the unmanaged asset. Linux and Mac: The major version, minor version, and patch version. Windows: The build number. Ex: kernel_version:'5.4.0' Ex: kernel_version:'19041' Ex: kernel_version:*'5.4*'|
|system_manufacturer|String|Yes|System manufacturer of the unmanaged asset. Ex: system_manufacturer:'Dell Inc.' Ex: system_manufacturer:'VMware, Inc.' Ex: system_manufacturer:*'Dell*'|
|system_product_name|String|Yes|System product name of the unmanaged asset. Ex: system_product_name:'OptiPlex 7090' Ex: system_product_name:'VMware Virtual Platform' Ex: system_product_name:*'OptiPlex*'|
|criticality|String|Yes|Criticality level assigned to the unmanaged asset. Ex: criticality:'Critical' Ex: criticality:'High' Ex: criticality:'Medium' Ex: criticality:'Low' Ex: criticality:'Unassigned'|
|internet_exposure|String|Yes|Whether the unmanaged asset is exposed to the internet. Ex: internet_exposure:'Yes' Ex: internet_exposure:'No' Ex: internet_exposure:'Pending' Ex: internet_exposure:['Yes','Pending']|
|discovering_by|String|Yes|Method by which the unmanaged asset was discovered. Ex: discovering_by:'Passive' Ex: discovering_by:'Active' Ex: discovering_by:['Passive','Active']|
|confidence|Number|Yes|Confidence level of the unmanaged asset discovery (0-100). Higher values indicate higher confidence that the asset is real. Ex: confidence:>80 Ex: confidence:>=90 Ex: confidence:<50 Ex: confidence:[80,90,95]|

=== IMPORTANT NOTES ===
• entity_type:'unmanaged' is automatically applied - do not include in your filter
• Use single quotes around string values: 'value'
• Use square brackets for exact matches and multiple values: ['value1','value2']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Boolean values: true or false (no quotes)
• Some fields require specific capitalization (check individual field descriptions)

=== COMMON FILTER EXAMPLES ===
• Find Windows unmanaged assets: platform_name:'Windows'
• Find high-confidence unmanaged assets: confidence:>80
• Find recently discovered assets: first_seen_timestamp:>'now-7d'
• Find assets by hostname pattern: hostname:*'PC-*'
• Find critical unmanaged assets: criticality:'Critical'
• Find servers: product_type_desc:'Server'
• Find internet-exposed assets: internet_exposure:'Yes'
• Find assets in specific network: external_ip:'192.168.1.0/24'
• Find assets by manufacturer: system_manufacturer:*'Dell*'
• Find recently seen assets: last_seen_timestamp:>'now-24h'

=== COMPLEX QUERY EXAMPLES ===
• Windows workstations seen recently: platform_name:'Windows'+product_type_desc:'Workstation'+last_seen_timestamp:>'now-7d'
• Critical servers with internet exposure: criticality:'Critical'+product_type_desc:'Server'+internet_exposure:'Yes'
• Dell systems discovered this month: system_manufacturer:*'Dell*'+first_seen_timestamp:>'now-30d'
