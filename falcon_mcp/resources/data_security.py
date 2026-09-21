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
        Use exact match with the full email address.
        Note: ~ on email fields matches only complete @-delimited segments
        (the full local part or the whole address), not arbitrary substrings.

        Ex: created_by:'user@example.com'
        """,
    ),
    (
        "modified_by",
        "String",
        "Yes",
        """
        Email of the user who last modified the classification.
        Use exact match with the full email address.
        Note: ~ on email fields matches only complete @-delimited segments
        (the full local part or the whole address), not arbitrary substrings.

        Ex: modified_by:'user@example.com'
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
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
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
        Policy description text. Supports text match (~).

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
        Use exact match with the full email address.
        Note: ~ on email fields matches only complete @-delimited segments
        (the full local part or the whole address), not arbitrary substrings.

        Ex: modified_by:'user@example.com'
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
        Whether the content pattern has been deleted.

        Ex: deleted:false
        Ex: deleted:true
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
• deleted:false - Active (non-deleted) patterns
• region:'US'+type:'predefined' - US-specific predefined patterns
• name:~'credit' - Patterns with "credit" in the name

=== SORTING ===

Supported sort fields: category.asc, region.asc
(name sorting is not honored by this endpoint in either direction, so it is omitted)

=== IMPORTANT NOTES ===
• Use single quotes around values: 'value'
• Use ~ operator for case-insensitive name matching
• Boolean values have no quotes: deleted:false
• type values are lowercase: 'custom', 'predefined'
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


def _fql_doc(title: str, tool_name: str, filters: list[tuple], sort_fields: str) -> str:
    """Assemble a standard entity FQL guide from its filter table and sort fields."""
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
        + "• Boolean values have no quotes (e.g. deleted:false)\n"
        + "• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'\n"
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
        Whether the cloud application has been soft-deleted.

        Ex: deleted:false
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

        Ex: application_group_id:'abc123'
        """,
    ),
]

SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Cloud Applications",
    "falcon_search_data_security_entities (entity_type='cloud_application')",
    SEARCH_CLOUD_APPLICATIONS_FQL_FILTERS,
    "name.asc, name.desc",
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
        Whether the enterprise account has been soft-deleted.

        Ex: deleted:false
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the enterprise account was created (RFC3339).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the enterprise account was last updated (RFC3339).

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
        Whether the web location has been soft-deleted.

        Ex: deleted:false
        """,
    ),
    (
        "application_id",
        "String",
        "Yes",
        """
        Associated cloud application ID.

        Ex: application_id:'abc123'
        """,
    ),
    (
        "provider_location_id",
        "String",
        "Yes",
        """
        Provider-assigned location ID.

        Ex: provider_location_id:'site-1'
        """,
    ),
    (
        "enterprise_account_id",
        "String",
        "Yes",
        """
        Enterprise account ID this web location belongs to.

        Ex: enterprise_account_id:'abc123'
        """,
    ),
]

SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Web Locations",
    "falcon_search_data_security_entities (entity_type='web_location')",
    SEARCH_WEB_LOCATIONS_FQL_FILTERS,
    "Sort is not supported for this entity.",
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
        Whether the local application has been soft-deleted.

        Ex: deleted:false
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the local application was created (RFC3339).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the local application was last updated (RFC3339).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Local Applications",
    "falcon_search_data_security_entities (entity_type='local_application')",
    SEARCH_LOCAL_APPLICATIONS_FQL_FILTERS,
    "Sort is not supported for this entity.",
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
        Whether the local application group has been soft-deleted.

        Ex: deleted:false
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the group was created (RFC3339).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the group was last updated (RFC3339).

        Ex: last_updated:>'2024-06-01'
        """,
    ),
]

SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION = _fql_doc(
    "Search Data Security Local Application Groups",
    "falcon_search_data_security_entities (entity_type='local_application_group')",
    SEARCH_LOCAL_APPLICATION_GROUPS_FQL_FILTERS,
    "Sort is not supported for this entity.",
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
        Whether the sensitivity label has been soft-deleted.

        Ex: deleted:false
        """,
    ),
    (
        "created",
        "Timestamp",
        "Yes",
        """
        Date the label was created (RFC3339).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the label was last updated (RFC3339).

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
        Date the file type was created (RFC3339).

        Ex: created:>'2024-01-01'
        """,
    ),
    (
        "last_updated",
        "Timestamp",
        "Yes",
        """
        Date the file type was last updated (RFC3339).

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

Policies reference Classifications by ID; Classifications combine detection
criteria (Content Patterns, File Types, Web Origins, Sensitivity Labels) with
response Rules. Use search/get tools to resolve referenced IDs.

Policy  (HOW to respond)
└── references one or more Classifications
        ├── WHAT to detect — any combination of:
        │     ├── Content Patterns (content): regex-based data pattern detectors
        │     ├── File Paths (context): where data is stored/named (glob syntax)
        │     ├── File Types (context): true file type, regardless of extension
        │     ├── Web Origins (context): where data originated from
        │     └── Sensitivity (MIP) Labels (context): Microsoft Information Protection labels
        └── one or more Rules  (WHO / WHICH channels / WHAT action)
              ├── Egress Channels: USB, Printer, Web Upload, Local Application
              ├── User Scope: all users OR specific AD Users/Groups (by SID)
              └── Response Action: block, allow, or justify

When displaying a policy or classification, offer to drill into referenced
entity IDs (classifications, content patterns, web locations, etc.) and
present the relationships using the tree structure above.

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

1. Always use falcon-mcp tools for Data Security queries — do not fabricate
   configuration details from memory.
2. When in doubt about any setting value, ask the user before proceeding.
3. After displaying entity details, check for UUIDs or references to other
   entities. Offer to fetch and display those relationships using the data
   model in falcon://data-security/entities/model-guide.

=== FRESHNESS RULE ===

When presenting details about a specific entity (policy, classification, etc.),
always re-fetch it by ID using the appropriate get tool (e.g.,
falcon_get_data_security_entities with entity_type='policy') rather than relying on earlier search
results. Search results may be stale due to API caching or eventual
consistency — only a direct get-by-ID call guarantees the current state.
"""

FORMATTING_GUIDE_DOCUMENTATION = """\
Data Security Output Formatting Guide
=========================================

=== ENTITY LISTINGS ===

For multiple entities (policies, classifications, etc.), use clean aligned columns:

  #  Name                                    Mode       CPs  Rules  Created
 --- --------------------------------------- ---------- ---- ------ ----------
  1  Block PCI uploads to Gmail and Box       Sim.        3     1   2026-08-14
  2  Client Privacy                           Enf.        4     3   2024-10-24
  3  Customer PII                             Enf.        2     3   2023-08-31

Use emoji color indicators for protection modes:
  - Enforce: blue circle
  - Simulate: yellow circle
  - Monitor: green circle

Do not use red X emoji for missing/unset config — just say "Off".

=== SINGLE ENTITY DETAIL ===

For a single policy's full configuration, use a header block followed by
labeled sections. This is the template for "show me policy X":

  Policy: <name>  <mode circle>
  |   ID: <uuid>
  |   Platform: <platform> | Status: <enabled/disabled> | Precedence: <n> | Default: <yes/no>
  |   Description: <text or "(none)">
  |   Created: <date> by <user>
  |   Modified: <date> by <user>
  |   Host Groups: <n> assigned
  |     - <group id>
  |     - <group id>

  Inspection
  - Content inspection: <On/Off> | Context inspection: <On/Off> | Network inspection: <On/Off>
  - Clipboard inspection: <On/Off> (web origin: <On/Off>)
  - Min confidence: <level> | Depth: <level>
  - Similarity detection: <On/Off> (threshold <n>)
  - Max file size to inspect: ~<size>
  - Browsers without active extension: <action>
  - Print monitor: <On/Off> | Screen capture: <On/Off>
  - Block all data access: <On/Off>

  Evidence
  - Download: <On/Off> | Duplication: <On/Off> | Encrypted: <On/Off>
  - Storage: min <n>% free disk, max <n> (<unit>)

  End-user justification: <enabled/disabled>, <timeout>, <required?>; options: <list>

Rules for single entity detail:
  - Put the protection-mode circle (blue=Enforce, yellow=Simulate,
    green=Monitor) on the header line next to the name.
  - Use "Off" for disabled/unset settings — never a red X emoji.
  - For attached classifications, render NAMES, not raw UUIDs. If you only
    have the IDs, say "<n> classifications attached" and OFFER to expand them
    into names/patterns/rules rather than dumping the UUID list.
  - Omit a section entirely if the entity carries no data for it.

=== RELATIONSHIP DRILL-DOWNS ===

For policy/classification relationship details, use ASCII tree format:

  Policy: <name>
  |   ID: <uuid>
  |   Platform: <platform> | Status: <status> | Precedence: <n>
  |
  +-- Classification: <name>
      |   ID: <uuid>
      |   Protection Mode: <mode>
      |
      +-- WHAT TO DETECT (Content Patterns)
      |   +-- <pattern name>
      |   |     Category: <cat> | Threshold: <n>
      |   +-- <pattern name>
      |         Category: <cat> | Threshold: <n>
      |
      +-- RULE: <rule description>
          +-- User Scope .......... <scope>
          +-- Severity ............ <severity>
          +-- Response Action ...... <action>
          +-- Notify End User ...... <yes/no>
          +-- EGRESS CHANNELS
                +-- Web Locations .... <on/off> (<scope>)
                +-- USB Devices ...... <on/off>
                +-- Printer .......... <on/off>
                +-- Local Apps ....... <on/off>

=== SUMMARY BOXES ===

For confirmations, gap analysis, and state summaries, use double-line box style:

  +===============================================================+
  ||                                                              ||
  ||   CHANGES APPLIED SUCCESSFULLY                               ||
  ||                                                              ||
  ||   Policy:  <name>                                            ||
  ||   State:   Enabled  |  Simulate                              ||
  ||                                                              ||
  +===============================================================+

Rules for summary boxes:
  - NO EMOJI inside the box — text only
  - Pad all content lines to the SAME width so the right border aligns
  - Count characters carefully — every line must be identical length
  - Do NOT use single-line box drawing for these summary panels
"""
