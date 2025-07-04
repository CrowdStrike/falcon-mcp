"""
Contains Detections resources.
"""

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

=== IDENTIFICATION & CORE ===
• composite_id: Unique detection identifier
• aggregate_id: Related detection group identifier
• cid: Customer ID
• agent_id: Falcon agent identifier
• pattern_id: Detection pattern identifier

=== ASSIGNMENT & WORKFLOW ===
• assigned_to_name: Person assigned to this detection
• assigned_to_uid: Assigned user identifier
• assigned_to_uuid: Assigned user UUID
• status: Detection status (new, in_progress, closed, reopened)

=== TIMESTAMPS ===
• created_timestamp: When detection was created
• updated_timestamp: Last modification time
• timestamp: Detection occurrence timestamp

=== THREAT INTELLIGENCE ===
• confidence: Confidence level (1-100)
• severity: Detection severity level
• tactic: MITRE ATT&CK tactic
• tactic_id: MITRE ATT&CK tactic ID
• technique: MITRE ATT&CK technique
• technique_id: MITRE ATT&CK technique ID
• objective: Attack objective description

=== DETECTION METADATA ===
• name: Detection name/title
• display_name: Human-readable detection name
• description: Detection description
• type: Detection type classification
• scenario: Detection scenario

=== SYSTEM & PLATFORM ===
• platform: Operating system platform
• show_in_ui: Whether detection appears in UI (true/false)
• data_domains: Data classification domains

=== PRODUCT FILTERING ===
• product: Source Falcon product
    - 'epp' (Endpoint Protection)
    - 'idp' (Identity Protection)
    - 'mobile' (Falcon for Mobile)
    - 'xdr' (Falcon XDR)
    - 'overwatch' (OverWatch)
    - 'cwpp' (Cloud Workload Protection)
    - 'ngsiem' (Next-Gen SIEM)
    - 'thirdparty' (Third party data)
    - 'data-protection' (Data Protection)

=== SOURCE INFORMATION ===
• source_products: Products that generated this detection
• source_vendors: Vendor sources for the detection

=== TAGS & CLASSIFICATION ===
• tags: Detection classification tags

=== EXAMPLE USAGE ===

=== STATUS-BASED SEARCHES ===
• status:'new'
• status:'in_progress'
• status:'closed'
• status:'reopened'

=== PRODUCT-SPECIFIC SEARCHES ===
• product:'epp'
• product:'idp'
• product:'xdr'
• product:'overwatch'

=== SEVERITY & CONFIDENCE SEARCHES ===
• confidence:>80
• confidence:>=50

🔥 SEVERITY NUMERIC MAPPING (Critical for Proper Filtering):
• Critical: severity:>=90 (or severity:90 exactly)
• High: severity:>=70 (or severity:70 exactly)
• Medium: severity:>=50 (or severity:50 exactly)
• Low: severity:>=20 (covers range 20-40)
• Informational: severity:<=10 (covers range 2-5)

• severity:>=90
• severity:>=70
• severity:>=50
• severity:70
• severity:<=10

=== ASSIGNMENT SEARCHES ===
• assigned_to_name:!*
• assigned_to_name:'john.doe'

=== TIME-BASED SEARCHES ===
• created_timestamp:>'2024-01-20T00:00:00Z'
• created_timestamp:>='2024-01-15T00:00:00Z'+created_timestamp:<='2024-01-20T00:00:00Z'
• updated_timestamp:>'2024-01-19T00:00:00Z'

=== THREAT INTELLIGENCE SEARCHES ===
• tactic:'Persistence'
• technique_id:'T1055'
• objective:'*credential*'

=== ADVANCED COMBINED SEARCHES ===
• status:'new'+confidence:>75+product:'epp'
• product:'xdr'+status:'in_progress'+assigned_to_name:*
• created_timestamp:>'2024-01-18T00:00:00Z'+assigned_to_name:!*+confidence:>80
• product:'overwatch'+tactic:'Persistence'

=== BULK FILTERING SEARCHES ===
• (product:'epp'),(product:'xdr'),(product:'idp')
• (status:'new'),(status:'in_progress')
• (status:'new'),(status:'reopened')

=== INVESTIGATION-FOCUSED SEARCHES ===
• pattern_id:'12345'
• aggregate_id:'agg-67890'
• tags:'malware'
• show_in_ui:true

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Status values are: new, in_progress, closed, reopened
• Product filtering enables product-specific detection analysis
• Confidence values range from 1-100
• Complex queries may take longer to execute
• include_hidden parameter shows previously hidden detections
"""
