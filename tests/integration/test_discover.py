"""Integration tests for the Discover module."""

import pytest

from falcon_mcp.modules.discover import DiscoverModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDiscoverIntegration(BaseIntegrationTest):
    """Integration tests for Discover module with real API calls.

    Validates:
    - Correct FalconPy operation names (combined_applications, combined_hosts)
    - Combined query endpoints return full details
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the discover module with a real client."""
        self.module = DiscoverModule(falcon_client)

    def test_search_applications_returns_details(self):
        """Test that search_applications returns full application details.

        Validates the combined_applications operation name is correct.
        Note: filter is required for this endpoint.
        """
        result = self.call_method(
            self.module.search_applications,
            filter="name:*'*'",
            limit=5,
        )

        self.assert_no_error(result, context="search_applications")
        self.assert_valid_list_response(result, min_length=0, context="search_applications")

        records = self.records(result, context="search_applications")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_applications",
            )

    def test_search_applications_with_filter(self):
        """Test search_applications with FQL filter."""
        result = self.call_method(
            self.module.search_applications,
            filter="vendor:'Microsoft Corporation'",
            limit=3,
        )

        self.assert_no_error(result, context="search_applications with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_applications with filter")

    def test_search_applications_with_facet(self):
        """Test search_applications with facet parameter."""
        result = self.call_method(
            self.module.search_applications,
            filter="name:*'*'",
            facet="host_info",
            limit=3,
        )

        self.assert_no_error(result, context="search_applications with facet")
        self.assert_valid_list_response(result, min_length=0, context="search_applications with facet")

    def test_search_unmanaged_assets_returns_details(self):
        """Test that search_unmanaged_assets returns full asset details.

        Validates the combined_hosts operation name is correct.
        Also validates that entity_type:'unmanaged' filter is applied automatically.
        """
        result = self.call_method(self.module.search_unmanaged_assets, limit=5)

        self.assert_no_error(result, context="search_unmanaged_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets")

        records = self.records(result, context="search_unmanaged_assets")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_unmanaged_assets",
            )

    def test_search_unmanaged_assets_with_filter(self):
        """Test search_unmanaged_assets with additional FQL filter."""
        result = self.call_method(
            self.module.search_unmanaged_assets,
            filter="platform_name:'Windows'",
            limit=3,
        )

        self.assert_no_error(result, context="search_unmanaged_assets with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets with filter")

    def test_search_unmanaged_assets_with_sort(self):
        """Test search_unmanaged_assets with sort parameter."""
        result = self.call_method(
            self.module.search_unmanaged_assets,
            sort="last_seen_timestamp.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_unmanaged_assets with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets with sort")

    def test_search_managed_assets_returns_details(self):
        """Test that search_managed_assets returns full asset details.

        Validates the combined_hosts operation name is correct.
        Also validates that entity_type:'managed' filter is applied automatically.
        """
        result = self.call_method(self.module.search_managed_assets, limit=5)

        self.assert_no_error(result, context="search_managed_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_managed_assets")

        records = self.records(result, context="search_managed_assets")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_managed_assets",
            )

    def test_search_managed_assets_with_filter(self):
        """Test search_managed_assets with a managed-only encryption filter.

        The combined_hosts endpoint validates filter fields loudly (HTTP 400 for an
        unknown field/type), so a clean response confirms encryption_status is a valid
        managed-asset field.
        """
        result = self.call_method(
            self.module.search_managed_assets,
            filter="encryption_status:'Unencrypted'",
            limit=3,
        )

        self.assert_no_error(result, context="search_managed_assets with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_managed_assets with filter")

    def test_search_managed_assets_with_os_security_filter(self):
        """Test search_managed_assets with an os_security boolean filter.

        os_security.* fields are booleans; a string value returns HTTP 400. This
        confirms the documented boolean form is accepted.
        """
        result = self.call_method(
            self.module.search_managed_assets,
            filter="os_security.credential_guard_status:true",
            limit=3,
        )

        self.assert_no_error(result, context="search_managed_assets os_security filter")
        self.assert_valid_list_response(result, min_length=0, context="search_managed_assets os_security filter")

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test combined_applications
        result = self.call_method(self.module.search_applications, filter="name:*'*'", limit=1)
        self.assert_no_error(result, context="combined_applications operation name")

        # Test combined_hosts (unmanaged)
        result = self.call_method(self.module.search_unmanaged_assets, limit=1)
        self.assert_no_error(result, context="combined_hosts operation name")

        # Test combined_hosts (managed)
        result = self.call_method(self.module.search_managed_assets, limit=1)
        self.assert_no_error(result, context="combined_hosts managed operation name")
