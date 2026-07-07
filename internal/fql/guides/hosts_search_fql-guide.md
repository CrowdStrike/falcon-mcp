Falcon Query Language (FQL) - Search Hosts Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===

✅ **WORKING OPERATORS:**
• No operator = equals (default) - ALL FIELDS
• ! = not equal to - ALL FIELDS
• > = greater than - TIMESTAMP FIELDS ONLY
• >= = greater than or equal - TIMESTAMP FIELDS ONLY
• < = less than - TIMESTAMP FIELDS ONLY
• <= = less than or equal - TIMESTAMP FIELDS ONLY
• ~ = text match (case insensitive) - TEXT FIELDS ONLY
• * = wildcard matching - LIMITED SUPPORT (see examples below)

❌ **NON-WORKING OPERATORS:**
• !~ = does not text match - NOT SUPPORTED
• Simple wildcards (field:*) - NOT SUPPORTED

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

=== falcon_search_hosts FQL filter options ===

|Name|Type|Operators|Description|
|-|-|-|-|
|device_id|String|No|The ID of the device. Ex: 061a51ec742c44624a176f079d742052|
|agent_load_flags|String|No|Agent configuration field|
|agent_version|String|No|Agent version. Ex: 7.26.17905.0|
|bios_manufacturer|String|No|BIOS manufacturer. Ex: Phoenix Technologies LTD|
|bios_version|String|No|BIOS version. Ex: 6.00|
|config_id_base|String|No|Agent configuration field|
|config_id_build|String|No|Agent configuration field|
|config_id_platform|String|No|Agent configuration field|
|cpu_signature|String|Yes|CPU signature. Ex: GenuineIntel|
|cid|String|No|Customer ID|
|deployment_type|String|Yes|Linux deployment type: Standard, DaemonSet|
|external_ip|IP Address|Yes|External IP address. Ex: 192.0.2.100|
|first_seen|Timestamp|Yes|First connection timestamp (UTC). Ex: first_seen:>'2016-07-19T11:14:15Z'|
|groups|String|No|Host group ID. Ex: groups:'0bd018b7bd8b47cc8834228a294eabf2'|
|hostname|String|No|The name of the machine. ⚠️ LIMITED wildcard support: - hostname:'PC*' (prefix) - ✅ WORKS - hostname:'*-01' (suffix) - ✅ WORKS - hostname:'*server*' (contains) - ❌ FAILS Ex: hostname:'WinPC9251' or hostname:'PC*'|
|instance_id|String|No|Cloud resource information (EC2 instance ID, Azure VM ID, GCP instance ID, etc.). Ex: instance_id:'i-0dc41d0939384cd15' Ex: instance_id:'f9d3cef9-0123-4567-8901-123456789def'|
|kernel_version|String|No|Kernel version of the host OS. Ex: kernel_version:'6.1.7601.18741'|
|last_login_timestamp|Timestamp|Yes|User logon event timestamp, once a week.|
|last_seen|Timestamp|Yes|Last connection timestamp (UTC). Ex: last_seen:<'2016-07-19T11:14:15Z'|
|linux_sensor_mode|String|Yes|Linux sensor mode: Kernel Mode, User Mode|
|local_ip|IP Address|No|Local IP address. Ex: 192.0.2.1|
|local_ip.raw|IP Address with wildcards|No|Local IP with wildcard support. Use * prefix: Ex: local_ip.raw:*'192.0.2.*' Ex: local_ip.raw:*'*.0.2.100'|
|mac_address|String|No|The MAC address of the device Ex: 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff|
|machine_domain|String|No|Active Directory domain name.|
|major_version|String|No|Major version of the Operating System|
|minor_version|String|No|Minor version of the Operating System|
|modified_timestamp|Timestamp|Yes|Last record update timestamp (UTC)|
|os_version|String|No|Operating system version. Ex: Windows 7|
|ou|String|No|Active Directory organizational unit name|
|platform_id|String|No|Agent configuration field|
|platform_name|String|No|Operating system platform: Windows, Mac, Linux|
|product_type_desc|String|No|Product type: Server, Workstation|
|reduced_functionality_mode|String|Yes|Reduced functionality mode status: yes, no, or "" Ex: reduced_functionality_mode:'no'|
|release_group|String|No|Deployment group name|
|serial_number|String|Yes|Serial number of the device. Ex: C42AFKEBM563|
|service_provider|String|No|The cloud service provider. Available options: - AWS_EC2_V2 - AZURE - GCP Ex: service_provider:'AZURE'|
|service_provider_account_id|String|No|The cloud account ID (AWS Account ID, Azure Subscription ID, GCP Project ID, etc.). Ex: service_provider_account_id:'99841e6a-b123-4567-8901-123456789abc'|
|site_name|String|No|Active Directory site name.|
|status|String|No|Containment Status of the machine. "Normal" denotes good operations; other values might mean reduced functionality or support. Possible values: - normal - containment_pending - contained - lift_containment_pending|
|system_manufacturer|String|No|Name of system manufacturer Ex: VMware, Inc.|
|system_product_name|String|No|Name of system product Ex: VMware Virtual Platform|
|tags|String|No|Falcon grouping tags|

=== ✅ WORKING PATTERNS ===

**Basic Equality:**
• platform_name:'Windows', platform_name:'Linux', platform_name:'Mac'
• product_type_desc:'Server', product_type_desc:'Workstation'
• status:'normal', reduced_functionality_mode:'no'
• service_provider:'AZURE', service_provider:'AWS_EC2_V2', service_provider:'GCP'

**Combined Conditions:**
• service_provider:'AZURE'+platform_name:'Linux'
• platform_name:'Linux'+product_type_desc:'Server'
• (service_provider:'AZURE',service_provider:'AWS_EC2_V2')+platform_name:'Linux'

**Timestamp Comparisons:**
• first_seen:>'2020-01-01T00:00:00Z'
• first_seen:>='2020-01-01T00:00:00Z'
• last_seen:<='2024-12-31T23:59:59Z'

**Inequality Filters:**
• platform_name:!'Windows' (non-Windows hosts)
• service_provider_account_id:!'' (not empty)
• instance_id:!'' (not empty)

**Hostname Wildcards (Limited):**
• hostname:'PC*' (prefix) ✅
• hostname:'*-01' (suffix) ✅
• hostname:'*server*' (contains) ❌ Does NOT work

**IP Address Wildcards:**
• local_ip.raw:*'192.168.*'
• local_ip.raw:*'10.*'

**Text Match:**
• hostname:~'server'
• os_version:~'windows'

=== ❌ PATTERNS TO AVOID ===
• Simple wildcards: service_provider_account_id:*, hostname:*, etc.
• Contains wildcards: hostname:'*server*'
• Wrong IP syntax: local_ip:*

=== 💡 SYNTAX RULES ===
• Use single quotes around string values: 'value'
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Combine conditions with + (AND) or , (OR)
• Use parentheses for grouping: (condition1,condition2)+condition3
