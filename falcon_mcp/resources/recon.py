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

# ---------------------------------------------------------------------------
# Aggregation guides
# ---------------------------------------------------------------------------

_SHARED_AGGREGATION_SYNTAX = """
=== AGGREGATION TYPES ===
• terms: Top values of a field, ranked by document count. The default.
• date_histogram: Evenly spaced time buckets. Set `interval` to hour, day, week,
  month, quarter, or year.
• date_range: Explicit time windows. Set `date_ranges`, e.g.
  [{"from": "now-30d", "to": "now"}]
• range: Explicit numeric windows. Set `ranges`, e.g. [{"From": 0, "To": 100}]
• cardinality: Distinct-value count for a field.
• max / min: Largest and smallest value of a numeric field.

`date_histogram`, `date_range`, and `range` each fail without their companion
argument — `interval`, `date_ranges`, and `ranges` respectively. Always supply it
when choosing those types.

Not supported on either recon aggregate endpoint: sum, avg, and percentiles all
return a 400, including on numeric date fields.

=== READING THE RESPONSE ===
Each aggregation returns `{"name": ..., "buckets": [...]}`, where `name` echoes the
`name` you passed — use it to tell results apart. Bucket entries key on `label` and
`count`, not `key`.

For cardinality, max, and min the single bucket looks like `{"count": 0, "value": N}`.
The answer is `value`; the `count: 0` is an artifact of the shape and does NOT mean
"no data".

Date fields bucket as epoch-millisecond integers. `date_histogram` also returns
`key_as_string` with a readable ISO timestamp.

=== NARROWING AND NESTING ===
• `filter` accepts the same FQL as the matching search tool, applied before aggregating.
• `q` does a free-text search across the record.
• `size` caps the number of terms buckets returned.
• `sort` orders buckets, e.g. `_count|asc`.
• `sub_aggregates` nests a second aggregation inside every bucket of the first, which
  is how you get a breakdown-within-a-breakdown.

A filter that references an unknown field returns an empty `resources` list with HTTP
200 — indistinguishable from a filter that legitimately matched nothing. Malformed FQL
syntax returns a 400. Stick to the fields in the matching search FQL guide.
"""

AGGREGATE_RECON_NOTIFICATIONS_GUIDE = (
    """Recon Notification Aggregation Guide

Use `falcon_aggregate_recon_notifications` to answer "how many" and "which are the top"
questions about recon notifications without pulling individual records. For the records
themselves, use `falcon_search_recon_notifications`.

=== VERIFIED AGGREGATION FIELDS ===
Notification attributes:
• status — new, in-progress, pending-review, closed-true-positive,
  closed-false-positive, closed-no-action-true-positive
• rule_topic — SA_TYPOSQUATTING, SA_THIRD_PARTY, SA_CUSTOM, SA_DOMAIN, SA_IP,
  SA_BRAND_PRODUCT, SA_ALIAS, SA_VIP, SA_EMAIL, SA_CVE, SA_AUTHOR, SA_BIN
• rule_priority — low, medium, high, critical
• rule_id, item_type, item_site, source_category, cid, user_uuid, id
• assigned_to_uuid — unassigned, or a user UUID
• created_date, updated_date — epoch millis; use with date_histogram or date_range

Breach and typosquatting detail:
• breach_summary.credential_statuses, breach_summary.is_retroactively_deduped
• typosquatting.id, typosquatting.unicode_format, typosquatting.punycode_format
• typosquatting.parent_domain.{id,unicode_format,punycode_format}
• typosquatting.base_domain.{id,unicode_format,punycode_format,is_registered}
• typosquatting.base_domain.whois.registrar.{name,status}
• typosquatting.base_domain.whois.registrant.{email,name,org}
• typosquatting.base_domain.whois.name_servers

Do not aggregate on `rule_name` — it returns a server error on this endpoint. Aggregate
on `rule_id` instead, then resolve names with `falcon_search_recon_rules`. The fields
`notification_id`, `site`, and `author` belong to the exposed-data-record schema and
return no buckets here.
"""
    + _SHARED_AGGREGATION_SYNTAX
    + """
=== EXAMPLES ===

# Notification volume by status
field: status, aggregate_type: terms

# Busiest monitoring rules in the past 30 days
field: rule_id, aggregate_type: terms, size: 10, filter: created_date:>'now-30d'

# Daily notification trend
field: created_date, aggregate_type: date_histogram, interval: day

# Priority mix for typosquatting only
field: rule_priority, aggregate_type: terms, filter: rule_topic:'SA_TYPOSQUATTING'

# How many distinct rules have fired
field: rule_id, aggregate_type: cardinality

# Which registrars host the most typosquatting domains
field: typosquatting.base_domain.whois.registrar.name, aggregate_type: terms, size: 10
"""
)

AGGREGATE_RECON_EXPOSED_DATA_RECORDS_GUIDE = (
    """Recon Exposed-Data Record Aggregation Guide

Use `falcon_aggregate_recon_exposed_data_records` to summarize leaked credential and PII
records — top breach sites, credential-status mix, volume over time — without pulling
individual rows. For the rows themselves, use `falcon_search_recon_exposed_data_records`.

=== AGGREGATION FIELDS: A STRICT LIST ===
This endpoint accepts only the fourteen fields below and rejects anything else with a
400. That is a much narrower set than the tool's `filter` parameter accepts, so a field
you can filter on is not necessarily a field you can aggregate on.

• cid
• notification_id
• notification_group_id
• created_date — epoch millis; use with date_histogram or date_range
• rule.id
• rule.name
• rule.topic — SA_DOMAIN, SA_EMAIL
• source_category — chat_medium, other, and similar
• site — telegram.org, stealer_logs, malware_logs, and similar
• author
• file.name
• credential_status — newly_reported, previously_reported, confirmed_active
• bot.operating_system.hardware_id
• bot.bot_id

Note the dotted spellings: this endpoint uses `rule.topic` and `rule.name`, whereas
`falcon_aggregate_recon_notifications` uses `rule_topic`. They are not interchangeable.
Commonly attempted but rejected here: id, email, domain, login_id, exposure_date,
hash_type, user_uuid, site_id, author_id, status, rule_topic, and any location.*,
financial.*, or social.* field.
"""
    + _SHARED_AGGREGATION_SYNTAX
    + """
=== EXAMPLES ===

# Credential-status mix across all exposed data
field: credential_status, aggregate_type: terms

# Top sites leaking your credentials
field: site, aggregate_type: terms, size: 10

# Newly reported exposures by site
field: site, aggregate_type: terms, size: 10, filter: credential_status:'newly_reported'

# Exposure volume per day
field: created_date, aggregate_type: date_histogram, interval: day

# Which monitoring rules surface the most exposed records
field: rule.name, aggregate_type: terms, size: 10

# Credential-status breakdown within each rule topic
field: rule.topic, aggregate_type: terms, sub_aggregates:
  [{"type": "terms", "field": "credential_status", "name": "by_status"}]
"""
)

PREVIEW_RECON_RULE_GUIDE = """Recon Rule Preview Guide

Use `falcon_preview_recon_rule` to estimate how noisy a prospective monitoring rule would
be before creating it. You supply a candidate rule definition and Falcon reports how many
notifications it would have produced, broken down by channel and site.

This tool takes a rule definition, not a notification search filter. To aggregate
notifications that already exist, use `falcon_aggregate_recon_notifications`.

=== THE FILTER IS RULE FQL, NOT SEARCH FQL ===
`filter` is the prospective rule's own match expression, written in the monitoring-rule
dialect and parenthesized per condition. It is a different language from the FQL used by
`falcon_search_recon_notifications` — fields like `status` or `created_date` are invalid
here. A bare value such as `example.com` is rejected as invalid FQL.

Verified expressions by topic:
| Topic            | Example filter                                    |
|------------------|---------------------------------------------------|
| SA_DOMAIN        | (domain:'example.com')                            |
| SA_EMAIL         | (email:'user@example.com')                        |
| SA_IP            | (ip:'1.2.3.4')                                    |
| SA_AUTHOR        | (author:'handle')                                 |
| SA_BRAND_PRODUCT | (phrase:'BrandName')+(keyword:'BrandName')        |
| SA_THIRD_PARTY   | (phrase:'VendorName')                             |
| SA_CUSTOM        | (keyword:'term')                                  |
| SA_VIP           | (keyword:'term')                                  |
| SA_CVE           | (keyword:'term')                                  |
| SA_ALIAS         | (keyword:'term')                                  |

Combine conditions with `+`. Using a condition word the topic does not support returns a
400 naming `filter.expressions[0]`.

=== TOPIC AND LOOKBACK CONSTRAINTS ===
`topic` must be one of the topics above. SA_TYPOSQUATTING is rejected — typosquatting
rules cannot be previewed. SA_BIN is accepted as a topic but has no supported condition
word, so it cannot be previewed in practice either.

`lookback_days` accepts only 7, 30, 180, and 365. Any other value, including 1, 14, or 90,
returns a 400. Omitting it previews against the full retained window and returns a single
`Total` count; supplying it adds a separate `Total - EDR` count for exposed-data matches.

=== READING THE RESPONSE ===
The breakdown is fixed — you cannot choose the aggregation fields. Three aggregations come
back, each with `label`/`count` buckets:
• channel — the kinds of sources that matched, e.g. public_repo, chat_medium, forum
• count — total matches; `Total`, plus `Total - EDR` when lookback_days is set
• site — the specific sites that matched, e.g. github.com, telegram.org

`sum_other_doc_count` on channel and site reports matches beyond the returned buckets.
A high total means the rule would be noisy; tighten the filter and preview again.

=== EXAMPLES ===

# How noisy would monitoring this domain be over the past 30 days?
topic: SA_DOMAIN, filter: (domain:'example.com'), lookback_days: 30

# Brand mention volume for the past week
topic: SA_BRAND_PRODUCT, filter: (phrase:'Acme')+(keyword:'Acme'), lookback_days: 7

# Full-window estimate for watching an executive's email
topic: SA_EMAIL, filter: (email:'ceo@example.com')
"""
