"""Integration tests for the Recon module."""

import pytest

from falcon_mcp.modules.recon import ReconModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestReconIntegration(BaseIntegrationTest):
    """Integration tests for the Recon module with real API calls.

    Validates:
    - Correct FalconPy operation names (QueryNotificationsV1, GetNotificationsDetailedV1, etc.)
    - GET-with-params pattern for all three Get* operations (use_params=True)
    - Two-step search pattern returns full details, not just IDs
    - FQL filter fields accepted by the live API

    Requires Falcon Intelligence Recon, Counter Adversary, or Adversary Intelligence
    subscription. Tests skip gracefully if no data is present.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Recon module with a real client."""
        self.module = ReconModule(falcon_client)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def test_search_recon_notifications_operation_names(self):
        """Validate QueryNotificationsV1 and GetNotificationsDetailedV1 operation names."""
        result = self.call_method(self.module.search_recon_notifications, limit=1)
        self.assert_no_error(result, context="QueryNotificationsV1 / GetNotificationsDetailedV1 validation")

    def test_search_recon_notifications_returns_list(self):
        """Test that search returns a list or empty-response dict (never an error)."""
        result = self.call_method(self.module.search_recon_notifications, limit=5)

        self.assert_no_error(result, context="search_recon_notifications")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_recon_notifications")

    def test_search_recon_notifications_returns_full_details(self):
        """Test that results contain full notification detail, not just IDs."""
        result = self.call_method(self.module.search_recon_notifications, limit=3)

        self.assert_no_error(result, context="search_recon_notifications details")

        if not isinstance(result, list) or len(result) == 0:
            self.skip_with_warning(
                "No recon notifications available — skipping details field validation",
                context="search_recon_notifications full details",
            )
            return

        # Full details should have more than just an id field
        first = result[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        # A detailed notification has status and rule metadata at minimum
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_notifications_with_filter(self):
        """Test search with a simple FQL filter."""
        result = self.call_method(
            self.module.search_recon_notifications,
            filter="status:'new'",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications filter=status:'new'")

    def test_search_recon_notifications_with_sort(self):
        """Test sort parameter accepted by the API."""
        result = self.call_method(
            self.module.search_recon_notifications,
            sort="created_date|desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications sort=created_date|desc")

    def test_search_recon_notifications_with_q(self):
        """Test free-text q parameter."""
        result = self.call_method(
            self.module.search_recon_notifications,
            q="domain",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications q=domain")

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    def test_search_recon_rules_operation_names(self):
        """Validate QueryRulesV1 and GetRulesV1 operation names."""
        result = self.call_method(self.module.search_recon_rules, limit=1)
        self.assert_no_error(result, context="QueryRulesV1 / GetRulesV1 validation")

    def test_search_recon_rules_returns_list(self):
        """Test that rule search returns a list or empty-response dict."""
        result = self.call_method(self.module.search_recon_rules, limit=5)

        self.assert_no_error(result, context="search_recon_rules")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_recon_rules")

    def test_search_recon_rules_returns_full_details(self):
        """Test that rule results contain full rule definition, not just IDs."""
        result = self.call_method(self.module.search_recon_rules, limit=3)

        self.assert_no_error(result, context="search_recon_rules details")

        if not isinstance(result, list) or len(result) == 0:
            self.skip_with_warning(
                "No recon rules available — skipping details field validation",
                context="search_recon_rules full details",
            )
            return

        first = result[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_rules_with_filter(self):
        """Test rule search with status filter."""
        result = self.call_method(
            self.module.search_recon_rules,
            filter="status:'active'",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_rules filter=status:'active'")

    # ------------------------------------------------------------------
    # Exposed-data records
    # ------------------------------------------------------------------

    def test_search_recon_exposed_data_records_operation_names(self):
        """Validate QueryNotificationsExposedDataRecordsV1 and GetNotificationsExposedDataRecordsV1 names."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=1)
        self.assert_no_error(
            result,
            context="QueryNotificationsExposedDataRecordsV1 / GetNotificationsExposedDataRecordsV1 validation",
        )

    def test_search_recon_exposed_data_records_returns_list(self):
        """Test that exposed-data search returns a list or empty-response dict."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=5)

        self.assert_no_error(result, context="search_recon_exposed_data_records")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_recon_exposed_data_records"
            )

    def test_search_recon_exposed_data_records_returns_full_details(self):
        """Test that exposed-data results contain full record detail, not just IDs."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=3)

        self.assert_no_error(result, context="search_recon_exposed_data_records details")

        if not isinstance(result, list) or len(result) == 0:
            self.skip_with_warning(
                "No exposed-data records available — skipping details field validation",
                context="search_recon_exposed_data_records full details",
            )
            return

        first = result[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_exposed_data_records_with_sort(self):
        """Test sort parameter accepted by the API."""
        result = self.call_method(
            self.module.search_recon_exposed_data_records,
            sort="created_date|desc",
            limit=3,
        )
        self.assert_no_error(
            result, context="search_recon_exposed_data_records sort=created_date|desc"
        )
