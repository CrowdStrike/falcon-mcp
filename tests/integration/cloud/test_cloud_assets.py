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
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="cloud_provider:'AWS'",
            limit=3,
        )
        self.assert_no_error(result, context="search_cspm_assets with cloud_provider filter")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets cloud_provider filter")
        if len(result) > 0:
            for asset in result:
                assert "cloud_provider" in asset, "Asset should have cloud_provider field"
                assert asset["cloud_provider"].upper() == "AWS", (
                    f"Expected cloud_provider AWS, got {asset['cloud_provider']}"
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
