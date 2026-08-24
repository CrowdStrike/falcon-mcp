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

# The value-bearing keys an insight entry may carry, in the order they are consulted.
# Live data holds exactly one per entry; the explicit tuple keeps the choice
# deterministic instead of depending on dict insertion order, and maps 1:1 onto the
# insights.<type>_value FQL filter fields documented in the FQL guide. The list is closed,
# so _insight_value falls back to any other `*Value` key rather than reporting None for a
# type the API adds later.
_INSIGHT_VALUE_KEYS = (
    "booleanValue",
    "stringValue",
    "integerValue",
    "dateValue",
    "stringListValue",
)

# Default page size for the client-side insight definition catalog. The live catalog is
# ~60 definitions, so the default returns all of them; the cap bounds the response if the
# catalog grows.
_DEFINITIONS_DEFAULT_LIMIT = 200


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
        limit: int = Field(
            default=_DEFINITIONS_DEFAULT_LIMIT,
            ge=1,
            le=500,
            description=(
                f"Maximum number of definitions to return (default: {_DEFINITIONS_DEFAULT_LIMIT};"
                " max: 500). The live catalog is well under the default, so the default"
                " returns every definition. Use with `offset` if `pagination.total`"
                " exceeds what you received."
            ),
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Number of definitions to skip before returning results (default: 0).",
        ),
    ) -> dict[str, Any]:
        """Return all available cloud insight definitions, deduplicated by insight_id.

        Each entry represents one unique insight type with aggregated providers,
        resource_types, and (when non-empty) compliance framework controls. Call this
        first to discover valid insight_ids before filtering with falcon_search_cloud_insights.
        Returns the standard pagination envelope; `pagination.total` is an exact count
        rather than an estimate, because the catalog is assembled and counted locally
        rather than server-paged. When `categories` is supplied it counts the matching
        entries, not the whole catalog.
        """
        # Resolve unset Pydantic Field defaults to avoid leaking FieldInfo objects (issue #384)
        resolved_categories = unwrap_field_default(categories)
        resolved_limit = unwrap_field_default(limit)
        resolved_offset = unwrap_field_default(offset)

        try:
            definitions = self._get_insight_definitions()
        except RuntimeError as exc:
            return {"error": "Failed to load insight definitions from Policy Framework API", "detail": str(exc)}

        if resolved_categories is not None:
            lower_cats = {c.lower() for c in resolved_categories}
            definitions = [
                entry for entry in definitions if entry.get("category", "").lower() in lower_cats
            ]

        page = definitions[resolved_offset : resolved_offset + resolved_limit]
        return self._build_pagination_envelope(
            page,
            {"total": len(definitions), "offset": resolved_offset, "limit": resolved_limit},
        )

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
                "Sort assets using field.asc or field.desc. Asset fields:"
                " cloud_provider, account_id, account_name, resource_type, region,"
                " resource_name, service, creation_time, first_seen, updated_at."
                " Three insight fields are also sortable — publiclyExposedToTheInternet,"
                " publiclyExposedAccessRange, publiclyExposedExposureMethod — but no other"
                " insight ID is; sorting by one returns an error naming the valid fields."
                " Use the dot separator ('updated_at.desc'); the pipe form"
                " ('updated_at|desc') is equivalent here."
            ),
            examples=["updated_at.desc", "resource_name.asc", "publiclyExposedToTheInternet.desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for cloud security insights using FQL.

        Returns asset records — one per asset — each with asset context and a nested
        `insights` array of insight facts. Omit `filter` to return all assets that have
        any insight; pass `insights.id:['id1','id2']` to scope by insight type. Use
        `falcon_get_cloud_asset_insights` for the full per-asset detail. Consult
        falcon://cloud/cloud-insights/fql-guide for filter syntax and field reference.
        Responses include `pagination.total` and `pagination.next` for cursor-based paging.
        """
        # Resolve unset Pydantic Field defaults to avoid leaking FieldInfo objects (issue #384)
        resolved_fql = unwrap_field_default(filter)
        resolved_limit = unwrap_field_default(limit)
        resolved_after = unwrap_field_default(after)
        resolved_sort = unwrap_field_default(sort)

        try:
            effective_filter, auto_insight_count = self._build_insight_filter(resolved_fql)
        except RuntimeError as exc:
            return {
                "error": "Failed to load insight definitions from Policy Framework API",
                "detail": str(exc),
            }

        if effective_filter is None:
            return {
                **self._build_pagination_envelope([], None, None),
                "message": "No insight definitions found in the Policy Framework catalog. The catalog may be empty or unavailable.",
            }

        raw_ids, pagination = self._base_search_with_meta(
            operation="cloud_security_assets_queries",
            search_params={
                "filter": effective_filter,
                "limit": resolved_limit,
                "after": resolved_after,
                "sort": resolved_sort,
            },
            error_message="Failed to query cloud insights",
        )

        if self._is_error(raw_ids):
            # The expanded filter is what the API rejected, so echo it rather than the
            # caller's (possibly absent) one.
            return self._format_fql_error_response(
                [raw_ids],  # type: ignore[list-item]
                effective_filter,
                CLOUD_INSIGHTS_FQL_DOCUMENTATION,
            )

        asset_ids: list[str] = raw_ids  # type: ignore[assignment]
        if not asset_ids:
            return self._auto_filter_note(
                self._build_pagination_envelope([], pagination, resolved_fql),
                resolved_fql,
                auto_insight_count,
            )

        raw_details = self._batch_get_cspm_assets(asset_ids)
        if self._is_error(raw_details):
            return [raw_details]  # type: ignore[list-item]

        details: list[dict[str, Any]] = self._reorder_by_ids(asset_ids, raw_details, id_field="id")  # type: ignore[arg-type,assignment]
        records = self._group_insights_by_asset(details)

        return self._auto_filter_note(
            self._build_pagination_envelope(records, pagination, resolved_fql),
            resolved_fql,
            auto_insight_count,
        )

    @staticmethod
    def _auto_filter_note(
        envelope: dict[str, Any],
        resolved_fql: str | None,
        auto_insight_count: int,
    ) -> dict[str, Any]:
        """Flag that the tool supplied the filter itself, without echoing it.

        `filter_used` stays the caller's filter — `None` when they omitted it. Echoing the
        auto-generated `insights.id:[...]` expression there instead cost ~1.5 KB of every
        no-filter response (one quoted ID per catalog entry) to restate something the
        caller did not ask for, so the fact of auto-scoping is reported as two small keys.
        """
        if resolved_fql is None:
            envelope["auto_filter_applied"] = True
            envelope["auto_filter_insight_count"] = auto_insight_count
        return envelope

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

        `category` and `name` are taken from the first rule seen for an insight_id rather
        than aggregated, because an insight_id maps to exactly one of each — see
        `test_first_rule_wins_for_single_valued_fields`.

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
        """Drop the trailing ``" - <resource type>"`` qualifier from a rule name.

        Splits on the first separator. Every rule name in the catalog carries exactly one,
        so first and last are equivalent today; splitting on the first keeps the insight
        name itself intact if a resource-type qualifier ever contains a separator of its
        own. ``test_name_with_multiple_separators_keeps_leading_segment`` pins the choice.
        """
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
            "section": ctrl.get("section_name") or "",
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

    def _build_insight_filter(self, resolved_fql: str | None) -> tuple[str | None, int]:
        """Return the effective FQL filter for the asset query, and how many IDs it names.

        When no filter is provided, fetches all known insight IDs from the PFM
        definitions and builds an explicit insights.id:[...] expression. A wildcard
        (insights.id:*'*') is NOT used — the FQL layer only rewrites explicit
        insights.id expressions to query the internal ruleId field; wildcards fall
        through untransformed and miss assets whose .id field is not backfilled.

        Returns:
            (filter, auto_insight_count). The count is 0 when the caller supplied the
            filter, and the number of catalog IDs when the filter was generated here.
            The filter is None when the definitions are empty (no results).

        Raises:
            RuntimeError: If the PFM API call fails.
        """
        if resolved_fql is not None:
            return resolved_fql, 0

        rules = self._fetch_pfm_rules(_INSIGHT_RULES_FILTER)
        all_ids = sorted({
            r["insight_id"] for r in rules
            if isinstance(r, dict) and r.get("insight_id")
        })
        if not all_ids:
            return None, 0

        quoted = ", ".join(f"'{iid}'" for iid in all_ids)
        return f"insights.id:[{quoted}]", len(all_ids)

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

    @staticmethod
    def _insight_value(item: dict[str, Any]) -> Any:
        """Read an insight entry's single value, whatever key it arrives under.

        Prefers the known keys in a fixed order so the result never depends on dict
        ordering, then falls back to any other `*Value` key. The fallback matters because
        the known list is closed: without it, a value type the API adds later would read
        as None and the insight would look empty rather than unrecognized.
        """
        for key in _INSIGHT_VALUE_KEYS:
            if key in item:
                return item[key]
        for key, value in item.items():
            if key.endswith("Value"):
                logger.debug("Unrecognized insight value key %r on insight %r", key, item.get("id"))
                return value
        return None

    def _group_insights_by_asset(
        self,
        assets: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Group insight instances by asset, one result per asset.

        Assets with no well-formed insight entries are skipped. Each entry's value is read
        by `_insight_value`, which prefers the known `*Value` keys in a fixed order and
        falls back to any other one.
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
                asset_insights.append({
                    "insight_id": insight_id_val,
                    # Deliberately null: the per-insight category lives in the Policy
                    # Framework catalog, not on the asset record, and resolving it here
                    # would add a PFM round-trip to every search. Call
                    # falcon_list_cloud_insight_definitions to map insight_id -> category.
                    "category": None,
                    "value": self._insight_value(item),
                    "rule_id": item.get("ruleId"),
                })

            if not asset_insights:
                continue

            records.append({**self._asset_context(asset), "insights": asset_insights})

        return records
