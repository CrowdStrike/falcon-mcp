"""
Cloud module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon cloud resources like
Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.cloud import (
    CSPM_IOM_FINDINGS_FQL_DOCUMENTATION,
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

        self._add_tool(
            server=server,
            method=self.search_iom_findings,
            name="search_iom_findings",
        )

        self._add_tool(
            server=server,
            method=self.search_cspm_suppression_rules,
            name="search_cspm_suppression_rules",
        )

        self._add_tool(
            server=server,
            method=self.create_cspm_suppression_rule,
            name="create_cspm_suppression_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_cspm_suppression_rules,
            name="delete_cspm_suppression_rules",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
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

        cspm_assets_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/cspm-assets/fql-guide"),
            name="falcon_search_cspm_assets_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.",
            text=SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
        )

        cspm_iom_findings_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/cspm-iom-findings/fql-guide"),
            name="falcon_search_iom_findings_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.",
            text=CSPM_IOM_FINDINGS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            kubernetes_containers_fql_resource,
        )
        self._add_resource(
            server,
            images_vulnerabilities_fql_resource,
        )

        self._add_resource(
            server,
            cspm_assets_fql_resource,
        )

        self._add_resource(
            server,
            cspm_iom_findings_fql_resource,
        )

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
        """Search for Kubernetes containers in your CrowdStrike container inventory.

        Use this to find containers by cluster, namespace, image, or cloud provider.
        Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter
        expressions. Returns full container details including image, status, and vulnerabilities.
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
            description="FQL filter expression. See `falcon://cloud/kubernetes-containers/fql-guide` for syntax.",
            examples={"cloud:'Azure'", "container_name:'service'"},
        ),
    ) -> int:
        """Count Kubernetes containers matching filter criteria.

        Use this for aggregate counts without returning full container details. Consult
        falcon://cloud/kubernetes-containers/fql-guide before constructing filter
        expressions. Returns the count as a single-element list.
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
        """Search for container image vulnerabilities in CrowdStrike Image Assessments.

        Use this to find CVEs affecting container images by severity, CVSS score, or
        CVE ID. Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing
        filter expressions. Returns vulnerability details including CVE IDs, scores, and
        impacted image counts.
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
            description="FQL filter expression. See `falcon://cloud/cspm-assets/fql-guide` for syntax.",
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
        """Search for cloud assets in your CrowdStrike CSPM inventory.

        Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region,
        resource type, or tags. Consult falcon://cloud/cspm-assets/fql-guide before
        constructing filter expressions. Returns slimmed asset details with security
        posture context (IOM/IOA counts, exposure, severity).
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

        return [self._slim_cspm_asset(asset) for asset in details]

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

    def _slim_cspm_asset(self, asset: dict[str, Any]) -> dict[str, Any]:
        """Strip bloated fields from a CSPM asset record to reduce response size.

        Raw CSPM asset records can be 100+ KB each due to compliance benchmark
        details and raw configuration blobs. This keeps actionable fields and
        security posture data while dropping internal/verbose data.
        """
        KEEP_TOP_LEVEL = {
            "id",
            "arn",
            "resource_id",
            "resource_name",
            "resource_type",
            "resource_type_name",
            "account_id",
            "account_name",
            "region",
            "zone",
            "cloud_provider",
            "service",
            "service_category",
            "active",
            "first_seen",
            "updated_at",
            "creation_time",
            "tags",
            "resource_url",
            "relationships",
        }

        slimmed = {k: v for k, v in asset.items() if k in KEEP_TOP_LEVEL}

        cloud_context = asset.get("cloud_context")
        if isinstance(cloud_context, dict):
            slimmed["cloud_context"] = self._slim_cloud_context(cloud_context)

        return slimmed

    def _slim_cloud_context(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Keep security-relevant summary from cloud_context, strip benchmark bloat."""
        slimmed: dict[str, Any] = {}

        # Scalar fields worth keeping
        for key in (
            "cspm_license",
            "publicly_exposed",
            "managed_by",
            "has_tags",
            "instance_id",
            "instance_state",
            "open_cloud_risks",
            "scan_type",
            "data_classifications",
        ):
            if key in ctx:
                slimmed[key] = ctx[key]

        # Host info (platform, OS, state) — small and useful
        if "host" in ctx:
            slimmed["host"] = ctx["host"]

        # Detections — keep counts/severity, strip rule IDs and benchmark objects
        detections = ctx.get("detections")
        if isinstance(detections, dict):
            slimmed["detections"] = {
                k: detections[k]
                for k in (
                    "iom_counts",
                    "ioa_counts",
                    "severities",
                    "highest_severity",
                    "resource_url",
                )
                if k in detections
            }

        # Insights — keep external boolean flags, drop verbose details
        insights = ctx.get("insights")
        if isinstance(insights, dict):
            external = insights.get("external")
            if external:
                slimmed["insights"] = {"external": external}

        return slimmed

    def search_iom_findings(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression."
                " See `falcon://cloud/cspm-iom-findings/fql-guide` for syntax."
            ),
            examples=["severity:'critical'+status:'open'", "cloud_provider:'aws'+service:'S3'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description=(
                "The maximum number of IOM findings to return (default: 100; max: 1000)."
                " Use with the offset parameter to manage pagination."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return findings.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent(
                """
                Sort IOM findings. Use |asc or |desc suffix to specify direction.

                Common sort fields:
                severity: Finding severity level
                first_detected: When the finding was first detected
                last_detected: When the finding was last seen
                cloud_provider: Cloud provider name
                service: Cloud service name
                status: Finding status

                Examples: 'severity|desc', 'last_detected|desc', 'first_detected|asc'
            """
            ).strip(),
            examples=["severity|desc", "last_detected|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for CSPM Indicators of Misconfiguration (IOM) findings.

        Use this to find cloud misconfigurations by severity, provider, service, or
        suppression state. Consult falcon://cloud/cspm-iom-findings/fql-guide before
        constructing filter expressions. Returns IOM entities with cloud context,
        evaluation details, and resource information.
        """
        # Step 1: Query for IOM IDs
        iom_ids = self._base_search_api_call(
            operation="cspm_evaluations_iom_queries",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query IOM findings",
        )

        # Handle search error - return with FQL guide
        if self._is_error(iom_ids):
            return self._format_fql_error_response(
                [iom_ids],
                filter,
                CSPM_IOM_FINDINGS_FQL_DOCUMENTATION,
            )

        # Handle empty results - return with FQL guide
        if not iom_ids:
            return self._format_fql_error_response(
                [],
                filter,
                CSPM_IOM_FINDINGS_FQL_DOCUMENTATION,
            )

        # Step 2: Fetch full IOM entity details (GET with query params, max 100 per call)
        return self._batch_get_iom_entities(iom_ids)

    def _batch_get_iom_entities(self, iom_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch IOM entity details in batches of 100 (API limit).

        Args:
            iom_ids: List of IOM finding IDs to fetch

        Returns:
            List of IOM entity details or error dict
        """
        BATCH_SIZE = 100
        all_entities: list[dict[str, Any]] = []

        for i in range(0, len(iom_ids), BATCH_SIZE):
            batch = iom_ids[i : i + BATCH_SIZE]
            result = self._base_get_by_ids(
                operation="cspm_evaluations_iom_entities",
                ids=batch,
                id_key="ids",
                use_params=True,
            )

            if self._is_error(result):
                return result

            if isinstance(result, list):
                all_entities.extend(result)

        return all_entities

    def search_cspm_suppression_rules(
        self,
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of suppression rules to return (default: 100; max: 500).",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for CSPM IOM suppression rules.

        Use this to review existing suppressions before creating new ones. Returns
        suppression rule objects including scope, reason, and expiration details.
        Returns an empty list if no rules exist.
        """
        # Step 1: Query suppression rule IDs
        params = prepare_api_parameters({"limit": limit, "offset": offset})
        query_response = self.client.command(
            "QuerySuppressionRules",
            override="GET,/cloud-policies/queries/suppression-rules/v1",
            parameters=params,
        )

        query_result = handle_api_response(
            query_response,
            operation="QuerySuppressionRules",
            error_message="Failed to query suppression rules",
            default_result=[],
        )

        if self._is_error(query_result):
            return query_result

        if not query_result:
            return []

        # Step 2: Fetch suppression rule details
        detail_params = prepare_api_parameters({"ids": query_result})
        detail_response = self.client.command(
            "GetSuppressionRules",
            override="GET,/cloud-policies/entities/suppression-rules/v1",
            parameters=detail_params,
        )

        return handle_api_response(
            detail_response,
            operation="GetSuppressionRules",
            error_message="Failed to get suppression rule details",
            default_result=[],
        )

    def create_cspm_suppression_rule(
        self,
        name: str = Field(
            description="Name for the suppression rule. Should be descriptive.",
            examples=["Suppress S3 public access for dev accounts"],
        ),
        suppression_reason: str = Field(
            description=(
                "Reason for suppression. Required."
                " Values: 'accept-risk', 'compensating-control', 'false-positive'."
            ),
            examples=["accept-risk", "compensating-control", "false-positive"],
        ),
        rule_ids: list[str] | None = Field(
            default=None,
            description=(
                "Specific rule IDs to suppress."
                " If not provided, use rule_severities or rule_names to scope."
            ),
        ),
        rule_names: list[str] | None = Field(
            default=None,
            description="Rule names to suppress (supports wildcards).",
        ),
        rule_severities: list[str] | None = Field(
            default=None,
            description=(
                "Rule severities to suppress."
                " Values: 'critical', 'high', 'medium', 'low', 'informational'."
            ),
        ),
        cloud_providers: list[str] | None = Field(
            default=None,
            description=(
                "Limit suppression to specific cloud providers. Values: 'aws', 'azure', 'gcp'."
            ),
        ),
        account_ids: list[str] | None = Field(
            default=None,
            description="Limit suppression to specific cloud account IDs.",
        ),
        regions: list[str] | None = Field(
            default=None,
            description=(
                "Limit suppression to specific cloud regions. Ex: ['us-east-1', 'eu-west-1']."
            ),
        ),
        resource_ids: list[str] | None = Field(
            default=None,
            description="Limit suppression to specific resource IDs.",
        ),
        resource_types: list[str] | None = Field(
            default=None,
            description=("Limit suppression to specific resource types. Ex: ['AWS::S3::Bucket']."),
        ),
        expiration_date: str | None = Field(
            default=None,
            description=(
                "Optional expiration date in RFC 3339 format"
                " (e.g., '2025-12-31T23:59:59Z')."
                " WARNING: Omitting this creates a PERMANENT suppression."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a CSPM IOM suppression rule to hide matching findings.

        Suppressed findings are still assessed but not surfaced in compliance scores.
        Requires at least one rule selection (rule_ids, rule_names, or rule_severities)
        and a suppression reason. Setting an expiration_date is strongly recommended to
        avoid permanent suppressions. Returns the created suppression rule object.
        """
        valid_reasons = {"accept-risk", "compensating-control", "false-positive"}
        if suppression_reason not in valid_reasons:
            return {
                "error": f"Invalid suppression_reason: '{suppression_reason}'",
                "details": f"Must be one of: {', '.join(sorted(valid_reasons))}",
            }

        # Build rule selection filter
        rule_filter: dict[str, Any] = {}
        if rule_ids:
            rule_filter["rule_ids"] = rule_ids
        if rule_names:
            rule_filter["rule_names"] = rule_names
        if rule_severities:
            rule_filter["rule_severities"] = rule_severities
        if not rule_filter:
            return {
                "error": "At least one rule selection parameter is required",
                "details": "Provide rule_ids, rule_names, or rule_severities to scope the suppression.",
            }

        # Build asset scope filter
        asset_filter: dict[str, Any] = {}
        if cloud_providers:
            asset_filter["cloud_providers"] = cloud_providers
        if account_ids:
            asset_filter["account_ids"] = account_ids
        if regions:
            asset_filter["regions"] = regions
        if resource_ids:
            asset_filter["resource_ids"] = resource_ids
        if resource_types:
            asset_filter["resource_types"] = resource_types

        # Build the flat suppression rule body
        body: dict[str, Any] = {
            "name": name,
            "domain": "CSPM",
            "subdomain": "IOM",
            "suppression_reason": suppression_reason,
            "rule_selection_type": "rule_selection_filter",
            "rule_selection_filter": rule_filter,
            "scope_type": "asset_filter" if asset_filter else "all_assets",
        }

        if asset_filter:
            body["scope_asset_filter"] = asset_filter

        if expiration_date:
            body["suppression_expiration_date"] = expiration_date

        response = self.client.command(
            "CreateSuppressionRule",
            override="POST,/cloud-policies/entities/suppression-rules/v1",
            body=body,
        )

        create_result = handle_api_response(
            response,
            operation="CreateSuppressionRule",
            error_message="Failed to create suppression rule",
            default_result=[],
        )

        if self._is_error(create_result):
            return create_result

        if not create_result:
            return []

        # API returns list of created rule IDs — fetch full details
        detail_params = prepare_api_parameters({"ids": create_result})
        detail_response = self.client.command(
            "GetSuppressionRules",
            override="GET,/cloud-policies/entities/suppression-rules/v1",
            parameters=detail_params,
        )

        return handle_api_response(
            detail_response,
            operation="GetSuppressionRules",
            error_message="Failed to get created suppression rule details",
            default_result=[],
        )

    def delete_cspm_suppression_rules(
        self,
        ids: list[str] = Field(
            description=(
                "List of suppression rule IDs to delete."
                " Use falcon_search_cspm_suppression_rules to find rule IDs."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete CSPM IOM suppression rules by ID.

        Deleting a suppression rule re-activates all findings that were previously
        suppressed by it. Use falcon_search_cspm_suppression_rules to find rule IDs
        first. Returns a confirmation response.
        """
        params = prepare_api_parameters({"ids": ids})
        response = self.client.command(
            "DeleteSuppressionRules",
            override="DELETE,/cloud-policies/entities/suppression-rules/v1",
            parameters=params,
        )

        return handle_api_response(
            response,
            operation="DeleteSuppressionRules",
            error_message="Failed to delete suppression rules",
            default_result=[],
        )
