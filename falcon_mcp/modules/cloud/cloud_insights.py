"""Cloud Insights tools mixin for the Cloud Security module."""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import Resource, TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from falcon_mcp.resources.cloud_insights import CLOUD_INSIGHTS_FQL_DOCUMENTATION

logger = get_logger(__name__)

_INSIGHT_RULES_FILTER = "rule_domain:'CSPM'+rule_subdomain:'Insight'"


class _CloudInsightsMixin(_CloudBase):
    """Tools for querying cloud security insights."""

    # -------------------------------------------------------------------------
    # Registration
    # -------------------------------------------------------------------------

    def register_tools(self, server: FastMCP) -> None:
        super().register_tools(server)
        self._add_tool(server=server, method=self.search_cloud_insights, name="search_cloud_insights")
        self._add_tool(server=server, method=self.get_cloud_asset_insights, name="get_cloud_asset_insights")
        self._add_tool(server=server, method=self.list_cloud_insight_definitions, name="list_cloud_insight_definitions")

    def register_resources(self, server: FastMCP) -> None:
        super().register_resources(server)
        resource: Resource = TextResource(
            uri=AnyUrl("falcon://cloud/cloud-insights/fql-guide"),
            name="falcon_search_cloud_insights_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the"
                " `falcon_search_cloud_insights` tool."
            ),
            text=CLOUD_INSIGHTS_FQL_DOCUMENTATION,
        )
        self._add_resource(server, resource)

    # -------------------------------------------------------------------------
    # Tools
    # -------------------------------------------------------------------------

    def list_cloud_insight_definitions(
        self,
        categories: list[str] | None = Field(
            default=None,
            description=(
                "Filter to specific categories. Available categories and the topics they cover:\n"
                "  - Identity: MFA status, admin privileges, credential rotation, unused accounts,"
                " excessive permissions, guest users, external identities\n"
                "  - Network: internet exposure, public IPs, access ranges, exposure methods\n"
                "  - Vulnerabilities: reachable CVEs, RCE vulnerabilities, sensor presence\n"
                "  - Data: secrets, sensitive data, encryption at rest, logging, backup, credentials\n"
                "  - AI: LLM model usage, MCP server exposure, public AI service consumption\n"
                "  - Application: third-party vendor compliance, excessive actions, sensitive data sources\n"
                "Case-insensitive. Omit to return all categories."
            ),
        ),
    ) -> list[dict[str, Any]]:
        """Return all available cloud insight definitions, deduplicated by insight_id.

        Each entry represents one unique insight type with aggregated providers,
        resource_types, and (when non-empty) compliance framework controls.

        Call this first whenever you are not certain which insight_id covers the user's
        question. Do not guess insight IDs or reach for other tools before checking
        whether a relevant insight type exists — the definitions catalog is the
        authoritative source for what CSPM tracks as insight facts. If a relevant
        definition is found here, use its insight_id in falcon_search_cloud_insights.
        """
        try:
            definitions = self._get_insight_definitions()
        except RuntimeError as exc:
            return [{"error": "Failed to load insight definitions from Policy Framework API", "detail": str(exc)}]

        resolved_categories = unwrap_field_default(categories)
        if resolved_categories is None:
            return definitions

        lower_cats = {c.lower() for c in resolved_categories}
        return [entry for entry in definitions if entry.get("category", "").lower() in lower_cats]

    def search_cloud_insights(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. Use `insights.id:[...]` to scope by insight ID(s),"
                " combined with value filters and asset attributes."
                " To filter by category, first call `list_cloud_insight_definitions`"
                " to discover the insight_ids for that category, then pass them here."
                " Omit entirely to return all assets that have any insight across all categories"
                " — do NOT call `list_cloud_insight_definitions` first when you want all insights,"
                " just leave this param empty."
                " See `falcon://cloud/cloud-insights/fql-guide` for all supported fields and syntax."
                " Example: insights.id:'publiclyExposedToTheInternet'+insights.boolean_value:true"
            ),
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description=(
                "Maximum number of assets to query (default: 100; max: 500). Each asset"
                " produces exactly one result. Use with `after` for pagination."
            ),
        ),
        after: str | None = Field(
            default=None,
            description=(
                "A pagination token used with the limit parameter to manage pagination of results."
                " On your first request, don't provide an after token. On subsequent requests,"
                " provide the after token from the previous response to continue from that result set."
            ),
        ),
        sort: str | None = Field(
            default=None,
            description=(
                "Sort assets using field.asc or field.desc. Supported fields:"
                " cloud_provider, account_id, account_name, resource_type, region,"
                " creation_time, updated_at. Insight-field sorting is also supported"
                " (e.g. 'publiclyExposedToTheInternet.desc')."
                " Use the dot separator ('updated_at.desc')."
            ),
        ),
    ) -> dict[str, Any]:
        """Search for cloud security insights using FQL.

        Returns asset records — one per asset — each with asset context and a nested
        `insights` array of the insight facts found on that asset.

        To filter by category or specific insight types, first call
        `list_cloud_insight_definitions` to get the insight_ids for the category you
        care about, then pass `insights.id:['id1','id2']` (or a single value
        `insights.id:'id1'`) in the `filter` param. Omit `filter` entirely to
        return all assets that have any insight across all categories — the server
        automatically scopes the query to insight-bearing assets only, so omitting
        filter does NOT return plain asset inventory.

        The `insights` array in each result contains ALL insight entries on that asset.
        Use `falcon_get_cloud_asset_insights` to drill into a specific asset's full
        insight detail including the richer `details{}` map.
        For the top-down correlated risk view use `falcon_search_cloud_risks`.

        Responses include `pagination.total` (total assets matching the filter, or null
        when the API does not report a count). Use `pagination.next` as the `after`
        cursor on the next call to page through results.

        The `rule_id` field in each insight entry is the PFM rule instance ID that
        triggered the insight. The `value` field is polymorphic: boolean, string,
        integer, list of strings, or date/timestamp depending on the insight_id.
        The `category` field is null — use `list_cloud_insight_definitions` if you need
        the category label for a given insight_id.
        Consult falcon://cloud/cloud-insights/fql-guide for filter field details.

        When the user asks for "all" results and `pagination.total` exceeds the count
        returned, continue paginating with the `after` cursor until all pages are
        retrieved before summarising — do not summarise a partial result set.
        """
        resolved_fql = unwrap_field_default(filter)
        resolved_after = unwrap_field_default(after)
        resolved_sort = unwrap_field_default(sort)

        try:
            effective_filter = self._build_insight_filter(resolved_fql)
        except RuntimeError as exc:
            return {
                "error": "Failed to load insight definitions from Policy Framework API",
                "detail": str(exc),
            }

        if effective_filter is None:
            return self._build_pagination_envelope([], None, None)

        raw_ids, pagination = self._base_search_with_meta(
            operation="cloud_security_assets_queries",
            search_params={"filter": effective_filter, "limit": limit, "after": resolved_after, "sort": resolved_sort},
            error_message="Failed to query cloud insights",
        )

        if self._is_error(raw_ids):
            return self._format_fql_error_response(
                [raw_ids],
                effective_filter,
                CLOUD_INSIGHTS_FQL_DOCUMENTATION,
            )

        asset_ids: list[str] = raw_ids  # type: ignore[assignment]
        if not asset_ids:
            return self._build_pagination_envelope([], pagination, None)

        raw_details = self._batch_get_cspm_assets(asset_ids)
        if self._is_error(raw_details):
            return raw_details

        details: list[dict[str, Any]] = self._reorder_by_ids(asset_ids, raw_details, id_field="id")  # type: ignore[arg-type,assignment]
        records = self._group_insights_by_asset(details)

        return self._build_pagination_envelope(records, pagination, None)

    def get_cloud_asset_insights(
        self,
        asset_ids: list[str] = Field(
            description=(
                "One or more cloud ASSET IDs (not insight IDs) to retrieve insights for."
                " These are the `asset_id` values returned by falcon_search_cloud_insights"
                " or the `id` field from falcon_search_cspm_assets."
            ),
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve the full insight detail for one or more cloud ASSET IDs.

        Takes cloud asset IDs (not insight-definition IDs) and returns each asset's
        complete `cloud_context.insights` — both the `external[]` insight instances and
        the richer `details{}` map (per-insight value, context, and calculatedAt) — plus
        asset context. Use this to drill into why an asset is flagged after finding it with
        falcon_search_cloud_insights or falcon_search_cspm_assets. Returns one record per
        requested asset that has insight data.
        """
        raw_details = self._batch_get_cspm_assets(asset_ids)
        if self._is_error(raw_details):
            return [raw_details]  # type: ignore[list-item]

        details: list[dict[str, Any]] = self._reorder_by_ids(asset_ids, raw_details, id_field="id")  # type: ignore[arg-type,assignment]

        records: list[dict[str, Any]] = []
        for asset in details:
            cloud_context = asset.get("cloud_context")
            insights = cloud_context.get("insights") if isinstance(cloud_context, dict) else None
            if not isinstance(insights, dict):
                continue
            records.append({**self._asset_context(asset), "insights": insights})

        return records

    # -------------------------------------------------------------------------
    # Insight definitions helpers
    # -------------------------------------------------------------------------

    def _get_insight_definitions(self) -> list[dict[str, Any]]:
        """Return deduplicated, slimmed insight definition entries.

        Each entry corresponds to one unique insight_id. Multiple rule instances for the
        same insight_id (one per resource_type) are merged: providers and resource_types
        are aggregated; controls are deduplicated; name suffix is stripped.

        Raises:
            RuntimeError: If the API returns an error response.
        """
        rules = self._fetch_pfm_rules(_INSIGHT_RULES_FILTER)
        if not rules:
            return []

        merged: dict[str, dict[str, Any]] = {}
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            insight_id: str = rule.get("insight_id") or ""
            category: str = rule.get("category") or ""
            if not insight_id or not category:
                continue

            if insight_id not in merged:
                merged[insight_id] = {
                    "insight_id": insight_id,
                    "category": category,
                    "name": self._strip_name_suffix(rule.get("name") or ""),
                    "description": rule.get("description") or "",
                    "_providers": set(),
                    "_resource_types": set(),
                    "_control_keys": set(),
                    "controls": [],
                }

            self._merge_rule_into_entry(merged[insight_id], rule)

        return self._finalize_definitions(merged)

    @staticmethod
    def _strip_name_suffix(raw_name: str) -> str:
        return raw_name.split(" - ")[0].strip() if " - " in raw_name else raw_name

    @staticmethod
    def _slim_control(ctrl: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(ctrl, dict):
            return None
        frameworks = ctrl.get("security_framework") or []
        framework = frameworks[0].get("name") if frameworks and isinstance(frameworks[0], dict) else ""
        return {
            "name": ctrl.get("name") or "",
            "framework": framework,
            "section": ctrl.get("section") or "",
            "requirement": ctrl.get("requirement") or "",
        }

    @staticmethod
    def _merge_rule_into_entry(entry: dict[str, Any], rule: dict[str, Any]) -> None:
        provider = rule.get("provider")
        if provider:
            entry["_providers"].add(provider)

        for rt_obj in rule.get("resource_types") or []:
            if isinstance(rt_obj, dict):
                rt = rt_obj.get("resource_type")
                if rt:
                    entry["_resource_types"].add(rt)

        for ctrl in rule.get("controls") or []:
            slimmed = _CloudInsightsMixin._slim_control(ctrl)
            if slimmed is None:
                continue
            key = (slimmed["name"], slimmed["framework"])
            if key not in entry["_control_keys"]:
                entry["_control_keys"].add(key)
                entry["controls"].append(slimmed)

    @staticmethod
    def _finalize_definitions(merged: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        definitions = []
        for entry in merged.values():
            item: dict[str, Any] = {
                "insight_id": entry["insight_id"],
                "category": entry["category"],
                "name": entry["name"],
                "description": entry["description"],
                "providers": sorted(entry["_providers"]),
                "resource_types": sorted(entry["_resource_types"]),
            }
            if entry["controls"]:
                item["controls"] = entry["controls"]
            definitions.append(item)
        return definitions

    # -------------------------------------------------------------------------
    # Search helpers
    # -------------------------------------------------------------------------

    def _build_insight_filter(self, resolved_fql: str | None) -> str | None:
        """Return the effective FQL filter for the asset query.

        When no filter is provided, fetches all known insight IDs from the PFM
        definitions and builds an explicit insights.id:[...] expression. A wildcard
        (insights.id:*'*') is NOT used — the FQL layer only rewrites explicit
        insights.id expressions to query the internal ruleId field; wildcards fall
        through untransformed and miss assets whose .id field is not backfilled.

        Returns a str filter, or None when the definitions are empty (no results).

        Raises:
            RuntimeError: If the PFM API call fails.
        """
        if resolved_fql is not None:
            return resolved_fql

        rules = self._fetch_pfm_rules(_INSIGHT_RULES_FILTER)
        all_ids = sorted({
            r["insight_id"] for r in rules
            if isinstance(r, dict) and r.get("insight_id")
        })
        if not all_ids:
            return None

        quoted = ", ".join(f"'{iid}'" for iid in all_ids)
        return f"insights.id:[{quoted}]"

    @staticmethod
    def _asset_context(asset: dict[str, Any]) -> dict[str, Any]:
        return {
            "asset_id": asset.get("id"),
            "asset_name": asset.get("resource_name"),
            "asset_type": asset.get("resource_type"),
            "cloud_provider": asset.get("cloud_provider"),
            "region": asset.get("region"),
            "account_id": asset.get("account_id"),
            "account_name": asset.get("account_name"),
            "service_category": asset.get("service_category"),
        }

    def _group_insights_by_asset(
        self,
        assets: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Group insight instances by asset, one result per asset.

        Assets with no well-formed insight entries are skipped.
        """
        records: list[dict[str, Any]] = []

        for asset in assets:
            cloud_context = asset.get("cloud_context")
            if not isinstance(cloud_context, dict):
                continue
            insights_block = cloud_context.get("insights")
            if not isinstance(insights_block, dict):
                continue
            external = insights_block.get("external")
            if not isinstance(external, list):
                continue

            asset_insights: list[dict[str, Any]] = []
            for item in external:
                if not isinstance(item, dict):
                    continue
                insight_id_val = item.get("id")
                if not isinstance(insight_id_val, str):
                    continue
                value = next((v for k, v in item.items() if k.endswith("Value")), None)
                asset_insights.append({
                    "insight_id": insight_id_val,
                    "category": None,
                    "value": value,
                    "rule_id": item.get("ruleId"),
                })

            if not asset_insights:
                continue

            records.append({**self._asset_context(asset), "insights": asset_insights})

        return records
