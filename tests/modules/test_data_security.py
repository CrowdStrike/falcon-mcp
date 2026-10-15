"""
Tests for the Data Security module.
"""

import unittest
from unittest.mock import patch

from mcp.server.fastmcp.tools import Tool

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.data_security import DataSecurityModule
from tests.modules.utils.test_modules import TestModules


class TestDataSecurityModule(TestModules):
    """Test cases for the Data Security module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DataSecurityModule)

    # FQL-guide resources remain per-entity (unchanged by the tool consolidation).
    _FQL_GUIDE_ENTITIES = [
        "classifications",
        "policies",
        "content_patterns",
        "cloud_applications",
        "enterprise_accounts",
        "web_locations",
        "local_applications",
        "local_application_groups",
        "sensitivity_labels",
        "file_types",
    ]

    def test_register_tools(self):
        """Test registering the generic entity_type-keyed tools and the schema tool."""
        expected_tools = [
            "falcon_search_data_security_entities",
            "falcon_get_data_security_entities",
            "falcon_get_data_security_entity_schema",
            "falcon_create_data_security_entity",
            "falcon_update_data_security_entity",
        ]
        self.assert_tools_registered(expected_tools)

    # Body-guide resources, one per writable entity type.
    _BODY_GUIDE_ENTITIES = [
        "classification",
        "policy",
        "content_pattern",
        "cloud_application",
        "enterprise_account",
        "web_location",
        "local_application",
        "local_application_group",
        "sensitivity_label",
    ]

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = (
            [f"falcon_search_data_security_{e}_fql_guide" for e in self._FQL_GUIDE_ENTITIES]
            + [f"falcon_data_security_{e}_body_guide" for e in self._BODY_GUIDE_ENTITIES]
            + [
                "falcon_data_security_entity_model",
                "falcon_data_security_behavioral_guide",
            ]
        )
        self.assert_resources_registered(expected_resources)

    def test_body_guide_resources_serve_the_schema_tool_guides(self):
        """Each body-guide resource carries the same text the schema tool returns."""
        self.module.register_resources(self.mock_server)
        by_name = {
            call.kwargs["resource"].name: call.kwargs["resource"]
            for call in self.mock_server.add_resource.call_args_list
        }
        for entity_type in self._BODY_GUIDE_ENTITIES:
            resource = by_name[f"falcon_data_security_{entity_type}_body_guide"]
            self.assertEqual(resource.text, self.module._BODY_GUIDES[entity_type], entity_type)
        self.assertEqual(sorted(self.module._BODY_GUIDES), sorted(self._BODY_GUIDE_ENTITIES))

    def test_read_tools_are_read_only_and_write_tools_are_not(self):
        """Search/get tools are read-only; create/update tools are not."""
        self.module.register_tools(self.mock_server)
        for call in self.mock_server.add_tool.call_args_list:
            name = call.kwargs.get("name")
            annotations = call.kwargs.get("annotations")
            if name == "falcon_get_data_security_entity_schema":
                self.assertTrue(annotations.readOnlyHint, f"{name} should be read-only")
                self.assertFalse(annotations.destructiveHint, f"{name} must not be destructive")
                self.assertFalse(annotations.openWorldHint, f"{name} makes no API call")
            elif name.startswith(("falcon_search_", "falcon_get_")):
                self.assertEqual(annotations, READ_ONLY_ANNOTATIONS, f"{name} should be read-only")
            elif name.startswith("falcon_create_"):
                self.assertFalse(annotations.readOnlyHint, f"{name} must not be read-only")
                self.assertTrue(annotations.destructiveHint, f"{name} must be destructive")
                self.assertFalse(annotations.idempotentHint, f"{name} create is not idempotent")
            elif name.startswith("falcon_update_"):
                self.assertFalse(annotations.readOnlyHint, f"{name} must not be read-only")
                self.assertTrue(annotations.destructiveHint, f"{name} must be destructive")
                self.assertTrue(annotations.idempotentHint, f"{name} update is idempotent")
            else:
                self.fail(f"Unexpected tool name: {name}")

    # --- entity_type discriminator validation ---

    def test_search_invalid_entity_type_returns_error(self):
        """An unknown entity_type is rejected before any API call."""
        result = self.module.search_data_security_entities(
            entity_type="bogus", filter=None, limit=100, offset=0, sort=None
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("Invalid entity_type", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_get_invalid_entity_type_returns_error(self):
        """get rejects an unknown entity_type before any API call."""
        result = self.module.get_data_security_entities(entity_type="bogus", ids=["x"])
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_invalid_entity_type_returns_error(self):
        """create rejects an unknown entity_type before any API call."""
        result = self.module.create_data_security_entity(entity_type="bogus", body={})
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_invalid_entity_type_returns_error(self):
        """update rejects an unknown entity_type before any API call."""
        result = self.module.update_data_security_entity(entity_type="bogus", body={})
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # --- Search: two-step / reorder / empty / error (classification) ---

    def test_search_classifications_success(self):
        """Test searching classifications with successful two-step response."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["cls-id-1", "cls-id-2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "cls-id-1",
                        "name": "Credit Card Detection",
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                    {
                        "id": "cls-id-2",
                        "name": "SSN Detection",
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_security_entities(
            entity_type="classification", filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(
            self.mock_client.command.call_args_list[0].args[0], "queries_classification_get_v2"
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1].args[0], "entities_classification_get_v2"
        )
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["name"], "Credit Card Detection")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_classifications_reorders_to_match_sorted_ids(self):
        """When the get step returns classifications out of order, the result is
        reordered to match the sorted ID order from the query step."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cls-id-b", "cls-id-a"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "cls-id-a", "name": "Classification A"},
                    {"id": "cls-id-b", "name": "Classification B"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_security_entities(
            entity_type="classification", filter=None, limit=100, offset=0, sort="created_at.desc"
        )

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "cls-id-b")
        self.assertEqual(result["results"][1]["id"], "cls-id-a")

    def test_search_classifications_empty_results(self):
        """Test that empty search returns clean empty response."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        result = self.module.search_data_security_entities(
            entity_type="classification",
            filter="name:~'nonexistent'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])
        self.assertEqual(result["filter_used"], "name:~'nonexistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_classifications_error_response(self):
        """Test that an API error returns FQL guide with error hint."""
        error_response = {
            "status_code": 400,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "invalid filter key: foo"}],
            },
        }
        self.mock_client.command.side_effect = [error_response]

        result = self.module.search_data_security_entities(
            entity_type="classification", filter="foo:'bar'", limit=100, offset=0, sort=None
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])

    def test_search_classifications_hydration_failure(self):
        """When the query step succeeds but the get (hydration) step fails,
        the error is returned wrapped in a list."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["cls-id-1"]},
        }
        get_response = {
            "status_code": 500,
            "body": {
                "resources": [],
                "errors": [{"code": 500, "message": "internal server error"}],
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_security_entities(
            entity_type="classification", filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    # --- Search: policy platform_name handling ---

    def test_search_policies_success(self):
        """Test searching policies with platform_name and two-step response."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["pol-id-1"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "pol-id-1",
                        "name": "Windows Data Security Policy",
                        "platform_name": "win",
                        "is_enabled": True,
                    }
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_data_security_entities(
            entity_type="policy", platform_name="win", filter=None, limit=100, offset=0, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["platform_name"], "win")
        self.assertEqual(result["pagination"]["total"], 1)

    def test_search_policies_passes_platform_name(self):
        """Test that platform_name is sent to the query API."""
        query_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [query_response]

        self.module.search_data_security_entities(
            entity_type="policy", platform_name="mac", filter=None, limit=100, offset=0, sort=None
        )

        call_args = self.mock_client.command.call_args
        params = call_args.kwargs.get("parameters") or call_args[1].get("parameters", {})
        self.assertEqual(params.get("platform_name"), "mac")

    def test_search_policies_without_platform_name_errors(self):
        """Searching policies without platform_name returns a guiding error."""
        result = self.module.search_data_security_entities(
            entity_type="policy", platform_name=None, filter=None, limit=100, offset=0, sort=None
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("platform_name", result[0]["error"])
        self.mock_client.command.assert_not_called()

    # --- Search: representative op-id dispatch + sort gating ---

    def test_search_cloud_applications_two_step(self):
        """Cloud application search hits query then get op."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["ca-1"]}},
            {"status_code": 200, "body": {"resources": [{"id": "ca-1", "name": "Box"}]}},
        ]
        result = self.module.search_data_security_entities(
            entity_type="cloud_application", filter=None, limit=100, offset=0, sort=None
        )
        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(
            self.mock_client.command.call_args_list[0].args[0],
            "queries_cloud_application_get_v2",
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1].args[0],
            "entities_cloud_application_get",
        )
        self.assertIn("results", result)
        self.assertEqual(result["results"][0]["name"], "Box")

    def test_search_forwards_sort_for_every_entity_type(self):
        """Sort reaches the query op for every type, including the ones whose SDK
        spec omits it (web locations and local applications accept and honor it)."""
        for entity_type in DataSecurityModule._OPERATIONS:
            with self.subTest(entity_type=entity_type):
                self.mock_client.reset_mock()
                self.mock_client.command.side_effect = [
                    {"status_code": 200, "body": {"resources": []}}
                ]
                self.module.search_data_security_entities(
                    entity_type=entity_type,
                    filter=None,
                    limit=100,
                    offset=0,
                    sort="name.desc",
                    platform_name="win",
                )
                params = self.mock_client.command.call_args_list[0].kwargs["parameters"]
                self.assertEqual(params["sort"], "name.desc")

    # --- Get by IDs ---

    def test_get_content_patterns_uses_params(self):
        """Get-by-id sends IDs as query parameters (GET), not body."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cp-1"}]}}
        ]
        result = self.module.get_data_security_entities(
            entity_type="content_pattern", ids=["cp-1"]
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_content_pattern_get")
        self.assertIn("parameters", call.kwargs)
        self.assertNotIn("body", call.kwargs)
        self.assertEqual(call.kwargs["parameters"]["ids"], ["cp-1"])
        self.assertEqual(result[0]["id"], "cp-1")

    def test_get_error_is_wrapped_in_a_list(self):
        """Get returns errors as [error], the same shape as search, create and update."""
        self.mock_client.command.side_effect = [
            {"status_code": 404, "body": {"errors": [{"message": "not found"}]}}
        ]
        result = self.module.get_data_security_entities(entity_type="policy", ids=["missing"])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # --- Create: body wrapping is the critical contract ---

    def test_create_content_pattern_bare_body(self):
        """Content pattern create sends a bare object body."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cp-new"}]}}
        ]
        self.module.create_data_security_entity(
            entity_type="content_pattern",
            body={
                "name": "SSN",
                "category": "PII",
                "description": "d",
                "example": "123-45-6789",
                "regexes": [r"\d{3}-\d{2}-\d{4}"],
                "min_match_threshold": 1,
                "region": "ALL",
            },
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_content_pattern_create")
        body = call.kwargs["body"]
        self.assertEqual(body["name"], "SSN")
        self.assertNotIn("resources", body)
        self.assertNotIn("web_locations", body)

    def test_create_web_location_wraps_in_web_locations(self):
        """Web location create wraps the object under the 'web_locations' key."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "wl-new"}]}}
        ]
        self.module.create_data_security_entity(
            entity_type="web_location",
            body={
                "name": "Corp Drive",
                "application_id": "ca-1",
                "location_type": "custom",
                "type": "custom",
            },
        )
        body = self.mock_client.command.call_args.kwargs["body"]
        self.assertIn("web_locations", body)
        self.assertEqual(body["web_locations"][0]["name"], "Corp Drive")

    def test_create_classification_wraps_in_resources(self):
        """Classification create wraps the object under the 'resources' key."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cls-new"}]}}
        ]
        self.module.create_data_security_entity(
            entity_type="classification",
            body={"name": "PII", "classification_properties": {"protection_mode": "monitor"}},
        )
        body = self.mock_client.command.call_args.kwargs["body"]
        self.assertIn("resources", body)
        self.assertEqual(body["resources"][0]["name"], "PII")

    def test_create_policy_sends_platform_name_query_param(self):
        """Policy create wraps in 'resources' and passes platform_name as a query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "pol-new"}]}}
        ]
        self.module.create_data_security_entity(
            entity_type="policy", platform_name="win", body={"name": "P", "is_enabled": False}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_policy_post_v2")
        self.assertEqual(call.kwargs["parameters"]["platform_name"], "win")
        self.assertIn("resources", call.kwargs["body"])

    def test_create_policy_without_platform_name_errors(self):
        """Creating a policy without platform_name returns a guiding error."""
        result = self.module.create_data_security_entity(
            entity_type="policy", platform_name=None, body={"name": "P"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("platform_name", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_create_file_type_is_read_only(self):
        """file_type does not support create; a guiding error is returned."""
        result = self.module.create_data_security_entity(entity_type="file_type", body={})
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("read-only", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_create_error_returns_wrapped_error(self):
        """A failed create returns the error wrapped in a list."""
        self.mock_client.command.side_effect = [
            {"status_code": 400, "body": {"errors": [{"code": 400, "message": "bad"}]}}
        ]
        result = self.module.create_data_security_entity(
            entity_type="content_pattern",
            body={
                "name": "x",
                "category": "PII",
                "description": "d",
                "example": "e",
                "regexes": ["r"],
                "min_match_threshold": 1,
                "region": "ALL",
            },
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    # --- Update ---

    def test_update_content_pattern_sends_id_query_param(self):
        """Content pattern update pulls id from the body and sends it as a query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cp-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="content_pattern", body={"id": "cp-1", "name": "new name"}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_content_pattern_patch")
        self.assertEqual(call.kwargs["parameters"]["id"], "cp-1")
        self.assertEqual(call.kwargs["body"]["name"], "new name")
        self.assertNotIn("id", call.kwargs["body"])

    def test_update_flat_entity_without_id_errors(self):
        """A flat-entity update without an 'id' in the body returns a guiding error."""
        result = self.module.update_data_security_entity(
            entity_type="content_pattern", body={"name": "new name"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("id", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_update_policy_sends_platform_name_and_resources(self):
        """Policy update wraps in 'resources' and passes platform_name as a query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "pol-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="policy", platform_name="mac", body={"id": "pol-1", "is_enabled": True}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_policy_patch_v2")
        self.assertEqual(call.kwargs["parameters"]["platform_name"], "mac")
        self.assertEqual(call.kwargs["body"]["resources"][0]["id"], "pol-1")

    def test_update_classification_wraps_in_resources_with_id_in_body(self):
        """Classification update wraps in 'resources'
        and keeps the id inside the body rather than sending it as a query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cls-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="classification", body={"id": "cls-1", "name": "renamed"}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_classification_patch_v2")
        self.assertEqual(call.kwargs["body"]["resources"][0]["id"], "cls-1")
        self.assertEqual(call.kwargs["body"]["resources"][0]["name"], "renamed")
        # The id stays in the body; it is NOT sent as a query param.
        self.assertNotIn("id", call.kwargs.get("parameters") or {})

    def test_update_classification_without_id_errors(self):
        """A classification update without an 'id' returns a guiding error."""
        result = self.module.update_data_security_entity(
            entity_type="classification", body={"name": "renamed"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("id", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_update_with_only_id_errors_without_calling_the_api(self):
        """An update body holding nothing but the id returns a guiding error for every
        updatable type instead of sending an empty PATCH."""
        for entity_type, ops in self.module._OPERATIONS.items():
            if ops["update"] is None:
                continue
            self.mock_client.command.reset_mock()
            result = self.module.update_data_security_entity(
                entity_type=entity_type, body={"id": "x-1"}, platform_name="win"
            )
            self.assertIsInstance(result, list, entity_type)
            self.assertIn("at least one field", result[0]["error"], entity_type)
            self.mock_client.command.assert_not_called()

    def test_update_web_location_sends_flat_body_and_id(self):
        """Web location update sends a flat body (create's 'web_locations' wrapper is
        rejected by PATCH) with the id as a query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "wl-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="web_location", body={"id": "wl-1", "name": "renamed"}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_web_location_patch_v2")
        self.assertEqual(call.kwargs["parameters"]["id"], "wl-1")
        self.assertEqual(call.kwargs["body"], {"name": "renamed"})

    # --- update_merge: whole-entity replace types ---

    _LOCAL_APP = {
        "id": "la-1",
        "cid": "cid-1",
        "name": "Excel",
        "executable_name": "excel.exe",
        "group_ids": ["grp-1"],
        "apply_rules_for_children_processes": True,
        "enable_rename_detection": False,
        "emit_rule_matched_events_only": False,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "deleted": False,
        "deleted_at": "0001-01-01T00:00:00Z",
    }

    def test_update_local_application_merges_onto_current_entity(self):
        """A partial local_application update fetches the entity first and sends the
        full object, so fields the caller omitted are not wiped."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [dict(self._LOCAL_APP)]}},
            {"status_code": 200, "body": {"resources": [{"id": "la-1"}]}},
        ]
        self.module.update_data_security_entity(
            entity_type="local_application",
            body={"id": "la-1", "enable_rename_detection": True},
        )
        get_call, patch_call = self.mock_client.command.call_args_list
        self.assertEqual(get_call.args[0], "entities_local_application_get")
        self.assertEqual(get_call.kwargs["parameters"]["ids"], ["la-1"])
        self.assertEqual(patch_call.args[0], "entities_local_application_patch")
        self.assertEqual(patch_call.kwargs["parameters"], {"id": "la-1"})
        self.assertEqual(
            patch_call.kwargs["body"],
            {
                "name": "Excel",
                "executable_name": "excel.exe",
                "group_ids": ["grp-1"],
                "apply_rules_for_children_processes": True,
                "enable_rename_detection": True,
                "emit_rule_matched_events_only": False,
            },
        )

    def test_update_local_application_group_caller_values_win(self):
        """Caller-supplied fields override the fetched values; untouched ones survive."""
        current = {
            "id": "grp-1",
            "cid": "cid-1",
            "name": "Office",
            "description": "orig",
            "local_application_ids": ["la-1", "la-2"],
            "created_at": "x",
            "updated_at": "x",
            "deleted": False,
            "deleted_at": "x",
        }
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [current]}},
            {"status_code": 200, "body": {"resources": [{"id": "grp-1"}]}},
        ]
        self.module.update_data_security_entity(
            entity_type="local_application_group",
            body={"id": "grp-1", "local_application_ids": ["la-3"]},
        )
        patch_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(
            patch_call.kwargs["body"],
            {"name": "Office", "description": "orig", "local_application_ids": ["la-3"]},
        )

    def test_update_merge_not_found_does_not_patch(self):
        """When the entity to merge onto does not exist, no PATCH is sent."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": []}},
        ]
        result = self.module.update_data_security_entity(
            entity_type="local_application", body={"id": "missing", "name": "x"}
        )
        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("error", result[0])
        self.assertIn("missing", result[0]["error"])

    def test_update_merge_get_error_does_not_patch(self):
        """A failed fetch is returned as an error and no PATCH is sent."""
        self.mock_client.command.side_effect = [
            {"status_code": 403, "body": {"errors": [{"message": "access denied"}]}},
        ]
        result = self.module.update_data_security_entity(
            entity_type="local_application_group", body={"id": "grp-1", "name": "x"}
        )
        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(
            self.mock_client.command.call_args.args[0], "entities_local_application_group_get"
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_update_partial_merge_types_do_not_fetch(self):
        """Types whose PATCH merges server-side send only the caller's fields."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "app-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="cloud_application", body={"id": "app-1", "description": "d"}
        )
        self.assertEqual(self.mock_client.command.call_count, 1)
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_cloud_application_patch")
        self.assertEqual(call.kwargs["body"], {"description": "d"})

    def test_update_sensitivity_label_unsupported(self):
        """sensitivity_label does not support update; a guiding error is returned."""
        result = self.module.update_data_security_entity(
            entity_type="sensitivity_label", body={"id": "sl-1"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("does not support update", result[0]["error"])
        self.mock_client.command.assert_not_called()

    # --- Tool schema enums ---

    def _tool_schema(self, method) -> dict:
        return Tool.from_function(method).parameters["properties"]

    @staticmethod
    def _enum(prop: dict) -> list:
        """The enum of a Literal parameter, unwrapping an `X | None` anyOf."""
        if "enum" in prop:
            return prop["enum"]
        return next(p["enum"] for p in prop["anyOf"] if "enum" in p)

    def test_entity_type_enums_match_the_dispatch_table(self):
        """Read tools accept every entity type; create leaves out read-only file_type and
        update also leaves out create-only sensitivity_label."""
        all_types = sorted(self.module._OPERATIONS)
        writable = sorted(t for t, ops in self.module._OPERATIONS.items() if ops["create"])
        updatable = sorted(t for t, ops in self.module._OPERATIONS.items() if ops["update"])
        for method, expected in [
            (self.module.search_data_security_entities, all_types),
            (self.module.get_data_security_entities, all_types),
            (self.module.create_data_security_entity, writable),
            (self.module.update_data_security_entity, updatable),
        ]:
            with self.subTest(tool=method.__name__):
                self.assertEqual(sorted(self._enum(self._tool_schema(method)["entity_type"])), expected)
        schema_items = self._tool_schema(self.module.get_data_security_entity_schema)["entity_types"]
        self.assertEqual(sorted(schema_items["items"]["enum"]), writable)

    def test_platform_name_and_deleted_enums(self):
        """platform_name and deleted are enums, so bad values fail before any API call."""
        for method in (
            self.module.search_data_security_entities,
            self.module.create_data_security_entity,
            self.module.update_data_security_entity,
        ):
            with self.subTest(tool=method.__name__):
                self.assertEqual(self._enum(self._tool_schema(method)["platform_name"]), ["win", "mac"])
        search = self._tool_schema(self.module.search_data_security_entities)
        self.assertEqual(search["deleted"]["enum"], ["exclude", "include", "only"])
        self.assertEqual(search["deleted"]["default"], "exclude")

    def test_search_limit_and_get_ids_are_capped_at_100(self):
        """Search hydrates every queried ID through get, so both stop at 100."""
        search = self._tool_schema(self.module.search_data_security_entities)
        self.assertEqual(search["limit"]["maximum"], 100)
        self.assertEqual(search["limit"]["default"], 50)
        ids = self._tool_schema(self.module.get_data_security_entities)["ids"]
        self.assertEqual(ids["minItems"], 1)
        self.assertEqual(ids["maxItems"], 100)

    # --- Search: deleted argument ---

    def _search_filter_sent(self, entity_type: str, **kwargs) -> str | None:
        self.mock_client.reset_mock()
        self.mock_client.command.side_effect = [{"status_code": 200, "body": {"resources": []}}]
        result = self.module.search_data_security_entities(
            entity_type=entity_type, limit=50, offset=0, sort=None, **kwargs
        )
        sent = self.mock_client.command.call_args_list[0].kwargs["parameters"].get("filter")
        self.assertEqual(result.get("filter_used"), sent)
        return sent

    def test_search_deleted_argument_on_soft_delete_types(self):
        """exclude (the default) and only add a deleted clause; include sends the filter as-is."""
        cases = [
            ({"filter": None}, "deleted:false"),
            ({"filter": None, "deleted": "exclude"}, "deleted:false"),
            ({"filter": "type:'custom'"}, "deleted:false+(type:'custom')"),
            ({"filter": "type:'custom',name:~'x'"}, "deleted:false+(type:'custom',name:~'x')"),
            ({"filter": None, "deleted": "only"}, "deleted:true"),
            ({"filter": "type:'custom'", "deleted": "only"}, "deleted:true+(type:'custom')"),
            ({"filter": None, "deleted": "include"}, None),
            ({"filter": "type:'custom'", "deleted": "include"}, "type:'custom'"),
        ]
        for kwargs, expected in cases:
            with self.subTest(**kwargs):
                self.assertEqual(self._search_filter_sent("content_pattern", **kwargs), expected)

    def test_search_deleted_on_types_without_soft_delete(self):
        """classification, policy and file_type keep the caller's filter and reject 'only'."""
        for entity_type in ("classification", "policy", "file_type"):
            with self.subTest(entity_type=entity_type):
                for deleted in ("exclude", "include"):
                    self.assertEqual(
                        self._search_filter_sent(
                            entity_type, filter="name:~'x'", deleted=deleted, platform_name="win"
                        ),
                        "name:~'x'",
                    )
                self.mock_client.reset_mock()
                result = self.module.search_data_security_entities(
                    entity_type=entity_type,
                    filter=None,
                    limit=50,
                    offset=0,
                    sort=None,
                    platform_name="win",
                    deleted="only",
                )
                self.assertIn("has no deleted entities", result[0]["error"])
                self.mock_client.command.assert_not_called()

    def test_soft_delete_matches_the_fql_guides(self):
        """A type hides deleted entities exactly when its FQL guide documents a deleted field."""
        for entity_type, ops in self.module._OPERATIONS.items():
            with self.subTest(entity_type=entity_type):
                self.assertEqual(
                    ops["soft_delete"], "|deleted|" in self.module._FQL_DOCS[entity_type]
                )

    def test_search_fql_error_echoes_effective_filter(self):
        """An FQL error reports the filter the API actually received."""
        self.mock_client.command.side_effect = [
            {"status_code": 400, "body": {"errors": [{"code": 400, "message": "bad filter"}]}}
        ]
        result = self.module.search_data_security_entities(
            entity_type="web_location", filter="foo:'x'", limit=50, offset=0, sort=None
        )
        self.assertEqual(result["filter_used"], "deleted:false+(foo:'x')")
        self.assertIn("fql_guide", result)

    # --- Partial and errors-only 2xx responses ---

    def test_get_partial_errors_are_warnings(self):
        """A 2xx with resources and per-ID errors keeps both."""
        missing = {"code": 404, "id": "cp-missing", "message": "Not Found"}
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {"resources": [{"id": "cp-1"}], "errors": [missing]},
            }
        ]
        result = self.module.get_data_security_entities(
            entity_type="content_pattern", ids=["cp-1", "cp-missing"]
        )
        self.assertEqual(result, {"results": [{"id": "cp-1"}], "_warnings": [missing]})

    def test_search_partial_errors_are_warnings(self):
        """A partial hydration keeps the envelope and adds the errors as _warnings."""
        missing = {"code": 404, "id": "cls-2", "message": "Not Found"}
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["cls-1", "cls-2"],
                    "meta": {"pagination": {"offset": 0, "limit": 50, "total": 2}},
                },
            },
            {"status_code": 200, "body": {"resources": [{"id": "cls-1"}], "errors": [missing]}},
        ]
        result = self.module.search_data_security_entities(
            entity_type="classification", filter=None, limit=50, offset=0, sort=None
        )
        self.assertEqual(result["results"], [{"id": "cls-1"}])
        self.assertEqual(result["pagination"]["total"], 2)
        self.assertEqual(result["_warnings"], [missing])

    def test_empty_errors_list_leaves_the_result_unchanged(self):
        """`errors: []` is not a failure."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "cp-1"}], "errors": []}}
        ]
        result = self.module.get_data_security_entities(entity_type="content_pattern", ids=["cp-1"])
        self.assertEqual(result, [{"id": "cp-1"}])

    def test_get_errors_without_resources_is_an_error(self):
        """A 2xx carrying only errors fails, with the status taken from the error code."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {"resources": [], "errors": [{"code": 404, "message": "Not Found"}]},
            }
        ]
        result = self.module.get_data_security_entities(entity_type="policy", ids=["missing"])
        self.assertIsInstance(result, list)
        self.assertIn("Not Found", result[0]["error"])
        self.assertEqual(result[0]["details"]["status_code"], 404)
        self.assertNotIn("may have been applied", result[0]["error"])

    def test_search_hydration_errors_without_resources_is_an_error(self):
        """When every hydrated ID fails, search returns an error rather than empty results."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["cls-1"]}},
            {"status_code": 200, "body": {"errors": [{"code": 500, "message": "boom"}]}},
        ]
        result = self.module.search_data_security_entities(
            entity_type="classification", filter=None, limit=50, offset=0, sort=None
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_write_errors_without_resources_may_have_been_applied(self):
        """A write that failed with a server error says to verify before retrying."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"errors": [{"code": 500, "message": "boom"}]}}
        ]
        result = self.module.create_data_security_entity(
            entity_type="cloud_application", body={"name": "x", "urls": []}
        )
        self.assertIsInstance(result, list)
        self.assertIn("may have been applied", result[0]["error"])
        self.assertNotIn("body_guide", result[0])

    def test_may_have_applied_follows_the_status_not_the_path(self):
        """Server errors and missing statuses warn on either path; clean 4xx do not."""
        cases = [
            ({"status_code": 500, "body": {"errors": [{"message": "boom"}]}}, True),
            ({"status_code": 504, "body": {}}, True),
            ({"body": {}}, True),
            ({"status_code": 404, "body": {"errors": [{"message": "no"}]}}, False),
            ({"status_code": 200, "body": {"errors": [{"code": 403, "message": "no"}]}}, False),
            ({"status_code": 200, "body": {"errors": [{"code": 409, "message": "dup"}]}}, False),
        ]
        for response, warns in cases:
            with self.subTest(response=response):
                self.mock_client.command.side_effect = [response]
                result = self.module.create_data_security_entity(
                    entity_type="cloud_application", body={"name": "x", "urls": []}
                )
                self.assertEqual("may have been applied" in result[0]["error"], warns)

    def test_rejected_write_does_not_blame_the_filter(self):
        """A 400 on a write uses body wording, not the shared FQL-filter advice."""
        for response in (
            {"status_code": 400, "body": {"errors": [{"message": "bad name"}]}},
            {"status_code": 200, "body": {"errors": [{"code": 400, "message": "bad name"}]}},
        ):
            with self.subTest(response=response):
                self.mock_client.command.side_effect = [response]
                result = self.module.create_data_security_entity(
                    entity_type="classification", body={"name": "x"}
                )
                self.assertIn("The API rejected the request body. API said: bad name", result[0]["error"])
                self.assertNotIn("filter syntax", result[0]["error"])

    def test_search_rejects_a_deleted_term_in_the_filter(self):
        """With exclude/only, a caller's own deleted term could only narrow to nothing."""
        for deleted in ("exclude", "only"):
            with self.subTest(deleted=deleted):
                result = self.module.search_data_security_entities(
                    entity_type="content_pattern",
                    filter="name:~'x'+deleted:true",
                    limit=50,
                    offset=0,
                    sort=None,
                    deleted=deleted,
                )
                self.assertIn("set the deleted argument", result[0]["error"])
        self.mock_client.command.assert_not_called()
        # 'include' passes the caller's filter through untouched, deleted term and all.
        self.assertEqual(
            self._search_filter_sent("content_pattern", filter="deleted:true", deleted="include"),
            "deleted:true",
        )
        # A field that merely ends in "deleted" is not the deleted field.
        self.assertEqual(
            self._search_filter_sent("content_pattern", filter="is_deleted:true"),
            "deleted:false+(is_deleted:true)",
        )
        # Nor is the word inside a quoted value.
        self.assertEqual(
            self._search_filter_sent("content_pattern", filter="name:~'deleted: old'"),
            "deleted:false+(name:~'deleted: old')",
        )

    def test_write_errors_without_code_report_a_failed_2xx(self):
        """With no error code to go by, the error says the 2xx did not succeed."""
        self.mock_client.command.side_effect = [
            {"status_code": 201, "body": {"errors": [{"message": "something failed"}]}}
        ]
        result = self.module.create_data_security_entity(
            entity_type="cloud_application", body={"name": "x", "urls": []}
        )
        self.assertIn("HTTP 201 but the request did not succeed", result[0]["error"])
        self.assertIn("something failed", result[0]["error"])
        self.assertIn("may have been applied", result[0]["error"])

    def test_write_partial_errors_are_warnings(self):
        """A write that returns its entity next to errors keeps both."""
        warning = {"code": 409, "message": "partially applied"}
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "ca-1"}], "errors": [warning]}}
        ]
        result = self.module.create_data_security_entity(
            entity_type="cloud_application", body={"name": "x", "urls": []}
        )
        self.assertEqual(result, {"results": [{"id": "ca-1"}], "_warnings": [warning]})

    # --- Empty write success ---

    def test_empty_create_success_is_acknowledged(self):
        """A create that succeeds with no entity is acknowledged, not reported as empty."""
        for response in (
            {"status_code": 204, "body": {}},
            {"status_code": 201, "body": {"resources": []}},
        ):
            with self.subTest(status=response["status_code"]):
                self.mock_client.command.side_effect = [response]
                result = self.module.create_data_security_entity(
                    entity_type="cloud_application", body={"name": "x", "urls": []}
                )
                self.assertEqual(result["status"], "created")
                self.assertEqual(result["entity_type"], "cloud_application")
                self.assertNotIn("id", result)
                self.assertIn("Do not retry", result["message"])

    def test_empty_update_success_is_acknowledged(self):
        """An update that succeeds with no entity is acknowledged with its id."""
        self.mock_client.command.side_effect = [{"status_code": 204, "body": {}}]
        result = self.module.update_data_security_entity(
            entity_type="content_pattern", body={"id": "cp-1", "name": "renamed"}
        )
        self.assertEqual(result["status"], "updated")
        self.assertEqual(result["id"], "cp-1")
        self.assertIn("falcon_get_data_security_entities", result["message"])

    def test_empty_get_stays_an_empty_list(self):
        """Reads are not acknowledged: an empty get is just empty."""
        self.mock_client.command.side_effect = [{"status_code": 200, "body": {"resources": []}}]
        result = self.module.get_data_security_entities(entity_type="content_pattern", ids=["x"])
        self.assertEqual(result, [])

    def test_create_with_empty_body_is_rejected(self):
        """An empty create body is rejected before any API call."""
        result = self.module.create_data_security_entity(entity_type="cloud_application", body={})
        self.assertIn("body must not be empty", result[0]["error"])
        self.mock_client.command.assert_not_called()

    # --- Body guide on rejected writes ---

    def test_rejected_write_includes_the_body_guide(self):
        """A 400/422 on create or update returns the entity's body guide and a hint."""
        cases = [
            ("create", 400, {"status_code": 400, "body": {"errors": [{"code": 400, "message": "bad"}]}}),
            ("create", 422, {"status_code": 422, "body": {"errors": [{"message": "bad"}]}}),
            ("create", 422, {"status_code": 200, "body": {"errors": [{"code": 422, "message": "bad"}]}}),
            ("update", 400, {"status_code": 400, "body": {"errors": [{"message": "bad"}]}}),
        ]
        for verb, status, response in cases:
            with self.subTest(verb=verb, response=response):
                self.mock_client.command.side_effect = [response]
                if verb == "create":
                    result = self.module.create_data_security_entity(
                        entity_type="classification", body={"name": "x"}
                    )
                else:
                    result = self.module.update_data_security_entity(
                        entity_type="classification", body={"id": "cls-1", "name": "x"}
                    )
                error = result[0]
                self.assertEqual(error["body_guide"], self.module._BODY_GUIDES["classification"])
                self.assertIn("Rebuild it using body_guide", error["hint"])
                self.assertEqual(error["details"]["status_code"], status)
                self.assertNotIn("may have been applied", error["error"])

    def test_other_write_failures_have_no_body_guide(self):
        """Statuses other than 400/422 would not be fixed by the guide, so it is left out."""
        for status in (403, 404, 409, 500):
            with self.subTest(status=status):
                self.mock_client.command.side_effect = [
                    {"status_code": status, "body": {"errors": [{"message": "no"}]}}
                ]
                result = self.module.create_data_security_entity(
                    entity_type="classification", body={"name": "x"}
                )
                self.assertIn("error", result[0])
                self.assertNotIn("body_guide", result[0])

    def test_failed_merge_fetch_has_no_body_guide(self):
        """A 400 from the update's pre-fetch is a read failure, not a rejected body."""
        self.mock_client.command.side_effect = [
            {"status_code": 400, "body": {"errors": [{"message": "bad id"}]}}
        ]
        result = self.module.update_data_security_entity(
            entity_type="local_application", body={"id": "la-1", "name": "x"}
        )
        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("error", result[0])
        self.assertNotIn("body_guide", result[0])

    def test_read_failures_have_no_body_guide(self):
        """Gets and searches never carry a body guide."""
        self.mock_client.command.side_effect = [
            {"status_code": 400, "body": {"errors": [{"message": "bad"}]}}
        ]
        result = self.module.get_data_security_entities(entity_type="classification", ids=["x"])
        self.assertIn("error", result[0])
        self.assertNotIn("body_guide", result[0])

    # --- Schema tool ---

    def test_schema_returns_the_body_guides(self):
        """The schema tool returns one guide per type, in order, without calling the API."""
        result = self.module.get_data_security_entity_schema(
            entity_types=["policy", "classification", "policy"]
        )
        self.assertEqual(
            [s["entity_type"] for s in result["schemas"]], ["policy", "classification"]
        )
        self.assertEqual(result["schemas"][0]["body_guide"], self.module._BODY_GUIDES["policy"])
        self.assertIn("a list you send replaces the stored list", result["hint"])
        self.mock_client.command.assert_not_called()

    def test_schema_rejects_unknown_read_only_and_empty(self):
        """Unknown types, read-only file_type and an empty list are rejected."""
        for entity_types, message in [
            (["bogus"], "Invalid entity_type"),
            (["classification", "file_type"], "read-only and has no body"),
            ([], "must not be empty"),
        ]:
            with self.subTest(entity_types=entity_types):
                result = self.module.get_data_security_entity_schema(entity_types=entity_types)
                self.assertIsInstance(result, list)
                self.assertIn(message, result[0]["error"])
        self.mock_client.command.assert_not_called()

    # --- Get: id handling ---

    def test_get_deduplicates_ids_keeping_order(self):
        """Duplicate IDs are dropped before the call; first-seen order is kept."""
        self.mock_client.command.side_effect = [{"status_code": 200, "body": {"resources": []}}]
        self.module.get_data_security_entities(entity_type="content_pattern", ids=["b", "a", "b"])
        self.assertEqual(self.mock_client.command.call_args.kwargs["parameters"]["ids"], ["b", "a"])

    def test_get_rejects_empty_and_more_than_100_ids(self):
        """Out-of-range id lists are rejected before any API call."""
        for ids in ([], [f"id-{i}" for i in range(101)]):
            with self.subTest(count=len(ids)):
                result = self.module.get_data_security_entities(
                    entity_type="content_pattern", ids=ids
                )
                self.assertIn("between 1 and 100", result[0]["error"])
        self.mock_client.command.assert_not_called()

    # --- Update hardening ---

    def test_update_rejects_a_non_string_id(self):
        """The id must be a non-empty string; anything else is rejected before any call."""
        for bad_id in (123, "", None, ["x"]):
            with self.subTest(id=bad_id):
                result = self.module.update_data_security_entity(
                    entity_type="content_pattern", body={"id": bad_id, "name": "x"}
                )
                self.assertIn("non-empty string", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_update_merge_uses_the_matching_record(self):
        """The merge overlays onto the fetched record whose id matches, not the first one."""
        other = {**self._LOCAL_APP, "id": "la-other", "name": "Other"}
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [other, dict(self._LOCAL_APP)]}},
            {"status_code": 200, "body": {"resources": [{"id": "la-1"}]}},
        ]
        self.module.update_data_security_entity(
            entity_type="local_application", body={"id": "la-1", "enable_rename_detection": True}
        )
        self.assertEqual(self.mock_client.command.call_args.kwargs["body"]["name"], "Excel")

    def test_update_merge_refuses_unusable_records(self):
        """A deleted record, or only records with another id, are not patched."""
        for resources, message in [
            ([{**self._LOCAL_APP, "deleted": True}], "is deleted"),
            ([{**self._LOCAL_APP, "id": "la-other"}], "No local_application found"),
        ]:
            with self.subTest(message=message):
                self.mock_client.reset_mock()
                self.mock_client.command.side_effect = [
                    {"status_code": 200, "body": {"resources": resources}}
                ]
                result = self.module.update_data_security_entity(
                    entity_type="local_application", body={"id": "la-1", "name": "x"}
                )
                self.assertEqual(self.mock_client.command.call_count, 1)
                self.assertIn(message, result[0]["error"])

    def test_update_merge_is_independent_of_id_in_query(self):
        """A merge type that keeps its id in the body still merges and keeps the caller's id."""
        ops = dict(self.module._OPERATIONS["classification"], update_merge=True)
        with patch.dict(self.module._OPERATIONS, {"classification": ops}):
            self.mock_client.command.side_effect = [
                {
                    "status_code": 200,
                    "body": {
                        "resources": [
                            {"id": "cls-1", "cid": "c", "created_at": "t", "name": "old", "x": 1}
                        ]
                    },
                },
                {"status_code": 200, "body": {"resources": [{"id": "cls-1"}]}},
            ]
            self.module.update_data_security_entity(
                entity_type="classification", body={"id": "cls-1", "name": "new"}
            )
        self.assertEqual(
            self.mock_client.command.call_args.kwargs["body"],
            {"resources": [{"x": 1, "id": "cls-1", "name": "new"}]},
        )

    def test_write_body_is_sent_verbatim(self):
        """Null and false values in a flat body reach the API unchanged."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "ca-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="cloud_application",
            body={"id": "ca-1", "description": None, "flag": False},
        )
        self.assertEqual(
            self.mock_client.command.call_args.kwargs["body"], {"description": None, "flag": False}
        )


if __name__ == "__main__":
    unittest.main()
