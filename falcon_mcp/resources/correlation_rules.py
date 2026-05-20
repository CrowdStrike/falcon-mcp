"""
Contains Correlation Rules resources.
"""

from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, description)
SEARCH_CORRELATION_RULES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        """
        Rule name. Supports exact and wildcard match.
        Ex: name:'Suspicious PowerShell', name:~'PowerShell'
        """
    ),
    (
        "status",
        "String",
        """
        Rule execution status. Possible values:
        - active: Rule is enabled and running
        - inactive: Rule is disabled
        Ex: status:'active'
        """
    ),
    (
        "state",
        "String",
        """
        Version state of the rule. Possible values:
        - published: Rule is live and active
        - unpublished: Rule exists but is not published
        - draft: Rule is in draft and not yet published
        Ex: state:'published'
        """
    ),
    (
        "severity",
        "Integer",
        """
        Severity score of the rule. Valid values:
        10 (Informational), 30 (Low), 50 (Medium), 70 (High), 90 (Critical).
        Supports range operators.
        Ex: severity:>50, severity:>=70
        """
    ),
    (
        "type",
        "String",
        """
        Rule type. Possible values:
        - correlation: Standard correlation rule
        - behavioral: Behavioral detection rule
        Ex: type:'correlation'
        """
    ),
    (
        "tactic",
        "String",
        """
        MITRE ATT&CK tactic ID. Uses ATT&CK tactic IDs,
        not names.
        Ex: tactic:'TA0001', tactic:'TA0002'
        """
    ),
    (
        "technique",
        "String",
        """
        MITRE ATT&CK technique ID.
        Ex: technique:'T1059', technique:'T1003'
        """
    ),
    (
        "description",
        "String",
        """
        Rule description text. Supports wildcard match.
        Ex: description:~'lateral movement'
        """
    ),
    (
        "version",
        "Integer",
        """
        Rule version number. Supports range operators.
        Ex: version:>1
        """
    ),
    (
        "user_id",
        "String",
        """
        ID of the user who created or owns the rule.
        Ex: user_id:'api_client'
        """
    ),
    (
        "created_on",
        "Timestamp",
        """
        Creation timestamp. Supports range operators.
        Ex: created_on:>'2025-01-01'
        """
    ),
    (
        "last_updated_on",
        "Timestamp",
        """
        Last modification timestamp. Supports range operators.
        Ex: last_updated_on:>'2025-06-01'
        """
    ),
]

SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION = r"""Falcon Query Language (FQL) - Search Correlation Rules Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• ~: field_name:~'partial' (contains match, case insensitive)
• >, >=, <, <=: field_name:>50 (comparison for numbers/timestamps)
• !: field_name:!'value' (not equal)

=== DATA TYPES ===
• String: 'value'
• Integer: 50 (no quotes)
• Timestamp: 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'

=== COMBINING ===
• + = AND: status:'active'+severity:>50
• , = OR: tactic:'TA0001',tactic:'TA0002'

=== SORT OPTIONS ===
Sort fields: created_on, last_updated_on, name, severity, status
Sort formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
Example: 'last_updated_on.desc'

=== SEVERITY SCORES ===
• 10 = Informational
• 30 = Low
• 50 = Medium
• 70 = High
• 90 = Critical

Use range operators for severity:
• High and above: severity:>=70
• Medium and above: severity:>=50
• Critical only: severity:>=90

=== STATUS vs STATE ===
These are distinct fields:
• status: execution state — 'active' or 'inactive'
• state: version lifecycle — 'published', 'unpublished', or 'draft'

A rule can be active but unpublished, or published but inactive.

=== TACTIC FORMAT ===
Tactic field uses MITRE ATT&CK tactic IDs (TA####), not names.
• ✅ Correct: tactic:'TA0001'
• ❌ Wrong: tactic:'Execution'

Common tactic IDs:
• TA0001: Initial Access
• TA0002: Execution
• TA0003: Persistence
• TA0004: Privilege Escalation
• TA0005: Defense Evasion
• TA0006: Credential Access
• TA0007: Discovery
• TA0008: Lateral Movement
• TA0009: Collection
• TA0010: Exfiltration
• TA0011: Command and Control

=== falcon_search_correlation_rules FQL filter available fields ===

""" + generate_md_table(SEARCH_CORRELATION_RULES_FQL_FILTERS) + """

=== FILTER EXAMPLES ===

# Active high-severity rules
status:'active'+severity:>=70

# Published rules covering a MITRE tactic
state:'published'+tactic:'TA0001'

# Recently updated published rules
state:'published'+last_updated_on:>'2025-01-01'

# Rules by name (wildcard)
name:~'PowerShell'

# Critical active rules
status:'active'+severity:>=90

# Rules for a specific technique
technique:'T1059'

# Active rules covering lateral movement or credential access
status:'active'+(tactic:'TA0008',tactic:'TA0006')

# High-severity active rules updated recently
status:'active'+severity:>=70+last_updated_on:>'2025-01-01'

# Draft rules (in progress, not yet published)
state:'draft'

# Only correlation type rules (exclude behavioral)
type:'correlation'+status:'active'
"""
