"""CSPM asset inventory tools mixin for the Cloud Security module."""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from falcon_mcp.resources.cloud import SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION


class _CloudAssetsMixin(_CloudBase):
    """Tools for querying CSPM cloud asset inventory."""

    def register_tools(self, server: FastMCP) -> None:
        super().register_tools(server)
        self._add_tool(server=server, method=self.search_cspm_assets, name="search_cspm_assets")

    def register_resources(self, server: FastMCP) -> None:
        super().register_resources(server)
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://cloud/cspm-assets/fql-guide"),
            name="falcon_search_cspm_assets_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_cspm_assets` tool."
            ),
            text=SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
        ))

    def search_cspm_assets(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://cloud/cspm-assets/fql-guide` for syntax.",
            examples=["cloud_provider:'aws'", "tag_key:'Environment'+tag_value:'Production'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="The maximum number of assets to return in this response (default: 100; max: 1000). Use with the after parameter to manage pagination of results.",
        ),
        after: str | None = Field(
            default=None,
            description="A pagination token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that result set.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort cloud assets using these options:

                cloud_provider: Cloud provider name (aws, azure, gcp)
                account_id: Cloud account ID
                account_name: Cloud account name
                resource_type: Resource type (e.g., AWS::EC2::Instance)
                resource_name: Resource name
                region: Cloud region
                service: Cloud service the resource belongs to
                creation_time: When the asset was created
                first_seen: When the asset was first observed
                updated_at: When the asset was last updated

                Sort either asc (ascending) or desc (descending), lowercase. Use the
                dot separator ('updated_at.desc'), which is supported on every Falcon
                sort endpoint. The pipe form ('updated_at|desc') is equivalent here,
                but rejected by some endpoints, so prefer the dot form.

                Examples: 'updated_at.desc', 'resource_type.asc'
            """).strip(),
            examples=["updated_at.desc", "resource_type.asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for cloud assets in your CrowdStrike CSPM inventory.

        Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region,
        resource type, or tags. Consult falcon://cloud/cspm-assets/fql-guide before
        constructing filter expressions. Returns slimmed asset details with security
        posture context (IOM/IOA counts, exposure, severity).
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions. For cursor-based paging, use `pagination.next` as the `after` parameter on the next call.
        """
        asset_ids, pagination = self._base_search_with_meta(
            operation="cloud_security_assets_queries",
            search_params={"filter": filter, "limit": limit, "after": after, "sort": sort},
            error_message="Failed to query CSPM assets",
        )

        if self._is_error(asset_ids):
            return self._format_fql_error_response(
                [asset_ids],
                filter,
                SEARCH_CSPM_ASSETS_FQL_DOCUMENTATION,
            )

        if not asset_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._batch_get_cspm_assets(asset_ids)

        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(asset_ids, details, id_field="id")

        return self._build_pagination_envelope(
            [self._slim_cspm_asset(asset) for asset in details], pagination, filter
        )

    def _slim_cspm_asset(self, asset: dict[str, Any]) -> dict[str, Any]:
        """Strip bloated fields from a CSPM asset record to reduce response size.

        Raw CSPM asset records can be 100+ KB each due to compliance benchmark
        details and raw configuration blobs. This keeps actionable fields and
        security posture data while dropping internal/verbose data.
        """
        KEEP_TOP_LEVEL = {
            "id", "arn", "resource_id", "resource_name", "resource_type",
            "resource_type_name", "account_id", "account_name", "region", "zone",
            "cloud_provider", "service", "service_category", "active", "first_seen",
            "updated_at", "creation_time", "tags", "resource_url", "relationships",
        }

        slimmed = {k: v for k, v in asset.items() if k in KEEP_TOP_LEVEL}

        cloud_context = asset.get("cloud_context")
        if isinstance(cloud_context, dict):
            slimmed["cloud_context"] = self._slim_cloud_context(cloud_context)

        return slimmed

    def _slim_cloud_context(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Keep security-relevant summary from cloud_context, strip benchmark bloat."""
        slimmed: dict[str, Any] = {}

        for key in (
            "cspm_license", "publicly_exposed", "managed_by", "has_tags",
            "instance_id", "instance_state", "open_cloud_risks", "scan_type",
            "data_classifications",
        ):
            if key in ctx:
                slimmed[key] = ctx[key]

        if "host" in ctx:
            slimmed["host"] = ctx["host"]

        detections = ctx.get("detections")
        if isinstance(detections, dict):
            slimmed["detections"] = {
                k: detections[k]
                for k in ("iom_counts", "ioa_counts", "severities", "highest_severity", "resource_url")
                if k in detections
            }

        insights = ctx.get("insights")
        if isinstance(insights, dict):
            external = insights.get("external")
            if external:
                slimmed["insights"] = {"external": external}

        return slimmed
