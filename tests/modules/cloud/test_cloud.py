"""
Tests for the Cloud module — registration only.

Per-tool tests live in their respective mixin test files:
  test_cloud_risks.py, test_cloud_iom.py, test_cloud_containers.py,
  test_cloud_assets.py, test_cloud_insights.py
"""

import unittest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudModule(TestModules):
    """Test cases for the Cloud module."""

    def setUp(self):
        self.setup_module(CloudModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_list_cloud_insight_definitions",
            "falcon_search_cloud_insights",
            "falcon_get_cloud_asset_insights",
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
            "falcon_search_iom_findings",
            "falcon_search_cspm_suppression_rules",
            "falcon_create_cspm_suppression_rule",
            "falcon_delete_cspm_suppression_rules",
            "falcon_search_cloud_risks",
            "falcon_search_cloud_groups",
            "falcon_get_cloud_groups",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_search_cloud_insights_fql_guide",
            "falcon_kubernetes_containers_fql_filter_guide",
            "falcon_images_vulnerabilities_fql_filter_guide",
            "falcon_search_cspm_assets_fql_guide",
            "falcon_search_iom_findings_fql_guide",
            "falcon_search_cloud_risks_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)


if __name__ == "__main__":
    unittest.main()
