"""
AgentWorks module for Falcon MCP Server

This module provides tools for calling, listing, and observing CrowdStrike
AgentWorks (agentic-studio) Charlotte AI agents and their execution traces.

Required API scopes:
    - Charlotte AI Agent Definition: read (search/get/observe)
    - Charlotte AI Agent Definition: write (invoke)

None of these operations are wrapped by FalconPy, so every call uses the
`override="METHOD,/route"` raw-request escape hatch (precedent: cloud.py
suppression rules).
"""

import asyncio
import os
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.agentworks import (
    SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_DOCUMENTATION,
    SEARCH_AGENTWORKS_AGENTS_FQL_DOCUMENTATION,
    SEARCH_AGENTWORKS_SPANS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)

# Route for polling a running invocation, shared by the invoke tools and the
# standalone get-invocation tool.
_GET_INVOCATION_OP = "GetAgentInvocationV3"
_GET_INVOCATION_ROUTE = "/agentic-studio/entities/agent-invocations/v3"

# EntitiesSpansV1 accepts at most 1000 ids per fetch.
_SPANS_MAX_LIMIT = 1000

# API rejects an invocation deadline below 90 seconds with a 400.
_MIN_DEADLINE_SECONDS = 90

# Blocking-poll configuration (patchable in tests).
#
# The default timeout is deliberately below the MCP client request timeout (60s,
# see the note on `offload_to_thread` in modules/base.py). A run that outlives the
# client timeout is killed mid-call, so the timeout branch never returns and the
# invocation id is lost — while the agent keeps running and spending credits
# server-side, with no cancel operation and no way to look the run up again. 45s of
# poll budget leaves room for the invoke POST and the polls themselves to finish
# inside 60s, so the id always comes back. Raise FALCON_MCP_AGENTWORKS_TIMEOUT only
# on a client that allows longer calls.
#
# The poll interval floors at 1s: a 0 or negative value would never advance
# `elapsed`, turning the loop into an unthrottled poll of the invocation endpoint.
POLL_INTERVAL_SECONDS = max(1, int(os.environ.get("FALCON_MCP_AGENTWORKS_POLL_INTERVAL", "5")))
TIMEOUT_SECONDS = int(os.environ.get("FALCON_MCP_AGENTWORKS_TIMEOUT", "45"))


class AgentworksModule(BaseModule):
    """Module for calling and observing CrowdStrike AgentWorks agents."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_agentworks_agents,
            name="search_agentworks_agents",
        )

        self._add_tool(
            server=server,
            method=self.search_agentworks_agent_versions,
            name="search_agentworks_agent_versions",
        )

        self._add_tool(
            server=server,
            method=self.search_agentworks_spans,
            name="search_agentworks_spans",
        )

        self._add_tool(
            server=server,
            method=self.get_agentworks_agent_invocation,
            name="get_agentworks_agent_invocation",
        )

        # Invoking an agent runs it and spends credits — a launch/trigger action,
        # not read-only and not idempotent.
        self._add_tool(
            server=server,
            method=self.invoke_agentworks_agent,
            name="invoke_agentworks_agent",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        agents_fql_resource = TextResource(
            uri=AnyUrl("falcon://agentworks/agents/fql-guide"),
            name="falcon_search_agentworks_agents_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_agentworks_agents` tool."
            ),
            text=SEARCH_AGENTWORKS_AGENTS_FQL_DOCUMENTATION,
        )

        agent_versions_fql_resource = TextResource(
            uri=AnyUrl("falcon://agentworks/agent-versions/fql-guide"),
            name="falcon_search_agentworks_agent_versions_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_agentworks_agent_versions` tool."
            ),
            text=SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_DOCUMENTATION,
        )

        spans_fql_resource = TextResource(
            uri=AnyUrl("falcon://agentworks/spans/fql-guide"),
            name="falcon_search_agentworks_spans_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_agentworks_spans` tool."
            ),
            text=SEARCH_AGENTWORKS_SPANS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, agents_fql_resource)
        self._add_resource(server, agent_versions_fql_resource)
        self._add_resource(server, spans_fql_resource)

    def _search_agentworks(
        self,
        query_op: str,
        query_route: str,
        get_op: str,
        get_route: str,
        search_params: dict[str, Any],
        filter_used: str | None,
        fql_documentation: str,
        query_error_message: str,
        get_error_message: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Run a two-step query→fetch search against an agentic-studio endpoint.

        Mirrors `cloud.py::search_cspm_suppression_rules`: query IDs via the
        override GET route (capturing pagination before hydration drops it),
        fetch full entities by `ids`, then restore the query-step order.

        Args:
            query_op: Query operation label (for scope hints / logging)
            query_route: `/agentic-studio/queries/...` route for the override
            get_op: Entities-fetch operation label
            get_route: `/agentic-studio/entities/...` route for the override
            search_params: filter/limit/offset/sort for the query step
            filter_used: The FQL filter string, echoed back and used on errors
            fql_documentation: Guide returned inline on a filter error
            query_error_message: Error message for a failed query step
            get_error_message: Error message for a failed fetch step

        Returns:
            The pagination envelope, or an FQL-error dict on a query-step 400.
        """
        params = prepare_api_parameters(search_params)
        query_response = self.client.command(
            query_op,
            override=f"GET,{query_route}",
            parameters=params,
        )

        pagination = self._extract_pagination(query_response)

        query_result = handle_api_response(
            query_response,
            operation=query_op,
            error_message=query_error_message,
            default_result=[],
        )

        if self._is_error(query_result):
            return self._format_fql_error_response(
                [query_result],
                filter_used,
                fql_documentation,
            )

        if not query_result:
            return self._build_pagination_envelope([], pagination, filter_used)

        detail_params = prepare_api_parameters({"ids": query_result})
        detail_response = self.client.command(
            get_op,
            override=f"GET,{get_route}",
            parameters=detail_params,
        )

        details = handle_api_response(
            detail_response,
            operation=get_op,
            error_message=get_error_message,
            default_result=[],
        )

        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(query_result, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter_used)

    def search_agentworks_agents(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://agentworks/agents/fql-guide` "
                "for syntax."
            ),
            examples=["active_version.model:'bedrock.claude-4-6-sonnet'", "template_id:'ioc-review-agent'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of agents to return (default: 100; max: 500).",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return agents.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort agents. Supported field: created_date. Ex: 'created_date|desc'.",
            examples=["created_date|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for AgentWorks (Charlotte AI) agents in your CrowdStrike environment.

        Use this to list agents and find their IDs and active versions before invoking
        one or inspecting its versions. Filter by template, backing model, or published
        version — consult falcon://agentworks/agents/fql-guide before constructing filter
        expressions. Returns full agent details including active version and published
        version IDs.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).
        """
        return self._search_agentworks(
            query_op="QueryAgentsV2",
            query_route="/agentic-studio/queries/agents/v2",
            get_op="GetAgentsV2",
            get_route="/agentic-studio/entities/agents/v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            filter_used=filter,
            fql_documentation=SEARCH_AGENTWORKS_AGENTS_FQL_DOCUMENTATION,
            query_error_message="Failed to query AgentWorks agents",
            get_error_message="Failed to get AgentWorks agent details",
        )

    def search_agentworks_agent_versions(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See "
                "`falcon://agentworks/agent-versions/fql-guide` for syntax."
            ),
            examples=["agent_id:'467e856f-...'", "is_published:true"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of agent versions to return (default: 100; max: 500).",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return versions.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort versions. Supported field: created_at. Ex: 'created_at|desc'.",
            examples=["created_at|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for versions of AgentWorks agents.

        Use this to list an agent's versions (filter by `agent_id`) and find a specific
        `version_id` — for example to invoke a non-published version by passing that
        version_id to falcon_invoke_agentworks_agent. Filter by agent, name, model, or
        published/enabled state — consult falcon://agentworks/agent-versions/fql-guide
        before constructing filter expressions. Returns full version details.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).
        """
        return self._search_agentworks(
            query_op="QueryAgentVersionsV1",
            query_route="/agentic-studio/queries/agent-versions/v1",
            get_op="GetAgentVersionsV1",
            get_route="/agentic-studio/entities/agent-versions/v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            filter_used=filter,
            fql_documentation=SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_DOCUMENTATION,
            query_error_message="Failed to query AgentWorks agent versions",
            get_error_message="Failed to get AgentWorks agent version details",
        )

    def search_agentworks_spans(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://agentworks/spans/fql-guide` "
                "for syntax. ALWAYS filter — usually by trace_id."
            ),
            examples=["trace_id:'a1b2c3d4-...'", "trace_id:'...'+status:'error'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=_SPANS_MAX_LIMIT,
            description=(
                f"Maximum number of spans to return (default: 100; max: {_SPANS_MAX_LIMIT})."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return spans.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort spans. Supported field: start_time. Ex: 'start_time|desc'.",
            examples=["start_time|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search AgentWorks execution spans (traces) for observability.

        This is effectively a trace-scoped tool: spans number in the hundreds of
        thousands, so ALWAYS filter — the primary use is passing an invocation's
        `ai_trace_id` as `trace_id:'<value>'` to retrieve that run's spans (LLM calls,
        agent steps, cost, request/response content). You can further narrow by
        span_type, status, name, or duration_ms; note start_time is limited to the last
        90 days. Consult falcon://agentworks/spans/fql-guide before constructing filter
        expressions. Returns full span details.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).
        """
        return self._search_agentworks(
            query_op="QueriesSpansV1",
            query_route="/agentic-studio/queries/spans/v1",
            get_op="EntitiesSpansV1",
            get_route="/agentic-studio/entities/spans/v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            filter_used=filter,
            fql_documentation=SEARCH_AGENTWORKS_SPANS_FQL_DOCUMENTATION,
            query_error_message="Failed to query AgentWorks spans",
            get_error_message="Failed to get AgentWorks span details",
        )

    def get_agentworks_agent_invocation(
        self,
        id: str = Field(
            description=(
                "The invocation ID to retrieve. Returned by falcon_invoke_agentworks_agent "
                "(including on timeout or a tool-approval pause)."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get the current state of an AgentWorks agent invocation by ID.

        Use this to resume or observe a run that paused (waiting_for_tool_approval) or
        that timed out from falcon_invoke_agentworks_agent — poll it until `status` is
        terminal (completed/failed). Returns the invocation resource including status,
        conversation, ai_trace_id, and any tool approvals.
        """
        params = prepare_api_parameters({"id": id})
        response = self.client.command(
            _GET_INVOCATION_OP,
            override=f"GET,{_GET_INVOCATION_ROUTE}",
            parameters=params,
        )
        return handle_api_response(
            response,
            operation=_GET_INVOCATION_OP,
            error_message="Failed to get agent invocation",
            default_result=[],
        )

    async def _invoke_and_poll(
        self,
        invoke_op: str,
        invoke_route: str,
        body: dict[str, Any],
        error_message: str,
    ) -> dict[str, Any]:
        """Invoke an agent and block-poll the run to a terminal state.

        Captures `ai_trace_id` from the initial invoke response (it is present at
        status=processing but comes back null on the completed poll). Breaks early on
        waiting_for_tool_approval, and on timeout returns the invocation id so the
        run — which continues server-side, there being no cancel op — can be resumed
        via falcon_get_agentworks_agent_invocation.

        A 400 from the invoke POST is surfaced as-is rather than retried: the status
        covers genuine rejections (unknown agent, malformed body) that a retry only
        delays, and there is no reliable signal that distinguishes a transient one.

        Args:
            invoke_op: Invoke operation label
            invoke_route: `/agentic-studio/entities/...` route for the override
            body: Request body (id, messages, optional deadline/credit limits)
            error_message: Error message for a failed invoke

        Returns:
            A dict with id, status, ai_trace_id and (per outcome) conversation,
            hint, or note.
        """
        invoke_response = await self.client.command_async(
            operation=invoke_op,
            override=f"POST,{invoke_route}",
            body=body,
        )

        if invoke_response.get("status_code") != 200:
            return handle_api_response(
                invoke_response,
                operation=invoke_op,
                error_message=error_message,
                default_result=[],
            )

        resources = invoke_response.get("body", {}).get("resources", [])
        if not resources:
            return _format_error_response(
                message=f"{error_message}: no invocation returned",
                details=invoke_response.get("body", {}),
                operation=invoke_op,
            )

        invocation = resources[0]
        inv_id = invocation.get("id")
        if not inv_id:
            return _format_error_response(
                message=f"{error_message}: invocation returned without an id",
                details=invoke_response.get("body", {}),
                operation=invoke_op,
            )
        # ai_trace_id is present here (status=processing); it is null on the
        # completed poll, so capture it now and thread it through every return.
        ai_trace_id = invocation.get("ai_trace_id")

        elapsed = 0.0
        status = invocation.get("status")
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            poll_response = await self.client.command_async(
                operation=_GET_INVOCATION_OP,
                override=f"GET,{_GET_INVOCATION_ROUTE}",
                parameters={"id": inv_id},
            )

            if poll_response.get("status_code") != 200:
                return handle_api_response(
                    poll_response,
                    operation=_GET_INVOCATION_OP,
                    error_message="Failed to poll agent invocation status",
                    default_result=[],
                )

            poll_resources = poll_response.get("body", {}).get("resources", [])
            invocation = poll_resources[0] if poll_resources else {}
            status = invocation.get("status")

            if status == "completed":
                return {
                    "id": inv_id,
                    "status": status,
                    "ai_trace_id": ai_trace_id,
                    "conversation": invocation.get("conversation", []),
                    "hint": (
                        "Pass ai_trace_id as trace_id to falcon_search_agentworks_spans "
                        "to see this run's spans."
                    ),
                }
            if status == "failed":
                return {
                    "id": inv_id,
                    "status": status,
                    "ai_trace_id": ai_trace_id,
                    "conversation": invocation.get("conversation", []),
                }
            if status == "waiting_for_tool_approval":
                return {
                    "id": inv_id,
                    "status": status,
                    "ai_trace_id": ai_trace_id,
                    "note": (
                        "Invocation is paused waiting for tool approval. Approving a "
                        "tool is not supported; observe the run via "
                        "falcon_get_agentworks_agent_invocation."
                    ),
                }

        # Timeout: there is no stop/cancel op, so the run continues server-side.
        # Hand back the id + last status so it can be resumed/observed.
        return {
            # `status` is None when every poll returned an empty resources list —
            # report that as unknown rather than guessing "processing".
            "id": inv_id,
            "status": status or "unknown",
            "ai_trace_id": ai_trace_id,
            "timeout_seconds": TIMEOUT_SECONDS,
            "note": (
                f"Invocation still running after {TIMEOUT_SECONDS}s; it continues "
                "server-side. Resume/observe via falcon_get_agentworks_agent_invocation "
                "with this id."
            ),
        }

    async def invoke_agentworks_agent(
        self,
        prompt: str = Field(
            description="The user message to send to the agent.",
            examples=["Reply OK", "Summarize the latest critical detections"],
        ),
        agent_id: str = Field(
            description=(
                "ID of the agent to invoke. Find IDs with falcon_search_agentworks_agents."
            ),
        ),
        version_id: str | None = Field(
            default=None,
            description=(
                "Optional ID of a specific agent version to invoke, for testing a "
                "version that is not published. Omit to invoke the agent's published "
                "version. Find version IDs with falcon_search_agentworks_agent_versions."
            ),
        ),
        deadline_seconds: int | None = Field(
            default=None,
            description=(
                "Optional server-side deadline for the run, in seconds. Must be at "
                f"least {_MIN_DEADLINE_SECONDS} (the API rejects smaller values)."
            ),
        ),
        credit_cents_limit: int | None = Field(
            default=None,
            description="Optional cap on credits (in cents) the run may spend.",
        ),
    ) -> dict[str, Any]:
        """Invoke an AgentWorks (Charlotte AI) agent and return its reply.

        Use this to actually run an agent on a prompt: it invokes the agent's published
        version, or a specific version when you pass version_id. This is asynchronous and
        spends credits — it starts the run and blocks, polling until the agent finishes
        (timeout FALCON_MCP_AGENTWORKS_TIMEOUT, default 45s, kept under the MCP client
        request timeout). Returns the invocation id, status, conversation, and ai_trace_id —
        feed ai_trace_id to falcon_search_agentworks_spans to observe the run. If the run
        pauses for tool approval (approving a tool is not supported) or exceeds the timeout,
        it returns the id and status so you can resume or observe the run with
        falcon_get_agentworks_agent_invocation; the run continues server-side either way.
        """
        # Dispatch on version_id: the published-agent and specific-version invocations
        # are separate operations with separate routes.
        if version_id is None:
            invoke_op = "InvokePublishedAgentExternalV1"
            invoke_route = "/agentic-studio/entities/agent-invocations/v1"
        else:
            invoke_op = "InvokeAgentVersionExternalV1"
            invoke_route = "/agentic-studio/entities/agent-version-invocations/v1"

        if deadline_seconds is not None and deadline_seconds < _MIN_DEADLINE_SECONDS:
            return _format_error_response(
                message=(
                    f"deadline_seconds must be at least {_MIN_DEADLINE_SECONDS} "
                    f"(got {deadline_seconds})"
                ),
                operation=invoke_op,
            )

        body: dict[str, Any] = {
            "id": agent_id,
            "messages": [{"role": "user", "content": prompt}],
        }
        if version_id is not None:
            body["version_id"] = version_id
        if deadline_seconds is not None:
            body["deadline_seconds"] = deadline_seconds
        if credit_cents_limit is not None:
            body["credit_cents_limit"] = credit_cents_limit

        return await self._invoke_and_poll(
            invoke_op=invoke_op,
            invoke_route=invoke_route,
            body=body,
            error_message="Failed to invoke AgentWorks agent",
        )
