"""
Cloud module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon cloud resources like
Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets.
"""

from textwrap import dedent
from typing import Any, Dict, List

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.common.constants import SearchLimits
from falcon_mcp.resources.cloud import (
    IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
    KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
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
            server=server,
            method=self.search_kubernetes_containers,
            name="search_kubernetes_containers",
        )

        # fmt: off
        self._add_tool(
            server=server,
            method=self.count_kubernetes_containers,
            name="count_kubernetes_containers",
        )

        self._add_tool(
            server=server,
            method=self.search_images_vulnerabilities,
            name="search_images_vulnerabilities",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.
        Args:
            server: MCP server instance
        """
        kubernetes_containers_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/kubernetes-containers/fql-guide"),
            name="falcon_kubernetes_containers_fql_filter_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.",
            text=KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
        )

        images_vulnerabilities_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/images-vulnerabilities/fql-guide"),
            name="falcon_images_vulnerabilities_fql_filter_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.",
            text=IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            kubernetes_containers_fql_resource,
        )
        self._add_resource(
            server,
            images_vulnerabilities_fql_resource,
        )

    def search_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://cloud/kubernetes-containers/fql-guide` resource when building this filter parameter.",
            examples={"cloud:'AWS'", "cluster_name:'prod'"},
        ),
        limit: int = Field(
            default=SearchLimits.DEFAULT,
            ge=1,
            le=SearchLimits.MAX_DETECTIONS,
            description="The maximum number of containers to return in this response (default: 10; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return containers.",
        ),
        sort: str | None = Field(
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

        IMPORTANT: You must use the `falcon://cloud/kubernetes-containers/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for `falcon_search_kubernetes_containers` tool.
        """

        return self._base_search_api_call(
            operation="ReadContainerCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Kubernetes containers",
        )

    def count_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://cloud/kubernetes-containers/fql-guide` resource when building this filter parameter.",
            examples={"cloud:'Azure'", "container_name:'service'"},
        ),
    ) -> int:
        """Count kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

        IMPORTANT: You must use the `falcon://cloud/kubernetes-containers/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for `falcon_count_kubernetes_containers` tool.
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

    def search_images_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://cloud/images-vulnerabilities/fql-guide` resource when building this filter parameter.",
            examples={"cve_id:*'*2025*'", "cvss_score:>5"},
        ),
        limit: int = Field(
            default=SearchLimits.DEFAULT,
            ge=1,
            le=SearchLimits.MAX_DETECTIONS,
            description="The maximum number of containers to return in this response (default: 10; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return containers.",
        ),
        sort: str | None = Field(
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

        IMPORTANT: You must use the `falcon://cloud/images-vulnerabilities/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for `falcon_search_images_vulnerabilities` tool.
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
