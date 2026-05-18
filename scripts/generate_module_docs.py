"""Generate Starlight documentation pages from falcon_mcp module source code.

Introspects module classes, tool methods, and resource definitions to produce
markdown files for docs-site/src/content/docs/modules/.

Usage:
    uv run python scripts/generate_module_docs.py
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
import sys
from pathlib import Path
from typing import Any

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "docs-site" / "src" / "content" / "docs" / "modules"

# Module display metadata — overrides only.
# Titles and descriptions are auto-derived from module docstrings.
# Add entries here when you need a custom title, slug, or description.
MODULE_METADATA: dict[str, dict[str, Any]] = {
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
}

# Natural language prompt examples for each tool, shown in generated docs
TOOL_EXAMPLES: dict[str, list[str]] = {
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
    ],
    "falcon_update_case": [
        "Set that case to in_progress and assign it to the analyst",
        "Close the case — investigation is complete",
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
    # Detections
    "falcon_search_detections": [
        "Show me new high severity detections from the last 7 days",
        "Find all unassigned critical detections",
    ],
    "falcon_get_detection_details": [
        "Get me the details for this detection",
    ],
    # Discover
    "falcon_search_applications": [
        "Find all Chrome installations across my environment",
    ],
    "falcon_search_unmanaged_assets": [
        "Show me unmanaged Windows devices on the network",
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
    "falcon_check_rtr_command_status": [
        "Check the status of RTR command request abc123",
    ],
    "falcon_list_rtr_session_files": [
        "List files extracted during RTR session abc123",
    ],
    "falcon_delete_rtr_session": [
        "End the RTR session abc123",
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


def discover_module_classes() -> dict[str, dict[str, Any]]:
    """Discover all module classes and auto-derive titles/descriptions from file docstrings."""
    modules_path = str(PROJECT_ROOT / "falcon_mcp" / "modules")
    result: dict[str, dict[str, Any]] = {}

    for _, name, is_pkg in pkgutil.iter_modules([modules_path]):
        if is_pkg or name == "base":
            continue
        mod = importlib.import_module(f"falcon_mcp.modules.{name}")

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

        for attr_name in dir(mod):
            if attr_name.endswith("Module") and attr_name != "BaseModule":
                cls = getattr(mod, attr_name)
                module_key = attr_name.lower().replace("module", "")
                result[module_key] = {
                    "cls": cls,
                    "auto_title": auto_title or module_key.title(),
                    "auto_description": auto_description,
                }

    return result


def extract_module_scopes(module_cls: type) -> list[str]:
    """Derive API scopes by finding operation names in module source and looking them up in API_SCOPE_REQUIREMENTS."""
    source = inspect.getsource(module_cls)

    # Find all string literals that match known operation names
    all_strings = set(re.findall(r'["\'](\w+)["\']', source))
    scopes: set[str] = set()
    for op_name, op_scopes in API_SCOPE_REQUIREMENTS.items():
        if op_name in all_strings:
            scopes.update(op_scopes)

    # Sort: read scopes first, then write, alphabetically within each group
    return sorted(scopes, key=lambda s: (":write" in s, s))


def extract_tool_scopes(method: Any, module_cls: type) -> list[str]:
    """Derive API scopes for a single tool method by tracing its helper calls.

    Only follows private helpers defined on the concrete module class itself,
    NOT inherited BaseModule helpers (which contain operation names from all modules).
    """
    try:
        method_source = inspect.getsource(method)
    except (TypeError, OSError):
        return []

    # Collect combined source: the method itself + own-class private helpers it calls
    combined_source = method_source

    # Only trace helpers defined directly on this class (not inherited from BaseModule)
    own_methods = set(module_cls.__dict__.keys())

    # Find private helper calls: self._something(
    helper_names = re.findall(r"self\.(_\w+)\(", method_source)
    for helper_name in helper_names:
        if helper_name in own_methods:
            helper = module_cls.__dict__[helper_name]
            if callable(helper):
                try:
                    combined_source += "\n" + inspect.getsource(helper)
                except (TypeError, OSError):
                    pass

    # Find all string literals and look them up in API_SCOPE_REQUIREMENTS
    all_strings = set(re.findall(r'["\'](\w+)["\']', combined_source))
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


def extract_resource_info(module_cls: type) -> list[dict[str, str]]:
    """Extract resource URIs and descriptions by inspecting register_resources."""
    try:
        source = inspect.getsource(module_cls.register_resources)  # type: ignore[attr-defined]
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
        desc_m = re.search(r'description=["\']([^"\']+)["\']', block)

        if uri_m:
            resources.append(
                {
                    "uri": uri_m.group(1),
                    "name": name_m.group(1) if name_m else "",
                    "description": desc_m.group(1) if desc_m else "",
                }
            )

    return resources


def extract_tool_annotations(module_cls: type) -> dict[str, dict[str, bool]]:
    """Extract tool annotations from register_tools source."""
    source = inspect.getsource(module_cls.register_tools)  # type: ignore[attr-defined]
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

    # Extract tools
    tools = []
    tool_annotations = extract_tool_annotations(module_cls)

    for attr_name in dir(module_cls):
        method = getattr(module_cls, attr_name)
        if (
            callable(method)
            and not attr_name.startswith("_")
            and attr_name not in ("register_tools", "register_resources")
        ):
            # Check if this method is registered as a tool
            source = inspect.getsource(module_cls.register_tools)  # type: ignore[attr-defined]
            if attr_name in source:
                info = extract_tool_info(method)
                info["name"] = f"falcon_{attr_name}"
                info["raw_name"] = attr_name
                info["method"] = method

                # Get annotations
                if attr_name in tool_annotations:
                    info["annotations"] = tool_annotations[attr_name]
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
    lines.append("---")
    lines.append(f"title: {title}")
    lines.append(f"description: {description}")
    lines.append("sidebar:")
    lines.append("  order: 10")
    lines.append("---")
    lines.append("")
    lines.append(description)
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

            # Admonition for mutating/destructive tools
            if destructive:
                lines.append(":::caution")
                lines.append("This tool performs destructive operations.")
                lines.append(":::")
                lines.append("")
            elif not read_only:
                lines.append(":::note")
                lines.append("This tool modifies data.")
                lines.append(":::")
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
    lines.append("---")
    lines.append("title: Module Overview")
    lines.append("description: Overview of all available Falcon MCP modules with API scopes.")
    lines.append("sidebar:")
    lines.append("  order: 0")
    lines.append("---")
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
        lines.append(f"| [{title}](/falcon-mcp/modules/{slug}/) | {scopes} | {desc} |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Generate all module documentation pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    modules = discover_module_classes()
    print(f"Discovered {len(modules)} modules: {', '.join(sorted(modules.keys()))}")

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


if __name__ == "__main__":
    main()
