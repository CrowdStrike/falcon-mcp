"""
Tests for the Detections module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.detections import DetectionsModule
from tests.modules.utils.test_modules import TestModules


class TestDetectionsModule(TestModules):
    """Test cases for the Detections module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DetectionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_detections",
            "falcon_get_detection_details",
            "falcon_update_detections",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_detections_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_detections(self):
        """Test searching for detections - details returns empty (not FQL-related)."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {"resources": ["detection1", "detection2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": []},  # Empty resources for PostEntitiesAlertsV2
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(
            filter="test query", limit=10, include_hidden=True
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={
                "composite_ids": ["detection1", "detection2"],
                "include_hidden": True,
            },
        )

        # Verify result is raw empty list (not FQL-wrapped - query succeeded)
        self.assertEqual(result, [])

    def test_search_detections_with_details(self):
        """Test searching for detections with details - success returns raw list."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {"resources": ["detection1", "detection2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "detection1", "name": "Test Detection 1"},
                    {"id": "detection2", "name": "Test Detection 2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(
            filter="test query", limit=10, include_hidden=True
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={
                "composite_ids": ["detection1", "detection2"],
                "include_hidden": True,
            },
        )

        # Verify result is raw list of detections (no wrapping)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "detection1")
        self.assertEqual(result[1]["id"], "detection2")

    def test_search_detections_error(self):
        """Test searching for detections with API error returns FQL guide."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid query"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_detections
        result = self.module.search_detections(filter="invalid query")

        # Verify result contains error AND fql_guide
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    def test_get_detection_details(self):
        """Test getting detection details."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["detection1"], include_hidden=True)

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"], "include_hidden": True},
        )

        # Verify result - handle_api_response returns a list of resources
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)

    def test_get_detection_details_not_found(self):
        """Test getting detection details for non-existent detection."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["nonexistent"])

        # For empty resources, handle_api_response returns the default_result (empty list)
        # We should check that the result is empty
        self.assertEqual(result, [])

    def test_search_detections_include_hidden_false(self):
        """Test searching for detections with include_hidden=False."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {"resources": ["detection1", "detection2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections with include_hidden=False
        result = self.module.search_detections(
            filter="test query", include_hidden=False
        )

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the second call includes include_hidden=False
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={
                "composite_ids": ["detection1", "detection2"],
                "include_hidden": False,
            },
        )

        # Verify result is raw list (success = no wrapping)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "detection1")

    def test_get_detection_details_include_hidden_false(self):
        """Test getting detection details with include_hidden=False."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "detection1", "name": "Test Detection 1"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details with include_hidden=False
        result = self.module.get_detection_details(["detection1"], include_hidden=False)

        # Verify client command was called correctly with include_hidden=False
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"], "include_hidden": False},
        )

        # Verify result
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)


    def test_format_fql_error_response_empty_results(self):
        """Test that empty results include FQL guide for refinement."""
        from falcon_mcp.resources.detections import SEARCH_DETECTIONS_FQL_DOCUMENTATION

        result = self.module._format_fql_error_response(
            error_or_empty=[],
            filter_used="status:'nonexistent'",
            fql_documentation=SEARCH_DETECTIONS_FQL_DOCUMENTATION
        )

        self.assertEqual(result["results"], [])
        self.assertEqual(result["filter_used"], "status:'nonexistent'")
        self.assertIn("fql_guide", result)
        self.assertEqual(result["fql_guide"], SEARCH_DETECTIONS_FQL_DOCUMENTATION)
        self.assertIn("hint", result)
        self.assertIn("No results matched", result["hint"])

    def test_format_fql_error_response_error(self):
        """Test that error responses include FQL guide."""
        from falcon_mcp.resources.detections import SEARCH_DETECTIONS_FQL_DOCUMENTATION

        error_result = {"error": "Invalid filter syntax", "details": "..."}
        result = self.module._format_fql_error_response(
            error_or_empty=[error_result],
            filter_used="bad filter",
            fql_documentation=SEARCH_DETECTIONS_FQL_DOCUMENTATION
        )

        self.assertEqual(result["results"], [error_result])
        self.assertIn("fql_guide", result)
        self.assertEqual(result["fql_guide"], SEARCH_DETECTIONS_FQL_DOCUMENTATION)
        self.assertIn("error", result["hint"].lower())

    def test_update_detections_has_write_annotations(self):
        """Verify falcon_update_detections has correct non-read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_detections",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_detections_status(self):
        """Test updating detection status."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"], status="in_progress",
            assign_to_uuid=None, assign_to_user_id=None,
            assign_to_name=None, unassign=None, append_comment=None, show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_called_once_with(
            "PatchEntitiesAlertsV3",
            body={
                "composite_ids": ["id1"],
                "action_parameters": [{"name": "update_status", "value": "in_progress"}],
            },
        )
        self.assertEqual(result, [])

    def test_update_detections_assign_uuid(self):
        """Test assigning detection to a user by UUID."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_uuid", "value": "00000000-0000-0000-0000-000000000000"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_user_id(self):
        """Test assigning detection to a user by email."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_user_id", "value": "analyst@example.com"},
            call_body["action_parameters"],
        )

    def test_update_detections_no_params_returns_error(self):
        """Test that providing no update params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_false(self):
        """Test hiding a detection from UI.

        show_in_ui must be sent as the string "false" — live-validated 2026-06-10:
        JSON boolean False returns 400 "failed to read and parse request";
        string "false" returns 200 and the read-back field is Python False.
        """
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=False,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "false"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign(self):
        """Test unassigning a detection from the current user."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "unassign", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign_false_only_returns_error(self):
        """Test that unassign=False as the only argument hits the no-param guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_api_error_returns_error_dict(self):
        """Test that a non-200 API response produces an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_uuid_and_name_returns_error(self):
        """Test that assign_to_uuid + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_user_id_and_name_returns_error(self):
        """Test that assign_to_user_id + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_user_id_and_unassign_returns_error(self):
        """Test that assign_to_user_id + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_name_and_unassign_returns_error(self):
        """Test that assign_to_name + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_invalid_status_returns_error(self):
        """Test that an invalid status value returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status="true_positive",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("status", result["error"])

    def test_update_detections_empty_ids_returns_error(self):
        """Test that passing an empty ids list returns an error without calling API."""
        result = self.module.update_detections(
            ids=[],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_true(self):
        """Test showing a detection in the UI sends the string 'true'."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=True,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_name(self):
        """Test assigning detection to a user by full name."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_name", "value": "Jane Smith"},
            call_body["action_parameters"],
        )

    def test_update_detections_append_comment(self):
        """Test appending a comment sends the correct action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="Investigating now",
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "append_comment", "value": "Investigating now"},
            call_body["action_parameters"],
        )

    def test_update_detections_verdict_false_positive(self):
        """Test setting verdict to false_positive emits add_tag action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict="false_positive",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "false_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_verdict_ignored(self):
        """Test setting verdict to ignored emits add_tag action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict="ignored",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "ignored"},
            call_body["action_parameters"],
        )

    def test_update_detections_two_assign_params_returns_error(self):
        """Test that providing multiple assign_to_* params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("assign_to_uuid", result["error"])

    def test_update_detections_assign_and_unassign_returns_error(self):
        """Test that combining any assign_to_* with unassign=True returns an error."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("unassign", result["error"])

    def test_update_detections_empty_comment_returns_error(self):
        """Test that an empty comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="",
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("append_comment", result["error"])

    def test_update_detections_whitespace_only_comment_returns_error(self):
        """Test that a whitespace-only comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="   ",
            show_in_ui=None,
            verdict=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_verdict_true_positive(self):
        """Test setting verdict to true_positive emits add_tag action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict="true_positive",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "true_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_verdict_invalid_returns_error(self):
        """Test that an invalid verdict value returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict="definitely_not_a_verdict",
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("verdict", result["error"])

    def test_update_detections_verdict_combined_with_status(self):
        """Test combining verdict with status update in one call."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            verdict="true_positive",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertIn("update_status", param_names)
        self.assertIn("add_tag", param_names)

    def test_update_detections_unassign_false_is_noop(self):
        """Test that unassign=False does not add the action parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            verdict=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertNotIn("unassign", param_names)


if __name__ == "__main__":
    unittest.main()
