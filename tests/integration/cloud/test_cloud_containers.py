"""Integration tests for Kubernetes containers and image vulnerability tools."""

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudContainersIntegration(BaseIntegrationTest):
    """Integration tests for Kubernetes containers and image vulnerability tools."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    def test_search_kubernetes_containers_returns_details(self):
        """Validates the ReadContainerCombined operation name is correct."""
        result = self.call_method(self.module.search_kubernetes_containers, limit=5)
        self.assert_no_error(result, context="search_kubernetes_containers")
        self.skip_unless_tenant_has(result, "Kubernetes containers", "search_kubernetes_containers")

        self.assert_search_returns_details(
            result,
            expected_fields=["container_id", "container_name"],
            context="search_kubernetes_containers",
        )

    def test_search_kubernetes_containers_with_filter(self):
        result = self.call_method(
            self.module.search_kubernetes_containers,
            filter="running_status:true",
            limit=3,
        )
        self.assert_no_error(result, context="search_kubernetes_containers with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with filter")

    def test_search_kubernetes_containers_with_sort(self):
        result = self.call_method(
            self.module.search_kubernetes_containers,
            sort="last_seen.desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_kubernetes_containers with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with sort")

    def test_count_kubernetes_containers(self):
        """Validates the ReadContainerCount operation name is correct."""
        result = self.call_method(self.module.count_kubernetes_containers)
        if isinstance(result, list):
            self.assert_no_error(result, context="count_kubernetes_containers")
        else:
            assert isinstance(result, int), f"Expected int, got {type(result)}"
            assert result >= 0, f"Expected non-negative count, got {result}"

    def test_count_kubernetes_containers_with_filter(self):
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
        """Validates the ReadCombinedVulnerabilities operation name is correct."""
        result = self.call_method(self.module.search_images_vulnerabilities, limit=5)
        self.assert_no_error(result, context="search_images_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities")

    def test_search_images_vulnerabilities_with_filter(self):
        result = self.call_method(
            self.module.search_images_vulnerabilities,
            filter="cvss_score:>5",
            limit=3,
        )
        self.assert_no_error(result, context="search_images_vulnerabilities with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities with filter")
