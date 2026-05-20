"""Tests for the Correlation Rules module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.correlation_rules import CorrelationRulesModule
from tests.modules.utils.test_modules import TestModules


class TestCorrelationRulesModule(TestModules):
    """Test cases for the Correlation Rules module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CorrelationRulesModule)

    # -------------------------------------------------------------------------
    # Registration Tests
    # -------------------------------------------------------------------------

    def test_register_tools(self):
        """Test that all 4 correlation rule tools are registered with correct prefixed names."""
        expected_tools = [
            "falcon_search_correlation_rules",
            "falcon_create_correlation_rule",
            "falcon_update_correlation_rule",
            "falcon_delete_correlation_rules",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test that the FQL guide resource is registered."""
        expected_resources = [
            "falcon_search_correlation_rules_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # -------------------------------------------------------------------------
    # Annotation Tests
    # -------------------------------------------------------------------------

    def test_read_only_tools_have_default_annotations(self):
        """Test that search tool uses READ_ONLY_ANNOTATIONS."""
        self.module.register_tools(self.mock_server)

        for tool_name in [
            "falcon_search_correlation_rules",
        ]:
            self.assert_tool_annotations(tool_name, READ_ONLY_ANNOTATIONS)

    def test_create_tool_annotations(self):
        """Test that create tool has non-read-only, non-destructive, non-idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_correlation_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_tool_annotations(self):
        """Test that update tool has non-read-only, non-destructive, idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_correlation_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_delete_tool_annotations(self):
        """Test that delete tool has destructive and idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_correlation_rules",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    # -------------------------------------------------------------------------
    # Search Tests
    # -------------------------------------------------------------------------

    def test_search_success(self):
        """Test searching correlation rules returns full rule objects directly."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v1", "rule_id": "r1", "name": "Test Rule", "severity": 70},
                {"id": "v2", "rule_id": "r2", "name": "Test Rule 2", "severity": 30},
            ]},
        }

        result = self.module.search_correlation_rules(
            filter="severity:>50",
            limit=10,
            offset=0,
            sort="last_updated_on.desc",
        )

        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "combined_rules_get_v2")
        self.assertEqual(call_args[1]["parameters"]["filter"], "severity:>50")
        self.assertEqual(call_args[1]["parameters"]["limit"], 10)
        self.assertEqual(call_args[1]["parameters"]["offset"], 0)
        self.assertEqual(call_args[1]["parameters"]["sort"], "last_updated_on.desc")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["rule_id"], "r1")
        self.assertEqual(result[1]["rule_id"], "r2")

    def test_search_with_filter(self):
        """Test that filter param is passed through to the API call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v1", "rule_id": "r1", "name": "Tactic Rule", "severity": 60},
            ]},
        }

        self.module.search_correlation_rules(filter="tactic:'TA0001'")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], "tactic:'TA0001'")

    def test_search_empty_results_returns_fql_guide(self):
        """Test that empty resources return a dict with fql_guide key."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_correlation_rules(filter="name:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["results"], [])
        self.assertIn("No results matched", result["hint"])

    def test_search_error_returns_fql_guide(self):
        """Test that API errors return a dict with fql_guide and error info."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter expression"}]},
        }

        result = self.module.search_correlation_rules(filter="bad filter!!!")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])

    # -------------------------------------------------------------------------
    # Create Tests
    # -------------------------------------------------------------------------

    def test_create_success(self):
        """Test creating a rule with required params applies correct defaults in the body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v1", "rule_id": "r1", "name": "Test Rule", "severity": 70}
            ]},
        }

        result = self.module.create_correlation_rule(
            customer_id="cid123",
            name="Test Rule",
            search_filter="#event=ProcessRollup2",
            severity=70,
            search_outcome="detection",
            lookback="1h0m",
            schedule="@every 1h0m",
            status="active",
            trigger_mode="summary",
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_rules_post_v1")

        body = call_args[1]["body"]
        self.assertEqual(body["customer_id"], "cid123")
        self.assertEqual(body["name"], "Test Rule")
        self.assertEqual(body["severity"], 70)
        self.assertEqual(body["status"], "active")
        self.assertEqual(body["search"]["filter"], "#event=ProcessRollup2")
        self.assertEqual(body["search"]["outcome"], "detection")
        self.assertEqual(body["search"]["lookback"], "1h0m")
        self.assertEqual(body["search"]["trigger_mode"], "summary")
        self.assertNotIn("execution_mode", body["search"])
        self.assertNotIn("use_ingest_time", body["search"])
        self.assertEqual(body["operation"]["schedule"]["definition"], "@every 1h0m")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_create_with_optional_params(self):
        """Test that description, tactic, technique, and comment appear in the body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v1", "rule_id": "r1", "name": "Rule"}]},
        }

        self.module.create_correlation_rule(
            customer_id="cid123",
            name="Rule",
            search_filter="#event=ProcessRollup2",
            severity=50,
            description="Detects suspicious activity",
            tactic="TA0001",
            technique="T1059",
            comment="Creating for audit trail",
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["description"], "Detects suspicious activity")
        self.assertEqual(body["tactic"], "TA0001")
        self.assertEqual(body["technique"], "T1059")
        self.assertEqual(body["comment"], "Creating for audit trail")

    def test_create_custom_defaults(self):
        """Test overriding search_outcome, lookback, schedule, status, and trigger_mode."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v1", "rule_id": "r1", "name": "Rule"}]},
        }

        self.module.create_correlation_rule(
            customer_id="cid123",
            name="Rule",
            search_filter="#event=ProcessRollup2",
            severity=25,
            search_outcome="case",
            lookback="24h0m",
            schedule="@every 24h0m",
            status="inactive",
            trigger_mode="per_event",
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["status"], "inactive")
        self.assertEqual(body["search"]["outcome"], "case")
        self.assertEqual(body["search"]["lookback"], "24h0m")
        self.assertEqual(body["search"]["trigger_mode"], "per_event")
        self.assertEqual(body["operation"]["schedule"]["definition"], "@every 24h0m")

    def test_create_error_returns_error_list(self):
        """Test that a create API error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Validation failed"}]},
        }

        result = self.module.create_correlation_rule(
            customer_id="cid123",
            name="Bad Rule",
            search_filter="invalid",
            severity=50,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Update Tests
    # -------------------------------------------------------------------------

    def test_update_success(self):
        """Test updating a rule sends the rule_id plus changed fields in the body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v2", "rule_id": "r1", "name": "Updated Rule", "severity": 90}
            ]},
        }

        result = self.module.update_correlation_rule(
            rule_id="r1",
            name="Updated Rule",
            severity=90,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_rules_patch_v1")
        body = call_args[1]["body"][0]
        self.assertEqual(body["id"], "r1")
        self.assertEqual(body["name"], "Updated Rule")
        self.assertEqual(body["severity"], 90)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_update_partial(self):
        """Test that only rule_id + name appear in body when only name is provided."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1", "name": "New Name"}]},
        }

        self.module.update_correlation_rule(
            rule_id="r1",
            name="New Name",
            description=None,
            status=None,
            severity=None,
            search_filter=None,
            lookback=None,
            trigger_mode=None,
            tactic=None,
            technique=None,
            comment=None,
        )

        body = self.mock_client.command.call_args[1]["body"][0]
        self.assertEqual(body["id"], "r1")
        self.assertEqual(body["name"], "New Name")
        self.assertNotIn("search", body)
        self.assertNotIn("severity", body)
        self.assertNotIn("status", body)

    def test_update_search_fields_nested(self):
        """Test that search_filter, lookback, and trigger_mode go into body['search']."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1"}]},
        }

        self.module.update_correlation_rule(
            rule_id="r1",
            search_filter="#event=NetworkConnect",
            lookback="24h0m",
            trigger_mode="per_event",
        )

        body = self.mock_client.command.call_args[1]["body"][0]
        self.assertIn("search", body)
        self.assertEqual(body["search"]["filter"], "#event=NetworkConnect")
        self.assertEqual(body["search"]["lookback"], "24h0m")
        self.assertEqual(body["search"]["trigger_mode"], "per_event")

    def test_update_error_returns_error_list(self):
        """Test that an update API error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "Rule not found"}]},
        }

        result = self.module.update_correlation_rule(rule_id="nonexistent", name="New Name")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Delete Tests
    # -------------------------------------------------------------------------

    def test_delete_success(self):
        """Test deleting rules passes ids in query parameters."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.delete_correlation_rules(ids=["r1", "r2"])

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_rules_delete_v1")
        self.assertIn("parameters", call_args[1])
        self.assertEqual(call_args[1]["parameters"]["ids"], ["r1", "r2"])

        self.assertIsInstance(result, list)

    def test_delete_with_comment(self):
        """Test that comment is included in query parameters when provided."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.delete_correlation_rules(ids=["r1"], comment="Removing stale rule")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["comment"], "Removing stale rule")
        self.assertEqual(call_args[1]["parameters"]["ids"], ["r1"])

    def test_delete_empty_ids_returns_error(self):
        """Test that empty ids list returns an error without calling the API."""
        result = self.module.delete_correlation_rules(ids=[])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # -------------------------------------------------------------------------
    # Security Validation Tests
    # -------------------------------------------------------------------------

    def test_search_with_special_characters_in_filter(self):
        """Test that special characters in filter are passed safely to the API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "name:*';DROP TABLE--*"
        self.module.search_correlation_rules(filter=filter_with_special)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_create_permission_error(self):
        """Test that a 403 permission error on create returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.create_correlation_rule(
            customer_id="cid123",
            name="Unauthorized Rule",
            search_filter="#event=ProcessRollup2",
            severity=50,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_delete_permission_error(self):
        """Test that a 403 permission error on delete returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.delete_correlation_rules(ids=["r1"])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_with_long_filter_value(self):
        """Test that extremely long filter values are passed through to the API."""
        long_value = "x" * 10000
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.search_correlation_rules(filter=f"name:'{long_value}'")

        call_args = self.mock_client.command.call_args
        self.assertIn(long_value, call_args[1]["parameters"]["filter"])


if __name__ == "__main__":
    unittest.main()
