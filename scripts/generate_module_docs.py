"""Generate Starlight documentation pages from falcon_mcp module source code.

Introspects module classes, tool methods, and resource definitions to produce
markdown files for docs/modules/.

Usage:
    uv run python scripts/generate_module_docs.py
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "docs" / "modules"
SITE_BASE_PATH = "/falcon-mcp"

# Module display metadata — overrides only.
# Titles and descriptions are auto-derived from module docstrings.
# Add entries here when you need a custom title, slug, or description.
MODULE_METADATA: dict[str, dict[str, Any]] = {
    "agentworks": {
        "title": "AgentWorks",
    },
    "cases": {
        "title": "Case Management",
        "slug": "cases",
    },
    "cloud": {
        "title": "Cloud Security",
    },
    "customioa": {
        "slug": "custom-ioa",
    },
    "dataprotection": {
        "slug": "data-protection",
    },
    "fusion": {
        "title": "Fusion SOAR",
    },
    "hostgroups": {
        "slug": "host-groups",
    },
    "idp": {
        "title": "Identity Protection",
    },
    "scheduledreports": {
        "slug": "scheduled-reports",
    },
    "sensorusage": {
        "slug": "sensor-usage",
    },
    "serverless": {
        "title": "Serverless",
    },
    "shield": {
        "title": "Shield",
    },
    "zerotrustassessment": {
        "title": "Zero Trust Assessment",
        "slug": "zero-trust-assessment",
    },
}

_OVERVIEW_LINK = f"{SITE_BASE_PATH}/modules/overview/#crowdstrike-hosted-mcp-differences"


def _module_link(module_key: str) -> str:
    """Site URL for a module page, honoring any slug override in MODULE_METADATA."""
    slug = MODULE_METADATA.get(module_key, {}).get("slug", module_key)
    return f"{SITE_BASE_PATH}/modules/{slug}/"


# Notes on differences from CrowdStrike's hosted Falcon MCP, rendered as an
# admonition under the module description. Keyed by module_key. See
# generate_overview_page for the summary of these differences.
HOSTED_MCP_MODULE_NOTES: dict[str, str] = {
    "fusion": (
        "This module is not available on CrowdStrike's hosted Falcon MCP; it is only "
        f"available when self-hosting this server. See [module overview]({_OVERVIEW_LINK})."
    ),
    "zerotrustassessment": (
        "This module is not available on CrowdStrike's hosted Falcon MCP; it is only "
        f"available when self-hosting this server. See [module overview]({_OVERVIEW_LINK})."
    ),
    "rtr": (
        "This module is not available on CrowdStrike's hosted Falcon MCP; it is only "
        f"available when self-hosting this server. See [module overview]({_OVERVIEW_LINK})."
    ),
    "policies": (
        "CrowdStrike's hosted Falcon MCP does not use these unified, `policy_type`-discriminated "
        "tools. It instead exposes six policy-type-specific variants of each tool below, suffixed "
        "by type (`_prevention`, `_sensor_update`, `_firewall`, `_device_control`, `_response`, "
        "`_content_update`) with no `policy_type` parameter — for example `falcon_search_policies` "
        "here corresponds to `falcon_search_policies_firewall`, `falcon_search_policies_prevention`, "
        f"etc. on the hosted MCP. See [module overview]({_OVERVIEW_LINK})."
    ),
}

# Notes on tools not (yet) available on CrowdStrike's hosted Falcon MCP, rendered
# as an admonition under the tool heading. Keyed by full tool name (falcon_*).
HOSTED_MCP_TOOL_NOTES: dict[str, str] = {
    "falcon_search_cloud_insights": (
        f"Not available on CrowdStrike's hosted Falcon MCP. See [module overview]({_OVERVIEW_LINK})."
    ),
    "falcon_get_cloud_asset_insights": (
        f"Not available on CrowdStrike's hosted Falcon MCP. See [module overview]({_OVERVIEW_LINK})."
    ),
    "falcon_list_cloud_insight_definitions": (
        f"Not available on CrowdStrike's hosted Falcon MCP. See [module overview]({_OVERVIEW_LINK})."
    ),
    "falcon_search_managed_assets": (
        f"Not available on CrowdStrike's hosted Falcon MCP. See [module overview]({_OVERVIEW_LINK})."
    ),
}

# Natural language prompt examples for each tool, shown in generated docs
TOOL_EXAMPLES: dict[str, list[str]] = {
    # AgentWorks
    "falcon_search_agentworks_agents": [
        "List my AgentWorks agents",
        "Which agents run on the claude-4-6-sonnet model?",
    ],
    "falcon_search_agentworks_agent_versions": [
        "Show me all versions of agent 467e856f",
        "Find the published versions of this agent",
    ],
    "falcon_search_agentworks_spans": [
        "Show the spans for trace abc123",
        "Find errored LLM spans in trace abc123",
    ],
    "falcon_get_agentworks_agent_invocation": [
        "Check the status of invocation inv-123",
    ],
    "falcon_invoke_agentworks_agent": [
        "Run the IOC review agent with the prompt 'Reply OK'",
        "Invoke agent 467e856f and summarize today's critical detections",
        "Test version v-42 of this agent with the prompt 'Reply OK'",
    ],
    # Cases
    "falcon_search_cases": [
        "Show me any open cases with high severity or above",
        "What cases have been created in the last 24 hours?",
    ],
    "falcon_get_cases": [
        "Pull up the full details on that case",
    ],
    "falcon_create_case": [
        "Create a critical case called 'Suspicious lateral movement from WORKSTATION-42'",
        "Open a high-severity case for the credential theft alerts and attach them as evidence",
        "Create a case with a markdown-formatted description",
    ],
    "falcon_update_case": [
        "Set that case to in_progress and assign it to the analyst",
        "Close the case — investigation is complete",
        "Rewrite the case description as markdown",
    ],
    "falcon_add_case_alert_evidence": [
        "Attach these detection alerts to the case",
    ],
    "falcon_add_case_event_evidence": [
        "Add these NGSIEM event IDs to the case as evidence",
    ],
    "falcon_manage_case_tags": [
        "Tag that case with 'ransomware' and 'escalated'",
        "Remove the 'escalated' tag from that case",
    ],
    "falcon_list_case_templates": [
        "What case templates are available?",
    ],
    "falcon_aggregate_case_slas": [
        "How many case SLA policies do we have?",
        "Break down our case SLAs by who created them",
    ],
    "falcon_aggregate_case_templates": [
        "How many case templates has each person created?",
        "Count the case templates added in the last 30 days",
    ],
    "falcon_aggregate_case_access_tags": [
        "What access tags are used to restrict case visibility, and how many of each?",
    ],
    "falcon_aggregate_case_notification_groups": [
        "How many case notification groups are configured?",
        "Show notification group counts by creator",
    ],
    "falcon_aggregate_case_file_details": [
        "What file names show up most often across case attachments?",
        "How many files are attached to these two cases?",
    ],
    # Correlation Rules
    "falcon_search_correlation_rules": [
        "Show me all active high-severity correlation rules",
        "Find correlation rules covering lateral movement tactics",
    ],
    "falcon_create_correlation_rule": [
        "Create a correlation rule using this CQL query: #event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*",
    ],
    "falcon_update_correlation_rule": [
        "Disable the correlation rule — set its status to inactive",
        "Update the rule severity to critical (90)",
    ],
    "falcon_delete_correlation_rules": [
        "Delete the test correlation rule we created",
    ],
    # Cloud
    "falcon_search_kubernetes_containers": [
        "Find all containers running in AWS clusters",
        "Show me containers in the prod cluster",
    ],
    "falcon_count_kubernetes_containers": [
        "How many containers are running in Azure?",
    ],
    "falcon_search_images_vulnerabilities": [
        "Find image vulnerabilities with CVSS score above 7",
    ],
    "falcon_search_cspm_assets": [
        "Find all AWS EC2 instances in my cloud inventory",
    ],
    "falcon_search_iom_findings": [
        "Show me critical open CSPM misconfiguration findings in AWS",
        "Find IOM findings for S3 buckets with public access",
        "What CSPM IOM findings are suppressed as accepted risk?",
    ],
    "falcon_search_cspm_suppression_rules": [
        "List all CSPM IOM suppression rules and their reasons",
        "Show me which CSPM findings are being suppressed and why",
    ],
    "falcon_create_cspm_suppression_rule": [
        "Create a CSPM suppression rule for the S3 encryption finding in the dev account as accepted risk",
        "Suppress the IAM password policy IOM finding as a false positive, expiring in 30 days",
    ],
    "falcon_delete_cspm_suppression_rules": [
        "Delete CSPM suppression rule abc-123",
        "Remove the CSPM IOM suppression rule for the S3 public access finding",
    ],
    "falcon_search_cloud_risks": [
        "Show me all open critical cloud risks in AWS",
        "Which account has the most unresolved critical risks?",
        "What new cloud risks appeared in the last 7 days?",
        "Show me risks for the production cloud group",
        "What cloud risks have been suppressed and why?",
    ],
    "falcon_search_cloud_groups": [
        "What cloud groups are configured in my environment?",
        "List all cloud groups tagged as production",
    ],
    "falcon_get_cloud_groups": [
        "Get the details for cloud group abc-123",
    ],
    "falcon_search_cloud_insights": [
        "What is internet-exposed in my cloud accounts?",
        "Which IAM identities have admin and are actually unused?",
        "Which exposed storage might hold sensitive data?",
        "Which access keys are stale or unrotated?",
    ],
    "falcon_get_cloud_asset_insights": [
        "Show me all the insight facts and context for cloud asset abc-123",
        "Why is this asset flagged — give me its full insight detail",
    ],
    "falcon_list_cloud_insight_definitions": [
        "What cloud security insights are available for Identity?",
        "List all insight definitions across all categories",
        "Which compliance controls map to cloud network insights?",
    ],
    # Custom IOA
    "falcon_search_ioa_rule_groups": [
        "Find enabled Windows Custom IOA rule groups",
    ],
    "falcon_get_ioa_platforms": [
        "What platforms are available for Custom IOA rule groups?",
    ],
    "falcon_get_ioa_rule_types": [
        "What Custom IOA rule types are available?",
    ],
    "falcon_create_ioa_rule_group": [
        "Create a Windows IOA rule group named 'Suspicious PowerShell Activity'",
    ],
    "falcon_update_ioa_rule_group": [
        "Disable IOA rule group abc123",
    ],
    "falcon_delete_ioa_rule_groups": [
        "Delete Custom IOA rule groups abc123 and def456",
    ],
    "falcon_create_ioa_rule": [
        "Add a process creation rule to IOA group abc123 that detects cmd.exe spawned from Word",
    ],
    "falcon_update_ioa_rule": [
        "Enable IOA rule instance abc in group xyz",
    ],
    "falcon_delete_ioa_rules": [
        "Delete rules from IOA group abc123",
    ],
    # Data Protection
    "falcon_search_data_protection_classifications": [
        "What Data Protection classifications are configured in my environment?",
        "Show me the classification rules that detect credit card data",
    ],
    "falcon_search_data_protection_policies": [
        "List all enabled Windows Data Protection policies",
        "Show me the Mac Data Protection policies and their precedence order",
    ],
    "falcon_search_data_protection_content_patterns": [
        "What predefined content patterns are available for Data Protection?",
        "Show me custom Data Protection regex patterns in the Financial category",
    ],
    # Detections
    "falcon_search_detections": [
        "Show me new high severity detections from the last 7 days",
        "Find all unassigned critical detections",
    ],
    "falcon_get_detection_details": [
        "Get me the details for this detection",
    ],
    "falcon_aggregate_detections": [
        "How many detections do we have by severity?",
        "What are the top 10 hosts by alert count this week?",
        "Show me alert volume per day for the last 30 days",
        "How many distinct hosts have critical alerts?",
    ],
    "falcon_update_detections": [
        "Mark detection abc123 as in_progress",
        "Assign detection abc123 to analyst@example.com",
        "Close these detections and add a comment: resolved via playbook",
        "Mark detection abc123 as a true positive and close it",
        "Remove all fc/ prefixed tags from this detection",
    ],
    # Discover
    "falcon_search_applications": [
        "Find all Chrome installations across my environment",
    ],
    "falcon_search_unmanaged_assets": [
        "Show me unmanaged Windows devices on the network",
    ],
    "falcon_search_managed_assets": [
        "Which managed Windows hosts are unencrypted?",
        "List critical assets that don't have Credential Guard enabled",
    ],
    # Firewall
    "falcon_search_firewall_rules": [
        "Show me all enabled Windows firewall rules",
        "Find firewall rules matching 'outbound'",
    ],
    "falcon_search_firewall_rule_groups": [
        "Find all enabled firewall rule groups for Windows",
    ],
    "falcon_search_firewall_policy_rules": [
        "Show me all rules in firewall policy abc123",
    ],
    "falcon_create_firewall_rule_group": [
        "Create a Windows firewall rule group named 'Prod Outbound'",
    ],
    "falcon_delete_firewall_rule_groups": [
        "Delete firewall rule group abc123",
    ],
    # Hosts
    "falcon_search_hosts": [
        "Find all Windows hosts in my environment",
        "Show me hosts last seen in the past 24 hours",
    ],
    "falcon_get_host_details": [
        "Get the full details for host device abc123",
    ],
    # Host Groups
    "falcon_search_host_groups": [
        "Show me all static host groups",
        "Find host groups created in the last 30 days",
    ],
    "falcon_search_host_group_members": [
        "List the Windows hosts in host group abc123",
        "Show me the members of the Production Servers group",
    ],
    "falcon_create_host_group": [
        "Create a static host group called 'Critical Servers'",
        "Create a dynamic host group for all Windows hosts",
    ],
    "falcon_update_host_group": [
        "Rename host group abc123 to 'Decommissioned'",
        "Update the assignment rule for the dynamic Windows group",
    ],
    "falcon_delete_host_groups": [
        "Delete host group abc123",
    ],
    "falcon_perform_host_group_action": [
        "Add the hosts matching platform_name Windows to group abc123",
        "Remove host device xyz from host group abc123",
    ],
    # Identity Protection
    "falcon_idp_investigate_entity": [
        "Investigate user john.doe@company.com and show their risk assessment",
        "Look up entity Administrator in domain CORP.LOCAL",
    ],
    # Intel
    "falcon_search_actors": [
        "Find threat actors targeting financial services",
        "Search for BEAR adversary groups",
    ],
    "falcon_search_indicators": [
        "Find intelligence IOCs of type domain published this year",
    ],
    "falcon_search_reports": [
        "Find intelligence reports published in the last 30 days",
    ],
    "falcon_get_mitre_report": [
        "Generate MITRE ATT&CK report for FANCY BEAR",
    ],
    # Exclusions
    "falcon_search_exclusions": [
        "Show me my most recent IOA and machine learning exclusions",
        "List sensor visibility exclusions created in the last 7 days",
    ],
    "falcon_create_exclusion": [
        "Create an ML exclusion for /tmp/foo.sh applied to all hosts",
        "Add a sensor visibility exclusion for C:\\Temp\\* on the Workstations group",
    ],
    "falcon_update_exclusion": [
        "Update IOA exclusion abc123 to also match a new command line regex",
    ],
    "falcon_delete_exclusions": [
        "Delete the certificate exclusion with ID abc123",
    ],
    "falcon_get_certificate_details": [
        "Look up the signing certificate for SHA256 3dd9a...",
    ],
    # IOC
    "falcon_search_iocs": [
        "Find all active domain IOCs",
        "Show me SHA256 hash IOCs with prevent action",
    ],
    "falcon_add_ioc": [
        "Block the domain evil.example.com",
        "Add a SHA256 hash IOC with prevent action",
    ],
    "falcon_remove_iocs": [
        "Delete IOC with ID abc123",
        "Remove all expired IOCs",
    ],
    # NGSIEM
    "falcon_search_ngsiem": [
        "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2",
        "Search NGSIEM for DNS events from January 2025",
    ],
    # Policies
    "falcon_search_policies": [
        "List all firewall policies",
        "Show enabled sensor update policies for Windows",
        "Find prevention policies whose name contains 'default'",
    ],
    "falcon_search_policy_members": [
        "What hosts are assigned to firewall policy 1a2b3c?",
    ],
    "falcon_create_policy": [
        "Create a disabled firewall policy named 'Test FW' for Windows",
    ],
    "falcon_update_policy": [
        "Rename prevention policy 1a2b3c to 'Servers - Strict'",
    ],
    "falcon_delete_policies": [
        "Delete firewall policy 1a2b3c",
    ],
    "falcon_perform_policy_action": [
        "Disable prevention policy 1a2b3c",
        "Add host group 9z8y7x to sensor update policy 1a2b3c",
    ],
    "falcon_set_policy_precedence": [
        "Set the precedence order of these Windows prevention policies: 1a2b3c, 4d5e6f, 7g8h9i",
    ],
    # Quarantine
    "falcon_search_quarantined_files": [
        "Show me quarantined files on host SE-DAO-WIN10-CO",
        "Find quarantined files for user badguy updated in the last 7 days",
        "Search for quarantined files with SHA256 starting with 3dd9",
    ],
    "falcon_preview_quarantine_actions": [
        "Preview how many quarantined files can be released vs deleted",
        "Preview quarantine action impact for state quarantined on host SE-DAO-WIN10-CO",
    ],
    "falcon_update_quarantined_files": [
        "Release quarantine record abc123",
        "Release all quarantined files for user badguy",
    ],
    "falcon_delete_quarantined_files": [
        "Delete quarantine records for host SE-DAO-WIN10-CO",
        "Delete quarantine record abc123",
    ],
    # Recon
    "falcon_search_recon_notifications": [
        "Show me recon alerts from the past 7 days",
        "Show me new recon alerts with high priority",
        "Find recon notifications for domain monitoring rules",
        "Show typosquatting recon alerts",
        "Find leaked credential notifications from stealer logs",
    ],
    "falcon_search_recon_rules": [
        "List all active Recon monitoring rules",
        "Show typosquatting monitoring rules",
        "Find Recon rules with breach monitoring enabled",
        "List high priority domain monitoring rules",
    ],
    "falcon_search_recon_exposed_data_records": [
        "Find exposed credentials for example.com",
        "Show leaked credentials from the past 7 days",
        "Find exposed data records for a specific notification",
    ],
    "falcon_aggregate_recon_notifications": [
        "How many recon notifications are there by status?",
        "What are the top 10 noisiest recon monitoring rules this month?",
        "Show recon notification volume per day for the past 30 days",
        "Break down typosquatting notifications by priority",
    ],
    "falcon_aggregate_recon_exposed_data_records": [
        "Which sites leak the most of our credentials?",
        "How many exposed credentials are newly reported vs previously reported?",
        "Show exposed data record volume per day",
    ],
    "falcon_preview_recon_rule": [
        "How noisy would a rule monitoring example.com be?",
        "Preview how many notifications a brand rule for Acme would generate in the past 30 days",
        "Estimate the notification volume before I create this monitoring rule",
    ],
    # Scheduled Reports
    "falcon_search_scheduled_reports": [
        "Show me all active scheduled reports",
    ],
    "falcon_launch_scheduled_report": [
        "Run scheduled report abc123 now",
    ],
    "falcon_search_report_executions": [
        "Show me completed executions for report abc123",
    ],
    "falcon_download_report_execution": [
        "Download the results for report execution abc123",
    ],
    # Sensor Usage
    "falcon_search_sensor_usage": [
        "Show me sensor usage data for the week of 2024-06-11",
    ],
    # Serverless
    "falcon_search_serverless_vulnerabilities": [
        "Find HIGH severity vulnerabilities in AWS Lambda functions",
    ],
    # Shield
    "falcon_search_shield_checks": [
        "Show me the failed Shield security checks",
        "Search for high impact Shield checks related to devices",
    ],
    "falcon_get_shield_check_affected_entities": [
        "Show me the entities affected by a failed Shield check",
    ],
    "falcon_get_shield_posture_metrics": [
        "Show me my overall Falcon Shield posture metrics",
    ],
    "falcon_get_shield_check_compliance": [
        "Find a Shield check with compliance framework mappings",
    ],
    "falcon_search_shield_alerts": [
        "Show me Shield alerts of type Threat",
        "Show me the 5 oldest Shield alerts sorted by date",
    ],
    "falcon_get_shield_activity_monitor": [
        "Show me Shield activity events from the last 24 hours",
    ],
    "falcon_search_shield_users": [
        "List privileged users across my connected SaaS apps in Shield",
    ],
    "falcon_search_shield_devices": [
        "Show me devices in Shield not associated with any known user",
    ],
    "falcon_search_shield_apps": [
        "Find OAuth apps in Shield that haven't been active in 90 days",
        "List all Shield apps with status 'in review'",
    ],
    "falcon_get_shield_app_users": [
        "Show me which users have authorized Shield app abc123",
    ],
    "falcon_search_shield_data_shares": [
        "Find files shared via public link in Shield",
    ],
    "falcon_get_shield_integrations": [
        "List all connected SaaS integrations in Falcon Shield",
    ],
    "falcon_get_shield_system_users": [
        "Show me the Falcon Shield platform administrators and their MFA status",
    ],
    "falcon_get_shield_supported_saas": [
        "List all SaaS platforms supported by Falcon Shield",
    ],
    "falcon_get_shield_system_logs": [
        "Show me the last 10 Falcon Shield system audit logs",
    ],
    "falcon_dismiss_shield_check": [
        "Dismiss a low-impact Shield check entity with reason 'No longer applicable'",
    ],
    # Spotlight
    "falcon_search_vulnerabilities": [
        "Show me open HIGH severity vulnerabilities",
        "Find vulnerabilities on host xyz",
    ],
    # Real Time Response
    "falcon_search_rtr_sessions": [
        "Find all active RTR sessions",
        "Show me RTR sessions for host abc123",
    ],
    "falcon_search_rtr_audit_sessions": [
        "Show me RTR audit activity from the last 7 days",
        "Who used RTR against host BRR-WB-LIB-22?",
    ],
    "falcon_aggregate_rtr_sessions": [
        "Summarize RTR sessions by command for the last 30 days",
        "Which hosts have the most RTR activity this week?",
    ],
    "falcon_get_rtr_session_details": [
        "Get details for RTR session abc123",
    ],
    "falcon_init_rtr_session": [
        "Start an RTR session on host xyz",
    ],
    "falcon_pulse_rtr_session": [
        "Refresh the RTR session to keep it alive",
    ],
    "falcon_execute_rtr_read_only_command": [
        "Run 'ps' on this host via RTR",
        "List running processes on host xyz",
    ],
    "falcon_run_rtr_read_only_command_and_wait": [
        "Run 'ps' via RTR and return the output when it completes",
        "Check C:\\Windows\\win.ini on this RTR session and wait for the result",
    ],
    "falcon_check_rtr_command_status": [
        "Check the status of RTR command request abc123",
    ],
    "falcon_list_rtr_session_files": [
        "List files extracted during RTR session abc123",
    ],
    "falcon_delete_rtr_session": [
        "End the RTR session abc123",
    ],
    # Zero Trust Assessment
    "falcon_search_zta_assessments": [
        "Which hosts have the weakest Zero Trust posture?",
        "Show me hosts scoring below 40 on Zero Trust Assessment",
    ],
    "falcon_get_zta_assessments": [
        "What is the security posture of host WEB-01?",
        "Show the Zero Trust hardening signals for this agent ID",
    ],
    "falcon_get_zta_audit": [
        "What is our overall Zero Trust score?",
        "Break down our Zero Trust posture by platform",
    ],
    # Fusion SOAR
    "falcon_search_workflow_definitions": [
        "What Fusion SOAR workflows can I trigger on demand?",
        "Find the Fusion workflow called 'Adversary Exposure Mitigation'",
        "Which Fusion workflows are currently disabled?",
    ],
    "falcon_search_workflow_executions": [
        "Show me workflow executions that completed",
        "Which Fusion workflows failed in the last 7 days?",
        "Are any workflow runs waiting on someone to approve them?",
    ],
    "falcon_get_workflow_execution_results": [
        "What did workflow execution 714511d8 actually do?",
        "Show me the ticket number the incident workflow created",
    ],
    "falcon_execute_workflow": [
        "Run the 'Notify SOC Channel' workflow",
        "Start workflow 2617e3fc with the hash abc123",
    ],
}

# Lines matching these patterns are stripped from docstrings
_DOCSTRING_NOISE_PATTERNS = [
    re.compile(r"^\s*IMPORTANT:\s*You must use the\b", re.IGNORECASE),
    re.compile(r"^\s*IMPORTANT:\s*use the\b", re.IGNORECASE),
    re.compile(r"^\s*This resource contains the guide\b", re.IGNORECASE),
    re.compile(r"^\s*Returns FQL syntax guide on error\b", re.IGNORECASE),
    re.compile(r"^\s*when you need to use the\b", re.IGNORECASE),
]


def clean_docstring(doc: str) -> str:
    """Strip noise sentences from a tool docstring."""
    lines = doc.splitlines()
    cleaned: list[str] = []
    for line in lines:
        if any(p.match(line) for p in _DOCSTRING_NOISE_PATTERNS):
            continue
        cleaned.append(line)

    # Collapse consecutive blank lines
    result: list[str] = []
    prev_blank = False
    for line in cleaned:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "\n".join(result).strip()


def _extract_module_meta(mod: Any) -> tuple[str, str]:
    """Derive (auto_title, auto_description) from a module's docstring."""
    doc_lines = (mod.__doc__ or "").strip().splitlines() if mod.__doc__ else []

    # Extract title from first line:
    # "Real Time Response module for Falcon MCP Server." → "Real Time Response"
    first_line = doc_lines[0].strip() if doc_lines else ""
    auto_title = re.sub(
        r"\s+module for Falcon MCP Server\.?$", "", first_line, flags=re.IGNORECASE
    )

    # Extract description from the second paragraph (first non-blank line after title)
    # Stops at the next blank line so numbered lists / extra sections aren't included.
    auto_description = ""
    past_blank = False
    desc_parts: list[str] = []
    for line in doc_lines[1:]:
        stripped = line.strip()
        if not stripped:
            if past_blank and desc_parts:
                break  # stop at the next blank line after description
            past_blank = True
            continue
        if past_blank:
            desc_parts.append(stripped)
    if desc_parts:
        desc_text = " ".join(desc_parts)
        # Take only the first sentence to avoid leaking numbered lists / extra sections
        first_sentence = re.split(r"(?<=\.)\s", desc_text, maxsplit=1)[0].rstrip(".")
        # Strip the common "This module provides tools for ..." prefix
        auto_description = re.sub(
            r"^This module provides tools? for\s+", "", first_sentence, flags=re.IGNORECASE
        )
        # Capitalise first letter after stripping
        if auto_description:
            auto_description = auto_description[0].upper() + auto_description[1:]

    return auto_title, auto_description


def _register_module_classes(mod: Any, result: dict[str, dict[str, Any]]) -> None:
    """Find *Module classes in a module and add them to result, deriving meta from docstring."""
    auto_title, auto_description = _extract_module_meta(mod)
    for attr_name in dir(mod):
        if attr_name.endswith("Module") and attr_name != "BaseModule":
            cls = getattr(mod, attr_name)
            # Skip classes imported from other modules — only register classes defined here.
            if cls.__module__ != mod.__name__:
                continue
            module_key = attr_name.lower().replace("module", "")
            result[module_key] = {
                "cls": cls,
                "auto_title": auto_title or module_key.title(),
                "auto_description": auto_description,
            }


def discover_module_classes() -> dict[str, dict[str, Any]]:
    """Discover all module classes and auto-derive titles/descriptions from file docstrings."""
    modules_path = PROJECT_ROOT / "falcon_mcp" / "modules"
    result: dict[str, dict[str, Any]] = {}

    for _, name, is_pkg in pkgutil.iter_modules([str(modules_path)]):
        if name == "base":
            continue

        if is_pkg:
            # Recurse into the package: each submodule is scanned independently so that
            # each file's docstring drives its own title/description without dir() collisions.
            pkg_path = modules_path / name
            for _, subname, sub_is_pkg in pkgutil.iter_modules([str(pkg_path)]):
                if sub_is_pkg or subname == "__init__":
                    continue
                submod = importlib.import_module(f"falcon_mcp.modules.{name}.{subname}")
                _register_module_classes(submod, result)
        else:
            mod = importlib.import_module(f"falcon_mcp.modules.{name}")
            _register_module_classes(mod, result)

    return result


def _own_classes(module_cls: type) -> list[type]:
    """The MRO classes belonging to this module, stopping before BaseModule.

    A module assembled from mixins spreads its tools and helpers over several classes, so
    scope detection has to read all of them. It must stop at BaseModule: that source is
    shared by every module and mentions operation names from all of them, which would
    attribute unrelated scopes to whichever module was being documented.
    """
    import abc

    from falcon_mcp.modules.base import BaseModule

    stop_at = {BaseModule, abc.ABC, object}
    classes: list[type] = []
    for klass in module_cls.__mro__:
        if klass in stop_at:
            break
        classes.append(klass)
    return classes


def _module_string_constants(module_name: str) -> dict[str, str]:
    """Map the module-level ``NAME = "literal"`` assignments declared in one file.

    Scope detection works by spotting operation-name string literals in the source. A
    module may instead name its operation once in a module-level constant and reference
    it by name at every call site, as ``agentworks.py`` does with ``_GET_INVOCATION_OP``.
    `inspect.getsource` on the class, or on one method, never sees that assignment, so
    the literal is absent and the tool silently documents no scopes at all. Resolving
    these constants first closes that hole for any module that factors its operation
    name out.

    Annotated assignments (``NAME: str = "literal"``) count too — the annotation is
    invisible at runtime but changes the AST node type, and missing that would reopen
    the same hole for a module that spells its constant with a type.
    """
    module = sys.modules.get(module_name)
    if module is None:
        return {}
    try:
        tree = ast.parse(inspect.getsource(module))
    except (TypeError, OSError, SyntaxError):
        return {}

    constants: dict[str, str] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                constants[target.id] = node.value.value
    return constants


def _class_literal_containers(module_cls: type) -> dict[str, Any]:
    """Class-level attributes whose value is a pure literal, as real Python objects.

    A module that dispatches on a discriminator keeps its operation names in a class
    attribute rather than at a call site — ``policies.py`` and ``exclusions.py`` both
    hold every operation in an ``_OPERATIONS`` dict and select one with
    ``self._OPERATIONS[type]["verb"]``. Helper tracing only follows callables, so a dict
    is skipped and none of those operation names is ever seen. Unlike module globals,
    these really are class attributes, so the earliest definition in the MRO wins,
    exactly as attribute lookup resolves it.
    """
    containers: dict[str, Any] = {}
    for klass in _own_classes(module_cls):
        try:
            tree = ast.parse(textwrap.dedent(inspect.getsource(klass)))
        except (TypeError, OSError, SyntaxError):
            continue
        if not (tree.body and isinstance(tree.body[0], ast.ClassDef)):
            continue
        for node in tree.body[0].body:
            target: str | None = None
            value: ast.expr | None = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                target, value = node.targets[0].id, node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target, value = node.target.id, node.value
            if target is None or value is None or target in containers:
                continue
            try:
                containers[target] = ast.literal_eval(value)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                continue
    return containers


def _flatten_strings(obj: Any) -> set[str]:
    """Every string reachable inside a nested literal container."""
    if isinstance(obj, str):
        return {obj}
    if isinstance(obj, dict):
        return set().union(*(_flatten_strings(v) for v in obj.values())) if obj else set()
    if isinstance(obj, (list, tuple, set, frozenset)):
        return set().union(*(_flatten_strings(v) for v in obj)) if obj else set()
    return set()


# self.ATTR["key"] / self.ATTR[var] / self.ATTR[a]["b"] — one group per subscript level
_SUBSCRIPT_CHAIN = re.compile(r"self\.(\w+)((?:\[[^\[\]]*\])+)")
_SUBSCRIPT_LEVEL = re.compile(r"\[([^\[\]]*)\]")
_QUOTED_KEY = re.compile(r"""^\s*(?:"([^"]*)"|'([^']*)')\s*$""")


def _local_literal_values(source: str, name: str) -> set[str]:
    """String literals assigned to ``name`` anywhere in ``source``.

    Lets a variable subscript key narrow instead of widening to every entry:
    ``op_key = "update" if is_update else "create"`` reaches only two of the verbs, so a
    tool selecting ``[op_key]`` should not claim the scopes of the ones it cannot reach.
    """
    values: set[str] = set()
    for match in re.finditer(rf"\b{re.escape(name)}\s*=(?!=)([^\n]*)", source):
        values |= {
            dq if dq else sq for dq, sq in re.findall(r'"([^"]*)"|\'([^\']*)\'', match.group(1))
        }
    return values


def _container_ops_in(source: str, containers: dict[str, Any]) -> set[str]:
    """Operation names reached by subscripting a class-level literal container.

    A literal key narrows to that entry. A variable key is resolved against literals
    assigned to that name in the same source, and only widens to every entry at the level
    when that yields nothing usable — widening is the honest answer there, because the
    tool really can call any of them depending on its argument.
    """
    names: set[str] = set()
    for attr, subscripts in _SUBSCRIPT_CHAIN.findall(source):
        if attr not in containers:
            continue
        level: list[Any] = [containers[attr]]
        for raw_key in _SUBSCRIPT_LEVEL.findall(subscripts):
            quoted = _QUOTED_KEY.match(raw_key)
            keys: set[str] | None = None
            if quoted:
                keys = {quoted.group(1) if quoted.group(1) is not None else quoted.group(2)}
            elif re.fullmatch(r"\s*[A-Za-z_]\w*\s*", raw_key):
                candidates = _local_literal_values(source, raw_key.strip())
                # Only trust the narrowing if it actually names entries at this level;
                # otherwise those literals were something else and we must widen.
                usable = {
                    c
                    for c in candidates
                    for obj in level
                    if isinstance(obj, dict) and c in obj
                }
                keys = usable or None
            nxt: list[Any] = []
            for obj in level:
                if not isinstance(obj, dict):
                    continue
                if keys is None:
                    nxt.extend(obj.values())
                else:
                    nxt.extend(obj[k] for k in keys if k in obj)
            level = nxt
        for obj in level:
            names |= _flatten_strings(obj)
    return names


def _operation_names_in(
    chunks: list[tuple[str, str]], containers: dict[str, Any] | None = None
) -> set[str]:
    """Operation names referenced by each ``(source, defining module)`` chunk.

    A module assembled from mixins spreads its methods over several files, and each file
    may declare its own constants, so every chunk resolves against the module that
    defines it — the same file Python resolves the reference against at runtime, since a
    function reads its globals from where it was written rather than from its class's
    position in the MRO. Merging every file's constants into one map instead would let a
    same-named constant in a sibling mixin win and attribute the wrong operation.

    ``containers`` carries the module's class-level literal containers, so an operation
    selected out of a dict is found as well as one written inline.
    """
    names: set[str] = set()
    for source, module_name in chunks:
        names |= set(re.findall(r'["\'](\w+)["\']', source))
        constants = _module_string_constants(module_name)
        if constants:
            referenced = set(re.findall(r"\b([A-Za-z_]\w*)\b", source))
            names |= {constants[n] for n in referenced & constants.keys()}
        if containers:
            names |= _container_ops_in(source, containers)
    return names


def extract_module_scopes(module_cls: type) -> list[str]:
    """Derive API scopes by finding operation names in module source and looking them up in API_SCOPE_REQUIREMENTS."""
    chunks: list[tuple[str, str]] = []
    for klass in _own_classes(module_cls):
        try:
            chunks.append((inspect.getsource(klass), klass.__module__))
        except (TypeError, OSError):
            pass

    all_strings = _operation_names_in(chunks, _class_literal_containers(module_cls))
    scopes: set[str] = set()
    for op_name, op_scopes in API_SCOPE_REQUIREMENTS.items():
        if op_name in all_strings:
            scopes.update(op_scopes)

    # Sort: read scopes first, then write, alphabetically within each group
    return sorted(scopes, key=lambda s: (":write" in s, s))


def _module_own_functions(module_name: str) -> dict[str, str]:
    """Source of every plain function defined in one module's own file.

    A tool can reach the API through a module-level function rather than a method —
    ``hosts.py`` names ``UpdateDeviceTags`` only inside ``_tag_error``, and ``ngsiem.py``
    names ``StartSearchV1`` inside ``_validate_repository``. Helper tracing keys on
    ``self.<name>``, so a bare call is invisible to it.

    Only functions defined in this very file are eligible. An imported one belongs to a
    shared module that names operations from every module, so following it would attribute
    unrelated scopes for the same reason BaseModule is excluded.
    """
    module = sys.modules.get(module_name)
    if module is None:
        return {}
    functions: dict[str, str] = {}
    for name, value in vars(module).items():
        if not inspect.isfunction(value) or getattr(value, "__module__", None) != module_name:
            continue
        try:
            functions[name] = inspect.getsource(value)
        except (TypeError, OSError):
            continue
    return functions


# A call to a bare name: `helper(...)`, but not `obj.helper(...)` or `def helper(...)`
_BARE_CALL = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\(")


def extract_tool_scopes(method: Any, module_cls: type) -> list[str]:
    """Derive API scopes for a single tool method by tracing its helper calls.

    Only follows helpers defined on the concrete module class itself, NOT inherited
    BaseModule helpers (which contain operation names from all modules). Follows the
    chain transitively and includes public methods, because a tool that reaches the API
    only through another tool method needs the union of the scopes of everything it
    calls: ``agentworks.py``'s ``invoke_agentworks_agent`` polls
    ``get_agentworks_agent_invocation``, so it needs that operation's read scope on top
    of its own write scope. Module-level functions defined in the same file are followed
    too, since an operation named only inside one would otherwise be invisible.
    """
    try:
        method_source = inspect.getsource(method)
    except (TypeError, OSError):
        return []

    # Build a map of method name → (source, defining module) from every class this module
    # owns, so a mixin package resolves a helper that lives on a sibling mixin. The module
    # is carried alongside because each file resolves its own constants. Public methods are
    # included too: a tool that reaches the API only through another tool method needs that
    # operation's scopes as well.
    own_method_source: dict[str, tuple[str, str]] = {}
    for klass in _own_classes(module_cls):
        for attr, val in klass.__dict__.items():
            if attr not in own_method_source and callable(val):
                try:
                    own_method_source[attr] = (inspect.getsource(val), klass.__module__)
                except (TypeError, OSError):
                    pass

    # Walk the chain breadth-first, guarding against recursion. Match bare `self.name`
    # too, not just `self.name(`, so a method passed as a callable rather than called
    # directly is still followed.
    method_module = getattr(method, "__module__", "")
    chunks: list[tuple[str, str]] = [(method_source, method_module)]
    seen: set[tuple[str, str]] = set()
    pending: list[tuple[str, str]] = [(name, method_module)
                                      for name in re.findall(r"self\.(\w+)", method_source)]
    pending += [(name, method_module) for name in _BARE_CALL.findall(method_source)]
    while pending:
        helper_name, from_module = pending.pop()
        if (helper_name, from_module) in seen:
            continue
        seen.add((helper_name, from_module))

        if helper_name in own_method_source:
            helper_source, helper_module = own_method_source[helper_name]
        else:
            # A plain function, resolved only against the file the caller was written in
            helper_source = _module_own_functions(from_module).get(helper_name, "")
            helper_module = from_module
            if not helper_source:
                continue

        chunks.append((helper_source, helper_module))
        pending += [(name, helper_module) for name in re.findall(r"self\.(\w+)", helper_source)]
        pending += [(name, helper_module) for name in _BARE_CALL.findall(helper_source)]

    # Find all string literals (and constant- or container-referenced operation names)
    # and look them up in API_SCOPE_REQUIREMENTS
    all_strings = _operation_names_in(chunks, _class_literal_containers(module_cls))
    scopes: set[str] = set()
    for op_name, op_scopes in API_SCOPE_REQUIREMENTS.items():
        if op_name in all_strings:
            scopes.update(op_scopes)

    return sorted(scopes, key=lambda s: (":write" in s, s))


def extract_tool_info(method: Any) -> dict[str, Any]:
    """Extract tool name and docstring from a tool method."""
    doc = inspect.getdoc(method) or ""

    return {
        "docstring": doc,
    }


def _collect_method_source(module_cls: type, method_name: str) -> str:
    """Collect source from every class in the MRO that defines method_name.

    Needed because CloudModule (and similar) is assembled from multiple mixins,
    each with its own register_tools/register_resources. Plain
    inspect.getsource(cls.method) resolves via MRO to only the first definition.
    """
    parts: list[str] = []
    seen: set[type] = set()
    for klass in reversed(module_cls.__mro__):
        if klass in seen or method_name not in klass.__dict__:
            continue
        seen.add(klass)
        try:
            parts.append(inspect.getsource(klass.__dict__[method_name]))
        except (TypeError, OSError):
            pass
    return "\n".join(parts)


def extract_registered_tool_names(module_cls: type) -> dict[str, str]:
    """Extract method-to-tool-name mappings from register_tools.

    Registered MCP tool names can differ from Python method names. The docs
    should show the actual tool names exposed to MCP clients.
    """
    try:
        source = _collect_method_source(module_cls, "register_tools")
    except (AttributeError, TypeError):
        return {}

    registered: dict[str, str] = {}

    # Find each _add_tool( block and collect its full call by tracking parens.
    for match in re.finditer(r"self\._add_tool\(", source):
        start = match.end()
        depth = 1
        pos = start
        while pos < len(source) and depth > 0:
            if source[pos] == "(":
                depth += 1
            elif source[pos] == ")":
                depth -= 1
            pos += 1
        block = source[start : pos - 1]

        method_match = re.search(r"method=self\.(\w+)", block)
        name_match = re.search(r'name=["\']([^"\']+)["\']', block)
        if method_match and name_match:
            registered[method_match.group(1)] = name_match.group(1)

    return registered


def _extract_kwarg_string(block: str, kwarg: str) -> str:
    """Extract a string-valued kwarg, joining adjacent/parenthesized literals.

    Handles both `description="..."` single literals and reflowed
    `description=(\n    "part one "\n    "part two"\n)` concatenations, which
    Python joins into one string at runtime.
    """
    m = re.search(rf"{kwarg}\s*=\s*", block)
    if not m:
        return ""
    rest = block[m.end() :]

    # Parenthesized group: capture everything up to the matching close paren,
    # then join every quoted literal inside it.
    if rest.startswith("("):
        depth = 0
        for i, ch in enumerate(rest):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    inner = rest[1:i]
                    break
        else:
            inner = rest
        pairs = re.findall(r'"([^"]*)"|\'([^\']*)\'', inner)
        return "".join(dq or sq for dq, sq in pairs)

    # Bare value: join only the leading run of adjacent string literals
    # (implicit concatenation), stopping at the first non-literal token so we
    # don't swallow later kwargs' strings.
    literals: list[str] = []
    scan = rest
    lit = re.compile(r'^\s*(?:"([^"]*)"|\'([^\']*)\')')
    while match := lit.match(scan):
        literals.append(match.group(1) if match.group(1) is not None else match.group(2))
        scan = scan[match.end() :]
    return "".join(literals)


def extract_resource_info(module_cls: type) -> list[dict[str, str]]:
    """Extract resource URIs and descriptions by inspecting register_resources."""
    try:
        source = _collect_method_source(module_cls, "register_resources")
    except (AttributeError, TypeError):
        return []

    resources = []

    # Find each TextResource( and collect its full block by tracking parens
    for m in re.finditer(r"TextResource\(", source):
        start = m.end()
        depth = 1
        pos = start
        while pos < len(source) and depth > 0:
            if source[pos] == "(":
                depth += 1
            elif source[pos] == ")":
                depth -= 1
            pos += 1
        block = source[start : pos - 1]

        uri_m = re.search(r'uri=AnyUrl\(["\']([^"\']+)["\']\)', block)
        name_m = re.search(r'name=["\']([^"\']+)["\']', block)
        description = _extract_kwarg_string(block, "description")

        if uri_m:
            resources.append(
                {
                    "uri": uri_m.group(1),
                    "name": name_m.group(1) if name_m else "",
                    "description": description,
                }
            )

    return resources


def extract_tool_annotations(module_cls: type) -> dict[str, dict[str, bool]]:
    """Extract tool annotations from register_tools source."""
    source = _collect_method_source(module_cls, "register_tools")
    annotations = {}

    # Find _add_tool calls with explicit annotations
    tool_pattern = r'self\._add_tool\([^)]*?name=["\']([\w]+)["\'][^)]*?annotations=ToolAnnotations\(\s*([^)]+)\)'
    for match in re.finditer(tool_pattern, source, re.DOTALL):
        tool_name = match.group(1)
        anno_str = match.group(2)

        anno = {}
        for key in ["readOnlyHint", "destructiveHint", "idempotentHint"]:
            val_match = re.search(rf"{key}=(\w+)", anno_str)
            if val_match:
                anno[key] = val_match.group(1) == "True"

        annotations[tool_name] = anno

    return annotations


def generate_module_page(module_key: str, module_cls: type, auto_title: str, auto_description: str) -> str:
    """Generate a complete markdown page for a module."""
    meta = MODULE_METADATA.get(module_key, {})
    title = meta.get("title", auto_title)
    fallback_desc = auto_description or f"{title} module for CrowdStrike Falcon."
    description = meta.get("description", fallback_desc)
    scopes = extract_module_scopes(module_cls)

    # Extract tools in runtime registration order (reverse-MRO, as built by _collect_method_source)
    tools = []
    tool_annotations = extract_tool_annotations(module_cls)
    registered_tool_names = extract_registered_tool_names(module_cls)

    for attr_name, registered_name in registered_tool_names.items():
        method = getattr(module_cls, attr_name, None)
        if method is None or not callable(method):
            continue
        info = extract_tool_info(method)
        info["name"] = f"falcon_{registered_name}"
        info["raw_name"] = registered_name
        info["method"] = method

        # Get annotations
        if registered_name in tool_annotations:
            info["annotations"] = tool_annotations[registered_name]
        else:
            info["annotations"] = {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
            }

        # Get per-tool scopes
        info["scopes"] = extract_tool_scopes(method, module_cls)

        # Example prompts (from static TOOL_EXAMPLES dict)
        info["examples"] = TOOL_EXAMPLES.get(info["name"], [])

        tools.append(info)

    # Extract resources
    resources = extract_resource_info(module_cls)

    # Build markdown
    lines = []
    lines.append(f"<!-- meta:title {title} -->")
    lines.append(f"<!-- meta:description {description} -->")
    lines.append("<!-- meta:section modules -->")
    lines.append("<!-- meta:link-base /falcon-mcp/ -->")
    lines.append("<!-- frontmatter:sidebar order:10 -->")
    lines.append("")
    lines.append(description)
    lines.append("")

    # Note on differences from CrowdStrike's hosted Falcon MCP, if any
    if module_key in HOSTED_MCP_MODULE_NOTES:
        lines.append("> [!NOTE]")
        lines.append(f"> {HOSTED_MCP_MODULE_NOTES[module_key]}")
        lines.append("")

    # API Scopes
    if scopes:
        lines.append("## API Scopes")
        lines.append("")
        for scope in scopes:
            lines.append(f"- `{scope}`")
        lines.append("")

    # Tools
    if tools:
        lines.append("## Tools")
        lines.append("")
        for tool in tools:
            read_only = tool["annotations"].get("readOnlyHint", True)
            destructive = tool["annotations"].get("destructiveHint", False)

            lines.append(f"### `{tool['name']}`")
            lines.append("")

            # Note on hosted-MCP availability, if any
            if tool["name"] in HOSTED_MCP_TOOL_NOTES:
                lines.append("> [!NOTE]")
                lines.append(f"> {HOSTED_MCP_TOOL_NOTES[tool['name']]}")
                lines.append("")

            # Admonition for mutating/destructive tools
            if destructive:
                lines.append("> [!CAUTION]")
                lines.append("> This tool performs destructive operations.")
                lines.append("")
            elif not read_only:
                lines.append("> [!NOTE]")
                lines.append("> This tool modifies data.")
                lines.append("")

            # Per-tool scopes
            tool_scopes = tool.get("scopes", [])
            if tool_scopes:
                lines.append(f"**Required scopes:** {', '.join(f'`{s}`' for s in tool_scopes)}")
                lines.append("")

            # Cleaned docstring
            cleaned = clean_docstring(tool["docstring"])
            if cleaned:
                lines.append(cleaned)
                lines.append("")

            # Example prompts
            examples = tool.get("examples", [])
            if examples:
                lines.append("**Example prompts:**")
                lines.append("")
                for ex in examples:
                    lines.append(f'- "{ex}"')
                lines.append("")

    # Resources
    if resources:
        lines.append("## Resources")
        lines.append("")
        for r in resources:
            lines.append(f"- **`{r['uri']}`**: {r['description']}")
        lines.append("")

    return "\n".join(lines)


def generate_overview_page(modules: dict[str, dict[str, Any]]) -> str:
    """Generate the modules overview page with summary table."""
    lines = []
    lines.append("<!-- meta:title Module Overview -->")
    lines.append(
        "<!-- meta:description Overview of all available Falcon MCP modules with API scopes. -->"
    )
    lines.append("<!-- meta:section modules -->")
    lines.append("<!-- meta:link-base /falcon-mcp/ -->")
    lines.append("<!-- frontmatter:sidebar order:0 -->")
    lines.append("")
    lines.append(
        "The Falcon MCP Server provides the following modules. Each module requires specific CrowdStrike API scopes."
    )
    lines.append("")
    lines.append("| Module | API Scopes | Description |")
    lines.append("|--------|-------------------|-------------|")

    for key in sorted(modules.keys()):
        meta = MODULE_METADATA.get(key, {})
        title = meta.get("title", modules[key]["auto_title"])
        slug = meta.get("slug", key)
        module_cls = modules[key]["cls"]
        scopes_list = extract_module_scopes(module_cls)
        scopes = ", ".join(f"`{s}`" for s in scopes_list)
        fallback_desc = modules[key]["auto_description"] or f"{title} module for CrowdStrike Falcon."
        desc = meta.get("description", fallback_desc)
        lines.append(f"| [{title}]({SITE_BASE_PATH}/modules/{slug}/) | {scopes} | {desc} |")

    lines.append("")
    lines.append("## CrowdStrike-hosted MCP differences")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(
        "> This section compares this self-hosted server against CrowdStrike's hosted "
        "Falcon MCP. Skip it unless you also use the hosted MCP, or are moving between the two."
    )
    lines.append("")
    lines.append(
        "The two servers differ in how a client reaches a tool. The hosted Falcon MCP works "
        "through discovery: a client calls `search_tools` to find a Falcon tool by name or "
        "keyword, then `execute_tool` to run it with arguments. The self-hosted falcon-mcp "
        "server registers each `falcon_*` tool up front instead, so a client calls one by name "
        "with no discovery round-trip."
    )
    lines.append("")
    lines.append(
        "If you self-host and want the same discovery pattern, enable "
        f"[dynamic mode]({SITE_BASE_PATH}/usage/dynamic-mode/): it swaps the full tool surface "
        "for `falcon_search_tools`, `falcon_execute_tool`, and an always-on "
        "`falcon_list_enabled_tools` inventory. Mind the `falcon_` prefix — those three are "
        "the self-hosted falcon-mcp server's tools, not the hosted MCP's."
    )
    lines.append("")
    lines.append("Module and tool coverage also differs:")
    lines.append("")
    lines.append(
        f"- [Fusion SOAR]({_module_link('fusion')}), "
        f"[Zero Trust Assessment]({_module_link('zerotrustassessment')}), and "
        f"[Real Time Response]({_module_link('rtr')}) are available only on this self-hosted "
        "server; the hosted MCP has no equivalent modules."
    )
    lines.append(
        f"- [Cloud Security]({_module_link('cloud')}): `falcon_search_cloud_insights`, "
        "`falcon_list_cloud_insight_definitions`, and `falcon_get_cloud_asset_insights` are not "
        "available on the hosted MCP."
    )
    lines.append(
        f"- [Discover]({_module_link('discover')}): `falcon_search_managed_assets` is "
        "not available on the hosted MCP."
    )
    lines.append(
        f"- [Policies]({_module_link('policies')}): the hosted MCP does not use the "
        "unified `policy_type`-discriminated tools. It instead exposes six policy-type-specific "
        "variants of each tool (for example `falcon_search_policies_firewall`, "
        "`falcon_create_policy_prevention`)."
    )
    lines.append("")
    return "\n".join(lines)


def validate_hosted_mcp_notes(modules: dict[str, dict[str, Any]]) -> None:
    """Fail loudly when a hosted-MCP note key matches no module or no registered tool.

    Both note dicts are keyed by name, so a module or tool rename silently drops the
    note: the page regenerates without it, the committed docs match, and the docs
    freshness check passes. Raise here instead so a rename is caught at generation time.
    """
    stale_modules = sorted(set(HOSTED_MCP_MODULE_NOTES) - set(modules))

    known_tools = {
        f"falcon_{registered}"
        for mod_info in modules.values()
        for registered in extract_registered_tool_names(mod_info["cls"]).values()
    }
    stale_tools = sorted(set(HOSTED_MCP_TOOL_NOTES) - known_tools)

    problems = []
    if stale_modules:
        problems.append(
            f"HOSTED_MCP_MODULE_NOTES keys match no discovered module: {', '.join(stale_modules)}"
        )
    if stale_tools:
        problems.append(
            f"HOSTED_MCP_TOOL_NOTES keys match no registered tool: {', '.join(stale_tools)}"
        )
    if problems:
        raise ValueError(
            "Stale hosted-MCP note keys in scripts/generate_module_docs.py. "
            "Update or remove them after a rename:\n  " + "\n  ".join(problems)
        )


def main() -> None:
    """Generate all module documentation pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    modules = discover_module_classes()
    print(f"Discovered {len(modules)} modules: {', '.join(sorted(modules.keys()))}")

    validate_hosted_mcp_notes(modules)

    # Generate overview page
    overview = generate_overview_page(modules)
    (OUTPUT_DIR / "overview.md").write_text(overview)
    print("  Generated: modules/overview.md")

    # Generate per-module pages
    expected_files = {"overview.md"}
    for key, mod_info in sorted(modules.items()):
        meta = MODULE_METADATA.get(key, {})
        slug = meta.get("slug", key)
        filename = f"{slug}.md"
        expected_files.add(filename)

        page = generate_module_page(key, mod_info["cls"], mod_info["auto_title"], mod_info["auto_description"])
        (OUTPUT_DIR / filename).write_text(page)
        print(f"  Generated: modules/{filename}")

    # Clean up stale module files
    for existing in OUTPUT_DIR.glob("*.md"):
        if existing.name not in expected_files:
            existing.unlink()
            print(f"  Removed stale: modules/{existing.name}")

    print(f"\nDone. {len(modules) + 1} files written to {OUTPUT_DIR}")


if __name__ == "__main__":  # pragma: no cover
    main()
