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
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets")
        if len(result) > 0:
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
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="tag_key:'Environment'",
            limit=10,
        )
        self.assert_no_error(result, context="search_cspm_assets with tag filter")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with tag filter")
        else:
            assert isinstance(result, dict), "Expected dict or list response for tag filter"
            assert "results" in result or "total" in result

    def test_search_cspm_assets_with_sort(self):
        result = self.call_method(
            self.module.search_cspm_assets,
            sort="updated_at.desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_cspm_assets with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with sort")

    def test_search_cspm_assets_batching(self):
        """Tests batching logic when environment has >100 assets."""
        result = self.call_method(self.module.search_cspm_assets, limit=500)
        self.assert_no_error(result, context="search_cspm_assets with large limit")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets large result")
        if len(result) > 100:
            print(f"✅ Batching tested successfully with {len(result)} assets")
