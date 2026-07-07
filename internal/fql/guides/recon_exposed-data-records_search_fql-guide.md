Falcon Query Language (FQL) - Search Recon Exposed-Data Records Guide

=== ABOUT EXPOSED-DATA RECORDS ===
Exposed-data records are the underlying leaked credential and PII rows associated
with Recon notifications. One notification may have many records. Use
falcon_search_recon_notifications first to find matching notification IDs, then
use this tool to retrieve the detailed credential/PII rows.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value' (not equal)
• >, >=, <, <=: created_date:>'2024-01-01T00:00:00Z'
• ~: field_name:~'partial' (text match — support is per-field, verify live)
• *: field_name:'prefix*' (wildcards — support is per-field, verify live)

=== DATA TYPES ===
• String: 'value'
• Boolean: true/false (no quotes)
• Timestamp: 'YYYY-MM-DDTHH:MM:SSZ' or relative 'now-7d'

=== COMBINING ===
• + = AND: rule.topic:'SA_DOMAIN'+credential_status:'confirmed_active'
• , = OR:  site:'pastebin.com',site:'telegram.org'
• () = GROUPING: (site:'pastebin.com',site:'telegram.org')+created_date:>'now-7d'

=== COMMON PATTERNS ===
• Records for a specific notification: notification_id:'<id>'
• By domain: domain:'example.com'
• By email: email:'user@example.com'
• By credential status: credential_status:'newly_reported'
• From a specific site: site:'stealer_logs'
• Recent records (past 7 days): created_date:>'now-7d'
• By monitoring rule topic: rule.topic:'SA_DOMAIN'
• Full-text search: _all:'example.com'

=== falcon_search_recon_exposed_data_records FQL filter available fields ===

|Name|Type|Description|
|-|-|-|
|id|String|Unique exposed-data record identifier.|
|cid|String|Customer ID (CID). Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158|
|user_uuid|String|UUID of the user who owns the monitoring rule that triggered this record.|
|notification_id|String|ID of the parent Recon notification this record is associated with. Ex: abc123def456|
|notification_group_id|String|Notification group ID grouping related records.|
|created_date|Timestamp|When the exposed-data record was created (ISO 8601 / relative). Ex: 2024-06-01T00:00:00Z|
|exposure_date|Timestamp|When the credentials/data were exposed or breached (ISO 8601 / relative). Ex: 2024-01-01T00:00:00Z|
|rule.id|String|ID of the monitoring rule that matched this record.|
|rule.name|String|Name of the monitoring rule that matched this record. Ex: Company Domain Watch|
|rule.topic|String|Topic of the monitoring rule. Possible values include: SA_BRAND_PRODUCT, SA_DOMAIN, SA_EMAIL, SA_IP, SA_TYPOSQUATTING Ex: SA_DOMAIN|
|source_category|String|Category of the intelligence source where the data was found. Ex: darkweb_forum, paste_site, breach_compilation|
|site|String|Specific site where the data was exposed. Ex: pastebin.com, telegram.org|
|site_id|String|Identifier of the specific site.|
|author|String|Username/handle of the actor who posted the exposed data.|
|author_id|String|Identifier for the author on the source platform.|
|email|String|Email address found in the exposed data. Ex: user@example.com|
|domain|String|Domain associated with the exposed credentials. Ex: example.com|
|credentials_domain|String|Domain used for credential authentication. Ex: example.com|
|credentials_url|String|URL associated with the exposed credentials.|
|credentials_ip|String|IP address associated with the exposed credentials.|
|login_id|String|Login username or identifier found in the exposed data. Ex: jsmith|
|credential_status|String|Status of the exposed credential. Confirmed values: - newly_reported: First time this credential has appeared - previously_reported: Seen in a prior breach - confirmed_active: Verified as currently active Ex: newly_reported|
|user_id|String|User identifier on the source platform.|
|user_name|String|Username on the source platform.|
|display_name|String|Display name associated with the exposed account.|
|full_name|String|Full name of the person in the exposed data.|
|hash_type|String|Type of hash for the exposed password (if hashed). Ex: md5, sha1, bcrypt|
|user_ip|String|IP address of the exposed user.|
|phone_number|String|Phone number found in the exposed data.|
|company|String|Company name associated with the exposed account.|
|job_position|String|Job position/title in the exposed data.|
|file.name|String|Name of the file containing the exposed data.|
|file.complete_data_set|Boolean|Whether the file represents a complete data set. Ex: true|
|file.download_urls|String|Download URL(s) for the exposed data file.|
|location.country_code|String|Country code from the exposed data location. Ex: US, GB, DE|
|location.city|String|City from the exposed data location.|
|location.state|String|State/province from the exposed data location.|
|location.postal_code|String|Postal code from the exposed data location.|
|location.federal_district|String|Federal district from the exposed data location.|
|location.federal_admin_region|String|Federal administrative region from the exposed data location.|
|social.twitter_id|String|Twitter/X user ID found in the exposed data.|
|social.instagram_id|String|Instagram user ID found in the exposed data.|
|social.facebook_id|String|Facebook user ID found in the exposed data.|
|social.skype_id|String|Skype ID found in the exposed data.|
|financial.credit_card|String|Credit card number found in the exposed data.|
|financial.bank_account|String|Bank account information found in the exposed data.|
|financial.crypto_currency_addresses|String|Cryptocurrency wallet addresses found in the exposed data.|
|bot.operating_system.hardware_id|String|Hardware ID of a bot/stealer associated with the data.|
|bot.bot_id|String|Bot ID of a stealer/info-stealer associated with the record.|
|_all|String|Special field: search across all indexed fields in the record. Useful for broad text searches. Ex: _all:'example.com'|

=== COMPLEX FILTER EXAMPLES ===

# Newly reported credentials for a specific domain, past 30 days
domain:'example.com'+credential_status:'newly_reported'+created_date:>'now-30d'

# All records associated with a specific notification
notification_id:'<notification_id_here>'

# Records from domain monitoring rules, recent
rule.topic:'SA_DOMAIN'+created_date:>'now-7d'

# Records by credential status across all rule topics
credential_status:'newly_reported',credential_status:'confirmed_active'
