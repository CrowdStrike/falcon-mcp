"""Integration tests for the Firewall module."""

import pytest

from falcon_mcp.modules.firewall import FirewallModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestFirewallIntegration(BaseIntegrationTest):
    """Integration tests for Firewall module with real API calls.

    Validates:
    - Correct FalconPy operation names (query_rules, get_rules, query_rule_groups, get_rule_groups)
    - Two-step search pattern returns full details, not just IDs
    - GET query param usage for get_by_ids calls
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the firewall module with a real client."""
        self.module = FirewallModule(falcon_client)

    def test_operation_names_are_correct(self):
        """Validate operation names by executing a minimal read query."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )
        self.assert_no_error(result, context="operation name validation")

    def test_search_firewall_rules_returns_details(self):
        """Test that search_firewall_rules returns full details, not only IDs."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rules")
        self.assert_valid_list_response(result, min_length=0, context="search_firewall_rules")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "platform"],
                context="search_firewall_rules",
            )

    def test_search_firewall_rules_with_filter(self):
        """Test firewall rule search with an FQL filter."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter="enabled:true",
            limit=3,
            offset=0,
            sort="modified_on.desc",
            q=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rules with filter")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_firewall_rules with filter"
            )

    def test_search_firewall_rule_groups_returns_details(self):
        """Test that search_firewall_rule_groups returns full details."""
        result = self.call_method(
            self.module.search_firewall_rule_groups,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rule_groups")
        self.assert_valid_list_response(
            result, min_length=0, context="search_firewall_rule_groups"
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "platform"],
                context="search_firewall_rule_groups",
            )

    def test_search_firewall_rule_groups_with_filter(self):
        """Test firewall rule group search with an FQL filter."""
        result = self.call_method(
            self.module.search_firewall_rule_groups,
            filter="enabled:true",
            limit=3,
            offset=0,
            sort="modified_on.desc",
            q=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rule_groups with filter")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_firewall_rule_groups with filter"
            )

    def test_search_firewall_policy_rules(self):
        """Test searching policy rules using a discovered rule group ID.

        Uses dynamic ID discovery: first searches for a rule group,
        then uses its ID to search for policy rules.
        """
        groups_result = self.call_method(
            self.module.search_firewall_rule_groups,
            limit=1,
        )

        if not groups_result or (isinstance(groups_result, list) and len(groups_result) == 0):
            self.skip_with_warning(
                "No firewall rule groups available",
                context="test_search_firewall_policy_rules",
            )

        group_id = self.get_first_id(groups_result)
        if not group_id:
            self.skip_with_warning(
                "Could not extract rule group ID from search results",
                context="test_search_firewall_policy_rules",
            )

        result = self.call_method(
            self.module.search_firewall_policy_rules,
            policy_id=group_id,
            limit=3,
        )

        # Gracefully handle cases where no firewall policy matches the ID
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            if "error" in result[0]:
                self.skip_with_warning(
                    "No firewall policy found for the discovered ID",
                    context="test_search_firewall_policy_rules",
                )

        self.assert_no_error(result, context="search_firewall_policy_rules")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_firewall_policy_rules"
            )

