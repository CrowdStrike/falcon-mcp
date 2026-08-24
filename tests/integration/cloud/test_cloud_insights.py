"""Integration tests for cloud insights tools."""

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

# The three insight fields the API accepts as sort keys. Sorting by any other insight ID
# is rejected with a 400 that enumerates this exact set, so it is a closed list, not a
# sample. Validated live: `identityIsAdmin.desc` returns 400.
SORTABLE_INSIGHT_FIELDS = [
    "publiclyExposedAccessRange",
    "publiclyExposedExposureMethod",
    "publiclyExposedToTheInternet",
]


@pytest.mark.integration
class TestCloudInsightsIntegration(BaseIntegrationTest):
    """Integration tests for cloud insights tools.

    Validates falcon_search_cloud_insights, falcon_get_cloud_asset_insights, and
    falcon_list_cloud_insight_definitions against the live API.

    A note on skips. `cloud_security_assets_queries` rejects an unknown filter field or
    an invalid sort key with a 400 that enumerates the valid set, but it answers an
    unknown *value* with an empty HTTP 200. So a filter test that tolerates zero rows
    cannot distinguish "the documented operator does not work" from "this tenant has no
    such data". Every operator test below therefore establishes a positive control from
    real data first and fails on zero rows; the only tests that skip are the ones that
    first *prove* the tenant holds no data of the relevant type.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    # ------------------------------------------------------------------
    # Fixtures discovered from live data
    # ------------------------------------------------------------------

    def definitions(self, **kwargs):
        """Return the definition entries from the pagination envelope."""
        result = self.call_method(self.module.list_cloud_insight_definitions, **kwargs)
        self.assert_no_error(result, context="list_cloud_insight_definitions")
        assert isinstance(result, dict), f"Expected the pagination envelope, got {type(result)}"
        assert "pagination" in result, f"Missing pagination. Got: {sorted(result)}"
        return result["results"]

    def search(self, **kwargs):
        """Call search_cloud_insights and assert the call itself succeeded."""
        result = self.call_method(self.module.search_cloud_insights, **kwargs)
        self.assert_no_error(result, context=f"search_cloud_insights {kwargs}")
        assert isinstance(result, dict), f"Expected the pagination envelope, got {type(result)}"
        return result

    def _sample_insight_entries(self, limit=100):
        """Return every (insight_id, value) pair from a sample of assets carrying insights.

        Discovered without any `insights.*` value filter, so it is independent of the
        filters these tests verify. A fixture found *with* the filter under test would
        make a broken filter skip the test instead of failing it.
        """
        records = self.search(limit=limit)["results"]
        return [
            (entry.get("insight_id"), entry.get("value"))
            for record in records
            for entry in record.get("insights", [])
        ]

    def _a_value_of_type(self, value_type, limit=100):
        """Return one (insight_id, value) pair whose value has the given Python type.

        Returns None when the tenant holds no insight of that type at all, which is the
        only legitimate reason for an operator test to skip.
        """
        for insight_id, value in self._sample_insight_entries(limit=limit):
            if value_type is int:
                # bool is a subclass of int; an integer insight is not a boolean one.
                if isinstance(value, int) and not isinstance(value, bool):
                    return insight_id, value
            elif isinstance(value, value_type):
                if value_type is list and not value:
                    continue  # an empty list gives us no member to filter on
                return insight_id, value
        return None

    # ------------------------------------------------------------------
    # list_cloud_insight_definitions
    # ------------------------------------------------------------------

    def test_list_cloud_insight_definitions_returns_entries(self):
        """Validates QueryRule + GetRule operation names and deduplication."""
        entries = self.definitions()
        assert len(entries) > 0, "Expected at least one insight definition"
        first = entries[0]
        for field in ["insight_id", "category", "name", "description", "providers", "resource_types"]:
            assert field in first, f"Expected '{field}' in definition. Got: {sorted(first.keys())}"
        assert isinstance(first["providers"], list), "providers should be a list"
        assert isinstance(first["resource_types"], list), "resource_types should be a list"

    def test_list_cloud_insight_definitions_deduplicated(self):
        """insight_ids are unique — no duplicate entries."""
        entries = self.definitions()
        ids = [e["insight_id"] for e in entries]
        assert len(ids) == len(set(ids)), (
            f"Duplicate insight_ids found: {sorted({x for x in ids if ids.count(x) > 1})}"
        )

    def test_pfm_catalog_pagination_is_complete(self):
        """The catalog walk returns every rule the API reports, with no gaps or repeats.

        `pagination.total` here is the exact size of the locally assembled catalog, so
        comparing it against the page contents proves the QueryRule/GetRule walk did not
        stop early. The tenant's catalog fits one QueryRule page today; a truncating walk
        would show up as a total that disagrees with the entries, or as missing categories.
        """
        result = self.call_method(self.module.list_cloud_insight_definitions, limit=500)
        self.assert_no_error(result, context="pfm catalog pagination")
        entries = result["results"]

        assert entries, "Expected at least one insight definition"
        assert result["pagination"]["total"] == len(entries), (
            f"pagination.total {result['pagination']['total']} disagrees with "
            f"{len(entries)} returned entries — the catalog walk is truncating or "
            "double-counting."
        )
        for entry in entries:
            assert entry.get("insight_id"), f"Missing insight_id in entry: {entry}"
            assert entry.get("category"), f"Missing category in entry: {entry}"

    def test_definitions_pagination_covers_catalog_without_overlap(self):
        """Walking the catalog with limit/offset yields each entry exactly once."""
        total = self.call_method(self.module.list_cloud_insight_definitions, limit=1)["pagination"]["total"]
        assert total > 2, f"Need more than 2 definitions to test paging, tenant has {total}"

        page_size = max(2, total // 3)
        seen = []
        offset = 0
        while offset < total:
            page = self.definitions(limit=page_size, offset=offset)
            assert page, f"Empty page at offset {offset} while total is {total}"
            seen.extend(e["insight_id"] for e in page)
            offset += len(page)

        assert len(seen) == total, f"Paged walk saw {len(seen)} entries, total says {total}"
        assert len(set(seen)) == total, "Paged walk returned an entry more than once"

    def test_definitions_categories_filter(self):
        """categories filter returns only matching entries (case-insensitive)."""
        lower = self.definitions(categories=["identity"])
        assert lower, "Expected at least one Identity definition"
        for entry in lower:
            assert entry["category"] == "Identity", f"Expected Identity, got {entry['category']}"

        upper = self.definitions(categories=["IDENTITY"])
        assert len(lower) == len(upper), "Case-insensitive filter must return same count"

    def test_definitions_categories_filter_unknown(self):
        """Unknown category returns an empty page, not an error."""
        result = self.call_method(
            self.module.list_cloud_insight_definitions,
            categories=["NonExistentCategory"],
        )
        self.assert_no_error(result, context="unknown category")
        assert result["results"] == [], f"Expected no entries, got {result['results']}"
        assert result["pagination"]["total"] == 0, "total must reflect the filtered catalog"

    def test_definitions_name_has_no_suffix(self):
        """Names must not contain the ' - <resource_type>' suffix from the raw API."""
        for entry in self.definitions():
            name = entry.get("name", "")
            assert not any(
                name.endswith(f" - {rt}") for rt in entry.get("resource_types", [])
            ), f"Name still has resource_type suffix: {name!r}"

    def test_definitions_providers_are_sorted(self):
        """providers list is sorted on every entry."""
        for entry in self.definitions():
            providers = entry.get("providers", [])
            assert providers == sorted(providers), (
                f"providers not sorted on {entry['insight_id']}: {providers}"
            )

    def test_definitions_known_categories_present(self):
        """The six documented categories are all present in the live catalog.

        The `categories` param description enumerates these, so a category that
        disappears from the API silently makes that documentation wrong.
        """
        categories = {e["category"] for e in self.definitions()}
        for expected in ["Identity", "Network", "Data", "Vulnerabilities", "AI", "Application"]:
            assert expected in categories, (
                f"Expected category '{expected}' not found. Got: {sorted(categories)}"
            )

    def test_definitions_have_exactly_one_category_each(self):
        """Each insight_id maps to a single category.

        _get_insight_definitions takes category from the first rule it sees for an
        insight_id rather than aggregating. That is only correct while this holds, so
        assert it against live data instead of assuming it.
        """
        entries = self.definitions()
        by_id = {}
        for entry in entries:
            by_id.setdefault(entry["insight_id"], set()).add(entry["category"])
        multi = {k: v for k, v in by_id.items() if len(v) > 1}
        assert not multi, (
            f"insight_ids carrying more than one category: {multi}. "
            "_get_insight_definitions must start aggregating category if this is now real."
        )

    def test_definitions_controls_have_section(self):
        """Controls, when present, carry a non-empty section from the live API.

        Guards the section_name -> section mapping: a wrong source field name
        yields controls whose section is uniformly "".
        """
        with_controls = [e for e in self.definitions() if e.get("controls")]
        if not with_controls:
            pytest.skip("no insight definitions carry compliance controls in this CID")

        all_controls = [c for e in with_controls for c in e["controls"]]
        for c in all_controls:
            assert set(c.keys()) == {"name", "framework", "section", "requirement"}
        assert any(c["section"] for c in all_controls), (
            "all controls have empty section — check the source field name is section_name"
        )

    # ------------------------------------------------------------------
    # search_cloud_insights — shape
    # ------------------------------------------------------------------

    def test_search_cloud_insights_returns_flattened_records(self):
        """Validates the cloud_security_assets_* pipeline end to end with a filter."""
        records = self.assert_filter_matches(
            self.module.search_cloud_insights,
            "insights.id:'identityIsAdmin'",
            note="identityIsAdmin is in the live catalog and is the most widely held insight.",
        )["results"]

        first = records[0]
        for field in ["asset_id", "asset_type", "cloud_provider", "region", "account_id", "insights"]:
            assert field in first, f"Expected '{field}' in insight record. Got: {sorted(first.keys())}"
        assert isinstance(first["insights"], list), "insights should be a list"
        for field in ["insight_id", "value", "rule_id", "category"]:
            assert field in first["insights"][0], (
                f"Expected '{field}' in nested insight. Got: {sorted(first['insights'][0].keys())}"
            )

    def test_search_cloud_insights_with_multiple_insight_ids(self):
        """A list-valued insights.id filter returns records carrying one of the listed IDs."""
        wanted = {"identityIsAdmin", "publiclyExposedToTheInternet"}
        self.assert_filter_matches(
            self.module.search_cloud_insights,
            "insights.id:['identityIsAdmin','publiclyExposedToTheInternet']",
            predicate=lambda record: wanted & {
                entry["insight_id"] for entry in record.get("insights", [])
            },
            predicate_desc="record carries identityIsAdmin or publiclyExposedToTheInternet",
        )

    def test_search_cloud_insights_no_filter_scopes_to_assets_with_insights(self):
        """Omitting filter returns only assets that actually carry an insight.

        The tool substitutes an explicit insights.id:[...] over the whole catalog. If that
        substitution broke, this would come back with assets that have no insights (or
        with nothing at all), which is exactly what the auto-scoping exists to prevent.
        """
        result = self.search(limit=5)
        records = result["results"]
        assert records, (
            "No-filter search returned nothing. Either the catalog lookup failed or the "
            "auto-generated insights.id:[...] filter no longer matches."
        )
        for record in records:
            assert record.get("insights"), (
                f"Asset {record.get('asset_id')} has no insights but was returned by the "
                "auto-scoped query."
            )

        assert result["auto_filter_applied"] is True
        assert result["auto_filter_insight_count"] > 0
        assert "filter_used" not in result, (
            "The caller supplied no filter, so the generated expression must not be "
            f"echoed back as filter_used. Got: {result.get('filter_used')!r}"
        )

    def test_search_cloud_insights_pagination_fields_present(self):
        """Response includes the pagination envelope with a real total."""
        result = self.search(limit=5)
        assert "results" in result, "Missing 'results' key"
        assert "pagination" in result, "Missing 'pagination' key"
        total = result["pagination"]["total"]
        assert isinstance(total, int) and total > 0, (
            f"Expected a positive pagination.total from cloud_security_assets_queries, got {total!r}"
        )

    def test_search_cloud_insights_id_filter_scopes_results(self):
        """An insights.id filter returns only assets carrying that insight."""
        identity_defs = self.definitions(categories=["Identity"])
        assert identity_defs, "Expected at least one Identity definition in the catalog"

        # Pick an Identity insight that this tenant actually has assets for, so the
        # assertion below runs against real rows rather than passing on an empty loop.
        for definition in identity_defs:
            insight_id = definition["insight_id"]
            if self.search(filter=f"insights.id:'{insight_id}'", limit=1)["results"]:
                break
        else:
            self.skip_with_warning(
                f"tenant has no assets for any of the {len(identity_defs)} Identity insights",
                context="insights.id scoping",
            )
            return

        self.assert_filter_matches(
            self.module.search_cloud_insights,
            f"insights.id:'{insight_id}'",
            predicate=lambda record: insight_id in {
                entry["insight_id"] for entry in record.get("insights", [])
            },
            predicate_desc=f"record carries insight {insight_id}",
        )

    def test_search_cloud_insights_unknown_filter_field_is_a_loud_error(self):
        """An unknown filter field 400s rather than returning an empty 200.

        This is why the other filter tests can treat zero rows as a failure: the API
        distinguishes a bad field from a value that matches nothing. If it ever starts
        answering unknown fields with an empty 200, this test tells us the rest of the
        suite has gone blind.
        """
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.no_such_field:true",
            limit=1,
        )
        assert isinstance(result, dict), f"Expected the FQL-error dict, got {type(result)}"
        assert result.get("fql_guide"), (
            f"Expected an FQL error response carrying the guide. Got: {sorted(result)}"
        )

    # ------------------------------------------------------------------
    # search_cloud_insights — the documented value filters
    #
    # Each test discovers a real value first, filters on it, and verifies every returned
    # record. Zero rows is a failure, not a skip.
    # ------------------------------------------------------------------

    def test_boolean_value_filter(self):
        """insights.boolean_value selects assets carrying a boolean insight."""
        self.assert_filter_matches(
            self.module.search_cloud_insights,
            "insights.id:'identityIsAdmin'+insights.boolean_value:true",
            predicate=lambda record: any(
                isinstance(entry.get("value"), bool) for entry in record.get("insights", [])
            ),
            predicate_desc="record carries at least one boolean-valued insight",
        )

    def test_string_value_exact_and_wildcard(self):
        """insights.string_value matches exactly, and with the :*'*val*' wildcard.

        The trailing-only form ('val*') and the ~ operator are both unsupported on this
        endpoint, so the guide documents :*'*val*' — asserted here in both directions.
        """
        found = self._a_value_of_type(str)
        if found is None:
            self.skip_with_warning(
                "tenant holds no string-valued insight in the sampled assets",
                context="string_value filter",
            )
            return
        insight_id, value = found

        self.assert_filter_matches(
            self.module.search_cloud_insights,
            f"insights.id:'{insight_id}'+insights.string_value:'{value}'",
            predicate=lambda record: any(
                entry.get("value") == value for entry in record.get("insights", [])
            ),
            predicate_desc=f"record carries the exact string value {value!r}",
            note=f"{insight_id} was observed carrying {value!r} on a live asset.",
        )

        fragment = value[: max(3, len(value) // 2)]
        self.assert_filter_matches(
            self.module.search_cloud_insights,
            f"insights.id:'{insight_id}'+insights.string_value:*'*{fragment}*'",
            predicate=lambda record: any(
                isinstance(entry.get("value"), str) and fragment in entry["value"]
                for entry in record.get("insights", [])
            ),
            predicate_desc=f"record carries a string value containing {fragment!r}",
            note="Substring match on this endpoint requires the :* operator.",
        )

        absent = self.search(
            filter=f"insights.id:'{insight_id}'+insights.string_value:'no-such-value-xyzzy'",
            limit=1,
        )
        assert not absent["results"], (
            "A string value that exists on no asset returned rows, so the exact-match "
            "assertion above proves nothing."
        )

    def test_string_list_value_containment(self):
        """insights.string_list_value matches a single member of a list-valued insight."""
        found = self._a_value_of_type(list)
        if found is None:
            self.skip_with_warning(
                "tenant holds no non-empty list-valued insight in the sampled assets",
                context="string_list_value filter",
            )
            return
        insight_id, value = found
        member = value[0]

        self.assert_filter_matches(
            self.module.search_cloud_insights,
            f"insights.string_list_value:'{member}'",
            predicate=lambda record: any(
                isinstance(entry.get("value"), list) and member in entry["value"]
                for entry in record.get("insights", [])
            ),
            predicate_desc=f"record carries a list value containing {member!r}",
            note=f"{insight_id} was observed carrying {member!r} on a live asset.",
        )

        absent = self.search(
            filter="insights.string_list_value:'no-such-member-xyzzy.example.com'",
            limit=1,
        )
        assert not absent["results"], (
            "A list member that exists on no asset returned rows, so the containment "
            "assertion above proves nothing."
        )

    def test_integer_value_comparison(self):
        """insights.integer_value with a comparison operator.

        The API lists insights.integer_value among its supported filter fields, but no
        insight in the sampled assets carries an integer value. When that is the case
        this test proves the absence before skipping, so it is a statement about the
        tenant rather than a shrug at an unverified claim.
        """
        found = self._a_value_of_type(int)
        if found is None:
            for probe in ["insights.integer_value:>0", "insights.integer_value:<999999999"]:
                result = self.search(filter=probe, limit=1)
                assert not result["results"], (
                    f"{probe} returned rows, so this tenant does have integer-valued "
                    "insights — replace this skip with a positive control."
                )
            self.skip_with_warning(
                "no insight in this tenant carries an integer value, so the "
                ":> comparison cannot be positively verified here",
                context="integer_value filter",
            )
            return

        insight_id, value = found
        self.assert_filter_matches(
            self.module.search_cloud_insights,
            f"insights.id:'{insight_id}'+insights.integer_value:>={value}",
            predicate=lambda record: any(
                isinstance(entry.get("value"), int)
                and not isinstance(entry.get("value"), bool)
                and entry["value"] >= value
                for entry in record.get("insights", [])
            ),
            predicate_desc=f"record carries an integer value >= {value}",
        )

    def test_date_value_comparison(self):
        """insights.date_value with a comparison operator.

        Same shape as the integer case: the field is API-supported but no sampled insight
        carries a date value, so the absence is proven before skipping.
        """
        wide_open = "insights.date_value:<'2099-01-01T00:00:00Z'"
        result = self.search(filter=wide_open, limit=5)
        if not result["results"]:
            self.skip_with_warning(
                "no insight in this tenant carries a date value — a filter matching every "
                "possible date returned nothing, so the :< comparison cannot be verified here",
                context="date_value filter",
            )
            return

        self.assert_filter_matches(
            self.module.search_cloud_insights,
            wide_open,
            predicate=lambda record: any(
                isinstance(entry.get("value"), str) and entry["value"].endswith("Z")
                for entry in record.get("insights", [])
            ),
            predicate_desc="record carries a timestamp-shaped value",
        )

    # ------------------------------------------------------------------
    # search_cloud_insights — sort
    # ------------------------------------------------------------------

    def test_sort_changes_order_and_is_monotone(self):
        """A documented sort key actually orders the results.

        resource_name is used because it is strictly monotone under sort on this endpoint;
        updated_at is not (equal timestamps tie-break unstably in both the `.` and `|`
        forms), so asserting on it would produce a flaky test rather than a real one.
        Accepting the sort string is not enough — an unsupported key here is a 400, but a
        key the tool forwarded incorrectly would just return default order.
        """
        scope = "insights.id:'publiclyExposedToTheInternet'"
        ascending = [r["asset_name"] for r in self.search(filter=scope, sort="resource_name.asc", limit=20)["results"]]
        descending = [r["asset_name"] for r in self.search(filter=scope, sort="resource_name.desc", limit=20)["results"]]

        assert len(ascending) > 1, f"Need more than one asset under {scope} to test ordering"
        assert ascending == sorted(ascending), f"resource_name.asc is not ascending: {ascending}"
        assert descending == sorted(descending, reverse=True), (
            f"resource_name.desc is not descending: {descending}"
        )
        assert ascending != descending, "asc and desc returned the same order"

    def test_sort_pipe_and_dot_separators_agree(self):
        """Both separators work. The API documents `|`; the tool's examples use `.`."""
        scope = "insights.id:'publiclyExposedToTheInternet'"
        dot = [r["asset_name"] for r in self.search(filter=scope, sort="resource_name.desc", limit=10)["results"]]
        pipe = [r["asset_name"] for r in self.search(filter=scope, sort="resource_name|desc", limit=10)["results"]]

        assert dot, "Expected rows to compare separator forms"
        assert dot == pipe, (
            f"'resource_name.desc' and 'resource_name|desc' disagree.\n dot: {dot}\npipe: {pipe}"
        )

    def test_documented_sort_fields_are_accepted(self):
        """Every field named in the `sort` param description is a valid sort key."""
        scope = "insights.id:'publiclyExposedToTheInternet'"
        for field in ["cloud_provider", "account_id", "account_name", "resource_type",
                      "region", "creation_time", "updated_at"]:
            result = self.call_method(
                self.module.search_cloud_insights, filter=scope, sort=f"{field}.desc", limit=2
            )
            assert "fql_guide" not in result, (
                f"sort={field!r} was rejected by the API, but the sort param description "
                f"lists it as supported. Response: {result}"
            )
            assert result["results"], f"sort={field!r} returned no rows under {scope}"

    def test_sortable_insight_fields_are_accepted(self):
        """The three insight fields the API allows as sort keys are accepted."""
        scope = "insights.id:'publiclyExposedToTheInternet'"
        for field in SORTABLE_INSIGHT_FIELDS:
            result = self.call_method(
                self.module.search_cloud_insights, filter=scope, sort=f"{field}.desc", limit=2
            )
            assert "fql_guide" not in result, (
                f"Insight sort field {field!r} was rejected. The FQL guide names it as "
                f"sortable. Response: {result}"
            )

    def test_arbitrary_insight_id_is_not_sortable(self):
        """Sorting by an insight ID outside the supported three is rejected.

        The `sort` description used to claim insight-field sorting generally. It is
        limited to the three fields above, and this pins that limit so the guide cannot
        quietly drift back to the broader claim.
        """
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'identityIsAdmin'",
            sort="identityIsAdmin.desc",
            limit=2,
        )
        assert result.get("fql_guide"), (
            "Expected a 400 for sorting by an arbitrary insight ID. If the API now "
            "supports it, widen SORTABLE_INSIGHT_FIELDS and the FQL guide. "
            f"Response: {result}"
        )

    def test_invalid_sort_field_is_a_loud_error(self):
        """An unsupported sort key errors rather than being silently ignored."""
        result = self.call_method(
            self.module.search_cloud_insights,
            filter="insights.id:'identityIsAdmin'",
            sort="no_such_field.desc",
            limit=2,
        )
        assert result.get("fql_guide"), (
            f"Expected a 400 for an invalid sort field. Got: {sorted(result)}"
        )

    # ------------------------------------------------------------------
    # filter_used
    # ------------------------------------------------------------------

    def test_filter_used_echoes_caller_filter_on_empty_result(self):
        """filter_used is the caller's filter even when nothing matches."""
        fql = "insights.id:'publiclyExposedToTheInternet'+account_id:'this-account-does-not-exist-xyzzy'"
        result = self.search(filter=fql, limit=1)
        assert result["results"] == [], "Expected no matches for a nonexistent account"
        assert result["filter_used"] == fql
        assert "auto_filter_applied" not in result

    def test_filter_used_echoes_caller_filter_on_success(self):
        """filter_used is the caller's filter verbatim when rows come back."""
        fql = "insights.boolean_value:true"
        result = self.assert_filter_matches(self.module.search_cloud_insights, fql, limit=1)
        assert result["filter_used"] == fql
        assert "auto_filter_applied" not in result

    # ------------------------------------------------------------------
    # get_cloud_asset_insights
    # ------------------------------------------------------------------

    def test_get_cloud_asset_insights_returns_full_detail(self):
        """Drills into an asset found via search_cloud_insights and validates the shape."""
        found = self.assert_filter_matches(
            self.module.search_cloud_insights, "insights.id:'identityIsAdmin'"
        )
        asset_id = found["results"][0].get("asset_id")
        assert asset_id, "Expected 'asset_id' in insight record"

        result = self.call_method(self.module.get_cloud_asset_insights, asset_ids=[asset_id])
        self.assert_no_error(result, context="get_cloud_asset_insights")
        self.assert_valid_list_response(result, min_length=1, context="get_cloud_asset_insights")

        rec = result[0]
        assert rec["asset_id"] == asset_id, f"Expected {asset_id}, got {rec.get('asset_id')}"
        assert "insights" in rec, f"Expected 'insights' in record. Got: {sorted(rec.keys())}"
        assert "external" in rec["insights"], "Expected 'external' in insights"

    def test_get_cloud_asset_insights_multiple_ids(self):
        """Multiple asset IDs return one record each, in the requested order."""
        found = self.assert_filter_matches(
            self.module.search_cloud_insights, "insights.id:'identityIsAdmin'", limit=5
        )
        if len(found["results"]) < 2:
            self.skip_with_warning(
                "tenant has fewer than 2 assets carrying identityIsAdmin",
                context="get_cloud_asset_insights multi-id",
            )
            return

        asset_ids = [r["asset_id"] for r in found["results"][:2]]
        result = self.call_method(self.module.get_cloud_asset_insights, asset_ids=asset_ids)
        self.assert_no_error(result, context="get_cloud_asset_insights multiple ids")
        assert isinstance(result, list)
        assert len(result) == 2, f"Expected 2 records for 2 asset IDs, got {len(result)}"
        assert [r["asset_id"] for r in result] == asset_ids, (
            "get_cloud_asset_insights must return records in the requested ID order"
        )

    # ------------------------------------------------------------------
    # Insight ID coverage: every ID named in the FQL guide must exist
    # ------------------------------------------------------------------

    def test_fql_guide_insight_ids_all_exist_in_catalog(self):
        """Every insight_id used as an example in the FQL guide is a real catalog ID.

        A guide that names an ID the catalog does not have hands agents a filter that
        returns an empty 200 forever, with no error to explain why. One catalog fetch
        checks them all.
        """
        documented = [
            "publiclyExposedToTheInternet",
            "publiclyExposedAccessRange",
            "identityIsAdmin",
            "unusedIdentity",
            "identityUnrotatedAccessKeys",
            "reachableCriticalVulnerabilities",
            "reachableRceVulnerabilities",
            "hasSensor",
            "hasSecrets",
            "hasSensitiveData",
            "loggingEnabled",
            "usesAiServices",
            "hasExcessiveActions",
            "exposesMcpServerInterface",
            "identityAssumableByService",
            "enabledLoggingSources",
        ]
        catalog_ids = {entry["insight_id"] for entry in self.definitions(limit=500)}
        missing = [iid for iid in documented if iid not in catalog_ids]
        assert not missing, (
            f"FQL guide names insight IDs absent from the catalog: {missing}. "
            f"Catalog has {len(catalog_ids)} IDs: {sorted(catalog_ids)}"
        )
