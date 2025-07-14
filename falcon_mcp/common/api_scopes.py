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
    # Alerts operations (migrated from detections)
    "GetQueriesAlertsV2": ["alerts:read"],
    "PostEntitiesAlertsV2": ["alerts:read"],
    # Hosts operations
    "QueryDevicesByFilter": ["hosts:read"],
    "PostDeviceDetailsV2": ["hosts:read"],
    # Incidents operations
    "QueryIncidents": ["incidents:read"],
    "GetIncidentDetails": ["incidents:read"],
    "CrowdScore": ["incidents:read"],
    "GetIncidents": ["incidents:read"],
    "GetBehaviors": ["incidents:read"],
    "QueryBehaviors": ["incidents:read"],
    # Intel operations
    "QueryIntelActorEntities": ["actors-falcon-intelligence:read"],
    "QueryIntelIndicatorEntities": ["indicators-falcon-intelligence:read"],
    "QueryIntelReportEntities": ["reports-falcon-intelligence:read"],
    # Spotlight operations
    "combinedQueryVulnerabilities": ["spotlight-vulnerabilities:read"],
    # Add more mappings as needed
}


def get_required_scopes(operation: Optional[str]) -> List[str]:
    """Get the required API scopes for a specific operation.

    Args:
        operation: The API operation name

    Returns:
        List[str]: List of required API scopes
    """
    return API_SCOPE_REQUIREMENTS.get(operation, [])
