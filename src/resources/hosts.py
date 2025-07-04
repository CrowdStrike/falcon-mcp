"""
Contains Hosts resources.
"""

SEARCH_HOSTS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Hosts Guide

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

=== falcon_search_hosts FQL filter options ===

=== IDENTIFICATION & CORE ===
• device_id: Unique device identifier
• hostname: Host name/computer name (supports wildcards)
• cid: Customer ID
• agent_version: CrowdStrike agent version
• serial_number: Device serial number

=== PLATFORM & SYSTEM ===
• platform_name: Operating system platform
  Available Options:
    - 'Windows'
    - 'Mac'
    - 'Linux'
• platform_id: Numeric platform identifier
• os_version: Operating system version
• major_version: Major OS version number
• minor_version: Minor OS version number
• kernel_version: Linux kernel version
• product_type_desc: System type
  Available Options:
    - 'Workstation'
    - 'Server'
    - 'Domain Controller'

=== NETWORK INFORMATION ===
• external_ip: External IP address as seen by CrowdStrike
• local_ip: Local/internal IP address
• local_ip.raw: IP address with wildcard support (use *'192.168.1.*')
• connection_ip: Current connection IP
• default_gateway_ip: Default gateway IP
• mac_address: MAC address
• connection_mac_address: Connection MAC address

=== STATUS & CONTAINMENT ===
• status: Host containment status
  Available Options:
    - 'normal' (normal operations)
    - 'containment_pending' (containment in progress)
    - 'contained' (host contained)
    - 'lift_containment_pending' (lifting containment)
• filesystem_containment_status: File system containment status
• reduced_functionality_mode: RFM status ('yes', 'no', or blank)
• rtr_state: Real Time Response state

=== TIMESTAMPS ===
• first_seen: When host first connected to Falcon
• last_seen: Most recent connection to Falcon
• modified_timestamp: Last host record update
• agent_local_time: Agent's local timestamp

=== HARDWARE & BIOS ===
• bios_manufacturer: BIOS manufacturer name
• bios_version: BIOS version
• system_manufacturer: System manufacturer
• system_product_name: System product name
• cpu_signature: CPU signature
• cpu_vendor: CPU vendor code
• chassis_type: Chassis type code
• chassis_type_desc: Chassis type description

=== DOMAIN & GROUPS ===
• machine_domain: Active Directory domain
• ou: Organizational unit
• groups: Host groups
• tags: Falcon grouping tags

=== CLOUD & VIRTUALIZATION ===
• service_provider: Cloud provider ('AZURE', 'AWS', 'GCP', etc.)
• service_provider_account_id: Cloud account ID
• instance_id: Cloud instance ID
• k8s_cluster_id: Kubernetes cluster ID
• deployment_type: Deployment type ('Standard', 'DaemonSet')
• linux_sensor_mode: Linux sensor mode ('Kernel Mode', 'User Mode')

=== CONFIGURATION ===
• config_id_base: Agent configuration base ID
• config_id_build: Agent configuration build ID
• config_id_platform: Agent configuration platform ID
• agent_load_flags: Agent load flags

=== EXAMPLE USAGE ===

=== PLATFORM-BASED SEARCHES ===
• platform_name:'Windows'
• platform_name:'Linux'+product_type_desc:'Server'
• platform_name:'Mac'+product_type_desc:'Workstation'

=== HOSTNAME SEARCHES ===
• hostname:'PC*'
• hostname:'*server*'
• hostname:'DESKTOP-ABC123'

=== STATUS-BASED SEARCHES ===
• status:'normal'
• status:'contained'
• reduced_functionality_mode:'yes'

=== NETWORK-BASED SEARCHES ===
• local_ip.raw:*'192.168.1.*'
• external_ip:'203.0.113.10'
• mac_address:'00:50:56:*'

=== TIME-BASED SEARCHES ===
• last_seen:>'2024-01-20T00:00:00Z'
• first_seen:>='2024-01-15T00:00:00Z'+first_seen:<='2024-01-20T00:00:00Z'
• last_seen:<'2024-01-15T00:00:00Z'

=== AGENT & VERSION SEARCHES ===
• agent_version:'7.26.*'
• agent_version:<'7.20.0'
• os_version:'*Windows 10*'

=== CLOUD & INFRASTRUCTURE SEARCHES ===
• service_provider:'AZURE'
• service_provider:'AWS'
• deployment_type:'DaemonSet'
• k8s_cluster_id:*

=== HARDWARE-BASED SEARCHES ===
• system_manufacturer:'VMware*'
• system_manufacturer:'Microsoft Corporation'
• bios_manufacturer:'American Megatrends*'

=== ADVANCED COMBINED SEARCHES ===
• platform_name:'Windows'+product_type_desc:'Server'+status:'normal'
• platform_name:'Linux'+machine_domain:'company.local'
• platform_name:'Windows'+product_type_desc:'Workstation'+status:'contained'
• service_provider:'AZURE'+platform_name:'Linux'+product_type_desc:'Server'+last_seen:>'2024-01-18T00:00:00Z'
• tags:'*production*'

=== BULK FILTERING SEARCHES ===
• (platform_name:'Windows'),(platform_name:'Linux')
• (product_type_desc:'Server'),(product_type_desc:'Workstation')
• (local_ip.raw:*'192.168.1.*'),(local_ip.raw:*'10.0.1.*')

=== TROUBLESHOOTING SEARCHES ===
• (status:'containment_pending'),(status:'contained'),(reduced_functionality_mode:'yes')
• last_seen:<'2024-01-15T00:00:00Z'
• (rtr_state:!'')+status:'normal'

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Hostname supports wildcards: 'PC*', '*server*'
• IP wildcards require local_ip.raw with specific syntax
• Complex queries may take longer to execute
• Status values: normal, containment_pending, contained, lift_containment_pending
"""
