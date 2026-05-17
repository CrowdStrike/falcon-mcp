"""Integration tests for the Cases module."""

import time

import pytest

from falcon_mcp.modules.cases import CasesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCasesIntegration(BaseIntegrationTest):
    """Integration tests for Cases module with real API calls.

    Validates:
    - Correct FalconPy operation names (queries_cases_get_v1, entities_cases_post_v2, etc.)
    - Two-step search pattern returns full details, not just IDs
    - POST body usage for get_cases
    - Create (PUT) and update (PATCH) body formats
    - Evidence attachment body format (alert objects, not strings)
    - Tag management asymmetry (POST body add vs DELETE query params remove)
    - Template listing with GET query params (use_params=True)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the cases module with a real client."""
        self.module = CasesModule(falcon_client)

    # -------------------------------------------------------------------------
    # Operation Name Validation
    # -------------------------------------------------------------------------

    def test_operation_names_search(self):
        """Validate queries_cases_get_v1 and entities_cases_post_v2 are correct."""
        result = self.call_method(self.module.search_cases, limit=1)
        self.assert_no_error(result, context="search operation names")

    def test_operation_names_templates(self):
        """Validate queries_templates_get_v1 and entities_templates_get_v1 are correct."""
        result = self.call_method(self.module.list_case_templates, limit=1)
        self.assert_no_error(result, context="template operation names")

    # -------------------------------------------------------------------------
    # Search Tests
    # -------------------------------------------------------------------------

    def test_search_cases_returns_details(self):
        """Test that search_cases returns full case details, not just IDs.

        Validates the two-step search pattern:
        1. queries_cases_get_v1 returns case IDs
        2. entities_cases_post_v2 returns full details
        """
        result = self.call_method(self.module.search_cases, limit=5)

        self.assert_no_error(result, context="search_cases")
        self.assert_valid_list_response(result, min_length=0, context="search_cases")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "status", "severity"],
                context="search_cases full details",
            )

    def test_search_cases_with_filter(self):
        """Test search_cases with FQL filter."""
        result = self.call_method(
            self.module.search_cases,
            filter="status:'new'",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with filter"
        )

    def test_search_cases_with_sort(self):
        """Test search_cases with sort parameter."""
        result = self.call_method(
            self.module.search_cases,
            sort="created_timestamp.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with sort"
        )

    def test_search_cases_with_q(self):
        """Test search_cases with free-text search."""
        result = self.call_method(
            self.module.search_cases,
            q="test",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with q")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with q"
        )

    # -------------------------------------------------------------------------
    # Get Tests
    # -------------------------------------------------------------------------

    def test_get_cases_with_valid_id(self):
        """Test get_cases with a valid case ID from search."""
        search_result = self.call_method(self.module.search_cases, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No cases available to test get_cases",
                context="test_get_cases_with_valid_id",
            )

        case_id = self.get_first_id(search_result, id_field="id")
        if not case_id:
            self.skip_with_warning(
                "Could not extract case ID from search results",
                context="test_get_cases_with_valid_id",
            )

        result = self.call_method(self.module.get_cases, ids=[case_id])

        self.assert_no_error(result, context="get_cases")
        self.assert_valid_list_response(result, min_length=1, context="get_cases")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "status", "severity"],
            context="get_cases",
        )

    # -------------------------------------------------------------------------
    # Create / Update / Tag Round-trip
    # -------------------------------------------------------------------------

    def test_create_update_tag_roundtrip(self):
        """Full lifecycle: create a case, update it, add/remove tags, verify.

        Creates a unique test case, updates fields, manages tags, then
        verifies the final state. The case is left in 'closed' state as cleanup.
        """
        unique_name = f"falcon-mcp-test-{int(time.time())}"

        # Step 1: Create
        create_result = self.call_method(
            self.module.create_case,
            name=unique_name,
            severity=25,
            description="Integration test case - safe to delete",
            status="new",
        )

        self.assert_no_error(create_result, context="create_case")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create_case"
        )

        case = create_result[0]
        assert isinstance(case, dict), f"Expected dict, got {type(case)}"
        assert "id" in case, f"Missing 'id' in created case. Fields: {list(case.keys())}"

        case_id = case["id"]
        case_version = case.get("version", 1)

        # Step 2: Update (change status and severity)
        update_result = self.call_method(
            self.module.update_case,
            id=case_id,
            status="in_progress",
            severity=50,
            expected_version=case_version,
        )

        self.assert_no_error(update_result, context="update_case")
        self.assert_valid_list_response(
            update_result, min_length=1, context="update_case"
        )

        updated_case = update_result[0]
        assert updated_case.get("status") == "in_progress", (
            f"Expected status 'in_progress', got '{updated_case.get('status')}'"
        )

        # Step 3: Add tags
        tag_add_result = self.call_method(
            self.module.manage_case_tags,
            id=case_id,
            action="add",
            tags=["mcp-test", "integration"],
        )

        self.assert_no_error(tag_add_result, context="add tags")

        # Step 4: Remove one tag
        tag_remove_result = self.call_method(
            self.module.manage_case_tags,
            id=case_id,
            action="remove",
            tags=["integration"],
        )

        self.assert_no_error(tag_remove_result, context="remove tags")

        # Step 5: Verify final state
        get_result = self.call_method(self.module.get_cases, ids=[case_id])

        self.assert_no_error(get_result, context="verify final state")
        self.assert_valid_list_response(
            get_result, min_length=1, context="verify final state"
        )

        final_case = get_result[0]
        assert final_case.get("status") == "in_progress"
        assert "mcp-test" in (final_case.get("tags") or [])
        assert "integration" not in (final_case.get("tags") or [])

        # Step 6: Close the case (cleanup)
        updated_version = final_case.get("version", case_version + 2)
        close_result = self.call_method(
            self.module.update_case,
            id=case_id,
            status="closed",
            expected_version=updated_version,
        )
        self.assert_no_error(close_result, context="close case cleanup")

    # -------------------------------------------------------------------------
    # Template Tests
    # -------------------------------------------------------------------------

    def test_list_case_templates(self):
        """Test that list_case_templates returns template details."""
        result = self.call_method(self.module.list_case_templates, limit=5)

        self.assert_no_error(result, context="list_case_templates")
        self.assert_valid_list_response(
            result, min_length=0, context="list_case_templates"
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="list_case_templates details",
            )

    # -------------------------------------------------------------------------
    # FQL Filter Validation
    # -------------------------------------------------------------------------

    def test_fql_filter_by_severity(self):
        """Test FQL filter by severity range."""
        result = self.call_method(
            self.module.search_cases,
            filter="severity:>50",
            limit=3,
        )

        self.assert_no_error(result, context="FQL severity filter")

    def test_fql_filter_combined(self):
        """Test FQL combined filter."""
        result = self.call_method(
            self.module.search_cases,
            filter="status:'new'+severity:>50",
            limit=3,
        )

        self.assert_no_error(result, context="FQL combined filter")
