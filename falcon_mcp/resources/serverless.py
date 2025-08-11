"""
Contains Serverless Vulnerabilities resources.
"""

from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, operators, description)
SERVERLESS_VULNERABILITIES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "application_name",
        "String",
        "Yes",
        """
        Name of the application associated with the serverless function.
        
        Ex: application_name:'my-lambda-app'
        """
    ),
    (
        "application_name_version",
        "String",
        "Yes",
        """
        Version of the application associated with the serverless function.
        
        Ex: application_name_version:'1.0.0'
        """
    ),
    (
        "cid",
        "String",
        "No",
        """
        Unique system-generated customer identifier (CID) of the account.
        
        Ex: cid:'0123456789ABCDEFGHIJKLMNOPQRSTUV'
        """
    ),
    (
        "cloud_account_id",
        "String",
        "Yes",
        """
        Unique identifier of the cloud account where the serverless function is deployed.
        
        Ex: cloud_account_id:'123456789012'
        """
    ),
    (
        "cloud_account_name",
        "String",
        "Yes",
        """
        Name of the cloud account where the serverless function is deployed.
        
        Ex: cloud_account_name:'production-account'
        """
    ),
    (
        "cloud_provider",
        "String",
        "Yes",
        """
        Name of the cloud service provider hosting the serverless function.
        Values: AWS, Azure, GCP
        
        Ex: cloud_provider:'AWS'
        """
    ),
    (
        "cve_id",
        "String",
        "Yes",
        """
        Unique identifier for a vulnerability as cataloged in the National Vulnerability Database (NVD).
        Supports multiple values and negation.
        
        Ex: cve_id:['CVE-2022-1234']
        Ex: cve_id:['CVE-2022-1234','CVE-2023-5678']
        """
    ),
    (
        "cvss_base_score",
        "Number",
        "Yes",
        """
        Common Vulnerability Scoring System (CVSS) base score of the vulnerability.
        
        Ex: cvss_base_score:>7.0
        Ex: cvss_base_score:<5.0
        """
    ),
    (
        "exprt_rating",
        "String",
        "Yes",
        """
        ExPRT rating assigned by CrowdStrike's predictive AI rating system.
        Values: UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL
        
        Ex: exprt_rating:'HIGH'
        Ex: exprt_rating:['HIGH','CRITICAL']
        """
    ),
    (
        "first_seen_timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time when this vulnerability was first detected in the serverless function.
        
        Ex: first_seen_timestamp:>'2023-01-01'
        Ex: first_seen_timestamp:<'2023-12-31'
        """
    ),
    (
        "function_name",
        "String",
        "Yes",
        """
        Name of the serverless function where the vulnerability was detected.
        
        Ex: function_name:'process-payment'
        """
    ),
    (
        "function_resource_id",
        "String",
        "Yes",
        """
        Unique resource identifier of the serverless function.
        
        Ex: function_resource_id:'arn:aws:lambda:us-east-1:123456789012:function:my-function'
        """
    ),
    (
        "is_supported",
        "Boolean",
        "No",
        """
        Indicates if the serverless function is supported for vulnerability scanning.
        
        Ex: is_supported:true
        """
    ),
    (
        "is_valid_asset_id",
        "Boolean",
        "No",
        """
        Indicates if the asset ID associated with the serverless function is valid.
        
        Ex: is_valid_asset_id:true
        """
    ),
    (
        "layer",
        "String",
        "Yes",
        """
        Layer in the serverless function where the vulnerability was detected.
        
        Ex: layer:'runtime'
        Ex: layer:'dependency'
        """
    ),
    (
        "region",
        "String",
        "Yes",
        """
        Cloud region where the serverless function is deployed.
        
        Ex: region:'us-east-1'
        Ex: region:['us-east-1','us-west-2']
        """
    ),
    (
        "runtime",
        "String",
        "Yes",
        """
        Runtime environment of the serverless function.
        Values: nodejs, python, java, ruby, go, dotnet
        
        Ex: runtime:'nodejs'
        Ex: runtime:['python','nodejs']
        """
    ),
    (
        "severity",
        "String",
        "Yes",
        """
        Severity level of the vulnerability.
        Values: UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL
        
        Ex: severity:'HIGH'
        Ex: severity:['HIGH','CRITICAL']
        """
    ),
    (
        "timestamp",
        "Timestamp",
        "Yes",
        """
        Date and time when the vulnerability was last updated.
        
        Ex: timestamp:>'2023-06-01'
        Ex: timestamp:<'2023-12-31'
        """
    ),
    (
        "type",
        "String",
        "Yes",
        """
        Type of the vulnerability.
        Values: Vulnerability, Misconfiguration, Unsupported software
        
        Ex: type:'Vulnerability'
        Ex: type:!'Misconfiguration'
        """
    ),
]

SERVERLESS_VULNERABILITIES_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Serverless Vulnerabilities Guide

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

=== falcon_search_serverless_vulnerabilities FQL filter options ===

""" + generate_md_table(SERVERLESS_VULNERABILITIES_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches and multiple values: ['value1','value2']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• For case-insensitive filtering, add .insensitive to field names
• Boolean values: true or false (no quotes)
• Wildcards (*) are unsupported in this API
• Some fields require specific capitalization (check individual field descriptions)

=== COMMON FILTER EXAMPLES ===
• Filter by cloud provider: cloud_provider:'AWS'
• High severity vulnerabilities: severity:'HIGH'
• Recent vulnerabilities: first_seen_timestamp:>'2023-01-01'
• Filter by specific runtime: runtime:'nodejs'
• Filter by region: region:'us-east-1'
• Critical vulnerabilities in a specific account: severity:'CRITICAL'+cloud_account_id:'123456789012'
• Filter by function name: function_name:'payment-processor'
• High CVSS score vulnerabilities: cvss_base_score:>7.0
"""
