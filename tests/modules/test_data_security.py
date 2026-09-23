"""
Tests for the Data Security module.
"""

import unittest

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
        """Test registering the 4 generic entity_type-keyed tools."""
        expected_tools = [
            "falcon_search_data_security_entities",
            "falcon_get_data_security_entities",
            "falcon_create_data_security_entity",
            "falcon_update_data_security_entity",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            f"falcon_search_data_security_{e}_fql_guide" for e in self._FQL_GUIDE_ENTITIES
        ] + [
            "falcon_data_security_entity_model",
            "falcon_data_security_behavioral_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_read_tools_are_read_only_and_write_tools_are_not(self):
        """Search/get tools are read-only; create/update tools are not."""
        self.module.register_tools(self.mock_server)
        for call in self.mock_server.add_tool.call_args_list:
            name = call.kwargs.get("name")
            annotations = call.kwargs.get("annotations")
            if name.startswith(("falcon_search_", "falcon_get_")):
                self.assertEqual(annotations, READ_ONLY_ANNOTATIONS, f"{name} should be read-only")
            elif name.startswith("falcon_create_"):
                self.assertFalse(annotations.readOnlyHint, f"{name} must not be read-only")
                self.assertFalse(annotations.idempotentHint, f"{name} create is not idempotent")
            elif name.startswith("falcon_update_"):
                self.assertFalse(annotations.readOnlyHint, f"{name} must not be read-only")
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

    def test_search_web_locations_omits_sort(self):
        """Web location query op does not support sort, so it must not be sent."""
        self.mock_client.command.side_effect = [{"status_code": 200, "body": {"resources": []}}]
        self.module.search_data_security_entities(
            entity_type="web_location", filter=None, limit=100, offset=0, sort="name.asc"
        )
        params = self.mock_client.command.call_args_list[0].kwargs.get("parameters", {})
        self.assertNotIn("sort", params)

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
        """Classification update (else branch: no id query param) wraps in 'resources'
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
        # Distinguishing behavior of the else branch: id is NOT sent as a query param.
        self.assertNotIn("id", call.kwargs.get("parameters") or {})

    def test_update_classification_without_id_errors(self):
        """A classification update (else branch) without an 'id' returns a guiding error."""
        result = self.module.update_data_security_entity(
            entity_type="classification", body={"name": "renamed"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("id", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_update_web_location_wraps_and_sends_id(self):
        """Web location update wraps under 'web_locations' and sends id query param."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": [{"id": "wl-1"}]}}
        ]
        self.module.update_data_security_entity(
            entity_type="web_location", body={"id": "wl-1", "name": "renamed"}
        )
        call = self.mock_client.command.call_args
        self.assertEqual(call.args[0], "entities_web_location_patch_v2")
        self.assertEqual(call.kwargs["parameters"]["id"], "wl-1")
        self.assertEqual(call.kwargs["body"]["web_locations"][0]["name"], "renamed")
        self.assertNotIn("id", call.kwargs["body"]["web_locations"][0])

    def test_update_sensitivity_label_unsupported(self):
        """sensitivity_label does not support update; a guiding error is returned."""
        result = self.module.update_data_security_entity(
            entity_type="sensitivity_label", body={"id": "sl-1"}
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("does not support update", result[0]["error"])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
