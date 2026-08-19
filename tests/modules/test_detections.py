"""
Tests for the Detections module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.detections import DetectionsModule
from tests.modules.utils.test_modules import TestModules


class TestDetectionsModule(TestModules):
    """Test cases for the Detections module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DetectionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_detections",
            "falcon_get_detection_details",
            "falcon_aggregate_detections",
            "falcon_update_detections",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_detections_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_detections(self):
        """Test searching for detections - details returns empty (not FQL-related)."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": []},  # Empty resources for PostEntitiesAlertsV2
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(
            filter="test query", limit=10, include_hidden=True
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"]},
            parameters={"include_hidden": True},
        )

        # Verify result is paginated envelope with empty results
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_detections_with_details(self):
        """Test searching for detections with details - success returns envelope."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": "detection1", "name": "Test Detection 1"},
                    {"composite_id": "detection2", "name": "Test Detection 2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(
            filter="test query", limit=10, include_hidden=True
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"]},
            parameters={"include_hidden": True},
        )

        # Verify result is paginated envelope
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["composite_id"], "detection1")
        self.assertEqual(result["results"][1]["composite_id"], "detection2")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_detections_reorders_to_match_sorted_ids(self):
        """When PostEntitiesAlertsV2 returns entities out of order, the result is
        reordered to match the sorted ID order from GetQueriesAlertsV2.

        Live API validated: the details endpoint scrambles order, and entities
        carry their ID in the ``composite_id`` field.
        """
        query_response = {
            "status_code": 200,
            "body": {"resources": ["high-sev", "low-sev"]},
        }
        # Details returned in the opposite (scrambled) order
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": "low-sev", "severity": 10},
                    {"composite_id": "high-sev", "severity": 90},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_detections(sort="severity.desc")

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["composite_id"], "high-sev")
        self.assertEqual(result["results"][1]["composite_id"], "low-sev")

    def test_search_detections_error(self):
        """Test searching for detections with API error returns FQL guide."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid query"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_detections
        result = self.module.search_detections(filter="invalid query")

        # Verify result contains error AND fql_guide
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    def test_search_detections_details_error(self):
        """Test that a details-step error (query ok, details 400) returns the wrapped error."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["detection1"]},
        }
        details_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "server error"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_detections(filter="status:'new'")

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])

    def test_search_detections_empty_results(self):
        """Test that an empty query result returns a clean empty response (no FQL guide)."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [], "meta": {"pagination": {"offset": 0, "limit": 100, "total": 0}}}},
        ]

        result = self.module.search_detections(filter="status:'new'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["total"], 0)
        self.assertIsNone(result["pagination"]["next"])
        self.assertNotIn("fql_guide", result)

    def test_get_detection_details(self):
        """Test getting detection details."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["detection1"], include_hidden=True)

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"]},
            parameters={"include_hidden": True},
        )

        # Verify result - handle_api_response returns a list of resources
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)

    def test_get_detection_details_not_found(self):
        """Test getting detection details for non-existent detection."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["nonexistent"])

        # For empty resources, handle_api_response returns the default_result (empty list)
        # We should check that the result is empty
        self.assertEqual(result, [])

    def test_search_detections_include_hidden_false(self):
        """Test searching for detections with include_hidden=False."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"composite_id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections with include_hidden=False
        result = self.module.search_detections(
            filter="test query", include_hidden=False
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the second call includes include_hidden=False
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"]},
            parameters={"include_hidden": False},
        )

        # Verify result is paginated envelope
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["composite_id"], "detection1")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_detections_include_hidden_reaches_query_step(self):
        """include_hidden must reach the GetQueriesAlertsV2 query step.

        The query step is what decides which IDs — and therefore
        `pagination.total` — come back. Forwarding include_hidden only to the
        hydration step leaves hidden alerts in the result set and the count.
        """
        for include_hidden in (True, False):
            with self.subTest(include_hidden=include_hidden):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = [
                    {
                        "status_code": 200,
                        "body": {
                            "resources": ["detection1"],
                            "meta": {"pagination": {"offset": 0, "limit": 10, "total": 1}},
                        },
                    },
                    {
                        "status_code": 200,
                        "body": {"resources": [{"composite_id": "detection1"}]},
                    },
                ]

                self.module.search_detections(include_hidden=include_hidden)

                query_call = self.mock_client.command.call_args_list[0]
                self.assertEqual(query_call[0][0], "GetQueriesAlertsV2")
                self.assertEqual(
                    query_call[1]["parameters"].get("include_hidden"),
                    include_hidden,
                )

    def test_search_detections_include_hidden_is_query_param_not_body(self):
        """The hydration step must send include_hidden as a query param, not in the body.

        PostEntitiesAlertsV2 declares include_hidden `in: query`; a copy in the
        POST body is silently ignored, so asserting only that the value was
        "passed somewhere" would not catch the bug.
        """
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["detection1"],
                    "meta": {"pagination": {"offset": 0, "limit": 10, "total": 1}},
                },
            },
            {"status_code": 200, "body": {"resources": [{"composite_id": "detection1"}]}},
        ]

        self.module.search_detections(include_hidden=False)

        details_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(details_call[0][0], "PostEntitiesAlertsV2")
        self.assertEqual(details_call[1]["parameters"], {"include_hidden": False})
        self.assertNotIn("include_hidden", details_call[1]["body"])

    def test_get_detection_details_include_hidden_false(self):
        """Test getting detection details with include_hidden=False."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details with include_hidden=False
        result = self.module.get_detection_details(["detection1"], include_hidden=False)

        # Verify client command was called correctly with include_hidden=False
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"]},
            parameters={"include_hidden": False},
        )

        # Verify result
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)

    def test_get_detection_details_include_hidden_is_query_param_not_body(self):
        """include_hidden must land in query parameters, never in the POST body.

        PostEntitiesAlertsV2 declares it `in: query`; the API silently ignores a
        body copy, so a test that accepts either placement reproduces the bug.
        """
        for include_hidden in (True, False):
            with self.subTest(include_hidden=include_hidden):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": [{"composite_id": "detection1"}]},
                }

                self.module.get_detection_details(
                    ["detection1"], include_hidden=include_hidden
                )

                kwargs = self.mock_client.command.call_args[1]
                self.assertEqual(kwargs["parameters"], {"include_hidden": include_hidden})
                self.assertNotIn("include_hidden", kwargs["body"])


    def test_format_fql_error_response_error(self):
        """Test that error responses include FQL guide."""
        from falcon_mcp.resources.detections import SEARCH_DETECTIONS_FQL_DOCUMENTATION

        error_result = {"error": "Invalid filter syntax", "details": "..."}
        result = self.module._format_fql_error_response(
            errors=[error_result],
            filter_used="bad filter",
            fql_documentation=SEARCH_DETECTIONS_FQL_DOCUMENTATION
        )

        self.assertEqual(result["results"], [error_result])
        self.assertIn("fql_guide", result)
        self.assertEqual(result["fql_guide"], SEARCH_DETECTIONS_FQL_DOCUMENTATION)
        self.assertIn("error", result["hint"].lower())

    def test_aggregate_detections_builds_minimal_body(self):
        """Aggregating sends a list-wrapped spec and omits unset keys."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "alert_aggregation",
                        "buckets": [{"label": "Critical", "count": 7}],
                    }
                ]
            },
        }

        result = self.module.aggregate_detections(
            field="severity_name",
            type="terms",
            filter=None,
            size=10,
            sort=None,
            interval=None,
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="alert_aggregation",
            time_zone=None,
            sub_aggregates=None,
            include_hidden=True,
        )

        operation, kwargs = (
            self.mock_client.command.call_args[0][0],
            self.mock_client.command.call_args[1],
        )
        self.assertEqual(operation, "PostAggregatesAlertsV2")

        # The API rejects a bare object, so the body must be list-wrapped.
        self.assertEqual(
            kwargs["body"],
            [
                {
                    "type": "terms",
                    "field": "severity_name",
                    "name": "alert_aggregation",
                    "size": 10,
                }
            ],
        )
        self.assertEqual(result[0]["buckets"], [{"label": "Critical", "count": 7}])

    def test_aggregate_detections_forwards_include_hidden_as_query_param(self):
        """include_hidden travels as a query parameter, not inside the body spec."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "alert_aggregation", "buckets": []}]},
        }

        self.module.aggregate_detections(
            field="status",
            type="terms",
            filter=None,
            size=None,
            sort=None,
            interval=None,
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="alert_aggregation",
            time_zone=None,
            sub_aggregates=None,
            include_hidden=False,
        )

        kwargs = self.mock_client.command.call_args[1]
        self.assertEqual(kwargs["parameters"], {"include_hidden": False})
        self.assertNotIn("include_hidden", kwargs["body"][0])

    def test_aggregate_detections_passes_through_optional_spec_fields(self):
        """Optional aggregation controls reach the body under their wire names."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "daily", "buckets": []}]},
        }

        self.module.aggregate_detections(
            field="timestamp",
            type="date_histogram",
            filter="status:'new'",
            size=None,
            sort="_count|desc",
            interval="day",
            date_ranges=None,
            ranges=None,
            percents=None,
            missing="Unassigned",
            include="High|Critical",
            name="daily",
            time_zone="+00:00",
            sub_aggregates=[{"type": "terms", "field": "status"}],
            include_hidden=True,
        )

        spec = self.mock_client.command.call_args[1]["body"][0]
        self.assertEqual(spec["type"], "date_histogram")
        self.assertEqual(spec["interval"], "day")
        self.assertEqual(spec["filter"], "status:'new'")
        self.assertEqual(spec["sort"], "_count|desc")
        self.assertEqual(spec["missing"], "Unassigned")
        self.assertEqual(spec["include"], "High|Critical")
        self.assertEqual(spec["time_zone"], "+00:00")
        self.assertEqual(spec["sub_aggregates"], [{"type": "terms", "field": "status"}])

    def test_aggregate_detections_error(self):
        """A failed aggregation surfaces an error rather than empty buckets."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "failed to validate aggregates query(s)"}]},
        }

        result = self.module.aggregate_detections(
            field="severity_name",
            type="terms",
            filter=None,
            size=10,
            sort=None,
            interval=None,
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="alert_aggregation",
            time_zone=None,
            sub_aggregates=None,
            include_hidden=True,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_aggregate_detections_handles_null_buckets(self):
        """A zero-match aggregation returns buckets: null, which must pass through."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "alert_aggregation", "buckets": None, "sum_other_doc_count": 0}
                ]
            },
        }

        result = self.module.aggregate_detections(
            field="severity_name",
            type="terms",
            filter="status:'nonexistent'",
            size=10,
            sort=None,
            interval=None,
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="alert_aggregation",
            time_zone=None,
            sub_aggregates=None,
            include_hidden=True,
        )

        self.assertIsNone(result[0]["buckets"])

    def test_aggregate_detections_requires_type_specific_companion(self):
        """Types needing a companion argument fail fast instead of 500ing upstream."""
        cases = [
            ("date_histogram", "interval"),
            ("date_range", "date_ranges"),
            ("range", "ranges"),
        ]
        for agg_type, companion in cases:
            with self.subTest(agg_type=agg_type):
                self.mock_client.command.reset_mock()

                result = self.module.aggregate_detections(
                    field="timestamp",
                    type=agg_type,
                    filter=None,
                    size=None,
                    sort=None,
                    interval=None,
                    date_ranges=None,
                    ranges=None,
                    percents=None,
                    missing=None,
                    include=None,
                    name="alert_aggregation",
                    time_zone=None,
                    sub_aggregates=None,
                    include_hidden=True,
                )

                self.assertIn("error", result)
                self.assertIn(companion, result["error"])
                # The point of the guard: no request is sent at all.
                self.mock_client.command.assert_not_called()

    def test_aggregate_detections_accepts_type_with_its_companion(self):
        """Supplying the companion argument lets the request through."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "daily", "buckets": []}]},
        }

        result = self.module.aggregate_detections(
            field="timestamp",
            type="date_histogram",
            filter=None,
            size=None,
            sort=None,
            interval="day",
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="daily",
            time_zone=None,
            sub_aggregates=None,
            include_hidden=True,
        )

        self.assertEqual(result[0]["name"], "daily")
        self.mock_client.command.assert_called_once()

    def test_aggregate_detections_checks_nested_spec_companions(self):
        """A nested spec missing its companion argument is caught too.

        The API validates sub_aggregates the same way, so a nested
        date_histogram without an interval must not reach it.
        """
        result = self.module.aggregate_detections(
            field="status",
            type="terms",
            filter=None,
            size=None,
            sort=None,
            interval=None,
            date_ranges=None,
            ranges=None,
            percents=None,
            missing=None,
            include=None,
            name="alert_aggregation",
            time_zone=None,
            sub_aggregates=[{"type": "date_histogram", "field": "timestamp"}],
            include_hidden=True,
        )

        self.assertIn("error", result)
        self.assertIn("interval", result["error"])
        self.mock_client.command.assert_not_called()

    def test_aggregate_detections_is_read_only(self):
        """falcon_aggregate_detections must advertise itself as read-only."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_aggregate_detections",
            ToolAnnotations(
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_update_detections_has_write_annotations(self):
        """Verify falcon_update_detections has correct non-read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_detections",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_detections_status(self):
        """Test updating detection status."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"], status="in_progress",
            assign_to_uuid=None, assign_to_user_id=None,
            assign_to_name=None, unassign=None, append_comment=None, show_in_ui=None,
            add_tags=None, remove_tags=None, remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_called_once_with(
            "PatchEntitiesAlertsV3",
            body={
                "composite_ids": ["id1"],
                "action_parameters": [{"name": "update_status", "value": "in_progress"}],
            },
        )
        self.assertEqual(result, [])

    def test_update_detections_assign_uuid(self):
        """Test assigning detection to a user by UUID."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_uuid", "value": "00000000-0000-0000-0000-000000000000"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_user_id(self):
        """Test assigning detection to a user by email."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_user_id", "value": "analyst@example.com"},
            call_body["action_parameters"],
        )

    def test_update_detections_no_params_returns_error(self):
        """Test that providing no update params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_false(self):
        """Test hiding a detection from UI.

        show_in_ui must be sent as the string "false" — live-validated 2026-06-10:
        JSON boolean False returns 400 "failed to read and parse request";
        string "false" returns 200 and the read-back field is Python False.
        """
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=False,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "false"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign(self):
        """Test unassigning a detection from the current user."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "unassign", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign_false_only_returns_error(self):
        """Test that unassign=False as the only argument hits the no-param guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_api_error_returns_error_dict(self):
        """Test that a non-200 API response produces an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_uuid_and_name_returns_error(self):
        """Test that assign_to_uuid + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_user_id_and_name_returns_error(self):
        """Test that assign_to_user_id + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_user_id_and_unassign_returns_error(self):
        """Test that assign_to_user_id + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_name_and_unassign_returns_error(self):
        """Test that assign_to_name + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_invalid_status_returns_error(self):
        """Test that an invalid status value returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status="true_positive",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("status", result["error"])

    def test_update_detections_empty_ids_returns_error(self):
        """Test that passing an empty ids list returns an error without calling API."""
        result = self.module.update_detections(
            ids=[],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_true(self):
        """Test showing a detection in the UI sends the string 'true'."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=True,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_name(self):
        """Test assigning detection to a user by full name."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_name", "value": "Jane Smith"},
            call_body["action_parameters"],
        )

    def test_update_detections_append_comment(self):
        """Test appending a comment sends the correct action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="Investigating now",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "append_comment", "value": "Investigating now"},
            call_body["action_parameters"],
        )

    def test_update_detections_add_tags_resolution(self):
        """Test add_tags with a resolution tag emits an add_tag action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "true_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_add_tags_arbitrary(self):
        """Test that arbitrary (non-resolution) tags are accepted and emitted."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["custom_tag", "testing"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "custom_tag"},
            call_body["action_parameters"],
        )
        self.assertIn(
            {"name": "add_tag", "value": "testing"},
            call_body["action_parameters"],
        )

    def test_update_detections_remove_tags(self):
        """Test remove_tags emits a remove_tag action_parameter per tag."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=["false_positive"],
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "remove_tag", "value": "false_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_remove_tags_by_prefix(self):
        """Test remove_tags_by_prefix emits the remove_tags_by_prefix action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix="fc/",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "remove_tags_by_prefix", "value": "fc/"},
            call_body["action_parameters"],
        )

    def test_update_detections_empty_tag_returns_error(self):
        """Test that an empty/whitespace tag returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["   "],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_empty_remove_tag_returns_error(self):
        """Test that an empty/whitespace value in remove_tags returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=["   "],
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_empty_prefix_returns_error(self):
        """Test that an empty/whitespace remove_tags_by_prefix returns an error without calling API."""
        for prefix in ("", "   "):
            result = self.module.update_detections(
                ids=["id1"],
                status=None,
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=None,
                remove_tags=None,
                remove_tags_by_prefix=prefix,
            )

            self.mock_client.command.assert_not_called()
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)

    def test_update_detections_two_assign_params_returns_error(self):
        """Test that providing multiple assign_to_* params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("assign_to_uuid", result["error"])

    def test_update_detections_assign_and_unassign_returns_error(self):
        """Test that combining any assign_to_* with unassign=True returns an error."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("unassign", result["error"])

    def test_update_detections_empty_comment_returns_error(self):
        """Test that an empty comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("append_comment", result["error"])

    def test_update_detections_whitespace_only_comment_returns_error(self):
        """Test that a whitespace-only comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="   ",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_add_tags_combined_with_status(self):
        """Test combining add_tags with a status update in one call."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertIn("update_status", param_names)
        self.assertIn("add_tag", param_names)

    def test_update_detections_close_without_resolution_tag_returns_hint(self):
        """Test that closing without a resolution tag wraps success with a hint.

        Covers both add_tags=None and add_tags=[] (explicit empty list) — both must
        trigger the hint since neither carries a resolution tag.
        """
        mock_response = {"status_code": 200, "body": {"resources": []}}

        for add_tags in (None, []):
            self.mock_client.command.reset_mock()
            self.mock_client.command.return_value = mock_response

            result = self.module.update_detections(
                ids=["id1"],
                status="closed",
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=add_tags,
                remove_tags=None,
                remove_tags_by_prefix=None,
            )

            self.mock_client.command.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertIn("hint", result)
            self.assertIn("resolution", result["hint"].lower())
            self.assertEqual(result["result"], [])

    def test_update_detections_close_with_resolution_tag_no_hint(self):
        """Test that closing with any resolution tag returns the plain success shape."""
        mock_response = {"status_code": 200, "body": {"resources": []}}

        for tag in ("true_positive", "false_positive", "ignored"):
            self.mock_client.command.return_value = mock_response
            result = self.module.update_detections(
                ids=["id1"],
                status="closed",
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=[tag],
                remove_tags=None,
                remove_tags_by_prefix=None,
            )

            self.assertEqual(result, [], msg=f"hint must not fire for resolution tag {tag!r}")

    def test_update_detections_close_with_mixed_tags_no_hint(self):
        """Test that a resolution tag mixed with a custom tag still suppresses the hint."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive", "my_custom_tag"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertEqual(result, [])

    def test_update_detections_close_with_non_resolution_tag_returns_hint(self):
        """Test that closing with only a non-resolution tag still emits the hint."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["MY_CUSTOM_TAG"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("hint", result)
        self.assertEqual(result["result"], [])

    def test_update_detections_close_api_error_no_hint(self):
        """Test that an API error while closing is returned as-is, not hint-wrapped."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertNotIn("hint", result)

    def test_update_detections_omits_include_hidden(self):
        """update_detections must not send include_hidden at all.

        PatchEntitiesAlertsV3 declares the parameter, but sending False makes
        updates to hidden alerts fail outright (live-validated: 400 "no visible
        alert present in the update query"), which would make it impossible to
        un-hide an alert previously hidden via show_in_ui=False. Omitting it
        keeps the endpoint's own default.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        kwargs = self.mock_client.command.call_args[1]
        self.assertNotIn("parameters", kwargs)
        self.assertNotIn("include_hidden", kwargs["body"])

    def test_update_detections_unassign_false_is_noop(self):
        """Test that unassign=False does not add the action parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertNotIn("unassign", param_names)

    def test_update_detections_single_batch_no_chunking(self):
        """Exactly 1000 ids stay in one call (the API cap is inclusive)."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        ids = [f"id{i}" for i in range(1000)]

        result = self.module.update_detections(
            ids=ids,
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(
            self.mock_client.command.call_args[1]["body"]["composite_ids"], ids
        )
        self.assertEqual(result, [])

    def test_update_detections_chunks_over_1000_ids(self):
        """More than 1000 ids are split into batches of the API max and aggregated."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        ids = [f"id{i}" for i in range(2500)]

        result = self.module.update_detections(
            ids=ids,
            status="in_progress",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        # 2500 ids -> 1000 + 1000 + 500
        self.assertEqual(self.mock_client.command.call_count, 3)
        batches = [
            call.kwargs["body"]["composite_ids"]
            for call in self.mock_client.command.call_args_list
        ]
        self.assertEqual([len(b) for b in batches], [1000, 1000, 500])
        # Every id is covered exactly once, in order, with no overlap or gaps.
        self.assertEqual([cid for b in batches for cid in b], ids)
        # Each batch carries the same action parameters.
        for call in self.mock_client.command.call_args_list:
            self.assertEqual(
                call.kwargs["body"]["action_parameters"],
                [{"name": "update_status", "value": "in_progress"}],
            )
        self.assertEqual(result, [])

    def test_update_detections_failing_batch_surfaces_error(self):
        """A failure on any batch returns an error dict and stops further calls."""
        ok = {"status_code": 200, "body": {"resources": []}}
        boom = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        # First batch succeeds, second fails; third must never be attempted.
        self.mock_client.command.side_effect = [ok, boom, ok]
        ids = [f"id{i}" for i in range(2500)]

        result = self.module.update_detections(
            ids=ids,
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        # The first batch already mutated its ids on the backend (no rollback), so
        # the error must report them for a safe partial retry.
        self.assertIn("partial_success", result)
        self.assertEqual(result["partial_success"]["updated_count"], 1000)
        self.assertEqual(result["partial_success"]["updated_ids"], ids[:1000])
        self.assertEqual(result["partial_success"]["failed_and_remaining_ids"], ids[1000:])

    def test_update_detections_first_batch_failure_has_no_partial_success(self):
        """A failure on the very first batch reports no partial success (nothing applied)."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "boom"}]},
        }
        ids = [f"id{i}" for i in range(2500)]

        result = self.module.update_detections(
            ids=ids,
            status="in_progress",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertNotIn("partial_success", result)


if __name__ == "__main__":
    unittest.main()
