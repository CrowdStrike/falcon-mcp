Falcon Query Language (FQL) - Search Recon Notifications Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: field_name:>50 (comparison, mainly for numbers)
• ~: field_name:~'partial' (text match, case insensitive — support is per-field, verify live)
• !~: field_name:!~'exclude' (not text match)
• *: field_name:'prefix*' or field_name:'*suffix*' (wildcards — support is per-field, verify live)

=== DATA TYPES ===
• String: 'value'
• Number: 123 (no quotes)
• Boolean: true/false (no quotes)
• Timestamp: 'YYYY-MM-DDTHH:MM:SSZ' or relative 'now-24h'

=== WILDCARDS ===
⚠️ FQL operator support is per-operation. Query APIs silently return empty (HTTP 200)
   for unsupported fields/operators — empty results do NOT confirm a filter is correct.
   Use exact-match filters on confirmed fields when in doubt.
✅ Relative timestamps: created_date:>'now-24h' (lowercase 'now', quoted)

=== COMBINING ===
• + = AND: status:'new'+rule_priority:'high'
• , = OR:  rule_topic:'SA_DOMAIN',rule_topic:'SA_TYPOSQUATTING'
• () = GROUPING: status:'new'+(rule_priority:'high',rule_priority:'medium')

=== ASSIGNEE NOTE ===
⚠️ assigned_to_uuid requires a user UUID, NOT an email address.
   Look up the UUID in the Falcon console under User Management before filtering.

=== COMMON PATTERNS ===
• New high-priority notifications: status:'new'+rule_priority:'high'
• Recent notifications (past 24h): created_date:>'now-24h'
• Recent notifications (past 7 days): created_date:>'now-7d'
• By site (e.g. stealer logs): item_site:'stealer_logs'
• By item type: item_type:'exposed_data'
• Leaked credential notifications: rule_topic:'SA_DOMAIN'+item_type:'exposed_data'
• Typosquatting notifications: rule_topic:'SA_TYPOSQUATTING'
• By monitoring rule: rule_name:'My Domain Watch'
• By rule ID: rule_id:'rule-abc123'

=== falcon_search_recon_notifications FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|id|String|Unique notification identifier. Ex: abc123def456|
|cid|String|Customer ID (CID). Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158|
|user_uuid|String|UUID of the user who owns the monitoring rule that triggered this notification. Ex: 00000000-0000-0000-0000-000000000000|
|status|String|Notification review status. Confirmed values: - new: Newly triggered, not yet reviewed - in-progress: Under investigation - closed-false-positive: Reviewed, not a real threat - closed-true-positive: Reviewed, confirmed threat Ex: new|
|rule_id|String|ID of the monitoring rule that triggered this notification. Ex: rule-abc123|
|rule_name|String|Name of the monitoring rule that triggered this notification. Ex: Company Domain Watch|
|rule_topic|String|Topic category of the monitoring rule. Confirmed values: - SA_DOMAIN: Company domain monitoring - SA_TYPOSQUATTING: Typosquatting domain detection - SA_EMAIL: Email address monitoring - SA_IP: IP address monitoring - SA_BRAND_PRODUCT: Brand and product mentions Ex: SA_DOMAIN|
|rule_priority|String|Priority of the monitoring rule. Confirmed values: - low, medium, high Ex: medium|
|item_type|String|Type of the intelligence item that triggered the notification. Confirmed value: exposed_data Ex: exposed_data|
|item_site|String|Site or platform where the intelligence item was found. Use this to filter notifications from specific dark-web forums or messaging platforms. Confirmed value: stealer_logs Ex: stealer_logs, telegram.org|
|created_date|Timestamp|When the notification was created (ISO 8601 / relative). Relative dates: 'now-24h', 'now-7d', 'now-30d' Ex: 2024-06-01T00:00:00Z|
|updated_date|Timestamp|When the notification was last updated (ISO 8601 / relative). Ex: 2024-06-01T00:00:00Z|
|assigned_to_uuid|String|UUID of the analyst the notification is assigned to. NOTE: This field requires a UUID, not an email address. To find a user's UUID, look it up in the Falcon console (Support → User Management) before filtering here. Ex: 00000000-0000-0000-0000-000000000000|
|breach_summary.credential_statuses|String|NOTE: Live testing confirmed this field causes a 400 FQL parse failure on QueryNotificationsV1 — it is NOT queryable via FQL. Breach credential data is available in the notification response body (notification.breach_summary) but cannot be used as a filter. To find breach notifications, filter by rule_topic:'SA_DOMAIN' combined with item_type:'exposed_data' instead.|
|breach_summary.is_retroactively_deduped|Boolean|NOTE: Queryability of this field has not been confirmed live. Use with caution — query APIs silently return empty (not 400) for unsupported fields, so empty results do not confirm it works. Ex: true|
|typosquatting.id|String|NOTE: The typosquatting.* fields below reflect the response schema from GetNotificationsDetailedV1. Their queryability on QueryNotificationsV1 has not been confirmed live. Query APIs silently return empty (HTTP 200) for unsupported fields — empty results do NOT confirm a filter worked. Use rule_topic:'SA_TYPOSQUATTING' as the reliable filter for typosquatting notifications. ID of the typosquatting domain record. Ex: typo-abc123|
|typosquatting.unicode_format|String|Unicode (human-readable) format of the typosquatting domain. Ex: crowdstr1ke.com|
|typosquatting.punycode_format|String|Punycode-encoded format of the typosquatting domain. Ex: xn--crowdstrke-n2a.com|
|typosquatting.parent_domain.id|String|ID of the parent domain being spoofed.|
|typosquatting.parent_domain.unicode_format|String|Unicode format of the parent domain being spoofed. Ex: crowdstrike.com|
|typosquatting.parent_domain.punycode_format|String|Punycode format of the parent domain being spoofed.|
|typosquatting.base_domain.id|String|ID of the typosquatting base domain.|
|typosquatting.base_domain.unicode_format|String|Unicode format of the typosquatting base domain.|
|typosquatting.base_domain.punycode_format|String|Punycode format of the typosquatting base domain.|
|typosquatting.base_domain.is_registered|Boolean|Whether the typosquatting base domain is currently registered. Ex: true|
|typosquatting.base_domain.whois.registrar.name|String|Name of the registrar for the typosquatting domain. Ex: GoDaddy|
|typosquatting.base_domain.whois.registrar.status|String|Registrar status of the typosquatting domain.|
|typosquatting.base_domain.whois.registrant.email|String|Registrant email for the typosquatting domain.|
|typosquatting.base_domain.whois.registrant.name|String|Registrant name for the typosquatting domain.|
|typosquatting.base_domain.whois.registrant.org|String|Registrant organization for the typosquatting domain.|
|typosquatting.base_domain.whois.name_servers|String|Name servers for the typosquatting domain.|

=== COMPLEX FILTER EXAMPLES ===

# New high-priority notifications from the past 7 days
status:'new'+rule_priority:'high'+created_date:>'now-7d'

# Typosquatting notifications for any registered domain
rule_topic:'SA_TYPOSQUATTING'+created_date:>'now-30d'

# Exposed-data notifications from stealer logs
item_type:'exposed_data'+item_site:'stealer_logs'

# Domain monitoring notifications, unreviewed
rule_topic:'SA_DOMAIN'+status:'new'

# Unreviewed brand and domain notifications
status:'new'+(rule_topic:'SA_BRAND_PRODUCT',rule_topic:'SA_DOMAIN')
