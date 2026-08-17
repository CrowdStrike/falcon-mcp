"""
Tests for IOM findings and CSPM suppression rules tools (part of CloudModule).
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudIomTools(TestModules):
    """Test cases for the IOM and suppression rules tools within CloudModule."""

    def setUp(self):
        self.setup_module(CloudModule)

    # --- IOM Findings ---

    def test_search_iom_findings_success(self):
        """Test searching for IOM findings with two-step pattern."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["iom_1", "iom_2"],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "iom_1", "severity": "critical", "status": "open"},
                    {"id": "iom_2", "severity": "high", "status": "open"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_iom_findings(
            filter="severity:'critical'+status:'open'", limit=10
        )

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "cspm_evaluations_iom_queries")
        self.assertEqual(first_call[1]["parameters"]["filter"], "severity:'critical'+status:'open'")

        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cspm_evaluations_iom_entities")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["iom_1", "iom_2"])

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertIn("severity", result["results"][0])
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_iom_findings_reorders_to_match_sorted_ids(self):
        """When cspm_evaluations_iom_entities returns findings out of order,
        the result is reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["iom-b", "iom-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "iom-a", "severity": "high", "status": "open"},
                    {"id": "iom-b", "severity": "critical", "status": "open"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_iom_findings(filter=None, limit=10)

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "iom-b")
        self.assertEqual(result["results"][1]["id"], "iom-a")

    def test_search_iom_findings_error_returns_fql_guide(self):
        """Test IOM search returns FQL guide on error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }
        result = self.module.search_iom_findings(filter="invalid::syntax")
        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertIn("severity", result["fql_guide"])

    def test_search_iom_findings_empty(self):
        """Test IOM search returns clean empty response on empty results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_iom_findings(filter="severity:'nonexistent'")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])
        self.assertEqual(result["filter_used"], "severity:'nonexistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_iom_findings_batching(self):
        """Test IOM search handles >100 IDs with batching."""
        iom_ids = [f"iom_{i}" for i in range(150)]
        query_response = {
            "status_code": 200,
            "body": {
                "resources": iom_ids,
                "meta": {"pagination": {"offset": 0, "limit": 200, "total": 150}},
            },
        }
        batch1 = {
            "status_code": 200,
            "body": {"resources": [{"id": f"iom_{i}"} for i in range(100)]},
        }
        batch2 = {
            "status_code": 200,
            "body": {"resources": [{"id": f"iom_{i}"} for i in reversed(range(100, 150))]},
        }
        self.mock_client.command.side_effect = [query_response, batch1, batch2]

        result = self.module.search_iom_findings(limit=200)

        self.assertEqual(self.mock_client.command.call_count, 3)
        self.assertEqual(len(result["results"]), 150)
        self.assertEqual(result["pagination"]["total"], 150)
        # Reorder restores query-step order across batches even though batch2 was reversed.
        self.assertEqual([r["id"] for r in result["results"]], iom_ids)

    def test_search_iom_findings_batch_error_fails_fast(self):
        """Test IOM search wraps a step-2 (entities) error in a list."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["iom_1", "iom_2"]}},
            {"status_code": 500, "body": {"errors": [{"message": "Internal server error"}]}},
        ]
        result = self.module.search_iom_findings(limit=10)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_iom_findings_uses_params_true(self):
        """Test IOM entity fetch uses GET with query params."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["iom_1"]}},
            {"status_code": 200, "body": {"resources": [{"id": "iom_1"}]}},
        ]
        self.module.search_iom_findings(limit=1)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])

    # --- Suppression Rules ---

    def test_search_suppression_rules_success(self):
        """Test searching for suppression rules with two-step pattern."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["rule_1", "rule_2"],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule_1", "suppression_reason": "accept-risk"},
                    {"id": "rule_2", "suppression_reason": "false-positive"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_suppression_rules(limit=10)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(
            first_call[1]["override"], "GET,/cloud-policies/queries/suppression-rules/v1"
        )
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(
            second_call[1]["override"], "GET,/cloud-policies/entities/suppression-rules/v1"
        )

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_suppression_rules_empty(self):
        """Test suppression rules search with no results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_cspm_suppression_rules()
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])

    def test_search_suppression_rules_reorders_to_match_sorted_ids(self):
        """When GetSuppressionRules returns rules out of order, the result is
        reordered to match the query-step ID order."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule_2", "rule_1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule_1", "suppression_reason": "accept-risk"},
                    {"id": "rule_2", "suppression_reason": "false-positive"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_suppression_rules(limit=10)

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "rule_2")
        self.assertEqual(result["results"][1]["id"], "rule_1")

    def test_create_suppression_rule_success(self):
        """Test creating a suppression rule."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.module.create_cspm_suppression_rule(
            name="Test suppression rule",
            suppression_reason="accept-risk",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=["aws"],
            account_ids=["123456789012"],
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date="2025-12-31T23:59:59Z",
        )

        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[1]["override"], "POST,/cloud-policies/entities/suppression-rules/v1")

        body = call[1]["body"]
        self.assertEqual(body["name"], "Test suppression rule")
        self.assertEqual(body["suppression_reason"], "accept-risk")
        self.assertEqual(body["domain"], "CSPM")
        self.assertEqual(body["subdomain"], "IOM")
        self.assertEqual(body["suppression_expiration_date"], "2025-12-31T23:59:59Z")
        self.assertEqual(body["rule_selection_filter"]["rule_ids"], ["rule_123"])
        self.assertEqual(body["scope_asset_filter"]["cloud_providers"], ["aws"])

    def test_create_suppression_rule_invalid_reason(self):
        """Test create suppression rule rejects invalid reason."""
        result = self.module.create_cspm_suppression_rule(
            name="Test rule",
            suppression_reason="invalid-reason",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Invalid suppression_reason", result["error"])

    def test_create_suppression_rule_requires_rule_selection(self):
        """Test create suppression rule requires at least one rule selector."""
        result = self.module.create_cspm_suppression_rule(
            suppression_reason="accept-risk",
            rule_ids=None,
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("rule selection parameter is required", result["error"])

    def test_create_suppression_rule_all_assets_scope(self):
        """Test create suppression rule with no asset filter uses all_assets scope."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.module.create_cspm_suppression_rule(
            name="Test all assets rule",
            suppression_reason="false-positive",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )

        call = self.mock_client.command.call_args_list[0]
        body = call[1]["body"]
        self.assertEqual(body["scope_type"], "all_assets")
        self.assertNotIn("scope_asset_filter", body)

    def test_delete_suppression_rules_success(self):
        """Test deleting suppression rules."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule_1"}]},
        }
        self.module.delete_cspm_suppression_rules(ids=["rule_1", "rule_2"])

        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(
            call[1]["override"], "DELETE,/cloud-policies/entities/suppression-rules/v1"
        )
        self.assertEqual(call[1]["parameters"]["ids"], ["rule_1", "rule_2"])

    def test_mutating_tools_have_correct_annotations(self):
        """Test that mutating tools have correct ToolAnnotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations(
            "falcon_create_cspm_suppression_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_cspm_suppression_rules",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    # --- coverage gap tests ---

    def test_search_suppression_rules_query_error(self):
        """QuerySuppressionRules error is returned directly (not wrapped)."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "forbidden"}]},
        }
        result = self.module.search_cspm_suppression_rules()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_search_suppression_rules_get_details_error_wraps_in_list(self):
        """GetSuppressionRules error wraps the error dict in a list."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule_1"]},
        }
        error_response = {
            "status_code": 500,
            "body": {"errors": [{"message": "server error"}]},
        }
        self.mock_client.command.side_effect = [query_response, error_response]
        result = self.module.search_cspm_suppression_rules()
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_create_suppression_rule_with_rule_names(self):
        """rule_names populates rule_selection_filter.rule_names."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.module.create_cspm_suppression_rule(
            suppression_reason="false-positive",
            rule_ids=None,
            rule_names=["S3 public access"],
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        body = self.mock_client.command.call_args_list[0][1]["body"]
        self.assertEqual(body["rule_selection_filter"]["rule_names"], ["S3 public access"])
        self.assertNotIn("rule_ids", body["rule_selection_filter"])

    def test_create_suppression_rule_with_rule_severities(self):
        """rule_severities populates rule_selection_filter.rule_severities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.module.create_cspm_suppression_rule(
            suppression_reason="accept-risk",
            rule_ids=None,
            rule_names=None,
            rule_severities=["critical", "high"],
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        body = self.mock_client.command.call_args_list[0][1]["body"]
        self.assertEqual(body["rule_selection_filter"]["rule_severities"], ["critical", "high"])

    def test_create_suppression_rule_with_regions_resource_ids_types(self):
        """regions, resource_ids, resource_types all populate scope_asset_filter."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.module.create_cspm_suppression_rule(
            suppression_reason="false-positive",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=["us-east-1"],
            resource_ids=["res-id-1"],
            resource_types=["AWS::S3::Bucket"],
            expiration_date=None,
        )
        body = self.mock_client.command.call_args_list[0][1]["body"]
        self.assertEqual(body["scope_type"], "asset_filter")
        self.assertEqual(body["scope_asset_filter"]["regions"], ["us-east-1"])
        self.assertEqual(body["scope_asset_filter"]["resource_ids"], ["res-id-1"])
        self.assertEqual(body["scope_asset_filter"]["resource_types"], ["AWS::S3::Bucket"])

    def test_create_suppression_rule_api_error(self):
        """CreateSuppressionRule API error is returned directly."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "bad request"}]},
        }
        result = self.module.create_cspm_suppression_rule(
            suppression_reason="accept-risk",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_create_suppression_rule_empty_api_response(self):
        """CreateSuppressionRule returning empty resources list returns []."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.create_cspm_suppression_rule(
            suppression_reason="accept-risk",
            rule_ids=["rule_123"],
            rule_names=None,
            rule_severities=None,
            cloud_providers=None,
            account_ids=None,
            regions=None,
            resource_ids=None,
            resource_types=None,
            expiration_date=None,
        )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
