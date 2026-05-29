"""Integration tests for the Data Protection module."""

import pytest

from falcon_mcp.modules.data_protection import DataProtectionModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDataProtectionIntegration(BaseIntegrationTest):
    """Integration tests for Data Protection module with real API calls.

    Validates:
    - Correct FalconPy operation names (queries_classification_get_v2,
      entities_classification_get_v2, queries_policy_get_v2, entities_policy_get_v2,
      queries_content_pattern_get_v2, entities_content_pattern_get)
    - Two-step search pattern returns full details, not just IDs
    - GET with params usage for get_by_ids (use_params=True)
    - platform_name parameter handling for policies
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Data Protection module with a real client."""
        self.module = DataProtectionModule(falcon_client)

    # --- Classifications ---

    def test_search_classifications(self):
        """Test that search_data_protection_classifications returns results."""
        result = self.call_method(self.module.search_data_protection_classifications, limit=5)

        self.assert_no_error(result, context="search_data_protection_classifications")
        self.assert_valid_list_response(result, min_length=0, context="search_data_protection_classifications")

    def test_search_classifications_returns_full_details(self):
        """Test that classifications include full entity details."""
        result = self.call_method(self.module.search_data_protection_classifications, limit=2)

        if not result or isinstance(result, dict):
            self.skip_with_warning("No classifications found", "classifications details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "cid", "created_at", "classification_properties"],
            context="search_data_protection_classifications full details",
        )

    def test_search_classifications_with_filter(self):
        """Test classification search with FQL filter."""
        result = self.call_method(
            self.module.search_data_protection_classifications,
            filter="created_at:>'2024-01-01'",
            limit=3,
        )

        self.assert_no_error(result, context="search_data_protection_classifications with filter")

    def test_search_classifications_with_sort(self):
        """Test classification search with sort parameter."""
        result = self.call_method(
            self.module.search_data_protection_classifications,
            sort="name.asc",
            limit=3,
        )

        self.assert_no_error(result, context="search_data_protection_classifications with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search_data_protection_classifications with sort"
        )

    # --- Policies ---

    def test_search_policies_windows(self):
        """Test that search_data_protection_policies works with platform_name='win'."""
        result = self.call_method(
            self.module.search_data_protection_policies,
            platform_name="win",
            limit=5,
        )

        self.assert_no_error(result, context="search_data_protection_policies win")
        self.assert_valid_list_response(result, min_length=0, context="search_data_protection_policies win")

    def test_search_policies_mac(self):
        """Test that search_data_protection_policies works with platform_name='mac'."""
        result = self.call_method(
            self.module.search_data_protection_policies,
            platform_name="mac",
            limit=5,
        )

        self.assert_no_error(result, context="search_data_protection_policies mac")
        self.assert_valid_list_response(result, min_length=0, context="search_data_protection_policies mac")

    def test_search_policies_returns_full_details(self):
        """Test that policies include full entity details."""
        result = self.call_method(
            self.module.search_data_protection_policies,
            platform_name="win",
            limit=2,
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No win policies found", "policies details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "platform_name", "is_enabled", "precedence"],
            context="search_data_protection_policies full details",
        )

    def test_search_policies_with_filter(self):
        """Test policy search with FQL filter."""
        result = self.call_method(
            self.module.search_data_protection_policies,
            platform_name="win",
            filter="is_enabled:true",
            limit=3,
        )

        self.assert_no_error(result, context="search_data_protection_policies with filter")

    # --- Content Patterns ---

    def test_search_content_patterns(self):
        """Test that search_data_protection_content_patterns returns results."""
        result = self.call_method(self.module.search_data_protection_content_patterns, limit=5)

        self.assert_no_error(result, context="search_data_protection_content_patterns")
        self.assert_valid_list_response(
            result, min_length=0, context="search_data_protection_content_patterns"
        )

    def test_search_content_patterns_returns_full_details(self):
        """Test that content patterns include full entity details."""
        result = self.call_method(self.module.search_data_protection_content_patterns, limit=2)

        if not result or isinstance(result, dict):
            self.skip_with_warning("No content patterns found", "content patterns details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "type", "category", "region"],
            context="search_data_protection_content_patterns full details",
        )

    def test_search_content_patterns_with_filter(self):
        """Test content pattern search with FQL filter."""
        result = self.call_method(
            self.module.search_data_protection_content_patterns,
            filter="deleted:false",
            limit=3,
        )

        self.assert_no_error(result, context="search_data_protection_content_patterns with filter")

    def test_search_content_patterns_by_type(self):
        """Test filtering content patterns by type."""
        result = self.call_method(
            self.module.search_data_protection_content_patterns,
            filter="type:'predefined'",
            limit=3,
        )

        self.assert_no_error(result, context="search_data_protection_content_patterns by type")
        self.assert_valid_list_response(
            result, min_length=0, context="search_data_protection_content_patterns by type"
        )

    # --- Operation Name Validation ---

    def test_operation_names_are_correct(self):
        """Validate that all 6 FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        This is the primary defense against the entities_content_pattern_get
        no-_v2 gotcha.
        """
        # queries_classification_get_v2 + entities_classification_get_v2
        result = self.call_method(self.module.search_data_protection_classifications, limit=1)
        self.assert_no_error(result, context="classification operation names")

        # queries_policy_get_v2 + entities_policy_get_v2
        result = self.call_method(
            self.module.search_data_protection_policies, platform_name="win", limit=1
        )
        self.assert_no_error(result, context="policy operation names")

        # queries_content_pattern_get_v2 + entities_content_pattern_get (no _v2!)
        result = self.call_method(self.module.search_data_protection_content_patterns, limit=1)
        self.assert_no_error(result, context="content_pattern operation names")
