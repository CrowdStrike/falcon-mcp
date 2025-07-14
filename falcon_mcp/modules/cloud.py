"""
Cloud module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon cloud resources like
Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets.
"""

from typing import Dict, List, Optional, Any
from textwrap import dedent

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

from falcon_mcp.resources.cloud import (
    SEARCH_KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
    SEARCH_IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class CloudModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon cloud resources."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.kubernetes_containers_fql_filter_guide,
            name="kubernetes_containers_fql_filter_guide",
        )

        self._add_tool(
            server,
            self.search_kubernetes_containers,
            name="search_kubernetes_containers",
        )

        self._add_tool(server, self.count_kubernetes_containers, name="count_kubernetes_containers")

        self._add_tool(
            server,
            self.images_vulnerabilities_fql_filter_guide,
            name="images_vulnerabilities_fql_filter_guide",
        )

        self._add_tool(
            server,
            self.search_images_vulnerabilities,
            name="search_images_vulnerabilities",
        )

    def search_kubernetes_containers(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_kubernetes_containers_fql_filter_guide` tool when building this filter parameter.",
            examples={"cloud:'AWS'", "cluster_name:'prod'"},
        ),
        limit: Optional[int] = Field(
            default=10,
            ge=1,
            le=9999,
            description="The maximum number of containers to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: Optional[int] = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return containers.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description=dedent(
                """
                Sort kubernetes containers using these options:

                cloud_name: Cloud provider name
                cloud_region: Cloud region name
                cluster_name: Kubernetes cluster name
                container_name: Kubernetes container name
                namespace: Kubernetes namespace name
                last_seen: Timestamp when the container was last seen
                first_seen: Timestamp when the container was first seen
                running_status: Container running status which is either true or false

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'container_name.desc' or 'container_name|desc'

                When searching containers running vulnerable images, use 'image_vulnerability_count.desc' to get container with most images vulnerabilities.

                Examples: 'container_name.desc', 'last_seen.desc'
            """
            ).strip(),
            examples={"container_name.desc", "last_seen.desc"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

        IMPORTANT: You must use the tool `falcon_kubernetes_containers_fql_filter_guide` whenever you want to use the `filter` parameter.
        This tool contains the guide on how to build the FQL `filter` parameter for `falcon_search_kubernetes_containers` tool.

        Returns:
            List of kubernetes containers
        """

        # Prepare parameters
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Define the operation name
        operation = "ReadContainerCombined"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def count_kubernetes_containers(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_kubernetes_containers_fql_filter_guide` tool when building this filter parameter.",
            examples={"cloud:'Azure'", "container_name:'service'"},
        ),
    ) -> List[Dict[str, Any]]:
        """Count kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

        IMPORTANT: You must use the tool `falcon_kubernetes_containers_fql_filter_guide` whenever you want to use the `filter` parameter.
        This tool contains the guide on how to build the FQL `filter` parameter for `falcon_count_kubernetes_containers` tool.

        Returns:
            List with a single count result
        """

        # Prepare parameters
        params = prepare_api_parameters(
            {
                "filter": filter,
            }
        )

        # Define the operation name
        operation = "ReadContainerCount"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def kubernetes_containers_fql_filter_guide(self) -> str:
        """
        Returns the guide for the `filter` for kubernetes containers tools.

        IMPORTANT: Before running `falcon_search_kubernetes_containers` or `falcon_count_kubernetes_containers`,
        always call this tool to get information about how to build the FQL for the filter.
        """
        return SEARCH_KUBERNETES_CONTAINERS_FQL_DOCUMENTATION

    def search_images_vulnerabilities(
        self,
        filter: Optional[str] = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_images_vulnerabilities_fql_filter_guide` tool when building this filter parameter.",
            examples={"cve_id:*'*2025*'", "cvss_score:>5"},
        ),
        limit: Optional[int] = Field(
            default=10,
            ge=1,
            le=9999,
            description="The maximum number of containers to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: Optional[int] = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return containers.",
        ),
        sort: Optional[str] = Field(
            default=None,
            description=dedent(
                """
                Sort images vulnerabilities using these options:

                cps_current_rating: CSP rating of the image vulnerability
                cve_id: CVE ID of the image vulnerability
                cvss_score: CVSS score of the image vulnerability
                images_impacted: Number of images impacted by the vulnerability

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'container_name.desc' or 'container_name|desc'

                Examples: 'cvss_score.desc', 'cps_current_rating.asc'
            """
            ).strip(),
            examples={"cvss_score.desc", "cps_current_rating.asc"},
        ),
    ) -> List[Dict[str, Any]]:
        """Search for images vulnerabilities in your CrowdStrike Image Assessments

        IMPORTANT: You must use the tool `falcon_images_vulnerabilities_fql_filter_guide` whenever you want to use the `filter` parameter.
        This tool contains the guide on how to build the FQL `filter` parameter for `falcon_search_images_vulnerabilities` tool.

        Returns:
            List of images vulnerabilities
        """

        # Prepare parameters
        params = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            }
        )

        # Define the operation name
        operation = "ReadCombinedVulnerabilities"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def images_vulnerabilities_fql_filter_guide(self) -> str:
        """
        Returns the guide for the `filter` for images vulnerabilities tools.

        IMPORTANT: Before running `falcon_search_images_vulnerabilities`,
        always call this tool to get information about how to build the FQL for the filter.
        """
        return SEARCH_IMAGES_VULNERABILITIES_FQL_DOCUMENTATION
