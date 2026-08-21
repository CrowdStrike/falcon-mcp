"""Integration tests for the Zero Trust Assessment module."""

import pytest

from falcon_mcp.modules.zero_trust_assessment import ZeroTrustAssessmentModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

# An AID is 32 lowercase hex characters; an all-zero one cannot belong to a real host.
BOGUS_AID = "0" * 32


@pytest.mark.integration
class TestZeroTrustAssessmentIntegration(BaseIntegrationTest):
    """Integration tests for Zero Trust Assessment with real API calls.

    Validates:
    - Correct FalconPy operation names (getAssessmentsByScoreV1, getAssessmentV1, getAuditV1)
    - The score filter the search tool builds is accepted by the query endpoint
    - The query's `score` matches `assessment.overall` in the hydrated record
    - An unassessed AID is reported in `not_found` rather than silently dropped
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Zero Trust Assessment module with a real client."""
        self.module = ZeroTrustAssessmentModule(falcon_client)

    def test_search_zta_assessments_returns_envelope(self):
        """search_zta_assessments returns the pagination envelope with a real count.

        Validates the getAssessmentsByScoreV1 and getAssessmentV1 operation names, and
        that the locally built `score:<=50` filter is accepted.
        """
        result = self.call_method(self.module.search_zta_assessments, max_score=50)

        self.assert_no_error(result, context="search_zta_assessments")
        self.assert_valid_list_response(result, context="search_zta_assessments")

        assert result["filter_used"] == "score:<=50"
        assert result["pagination"]["total"] is not None, (
            "Expected the query endpoint to report a total, got "
            f"{result['pagination']}"
        )

    def test_search_zta_assessments_returns_full_details(self):
        """The search tool hydrates the query's AIDs into full assessment records."""
        result = self.call_method(self.module.search_zta_assessments, max_score=100, limit=5)

        self.assert_no_error(result, context="search_zta_assessments details")

        if not result["results"]:
            self.skip_with_warning(
                "No assessed hosts in this tenant", context="search_zta_assessments"
            )

        self.assert_search_returns_details(
            result,
            expected_fields=["aid", "cid", "assessment", "assessment_items"],
            context="search_zta_assessments",
        )

    def test_query_score_matches_assessment_overall(self):
        """The score the query reports equals `assessment.overall` in the detail record.

        Chains the raw query into get_zta_assessments so both values are observable.
        """
        query = self.module.client.command(
            "getAssessmentsByScoreV1",
            parameters={"filter": "score:>=0", "limit": 5, "sort": "score|asc"},
        )
        scores_by_aid = {
            record["aid"]: record["score"]
            for record in query.get("body", {}).get("resources", [])
        }

        if not scores_by_aid:
            self.skip_with_warning(
                "No assessed hosts in this tenant", context="query_score_matches"
            )

        result = self.call_method(
            self.module.get_zta_assessments, ids=list(scores_by_aid)
        )

        self.assert_no_error(result, context="get_zta_assessments")
        assert result["not_found"] == [], (
            f"AIDs the query just returned should still resolve: {result['not_found']}"
        )

        for record in result["results"]:
            assert record["assessment"]["overall"] == scores_by_aid[record["aid"]], (
                f"Score mismatch for {record['aid']}: query reported "
                f"{scores_by_aid[record['aid']]}, detail reported "
                f"{record['assessment']['overall']}"
            )

    def test_get_zta_assessments_reports_unassessed_aid(self):
        """An AID with no assessment comes back in `not_found`, not as an error.

        The API answers an unknown AID with a success status and simply omits the
        record, so this proves the miss is surfaced.
        """
        result = self.call_method(self.module.get_zta_assessments, ids=[BOGUS_AID])

        self.assert_no_error(result, context="get_zta_assessments bogus AID")
        assert result["results"] == []
        assert result["not_found"] == [BOGUS_AID]

    def test_get_zta_audit_returns_tenant_summary(self):
        """get_zta_audit returns one CID-level rollup.

        Validates the getAuditV1 operation name.
        """
        result = self.call_method(self.module.get_zta_audit)

        self.assert_no_error(result, context="get_zta_audit")
        self.assert_valid_list_response(result, min_length=1, context="get_zta_audit")

        summary = result[0]
        for field in ("num_aids", "average_overall_score", "platforms"):
            assert field in summary, (
                f"Expected '{field}' in the audit summary. "
                f"Available fields: {list(summary.keys())}"
            )

    def test_search_rejects_inverted_bounds_without_calling_the_api(self):
        """Inverted score bounds are refused locally, so the API is never asked."""
        result = self.call_method(
            self.module.search_zta_assessments, min_score=80, max_score=20
        )

        assert "error" in result
        assert "details" not in result, (
            "An inverted-bounds rejection must be local, but the response carries "
            "API details"
        )
