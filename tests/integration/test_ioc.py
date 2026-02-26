"""Integration tests for the IOC module."""

import pytest

from falcon_mcp.modules.ioc import IOCModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIOCIntegration(BaseIntegrationTest):
    """Integration tests for IOC module with real API calls.

    Validates:
    - Correct FalconPy operation names (indicator_search_v1, indicator_get_v1,
      indicator_create_v1, indicator_delete_v1)
    - Two-step search pattern returns full details, not just IDs
    - GET query param usage for indicator_get_v1
    - Full CRUD lifecycle (create, search, delete)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the IOC module with a real client."""
        self.module = IOCModule(falcon_client)

    @pytest.fixture(autouse=True, scope="class")
    def create_test_ioc(self, falcon_client):
        """Create a test IOC for the class and clean up after all tests.

        Creates a domain IOC with .invalid TLD (IANA-reserved, never resolves)
        and detect-only action for safety. Tagged with a unique source for
        easy identification and filter-based searching.
        """
        module = IOCModule(falcon_client)

        # Create test IOC
        from tests.integration.utils.base_integration_test import resolve_field_defaults

        create_kwargs = resolve_field_defaults(module.add_ioc, {
            "type": "domain",
            "value": "falcon-mcp-integration-test.invalid",
            "action": "detect",
            "severity": "low",
            "source": "falcon-mcp-integration-test",
            "description": "Integration test IOC - safe to delete",
            "platforms": ["linux"],
            "applied_globally": True,
            "ignore_warnings": True,
        })
        result = module.add_ioc(**create_kwargs)

        # Validate creation succeeded
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                pytest.skip(
                    f"Cannot create test IOC (check IOC Management:write scope): {first}"
                )
            if isinstance(first, dict) and "id" in first:
                self.__class__._test_ioc = first
                self.__class__._test_ioc_id = first["id"]
            else:
                pytest.skip(f"Unexpected create response shape: {result}")
        else:
            pytest.skip(f"Unexpected create response: {result}")

        yield

        # Teardown: delete the test IOC
        try:
            delete_kwargs = resolve_field_defaults(module.remove_iocs, {
                "ids": [self.__class__._test_ioc_id],
                "comment": "Integration test cleanup",
            })
            module.remove_iocs(**delete_kwargs)
        except Exception as e:
            import warnings
            warnings.warn(
                f"Failed to clean up test IOC {self.__class__._test_ioc_id}: {e}",
                stacklevel=2,
            )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong (e.g., 'indicator_search_v1' typo),
        the API call will fail with an error response.
        """
        result = self.call_method(self.module.search_iocs, limit=1)
        self.assert_no_error(result, context="operation name validation")

    def test_search_iocs_returns_details(self):
        """Test that search_iocs returns full IOC details, not just IDs.

        Validates the two-step search pattern:
        1. indicator_search_v1 returns IOC IDs
        2. indicator_get_v1 returns full details (GET with query params)
        """
        result = self.call_method(self.module.search_iocs, limit=5)

        self.assert_no_error(result, context="search_iocs")
        self.assert_valid_list_response(result, min_length=0, context="search_iocs")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "type", "value"],
                context="search_iocs",
            )

    def test_search_iocs_with_filter(self):
        """Test search_iocs with FQL filter targeting the test IOC."""
        result = self.call_method(
            self.module.search_iocs,
            filter="source:'falcon-mcp-integration-test'",
            limit=5,
        )

        self.assert_no_error(result, context="search_iocs with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_iocs with filter"
        )

    def test_search_iocs_with_sort(self):
        """Test search_iocs with sort parameter."""
        result = self.call_method(
            self.module.search_iocs,
            sort="modified_on.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_iocs with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search_iocs with sort"
        )

    def test_add_ioc_response_shape(self):
        """Test that the create response from the fixture has expected fields."""
        test_ioc = self.__class__._test_ioc

        assert isinstance(test_ioc, dict), (
            f"Expected dict for created IOC, got {type(test_ioc)}"
        )

        for field in ["id", "type", "value"]:
            assert field in test_ioc, (
                f"Expected '{field}' in created IOC. "
                f"Available fields: {list(test_ioc.keys())}"
            )

        assert test_ioc["type"] == "domain", (
            f"Expected type 'domain', got '{test_ioc['type']}'"
        )
        assert test_ioc["value"] == "falcon-mcp-integration-test.invalid", (
            f"Expected value 'falcon-mcp-integration-test.invalid', got '{test_ioc['value']}'"
        )

    def test_created_ioc_appears_in_search(self):
        """Round-trip: verify the created IOC is findable via search."""
        result = self.call_method(
            self.module.search_iocs,
            filter="source:'falcon-mcp-integration-test'+value:'falcon-mcp-integration-test.invalid'",
            limit=10,
        )

        self.assert_no_error(result, context="round-trip search")
        self.assert_valid_list_response(
            result, min_length=1, context="round-trip search"
        )

        # Verify the test IOC is in results
        found_ids = [
            item.get("id") for item in result if isinstance(item, dict)
        ]
        assert self.__class__._test_ioc_id in found_ids, (
            f"Created IOC {self.__class__._test_ioc_id} not found in search results. "
            f"Found IDs: {found_ids}"
        )

    def test_remove_ioc_by_id(self):
        """Test remove_iocs by ID using a dedicated IOC.

        Creates a separate IOC (not the shared fixture), deletes it by ID,
        and verifies the delete response has no errors.
        """
        # Create a disposable IOC for this test
        create_result = self.call_method(
            self.module.add_ioc,
            type="domain",
            value="falcon-mcp-delete-test.invalid",
            action="detect",
            severity="low",
            source="falcon-mcp-integration-test",
            description="Disposable IOC for delete test",
            platforms=["linux"],
            applied_globally=True,
            ignore_warnings=True,
        )

        self.assert_no_error(create_result, context="create disposable IOC")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create disposable IOC"
        )

        disposable_id = self.get_first_id(create_result, id_field="id")
        if not disposable_id:
            self.skip_with_warning(
                "Could not extract ID from created IOC",
                context="test_remove_ioc_by_id",
            )

        # Delete it
        delete_result = self.call_method(
            self.module.remove_iocs,
            ids=[disposable_id],
            comment="Integration test delete verification",
        )

        self.assert_no_error(delete_result, context="remove_iocs by ID")
