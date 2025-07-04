"""
Contains Detections resources.
"""

# TODO: verify filter and provide valid examples
SEARCH_DETECTIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Detections Guide

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

=== falcon_search_detections FQL filter options ===

Filter options are broken out into four categories:

• General
• Behavioral
• Devices
• Miscellaneous

==== General ====

• adversary_ids
• assigned_to_name
• cid
• date_updated
• detection_id
• first_behavior
• last_behavior
• max_confidence
• max_severity
• max_severity_displayname
• seconds_to_resolved
• seconds_to_triaged
• status

==== Behavioral ====

• alleged_filetype
• behavior_id
• cmdline
• confidence
• contral_graph_id
• device_id
• filename
• ioc_source
• ioc_type
• ioc_value
• md5
• objective
• parent_details.parent_cmdline
• parent_details.parent_md5
• parent_details.parent_process_graph_id
• parent_details.parent_process_id
• parent_details.parent_sha256
• pattern_disposition
• scenario
• severity
• sha256
• tactic
• technique
• timestamp
• triggering_process_graph_id
• triggering_process_id
• user_id
• user_name

Example: behaviors.ioc_type

==== Devices ====

• agent_load_flags
• agent_local_time
• agent_version
• bios_manufacturer
• bios_version
• cid
• config_id_base
• config_id_build
• config_id_platform
• cpu_signature
• device_id
• external_ip
• first_seen
• hostname
• last_seen
• local_ip
• mac_address
• machine_domain
• major_version
• minor_version
• modified_timestamp
• os_version
• ou
• platform_id
• platform_name
• product_type
• product_type_desc
• reduced_functionality_mode
• release_group
• serial_number
• site_name
• status
• system_manufacturer
• system_product_name

Example: device.platform_name

==== Miscellaneous ====

• hostinfo.active_directory_dn_display
• hostinfo.domain
• quarantined_files.id
• quarantined_files.paths
• quarantined_files.sha256
• quarantined_files.state

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
"""
