"""Integration tests for cloud risks and cloud groups tools."""

from typing import Any

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudRisksIntegration(BaseIntegrationTest):
    """Integration tests for cloud risks and cloud groups tools."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    @staticmethod
    def _is_403_error(result: Any) -> bool:
        for candidate in ([result] if isinstance(result, dict) else (result if isinstance(result, list) else [])):
            if isinstance(candidate, dict) and "error" in candidate:
                msg = str(candidate)
                if any(s in msg.lower() for s in ("403", "access denied", "forbidden", "scope not permitted")):
                    return True
        return False

    def test_search_cloud_risks_operation_name_correct(self):
        """Validates combined_cloud_risks operation name is correct."""
        result = self.call_method(self.module.search_cloud_risks, limit=1)
        self.assert_no_error(result, context="combined_cloud_risks operation name")
        self.assert_valid_list_response(result, min_length=0, context="search_cloud_risks")

    def test_search_cloud_risks_returns_full_details(self):
        result = self.call_method(self.module.search_cloud_risks, limit=3)
        self.assert_no_error(result, context="search_cloud_risks full details")
        if not result:
            self.skip_with_warning("No cloud risks found in environment", "search_cloud_risks details")
            return
        first = result[0]
        assert isinstance(first, dict), f"Expected dict, got {type(first)}"
        for field in ["id", "severity", "status"]:
            assert field in first, f"Expected '{field}' in risk entity. Got: {sorted(first.keys())}"

    def test_search_cloud_risks_with_severity_filter(self):
        result = self.call_method(self.module.search_cloud_risks, filter="severity:'Critical'", limit=3)
        self.assert_no_error(result, context="search_cloud_risks severity filter")
        self.assert_valid_list_response(result, min_length=0, context="severity filter")

    def test_search_cloud_risks_with_status_filter(self):
        result = self.call_method(self.module.search_cloud_risks, filter="status:'Open'", limit=3)
        self.assert_no_error(result, context="search_cloud_risks status filter")
        self.assert_valid_list_response(result, min_length=0, context="status filter")

    def test_search_cloud_risks_capitalized_filter_values_return_results(self):
        """Regression: lowercase severity/status values silently return 0 on this endpoint."""
        baseline = self.call_method(self.module.search_cloud_risks, limit=1)
        self.assert_no_error(baseline, context="baseline cloud risks")
        if not baseline:
            self.skip_with_warning("No cloud risks in environment", "cloud risks case-sensitivity")
            return
        result = self.call_method(
            self.module.search_cloud_risks,
            filter="severity:'Critical',severity:'High',severity:'Medium',severity:'Low',severity:'Informational'",
            limit=5,
        )
        self.assert_no_error(result, context="capitalized severity filter")
        self.assert_valid_list_response(result, min_length=1, context="capitalized severity values must match when risks exist")

    def test_search_cloud_risks_with_cloud_provider_filter(self):
        result = self.call_method(self.module.search_cloud_risks, filter="cloud_provider:'aws'", limit=3)
        self.assert_no_error(result, context="search_cloud_risks cloud_provider filter")
        self.assert_valid_list_response(result, min_length=0, context="cloud_provider filter")

    def test_search_cloud_risks_with_sort(self):
        result = self.call_method(self.module.search_cloud_risks, sort="severity|desc", limit=3)
        self.assert_no_error(result, context="search_cloud_risks with sort")
        self.assert_valid_list_response(result, min_length=0, context="sort")

    def test_search_cloud_groups_operation_name_correct(self):
        """Validates ListCloudGroupsExternal operation name is correct."""
        result = self.call_method(self.module.search_cloud_groups, limit=5)
        if self._is_403_error(result):
            self.skip_with_warning("Cloud groups scope not available on this key", "search_cloud_groups")
            return
        self.assert_no_error(result, context="ListCloudGroupsExternal operation name")
        self.assert_valid_list_response(result, min_length=0, context="search_cloud_groups")

    def test_search_cloud_groups_returns_full_details(self):
        result = self.call_method(self.module.search_cloud_groups, limit=3)
        if self._is_403_error(result):
            self.skip_with_warning("Cloud groups scope not available on this key", "search_cloud_groups details")
            return
        self.assert_no_error(result, context="search_cloud_groups full details")
        if not result:
            self.skip_with_warning("No cloud groups found in environment", "search_cloud_groups details")
            return
        first = result[0]
        assert isinstance(first, dict), f"Expected dict, got {type(first)}"
        assert "id" in first, f"Expected 'id' in group entity. Got: {sorted(first.keys())}"

    def test_get_cloud_groups_operation_name_correct(self):
        """Validates ListCloudGroupsByIDExternal operation name is correct."""
        groups = self.call_method(self.module.search_cloud_groups, limit=1)
        if self._is_403_error(groups):
            self.skip_with_warning("Cloud groups scope not available on this key", "get_cloud_groups by ID")
            return
        self.assert_no_error(groups, context="get groups for ID lookup")
        if not groups:
            self.skip_with_warning("No cloud groups found", "get_cloud_groups by ID")
            return
        group_id = groups[0].get("id")
        assert group_id, "Expected 'id' field in group"
        result = self.call_method(self.module.get_cloud_groups, ids=[group_id])
        self.assert_no_error(result, context="ListCloudGroupsByIDExternal operation name")
        self.assert_valid_list_response(result, min_length=1, context="get_cloud_groups by ID")
        assert result[0]["id"] == group_id
