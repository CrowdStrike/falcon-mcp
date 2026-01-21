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
