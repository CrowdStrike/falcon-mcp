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

+----------------------+---------------------------+----------+------------------------------------------------------------------+
| Name                 | Type                      | Operators| Description                                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| device_id            | String                    | No       | The ID of the device.                                            |
|                      |                           |          | Ex: 061a51ec742c44624a176f079d742052                             |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| agent_load_flags     | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| agent_version        | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| bios_manufacturer    | String                    | No       | Bios manufacture name.                                           |
|                      |                           |          | Ex: Phoenix Technologies LTD                                     |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| bios_version         | String                    | No       | Bios version.                                                    |
|                      |                           |          | Ex: 6.00                                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| config_id_base       | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| config_id_build      | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| config_id_platform   | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| cpu_signature        | String                    | Yes      | The CPU signature of the device.                                 |
|                      |                           |          | Ex: GenuineIntel                                                 |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| deployment_type      | String                    | Yes      | Linux deployment type:                                           |
|                      |                           |          | - Standard                                                       |
|                      |                           |          | - DaemonSet                                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| external_ip          | IP Address                | Yes      | External IP of the device, as seen by CrowdStrike.               |
|                      |                           |          | Ex: 192.0.2.100                                                  |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| first_seen           | Timestamp                 | Yes      | Timestamp of device's first connection to Falcon,                |
|                      |                           |          | in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").                     |
|                      |                           |          | Ex: 2016-07-19T11:14:15Z                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| hostname             | String                    | No       | The name of the machine. Supports prefix and suffix              |
|                      |                           |          | searching with wildcard, so you can search for                   |
|                      |                           |          | terms like abc and *abc.                                         |
|                      |                           |          | Ex: WinPC9251                                                    |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| last_login_timestamp | Timestamp                 | Yes      | User logon event timestamp, once a week.                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| last_seen            | Timestamp                 | Yes      | Timestamp of device's most recent connection to Falcon,          |
|                      |                           |          | in UTC date format ("YYYY-MM-DDTHH:MM:SSZ").                     |
|                      |                           |          | Ex: 2016-07-19T11:14:15Z                                         |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| linux_sensor_mode    | String                    | Yes      | Linux sensor mode:                                               |
|                      |                           |          | - Kernel Mode                                                    |
|                      |                           |          | - User Mode                                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| local_ip             | IP Address                | No       | The device's local IP address. As a device management            |
|                      |                           |          | parameter, this is the IP address of this device at the          |
|                      |                           |          | last time it connected to the CrowdStrike Cloud.                 |
|                      |                           |          | Ex: 192.0.2.1                                                    |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| local_ip.raw         | IP Address with wildcards | No       | A portion of the device's local IP address, used only for        |
|                      | (*)                       |          | searches that include wildcard characters. Using a wildcard      |
|                      |                           |          | requires specific syntax: when you specify an IP address with    |
|                      |                           |          | this parameter, prefix the IP address with an asterisk (*)       |
|                      |                           |          | and enclose the IP address in single quotes.                     |
|                      |                           |          |                                                                  |
|                      |                           |          | Search for a device with the IP address 192.0.2.100:             |
|                      |                           |          | local_ip.raw:*'192.0.2.*'                                       |
|                      |                           |          | local_ip.raw:*'*.0.2.100'                                        |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| mac_address          | String                    | No       | The MAC address of the device                                    |
|                      |                           |          | Ex: 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff                       |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| machine_domain       | String                    | No       | Active Directory domain name.                                    |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| major_version        | String                    | No       | Major version of the Operating System                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| minor_version        | String                    | No       | Minor version of the Operating System                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| modified_timestamp   | Timestamp                 | Yes      | The last time that the machine record was updated. Can include   |
|                      |                           |          | status like containment status changes or configuration          |
|                      |                           |          | group changes.                                                   |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| os_version           | String                    | No       | Operating system version.                                        |
|                      |                           |          | Ex: Windows 7                                                    |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| ou                   | String                    | No       | Active Directory organizational unit name.                        |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| platform_id          | String                    | No       | CrowdStrike agent configuration notes                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| platform_name        | String                    | No       | Operating system platform.                                       |
|                      |                           |          |                                                                  |
|                      |                           |          | Available options:                                               |
|                      |                           |          | - Windows                                                        |
|                      |                           |          | - Mac                                                            |
|                      |                           |          | - Linux                                                          |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| product_type_desc    | String                    | No       | Name of product type.                                            |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| reduced_functionality| String                    | Yes      | Reduced functionality mode (RFM) status:                         |
| _mode                |                           |          | - yes                                                            |
|                      |                           |          | - no                                                             |
|                      |                           |          | - Unknown (displayed as a blank string)                          |
|                      |                           |          |                                                                  |
|                      |                           |          | Unknown is used for hosts with an unavailable RFM status:        |
|                      |                           |          | - The sensor was deployed less than 24 hours ago and has not     |
|                      |                           |          |   yet provided an RFM status.                                    |
|                      |                           |          | - The sensor version does not support RFM.                       |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| release_group        | String                    | No       | Name of the Falcon deployment group, if the this machine is      |
|                      |                           |          | part of a Falcon sensor deployment group.                        |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| serial_number        | String                    | Yes      | Serial number of the device.                                     |
|                      |                           |          | Ex: C42AFKEBM563                                                 |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| site_name            | String                    | No       | Active Directory site name.                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| status               | String                    | No       | Containment Status of the machine. "Normal" denotes good         |
|                      |                           |          | operations; other values might mean reduced functionality        |
|                      |                           |          | or support.                                                      |
|                      |                           |          |                                                                  |
|                      |                           |          | Possible values:                                                 |
|                      |                           |          | - normal                                                         |
|                      |                           |          | - containment_pending                                            |
|                      |                           |          | - contained                                                      |
|                      |                           |          | - lift_containment_pending                                       |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| system_manufacturer  | String                    | No       | Name of system manufacturer                                      |
|                      |                           |          | Ex: VMware, Inc.                                                 |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| system_product_name  | String                    | No       | Name of system product                                           |
|                      |                           |          | Ex: VMware Virtual Platform                                      |
+----------------------+---------------------------+----------+------------------------------------------------------------------+
| tags                 | String                    | No       | Falcon grouping tags                                             |
+----------------------+---------------------------+----------+------------------------------------------------------------------+

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Hostname supports wildcards: 'PC*', '*server*'
• IP wildcards require local_ip.raw with specific syntax
"""
