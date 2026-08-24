"""
Tests for cloud insights tools (part of CloudModule).
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudInsightsTools(TestModules):
    """Test cases for the cloud insights tools within CloudModule."""

    def setUp(self):
        self.setup_module(CloudModule)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        read_only = ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
        self.assert_tool_annotations("falcon_search_cloud_insights", read_only)
        self.assert_tool_annotations("falcon_get_cloud_asset_insights", read_only)
        self.assert_tool_annotations("falcon_list_cloud_insight_definitions", read_only)

    @staticmethod
    def _asset_with_insights(asset_id, external, details=None):
        """Build a cloud asset entity carrying cloud_context.insights."""
        insights = {"external": external}
        if details is not None:
            insights["details"] = details
        return {
            "id": asset_id,
            "resource_name": f"name-{asset_id}",
            "resource_type": "AWS::S3::Bucket",
            "cloud_provider": "aws",
            "region": "us-east-1",
            "account_id": "123456789012",
            "account_name": "prod",
            "service_category": "Storage",
            "cloud_context": {"insights": insights},
        }

    # --- helpers ---

    @staticmethod
    def _catalog_responses(ids: list[str]) -> list[dict]:
        """Build [QueryRule, GetRule] mock responses for a flat list of insight IDs."""
        uuids = [f"uuid-{iid}" for iid in ids]
        rules = [{"uuid": f"uuid-{iid}", "insight_id": iid, "category": "Network"} for iid in ids]
        return [
            {"status_code": 200, "body": {"resources": uuids, "meta": {"pagination": {"total": len(uuids), "offset": 0, "limit": 500}}}},
            {"status_code": 200, "body": {"resources": rules}},
        ]

    # --- search_cloud_insights ---

    def test_search_cloud_insights_returns_asset_records(self):
        """search_cloud_insights returns one record per asset with nested insights array."""
        query_response = {"status_code": 200, "body": {"resources": ["a1", "a2"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "a1",
                        [
                            {"id": "publiclyExposed", "ruleId": "r1", "booleanValue": True},
                            {"id": "publiclyExposedRange", "ruleId": "r2", "stringValue": "0.0.0.0/0"},
                        ],
                    ),
                    self._asset_with_insights(
                        "a2",
                        [{"id": "publiclyExposed", "ruleId": "r1", "booleanValue": False}],
                    ),
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(
            filter="insights.id:'publiclyExposed'", limit=100
        )

        self.assertIsInstance(result, dict)
        records = result["results"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["asset_id"], "a1")
        self.assertEqual(len(records[0]["insights"]), 2)
        self.assertEqual(records[0]["insights"][0]["insight_id"], "publiclyExposed")
        self.assertEqual(records[1]["asset_id"], "a2")

    def test_search_cloud_insights_success_exposes_filter_used(self):
        """filter_used in the envelope reflects the FQL expression sent to the API."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {"resources": [self._asset_with_insights("a1", [{"id": "x", "ruleId": "r", "booleanValue": True}])]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(
            filter="insights.id:'publiclyExposed'+insights.boolean_value:true", limit=10
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("filter_used"), "insights.id:'publiclyExposed'+insights.boolean_value:true")

    def test_search_cloud_insights_all_insights_shown(self):
        """All insight entries on an asset appear in the output regardless of insight ID."""
        catalog = self._catalog_responses(["netInsight", "idInsight"])
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "a1",
                        [
                            {"id": "netInsight", "ruleId": "r1", "booleanValue": True},
                            {"id": "idInsight", "ruleId": "r2", "booleanValue": True},
                        ],
                    )
                ]
            },
        }
        self.mock_client.command.side_effect = [*catalog, query_response, get_response]

        result = self.module.search_cloud_insights(limit=100)

        records = result["results"]
        self.assertEqual(len(records), 1)
        self.assertEqual(len(records[0]["insights"]), 2)
        ids = {i["insight_id"] for i in records[0]["insights"]}
        self.assertEqual(ids, {"netInsight", "idInsight"})

    def test_search_cloud_insights_category_is_null(self):
        """category field is None on insight entries — no PFM call at search time."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "a1",
                        [{"id": "publiclyExposed", "ruleId": "r1", "booleanValue": True}],
                    )
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(
            filter="insights.id:'publiclyExposed'", limit=100
        )

        insight = result["results"][0]["insights"][0]
        self.assertIsNone(insight["category"])

    def test_search_cloud_insights_asset_context_fields(self):
        """Each result carries the expected asset context fields."""
        query_response = {"status_code": 200, "body": {"resources": ["asset_1"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "asset_1",
                        [{"id": "publiclyExposed", "ruleId": "r1", "booleanValue": True}],
                    )
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(
            filter="insights.id:'publiclyExposed'", limit=100
        )

        rec = result["results"][0]
        self.assertEqual(rec["asset_id"], "asset_1")
        self.assertEqual(rec["asset_name"], "name-asset_1")
        self.assertEqual(rec["asset_type"], "AWS::S3::Bucket")
        self.assertEqual(rec["cloud_provider"], "aws")
        self.assertEqual(rec["region"], "us-east-1")
        self.assertEqual(rec["account_id"], "123456789012")
        self.assertEqual(rec["service_category"], "Storage")
        insight = rec["insights"][0]
        self.assertEqual(insight["value"], True)
        self.assertEqual(insight["rule_id"], "r1")
        self.assertEqual(insight["insight_id"], "publiclyExposed")

    def test_search_cloud_insights_no_pfm_call_when_filter_provided(self):
        """When filter is provided, no PFM (QueryRule/GetRule) call is made."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        self.module.search_cloud_insights(
            filter="insights.id:'identityIsAdmin'", limit=100
        )

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertNotIn("QueryRule", ops)
        self.assertNotIn("GetRule", ops)

    def test_search_cloud_insights_filter_forwarded_to_api(self):
        """When filter is provided it is forwarded verbatim — no PFM call."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        self.module.search_cloud_insights(
            filter="insights.id:'identityIsAdmin'+insights.boolean_value:true", limit=100
        )

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertNotIn("QueryRule", ops)
        params = self.mock_client.command.call_args_list[0][1]["parameters"]
        self.assertEqual(
            params["filter"],
            "insights.id:'identityIsAdmin'+insights.boolean_value:true",
        )

    def test_search_cloud_insights_no_filter_builds_explicit_id_list(self):
        """Omitting filter triggers a PFM definitions fetch and builds insights.id:[all_ids] filter."""
        catalog = self._catalog_responses(["netInsight", "idInsight"])
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [*catalog, query_response]

        self.module.search_cloud_insights(limit=10)

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertIn("QueryRule", ops)
        params = self.mock_client.command.call_args_list[-1][1]["parameters"]
        self.assertIn("netInsight", params["filter"])
        self.assertIn("idInsight", params["filter"])
        self.assertIn("insights.id:[", params["filter"])

    def test_search_cloud_insights_passes_sort_after(self):
        """sort and after cursor are forwarded to the asset query."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        self.module.search_cloud_insights(
            filter="insights.id:'x'", limit=50, after="cursor-token-abc", sort="updated_at.desc"
        )

        params = self.mock_client.command.call_args_list[0][1]["parameters"]
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["after"], "cursor-token-abc")
        self.assertEqual(params["sort"], "updated_at.desc")

    def test_search_cloud_insights_omitted_sort_after_not_sent(self):
        """Omitting sort and after does not forward FieldInfo objects to the API."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        self.module.search_cloud_insights(filter="insights.id:'x'", limit=10)

        params = self.mock_client.command.call_args_list[0][1]["parameters"]
        self.assertNotIn("after", params)
        self.assertNotIn("sort", params)

    def test_search_cloud_insights_omitted_limit_sends_int_default(self):
        """An omitted `limit` reaches the API as its int default, not a FieldInfo object.

        Every other Field-defaulted param on this tool is unwrapped; `limit` was not, so a
        direct Python call (as opposed to one routed through FastMCP's schema coercion)
        sent a pydantic FieldInfo as the API's limit.
        """
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        self.module.search_cloud_insights(filter="insights.id:'x'")

        params = self.mock_client.command.call_args_list[0][1]["parameters"]
        self.assertIsInstance(params["limit"], int)
        self.assertEqual(params["limit"], 100)

    def test_search_cloud_insights_auto_filter_is_flagged_not_echoed(self):
        """With no filter, the envelope flags auto-scoping instead of echoing the ID list."""
        catalog = self._catalog_responses(["netInsight", "idInsight"])
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [*catalog, query_response]

        result = self.module.search_cloud_insights(limit=10)

        # The generated insights.id:[...] expression is still what gets sent to the API...
        sent = self.mock_client.command.call_args_list[-1][1]["parameters"]["filter"]
        self.assertIn("insights.id:[", sent)
        # ...but it is not echoed back to the caller, who did not supply a filter.
        # _build_pagination_envelope omits filter_used entirely when it is None.
        self.assertNotIn("filter_used", result)
        self.assertNotIn("insights.id:[", str(result))
        self.assertTrue(result["auto_filter_applied"])
        self.assertEqual(result["auto_filter_insight_count"], 2)

    def test_search_cloud_insights_caller_filter_not_flagged_as_auto(self):
        """A caller-supplied filter is echoed verbatim and carries no auto-scoping keys."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_cloud_insights(filter="insights.id:'x'", limit=10)

        self.assertEqual(result["filter_used"], "insights.id:'x'")
        self.assertNotIn("auto_filter_applied", result)
        self.assertNotIn("auto_filter_insight_count", result)

    def test_search_cloud_insights_empty_returns_empty_response(self):
        """No matching assets returns the empty envelope with filter_used set."""
        query_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_cloud_insights(filter="insights.id:'x'", limit=100)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("pagination", result)
        self.assertEqual(result.get("filter_used"), "insights.id:'x'")

    def test_search_cloud_insights_entity_api_error(self):
        """An error fetching asset entities is wrapped in a list, as the other search tools do."""
        query_response = {"status_code": 200, "body": {"resources": ["a"]}}
        error_response = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        self.mock_client.command.side_effect = [query_response, error_response]

        result = self.module.search_cloud_insights(filter="insights.id:'x'", limit=100)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_cloud_insights_batching(self):
        """More than 100 matching assets are fetched in batches of 100."""
        asset_ids = [f"asset_{i}" for i in range(150)]
        query_response = {"status_code": 200, "body": {"resources": asset_ids}}
        batch1 = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        aid, [{"id": "publiclyExposed", "ruleId": "r", "booleanValue": True}]
                    )
                    for aid in asset_ids[:100]
                ]
            },
        }
        batch2 = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        aid, [{"id": "publiclyExposed", "ruleId": "r", "booleanValue": True}]
                    )
                    for aid in asset_ids[100:]
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, batch1, batch2]

        result = self.module.search_cloud_insights(filter="insights.id:'publiclyExposed'", limit=500)

        self.assertIsInstance(result, dict)
        records = result["results"]
        self.assertEqual(len(records), 150)
        self.assertEqual([r["asset_id"] for r in records], asset_ids)

    def test_search_cloud_insights_asset_query_error_returns_fql_error(self):
        """FQL error from cloud_security_assets_queries returns an FQL guide response."""
        error_response = {"status_code": 400, "body": {"errors": [{"message": "bad filter"}]}}
        self.mock_client.command.side_effect = [error_response]

        result = self.module.search_cloud_insights(
            filter="insights.id:'bad'", limit=100
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("filter_used", result)
        self.assertIn("insights.id:'bad'", result["filter_used"])

    def test_register_resources_registers_fql_guide(self):
        """register_resources adds the cloud-insights FQL guide resource to the server."""
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("test")
        self.module.register_resources(server)
        self.assertIn("falcon://cloud/cloud-insights/fql-guide", self.module.resources)

    # --- _group_insights_by_asset defensive guards ---

    def test_group_insights_skips_asset_without_cloud_context(self):
        """Assets without cloud_context are skipped."""
        query_response = {"status_code": 200, "body": {"resources": ["a1", "a2"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "a1", "resource_name": "no-ctx"},
                    self._asset_with_insights(
                        "a2", [{"id": "netInsight", "ruleId": "r1", "booleanValue": True}]
                    ),
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'netInsight'", limit=100)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["asset_id"], "a2")

    def test_group_insights_skips_asset_without_insights_block(self):
        """Assets with cloud_context but no insights block are skipped."""
        query_response = {"status_code": 200, "body": {"resources": ["a1", "a2"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "a1", "cloud_context": {"other": True}},
                    self._asset_with_insights(
                        "a2", [{"id": "netInsight", "ruleId": "r1", "booleanValue": True}]
                    ),
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'netInsight'", limit=100)
        self.assertEqual(len(result["results"]), 1)

    def test_group_insights_skips_asset_with_non_list_external(self):
        """Assets with insights block but non-list external are skipped."""
        query_response = {"status_code": 200, "body": {"resources": ["a1", "a2"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "a1", "cloud_context": {"insights": {"external": "not-a-list"}}},
                    self._asset_with_insights(
                        "a2", [{"id": "netInsight", "ruleId": "r1", "booleanValue": True}]
                    ),
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'netInsight'", limit=100)
        self.assertEqual(len(result["results"]), 1)

    def test_group_insights_skips_non_dict_external_item(self):
        """Non-dict items inside external list are skipped; valid items still processed."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        asset = {
            "id": "a1", "resource_name": "n", "resource_type": "t", "cloud_provider": "aws",
            "region": "r", "account_id": "123", "account_name": "a", "service_category": "s",
            "cloud_context": {"insights": {"external": [
                "not-a-dict",
                {"id": "netInsight", "ruleId": "r1", "booleanValue": True},
            ]}},
        }
        get_response = {"status_code": 200, "body": {"resources": [asset]}}
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'netInsight'", limit=100)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(len(result["results"][0]["insights"]), 1)

    def test_group_insights_string_value(self):
        """stringValue is mapped to the insight value field."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        asset = self._asset_with_insights(
            "a1", [{"id": "exposedRange", "ruleId": "r1", "stringValue": "Internet (0.0.0.0/0)"}]
        )
        get_response = {"status_code": 200, "body": {"resources": [asset]}}
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'exposedRange'", limit=100)
        self.assertEqual(result["results"][0]["insights"][0]["value"], "Internet (0.0.0.0/0)")

    def test_group_insights_integer_value(self):
        """integerValue is mapped to the insight value field."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        asset = self._asset_with_insights(
            "a1", [{"id": "groupsMembers", "ruleId": "r1", "integerValue": 42}]
        )
        get_response = {"status_code": 200, "body": {"resources": [asset]}}
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'groupsMembers'", limit=100)
        self.assertEqual(result["results"][0]["insights"][0]["value"], 42)

    def test_group_insights_string_list_value(self):
        """stringListValue is mapped to the insight value field."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        asset = self._asset_with_insights(
            "a1", [{"id": "llmModelsUsed", "ruleId": "r1", "stringListValue": ["claude-sonnet-4"]}]
        )
        get_response = {"status_code": 200, "body": {"resources": [asset]}}
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'llmModelsUsed'", limit=100)
        self.assertEqual(result["results"][0]["insights"][0]["value"], ["claude-sonnet-4"])

    def test_group_insights_date_value(self):
        """dateValue is mapped to the insight value field."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        asset = self._asset_with_insights(
            "a1", [{"id": "accessKeyLastRotated", "ruleId": "r1", "dateValue": "2024-11-01T00:00:00Z"}]
        )
        get_response = {"status_code": 200, "body": {"resources": [asset]}}
        self.mock_client.command.side_effect = [query_response, get_response]
        result = self.module.search_cloud_insights(filter="insights.id:'accessKeyLastRotated'", limit=100)
        self.assertEqual(result["results"][0]["insights"][0]["value"], "2024-11-01T00:00:00Z")

    def test_group_insights_unknown_value_key_falls_back(self):
        """A *Value key outside the known list is still surfaced, not read as None.

        The known-key tuple is closed, so without the fallback scan a value type the API
        adds later would make the insight look empty instead of unrecognized.
        """
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "a1", [{"id": "futureInsight", "ruleId": "r1", "durationValue": 42}]
                    )
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(filter="insights.id:'futureInsight'", limit=10)

        self.assertEqual(result["results"][0]["insights"][0]["value"], 42)

    def test_group_insights_known_key_wins_over_unknown(self):
        """When a known and an unknown *Value key co-occur, the known one is chosen.

        Live entries carry exactly one value key, so this only pins the ordering rule.
        """
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "a1",
                        [{"id": "x", "ruleId": "r1", "durationValue": 42, "booleanValue": True}],
                    )
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(filter="insights.id:'x'", limit=10)

        self.assertIs(result["results"][0]["insights"][0]["value"], True)

    def test_group_insights_no_value_key_yields_none(self):
        """An entry with no *Value key at all reports value=None rather than raising."""
        query_response = {"status_code": 200, "body": {"resources": ["a1"]}}
        get_response = {
            "status_code": 200,
            "body": {"resources": [self._asset_with_insights("a1", [{"id": "x", "ruleId": "r1"}])]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_cloud_insights(filter="insights.id:'x'", limit=10)

        self.assertIsNone(result["results"][0]["insights"][0]["value"])

    def test_search_cloud_insights_no_filter_pfm_error_returns_error(self):
        """PFM failure when no filter is provided returns a structured error."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "forbidden"}]},
        }
        result = self.module.search_cloud_insights(limit=100)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_search_cloud_insights_no_filter_empty_definitions_returns_empty(self):
        """Empty PFM definitions when no filter returns empty envelope with message, without querying assets."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        result = self.module.search_cloud_insights(limit=100)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("message", result)
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertNotIn("cloud_security_assets_queries", ops)

    # --- get_cloud_asset_insights ---

    def test_get_cloud_asset_insights_success(self):
        """get_cloud_asset_insights returns full insights (external + details) per asset."""
        details_map = {
            "publiclyExposedToTheInternet": {
                "value": True,
                "context": {"ports": [443]},
                "calculatedAt": "2026-01-01T00:00:00Z",
            }
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        "asset_1",
                        [{"id": "publiclyExposedToTheInternet", "ruleId": "r1", "booleanValue": True}],
                        details=details_map,
                    )
                ]
            },
        }
        self.mock_client.command.return_value = get_response

        result = self.module.get_cloud_asset_insights(asset_ids=["asset_1"])

        self.assertEqual(
            self.mock_client.command.call_args_list[0][0][0],
            "cloud_security_assets_entities_get",
        )
        self.assertEqual(self.mock_client.command.call_args_list[0][1]["parameters"]["ids"], ["asset_1"])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["asset_id"], "asset_1")
        self.assertEqual(rec["asset_name"], "name-asset_1")
        self.assertEqual(rec["asset_type"], "AWS::S3::Bucket")
        self.assertEqual(rec["cloud_provider"], "aws")
        self.assertEqual(rec["region"], "us-east-1")
        self.assertEqual(rec["account_id"], "123456789012")
        self.assertEqual(rec["account_name"], "prod")
        self.assertEqual(rec["service_category"], "Storage")
        self.assertIn("external", rec["insights"])
        self.assertIn("details", rec["insights"])
        self.assertEqual(
            rec["insights"]["details"]["publiclyExposedToTheInternet"]["calculatedAt"],
            "2026-01-01T00:00:00Z",
        )

    def test_get_cloud_asset_insights_reorders_to_match_requested_ids(self):
        """Results follow the caller's requested asset_ids order."""
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights("a", [{"id": "ia", "ruleId": "r", "booleanValue": True}]),
                    self._asset_with_insights("b", [{"id": "ib", "ruleId": "r", "booleanValue": True}]),
                ]
            },
        }
        self.mock_client.command.return_value = get_response

        result = self.module.get_cloud_asset_insights(asset_ids=["b", "a"])

        self.assertEqual([r["asset_id"] for r in result], ["b", "a"])

    def test_get_cloud_asset_insights_skips_assets_without_insights(self):
        """Assets lacking cloud_context.insights contribute no records."""
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "a", "resource_name": "no-insights"},
                    self._asset_with_insights("b", [{"id": "ib", "ruleId": "r", "booleanValue": True}]),
                ]
            },
        }
        self.mock_client.command.return_value = get_response

        result = self.module.get_cloud_asset_insights(asset_ids=["b", "a"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["asset_id"], "b")

    def test_get_cloud_asset_insights_error(self):
        """An entities-get error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "boom"}]},
        }

        result = self.module.get_cloud_asset_insights(asset_ids=["a"])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_get_cloud_asset_insights_batching(self):
        """More than 100 asset_ids are fetched in batches of 100."""
        asset_ids = [f"asset_{i}" for i in range(150)]
        batch1 = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        aid, [{"id": "x", "ruleId": "r", "booleanValue": True}]
                    )
                    for aid in reversed(asset_ids[:100])
                ]
            },
        }
        batch2 = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        aid, [{"id": "x", "ruleId": "r", "booleanValue": True}]
                    )
                    for aid in asset_ids[100:]
                ]
            },
        }
        self.mock_client.command.side_effect = [batch1, batch2]

        result = self.module.get_cloud_asset_insights(asset_ids=asset_ids)

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(len(result), 150)
        self.assertEqual(
            self.mock_client.command.call_args_list[0][1]["parameters"]["ids"], asset_ids[:100]
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["parameters"]["ids"], asset_ids[100:]
        )
        self.assertEqual([r["asset_id"] for r in result], asset_ids)

    def test_get_cloud_asset_insights_second_batch_error_fails_fast(self):
        """If the second batch errors, the error is propagated without partial results."""
        asset_ids = [f"asset_{i}" for i in range(150)]
        batch1 = {
            "status_code": 200,
            "body": {
                "resources": [
                    self._asset_with_insights(
                        aid, [{"id": "x", "ruleId": "r", "booleanValue": True}]
                    )
                    for aid in asset_ids[:100]
                ]
            },
        }
        batch2_error = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        self.mock_client.command.side_effect = [batch1, batch2_error]

        result = self.module.get_cloud_asset_insights(asset_ids=asset_ids)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


class TestCloudInsightDefinitionsTools(TestModules):
    """Tests for list_cloud_insight_definitions."""

    def setUp(self):
        self.setup_module(CloudModule)

    @staticmethod
    def _make_rule(insight_id, category, name, provider="aws", resource_types=None, controls=None, description="desc"):
        return {
            "insight_id": insight_id,
            "category": category,
            "name": name,
            "description": description,
            "provider": provider,
            "resource_types": [{"resource_type": rt} for rt in (resource_types or [])],
            "controls": controls or [],
        }

    def _insights_definition_api_responses(self, rules):
        """Build [QueryRule response, GetRule response] from raw rule dicts."""
        uuids = [f"uuid-{r['insight_id']}" for r in rules]
        query_resp = {"status_code": 200, "body": {"resources": uuids, "meta": {"pagination": {"total": len(uuids), "offset": 0, "limit": 500}}}}
        get_resp = {"status_code": 200, "body": {"resources": rules}}
        return [query_resp, get_resp]

    def _definitions(self, **kwargs):
        """Call list_cloud_insight_definitions and return just the definition list.

        The tool returns the standard pagination envelope; these tests assert on the
        definition entries, so unwrap here and check the envelope shape once.
        """
        result = self.module.list_cloud_insight_definitions(**kwargs)
        self.assertIsInstance(result, dict)
        self.assertIn("pagination", result)
        return result["results"]

    def test_deduplicates_by_insight_id(self):
        """Two rules with same insight_id produce one catalog entry."""
        rules = [
            self._make_rule("iid1", "Network", "MyInsight - EC2", provider="aws", resource_types=["EC2"]),
            self._make_rule("iid1", "Network", "MyInsight - S3", provider="aws", resource_types=["S3"]),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["insight_id"], "iid1")

    def test_name_suffix_stripped(self):
        """' - <resource_type>' suffix is stripped from the name."""
        rules = [self._make_rule("iid1", "Network", "Public Exposure - EC2")]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["name"], "Public Exposure")

    def test_name_no_suffix_unchanged(self):
        """Names without a ' - ' suffix are returned as-is."""
        rules = [self._make_rule("iid1", "Network", "Public Exposure")]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["name"], "Public Exposure")

    def test_providers_aggregated_and_sorted(self):
        """Providers from multiple rule instances are aggregated and sorted."""
        rules = [
            self._make_rule("iid1", "Network", "N - EC2", provider="gcp"),
            self._make_rule("iid1", "Network", "N - S3", provider="aws"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["providers"], ["aws", "gcp"])

    def test_resource_types_aggregated(self):
        """resource_types are aggregated across rule instances."""
        rules = [
            self._make_rule("iid1", "Network", "N - EC2", resource_types=["EC2"]),
            self._make_rule("iid1", "Network", "N - S3", resource_types=["S3"]),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertIn("EC2", result[0]["resource_types"])
        self.assertIn("S3", result[0]["resource_types"])

    def test_categories_filter_case_insensitive(self):
        """categories filter is case-insensitive."""
        rules = [
            self._make_rule("iid1", "Network", "N"),
            self._make_rule("iid2", "Identity", "I"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions(categories=["network"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["category"], "Network")

    def test_categories_filter_unknown_returns_empty(self):
        """Unknown category returns empty list, not an error."""
        rules = [self._make_rule("iid1", "Network", "N")]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions(categories=["DoesNotExist"])
        self.assertEqual(result, [])

    def test_categories_none_returns_all(self):
        """categories=None returns all entries."""
        rules = [
            self._make_rule("iid1", "Network", "N"),
            self._make_rule("iid2", "Identity", "I"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(len(result), 2)

    def test_controls_slimmed_when_present(self):
        """Controls output only name, framework, section, requirement."""
        ctrl = {
            "name": "CIS 1.1",
            "security_framework": [{"name": "CIS"}],
            "section_name": "IAM",
            "requirement": "1.1",
            "extra_field": "dropped",
        }
        rules = [self._make_rule("iid1", "Identity", "I", controls=[ctrl])]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertIn("controls", result[0])
        c = result[0]["controls"][0]
        self.assertEqual(set(c.keys()), {"name", "framework", "section", "requirement"})
        self.assertEqual(c["name"], "CIS 1.1")
        self.assertEqual(c["framework"], "CIS")
        self.assertEqual(c["section"], "IAM")
        self.assertEqual(c["requirement"], "1.1")
        self.assertNotIn("extra_field", c)

    def test_controls_omitted_when_empty(self):
        """controls key is absent when no controls on the rule."""
        rules = [self._make_rule("iid1", "Network", "N", controls=[])]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertNotIn("controls", result[0])

    def test_api_error_returns_error_dict(self):
        """QueryRule API error returns {"error": ..., "detail": ...} — a dict, not a list."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "forbidden"}]},
        }
        result = self.module.list_cloud_insight_definitions()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("detail", result)

    def test_tool_registered(self):
        """list_cloud_insight_definitions is registered as a tool."""
        self.module.register_tools(self.mock_server)
        registered = [call.kwargs["name"] for call in self.mock_server.add_tool.call_args_list]
        self.assertIn("falcon_list_cloud_insight_definitions", registered)

    def test_fetch_pfm_rules_empty_query_returns_empty(self):
        """QueryRule returns empty → no GetRule call → list_cloud_insight_definitions returns []."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        result = self._definitions()
        self.assertEqual(result, [])

    def test_fetch_pfm_rules_getRule_error_returns_error_dict(self):
        """A GetRule error surfaces as an error dict — and GetRule is actually reached.

        The QueryRule response deliberately carries meta.pagination.total so the catalog
        loop terminates on page 1. Without it this test used to spend `error_resp` on a
        second QueryRule call and assert on a QueryRule failure, never exercising the
        GetRule path it names. The op-sequence assertion is what keeps that from
        happening again.
        """
        query_resp = {
            "status_code": 200,
            "body": {
                "resources": ["uuid-1"],
                "meta": {"pagination": {"total": 1, "offset": 0, "limit": 500}},
            },
        }
        error_resp = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        self.mock_client.command.side_effect = [query_resp, error_resp]

        result = self.module.list_cloud_insight_definitions()

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops, ["QueryRule", "GetRule"])
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("GetRule", result["detail"])

    def test_definitions_skips_non_dict_rules(self):
        """Non-dict entries in GetRule response are silently skipped."""
        query_resp = {"status_code": 200, "body": {"resources": ["uuid-1", "uuid-2"], "meta": {"pagination": {"total": 2, "offset": 0, "limit": 500}}}}
        get_resp = {"status_code": 200, "body": {"resources": [
            "not-a-dict",
            {"insight_id": "iid1", "category": "Network", "name": "N", "description": "d",
             "provider": "aws", "resource_types": [], "controls": []},
        ]}}
        self.mock_client.command.side_effect = [query_resp, get_resp]
        result = self._definitions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["insight_id"], "iid1")

    def test_definitions_skips_rules_missing_insight_id_or_category(self):
        """Rules missing insight_id or category are skipped."""
        rules = [
            {"insight_id": None, "category": "Network", "name": "N", "description": "d",
             "provider": "aws", "resource_types": [], "controls": []},
            {"insight_id": "iid1", "category": None, "name": "N", "description": "d",
             "provider": "aws", "resource_types": [], "controls": []},
            self._make_rule("iid2", "Network", "Good"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["insight_id"], "iid2")

    def test_definitions_skips_non_dict_controls(self):
        """Non-dict control entries are silently skipped."""
        ctrl_bad = "not-a-dict"
        ctrl_good = {"name": "C1", "security_framework": [{"name": "F1"}], "section_name": "s", "requirement": "1.0"}
        rule = self._make_rule("iid1", "Network", "N", controls=[ctrl_bad, ctrl_good])
        self.mock_client.command.side_effect = self._insights_definition_api_responses([rule])
        result = self._definitions()
        self.assertEqual(len(result[0]["controls"]), 1)
        self.assertEqual(result[0]["controls"][0]["name"], "C1")

    def test_control_section_maps_from_api_section_name(self):
        """PFM returns section_name; output exposes it as section."""
        ctrl = {
            "name": "C1",
            "security_framework": [{"name": "CIS"}],
            "section_name": "IAM",
            "requirement": "1.2",
        }
        rules = [self._make_rule("iid1", "Identity", "I", controls=[ctrl])]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["controls"][0]["section"], "IAM")

    def test_control_section_empty_when_api_field_absent(self):
        """A control with no section_name yields an empty section, not a KeyError."""
        ctrl = {"name": "C1", "security_framework": [{"name": "CIS"}], "requirement": "1.2"}
        rules = [self._make_rule("iid1", "Identity", "I", controls=[ctrl])]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["controls"][0]["section"], "")

    def test_fetch_pfm_rules_paginates_query_rule(self):
        """Catalog build paginates QueryRule when more than 500 results are returned."""
        page1_uuids = [f"uuid-{i}" for i in range(500)]
        page2_uuids = [f"uuid-extra-{i}" for i in range(10)]
        all_uuids = page1_uuids + page2_uuids
        rules = [
            {"uuid": uid, "insight_id": f"id-{uid}", "category": "Identity"} for uid in all_uuids
        ]
        batch_responses = []
        for i in range(0, len(all_uuids), 100):
            batch_responses.append({"status_code": 200, "body": {"resources": rules[i : i + 100]}})

        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": page1_uuids, "meta": {"pagination": {"total": 510, "offset": 0, "limit": 500}}}},
            {"status_code": 200, "body": {"resources": page2_uuids, "meta": {"pagination": {"total": 510, "offset": 500, "limit": 500}}}},
            *batch_responses,
        ]

        result = self.module.list_cloud_insight_definitions(limit=500)
        page2 = self.module.list_cloud_insight_definitions(limit=500, offset=500)

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)
        self.assertEqual(result["pagination"]["total"], 510)
        ids = {e["insight_id"] for e in result["results"]} | {
            e["insight_id"] for e in page2["results"]
        }
        self.assertIn(f"id-{page1_uuids[0]}", ids)
        self.assertIn(f"id-{page2_uuids[0]}", ids)
        self.assertEqual(len(ids), 510)

    # --- invariants observed in the live catalog (see the module docstrings) ---

    def test_name_with_multiple_separators_keeps_leading_segment(self):
        """Splitting on the first ' - ' is the documented choice.

        Live names carry exactly one separator (0 of 262 have more, 0 have none), so this
        pins behaviour that live data cannot currently distinguish rather than asserting
        an observed shape.
        """
        rules = [self._make_rule("iid1", "Network", "Public Exposure - EC2 - Classic")]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(result[0]["name"], "Public Exposure")

    def test_first_rule_wins_for_single_valued_fields(self):
        """category/name/description come from the first rule seen for an insight_id.

        Live data has no insight_id carrying two categories (0 of 61) or two distinct
        stripped names, so aggregating them would be speculative. This asserts the
        first-wins rule that the code actually implements, so a future multi-category
        insight shows up as a test change rather than silently picking an arbitrary value.
        """
        rules = [
            self._make_rule("iid1", "Network", "First Name - EC2", provider="aws", description="first"),
            self._make_rule("iid1", "Identity", "Second Name - S3", provider="gcp", description="second"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)
        result = self._definitions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["category"], "Network")
        self.assertEqual(result[0]["name"], "First Name")
        self.assertEqual(result[0]["description"], "first")
        # Multi-valued fields are still aggregated across both rules.
        self.assertEqual(result[0]["providers"], ["aws", "gcp"])

    # --- pagination of the client-side catalog ---

    def test_definitions_limit_truncates_and_reports_full_total(self):
        """`limit` bounds the page while pagination.total stays the full catalog size."""
        rules = [self._make_rule(f"iid{i}", "Network", f"N{i}") for i in range(5)]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)

        result = self.module.list_cloud_insight_definitions(limit=2)

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["pagination"]["total"], 5)
        self.assertEqual(result["pagination"]["limit"], 2)
        self.assertEqual(result["pagination"]["offset"], 0)

    def test_definitions_offset_selects_a_later_page(self):
        """`offset` skips entries; consecutive pages cover the catalog without overlap."""
        rules = [self._make_rule(f"iid{i}", "Network", f"N{i}") for i in range(5)]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)

        page1 = self.module.list_cloud_insight_definitions(limit=2, offset=0)["results"]
        page2 = self.module.list_cloud_insight_definitions(limit=2, offset=2)["results"]
        page3 = self.module.list_cloud_insight_definitions(limit=2, offset=4)["results"]

        seen = [e["insight_id"] for e in page1 + page2 + page3]
        self.assertEqual(seen, [f"iid{i}" for i in range(5)])
        self.assertEqual(len(page3), 1)

    def test_definitions_offset_past_end_returns_empty_page(self):
        """An offset beyond the catalog yields an empty page, not an error."""
        rules = [self._make_rule("iid0", "Network", "N")]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)

        result = self.module.list_cloud_insight_definitions(offset=500)

        self.assertEqual(result["results"], [])
        self.assertEqual(result["pagination"]["total"], 1)

    def test_definitions_total_reflects_category_filter(self):
        """pagination.total counts the filtered catalog, not the whole one."""
        rules = [
            self._make_rule("iid1", "Network", "N"),
            self._make_rule("iid2", "Identity", "I"),
            self._make_rule("iid3", "Identity", "I2"),
        ]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)

        result = self.module.list_cloud_insight_definitions(categories=["identity"])

        self.assertEqual(result["pagination"]["total"], 2)
        self.assertEqual(len(result["results"]), 2)

    def test_definitions_omitted_limit_offset_send_int_defaults(self):
        """Omitted limit/offset are unwrapped to ints before slicing."""
        rules = [self._make_rule(f"iid{i}", "Network", f"N{i}") for i in range(3)]
        self.mock_client.command.side_effect = self._insights_definition_api_responses(rules)

        result = self.module.list_cloud_insight_definitions()

        self.assertEqual(len(result["results"]), 3)
        self.assertIsInstance(result["pagination"]["limit"], int)
        self.assertIsInstance(result["pagination"]["offset"], int)


if __name__ == "__main__":
    unittest.main()
