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
            verdict=None,
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
            # Restore original status
            self.call_method(
                self.module.update_detections,
                ids=[detection_id],
                status=original_status,
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                verdict=None,
            )

    def test_update_detections_verdict(self):
        """Test setting a verdict tag (true_positive) via PatchEntitiesAlertsV3.

        Validates that add_tag action_parameter is accepted and the tag appears
        in the read-back entity. Always cleans up the tag afterward.

        Skips gracefully if Alerts:write scope is not available.
        """
        search_result = self.call_method(self.module.search_detections, limit=1)
        if not search_result or isinstance(search_result, dict):
            self.skip_with_warning(
                "No detections available to test update_detections verdict",
                context="test_update_detections_verdict",
            )
            return

        detection_id = self.get_first_id(search_result, id_field="composite_id")
        if not detection_id:
            self.skip_with_warning(
                "Could not extract composite_id from search results",
                context="test_update_detections_verdict",
            )
            return

        # Set verdict to true_positive
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
            verdict="true_positive",
        )

        # Skip on 401/403 — the caller lacks Alerts:write
        if isinstance(result, dict) and "error" in result:
            details = result.get("details", {})
            status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
            if status_code in (401, 403):
                self.skip_with_warning(
                    f"Insufficient scope for update_detections verdict (Alerts:write required): {result}",
                    context="test_update_detections_verdict",
                )
                return
            pytest.fail(f"update_detections verdict failed unexpectedly: {result}")

        # Read back and confirm tag is present; cleanup always runs via try/finally
        updated = self.call_method(
            self.module.get_detection_details,
            ids=[detection_id],
        )
        try:
            self.assert_no_error(updated, context="read-back after update_detections verdict")
            assert updated, f"get_detection_details returned empty after successful verdict update for {detection_id}"
            tags = updated[0].get("tags") or []
            assert "true_positive" in tags, (
                f"Expected 'true_positive' in tags after setting verdict, got: {tags}"
            )
        finally:
            # Clean up — remove the tag via direct API call (remove_tag is not exposed on the tool)
            self.module.client.command(
                "PatchEntitiesAlertsV3",
                body={
                    "composite_ids": [detection_id],
                    "action_parameters": [{"name": "remove_tag", "value": "true_positive"}],
                },
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
            verdict=None,
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
                verdict=None,
            )
