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
        """Test that all 8 correlation rule tools are registered with correct prefixed names."""
        expected_tools = [
            "falcon_search_correlation_rules",
            "falcon_create_correlation_rule",
            "falcon_update_correlation_rule",
            "falcon_delete_correlation_rules",
            "falcon_search_correlation_rule_templates",
            "falcon_deploy_correlation_rule_template",
            "falcon_get_correlation_rule",
            "falcon_get_correlation_rule_template",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test that both FQL guide resources are registered."""
        expected_resources = [
            "falcon_search_correlation_rules_fql_guide",
            "falcon_search_correlation_rule_templates_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_templates_tool_annotations(self):
        """Test that search templates tool uses READ_ONLY_ANNOTATIONS."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_correlation_rule_templates", READ_ONLY_ANNOTATIONS
        )

    # -------------------------------------------------------------------------
    # Annotation Tests
    # -------------------------------------------------------------------------

    def test_read_only_tools_have_default_annotations(self):
        """Test that search tools use READ_ONLY_ANNOTATIONS."""
        self.module.register_tools(self.mock_server)

        for tool_name in [
            "falcon_search_correlation_rules",
            "falcon_search_correlation_rule_templates",
            "falcon_get_correlation_rule",
            "falcon_get_correlation_rule_template",
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
                destructiveHint=True,
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
                {"id": "v1", "rule_id": "r1", "name": "Test Rule", "severity": 70,
                 "search": {"filter": "#event=Test", "lookback": "1h0m"},
                 "operation": {"schedule": {"definition": "@every 1h0m"}},
                 "notifications": [], "customer_id": "cid123"},
                {"id": "v2", "rule_id": "r2", "name": "Test Rule 2", "severity": 30,
                 "search": {"filter": "#event=Other"}, "operation": {}},
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

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["rule_id"], "r1")
        self.assertEqual(result["results"][1]["rule_id"], "r2")

        # Verify slim projection strips non-summary fields
        for rule in result["results"]:
            self.assertNotIn("search", rule)
            self.assertNotIn("operation", rule)
            self.assertNotIn("notifications", rule)
            self.assertNotIn("customer_id", rule)

    def test_search_with_filter(self):
        """Test that filter param is passed through to the API call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v1", "rule_id": "r1", "name": "Tactic Rule", "severity": 60},
            ]},
        }

        self.module.search_correlation_rules(filter="mitre_attack.tactic_id:'TA0001'")

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], "mitre_attack.tactic_id:'TA0001'")

    def test_search_empty_results_returns_fql_guide(self):
        """Test that empty resources return clean empty response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_correlation_rules(filter="name:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])
        self.assertEqual(result["filter_used"], "name:'nonexistent'")
        self.assertNotIn("fql_guide", result)

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
    # Get Rule Tests
    # -------------------------------------------------------------------------

    def test_get_correlation_rule_success(self):
        """Test getting a single rule returns the full unfiltered object."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "v1", "rule_id": "r1", "name": "Test Rule", "severity": 70,
                 "search": {"filter": "#event=Test", "lookback": "1h0m"},
                 "operation": {"schedule": {"definition": "@every 1h0m"}}},
            ]},
        }

        result = self.module.get_correlation_rule(rule_id="r1")

        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "combined_rules_get_v2")
        self.assertEqual(call_args[1]["parameters"]["filter"], "rule_id:'r1'")
        self.assertEqual(call_args[1]["parameters"]["limit"], 1)

        # Full object returned — non-slim fields preserved
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["rule_id"], "r1")
        self.assertIn("search", result[0])
        self.assertIn("operation", result[0])

    def test_get_correlation_rule_not_found(self):
        """Test that a missing rule returns a clean error."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_correlation_rule(rule_id="nonexistent")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_get_correlation_rule_api_error(self):
        """Test that an API error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal error"}]},
        }

        result = self.module.get_correlation_rule(rule_id="r1")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

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
            use_ingest_time=False,
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
        self.assertEqual(body["search"]["use_ingest_time"], False)
        self.assertEqual(body["operation"]["schedule"]["definition"], "@every 1h0m")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_create_with_optional_params(self):
        """Test that description, mitre_attack, and comment appear in the body."""
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
            mitre_attack=[{"tactic_id": "TA0001", "technique_id": "T1059"}],
            comment="Creating for audit trail",
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["description"], "Detects suspicious activity")
        self.assertEqual(
            body["mitre_attack"],
            [{"tactic_id": "TA0001", "technique_id": "T1059"}],
        )
        self.assertEqual(body["comment"], "Creating for audit trail")

    def test_create_custom_defaults(self):
        """Test overriding search_outcome, lookback, schedule, status, trigger_mode, and use_ingest_time."""
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
            trigger_mode="verbose",
            use_ingest_time=True,
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["status"], "inactive")
        self.assertEqual(body["search"]["outcome"], "case")
        self.assertEqual(body["search"]["lookback"], "24h0m")
        self.assertEqual(body["search"]["trigger_mode"], "verbose")
        self.assertEqual(body["search"]["use_ingest_time"], True)
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
            use_ingest_time=None,
            schedule=None,
            mitre_attack=None,
            comment=None,
        )

        body = self.mock_client.command.call_args[1]["body"][0]
        self.assertEqual(body["id"], "r1")
        self.assertEqual(body["name"], "New Name")
        self.assertNotIn("search", body)
        self.assertNotIn("operation", body)
        self.assertNotIn("severity", body)
        self.assertNotIn("status", body)

    def test_update_search_fields_nested(self):
        """Test that search_filter, lookback, trigger_mode, and use_ingest_time go into body['search']."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1"}]},
        }

        self.module.update_correlation_rule(
            rule_id="r1",
            search_filter="#event=NetworkConnect",
            lookback="24h0m",
            trigger_mode="verbose",
            use_ingest_time=True,
        )

        body = self.mock_client.command.call_args[1]["body"][0]
        self.assertIn("search", body)
        self.assertEqual(body["search"]["filter"], "#event=NetworkConnect")
        self.assertEqual(body["search"]["lookback"], "24h0m")
        self.assertEqual(body["search"]["trigger_mode"], "verbose")
        self.assertEqual(body["search"]["use_ingest_time"], True)

    def test_update_schedule(self):
        """Test that schedule goes into body['operation']['schedule']['definition']."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1"}]},
        }

        self.module.update_correlation_rule(
            rule_id="r1",
            schedule="@every 1h30m",
            name=None,
            description=None,
            status=None,
            severity=None,
            search_filter=None,
            lookback=None,
            trigger_mode=None,
            use_ingest_time=None,
            mitre_attack=None,
            comment=None,
        )

        body = self.mock_client.command.call_args[1]["body"][0]
        self.assertIn("operation", body)
        self.assertEqual(body["operation"]["schedule"]["definition"], "@every 1h30m")
        self.assertNotIn("search", body)

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

    def test_update_only_schedule_no_validation(self):
        """Test that providing only schedule (no lookback) skips validation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1"}]},
        }

        result = self.module.update_correlation_rule(rule_id="r1", schedule="@every 2h0m")

        self.mock_client.command.assert_called_once()
        self.assertIsInstance(result, list)

    def test_update_only_lookback_no_validation(self):
        """Test that providing only lookback (no schedule) skips validation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "v2", "rule_id": "r1"}]},
        }

        result = self.module.update_correlation_rule(rule_id="r1", lookback="0h30m")

        self.mock_client.command.assert_called_once()
        self.assertIsInstance(result, list)

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

    # -------------------------------------------------------------------------
    # Search Templates Tests
    # -------------------------------------------------------------------------

    def test_search_templates_success(self):
        """Test searching templates uses query+hydrate pattern and returns full objects."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["tmpl-1", "tmpl-2"],
                    "meta": {"pagination": {"total": 2}},
                },
            },
            {
                "status_code": 200,
                "body": {"resources": [
                    {"id": "tmpl-1", "name": "Lateral Movement Detection", "severity": 70,
                     "search": {"filter": "#event=NetworkConnect"}, "operation": {},
                     "license_details": {}, "execution_mode": "standard", "type": "correlation"},
                    {"id": "tmpl-2", "name": "Credential Theft Alert", "severity": 90,
                     "search": {"filter": "#event=Auth"}, "operation": {},
                     "license_details": {}, "type": "correlation"},
                ]},
            },
        ]

        result = self.module.search_correlation_rule_templates(
            filter="mitre_attack.tactic_id:'TA0008'",
            limit=10,
        )

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "queries_templates_get_v1Mixin0")
        self.assertEqual(first_call[1]["parameters"]["filter"], "mitre_attack.tactic_id:'TA0008'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "entities_templates_get_v1Mixin0")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "tmpl-1")
        self.assertEqual(result["results"][1]["id"], "tmpl-2")
        self.assertEqual(result["pagination"]["total"], 2)

        # Verify slim projection strips non-summary fields
        for tmpl in result["results"]:
            self.assertNotIn("search", tmpl)
            self.assertNotIn("operation", tmpl)
            self.assertNotIn("license_details", tmpl)
            self.assertNotIn("execution_mode", tmpl)
            self.assertNotIn("type", tmpl)

    def test_search_templates_empty_results(self):
        """Test that empty query results return clean empty envelope."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_correlation_rule_templates(
            filter="name:'nonexistent'"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["filter_used"], "name:'nonexistent'")
        self.assertNotIn("fql_guide", result)
        self.mock_client.command.assert_called_once()

    def test_search_templates_query_error_returns_fql_guide(self):
        """Test that query-step API errors return a dict with fql_guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_correlation_rule_templates(filter="bad!!!")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])

    def test_search_templates_hydrate_error_returns_error_list(self):
        """Test that hydrate-step API errors return the error directly, not an FQL guide."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["tmpl-1"],
                    "meta": {"pagination": {"total": 1}},
                },
            },
            {
                "status_code": 500,
                "body": {"errors": [{"message": "Internal error"}]},
            },
        ]

        result = self.module.search_correlation_rule_templates()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_templates_preserves_sort_order(self):
        """Test that hydrated results are reordered to match query ID order."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["tmpl-a", "tmpl-b", "tmpl-c"],
                    "meta": {"pagination": {"total": 3}},
                },
            },
            {
                "status_code": 200,
                "body": {"resources": [
                    {"id": "tmpl-c", "name": "C"},
                    {"id": "tmpl-a", "name": "A"},
                    {"id": "tmpl-b", "name": "B"},
                ]},
            },
        ]

        result = self.module.search_correlation_rule_templates(
            sort="last_updated_on|desc"
        )

        self.assertEqual(result["results"][0]["id"], "tmpl-a")
        self.assertEqual(result["results"][1]["id"], "tmpl-b")
        self.assertEqual(result["results"][2]["id"], "tmpl-c")

    # -------------------------------------------------------------------------
    # Get Template Tests
    # -------------------------------------------------------------------------

    def test_get_correlation_rule_template_success(self):
        """Test getting a single template returns the full unfiltered object."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [
                {"id": "tmpl-1", "name": "Lateral Movement Detection", "severity": 70,
                 "search": {"filter": "#event=NetworkConnect", "lookback": "2h0m"},
                 "operation": {"schedule": {"definition": "@every 2h0m"}},
                 "license_details": {"tier": "standard"}},
            ]},
        }

        result = self.module.get_correlation_rule_template(id="tmpl-1")

        self.mock_client.command.assert_called_once()
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_templates_get_v1Mixin0")

        # Full object returned — non-slim fields preserved
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "tmpl-1")
        self.assertIn("search", result[0])
        self.assertIn("operation", result[0])
        self.assertIn("license_details", result[0])

    def test_get_correlation_rule_template_not_found(self):
        """Test that a missing template returns a clean error."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_correlation_rule_template(id="nonexistent")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_get_correlation_rule_template_api_error(self):
        """Test that an API error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal error"}]},
        }

        result = self.module.get_correlation_rule_template(id="tmpl-1")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Deploy Template Tests
    # -------------------------------------------------------------------------

    def test_deploy_template_tool_annotations(self):
        """Test that deploy template tool has non-read-only, non-destructive, non-idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_deploy_correlation_rule_template",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_deploy_template_success_with_defaults(self):
        """Test deploying a template with only required params uses template defaults."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Lateral Movement via SMB",
                    "description": "Detects SMB lateral movement",
                    "severity": 70,
                    "search": {
                        "filter": "#event_simpleName=NetworkConnect",
                        "outcome": "detection",
                        "lookback": "2h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {
                        "schedule": {"definition": "@every 2h0m"},
                    },
                    "mitre_attack": [
                        {"tactic_id": "TA0008", "technique_id": "T1021"},
                    ],
                }]},
            },
            # 2. Duplicate check — no match
            {
                "status_code": 200,
                "body": {
                    "resources": [],
                    "meta": {"pagination": {"total": 0}},
                },
            },
            # 3. Deploy
            {
                "status_code": 200,
                "body": {"resources": [
                    {"id": "v1", "rule_id": "r1", "name": "Lateral Movement via SMB"},
                ]},
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "entities_templates_get_v1Mixin0")

        # The deploy call is now the third (index 2) after the duplicate check
        deploy_call = self.mock_client.command.call_args_list[2]
        self.assertEqual(deploy_call[0][0], "entities_templates_rules_post_v1")
        body = deploy_call[1]["body"]
        self.assertEqual(body[0]["customer_id"], "cid123")
        tmpl = body[0]["templates"][0]
        self.assertEqual(tmpl["template_id"], "tmpl-1")
        self.assertEqual(tmpl["name"], "Lateral Movement via SMB")
        self.assertEqual(tmpl["severity"], 70)
        self.assertEqual(tmpl["status"], "active")
        self.assertEqual(tmpl["search"]["filter"], "#event_simpleName=NetworkConnect")
        self.assertEqual(tmpl["search"]["lookback"], "2h0m")
        self.assertEqual(tmpl["search"]["trigger_mode"], "summary")
        self.assertEqual(tmpl["operation"]["schedule"]["definition"], "@every 2h0m")
        self.assertEqual(tmpl["mitre_attack"], [{"tactic_id": "TA0008", "technique_id": "T1021"}])
        self.assertEqual(tmpl["description"], "Detects SMB lateral movement")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_deploy_template_with_overrides(self):
        """Test that user-provided overrides take precedence over template defaults."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Template Name",
                    "severity": 50,
                    "search": {
                        "filter": "#event=Test",
                        "outcome": "detection",
                        "lookback": "1h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — no match
            {
                "status_code": 200,
                "body": {
                    "resources": [],
                    "meta": {"pagination": {"total": 0}},
                },
            },
            # 3. Deploy
            {
                "status_code": 200,
                "body": {"resources": [{"id": "v1", "rule_id": "r1"}]},
            },
        ]

        self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
            name="My Custom Name",
            severity=90,
            status="inactive",
            schedule="@every 24h0m",
            lookback="24h0m",
            trigger_mode="verbose",
            description="My custom description",
            comment="Deploying for testing",
        )

        body = self.mock_client.command.call_args_list[2][1]["body"]
        tmpl = body[0]["templates"][0]
        self.assertEqual(tmpl["name"], "My Custom Name")
        self.assertEqual(tmpl["severity"], 90)
        self.assertEqual(tmpl["status"], "inactive")
        self.assertEqual(tmpl["search"]["lookback"], "24h0m")
        self.assertEqual(tmpl["search"]["trigger_mode"], "verbose")
        self.assertEqual(tmpl["operation"]["schedule"]["definition"], "@every 24h0m")
        self.assertEqual(tmpl["description"], "My custom description")
        self.assertEqual(tmpl["comment"], "Deploying for testing")

    def test_deploy_template_not_found(self):
        """Test that a missing template returns error without calling deploy."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.deploy_correlation_rule_template(
            template_id="nonexistent",
            customer_id="cid123",
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_called_once()

    def test_deploy_template_hydrate_error(self):
        """Test that a hydrate API error is returned without calling deploy."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal error"}]},
        }

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_called_once()

    def test_deploy_template_deploy_error(self):
        """Test that a deploy API error is returned wrapped in a list."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Template",
                    "severity": 50,
                    "search": {
                        "filter": "#event=Test",
                        "outcome": "detection",
                        "lookback": "1h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — no match
            {
                "status_code": 200,
                "body": {
                    "resources": [],
                    "meta": {"pagination": {"total": 0}},
                },
            },
            # 3. Deploy fails
            {
                "status_code": 403,
                "body": {"errors": [{"message": "Access denied"}]},
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_deploy_template_duplicate_found_returns_existing_rule(self):
        """Test that deploying a template when a rule with the same name exists returns duplicate info."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Lateral Movement via SMB",
                    "description": "Detects SMB lateral movement",
                    "severity": 70,
                    "search": {
                        "filter": "#event_simpleName=NetworkConnect",
                        "outcome": "detection",
                        "lookback": "2h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {
                        "schedule": {"definition": "@every 2h0m"},
                    },
                    "mitre_attack": [
                        {"tactic_id": "TA0008", "technique_id": "T1021"},
                    ],
                }]},
            },
            # 2. Duplicate check — existing rule found
            {
                "status_code": 200,
                "body": {
                    "resources": [{
                        "rule_id": "existing-rule-1",
                        "name": "Lateral Movement via SMB",
                        "severity": 70,
                        "status": "active",
                        "state": "published",
                        "template_id": "tmpl-1",
                    }],
                    "meta": {"pagination": {"total": 1}},
                },
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        # Should return a duplicate_found dict, not a list of deployed rules
        self.assertIsInstance(result, dict)
        self.assertTrue(result["duplicate_found"])
        self.assertIn("existing-rule-1", result["message"])
        self.assertEqual(result["existing_rule"]["rule_id"], "existing-rule-1")
        self.assertEqual(result["template_id"], "tmpl-1")
        # Should NOT have called the deploy endpoint (only hydrate + search)
        self.assertEqual(self.mock_client.command.call_count, 2)

    def test_deploy_template_duplicate_check_uses_name_override(self):
        """Test that the duplicate check uses the caller's name override, not the template name."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Template Name",
                    "severity": 50,
                    "search": {
                        "filter": "#event=Test",
                        "outcome": "detection",
                        "lookback": "1h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — searches with overridden name, finds match
            {
                "status_code": 200,
                "body": {
                    "resources": [{
                        "rule_id": "existing-rule-2",
                        "name": "My Custom Name",
                        "severity": 50,
                        "status": "active",
                        "state": "published",
                    }],
                    "meta": {"pagination": {"total": 1}},
                },
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
            name="My Custom Name",
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result["duplicate_found"])
        # Verify the search used the overridden name
        search_call = self.mock_client.command.call_args_list[1]
        search_filter = search_call[1].get("filter") or search_call[0][1] if len(search_call[0]) > 1 else search_call[1].get("filter")
        # The filter should reference the overridden name, not the template name
        self.assertIn("My Custom Name", result["message"])

    def test_deploy_template_no_duplicate_proceeds_to_deploy(self):
        """Test that deployment proceeds normally when no duplicate is found."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Unique Rule Name",
                    "severity": 50,
                    "search": {
                        "filter": "#event=Test",
                        "outcome": "detection",
                        "lookback": "1h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — no match
            {
                "status_code": 200,
                "body": {
                    "resources": [],
                    "meta": {"pagination": {"total": 0}},
                },
            },
            # 3. Deploy succeeds
            {
                "status_code": 200,
                "body": {"resources": [{"rule_id": "new-rule-1", "name": "Unique Rule Name"}]},
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        # Should return the deployed rule, not a duplicate response
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["rule_id"], "new-rule-1")
        # All three API calls should have been made
        self.assertEqual(self.mock_client.command.call_count, 3)

    def test_deploy_template_duplicate_check_error_still_deploys(self):
        """Test that an error during the duplicate check doesn't block deployment."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Test Template",
                    "severity": 50,
                    "search": {
                        "filter": "#event=Test",
                        "outcome": "detection",
                        "lookback": "1h0m",
                        "trigger_mode": "summary",
                        "execution_mode": "standard",
                    },
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — API error
            {
                "status_code": 500,
                "body": {"errors": [{"message": "Internal error"}]},
            },
            # 3. Deploy succeeds anyway
            {
                "status_code": 200,
                "body": {"resources": [{"rule_id": "new-rule-2"}]},
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
        )

        # Should still deploy despite the search error
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["rule_id"], "new-rule-2")
        self.assertEqual(self.mock_client.command.call_count, 3)

    def test_deploy_template_only_schedule_override_no_validation(self):
        """Test that providing only schedule override (no lookback override) skips validation."""
        self.mock_client.command.side_effect = [
            # 1. Hydrate template
            {
                "status_code": 200,
                "body": {"resources": [{
                    "id": "tmpl-1",
                    "name": "Test Template",
                    "severity": 70,
                    "search": {"filter": "#test", "outcome": "detection", "lookback": "1h0m", "trigger_mode": "summary", "execution_mode": "scheduled"},
                    "operation": {"schedule": {"definition": "@every 1h0m"}},
                }]},
            },
            # 2. Duplicate check — no match
            {
                "status_code": 200,
                "body": {
                    "resources": [],
                    "meta": {"pagination": {"total": 0}},
                },
            },
            # 3. Deploy
            {
                "status_code": 200,
                "body": {"resources": [{"rule_id": "new-rule"}]},
            },
        ]

        result = self.module.deploy_correlation_rule_template(
            template_id="tmpl-1",
            customer_id="cid123",
            schedule="@every 2h0m",
        )

        self.assertEqual(self.mock_client.command.call_count, 3)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
