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
    # Incidents operations
    "QueryIncidents": ["Incidents:read"],
    "CrowdScore": ["Incidents:read"],
    "GetIncidents": ["Incidents:read"],
    "GetBehaviors": ["Incidents:read"],
    "QueryBehaviors": ["Incidents:read"],
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
    "cloud_security_assets_queries": ["Cloud Security API Assets:Read"],
    "cloud_security_assets_entities_get": ["Cloud Security API Assets:Read"],
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
    # Add more mappings as needed
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
