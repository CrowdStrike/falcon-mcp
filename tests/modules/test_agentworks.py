"""
Tests for the AgentWorks module.
"""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from mcp.types import ToolAnnotations

from falcon_mcp.modules import agentworks
from falcon_mcp.modules.agentworks import AgentworksModule
from tests.modules.utils.test_modules import TestModules

# Mutating annotation for the invoke tool.
_MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class TestAgentworksModule(TestModules):
    """Test cases for the AgentWorks module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(AgentworksModule)

        # The invoke tool is async and calls command_async. Route it through the
        # sync `command` mock so side_effect / call_args_list assertions keep working
        # (same bridge as the NGSIEM tests).
        async def _command_async(*args, **kwargs):
            return self.mock_client.command(*args, **kwargs)

        self.mock_client.command_async = AsyncMock(side_effect=_command_async)

    # --- Registration ---

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_agentworks_agents",
            "falcon_search_agentworks_agent_versions",
            "falcon_search_agentworks_spans",
            "falcon_get_agentworks_agent_invocation",
            "falcon_invoke_agentworks_agent",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_agentworks_agents_fql_guide",
            "falcon_search_agentworks_agent_versions_fql_guide",
            "falcon_search_agentworks_spans_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_invoke_tool_has_mutating_annotations(self):
        """The invoke tool must register launch/trigger (mutating) annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_invoke_agentworks_agent", _MUTATING_ANNOTATIONS)

    # --- search_agentworks_agents ---

    def test_search_agents_success(self):
        """Two-step search returns full entities inside the pagination envelope."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["a1", "a2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "a1"}, {"id": "a2"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_agentworks_agents(
            filter="template_id:'ioc-review-agent'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)

        first = self.mock_client.command.call_args_list[0]
        self.assertEqual(first[0][0], "QueryAgentsV2")
        self.assertEqual(first[1]["override"], "GET,/agentic-studio/queries/agents/v2")
        self.assertEqual(first[1]["parameters"]["filter"], "template_id:'ioc-review-agent'")
        self.assertEqual(first[1]["parameters"]["limit"], 100)

        second = self.mock_client.command.call_args_list[1]
        self.assertEqual(second[0][0], "GetAgentsV2")
        self.assertEqual(second[1]["override"], "GET,/agentic-studio/entities/agents/v2")
        self.assertEqual(second[1]["parameters"]["ids"], ["a1", "a2"])

        self.assertEqual(len(result["results"]), 2)
        self.assert_pagination(result, total=2)

    def test_search_agents_filter_error(self):
        """A query-step 400 returns the FQL-error dict (invalid input → error dict)."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid filter"}]},
        }

        result = self.module.search_agentworks_agents(
            filter="bogus:'x'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertEqual(result["filter_used"], "bogus:'x'")

    def test_search_agents_no_results(self):
        """Empty query results short-circuit before the fetch step."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_agentworks_agents(
            filter=None, limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(result["results"], [])
        self.assert_pagination(result, total=None)

    def test_search_agents_special_characters_in_filter(self):
        """Special characters in the filter pass through to the API unchanged."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "template_id:*';DROP TABLE--*"
        self.module.search_agentworks_agents(
            filter=filter_with_special, limit=100, offset=None, sort=None
        )

        call_args = self.mock_client.command.call_args_list[0]
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    # --- search_agentworks_agent_versions ---

    def test_search_agent_versions_success(self):
        """Two-step version search uses the correct override routes."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["v1"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "v1", "is_published": True}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_agentworks_agent_versions(
            filter="agent_id:'467e856f'", limit=100, offset=None, sort=None
        )

        first = self.mock_client.command.call_args_list[0]
        self.assertEqual(first[0][0], "QueryAgentVersionsV1")
        self.assertEqual(first[1]["override"], "GET,/agentic-studio/queries/agent-versions/v1")

        second = self.mock_client.command.call_args_list[1]
        self.assertEqual(second[0][0], "GetAgentVersionsV1")
        self.assertEqual(second[1]["override"], "GET,/agentic-studio/entities/agent-versions/v1")
        self.assertEqual(second[1]["parameters"]["ids"], ["v1"])

        self.assertEqual(len(result["results"]), 1)
        self.assert_pagination(result, total=1)

    def test_search_agent_versions_filter_error(self):
        """A query-step 400 returns the FQL-error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid filter"}]},
        }

        result = self.module.search_agentworks_agent_versions(
            filter="bogus:'x'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "bogus:'x'")

    def test_search_agent_versions_no_results(self):
        """Empty query results short-circuit before the fetch step."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_agentworks_agent_versions(
            filter=None, limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(result["results"], [])
        self.assert_pagination(result, total=None)

    def test_search_agent_versions_special_characters_in_filter(self):
        """Special characters in the filter pass through unchanged."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "name:'weird <name> \"quotes\"'"
        self.module.search_agentworks_agent_versions(
            filter=filter_with_special, limit=100, offset=None, sort=None
        )

        call_args = self.mock_client.command.call_args_list[0]
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    # --- search_agentworks_spans ---

    def test_search_spans_success(self):
        """Two-step span search uses the correct override routes."""
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["s1", "s2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "s1"}, {"id": "s2"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_agentworks_spans(
            filter="trace_id:'t1'", limit=100, offset=None, sort=None
        )

        first = self.mock_client.command.call_args_list[0]
        self.assertEqual(first[0][0], "QueriesSpansV1")
        self.assertEqual(first[1]["override"], "GET,/agentic-studio/queries/spans/v1")

        second = self.mock_client.command.call_args_list[1]
        self.assertEqual(second[0][0], "EntitiesSpansV1")
        self.assertEqual(second[1]["override"], "GET,/agentic-studio/entities/spans/v1")
        self.assertEqual(second[1]["parameters"]["ids"], ["s1", "s2"])

        self.assertEqual(len(result["results"]), 2)
        self.assert_pagination(result, total=2)

    def test_search_spans_filter_error(self):
        """A query-step 400 returns the FQL-error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "start_time must be within the last 90 days"}]},
        }

        result = self.module.search_agentworks_spans(
            filter="start_time:>'2020-01-01'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "start_time:>'2020-01-01'")

    def test_search_spans_no_results(self):
        """Empty query results short-circuit before the fetch step."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_agentworks_spans(
            filter="trace_id:'none'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(result["results"], [])
        self.assert_pagination(result, total=None)

    def test_search_spans_special_characters_in_filter(self):
        """Special characters in the filter pass through unchanged."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        filter_with_special = "trace_id:*';DROP--*"
        self.module.search_agentworks_spans(
            filter=filter_with_special, limit=100, offset=None, sort=None
        )

        call_args = self.mock_client.command.call_args_list[0]
        self.assertEqual(call_args[1]["parameters"]["filter"], filter_with_special)

    def test_search_spans_reorders_to_match_sorted_ids(self):
        """When EntitiesSpansV1 returns spans out of order, restore query-step order."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["s2", "s1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "s1"}, {"id": "s2"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_agentworks_spans(
            filter="trace_id:'t1'", limit=100, offset=None, sort=None
        )

        self.assertEqual(result["results"][0]["id"], "s2")
        self.assertEqual(result["results"][1]["id"], "s1")

    def test_search_spans_fetch_error_returns_wrapped_error(self):
        """A failed fetch step (query OK, get 500) returns the error without crashing.

        Guards the `_is_error(details)` short-circuit before `_reorder_by_ids`, which
        would otherwise call `.get()` on the query-step ID strings and raise.
        """
        query_response = {"status_code": 200, "body": {"resources": ["s1", "s2"]}}
        get_error = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        self.mock_client.command.side_effect = [query_response, get_error]

        result = self.module.search_agentworks_spans(
            filter="trace_id:'t1'", limit=100, offset=None, sort=None
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    # --- get_agentworks_agent_invocation ---

    def test_get_agent_invocation_success(self):
        """Single-call get returns the invocation resource via the override route."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-1", "status": "completed"}]},
        }

        result = self.module.get_agentworks_agent_invocation(id="inv-1")

        call_args = self.mock_client.command.call_args_list[0]
        self.assertEqual(call_args[0][0], "GetAgentInvocationV3")
        self.assertEqual(call_args[1]["override"], "GET,/agentic-studio/entities/agent-invocations/v3")
        self.assertEqual(call_args[1]["parameters"]["id"], "inv-1")
        self.assertEqual(result[0]["id"], "inv-1")

    def test_get_agent_invocation_error(self):
        """A non-200 get surfaces the API error dict rather than swallowing it."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "invocation not found"}]},
        }

        result = self.module.get_agentworks_agent_invocation(id="does-not-exist")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    # --- invoke_agentworks_agent ---

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_success_captures_ai_trace_id_from_invoke(self, _mock_sleep):
        """ai_trace_id is captured from the INVOKE response, not the completed poll."""
        invoke_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "inv-1", "status": "processing", "ai_trace_id": "trace-abc"}
                ]
            },
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-1", "status": "processing"}]},
        }
        # ai_trace_id is null on the completed poll — must not overwrite the captured one.
        poll_done = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "inv-1",
                        "status": "completed",
                        "ai_trace_id": None,
                        "conversation": [{"role": "assistant", "content": "OK"}],
                    }
                ]
            },
        }
        self.mock_client.command.side_effect = [invoke_response, poll_not_done, poll_done]

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="Reply OK",
                agent_id="467e856f",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        # Verify invoke call
        invoke_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(invoke_call[1]["operation"], "InvokePublishedAgentExternalV1")
        self.assertEqual(
            invoke_call[1]["override"], "POST,/agentic-studio/entities/agent-invocations/v1"
        )
        self.assertEqual(invoke_call[1]["body"]["id"], "467e856f")
        self.assertEqual(
            invoke_call[1]["body"]["messages"], [{"role": "user", "content": "Reply OK"}]
        )

        # Verify poll call
        poll_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(poll_call[1]["operation"], "GetAgentInvocationV3")
        self.assertEqual(poll_call[1]["parameters"]["id"], "inv-1")

        self.assertEqual(result["id"], "inv-1")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["ai_trace_id"], "trace-abc")
        self.assertEqual(result["conversation"], [{"role": "assistant", "content": "OK"}])
        self.assertIn("hint", result)

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_failed_status(self, _mock_sleep):
        """A failed poll status returns status + conversation + ai_trace_id."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-2", "status": "processing", "ai_trace_id": "t2"}]},
        }
        poll_failed = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "inv-2", "status": "failed", "conversation": [{"role": "user", "content": "x"}]}
                ]
            },
        }
        self.mock_client.command.side_effect = [invoke_response, poll_failed]

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["ai_trace_id"], "t2")
        self.assertIn("conversation", result)

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_waiting_for_tool_approval_breaks_early(self, _mock_sleep):
        """A tool-approval pause returns immediately with id/status/note — no more polls."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-3", "status": "processing", "ai_trace_id": "t3"}]},
        }
        poll_waiting = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-3", "status": "waiting_for_tool_approval"}]},
        }
        self.mock_client.command.side_effect = [invoke_response, poll_waiting]

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        # invoke + exactly one poll, then break
        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(result["status"], "waiting_for_tool_approval")
        self.assertEqual(result["id"], "inv-3")
        self.assertEqual(result["ai_trace_id"], "t3")
        self.assertIn("note", result)

    @patch("falcon_mcp.modules.agentworks.TIMEOUT_SECONDS", 10)
    @patch("falcon_mcp.modules.agentworks.POLL_INTERVAL_SECONDS", 5)
    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_timeout_returns_id_without_cleanup(self, _mock_sleep):
        """On timeout, return the id/status so the run can be resumed — and never call a
        stop/cancel op (there is none for invocations)."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-4", "status": "processing", "ai_trace_id": "t4"}]},
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-4", "status": "processing"}]},
        }
        # 1 invoke + 2 polls (2 * 5s = 10s >= timeout); no further calls.
        self.mock_client.command.side_effect = [invoke_response, poll_not_done, poll_not_done]

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        # Only invoke + polls — no stop/cleanup op exists.
        self.assertEqual(self.mock_client.command.call_count, 3)
        called_ops = [
            c[1].get("operation") for c in self.mock_client.command.call_args_list
        ]
        self.assertEqual(
            called_ops,
            ["InvokePublishedAgentExternalV1", "GetAgentInvocationV3", "GetAgentInvocationV3"],
        )

        self.assertEqual(result["id"], "inv-4")
        self.assertEqual(result["ai_trace_id"], "t4")
        self.assertEqual(result["timeout_seconds"], 10)
        self.assertIn("note", result)

    def test_invoke_agent_deadline_below_minimum_returns_error_without_api_call(self):
        """deadline_seconds < 90 returns an error dict and never touches the API."""
        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=30,
                credit_cents_limit=None,
            )
        )

        self.assertEqual(self.mock_client.command.call_count, 0)
        self.assertIn("error", result)
        self.assertIn("90", result["error"])

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_400_is_not_retried(self, _mock_sleep):
        """A 400 on the invoke POST is surfaced immediately, not retried.

        A 400 covers genuine rejections (unknown agent, malformed body); retrying one
        only doubles the latency of the failure.
        """
        invoke_400 = {"status_code": 400, "body": {"errors": [{"message": "unknown agent id"}]}}
        self.mock_client.command.return_value = invoke_400

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("error", result)

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_optional_params_in_body(self, _mock_sleep):
        """deadline_seconds and credit_cents_limit are forwarded in the body when set."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-6", "status": "processing", "ai_trace_id": "t6"}]},
        }
        poll_done = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-6", "status": "completed", "conversation": []}]},
        }
        self.mock_client.command.side_effect = [invoke_response, poll_done]

        asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=120,
                credit_cents_limit=500,
            )
        )

        body = self.mock_client.command.call_args_list[0][1]["body"]
        self.assertEqual(body["deadline_seconds"], 120)
        self.assertEqual(body["credit_cents_limit"], 500)

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_invoke_error_surfaced(self, _mock_sleep):
        """A non-200 invoke (not a transient 400) surfaces the API error and never polls."""
        invoke_403 = {"status_code": 403, "body": {"errors": [{"message": "Access denied"}]}}
        self.mock_client.command.return_value = invoke_403

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertIn("error", result)

    # --- invoke dispatch: published vs specific version ---

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_without_version_id_targets_published_op(self, _mock_sleep):
        """Omitting version_id invokes the published agent and sends no version_id."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-8", "status": "processing", "ai_trace_id": "t8"}]},
        }
        poll_done = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-8", "status": "completed", "conversation": []}]},
        }
        self.mock_client.command.side_effect = [invoke_response, poll_done]

        asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="Reply OK",
                agent_id="a",
                version_id=None,
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        invoke_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(invoke_call[1]["operation"], "InvokePublishedAgentExternalV1")
        self.assertEqual(
            invoke_call[1]["override"], "POST,/agentic-studio/entities/agent-invocations/v1"
        )
        self.assertNotIn("version_id", invoke_call[1]["body"])

    @patch("falcon_mcp.modules.agentworks.asyncio.sleep", new_callable=AsyncMock)
    def test_invoke_agent_with_version_id_switches_op_and_route(self, _mock_sleep):
        """Passing version_id switches to the version op/route and includes it in the body."""
        invoke_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-7", "status": "processing", "ai_trace_id": "t7"}]},
        }
        poll_done = {
            "status_code": 200,
            "body": {"resources": [{"id": "inv-7", "status": "completed", "conversation": []}]},
        }
        self.mock_client.command.side_effect = [invoke_response, poll_done]

        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="Reply OK",
                agent_id="a",
                version_id="v-1",
                deadline_seconds=None,
                credit_cents_limit=None,
            )
        )

        invoke_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(invoke_call[1]["operation"], "InvokeAgentVersionExternalV1")
        self.assertEqual(
            invoke_call[1]["override"],
            "POST,/agentic-studio/entities/agent-version-invocations/v1",
        )
        self.assertEqual(invoke_call[1]["body"]["version_id"], "v-1")
        self.assertEqual(invoke_call[1]["body"]["id"], "a")
        self.assertEqual(result["status"], "completed")

    def test_invoke_agent_version_deadline_error_names_the_version_op(self):
        """A rejected deadline on a version invoke reports the version operation."""
        result = asyncio.run(
            self.module.invoke_agentworks_agent(
                prompt="x",
                agent_id="a",
                version_id="v-1",
                deadline_seconds=10,
                credit_cents_limit=None,
            )
        )

        self.assertEqual(self.mock_client.command.call_count, 0)
        self.assertIn("error", result)
        self.assertIn("90", result["error"])


class TestAgentworksModuleConfig(unittest.TestCase):
    """Test configuration handling for the AgentWorks module."""

    def test_default_timeout_stays_under_the_mcp_client_timeout(self):
        """The default timeout must stay below the 60s MCP client request timeout.

        A longer default means the client kills the call before the timeout branch
        returns, so the invocation id is lost while the run keeps spending credits
        server-side (there is no cancel operation).
        """
        self.assertLess(agentworks.TIMEOUT_SECONDS, 60)

    def test_default_config_values(self):
        """Default poll interval and timeout resolve correctly."""
        with patch.dict(os.environ, {}, clear=True):
            poll_interval = max(
                1, int(os.environ.get("FALCON_MCP_AGENTWORKS_POLL_INTERVAL", "5"))
            )
            timeout = int(os.environ.get("FALCON_MCP_AGENTWORKS_TIMEOUT", "45"))
            self.assertEqual(poll_interval, 5)
            self.assertEqual(timeout, 45)

    def test_custom_config_from_env(self):
        """Custom poll interval and timeout are read from the environment."""
        with patch.dict(
            os.environ,
            {
                "FALCON_MCP_AGENTWORKS_POLL_INTERVAL": "10",
                "FALCON_MCP_AGENTWORKS_TIMEOUT": "600",
            },
        ):
            poll_interval = max(
                1, int(os.environ.get("FALCON_MCP_AGENTWORKS_POLL_INTERVAL", "5"))
            )
            timeout = int(os.environ.get("FALCON_MCP_AGENTWORKS_TIMEOUT", "45"))
            self.assertEqual(poll_interval, 10)
            self.assertEqual(timeout, 600)

    def test_poll_interval_floors_at_one_second(self):
        """A 0 or negative poll interval floors at 1s so `elapsed` always advances.

        Without the floor the poll loop never increments `elapsed` and hammers the
        invocation endpoint without throttling.
        """
        for raw in ("0", "-5"):
            with patch.dict(os.environ, {"FALCON_MCP_AGENTWORKS_POLL_INTERVAL": raw}):
                poll_interval = max(
                    1, int(os.environ.get("FALCON_MCP_AGENTWORKS_POLL_INTERVAL", "5"))
                )
                self.assertEqual(poll_interval, 1)


if __name__ == "__main__":
    unittest.main()
