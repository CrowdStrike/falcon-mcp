"""
Curated inline FQL field hints for dynamic mode.

These compact hints are appended to filter parameter descriptions when tools are
discovered via falcon_search_tools, so LLMs have the most common fields at hand
without needing to read the full FQL resource.
"""

FILTER_HINTS: dict[str, str] = {
    # === Detections ===
    "falcon_search_detections": (
        "Common fields: severity_name (Critical|High|Medium|Low|Informational), "
        "status (new|in_progress|closed|reopened), product (epp|idp|xdr|overwatch), "
        "device.hostname, tactic, technique_id, "
        "assigned_to_name, filename, cmdline. "
        "Date filters: timestamp:>'now-24h' (relative) or timestamp:>'2026-01-01T00:00:00Z' (absolute). "
        "Sort by timestamp.desc for latest. "
        "Ex: status:'new'+severity_name:'Critical'"
    ),
    # === Hosts ===
    "falcon_search_hosts": (
        "Common fields: hostname, platform_name (Windows|Linux|Mac), "
        "status (normal|contained|containment_pending|lift_containment_pending), "
        "local_ip, external_ip, os_version, last_seen, "
        "product_type_desc (Workstation|Server|Domain Controller). "
        "Date filters: last_seen:>'now-7d' (relative). "
        "Use status:'contained' to find hosts in network containment. "
        "Ex: platform_name:'Windows'+status:'contained'"
    ),
    # === Cases ===
    "falcon_search_cases": (
        "Common fields: status (New|In Progress|Closed|Reopened), "
        "severity (Informational|Low|Medium|High|Critical), name, "
        "assigned_to_name, created_timestamp (UTC datetime), tags."
    ),
    # === Cloud: Kubernetes Containers ===
    "falcon_search_kubernetes_containers": (
        "Common fields: cluster_name, namespace, container_name, "
        "image_repository, pod_name, running_status (true|false), "
        "cloud_name, cloud_region, first_seen (UTC datetime)."
    ),
    "falcon_count_kubernetes_containers": (
        "Common fields: cluster_name, namespace, container_name, "
        "image_repository, running_status (true|false), cloud_name, cloud_region."
    ),
    # === Cloud: Image Vulnerabilities ===
    "falcon_search_images_vulnerabilities": (
        "Common fields: cve_id, severity (Critical|High|Medium|Low|Unknown), "
        "cvss_score, registry, repository, tag, container_running_status (running|stopped)."
    ),
    # === Cloud: CSPM Assets ===
    "falcon_search_cspm_assets": (
        "Common fields: cloud_provider (aws|azure|gcp), account_name, "
        "resource_type, region, service, active (true|false), tags."
    ),
    # === Cloud: IOM Findings ===
    "falcon_search_iom_findings": (
        "Common fields: severity (Critical|High|Medium|Low|Informational), "
        "status (open|pass), cloud_provider (aws|azure|gcp), "
        "service, region, resource_type, account_name, rule_name."
    ),
    # === Correlation Rules ===
    "falcon_search_correlation_rules": (
        "Common fields: name, status (enabled|disabled), "
        "severity (critical|high|medium|low|informational), "
        "tactic, technique, created_on (UTC datetime)."
    ),
    # === Custom IOA Rule Groups ===
    "falcon_search_ioa_rule_groups": (
        "Common fields: platform (windows|mac|linux), name, enabled (true|false), "
        "rules.pattern_severity (critical|high|medium|low|informational), "
        "rules.ruletype_name, created_on (UTC datetime)."
    ),
    # === Discover: Applications ===
    "falcon_search_applications": (
        "Common fields: name, vendor, category, is_suspicious (true|false), "
        "host.hostname, host.platform_name (Windows|Linux|Mac), "
        "last_used_timestamp (UTC datetime), installation_timestamp (UTC datetime)."
    ),
    # === Discover: Unmanaged Assets ===
    "falcon_search_unmanaged_assets": (
        "Common fields: hostname, platform_name (Windows|Linux|Mac), "
        "external_ip, local_ip_addresses, os_version, "
        "first_seen_timestamp (UTC datetime), last_seen_timestamp (UTC datetime)."
    ),
    # === Firewall Rules ===
    "falcon_search_firewall_rules": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime)."
    ),
    "falcon_search_firewall_rule_groups": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime)."
    ),
    "falcon_search_firewall_policy_rules": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime)."
    ),
    # === Intel: Actors ===
    "falcon_query_actor_entities": (
        "Common fields: name, actor_type, known_as, "
        "motivations.value (Criminal|Destruction|Espionage|Hacktivism), "
        "target_countries, target_industries.value (e.g. 'Financial Services'|'Government'|'Technology'|'Healthcare'|'Energy'), "
        "last_activity_date. Date filters: last_activity_date:>'now-90d' (relative). "
        "Use q parameter for free-text keyword search across all fields."
    ),
    "falcon_search_actors": (
        "Common fields: name, actor_type, known_as, "
        "motivations.value (Criminal|Destruction|Espionage|Hacktivism), "
        "target_countries, target_industries.value (e.g. 'Financial Services'|'Government'|'Technology'|'Healthcare'|'Energy'), "
        "last_activity_date. Date filters: last_activity_date:>'now-90d' (relative). "
        "Use q parameter for free-text keyword search across all fields."
    ),
    # === Intel: Indicators ===
    "falcon_query_indicator_entities": (
        "Common fields: type (hash_md5|hash_sha256|domain|ip_address|url|email_address), "
        "malicious_confidence (high|medium|low|unverified), "
        "malware_families, threat_types, kill_chains, "
        "published_date. Date filters: published_date:>'now-7d' (relative)."
    ),
    "falcon_search_indicators": (
        "Common fields: type (hash_md5|hash_sha256|domain|ip_address|url|email_address), "
        "malicious_confidence (high|medium|low|unverified), "
        "malware_families, threat_types, kill_chains, "
        "published_date. Date filters: published_date:>'now-7d' (relative)."
    ),
    # === Intel: Reports ===
    "falcon_query_report_entities": (
        "Common fields: name, type, sub_type, actors, "
        "target_countries, target_industries, tags, "
        "created_date (UTC datetime), last_modified_date (UTC datetime)."
    ),
    "falcon_search_reports": (
        "Common fields: name, type, sub_type, actors, "
        "target_countries, target_industries, tags, "
        "created_date (UTC datetime), last_modified_date (UTC datetime)."
    ),
    # === IOC ===
    "falcon_search_iocs": (
        "Common fields: type (domain|ipv4|ipv6|md5|sha256), "
        "action (detect|prevent|allow), severity_number (1-5), "
        "source, applied_globally (true|false), expired (true|false), "
        "created_on (UTC datetime)."
    ),
    # === RTR Sessions ===
    "falcon_search_sessions": (
        "Common fields: hostname, user_id, origin, "
        "created_at (UTC datetime), offline_queued (true|false), "
        "base_command."
    ),
    "falcon_search_rtr_sessions": (
        "Common fields: hostname, user_id, origin, "
        "created_at (UTC datetime), offline_queued (true|false), "
        "base_command."
    ),
    # === Quarantine ===
    "falcon_search_quarantined_files": (
        "Common fields: hostname, sha256, state (quarantined|released), "
        "date_updated (UTC datetime), paths."
    ),
    "falcon_preview_quarantine_actions": (
        "Common fields: hostname, sha256, state (quarantined|released), "
        "date_updated (UTC datetime), paths."
    ),
    "falcon_update_quarantined_files": (
        "Common fields: hostname, sha256, state (quarantined|released), "
        "date_updated (UTC datetime), paths."
    ),
    "falcon_delete_quarantined_files": (
        "Common fields: hostname, sha256, state (quarantined|released), "
        "date_updated (UTC datetime), paths."
    ),
    # === Scheduled Reports ===
    "falcon_search_scheduled_reports": (
        "Common fields: name, type, status (Active|Inactive|Expired), "
        "last_execution.status (Success|Failed|Pending), "
        "created_on (UTC datetime), next_execution_on (UTC datetime)."
    ),
    "falcon_search_report_executions": (
        "Common fields: scheduled_report_id, status (Success|Failed|Pending|Running), "
        "type, created_on (UTC datetime)."
    ),
    # === Sensor Usage ===
    "falcon_search_sensor_usage": (
        "Common fields: event_date (YYYY-MM-DD), period (daily|weekly|monthly)."
    ),
    # === Serverless Vulnerabilities ===
    "falcon_search_serverless_vulnerabilities": (
        "Common fields: cve_id, severity (Critical|High|Medium|Low|Unknown), "
        "cloud_provider (aws|azure|gcp), function_name, "
        "application_name, runtime, cvss_base_score."
    ),
    # === Spotlight Vulnerabilities ===
    "falcon_search_vulnerabilities": (
        "Common fields: cve.id, cve.severity (Critical|High|Medium|Low), "
        "cve.exprt_rating (Critical|High|Medium|Low), "
        "status (open|closed|reopen), host_info.hostname, "
        "cve.exploit_status, created_timestamp (UTC datetime)."
    ),
}
