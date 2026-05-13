"""
Tests for the Cloud module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudModule(TestModules):
    """Test cases for the Cloud module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CloudModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
            "falcon_search_iom_findings",
            "falcon_search_ioa_findings",
            "falcon_search_cspm_suppression_rules",
            "falcon_create_cspm_suppression_rule",
            "falcon_delete_cspm_suppression_rules",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_kubernetes_containers_fql_filter_guide",
            "falcon_images_vulnerabilities_fql_filter_guide",
            "falcon_search_cspm_assets_fql_guide",
            "falcon_search_iom_findings_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_kubernetes_containers(self):
        """Test searching for kubernetes containers."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": ["container_1", "container_2"]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(
            filter="cloud_name:'AWS'", limit=1
        )

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCombined")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_name:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertEqual(result, ["container_1", "container_2"])

    def test_search_kubernetes_containers_errors(self):
        """Test searching for kubernetes containers with API error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(filter="invalid_filter")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_count_kubernetes_containers(self):
        """Test count for kubernetes containers."""
        mock_response = {"status_code": 200, "body": {"resources": [500]}}
        self.mock_client.command.return_value = mock_response

        result = self.module.count_kubernetes_containers(filter="cloud_region:'us-1'")

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadContainerCount")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_region:'us-1'")
        self.assertEqual(result, [500])

    def test_count_kubernetes_containers_errors(self):
        """Test count for kubernetes containers with API error."""
        mock_response = {
            "status_code": 500,
            "body": {"errors": [{"message": "internal error"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(filter="invalid_filter")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_search_images_vulnerabilities(self):
        """Test search for images vulnerabilities."""
        mock_response = {"status_code": 200, "body": {"resources": ["cve_id_1"]}}
        self.mock_client.command.return_value = mock_response

        result = self.module.search_images_vulnerabilities(
            filter="cvss_score:>5", limit=1
        )

        self.assertEqual(self.mock_client.command.call_count, 1)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "ReadCombinedVulnerabilities")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cvss_score:>5")
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)
        self.assertEqual(result, ["cve_id_1"])

    def test_search_images_vulnerabilities_errors(self):
        """Test search for images vulnerabilities with API error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid sort"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_kubernetes_containers(sort="1|1")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_search_cspm_assets_success(self):
        """Test searching for CSPM assets with two-step pattern."""
        # Mock query response (returns IDs)
        query_response = {
            "status_code": 200,
            "body": {"resources": ["asset_1", "asset_2", "asset_3"]},
        }
        # Mock get response (returns full details)
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "asset_1", "cloud_provider": "AWS", "resource_type": "ec2-instance"},
                    {"id": "asset_2", "cloud_provider": "AWS", "resource_type": "s3-bucket"},
                    {"id": "asset_3", "cloud_provider": "Azure", "resource_type": "vm"},
                ]
            },
        }

        # Configure side_effect to return query then get
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_assets(
            filter="cloud_provider:'AWS'", limit=10
        )

        # Verify 2 API calls made
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Verify first call (query)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "cloud_security_assets_queries")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_provider:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        # Verify second call (get details)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], ["asset_1", "asset_2", "asset_3"]
        )

        # Verify result is full details, not just IDs
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("cloud_provider", result[0])
        self.assertIn("resource_type", result[0])

    def test_search_cspm_assets_batching(self):
        """Test CSPM assets search handles >100 IDs with batching."""
        # Mock 250 IDs
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}

        # Mock 3 batches (100 + 100 + 50)
        batch1_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(100)
        ]
        batch2_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(100, 200)
        ]
        batch3_assets = [
            {"id": f"asset_{i}", "cloud_provider": "AWS"}
            for i in range(200, 250)
        ]

        batch1 = {"status_code": 200, "body": {"resources": batch1_assets}}
        batch2 = {"status_code": 200, "body": {"resources": batch2_assets}}
        batch3 = {"status_code": 200, "body": {"resources": batch3_assets}}

        self.mock_client.command.side_effect = [
            query_response,
            batch1,
            batch2,
            batch3,
        ]

        result = self.module.search_cspm_assets(limit=1000)

        # Verify 4 calls: 1 query + 3 get batches
        self.assertEqual(self.mock_client.command.call_count, 4)

        # Verify batching calls - validate both length and content
        # Second call should contain IDs 0-99
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            second_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100)]
        )

        # Third call should contain IDs 100-199
        third_call = self.mock_client.command.call_args_list[2]
        self.assertEqual(third_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            third_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100, 200)]
        )

        # Fourth call should contain IDs 200-249
        fourth_call = self.mock_client.command.call_args_list[3]
        self.assertEqual(fourth_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(
            fourth_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(200, 250)]
        )

        # Verify all 250 assets returned
        self.assertEqual(len(result), 250)

    def test_search_cspm_assets_error_returns_fql_guide(self):
        """Test CSPM assets search returns FQL guide on error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_cspm_assets(filter="invalid::syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertIn("hint", result)
        self.assertIn("tag_key", result["fql_guide"])

    def test_search_cspm_assets_empty_returns_fql_guide(self):
        """Test CSPM assets search returns FQL guide on empty results."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = query_response

        result = self.module.search_cspm_assets(filter="cloud_provider:'NonExistent'")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertEqual(result["results"], [])
        self.assertIn("Cloud Resource Tag Filtering", result["fql_guide"])

    def test_search_cspm_assets_batch_error_fails_fast(self):
        """Test CSPM assets batching fails fast on batch error."""
        # Mock 250 IDs
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}

        # First batch succeeds, second batch fails
        batch1 = {
            "status_code": 200,
            "body": {"resources": [{"id": f"asset_{i}"} for i in range(100)]},
        }
        batch2_error = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }

        self.mock_client.command.side_effect = [
            query_response,
            batch1,
            batch2_error,
        ]

        result = self.module.search_cspm_assets(limit=1000)

        # Verify only 3 calls (query + batch1 + batch2 error)
        self.assertEqual(self.mock_client.command.call_count, 3)

        # Verify error returned (not partial results)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_cspm_assets_uses_params_true(self):
        """Test CSPM assets get request uses use_params=True for GET method."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["asset_1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "asset_1"}]},
        }

        self.mock_client.command.side_effect = [query_response, get_response]

        self.module.search_cspm_assets(limit=1)

        # Verify second call uses parameters (not body)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])

    # --- IOM Findings Tests ---

    def test_search_iom_findings_success(self):
        """Test searching for IOM findings with two-step pattern."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["iom_1", "iom_2"]},
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

        # Verify query call
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "cspm_evaluations_iom_queries")
        self.assertEqual(first_call[1]["parameters"]["filter"], "severity:'critical'+status:'open'")

        # Verify get call
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cspm_evaluations_iom_entities")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["iom_1", "iom_2"])

        # Verify full details returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("severity", result[0])

    def test_search_iom_findings_error_returns_fql_guide(self):
        """Test IOM search returns FQL guide on error."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_iom_findings(filter="invalid::syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertIn("severity", result["fql_guide"])

    def test_search_iom_findings_empty_returns_fql_guide(self):
        """Test IOM search returns FQL guide on empty results."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = query_response

        result = self.module.search_iom_findings(filter="severity:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("results", result)
        self.assertEqual(result["results"], [])

    def test_search_iom_findings_batching(self):
        """Test IOM search handles >100 IDs with batching."""
        iom_ids = [f"iom_{i}" for i in range(150)]
        query_response = {"status_code": 200, "body": {"resources": iom_ids}}

        batch1 = {"status_code": 200, "body": {"resources": [{"id": f"iom_{i}"} for i in range(100)]}}
        batch2 = {"status_code": 200, "body": {"resources": [{"id": f"iom_{i}"} for i in range(100, 150)]}}

        self.mock_client.command.side_effect = [query_response, batch1, batch2]

        result = self.module.search_iom_findings(limit=200)

        self.assertEqual(self.mock_client.command.call_count, 3)
        self.assertEqual(len(result), 150)

    def test_search_iom_findings_uses_params_true(self):
        """Test IOM entity fetch uses GET with query params."""
        query_response = {"status_code": 200, "body": {"resources": ["iom_1"]}}
        get_response = {"status_code": 200, "body": {"resources": [{"id": "iom_1"}]}}
        self.mock_client.command.side_effect = [query_response, get_response]

        self.module.search_iom_findings(limit=1)

        second_call = self.mock_client.command.call_args_list[1]
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])

    # --- IOA Findings Tests ---

    def test_search_ioa_findings_success(self):
        """Test searching for IOA behavior detections."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"event_id": "ioa_1", "severity": "High"}]},
        }
        self.mock_client.command.return_value = mock_response

        self.module.search_ioa_findings(
            cloud_provider="aws", severity="High", limit=10
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "GetBehaviorDetections")
        self.assertEqual(call[1]["parameters"]["cloud_provider"], "aws")
        self.assertEqual(call[1]["parameters"]["severity"], "High")

    def test_search_ioa_findings_error(self):
        """Test IOA search error handling."""
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "cloud_provider is required"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.search_ioa_findings(cloud_provider="invalid")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    # --- Suppression Rules Tests ---

    def test_search_suppression_rules_success(self):
        """Test searching for suppression rules with two-step pattern."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule_1", "rule_2"]},
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

        # Verify override used for query
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["override"], "GET,/cloud-policies/queries/suppression-rules/v1")

        # Verify override used for get
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[1]["override"], "GET,/cloud-policies/entities/suppression-rules/v1")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_search_suppression_rules_empty(self):
        """Test suppression rules search with no results."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = query_response

        result = self.module.search_cspm_suppression_rules()

        self.assertEqual(result, [])

    def test_create_suppression_rule_success(self):
        """Test creating a suppression rule."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.mock_client.command.return_value = mock_response

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
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "new_rule_1"}]},
        }
        self.mock_client.command.return_value = mock_response

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
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule_1"}]},
        }
        self.mock_client.command.return_value = mock_response

        self.module.delete_cspm_suppression_rules(ids=["rule_1", "rule_2"])

        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[1]["override"], "DELETE,/cloud-policies/entities/suppression-rules/v1")
        self.assertEqual(call[1]["parameters"]["ids"], ["rule_1", "rule_2"])

    def test_mutating_tools_have_correct_annotations(self):
        """Test that mutating tools have destructiveHint=True."""
        self.module.register_tools(self.mock_server)

        # Check create tool
        self.assert_tool_annotations(
            "falcon_create_cspm_suppression_rule",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        # Check delete tool
        self.assert_tool_annotations(
            "falcon_delete_cspm_suppression_rules",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()

