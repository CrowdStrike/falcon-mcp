"""
Cloud module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon cloud resources like
Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.cloud import (
    IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
    KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
    SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
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

        self._add_tool(
            server=server,
            method=self.search_cspm_assets,
            name="search_cspm_assets",
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

        cspm_assets_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/cspm-assets/fql-guide"),
            name="falcon_search_cspm_assets_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.",
            text=SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            cspm_assets_fql_resource,
        )

    def search_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://cloud/kubernetes-containers/fql-guide` resource when building this filter parameter.",
            examples={"cloud:'AWS'", "cluster_name:'prod'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=9999,
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
    ) -> list[dict[str, Any]]:
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
            default=10,
            ge=1,
            le=9999,
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
    ) -> list[dict[str, Any]]:
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

    def search_cspm_assets(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://cloud/cspm-assets/fql-guide` resource when building this filter parameter.",
            examples=["cloud_provider:'AWS'", "tag_key:'Environment'+tag_value:'Production'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="The maximum number of assets to return in this response (default: 100; max: 1000). Use with the offset or after parameter to manage pagination of results.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return assets.",
        ),
        after: str | None = Field(
            default=None,
            description="A pagination token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that result set.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent(
                """
                Sort cloud assets using these options:

                cloud_provider: Cloud provider name (AWS, Azure, GCP)
                account_id: Cloud account ID
                account_name: Cloud account name
                resource_type: Resource type (e.g., AWS::EC2::Instance)
                region: Cloud region
                creation_time: When the asset was created
                updated_at: When the asset was last updated

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'updated_at.desc' or 'updated_at|desc'

                Examples: 'updated_at.desc', 'resource_type.asc'
            """
            ).strip(),
            examples=["updated_at.desc", "resource_type.asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for cloud assets in your CrowdStrike CSPM Asset Inventory.

        This tool queries cloud resources (EC2 instances, VPCs, subnets, load balancers, etc.)
        managed by CrowdStrike CSPM. Supports comprehensive FQL filtering including:
        - Cloud provider and resource type filtering
        - Tag-based filtering (AWS/Azure/GCP tags)
        - Security posture (publicly exposed, severity, IOM/IOA counts)
        - Compliance status and benchmarks
        - Temporal filtering (creation time, last updated)

        IMPORTANT: You must use the `falcon://cloud/cspm-assets/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for `falcon_search_cspm_assets` tool.

        Returns FQL syntax guide on error or empty results to help refine queries.
        """
        # Step 1: Query for asset IDs
        asset_ids = self._base_search_api_call(
            operation="cloud_security_assets_queries",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "after": after,
                "sort": sort,
            },
            error_message="Failed to query CSPM assets",
        )

        # Handle search error - return with FQL guide
        if self._is_error(asset_ids):
            return self._format_fql_error_response(
                [asset_ids],
                filter,
                SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
            )

        # Handle empty results - return with FQL guide
        if not asset_ids:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
            )

        # Step 2: Batch fetch full details (API limit: 100 IDs per request)
        details = self._batch_get_cspm_assets(asset_ids)

        if self._is_error(details):
            return [details]

        return details

    def _batch_get_cspm_assets(self, asset_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch CSPM asset details in batches of 100 (API limit).

        The cloud_security_assets_entities_get API endpoint has a strict limit of 100 IDs
        per request (as confirmed by API validation). This helper method splits large ID
        lists into chunks and aggregates the results.

        Args:
            asset_ids: List of asset IDs to fetch

        Returns:
            List of asset details or error dict
        """
        BATCH_SIZE = 100
        all_assets: list[dict[str, Any]] = []

        for i in range(0, len(asset_ids), BATCH_SIZE):
            batch = asset_ids[i : i + BATCH_SIZE]
            result = self._base_get_by_ids(
                operation="cloud_security_assets_entities_get",
                ids=batch,
                id_key="ids",
                use_params=True,  # CRITICAL: GET method requires use_params
            )

            # Fail fast on error
            if self._is_error(result):
                return result

            # Aggregate results
            if isinstance(result, list):
                all_assets.extend(result)

        return all_assets
