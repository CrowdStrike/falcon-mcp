"""
Contains Recon resources.
"""

from falcon_mcp.common.utils import generate_md_table

# ---------------------------------------------------------------------------
# Notifications FQL filters
# ---------------------------------------------------------------------------

SEARCH_RECON_NOTIFICATIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        """
        Unique notification identifier.
        Ex: abc123def456
        """,
    ),
    (
        "cid",
        "String",
        """
        Customer ID (CID).
        Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158
        """,
    ),
    (
        "user_uuid",
        "String",
        """
        UUID of the user who owns the monitoring rule that triggered
        this notification.
        Ex: 00000000-0000-0000-0000-000000000000
        """,
    ),
    (
        "status",
        "String",
        """
        Notification review status. Confirmed values:
        - new: Newly triggered, not yet reviewed
        - in-progress: Under investigation
        - closed-false-positive: Reviewed, not a real threat
        - closed-true-positive: Reviewed, confirmed threat
        Ex: new
        """,
    ),
    (
        "rule_id",
        "String",
        """
        ID of the monitoring rule that triggered this notification.
        Ex: rule-abc123
        """,
    ),
    (
        "rule_name",
        "String",
        """
        Name of the monitoring rule that triggered this notification.
        Ex: Company Domain Watch
        """,
    ),
    (
        "rule_topic",
        "String",
        """
        Topic category of the monitoring rule. Confirmed values:
        - SA_DOMAIN: Company domain monitoring
        - SA_TYPOSQUATTING: Typosquatting domain detection
        - SA_EMAIL: Email address monitoring
        - SA_IP: IP address monitoring
        - SA_BRAND_PRODUCT: Brand and product mentions
        Ex: SA_DOMAIN
        """,
    ),
    (
        "rule_priority",
        "String",
        """
        Priority of the monitoring rule. Confirmed values:
        - low, medium, high
        Ex: medium
        """,
    ),
    (
        "item_type",
        "String",
        """
        Type of the intelligence item that triggered the notification.
        Confirmed value: exposed_data
        Ex: exposed_data
        """,
    ),
    (
        "item_site",
        "String",
        """
        Site or platform where the intelligence item was found.
        Use this to filter notifications from specific dark-web
        forums or messaging platforms.
        Confirmed value: stealer_logs
        Ex: stealer_logs, telegram.org
        """,
    ),
    (
        "created_date",
        "Timestamp",
        """
        When the notification was created (ISO 8601 / relative).
        Relative dates: 'now-24h', 'now-7d', 'now-30d'
        Ex: 2024-06-01T00:00:00Z
        """,
    ),
    (
        "updated_date",
        "Timestamp",
        """
        When the notification was last updated (ISO 8601 / relative).
        Ex: 2024-06-01T00:00:00Z
        """,
    ),
    (
        "assigned_to_uuid",
        "String",
        """
        UUID of the analyst the notification is assigned to.
        NOTE: This field requires a UUID, not an email address.
        To find a user's UUID, look it up in the Falcon console
        (Support → User Management) before filtering here.
        Ex: 00000000-0000-0000-0000-000000000000
        """,
    ),
    (
        "breach_summary.credential_statuses",
        "String",
        """
        NOTE: Live testing confirmed this field causes a 400 FQL parse
        failure on QueryNotificationsV1 — it is NOT queryable via FQL.
        Breach credential data is available in the notification response
        body (notification.breach_summary) but cannot be used as a filter.
        To find breach notifications, filter by rule_topic:'SA_DOMAIN'
        combined with item_type:'exposed_data' instead.
        """,
    ),
    (
        "breach_summary.is_retroactively_deduped",
        "Boolean",
        """
        NOTE: Queryability of this field has not been confirmed live.
        Use with caution — query APIs silently return empty (not 400)
        for unsupported fields, so empty results do not confirm it works.
        Ex: true
        """,
    ),
    (
        "typosquatting.id",
        "String",
        """
        NOTE: The typosquatting.* fields below reflect the response schema
        from GetNotificationsDetailedV1. Their queryability on
        QueryNotificationsV1 has not been confirmed live. Query APIs
        silently return empty (HTTP 200) for unsupported fields — empty
        results do NOT confirm a filter worked. Use rule_topic:'SA_TYPOSQUATTING'
        as the reliable filter for typosquatting notifications.

        ID of the typosquatting domain record.
        Ex: typo-abc123
        """,
    ),
    (
        "typosquatting.unicode_format",
        "String",
        """
        Unicode (human-readable) format of the typosquatting domain.
        Ex: crowdstr1ke.com
        """,
    ),
    (
        "typosquatting.punycode_format",
        "String",
        """
        Punycode-encoded format of the typosquatting domain.
        Ex: xn--crowdstrke-n2a.com
        """,
    ),
    (
        "typosquatting.parent_domain.id",
        "String",
        """
        ID of the parent domain being spoofed.
        """,
    ),
    (
        "typosquatting.parent_domain.unicode_format",
        "String",
        """
        Unicode format of the parent domain being spoofed.
        Ex: crowdstrike.com
        """,
    ),
    (
        "typosquatting.parent_domain.punycode_format",
        "String",
        """
        Punycode format of the parent domain being spoofed.
        """,
    ),
    (
        "typosquatting.base_domain.id",
        "String",
        """
        ID of the typosquatting base domain.
        """,
    ),
    (
        "typosquatting.base_domain.unicode_format",
        "String",
        """
        Unicode format of the typosquatting base domain.
        """,
    ),
    (
        "typosquatting.base_domain.punycode_format",
        "String",
        """
        Punycode format of the typosquatting base domain.
        """,
    ),
    (
        "typosquatting.base_domain.is_registered",
        "Boolean",
        """
        Whether the typosquatting base domain is currently registered.
        Ex: true
        """,
    ),
    (
        "typosquatting.base_domain.whois.registrar.name",
        "String",
        """
        Name of the registrar for the typosquatting domain.
        Ex: GoDaddy
        """,
    ),
    (
        "typosquatting.base_domain.whois.registrar.status",
        "String",
        """
        Registrar status of the typosquatting domain.
        """,
    ),
    (
        "typosquatting.base_domain.whois.registrant.email",
        "String",
        """
        Registrant email for the typosquatting domain.
        """,
    ),
    (
        "typosquatting.base_domain.whois.registrant.name",
        "String",
        """
        Registrant name for the typosquatting domain.
        """,
    ),
    (
        "typosquatting.base_domain.whois.registrant.org",
        "String",
        """
        Registrant organization for the typosquatting domain.
        """,
    ),
    (
        "typosquatting.base_domain.whois.name_servers",
        "String",
        """
        Name servers for the typosquatting domain.
        """,
    ),
]

SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Recon Notifications Guide

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

"""
    + generate_md_table(SEARCH_RECON_NOTIFICATIONS_FQL_FILTERS)
    + """

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
"""
)

# ---------------------------------------------------------------------------
# Monitoring Rules FQL filters
# ---------------------------------------------------------------------------

SEARCH_RECON_RULES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        """
        Unique rule identifier.
        Ex: rule-abc123
        """,
    ),
    (
        "cid",
        "String",
        """
        Customer ID (CID).
        Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158
        """,
    ),
    (
        "user_uuid",
        "String",
        """
        UUID of the user who owns the rule.
        Ex: 00000000-0000-0000-0000-000000000000
        """,
    ),
    (
        "topic",
        "String",
        """
        Rule topic category. Confirmed values:
        - SA_DOMAIN: Company domain monitoring
        - SA_TYPOSQUATTING: Typosquatting domain detection
        - SA_EMAIL: Email address monitoring
        - SA_IP: IP address monitoring
        - SA_BRAND_PRODUCT: Brand and product mentions
        Ex: SA_DOMAIN
        """,
    ),
    (
        "priority",
        "String",
        """
        Rule priority level. Confirmed values:
        - low, medium, high
        Ex: medium
        """,
    ),
    (
        "permissions",
        "String",
        """
        Rule visibility permissions. Possible values:
        - private: Visible only to the owning user
        - public: Visible to all users in the CID
        Ex: public
        """,
    ),
    (
        "status",
        "String",
        """
        Rule operational status. Confirmed values:
        - active: Rule is actively monitoring
        - inactive: Rule is paused (valid syntax; unconfirmed in live test)
        Ex: active
        """,
    ),
    (
        "filter",
        "String",
        """
        The rule's own filter/keyword expression used to match
        intelligence items.
        """,
    ),
    (
        "breach_monitoring_enabled",
        "Boolean",
        """
        Whether the rule has breach/exposed-data monitoring enabled.
        Ex: true
        """,
    ),
    (
        "substring_matching_enabled",
        "Boolean",
        """
        Whether the rule uses substring/partial matching.
        Ex: false
        """,
    ),
    (
        "created_timestamp",
        "Timestamp",
        """
        When the rule was created (ISO 8601 / relative).
        Ex: 2024-01-01T00:00:00Z
        """,
    ),
    (
        "last_updated_timestamp",
        "Timestamp",
        """
        When the rule was last updated (ISO 8601 / relative).
        Ex: 2024-06-01T00:00:00Z
        """,
    ),
]

SEARCH_RECON_RULES_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Recon Monitoring Rules Guide

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

"""
    + generate_md_table(SEARCH_RECON_RULES_FQL_FILTERS)
    + """

=== COMPLEX FILTER EXAMPLES ===

# Enabled high-priority domain monitoring rules
status:'active'+priority:'high'+topic:'SA_DOMAIN'

# All typosquatting rules with breach monitoring enabled
topic:'SA_TYPOSQUATTING'+breach_monitoring_enabled:true

# Recently updated rules (past 7 days)
last_updated_timestamp:>'now-7d'

# Public rules for domain or email monitoring
permissions:'public'+(topic:'SA_DOMAIN',topic:'SA_EMAIL')
"""
)

# ---------------------------------------------------------------------------
# Exposed-Data Records FQL filters
# ---------------------------------------------------------------------------

SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        """
        Unique exposed-data record identifier.
        """,
    ),
    (
        "cid",
        "String",
        """
        Customer ID (CID).
        Ex: d61501xxxxxxxxxxxxxxxxxxxxa2da2158
        """,
    ),
    (
        "user_uuid",
        "String",
        """
        UUID of the user who owns the monitoring rule
        that triggered this record.
        """,
    ),
    (
        "notification_id",
        "String",
        """
        ID of the parent Recon notification this record
        is associated with.
        Ex: abc123def456
        """,
    ),
    (
        "notification_group_id",
        "String",
        """
        Notification group ID grouping related records.
        """,
    ),
    (
        "created_date",
        "Timestamp",
        """
        When the exposed-data record was created (ISO 8601 / relative).
        Ex: 2024-06-01T00:00:00Z
        """,
    ),
    (
        "exposure_date",
        "Timestamp",
        """
        When the credentials/data were exposed or breached
        (ISO 8601 / relative).
        Ex: 2024-01-01T00:00:00Z
        """,
    ),
    (
        "rule.id",
        "String",
        """
        ID of the monitoring rule that matched this record.
        """,
    ),
    (
        "rule.name",
        "String",
        """
        Name of the monitoring rule that matched this record.
        Ex: Company Domain Watch
        """,
    ),
    (
        "rule.topic",
        "String",
        """
        Topic of the monitoring rule. Possible values include:
        SA_BRAND_PRODUCT, SA_DOMAIN, SA_EMAIL, SA_IP,
        SA_TYPOSQUATTING
        Ex: SA_DOMAIN
        """,
    ),
    (
        "source_category",
        "String",
        """
        Category of the intelligence source where the data was found.
        Ex: darkweb_forum, paste_site, breach_compilation
        """,
    ),
    (
        "site",
        "String",
        """
        Specific site where the data was exposed.
        Ex: pastebin.com, telegram.org
        """,
    ),
    (
        "site_id",
        "String",
        """
        Identifier of the specific site.
        """,
    ),
    (
        "author",
        "String",
        """
        Username/handle of the actor who posted the exposed data.
        """,
    ),
    (
        "author_id",
        "String",
        """
        Identifier for the author on the source platform.
        """,
    ),
    (
        "email",
        "String",
        """
        Email address found in the exposed data.
        Ex: user@example.com
        """,
    ),
    (
        "domain",
        "String",
        """
        Domain associated with the exposed credentials.
        Ex: example.com
        """,
    ),
    (
        "credentials_domain",
        "String",
        """
        Domain used for credential authentication.
        Ex: example.com
        """,
    ),
    (
        "credentials_url",
        "String",
        """
        URL associated with the exposed credentials.
        """,
    ),
    (
        "credentials_ip",
        "String",
        """
        IP address associated with the exposed credentials.
        """,
    ),
    (
        "login_id",
        "String",
        """
        Login username or identifier found in the exposed data.
        Ex: jsmith
        """,
    ),
    (
        "credential_status",
        "String",
        """
        Status of the exposed credential. Confirmed values:
        - newly_reported: First time this credential has appeared
        - previously_reported: Seen in a prior breach
        - confirmed_active: Verified as currently active
        Ex: newly_reported
        """,
    ),
    (
        "user_id",
        "String",
        """
        User identifier on the source platform.
        """,
    ),
    (
        "user_name",
        "String",
        """
        Username on the source platform.
        """,
    ),
    (
        "display_name",
        "String",
        """
        Display name associated with the exposed account.
        """,
    ),
    (
        "full_name",
        "String",
        """
        Full name of the person in the exposed data.
        """,
    ),
    (
        "hash_type",
        "String",
        """
        Type of hash for the exposed password (if hashed).
        Ex: md5, sha1, bcrypt
        """,
    ),
    (
        "user_ip",
        "String",
        """
        IP address of the exposed user.
        """,
    ),
    (
        "phone_number",
        "String",
        """
        Phone number found in the exposed data.
        """,
    ),
    (
        "company",
        "String",
        """
        Company name associated with the exposed account.
        """,
    ),
    (
        "job_position",
        "String",
        """
        Job position/title in the exposed data.
        """,
    ),
    (
        "file.name",
        "String",
        """
        Name of the file containing the exposed data.
        """,
    ),
    (
        "file.complete_data_set",
        "Boolean",
        """
        Whether the file represents a complete data set.
        Ex: true
        """,
    ),
    (
        "file.download_urls",
        "String",
        """
        Download URL(s) for the exposed data file.
        """,
    ),
    (
        "location.country_code",
        "String",
        """
        Country code from the exposed data location.
        Ex: US, GB, DE
        """,
    ),
    (
        "location.city",
        "String",
        """
        City from the exposed data location.
        """,
    ),
    (
        "location.state",
        "String",
        """
        State/province from the exposed data location.
        """,
    ),
    (
        "location.postal_code",
        "String",
        """
        Postal code from the exposed data location.
        """,
    ),
    (
        "location.federal_district",
        "String",
        """
        Federal district from the exposed data location.
        """,
    ),
    (
        "location.federal_admin_region",
        "String",
        """
        Federal administrative region from the exposed data location.
        """,
    ),
    (
        "social.twitter_id",
        "String",
        """
        Twitter/X user ID found in the exposed data.
        """,
    ),
    (
        "social.instagram_id",
        "String",
        """
        Instagram user ID found in the exposed data.
        """,
    ),
    (
        "social.facebook_id",
        "String",
        """
        Facebook user ID found in the exposed data.
        """,
    ),
    (
        "social.skype_id",
        "String",
        """
        Skype ID found in the exposed data.
        """,
    ),
    (
        "financial.credit_card",
        "String",
        """
        Credit card number found in the exposed data.
        """,
    ),
    (
        "financial.bank_account",
        "String",
        """
        Bank account information found in the exposed data.
        """,
    ),
    (
        "financial.crypto_currency_addresses",
        "String",
        """
        Cryptocurrency wallet addresses found in the exposed data.
        """,
    ),
    (
        "bot.operating_system.hardware_id",
        "String",
        """
        Hardware ID of a bot/stealer associated with the data.
        """,
    ),
    (
        "bot.bot_id",
        "String",
        """
        Bot ID of a stealer/info-stealer associated with the record.
        """,
    ),
    (
        "_all",
        "String",
        """
        Special field: search across all indexed fields in the record.
        Useful for broad text searches.
        Ex: _all:'example.com'
        """,
    ),
]

SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Recon Exposed-Data Records Guide

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

"""
    + generate_md_table(SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_FILTERS)
    + """

=== COMPLEX FILTER EXAMPLES ===

# Newly reported credentials for a specific domain, past 30 days
domain:'example.com'+credential_status:'newly_reported'+created_date:>'now-30d'

# All records associated with a specific notification
notification_id:'<notification_id_here>'

# Records from domain monitoring rules, recent
rule.topic:'SA_DOMAIN'+created_date:>'now-7d'

# Records by credential status across all rule topics
credential_status:'newly_reported',credential_status:'confirmed_active'
"""
)
