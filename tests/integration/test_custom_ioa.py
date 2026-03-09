"""Integration tests for the Custom IOA module."""

import warnings

import pytest

from falcon_mcp.modules.custom_ioa import CustomIOAModule
from tests.integration.utils.base_integration_test import (
    BaseIntegrationTest,
    resolve_field_defaults,
)


@pytest.mark.integration
class TestCustomIOAIntegration(BaseIntegrationTest):
    """Integration tests for Custom IOA module with real API calls.

    Validates:
    - Correct FalconPy operation names (query_rule_groups_full, query_platformsMixin0,
      get_platformsMixin0, query_rule_types, get_rule_types, create_rule_groupMixin0,
      delete_rule_groupsMixin0)
    - Two-step search pattern returns full details, not just IDs
    - Full CRUD lifecycle for rule groups
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Custom IOA module with a real client."""
        self.module = CustomIOAModule(falcon_client)

    @pytest.fixture(autouse=True, scope="class")
    def create_test_rule_group(self, falcon_client):
        """Create a test rule group for the class and clean up after all tests.

        Creates a linux rule group with a clearly identifiable name for
        easy identification and filter-based searching.
        """
        module = CustomIOAModule(falcon_client)

        # Create test rule group
        create_kwargs = resolve_field_defaults(module.create_ioa_rule_group, {
            "name": "falcon-mcp-integration-test",
            "platform": "linux",
            "description": "Integration test rule group - safe to delete",
            "comment": "Created by falcon-mcp integration tests",
        })
        result = module.create_ioa_rule_group(**create_kwargs)

        # Validate creation succeeded
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                pytest.skip(
                    f"Cannot create test rule group (check Custom IOA Rules:write scope): {first}"
                )
            if isinstance(first, dict) and "id" in first:
                self.__class__._test_rule_group = first
                self.__class__._test_rule_group_id = first["id"]
            else:
                pytest.skip(f"Unexpected create response shape: {result}")
        else:
            pytest.skip(f"Unexpected create response: {result}")

        yield

        # Teardown: delete the test rule group
        try:
            delete_kwargs = resolve_field_defaults(module.delete_ioa_rule_groups, {
                "ids": [self.__class__._test_rule_group_id],
                "comment": "Integration test cleanup",
            })
            module.delete_ioa_rule_groups(**delete_kwargs)
        except Exception as e:
            warnings.warn(
                f"Failed to clean up test rule group {self.__class__._test_rule_group_id}: {e}",
                stacklevel=2,
            )

    # ── Read-only tests ──────────────────────────────────────────────

    def test_search_ioa_rule_groups(self):
        """Test basic search returns results without errors."""
        result = self.call_method(self.module.search_ioa_rule_groups, limit=5)
        self.assert_no_error(result, context="search_ioa_rule_groups")
        self.assert_valid_list_response(result, min_length=0, context="search_ioa_rule_groups")

    def test_search_returns_full_details(self):
        """Test that search returns full rule group details, not just IDs.

        Validates the two-step search pattern returns objects with
        expected fields including nested rules.
        """
        result = self.call_method(self.module.search_ioa_rule_groups, limit=5)

        self.assert_no_error(result, context="search_returns_full_details")
        self.assert_valid_list_response(result, min_length=0, context="search_returns_full_details")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "platform", "enabled", "rules"],
                context="search_returns_full_details",
            )

    def test_search_with_filter(self):
        """Test search with FQL filter targeting the test rule group."""
        result = self.call_method(
            self.module.search_ioa_rule_groups,
            filter="name:'falcon-mcp-integration-test'",
            limit=5,
        )

        self.assert_no_error(result, context="search with filter")
        self.assert_valid_list_response(result, min_length=0, context="search with filter")

    def test_get_ioa_platforms(self):
        """Test that get_ioa_platforms returns results with expected structure."""
        result = self.call_method(self.module.get_ioa_platforms)

        self.assert_no_error(result, context="get_ioa_platforms")
        self.assert_valid_list_response(result, min_length=1, context="get_ioa_platforms")

        if len(result) > 0:
            first = result[0]
            assert isinstance(first, dict), (
                f"Expected dict for platform, got {type(first)}"
            )

    def test_get_ioa_rule_types(self):
        """Test that get_ioa_rule_types returns results with expected structure."""
        result = self.call_method(self.module.get_ioa_rule_types, limit=5)

        self.assert_no_error(result, context="get_ioa_rule_types")
        self.assert_valid_list_response(result, min_length=1, context="get_ioa_rule_types")

        if len(result) > 0:
            first = result[0]
            assert isinstance(first, dict), (
                f"Expected dict for rule type, got {type(first)}"
            )

    # ── Write tests (using shared fixture) ───────────────────────────

    def test_create_rule_group_response_shape(self):
        """Test that the create response from the fixture has expected fields."""
        test_group = self.__class__._test_rule_group

        assert isinstance(test_group, dict), (
            f"Expected dict for created rule group, got {type(test_group)}"
        )

        for field in ["id", "name", "platform", "enabled", "rules"]:
            assert field in test_group, (
                f"Expected '{field}' in created rule group. "
                f"Available fields: {list(test_group.keys())}"
            )

        assert test_group["name"] == "falcon-mcp-integration-test", (
            f"Expected name 'falcon-mcp-integration-test', got '{test_group['name']}'"
        )
        assert test_group["platform"] == "linux", (
            f"Expected platform 'linux', got '{test_group['platform']}'"
        )

    def test_search_finds_created_group(self):
        """Round-trip: verify the created rule group is findable via search."""
        result = self.call_method(
            self.module.search_ioa_rule_groups,
            filter="name:'falcon-mcp-integration-test'",
            limit=10,
        )

        self.assert_no_error(result, context="round-trip search")
        self.assert_valid_list_response(result, min_length=1, context="round-trip search")

        found_ids = [
            item.get("id") for item in result if isinstance(item, dict)
        ]
        assert self.__class__._test_rule_group_id in found_ids, (
            f"Created rule group {self.__class__._test_rule_group_id} not found in search results. "
            f"Found IDs: {found_ids}"
        )

    # ── Delete test (disposable object) ──────────────────────────────

    def test_delete_rule_group(self):
        """Test delete by creating a separate disposable rule group.

        Creates a separate rule group (not the shared fixture), deletes it,
        and verifies the delete response has no errors.
        """
        # Create a disposable rule group
        create_result = self.call_method(
            self.module.create_ioa_rule_group,
            name="falcon-mcp-delete-test",
            platform="linux",
            description="Disposable rule group for delete test",
            comment="Integration test delete verification",
        )

        self.assert_no_error(create_result, context="create disposable rule group")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create disposable rule group"
        )

        disposable_id = self.get_first_id(create_result, id_field="id")
        if not disposable_id:
            self.skip_with_warning(
                "Could not extract ID from created rule group",
                context="test_delete_rule_group",
            )

        # Delete it
        delete_result = self.call_method(
            self.module.delete_ioa_rule_groups,
            ids=[disposable_id],
            comment="Integration test delete verification",
        )

        self.assert_no_error(delete_result, context="delete_ioa_rule_groups")
