"""Cloud risks and cloud groups tools mixin for the Cloud Security module."""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from falcon_mcp.resources.cloud import CLOUD_RISKS_FQL_DOCUMENTATION


class _CloudRisksMixin(_CloudBase):
    """Tools for querying cloud risks and cloud groups."""

    def register_tools(self, server: FastMCP) -> None:
        super().register_tools(server)
        self._add_tool(server=server, method=self.search_cloud_risks, name="search_cloud_risks")
        self._add_tool(server=server, method=self.search_cloud_groups, name="search_cloud_groups")
        self._add_tool(server=server, method=self.get_cloud_groups, name="get_cloud_groups")

    def register_resources(self, server: FastMCP) -> None:
        super().register_resources(server)
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://cloud/cloud-risks/fql-guide"),
            name="falcon_search_cloud_risks_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_cloud_risks` tool.",
            text=CLOUD_RISKS_FQL_DOCUMENTATION,
        ))

    def search_cloud_risks(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://cloud/cloud-risks/fql-guide` for syntax.",
            examples=[
                "severity:'Critical'+status:'Open'",
                "cloud_provider:'aws'+groups.environment:'production'",
            ],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of risks to return (default: 100; max: 1000). Use with offset for pagination.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return results.",
        ),
        sort: str | None = Field(
            default=None,
            description=(
                "Sort risks using field.asc or field.desc syntax. Prefer the dot "
                "separator, supported on every Falcon sort endpoint.\n\n"
                "Supported fields: account_id, account_name, asset_id, asset_name, "
                "asset_region, asset_type, cloud_provider, first_seen, last_seen, "
                "resolved_at, rule_name, service_category, severity, status\n\n"
                "Examples: 'severity.desc', 'first_seen.desc', 'account_name.asc'"
            ),
            examples=["severity.desc", "first_seen.desc", "account_name.asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for cloud risks in your CrowdStrike environment.

        Use this to find risks by severity, status, cloud provider, account, asset, rule,
        or threat actor. Cloud risks aggregate IOM and IOA findings into per-asset risk
        records and include threat intelligence attribution. For individual compliance rule
        violations on specific resources, use falcon_search_iom_findings instead.

        For the underlying per-asset security facts that risks are computed from, use
        falcon_search_cloud_insights instead — that covers all insight categories:
        Identity (MFA status, admin privileges, credential rotation, unused accounts),
        Network (internet exposure, public IPs, access ranges),
        Vulnerabilities (reachable CVEs, RCE, sensor presence),
        Data (secrets, sensitive data, encryption, logging),
        AI (LLM model usage, MCP server exposure),
        Application (third-party vendor compliance, excessive permissions).

        Consult falcon://cloud/cloud-risks/fql-guide before constructing filter expressions.
        Returns full risk details including severity, lifecycle status, asset context, and
        threat intelligence attribution.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        results, pagination = self._base_search_with_meta(
            operation="combined_cloud_risks",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search cloud risks",
        )

        if self._is_error(results):
            return [results]

        return self._build_pagination_envelope(results, pagination, filter)

    def search_cloud_groups(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. Supports group properties: name, description, "
                "created_at, updated_at. Selector properties: cloud_provider, account_id, "
                "region. Group tags: business_unit, business_impact, environment.\n\n"
                "Examples: \"name:'prod-group'\", \"environment:'production'\""
            ),
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of cloud groups to return (default: 100).",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort groups. Default: name.asc. Prefer the dot separator, supported on every Falcon sort endpoint. Examples: 'name.asc', 'created_at.desc'",
            examples=["name.asc", "created_at.desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List cloud groups in your CrowdStrike environment.

        Use this to discover available cloud groups before filtering risks by
        `cloud_group` or `groups.*` FQL fields in `falcon_search_cloud_risks`.
        Returns full group details including name, selectors, and tags.
        """
        results, pagination = self._base_search_with_meta(
            operation="ListCloudGroupsExternal",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search cloud groups",
        )

        if self._is_error(results):
            return [results]

        return self._build_pagination_envelope(results, pagination, filter)

    def get_cloud_groups(
        self,
        ids: list[str] = Field(
            description="One or more cloud group IDs to retrieve. Find IDs with falcon_search_cloud_groups.",
        ),
    ) -> list[dict[str, Any]]:
        """Get detailed information for cloud groups by ID.

        Use when you already have specific cloud group IDs — for example, the `cloud_groups`
        field returned by `falcon_search_cloud_risks`. Returns full group details including
        name, selectors, business impact, and environment tags.
        """
        params = prepare_api_parameters({"ids": ids})
        response = self.client.command("ListCloudGroupsByIDExternal", parameters=params)
        return handle_api_response(
            response,
            operation="ListCloudGroupsByIDExternal",
            error_message="Failed to get cloud groups",
            default_result=[],
        )
