"""
Tests for the Recon module.
"""

import unittest

from falcon_mcp.modules.recon import ReconModule
from tests.modules.utils.test_modules import TestModules


class TestReconModule(TestModules):
    """Test cases for the Recon module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ReconModule)

    # ------------------------------------------------------------------
    # Registration tests
    # ------------------------------------------------------------------

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_recon_notifications",
            "falcon_search_recon_rules",
            "falcon_search_recon_exposed_data_records",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_recon_notifications_fql_guide",
            "falcon_search_recon_rules_fql_guide",
            "falcon_search_recon_exposed_data_records_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # ------------------------------------------------------------------
    # search_recon_notifications
    # ------------------------------------------------------------------

    def test_search_recon_notifications_two_step(self):
        """Test two-step search pattern: QueryNotificationsV1 → GetNotificationsDetailedV1."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["notif1", "notif2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "notif1", "status": "new"},
                    {"id": "notif2", "status": "closed-true-positive"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_notifications(filter="status:'new'", limit=10)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryNotificationsV1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "status:'new'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        # Second call must use GET parameters (use_params=True), not POST body
        self.mock_client.command.assert_any_call(
            "GetNotificationsDetailedV1",
            parameters={"ids": ["notif1", "notif2"]},
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "notif1")

    def test_search_recon_notifications_empty(self):
        """Test that empty query results return the empty-response dict (no fql_guide)."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_recon_notifications()

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertNotIn("fql_guide", result)

    def test_search_recon_notifications_fql_error(self):
        """Test that a filter error returns a dict with fql_guide and hint."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid filter"}]},
        }

        result = self.module.search_recon_notifications(filter="bad:filter")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    def test_search_recon_notifications_details_error(self):
        """Test that a details API error returns a list containing the error dict."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["notif1"]},
        }
        details_error = {
            "status_code": 500,
            "body": {"errors": [{"message": "internal error"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_error]

        result = self.module.search_recon_notifications()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # ------------------------------------------------------------------
    # search_recon_rules
    # ------------------------------------------------------------------

    def test_search_recon_rules_two_step(self):
        """Test two-step search pattern: QueryRulesV1 → GetRulesV1."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule1", "rule2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule1", "topic": "SA_DOMAIN", "status": "active"},
                    {"id": "rule2", "topic": "SA_TYPOSQUATTING", "status": "active"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_rules(filter="status:'active'", limit=5)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryRulesV1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "status:'active'")

        self.mock_client.command.assert_any_call(
            "GetRulesV1",
            parameters={"ids": ["rule1", "rule2"]},
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "rule1")

    def test_search_recon_rules_empty(self):
        """Test that empty rule query returns the empty-response dict."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_recon_rules()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertNotIn("fql_guide", result)

    def test_search_recon_rules_fql_error(self):
        """Test that a filter error returns a dict with fql_guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid filter"}]},
        }

        result = self.module.search_recon_rules(filter="bad:filter")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    # ------------------------------------------------------------------
    # search_recon_exposed_data_records
    # ------------------------------------------------------------------

    def test_search_recon_exposed_data_records_two_step(self):
        """Test two-step pattern: QueryNotificationsExposedDataRecordsV1 → GetNotificationsExposedDataRecordsV1."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rec1", "rec2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rec1", "email": "user@example.com", "credential_status": "newly_reported"},
                    {"id": "rec2", "email": "other@example.com", "credential_status": "previously_reported"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_exposed_data_records(
            filter="domain:'example.com'", limit=10
        )

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryNotificationsExposedDataRecordsV1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "domain:'example.com'")

        self.mock_client.command.assert_any_call(
            "GetNotificationsExposedDataRecordsV1",
            parameters={"ids": ["rec1", "rec2"]},
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["email"], "user@example.com")

    def test_search_recon_exposed_data_records_empty(self):
        """Test that empty exposed-data query returns the empty-response dict."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_recon_exposed_data_records()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertNotIn("fql_guide", result)

    def test_search_recon_exposed_data_records_fql_error(self):
        """Test that a filter error returns a dict with fql_guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid filter"}]},
        }

        result = self.module.search_recon_exposed_data_records(filter="bad:filter")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    # ------------------------------------------------------------------
    # Negative / security tests
    # ------------------------------------------------------------------

    def test_limit_max_enforced_by_field(self):
        """Verify limit=500 is accepted (max) and limit=0 would be caught by Field ge=1."""
        # We can't directly test Pydantic validation at the unit level without FastMCP,
        # but we verify the normal path with limit=500 reaches the API correctly.
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_recon_notifications(limit=500)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["limit"], 500)
        self.assertIsInstance(result, dict)

    def test_search_does_not_call_details_when_empty(self):
        """Verify that the details API is NOT called when the query returns no IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_recon_notifications()
        self.module.search_recon_rules()
        self.module.search_recon_exposed_data_records()

        # 3 calls total (one query per tool), no details calls
        self.assertEqual(self.mock_client.command.call_count, 3)


if __name__ == "__main__":
    unittest.main()
