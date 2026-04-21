"""Tests for the Shield (SaaS Security) module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.shield import IMPACT_MAP, ShieldModule
from tests.modules.utils.test_modules import TestModules


class TestShieldModule(TestModules):
    """Test cases for the Shield module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ShieldModule)

    # --- Registration tests ---

    def test_register_tools(self):
        """Test registering all 14 tools with the server."""
        expected_tools = [
            "falcon_search_shield_checks",
            "falcon_get_shield_check_affected_entities",
            "falcon_get_shield_posture_metrics",
            "falcon_get_shield_check_compliance",
            "falcon_search_shield_alerts",
            "falcon_get_shield_activity_monitor",
            "falcon_search_shield_users",
            "falcon_search_shield_devices",
            "falcon_search_shield_apps",
            "falcon_get_shield_app_users",
            "falcon_search_shield_data_shares",
            "falcon_get_shield_integrations",
            "falcon_get_shield_system_users",
            "falcon_dismiss_shield_check",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering the query parameter guide resource."""
        expected_resources = [
            "falcon_shield_query_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # --- Annotation tests ---

    def test_search_shield_checks_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_checks", READ_ONLY_ANNOTATIONS)

    def test_get_shield_check_affected_entities_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_get_shield_check_affected_entities", READ_ONLY_ANNOTATIONS
        )

    def test_get_shield_posture_metrics_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_posture_metrics", READ_ONLY_ANNOTATIONS)

    def test_get_shield_check_compliance_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_check_compliance", READ_ONLY_ANNOTATIONS)

    def test_search_shield_alerts_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_alerts", READ_ONLY_ANNOTATIONS)

    def test_get_shield_activity_monitor_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_activity_monitor", READ_ONLY_ANNOTATIONS)

    def test_search_shield_users_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_users", READ_ONLY_ANNOTATIONS)

    def test_search_shield_devices_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_devices", READ_ONLY_ANNOTATIONS)

    def test_search_shield_apps_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_apps", READ_ONLY_ANNOTATIONS)

    def test_get_shield_app_users_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_app_users", READ_ONLY_ANNOTATIONS)

    def test_search_shield_data_shares_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_shield_data_shares", READ_ONLY_ANNOTATIONS)

    def test_get_shield_integrations_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_integrations", READ_ONLY_ANNOTATIONS)

    def test_get_shield_system_users_has_read_only_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_shield_system_users", READ_ONLY_ANNOTATIONS)

    def test_dismiss_shield_check_has_destructive_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_dismiss_shield_check",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    # --- Impact mapping tests ---

    def test_impact_map_values(self):
        self.assertEqual(IMPACT_MAP["low"], 1)
        self.assertEqual(IMPACT_MAP["medium"], 2)
        self.assertEqual(IMPACT_MAP["high"], 3)

    def test_map_impact_low(self):
        self.assertEqual(self.module._map_impact("Low"), 1)

    def test_map_impact_high(self):
        self.assertEqual(self.module._map_impact("High"), 3)

    def test_map_impact_none(self):
        self.assertIsNone(self.module._map_impact(None))

    def test_map_impact_case_insensitive(self):
        self.assertEqual(self.module._map_impact("low"), 1)
        self.assertEqual(self.module._map_impact("MEDIUM"), 2)
        self.assertEqual(self.module._map_impact("high"), 3)

    def test_map_impact_invalid_string_returns_none(self):
        self.assertIsNone(self.module._map_impact("critical"))

    def test_map_impact_invalid_string_logs_warning(self):
        with self.assertLogs("falcon_mcp.modules.shield", level="WARNING") as cm:
            self.module._map_impact("critical")
        self.assertTrue(any("critical" in msg for msg in cm.output))

    # --- Functional tests: search_shield_checks ---

    def test_search_shield_checks_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "check-1", "name": "MFA Enabled", "status": "Failed", "impact": 3}
                ]
            },
        }

        result = self.module.search_shield_checks(status="Failed", impact="High", limit=10)

        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSecurityChecksV3")
        self.assertEqual(call_args[1]["parameters"]["status"], "Failed")
        self.assertEqual(call_args[1]["parameters"]["impact"], 3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "check-1")

    def test_search_shield_checks_empty_results(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_shield_checks()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("query_guide", result)

    def test_search_shield_checks_api_error(self):
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad Request"}]},
        }

        result = self.module.search_shield_checks()

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])
        self.assertIn("query_guide", result)

    # --- Functional tests: get_shield_check_affected_entities ---

    def test_get_shield_check_affected_entities_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"entity_name": "user@example.com", "type": "user", "dismissed": False}
                ]
            },
        }

        result = self.module.get_shield_check_affected_entities(id="check-1", limit=10)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSecurityCheckAffectedV3")
        self.assertEqual(call_args[1]["parameters"]["id"], "check-1")
        self.assertEqual(len(result), 1)

    def test_get_shield_check_affected_entities_empty(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_shield_check_affected_entities(id="check-1")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])

    # --- Functional tests: get_shield_posture_metrics ---

    def test_get_shield_posture_metrics_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"total_security_checks_count": 50, "total_score_percentage": 72}]
            },
        }

        result = self.module.get_shield_posture_metrics(impact="Medium")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetMetricsV3")
        self.assertEqual(call_args[1]["parameters"]["impact"], 2)
        self.assertEqual(len(result), 1)

    # --- Functional tests: get_shield_check_compliance ---

    def test_get_shield_check_compliance_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"standard": "SOC 2", "control": "CC6.1", "requirement": "Logical access"}
                ]
            },
        }

        result = self.module.get_shield_check_compliance(id="check-1")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSecurityCheckComplianceV3")
        self.assertEqual(call_args[1]["parameters"]["id"], "check-1")
        self.assertEqual(len(result), 1)

    # --- Functional tests: search_shield_alerts ---

    def test_search_shield_alerts_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "alert-1", "alert_type": "configuration_drift"}]},
        }

        result = self.module.search_shield_alerts(type="configuration_drift", limit=5)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetAlertsV3")
        self.assertEqual(call_args[1]["parameters"]["type"], "configuration_drift")
        self.assertEqual(len(result), 1)

    def test_search_shield_alerts_empty(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_shield_alerts()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])

    # --- Functional tests: get_shield_activity_monitor ---

    def test_get_shield_activity_monitor_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"event_name": "file_shared", "actor": "user@example.com"}]},
        }

        result = self.module.get_shield_activity_monitor(category="Events", limit=100)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetActivityMonitorV3")
        self.assertEqual(call_args[1]["parameters"]["category"], "Events")
        self.assertEqual(len(result), 1)

    # --- Functional tests: search_shield_users ---

    def test_search_shield_users_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"email": "admin@example.com", "privileged": True}]},
        }

        result = self.module.search_shield_users(privileged_only=True, limit=10)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetUserInventoryV3")
        self.assertEqual(call_args[1]["parameters"]["privileged_only"], True)
        self.assertEqual(len(result), 1)

    # --- Functional tests: search_shield_devices ---

    def test_search_shield_devices_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_name": "laptop-01", "os": "macOS", "globally_compliant": True}
                ]
            },
        }

        result = self.module.search_shield_devices(limit=10)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetDeviceInventoryV3")
        self.assertEqual(len(result), 1)

    # --- Functional tests: search_shield_apps ---

    def test_search_shield_apps_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"app_name": "Slack", "app_type": "oauth", "access_level": "high"}]
            },
        }

        result = self.module.search_shield_apps(type="oauth", access_level="high")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetAppInventory")
        self.assertEqual(call_args[1]["parameters"]["type"], "oauth")
        self.assertEqual(len(result), 1)

    # --- Functional tests: get_shield_app_users ---

    def test_get_shield_app_users_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"username": "user@example.com", "permission_grant_id": "grant-1"}]
            },
        }

        result = self.module.get_shield_app_users(item_id="integration-1|||app-1")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetAppInventoryUsers")
        self.assertEqual(call_args[1]["parameters"]["item_id"], "integration-1|||app-1")
        self.assertEqual(len(result), 1)

    # --- Functional tests: search_shield_data_shares ---

    def test_search_shield_data_shares_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"resource_name": "report.xlsx", "access_level": "external"}]},
        }

        result = self.module.search_shield_data_shares(resource_type="XLSX", limit=10)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetAssetInventoryV3")
        self.assertEqual(call_args[1]["parameters"]["resource_type"], "XLSX")
        self.assertEqual(len(result), 1)

    # --- Functional tests: get_shield_integrations ---

    def test_get_shield_integrations_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "int-1", "alias": "Production Google", "saas_name": "Google Workspace"}
                ]
            },
        }

        result = self.module.get_shield_integrations()

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetIntegrationsV3")
        self.assertEqual(len(result), 1)

    # --- Functional tests: get_shield_system_users ---

    def test_get_shield_system_users_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"email": "admin@cs.com", "role": "admin", "mfa_enabled": True}]
            },
        }

        result = self.module.get_shield_system_users()

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetSystemUsersV3")
        self.assertEqual(len(result), 1)

    # --- Functional tests: dismiss_shield_check ---

    def test_dismiss_shield_check_whole_check(self):
        """Without entities, dismisses the entire check via DismissSecurityCheckV3."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "check-1", "status": "Dismissed"}]},
        }

        result = self.module.dismiss_shield_check(id="check-1", reason="Accepted risk")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "DismissSecurityCheckV3")
        self.assertEqual(call_args[1]["body"]["id"], "check-1")
        self.assertEqual(call_args[1]["body"]["reason"], "Accepted risk")
        self.assertEqual(len(result), 1)

    def test_dismiss_shield_check_specific_entities(self):
        """With entities, dismisses specific entities via DismissAffectedEntityV3."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "check-1", "dismissed_entities": ["user@ex.com"]}]},
        }

        result = self.module.dismiss_shield_check(
            id="check-1", reason="User exception", entities="user@ex.com,admin@ex.com"
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "DismissAffectedEntityV3")
        self.assertEqual(call_args[1]["body"]["id"], "check-1")
        self.assertEqual(call_args[1]["body"]["reason"], "User exception")
        self.assertEqual(call_args[1]["body"]["entities"], ["user@ex.com", "admin@ex.com"])
        self.assertEqual(len(result), 1)

    def test_dismiss_shield_check_api_error(self):
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.dismiss_shield_check(id="check-1", reason="Test")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    # --- Security validation tests ---

    def test_search_shield_checks_special_characters_pass_through(self):
        """Special characters in filter params pass through unchanged."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_shield_checks(
            id="check-';DROP TABLE--", check_type="<script>alert(1)</script>"
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["id"], "check-';DROP TABLE--")
        self.assertEqual(call_args[1]["parameters"]["check_type"], "<script>alert(1)</script>")

    def test_search_shield_checks_invalid_id_returns_api_error(self):
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "Not found"}]},
        }

        result = self.module.search_shield_checks(id="not-a-real-id-!!!")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result["results"][0])

    def test_search_shield_checks_permission_error(self):
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.search_shield_checks()

        self.assertIsInstance(result, dict)
        self.assertIn("error", result["results"][0])

    def test_search_shield_checks_long_input_not_truncated(self):
        """Long input values pass through without truncation."""
        long_value = "a" * 10000
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_shield_checks(check_tags=long_value)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["check_tags"], long_value)


if __name__ == "__main__":
    unittest.main()
