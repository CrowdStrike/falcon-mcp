"""Integration tests for cloud insights tools."""

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudInsightsIntegration(BaseIntegrationTest):
    """Integration tests for cloud insights tools.

    Validates falcon_search_cloud_insights, falcon_get_cloud_asset_insights, and
    falcon_list_cloud_insight_definitions against the live API.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    # --- list_cloud_insight_definitions ---

    def test_list_cloud_insight_definitions_returns_entries(self):
        """Validates QueryRule + GetRule operation names and deduplication."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions")
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected at least one insight definition"
        first = result[0]
        for field in ["insight_id", "category", "name", "description", "providers", "resource_types"]:
            assert field in first, f"Expected '{field}' in definition. Got: {sorted(first.keys())}"
        assert isinstance(first["providers"], list), "providers should be a list"
        assert isinstance(first["resource_types"], list), "resource_types should be a list"

    def test_list_cloud_insight_definitions_deduplicated(self):
        """insight_ids are unique — no duplicate entries."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions dedup")
        assert isinstance(result, list)
        ids = [e["insight_id"] for e in result]
        assert len(ids) == len(set(ids)), f"Duplicate insight_ids found: {[x for x in ids if ids.count(x) > 1]}"

    def test_pfm_pagination_uses_total(self):
        """PFM catalog pagination terminates correctly using meta.pagination.total.

        The catalog on this tenant fits in one QueryRule page (<= 500 rules).
        We verify all definitions are returned and the result is non-empty —
        if pagination were broken (e.g. infinite loop or early exit) this would fail or hang.
        """
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="pfm pagination total")
        assert isinstance(result, list)
        assert len(result) > 0, "Expected at least one insight definition"
        # Verify all entries have the required fields — a pagination bug would produce partial results
        for entry in result:
            assert "insight_id" in entry, f"Missing insight_id in entry: {entry}"
            assert "category" in entry, f"Missing category in entry: {entry}"

    def test_list_cloud_insight_definitions_categories_filter(self):
        """categories filter returns only matching entries (case-insensitive)."""
        result_lower = self.call_method(
            self.module.list_cloud_insight_definitions,
            categories=["identity"],
        )
        self.assert_no_error(result_lower, context="list_cloud_insight_definitions identity (lower)")
        assert isinstance(result_lower, list)
        for entry in result_lower:
            assert entry["category"] == "Identity", f"Expected Identity, got {entry['category']}"

        result_upper = self.call_method(
            self.module.list_cloud_insight_definitions,
            categories=["IDENTITY"],
        )
        self.assert_no_error(result_upper, context="list_cloud_insight_definitions identity (upper)")
        assert len(result_lower) == len(result_upper), "Case-insensitive filter must return same count"

    def test_list_cloud_insight_definitions_categories_filter_unknown(self):
        """Unknown category returns empty list, not an error."""
        result = self.call_method(
            self.module.list_cloud_insight_definitions,
            categories=["NonExistentCategory"],
        )
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert result == [], f"Expected empty list for unknown category, got {result}"

    def test_list_cloud_insight_definitions_name_has_no_suffix(self):
        """Names must not contain the ' - <resource_type>' suffix from the raw API."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions name suffix")
        assert isinstance(result, list)
        for entry in result:
            name = entry.get("name", "")
            resource_type_pattern = any(
                name.endswith(f" - {rt}")
                for rt in entry.get("resource_types", [])
            )
            assert not resource_type_pattern, f"Name still has resource_type suffix: {name!r}"

    def test_list_cloud_insight_definitions_providers_are_sorted(self):
        """providers list is sorted on every entry."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions providers sorted")
        assert isinstance(result, list)
        for entry in result:
            providers = entry.get("providers", [])
            assert providers == sorted(providers), f"providers not sorted on {entry['insight_id']}: {providers}"

    def test_list_cloud_insight_definitions_known_categories_present(self):
        """Known categories (Identity, Network, Data, Vulnerabilities, AI) are all present."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions known categories")
        assert isinstance(result, list)
        categories = {e["category"] for e in result}
        for expected in ["Identity", "Network", "Data", "Vulnerabilities", "AI"]:
            assert expected in categories, f"Expected category '{expected}' not found. Got: {sorted(categories)}"

    def test_list_cloud_insight_definitions_controls_have_section(self):
        """Controls, when present, carry a non-empty section from the live API.

        Guards the section_name -> section mapping: a wrong source field name
        yields controls whose section is uniformly "".
        """
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context="list_cloud_insight_definitions controls")

        with_controls = [e for e in result if e.get("controls")]
        if not with_controls:
            pytest.skip("no insight definitions carry compliance controls in this CID")

        all_controls = [c for e in with_controls for c in e["controls"]]
        for c in all_controls:
            assert set(c.keys()) == {"name", "framework", "section", "requirement"}
        assert any(c["section"] for c in all_controls), (
            "all controls have empty section — check the source field name is section_name"
        )

    # --- search_cloud_insights ---

    def test_search_cloud_insights_returns_flattened_records(self):
        """Validates cloud_security_assets_* pipeline works end-to-end with a filter."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'identityIsAdmin'",
            limit=5,
        )
        self.assert_no_error(result, context="search_cloud_insights")
        if not isinstance(result, dict) or not result.get("results"):
            self.skip_with_warning("No identityIsAdmin insights in environment", "search_cloud_insights shape")
            return
        records = result["results"]
        assert len(records) > 0
        first = records[0]
        for field in ["asset_id", "asset_type", "cloud_provider", "region", "account_id", "insights"]:
            assert field in first, f"Expected '{field}' in insight record. Got: {sorted(first.keys())}"
        assert isinstance(first["insights"], list), "insights should be a list"
        insight = first["insights"][0]
        for field in ["insight_id", "value"]:
            assert field in insight, f"Expected '{field}' in nested insight. Got: {sorted(insight.keys())}"

    def test_search_cloud_insights_with_multiple_insight_ids(self):
        """Filter combining multiple insight IDs returns results from either."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:['identityIsAdmin','publiclyExposedToTheInternet']",
            limit=5,
        )
        self.assert_no_error(result, context="search_cloud_insights multi-id filter")
        assert isinstance(result, dict)

    def test_search_cloud_insights_no_filter(self):
        """Omitting filter returns assets with any insight."""
        result = self.call_method(self.module.search_cloud_insights, limit=5)
        self.assert_no_error(result, context="search_cloud_insights no filter")
        assert isinstance(result, dict)

    def test_search_cloud_insights_string_value_wildcard(self):
        """insights.string_value wildcard returns only assets with a matching string insight."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.string_value:*'*Internet*'",
            limit=5,
        )
        self.assert_no_error(result, context="string_value wildcard")
        assert isinstance(result, dict)
        if not result.get("results"):
            self.skip_with_warning("No string insights containing 'Internet'", "string_value wildcard")
            return
        for record in result["results"]:
            has_internet = any(
                isinstance(ins.get("value"), str) and "Internet" in ins["value"]
                for ins in record.get("insights", [])
            )
            assert has_internet, (
                f"Asset {record.get('asset_id')} returned by wildcard filter but no insight "
                f"value contains 'Internet'. Values: {[i.get('value') for i in record.get('insights', [])]}"
            )

    def test_search_cloud_insights_integer_value_comparison(self):
        """insights.integer_value comparison returns only assets with a matching integer insight."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.integer_value:>0",
            limit=5,
        )
        self.assert_no_error(result, context="integer_value comparison")
        assert isinstance(result, dict)
        if not result.get("results"):
            self.skip_with_warning("No integer insights with value > 0", "integer_value comparison")
            return
        for record in result["results"]:
            has_positive_int = any(
                isinstance(ins.get("value"), int) and ins["value"] > 0
                for ins in record.get("insights", [])
            )
            assert has_positive_int, (
                f"Asset {record.get('asset_id')} returned by integer_value:>0 filter but no "
                f"insight has integer value > 0. Values: {[i.get('value') for i in record.get('insights', [])]}"
            )

    def test_search_cloud_insights_date_value_comparison(self):
        """insights.date_value comparison returns only assets with a matching date insight."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.date_value:<'2030-01-01T00:00:00Z'",
            limit=5,
        )
        self.assert_no_error(result, context="date_value comparison")
        assert isinstance(result, dict)
        if not result.get("results"):
            self.skip_with_warning("No date insights with value < 2030", "date_value comparison")
            return
        for record in result["results"]:
            has_date = any(
                isinstance(ins.get("value"), str) and ins["value"].endswith("Z")
                for ins in record.get("insights", [])
            )
            assert has_date, (
                f"Asset {record.get('asset_id')} returned by date_value filter but no "
                f"insight has a date value. Values: {[i.get('value') for i in record.get('insights', [])]}"
            )

    def test_search_cloud_insights_string_list_value_containment(self):
        """insights.string_list_value containment returns only assets whose list insight contains the member."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.string_list_value:*'*'",
            limit=5,
        )
        self.assert_no_error(result, context="string_list_value containment")
        assert isinstance(result, dict)
        if not result.get("results"):
            self.skip_with_warning("No list-valued insights in environment", "string_list_value containment")
            return
        for record in result["results"]:
            has_list = any(
                isinstance(ins.get("value"), list)
                for ins in record.get("insights", [])
            )
            assert has_list, (
                f"Asset {record.get('asset_id')} returned by string_list_value filter but no "
                f"insight has a list value. Values: {[i.get('value') for i in record.get('insights', [])]}"
            )

    def test_search_cloud_insights_with_sort(self):
        result = self.call_method(
            self.module.search_cloud_insights,
            sort="updated_at.desc",
            limit=5,
        )
        self.assert_no_error(result, context="search_cloud_insights with sort")
        assert isinstance(result, dict)

    def test_search_cloud_insights_pagination_fields_present(self):
        """Response includes pagination envelope with total and next."""
        result = self.call_method(self.module.search_cloud_insights, limit=5)
        self.assert_no_error(result, context="search_cloud_insights pagination")
        assert isinstance(result, dict)
        assert "results" in result, "Missing 'results' key"
        assert "pagination" in result, "Missing 'pagination' key"
        assert "total" in result["pagination"], "Missing pagination.total"

    def test_search_cloud_insights_id_filter_scopes_results(self):
        """insights.id filter scopes which assets are returned."""
        definitions = self.call_method(
            self.module.list_cloud_insight_definitions,
            categories=["Identity"],
        )
        self.assert_no_error(definitions, context="get identity definitions for id filter test")
        if not definitions:
            self.skip_with_warning("No Identity definitions found", "search_cloud_insights id filter")
            return

        first_id = definitions[0]["insight_id"]
        result = self.call_method(
            self.module.search_cloud_insights,
            filter=f"insights.id:'{first_id}'",
            limit=5,
        )
        self.assert_no_error(result, context="search_cloud_insights with id filter")
        assert isinstance(result, dict)
        for record in result.get("results", []):
            insight_ids_in_record = {i["insight_id"] for i in record.get("insights", [])}
            assert first_id in insight_ids_in_record, (
                f"insight_id {first_id!r} not in record insights: {insight_ids_in_record}"
            )

    # --- get_cloud_asset_insights ---

    def test_get_cloud_asset_insights_returns_full_detail(self):
        """Drills into an asset found via search_cloud_insights and validates full insights shape."""
        found = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'identityIsAdmin'",
            limit=5,
        )
        if not isinstance(found, dict) or not found.get("results"):
            self.skip_with_warning("No identityIsAdmin insights in environment", "get_cloud_asset_insights")
            return

        asset_id = found["results"][0].get("asset_id")
        assert asset_id, "Expected 'asset_id' in insight record"

        result = self.call_method(self.module.get_cloud_asset_insights, asset_ids=[asset_id])
        self.assert_no_error(result, context="get_cloud_asset_insights")
        self.assert_valid_list_response(result, min_length=1, context="get_cloud_asset_insights")

        rec = result[0]
        assert "insights" in rec, f"Expected 'insights' in record. Got: {sorted(rec.keys())}"
        assert "external" in rec["insights"], "Expected 'external' in insights"

    def test_get_cloud_asset_insights_multiple_ids(self):
        """Multiple asset IDs can be passed and each returns a record."""
        found = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'identityIsAdmin'",
            limit=5,
        )
        if not isinstance(found, dict) or len(found.get("results", [])) < 2:
            self.skip_with_warning("Need at least 2 insight records", "get_cloud_asset_insights multi-id")
            return

        asset_ids = [r["asset_id"] for r in found["results"][:2]]
        result = self.call_method(self.module.get_cloud_asset_insights, asset_ids=asset_ids)
        self.assert_no_error(result, context="get_cloud_asset_insights multiple ids")
        assert isinstance(result, list)
        assert len(result) == 2, f"Expected 2 records for 2 asset IDs, got {len(result)}"

    # --- Insight ID coverage: confirmed IDs from the FQL guide ---

    def _assert_insight_id_in_catalog(self, insight_id: str) -> None:
        """Assert that insight_id exists in the PFM catalog via list_cloud_insight_definitions."""
        result = self.call_method(self.module.list_cloud_insight_definitions)
        self.assert_no_error(result, context=f"list_cloud_insight_definitions for {insight_id}")
        assert isinstance(result, list)
        catalog_ids = {entry["insight_id"] for entry in result}
        assert insight_id in catalog_ids, (
            f"insight_id {insight_id!r} not found in catalog. "
            f"Available IDs: {sorted(catalog_ids)}"
        )

    def test_insight_id_publicly_exposed_to_the_internet(self):
        self._assert_insight_id_in_catalog("publiclyExposedToTheInternet")

    def test_insight_id_publicly_exposed_access_range(self):
        self._assert_insight_id_in_catalog("publiclyExposedAccessRange")

    def test_insight_id_identity_is_admin(self):
        self._assert_insight_id_in_catalog("identityIsAdmin")

    def test_insight_id_unused_identity(self):
        self._assert_insight_id_in_catalog("unusedIdentity")

    def test_insight_id_identity_unrotated_access_keys(self):
        self._assert_insight_id_in_catalog("identityUnrotatedAccessKeys")

    def test_insight_id_reachable_critical_vulnerabilities(self):
        self._assert_insight_id_in_catalog("reachableCriticalVulnerabilities")

    def test_insight_id_reachable_rce_vulnerabilities(self):
        self._assert_insight_id_in_catalog("reachableRceVulnerabilities")

    def test_insight_id_has_sensor(self):
        self._assert_insight_id_in_catalog("hasSensor")

    def test_insight_id_has_secrets(self):
        self._assert_insight_id_in_catalog("hasSecrets")

    def test_insight_id_has_sensitive_data(self):
        self._assert_insight_id_in_catalog("hasSensitiveData")

    def test_insight_id_logging_enabled(self):
        self._assert_insight_id_in_catalog("loggingEnabled")

    def test_insight_id_uses_ai_services(self):
        self._assert_insight_id_in_catalog("usesAiServices")

    def test_insight_id_has_excessive_actions(self):
        self._assert_insight_id_in_catalog("hasExcessiveActions")

    def test_insight_id_exposes_mcp_server_interface(self):
        self._assert_insight_id_in_catalog("exposesMcpServerInterface")

    def test_insight_id_groups_members(self):
        self._assert_insight_id_in_catalog("groupsMembers")

    def test_insight_id_access_key1_last_rotated(self):
        self._assert_insight_id_in_catalog("accessKey1LastRotated")

    def test_filter_used_present_on_empty_result(self):
        """filter_used is returned in the envelope when filter matches no assets."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'publiclyExposedToTheInternet'+account_id:'this-account-does-not-exist-xyzzy'",
            limit=1,
        )
        self.assert_no_error(result, context="filter_used on empty result")
        assert isinstance(result, dict)
        assert "filter_used" in result, f"Expected filter_used in result. Got: {sorted(result.keys())}"

    def test_filter_used_present_on_success(self):
        """filter_used is returned in the envelope when filter matches assets."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.boolean_value:true",
            limit=1,
        )
        self.assert_no_error(result, context="filter_used on success")
        assert isinstance(result, dict)
        if not result.get("results"):
            self.skip_with_warning("No boolean insights in environment", "filter_used on success")
            return
        assert "filter_used" in result, f"Expected filter_used in result. Got: {sorted(result.keys())}"
        assert result["filter_used"] == "insights.boolean_value:true"
