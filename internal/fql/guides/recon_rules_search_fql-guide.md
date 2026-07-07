Falcon Query Language (FQL) - Search Recon Monitoring Rules Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: created_timestamp:>'2024-01-01T00:00:00Z'
• ~: field_name:~'partial' (text match — support is per-field, verify live)
• *: field_name:'prefix*' (wildcards — support is per-field, verify live)

=== DATA TYPES ===
• String: 'value'
• Boolean: true/false (no quotes)
• Timestamp: 'YYYY-MM-DDTHH:MM:SSZ' or relative 'now-30d'

=== COMBINING ===
• + = AND: status:'active'+priority:'high'
• , = OR:  topic:'SA_DOMAIN',topic:'SA_EMAIL'
• () = GROUPING: status:'active'+(priority:'high',priority:'medium')

=== COMMON PATTERNS ===
• All active rules: status:'active'
• High-priority rules: priority:'high'
• Domain monitoring rules: topic:'SA_DOMAIN'
• Typosquatting rules: topic:'SA_TYPOSQUATTING'
• Rules with breach monitoring on: breach_monitoring_enabled:true
• Public rules: permissions:'public'
• Recently created: created_timestamp:>'now-30d'

=== falcon_search_recon_rules FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|id|String|Unique rule identifier. Ex: rule-abc123|
|cid|String|Customer ID (CID). Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158|
|user_uuid|String|UUID of the user who owns the rule. Ex: 00000000-0000-0000-0000-000000000000|
|topic|String|Rule topic category. Confirmed values: - SA_DOMAIN: Company domain monitoring - SA_TYPOSQUATTING: Typosquatting domain detection - SA_EMAIL: Email address monitoring - SA_IP: IP address monitoring - SA_BRAND_PRODUCT: Brand and product mentions Ex: SA_DOMAIN|
|priority|String|Rule priority level. Confirmed values: - low, medium, high Ex: medium|
|permissions|String|Rule visibility permissions. Possible values: - private: Visible only to the owning user - public: Visible to all users in the CID Ex: public|
|status|String|Rule operational status. Confirmed values: - active: Rule is actively monitoring - inactive: Rule is paused (valid syntax; unconfirmed in live test) Ex: active|
|filter|String|The rule's own filter/keyword expression used to match intelligence items.|
|breach_monitoring_enabled|Boolean|Whether the rule has breach/exposed-data monitoring enabled. Ex: true|
|substring_matching_enabled|Boolean|Whether the rule uses substring/partial matching. Ex: false|
|created_timestamp|Timestamp|When the rule was created (ISO 8601 / relative). Ex: 2024-01-01T00:00:00Z|
|last_updated_timestamp|Timestamp|When the rule was last updated (ISO 8601 / relative). Ex: 2024-06-01T00:00:00Z|

=== COMPLEX FILTER EXAMPLES ===

# Enabled high-priority domain monitoring rules
status:'active'+priority:'high'+topic:'SA_DOMAIN'

# All typosquatting rules with breach monitoring enabled
topic:'SA_TYPOSQUATTING'+breach_monitoring_enabled:true

# Recently updated rules (past 7 days)
last_updated_timestamp:>'now-7d'

# Public rules for domain or email monitoring
permissions:'public'+(topic:'SA_DOMAIN',topic:'SA_EMAIL')
