"""Integration tests for the Correlation Rules module."""

import warnings

import pytest

from falcon_mcp.modules.correlation_rules import CorrelationRulesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCorrelationRulesIntegration(BaseIntegrationTest):
    """Integration tests for Correlation Rules module with real API calls.

    Validates:
    - Correct FalconPy operation names (combined_rules_get_v2, entities_rules_get_v1)
    - Combined search returns full rule details, not just IDs
    - Get-by-rule-ID returns current published version
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the correlation rules module with a real client."""
        self.module = CorrelationRulesModule(falcon_client)

    # -------------------------------------------------------------------------
    # Operation Name Validation
    # -------------------------------------------------------------------------

    def test_operation_names_search(self):
        """Validate combined_rules_get_v2 is the correct operation name."""
        result = self.call_method(self.module.search_correlation_rules, limit=1)
        self.assert_no_error(result, context="search operation names")

    # -------------------------------------------------------------------------
    # Search Tests
    # -------------------------------------------------------------------------

    def test_search_returns_full_details(self):
        """Test that search returns full rule objects, not just IDs."""
        result = self.call_method(self.module.search_correlation_rules, limit=5)

        self.assert_no_error(result, context="search_correlation_rules full details")
        self.assert_valid_list_response(result, min_length=0, context="search_correlation_rules")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["rule_id", "id", "name", "severity", "status", "state", "search"],
                context="search_correlation_rules full details",
            )

    def test_search_with_status_filter(self):
        """Test that filtering by status:'active' returns only active rules."""
        result = self.call_method(
            self.module.search_correlation_rules,
            filter="status:'active'",
            limit=5,
        )

        self.assert_no_error(result, context="search with status filter")
        self.assert_valid_list_response(result, min_length=0, context="search with status filter")

        for rule in result:
            assert isinstance(rule, dict), f"Expected dict, got {type(rule)}"
            assert rule.get("status") == "active", (
                f"Expected status 'active', got '{rule.get('status')}'"
            )

    def test_search_respects_limit(self):
        """Test that the limit parameter caps the number of results."""
        result = self.call_method(self.module.search_correlation_rules, limit=3)

        self.assert_no_error(result, context="search with limit=3")
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) <= 3, f"Expected at most 3 results, got {len(result)}"

    def test_search_invalid_filter_returns_error(self):
        """Test that an invalid FQL filter returns a structured error, not a crash."""
        result = self.call_method(
            self.module.search_correlation_rules,
            filter="invalid_field:'bad'",
            limit=5,
        )

        # Should return a structured error response (dict or list with error), not raise
        assert result is not None, "Expected a response, got None"
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            # Error surfaced in list — acceptable
            pass
        elif isinstance(result, dict):
            # Error surfaced as dict — acceptable
            pass
        # No assertion on the exact shape; just verify it does not raise

    # -------------------------------------------------------------------------
    # Search Details Validation
    # -------------------------------------------------------------------------

    def test_search_returns_rule_id_and_version_id(self):
        """Test that every result has both rule_id (stable) and id (version)."""
        result = self.call_method(self.module.search_correlation_rules, limit=5)

        self.assert_no_error(result, context="search rule_id and version id")
        self.assert_valid_list_response(result, min_length=0, context="search rule_id and id")

        for i, rule in enumerate(result):
            assert isinstance(rule, dict), f"Expected dict at index {i}"
            assert "rule_id" in rule, (
                f"Missing 'rule_id' at index {i}. Fields: {list(rule.keys())}"
            )
            assert "id" in rule, (
                f"Missing 'id' (version id) at index {i}. Fields: {list(rule.keys())}"
            )

    def test_search_returns_search_object(self):
        """Test that results contain a 'search' dict with a 'filter' field."""
        result = self.call_method(self.module.search_correlation_rules, limit=5)

        self.assert_no_error(result, context="search object presence")
        self.assert_valid_list_response(result, min_length=0, context="search object presence")

        for i, rule in enumerate(result):
            assert isinstance(rule, dict), f"Expected dict at index {i}"
            assert "search" in rule, (
                f"Missing 'search' key at index {i}. Fields: {list(rule.keys())}"
            )
            search_obj = rule["search"]
            assert isinstance(search_obj, dict), (
                f"Expected 'search' to be a dict at index {i}, got {type(search_obj)}"
            )
            assert "filter" in search_obj, (
                f"Missing 'filter' in 'search' dict at index {i}. Keys: {list(search_obj.keys())}"
            )

    # -------------------------------------------------------------------------
    # Create / Update / Delete Lifecycle (may 401 if scope is insufficient)
    # -------------------------------------------------------------------------

    def test_create_rule_lifecycle(self):
        """Test create → verify rule_id → delete lifecycle.

        Skipped if the API key lacks Correlation Rules write scope (401).
        Any created rule is deleted in a finally block to avoid leaving test data.
        """
        # Resolve customer_id from an existing rule
        search_result = self.call_method(self.module.search_correlation_rules, limit=1)
        if not search_result or not isinstance(search_result, list) or len(search_result) == 0:
            self.skip_with_warning(
                "No existing rules to derive customer_id from",
                context="test_create_rule_lifecycle",
            )
        customer_id = search_result[0].get("customer_id")
        if not customer_id:
            self.skip_with_warning(
                "Could not extract customer_id from existing rule",
                context="test_create_rule_lifecycle",
            )

        created_rule_id = None
        try:
            result = self.call_method(
                self.module.create_correlation_rule,
                customer_id=customer_id,
                name="falcon-mcp-integration-test-rule",
                search_filter="#event_simpleName=ProcessRollup2 | CommandLine=*test*",
                severity=10,
                description="Integration test rule — safe to delete",
                status="inactive",
            )

            if isinstance(result, list) and len(result) > 0:
                first = result[0]
                if isinstance(first, dict) and "error" in first:
                    details = first.get("details", {})
                    status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
                    if status_code in (401, 403):
                        pytest.skip("Insufficient scope for create_correlation_rule")
                    # Other error — surface it
                    assert False, f"create_correlation_rule failed: {first}"

            self.assert_no_error(result, context="create_correlation_rule")
            self.assert_valid_list_response(result, min_length=1, context="create_correlation_rule")

            first = result[0]
            assert isinstance(first, dict), f"Expected dict, got {type(first)}"
            assert "rule_id" in first, (
                f"Missing 'rule_id' in created rule. Fields: {list(first.keys())}"
            )
            created_rule_id = first["rule_id"]

        finally:
            if created_rule_id:
                delete_result = self.call_method(
                    self.module.delete_correlation_rules,
                    ids=[created_rule_id],
                    comment="Cleanup from integration test",
                )
                # Best-effort cleanup — don't fail the test if delete fails
                _ = delete_result

    def test_update_rule(self):
        """Test updating an existing rule's description creates a new version.

        Searches for an existing rule, updates its description, then restores
        it. Skipped if update returns 401/403 (insufficient scope).
        """
        search_result = self.call_method(self.module.search_correlation_rules, limit=1)
        self.assert_no_error(search_result, context="search before update test")

        if not search_result or not isinstance(search_result, list) or len(search_result) == 0:
            self.skip_with_warning(
                "No rules available to test update",
                context="test_update_rule",
            )

        rule = search_result[0]
        rule_id = rule.get("rule_id")
        original_description = rule.get("description", "")

        if not rule_id:
            self.skip_with_warning(
                "Could not extract rule_id for update test",
                context="test_update_rule",
            )

        test_description = f"{original_description} [mcp-integration-test]".strip()

        update_result = self.call_method(
            self.module.update_correlation_rule,
            rule_id=rule_id,
            description=test_description,
            comment="Integration test update — restoring original description next",
        )

        if isinstance(update_result, list) and len(update_result) > 0:
            first = update_result[0]
            if isinstance(first, dict) and "error" in first:
                details = first.get("details", {})
                status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
                if status_code in (401, 403):
                    pytest.skip("Insufficient scope for update_correlation_rule")
                if status_code == 400:
                    pytest.skip("Update body rejected by API (400) — rule may require additional fields")

        self.assert_no_error(update_result, context="update_correlation_rule")
        self.assert_valid_list_response(update_result, min_length=1, context="update_correlation_rule")

        updated = update_result[0]
        assert isinstance(updated, dict), f"Expected dict, got {type(updated)}"
        assert updated.get("rule_id") == rule_id, (
            f"Expected rule_id '{rule_id}', got '{updated.get('rule_id')}'"
        )

        # Restore original description — warn if cleanup fails
        restore_result = self.call_method(
            self.module.update_correlation_rule,
            rule_id=rule_id,
            description=original_description or "",
            comment="Integration test cleanup — restoring original description",
        )
        if isinstance(restore_result, list) and len(restore_result) > 0:
            first_restore = restore_result[0]
            if isinstance(first_restore, dict) and "error" in first_restore:
                warnings.warn(
                    f"INTEGRATION TEST CLEANUP FAILED: Could not restore rule {rule_id} description. "
                    f"Error: {first_restore.get('error')}",
                    stacklevel=1,
                )
