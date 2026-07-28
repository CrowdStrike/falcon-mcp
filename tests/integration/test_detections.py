"""Integration tests for the Detections module."""

import pytest

from falcon_mcp.modules.detections import DetectionsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDetectionsIntegration(BaseIntegrationTest):
    """Integration tests for Detections module with real API calls.

    Validates:
    - Correct FalconPy operation names (GetQueriesAlertsV2, PostEntitiesAlertsV2)
    - Two-step search pattern returns full details, not just IDs
    - POST body usage for get_by_ids
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the detections module with a real client."""
        self.module = DetectionsModule(falcon_client)

    def test_search_detections_returns_details(self):
        """Test that search_detections returns full detection details, not just IDs.

        This validates the two-step search pattern:
        1. GetQueriesAlertsV2 returns detection IDs
        2. PostEntitiesAlertsV2 returns full details
        """
        result = self.call_method(self.module.search_detections, limit=5)

        self.assert_no_error(result, context="search_detections")
        self.assert_valid_list_response(result, min_length=0, context="search_detections")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["composite_id", "severity", "status"],
                context="search_detections",
            )

    def test_search_detections_with_filter(self):
        """Test search_detections with FQL filter."""
        result = self.call_method(
            self.module.search_detections,
            filter="status:'new'",
            limit=3,
        )

        self.assert_no_error(result, context="search_detections with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_detections with filter")

    def test_search_detections_with_sort(self):
        """Test search_detections with sort parameter."""
        result = self.call_method(
            self.module.search_detections,
            sort="severity.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_detections with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_detections with sort")

    def test_get_detection_details_with_valid_id(self):
        """Test get_detection_details with a valid detection ID.

        First searches for a detection, then gets its details.
        """
        # First, search for a detection to get a valid ID
        search_result = self.call_method(self.module.search_detections, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No detections available to test get_detection_details",
                context="test_get_detection_details_with_valid_id",
            )

        detection_id = self.get_first_id(search_result, id_field="composite_id")
        if not detection_id:
            self.skip_with_warning(
                "Could not extract detection ID from search results",
                context="test_get_detection_details_with_valid_id",
            )

        # Now get details for that detection
        result = self.call_method(self.module.get_detection_details, ids=[detection_id])

        self.assert_no_error(result, context="get_detection_details")
        self.assert_valid_list_response(result, min_length=1, context="get_detection_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["composite_id", "severity", "status"],
            context="get_detection_details",
        )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        This test catches typos like 'GetQueriesAlertsV2' vs 'GetQueryAlertsV2'.
        """
        # Simple search should work if operation names are correct
        result = self.call_method(self.module.search_detections, limit=1)

        # If operation name is wrong, this will be an error response
        self.assert_no_error(result, context="operation name validation")

        # PostAggregatesAlertsV2 is only exercised by aggregate_detections.
        aggregated = self.call_method(
            self.module.aggregate_detections, field="severity_name"
        )
        self.assert_no_error(aggregated, context="PostAggregatesAlertsV2 name validation")

    def test_aggregate_detections_terms_returns_labelled_buckets(self):
        """A terms aggregation returns buckets keyed on `label` with a count."""
        result = self.call_method(
            self.module.aggregate_detections,
            field="severity_name",
            type="terms",
            sort="_count|desc",
        )

        self.assert_no_error(result, context="aggregate_detections terms")
        self.assert_valid_list_response(
            result, min_length=1, context="aggregate_detections terms"
        )

        buckets = result[0].get("buckets")
        if not buckets:
            self.skip_with_warning(
                "No alerts to aggregate", "aggregate_detections terms buckets"
            )
            return

        # Buckets key on `label`, not `key` — asserted so a shape change is caught.
        assert "label" in buckets[0], f"expected `label` in bucket, got {buckets[0]}"
        assert "count" in buckets[0], f"expected `count` in bucket, got {buckets[0]}"

    def test_aggregate_detections_sort_pipe_format_is_accepted(self):
        """Aggregate sorts use the pipe form; the dot form is rejected upstream.

        Locks in the live behavior that `_count|desc` works here, unlike the
        `severity.desc` form accepted by search sorts.
        """
        result = self.call_method(
            self.module.aggregate_detections,
            field="severity_name",
            type="terms",
            sort="_count|desc",
        )
        self.assert_no_error(result, context="aggregate_detections sort=_count|desc")

        buckets = result[0].get("buckets") or []
        if len(buckets) > 1:
            counts = [b.get("count", 0) for b in buckets]
            assert counts == sorted(counts, reverse=True), (
                f"_count|desc did not order buckets by descending count: {counts}"
            )

    def test_aggregate_detections_cardinality_reports_value(self):
        """Single-value aggregations report their answer as `value`, not `count`."""
        result = self.call_method(
            self.module.aggregate_detections,
            field="device.hostname",
            type="cardinality",
        )

        self.assert_no_error(result, context="aggregate_detections cardinality")
        buckets = result[0].get("buckets") or []
        if not buckets:
            self.skip_with_warning(
                "No alerts to aggregate", "aggregate_detections cardinality"
            )
            return

        assert "value" in buckets[0], f"expected `value` in bucket, got {buckets[0]}"

    def test_aggregate_detections_date_histogram_buckets_by_interval(self):
        """A date_histogram over timestamp accepts a bare interval unit."""
        result = self.call_method(
            self.module.aggregate_detections,
            field="timestamp",
            type="date_histogram",
            interval="day",
            filter="timestamp:>'now-7d'",
        )

        self.assert_no_error(result, context="aggregate_detections date_histogram")
        self.assert_valid_list_response(
            result, min_length=1, context="aggregate_detections date_histogram"
        )

    def test_aggregate_detections_include_hidden_changes_totals(self):
        """include_hidden=False counts no more alerts than the default."""
        shown = self.call_method(
            self.module.aggregate_detections,
            field="severity_name",
            include_hidden=False,
        )
        everything = self.call_method(
            self.module.aggregate_detections,
            field="severity_name",
            include_hidden=True,
        )

        self.assert_no_error(shown, context="aggregate_detections include_hidden=False")
        self.assert_no_error(everything, context="aggregate_detections include_hidden=True")

        def total(result):
            return sum(b.get("count", 0) for b in (result[0].get("buckets") or []))

        # Hidden alerts are a superset, so excluding them cannot raise the count.
        assert total(shown) <= total(everything), (
            f"include_hidden=False counted more ({total(shown)}) "
            f"than include_hidden=True ({total(everything)})"
        )

    def test_aggregate_detections_missing_companion_is_caught_locally(self):
        """A type missing its companion argument is rejected before the API call.

        The live API answers these with an opaque 500, so the tool must catch them.
        """
        result = self.call_method(
            self.module.aggregate_detections,
            field="timestamp",
            type="date_histogram",
        )

        assert isinstance(result, dict) and "error" in result, (
            f"expected a local validation error, got {result!r}"
        )
        assert "interval" in result["error"], (
            f"error should name the missing argument, got {result['error']!r}"
        )

    def test_aggregate_detections_unsupported_field_returns_empty(self):
        """An unsupported aggregation field returns empty buckets, not an error.

        Documents the silent-ignore behavior that makes a bad field
        indistinguishable from a genuine zero count.
        """
        result = self.call_method(
            self.module.aggregate_detections,
            field="not_a_real_alert_field_xyz",
        )

        self.assert_no_error(result, context="aggregate_detections unsupported field")
        assert not (result[0].get("buckets") or []), (
            "expected no buckets for an unsupported aggregation field, "
            f"got {result[0].get('buckets')}"
        )

    def test_update_detections_status(self):
        """Test updating a detection status using PatchEntitiesAlertsV3.

        Validates the operation name, body format, and action_parameters shape.
        Performs a real round-trip: changes status to a different value, reads
        back to confirm the change, then restores the original status.

        Skips gracefully if Alerts:write scope is not available.
        """
        search_result = self.call_method(self.module.search_detections, limit=1)
        if not search_result or isinstance(search_result, dict):
            self.skip_with_warning(
                "No detections available to test update_detections",
                context="test_update_detections_status",
            )
            return

        detection_id = self.get_first_id(search_result, id_field="composite_id")
        if not detection_id:
            self.skip_with_warning(
                "Could not extract composite_id from search results",
                context="test_update_detections_status",
            )
            return

        original_status = search_result[0].get("status", "new")
        new_status = "in_progress" if original_status != "in_progress" else "new"

        # Attempt the write — skip gracefully if scope is missing
        result = self.call_method(
            self.module.update_detections,
            ids=[detection_id],
            status=new_status,
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

        # Skip on 401/403 — the caller lacks Alerts:write
        if isinstance(result, dict) and "error" in result:
            details = result.get("details", {})
            status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
            if status_code in (401, 403):
                self.skip_with_warning(
                    f"Insufficient scope for update_detections (Alerts:write required): {result}",
                    context="test_update_detections_status",
                )
                return
            pytest.fail(f"update_detections failed unexpectedly: {result}")

        # Success — read back and confirm the status changed; restore always runs
        updated = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        try:
            self.assert_no_error(updated, context="read-back after update_detections")
            assert updated, f"get_detection_details returned empty after successful status update for {detection_id}"
            assert updated[0].get("status") == new_status, (
                f"Detection status did not change: expected {new_status!r}, "
                f"got {updated[0].get('status')!r}"
            )
        finally:
            # Restore original status. A hint-wrapped dict is an acceptable (non-error)
            # outcome here if the original status was 'closed'.
            restore_result = self.call_method(
                self.module.update_detections,
                ids=[detection_id],
                status=original_status,
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
            self.assert_no_error(restore_result, context="restore original_status")

    def test_update_detections_tags(self):
        """Test adding and removing a resolution tag via PatchEntitiesAlertsV3.

        Validates the add_tag and remove_tag action_parameters against a real
        detection: adds true_positive and confirms it in the read-back, then
        removes it via the tool's own remove_tags path and confirms it is gone.

        Skips gracefully if Alerts:write scope is not available.
        """
        search_result = self.call_method(self.module.search_detections, limit=1)
        if not search_result or isinstance(search_result, dict):
            self.skip_with_warning(
                "No detections available to test update_detections tags",
                context="test_update_detections_tags",
            )
            return

        detection_id = self.get_first_id(search_result, id_field="composite_id")
        if not detection_id:
            self.skip_with_warning(
                "Could not extract composite_id from search results",
                context="test_update_detections_tags",
            )
            return

        # Add the true_positive resolution tag
        result = self.call_method(
            self.module.update_detections,
            ids=[detection_id],
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

        # Skip on 401/403 — the caller lacks Alerts:write
        if isinstance(result, dict) and "error" in result:
            details = result.get("details", {})
            status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
            if status_code in (401, 403):
                self.skip_with_warning(
                    f"Insufficient scope for update_detections tags (Alerts:write required): {result}",
                    context="test_update_detections_tags",
                )
                return
            pytest.fail(f"update_detections add_tags failed unexpectedly: {result}")

        # Read back and confirm tag is present; cleanup always runs via try/finally
        updated = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        try:
            self.assert_no_error(updated, context="read-back after update_detections add_tags")
            assert updated, f"get_detection_details returned empty after successful add_tags for {detection_id}"
            tags = updated[0].get("tags") or []
            assert "true_positive" in tags, (
                f"Expected 'true_positive' in tags after add_tags, got: {tags}"
            )
        finally:
            # Remove the tag via the tool's own remove_tags path (now live-validated)
            remove_result = self.call_method(
                self.module.update_detections,
                ids=[detection_id],
                status=None,
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=None,
                remove_tags=["true_positive"],
                remove_tags_by_prefix=None,
            )
            self.assert_no_error(remove_result, context="update_detections remove_tags")

        # Confirm the tag is gone after removal
        after_remove = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        self.assert_no_error(after_remove, context="read-back after update_detections remove_tags")
        assert after_remove, f"get_detection_details returned empty after remove_tags for {detection_id}"
        remaining_tags = after_remove[0].get("tags") or []
        assert "true_positive" not in remaining_tags, (
            f"Expected 'true_positive' to be removed, but still present: {remaining_tags}"
        )

        # Round-trip remove_tags_by_prefix: add a prefixed tag, then remove by prefix
        prefix_tag = "fc_mcp_probe/scratch"
        prefix = "fc_mcp_probe/"
        add_prefixed = self.call_method(
            self.module.update_detections,
            ids=[detection_id],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=[prefix_tag],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )
        self.assert_no_error(add_prefixed, context="update_detections add prefixed tag")
        try:
            with_prefix = self.call_method(
                self.module.get_detection_details,
                ids=[detection_id],
            )
            self.assert_no_error(with_prefix, context="read-back after adding prefixed tag")
            assert with_prefix, f"get_detection_details returned empty after adding prefixed tag for {detection_id}"
            assert prefix_tag in (with_prefix[0].get("tags") or []), (
                f"Expected {prefix_tag!r} in tags, got: {with_prefix[0].get('tags')}"
            )
        finally:
            remove_by_prefix = self.call_method(
                self.module.update_detections,
                ids=[detection_id],
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
            self.assert_no_error(remove_by_prefix, context="update_detections remove_tags_by_prefix")

        # Confirm the prefixed tag is gone after prefix removal
        after_prefix_remove = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        self.assert_no_error(after_prefix_remove, context="read-back after remove_tags_by_prefix")
        assert after_prefix_remove, f"get_detection_details returned empty after remove_tags_by_prefix for {detection_id}"
        assert prefix_tag not in (after_prefix_remove[0].get("tags") or []), (
            f"Expected {prefix_tag!r} to be removed by prefix, but still present: "
            f"{after_prefix_remove[0].get('tags')}"
        )

    def test_update_detections_show_in_ui(self):
        """Test toggling show_in_ui validates that string encoding reaches the API correctly.

        show_in_ui is a live-validated parameter where sending a Python bool returns 400;
        only the string 'true'/'false' is accepted. This test catches encoding regressions
        that unit tests cannot catch.

        Skips gracefully if Alerts:write scope is not available.
        """
        search_result = self.call_method(self.module.search_detections, limit=1)
        if not search_result or isinstance(search_result, dict):
            self.skip_with_warning(
                "No detections available to test update_detections show_in_ui",
                context="test_update_detections_show_in_ui",
            )
            return

        detection_id = self.get_first_id(search_result, id_field="composite_id")
        if not detection_id:
            self.skip_with_warning(
                "Could not extract composite_id from search results",
                context="test_update_detections_show_in_ui",
            )
            return

        original_show_in_ui = bool(search_result[0].get("show_in_ui", True))
        new_show_in_ui = not original_show_in_ui

        result = self.call_method(
            self.module.update_detections,
            ids=[detection_id],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=new_show_in_ui,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        # Skip on 401/403 — the caller lacks Alerts:write
        if isinstance(result, dict) and "error" in result:
            details = result.get("details", {})
            status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
            if status_code in (401, 403):
                self.skip_with_warning(
                    f"Insufficient scope for update_detections show_in_ui (Alerts:write required): {result}",
                    context="test_update_detections_show_in_ui",
                )
                return
            pytest.fail(f"update_detections show_in_ui failed unexpectedly: {result}")

        # Read back and confirm show_in_ui changed; restore always runs
        updated = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        try:
            self.assert_no_error(updated, context="read-back after update_detections show_in_ui")
            assert updated, f"get_detection_details returned empty after show_in_ui update for {detection_id}"
            assert updated[0].get("show_in_ui") == new_show_in_ui, (
                f"show_in_ui did not change: expected {new_show_in_ui!r}, "
                f"got {updated[0].get('show_in_ui')!r}"
            )
        finally:
            self.call_method(
                self.module.update_detections,
                ids=[detection_id],
                status=None,
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=original_show_in_ui,
                add_tags=None,
                remove_tags=None,
                remove_tags_by_prefix=None,
            )
