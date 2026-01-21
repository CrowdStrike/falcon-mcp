"""Integration tests for the Hosts module."""

import pytest

from falcon_mcp.modules.hosts import HostsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestHostsIntegration(BaseIntegrationTest):
    """Integration tests for Hosts module with real API calls.

    Validates:
    - Correct FalconPy operation names (QueryDevicesByFilter, PostDeviceDetailsV2)
    - Two-step search pattern returns full details, not just IDs
    - POST body usage for get_by_ids
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the hosts module with a real client."""
        self.module = HostsModule(falcon_client)

    def test_search_hosts_returns_details(self):
        """Test that search_hosts returns full host details, not just IDs.

        This validates the two-step search pattern:
        1. QueryDevicesByFilter returns device IDs
        2. PostDeviceDetailsV2 returns full details
        """
        result = self.call_method(self.module.search_hosts, limit=5)

        self.assert_no_error(result, context="search_hosts")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["device_id", "hostname"],
                context="search_hosts",
            )

    def test_search_hosts_with_filter(self):
        """Test search_hosts with FQL filter."""
        result = self.call_method(
            self.module.search_hosts,
            filter="platform_name:'Windows'",
            limit=3,
        )

        self.assert_no_error(result, context="search_hosts with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts with filter")

    def test_search_hosts_with_sort(self):
        """Test search_hosts with sort parameter."""
        result = self.call_method(
            self.module.search_hosts,
            sort="last_seen.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_hosts with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts with sort")

    def test_get_host_details_with_valid_id(self):
        """Test get_host_details with a valid device ID.

        First searches for a host, then gets its details.
        """
        # First, search for a host to get a valid ID
        search_result = self.call_method(self.module.search_hosts, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No hosts available to test get_host_details",
                context="test_get_host_details_with_valid_id",
            )

        device_id = self.get_first_id(search_result, id_field="device_id")
        if not device_id:
            self.skip_with_warning(
                "Could not extract device ID from search results",
                context="test_get_host_details_with_valid_id",
            )

        # Now get details for that host
        result = self.call_method(self.module.get_host_details, ids=[device_id])

        self.assert_no_error(result, context="get_host_details")
        self.assert_valid_list_response(result, min_length=1, context="get_host_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["device_id", "hostname"],
            context="get_host_details",
        )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        result = self.call_method(self.module.search_hosts, limit=1)
        self.assert_no_error(result, context="operation name validation")
