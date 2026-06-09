"""
Tests for the Policies module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.policies import PoliciesModule
from tests.modules.utils.test_modules import TestModules

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)

# Maps policy_type -> (combined_op, query_op, get_op, members_op).
EXPECTED_OPS = {
    "prevention": (
        "queryCombinedPreventionPolicies",
        "queryPreventionPolicies",
        "getPreventionPolicies",
        "queryCombinedPreventionPolicyMembers",
    ),
    "sensor_update": (
        "queryCombinedSensorUpdatePoliciesV2",
        "querySensorUpdatePolicies",
        "getSensorUpdatePoliciesV2",
        "queryCombinedSensorUpdatePolicyMembers",
    ),
    "firewall": (
        "queryCombinedFirewallPolicies",
        "queryFirewallPolicies",
        "getFirewallPolicies",
        "queryCombinedFirewallPolicyMembers",
    ),
    "device_control": (
        "queryCombinedDeviceControlPolicies",
        "queryDeviceControlPolicies",
        "getDeviceControlPoliciesV2",
        "queryCombinedDeviceControlPolicyMembers",
    ),
    "response": (
        "queryCombinedRTResponsePolicies",
        "queryRTResponsePolicies",
        "getRTResponsePolicies",
        "queryCombinedRTResponsePolicyMembers",
    ),
    "content_update": (
        "queryCombinedContentUpdatePolicies",
        "queryContentUpdatePolicies",
        "getContentUpdatePolicies",
        "queryCombinedContentUpdatePolicyMembers",
    ),
}


class TestPoliciesModule(TestModules):
    """Test cases for the Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(PoliciesModule)

    # ---- Registration ----------------------------------------------------------

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_policies",
            "falcon_search_policy_members",
            "falcon_create_policy",
            "falcon_update_policy",
            "falcon_delete_policies",
            "falcon_perform_policy_action",
            "falcon_set_policy_precedence",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_policies_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_tool_is_read_only(self):
        """search_policies must carry read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_policies", READ_ONLY_ANNOTATIONS)

    def test_tool_annotations(self):
        """Read and mutating tools must carry the correct annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_policies", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_search_policy_members", READ_ONLY_ANNOTATIONS
        )
        self.assert_tool_annotations("falcon_create_policy", MUTATING_ANNOTATIONS)
        self.assert_tool_annotations("falcon_update_policy", MUTATING_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_policies", DESTRUCTIVE_ANNOTATIONS
        )
        self.assert_tool_annotations(
            "falcon_perform_policy_action", MUTATING_ANNOTATIONS
        )
        self.assert_tool_annotations(
            "falcon_set_policy_precedence", MUTATING_ANNOTATIONS
        )

    # ---- Search ----------------------------------------------------------------

    def _combined_response(self):
        return {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "pol-1", "name": "a", "platform_name": "Windows"},
                    {"id": "pol-2", "name": "b", "platform_name": "Windows"},
                ]
            },
        }

    def _query_then_get_responses(self):
        query_response = {
            "status_code": 200,
            "body": {"resources": ["pol-1", "pol-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "pol-1", "name": "a", "usb_settings": {}},
                    {"id": "pol-2", "name": "b", "usb_settings": {}},
                ]
            },
        }
        return query_response, get_response

    def test_search_dispatches_to_correct_op_per_type(self):
        """Combined types do one call; device_control does query then getV2."""
        for policy_type, ops in EXPECTED_OPS.items():
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()

                if policy_type == "device_control":
                    self.mock_client.command.side_effect = (
                        self._query_then_get_responses()
                    )
                else:
                    self.mock_client.command.return_value = self._combined_response()
                    self.mock_client.command.side_effect = None

                result = self.module.search_policies(
                    policy_type=policy_type,
                    filter="enabled:true",
                    limit=50,
                    offset=0,
                    sort=None,
                )

                calls = self.mock_client.command.call_args_list
                if policy_type == "device_control":
                    # Two-step: query op then get op (get uses params).
                    self.assertEqual(self.mock_client.command.call_count, 2)
                    self.assertEqual(calls[0][0][0], ops[1])  # query op
                    self.assertEqual(calls[1][0][0], ops[2])  # get op
                    self.assertIn("parameters", calls[1][1])
                    self.assertNotIn("body", calls[1][1])
                else:
                    # Single combined call.
                    self.assertEqual(self.mock_client.command.call_count, 1)
                    self.assertEqual(calls[0][0][0], ops[0])  # combined op

                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]["id"], "pol-1")

    def test_search_invalid_type(self):
        """An invalid policy_type returns an error and makes no API call."""
        result = self.module.search_policies(
            policy_type="bogus",
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_search_platform_name_sort_rejected(self):
        """Sorting by platform_name returns an error before any API call."""
        result = self.module.search_policies(
            policy_type="prevention",
            filter=None,
            limit=10,
            offset=0,
            sort="platform_name.asc",
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_search_unknown_sort_rejected(self):
        """An unknown sort field returns an error before any API call."""
        result = self.module.search_policies(
            policy_type="prevention",
            filter=None,
            limit=10,
            offset=0,
            sort="bogus_field.desc",
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_search_empty_returns_fql_guide(self):
        """Empty combined results include the FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_policies(
            policy_type="firewall",
            filter="name:'nothing'",
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_device_control_empty_returns_fql_guide(self):
        """Empty device_control (two-step) results also include the FQL guide.

        The two-step path has its own empty-result branch (after the query op
        returns no IDs); it must return the FQL guide dict, not a bare list.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_policies(
            policy_type="device_control",
            filter="name:~'nothing'",
            limit=10,
            offset=0,
            sort=None,
        )
        # Only the query op should have been called (no get, since no IDs).
        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_policy_members_per_type(self):
        """Each type calls its members op and passes the policy id through."""
        for policy_type, ops in EXPECTED_OPS.items():
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = None
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {
                        "resources": [
                            {"device_id": "h1", "hostname": "host-1"},
                        ]
                    },
                }
                result = self.module.search_policy_members(
                    policy_type=policy_type,
                    id="pol-123",
                    filter="platform_name:'Windows'",
                    limit=50,
                    offset=0,
                    sort=None,
                )
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(call[0][0], ops[3])  # members op
                self.assertEqual(call[1]["parameters"]["id"], "pol-123")
                self.assertEqual(result[0]["device_id"], "h1")

    def test_search_policy_members_missing_id(self):
        """Members search without an id returns a guiding error, no API call."""
        result = self.module.search_policy_members(
            policy_type="firewall",
            id="",
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_search_policy_members_invalid_type(self):
        """Members search with an invalid type returns an error, no API call."""
        result = self.module.search_policy_members(
            policy_type="bogus",
            id="pol-1",
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    # ---- Create / Update -------------------------------------------------------

    def _create_kwargs(self, **overrides):
        """Full create kwargs with everything None unless overridden."""
        base = dict(
            name=None,
            platform_name=None,
            description=None,
            settings=None,
            clone_id=None,
        )
        base.update(overrides)
        return base

    def _create_response(self, entity):
        return {"status_code": 201, "body": {"resources": [entity]}}

    def test_create_missing_name_per_type(self):
        """Create without a name returns a guiding error for every type."""
        for policy_type in EXPECTED_OPS:
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()
                result = self.module.create_policy(
                    policy_type=policy_type,
                    **self._create_kwargs(platform_name="Windows"),
                )
                self.assertIn("error", result[0])
                self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_missing_platform_for_required_types(self):
        """Create without platform_name errors for every type except content_update."""
        for policy_type in EXPECTED_OPS:
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = self._create_response(
                    {"id": "pol-1", "name": "n"}
                )
                result = self.module.create_policy(
                    policy_type=policy_type,
                    **self._create_kwargs(name="my-policy"),
                )
                if policy_type == "content_update":
                    # No platform required — the call should go through.
                    self.assertEqual(self.mock_client.command.call_count, 1)
                else:
                    self.assertIn("error", result[0])
                    self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_content_update_omits_platform_name(self):
        """content_update create body must NOT contain platform_name."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "cu-1", "name": "n"}
        )
        self.module.create_policy(
            policy_type="content_update",
            **self._create_kwargs(name="my-cu", platform_name="Windows"),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "createContentUpdatePolicies")
        body = call[1]["body"]
        resource = body["resources"][0]
        self.assertNotIn("platform_name", resource)

    def test_create_device_control_uses_policies_wrapper(self):
        """device_control create uses the 'policies' wrapper, not 'resources'."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "dc-1", "name": "n"}
        )
        self.module.create_policy(
            policy_type="device_control",
            **self._create_kwargs(name="my-dc", platform_name="Windows"),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "postDeviceControlPoliciesV2")
        body = call[1]["body"]
        self.assertIn("policies", body)
        self.assertNotIn("resources", body)
        self.assertEqual(body["policies"][0]["platform_name"], "Windows")

    def test_create_non_device_control_uses_resources_wrapper(self):
        """Non-device_control create uses the 'resources' wrapper."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "fw-1", "name": "n"}
        )
        self.module.create_policy(
            policy_type="firewall",
            **self._create_kwargs(name="my-fw", platform_name="Windows"),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "createFirewallPolicies")
        body = call[1]["body"]
        self.assertIn("resources", body)
        self.assertNotIn("policies", body)

    def test_create_passes_clone_id_and_settings(self):
        """clone_id and settings pass through unchanged on create."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "p-1", "name": "n"}
        )
        self.module.create_policy(
            policy_type="prevention",
            **self._create_kwargs(
                name="cloned",
                platform_name="Windows",
                clone_id="src-1",
                settings=[{"id": "x", "value": True}],
            ),
        )
        call = self.mock_client.command.call_args_list[0]
        resource = call[1]["body"]["resources"][0]
        self.assertEqual(resource["clone_id"], "src-1")
        self.assertEqual(resource["settings"], [{"id": "x", "value": True}])

    def test_create_invalid_type(self):
        """Create with an invalid type returns an error, no API call."""
        result = self.module.create_policy(
            policy_type="bogus", **self._create_kwargs(name="n", platform_name="Windows")
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_update_missing_id(self):
        """Update without an id returns a guiding error, no API call."""
        result = self.module.update_policy(
            policy_type="prevention",
            id=None,
            name="renamed",
            description=None,
            settings=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_update_invalid_type(self):
        """Update with an invalid type returns an error, no API call."""
        result = self.module.update_policy(
            policy_type="bogus",
            id="p-1",
            name="renamed",
            description=None,
            settings=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_update_places_id_inside_resource(self):
        """Update body places id inside the resource object."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "p-1", "name": "renamed"}
        )
        self.module.update_policy(
            policy_type="prevention",
            id="p-1",
            name="renamed",
            description=None,
            settings=None,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "updatePreventionPolicies")
        resource = call[1]["body"]["resources"][0]
        self.assertEqual(resource["id"], "p-1")
        self.assertEqual(resource["name"], "renamed")
        self.assertNotIn("platform_name", resource)

    def test_update_device_control_uses_policies_wrapper(self):
        """device_control update uses the 'policies' wrapper with id inside."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "dc-1", "name": "n"}
        )
        self.module.update_policy(
            policy_type="device_control",
            id="dc-1",
            name="renamed",
            description=None,
            settings=None,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "patchDeviceControlPoliciesV2")
        body = call[1]["body"]
        self.assertIn("policies", body)
        self.assertEqual(body["policies"][0]["id"], "dc-1")

    def test_update_dispatches_to_correct_op_per_type(self):
        """update_policy dispatches to the correct update op for every type.

        Guards against a typo in any of the six update operation names — search,
        delete, and members already loop over every type, so update should too.
        """
        for policy_type in EXPECTED_OPS:
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = None
                self.mock_client.command.return_value = self._create_response(
                    {"id": "p-1", "name": "renamed"}
                )
                self.module.update_policy(
                    policy_type=policy_type,
                    id="p-1",
                    name="renamed",
                    description=None,
                    settings=None,
                )
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(
                    call[0][0], self.module._OPERATIONS[policy_type]["update"]
                )
                wrapper = self.module._BODY_WRAPPER[policy_type]
                self.assertEqual(call[1]["body"][wrapper][0]["id"], "p-1")

    def test_update_minimal_body_contains_only_id(self):
        """An update with no optional fields produces a body with only the id."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "p-1"}
        )
        self.module.update_policy(
            policy_type="prevention",
            id="p-1",
            name=None,
            description=None,
            settings=None,
        )
        call = self.mock_client.command.call_args_list[0]
        resource = call[1]["body"]["resources"][0]
        self.assertEqual(resource, {"id": "p-1"})

    # ---- Delete ----------------------------------------------------------------

    def test_delete_per_type(self):
        """Delete uses the right op and passes ids via query params, not body."""
        for policy_type in EXPECTED_OPS:
            with self.subTest(policy_type=policy_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = None
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": []},
                }
                self.module.delete_policies(
                    policy_type=policy_type, ids=["p-1", "p-2"]
                )
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(
                    call[0][0], self.module._OPERATIONS[policy_type]["delete"]
                )
                self.assertEqual(call[1]["parameters"]["ids"], ["p-1", "p-2"])
                self.assertNotIn("body", call[1])

    def test_delete_empty_ids(self):
        """Delete with no ids returns a guiding error, no API call."""
        result = self.module.delete_policies(policy_type="firewall", ids=None)
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_delete_invalid_type(self):
        """Delete with an invalid type returns an error, no API call."""
        result = self.module.delete_policies(policy_type="bogus", ids=["p-1"])
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    # ---- Perform action --------------------------------------------------------

    def test_perform_action_rule_group_validity_per_type(self):
        """add-rule-group is valid for prevention/sensor_update/response, rejected for firewall/dc."""
        # prevention/sensor_update/response accept add-rule-group (with a group_id).
        for policy_type, action_op in (
            ("prevention", "performPreventionPoliciesAction"),
            ("sensor_update", "performSensorUpdatePoliciesAction"),
            ("response", "performRTResponsePoliciesAction"),
        ):
            with self.subTest(policy_type=policy_type, expect="accepted"):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": [{"id": "p-1"}]},
                }
                result = self.module.perform_policy_action(
                    policy_type=policy_type,
                    action_name="add-rule-group",
                    ids=["p-1"],
                    group_id="rg-1",
                )
                self.assertNotIn("error", result[0])
                self.assertEqual(self.mock_client.command.call_count, 1)
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(call[0][0], action_op)
                self.assertEqual(
                    call[1]["body"]["action_parameters"],
                    [{"name": "group_id", "value": "rg-1"}],
                )

        # firewall and device_control reject rule-group actions before any API call.
        for policy_type in ("firewall", "device_control"):
            with self.subTest(policy_type=policy_type, expect="rejected"):
                self.mock_client.command.reset_mock()
                result = self.module.perform_policy_action(
                    policy_type=policy_type,
                    action_name="add-rule-group",
                    ids=["p-1"],
                    group_id="rg-1",
                )
                self.assertIn("error", result[0])
                self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_rule_group_requires_group_id(self):
        """add-rule-group without group_id returns a guiding error, no API call.

        Rule-group actions need the same action_parameters group_id payload as
        host-group actions; omitting it must be caught before the API call.
        """
        result = self.module.perform_policy_action(
            policy_type="prevention",
            action_name="add-rule-group",
            ids=["p-1"],
            group_id=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_content_update_override_accepted(self):
        """content_update override actions are accepted and send no action_parameters."""
        for action_name in ("override-allow", "override-pause", "override-revert"):
            with self.subTest(action_name=action_name):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": [{"id": "cu-1"}]},
                }
                result = self.module.perform_policy_action(
                    policy_type="content_update",
                    action_name=action_name,
                    ids=["cu-1"],
                    group_id=None,
                )
                self.assertNotIn("error", result[0])
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(call[0][0], "performContentUpdatePoliciesAction")
                self.assertEqual(call[1]["parameters"]["action_name"], action_name)
                self.assertNotIn("action_parameters", call[1]["body"])

    def test_perform_action_content_update_pin_actions_rejected(self):
        """content_update pin actions are out of scope for v1 and must be rejected.

        set/remove-pinned-content-version require a content-version value the tool
        cannot pass, so they are not in _VALID_ACTIONS and must error with zero calls.
        """
        for action_name in (
            "set-pinned-content-version",
            "remove-pinned-content-version",
        ):
            with self.subTest(action_name=action_name):
                self.mock_client.command.reset_mock()
                result = self.module.perform_policy_action(
                    policy_type="content_update",
                    action_name=action_name,
                    ids=["cu-1"],
                    group_id=None,
                )
                self.assertIn("error", result[0])
                self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_empty_ids(self):
        """perform_policy_action with empty ids returns a guiding error, no API call."""
        result = self.module.perform_policy_action(
            policy_type="prevention",
            action_name="enable",
            ids=[],
            group_id=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_invalid_action(self):
        """An unknown action_name returns a guiding error, no API call."""
        result = self.module.perform_policy_action(
            policy_type="prevention",
            action_name="bogus-action",
            ids=["p-1"],
            group_id=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_enable_omits_action_parameters(self):
        """enable builds a body with ids and no action_parameters."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.perform_policy_action(
            policy_type="prevention",
            action_name="enable",
            ids=["p-1"],
            group_id=None,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "performPreventionPoliciesAction")
        self.assertEqual(call[1]["parameters"]["action_name"], "enable")
        body = call[1]["body"]
        self.assertEqual(body["ids"], ["p-1"])
        self.assertNotIn("action_parameters", body)

    def test_perform_action_add_host_group_requires_group_id(self):
        """add-host-group without group_id returns a guiding error, no API call."""
        result = self.module.perform_policy_action(
            policy_type="firewall",
            action_name="add-host-group",
            ids=["p-1"],
            group_id=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_perform_action_add_host_group_builds_action_parameters(self):
        """add-host-group with group_id builds the group_id action_parameters."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.perform_policy_action(
            policy_type="firewall",
            action_name="add-host-group",
            ids=["p-1"],
            group_id="grp-1",
        )
        call = self.mock_client.command.call_args_list[0]
        body = call[1]["body"]
        self.assertEqual(
            body["action_parameters"], [{"name": "group_id", "value": "grp-1"}]
        )

    def test_perform_action_invalid_type(self):
        """perform_policy_action with an invalid type returns an error, no API call."""
        result = self.module.perform_policy_action(
            policy_type="bogus",
            action_name="enable",
            ids=["p-1"],
            group_id=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    # ---- Set precedence --------------------------------------------------------

    def test_precedence_requires_platform_for_non_content_update(self):
        """Non-content_update precedence requires platform_name (missing -> error)."""
        result = self.module.set_policy_precedence(
            policy_type="prevention",
            ids=["p-1", "p-2"],
            platform_name=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_precedence_content_update_omits_platform_name(self):
        """content_update precedence body must NOT contain platform_name."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.set_policy_precedence(
            policy_type="content_update",
            ids=["p-1", "p-2"],
            platform_name=None,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "setContentUpdatePoliciesPrecedence")
        body = call[1]["body"]
        self.assertEqual(body["ids"], ["p-1", "p-2"])
        self.assertNotIn("platform_name", body)

    def test_precedence_passes_ids_and_platform(self):
        """Non-content_update precedence passes ids and platform_name through."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.set_policy_precedence(
            policy_type="prevention",
            ids=["p-1", "p-2", "p-3"],
            platform_name="Windows",
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "setPreventionPoliciesPrecedence")
        body = call[1]["body"]
        self.assertEqual(body["ids"], ["p-1", "p-2", "p-3"])
        self.assertEqual(body["platform_name"], "Windows")

    def test_precedence_empty_ids(self):
        """Precedence with no ids returns a guiding error, no API call."""
        result = self.module.set_policy_precedence(
            policy_type="content_update",
            ids=[],
            platform_name=None,
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_precedence_invalid_type(self):
        """Precedence with an invalid type returns an error, no API call."""
        result = self.module.set_policy_precedence(
            policy_type="bogus",
            ids=["p-1"],
            platform_name="Windows",
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)
