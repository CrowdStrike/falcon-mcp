"""Integration tests for CSPM asset inventory tools."""

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudAssetsIntegration(BaseIntegrationTest):
    """Integration tests for CSPM asset inventory tools."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    def test_search_cspm_assets_returns_details(self):
        """Validates cloud_security_assets_queries and cloud_security_assets_entities_get operation names."""
        result = self.call_method(self.module.search_cspm_assets, limit=5)
        self.assert_no_error(result, context="search_cspm_assets")
        self.skip_unless_tenant_has(result, "CSPM assets", "search_cspm_assets")

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "cloud_provider", "resource_type"],
            context="search_cspm_assets",
        )

    def test_search_cspm_assets_with_cloud_provider_filter(self):
        """cloud_provider filters on the lowercase value the API returns.

        Asserts the returned value literally rather than via .upper(), which passed for
        either casing and so never covered which spelling the tool should document.
        """
        result = self.assert_filter_matches(
            self.module.search_cspm_assets,
            "cloud_provider:'aws'",
            predicate=lambda asset: asset.get("cloud_provider") == "aws",
            predicate_desc="asset.cloud_provider == 'aws'",
            note="Every guide, filter hint and example in this repo uses lowercase.",
            limit=3,
        )
        assert self._unwrap_results(result), "Expected at least one AWS asset"

    def test_cloud_provider_casing_differs_across_cloud_endpoints(self):
        """This endpoint is case-insensitive on cloud_provider; search_iom_findings is not.

        Documented because the failure is silent: `cloud_provider:'AWS'` against
        cspm_evaluations_iom_queries returns an empty HTTP 200 rather than an error, so a
        model that learned uppercase from one cloud tool gets zero findings from the other
        with nothing to explain why. Lowercase is the only spelling that works on both,
        which is why every guide and hint in the repo uses it.

        The assertion is zero-versus-nonzero rather than exact equality: the two calls run
        seconds apart against a live inventory, so their totals routinely differ by a
        record or two.
        """
        lower = self.call_method(self.module.search_cspm_assets, filter="cloud_provider:'aws'", limit=1)
        upper = self.call_method(self.module.search_cspm_assets, filter="cloud_provider:'AWS'", limit=1)
        self.assert_no_error(lower, context="cspm assets lowercase")
        self.assert_no_error(upper, context="cspm assets uppercase")
        lower_total = lower["pagination"]["total"]
        upper_total = upper["pagination"]["total"]
        assert lower_total, "cloud_provider:'aws' matched no assets, so this test proves nothing"
        assert upper_total > lower_total * 0.9, (
            "cloud_security_assets_queries used to treat cloud_provider case-insensitively; "
            "uppercase now returns a materially different count. "
            f"lowercase total={lower_total}, uppercase total={upper_total}"
        )

        iom_lower = self.call_method(self.module.search_iom_findings, filter="cloud_provider:'aws'", limit=1)
        iom_upper = self.call_method(self.module.search_iom_findings, filter="cloud_provider:'AWS'", limit=1)
        self.assert_no_error(iom_lower, context="iom lowercase")
        self.assert_no_error(iom_upper, context="iom uppercase")
        assert iom_lower["pagination"]["total"], (
            "cloud_provider:'aws' returned no IOM findings, so the comparison below proves nothing"
        )
        assert not iom_upper["pagination"]["total"], (
            "cspm_evaluations_iom_queries now matches uppercase cloud_provider. If that is "
            "real, the lowercase-only warning in the IOM FQL guide can be relaxed. "
            f"uppercase total={iom_upper['pagination']['total']}"
        )

    def test_search_cspm_assets_with_tag_filter(self):
        """`tag_key` selects assets carrying that key in their `tags` map.

        The filter names a key; the response returns the whole tag map, so the check is for
        membership rather than a value. Assets with no tags at all come back without a
        `tags` key, which is what makes this predicate able to fail: a filter that was
        being dropped would return untagged assets alongside the tagged ones.
        """
        self.assert_filter_matches(
            self.module.search_cspm_assets,
            "tag_key:'Environment'",
            predicate=lambda asset: "Environment" in (asset.get("tags") or {}),
            predicate_desc="'Environment' in asset.tags",
            note="tag_key matches the key name only; tag_value filters the value.",
            limit=10,
        )

    def test_search_cspm_assets_sort_orders_by_resource_name(self):
        """`resource_name` really orders the query step, in both directions.

        This is the other half of `test_search_cspm_assets_returns_rows_in_query_step_order`
        below. That one proves the hydration step preserves whatever order it was handed;
        this one proves there was an order to preserve, which a tool that quietly stopped
        forwarding `sort` would still pass.

        `allow_ties=True` because nothing on this endpoint is tie-free — duplicate resource
        names are common, and every other documented key ties harder. Ties are safe for what
        is compared here (the value sequence, within a single response) and unsafe only for
        comparing two runs row by row, which this does not do. `updated_at`, the tool's own
        example, is monotone but ties heavily; `creation_time` is absent on many assets and
        its descending page is not ordered at all.
        """
        key = "resource_name"
        ascending = self.call_method(self.module.search_cspm_assets, sort=f"{key}.asc", limit=50)
        descending = self.call_method(self.module.search_cspm_assets, sort=f"{key}.desc", limit=50)
        self.assert_no_error(ascending, context=f"search_cspm_assets {key}.asc")
        self.assert_no_error(descending, context=f"search_cspm_assets {key}.desc")

        def names(result, direction):
            assets = self.skip_unless_tenant_has(result, "CSPM assets", f"{key}.{direction}")
            missing = [a["id"] for a in assets if not a.get(key)]
            # Sorting on resource_name returns only assets that have one, so this is a
            # statement about the endpoint rather than defensive noise: an unnamed asset in
            # a name-sorted page means the sort was not applied to the query at all.
            assert not missing, (
                f"{len(missing)} of {len(assets)} assets in the {key}.{direction} page carry "
                f"no {key}, so their order cannot be compared. First few: {missing[:3]}"
            )
            return [a[key] for a in assets]

        self.assert_sort_orders_rows(
            names(ascending, "asc"),
            names(descending, "desc"),
            key,
            context="search_cspm_assets",
            allow_ties=True,
        )

    def test_search_cspm_assets_returns_rows_in_query_step_order(self):
        """Hydrated assets come back in the order the query step reported them.

        A reorder-contract test rather than a monotonicity one, because
        `search_cspm_assets` has no strictly monotone sort field on this tenant — every
        documented key (`updated_at`, `resource_type`, `region`, ...) ties across rows, so
        an asc/desc comparison would tie-break unstably and flake.

        The contract is load-bearing here: `cloud_security_assets_entities_get` returned a
        different order than it was handed on 6 of 6 measured trials, so without the reorder
        the tool's `sort` would be silently discarded on essentially every call.

        Limit is 50 to stay under the 100-ID detail batch size, so the query step's order is
        captured in a single request.
        """
        self.assert_rows_in_query_step_order(
            self.module.search_cspm_assets,
            id_field="id",
            context="search_cspm_assets reorder contract",
            limit=50,
        )

    def test_search_cspm_assets_batching(self):
        """A limit above the 100-per-request detail batch size still returns every record.

        `len()` on the envelope counts its keys, so the old `len(result) > 100` guard was
        always false and this never exercised batching at all.
        """
        result = self.call_method(self.module.search_cspm_assets, limit=500)
        self.assert_no_error(result, context="search_cspm_assets with large limit")
        assets = self.skip_unless_tenant_has(result, "CSPM assets", "search_cspm_assets batching")

        total = result["pagination"]["total"]
        if total is not None and total <= 100:
            self.skip_with_warning(
                f"tenant has only {total} CSPM assets, so batching is not exercised",
                context="search_cspm_assets batching",
            )
            return

        assert len(assets) > 100, (
            f"Requested 500 assets from a tenant reporting {total}, but only {len(assets)} "
            "came back — the 100-per-request detail batching is dropping records."
        )
        ids = [a.get("id") for a in assets]
        assert len(set(ids)) == len(ids), "Batching returned the same asset more than once"
