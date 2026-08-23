"""
Tests for the Fusion SOAR module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.fusion import FusionModule
from tests.modules.utils.test_modules import TestModules

# Annotations for the execute tool: a workflow's action graph is authored
# elsewhere, so its reachable effect is destructive and not idempotent.
_EXECUTE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class TestFusionModule(TestModules):
    """Test cases for the Fusion SOAR module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(FusionModule)

    # --- Registration ---

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_workflow_definitions",
            "falcon_search_workflow_executions",
            "falcon_get_workflow_execution_results",
            "falcon_execute_workflow",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_workflow_definitions_fql_guide",
            "falcon_search_workflow_executions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_execute_tool_has_destructive_annotations(self):
        """The execute tool must register destructive, non-idempotent annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_execute_workflow", _EXECUTE_ANNOTATIONS)

    # --- search_workflow_definitions ---

    def test_search_definitions_success(self):
        """A single call returns full definitions inside the pagination envelope."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "d1", "name": "Contain Host", "enabled": True, "version": 2},
                    {"id": "d1", "name": "Contain Host", "enabled": False, "version": 1},
                ],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
            },
        }

        result = self.module.search_workflow_definitions(
            filter="enabled:true",
            limit=10,
            offset=None,
            sort="last_modified_timestamp.desc",
        )

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["name"], "Contain Host")
        self.assertEqual(result["filter_used"], "enabled:true")
        self.assert_pagination(result, total=2)

        # One call: the combined endpoint returns full records, so there is no
        # hydrate-by-ID second step.
        self.mock_client.command.assert_called_once()
        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "WorkflowDefinitionsCombined")
        self.assertEqual(
            kwargs["parameters"],
            {"filter": "enabled:true", "limit": 10, "sort": "last_modified_timestamp.desc"},
        )

    def test_search_definitions_empty_returns_envelope(self):
        """No matches still returns the envelope, not an FQL-error dict."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 0}},
            },
        }

        result = self.module.search_workflow_definitions(
            filter="enabled:true",
            limit=10,
            offset=None,
            sort="last_modified_timestamp.desc",
        )

        self.assertEqual(result["results"], [])
        self.assertNotIn("fql_guide", result)
        self.assert_pagination(result, total=0)

    def test_search_definitions_fql_error_returns_guide(self):
        """A 400 on the filter returns the definitions FQL guide inline."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {"code": 400, "message": "Invalid FQL: fql: bogus is an unknown property"}
                ]
            },
        }

        result = self.module.search_workflow_definitions(
            filter="bogus:'x'",
            limit=10,
            offset=None,
            sort="last_modified_timestamp.desc",
        )

        self.assertIn("fql_guide", result)
        self.assertIn("name.raw", result["fql_guide"])
        self.assertEqual(result["filter_used"], "bogus:'x'")
        self.assertIn("error", result["results"][0])

    def test_search_definitions_non_filter_error_omits_guide(self):
        """A 500 is not a filter problem, so it must not return the FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"code": 500, "message": "Internal Server Error"}]},
        }

        result = self.module.search_workflow_definitions(
            filter=None,
            limit=500,
            offset=None,
            sort="last_modified_timestamp.desc",
        )

        self.assertIn("error", result)
        self.assertNotIn("fql_guide", result)

    def test_search_definitions_scope_error_surfaces_required_scopes(self):
        """A 403 surfaces required_scopes at the top level, not buried in an envelope.

        Routing every error through the FQL-error shape would nest the 403 inside
        `results` under a top-level hint saying the filter is wrong — so the actual
        remedy, granting the scope, would be one level down behind misleading advice.
        """
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"code": 403, "message": "access denied, scope not permitted"}]},
        }

        result = self.module.search_workflow_definitions(
            filter="enabled:true",
            limit=10,
            offset=None,
            sort="last_modified_timestamp.desc",
        )

        self.assertNotIn("fql_guide", result)
        self.assertEqual(result["required_scopes"], ["Workflows:read"])
        self.assertIn("resolution", result)

    def test_search_definitions_bad_sort_400_omits_guide(self):
        """A rejected `sort` is a 400, but not a filter problem — no FQL guide.

        The guide would send the caller to rewrite `filter` when the parameter at
        fault is `sort`. Note the raw API message never mentions FQL here, while
        the composed error string does, because handle_api_response prefixes every
        400 with FQL boilerplate.
        """
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "code": 400,
                        "message": (
                            "Input validation failed for query string parameter "
                            "'sort'. Please ensure your input follows the required format."
                        ),
                    }
                ]
            },
        }

        result = self.module.search_workflow_definitions(
            filter="enabled:true",
            limit=10,
            offset=None,
            sort="name|desc",
        )

        self.assertNotIn("fql_guide", result)
        self.assertIn("error", result)
        self.assertIn("'sort'", result["error"])

    def test_search_definitions_400_without_filter_omits_guide(self):
        """With no filter supplied, the guide is withheld even if the API says FQL.

        This pins the filter-supplied guard specifically. The message check alone
        already excludes the realistic sort and limit 400s, so the case that
        isolates this guard is a 400 that DOES mention FQL while the caller sent no
        filter — there is then nothing for the guide to help rewrite.
        """
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {"code": 400, "message": "Invalid FQL: fql: something is an unknown property"}
                ]
            },
        }

        result = self.module.search_workflow_definitions(
            filter=None,
            limit=10,
            offset=None,
            sort="name.asc",
        )

        self.assertNotIn("fql_guide", result)
        self.assertIn("error", result)

    def test_search_executions_oversized_limit_400_omits_guide(self):
        """An invalid page size is a 400 about `limit`, so no FQL guide."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "code": 400,
                        "message": "501 is an invalid page size, must be between 1 and 500",
                    }
                ]
            },
        }

        result = self.module.search_workflow_executions(
            filter="ui_status:'Completed'",
            limit=500,
            offset=None,
            sort="started_timestamp.desc",
        )

        self.assertNotIn("fql_guide", result)
        self.assertIn("invalid page size", result["error"])

    def test_search_definitions_forwards_offset(self):
        """offset reaches the API when supplied."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [], "meta": {"pagination": {"total": 0}}},
        }

        self.module.search_workflow_definitions(
            filter=None, limit=25, offset=50, sort="name.asc"
        )

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(
            kwargs["parameters"], {"limit": 25, "offset": 50, "sort": "name.asc"}
        )

    # --- search_workflow_executions ---

    def test_search_executions_success(self):
        """A single call returns full executions inside the pagination envelope."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"execution_id": "e1", "definition_id": "d1", "status": "Completed"}
                ],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 10000}},
            },
        }

        result = self.module.search_workflow_executions(
            filter="ui_status:'Completed'",
            limit=10,
            offset=None,
            sort="started_timestamp.desc",
        )

        self.assertEqual(result["results"][0]["execution_id"], "e1")
        self.assertEqual(result["filter_used"], "ui_status:'Completed'")
        self.assert_pagination(result, total=10000)

        self.mock_client.command.assert_called_once()
        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "WorkflowExecutionsCombined")
        self.assertEqual(
            kwargs["parameters"],
            {
                "filter": "ui_status:'Completed'",
                "limit": 10,
                "sort": "started_timestamp.desc",
            },
        )

    def test_search_executions_empty_returns_envelope(self):
        """No matches still returns the envelope, not an FQL-error dict."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "meta": {"pagination": {"offset": 0, "limit": 10, "total": 0}},
            },
        }

        result = self.module.search_workflow_executions(
            filter="ui_status:'Failed'",
            limit=10,
            offset=None,
            sort="started_timestamp.desc",
        )

        self.assertEqual(result["results"], [])
        self.assertNotIn("fql_guide", result)
        self.assert_pagination(result, total=0)

    def test_search_executions_fql_error_returns_guide(self):
        """A 400 on the filter returns the executions FQL guide inline."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "code": 400,
                        "message": "Invalid FQL: fql: start_timestamp is an unknown property",
                    }
                ]
            },
        }

        result = self.module.search_workflow_executions(
            filter="start_timestamp:>'now-7d'",
            limit=10,
            offset=None,
            sort="started_timestamp.desc",
        )

        self.assertIn("fql_guide", result)
        self.assertIn("ui_status", result["fql_guide"])
        self.assertEqual(result["filter_used"], "start_timestamp:>'now-7d'")

    def test_search_executions_non_filter_error_omits_guide(self):
        """A 404 from internal hydration is not a filter problem, so no FQL guide.

        The executions endpoint hydrates matches by ID and returns 404 naming
        executions that are indexed but no longer retrievable. Answering that with
        the FQL guide would tell the caller to rewrite a filter that was correct —
        and here the filter is None, so there is nothing to rewrite.
        """
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {
                "errors": [
                    {"code": 404, "message": "execution ID '6bebefbd6edaaeaf3' not found"}
                ]
            },
        }

        result = self.module.search_workflow_executions(
            filter=None,
            limit=10,
            offset=None,
            sort="started_timestamp.asc",
        )

        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
        self.assertNotIn("fql_guide", result)

    # --- get_workflow_execution_results ---

    def test_get_execution_results_success(self):
        """Results are returned with each activity's own result payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "execution_id": "e1",
                        "status": "Completed",
                        "activities": [
                            {
                                "node_id": "CreateServiceNowIncident",
                                "status": "Completed",
                                "result": {"incident_number": "INC1559079"},
                            }
                        ],
                    }
                ]
            },
        }

        result = self.module.get_workflow_execution_results(ids=["e1"], skip_fields=None)

        self.assertEqual(
            result[0]["activities"][0]["result"]["incident_number"], "INC1559079"
        )
        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "WorkflowExecutionResults")
        self.assertEqual(kwargs["parameters"], {"ids": ["e1"]})

    def test_get_execution_results_forwards_skip_fields(self):
        """skip_fields reaches the API so the caller can shrink the payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"execution_id": "e1"}]},
        }

        self.module.get_workflow_execution_results(
            ids=["e1", "e2"], skip_fields=["trigger", "flows"]
        )

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(
            kwargs["parameters"],
            {"ids": ["e1", "e2"], "skip_fields": ["trigger", "flows"]},
        )

    def test_get_execution_results_not_found(self):
        """A 404 for an unknown execution surfaces the API message."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"code": 404, "message": "execution ID 'nope' not found"}]},
        }

        result = self.module.get_workflow_execution_results(ids=["nope"], skip_fields=None)

        self.assertIn("error", result)
        self.assertIn("execution ID 'nope' not found", result["error"])

    # --- execute_workflow ---

    def _execute(self, **overrides):
        """Call execute_workflow with every Field parameter set explicitly.

        Pydantic defaults do not resolve on a direct method call, so each
        parameter has to be passed.
        """
        kwargs = {
            "definition_id": None,
            "name": None,
            "parameters": None,
            "key": None,
            "depth": None,
            "source_event_url": None,
        }
        kwargs.update(overrides)
        return self.module.execute_workflow(**kwargs)

    def test_execute_requires_an_identifier(self):
        """Neither definition_id nor name is a local error and makes no API call."""
        result = self._execute()

        self.assertIn("error", result)
        self.assertIn("definition_id", result["error"])
        self.mock_client.command.assert_not_called()

    def test_execute_rejects_both_identifiers(self):
        """Both definition_id and name is a local error and makes no API call."""
        result = self._execute(definition_id="d1", name="Contain Host")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_execute_treats_blank_identifier_as_absent(self):
        """A blank `name` is not sent alongside a real `definition_id`.

        The exactly-one-of check treats "" as absent, and prepare_api_parameters
        drops only None — so without normalizing, both identifiers would reach the
        query string and the API would get an ambiguous request.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["e1"], "errors": []},
        }

        self._execute(definition_id="d1", name="", parameters={})

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(kwargs["parameters"], {"definition_id": "d1"})
        self.assertNotIn("name", kwargs["parameters"])

    def test_execute_rejects_two_blank_identifiers(self):
        """Two blank identifiers are still no identifier, and make no API call."""
        result = self._execute(definition_id="", name="")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_execute_splits_params_and_body(self):
        """definition_id is a query param and parameters is the body, verbatim."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": ["0e6a7a46545b926f3dff9fd2dab82fb3"],
                "errors": [],
                "meta": {"pagination": {"offset": 0, "limit": 0, "total": 0}},
            },
        }
        trigger_input = {"hash": "abc", "nested": {"a": [1, 2]}}

        result = self._execute(definition_id="d1", parameters=trigger_input)

        args, kwargs = self.mock_client.command.call_args
        self.assertEqual(args[0], "WorkflowExecute")
        self.assertEqual(kwargs["parameters"], {"definition_id": "d1"})
        self.assertEqual(kwargs["body"], trigger_input)
        self.assertEqual(result, [{"execution_id": "0e6a7a46545b926f3dff9fd2dab82fb3"}])

    def test_execute_sends_empty_body_when_no_parameters(self):
        """A workflow that takes no input still gets the required empty body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["e1"], "errors": []},
        }

        self._execute(definition_id="d1", parameters=None)

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(kwargs["body"], {})

    def test_execute_by_name_forwards_name(self):
        """The name route sends name as a query param and no definition_id."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["e1"], "errors": []},
        }

        self._execute(name="Testing 123", parameters={})

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(kwargs["parameters"], {"name": "Testing 123"})
        self.assertEqual(kwargs["body"], {})

    def test_execute_forwards_optional_query_params(self):
        """key, depth and source_event_url travel in the query string."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["e1"], "errors": []},
        }

        self._execute(
            definition_id="d1",
            parameters={},
            key="retry-key-1",
            depth=2,
            source_event_url="https://example.test/detection/1",
        )

        _, kwargs = self.mock_client.command.call_args
        self.assertEqual(
            kwargs["parameters"],
            {
                "definition_id": "d1",
                "key": "retry-key-1",
                "depth": 2,
                "source_event_url": "https://example.test/detection/1",
            },
        )

    def test_execute_wraps_bare_id_strings(self):
        """Bare execution-ID strings are labelled, never returned raw."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["aaa", "bbb"], "errors": []},
        }

        result = self._execute(definition_id="d1", parameters={})

        self.assertEqual(
            result, [{"execution_id": "aaa"}, {"execution_id": "bbb"}]
        )
        for entry in result:
            self.assertIsInstance(entry, dict)

    def test_execute_surfaces_schema_validation_message(self):
        """A 400 keeps the property name the API named, so a retry can be correct."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {
                "errors": [
                    {
                        "code": 400,
                        "message": (
                            "failed JSON schema validation: "
                            "[/required:hash is invalid, missing property 'hash']"
                        ),
                    }
                ]
            },
        }

        result = self._execute(definition_id="d1", parameters={})

        self.assertIn("error", result)
        self.assertIn("missing property 'hash'", result["error"])

    def test_execute_surfaces_disabled_definition_412(self):
        """The 412 for a disabled definition keeps its distinguishing message."""
        self.mock_client.command.return_value = {
            "status_code": 412,
            "body": {
                "errors": [
                    {
                        "code": 412,
                        "message": (
                            'workflow definition "b8b49f01" is disabled, '
                            "re-enable to allow running on-demand"
                        ),
                    }
                ],
                "resources": [],
            },
        }

        result = self._execute(definition_id="b8b49f01", parameters={})

        self.assertIn("error", result)
        self.assertIn("is disabled", result["error"])

    def test_execute_surfaces_ineligible_trigger_412(self):
        """The 412 for an ineligible trigger type keeps its own message."""
        self.mock_client.command.return_value = {
            "status_code": 412,
            "body": {
                "errors": [
                    {
                        "code": 412,
                        "message": (
                            'workflow definition "852849fa" is not an On-demand '
                            "or schedule triggered workflow"
                        ),
                    }
                ],
                "resources": [],
            },
        }

        result = self._execute(definition_id="852849fa", parameters={})

        self.assertIn("error", result)
        self.assertIn("not an On-demand or schedule triggered workflow", result["error"])


if __name__ == "__main__":
    unittest.main()
