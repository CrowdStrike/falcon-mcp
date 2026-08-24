"""
Tests for CSPM asset inventory tools (part of CloudModule).
"""

import unittest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudAssetsTools(TestModules):
    """Test cases for the cloud assets tools within CloudModule."""

    def setUp(self):
        self.setup_module(CloudModule)

    def test_search_cspm_assets_success(self):
        """Test searching for CSPM assets with two-step pattern."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["asset_1", "asset_2", "asset_3"],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 3}},
            },
        }
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
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_assets(filter="cloud_provider:'AWS'", limit=10)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "cloud_security_assets_queries")
        self.assertEqual(first_call[1]["parameters"]["filter"], "cloud_provider:'AWS'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["asset_1", "asset_2", "asset_3"])

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 3)
        self.assertIn("cloud_provider", result["results"][0])
        self.assertIn("resource_type", result["results"][0])
        self.assertEqual(result["pagination"]["total"], 3)

    def test_search_cspm_assets_reorders_to_match_sorted_ids(self):
        """When cloud_security_assets_entities_get returns assets out of order,
        the result is reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["asset-b", "asset-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "asset-a", "resource_type": "s3-bucket"},
                    {"id": "asset-b", "resource_type": "ec2-instance"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cspm_assets(filter=None, limit=10)

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "asset-b")
        self.assertEqual(result["results"][1]["id"], "asset-a")

    def test_search_cspm_assets_batching(self):
        """Test CSPM assets search handles >100 IDs with batching."""
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {
            "status_code": 200,
            "body": {
                "resources": asset_ids,
                "meta": {"pagination": {"offset": 0, "limit": 1000, "total": 250}},
            },
        }

        batch1_assets = [{"id": f"asset_{i}", "cloud_provider": "AWS"} for i in range(100)]
        batch2_assets = [{"id": f"asset_{i}", "cloud_provider": "AWS"} for i in range(100, 200)]
        batch3_assets = [{"id": f"asset_{i}", "cloud_provider": "AWS"} for i in range(200, 250)]

        self.mock_client.command.side_effect = [
            query_response,
            {"status_code": 200, "body": {"resources": batch1_assets}},
            {"status_code": 200, "body": {"resources": list(reversed(batch2_assets))}},
            {"status_code": 200, "body": {"resources": batch3_assets}},
        ]

        result = self.module.search_cspm_assets(limit=1000)

        self.assertEqual(self.mock_client.command.call_count, 4)

        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "cloud_security_assets_entities_get")
        self.assertEqual(second_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100)])

        third_call = self.mock_client.command.call_args_list[2]
        self.assertEqual(third_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(100, 200)])

        fourth_call = self.mock_client.command.call_args_list[3]
        self.assertEqual(fourth_call[1]["parameters"]["ids"], [f"asset_{i}" for i in range(200, 250)])

        self.assertEqual(len(result["results"]), 250)
        self.assertEqual(result["pagination"]["total"], 250)
        # Reorder restores query-step order across batches even though batch2 was reversed.
        self.assertEqual([r["id"] for r in result["results"]], asset_ids)

    def test_search_cspm_assets_error_returns_fql_guide(self):
        """Test CSPM assets search returns FQL guide on error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }
        result = self.module.search_cspm_assets(filter="invalid::syntax")
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertIn("hint", result)
        self.assertIn("tag_key", result["fql_guide"])

    def test_search_cspm_assets_empty(self):
        """Test CSPM assets search returns clean empty response on empty results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_cspm_assets(filter="cloud_provider:'NonExistent'")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])
        self.assertEqual(result["filter_used"], "cloud_provider:'NonExistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_cspm_assets_batch_error_fails_fast(self):
        """Test CSPM assets batching fails fast on batch error."""
        asset_ids = [f"asset_{i}" for i in range(250)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}
        batch1 = {
            "status_code": 200,
            "body": {"resources": [{"id": f"asset_{i}"} for i in range(100)]},
        }
        batch2_error = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }
        self.mock_client.command.side_effect = [query_response, batch1, batch2_error]

        result = self.module.search_cspm_assets(limit=1000)

        self.assertEqual(self.mock_client.command.call_count, 3)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_cspm_assets_uses_params_true(self):
        """Test CSPM assets get request uses GET with query params (use_params=True)."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["asset_1"]}},
            {"status_code": 200, "body": {"resources": [{"id": "asset_1"}]}},
        ]
        self.module.search_cspm_assets(limit=1)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])

    def test_search_cspm_assets_trims_bloated_fields(self):
        """Test CSPM assets strips large fields to reduce response size."""
        bloated_asset = {
            "id": "cid|aws|123|us-east-1|AWS::EC2::Instance|i-abc",
            "arn": "arn:aws:ec2:us-east-1:123:instance/i-abc",
            "resource_id": "i-abc",
            "resource_name": "my-instance",
            "resource_type": "AWS::EC2::Instance",
            "resource_type_name": "EC2 Instance",
            "account_id": "123456789012",
            "account_name": "production",
            "region": "us-east-1",
            "zone": "us-east-1a",
            "cloud_provider": "aws",
            "service": "EC2",
            "service_category": "Compute",
            "active": True,
            "first_seen": "2025-01-01T00:00:00Z",
            "updated_at": "2025-03-01T00:00:00Z",
            "creation_time": "2025-01-01T00:00:00Z",
            "tags": {"Environment": "Production"},
            "resource_url": "https://console.aws.amazon.com/ec2/...",
            "relationships": [{"type": "vpc", "id": "vpc-123"}],
            # Fields that should be REMOVED:
            "gcrn": "cid|aws|123|us-east-1|AWS::EC2::Instance|i-abc",
            "cid": "5ddb0407bef249c19c7a975f17979a1f",
            "hash": "a8fc79d611a11b1a01a4e9a235c3834c",
            "revision": 5,
            "configuration": '{"instanceId":"i-abc","instanceType":"m5.large"}',
            "supplementary_configuration": '{"vpcId":"vpc-123","subnetId":"subnet-456"}',
            "cloud_context": {
                "cspm_license": "cspm",
                "publicly_exposed": True,
                "managed_by": "Sensor",
                "has_tags": True,
                "instance_id": "i-abc",
                "instance_state": "running",
                "open_cloud_risks": 3,
                "scan_type": "resource",
                "data_classifications": {"scanned": True, "found": False},
                "host": {
                    "managed_by": "Sensor",
                    "platform_name": "Linux",
                    "platform_os_name": "Amazon Linux",
                    "platform_os_version": "2023",
                },
                "detections": {
                    "iom_counts": 5,
                    "ioa_counts": 1,
                    "severities": ["high", "medium"],
                    "highest_severity": "high",
                    "resource_url": "https://console.aws.amazon.com/ec2/...",
                    "compliant": {
                        "rules": ["rule-1", "rule-2"] * 50,
                        "controls": [{"benchmark": "CIS", "version": "1.4"}] * 20,
                        "benchmarkVersions": None,
                        "legacy_policy_ids": ["pol-1", "pol-2"],
                    },
                    "non_compliant": {
                        "rules": ["rule-x"] * 10,
                        "controls": [{"benchmark": "NIST", "section": "5.1"}] * 15,
                        "benchmarkVersions": None,
                        "legacy_policy_ids": ["pol-3"],
                    },
                },
                "insights": {
                    "external": [
                        {"id": "imdsv1Enabled", "ruleId": "r1", "booleanValue": True},
                        {"id": "hasPublicIp", "ruleId": "r2", "booleanValue": False},
                    ],
                    "details": {"verbose": "data" * 100},
                },
                "asset_graph": {"id": "graph-123", "res_id": "ec2.Instance"},
                "legacy_resource_id": "i-abc",
                "legacy_uuid": "some-long-uuid-string",
                "legacy_type_id": 1,
                "account_name": "production",
            },
        }

        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["asset_1"],
                    "meta": {"pagination": {"offset": 0, "limit": 1, "total": 1}},
                },
            },
            {"status_code": 200, "body": {"resources": [bloated_asset]}},
        ]

        result = self.module.search_cspm_assets(limit=1)

        self.assertEqual(len(result["results"]), 1)
        asset = result["results"][0]

        # Useful fields preserved
        self.assertEqual(asset["id"], "cid|aws|123|us-east-1|AWS::EC2::Instance|i-abc")
        self.assertEqual(asset["resource_type"], "AWS::EC2::Instance")
        self.assertEqual(asset["account_id"], "123456789012")
        self.assertEqual(asset["region"], "us-east-1")
        self.assertEqual(asset["tags"], {"Environment": "Production"})
        self.assertTrue(asset["active"])

        # Bloated fields removed
        self.assertNotIn("gcrn", asset)
        self.assertNotIn("cid", asset)
        self.assertNotIn("hash", asset)
        self.assertNotIn("revision", asset)
        self.assertNotIn("configuration", asset)
        self.assertNotIn("supplementary_configuration", asset)

        # cloud_context trimmed to security summary
        cc = asset["cloud_context"]
        self.assertTrue(cc["publicly_exposed"])
        self.assertEqual(cc["managed_by"], "Sensor")
        self.assertEqual(cc["instance_state"], "running")
        self.assertEqual(cc["open_cloud_risks"], 3)
        self.assertEqual(cc["host"]["platform_name"], "Linux")

        # Detections: counts kept, rules/controls stripped
        self.assertEqual(cc["detections"]["iom_counts"], 5)
        self.assertEqual(cc["detections"]["ioa_counts"], 1)
        self.assertEqual(cc["detections"]["highest_severity"], "high")
        self.assertNotIn("compliant", cc["detections"])
        self.assertNotIn("non_compliant", cc["detections"])

        # Insights: external flags kept, verbose details stripped
        self.assertEqual(len(cc["insights"]["external"]), 2)
        self.assertNotIn("details", cc["insights"])

        # Internal fields stripped from cloud_context
        self.assertNotIn("asset_graph", cc)
        self.assertNotIn("legacy_resource_id", cc)
        self.assertNotIn("legacy_uuid", cc)

    def test_search_cspm_assets_trims_handles_missing_cloud_context(self):
        """Test trimming handles records without cloud_context gracefully."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["asset_1"],
                    "meta": {"pagination": {"offset": 0, "limit": 1, "total": 1}},
                },
            },
            {
                "status_code": 200,
                "body": {
                    "resources": [
                        {"id": "asset_1", "resource_type": "AWS::S3::Bucket", "cloud_provider": "aws", "region": "us-east-1"}
                    ]
                },
            },
        ]

        result = self.module.search_cspm_assets(limit=1)
        self.assertEqual(len(result["results"]), 1)
        asset = result["results"][0]
        self.assertEqual(asset["id"], "asset_1")
        self.assertEqual(asset["resource_type"], "AWS::S3::Bucket")
        self.assertNotIn("cloud_context", asset)


if __name__ == "__main__":
    unittest.main()
