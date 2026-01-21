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
