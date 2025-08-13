"""
Contains Discover resources for applications and unmanaged assets.
"""

from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, operators, description)
SEARCH_APPLICATIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "architectures",
        "String",
        "Yes",
        """
        Application architecture. Unavailable for browser extensions.

        Ex: architectures:'x86'
        Ex: architectures:!'x64'
        Ex: architectures:['x86','x64']
        """
    ),
    (
        "category",
        "String",
        "Yes",
        """
        Category the application is in. Unavailable for browser extensions.

        Ex: category:'IT/Security Apps'
        Ex: category:'Web Browsers'
        Ex: category:'Back up and Recovery'
        Ex: category:['IT/Security Apps','Web Browsers']
        """
    ),
    (
        "cid",
        "String",
        "Yes",
        """
        The application's customer ID. In multi-CID environments:
        - You can filter on both parent and child CIDs.
        - If you're in a parent CID and leave this filter empty, the response includes data about the parent CID and all its child CIDs.
        - If you're in a parent CID and use this filter, the response includes data for only the CIDs you filtered on.
        - If you're in a child CID, this property will only show data for that CID.

        Ex: cid:'cxxx4'
        Ex: cid:!'cxxx4'
        Ex: cid:'cxxx4',cid:'dxxx5'
        """
    ),
    (
        "first_seen_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time the application was first seen.

        Ex: first_seen_timestamp:'2022-12-22T12:41:47.417Z'
        """
    ),
    (
        "groups",
        "String",
        "Yes",
        """
        All application groups the application is assigned to.

        Ex: groups:'ExampleAppGroup'
        Ex: groups:['AppGroup1','AppGroup2']
        """
    ),
    (
        "id",
        "String",
        "Yes",
        """
        Unique ID of the application. Each application ID represents a particular instance of an application on a particular asset.

        Ex: id:'a89xxxxx191'
        Ex: id:'a89xxxxx191',id:'a89xxxxx192'
        """
    ),
    (
        "installation_paths",
        "String",
        "Yes",
        """
        File paths of the application or executable file to the folder on the asset.

        Ex: installation_paths:'C:\\Program Files\\Internet Explorer\\iexplore.exe'
        Ex: installation_paths:'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        Ex: installation_paths:['C:\\Program Files (x86)\\Google*','C:\\Program Files (x86)\\Adobe*']
        """
    ),
    (
        "installation_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time the application was installed, if available.

        Ex: installation_timestamp:'2023-01-11T00:00:00.000Z'
        """
    ),
    (
        "is_normalized",
        "Boolean",
        "Yes",
        """
        Windows: Whether the application name is normalized (true/false).
        Applications can have different naming variations that result in different records for each variation.
        To avoid this duplication, the most common applications are listed under a single normalized application name.
        Unavailable for browser extensions.

        Ex: is_normalized:true
        """
    ),
    (
        "is_suspicious",
        "Boolean",
        "Yes",
        """
        Whether the application is suspicious based on how often it's been seen in a detection on that asset (true/false).
        Unavailable for browser extensions. See browser_extension.permission_severity instead.

        Ex: is_suspicious:true
        Ex: is_suspicious:!false
        """
    ),
    (
        "last_updated_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time the installation fields of the application instance most recently changed.

        Ex: last_updated_timestamp:'2022-12-22T12:41:47.417Z'
        """
    ),
    (
        "last_used_file_hash",
        "String",
        "Yes",
        """
        Windows and macOS: Most recent file hash used for the application.

        Ex: last_used_file_hash:'0xxxa'
        Ex: last_used_file_hash:['0xxxa','7xxxx9']
        """
    ),
    (
        "last_used_file_name",
        "String",
        "Yes",
        """
        Windows and macOS: Most recent file name used for the application.

        Ex: last_used_file_name:'setup.exe'
        Ex: last_used_file_name:'putty.exe'
        Ex: last_used_file_name:['setup.exe','putty.exe']
        """
    ),
    (
        "last_used_timestamp",
        "Timestamp",
        "Yes",
        """
        Windows and macOS: Date and time the application was most recently used.

        Ex: last_used_timestamp:'2023-01-10T23:00:00.000Z'
        """
    ),
    (
        "last_used_user_name",
        "String",
        "Yes",
        """
        Windows and macOS: Username of the account that most recently used the application.

        Ex: last_used_user_name:'Administrator'
        Ex: last_used_user_name:'xiany'
        Ex: last_used_user_name:['xiany','dursti']
        """
    ),
    (
        "last_used_user_sid",
        "String",
        "Yes",
        """
        Windows and macOS: Security identifier of the account that most recently used the application.

        Ex: last_used_user_sid:'S-1-x-x-xxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxx-xxx1'
        Ex: last_used_user_sid:['S-x-x-x-x-1','S-x-x-x-7']
        """
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Name of the application.

        Ex: name:'Chrome'
        Ex: name:'Falcon Sensor'
        Ex: name:['Chrome','Edge']
        """
    ),
    (
        "name_vendor",
        "String",
        "Yes",
        """
        To group results by application: The app name and vendor name for all application IDs with this application name.

        Ex: name_vendor:'Chrome-Google'
        Ex: name_vendor:'Tools-VMware'
        Ex: name_vendor:['Chrome-Google','Tools-VMware']
        """
    ),
    (
        "name_vendor_version",
        "String",
        "Yes",
        """
        To group results by application version: The app name, vendor name, and vendor version for all application IDs with this application name.

        Ex: name_vendor_version:'Chrome-Google-108.0.5359.99'
        Ex: name_vendor_version:'Flash Player-Adobe-32.0.0.387'
        Ex: name_vendor_version:['Chrome-Google-108*','Flash Player-Adobe-32*']
        """
    ),
    (
        "software_type",
        "String",
        "Yes",
        """
        The type of software: 'application' or 'browser_extension'.

        Ex: software_type:'application'
        """
    ),
    (
        "vendor",
        "String",
        "Yes",
        """
        Name of the application vendor.

        Ex: vendor:'Microsoft Corporation'
        Ex: vendor:'Google'
        Ex: vendor:'CrowdStrike'
        Ex: vendor:['Microsoft*','Google']
        """
    ),
    (
        "version",
        "String",
        "Yes",
        """
        Application version.

        Ex: version:'4.8.4320.0'
        Ex: version:'108.0.5359.99'
        Ex: version:'6.50.16403.0'
        Ex: version:['6.50.16403.0','6.50.16403.1']
        """
    ),
    (
        "versioning_scheme",
        "String",
        "Yes",
        """
        Versioning scheme of the application. Unavailable for browser extensions.

        Ex: versioning_scheme:'semver'
        Ex: versioning_scheme:['semver','calver']
        """
    ),
]

SEARCH_APPLICATIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Applications Guide

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

=== falcon_search_applications FQL filter options ===

""" + generate_md_table(SEARCH_APPLICATIONS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches and multiple values: ['value1','value2']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Boolean values: true or false (no quotes)
• Some fields require specific capitalization (check individual field descriptions)

=== COMMON FILTER EXAMPLES ===
• Find Chrome applications: name:'Chrome'
• Find applications from Microsoft: vendor:'Microsoft Corporation'
• Find recently installed applications: installation_timestamp:>'2024-01-01'
• Find suspicious applications: is_suspicious:true
• Find browser extensions: software_type:'browser_extension'
• Find applications used by a specific user: last_used_user_name:'Administrator'
"""

# List of tuples containing filter options for unmanaged assets
SEARCH_UNMANAGED_ASSETS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "platform_name",
        "String",
        "Yes",
        """
        Operating system platform of the unmanaged asset.

        Ex: platform_name:'Windows'
        Ex: platform_name:'Linux'
        Ex: platform_name:'Mac'
        Ex: platform_name:['Windows','Linux']
        """
    ),
    (
        "os_version",
        "String",
        "Yes",
        """
        Operating system version of the unmanaged asset.

        Ex: os_version:'Windows 10'
        Ex: os_version:'Ubuntu 20.04'
        Ex: os_version:'macOS 12.3'
        Ex: os_version:*'Windows*'
        """
    ),
    (
        "hostname",
        "String",
        "Yes",
        """
        Hostname of the unmanaged asset.

        Ex: hostname:'PC-001'
        Ex: hostname:*'PC-*'
        Ex: hostname:['PC-001','PC-002']
        """
    ),
    (
        "country",
        "String",
        "Yes",
        """
        Country where the unmanaged asset is located.

        Ex: country:'United States of America'
        Ex: country:'Germany'
        Ex: country:['United States of America','Canada']
        """
    ),
    (
        "city",
        "String",
        "Yes",
        """
        City where the unmanaged asset is located.

        Ex: city:'New York'
        Ex: city:'London'
        Ex: city:['New York','Los Angeles']
        """
    ),
    (
        "product_type_desc",
        "String",
        "Yes",
        """
        Product type description of the unmanaged asset.

        Ex: product_type_desc:'Workstation'
        Ex: product_type_desc:'Server'
        Ex: product_type_desc:'Domain Controller'
        Ex: product_type_desc:['Workstation','Server']
        """
    ),
    (
        "external_ip",
        "String",
        "Yes",
        """
        External IP address of the unmanaged asset.

        Ex: external_ip:'192.0.2.1'
        Ex: external_ip:'192.0.2.0/24'
        Ex: external_ip:['192.0.2.1','203.0.113.1']
        """
    ),
    (
        "local_ip_addresses",
        "String",
        "Yes",
        """
        Local IP addresses of the unmanaged asset.

        Ex: local_ip_addresses:'10.0.1.100'
        Ex: local_ip_addresses:'192.168.1.0/24'
        Ex: local_ip_addresses:['10.0.1.100','192.168.1.50']
        """
    ),
    (
        "mac_addresses",
        "String",
        "Yes",
        """
        MAC addresses of the unmanaged asset.

        Ex: mac_addresses:'AA-BB-CC-DD-EE-FF'
        Ex: mac_addresses:*'AA-BB-CC*'
        Ex: mac_addresses:['AA-BB-CC-DD-EE-FF','11-22-33-44-55-66']
        """
    ),
    (
        "first_seen_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time when the unmanaged asset was first discovered.

        Ex: first_seen_timestamp:'2024-01-01T00:00:00Z'
        Ex: first_seen_timestamp:>'2024-01-01T00:00:00Z'
        Ex: first_seen_timestamp:>'now-7d'
        """
    ),
    (
        "last_seen_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time when the unmanaged asset was last seen.

        Ex: last_seen_timestamp:'2024-06-15T12:00:00Z'
        Ex: last_seen_timestamp:>'now-24h'
        Ex: last_seen_timestamp:<'now-30d'
        """
    ),
    (
        "kernel_version",
        "String",
        "Yes",
        """
        Kernel version of the unmanaged asset.
        Linux and Mac: The major version, minor version, and patch version.
        Windows: The build number.

        Ex: kernel_version:'5.4.0'
        Ex: kernel_version:'19041'
        Ex: kernel_version:*'5.4*'
        """
    ),
    (
        "system_manufacturer",
        "String",
        "Yes",
        """
        System manufacturer of the unmanaged asset.

        Ex: system_manufacturer:'Dell Inc.'
        Ex: system_manufacturer:'VMware, Inc.'
        Ex: system_manufacturer:*'Dell*'
        """
    ),
    (
        "system_product_name",
        "String",
        "Yes",
        """
        System product name of the unmanaged asset.

        Ex: system_product_name:'OptiPlex 7090'
        Ex: system_product_name:'VMware Virtual Platform'
        Ex: system_product_name:*'OptiPlex*'
        """
    ),
    (
        "criticality",
        "String",
        "Yes",
        """
        Criticality level assigned to the unmanaged asset.

        Ex: criticality:'Critical'
        Ex: criticality:'High'
        Ex: criticality:'Medium'
        Ex: criticality:'Low'
        Ex: criticality:'Unassigned'
        """
    ),
    (
        "internet_exposure",
        "String",
        "Yes",
        """
        Whether the unmanaged asset is exposed to the internet.

        Ex: internet_exposure:'Yes'
        Ex: internet_exposure:'No'
        Ex: internet_exposure:'Pending'
        Ex: internet_exposure:['Yes','Pending']
        """
    ),
    (
        "discovering_by",
        "String",
        "Yes",
        """
        Method by which the unmanaged asset was discovered.

        Ex: discovering_by:'Passive'
        Ex: discovering_by:'Active'
        Ex: discovering_by:['Passive','Active']
        """
    ),
]

SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Unmanaged Assets Guide

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

=== AUTOMATIC FILTERING ===
This tool automatically filters for unmanaged assets only by adding entity_type:'unmanaged' to all queries.
You do not need to (and cannot) specify entity_type in your filter - it is always set to 'unmanaged'.

=== falcon_search_unmanaged_assets FQL filter options ===

""" + generate_md_table(SEARCH_UNMANAGED_ASSETS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• entity_type:'unmanaged' is automatically applied - do not include in your filter
• Use single quotes around string values: 'value'
• Use square brackets for exact matches and multiple values: ['value1','value2']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Boolean values: true or false (no quotes)
• Some fields require specific capitalization (check individual field descriptions)

=== COMMON FILTER EXAMPLES ===
• Find Windows unmanaged assets: platform_name:'Windows'
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
"""
