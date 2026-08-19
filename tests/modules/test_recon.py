"""
Tests for the Recon module.
"""

import unittest
from typing import Any

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
            "falcon_aggregate_recon_notifications",
            "falcon_aggregate_recon_exposed_data_records",
            "falcon_preview_recon_rule",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_recon_notifications_fql_guide",
            "falcon_search_recon_rules_fql_guide",
            "falcon_search_recon_exposed_data_records_fql_guide",
            "falcon_aggregate_recon_notifications_guide",
            "falcon_aggregate_recon_exposed_data_records_guide",
            "falcon_preview_recon_rule_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # ------------------------------------------------------------------
    # search_recon_notifications
    # ------------------------------------------------------------------

    def test_search_recon_notifications_two_step(self):
        """Test two-step search pattern: QueryNotificationsV1 → GetNotificationsDetailedV1."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["notif1", "notif2"],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
            },
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

        self.assertIsInstance(result, dict)
        self.assertIn("pagination", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "notif1")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_recon_notifications_reorders_to_match_sorted_ids(self):
        """When GetNotificationsDetailedV1 returns notifications out of order, the
        result is reordered to match the sorted ID order from QueryNotificationsV1.

        Live API validated: the details endpoint scrambles order; entities carry
        their ID in the ``id`` field.
        """
        query_response = {
            "status_code": 200,
            "body": {"resources": ["notif-b", "notif-a"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "notif-a", "status": "new"},
                    {"id": "notif-b", "status": "new"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_notifications(sort="created_date.desc")

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "notif-b")
        self.assertEqual(result["results"][1]["id"], "notif-a")

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
            "body": {
                "resources": ["rule1", "rule2"],
                "meta": {"pagination": {"offset": 0, "limit": 5, "total": 2}},
            },
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

        self.assertIsInstance(result, dict)
        self.assertIn("pagination", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "rule1")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_recon_rules_reorders_to_match_sorted_ids(self):
        """When GetRulesV1 returns rules out of order, the result is reordered
        to match the sorted ID order from QueryRulesV1."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule-b", "rule-a"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rule-a", "topic": "SA_DOMAIN", "status": "active"},
                    {"id": "rule-b", "topic": "SA_TYPOSQUATTING", "status": "active"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_rules(
            filter=None, limit=5, sort="created_date.desc"
        )

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "rule-b")
        self.assertEqual(result["results"][1]["id"], "rule-a")

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
            "body": {
                "resources": ["rec1", "rec2"],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
            },
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

        self.assertIsInstance(result, dict)
        self.assertIn("pagination", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["email"], "user@example.com")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_recon_exposed_data_records_reorders_to_match_sorted_ids(self):
        """When GetNotificationsExposedDataRecordsV1 returns records out of order,
        the result is reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rec-b", "rec-a"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "rec-a", "email": "a@example.com", "credential_status": "newly_reported"},
                    {"id": "rec-b", "email": "b@example.com", "credential_status": "previously_reported"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_recon_exposed_data_records(
            filter=None, limit=10, sort="created_date.desc"
        )

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "rec-b")
        self.assertEqual(result["results"][1]["id"], "rec-a")

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

    # ------------------------------------------------------------------
    # Aggregate notifications
    # ------------------------------------------------------------------

    def _aggregate_notifications(self, **overrides):
        """Call aggregate_recon_notifications with every Field param supplied.

        Pydantic defaults are not resolved when calling the method directly, so
        each parameter has to be passed explicitly.
        """
        params = {
            "field": "status",
            "aggregate_type": "terms",
            "filter": None,
            "q": None,
            "name": "by_status",
            "size": 10,
            "sort": None,
            "interval": None,
            "date_ranges": None,
            "ranges": None,
            "sub_aggregates": None,
        }
        params.update(overrides)
        return self.module.aggregate_recon_notifications(**params)

    def test_aggregate_recon_notifications_success(self):
        """Verify a terms aggregation returns the API's buckets."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "by_status",
                        "buckets": [
                            {"label": "new", "count": 8500073},
                            {"label": "in-progress", "count": 4},
                        ],
                    }
                ],
                "errors": [],
            },
        }

        result = self._aggregate_notifications()

        self.mock_client.command.assert_called_once()
        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "AggregateNotificationsV1")
        # The endpoint 400s on a bare object; the spec must be list-wrapped.
        self.assertEqual(
            kwargs["body"],
            [{"type": "terms", "field": "status", "name": "by_status", "size": 10}],
        )
        self.assertEqual(result[0]["buckets"][0]["label"], "new")

    def test_aggregate_recon_notifications_omits_unset_spec_keys(self):
        """Verify unset optional params are absent from the body, not sent as null."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "errors": []},
        }

        self._aggregate_notifications(size=None)

        spec = self.mock_client.command.call_args[1]["body"][0]
        for absent in ("filter", "q", "sort", "interval", "date_ranges", "sub_aggregates", "size"):
            self.assertNotIn(absent, spec)

    def test_aggregate_recon_notifications_forwards_all_spec_params(self):
        """Verify filter, q, sort, interval, date_ranges, and sub_aggregates reach the body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "errors": []},
        }

        sub = [{"type": "terms", "field": "status", "name": "inner"}]
        self._aggregate_notifications(
            field="created_date",
            aggregate_type="date_range",
            filter="rule_topic:'SA_TYPOSQUATTING'",
            q="crowdstrike",
            sort="_count|asc",
            interval="day",
            date_ranges=[{"from": "now-30d", "to": "now"}],
            sub_aggregates=sub,
        )

        spec = self.mock_client.command.call_args[1]["body"][0]
        self.assertEqual(spec["type"], "date_range")
        self.assertEqual(spec["field"], "created_date")
        self.assertEqual(spec["filter"], "rule_topic:'SA_TYPOSQUATTING'")
        self.assertEqual(spec["q"], "crowdstrike")
        self.assertEqual(spec["sort"], "_count|asc")
        self.assertEqual(spec["interval"], "day")
        self.assertEqual(spec["date_ranges"], [{"from": "now-30d", "to": "now"}])
        self.assertEqual(spec["sub_aggregates"], sub)

    def test_aggregate_every_declared_type_sends_required_companion_args(self):
        """Every aggregate_type the Literal allows must be able to build a usable spec.

        `date_histogram` needs `interval`, `date_range` needs `date_ranges`, and `range`
        needs `ranges`; without them the API 500s, so the tool has to expose a way to
        supply each.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "errors": []},
        }

        # aggregate_type -> the companion key its spec cannot work without.
        required_companion = {
            "terms": None,
            "cardinality": None,
            "max": None,
            "min": None,
            "date_histogram": "interval",
            "date_range": "date_ranges",
            "range": "ranges",
        }
        companion_values: dict[str, Any] = {
            "interval": "day",
            "date_ranges": [{"from": "now-30d", "to": "now"}],
            "ranges": [{"From": 0, "To": 100}],
        }

        for aggregate_type, companion in required_companion.items():
            extra = {companion: companion_values[companion]} if companion else {}
            for call in (self._aggregate_notifications, self._aggregate_records):
                self.mock_client.command.reset_mock()
                call(aggregate_type=aggregate_type, **extra)
                spec = self.mock_client.command.call_args[1]["body"][0]
                self.assertEqual(spec["type"], aggregate_type)
                if companion:
                    self.assertIn(
                        companion,
                        spec,
                        f"{aggregate_type} must forward {companion} into the spec",
                    )

    def test_aggregate_recon_notifications_server_error(self):
        """A 500 (as `rule_name` returns live) surfaces as an error, not empty buckets."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal Server Error"}]},
        }

        result = self._aggregate_notifications(field="rule_name")

        self.assertIn("error", result)

    def test_aggregate_recon_notifications_body_level_error_on_200(self):
        """A 2xx carrying body-level errors must not be reported as success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "errors": [{"message": "Invalid aggregates request"}]},
        }

        result = self._aggregate_notifications()

        self.assertIn("error", result)
        self.assertIn("Invalid aggregates request", result["error"])

    # ------------------------------------------------------------------
    # Aggregate exposed-data records
    # ------------------------------------------------------------------

    def _aggregate_records(self, **overrides):
        """Call aggregate_recon_exposed_data_records with every Field param supplied."""
        params = {
            "field": "credential_status",
            "aggregate_type": "terms",
            "filter": None,
            "q": None,
            "name": "by_cs",
            "size": 10,
            "sort": None,
            "interval": None,
            "date_ranges": None,
            "ranges": None,
            "sub_aggregates": None,
        }
        params.update(overrides)
        return self.module.aggregate_recon_exposed_data_records(**params)

    def test_aggregate_recon_exposed_data_records_success(self):
        """Verify the exposed-data aggregate hits its own operation and returns buckets."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "by_cs",
                        "buckets": [
                            {"label": "previously_reported", "count": 49577530},
                            {"label": "newly_reported", "count": 38150176},
                        ],
                    }
                ],
                "errors": [],
            },
        }

        result = self._aggregate_records()

        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "AggregateNotificationsExposedDataRecordsV1")
        self.assertEqual(
            kwargs["body"],
            [
                {
                    "type": "terms",
                    "field": "credential_status",
                    "name": "by_cs",
                    "size": 10,
                }
            ],
        )
        self.assertEqual(result[0]["buckets"][1]["label"], "newly_reported")

    def test_aggregate_recon_exposed_data_records_rejected_field(self):
        """This endpoint 400s on fields outside its whitelist (e.g. `email`)."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid aggregates request"}]},
        }

        result = self._aggregate_records(field="email")

        self.assertIn("error", result)

    def test_aggregate_recon_exposed_data_records_sub_aggregates(self):
        """Verify nested sub-aggregates are forwarded and returned intact."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "topic",
                        "buckets": [
                            {
                                "label": "SA_DOMAIN",
                                "count": 86295590,
                                "sub_aggregates": [
                                    {
                                        "name": "cs",
                                        "buckets": [{"label": "newly_reported", "count": 37788056}],
                                    }
                                ],
                            }
                        ],
                    }
                ],
                "errors": [],
            },
        }

        sub = [{"type": "terms", "field": "credential_status", "name": "cs", "size": 2}]
        result = self._aggregate_records(field="rule.topic", name="topic", sub_aggregates=sub)

        spec = self.mock_client.command.call_args[1]["body"][0]
        self.assertEqual(spec["sub_aggregates"], sub)
        self.assertEqual(result[0]["buckets"][0]["sub_aggregates"][0]["name"], "cs")

    # ------------------------------------------------------------------
    # Preview rule
    # ------------------------------------------------------------------

    def test_preview_recon_rule_success(self):
        """Verify the preview body is a bare object and the fixed trio comes back."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "channel", "buckets": [{"label": "public_repo", "count": 64}]},
                    {"name": "count", "buckets": [{"label": "Total", "count": 99}]},
                    {"name": "site", "buckets": [{"label": "github.com", "count": 57}]},
                ],
                "errors": [],
            },
        }

        result = self.module.preview_recon_rule(
            topic="SA_BRAND_PRODUCT",
            filter="(phrase:'Acme')+(keyword:'Acme')",
            lookback_days=30,
        )

        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "PreviewRuleV1")
        # Unlike the aggregate endpoints, this one takes a bare object, not a list.
        self.assertEqual(
            kwargs["body"],
            {
                "topic": "SA_BRAND_PRODUCT",
                "filter": "(phrase:'Acme')+(keyword:'Acme')",
                "lookback_days": 30,
            },
        )
        self.assertEqual([agg["name"] for agg in result], ["channel", "count", "site"])

    def test_preview_recon_rule_omits_unset_lookback(self):
        """lookback_days=None must be absent from the body rather than sent as null."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "errors": []},
        }

        self.module.preview_recon_rule(
            topic="SA_DOMAIN",
            filter="(domain:'example.com')",
            lookback_days=None,
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertNotIn("lookback_days", body)
        self.assertEqual(body["topic"], "SA_DOMAIN")

    def test_preview_recon_rule_invalid_filter_returns_guide(self):
        """A rejected rule filter returns the preview guide so the agent can self-correct."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "message": "Invalid request",
                        "details": [
                            {
                                "field": "filter",
                                "message_key": "RULE_FILTER_INVALID_FQL",
                            }
                        ],
                    }
                ]
            },
        }

        result = self.module.preview_recon_rule(
            topic="SA_DOMAIN",
            filter="example.com",
            lookback_days=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "example.com")
        # The guide must actually explain the rule-FQL dialect, not the search dialect.
        self.assertIn("(domain:'example.com')", result["fql_guide"])


if __name__ == "__main__":
    unittest.main()
