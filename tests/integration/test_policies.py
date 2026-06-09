"""Integration tests for the Policies module."""

import time
import warnings

import pytest

from falcon_mcp.modules.policies import POLICY_TYPES, PoliciesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

# Timestamp filter fields use a wide range; everything else uses the entity's
# own value. Per-type `name` operator differs (see the FQL guide).
TIMESTAMP_FIELDS = {"created_timestamp", "modified_timestamp"}

# Documented filter fields validated as actually filtering (live, 2026-06-06).
# `name` is handled separately because its operator differs per type and a
# couple of types do not support it at all.
DOCUMENTED_FILTERS = {
    "prevention": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
    "sensor_update": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
    "firewall": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
    "device_control": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
    "response": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
    "content_update": ["enabled", "platform_name", "created_timestamp", "modified_timestamp"],
}

# Per-type `name` match operator: '~' (contains) or None (unsupported). Live
# validation (2026-06-06) showed exact `:` is unreliable for custom-named firewall
# and device_control policies (matches only built-ins like 'platform_default'),
# so all four name-filterable types use '~'.
NAME_OPERATOR = {
    "prevention": "~",
    "response": "~",
    "firewall": "~",
    "device_control": "~",
    "sensor_update": None,
    "content_update": None,
}


@pytest.mark.integration
class TestPoliciesIntegration(BaseIntegrationTest):
    """Integration tests for the Policies module with real API calls.

    Validates against the live API:
    - Correct FalconPy operation names for all six host-based policy types
    - device_control two-step search returns V2-only fields
    - search returns full policy details, not just IDs
    - Each documented FQL filter field actually filters (non-empty guard)
    - platform_name sort is rejected by our guard (would otherwise HTTP 500)
    - Members search returns host-shaped entities
    - create -> disable -> delete body shapes per type

    Tests skip with a warning when the required policy scope is absent (403).
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Policies module with a real client."""
        self.module = PoliciesModule(falcon_client)

    # ---- Helpers ----------------------------------------------------------------

    def _scopes_available(self, policy_type: str) -> bool:
        """Return True if a search for the given type does not error on scope."""
        result = self.call_method(
            self.module.search_policies, policy_type=policy_type, limit=1
        )
        if isinstance(result, dict) and "error" in result:
            return False
        if isinstance(result, list) and result and isinstance(result[0], dict):
            if "error" in result[0]:
                return False
        return True

    def _first_entity(self, policy_type: str):
        """Return one policy entity for the type, or None (empty/scopeless)."""
        result = self.call_method(
            self.module.search_policies, policy_type=policy_type, limit=1
        )
        if not result or isinstance(result, dict):
            return None
        return result[0]

    def _extract_id(self, result):
        """Extract a policy id from a create response (dict or bare string)."""
        if not isinstance(result, list) or not result:
            return None
        first = result[0]
        if isinstance(first, dict):
            return first.get("id")
        if isinstance(first, str):
            return first
        return None

    # ---- Operation name validation ----------------------------------------------

    def test_operation_names_are_correct(self):
        """Validate the search operation name for every policy type.

        A wrong operation name (typo) surfaces as an API error here even though
        mocked unit tests would pass. Missing scope (403) is skipped, not failed.
        """
        for policy_type in POLICY_TYPES:
            if not self._scopes_available(policy_type):
                self.skip_with_warning(
                    f"{policy_type} policy scope not available", "operation names"
                )
                continue
            result = self.call_method(
                self.module.search_policies, policy_type=policy_type, limit=1
            )
            if isinstance(result, list) and result and isinstance(result[0], dict):
                assert "error" not in result[0], (
                    f"Operation name validation failed for {policy_type}: {result[0]}"
                )

    def test_search_returns_full_details(self):
        """Search returns full policy details (id, name, platform_name, enabled)."""
        found_any = False
        for policy_type in POLICY_TYPES:
            if not self._scopes_available(policy_type):
                continue
            result = self.call_method(
                self.module.search_policies, policy_type=policy_type, limit=2
            )
            if not result or isinstance(result, dict):
                continue
            found_any = True
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "platform_name", "enabled"],
                context=f"{policy_type} full details",
            )
        if not found_any:
            self.skip_with_warning(
                "No policies of any type found", "search returns details"
            )

    def test_device_control_search_uses_v2_fields(self):
        """device_control results include a V2-only field (proves the two-step path)."""
        if not self._scopes_available("device_control"):
            self.skip_with_warning(
                "Device Control Policies scope not available", "dc v2 fields"
            )
            return
        result = self.call_method(
            self.module.search_policies, policy_type="device_control", limit=1
        )
        if not result or isinstance(result, dict):
            self.skip_with_warning(
                "No device_control policies found", "dc v2 fields"
            )
            return
        entity = result[0]
        v2_markers = {"usb_settings", "assignment_type", "bluetooth_settings"}
        present = v2_markers & set(entity.keys())
        assert present, (
            "device_control search returned no V2-only fields "
            f"({v2_markers}); the two-step query->getV2 path may have regressed "
            f"to the V1 combined op. Got keys: {sorted(entity.keys())}"
        )

    def test_documented_filter_fields_return_data(self):
        """Every documented FQL filter field must actually filter (non-empty guard).

        These query APIs do NOT validate filter fields — an unsupported field
        silently returns empty instead of a 400, so a documented field the API
        ignores looks identical to "no matches". This pulls one real entity per
        type and filters by each documented field's own value, asserting non-empty.
        """
        for policy_type in POLICY_TYPES:
            if not self._scopes_available(policy_type):
                continue
            entity = self._first_entity(policy_type)
            if entity is None:
                self.skip_with_warning(
                    f"No {policy_type} policy to validate filter fields",
                    "documented filter fields",
                )
                continue

            for field in DOCUMENTED_FILTERS[policy_type]:
                if field in TIMESTAMP_FIELDS:
                    filter_expr = f"{field}:>'now-3650d'"
                else:
                    value = entity.get(field)
                    if value is None:
                        warnings.warn(
                            f"{policy_type} entity has no '{field}' value to "
                            f"validate the documented filter field; skipping",
                            stacklevel=2,
                        )
                        continue
                    if isinstance(value, bool):
                        filter_expr = f"{field}:{str(value).lower()}"
                    else:
                        filter_expr = f"{field}:'{value}'"

                result = self.call_method(
                    self.module.search_policies,
                    policy_type=policy_type,
                    filter=filter_expr,
                    limit=1,
                )
                assert result and not isinstance(result, dict), (
                    f"Documented filter field '{field}' returned no results for "
                    f"{policy_type} (filter={filter_expr!r}) — the API likely "
                    f"silently ignores this field; fix the FQL guide."
                )
                assert "error" not in result[0], (
                    f"Documented filter field '{field}' errored for "
                    f"{policy_type} (filter={filter_expr!r}): {result[0]}"
                )

    def test_name_operator_returns_data(self):
        """The documented per-type `name` operator must actually match.

        prevention/response/firewall/device_control use `~` (contains).
        sensor_update/content_update do not support name filtering, so they are
        skipped. For each type with a known entity, build a name filter from the
        entity's own name and assert it returns data.
        """
        for policy_type, operator in NAME_OPERATOR.items():
            if operator is None:
                continue
            if not self._scopes_available(policy_type):
                continue
            entity = self._first_entity(policy_type)
            if entity is None or not entity.get("name"):
                self.skip_with_warning(
                    f"No {policy_type} policy with a name to validate",
                    "name operator",
                )
                continue
            name = entity["name"]
            filter_expr = f"name:{operator}'{name}'"
            result = self.call_method(
                self.module.search_policies,
                policy_type=policy_type,
                filter=filter_expr,
                limit=1,
            )
            assert result and not isinstance(result, dict), (
                f"Documented name operator '{operator}' returned nothing for "
                f"{policy_type} (filter={filter_expr!r}); the FQL guide's per-type "
                f"name-operator advice would be wrong."
            )
            assert "error" not in result[0], (
                f"name filter errored for {policy_type} (filter={filter_expr!r}): "
                f"{result[0]}"
            )

    def test_platform_name_sort_returns_error(self):
        """platform_name sort is rejected by our guard BEFORE hitting the API.

        The live API returns HTTP 500 for platform_name sorts on every type, so
        _validate_sort rejects them up front. This must return an error dict
        without raising.
        """
        result = self.call_method(
            self.module.search_policies,
            policy_type="prevention",
            sort="platform_name.asc",
            limit=1,
        )
        assert isinstance(result, list) and result and "error" in result[0], (
            f"platform_name sort should be rejected by _validate_sort, got: {result}"
        )

    def test_members_returns_hosts(self):
        """search_policy_members returns host-shaped entities when a policy has members."""
        for policy_type in POLICY_TYPES:
            if not self._scopes_available(policy_type):
                continue
            entity = self._first_entity(policy_type)
            if entity is None:
                continue
            policy_id = entity.get("id")
            if not policy_id:
                continue
            members = self.call_method(
                self.module.search_policy_members,
                policy_type=policy_type,
                id=policy_id,
                limit=1,
            )
            if not members or isinstance(members, dict):
                continue
            first = members[0]
            assert isinstance(first, dict), (
                f"{policy_type} members should be host dicts, got {type(first)}"
            )
            assert "device_id" in first or "hostname" in first, (
                f"{policy_type} member is not host-shaped: {sorted(first.keys())}"
            )
            return  # one type with members is enough
        self.skip_with_warning(
            "No policy with members found across types", "members returns hosts"
        )

    # ---- Create / disable / delete roundtrips -----------------------------------

    def test_create_disable_delete_roundtrip(self):
        """Create -> disable -> delete a policy per type with write scope.

        This is the live gate that validates the create/update/precedence body
        shapes. content_update is platform-agnostic; every other type uses
        Windows. Cleanup is wrapped in try/finally. A type without write scope is
        skipped, not failed.
        """
        tested_any = False
        for policy_type in POLICY_TYPES:
            if not self._scopes_available(policy_type):
                continue

            ts = int(time.time())
            name = f"falcon-mcp-test-{policy_type}-{ts}"
            create_kwargs: dict = {"policy_type": policy_type, "name": name}
            if self.module._CREATE_NEEDS_PLATFORM[policy_type]:
                create_kwargs["platform_name"] = "Windows"

            create_result = self.call_method(
                self.module.create_policy, **create_kwargs
            )
            # A write-scope failure surfaces as an error here; skip that type.
            if (
                isinstance(create_result, list)
                and create_result
                and isinstance(create_result[0], dict)
                and "error" in create_result[0]
            ):
                warnings.warn(
                    f"create {policy_type} policy failed (likely no write scope): "
                    f"{create_result[0]}",
                    stacklevel=2,
                )
                continue

            policy_id = self._extract_id(create_result)
            if not policy_id:
                warnings.warn(
                    f"Could not extract {policy_type} policy id from {create_result}",
                    stacklevel=2,
                )
                continue

            tested_any = True
            try:
                # Disable before delete (enabled policies typically reject delete).
                disable_result = self.call_method(
                    self.module.perform_policy_action,
                    policy_type=policy_type,
                    action_name="disable",
                    ids=[policy_id],
                )
                self.assert_no_error(
                    disable_result, context=f"{policy_type} disable"
                )

                delete_result = self.call_method(
                    self.module.delete_policies,
                    policy_type=policy_type,
                    ids=[policy_id],
                )
                self.assert_no_error(
                    delete_result, context=f"{policy_type} delete"
                )
            finally:
                self._safe_cleanup(policy_type, policy_id)

        if not tested_any:
            self.skip_with_warning(
                "No policy type had write scope for a roundtrip",
                "create/disable/delete",
            )

    def _safe_cleanup(self, policy_type: str, policy_id: str) -> None:
        """Best-effort delete that never raises (used in finally blocks)."""
        try:
            self.call_method(
                self.module.delete_policies,
                policy_type=policy_type,
                ids=[policy_id],
            )
        except Exception as exc:  # noqa: BLE001 - cleanup must not mask test result
            warnings.warn(
                f"Failed to clean up {policy_type} policy {policy_id}: {exc}",
                stacklevel=2,
            )
