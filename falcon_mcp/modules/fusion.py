"""
Fusion SOAR module for Falcon MCP Server

This module provides tools for searching Fusion SOAR workflow definitions and
executions, reading what an execution produced, and running an on-demand
workflow.

Required API scopes:
    - Workflows: read (search definitions, search executions, execution results)
    - Workflows: write (execute)
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.fusion import (
    SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION,
    SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class FusionModule(BaseModule):
    """Module for searching and running CrowdStrike Fusion SOAR workflows."""

    @staticmethod
    def _is_filter_error(error: dict[str, Any], filter_used: str | None) -> bool:
        """Report whether the FQL guide is the right answer to an API error.

        Three conditions must all hold. Only a 400 suggests bad syntax at all. A
        filter must actually have been sent, since the guide cannot help a caller
        who supplied none. And at least one raw API message must mention FQL,
        because these endpoints answer a rejected `sort` or an oversized `limit`
        with a 400 too, and pointing those at the filter guide sends the caller to
        rewrite the wrong parameter.

        Read the raw messages under `details.body.errors`, not the composed
        `error` string: `handle_api_response` prefixes every 400 with boilerplate
        that itself mentions FQL, so the composed string always matches.

        The FQL check is keyed to the one filter-error format these endpoints were
        observed to return, `"Invalid FQL: fql: <field> is an unknown property"`.
        If the API ever rewords it the guide would stop being offered; the raw
        message still names the offending field, so a caller is not stranded.

        Args:
            error: An error dict from a search helper
            filter_used: The FQL filter the caller supplied, if any

        Returns:
            True when the FQL guide should be returned inline
        """
        details = error.get("details") or {}
        if details.get("status_code") != 400:
            return False
        if not filter_used:
            return False
        api_errors = (details.get("body") or {}).get("errors") or []
        return any("fql" in (item.get("message") or "").lower() for item in api_errors)

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_workflow_definitions,
            name="search_workflow_definitions",
        )

        self._add_tool(
            server=server,
            method=self.search_workflow_executions,
            name="search_workflow_executions",
        )

        self._add_tool(
            server=server,
            method=self.get_workflow_execution_results,
            name="get_workflow_execution_results",
        )

        # A workflow's effect is whatever its author put in it, and this server
        # cannot inspect the action graph before running it. Live on-demand
        # definitions include actions that disable identities and delete database
        # rows, so the reachable blast radius is destructive even though "execute"
        # does not sound like it. idempotentHint is False because a second call
        # starts a second run unless the caller reuses `key`.
        self._add_tool(
            server=server,
            method=self.execute_workflow,
            name="execute_workflow",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        definitions_fql_resource = TextResource(
            uri=AnyUrl("falcon://fusion/workflow-definitions/fql-guide"),
            name="falcon_search_workflow_definitions_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_workflow_definitions` tool."
            ),
            text=SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION,
        )

        executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://fusion/workflow-executions/fql-guide"),
            name="falcon_search_workflow_executions_fql_guide",
            description=(
                "Contains the guide for the `filter` param of the "
                "`falcon_search_workflow_executions` tool."
            ),
            text=SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, definitions_fql_resource)
        self._add_resource(server, executions_fql_resource)

    def search_workflow_definitions(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://fusion/workflow-definitions/fql-guide` "
                "for syntax. Match a workflow by name with `name.raw`, not `name`."
            ),
            examples={"enabled:true+trigger.type:'On demand'", "name.raw:*'*Exposure*'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="The maximum records to return. [1-500]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str = Field(
            default="last_modified_timestamp.desc",
            description=dedent("""
                Sort definitions using these options:

                name: Workflow name
                last_modified_timestamp: When the definition was last changed
                version: Definition version
                enabled: Whether the definition is enabled
                id: Definition ID

                Each was verified to reorder results. Sort either asc (ascending)
                or desc (descending), using the dot separator ('name.desc'). The
                pipe form ('name|desc') is rejected with a 400 here. A bare
                property defaults to descending. Nested fields such as
                trigger.type and name.raw are not sortable.

                Examples: 'last_modified_timestamp.desc', 'name.asc'
            """).strip(),
            examples={"last_modified_timestamp.desc", "name.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Fusion SOAR workflow definitions in your CrowdStrike environment.

        Use this to find a workflow to run or inspect, filtering on name, enabled
        state, trigger type, version, or last-modified time. Consult
        falcon://fusion/workflow-definitions/fql-guide before constructing filter
        expressions — matching a name needs `name.raw`, because `name` is analyzed
        and returns zero rows for an exact match. Returns full definition records
        including `id`, `name`, `enabled`, `version`, and the `trigger` block whose
        `parameters` field is the JSON Schema for that workflow's execute input.
        Records are large (a definition embeds its whole action configuration), so
        narrow the filter rather than raising the limit; one definition can appear
        as several rows, one per version, so a result set may hold more rows than
        the limit.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        definitions, pagination = self._base_search_with_meta(
            operation="WorkflowDefinitionsCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow definitions",
        )

        if self._is_error(definitions):
            if self._is_filter_error(definitions, filter):
                return self._format_fql_error_response(
                    [definitions], filter, SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION
                )
            return definitions

        return self._build_pagination_envelope(definitions or [], pagination, filter)

    def search_workflow_executions(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://fusion/workflow-executions/fql-guide` "
                "for syntax. Filter status with `ui_status`, not `status`."
            ),
            examples={"ui_status:'Completed'", "started_timestamp:>'now-7d'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="The maximum records to return. [1-500]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str = Field(
            default="started_timestamp.desc",
            description=dedent("""
                Sort executions using these options:

                started_timestamp: When the run started
                completed_timestamp: When the run finished
                definition_id: ID of the definition that ran
                definition_name: Name of the definition that ran
                definition_version: Version of the definition that ran
                ui_status: Displayed run status
                status: Internal run status
                id: Execution ID

                Each was verified to reorder results. Sort either asc (ascending)
                or desc (descending), using the dot separator
                ('started_timestamp.desc'). The pipe form
                ('started_timestamp|desc') is rejected with a 400 here. A bare
                property defaults to descending.

                Prefer descending on a long history: ascending reaches the oldest
                records first, and a matched execution that is no longer
                retrievable fails the whole call with a 404.

                Examples: 'started_timestamp.desc', 'completed_timestamp.desc'
            """).strip(),
            examples={"started_timestamp.desc", "completed_timestamp.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Fusion SOAR workflow execution history in your CrowdStrike environment.

        Use this to see whether a workflow ran and how it finished, filtering on
        definition, status, or start/finish time. Consult
        falcon://fusion/workflow-executions/fql-guide before constructing filter
        expressions — several fields are named differently in the filter than in
        the response (`id` vs `execution_id`, `started_timestamp` vs
        `start_timestamp`), and status must be filtered via `ui_status`, since
        `status` uses a separate internal vocabulary. Returns full execution
        records including `execution_id`, `definition_id`, `status`, timestamps,
        and per-activity state. Records are large (an execution embeds the whole
        triggering event), so narrow the filter rather than raising the limit, and
        note `pagination.total` saturates at 10000, so exactly 10000 means "at
        least 10000" rather than an exact count.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        executions, pagination = self._base_search_with_meta(
            operation="WorkflowExecutionsCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow executions",
        )

        if self._is_error(executions):
            if self._is_filter_error(executions, filter):
                return self._format_fql_error_response(
                    [executions], filter, SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION
                )
            return executions

        return self._build_pagination_envelope(executions or [], pagination, filter)

    def get_workflow_execution_results(
        self,
        ids: list[str] = Field(
            description=(
                "Workflow execution IDs to read results for, up to 500. Returned by "
                "falcon_execute_workflow as `execution_id`, or by "
                "falcon_search_workflow_executions."
            ),
        ),
        skip_fields: list[str] | None = Field(
            default=None,
            description=(
                "Sections to omit from each record to shrink the response. Any of "
                "'trigger', 'activities', 'flows', 'submodels'. Omitting 'trigger' "
                "drops the embedded triggering event, which is usually the largest "
                "part; do not omit 'activities' if you want the per-activity results."
            ),
            examples={"trigger"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Read what one or more Fusion SOAR workflow executions produced.

        Use this to look up executions directly by ID — up to 500 at once, with no
        filter to construct — and to read each activity's own `result` payload:
        ticket numbers, script output, API responses. This is the step after
        falcon_execute_workflow, which returns only an execution ID. Returns the
        full execution records including `status` and every activity's result;
        `skip_fields` trims the largest sections when the records are too big. A run
        still going reports `status` 'In progress': report that state back rather
        than re-polling in a tight loop. 'Completed' and 'Failed' are terminal;
        'Action required' means the run is waiting on a human, so polling will never
        finish it.
        """
        return self._base_search_api_call(
            operation="WorkflowExecutionResults",
            search_params={
                "ids": ids,
                "skip_fields": skip_fields,
            },
            error_message="Failed to get workflow execution results",
        )

    def execute_workflow(
        self,
        definition_id: str | None = Field(
            default=None,
            description=(
                "Workflow definition ID to execute. Provide this or `name`. Look it up "
                "with falcon_search_workflow_definitions."
            ),
        ),
        name: str | None = Field(
            default=None,
            description=(
                "Workflow name to execute. Provide this or `definition_id`. Prefer "
                "`definition_id` — names are not guaranteed unique."
            ),
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Trigger input for the workflow, sent verbatim as the request body. The "
                "accepted keys are defined by the workflow, not by this tool: read "
                "`trigger.parameters` on the definition (from "
                "falcon_search_workflow_definitions) for its JSON Schema and required "
                "fields. Pass {} for a workflow that takes no input."
            ),
        ),
        key: str | None = Field(
            default=None,
            description=(
                "Idempotency key used to deduplicate executions. Reuse the same key when "
                "retrying so the retry returns the original execution instead of starting "
                "a second run."
            ),
        ),
        depth: int | None = Field(
            default=None,
            ge=0,
            le=4,
            description="Execution depth guard for workflows that trigger workflows. Max 4.",
        ),
        source_event_url: str | None = Field(
            default=None,
            description="URL of the source that led to this execution, recorded as provenance.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Start a Fusion SOAR workflow by definition ID.

        Use this to run a workflow a team has already built and reviewed — notifying
        a channel, opening a ticket, or running a containment sequence. What this
        tool does depends entirely on the workflow you name and cannot be known from
        this tool's name: a workflow may contain a host, disable an identity, or
        notify third parties. Confirm the definition with
        falcon_search_workflow_definitions and check its `trigger.parameters`,
        `enabled` and `version` first; prefer a `trigger.type` of 'On demand', and
        note the API refuses a disabled definition or a 'Signal'-triggered one with
        a 412 whose message says which. Match `parameters` to `trigger.parameters`
        exactly — a missing required field is rejected and starts nothing, but a
        wrong type or malformed value is accepted and starts a real run. Returns
        `[{"execution_id": "<id>"}]`; the run is asynchronous, so read the outcome
        with falcon_get_workflow_execution_results.
        """
        if bool(definition_id) == bool(name):
            return _format_error_response(
                "Provide exactly one of `definition_id` or `name`.",
                operation="WorkflowExecute",
            )

        query_params = prepare_api_parameters(
            {
                # Normalized to None so a blank string is not sent alongside the
                # identifier that was actually supplied; the check above already
                # treats "" as absent, and prepare_api_parameters drops only None.
                "definition_id": definition_id or None,
                "name": name or None,
                "key": key,
                "depth": depth,
                "source_event_url": source_event_url,
            }
        )

        # `body` is required by the endpoint but legitimately empty for a workflow
        # that declares no trigger.parameters, so it is passed explicitly rather
        # than through a helper that drops a falsy body.
        response = self.client.command(
            "WorkflowExecute",
            parameters=query_params,
            body=parameters or {},
        )

        result = handle_api_response(
            response,
            operation="WorkflowExecute",
            error_message="Failed to execute workflow",
            default_result=[],
        )

        if self._is_error(result):
            return result

        # The API returns bare execution-ID strings, not entities. Label them so the
        # declared return type holds and the ID can be fed to
        # falcon_get_workflow_execution_results.
        return [{"execution_id": execution_id} for execution_id in result]
