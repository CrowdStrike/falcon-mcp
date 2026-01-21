"""Integration tests for the Incidents module."""

import pytest

from falcon_mcp.modules.incidents import IncidentsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIncidentsIntegration(BaseIntegrationTest):
    """Integration tests for Incidents module with real API calls.

    Validates:
    - Correct FalconPy operation names (QueryIncidents, GetIncidents, CrowdScore, etc.)
    - Two-step search pattern returns full details, not just IDs
    - POST body usage for get_by_ids
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the incidents module with a real client."""
        self.module = IncidentsModule(falcon_client)

    def test_show_crowd_score_returns_scores(self):
        """Test that show_crowd_score returns CrowdScore data."""
        result = self.call_method(self.module.show_crowd_score, limit=5)

        self.assert_no_error(result, context="show_crowd_score")
        assert isinstance(result, dict), "Expected dict response from show_crowd_score"

        # Verify score structure
        assert "average_score" in result, "Expected average_score in response"
        assert "scores" in result, "Expected scores in response"

    def test_search_incidents_returns_details(self):
        """Test that search_incidents returns full incident details, not just IDs.

        This validates the two-step search pattern:
        1. QueryIncidents returns incident IDs
        2. GetIncidents returns full details
        """
        result = self.call_method(self.module.search_incidents, limit=5)

        self.assert_no_error(result, context="search_incidents")
        self.assert_valid_list_response(result, min_length=0, context="search_incidents")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["incident_id"],
                context="search_incidents",
            )

    def test_search_incidents_with_filter(self):
        """Test search_incidents with FQL filter."""
        result = self.call_method(
            self.module.search_incidents,
            filter="state:'open'",
            limit=3,
        )

        self.assert_no_error(result, context="search_incidents with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_incidents with filter")

    def test_get_incident_details_with_valid_id(self):
        """Test get_incident_details with a valid incident ID."""
        # First, search for an incident to get a valid ID
        search_result = self.call_method(self.module.search_incidents, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No incidents available to test get_incident_details",
                context="test_get_incident_details_with_valid_id",
            )

        incident_id = self.get_first_id(search_result, id_field="incident_id")
        if not incident_id:
            self.skip_with_warning(
                "Could not extract incident ID from search results",
                context="test_get_incident_details_with_valid_id",
            )

        # Now get details for that incident
        result = self.call_method(self.module.get_incident_details, ids=[incident_id])

        self.assert_no_error(result, context="get_incident_details")
        self.assert_valid_list_response(result, min_length=1, context="get_incident_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["incident_id"],
            context="get_incident_details",
        )

    def test_search_behaviors_returns_details(self):
        """Test that search_behaviors returns full behavior details, not just IDs.

        This validates the two-step search pattern:
        1. QueryBehaviors returns behavior IDs
        2. GetBehaviors returns full details
        """
        result = self.call_method(self.module.search_behaviors, limit=5)

        self.assert_no_error(result, context="search_behaviors")
        self.assert_valid_list_response(result, min_length=0, context="search_behaviors")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["behavior_id"],
                context="search_behaviors",
            )

    def test_get_behavior_details_with_valid_id(self):
        """Test get_behavior_details with a valid behavior ID."""
        # First, search for a behavior to get a valid ID
        search_result = self.call_method(self.module.search_behaviors, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No behaviors available to test get_behavior_details",
                context="test_get_behavior_details_with_valid_id",
            )

        behavior_id = self.get_first_id(search_result, id_field="behavior_id")
        if not behavior_id:
            self.skip_with_warning(
                "Could not extract behavior ID from search results",
                context="test_get_behavior_details_with_valid_id",
            )

        # Now get details for that behavior
        result = self.call_method(self.module.get_behavior_details, ids=[behavior_id])

        self.assert_no_error(result, context="get_behavior_details")
        self.assert_valid_list_response(result, min_length=1, context="get_behavior_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["behavior_id"],
            context="get_behavior_details",
        )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test multiple operations to validate names
        crowd_score = self.call_method(self.module.show_crowd_score, limit=1)
        self.assert_no_error(crowd_score, context="CrowdScore operation name")

        incidents = self.call_method(self.module.search_incidents, limit=1)
        self.assert_no_error(incidents, context="QueryIncidents operation name")
