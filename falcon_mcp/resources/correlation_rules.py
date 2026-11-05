"""
Contains Correlation Rules resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Shared MITRE ATT&CK Enterprise Tactics reference (v16) — used by both
# the rules FQL guide and the templates FQL guide so the table stays in sync.
MITRE_ATTACK_TACTICS_REFERENCE = """\
=== MITRE ATT&CK ENTERPRISE TACTICS (v16) — ID, NAME, AND ALIASES ===
Use the aliases to match fuzzy user intent to the correct tactic ID.
If a user says any alias term, use the corresponding tactic ID in the filter.

• TA0043: Reconnaissance
  Aliases: recon, scanning, footprinting, OSINT, information gathering,
  target selection, open-source intelligence

• TA0042: Resource Development
  Aliases: infrastructure setup, staging, acquiring infrastructure,
  developing capabilities, establishing accounts

• TA0001: Initial Access
  Aliases: entry point, intrusion, exploitation, phishing, spearphishing,
  drive-by, trusted relationship, supply chain

• TA0002: Execution
  Aliases: code execution, running malware, script execution, command execution,
  PowerShell, scripting, user execution

• TA0003: Persistence
  Aliases: backdoor, implant, foothold, maintaining access, boot or logon,
  scheduled task, registry run key, startup

• TA0004: Privilege Escalation
  Aliases: privesc, elevating privileges, admin access, root access,
  token manipulation, exploitation for privilege escalation

• TA0005: Defense Evasion
  Aliases: stealth, evasion, hiding, obfuscation, masquerading,
  process injection, indicator removal, rootkit, disabling defenses

• TA0112: Defense Impairment
  Aliases: disabling security, tampering, impairing defenses, breaking security,
  disabling logging, killing security tools

• TA0006: Credential Access
  Aliases: credential theft, password stealing, credential dumping, brute force,
  keylogging, credential harvesting, Kerberoasting, pass-the-hash

• TA0007: Discovery
  Aliases: enumeration, network scanning, system discovery, account discovery,
  network share discovery, permission groups discovery

• TA0008: Lateral Movement
  Aliases: pivoting, moving laterally, spreading, remote services,
  pass-the-ticket, WMI, RDP, SMB, internal spearphishing

• TA0009: Collection
  Aliases: data gathering, data staging, harvesting, screen capture,
  clipboard data, email collection, audio capture

• TA0011: Command and Control
  Aliases: C2, C&C, beaconing, callback, remote access, encrypted channel,
  proxy, web service, DNS tunneling

• TA0010: Exfiltration
  Aliases: data theft, data exfil, stealing data, data transfer,
  exfiltration over C2, exfiltration over web service

• TA0040: Impact
  Aliases: destruction, ransomware, wiping, disruption, sabotage,
  data encryption, defacement, denial of service, resource hijacking
"""

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
        Rule name. Exact match is case-sensitive. Use ~* with * wildcards for
        case-insensitive substring matching.
        Ex (exact): name:'Suspicious PowerShell'
        Ex (substring): name:~*'*powershell*'
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
        "mitre_attack.tactic_id",
        "String",
        """
        MITRE ATT&CK tactic ID from the mitre_attack mapping.
        Uses ATT&CK tactic IDs, not names.
        Ex: mitre_attack.tactic_id:'TA0001'
        """
    ),
    (
        "mitre_attack.technique_id",
        "String",
        """
        MITRE ATT&CK technique ID from the mitre_attack mapping.
        Ex: mitre_attack.technique_id:'T1059'
        """
    ),
    (
        "description",
        "String",
        """
        Rule description text. Use ~* with * wildcards for case-insensitive
        substring matching.
        Ex (substring): description:~*'*lateral movement*'
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

# List of tuples containing template filter options: (name, type, description)
SEARCH_CORRELATION_RULE_TEMPLATES_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Description",
    ),
    (
        "name",
        "String",
        """
        Template name. Exact match is case-sensitive. Use ~* with * wildcards
        for case-insensitive substring matching.
        Ex (exact): name:'Suspicious PowerShell'
        Ex (substring): name:~*'*powershell*'
        """,
    ),
    (
        "description",
        "String",
        """
        Template description. Use ~* with * wildcards for case-insensitive
        substring matching. Best for natural-language keyword searches.
        Ex (substring): description:~*'*lateral movement*'
        """,
    ),
    (
        "vendor",
        "String",
        """
        Vendor or source of the template.
        Ex: vendor:'CrowdStrike'
        """,
    ),
    (
        "outcome",
        "String",
        """
        Rule outcome type when template is deployed. Possible values:
        - detection: Creates detections
        - case: Creates cases
        Ex: outcome:'detection'
        """,
    ),
    (
        "mitre_attack.tactic_id",
        "String",
        """
        MITRE ATT&CK tactic ID. Uses ATT&CK tactic IDs, not names.
        See the tactic reference table below for IDs and aliases.
        Ex: mitre_attack.tactic_id:'TA0001'
        """,
    ),
    (
        "mitre_attack.technique_id",
        "String",
        """
        MITRE ATT&CK technique ID from the mitre_attack mapping.
        Ex: mitre_attack.technique_id:'T1059'
        """,
    ),
    (
        "type",
        "String",
        """
        Template type.
        Ex: type:'correlation'
        """,
    ),
]

SEARCH_CORRELATION_RULE_TEMPLATES_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Correlation Rule Templates Guide

=== PURPOSE ===
Use this guide to translate natural language into FQL filters for template discovery.
Users may describe threats, tactics, or detection goals without knowing exact template
names or MITRE IDs — follow the search strategy below to map their intent.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value' (exact match, case-sensitive)
• ~*: field_name:~*'*term*' (glob/wildcard match, case-insensitive — use * as a
  wildcard; wrap the term in * for true substring/contains matching)
• >, >=, <, <=: field_name:>50 (comparison for numbers/timestamps)
• !: field_name:!'value' (not equal)

=== CHOOSING THE RIGHT STRING OPERATOR ===
• Exact match (must know precise casing): name:'Suspicious PowerShell'
• Substring/contains match (case-insensitive, anywhere in value): name:~*'*powershell*'

=== COMBINING ===
• + = AND: name:~*'*lateral*'+name:~*'*movement*'
• , = OR: mitre_attack.tactic_id:'TA0001',mitre_attack.tactic_id:'TA0002'

=== BROADENING MULTI-WORD SEARCHES ===
For multi-word searches, split each keyword into its own ~* clause joined with +.
This matches regardless of word order, extra whitespace, or intervening words —
over-fetch broadly, then pick the best matches from the results:
• name:~*'*email*'+name:~*'*phishing*'
  Matches "Phishing Email Link Clicked", "Email Phishing Alert", etc.
• description:~*'*credential*'+description:~*'*theft*'
  Matches descriptions containing both words in any order.

=== NATURAL LANGUAGE SEARCH STRATEGY ===
When the user describes a threat or detection goal in natural language:

1. CHECK MITRE TACTICS FIRST: If the user's intent maps to a known MITRE tactic
   (see the alias table below), filter by tactic ID. This is the most precise approach.
   Example: "detect lateral movement" → mitre_attack.tactic_id:'TA0008'

2. CHECK MITRE TECHNIQUES: If the user names a specific technique or sub-technique,
   filter by technique ID.
   Example: "PowerShell execution" → mitre_attack.technique_id:'T1059'

3. FALL BACK TO KEYWORD SEARCH: If no MITRE mapping fits, search the description
   and/or name fields with ~* wildcard matching. Split multi-word phrases into
   separate ~* clauses.
   Example: "ransomware detection" → description:~*'*ransomware*'

4. COMBINE APPROACHES: Use + (AND) to combine tactic filters with keyword filters
   for maximum precision.
   Example: mitre_attack.tactic_id:'TA0040'+description:~*'*ransomware*'

=== SEVERITY SCORES ===
• 10 = Informational
• 30 = Low
• 50 = Medium
• 70 = High
• 90 = Critical

=== SEVERITY: API vs. HUMAN PRESENTATION ===
• API / FQL filters: always use the integer (e.g. severity:>=70)
• Responses to the user: always use the name (e.g. "High", "Critical")
  Never show raw severity numbers to the user without the corresponding name.

"""
    + MITRE_ATTACK_TACTICS_REFERENCE
    + """
=== falcon_search_correlation_rule_templates FQL filter available fields ===

"""
    + generate_md_table(SEARCH_CORRELATION_RULE_TEMPLATES_FQL_FILTERS)
    + """

=== FILTER EXAMPLES ===

# Templates for detecting lateral movement (via MITRE tactic)
mitre_attack.tactic_id:'TA0008'

# Templates for credential theft (via MITRE tactic)
mitre_attack.tactic_id:'TA0006'

# Templates mentioning ransomware (keyword in description)
description:~*'*ransomware*'

# Templates for PowerShell-related detections (keyword in name)
name:~*'*powershell*'

# Templates for a specific MITRE technique
mitre_attack.technique_id:'T1059'

# Templates covering initial access OR persistence
mitre_attack.tactic_id:'TA0001',mitre_attack.tactic_id:'TA0003'

# CrowdStrike-authored templates
vendor:'CrowdStrike'

# Templates with "phishing" anywhere in name or description
name:~*'*phishing*',description:~*'*phishing*'

# Broad multi-word search (order-independent)
description:~*'*brute*'+description:~*'*force*'

# Combine tactic + keyword for precision
mitre_attack.tactic_id:'TA0040'+description:~*'*ransomware*'
"""
)


SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION = (
    r"""Falcon Query Language (FQL) - Search Correlation Rules Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value' (exact match, case-sensitive)
• ~*: field_name:~*'*term*' (glob/wildcard match, case-insensitive — use * as a
  wildcard; wrap the term in * for true substring/contains matching)
• >, >=, <, <=: field_name:>50 (comparison for numbers/timestamps)
• !: field_name:!'value' (not equal)

=== IMPORTANT: CHOOSING THE RIGHT STRING OPERATOR ===
• Exact match (must know precise casing): name:'Suspicious PowerShell'
• Substring/contains match (case-insensitive, anywhere in value): name:~*'*powershell*'

=== BROADENING MULTI-WORD SEARCHES ===
For multi-word searches, split each keyword into its own ~* clause joined with +.
This matches regardless of word order, extra whitespace, or intervening words —
over-fetch broadly, then pick the best matches from the results:
• name:~*'*email*'+name:~*'*phishing*'
  Matches "Phishing Email Link Clicked", "Email Phishing Alert", etc.
• description:~*'*credential*'+description:~*'*theft*'
  Matches descriptions containing both words in any order.

=== DATA TYPES ===
• String: 'value'
• Integer: 50 (no quotes)
• Timestamp: 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'

=== COMBINING ===
• + = AND: status:'active'+severity:>50
• , = OR: mitre_attack.tactic_id:'TA0001',mitre_attack.tactic_id:'TA0002'

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

=== SEVERITY: API vs. HUMAN PRESENTATION ===
• API / FQL filters: always use the integer (e.g. severity:>=70)
• Responses to the user: always use the name (e.g. "High", "Critical")
  Never show raw severity numbers to the user without the corresponding name.

=== STATUS vs STATE ===
These are distinct fields:
• status: execution state — 'active' or 'inactive'
• state: version lifecycle — 'published', 'unpublished', or 'draft'

A rule can be active but unpublished, or published but inactive.

=== MITRE ATT&CK MAPPING ===
The mitre_attack field uses ATT&CK tactic IDs (TA####) and technique IDs (T####).
Filter on nested fields:
• ✅ Correct: mitre_attack.tactic_id:'TA0001'
• ❌ Wrong: mitre_attack.tactic_id:'Execution'

"""
    + MITRE_ATTACK_TACTICS_REFERENCE
    + """
=== falcon_search_correlation_rules FQL filter available fields ===

""" + generate_md_table(SEARCH_CORRELATION_RULES_FQL_FILTERS) + """

=== FILTER EXAMPLES ===

# Active high-severity rules
status:'active'+severity:>=70

# Published rules covering a MITRE tactic
state:'published'+mitre_attack.tactic_id:'TA0001'

# Recently updated published rules
state:'published'+last_updated_on:>'2025-01-01'

# Rules by name (case-insensitive substring — finds "powershell" anywhere in the name)
name:~*'*powershell*'

# Critical active rules
status:'active'+severity:>=90

# Rules for a specific technique
mitre_attack.technique_id:'T1059'

# Active rules covering lateral movement or credential access
status:'active'+(mitre_attack.tactic_id:'TA0008',mitre_attack.tactic_id:'TA0006')

# High-severity active rules updated recently
status:'active'+severity:>=70+last_updated_on:>'2025-01-01'

# Draft rules (in progress, not yet published)
state:'draft'

# Only correlation type rules (exclude behavioral)
type:'correlation'+status:'active'

# Search description for a keyword (case-insensitive substring)
description:~*'*phishing*'

# Broad multi-word name search (order-independent, matches both words anywhere)
name:~*'*email*'+name:~*'*threat*'
"""
)
