"""Integration tests for the Data Security module."""

import pytest

from falcon_mcp.modules.data_security import DataSecurityModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDataSecurityIntegration(BaseIntegrationTest):
    """Integration tests for Data Security module with real API calls.

    Validates:
    - Correct FalconPy operation names dispatched by the generic
      search_data_security_entities / get_data_security_entities tools
      (e.g. queries_classification_get_v2, entities_classification_get_v2,
      queries_content_pattern_get_v2, entities_content_pattern_get)
    - Two-step search pattern returns full details, not just IDs
    - GET with params usage for get_by_ids (use_params=True)
    - platform_name parameter handling for policies
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Data Security module with a real client."""
        self.module = DataSecurityModule(falcon_client)

    # --- Classifications ---

    def test_search_classifications(self):
        """Test that searching classifications returns results."""
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="classification", limit=5
        )

        self.assert_no_error(result, context="search classification")
        self.assert_valid_list_response(result, min_length=0, context="search classification")

    def test_search_classifications_returns_full_details(self):
        """Test that classifications include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities, entity_type="classification", limit=2
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No classifications found", "classifications details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "cid", "created_at", "classification_properties"],
            context="search classification full details",
        )

    def test_search_classifications_with_filter(self):
        """Test classification search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="classification",
            filter="created_at:>'2024-01-01'",
            limit=3,
        )

        self.assert_no_error(result, context="search classification with filter")

    def test_search_classifications_with_sort(self):
        """Test classification search with sort parameter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="classification",
            sort="name.asc",
            limit=3,
        )

        self.assert_no_error(result, context="search classification with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search classification with sort"
        )

    def test_policy_precedence_sorts_ascending_but_not_descending(self):
        """Backs the `sort` description's precedence caveat with a live check.

        `precedence.asc` orders correctly (4 of 4 trials, 20 of 20 distinct values) while
        `precedence.desc` does not (0 of 4). Both directions are pinned together so the
        asymmetry is what fails if either half changes: if desc starts working, list
        `precedence.desc` in the policy FQL guide's sort fields; if asc stops, the guide is
        wrong the other way.

        Not a `_reorder_by_ids` concern — this endpoint's get step preserves the order it is
        handed (0 of 4 trials scrambled), so the defect is in the API's own sort.
        """

        def precedences(direction: str) -> list:
            result = self.call_method(
                self.module.search_data_security_entities,
                entity_type="policy",
                platform_name="win",
                sort=f"precedence.{direction}",
                limit=20,
            )
            self.assert_no_error(result, context=f"dp policies precedence.{direction}")
            return [p["precedence"] for p in self._unwrap_results(result)]

        ascending = precedences("asc")
        descending = precedences("desc")

        assert (
            len(ascending) > 1
        ), f"Need 2+ win data-security policies to compare order, got {len(ascending)}"
        assert ascending == sorted(ascending), (
            f"precedence.asc is no longer ascending, so the `sort` description's claim that "
            f"ascending works is wrong: {ascending}"
        )
        assert descending != sorted(descending, reverse=True), (
            "precedence.desc now returns correctly ordered results — the known defect is "
            "fixed. Add precedence.desc to the policy FQL guide's sort fields. "
            f"Got: {descending}"
        )

    def test_content_pattern_name_sort_orders_neither_direction(self):
        """Backs the `sort` description's name caveat with a live check.

        `name` fails to order results in either direction (0 of 4 trials each way, with 20
        of 20 distinct names, so this is an ordering defect rather than a tie-break). If
        either direction starts working, add `name` back to the content_pattern FQL guide's
        sort fields.

        Not a `_reorder_by_ids` concern — this endpoint's get step preserves the order it is
        handed (0 of 4 trials scrambled).
        """
        for direction in ("asc", "desc"):
            result = self.call_method(
                self.module.search_data_security_entities,
                entity_type="content_pattern",
                sort=f"name.{direction}",
                limit=20,
            )
            self.assert_no_error(result, context=f"dp content patterns name.{direction}")
            names = [p["name"] for p in self._unwrap_results(result)]

            assert len(names) > 1, f"Need 2+ content patterns to compare order, got {len(names)}"
            assert names != sorted(names, reverse=(direction == "desc")), (
                f"name.{direction} now orders results correctly — the known defect is fixed. "
                "Add name to the content_pattern FQL guide's sort fields. "
                f"Got: {names}"
            )

    # --- Policies ---

    def test_search_policies_windows(self):
        """Test that policy search works with platform_name='win'."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            limit=5,
        )

        self.assert_no_error(result, context="search policy win")
        self.assert_valid_list_response(result, min_length=0, context="search policy win")

    def test_search_policies_mac(self):
        """Test that policy search works with platform_name='mac'."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="mac",
            limit=5,
        )

        self.assert_no_error(result, context="search policy mac")
        self.assert_valid_list_response(result, min_length=0, context="search policy mac")

    def test_search_policies_returns_full_details(self):
        """Test that policies include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities,
                entity_type="policy",
                platform_name="win",
                limit=2,
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No win policies found", "policies details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "platform_name", "is_enabled", "precedence"],
            context="search policy full details",
        )

    def test_search_policies_with_filter(self):
        """Test policy search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            filter="is_enabled:true",
            limit=3,
        )

        self.assert_no_error(result, context="search policy with filter")

    # --- Content Patterns ---

    def test_search_content_patterns(self):
        """Test that content pattern search returns results."""
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="content_pattern", limit=5
        )

        self.assert_no_error(result, context="search content_pattern")
        self.assert_valid_list_response(result, min_length=0, context="search content_pattern")

    def test_search_content_patterns_returns_full_details(self):
        """Test that content patterns include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities, entity_type="content_pattern", limit=2
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No content patterns found", "content patterns details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "type", "category", "region"],
            context="search content_pattern full details",
        )

    def test_search_content_patterns_with_filter(self):
        """Test content pattern search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="content_pattern",
            filter="deleted:false",
            limit=3,
        )

        self.assert_no_error(result, context="search content_pattern with filter")

    def test_search_content_patterns_by_type(self):
        """Test filtering content patterns by type."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="content_pattern",
            filter="type:'predefined'",
            limit=3,
        )

        self.assert_no_error(result, context="search content_pattern by type")
        self.assert_valid_list_response(
            result, min_length=0, context="search content_pattern by type"
        )

    # --- Operation Name Validation ---

    def test_operation_names_are_correct(self):
        """Validate that core read (query + get) FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        This is the primary defense against gotchas like the
        entities_content_pattern_get no-_v2 naming.
        """
        # queries_classification_get_v2 + entities_classification_get_v2
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="classification", limit=1
        )
        self.assert_no_error(result, context="classification operation names")

        # queries_policy_get_v2 + entities_policy_get_v2
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            limit=1,
        )
        self.assert_no_error(result, context="policy operation names")

        # queries_content_pattern_get_v2 + entities_content_pattern_get (no _v2!)
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="content_pattern", limit=1
        )
        self.assert_no_error(result, context="content_pattern operation names")

    def test_additional_search_operation_names_are_correct(self):
        """Validate the query + get operation names for the remaining entity types."""
        entity_types = [
            "cloud_application",
            "enterprise_account",
            "web_location",
            "local_application",
            "local_application_group",
            "sensitivity_label",
            "file_type",
        ]
        for entity_type in entity_types:
            result = self.call_method(
                self.module.search_data_security_entities, entity_type=entity_type, limit=1
            )
            self.assert_no_error(result, context=f"{entity_type} operation names")
            self.assert_valid_list_response(result, min_length=0, context=f"{entity_type} response")
