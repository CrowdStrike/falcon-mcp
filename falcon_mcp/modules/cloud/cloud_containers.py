"""Kubernetes containers and image vulnerability tools mixin for the Cloud Security module."""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from falcon_mcp.resources.cloud import (
    IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
    KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
)


class _CloudContainersMixin(_CloudBase):
    """Tools for querying Kubernetes containers and image vulnerabilities."""

    def register_tools(self, server: FastMCP) -> None:
        super().register_tools(server)
        self._add_tool(server=server, method=self.search_kubernetes_containers, name="search_kubernetes_containers")
        self._add_tool(server=server, method=self.count_kubernetes_containers, name="count_kubernetes_containers")
        self._add_tool(server=server, method=self.search_images_vulnerabilities, name="search_images_vulnerabilities")

    def register_resources(self, server: FastMCP) -> None:
        super().register_resources(server)
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://cloud/kubernetes-containers/fql-guide"),
            name="falcon_kubernetes_containers_fql_filter_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools."
            ),
            text=KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
        ))
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://cloud/images-vulnerabilities/fql-guide"),
            name="falcon_images_vulnerabilities_fql_filter_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_images_vulnerabilities` tool."
            ),
            text=IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
        ))

    def search_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://cloud/kubernetes-containers/fql-guide` for syntax.",
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
            description=dedent("""
                Sort kubernetes containers using these options:

                cloud_name: Cloud provider name
                cloud_region: Cloud region name
                cluster_name: Kubernetes cluster name
                container_name: Kubernetes container name
                namespace: Kubernetes namespace name
                last_seen: Timestamp when the container was last seen
                first_seen: Timestamp when the container was first seen
                running_status: Container running status which is either true or false

                Sort either asc (ascending) or desc (descending). Use the dot
                separator ('container_name.desc'), which is supported on every
                Falcon sort endpoint. The pipe form ('container_name|desc') is
                accepted here but rejected by some endpoints, so prefer the dot form.

                When searching containers running vulnerable images, use 'image_vulnerability_count.desc' to get container with most images vulnerabilities.

                Examples: 'container_name.desc', 'last_seen.desc'
            """).strip(),
            examples={"container_name.desc", "last_seen.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for Kubernetes containers in your CrowdStrike container inventory.

        Use this to find containers by cluster, namespace, image, or cloud provider.
        Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter
        expressions. Returns full container details including image, status, and vulnerabilities.
        """
        results, pagination = self._base_search_with_meta(
            operation="ReadContainerCombined",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search Kubernetes containers",
        )
        if self._is_error(results):
            return [results]
        return self._build_pagination_envelope(results or [], pagination, filter)

    def count_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://cloud/kubernetes-containers/fql-guide` for syntax.",
            examples={"cloud:'Azure'", "container_name:'service'"},
        ),
    ) -> int:
        """Count Kubernetes containers matching filter criteria.

        Use this for aggregate counts without returning full container details. Consult
        falcon://cloud/kubernetes-containers/fql-guide before constructing filter
        expressions. Returns the matching container count as an integer.
        """
        params = prepare_api_parameters({"filter": filter})
        operation = "ReadContainerCount"
        response = self.client.command(operation, parameters=params)
        result = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to count Kubernetes containers",
            default_result=0,
        )
        if isinstance(result, list) and result and isinstance(result[0], dict):
            return result[0].get("count") or 0
        return result

    def search_images_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://cloud/images-vulnerabilities/fql-guide` for syntax.",
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
            description=dedent("""
                Sort images vulnerabilities using these options:

                cps_current_rating: CSP rating of the image vulnerability
                cve_id: CVE ID of the image vulnerability
                cvss_score: CVSS score of the image vulnerability
                images_impacted: Number of images impacted by the vulnerability

                Sort either asc (ascending) or desc (descending). Use the dot
                separator ('cvss_score.desc'), which is supported on every Falcon
                sort endpoint. The pipe form ('cvss_score|desc') is accepted here
                but rejected by some endpoints, so prefer the dot form.

                Examples: 'cvss_score.desc', 'cps_current_rating.asc'
            """).strip(),
            examples={"cvss_score.desc", "cps_current_rating.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for container image vulnerabilities in CrowdStrike Image Assessments.

        Use this to find CVEs affecting container images by severity, CVSS score, or
        CVE ID. Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing
        filter expressions. Returns vulnerability details including CVE IDs, scores, and
        impacted image counts.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        result, pagination = self._base_search_with_meta(
            operation="ReadCombinedVulnerabilities",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to perform operation",
        )
        if self._is_error(result):
            return [result]
        return self._build_pagination_envelope(result, pagination, filter)
