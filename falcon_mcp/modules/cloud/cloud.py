"""
Cloud module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon cloud resources like
Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, IOM Findings,
CSPM Suppression Rules, Cloud Risks, Cloud Groups, and Cloud Insights.
"""

from falcon_mcp.modules.cloud.cloud_assets import _CloudAssetsMixin
from falcon_mcp.modules.cloud.cloud_containers import _CloudContainersMixin
from falcon_mcp.modules.cloud.cloud_insights import _CloudInsightsMixin
from falcon_mcp.modules.cloud.cloud_iom import _CloudIomMixin
from falcon_mcp.modules.cloud.cloud_risks import _CloudRisksMixin


class CloudModule(
    _CloudRisksMixin,
    _CloudIomMixin,
    _CloudContainersMixin,
    _CloudAssetsMixin,
    _CloudInsightsMixin,
):
    """Module for accessing and analyzing CrowdStrike Falcon cloud resources."""
