"""
Contains Discover Applications resources.
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
