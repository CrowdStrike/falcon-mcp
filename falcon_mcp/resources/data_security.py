"""
Contains Data Security resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Classification FQL filters
SEARCH_CLASSIFICATIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Classification name. Only the ~ operator works on this field;
        exact match (without ~) is not supported for classifications.

        Ex: name:~'credit'
        """,
    ),
    (
        "created_at",
        "Timestamp",
        "Yes",
        """
        Date the classification was created.

        Ex: created_at:>'2024-01-01'
        Ex: created_at:<'2025-06-01'
        """,
    ),
    (
        "modified_at",
        "Timestamp",
        "Yes",
        """
        Date the classification was last modified.

        Ex: modified_at:>'2024-01-01'
        """,
    ),
    (
        "created_by",
        "String",
        "Yes",
        """
        Email of the user who created the classification.
        Exact match returns nothing on this field; use ~ with the full
        address or its full local part. Partial words do not match.

        Ex: created_by:~'user@example.com'
        """,
    ),
    (
        "modified_by",
        "String",
        "Yes",
        """
        Email of the user who last modified the classification.
        Exact match returns nothing on this field; use ~ with the full
        address or its full local part. Partial words do not match.

        Ex: modified_by:~'user@example.com'
        """,
    ),
]

SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search Data Security Classifications Guide

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
• Strings: 'value' (use ~ for case-insensitive matching)
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== falcon_search_data_security_entities (entity_type='classification') FQL filter options ===

"""
    + generate_md_table(SEARCH_CLASSIFICATIONS_FQL_FILTERS)
    + """

=== EXAMPLE USAGE ===

• name:~'credit' - Classifications with "credit" in the name (case-insensitive)
• created_at:>'2024-01-01' - Created after a date
• modified_at:>'2024-06-01' - Recently modified

=== SORTING ===

Supported sort fields: name.asc, name.desc, created_at.asc, created_at.desc, modified_at.desc

=== IMPORTANT NOTES ===
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Dates are UTC, as 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'; relative dates such as 'now-7d' also work
"""
)

# Policy FQL filters
SEARCH_POLICIES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Policy name. Only the ~ operator works on this field;
        exact match (without ~) is not supported for policies.

        Ex: name:~'production'
        """,
    ),
    (
        "is_enabled",
        "Boolean",
        "No",
        """
        Whether the policy is enabled.

        Ex: is_enabled:true
        Ex: is_enabled:false
        """,
    ),
    (
        "is_default",
        "Boolean",
        "No",
        """
        Whether this is the default policy.

        Ex: is_default:true
        """,
    ),
    (
        "created_at",
        "Timestamp",
        "Yes",
        """
        Date the policy was created.

        Ex: created_at:>'2024-01-01'
        """,
    ),
    (
        "description",
        "String",
        "Yes",
        """
        Policy description text. Only the ~ operator works on this field;
        exact match returns nothing.

        Ex: description:~'compliance'
        """,
    ),
    (
        "precedence",
        "Integer",
        "Yes",
        """
        Policy precedence (evaluation order). Lower = higher priority.

        Ex: precedence:>0
        Ex: precedence:0
        """,
    ),
    (
        "modified_by",
        "String",
        "Yes",
        """
        Email of the user who last modified the policy.
        Exact match returns nothing on this field; use ~ with the full
        address or its full local part. Partial words do not match.

        Ex: modified_by:~'user@example.com'
        """,
    ),
]

SEARCH_POLICIES_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search Data Security Policies Guide

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

=== DATA TYPES & SYNTAX ===
• Strings: 'value' (use ~ for case-insensitive matching)
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== IMPORTANT: platform_name parameter ===

The falcon_search_data_security_entities tool (entity_type='policy') requires a platform_name parameter ('win' or 'mac')
which is separate from the FQL filter. The filter applies within the selected platform.

=== falcon_search_data_security_entities (entity_type='policy') FQL filter options ===

"""
    + generate_md_table(SEARCH_POLICIES_FQL_FILTERS)
    + """

=== EXAMPLE USAGE ===

• is_enabled:true - All enabled policies
• is_default:true - Default policy only
• is_enabled:true+precedence:>0 - Enabled non-default policies
• name:~'production' - Policies with "production" in the name
• created_at:>'2024-01-01' - Recently created policies

=== SORTING ===

Supported sort fields: name.asc, name.desc, precedence.asc, created_at.desc

=== IMPORTANT NOTES ===
• platform_name ('win' or 'mac') is required and is not an FQL filter
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Boolean values have no quotes: is_enabled:true
"""
)

# Content Pattern FQL filters
SEARCH_CONTENT_PATTERNS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description",
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Content pattern name. Supports text match (~) for case-insensitive search.

        Ex: name:~'credit card'
        Ex: name:'SSN Pattern'
        """,
    ),
    (
        "type",
        "String",
        "Yes",
        """
        Pattern type. Values: custom, predefined.

        Ex: type:'custom'
        Ex: type:'predefined'
        """,
    ),
    (
        "category",
        "String",
        "Yes",
        """
        Pattern category. Values: PII, PCI DSS, PHI, Custom, ITAR, Secret.

        Ex: category:'PII'
        Ex: category:'Custom'
        """,
    ),
    (
        "region",
        "String",
        "Yes",
        """
        Geographic region the pattern applies to. Ex: ALL, US, EU.

        Ex: region:'ALL'
        Ex: region:'US'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the content pattern has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "example",
        "String",
        "Yes",
        """
        Example text for the content pattern.

        Ex: example:~'4111'
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the content pattern was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the content pattern was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search Data Security Content Patterns Guide

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

=== DATA TYPES & SYNTAX ===
• Strings: 'value' (use ~ for case-insensitive matching)
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition

=== falcon_search_data_security_entities (entity_type='content_pattern') FQL filter options ===

"""
    + generate_md_table(SEARCH_CONTENT_PATTERNS_FQL_FILTERS)
    + """

=== EXAMPLE USAGE ===

• type:'custom' - Custom patterns only
• type:'predefined' - CrowdStrike-provided patterns
• category:'PCI DSS' - Payment-card data patterns
• region:'US'+type:'predefined' - US-specific predefined patterns
• name:~'credit' - Patterns with "credit" in the name

=== SORTING ===

Supported sort fields: name.asc, name.desc, category.asc, region.asc
(name ordering ignores case and punctuation)

=== IMPORTANT NOTES ===
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• type values are lowercase: 'custom', 'predefined'
• Dates are UTC, as 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'
• Relative dates such as 'now-7d' are rejected; use an absolute UTC timestamp
"""
)

# Shared FQL syntax preamble reused by the entity guides below.
_FQL_SYNTAX_PREAMBLE = """
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

=== DATA TYPES & SYNTAX ===
• Strings: 'value' (use ~ for case-insensitive matching)
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
"""


def _fql_doc(
    title: str,
    tool_name: str,
    filters: list[tuple],
    sort_fields: str,
    bool_example: str | None = None,
) -> str:
    """Assemble a standard entity FQL guide from its filter table and sort fields.

    bool_example names a filterable boolean for the no-quotes note; guides with no
    such field (deleted is set through the search's deleted argument) omit the note.
    """
    bool_note = f"• Boolean values have no quotes (e.g. {bool_example})\n" if bool_example else ""
    return (
        f"Falcon Query Language (FQL) - {title} Guide\n"
        + _FQL_SYNTAX_PREAMBLE
        + f"\n=== {tool_name} FQL filter options ===\n\n"
        + generate_md_table(filters)
        + "\n\n=== SORTING ===\n\n"
        + f"Supported sort fields: {sort_fields}\n\n"
        + "=== IMPORTANT NOTES ===\n"
        + "• Use single quotes around values: 'value'\n"
        + "• Use ~ operator for case-insensitive name matching\n"
        + bool_note
        + "• Dates are UTC, as 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'\n"
        + "• Relative dates such as 'now-7d' are rejected; use an absolute UTC timestamp\n"
    )


# Cloud Application FQL filters
SEARCH_CLOUD_APPLICATIONS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Cloud application name. Supports text match (~).

        Ex: name:~'salesforce'
        """,
    ),
    (
        "type",
        "String",
        "Yes",
        """
        Cloud application origin. Values: integrated, predefined, custom.

        Ex: type:'custom'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the cloud application has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "supports_network_inspection",
        "Boolean",
        "No",
        """
        Whether network-level inspection is supported.

        Ex: supports_network_inspection:true
        """,
    ),
    (
        "application_group_id",
        "String",
        "Yes",
        """
        Cloud application group ID this application belongs to.

        Ex: application_group_id:'google'
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the cloud application was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the cloud application was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Cloud Applications",
    "falcon_search_data_security_entities (entity_type='cloud_application')",
    SEARCH_CLOUD_APPLICATIONS_FQL_FILTERS,
    "name.asc, name.desc",
    bool_example="supports_network_inspection:true",
)

# Enterprise Account FQL filters
SEARCH_ENTERPRISE_ACCOUNTS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Enterprise account name. Supports text match (~).

        Ex: name:~'corporate'
        """,
    ),
    (
        "application_group_id",
        "String",
        "Yes",
        """
        Application group this account belongs to. Values: google, microsoft, box.

        Ex: application_group_id:'microsoft'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the enterprise account has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the enterprise account was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the enterprise account was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_ENTERPRISE_ACCOUNTS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Enterprise Accounts",
    "falcon_search_data_security_entities (entity_type='enterprise_account')",
    SEARCH_ENTERPRISE_ACCOUNTS_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
)

# Web Location FQL filters
SEARCH_WEB_LOCATIONS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Web location name. Supports text match (~).

        Ex: name:~'sharepoint'
        """,
    ),
    (
        "type",
        "String",
        "Yes",
        """
        Whether predefined or user-created. Values: predefined, custom.

        Ex: type:'custom'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the web location has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "application_id",
        "String",
        "Yes",
        """
        ID of the cloud application the web location belongs to.

        Ex: application_id:'0123456789abcdef0123456789abcdef'
        """,
    ),
    (
        "enterprise_account_id",
        "String",
        "Yes",
        """
        ID of the enterprise account this web location belongs to.

        Ex: enterprise_account_id:'0123456789abcdef0123456789abcdef'
        """,
    ),
    (
        "web_location_group_id",
        "String",
        "Yes",
        """
        Matches web locations whose web_location_group_ids include this group ID.

        Ex: web_location_group_id:'0123456789abcdef0123456789abcdef'
        """,
    ),
    (
        "web_location_group_count",
        "Integer",
        "Yes",
        """
        Number of web location groups the web location belongs to.

        Ex: web_location_group_count:>0
        """,
    ),
    (
        "supports_network_inspection",
        "Boolean",
        "No",
        """
        Whether network-level inspection is supported.

        Ex: supports_network_inspection:true
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the web location was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the web location was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Web Locations",
    "falcon_search_data_security_entities (entity_type='web_location')",
    SEARCH_WEB_LOCATIONS_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
    bool_example="supports_network_inspection:true",
)

# Local Application FQL filters
SEARCH_LOCAL_APPLICATIONS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Local application name. Supports text match (~).

        Ex: name:~'excel'
        """,
    ),
    (
        "executable_name",
        "String",
        "Yes",
        """
        Name of the executable representing the local application
        (e.g. excel.exe, notepad.exe, cmd.exe - Windows only).

        Ex: executable_name:'excel.exe'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the local application has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the local application was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the local application was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Local Applications",
    "falcon_search_data_security_entities (entity_type='local_application')",
    SEARCH_LOCAL_APPLICATIONS_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
)

# Local Application Group FQL filters
SEARCH_LOCAL_APPLICATION_GROUPS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Local application group name. Supports text match (~).

        Ex: name:~'office'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the local application group has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the group was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the group was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Local Application Groups",
    "falcon_search_data_security_entities (entity_type='local_application_group')",
    SEARCH_LOCAL_APPLICATION_GROUPS_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
)

# Sensitivity Label FQL filters
SEARCH_SENSITIVITY_LABELS_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        Sensitivity label name (a unique identifier). Supports text match (~).

        Ex: name:~'confidential'
        """,
    ),
    (
        "display_name",
        "String",
        "Yes",
        """
        Human-readable label name.

        Ex: display_name:~'confidential'
        """,
    ),
    (
        "external_id",
        "String",
        "Yes",
        """
        The provider (Microsoft/Google) label ID.

        Ex: external_id:'label-123'
        """,
    ),
    (
        "deleted",
        "Boolean",
        "No",
        """
        Whether the sensitivity label has been soft-deleted. Do not filter on it;
        set the search's deleted argument instead (exclude by default, include, only).
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the label was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the label was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_SENSITIVITY_LABELS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Sensitivity Labels",
    "falcon_search_data_security_entities (entity_type='sensitivity_label')",
    SEARCH_SENSITIVITY_LABELS_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
)

# File Type FQL filters
SEARCH_FILE_TYPES_FQL_FILTERS = [
    ("Name", "Type", "Operators", "Description"),
    (
        "name",
        "String",
        "Yes",
        """
        File type name (e.g. 'RPM', 'RAR', 'CSV', 'Microsoft Word'). Supports text match (~).

        Ex: name:~'word'
        Ex: name:'CSV'
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the file type was created (UTC).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the file type was last updated (UTC).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_FILE_TYPES_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security File Types",
    "falcon_search_data_security_entities (entity_type='file_type')",
    SEARCH_FILE_TYPES_FQL_FILTERS,
    "name.asc, name.desc, created.desc, last_updated.desc",
)


# ── Non-FQL guide resources ─────────────────────────────────────────────
#
# These resources deliver agent behavioral guidance through the MCP
# protocol so any connecting LLM receives it without a local CLAUDE.md.

DATA_MODEL_DOCUMENTATION = """\
Data Security Entity Relationship Model
==========================================

All references are by ID. Create dependencies first (bottom-up): an entity can
only reference IDs that already exist. Use search/get tools to resolve
referenced IDs — never guess them. The one exception is AD users/groups (see
Key rules): they cannot be looked up, so their SIDs must come from the user.

Policy  (platform_name: win | mac — inspection, notification, forensics; NO enforcement)
└── policy_properties.classifications: ORDERED list — index 0 is evaluated first.
    │   For each egress, the first Classification that matches the data AND has a
    │   Rule covering that egress acts; the rest are skipped. Place "undefined"
    │   Classifications (no detection criteria) last, or they shadow the others.
    └── Classification  (WHAT to detect + enforcement)
          ├── protection_mode: monitor | simulate | enforce
          ├── Detection criteria — any combination (blank = match everything):
          │     ├── content_patterns     -> content_pattern   (predefined catalog + custom regex;
          │     │                                              content_patterns_operator and | or)
          │     ├── file_types           -> file_type         (read-only; true type, not extension)
          │     ├── sensitivity_labels   -> sensitivity_label (Microsoft MIP or Google labels)
          │     ├── web_sources          -> web_location      (Web ORIGIN: data came FROM here)
          │     └── win_/mac_file_path_patterns               (inline glob strings, no entity)
          └── rules[]  (nested, not searchable on their own; evaluated in order)  WHERE / WHO / ACTION
                ├── Channels:
                │     ├── Removable Media    (enable_usb_devices)
                │     ├── Printer            (enable_printer_egress; Windows only)
                │     ├── Web Upload         (enable_web_locations; web_locations_scope all | specific,
                │     │                       web_locations -> web_location = Web DESTINATION: data goes TO)
                │     └── Local Application  (enable_local_application_groups;
                │                             local_application_groups -> local_application_group)
                ├── User scope: user_scope all | specific (ad_users / ad_groups by SID —
                │                NOT searchable here: ask the user for the SIDs)
                ├── response_action: block | allow | justify
                └── detection_severity · trigger_detection (fires only in enforce) · notify_end_user

Supporting entities (create before the entities that reference them):

  cloud_application ──(application_id)──────────> web_location
  enterprise_account ─(enterprise_account_id)───> web_location   (makes it "managed":
                                                                  matches corporate activity only)
  application_group_id: google | microsoft | box ─> enterprise_account
  local_application <──(group_ids / local_application_ids)──> local_application_group
                                                                 (Windows only)

Read-only (search/get only, never create): file_type. sensitivity_label
supports create but not update.

Key rules
---------
- AD users and groups CANNOT be searched or fetched with these tools. When a
  Rule must be scoped to specific users/groups ("for HR", "except user Y"),
  tell the user they cannot be looked up and ask them for the exact SIDs
  (e.g. S-1-5-21-...) to put in ad_users / ad_groups. Never derive a SID from a
  name, never invent one, and never silently fall back to user_scope all —
  if the user cannot provide SIDs, ask whether to apply the Rule to all users.
- One Policy per host per platform: Policies never stack. Windows + macOS =
  two Policies referencing the same (platform-agnostic) Classifications.
- "Upload / send TO X" = Rule Web Destination (web_locations, scope specific).
  "Data FROM X" / "downloaded from X" = Classification Web Origin (web_sources).
  The same web_location ID can serve both roles.
- A Classification has no effect until a Policy references it.
- Enforcement lives only on the Classification (protection_mode, Rule
  response_action), never on the Policy.

When displaying a policy or classification, offer to drill into referenced
entity IDs (classifications, content patterns, web locations, etc.) and
present the relationships using the tree structure above.

For the exact create/update body of an entity type (field names, types,
allowed values), call falcon_get_data_security_entity_schema, or read
falcon://data-security/<entity>/body-guide (e.g.
falcon://data-security/classifications/body-guide).

Per-entity FQL guides
---------------------
Before composing a `filter`, read the guide for the entity_type you are
searching:

  classification          -> falcon://data-security/classifications/fql-guide
  policy                  -> falcon://data-security/policies/fql-guide
  content_pattern         -> falcon://data-security/content-patterns/fql-guide
  cloud_application       -> falcon://data-security/cloud-applications/fql-guide
  enterprise_account      -> falcon://data-security/enterprise-accounts/fql-guide
  web_location            -> falcon://data-security/web-locations/fql-guide
  local_application       -> falcon://data-security/local-applications/fql-guide
  local_application_group -> falcon://data-security/local-application-groups/fql-guide
  sensitivity_label       -> falcon://data-security/sensitivity-labels/fql-guide
  file_type               -> falcon://data-security/file-types/fql-guide
"""

WORKFLOW_GUIDE_DOCUMENTATION = """\
Data Security Agent Workflow Guide
=====================================

=== DOMAIN CONTEXT ===

You are working with CrowdStrike Falcon Data Security — an enterprise DLP
platform. Relevant compliance frameworks include GDPR, HIPAA, PCI-DSS, CCPA,
SOX, LGPD, PDPA, ISO 27001, and NIST. When in doubt about any data security
setting, ask the user rather than assuming.

=== OPERATIONAL RULES ===

1. Always use the Data Security tools for Data Security queries — do not
   fabricate configuration details from memory.
2. When in doubt about any setting value, ask the user before proceeding.
3. After displaying entity details, check for UUIDs or references to other
   entities. Offer to fetch and display those relationships using the data
   model in falcon://data-security/entities/model-guide.
4. AD users and groups cannot be looked up with the Data Security tools. When a
   rule must target specific users or groups, tell the user so and ask them for
   the exact SIDs. When displaying a rule, show its ad_users / ad_groups SIDs
   as-is — names cannot be resolved.
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
Data Security Classification Body Guide
=========================================

A Classification defines WHAT to detect and, through its nested rules, WHERE /
WHO / WHICH action. All references are IDs obtained via search/get.

{
  "name": string, // required. No special characters
  "classification_properties": {
    "protection_mode": "monitor" | "simulate" | "enforce", // required. The only classification-level enforcement control
    "content_patterns": [string], // optional. content_pattern IDs
    "content_patterns_operator": "or" | "and", // optional. 'or' = match any pattern, 'and' = match all
    "file_types": [string], // optional. file_type IDs; blank = all file types
    "sensitivity_labels": [string], // optional. sensitivity_label IDs
    "web_sources": [string], // optional. web_location IDs the data came FROM (origins). Never put a destination here
    "win_file_path_patterns": [string], // optional, max 20. Windows globs, e.g. **\\*.{py,js,ts}
    "mac_file_path_patterns": [string], // optional, max 20. macOS globs, e.g. **/*.{py,js,ts}
    "evidence_duplication_enabled": bool, // optional. Retain forensic evidence
    "rules": [Rule] // optional. Evaluated in list order: put an exception (allow) before the general rule (block)
  }
}

Rule (an element of classification_properties.rules):

{
  "id": string, // existing rules only: keep it on update, or the rule is re-added as new
  "user_scope": "all" | "specific", // required
  "ad_users": [string], // only when user_scope is 'specific'. AD user SIDs — provided by the user, cannot be looked up
  "ad_groups": [string], // only when user_scope is 'specific'. AD group SIDs — provided by the user, cannot be looked up
  "response_action": "allow" | "block" | "justify", // required. 'justify' is not valid on Printer or Local Application egress
  "detection_severity": "informational" | "low" | "medium" | "high" | "critical", // required
  "trigger_detection": bool, // required. Detections fire only when protection_mode is 'enforce'
  "notify_end_user": bool, // required
  "enable_usb_devices": bool, // required. Removable Media channel
  "enable_printer_egress": bool, // required. Printer channel, Windows only
  "enable_web_locations": bool, // required. Web Upload channel
  "enable_local_application_groups": bool, // required. Local Application channel
  "web_locations_scope": "all" | "specific", // required
  "web_locations": [string], // only when web_locations_scope is 'specific'. web_location IDs the data goes TO (destinations)
  "web_location_destination_groups": [string], // optional, max 15. Web location destination group IDs
  "local_application_groups": [string], // only with enable_local_application_groups. local_application_group IDs, max 15
  "enable_screen_capture_rule": bool, // optional. Needs the policy's enable_screen_capture (Windows)
  "description": string // optional
}

Update: send "id" plus only the fields to change, top-level or inside
classification_properties; omitted fields keep their stored values. A list you
send replaces the stored list. For rules, send the full current list (from
falcon_get_data_security_entities) with your change, and keep each existing
rule's "id": a rule without one is added as a new rule.
"""

POLICY_BODY_GUIDE = """\
Data Security Policy Body Guide
=================================

A Policy is platform-specific: pass platform_name ('win' or 'mac') as a tool
argument, never in the body. It carries inspection, notification and forensics
settings; enforcement lives on its classifications.

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

A new policy is created disabled and without host groups: is_enabled and
host_groups are not part of the create request — set them with an update.

Update: send "id" plus the fields to change; is_enabled (bool) and host_groups
([string] host group IDs) are update-only. Lists replace the stored list: to
add a classification, send the full current classifications list (from
falcon_get_data_security_entities) with the new ID in the right position.
"""

CONTENT_PATTERN_BODY_GUIDE = """\
Data Security Content Pattern Body Guide
==========================================

Search the predefined catalog first (e.g. filter category:~'PCI DSS'); create
a custom pattern only when none fits.

{
  "name": string, // required. No special characters
  "description": string, // required. What sensitive data it detects
  "category": "PII" | "PCI DSS" | "PHI" | "Custom" | "ITAR" | "Secret", // required
  "region": string, // required. e.g. 'ALL'
  "regexes": [string], // required. One entry per distinct pattern
  "example": string, // required. Sample text that the regexes match
  "min_match_threshold": integer // required, >= 1. Matches needed to trigger detection
}

Update: send "id" plus any of name, description, regexes, example,
min_match_threshold. category and region cannot be changed. regexes replaces
the stored list.
"""

CLOUD_APPLICATION_BODY_GUIDE = """\
Data Security Cloud Application Body Guide
============================================

A SaaS application that web locations reference via application_id. Search by
name first (FQDNs are not searchable) — predefined applications cover most
common services.

{
  "name": string, // required
  "description": string, // optional
  "urls": [{ "fqdn": string, "path": string }] // required. e.g. [{ "fqdn": "app.example.com", "path": "/" }]
}

Update: send "id" plus any of name, description, urls. urls replaces the
stored list.
"""

ENTERPRISE_ACCOUNT_BODY_GUIDE = """\
Data Security Enterprise Account Body Guide
=============================================

Separates corporate from personal use of a provider. A web_location that
references it (enterprise_account_id) becomes "managed".

{
  "name": string, // required. e.g. 'Corporate OneDrive'
  "application_group_id": "google" | "microsoft" | "box", // required
  "domains": [string], // required. The organization's domains for this provider, e.g. ['contoso.com']
  "plugin_config_id": string // links the Data Protection connector; needed for site-level tracking
}

Update: send "id" plus name and/or domains — the only updatable fields.
domains replaces the stored list.
"""

WEB_LOCATION_BODY_GUIDE = """\
Data Security Web Location Body Guide
=======================================

The same web location can be an origin (classification web_sources) or a
destination (rule web_locations). Search predefined locations first — a
duplicate custom one changes FQDN matching.

{
  "name": string, // required
  "application_id": string, // required. cloud_application ID
  "type": "custom", // required. Predefined locations cannot be created or changed
  "location_type": string, // required by the API spec; existing custom locations store ''
  "deleted": false, // required by the API spec
  "enterprise_account_id": string, // optional. Makes the location "managed" (corporate activity only)
  "provider_location_id": string, // optional. Site-level tracking (SharePoint site, Google shared drive, Box folder); needs the connector and enterprise_account_id
  "provider_location_name": string, // optional. Set together with provider_location_id
  "web_location_group_ids": [string] // optional
}

Update: send "id" and "name" plus the fields to change; omitted fields keep
their stored values. name is required unless the update sets
enterprise_account_id, in which case the stored name is kept and any name sent
is ignored. web_location_group_ids replaces the stored list.
"""

LOCAL_APPLICATION_BODY_GUIDE = """\
Data Security Local Application Body Guide
============================================

A desktop application (Windows only) whose data access a rule can scope through
a local_application_group.

{
  "name": string, // required
  "executable_name": string, // required. e.g. 'excel.exe'
  "group_ids": [string], // local_application_group IDs to join; use this to add a new application to existing groups
  "apply_rules_for_children_processes": bool, // rules also apply to child processes
  "enable_rename_detection": bool, // detect a renamed executable
  "emit_rule_matched_events_only": bool // emit events only when a rule matches
}

Update: send "id" plus the fields to change; the tool merges them onto the
current entity. group_ids replaces the stored list.
"""

LOCAL_APPLICATION_GROUP_BODY_GUIDE = """\
Data Security Local Application Group Body Guide
==================================================

Groups local applications so a rule's Local Application channel can target
them (rule local_application_groups).

{
  "name": string, // required
  "description": string, // required by the API spec
  "local_application_ids": [string] // required. local_application IDs in the group
}

Update: send "id" plus the fields to change; the tool merges them onto the
current entity. local_application_ids replaces the stored list.
"""

SENSITIVITY_LABEL_BODY_GUIDE = """\
Data Security Sensitivity Label Body Guide
============================================

A Microsoft (MIP) or Google label applied to files. Labels are normally synced
by the Microsoft 365 / Google Workspace connector — search before creating one.

{
  "name": string, // required
  "display_name": string, // required
  "external_id": string, // required. The label's ID at the provider
  "label_provider": "microsoft" | "google", // required
  "plugins_configuration_id": string, // required. The connector configuration ID
  "co_authoring": bool, // required
  "synced": bool // required
}

Create only: sensitivity labels cannot be updated.
"""
