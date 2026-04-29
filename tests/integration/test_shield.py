"""Integration tests for the Shield (SaaS Security) module."""

import pytest

from falcon_mcp.modules.shield import ShieldModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestShieldIntegration(BaseIntegrationTest):
    """Integration tests for Shield module with real API calls.

    Validates:
    - Correct FalconPy operation names for all 13 read-only tools
    - Direct GET endpoints return full entity details (no two-step pattern)
    - Impact string normalization works against real API
    - Dismiss tool (DismissSecurityCheckV3/DismissAffectedEntityV3) is skipped
      — write operations are not run in integration tests

    Note: SaaS Security endpoints may return empty results if no SaaS
    integrations are configured. Tests accept empty lists as valid.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Shield module with a real client."""
        self.module = ShieldModule(falcon_client)

    # --- Core posture tools ---

    def test_search_shield_checks(self):
        """Validate GetSecurityChecksV3 operation name and response shape."""
        result = self.call_method(self.module.search_shield_checks, limit=5)

        self.assert_no_error(result, context="search_shield_checks")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_shield_checks")

    def test_search_shield_checks_with_impact_filter(self):
        """Validate impact string normalization works against real API."""
        result = self.call_method(
            self.module.search_shield_checks,
            impact="High",
            limit=3,
        )

        self.assert_no_error(result, context="search_shield_checks with impact")

    def test_get_shield_check_affected_entities(self):
        """Validate GetSecurityCheckAffectedV3 with a real check ID."""
        checks = self.call_method(self.module.search_shield_checks, limit=1)

        if not isinstance(checks, list) or len(checks) == 0:
            self.skip_with_warning(
                "No security checks available",
                context="get_shield_check_affected_entities",
            )

        check_id = self.get_first_id(checks, id_field="id")
        if not check_id:
            self.skip_with_warning(
                "Could not extract check ID",
                context="get_shield_check_affected_entities",
            )

        result = self.call_method(
            self.module.get_shield_check_affected_entities,
            id=check_id,
            limit=5,
        )

        self.assert_no_error(result, context="get_shield_check_affected_entities")

    def test_get_shield_posture_metrics(self):
        """Validate GetMetricsV3 operation name and response shape."""
        result = self.call_method(self.module.get_shield_posture_metrics, limit=5)

        self.assert_no_error(result, context="get_shield_posture_metrics")

    def test_get_shield_check_compliance(self):
        """Validate GetSecurityCheckComplianceV3 with a real check ID."""
        checks = self.call_method(self.module.search_shield_checks, limit=1)

        if not isinstance(checks, list) or len(checks) == 0:
            self.skip_with_warning(
                "No security checks available",
                context="get_shield_check_compliance",
            )

        check_id = self.get_first_id(checks, id_field="id")
        if not check_id:
            self.skip_with_warning(
                "Could not extract check ID",
                context="get_shield_check_compliance",
            )

        result = self.call_method(
            self.module.get_shield_check_compliance,
            id=check_id,
        )

        self.assert_no_error(result, context="get_shield_check_compliance")

    # --- Alerts & activity ---

    def test_search_shield_alerts(self):
        """Validate GetAlertsV3 operation name and response shape."""
        result = self.call_method(self.module.search_shield_alerts, limit=5)

        self.assert_no_error(result, context="search_shield_alerts")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_shield_alerts")

    def test_get_shield_activity_monitor(self):
        """Validate GetActivityMonitorV3 operation name and response shape."""
        result = self.call_method(self.module.get_shield_activity_monitor, limit=5)

        self.assert_no_error(result, context="get_shield_activity_monitor")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="get_shield_activity_monitor"
            )

    # --- Inventory tools ---

    def test_search_shield_users(self):
        """Validate GetUserInventoryV3 operation name and response shape."""
        result = self.call_method(self.module.search_shield_users, limit=5)

        self.assert_no_error(result, context="search_shield_users")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_shield_users")

    def test_search_shield_devices(self):
        """Validate GetDeviceInventoryV3 operation name and response shape."""
        result = self.call_method(self.module.search_shield_devices, limit=5)

        self.assert_no_error(result, context="search_shield_devices")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_shield_devices")

    def test_search_shield_apps(self):
        """Validate GetAppInventory operation name and response shape."""
        result = self.call_method(self.module.search_shield_apps, limit=5)

        self.assert_no_error(result, context="search_shield_apps")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="search_shield_apps")

    def test_get_shield_app_users(self):
        """Validate GetAppInventoryUsers with a real app ID.

        Requires apps to exist; skips gracefully if none configured.
        """
        apps = self.call_method(self.module.search_shield_apps, limit=1)

        if not isinstance(apps, list) or len(apps) == 0:
            self.skip_with_warning(
                "No apps available to test app users",
                context="get_shield_app_users",
            )

        first_app = apps[0]
        if not isinstance(first_app, dict):
            self.skip_with_warning(
                "Unexpected app response shape",
                context="get_shield_app_users",
            )

        item_id = first_app.get("item_id") or first_app.get("id")
        if not item_id:
            self.skip_with_warning(
                "Could not extract app item_id",
                context="get_shield_app_users",
            )

        result = self.call_method(
            self.module.get_shield_app_users,
            item_id=item_id,
        )

        self.assert_no_error(result, context="get_shield_app_users")

    def test_search_shield_data_shares(self):
        """Validate GetAssetInventoryV3 operation name and response shape."""
        result = self.call_method(self.module.search_shield_data_shares, limit=5)

        self.assert_no_error(result, context="search_shield_data_shares")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_shield_data_shares"
            )

    # --- Platform management tools ---

    def test_get_shield_integrations(self):
        """Validate GetIntegrationsV3 operation name and response shape."""
        result = self.call_method(self.module.get_shield_integrations)

        self.assert_no_error(result, context="get_shield_integrations")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="get_shield_integrations"
            )

    def test_get_shield_system_users(self):
        """Validate GetSystemUsersV3 operation name and response shape."""
        result = self.call_method(self.module.get_shield_system_users)

        self.assert_no_error(result, context="get_shield_system_users")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="get_shield_system_users"
            )

    # --- Cross-tool validation ---

    def test_all_read_operation_names_are_correct(self):
        """Validate all 13 read-only operation names produce no errors.

        If any operation name is wrong (typo), the FalconPy client.command()
        call will fail with an error response. This test covers both
        parameterless tools and ID-dependent tools to catch typos in every
        operation name used by the module.
        """
        # 1. GetSecurityChecksV3
        checks = self.call_method(self.module.search_shield_checks, limit=1)
        self.assert_no_error(checks, context="GetSecurityChecksV3")

        # 2. GetMetricsV3
        result = self.call_method(self.module.get_shield_posture_metrics, limit=1)
        self.assert_no_error(result, context="GetMetricsV3")

        # 3. GetAlertsV3
        result = self.call_method(self.module.search_shield_alerts, limit=1)
        self.assert_no_error(result, context="GetAlertsV3")

        # 4. GetActivityMonitorV3
        result = self.call_method(self.module.get_shield_activity_monitor, limit=1)
        self.assert_no_error(result, context="GetActivityMonitorV3")

        # 5. GetUserInventoryV3
        result = self.call_method(self.module.search_shield_users, limit=1)
        self.assert_no_error(result, context="GetUserInventoryV3")

        # 6. GetDeviceInventoryV3
        result = self.call_method(self.module.search_shield_devices, limit=1)
        self.assert_no_error(result, context="GetDeviceInventoryV3")

        # 7. GetAppInventory
        apps = self.call_method(self.module.search_shield_apps, limit=1)
        self.assert_no_error(apps, context="GetAppInventory")

        # 8. GetAssetInventoryV3
        result = self.call_method(self.module.search_shield_data_shares, limit=1)
        self.assert_no_error(result, context="GetAssetInventoryV3")

        # 9. GetIntegrationsV3
        result = self.call_method(self.module.get_shield_integrations)
        self.assert_no_error(result, context="GetIntegrationsV3")

        # 10. GetSystemUsersV3
        result = self.call_method(self.module.get_shield_system_users)
        self.assert_no_error(result, context="GetSystemUsersV3")

        # ID-dependent operations — need a real check ID from step 1
        check_id = None
        if isinstance(checks, list) and len(checks) > 0:
            check_id = self.get_first_id(checks, id_field="id")

        if check_id:
            # 11. GetSecurityCheckAffectedV3
            result = self.call_method(
                self.module.get_shield_check_affected_entities,
                id=check_id,
                limit=1,
            )
            self.assert_no_error(result, context="GetSecurityCheckAffectedV3")

            # 12. GetSecurityCheckComplianceV3
            result = self.call_method(
                self.module.get_shield_check_compliance,
                id=check_id,
            )
            self.assert_no_error(result, context="GetSecurityCheckComplianceV3")

        # ID-dependent: GetAppInventoryUsers — needs a real app item_id
        if isinstance(apps, list) and len(apps) > 0:
            first_app = apps[0]
            if isinstance(first_app, dict):
                app_item_id = first_app.get("item_id") or first_app.get("id")
                if app_item_id:
                    # 13. GetAppInventoryUsers
                    result = self.call_method(
                        self.module.get_shield_app_users,
                        item_id=app_item_id,
                    )
                    self.assert_no_error(result, context="GetAppInventoryUsers")
