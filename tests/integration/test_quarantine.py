"""Integration tests for the Quarantine module."""

import pytest

from falcon_mcp.modules.quarantine import QuarantineModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestQuarantineIntegration(BaseIntegrationTest):
    """Integration tests for the Quarantine module with real API calls.

    Validates:
    - Correct FalconPy operation names for quarantine search and detail lookups
    - Two-step search pattern returns full quarantine details, not just IDs
    - Read-only count path works with a valid quarantine FQL filter
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Quarantine module with a real client."""
        self.module = QuarantineModule(falcon_client)

    def test_search_quarantined_files_returns_details(self):
        """Test that quarantine search returns full quarantine details."""
        result = self.call_method(self.module.search_quarantined_files, limit=5)

        self.assert_no_error(result, context="search_quarantined_files")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_quarantined_files",
        )
        records = self.records(result, context="search_quarantined_files")
        if len(records) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "sha256", "hostname"],
                context="search_quarantined_files",
            )

    def test_search_quarantined_files_with_sort(self):
        """Test quarantine search with a supported sort expression."""
        result = self.call_method(
            self.module.search_quarantined_files,
            sort="date_updated|desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_quarantined_files with sort")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_quarantined_files with sort",
        )

    def test_preview_quarantine_actions_with_filter(self):
        """Test the read-only quarantine action count with a valid FQL filter."""
        result = self.call_method(
            self.module.preview_quarantine_actions,
            filter="state:'quarantined'",
        )

        self.assert_no_error(result, context="preview_quarantine_actions")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="preview_quarantine_actions",
        )
        if result:
            assert isinstance(result[0], dict), (
                "Expected dict payload from preview_quarantine_actions"
            )
            assert "buckets" in result[0], (
                "Expected buckets in preview_quarantine_actions response"
            )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        search_quarantined_files exercises both QueryQuarantineFiles and
        GetQuarantineFiles via the two-step search pattern.
        """
        result = self.call_method(self.module.search_quarantined_files, limit=1)
        self.assert_no_error(result, context="QueryQuarantineFiles + GetQuarantineFiles operation names")

    # ------------------------------------------------------------------
    # Filter fields and the state vocabulary
    #
    # QueryQuarantineFiles answers an unknown field with an empty HTTP 200 (see
    # test_filter_classification.py), and so does a real field whose value matches
    # nothing — `sha256:'x'` and `zzz_not_a_field:'x'` are the same observation
    # here. A bogus-field control therefore proves nothing on its own, so field
    # existence is established from GetAggregateFiles instead: it returns buckets
    # for a field it knows and a null bucket list for one it does not.
    # ------------------------------------------------------------------

    def _aggregate_buckets(self, field):
        """Terms buckets for `field`, or None when the API does not know the field."""
        response = self.module.client.command(
            "GetAggregateFiles",
            body=[{"field": field, "type": "terms", "name": "probe", "size": 20}],
        )
        assert response.get("status_code") == 200, f"Aggregate on {field!r} failed: {response}"
        resources = (response.get("body") or {}).get("resources") or []
        return resources[0].get("buckets") if resources else None

    def test_aggregate_distinguishes_known_from_unknown_fields(self):
        """The oracle the two tests below rely on actually discriminates.

        A known field returns buckets and an unknown one returns null. Without
        this, `paths` coming back null would be indistinguishable from the
        aggregate simply not supporting nested fields.
        """
        assert self._aggregate_buckets("sha256"), (
            "GetAggregateFiles returned no buckets for sha256, a field that certainly "
            "exists. The field-existence oracle no longer works and the two tests "
            "below prove nothing."
        )
        assert self._aggregate_buckets("zzz_not_a_field") is None, (
            "GetAggregateFiles returned buckets for a field that cannot exist, so it "
            "no longer discriminates known from unknown fields."
        )

    def test_status_is_not_an_alias_for_state(self):
        """`status` is not a filter field, though it is accepted without error.

        The guide and all four quarantine hints used to offer it as an alias. It is
        unknown to the aggregate and matches nothing in a search, while `state`
        does both — and the `state` half runs here against the same records, so
        this is a divergence rather than an empty tenant.
        """
        assert self._aggregate_buckets("state"), (
            "state returned no aggregate buckets, so this tenant has no quarantine "
            "records to compare against and nothing here is conclusive."
        )
        assert self._aggregate_buckets("status") is None, (
            "status is now a known field. If it really works as an alias, restore it "
            "in the guide and the four quarantine filter hints."
        )

        matched = self.call_method(
            self.module.search_quarantined_files, filter="state:'quarantined'", limit=2
        )
        self.assert_envelope_ok(matched, context="state:'quarantined'")
        assert self.records(matched, "state:'quarantined'"), (
            "state:'quarantined' matched nothing, so the status comparison below has "
            "no positive control."
        )

        aliased = self.call_method(
            self.module.search_quarantined_files, filter="status:'quarantined'", limit=2
        )
        self.assert_envelope_ok(aliased, context="status:'quarantined'")
        assert not self.records(aliased, "status:'quarantined'"), (
            "status:'quarantined' now returns records while it previously matched "
            "nothing. Update the guide and the four quarantine hints."
        )

    def test_state_vocabulary_matches_the_aggregate(self):
        """Every state the field actually holds is filterable, and the hint lists them.

        The hint offered only quarantined and released. Set equality against the
        aggregate's own bucket labels is what keeps the list from drifting in
        either direction.
        """
        buckets = self._aggregate_buckets("state")
        assert buckets, "No state buckets, so there is nothing to check."
        observed = {bucket["label"] for bucket in buckets}
        documented = {"quarantined", "released", "purged", "cleaned", "error", "unknown"}
        assert observed <= documented, (
            f"The state field holds values the guide and hint do not list: "
            f"{sorted(observed - documented)}. Add them."
        )

        for value in sorted(observed):
            self.assert_filter_matches(
                self.module.search_quarantined_files,
                f"state:'{value}'",
                note="Each state the aggregate reports must also be filterable.",
                limit=2,
            )

    def test_paths_filters_only_in_its_dotted_form(self):
        """`paths.path` filters; bare `paths` does not.

        Bare `paths` appeared in all four quarantine hints and nowhere else in the
        repo except the response shape. It is unknown to the aggregate, and a real
        path value that `paths.path` matches returns nothing through `paths`.
        """
        assert self._aggregate_buckets("paths.path"), "No paths.path buckets to work from."
        assert self._aggregate_buckets("paths.state"), "No paths.state buckets to work from."
        assert self._aggregate_buckets("paths") is None, (
            "Bare `paths` is now a known field. If it filters, put it back in the "
            "guide and the four quarantine hints."
        )

        real_path = self._aggregate_buckets("paths.path")[0]["label"]

        self.assert_filter_matches(
            self.module.search_quarantined_files,
            f"paths.path:'{real_path}'",
            predicate=lambda record: any(
                entry.get("path") == real_path for entry in record.get("paths") or []
            ),
            predicate_desc=f"record carries the path {real_path!r}",
            note="paths.path is the dotted form the hint now documents.",
            limit=2,
        )

        bare = self.call_method(
            self.module.search_quarantined_files, filter=f"paths:'{real_path}'", limit=2
        )
        self.assert_envelope_ok(bare, context="bare paths")
        assert not self.records(bare, "bare paths"), (
            f"paths:'{real_path}' now returns records. The dotted form matched the "
            "same value on the line above, so if both work the hints can offer either."
        )
