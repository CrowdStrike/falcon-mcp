"""
API scope definitions and utilities for Falcon MCP Server

This module provides API scope definitions and related utilities for the Falcon MCP server.
"""

from .logging import get_logger

logger = get_logger(__name__)

# Map of API operations to required scopes
# This can be expanded as more modules and operations are added
API_SCOPE_REQUIREMENTS = {
    # Alerts operations (migrated from detections)
    "GetQueriesAlertsV2": ["Alerts:read"],
    "PostEntitiesAlertsV2": ["Alerts:read"],
    # Hosts operations
    "QueryDevicesByFilter": ["Hosts:read"],
    "PostDeviceDetailsV2": ["Hosts:read"],
    # Intel operations
    "QueryIntelActorEntities": ["Actors (Falcon Intelligence):read"],
    "QueryIntelIndicatorEntities": ["Indicators (Falcon Intelligence):read"],
    "QueryIntelReportEntities": ["Reports (Falcon Intelligence):read"],
    "GetMitreReport": ["Actors (Falcon Intelligence):read"],
    # IOC operations
    "indicator_search_v1": ["IOC Management:read"],
    "indicator_get_v1": ["IOC Management:read"],
    "indicator_create_v1": ["IOC Management:write"],
    "indicator_delete_v1": ["IOC Management:write"],
    # Firewall Management operations
    "query_rules": ["Firewall Management:read"],
    "get_rules": ["Firewall Management:read"],
    "query_rule_groups": ["Firewall Management:read"],
    "get_rule_groups": ["Firewall Management:read"],
    "query_policy_rules": ["Firewall Management:read"],
    "create_rule_group": ["Firewall Management:write"],
    "delete_rule_groups": ["Firewall Management:write"],
    # Spotlight operations
    "combinedQueryVulnerabilities": ["Vulnerabilities:read"],
    # Discover operations
    "combined_applications": ["Assets:read"],
    "combined_hosts": ["Assets:read"],
    # Cloud operations
    "ReadContainerCombined": ["Falcon Container Image:read"],
    "ReadContainerCount": ["Falcon Container Image:read"],
    "ReadCombinedVulnerabilities": ["Falcon Container Image:read"],
    # CSPM Assets operations
    "cloud_security_assets_queries": ["Cloud Security API Assets:read"],
    "cloud_security_assets_entities_get": ["Cloud Security API Assets:read"],
    # CSPM IOM Findings operations (CloudSecurityDetections)
    "cspm_evaluations_iom_queries": ["Cloud Security API Detections:read"],
    "cspm_evaluations_iom_entities": ["Cloud Security API Detections:read"],
    # CSPM Suppression Rules (override endpoints)
    "QuerySuppressionRules": ["Cloud Security Policies:read"],
    "GetSuppressionRules": ["Cloud Security Policies:read"],
    "CreateSuppressionRule": ["Cloud Security Policies:write"],
    "DeleteSuppressionRules": ["Cloud Security Policies:write"],
    # Identity Protection operations
    "api_preempt_proxy_post_graphql": [
        "Identity Protection Entities:read",
        "Identity Protection Timeline:read",
        "Identity Protection Detections:read",
        "Identity Protection Assessment:read",
        "Identity Protection GraphQL:write",
    ],
    # Sensor Usage operations
    "GetSensorUsageWeekly": ["Sensor Usage:read"],
    # Serverless operations
    "GetCombinedVulnerabilitiesSARIF": ["Falcon Container Image:read"],
    # Scheduled Reports operations
    "scheduled_reports_query": ["Scheduled Reports:read"],
    "scheduled_reports_get": ["Scheduled Reports:read"],
    "scheduled_reports_launch": ["Scheduled Reports:read"],
    # Report Executions operations (same scope as Scheduled Reports)
    "report_executions_query": ["Scheduled Reports:read"],
    "report_executions_get": ["Scheduled Reports:read"],
    "report_executions_download_get": ["Scheduled Reports:read"],
    # NGSIEM operations
    "StartSearchV1": ["NGSIEM:write"],
    "GetSearchStatusV1": ["NGSIEM:read"],
    "StopSearchV1": ["NGSIEM:write"],
    # Real Time Response operations
    "RTR_ListAllSessions": ["Real time response:read"],
    "RTR_ListSessions": ["Real time response:read"],
    "RTR_InitSession": ["Real time response:read"],
    "RTR_DeleteSession": ["Real time response:read"],
    "RTR_PulseSession": ["Real time response:read"],
    "RTR_CheckCommandStatus": ["Real time response:read"],
    "RTR_ExecuteCommand": ["Real time response:read"],
    "RTR_ListFilesV2": ["Real time response:write"],
    "RTRAuditSessions": ["real-time-response-audit:read"],
    "RTR_AggregateSessions": ["Real time response:read"],
    # Real Time Response Admin operations
    "RTR_ListScripts": ["Real time response (admin):write"],
    "RTR_GetScriptsV2": ["Real time response (admin):write"],
    "RTR_ListFalconScripts": ["Real time response (admin):write"],
    "RTR_GetFalconScripts": ["Real time response (admin):write"],
    "RTR_ListPut_Files": ["Real time response (admin):write"],
    "RTR_GetPut_FilesV2": ["Real time response (admin):write"],
    "RTR_CheckAdminCommandStatus": ["Real time response (admin):write"],
    "RTR_ExecuteAdminCommand": ["Real time response (admin):write"],
    # Quarantine operations
    "QueryQuarantineFiles": ["Quarantined Files:read"],
    "GetQuarantineFiles": ["Quarantined Files:read"],
    "ActionUpdateCount": ["Quarantined Files:read"],
    "UpdateQuarantinedDetectsByIds": ["Quarantined Files:write"],
    "UpdateQfByQuery": ["Quarantined Files:write"],
    # Custom IOA operations
    "query_rule_groups_full": ["Custom IOA Rules:read"],
    "query_platformsMixin0": ["Custom IOA Rules:read"],
    "get_platformsMixin0": ["Custom IOA Rules:read"],
    "query_rule_types": ["Custom IOA Rules:read"],
    "get_rule_types": ["Custom IOA Rules:read"],
    "create_rule_groupMixin0": ["Custom IOA Rules:write"],
    "update_rule_groupMixin0": ["Custom IOA Rules:write"],
    "delete_rule_groupsMixin0": ["Custom IOA Rules:write"],
    "create_rule": ["Custom IOA Rules:write"],
    "update_rules_v2": ["Custom IOA Rules:write"],
    "delete_rules": ["Custom IOA Rules:write"],
    # Shield (SaaS Security) operations
    "GetSecurityChecksV3": ["SaaS Security:read"],
    "GetSecurityCheckAffectedV3": ["SaaS Security:read"],
    "GetMetricsV3": ["SaaS Security:read"],
    "GetSecurityCheckComplianceV3": ["SaaS Security:read"],
    "GetAlertsV3": ["SaaS Security:read"],
    "GetActivityMonitorV3": ["SaaS Security:read"],
    "GetUserInventoryV3": ["SaaS Security:read"],
    "GetDeviceInventoryV3": ["SaaS Security:read"],
    "GetAppInventory": ["SaaS Security:read"],
    "GetAppInventoryUsers": ["SaaS Security:read"],
    "GetAssetInventoryV3": ["SaaS Security:read"],
    "GetIntegrationsV3": ["SaaS Security:read"],
    "GetSystemUsersV3": ["SaaS Security:read"],
    "GetSupportedSaasV3": ["SaaS Security:read"],
    "GetSystemLogsV3": ["SaaS Security:read"],
    "DismissSecurityCheckV3": ["SaaS Security:write"],
    "DismissAffectedEntityV3": ["SaaS Security:write"],
    # Case Management operations
    "queries_cases_get_v1": ["Cases:read"],
    "entities_cases_post_v2": ["Cases:read"],
    "entities_cases_put_v2": ["Cases:write"],
    "entities_cases_patch_v2": ["Cases:write"],
    "entities_alert_evidence_post_v1": ["Cases:write"],
    "entities_event_evidence_post_v1": ["Cases:write"],
    "entities_case_tags_post_v1": ["Cases:write"],
    "entities_case_tags_delete_v1": ["Cases:write"],
    # Case Templates operations
    "queries_templates_get_v1": ["Case Templates:read"],
    "entities_templates_get_v1": ["Case Templates:read"],
    # Correlation Rules operations
    "combined_rules_get_v2": ["Correlation Rules:read"],
    "entities_rules_post_v1": ["Correlation Rules:write"],
    "entities_rules_patch_v1": ["Correlation Rules:write"],
    "entities_rules_delete_v1": ["Correlation Rules:write"],
    # Data Protection operations
    "queries_classification_get_v2": ["Data Protection:read"],
    "entities_classification_get_v2": ["Data Protection:read"],
    "queries_policy_get_v2": ["Data Protection:read"],
    "entities_policy_get_v2": ["Data Protection:read"],
    "queries_content_pattern_get_v2": ["Data Protection:read"],
    "entities_content_pattern_get": ["Data Protection:read"],
}


def get_required_scopes(operation: str | None) -> list[str]:
    """Get the required API scopes for a specific operation.

    Args:
        operation: The API operation name

    Returns:
        List[str]: List of required API scopes
    """
    if operation is None:
        return []
    return API_SCOPE_REQUIREMENTS.get(operation, [])
