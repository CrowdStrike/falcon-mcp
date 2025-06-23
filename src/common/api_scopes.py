"""
API scope definitions and utilities for Falcon MCP Server

This module provides API scope definitions and related utilities for the Falcon MCP server.
"""
from typing import List, Optional

from .logging import get_logger

logger = get_logger(__name__)

# Map of API operations to required scopes
# This can be expanded as more modules and operations are added
API_SCOPE_REQUIREMENTS = {
    # Detections operations
    "QueryDetects": ["detections:read"],
    "GetDetectSummaries": ["detections:read"],
    # Hosts operations
    "QueryDevices": ["hosts:read"],
    "GetDeviceDetails": ["hosts:read"],
    # Incidents operations
    "QueryIncidents": ["incidents:read"],
    "GetIncidentDetails": ["incidents:read"],
    "CrowdScore": ["incidents:read"],
    "GetIncidents": ["incidents:read"],
    "GetBehaviors": ["incidents:read"],
    "QueryBehaviors": ["incidents:read"],
    # Intel operations
    "QueryIntelActorEntities": ["actors-falcon-intelligence:read"],
    "QueryIntelIndicatorEntities": ["indicators:read"],
    "QueryIntelReportEntities": ["reports:read"],
    "QueryIntelRuleEntities": ["rules:read"],
    "GetIntelActorEntities": ["actors-falcon-intelligence:read"],
    "GetIntelIndicatorEntities": ["indicators:read"],
    "GetIntelReportPDF": ["reports:read"],
    "GetIntelReportEntities": ["reports:read"],
    "GetIntelRuleEntities": ["rules:read"],
    "GetIntelRuleFile": ["rules:read"],
    "GetLatestIntelIndicatorTimestamp": ["indicators:read"],
    "GetMitreReport": ["actors-falcon-intelligence:read"],
    "GetRuleDetails": ["rules:read"],
    "GetRulesDetails": ["rules:read"],
    "GetRulePreview": ["rules:read"],
    "GetVulnerabilities": ["vulnerabilities:read"],
    # Add more mappings as needed
}


def get_required_scopes(operation: Optional[str]) -> List[str]:
    """Get the required API scopes for a specific operation.

    Args:
        operation: The API operation name

    Returns:
        List[str]: List of required API scopes
    """
    if operation is None:
        return []
    return API_SCOPE_REQUIREMENTS.get(operation, [])
