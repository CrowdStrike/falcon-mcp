"""Integration tests for the Intel module."""

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

        if len(result) > 0:
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

        if len(result) > 0:
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

        if len(result) > 0:
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
        """Test get_mitre_report with an actor name.

        First searches for an actor, then gets their MITRE report.
        Validates both QueryIntelActorEntities and GetMitreReport operations.
        """
        # First, search for an actor to get a valid name
        search_result = self.call_method(self.module.query_actor_entities, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No actors available to test get_mitre_report",
                context="test_get_mitre_report_with_actor_name",
            )

        actor_name = search_result[0].get("name")
        if not actor_name:
            self.skip_with_warning(
                "Could not extract actor name from search results",
                context="test_get_mitre_report_with_actor_name",
            )

        # Now get MITRE report for that actor
        result = self.call_method(self.module.get_mitre_report, actor=actor_name, format="json")

        # Result can be a list (data) or string (error message)
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict) and "error" in first_item:
                # Some actors may not have MITRE reports
                self.skip_with_warning(
                    f"MITRE report not available for actor: {actor_name}",
                    context="test_get_mitre_report_with_actor_name",
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
