"""Integration tests for the Cloud module."""

import pytest

from falcon_mcp.modules.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudIntegration(BaseIntegrationTest):
    """Integration tests for Cloud module with real API calls.

    Validates:
    - Correct FalconPy operation names (ReadContainerCombined, ReadContainerCount, ReadCombinedVulnerabilities)
    - Combined query endpoints return full details
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the cloud module with a real client."""
        self.module = CloudModule(falcon_client)

    def test_search_kubernetes_containers_returns_details(self):
        """Test that search_kubernetes_containers returns full container details.

        Validates the ReadContainerCombined operation name is correct.
        """
        result = self.call_method(self.module.search_kubernetes_containers, limit=5)

        self.assert_no_error(result, context="search_kubernetes_containers")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers")

        if len(result) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["container_id", "container_name"],
                context="search_kubernetes_containers",
            )

    def test_search_kubernetes_containers_with_filter(self):
        """Test search_kubernetes_containers with FQL filter."""
        result = self.call_method(
            self.module.search_kubernetes_containers,
            filter="running_status:true",
            limit=3,
        )

        self.assert_no_error(result, context="search_kubernetes_containers with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with filter")

    def test_search_kubernetes_containers_with_sort(self):
        """Test search_kubernetes_containers with sort parameter."""
        result = self.call_method(
            self.module.search_kubernetes_containers,
            sort="last_seen.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_kubernetes_containers with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with sort")

    def test_count_kubernetes_containers(self):
        """Test that count_kubernetes_containers returns a count.

        Validates the ReadContainerCount operation name is correct.
        """
        result = self.call_method(self.module.count_kubernetes_containers)

        # Result should be an integer or a list with error
        if isinstance(result, list):
            self.assert_no_error(result, context="count_kubernetes_containers")
        else:
            # Should be a valid count (integer >= 0)
            assert isinstance(result, int), f"Expected int, got {type(result)}"
            assert result >= 0, f"Expected non-negative count, got {result}"

    def test_count_kubernetes_containers_with_filter(self):
        """Test count_kubernetes_containers with FQL filter."""
        result = self.call_method(
            self.module.count_kubernetes_containers,
            filter="running_status:true",
        )

        if isinstance(result, list):
            self.assert_no_error(result, context="count_kubernetes_containers with filter")
        else:
            assert isinstance(result, int), f"Expected int, got {type(result)}"
            assert result >= 0, f"Expected non-negative count, got {result}"

    def test_search_images_vulnerabilities_returns_details(self):
        """Test that search_images_vulnerabilities returns full vulnerability details.

        Validates the ReadCombinedVulnerabilities operation name is correct.
        """
        result = self.call_method(self.module.search_images_vulnerabilities, limit=5)

        self.assert_no_error(result, context="search_images_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities")

    def test_search_images_vulnerabilities_with_filter(self):
        """Test search_images_vulnerabilities with FQL filter."""
        result = self.call_method(
            self.module.search_images_vulnerabilities,
            filter="cvss_score:>5",
            limit=3,
        )

        self.assert_no_error(result, context="search_images_vulnerabilities with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities with filter")

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test ReadContainerCombined
        result = self.call_method(self.module.search_kubernetes_containers, limit=1)
        self.assert_no_error(result, context="ReadContainerCombined operation name")

        # Test ReadCombinedVulnerabilities
        result = self.call_method(self.module.search_images_vulnerabilities, limit=1)
        self.assert_no_error(result, context="ReadCombinedVulnerabilities operation name")

        # Test cloud_security_assets_queries and cloud_security_assets_entities_get
        result = self.call_method(self.module.search_cspm_assets, limit=1)
        self.assert_no_error(result, context="CSPM operation names")

    def test_search_cspm_assets_returns_details(self):
        """Test that search_cspm_assets returns full asset details using two-step pattern.

        Validates:
        - cloud_security_assets_queries operation name is correct
        - cloud_security_assets_entities_get operation name is correct
        - Two-step pattern (query IDs -> get details) works correctly
        - Returns full asset records, not just IDs
        """
        result = self.call_method(self.module.search_cspm_assets, limit=5)

        self.assert_no_error(result, context="search_cspm_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "cloud_provider", "resource_type"],
                context="search_cspm_assets",
            )

    def test_search_cspm_assets_with_cloud_provider_filter(self):
        """Test search_cspm_assets with cloud provider FQL filter."""
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="cloud_provider:'AWS'",
            limit=3,
        )

        self.assert_no_error(result, context="search_cspm_assets with cloud_provider filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cspm_assets with cloud_provider filter"
        )

        # If results exist, verify they match the filter
        if len(result) > 0:
            for asset in result:
                assert "cloud_provider" in asset, "Asset should have cloud_provider field"
                # Note: Filter may return AWS and aws, be flexible
                assert asset["cloud_provider"].upper() == "AWS", (
                    f"Expected cloud_provider AWS, got {asset['cloud_provider']}"
                )

    def test_search_cspm_assets_with_tag_filter(self):
        """Test search_cspm_assets with tag FQL filter syntax.

        Validates the tags.'key':'value' FQL syntax is accepted by the API.
        May return empty results if no assets have this tag.
        """
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="tags.'Environment':*",
            limit=10,
        )

        self.assert_no_error(result, context="search_cspm_assets with tag filter")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with tag filter")

    def test_search_cspm_assets_with_sort(self):
        """Test search_cspm_assets with sort parameter."""
        result = self.call_method(
            self.module.search_cspm_assets,
            sort="updated_at.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_cspm_assets with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with sort")

    def test_search_cspm_assets_batching_large_result(self):
        """Test search_cspm_assets with large limit to verify batching works.

        If the environment has >100 assets, this tests the batching logic.
        """
        result = self.call_method(self.module.search_cspm_assets, limit=500)

        self.assert_no_error(result, context="search_cspm_assets with large limit")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets large result")

        # If we got >100 results, batching was tested successfully
        if len(result) > 100:
            print(f"✅ Batching tested successfully with {len(result)} assets")

