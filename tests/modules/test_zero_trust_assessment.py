"""
Tests for the Zero Trust Assessment module.
"""

import inspect
import unittest
from typing import Any

from pydantic.fields import FieldInfo

from falcon_mcp.modules.zero_trust_assessment import (
    ZeroTrustAssessmentModule,
    _build_score_filter,
)
from tests.modules.utils.test_modules import TestModules

QUERY_OP = "getAssessmentsByScoreV1"
ENTITY_OP = "getAssessmentV1"
AUDIT_OP = "getAuditV1"


def _query_response(aids_and_scores, pagination=None):
    """Build a getAssessmentsByScoreV1 response with {aid, score} resources."""
    body: dict[str, Any] = {
        "resources": [{"aid": aid, "score": score} for aid, score in aids_and_scores]
    }
    if pagination is not None:
        body["meta"] = {"pagination": pagination}
    return {"status_code": 200, "body": body}


def _entity_response(aids_and_scores):
    """Build a getAssessmentV1 response with full assessment records."""
    return {
        "status_code": 200,
        "body": {
            "resources": [
                {
                    "aid": aid,
                    "cid": "cid1",
                    "event_platform": "Win",
                    "assessment": {"overall": score, "os": score, "sensor_config": score},
                    "assessment_items": {"os_signals": [], "sensor_signals": []},
                }
                for aid, score in aids_and_scores
            ]
        },
    }


class TestZeroTrustAssessmentModule(TestModules):
    """Test cases for the Zero Trust Assessment module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ZeroTrustAssessmentModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_zta_assessments",
            "falcon_get_zta_assessments",
            "falcon_get_zta_audit",
        ]
        self.assert_tools_registered(expected_tools)

    # ---- Filter construction ------------------------------------------------------

    def test_build_score_filter_both_bounds(self):
        """Both bounds are joined with the AND operator."""
        self.assertEqual(_build_score_filter(20, 60), "score:>=20+score:<=60")

    def test_build_score_filter_min_only(self):
        """A min bound alone produces a single clause."""
        self.assertEqual(_build_score_filter(20, None), "score:>=20")

    def test_build_score_filter_max_only(self):
        """A max bound alone produces a single clause."""
        self.assertEqual(_build_score_filter(None, 60), "score:<=60")

    def test_build_score_filter_no_bounds(self):
        """No bounds falls back to the match-everything filter the API requires."""
        self.assertEqual(_build_score_filter(None, None), "score:>=0")

    def test_build_score_filter_equal_bounds(self):
        """Equal bounds select an exact score without being rejected."""
        self.assertEqual(_build_score_filter(50, 50), "score:>=50+score:<=50")

    def test_search_sends_built_filter_and_reports_it(self):
        """The built FQL reaches the API and comes back as filter_used."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments(min_score=10, max_score=40)

        query_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(query_call[0][0], QUERY_OP)
        self.assertEqual(
            query_call[1]["parameters"]["filter"], "score:>=10+score:<=40"
        )
        self.assertEqual(result["filter_used"], "score:>=10+score:<=40")

    def test_search_without_bounds_sends_default_filter(self):
        """Omitting both bounds still sends a filter, because the API demands one."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments()

        query_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(query_call[1]["parameters"]["filter"], "score:>=0")
        self.assertEqual(result["filter_used"], "score:>=0")

    # ---- Sort and bound validation ------------------------------------------------

    def test_search_sort_order_asc(self):
        """sort_order 'asc' maps to the pipe-separated sort the API accepts."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        self.module.search_zta_assessments(sort_order="asc")

        query_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(query_call[1]["parameters"]["sort"], "score|asc")

    def test_search_sort_order_desc(self):
        """sort_order 'desc' maps to the pipe-separated sort the API accepts."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 90)]),
            _entity_response([("aid1", 90)]),
        ]

        self.module.search_zta_assessments(sort_order="desc")

        query_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(query_call[1]["parameters"]["sort"], "score|desc")

    def test_search_invalid_sort_order_is_rejected_locally(self):
        """An unsupported sort_order is refused without spending an API call."""
        result = self.module.search_zta_assessments(sort_order="score.asc")

        self.assertIn("error", result)
        self.assertIn("score.asc", result["error"])
        self.mock_client.command.assert_not_called()

    def test_search_inverted_bounds_are_rejected_locally(self):
        """min_score above max_score is refused instead of returning zero rows."""
        result = self.module.search_zta_assessments(min_score=80, max_score=20)

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_search_declares_asc_as_the_default_sort_order(self):
        """The weakest-first default is declared on the signature."""
        declared = inspect.signature(
            self.module.search_zta_assessments
        ).parameters["sort_order"].default

        self.assertEqual(declared.default, "asc")

    def test_search_zero_arg_call_resolves_field_defaults(self):
        """A call with no arguments uses the real defaults and leaks no FieldInfo (issue #384)."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments()

        query_params = self.mock_client.command.call_args_list[0][1]["parameters"]
        self.assertEqual(query_params["sort"], "score|asc")
        self.assertEqual(query_params["limit"], 100)
        # An unresolved `after` FieldInfo would survive prepare_api_parameters' None filter.
        self.assertNotIn("after", query_params)

        def assert_no_fieldinfo(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    assert_no_fieldinfo(value)
            elif isinstance(obj, list):
                for value in obj:
                    assert_no_fieldinfo(value)
            else:
                self.assertNotIsInstance(obj, FieldInfo)

        assert_no_fieldinfo(result)
        assert_no_fieldinfo(query_params)

    # ---- Pagination and two-step wiring -------------------------------------------

    def test_search_surfaces_pagination_cursor_as_next(self):
        """The API's `after` cursor is surfaced as `pagination.next`."""
        self.mock_client.command.side_effect = [
            _query_response(
                [("aid1", 30)],
                pagination={"limit": 100, "total": 18958, "after": "cursor-abc"},
            ),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments()

        self.assert_pagination(result, 18958, has_next=True)
        self.assertEqual(result["pagination"]["next"], "cursor-abc")

    def test_search_forwards_after_token(self):
        """A supplied `after` token is passed through to the query endpoint."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        self.module.search_zta_assessments(after="cursor-abc")

        query_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(query_call[1]["parameters"]["after"], "cursor-abc")

    def test_search_hydrates_query_aids(self):
        """Both operations are called, and hydration receives the query's AIDs."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 10), ("aid2", 20)]),
            _entity_response([("aid1", 10), ("aid2", 20)]),
        ]

        result = self.module.search_zta_assessments()

        operations = [call[0][0] for call in self.mock_client.command.call_args_list]
        self.assertEqual(operations, [QUERY_OP, ENTITY_OP])

        entity_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(entity_call[1]["parameters"]["ids"], ["aid1", "aid2"])

        # Full details, not the {aid, score} pairs from the query step.
        self.assertEqual(len(result["results"]), 2)
        self.assertIn("assessment_items", result["results"][0])

    def test_search_restores_query_sort_order(self):
        """Hydrated records are reordered to match the query's sort."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 10), ("aid2", 20), ("aid3", 30)]),
            # The entity endpoint answers out of order.
            _entity_response([("aid3", 30), ("aid1", 10), ("aid2", 20)]),
        ]

        result = self.module.search_zta_assessments()

        self.assertEqual(
            [record["aid"] for record in result["results"]], ["aid1", "aid2", "aid3"]
        )

    def test_search_empty_result_returns_envelope(self):
        """An empty query returns the envelope and skips the entity endpoint."""
        self.mock_client.command.return_value = _query_response(
            [], pagination={"limit": 100, "total": 0}
        )

        result = self.module.search_zta_assessments(max_score=1)

        self.assertEqual(result["results"], [])
        self.assert_pagination(result, 0)
        self.assertEqual(result["filter_used"], "score:<=1")
        self.mock_client.command.assert_called_once()

    def test_search_omits_not_found_when_all_aids_resolve(self):
        """`not_found` stays absent from the search envelope when nothing is missing."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments()

        self.assertNotIn("not_found", result)

    def test_search_reports_aid_that_vanished_between_calls(self):
        """An AID the entity step drops is reported rather than silently lost."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30), ("aid2", 40)]),
            _entity_response([("aid1", 30)]),
        ]

        result = self.module.search_zta_assessments()

        self.assertEqual(result["not_found"], ["aid2"])
        self.assertEqual(len(result["results"]), 1)

    def test_search_query_error_is_wrapped_in_a_list(self):
        """A failed query is returned as a single-item list, not an envelope."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "missing filter expression"}]},
        }

        result = self.module.search_zta_assessments()

        self.assertIn("error", result[0])
        self.assertTrue(
            result[0]["error"].startswith("Failed to search Zero Trust Assessment scores")
        )

    def test_search_hydration_error_is_wrapped_in_a_list(self):
        """A failed hydration step is returned as a single-item list."""
        self.mock_client.command.side_effect = [
            _query_response([("aid1", 30)]),
            {"status_code": 403, "body": {"errors": [{"message": "access denied"}]}},
        ]

        result = self.module.search_zta_assessments()

        self.assertIn("error", result[0])

    # ---- get_zta_assessments ------------------------------------------------------

    def test_get_assessments_returns_results_and_empty_not_found(self):
        """`not_found` is present even when every requested AID resolved."""
        self.mock_client.command.return_value = _entity_response([("aid1", 30)])

        result = self.module.get_zta_assessments(ids=["aid1"])

        self.mock_client.command.assert_called_once_with(
            ENTITY_OP, parameters={"ids": ["aid1"]}
        )
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["not_found"], [])

    def test_get_assessments_reports_unassessed_aids(self):
        """An AID the API omits from a 200 response lands in `not_found`."""
        self.mock_client.command.return_value = _entity_response([("aid1", 30)])

        result = self.module.get_zta_assessments(ids=["aid1", "aid-unknown"])

        self.assertEqual(result["not_found"], ["aid-unknown"])
        self.assertEqual(len(result["results"]), 1)

    def test_get_assessments_not_found_preserves_request_order(self):
        """Missing AIDs are reported in the order they were requested."""
        self.mock_client.command.return_value = _entity_response([("aid2", 30)])

        result = self.module.get_zta_assessments(ids=["aid1", "aid2", "aid3"])

        self.assertEqual(result["not_found"], ["aid1", "aid3"])

    def test_get_assessments_error_is_returned_unchanged(self):
        """A failed lookup returns the error dict, not an envelope."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Max number of AIDs allowed is 1000"}]},
        }

        result = self.module.get_zta_assessments(ids=["aid1"])

        self.assertIn("error", result)
        self.assertNotIn("results", result)

    def test_get_assessments_declares_the_api_id_bounds(self):
        """The 1-1000 AID range the endpoint enforces is declared on the parameter."""
        declared = inspect.signature(
            self.module.get_zta_assessments
        ).parameters["ids"].default

        constraints = {type(m).__name__: m for m in declared.metadata}
        self.assertEqual(constraints["MinLen"].min_length, 1)
        self.assertEqual(constraints["MaxLen"].max_length, 1000)

    # ---- get_zta_audit ------------------------------------------------------------

    def test_get_audit_returns_one_record(self):
        """The audit endpoint returns a single CID-level rollup."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "cid": "cid1",
                        "num_aids": 18958,
                        "average_overall_score": 61.5,
                        "platforms": [{"name": "Windows", "num_aids": 900}],
                    }
                ]
            },
        }

        result = self.module.get_zta_audit()

        self.mock_client.command.assert_called_once_with(AUDIT_OP, parameters={})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["num_aids"], 18958)
        self.assertIn("platforms", result[0])

    def test_get_audit_error_is_wrapped_in_a_list(self):
        """A failed audit call is returned as a single-item list."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }

        result = self.module.get_zta_audit()

        self.assertIn("error", result[0])
        self.assertTrue(
            result[0]["error"].startswith(
                "Failed to get the Zero Trust Assessment audit summary"
            )
        )


if __name__ == "__main__":
    unittest.main()
