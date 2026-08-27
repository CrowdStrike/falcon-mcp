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
        """`running_status:true` selects only containers the response reports as running."""
        self.assert_filter_matches(
            self.module.search_kubernetes_containers,
            "running_status:true",
            predicate=lambda container: container.get("running_status") is True,
            predicate_desc="container.running_status is True",
            note="Most containers in a real inventory are stopped, so this must select.",
            limit=5,
        )

    def test_search_kubernetes_containers_sort_orders_by_cluster_name(self):
        """`cluster_name` is the one documented sort key this endpoint orders reliably.

        `allow_ties=True` is unavoidable here: containers share clusters, so any page is
        tied several times over. What that costs is small, because `ReadContainerCombined`
        returns whole records in one call — there is no hydration step to scramble the order,
        so the thing worth catching is the sort being dropped or ignored, which a tied
        comparison still catches.

        The other documented keys do not survive an order assertion against live data, which
        is worth knowing before reaching for one: `last_seen` and `first_seen` are null on
        most containers, so the ascending page has nothing to compare; `container_name`,
        `namespace`, `cloud_name` and `cloud_region` return pages that are genuinely out of
        order once empty-string values mix in; and `image_vulnerability_count` holds for a
        short page but breaks partway down a longer one.
        """
        key = "cluster_name"
        ascending = self.call_method(
            self.module.search_kubernetes_containers, sort=f"{key}.asc", limit=50
        )
        descending = self.call_method(
            self.module.search_kubernetes_containers, sort=f"{key}.desc", limit=50
        )
        self.assert_no_error(ascending, context=f"search_kubernetes_containers {key}.asc")
        self.assert_no_error(descending, context=f"search_kubernetes_containers {key}.desc")

        self.assert_sort_orders_rows(
            [c[key] for c in self.skip_unless_tenant_has(ascending, "Kubernetes containers")],
            [c[key] for c in self.skip_unless_tenant_has(descending, "Kubernetes containers")],
            key,
            context="search_kubernetes_containers",
            allow_ties=True,
        )

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
        self.skip_unless_tenant_has(result, "image vulnerabilities", "search_images_vulnerabilities")

        self.assert_search_returns_details(
            result,
            expected_fields=["cve_id", "severity", "cvss_score"],
            context="search_images_vulnerabilities",
        )

    def test_search_images_vulnerabilities_with_filter(self):
        """`cvss_score` accepts numeric comparison operators.

        This is the only converted filter here whose response field is named like the
        filter field, so the predicate reads the same name on both sides.
        """
        self.assert_filter_matches(
            self.module.search_images_vulnerabilities,
            "cvss_score:>5",
            predicate=lambda vuln: vuln.get("cvss_score") is not None and vuln["cvss_score"] > 5,
            predicate_desc="vuln.cvss_score > 5",
            note="A tenant with any assessed images has CVEs above a mid CVSS score.",
            limit=5,
        )
