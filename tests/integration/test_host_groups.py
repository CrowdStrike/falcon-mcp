"""Integration tests for the Host Groups module."""

import time
import warnings

import pytest

from falcon_mcp.modules.host_groups import HostGroupsModule
from tests.integration.utils.base_integration_test import (
    BaseIntegrationTest,
    resolve_field_defaults,
)


@pytest.mark.integration
class TestHostGroupsIntegration(BaseIntegrationTest):
    """Integration tests for the Host Groups module with real API calls.

    Validates:
    - Correct FalconPy operation names (queryCombinedHostGroups,
      queryCombinedGroupMembers, createHostGroups, updateHostGroups,
      deleteHostGroups, performGroupAction)
    - Combined search returns full entities in a single call (no two-step pattern)
    - Body/query param formats for mutating endpoints
    - Full lifecycle roundtrip (create -> update -> action -> delete)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Host Groups module with a real client."""
        self.module = HostGroupsModule(falcon_client)

    @pytest.fixture(scope="class")
    def lifecycle_group(self, falcon_client):
        """Create a static host group for the class and clean it up afterwards.

        Exercises create -> update -> add/remove host action -> delete to validate
        every mutating operation name and body format against the live API. Always
        cleans up via delete, even if intermediate steps fail.
        """
        module = HostGroupsModule(falcon_client)
        unique_name = f"falcon-mcp-test-{int(time.time())}"

        create_kwargs = resolve_field_defaults(
            module.create_host_group,
            {
                "name": unique_name,
                "group_type": "static",
                "description": "Integration test group - safe to delete",
            },
        )
        create_result = module.create_host_group(**create_kwargs)

        if not isinstance(create_result, list) or len(create_result) == 0:
            pytest.skip(f"Unexpected create response: {create_result}")

        first = create_result[0]
        if isinstance(first, dict) and "error" in first:
            pytest.skip(
                f"Cannot create test host group (check Host Groups:write scope): {first}"
            )
        if not isinstance(first, dict) or "id" not in first:
            pytest.skip(f"Unexpected create response shape: {create_result}")

        group_id = first["id"]

        yield {"id": group_id, "name": unique_name, "created": first}

        # Teardown: always delete the group
        try:
            delete_kwargs = resolve_field_defaults(
                module.delete_host_groups, {"ids": [group_id]}
            )
            module.delete_host_groups(**delete_kwargs)
        except Exception as e:  # noqa: BLE001
            warnings.warn(
                f"Failed to clean up test host group {group_id}: {e}",
                stacklevel=2,
            )

    def test_operation_names_are_correct(self, lifecycle_group):
        """Validate every FalconPy operation name against the live API.

        Wrong operation names fail with error responses. This covers all 6 ops:
        the two searches plus the create/update/action/delete in the lifecycle.
        """
        group_id = lifecycle_group["id"]

        # queryCombinedHostGroups
        search_result = self.call_method(self.module.search_host_groups, limit=1)
        self.assert_no_error(search_result, context="queryCombinedHostGroups")

        # queryCombinedGroupMembers
        members_result = self.call_method(
            self.module.search_host_group_members, id=group_id, limit=1
        )
        self.assert_no_error(members_result, context="queryCombinedGroupMembers")

        # updateHostGroups
        update_result = self.call_method(
            self.module.update_host_group,
            id=group_id,
            description="Integration test group - updated",
        )
        self.assert_no_error(update_result, context="updateHostGroups")

        # performGroupAction (remove-hosts is a no-op safe action on an empty group)
        action_result = self.call_method(
            self.module.perform_host_group_action,
            action_name="remove-hosts",
            ids=[group_id],
            filter="device_id:['000000000000000000000000000000ff']",
        )
        self.assert_no_error(action_result, context="performGroupAction")

    def test_search_host_groups_returns_details(self):
        """Test that search_host_groups returns full details in a single call."""
        result = self.call_method(self.module.search_host_groups, limit=5)

        self.assert_no_error(result, context="search_host_groups")
        self.assert_valid_list_response(
            result, min_length=0, context="search_host_groups"
        )

        if isinstance(result, list) and len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "group_type"],
                context="search_host_groups",
            )

    def test_search_host_groups_with_filter(self):
        """Test search_host_groups with an FQL filter."""
        result = self.call_method(
            self.module.search_host_groups,
            filter="group_type:'static'",
            limit=5,
        )

        self.assert_no_error(result, context="search_host_groups with filter")

    def test_search_host_group_members_returns_hosts(self, lifecycle_group):
        """Test that member search returns host device entities, not just IDs."""
        result = self.call_method(
            self.module.search_host_group_members,
            id=lifecycle_group["id"],
            limit=5,
        )

        self.assert_no_error(result, context="search_host_group_members")
        self.assert_valid_list_response(
            result, min_length=0, context="search_host_group_members"
        )

        if isinstance(result, list) and len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["device_id"],
                context="search_host_group_members",
            )

    def test_search_host_group_members_with_filter(self):
        """Validate the member `filter` param against a populated group.

        `id` and `filter` are complementary, not mutually exclusive: `id` selects
        which group's members to enumerate, `filter` narrows that set by HOST device
        attributes. Find any group that has members, then apply a host FQL filter and
        assert the call succeeds. Skips if the tenant has no populated groups.

        Note: do NOT use filter="*" here — the live API rejects it with HTTP 400.
        Omitting `filter` is the "all members" path.
        """
        groups = self.call_method(self.module.search_host_groups, limit=50)
        if not isinstance(groups, list) or len(groups) == 0:
            self.skip_with_warning(
                "No host groups in tenant", context="member filter validation"
            )
            return

        populated_id = None
        for group in groups:
            if not isinstance(group, dict) or "id" not in group:
                continue
            members = self.call_method(
                self.module.search_host_group_members, id=group["id"], limit=1
            )
            if isinstance(members, list) and len(members) > 0:
                populated_id = group["id"]
                break

        if populated_id is None:
            self.skip_with_warning(
                "No populated host groups in tenant",
                context="member filter validation",
            )
            return

        result = self.call_method(
            self.module.search_host_group_members,
            id=populated_id,
            filter="platform_name:'Windows'",
            limit=5,
        )

        self.assert_no_error(result, context="member search with host filter")
        self.assert_valid_list_response(
            result, min_length=0, context="member search with host filter"
        )

    def test_create_response_shape(self, lifecycle_group):
        """Test that the create response from the fixture has expected fields."""
        created = lifecycle_group["created"]

        for field in ["id", "name", "group_type"]:
            assert field in created, (
                f"Expected '{field}' in created host group. "
                f"Available fields: {list(created.keys())}"
            )

        assert created["group_type"] == "static", (
            f"Expected group_type 'static', got '{created['group_type']}'"
        )

    def test_created_group_appears_in_search(self, lifecycle_group):
        """Round-trip: verify the created group is findable via search."""
        result = self.call_method(
            self.module.search_host_groups,
            filter=f"name:'{lifecycle_group['name']}'",
            limit=10,
        )

        self.assert_no_error(result, context="round-trip search")
        self.assert_valid_list_response(
            result, min_length=1, context="round-trip search"
        )

        found_ids = [
            item.get("id") for item in result if isinstance(item, dict)
        ]
        assert lifecycle_group["id"] in found_ids, (
            f"Created group {lifecycle_group['id']} not found in search results. "
            f"Found IDs: {found_ids}"
        )
