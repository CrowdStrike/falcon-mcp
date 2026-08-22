"""
Tests for the Cases module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.cases import CasesModule, _is_filter_error
from tests.modules.utils.test_modules import TestModules


class TestCasesModule(TestModules):
    """Test cases for the Cases module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CasesModule)

    # -------------------------------------------------------------------------
    # Registration Tests
    # -------------------------------------------------------------------------

    def test_register_tools(self):
        """Test that all 13 case management tools are registered with correct prefixed names."""
        expected_tools = [
            "falcon_search_cases",
            "falcon_get_cases",
            "falcon_create_case",
            "falcon_update_case",
            "falcon_add_case_alert_evidence",
            "falcon_add_case_event_evidence",
            "falcon_manage_case_tags",
            "falcon_list_case_templates",
            "falcon_aggregate_case_slas",
            "falcon_aggregate_case_templates",
            "falcon_aggregate_case_access_tags",
            "falcon_aggregate_case_notification_groups",
            "falcon_aggregate_case_file_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test that the FQL guide resources are registered."""
        expected_resources = [
            "falcon_search_cases_fql_guide",
            "falcon_aggregate_case_config_fql_guide",
            "falcon_aggregate_case_file_details_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    # -------------------------------------------------------------------------
    # Annotation Tests
    # -------------------------------------------------------------------------

    def test_mutating_tools_have_correct_annotations(self):
        """Test that write tools have readOnlyHint=False, non-destructive annotations."""
        self.module.register_tools(self.mock_server)

        mutating_annotations = ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )

        for tool_name in [
            "falcon_create_case",
            "falcon_update_case",
            "falcon_add_case_alert_evidence",
            "falcon_add_case_event_evidence",
            "falcon_manage_case_tags",
        ]:
            self.assert_tool_annotations(tool_name, mutating_annotations)

    def test_read_only_tools_have_default_annotations(self):
        """Test that search/get/list tools have read-only annotations."""
        self.module.register_tools(self.mock_server)

        for tool_name in [
            "falcon_search_cases",
            "falcon_get_cases",
            "falcon_list_case_templates",
        ]:
            self.assert_tool_annotations(tool_name, READ_ONLY_ANNOTATIONS)

    # -------------------------------------------------------------------------
    # Search Tests
    # -------------------------------------------------------------------------

    def test_search_cases_success(self):
        """Test two-step search: query for IDs then fetch full details."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["case-id-1", "case-id-2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "case-id-1", "name": "Case One", "severity": 75},
                    {"id": "case-id-2", "name": "Case Two", "severity": 50},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_cases(filter="status:'new'", limit=10)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "queries_cases_get_v1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "status:'new'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)

        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "entities_cases_post_v2")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "case-id-1")
        self.assertEqual(result["results"][1]["id"], "case-id-2")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_cases_reorders_to_match_sorted_ids(self):
        """When entities_cases_post_v2 returns cases out of order, the result is
        reordered to match the sorted ID order from queries_cases_get_v1.

        Live API validated: the details endpoint scrambles order; entities carry
        their ID in the ``id`` field.
        """
        query_response = {
            "status_code": 200,
            "body": {"resources": ["case-b", "case-a"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "case-a", "name": "Case A"},
                    {"id": "case-b", "name": "Case B"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_cases(sort="created_timestamp.desc")

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "case-b")
        self.assertEqual(result["results"][1]["id"], "case-a")

    def test_search_cases_empty_results(self):
        """Test that empty query results return clean empty response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_cases(filter="status:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIsNone(result["pagination"]["total"])
        self.assertEqual(result["filter_used"], "status:'nonexistent'")
        self.assertNotIn("fql_guide", result)

    def test_search_cases_search_error(self):
        """Test that query API error returns FQL guide response."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid FQL syntax"}]},
        }

        result = self.module.search_cases(filter="bad filter!!!")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)

    def test_search_cases_details_error(self):
        """Test that details API error is returned wrapped in a list."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["case-id-1"]},
        }
        details_response = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_cases(filter="status:'new'")

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Get Tests
    # -------------------------------------------------------------------------

    def test_get_cases_success(self):
        """Test getting cases by IDs returns full case records."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "case-id-1", "name": "Test Case", "severity": 80},
                ]
            },
        }

        result = self.module.get_cases(ids=["case-id-1"])

        self.mock_client.command.assert_called_once_with(
            "entities_cases_post_v2",
            body={"ids": ["case-id-1"]},
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "case-id-1")

    def test_get_cases_error(self):
        """Test that get cases API error returns an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "Case not found"}]},
        }

        result = self.module.get_cases(ids=["nonexistent-case-id"])

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    # -------------------------------------------------------------------------
    # Create Tests
    # -------------------------------------------------------------------------

    def test_create_case_success(self):
        """Test creating a case with name and severity returns created record."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {
                "resources": [
                    {"id": "new-case-id", "name": "My Case", "severity": 75}
                ]
            },
        }

        result = self.module.create_case(
            name="My Case",
            severity=75,
            description=None,
            description_format=None,
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id=None,
            alert_ids=None,
            event_ids=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_cases_put_v2")
        body = call_args[1]["body"]
        self.assertEqual(body["name"], "My Case")
        self.assertEqual(body["severity"], 75)
        self.assertNotIn("description_format", body)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "new-case-id")

    def test_create_case_with_evidence(self):
        """Test that alert_ids and event_ids are converted to object format."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-case-id", "name": "Evidence Case"}]},
        }

        self.module.create_case(
            name="Evidence Case",
            severity=50,
            description=None,
            description_format=None,
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id=None,
            alert_ids=["alert-1", "alert-2"],
            event_ids=["event-1"],
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertIn("evidence", body)
        self.assertEqual(body["evidence"]["alerts"], [{"id": "alert-1"}, {"id": "alert-2"}])
        self.assertEqual(body["evidence"]["events"], [{"id": "event-1"}])

    def test_create_case_with_template(self):
        """Test that template_id is nested as {"template": {"id": "..."}}."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-case-id", "name": "Template Case"}]},
        }

        self.module.create_case(
            name="Template Case",
            severity=25,
            description=None,
            description_format=None,
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id="tmpl-abc-123",
            alert_ids=None,
            event_ids=None,
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["template"], {"id": "tmpl-abc-123"})

    def test_create_case_with_description_format(self):
        """Test that description_format is passed through to the request body."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "new-case-id", "name": "Markdown Case"}]},
        }

        self.module.create_case(
            name="Markdown Case",
            severity=50,
            description="**Bold** summary",
            description_format="markdown",
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id=None,
            alert_ids=None,
            event_ids=None,
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["description"], "**Bold** summary")
        self.assertEqual(body["description_format"], "markdown")

    def test_create_case_error(self):
        """Test that create case API error is returned wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Validation failed"}]},
        }

        result = self.module.create_case(
            name="Bad Case",
            severity=50,
            description=None,
            description_format=None,
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id=None,
            alert_ids=None,
            event_ids=None,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Update Tests
    # -------------------------------------------------------------------------

    def test_update_case_success(self):
        """Test updating a case sends id and updated fields correctly."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "case-id-1", "name": "Updated Name", "status": "in_progress"}
                ]
            },
        }

        result = self.module.update_case(
            id="case-id-1",
            name="Updated Name",
            description=None,
            description_format=None,
            status="in_progress",
            severity=None,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id=None,
            expected_version=None,
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_cases_patch_v2")
        body = call_args[1]["body"]
        self.assertEqual(body["id"], "case-id-1")
        self.assertIn("fields", body)
        self.assertEqual(body["fields"]["name"], "Updated Name")
        self.assertEqual(body["fields"]["status"], "in_progress")
        self.assertNotIn("description_format", body["fields"])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_update_case_with_expected_version(self):
        """Test that expected_version is included in the request body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1", "version": 3}]},
        }

        self.module.update_case(
            id="case-id-1",
            name=None,
            description=None,
            description_format=None,
            status=None,
            severity=90,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id=None,
            expected_version=2,
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["expected_version"], 2)
        self.assertEqual(body["fields"]["severity"], 90)

    def test_update_case_no_fields(self):
        """Test that updating with no fields returns a validation error."""
        result = self.module.update_case(
            id="case-id-1",
            name=None,
            description=None,
            description_format=None,
            status=None,
            severity=None,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id=None,
            expected_version=None,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_case_with_template(self):
        """Test that template_id in update is nested as {"template": {"id": "..."}}."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1"}]},
        }

        self.module.update_case(
            id="case-id-1",
            name=None,
            description=None,
            description_format=None,
            status=None,
            severity=None,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id="tmpl-xyz-789",
            expected_version=None,
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["fields"]["template"], {"id": "tmpl-xyz-789"})

    def test_update_case_with_description_format(self):
        """Test that description_format is included in the updated fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1"}]},
        }

        self.module.update_case(
            id="case-id-1",
            name=None,
            description="## Updated",
            description_format="markdown",
            status=None,
            severity=None,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id=None,
            expected_version=None,
        )

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["fields"]["description"], "## Updated")
        self.assertEqual(body["fields"]["description_format"], "markdown")

    # -------------------------------------------------------------------------
    # Evidence Tests
    # -------------------------------------------------------------------------

    def test_add_alert_evidence_success(self):
        """Test adding alert evidence with correct body format."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1"}]},
        }

        result = self.module.add_case_alert_evidence(
            id="case-id-1",
            alert_ids=["alert-composite-1", "alert-composite-2"],
        )

        self.mock_client.command.assert_called_once_with(
            "entities_alert_evidence_post_v1",
            body={
                "id": "case-id-1",
                "alerts": [{"id": "alert-composite-1"}, {"id": "alert-composite-2"}],
            },
        )
        self.assertIsInstance(result, list)

    def test_add_event_evidence_success(self):
        """Test adding event evidence with correct body format."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1"}]},
        }

        result = self.module.add_case_event_evidence(
            id="case-id-1",
            event_ids=["event-id-1", "event-id-2"],
        )

        self.mock_client.command.assert_called_once_with(
            "entities_event_evidence_post_v1",
            body={
                "id": "case-id-1",
                "events": [{"id": "event-id-1"}, {"id": "event-id-2"}],
            },
        )
        self.assertIsInstance(result, list)

    # -------------------------------------------------------------------------
    # Tag Tests
    # -------------------------------------------------------------------------

    def test_manage_tags_add(self):
        """Test adding tags sends POST body with id and tags."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1", "tags": ["tag1", "tag2"]}]},
        }

        result = self.module.manage_case_tags(
            id="case-id-1",
            action="add",
            tags=["tag1", "tag2"],
        )

        self.mock_client.command.assert_called_once_with(
            "entities_case_tags_post_v1",
            body={"id": "case-id-1", "tags": ["tag1", "tag2"]},
        )
        self.assertIsInstance(result, list)

    def test_manage_tags_remove(self):
        """Test removing tags sends DELETE with query parameters (not body)."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1", "tags": []}]},
        }

        result = self.module.manage_case_tags(
            id="case-id-1",
            action="remove",
            tags=["tag1"],
        )

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "entities_case_tags_delete_v1")
        # DELETE must use query parameters, not body
        self.assertIn("parameters", call_args[1])
        self.assertNotIn("body", call_args[1])
        self.assertEqual(call_args[1]["parameters"]["id"], "case-id-1")
        self.assertEqual(call_args[1]["parameters"]["tag"], ["tag1"])

        self.assertIsInstance(result, list)

    def test_manage_tags_invalid_action(self):
        """Test that an invalid action returns an error without calling the API."""
        result = self.module.manage_case_tags(
            id="case-id-1",
            action="invalid_action",
            tags=["tag1"],
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    # -------------------------------------------------------------------------
    # Template Tests
    # -------------------------------------------------------------------------

    def test_list_templates_success(self):
        """Test two-step template listing: query IDs then fetch details with use_params=True."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["tmpl-id-1", "tmpl-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "tmpl-id-1", "name": "Incident Template"},
                    {"id": "tmpl-id-2", "name": "Alert Template"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.list_case_templates(limit=50)

        self.assertEqual(self.mock_client.command.call_count, 2)

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "queries_templates_get_v1")

        # Verify the second call uses query parameters (use_params=True → GET)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "entities_templates_get_v1")
        self.assertIn("parameters", second_call[1])
        self.assertNotIn("body", second_call[1])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "tmpl-id-1")

    def test_list_templates_reorders_to_match_sorted_ids(self):
        """When entities_templates_get_v1 returns templates out of order, the result
        is reordered to match the query-step ID order."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["tmpl-id-2", "tmpl-id-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "tmpl-id-1", "name": "Incident Template"},
                    {"id": "tmpl-id-2", "name": "Alert Template"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.list_case_templates(limit=50)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "tmpl-id-2")
        self.assertEqual(result[1]["id"], "tmpl-id-1")

    def test_list_templates_empty(self):
        """Test that empty template query returns an empty list (no FQL guide)."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.list_case_templates()

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    # -------------------------------------------------------------------------
    # Security Validation Tests
    # -------------------------------------------------------------------------

    def test_search_cases_with_special_characters_in_filter(self):
        """Test that special characters in the filter are passed safely to the API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "status:'new'+name:*';DROP TABLE--*"
        self.module.search_cases(filter=filter_with_special)

        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_create_case_permission_error(self):
        """Test that a 403 permission error on create case returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied, authorization failed"}]},
        }

        result = self.module.create_case(
            name="Unauthorized Case",
            severity=50,
            description=None,
            description_format=None,
            status=None,
            assigned_to_user_uuid=None,
            tags=None,
            template_id=None,
            alert_ids=None,
            event_ids=None,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_update_case_conflict_error(self):
        """Test that a 409 conflict on update case returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 409,
            "body": {"errors": [{"message": "Version conflict"}]},
        }

        result = self.module.update_case(
            id="case-id-1",
            name="Conflicting Update",
            description=None,
            description_format=None,
            status=None,
            severity=None,
            assigned_to_user_uuid=None,
            remove_user_assignment=None,
            template_id=None,
            expected_version=1,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_add_alert_evidence_permission_error(self):
        """Test that a 403 error on add alert evidence returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.add_case_alert_evidence(
            id="case-id-1",
            alert_ids=["alert-1"],
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_manage_tags_add_with_long_tags(self):
        """Test that long tag values are passed through to the API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "case-id-1"}]},
        }

        long_tag = "x" * 128
        self.module.manage_case_tags(id="case-id-1", action="add", tags=[long_tag])

        call_args = self.mock_client.command.call_args
        body = call_args[1]["body"]
        self.assertIn(long_tag, body["tags"])

    def test_list_templates_error(self):
        """Test that a template query error is wrapped in a list."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }

        result = self.module.list_case_templates()

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    # -------------------------------------------------------------------------
    # Aggregate Tool Tests
    # -------------------------------------------------------------------------

    def _agg_ok(self, buckets=None):
        """Stub a successful aggregate response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "t", "buckets": buckets or [{"label": "a", "count": 2}]}
                ],
                "errors": [],
            },
        }

    def _sent_body(self):
        """Return the single aggregate spec sent to the API."""
        body = self.mock_client.command.call_args[1]["body"]
        self.assertIsInstance(body, list, "aggregate body must be list-wrapped")
        self.assertEqual(len(body), 1)
        return body[0]

    def test_aggregate_tools_are_read_only(self):
        """Test that all five aggregate tools register as read-only."""
        self.module.register_tools(self.mock_server)

        for tool in (
            "falcon_aggregate_case_slas",
            "falcon_aggregate_case_templates",
            "falcon_aggregate_case_access_tags",
            "falcon_aggregate_case_notification_groups",
            "falcon_aggregate_case_file_details",
        ):
            self.assert_tool_annotations(tool, READ_ONLY_ANNOTATIONS)

    def test_aggregate_tools_use_correct_operations(self):
        """Test that each aggregate tool calls its own verified FalconPy operation."""
        cases = [
            (self.module.aggregate_case_slas, "aggregates_slas_post_v1", "name"),
            (self.module.aggregate_case_templates, "aggregates_templates_post_v1", "name"),
            (
                self.module.aggregate_case_access_tags,
                "aggregates_access_tags_post_v1",
                "key",
            ),
            (
                self.module.aggregate_case_notification_groups,
                "aggregates_notification_groups_post_v2",
                "name",
            ),
        ]
        for method, operation, field in cases:
            with self.subTest(operation=operation):
                self.mock_client.command.reset_mock()
                self._agg_ok()

                result = method(
                    field=field,
                    agg_type="terms",
                    filter=None,
                    size=None,
                    from_=None,
                    date_ranges=None,
                    name=None,
                )

                self.assertEqual(
                    self.mock_client.command.call_args[0][0], operation
                )
                self.assertEqual(self._sent_body(), {"type": "terms", "field": field})
                self.assertEqual(result[0]["buckets"], [{"label": "a", "count": 2}])

    def test_aggregate_notification_groups_avoids_deprecated_v1(self):
        """Test that the deprecated v1 notification-groups operation is never called."""
        self._agg_ok()

        self.module.aggregate_case_notification_groups(
            field="name",
            agg_type="terms",
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        operation = self.mock_client.command.call_args[0][0]
        self.assertEqual(operation, "aggregates_notification_groups_post_v2")
        self.assertNotEqual(operation, "aggregates_notification_groups_post_v1")

    def test_aggregate_forwards_reduced_dialect_fields(self):
        """Test that the reduced-dialect fields reach the API under their wire names."""
        self._agg_ok()

        self.module.aggregate_case_templates(
            field="created_timestamp",
            agg_type="date_range",
            filter="created_by_name:'a@example.com'",
            size=5,
            from_=2,
            date_ranges=[{"from": "2026-01-01T00:00:00Z", "to": "2026-02-01T00:00:00Z"}],
            name="by_quarter",
        )

        self.assertEqual(
            self._sent_body(),
            {
                "type": "date_range",
                "field": "created_timestamp",
                "filter": "created_by_name:'a@example.com'",
                "from": 2,
                "name": "by_quarter",
                "size": 5,
                "date_ranges": [
                    {"from": "2026-01-01T00:00:00Z", "to": "2026-02-01T00:00:00Z"}
                ],
            },
        )

    def test_aggregate_omits_unset_fields(self):
        """Test that unset optional fields are omitted rather than sent as null."""
        self._agg_ok()

        self.module.aggregate_case_slas(
            field="name",
            agg_type="terms",
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertEqual(sorted(self._sent_body()), ["field", "type"])

    def test_aggregate_does_not_send_sort(self):
        """Test that no aggregate tool sends sort, which the API ignores."""
        self._agg_ok()

        self.module.aggregate_case_templates(
            field="name",
            agg_type="terms",
            filter=None,
            size=3,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertNotIn("sort", self._sent_body())

    def test_aggregate_filter_error_returns_fql_guide(self):
        """Test that a filter error is surfaced with the FQL guide attached."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "unexpected filter field"}],
            },
        }

        result = self.module.aggregate_case_templates(
            field="name",
            agg_type="terms",
            filter="status:'new'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("name", result["fql_guide"])
        self.assertIn("error", result["results"][0])

    def test_aggregate_non_filter_error_omits_fql_guide(self):
        """Test that a bad aggregation field is not blamed on the filter.

        The FQL guide covers the `filter` param, so attaching it to a `field`
        or `agg_type` failure would point the caller at the wrong argument.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [
                    {"code": 400, "message": "unsupported field for aggregation: status"}
                ],
            },
        }

        result = self.module.aggregate_case_templates(
            field="status",
            agg_type="terms",
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertNotIn("fql_guide", result[0])

    def test_aggregate_invalid_agg_type_error_omits_fql_guide(self):
        """Test that an invalid aggregate type is not reported as a filter error."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": 'invalid aggregate type: "avg"'}],
            },
        }

        result = self.module.aggregate_case_slas(
            field="name",
            agg_type="avg",
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertNotIn("fql_guide", result[0])

    def test_aggregate_date_range_without_date_ranges_skips_the_api(self):
        """Test that a date_range aggregation missing its buckets never reaches the API.

        The API answers such a spec with an opaque 500, so `_base_aggregate`
        rejects it up front. The reply is not a filter problem, so it must not
        carry the FQL guide.
        """
        for tool in (
            self.module.aggregate_case_slas,
            self.module.aggregate_case_templates,
            self.module.aggregate_case_access_tags,
            self.module.aggregate_case_notification_groups,
        ):
            with self.subTest(tool=tool.__name__):
                self.mock_client.command.reset_mock()

                result = tool(
                    field="name",
                    agg_type="date_range",
                    filter=None,
                    size=None,
                    from_=None,
                    date_ranges=None,
                    name=None,
                )

                self.mock_client.command.assert_not_called()
                self.assertIsInstance(result, list)
                self.assertIn("error", result[0])
                self.assertIn("date_ranges", result[0]["error"])
                self.assertNotIn("fql_guide", result[0])

    def test_aggregate_file_details_date_range_without_date_ranges_skips_the_api(self):
        """Test that the file-details tool also rejects the spec before any call."""
        result = self.module.aggregate_case_file_details(
            field="name",
            agg_type="date_range",
            case_ids=None,
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("date_ranges", result[0]["error"])
        self.assertNotIn("fql_guide", result[0])

    def test_aggregate_http_400_field_error_omits_fql_guide(self):
        """Test that a real 400 field error is not mistaken for a filter error.

        `handle_api_response` prepends generic filter-syntax advice to every
        400, so classification must read the API's own messages instead.
        """
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "code": 400,
                        "message": "unsupported field for aggregation: not_a_real_field",
                    }
                ]
            },
        }

        result = self.module.aggregate_case_templates(
            field="not_a_real_field",
            agg_type="terms",
            filter="name:'x'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertNotIn("fql_guide", result[0])

    def test_aggregate_http_400_filter_error_returns_fql_guide(self):
        """Test that a real 400 filter error still surfaces the FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"code": 400, "message": "unexpected filter field"}]},
        }

        result = self.module.aggregate_case_templates(
            field="name",
            agg_type="terms",
            filter="not_a_real_field:'x'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)

    def test_is_filter_error_tolerates_malformed_error_shapes(self):
        """Test that error classification never raises on an unexpected shape.

        A crash here would replace a useful API error with a TypeError, so every
        shape `_base_aggregate` can return must classify rather than blow up.
        """
        shapes = [
            {"error": "boom"},
            {"error": "boom", "details": None},
            {"error": "boom", "details": "not a dict"},
            {"error": "boom", "details": {"status_code": 403}},
            {"error": "boom", "details": {"body": None}},
            {"error": "boom", "details": {"body": {"resources": []}}},
            {"error": "boom", "details": {"body": {"errors": None}}},
            {"error": "boom", "details": {"body": {"errors": []}}},
            {"error": "boom", "details": {"body": {"errors": [{"code": 403}]}}},
            {"error": "boom", "details": {"body": {"errors": [{"message": None}]}}},
            {"error": "boom", "details": {"body": {"errors": ["filter"]}}},
            {"error": "boom", "details": {"body": {"errors": {"message": "filter"}}}},
        ]
        for shape in shapes:
            with self.subTest(shape=shape):
                self.assertFalse(_is_filter_error(shape))

    def test_is_filter_error_detects_api_filter_messages(self):
        """Test that a filter message is recognized, including past a sibling error."""
        self.assertTrue(
            _is_filter_error(
                {
                    "error": "boom",
                    "details": {
                        "body": {"errors": [{"message": "unexpected filter field"}]}
                    },
                }
            )
        )
        self.assertTrue(
            _is_filter_error(
                {
                    "error": "boom",
                    "details": {
                        "body": {
                            "errors": [
                                {"message": "something else"},
                                {"message": "failed to parse filter"},
                            ]
                        }
                    },
                }
            )
        )
        self.assertFalse(
            _is_filter_error(
                {
                    "error": "boom",
                    "details": {
                        "body": {
                            "errors": [
                                {"message": "unsupported field for aggregation: x"}
                            ]
                        }
                    },
                }
            )
        )

    def test_aggregate_access_tags_error_names_supported_fields(self):
        """Test that an access-tags filter failure returns its narrow field set."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [{"code": 400, "message": "unexpected filter field"}],
            },
        }

        result = self.module.aggregate_case_access_tags(
            field="key",
            agg_type="terms",
            filter="name:'x'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIn("key", result["fql_guide"])

    def test_aggregate_file_details_uses_correct_operation(self):
        """Test that file details calls its own operation and sends no ids when unscoped."""
        self._agg_ok()

        self.module.aggregate_case_file_details(
            field="name",
            agg_type="terms",
            case_ids=None,
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertEqual(
            self.mock_client.command.call_args[0][0],
            "aggregates_file_details_post_v1",
        )
        self.assertNotIn("parameters", self.mock_client.command.call_args[1])
        self.assertEqual(self._sent_body(), {"type": "terms", "field": "name"})

    def test_aggregate_file_details_scopes_case_ids_via_filter(self):
        """Test that case_ids becomes a case_id filter, since the ids param does not narrow."""
        self._agg_ok()

        self.module.aggregate_case_file_details(
            field="name",
            agg_type="terms",
            case_ids=["case-a", "case-b"],
            filter=None,
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertEqual(
            self._sent_body()["filter"], "case_id:['case-a','case-b']"
        )
        # Still sent as a query param, because the API declares ids required.
        self.assertEqual(
            self.mock_client.command.call_args[1]["parameters"],
            {"ids": ["case-a", "case-b"]},
        )

    def test_aggregate_file_details_parenthesizes_user_filter(self):
        """Test that an OR in the caller's filter cannot widen the case scope."""
        self._agg_ok()

        self.module.aggregate_case_file_details(
            field="name",
            agg_type="terms",
            case_ids=["case-a"],
            filter="name:'x',name:*'*.png'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertEqual(
            self._sent_body()["filter"],
            "case_id:['case-a']+(name:'x',name:*'*.png')",
        )

    def test_aggregate_file_details_filter_only(self):
        """Test that a filter with no case_ids is passed through unwrapped."""
        self._agg_ok()

        self.module.aggregate_case_file_details(
            field="name",
            agg_type="terms",
            case_ids=None,
            filter="name:*'*.png'",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertEqual(self._sent_body()["filter"], "name:*'*.png'")

    def test_aggregate_file_details_error_returns_file_guide(self):
        """Test that a file-details failure returns the file guide, not the config guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "failed to parse filter"}]},
        }

        result = self.module.aggregate_case_file_details(
            field="name",
            agg_type="terms",
            case_ids=["case-a"],
            filter="name:::",
            size=None,
            from_=None,
            date_ranges=None,
            name=None,
        )

        self.assertIn("case_id", result["fql_guide"])
        self.assertIn("Case File Aggregates", result["fql_guide"])
        # The composed filter, not the caller's fragment, is what the API saw.
        self.assertEqual(result["filter_used"], "case_id:['case-a']+(name:::)")


if __name__ == "__main__":
    unittest.main()
