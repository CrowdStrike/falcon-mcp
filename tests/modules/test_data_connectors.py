"""Tests for the Data Connectors module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.data_connectors import DataConnectorsModule
from tests.modules.utils.test_modules import TestModules


class TestDataConnectorsModule(TestModules):
    """Test cases for the Data Connectors module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DataConnectorsModule)

    # -------------------------------------------------------------------------
    # Registration Tests
    # -------------------------------------------------------------------------

    def test_register_tools(self):
        """Test that all 11 tools are registered."""
        expected_tools = [
            "falcon_search_data_connectors",
            "falcon_search_data_connections",
            "falcon_get_data_connection",
            "falcon_create_data_connection",
            "falcon_manage_data_connection",
            "falcon_delete_data_connection",
            "falcon_regenerate_data_connection_token",
            "falcon_list_connector_configs",
            "falcon_create_connector_config",
            "falcon_update_connector_config",
            "falcon_delete_connector_configs",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test that all 4 resources are registered."""
        expected_resources = [
            "falcon_search_data_connections_fql_guide",
            "falcon_search_data_connectors_fql_guide",
            "falcon_data_connectors_data_source_mapping_guide",
            "falcon_data_connectors_troubleshooting_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # -------------------------------------------------------------------------
    # Annotation Tests
    # -------------------------------------------------------------------------

    def test_read_only_tools_have_default_annotations(self):
        """Test that read-only tools use READ_ONLY_ANNOTATIONS."""
        self.module.register_tools(self.mock_server)
        for tool_name in [
            "falcon_search_data_connectors",
            "falcon_search_data_connections",
            "falcon_get_data_connection",
        ]:
            self.assert_tool_annotations(tool_name, READ_ONLY_ANNOTATIONS)

    def test_create_connection_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_data_connection",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_manage_connection_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_manage_data_connection",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_delete_connection_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_data_connection",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_regenerate_token_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_regenerate_data_connection_token",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_list_connector_configs_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_list_connector_configs",
            READ_ONLY_ANNOTATIONS,
        )

    def test_create_connector_config_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_connector_config",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_connector_config_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_connector_config",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_delete_connector_configs_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_connector_configs",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    # -------------------------------------------------------------------------
    # search_data_connectors
    # -------------------------------------------------------------------------

    def test_search_data_connectors_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "okta", "name": "Okta", "type": "PULL"},
                    {"id": "custom_hec", "name": "Custom HEC", "type": "PUSH"},
                ],
                "meta": {"pagination": {"total": 2}},
            },
        }
        result = self.module.search_data_connectors()
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["pagination"]["total"], 2)

    # -------------------------------------------------------------------------
    # search_data_connections
    # -------------------------------------------------------------------------

    def test_search_data_connections_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "conn-1", "name": "My Okta", "status": "active"},
                ],
                "meta": {"pagination": {"total": 1}},
            },
        }
        result = self.module.search_data_connections(filter="status:'active'")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["filter_used"], "status:'active'")

    def test_search_data_connections_error(self):
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Forbidden"}]},
        }
        result = self.module.search_data_connections()
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertTrue(any("error" in r for r in result["results"] if isinstance(r, dict)))

    # -------------------------------------------------------------------------
    # get_data_connection
    # -------------------------------------------------------------------------

    def test_get_data_connection_details_and_status(self):
        """Test that get_data_connection returns both details and provisioning status."""
        self.mock_client.command.side_effect = [
            # First call: ExternalGetDataConnectionByID (via _base_get_by_ids with use_params=True)
            {
                "status_code": 200,
                "body": {"resources": [{"id": "conn-1", "name": "My Okta", "status": "active"}]},
            },
            # Second call: ExternalGetDataConnectionStatus (via _base_get_by_ids with use_params=True)
            {
                "status_code": 200,
                "body": {"resources": [{"id": "conn-1", "status": "provisioned"}]},
            },
        ]
        result = self.module.get_data_connection(id="conn-1", include_token=False)
        self.assertIn("connection", result)
        self.assertIn("provisioning_status", result)
        self.assertNotIn("token", result)
        self.assertEqual(result["connection"]["id"], "conn-1")

    def test_get_data_connection_with_token(self):
        """Test that include_token=True also fetches the ingest token."""
        self.mock_client.command.side_effect = [
            # ExternalGetDataConnectionByID
            {
                "status_code": 200,
                "body": {"resources": [{"id": "conn-1", "name": "Push Conn"}]},
            },
            # ExternalGetDataConnectionStatus
            {
                "status_code": 200,
                "body": {"resources": [{"id": "conn-1", "status": "provisioned"}]},
            },
            # ExternalGetDataConnectionToken
            {
                "status_code": 200,
                "body": {"resources": {"token": "abc123", "url": "https://ingest.example.com"}},
            },
        ]
        result = self.module.get_data_connection(id="conn-1", include_token=True)
        self.assertIn("connection", result)
        self.assertIn("provisioning_status", result)
        self.assertIn("token", result)

    def test_get_data_connection_error(self):
        """Test that API errors propagate correctly."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "Not found"}]},
        }
        result = self.module.get_data_connection(id="nonexistent")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    # -------------------------------------------------------------------------
    # create_data_connection
    # -------------------------------------------------------------------------

    def test_create_data_connection_success(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-1"}]},
        }
        result = self.module.create_data_connection(
            connector_id="okta", name="My Okta Connection",
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], "new-conn-1")

    def test_create_data_connection_minimal(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-2"}]},
        }
        self.module.create_data_connection(connector_id="custom_hec")
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertEqual(body["connector_id"], "custom_hec")

    def test_create_data_connection_with_custom(self):
        """Test that custom dict is included in the request body when provided."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-3"}]},
        }
        self.module.create_data_connection(
            connector_id="1password",
            custom={"dcc1": "my-api-token"},
        )
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertEqual(body["custom"], {"dcc1": "my-api-token"})

    def test_create_data_connection_custom_omitted_when_none(self):
        """Test that custom is not in the request body when not provided."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-4"}]},
        }
        self.module.create_data_connection(connector_id="custom_hec")
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertNotIn("custom", body)

    def test_create_data_connection_with_config(self):
        """Test that inline config is included in the request body when provided."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-5"}]},
        }
        inline_config = {
            "auth": {"type": "api_key"},
            "name": "My Config",
            "params": {"domain": "example.okta.com"},
        }
        self.module.create_data_connection(
            connector_id="okta",
            config=inline_config,
        )
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertEqual(body["config"], inline_config)

    def test_create_data_connection_config_omitted_when_none(self):
        """Test that config is not in the request body when not provided."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-conn-6"}]},
        }
        self.module.create_data_connection(connector_id="okta", config_id="cfg-1")
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertNotIn("config", body)

    # -------------------------------------------------------------------------
    # manage_data_connection
    # -------------------------------------------------------------------------

    def test_manage_connection_rename(self):
        """Test renaming calls the update endpoint, not the status endpoint."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "conn-1"}]},
        }
        result = self.module.manage_data_connection(ids="conn-1", name="New Name", status=None)
        self.assertIsInstance(result, list)
        self.assertIn("connection_update", result[0])

    def test_manage_connection_pause(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "conn-1", "status": "paused"}]},
        }
        result = self.module.manage_data_connection(ids="conn-1", status="paused")
        self.assertIsInstance(result, list)
        self.assertIn("status_update", result[0])

    def test_manage_connection_pause_and_rename(self):
        """Test both status change and field update in one call."""
        self.mock_client.command.side_effect = [
            # Status update
            {"status_code": 200, "body": {"resources": [{"id": "conn-1", "status": "paused"}]}},
            # Field update
            {"status_code": 200, "body": {"resources": [{"id": "conn-1"}]}},
        ]
        result = self.module.manage_data_connection(
            ids="conn-1", status="paused", name="Renamed",
        )
        self.assertEqual(len(result), 2)

    def test_manage_connection_no_changes(self):
        result = self.module.manage_data_connection(ids="conn-1", status=None)
        self.assertIsInstance(result, list)
        self.assertIn("message", result[0])

    def test_manage_connection_with_custom(self):
        """Test that custom dict is included in the update body when provided."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "conn-1"}]},
        }
        self.module.manage_data_connection(
            ids="conn-1",
            custom={"dcc1": "new-api-token"},
        )
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertEqual(body["custom"], {"dcc1": "new-api-token"})

    def test_manage_connection_custom_omitted_when_none(self):
        """Test that custom is not in the update body when not provided."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "conn-1"}]},
        }
        self.module.manage_data_connection(ids="conn-1", name="Renamed")
        call_args = self.mock_client.command.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body", {})
        self.assertNotIn("custom", body)

    # -------------------------------------------------------------------------
    # delete_data_connection
    # -------------------------------------------------------------------------

    def test_delete_data_connection_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "conn-1"}]},
        }
        result = self.module.delete_data_connection(ids="conn-1")
        self.assertIsInstance(result, list)

    # -------------------------------------------------------------------------
    # regenerate_data_connection_token
    # -------------------------------------------------------------------------

    def test_regenerate_token_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": {"token": "new-token", "url": "https://ingest.example.com"}},
        }
        result = self.module.regenerate_data_connection_token(ids="conn-1")
        self.assertIsNotNone(result)

    # -------------------------------------------------------------------------
    # list_connector_configs
    # -------------------------------------------------------------------------

    def test_config_list(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "cfg-1", "connector_id": "okta"}]},
        }
        result = self.module.list_connector_configs(connector_id="okta")
        self.assertEqual(len(result), 1)

    # -------------------------------------------------------------------------
    # create_connector_config
    # -------------------------------------------------------------------------

    def test_config_create(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "cfg-new"}]},
        }
        result = self.module.create_connector_config(
            connector_id="okta",
            config={"api_token": "secret", "domain": "example.okta.com"},
        )
        self.assertIsInstance(result, list)

    # -------------------------------------------------------------------------
    # update_connector_config
    # -------------------------------------------------------------------------

    def test_config_update(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "cfg-1"}]},
        }
        result = self.module.update_connector_config(
            config_id="cfg-1",
            connector_id="okta",
            config={"api_token": "new-secret"},
        )
        self.assertIsInstance(result, list)

    # -------------------------------------------------------------------------
    # delete_connector_configs
    # -------------------------------------------------------------------------

    def test_config_delete(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "cfg-1"}]},
        }
        result = self.module.delete_connector_configs(
            connector_id="okta", config_ids=["cfg-1"],
        )
        self.assertIsInstance(result, list)

    def test_config_delete_empty_ids(self):
        result = self.module.delete_connector_configs(
            connector_id="okta", config_ids=[],
        )
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
