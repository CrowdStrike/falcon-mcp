"""
Contains Data Security resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Data Security FQL syntax summary, shared by the entity guides below. It is shorter
# than the generic FQL summary: these APIs reject syntax that one advertises (e.g.
# relative dates on most entity types).
_FQL_SYNTAX_SUMMARY = """\
=== SYNTAX ===
• field:'value' equals · field:!'value' not equal · field:>'value' (also >=, <, <=) · field:~'text' case-insensitive text match · field:!~'text' no text match
• + = AND, , = OR, ( ) = group; never the words AND/OR. Ex: type:'predefined'+(category:'PII',category:'PHI')
• Single-quote strings and dates; booleans and numbers stay bare (is_enabled:true, precedence:>0)
• Dates are UTC, as 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'
"""

_FILTER_FIELDS_HEADER = ("Field", "Type", "Notes")

# The deleted row of the soft-delete entity types; deleted entities are handled by
# the search's deleted argument.
_DELETED_ROW = ("deleted", "Boolean", "Do not filter on it; use the search's deleted argument")
_CREATED_ROW = ("created", "Timestamp", "Ex: created:>'2024-01-01'")
_LAST_UPDATED_ROW = ("last_updated", "Timestamp", "Ex: last_updated:>'2024-06-01'")

_RELATIVE_DATES_REJECTED = "Relative dates ('now-7d') are rejected: use an absolute date"


def _fql_doc(
    label: str,
    entity_type: str,
    filters: list[tuple],
    notes: list[str],
    platform: str | None = None,
) -> str:
    """Assemble an entity's FQL guide: syntax summary, filter fields and notes.

    platform is the policy-only section on the platform_name argument.
    """
    platform_section = f"\n=== PLATFORM ===\n{platform}\n" if platform else ""
    return (
        f"FQL guide: Data Security {label} (entity_type '{entity_type}')\n\n"
        + _FQL_SYNTAX_SUMMARY
        + platform_section
        + "\n=== FILTER FIELDS ===\n\n"
        + generate_md_table([_FILTER_FIELDS_HEADER, *filters])
        + "\n\n=== NOTES ===\n"
        + "".join(f"• {note}\n" for note in notes)
    )


# Classification FQL filters
SEARCH_CLASSIFICATIONS_FQL_FILTERS = [
    ("name", "String", "~ or !~ only; exact match is unsupported. Ex: name:~'credit'"),
    ("created_at", "Timestamp", "Ex: created_at:>'2024-01-01'"),
    ("modified_at", "Timestamp", "Ex: modified_at:>'2024-06-01'"),
    (
        "created_by",
        "String",
        "Creator email. ~ only, with the full address or its full local part; partial "
        "words do not match. Ex: created_by:~'user@example.com'",
    ),
    ("modified_by", "String", "Last modifier email; same matching as created_by"),
]

SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "classifications",
    "classification",
    SEARCH_CLASSIFICATIONS_FQL_FILTERS,
    [
        "Sort: name.asc, name.desc, created_at.asc, created_at.desc, modified_at.desc",
        "Relative dates work, e.g. modified_at:>'now-30d'",
    ],
)

# Policy FQL filters
SEARCH_POLICIES_FQL_FILTERS = [
    (
        "name",
        "String",
        "~ or !~ only; exact match is unsupported. Matches whole words: name:~'test' "
        "misses \"Tests\", so exclude each variant (name:!~'test'+name:!~'tests')",
    ),
    ("description", "String", "~ only. Ex: description:~'compliance'"),
    ("is_enabled", "Boolean", "Ex: is_enabled:true"),
    ("is_default", "Boolean", "Ex: is_default:true"),
    ("precedence", "Integer", "Evaluation order, lower first. Ex: precedence:>0"),
    ("created_at", "Timestamp", "Ex: created_at:>'2024-01-01'"),
    (
        "modified_by",
        "String",
        "Last modifier email. ~ only, with the full address or its full local part; "
        "partial words do not match. Ex: modified_by:~'user@example.com'",
    ),
]

SEARCH_POLICIES_FQL_DOCUMENTATION = _fql_doc(
    "policies",
    "policy",
    SEARCH_POLICIES_FQL_FILTERS,
    [
        "Ex: is_enabled:true+precedence:>0 (enabled non-default policies)",
        "Sort: name.asc, name.desc, precedence.asc, created_at.desc",
        "Relative dates work, e.g. created_at:>'now-30d'",
        "A tenant can hold hundreds of policies per platform: list one page and offer "
        "the next (behavioral guide); if the total is in the hundreds, offer to narrow "
        "it (name, is_enabled:true, the test exclusion above)",
    ],
    platform=(
        "platform_name ('win' or 'mac') is a required tool argument, not an FQL field;\n"
        "the filter applies within that platform. The tool wraps the filter in\n"
        "parentheses, so a , (OR) does not let policies of the other platform leak in."
    ),
)

# Content Pattern FQL filters
SEARCH_CONTENT_PATTERNS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'credit card', name:'SSN Pattern'"),
    ("type", "String", "custom or predefined (lowercase). Ex: type:'predefined'"),
    ("category", "String", "PII, PCI DSS, PHI, Custom, ITAR, Secret. Ex: category:'PCI DSS'"),
    ("region", "String", "e.g. ALL, US, EU. Ex: region:'US'+type:'predefined'"),
    ("example", "String", "Example text. Ex: example:~'4111'"),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION = _fql_doc(
    "content patterns",
    "content_pattern",
    SEARCH_CONTENT_PATTERNS_FQL_FILTERS,
    [
        "Sort: name.asc, name.desc (ignoring case and punctuation), category.asc, region.asc",
        _RELATIVE_DATES_REJECTED,
    ],
)

# Cloud Application FQL filters
SEARCH_CLOUD_APPLICATIONS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'salesforce'"),
    ("type", "String", "integrated, predefined or custom. Ex: type:'custom'"),
    ("application_group_id", "String", "Ex: application_group_id:'google'"),
    ("supports_network_inspection", "Boolean", "Ex: supports_network_inspection:true"),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "cloud applications",
    "cloud_application",
    SEARCH_CLOUD_APPLICATIONS_FQL_FILTERS,
    ["Sort: name.asc, name.desc", _RELATIVE_DATES_REJECTED],
)

# Enterprise Account FQL filters
SEARCH_ENTERPRISE_ACCOUNTS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'corporate'"),
    (
        "application_group_id",
        "String",
        "google, microsoft or box. Ex: application_group_id:'microsoft'",
    ),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_ENTERPRISE_ACCOUNTS_FQL_DOCUMENTATION = _fql_doc(
    "enterprise accounts",
    "enterprise_account",
    SEARCH_ENTERPRISE_ACCOUNTS_FQL_FILTERS,
    ["Sort: name.asc, name.desc, created.desc, last_updated.desc", _RELATIVE_DATES_REJECTED],
)

# Web Location FQL filters
SEARCH_WEB_LOCATIONS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'sharepoint'"),
    ("type", "String", "predefined or custom. Ex: type:'custom'"),
    (
        "application_id",
        "String",
        "The cloud application's ID. Ex: application_id:'0123456789abcdef0123456789abcdef'",
    ),
    ("enterprise_account_id", "String", "The enterprise account's ID"),
    (
        "web_location_group_id",
        "String",
        "Matches locations whose web_location_group_ids include this ID",
    ),
    (
        "web_location_group_count",
        "Integer",
        "Number of groups the location is in. Ex: web_location_group_count:>0",
    ),
    ("supports_network_inspection", "Boolean", "Ex: supports_network_inspection:true"),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION = _fql_doc(
    "web locations",
    "web_location",
    SEARCH_WEB_LOCATIONS_FQL_FILTERS,
    ["Sort: name.asc, name.desc, created.desc, last_updated.desc", _RELATIVE_DATES_REJECTED],
)

# Local Application FQL filters
SEARCH_LOCAL_APPLICATIONS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'excel'"),
    (
        "executable_name",
        "String",
        "Windows executable, e.g. excel.exe, notepad.exe, cmd.exe. "
        "Ex: executable_name:'excel.exe'",
    ),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "local applications",
    "local_application",
    SEARCH_LOCAL_APPLICATIONS_FQL_FILTERS,
    ["Sort: name.asc, name.desc, created.desc, last_updated.desc", _RELATIVE_DATES_REJECTED],
)

# Local Application Group FQL filters
SEARCH_LOCAL_APPLICATION_GROUPS_FQL_FILTERS = [
    ("name", "String", "Ex: name:~'office'"),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION = _fql_doc(
    "local application groups",
    "local_application_group",
    SEARCH_LOCAL_APPLICATION_GROUPS_FQL_FILTERS,
    ["Sort: name.asc, name.desc, created.desc, last_updated.desc", _RELATIVE_DATES_REJECTED],
)

# Sensitivity Label FQL filters
SEARCH_SENSITIVITY_LABELS_FQL_FILTERS = [
    ("name", "String", "Unique label identifier. Ex: name:~'confidential'"),
    ("display_name", "String", "Human-readable name. Ex: display_name:~'confidential'"),
    (
        "external_id",
        "String",
        "The provider's (Microsoft / Google) label ID. Ex: external_id:'label-123'",
    ),
    _DELETED_ROW,
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_SENSITIVITY_LABELS_FQL_DOCUMENTATION = _fql_doc(
    "sensitivity labels",
    "sensitivity_label",
    SEARCH_SENSITIVITY_LABELS_FQL_FILTERS,
    [
        "Labels on egressed files are auto-discovered, so existing ones are usually searchable",
        "Valid on any file type, but ANDed with file_types only types with "
        "supports_mip_extraction match: say so, and offer a sibling content pattern for the rest",
        "Google labels need the Workspace connector and an Enterprise edition; no personal "
        "drives or Gmail",
        "Printers never receive labels",
        "Sort: name.asc, name.desc, created.desc, last_updated.desc",
        _RELATIVE_DATES_REJECTED,
    ],
)

# File Type FQL filters
SEARCH_FILE_TYPES_FQL_FILTERS = [
    (
        "name",
        "String",
        "A format or language, e.g. RPM, RAR, CSV, Python, Script, JPEG, Microsoft Word. "
        "Ex: name:~'python', name:'CSV'",
    ),
    _CREATED_ROW,
    _LAST_UPDATED_ROW,
]

SEARCH_FILE_TYPES_FQL_DOCUMENTATION = _fql_doc(
    "file types",
    "file_type",
    SEARCH_FILE_TYPES_FQL_FILTERS,
    [
        "Read-only catalog that keeps growing: always search; never assume a type exists "
        "or is missing",
        "One search per named format or language (name:~'python', 'java', 'mp4', 'word'); "
        "use every match. Category words ('video', 'source code') are not type names",
        "Extensions no type covers → file path globs in a sibling classification with the "
        "same rules (types and paths AND)",
        "Result flags: supports_mip_extraction (sensitivity labels readable), "
        "supports_content_inspection (content patterns matchable)",
        "Sort: name.asc, name.desc, created.desc, last_updated.desc",
        _RELATIVE_DATES_REJECTED,
    ],
)


# ── Non-FQL guide resources ─────────────────────────────────────────────
#
# These resources deliver agent behavioral guidance through the MCP
# protocol so any connecting LLM receives it without a local CLAUDE.md.

DATA_MODEL_DOCUMENTATION = """\
Data Security entity model
==========================

All references are IDs from search/get, never guessed; AD SIDs are the one
exception and come from the user. Create bottom-up: an entity can only
reference IDs that already exist.

Policy  (platform_name win | mac: inspection, notification, forensics; NO enforcement)
└── policy_properties.classifications: ORDERED, index 0 first. For each egress, the
    │   first Classification that matches the data AND has a Rule covering that egress
    │   acts; the rest are skipped. "Undefined" Classifications (no detection criteria)
    │   go last, or they shadow the others.
    └── Classification  (WHAT to detect + enforcement)
          ├── protection_mode: enforce applies Rule response_action and notify_end_user;
          │     simulate runs Rules silently (events show what would have happened);
          │     monitor only observes. A 'block' Rule outside enforce blocks nothing.
          ├── Detection criteria, any combination (blank = match everything):
          │     ├── content_patterns   -> content_pattern   (predefined catalog + custom regex;
          │     │                                            content_patterns_operator and | or)
          │     ├── file_types         -> file_type         (read-only; true type, not extension)
          │     ├── sensitivity_labels -> sensitivity_label (Microsoft MIP or Google labels)
          │     ├── web_sources        -> web_location      (ORIGIN: data came FROM here)
          │     └── win_/mac_file_path_patterns             (inline globs, no entity)
          └── rules[]  (nested, no own ID, evaluated in order): WHERE / WHO / ACTION
                ├── Channels:
                │     ├── Removable Media    (enable_usb_devices)
                │     ├── Printer            (enable_printer_egress; Windows only)
                │     ├── Web Upload         (enable_web_locations; web_locations_scope all | specific;
                │     │                       web_locations -> web_location = DESTINATION: data goes TO)
                │     └── Local Application  (enable_local_application_groups;
                │                             local_application_groups -> local_application_group)
                ├── Users: user_scope all | specific (ad_users / ad_groups SIDs, not searchable)
                ├── response_action: block | allow | justify
                └── detection_severity · trigger_detection (enforce only) · notify_end_user

Supporting entities (create before the entities that reference them):

  cloud_application  ─(application_id)────────> web_location
  enterprise_account ─(enterprise_account_id)──> web_location  (makes it "managed":
                                                               corporate activity only)
  enterprise_account.application_group_id: google | microsoft | box
  local_application <─(group_ids / local_application_ids)─> local_application_group
                                                              (Windows only)

file_type is read-only; sensitivity_label can be created but not updated.

Key rules
---------
- One Policy per host per platform: Policies never stack. Windows + macOS = two
  Policies referencing the same (platform-agnostic) Classifications.
- "Upload / send TO X" = Rule destination (web_locations, scope specific).
  "Data FROM X" / "downloaded from X" = Classification origin (web_sources).
  One web_location ID can serve both roles.
- Criteria AND, values OR: a file must match every detection criterion set
  (patterns, types, paths, origins, labels) and any value within one (PDF or
  Word; PCI or PII unless content_patterns_operator is 'and'). One
  Classification narrows ("PDFs with PII"); alternatives ("Python type or
  *.go", "labelled or marked") need sibling Classifications with the same
  Rules, all listed in the Policy.
- A Classification has no effect until a Policy references it.

Guides per entity_type: falcon://data-security/<type>/fql-guide (search
filters) and falcon://data-security/<type>/body-guide (write body), where
<type> is the plural, hyphenated entity_type: classifications, policies,
content-patterns, cloud-applications, enterprise-accounts, web-locations,
local-applications, local-application-groups, sensitivity-labels, file-types
(FQL guide only).
"""

WORKFLOW_GUIDE_DOCUMENTATION = """\
Data Security operating rules
=============================

Falcon Data Security is CrowdStrike's endpoint DLP. Answer from tool results,
never from memory, and ask the user rather than assume any setting.
Compliance asks map to content pattern categories: PCI-DSS → 'PCI DSS',
HIPAA → 'PHI', GDPR / CCPA / LGPD / PDPA → 'PII', ITAR → 'ITAR'.

1. Vague request ("protect my sensitive data", "set up DLP"): ask before any
   search or get call. Ask what data (e.g. card numbers, source code, labelled
   documents), which channels (web upload, removable media, printer, local
   applications), which platforms (Windows, macOS), and monitor or enforce.
   Then read only what the answers point to, with filtered, small-limit
   searches (e.g. policies with is_enabled:true, classifications by name).
2. Listing: show one page with pagination.total and offer the next; do not
   fetch every page unasked. Pass fields with only what you show (e.g.
   ["name"]) and limit 100, or limit about 20 without fields; limit 1 only
   answers "how many". If the total is in the hundreds, offer to narrow it by
   name or by excluding test entities with !~ where the FQL guide allows
   (policies: name:!~'test'+name:!~'tests').
3. Displaying: offer to fetch the entities a record references and show them
   as the tree in falcon://data-security/entities/model-guide. Describe a
   classification by its protection_mode first: only 'enforce' blocks, asks
   for justification or notifies; 'simulate' runs rules silently and
   'monitor' only observes. Show rule ad_users / ad_groups SIDs as-is; they
   cannot be resolved to names.
4. AD users and groups cannot be looked up. When a rule must target users or
   groups ("for HR", "except user Y"), say so and ask for the exact SIDs
   (S-1-5-21-…). Never derive or invent a SID, and never silently fall back to
   user_scope 'all': if the user has no SIDs, ask whether the rule should
   apply to all users.
5. "Confidential", "internal use only", "restricted" or labelled documents
   mean sensitivity labels: search sensitivity_label by display_name (~) and
   offer the matches; if none match, offer to create the label by its
   Purview / Google name. A content pattern for the marking text is opt-in
   only, in a sibling classification with the same rules.
6. File kinds (PDF / Word / Excel, images, media, source code, archives) mean
   file types: search file_type once per named format or language (read-only;
   the catalog grows). Use file path globs only for what no file type covers,
   in a sibling classification with the same rules (criteria in one
   classification AND).
"""


# ── Write body guides ────────────────────────────────────────────────────
#
# The exact create/update body of each writable entity type, served by
# falcon_get_data_security_entity_schema, as falcon://data-security/<entity>/body-guide
# resources, and with a create/update the API rejects as a bad request.

BODY_GUIDE_NOTATION = (
    "Each value shows the field's type (string, integer, number, bool, [T] for a list) "
    'or its allowed values ("a" | "b"); // comments are notes, not part of the body.'
)

CLASSIFICATION_BODY_GUIDE = """\
Data Security classification body
=================================

WHAT to detect and, in nested rules, WHERE / WHO / WHICH action. Unmarked
fields are optional. Criteria fields AND each other, values within one field
OR; alternatives need sibling classifications.

{
  "name": string, // required. No special characters
  "classification_properties": {
    "protection_mode": "monitor" | "simulate" | "enforce", // required. Only 'enforce' applies rule response_action and notify_end_user; 'simulate' runs rules silently (events show what would have happened); 'monitor' only observes
    "content_patterns": [string], // content_pattern IDs
    "content_patterns_operator": "or" | "and", // 'or' = any pattern, 'and' = all
    "file_types": [string], // file_type IDs; blank = all. True format, not extension. Preferred for file kinds; search each named format/language
    "sensitivity_labels": [string], // sensitivity_label IDs (Microsoft MIP or Google), for labelled/marked documents
    "web_sources": [string], // web_location IDs the data came FROM (origins); never a destination
    "win_file_path_patterns": [string], // max 20 Windows globs, e.g. **\\*.{go,java,rs}. Only for extensions no file type covers, in a sibling classification
    "mac_file_path_patterns": [string], // max 20 macOS globs, e.g. **/*.{go,java,rs}. Same rule
    "evidence_duplication_enabled": bool, // retain forensic evidence
    "rules": [Rule] // evaluated in order: an exception (allow) before the general rule (block)
  }
}

Rule:

{
  "id": string, // existing rules only: keep it on update, or the rule is re-added as new
  "user_scope": "all" | "specific", // required
  "ad_users": [string], // with user_scope 'specific'. AD user SIDs from the user; cannot be looked up
  "ad_groups": [string], // with user_scope 'specific'. AD group SIDs from the user; cannot be looked up
  "response_action": "allow" | "block" | "justify", // required. 'justify' is invalid on Printer and Local Application
  "detection_severity": "informational" | "low" | "medium" | "high" | "critical", // required
  "trigger_detection": bool, // required. Fires only in 'enforce'
  "notify_end_user": bool, // required
  "enable_usb_devices": bool, // required. Removable Media channel
  "enable_printer_egress": bool, // required. Printer channel, Windows only
  "enable_web_locations": bool, // required. Web Upload channel
  "enable_local_application_groups": bool, // required. Local Application channel
  "web_locations_scope": "all" | "specific", // required
  "web_locations": [string], // with web_locations_scope 'specific'. web_location IDs the data goes TO (destinations)
  "web_location_destination_groups": [string], // max 15 web location destination group IDs
  "local_application_groups": [string], // with enable_local_application_groups. Max 15 local_application_group IDs
  "enable_screen_capture_rule": bool, // needs the policy's enable_screen_capture (Windows)
  "description": string
}

Update: "id" plus only the fields to change, top level or inside
classification_properties; omitted fields keep their values and a list you
send replaces the stored one. For rules, send the full current list (from
falcon_get_data_security_entities) with your change, keeping each existing
rule's "id": a rule without one is added as a new rule.
"""

POLICY_BODY_GUIDE = """\
Data Security policy body
=========================

Platform-specific: pass platform_name ('win' or 'mac') as the tool argument,
never in the body. Holds inspection, notification and forensics settings;
enforcement lives on its classifications.

{
  "name": string, // required. No special characters
  "description": string, // required. No special characters
  "precedence": integer, // required on create. Lower numbers evaluate first
  "policy_properties": {
    "classifications": [string], // classification IDs, ORDERED: the first match with a rule covering the egress wins; classifications without detection criteria go last
    "enable_content_inspection": bool,
    "enable_context_inspection": bool,
    "enable_clipboard_inspection": bool,
    "enable_clipboard_web_origin": bool, // attribute web sources for clipboard content; needs context inspection
    "inspection_depth": "balanced" | "high_performance" | "deep_scan",
    "min_confidence_level": "low" | "medium" | "high",
    "max_file_size_to_inspect": number, // paired with max_file_size_to_inspect_unit
    "max_file_size_to_inspect_unit": "Bytes" | "KB" | "MB",
    "similarity_detection": bool, // near-duplicate / derived content
    "similarity_threshold": "10" | "20" | "30" | "40" | "50" | "60" | "70" | "80" | "90" | "100", // string; set only with similarity_detection
    "block_notifications": "default" | "custom", // 'custom' needs custom_block_notification
    "custom_block_notification": string, // 2-256 chars, max 4 lines
    "allow_notifications": "default" | "custom", // 'custom' needs custom_allow_notification
    "custom_allow_notification": string, // 2-256 chars, max 4 lines
    "evidence_download_enabled": bool, // retrieval of forensic evidence
    "browsers_without_active_extension": "allow" | "block_policy", // inspection coverage, NOT enforcement

    // Windows only:
    "enable_network_inspection": bool,
    "network_inspection_exclude_list_v2": [string], // max 200
    "network_inspection_files_exceeding_size_limit": "block" | "allow",
    "enable_print_monitor": bool,
    "enable_screen_capture": bool, // prerequisite for a rule's enable_screen_capture_rule
    "screen_capture_duration_pre_event": "3" | "5" | "10",
    "screen_capture_duration_post_event": "3" | "5" | "10",
    "evidence_encrypted_enabled": bool, // inspect encrypted archives (ZIP, RAR)
    "block_all_data_access": bool,
    "enable_end_user_notifications_unsupported_browser": bool,

    // macOS only:
    "enable_ocr": bool
  }
}

Update: "id" plus the fields to change. A new policy is created disabled and
without host groups: is_enabled (bool) and host_groups ([string] host group
IDs) are update-only. A list replaces the stored list: to add a
classification, send the full current list (from
falcon_get_data_security_entities) with the new ID in the right position.
"""

CONTENT_PATTERN_BODY_GUIDE = """\
Data Security content pattern body
==================================

Standard data (card numbers, SSNs, PHI, secrets): search the predefined
catalog first (e.g. filter category:~'PCI DSS') and create a custom pattern
only when none fits. Organisation-specific formats (employee IDs, internal
codes) have no predefined pattern: create the custom one directly.

{
  "name": string, // required. No special characters
  "description": string, // required. What sensitive data it detects
  "category": "PII" | "PCI DSS" | "PHI" | "Custom" | "ITAR" | "Secret", // required
  "region": string, // required. e.g. 'ALL'
  "regexes": [string], // required. One entry per distinct pattern
  "example": string, // required. Sample text that the regexes match
  "min_match_threshold": integer // required, >= 1. Matches needed to trigger detection
}

Update: "id" plus any of name, description, regexes, example,
min_match_threshold; category and region cannot change. regexes replaces the
stored list.
"""

CLOUD_APPLICATION_BODY_GUIDE = """\
Data Security cloud application body
====================================

A SaaS application that web locations reference via application_id.
Predefined applications cover most services: search by name first (FQDNs are
not searchable).

{
  "name": string, // required
  "description": string,
  "urls": [{ "fqdn": string, "path": string }] // required. e.g. [{ "fqdn": "app.example.com", "path": "/" }]
}

Update: "id" plus any of name, description, urls. urls replaces the stored
list.
"""

ENTERPRISE_ACCOUNT_BODY_GUIDE = """\
Data Security enterprise account body
=====================================

Separates corporate from personal use of a provider: a web_location that
references it (enterprise_account_id) becomes "managed".

{
  "name": string, // required. e.g. 'Corporate OneDrive'
  "application_group_id": "google" | "microsoft" | "box", // required
  "domains": [string], // required. The organization's domains for this provider, e.g. ['contoso.com']
  "plugin_config_id": string // links the Data Protection connector; needed for site-level tracking
}

Update: "id" plus name and/or domains, the only updatable fields. domains
replaces the stored list.
"""

WEB_LOCATION_BODY_GUIDE = """\
Data Security web location body
===============================

One web location can be an origin (classification web_sources) or a
destination (rule web_locations). Search predefined locations first: a
duplicate custom one changes FQDN matching.

{
  "name": string, // required
  "application_id": string, // required. cloud_application ID
  "type": "custom", // required. Predefined locations cannot be created or changed
  "location_type": string, // required by the API spec; existing custom locations store ''
  "deleted": false, // required by the API spec
  "enterprise_account_id": string, // makes the location "managed" (corporate activity only)
  "provider_location_id": string, // site-level tracking (SharePoint site, Google shared drive, Box folder); needs the connector and enterprise_account_id
  "provider_location_name": string, // set together with provider_location_id
  "web_location_group_ids": [string]
}

Update: "id" and "name" plus the fields to change; omitted fields keep their
values. name may be left out only when the update sets enterprise_account_id:
the stored name is then kept and any name sent is ignored.
web_location_group_ids replaces the stored list.
"""

LOCAL_APPLICATION_BODY_GUIDE = """\
Data Security local application body
====================================

A Windows desktop application whose data access a rule can scope through a
local_application_group.

{
  "name": string, // required
  "executable_name": string, // required. e.g. 'excel.exe'
  "group_ids": [string], // local_application_group IDs to join; use it to add a new application to existing groups
  "apply_rules_for_children_processes": bool, // rules also apply to child processes
  "enable_rename_detection": bool, // detect a renamed executable
  "emit_rule_matched_events_only": bool // emit events only when a rule matches
}

Update: "id" plus the fields to change; omitted fields keep their values.
group_ids replaces the stored list.
"""

LOCAL_APPLICATION_GROUP_BODY_GUIDE = """\
Data Security local application group body
==========================================

Groups local applications so a rule's Local Application channel can target
them (rule local_application_groups).

{
  "name": string, // required
  "description": string, // required by the API spec
  "local_application_ids": [string] // required. local_application IDs in the group
}

Update: "id" plus the fields to change; omitted fields keep their values.
local_application_ids replaces the stored list.
"""

SENSITIVITY_LABEL_BODY_GUIDE = """\
Data Security sensitivity label body
====================================

A Microsoft (MIP) or Google label on files. The Microsoft 365 / Google
Workspace connector normally syncs labels: search before creating one.
Create only: labels cannot be updated.

{
  "name": string, // required
  "display_name": string, // required
  "external_id": string, // required. The label's ID at the provider
  "label_provider": "microsoft" | "google", // required
  "plugins_configuration_id": string, // required. The connector configuration ID
  "co_authoring": bool, // required
  "synced": bool // required
}
"""
