"""Integration tests for the Intel module."""

import time
from datetime import datetime, timezone

import pytest

from falcon_mcp.modules.intel import IntelModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIntelIntegration(BaseIntegrationTest):
    """Integration tests for Intel module with real API calls.

    Validates:
    - Correct FalconPy operation names (QueryIntelActorEntities, QueryIntelIndicatorEntities, etc.)
    - Combined query endpoints return full details directly
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the intel module with a real client."""
        self.module = IntelModule(falcon_client)

    def test_query_actor_entities_returns_details(self):
        """Test that query_actor_entities returns full actor details.

        Validates the QueryIntelActorEntities operation name is correct.
        """
        result = self.call_method(self.module.query_actor_entities, limit=5)

        self.assert_no_error(result, context="query_actor_entities")
        self.assert_valid_list_response(result, min_length=0, context="query_actor_entities")

        records = self.records(result, context="query_actor_entities")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="query_actor_entities",
            )

    def test_query_actor_entities_with_filter(self):
        """Test query_actor_entities with FQL filter."""
        result = self.call_method(
            self.module.query_actor_entities,
            filter="target_industries:'Technology'",
            limit=3,
        )

        self.assert_no_error(result, context="query_actor_entities with filter")
        self.assert_valid_list_response(result, min_length=0, context="query_actor_entities with filter")

    def test_query_actor_entities_with_free_text(self):
        """Test query_actor_entities with free text search."""
        result = self.call_method(
            self.module.query_actor_entities,
            q="BEAR",
            limit=5,
        )

        self.assert_no_error(result, context="query_actor_entities with q param")
        self.assert_valid_list_response(result, min_length=0, context="query_actor_entities with q param")

    def test_query_indicator_entities_returns_details(self):
        """Test that query_indicator_entities returns full indicator details.

        Validates the QueryIntelIndicatorEntities operation name is correct.
        """
        result = self.call_method(self.module.query_indicator_entities, limit=5)

        self.assert_no_error(result, context="query_indicator_entities")
        self.assert_valid_list_response(result, min_length=0, context="query_indicator_entities")

        records = self.records(result, context="query_indicator_entities")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "indicator"],
                context="query_indicator_entities",
            )

    def test_query_indicator_entities_with_filter(self):
        """Test query_indicator_entities with FQL filter."""
        result = self.call_method(
            self.module.query_indicator_entities,
            filter="type:'domain'",
            limit=3,
        )

        self.assert_no_error(result, context="query_indicator_entities with filter")
        self.assert_valid_list_response(result, min_length=0, context="query_indicator_entities with filter")

    def test_query_report_entities_returns_details(self):
        """Test that query_report_entities returns full report details.

        Validates the QueryIntelReportEntities operation name is correct.
        """
        result = self.call_method(self.module.query_report_entities, limit=5)

        self.assert_no_error(result, context="query_report_entities")
        self.assert_valid_list_response(result, min_length=0, context="query_report_entities")

        records = self.records(result, context="query_report_entities")
        if len(records) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="query_report_entities",
            )

    def test_query_report_entities_with_filter(self):
        """Test query_report_entities with FQL filter."""
        result = self.call_method(
            self.module.query_report_entities,
            filter="type:'CSIT'",
            limit=3,
        )

        self.assert_no_error(result, context="query_report_entities with filter")
        self.assert_valid_list_response(result, min_length=0, context="query_report_entities with filter")

    def test_get_mitre_report_with_actor_name(self):
        """Test get_mitre_report JSON format returns parsed list of dicts.

        First searches for an actor, then gets their MITRE report.
        Validates both QueryIntelActorEntities and GetMitreReport operations.
        """
        # First, search for an actor to get a valid name
        search_result = self.skip_unless_tenant_has(
            self.call_method(self.module.query_actor_entities, limit=1),
            "actors",
            context="test_get_mitre_report_with_actor_name",
        )

        actor_name = search_result[0].get("name")
        if not actor_name:
            self.skip_with_warning(
                "Could not extract actor name from search results",
                context="test_get_mitre_report_with_actor_name",
            )

        # Now get MITRE report for that actor in JSON format
        result = self.call_method(self.module.get_mitre_report, actor=actor_name, format="json")

        # JSON format must return a list (possibly empty for actors without MITRE mappings)
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict) and "error" in first_item:
                # Some actors may not have MITRE reports
                self.skip_with_warning(
                    f"MITRE report not available for actor: {actor_name}",
                    context="test_get_mitre_report_with_actor_name",
                )

        assert isinstance(result, list), (
            f"Expected list for JSON format, got {type(result).__name__}: {repr(result)[:200]}"
        )

        # If we got results, validate the structure
        if result:
            assert isinstance(result[0], dict), (
                f"Expected list of dicts, got list of {type(result[0]).__name__}"
            )
            expected_fields = {"id", "tactic_id", "tactic_name", "technique_id", "technique_name"}
            actual_fields = set(result[0].keys())
            missing = expected_fields - actual_fields
            assert not missing, f"Missing expected MITRE fields: {missing}"

    def test_get_mitre_report_csv_format(self):
        """Test get_mitre_report CSV format returns raw string.

        Validates that CSV format is not parsed and remains a string.
        """
        # First, search for an actor to get a valid name
        search_result = self.skip_unless_tenant_has(
            self.call_method(self.module.query_actor_entities, limit=1),
            "actors",
            context="test_get_mitre_report_csv_format",
        )

        actor_name = search_result[0].get("name")
        if not actor_name:
            self.skip_with_warning(
                "Could not extract actor name from search results",
                context="test_get_mitre_report_csv_format",
            )

        # Get MITRE report in CSV format
        result = self.call_method(self.module.get_mitre_report, actor=actor_name, format="csv")

        # Handle error response (actor may not have MITRE data)
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict) and "error" in first_item:
                self.skip_with_warning(
                    f"MITRE report not available for actor: {actor_name}",
                    context="test_get_mitre_report_csv_format",
                )

        # CSV format must return a string
        assert isinstance(result, str), (
            f"Expected str for CSV format, got {type(result).__name__}: {repr(result)[:200]}"
        )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test QueryIntelActorEntities
        result = self.call_method(self.module.query_actor_entities, limit=1)
        self.assert_no_error(result, context="QueryIntelActorEntities operation name")

        # Test QueryIntelIndicatorEntities
        result = self.call_method(self.module.query_indicator_entities, limit=1)
        self.assert_no_error(result, context="QueryIntelIndicatorEntities operation name")

        # Test QueryIntelReportEntities
        result = self.call_method(self.module.query_report_entities, limit=1)
        self.assert_no_error(result, context="QueryIntelReportEntities operation name")

    # ------------------------------------------------------------------
    # Actor and report filter shapes
    #
    # These endpoints reject an unknown field but answer an impossible value with
    # an empty 200 (see test_filter_classification.py), so each value below is
    # established by rows. Actor content is CrowdStrike's own catalog rather than
    # tenant data, so scarcity does not apply to the actor cases.
    # ------------------------------------------------------------------

    def _actor_count(self, filter=None):
        """Number of actors matching `filter`.

        Counted from the returned records rather than `pagination.total`, which
        this endpoint reports as 1 regardless of how many actors come back — so a
        total-based comparison would read every filter as identical.
        """
        result = self.call_method(
            self.module.query_actor_entities, filter=filter, limit=200
        )
        self.assert_envelope_ok(result, context=f"actors {filter!r}")
        return len(self.records(result, context=f"actors {filter!r}"))

    def test_actor_last_activity_date_accepts_relative_dates(self):
        """`last_activity_date:>'now-90d'` is honored, not dropped.

        The guide showed only an epoch integer for this field and documented
        relative dates on indicators, a different operation. A dropped clause would
        return the same actors as no filter at all, so the assertion is that the
        result is strictly smaller — and the wider window returning everything is
        what shows the narrowing came from the cutoff rather than a broken filter.
        """
        unfiltered = self._actor_count()
        assert unfiltered > 1, f"Only {unfiltered} actors available; nothing to narrow."

        recent = self._actor_count("last_activity_date:>'now-90d'")
        assert 0 < recent < unfiltered, (
            f"last_activity_date:>'now-90d' returned {recent} of {unfiltered} actors. "
            "Zero means no actor is recently active; equal means the clause was "
            "parsed as garbage and dropped. Neither confirms the syntax."
        )

        wide = self._actor_count("last_activity_date:>'now-3650d'")
        assert wide == unfiltered, (
            f"A ten-year window returned {wide} of {unfiltered} actors, so the field "
            "is not simply a cutoff on activity and the comparison above is unsound."
        )

    def test_actor_motivations_and_target_industries(self):
        """The documented motivation and industry values are real, not invented.

        Enumerated from the actor catalog first, so every value asserted here is
        one the API itself reports; a bogus value is checked in the same run to
        show the filter is doing the selecting.
        """
        actors = self.records(
            self.call_method(self.module.query_actor_entities, limit=100),
            context="actor catalog",
        )
        assert actors, "No actors returned, so nothing can be enumerated."

        def values(field):
            return {
                entry["value"]
                for actor in actors
                for entry in actor.get(field) or []
                if entry.get("value")
            }

        for field, hint_values in (
            ("motivations", {"State-Sponsored", "Criminal"}),
            (
                "target_industries",
                {"Financial Services", "Government", "Technology", "Healthcare", "Energy"},
            ),
        ):
            observed = values(field)
            assert hint_values <= observed, (
                f"The {field} values the hint documents are not in the catalog: "
                f"{sorted(hint_values - observed)}. Either they were invented or the "
                "catalog changed."
            )
            for value in sorted(hint_values):
                self.assert_filter_matches(
                    self.module.query_actor_entities,
                    f"{field}.value:'{value}'",
                    predicate=lambda actor, field=field, value=value: any(
                        entry.get("value") == value for entry in actor.get(field) or []
                    ),
                    predicate_desc=f"actor.{field} includes {value!r}",
                    note=f"Every {field}.value in the hint must select actors.",
                    limit=3,
                )

            assert self._actor_count(f"{field}.value:'ZZZ Not A Value'") == 0, (
                f"A nonsense {field}.value matched actors, so the filter is not "
                "selecting and the assertions above prove nothing."
            )

    def test_report_created_date_accepts_three_forms(self):
        """`created_date` takes an ISO string, an unquoted epoch, or a relative expression.

        The field table gave an epoch integer while the notes said the format must
        be ISO — each was right about a form the other omitted. A *quoted* epoch is
        the one shape that fails, which is why the note now says unquoted.

        Each predicate checks the row against the cutoff the filter asked for, and
        the relative form additionally has to narrow the population. Asserting only
        that `created_date` is an integer would be satisfied by every report alive,
        so a clause the API parsed as garbage and dropped would still pass.
        """
        reports = self.skip_unless_tenant_has(
            self.call_method(self.module.query_report_entities, limit=3),
            "intel reports",
            context="report created_date",
        )
        epoch = reports[0].get("created_date")
        assert isinstance(epoch, int), (
            f"created_date is no longer an epoch integer in the response: {epoch!r}. "
            "The field table's type needs updating."
        )

        iso_cutoff = int(
            datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
        )
        for filter, cutoff in (
            (f"created_date:>{epoch - 1}", epoch - 1),
            ("created_date:>'2020-01-01T00:00:00Z'", iso_cutoff),
        ):
            self.assert_filter_matches(
                self.module.query_report_entities,
                filter,
                predicate=lambda report, cutoff=cutoff: (
                    isinstance(report.get("created_date"), int)
                    and report["created_date"] > cutoff
                ),
                predicate_desc=f"report.created_date > {cutoff}",
                note="All three date forms are documented for created_date.",
                limit=3,
            )

        relative_cutoff = int(time.time()) - 30 * 86400
        self.assert_filter_narrows(
            self.module.query_report_entities,
            "created_date:>'now-30d'",
            predicate=lambda report: (
                isinstance(report.get("created_date"), int)
                and report["created_date"] > relative_cutoff
            ),
            predicate_desc=f"report.created_date > {relative_cutoff} (now-30d)",
            note="The relative form is the one most likely to be silently dropped.",
            limit=3,
        )

        quoted = self.call_method(
            self.module.query_report_entities,
            filter=f"created_date:>'{epoch - 1}'",
            limit=1,
        )
        assert self.error_dicts(quoted), (
            f"A quoted epoch was accepted. If it now works, drop the caveat from the "
            f"guide's notes. Got: {quoted}"
        )
