"""
Curated inline FQL field hints for dynamic mode.

These compact hints are appended to filter parameter descriptions when tools are
discovered via falcon_search_tools, so LLMs have the most common fields at hand
without needing to read the full FQL resource.
"""

FILTER_HINTS: dict[str, str] = {
    # === AgentWorks ===
    "falcon_search_agentworks_agents": (
        "Common fields: template_id, active_version.model "
        "(e.g. 'bedrock.claude-4-6-sonnet'), published_version_ids. "
        "The agent has no top-level name/model — filter model via active_version.model. "
        "No wildcards. Sort by created_date. "
        "Ex: active_version.model:'bedrock.claude-4-6-sonnet'"
    ),
    "falcon_search_agentworks_agent_versions": (
        "Common fields: agent_id, name (exact, no wildcards), model, "
        "is_published (true|false), is_enabled (true|false), created_at (UTC datetime). "
        "Sort by created_at. "
        "Ex: agent_id:'<uuid>'+is_published:true"
    ),
    "falcon_search_agentworks_spans": (
        "ALWAYS filter, usually by trace_id (pass an invocation's ai_trace_id). "
        "Common fields: trace_id, span_type (llm|aw_agent|aiplatform_agent|...), "
        "status (unset|ok|error), name, duration_ms, "
        "start_time (last 90 days only, e.g. start_time:>'now-7d'). "
        "Sort by start_time. "
        "Ex: trace_id:'<ai_trace_id>'"
    ),
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
    "falcon_aggregate_detections": (
        "Common fields: severity_name (Critical|High|Medium|Low|Informational), "
        "status (new|in_progress|closed|reopened), product (epp|idp|xdr|overwatch), "
        "device.hostname, tactic, technique_id, assigned_to_name, filename. "
        "The filter narrows which alerts are counted; the aggregated field is set "
        "separately by the field param. "
        "Date filters: timestamp:>'now-24h' (relative). "
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
        "Common fields: status (new|in_progress|closed|reopened), "
        "severity (Integer 1-100: Informational=1, Low~25, Medium~50, High~75, Critical=100), "
        "name, assigned_to_name, created_timestamp (UTC datetime), tags."
    ),
    "falcon_aggregate_case_slas": (
        "Common fields: name, id, cid, created_by_name, updated_by_name, "
        "created_timestamp, updated_timestamp. "
        "Substring match uses :* (name:*'*Corp*'); ~ and 'val*' return nothing. "
        "Date filters: created_timestamp:>'now-30d' (relative). "
        "Ex: created_timestamp:>'now-30d'"
    ),
    "falcon_aggregate_case_templates": (
        "Common fields: name, id, cid, created_by_name, updated_by_name, "
        "created_timestamp, updated_timestamp. "
        "Substring match uses :* (name:*'*Case*'); ~ and 'val*' return nothing. "
        "Date filters: created_timestamp:>'now-30d' (relative). "
        "Ex: created_by_name:'analyst@example.com'"
    ),
    "falcon_aggregate_case_access_tags": (
        "Common fields: key, id, cid — access tags accept no other field. "
        "Substring match uses :* (key:*'*ANALYST*'); ~ and 'val*' return nothing. "
        "Ex: key:'ANALYST1'"
    ),
    "falcon_aggregate_case_notification_groups": (
        "Common fields: name, id, cid, created_by_name, updated_by_name, "
        "created_timestamp, updated_timestamp. "
        "Substring match uses :* (name:*'*Analyst*'); ~ and 'val*' return nothing. "
        "Date filters: created_timestamp:>'now-90d' (relative). "
        "Ex: name:*'*Analyst*'"
    ),
    "falcon_aggregate_case_file_details": (
        "Common fields: name (file name), case_id, id (file id), cid, "
        "file_size (a string such as '114.8 KB', not a number). "
        "Substring match uses :* (name:*'*.png'); ~ returns nothing. "
        "Prefer the case_ids parameter over a case_id filter. "
        "Ex: name:*'*.png'"
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
        "status (open|suppressed|pass), cloud_provider (aws|azure|gcp — lowercase "
        "required; uppercase returns an empty result, not an error), "
        "service, region, resource_type, account_name, rule_name."
    ),
    # === Cloud: Cloud Insights ===
    "falcon_search_cloud_insights": (
        "Filter on insights.id (insight ID), insights.boolean_value (true|false), "
        "insights.string_value (string; substring match needs :*'*val*' — 'val*' and ~ return nothing), "
        "insights.integer_value (integer, supports range ops e.g. :>0), "
        "insights.date_value (ISO-8601 timestamp, e.g. :<'2025-01-01T00:00:00Z'), "
        "insights.string_list_value (list member match). "
        "All fields are asset-level: a condition matches if any insight on the asset satisfies it. "
        "Use snake_case field names — camelCase is rejected. "
        "To scope by category: call list_cloud_insight_definitions(categories=['X']) first, "
        "then pass the returned insight_ids as insights.id:['id1','id2']. "
        "Ex: insights.id:'identityIsAdmin'+insights.boolean_value:true"
    ),
    # === Cloud: Cloud Risks ===
    "falcon_search_cloud_groups": (
        "Common fields: name, created_at (UTC datetime), updated_at (UTC datetime). "
        "Group tag fields: environment, business_unit, business_impact."
    ),
    "falcon_search_cloud_risks": (
        "Common fields: severity (Critical|High|Medium|Low|Informational), "
        "status (Open|Resolved|Suppressed), cloud_provider (aws|azure|gcp), "
        "asset_name, asset_type, asset_region, account_id, account_name, "
        "rule_name, service_category, groups.environment, groups.business_unit. "
        "Date filters: use absolute ISO-8601 only, e.g. first_seen:>'2024-01-01T00:00:00Z'. "
        "Ex: severity:'Critical'+status:'Open'+cloud_provider:'aws'. "
        "Also: threat_actors (adversary/threat group name), risk_factor (risk factor identifier like PUBLIC_ACCESS)."
    ),
    # === Correlation Rules ===
    "falcon_search_correlation_rules": (
        "Common fields: name, status (active|inactive), state (published|unpublished|draft), "
        "severity (Integer: 10=Informational|30=Low|50=Medium|70=High|90=Critical; supports range ops e.g. severity:>50), "
        "mitre_attack.tactic_id (e.g. TA0001), mitre_attack.technique_id (e.g. T1059), "
        "created_on (UTC datetime)."
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
    # === Discover: Managed Assets ===
    "falcon_search_managed_assets": (
        "Common fields: aid (Falcon agent ID - same value as the device ID from "
        "falcon_search_hosts; if you already have one, prefer it since it is unique "
        "per sensor, but you do not need to fetch it first), "
        "encryption_status (Encrypted|Unencrypted), "
        "unencrypted_drives_count/number_of_disk_drives (numbers, use :>0), "
        "os_security.credential_guard_status / os_security.secure_boot_enabled_status / "
        "os_security.iommu_protection_status (booleans, use true|false - NOT 'Enabled'), "
        "used_disk_space/total_memory/average_processor_usage (numbers, use :>0), "
        "platform_name (Windows|Linux|Mac), criticality, internet_exposure (Yes|No), "
        "last_seen_timestamp:>'now-24h' (relative date). "
        "Ex: encryption_status:'Unencrypted'+platform_name:'Windows'"
    ),
    # === Firewall Rules ===
    "falcon_search_firewall_rules": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime). "
        "name: use the contains operator name:~'value' (whole-word substring); a "
        "name:'value*' glob is treated literally and returns nothing."
    ),
    "falcon_search_firewall_rule_groups": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime). "
        "name: use the contains operator name:~'value' (whole-word substring); a "
        "name:'value*' glob is treated literally and returns nothing."
    ),
    "falcon_search_firewall_policy_rules": (
        "Common fields: platform (windows|mac|linux), name, "
        "enabled (true|false), created_on (UTC datetime). "
        "name: use the contains operator name:~'value' (whole-word substring); a "
        "name:'value*' glob is treated literally and returns nothing."
    ),
    # === Intel: Actors ===
    "falcon_search_actors": (
        "Common fields: name, actor_type, known_as, "
        "motivations.value (Criminal|Destruction|Espionage|Hacktivism), "
        "target_countries, target_industries.value (e.g. 'Financial Services'|'Government'|'Technology'|'Healthcare'|'Energy'), "
        "last_activity_date. Date filters: last_activity_date:>'now-90d' (relative). "
        "Use q parameter for free-text keyword search across all fields."
    ),
    # === Intel: Indicators ===
    "falcon_search_indicators": (
        "Common fields: type (hash_md5|hash_sha256|domain|ip_address|url|email_address), "
        "malicious_confidence (high|medium|low|unverified), "
        "malware_families, threat_types, kill_chains, "
        "published_date. Date filters: published_date:>'now-7d' (relative)."
    ),
    # === Intel: Reports ===
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
    # === Exclusions ===
    "falcon_search_exclusions": (
        "Fields vary by exclusion_type. Common: applied_globally (true|false), "
        "created_on, last_modified (certificate uses modified_on instead). "
        "ioa: pattern_id. ml/sensor_visibility: value (use :* wildcard for substrings, "
        "e.g. value:*'*/usr/local*'; plain : is exact and treats * literally). "
        "certificate: name (use :* wildcard), created_by, modified_by. "
        "Date filters: created_on:>'now-7d' (relative)."
    ),
    # === Host Groups ===
    "falcon_search_host_groups": (
        "Common fields: name, group_type (static|dynamic|staticByID), "
        "created_by, created_timestamp (UTC datetime), "
        "modified_by, modified_timestamp (UTC datetime)."
    ),
    "falcon_search_host_group_members": (
        "Filters on HOST (device) attributes: hostname, platform_name (Windows|Linux|Mac), "
        "status (normal|contained), local_ip, external_ip, os_version, last_seen, "
        "product_type_desc (Workstation|Server|Domain Controller)."
    ),
    "falcon_perform_host_group_action": (
        "Filters on HOST (device) attributes to select members for the action: "
        "hostname, platform_name (Windows|Linux|Mac), status (normal|contained), "
        "local_ip, external_ip, os_version, product_type_desc (Workstation|Server|Domain Controller)."
    ),
    # === Policies ===
    "falcon_search_policies": (
        "Common fields: platform_name (Windows|Linux|Mac; 'all' for content_update), "
        "enabled (true|false), created_timestamp, modified_timestamp. "
        "name: use the contains operator name:~'value' for prevention/response/firewall/device_control "
        "(a '*value*' glob is literal and returns nothing); name is NOT filterable for sensor_update/content_update. "
        "Date filters: created_timestamp:>'now-7d' (relative). "
        "Do NOT sort by platform_name (HTTP 500)."
    ),
    "falcon_search_policy_members": (
        "Filters on HOST (device) attributes: hostname, platform_name (Windows|Linux|Mac), "
        "status (normal|contained), local_ip, external_ip, os_version, last_seen, "
        "product_type_desc (Workstation|Server|Domain Controller)."
    ),
    # === Data Protection ===
    "falcon_search_data_protection_classifications": (
        "Common fields: name, created_by, created_at (UTC datetime), "
        "modified_by, modified_at (UTC datetime)."
    ),
    "falcon_search_data_protection_policies": (
        "Common fields: name, description, is_enabled (true|false), "
        "is_default (true|false), precedence, created_at (UTC datetime), modified_by."
    ),
    "falcon_search_data_protection_content_patterns": (
        "Common fields: name, category, type, region, example, deleted (true|false)."
    ),
    # === Recon ===
    "falcon_search_recon_notifications": (
        "Common fields: status (new|in-progress|closed-false-positive|closed-true-positive), "
        "rule_priority (low|medium|high), "
        "rule_topic (SA_DOMAIN|SA_TYPOSQUATTING|SA_EMAIL|SA_IP|SA_BRAND_PRODUCT), "
        "item_type (exposed_data), item_site (stealer_logs|...), "
        "created_date:>'now-7d' (relative date). "
        "NOTE: assigned_to_uuid requires a UUID, not an email. "
        "Ex: status:'new'+rule_priority:'high'"
    ),
    "falcon_search_recon_rules": (
        "Common fields: status (active), "
        "topic (SA_DOMAIN|SA_TYPOSQUATTING|SA_EMAIL|SA_IP|SA_BRAND_PRODUCT), "
        "priority (low|medium|high), permissions (private|public), "
        "breach_monitoring_enabled (true|false), "
        "created_timestamp:>'now-30d' (relative date). "
        "Ex: status:'active'+topic:'SA_TYPOSQUATTING'"
    ),
    "falcon_search_recon_exposed_data_records": (
        "Common fields: domain, email, "
        "credential_status (newly_reported|confirmed_active|previously_reported), "
        "site, source_category, notification_id, "
        "rule.topic (SA_DOMAIN|...), "
        "created_date:>'now-7d' (relative date). "
        "Ex: domain:'example.com'+credential_status:'newly_reported'"
    ),
    "falcon_aggregate_recon_notifications": (
        "Filters which notifications are counted. Common fields: "
        "status (new|in-progress|pending-review|closed-true-positive|closed-false-positive), "
        "rule_priority (low|medium|high|critical), "
        "rule_topic (SA_TYPOSQUATTING|SA_THIRD_PARTY|SA_CUSTOM|SA_DOMAIN|SA_IP|SA_BRAND_PRODUCT), "
        "rule_id, item_type, item_site, source_category, "
        "created_date:>'now-30d' (relative date). "
        "Ex: rule_topic:'SA_TYPOSQUATTING'+created_date:>'now-30d'"
    ),
    "falcon_aggregate_recon_exposed_data_records": (
        "Filters which records are counted. Common fields: domain, email, "
        "credential_status (newly_reported|confirmed_active|previously_reported), "
        "site (telegram.org|stealer_logs|malware_logs), source_category, notification_id, "
        "rule.topic (SA_DOMAIN|SA_EMAIL), "
        "created_date:>'now-7d' (relative date). "
        "NOTE: the aggregatable `field` list is narrower than what this filter accepts. "
        "Ex: credential_status:'newly_reported'+created_date:>'now-30d'"
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
        "Common fields: event_date (YYYY-MM-DD format, e.g. event_date:'2024-06-11'), "
        "period (number of days as quoted string, e.g. period:'30'; min 1, max 395, default 28)."
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
    # === Fusion SOAR ===
    "falcon_search_workflow_definitions": (
        "Common fields: name.raw (exact: name.raw:'Full Name'; substring: name.raw:*'*part*'), "
        "id, enabled (true|false), trigger.type (On demand|Signal|Scheduled), version, "
        "description, last_modified_timestamp. "
        "Use name.raw, NOT name — name is analyzed and matches whole tokens only. "
        "trigger.type:'On demand' workflows are the ones to execute; 'Signal' ones are refused. "
        "Date filters: last_modified_timestamp:>'now-30d' (relative). "
        "Sort uses dots (name.asc), not pipes. "
        "Ex: enabled:true+trigger.type:'On demand'"
    ),
    "falcon_search_workflow_executions": (
        "Common fields: id (the response calls it execution_id), definition_id, "
        "ui_status (Completed|Failed|In progress|Action required), definition_name (~ token match), "
        "definition_version, test_mode, contains_mocks. "
        "Filter status via ui_status — the `status` field uses a different vocabulary "
        "('Succeeded' not 'Completed'). "
        "Date filters: started_timestamp:>'now-7d', completed_timestamp:>'now-1d' "
        "(NOT start_timestamp/end_timestamp — those are response-only names). "
        "Ex: ui_status:'Completed'+started_timestamp:>'now-7d'"
    ),
}


# Curated inline CQL hints for tools that take a `query_string` (CQL) parameter
# instead of an FQL `filter`. Injected onto the query_string param description in
# dynamic mode, mirroring FILTER_HINTS for FQL filters.
QUERY_STRING_HINTS: dict[str, str] = {
    # === NGSIEM ===
    "falcon_search_ngsiem": (
        "CQL is pipe-based: `filter | command | command` — not SQL or Splunk SPL "
        "(no SELECT/WHERE/stats/`| limit`). Start from a tag filter "
        "`#event_simpleName=ProcessRollup2`, then pipe into `groupBy([field], "
        "function=count())`, `sort(_count, order=desc)`, and `head(n)` to cap raw "
        "events. Unrecognized words become free-text stages instead of an error, so "
        "check `job.parsed_query` against your intent; on zero rows, "
        "`job.processed_events` above zero means a real negative. "
        "For distinct count, time bucketing, regex/contains match, or "
        "filtering on an aggregate, see `falcon://ngsiem/search/cql-guide`."
    ),
}
