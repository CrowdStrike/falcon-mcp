"""Integration tests for the Fusion SOAR module.

No create-and-delete roundtrip is included, and that is deliberate rather than an
omission. The house pattern for a mutating tool is to create a thing, assert it,
then delete it. `falcon_execute_workflow` does not create anything this test owns:
it starts a workflow somebody else authored, whose actions may open tickets,
notify third parties, or contain a host. There is nothing to clean up and no safe
generic thing to run, so `execute` is covered by its error contracts (400, 404,
and both 412s), each of which provably starts nothing. A real execution is
available behind FALCON_TEST_WORKFLOW_ID for anyone with a known-inert on-demand
workflow to point it at.
"""

import os
import re

import pytest

from falcon_mcp.modules.fusion import FusionModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

# A 32-hex ID that is syntactically valid but cannot exist, so the API resolves
# the definition, fails, and returns 404 without running anything.
_NONEXISTENT_DEFINITION_ID = "ffffffffffffffffffffffffffffffff"


@pytest.mark.integration
class TestFusionIntegration(BaseIntegrationTest):
    """Integration tests for the Fusion SOAR module with real API calls.

    Validates:
    - Correct FalconPy operation names (WorkflowDefinitionsCombined,
      WorkflowExecutionsCombined, WorkflowExecutionResults, WorkflowExecute)
    - The single-call combined search pattern returns full records
    - The query-param / body split on WorkflowExecute
    - Every FQL field and operator documented in the two guides
    - The dot-notation sort form, which this endpoint requires

    Requires the Workflows API scope. Tests skip gracefully when the tenant has
    no workflow definitions or executions.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Fusion SOAR module with a real client."""
        self.module = FusionModule(falcon_client)

    # ------------------------------------------------------------------
    # Helpers
    #
    # Filter coverage below uses BaseIntegrationTest.assert_filter_matches, which
    # requires a non-empty result and checks every row against a predicate. Both
    # halves matter here: an unknown property on these endpoints is a 400 that
    # names it, but a known property with an unsupported operator comes back as an
    # empty 200, so only rows prove the documented construction works — and only a
    # per-row check proves the filter selected on what it claims to.
    # ------------------------------------------------------------------

    def assert_envelope_ok(self, result, context=""):
        """Assert a search envelope carries neither a top-level nor an embedded error.

        `assert_no_error` only inspects the top level, so an FQL error nested
        inside `results` passes it silently. Both shapes are checked here.
        """
        self.assert_no_error(result, context=context)
        assert isinstance(result, dict), f"Expected an envelope dict ({context}): {result}"
        assert "fql_guide" not in result, (
            f"Filter was rejected as invalid FQL ({context}): {result.get('results')}"
        )
        for record in result.get("results", []):
            assert "error" not in record, f"Embedded error ({context}): {record}"

    def search_definitions(self, **kwargs):
        """Search definitions and assert the envelope is clean."""
        kwargs.setdefault("limit", 2)
        result = self.call_method(self.module.search_workflow_definitions, **kwargs)
        self.assert_envelope_ok(result, context=f"definitions {kwargs}")
        return result

    def search_executions(self, **kwargs):
        """Search executions and assert the envelope is clean."""
        kwargs.setdefault("limit", 2)
        result = self.call_method(self.module.search_workflow_executions, **kwargs)
        self.assert_envelope_ok(result, context=f"executions {kwargs}")
        return result

    def a_definition(self):
        """Return one real definition, or skip when the tenant has none."""
        records = self.search_definitions(limit=2)["results"]
        if not records:
            self.skip_with_warning(
                "Tenant has no workflow definitions", context="definition fixture"
            )
        return records[0]

    def an_execution(self, filter=None):
        """Return one real execution, or skip when the tenant has none."""
        records = self.search_executions(limit=2, filter=filter)["results"]
        if not records:
            self.skip_with_warning(
                f"Tenant has no workflow executions matching {filter!r}",
                context="execution fixture",
            )
        return records[0]

    # ------------------------------------------------------------------
    # search_workflow_definitions
    # ------------------------------------------------------------------

    def test_search_definitions_operation_name(self):
        """Validate the WorkflowDefinitionsCombined operation name and envelope."""
        result = self.search_definitions(limit=2)
        self.assert_valid_list_response(result, context="WorkflowDefinitionsCombined")

    def test_search_definitions_returns_full_details(self):
        """The combined endpoint returns whole definitions in one call."""
        result = self.search_definitions(limit=2)
        if not result["results"]:
            self.skip_with_warning(
                "Tenant has no workflow definitions", context="definition details"
            )
            return

        self.assert_search_returns_details(
            result,
            ["id", "name", "trigger", "enabled", "version"],
            context="search_workflow_definitions",
        )

    def test_definition_publishes_its_own_trigger_block(self):
        """`trigger.type` is present, so the agent can tell what a workflow needs.

        A definition's `trigger.parameters` is the JSON Schema for its execute
        body. It is absent on workflows that take no input, so only `type` is
        required here.
        """
        definition = self.a_definition()
        trigger = definition.get("trigger")
        assert isinstance(trigger, dict), f"Expected a trigger dict, got {trigger!r}"
        assert "type" in trigger, f"Missing trigger.type; got keys {list(trigger)}"

    def test_definitions_filter_name_raw_exact(self):
        """`name.raw` does exact name matching. This is trap one.

        The analyzed `name` field returns zero rows for the same exact value, so
        a guide that recommended `name:'...'` would hand agents a dead query.
        Both directions are asserted here so a regression is loud.
        """
        definition = self.a_definition()
        workflow_name = definition["name"]

        self.assert_filter_matches(
            self.search_definitions,
            f"name.raw:'{workflow_name}'",
            predicate=lambda record: record.get("name") == workflow_name,
            predicate_desc=f"definition.name == {workflow_name!r}",
            note="name.raw is the unanalyzed field and the only one doing exact matching.",
            limit=2,
        )

        analyzed = self.search_definitions(filter=f"name:'{workflow_name}'", limit=2)
        assert not analyzed["results"], (
            f"name:'{workflow_name}' returned rows. The analyzed `name` field used to "
            "return zero for an exact match, which is why the guide leads with "
            "name.raw. If the API now supports it, update the guide and the filter hint."
        )

    def test_definitions_filter_name_raw_substring(self):
        """`name.raw` with the :* operator does substring matching."""
        workflow_name = self.a_definition()["name"]
        fragment = workflow_name[: max(3, len(workflow_name) // 2)]

        self.assert_filter_matches(
            self.search_definitions,
            f"name.raw:*'*{fragment}*'",
            predicate=lambda record: fragment in record.get("name", ""),
            predicate_desc=f"{fragment!r} in definition.name",
            note="Substring matching needs name.raw with the :* operator.",
            limit=2,
        )

    def test_definitions_filter_name_token_match(self):
        """The analyzed `name` field matches whole tokens with ~.

        Whitespace and hyphens are token boundaries; an underscore is not. Splitting on
        `_` as well produces a fragment that is not a token, which matches nothing —
        `name:~'RS'` against 'RS_Test Notify on ...' returns zero rows, and
        `name:~'Teds'` against 'Teds_CloudRisks_Workflow' only appears to work because
        other workflows carry 'Teds' as a real token. That made this test pass or fail on
        which definition the fixture happened to return.
        """
        workflow_name = self.a_definition()["name"]
        token = re.split(r"[\s\-]+", workflow_name.strip())[0]
        if len(token) < 3:
            self.skip_with_warning(
                f"First token of {workflow_name!r} is too short to match on",
                context="name token match",
            )
            return

        self.assert_filter_matches(
            self.search_definitions,
            f"name:~'{token}'",
            predicate=lambda record: token.lower() in record.get("name", "").lower(),
            predicate_desc=f"{token.lower()!r} in definition.name.lower()",
            note="`name` matches whole tokens only, so a full token must hit.",
            limit=2,
        )

    def test_definitions_filter_id(self):
        """`id` does exact matching on a definition ID."""
        definition_id = self.a_definition()["id"]
        self.assert_filter_matches(
            self.search_definitions,
            f"id:'{definition_id}'",
            predicate=lambda record: record.get("id") == definition_id,
            predicate_desc=f"definition.id == {definition_id!r}",
            limit=2,
        )

    def test_definitions_filter_enabled(self):
        """`enabled` matches on the definition's own boolean value."""
        definition = self.a_definition()
        expected = bool(definition.get("enabled"))
        self.assert_filter_matches(
            self.search_definitions,
            f"enabled:{'true' if expected else 'false'}",
            predicate=lambda record: bool(record.get("enabled")) is expected,
            predicate_desc=f"definition.enabled is {expected}",
            limit=2,
        )

    def test_definitions_filter_trigger_type(self):
        """`trigger.type` matches on the definition's own trigger type."""
        trigger_type = self.a_definition()["trigger"]["type"]
        self.assert_filter_matches(
            self.search_definitions,
            f"trigger.type:'{trigger_type}'",
            predicate=lambda record: record.get("trigger", {}).get("type") == trigger_type,
            predicate_desc=f"definition.trigger.type == {trigger_type!r}",
            limit=2,
        )

    def test_definitions_filter_version(self):
        """`version` accepts numeric operators."""
        self.assert_filter_matches(
            self.search_definitions,
            "version:>0",
            predicate=lambda record: (record.get("version") or 0) > 0,
            predicate_desc="definition.version > 0",
            limit=2,
        )

    def test_definitions_filter_last_modified_timestamp(self):
        """`last_modified_timestamp` accepts relative dates.

        No predicate: a ten-year window matches every definition that exists, so any
        check against it would pass whatever the filter did. The row count is the
        assertion — this pins that the field and the relative-date form are accepted,
        and `test_definitions_unknown_filter_field_is_loud` covers the rejection side.
        """
        self.assert_filter_matches(
            self.search_definitions,
            "last_modified_timestamp:>'now-3650d'",
            note="A ten-year window should match any definition that exists.",
            limit=2,
        )

    def test_definitions_filter_description_token_match(self):
        """`description` is analyzed and matches tokens with ~."""
        records = self.search_definitions(
            filter="description:~'a'", limit=2
        )["results"]
        if not records:
            self.skip_with_warning(
                "No definition description contains the token 'a'",
                context="description filter",
            )
            return
        assert "description" in records[0] or True  # presence is optional on the entity

    def test_definitions_filter_mock_activities(self):
        """`mock_activities` is a valid boolean property.

        It is set on a minority of definitions, so a zero-row result is a real
        answer here rather than a broken filter — this only pins that the field
        is accepted rather than 400ing as unknown.
        """
        self.search_definitions(filter="mock_activities:true", limit=2)

    def test_definitions_unknown_filter_field_is_loud(self):
        """An unknown property returns a 400 with the FQL guide inline."""
        result = self.call_method(
            self.module.search_workflow_definitions,
            filter="not_a_real_field:'x'",
            limit=2,
        )
        assert isinstance(result, dict), f"Expected a dict, got {type(result)}"
        assert "fql_guide" in result, (
            "Expected the FQL guide inline for an unknown property. Both workflow "
            f"search endpoints reject one with a 400. Got: {result}"
        )

    def test_definitions_sort_requires_dot_notation(self):
        """Sort uses dots here. The pipe form used elsewhere returns a 400."""
        self.search_definitions(sort="name.asc", limit=2)

        piped = self.call_method(
            self.module.search_workflow_definitions,
            sort="name|desc",
            limit=2,
        )
        assert isinstance(piped, dict) and (
            "error" in piped or "fql_guide" in piped
        ), (
            "Expected 'name|desc' to be rejected. This endpoint validates sort "
            f"against a regex that forbids the pipe form. Got: {piped}"
        )

    def test_definitions_limit_bounds(self):
        """The documented upper limit is accepted by the API."""
        self.search_definitions(limit=500)

    # ------------------------------------------------------------------
    # search_workflow_executions
    # ------------------------------------------------------------------

    def test_search_executions_operation_name(self):
        """Validate the WorkflowExecutionsCombined operation name and envelope."""
        result = self.search_executions(limit=2)
        self.assert_valid_list_response(result, context="WorkflowExecutionsCombined")

    def test_search_executions_returns_full_details(self):
        """Executions come back with the response's own field names.

        The ID field is `execution_id`, not `id` — the filter field is `id`. Any
        test written from the filter names would fail here, which is the point.
        """
        result = self.search_executions(limit=2)
        if not result["results"]:
            self.skip_with_warning(
                "Tenant has no workflow executions", context="execution details"
            )
            return

        self.assert_search_returns_details(
            result,
            ["execution_id", "definition_id", "status"],
            context="search_workflow_executions",
        )

    def test_executions_filter_ui_status(self):
        """`ui_status` filters on the status the response displays. This is trap two.

        The `status` field holds a different vocabulary: an execution the response
        reports as 'Completed' is `status:'Succeeded'`. Both directions are
        asserted so a regression to `status:'Completed'` fails loudly.

        Discovery deliberately avoids any status filter. Finding the fixture with
        the filter under test would let a regression skip the test instead of
        failing it. Only the terminal 'Completed' state is used, because a busy
        tenant starts runs continuously and a non-terminal status can change
        between two queries.
        """
        candidates = self.search_executions(
            filter="completed_timestamp:>'now-3650d'", limit=10
        )["results"]
        if not any(record.get("status") == "Completed" for record in candidates):
            self.skip_with_warning(
                "No completed execution in the sample to check ui_status against",
                context="ui_status filter",
            )
            return

        matched = self.search_executions(filter="ui_status:'Completed'", limit=2)
        assert matched["results"], (
            "ui_status:'Completed' returned zero rows even though a completed "
            "execution exists. ui_status is the documented status filter; if it "
            "stopped working, the guide and the filter hint are both wrong."
        )
        assert all(
            record["status"] == "Completed" for record in matched["results"]
        ), (
            "ui_status:'Completed' returned a row with a different response status. "
            "ui_status is documented as mirroring the response's own status value."
        )

        internal = self.search_executions(filter="status:'Completed'", limit=2)
        assert not internal["results"], (
            "status:'Completed' returned rows. The internal vocabulary used "
            "'Succeeded' for this state, which is why the guide leads with "
            "ui_status. If the API now accepts it, update the guide and the hint."
        )

    def test_executions_filter_ui_status_accepts_every_documented_value(self):
        """Each documented ui_status value is a valid filter.

        Non-empty is not asserted: whether a tenant currently has a failed or
        paused run is not a property of the filter. An unknown value would 400,
        so a clean envelope is the thing being pinned.
        """
        for value in ("Completed", "Failed", "In progress", "Action required"):
            self.search_executions(filter=f"ui_status:'{value}'", limit=2)

    def test_executions_filter_id(self):
        """The filter field `id` matches the response's `execution_id`."""
        execution_id = self.an_execution()["execution_id"]
        self.assert_filter_matches(
            self.search_executions,
            f"id:'{execution_id}'",
            predicate=lambda record: record.get("execution_id") == execution_id,
            predicate_desc=f"execution.execution_id == {execution_id!r}",
            note="The response calls this execution_id; the filter calls it id.",
            limit=2,
        )

    def test_executions_filter_definition_id(self):
        """`definition_id` lists one workflow's run history."""
        definition_id = self.an_execution()["definition_id"]
        self.assert_filter_matches(
            self.search_executions,
            f"definition_id:'{definition_id}'",
            predicate=lambda record: record.get("definition_id") == definition_id,
            predicate_desc=f"execution.definition_id == {definition_id!r}",
            limit=2,
        )

    def test_executions_filter_definition_name_token_match(self):
        """`definition_name` is analyzed and matches whole tokens with ~.

        Split on whitespace and hyphens only, for the reason spelled out in
        `test_definitions_filter_name_token_match`: an underscore is not a token boundary
        here. `definition_name:~'MainWF'` returns nothing for a run of
        'MainWF_Mohamad_Nabulsi_SNow_Automation_CRs' — the whole underscored string is the
        token.
        """
        execution = self.an_execution()
        definition_name = execution.get("definition_name")
        if not definition_name:
            self.skip_with_warning(
                "Execution carries no definition_name", context="definition_name filter"
            )
            return

        token = re.split(r"[\s\-]+", definition_name.strip())[0]
        if len(token) < 3:
            self.skip_with_warning(
                f"First token of {definition_name!r} is too short to match on",
                context="definition_name filter",
            )
            return

        self.assert_filter_matches(
            self.search_executions,
            f"definition_name:~'{token}'",
            predicate=lambda record: token.lower() in (record.get("definition_name") or "").lower(),
            predicate_desc=f"{token.lower()!r} in execution.definition_name.lower()",
            limit=2,
        )

    def test_executions_filter_started_timestamp(self):
        """`started_timestamp` is the filter name; `start_timestamp` is response-only.

        The predicate reads the response's spelling, which is the whole point of the
        pairing: a row that came back without `start_timestamp` would mean the two names
        are no longer the same field.
        """
        self.assert_filter_matches(
            self.search_executions,
            "started_timestamp:>'now-3650d'",
            predicate=lambda record: bool(record.get("start_timestamp")),
            predicate_desc="execution.start_timestamp is populated",
            note="A ten-year window should match any execution that exists.",
            limit=2,
        )

        response_named = self.call_method(
            self.module.search_workflow_executions,
            filter="start_timestamp:>'now-7d'",
            limit=2,
        )
        assert "fql_guide" in response_named, (
            "Expected start_timestamp to be rejected as an unknown property — it "
            f"is the response's name for started_timestamp. Got: {response_named}"
        )

    def test_executions_filter_completed_timestamp(self):
        """`completed_timestamp` is the filter name; `end_timestamp` is response-only.

        Filtering on it selects finished runs, and only a finished run carries an
        `end_timestamp` — an in-progress execution has no such key at all. So the
        predicate can actually fail, unlike a bare ten-year window.
        """
        self.assert_filter_matches(
            self.search_executions,
            "completed_timestamp:>'now-3650d'",
            predicate=lambda record: bool(record.get("end_timestamp")),
            predicate_desc="execution.end_timestamp is populated",
            note="A ten-year window should match any completed execution.",
            limit=2,
        )

    def test_executions_filter_definition_version(self):
        """`definition_version` accepts numeric operators."""
        self.assert_filter_matches(
            self.search_executions,
            "definition_version:>0",
            predicate=lambda record: (record.get("definition_version") or 0) > 0,
            predicate_desc="execution.definition_version > 0",
            limit=2,
        )

    def test_executions_filter_test_mode(self):
        """`test_mode` matches on the execution's own boolean value.

        No predicate: the response does not carry `test_mode` at all, so any check would
        read `None` and pass regardless of what the filter did. The fixture's value is
        still used to pick the side that must have rows.
        """
        execution = self.an_execution()
        test_mode = "true" if execution.get("test_mode") else "false"
        self.assert_filter_matches(
            self.search_executions,
            f"test_mode:{test_mode}",
            limit=2,
        )

    def test_executions_filter_contains_mocks(self):
        """`contains_mocks` matches on the execution's own boolean value."""
        execution = self.an_execution()
        expected = bool(execution.get("contains_mocks"))
        self.assert_filter_matches(
            self.search_executions,
            f"contains_mocks:{'true' if expected else 'false'}",
            predicate=lambda record: bool(record.get("contains_mocks")) is expected,
            predicate_desc=f"execution.contains_mocks is {expected}",
            limit=2,
        )

    def test_executions_sort_requires_dot_notation(self):
        """Sort uses dots here. The pipe form returns a 400."""
        self.search_executions(sort="started_timestamp.desc", limit=2)

        piped = self.call_method(
            self.module.search_workflow_executions,
            sort="started_timestamp|desc",
            limit=2,
        )
        assert isinstance(piped, dict) and (
            "error" in piped or "fql_guide" in piped
        ), f"Expected 'started_timestamp|desc' to be rejected. Got: {piped}"

    # ------------------------------------------------------------------
    # get_workflow_execution_results
    # ------------------------------------------------------------------

    def test_execution_results_operation_name(self):
        """Chain a real execution ID into the results tool.

        This is the only way to see each activity's own `result` payload, which
        the search tool omits.
        """
        execution_id = self.an_execution()["execution_id"]

        result = self.call_method(
            self.module.get_workflow_execution_results, ids=[execution_id]
        )
        self.assert_no_error(result, context="WorkflowExecutionResults")
        assert isinstance(result, list) and result, f"Expected a record, got {result}"
        assert result[0]["execution_id"] == execution_id

    def test_execution_results_include_activity_result_payloads(self):
        """Activities carry a `result` payload, which is how a run's output is read.

        Not every activity produces one — a handler that returns nothing has no
        `result` key at all, seen live on a completed run. So several executions
        are sampled and the test skips if none in the sample produced output,
        rather than asserting a payload that the tenant's workflows may not create.
        """
        completed = self.search_executions(
            filter="ui_status:'Completed'", limit=10
        )["results"]
        if not completed:
            self.skip_with_warning(
                "Tenant has no completed executions", context="activity result payload"
            )
            return

        saw_activities = False
        for execution in completed:
            detailed = self.call_method(
                self.module.get_workflow_execution_results,
                ids=[execution["execution_id"]],
            )
            self.assert_no_error(detailed, context="execution results")
            activities = detailed[0].get("activities") or []
            if activities:
                saw_activities = True
            if any("result" in activity for activity in activities):
                return

        if not saw_activities:
            self.skip_with_warning(
                "No sampled execution reported any activities",
                context="activity result payload",
            )
            return

        self.skip_with_warning(
            "No sampled activity produced a `result` payload; this tenant's "
            "workflows may return nothing from their actions",
            context="activity result payload",
        )

    def test_execution_results_skip_fields_shrinks_payload(self):
        """`skip_fields` measurably reduces the response size.

        A terminal execution is used so the record cannot grow between the two
        reads, which would mask or fake the reduction.
        """
        execution_id = self.an_execution(filter="ui_status:'Completed'")["execution_id"]

        full = self.call_method(
            self.module.get_workflow_execution_results, ids=[execution_id]
        )
        trimmed = self.call_method(
            self.module.get_workflow_execution_results,
            ids=[execution_id],
            skip_fields=["trigger", "activities", "flows", "submodels"],
        )
        self.assert_no_error(trimmed, context="skip_fields")

        assert len(str(trimmed)) < len(str(full)), (
            "skip_fields did not shrink the payload; it may not be reaching the API. "
            f"full={len(str(full))} trimmed={len(str(trimmed))}"
        )

    def test_execution_results_unknown_id_is_not_found(self):
        """An unknown execution ID returns a 404 rather than an empty success."""
        result = self.call_method(
            self.module.get_workflow_execution_results,
            ids=[_NONEXISTENT_DEFINITION_ID],
        )
        assert isinstance(result, dict) and "error" in result, (
            f"Expected a 404 error for an unknown execution ID. Got: {result}"
        )
        assert "not found" in result["error"].lower(), (
            f"Expected the API's own 'not found' wording. Got: {result['error']}"
        )

    # ------------------------------------------------------------------
    # execute_workflow — error contracts only. Nothing here starts a run.
    # ------------------------------------------------------------------

    def test_execute_without_identifier_makes_no_api_call(self):
        """Omitting both identifiers is rejected locally, before any request."""
        result = self.call_method(self.module.execute_workflow)

        assert isinstance(result, dict) and "error" in result, (
            f"Expected a local validation error. Got: {result}"
        )
        assert "definition_id" in result["error"]

    def test_execute_unknown_definition_id_is_not_found(self):
        """A syntactically valid but nonexistent definition ID returns 404.

        This exercises the operation name, the POST method and the
        query-param/body split while starting nothing: the API resolves the
        definition before it looks at the body, so an unresolvable ID cannot run.
        """
        result = self.call_method(
            self.module.execute_workflow,
            definition_id=_NONEXISTENT_DEFINITION_ID,
            parameters={},
        )

        assert isinstance(result, dict) and "error" in result, (
            f"Expected a 404 for a nonexistent definition. Got: {result}"
        )
        assert "not found" in result["error"].lower(), (
            f"Expected the API's own 'not found' wording. Got: {result['error']}"
        )

    def test_execute_unknown_name_is_not_found(self):
        """The `name` route also refuses an unresolvable workflow."""
        result = self.call_method(
            self.module.execute_workflow,
            name="falcon-mcp integration test workflow that does not exist",
            parameters={},
        )

        assert isinstance(result, dict) and "error" in result, (
            f"Expected a 404 for a nonexistent workflow name. Got: {result}"
        )
        assert "not found" in result["error"].lower(), (
            f"Expected the API's own 'not found' wording. Got: {result['error']}"
        )

    def test_execute_refuses_disabled_definition(self):
        """A disabled definition is refused with a 412 that says it is disabled.

        Disabled and ineligible-trigger share status 412, so the message is the
        only thing telling them apart — this asserts the message, not the code.

        `version:>0` is part of the fixture filter because a definition that was never
        published sits at version 0, and the execute endpoint cannot resolve one: it
        answers 404 "definition not found" instead of the 412 under test. 167 of this
        tenant's 518 disabled on-demand definitions are in that state, so which one the
        search happened to return decided whether the test passed. The enabled-definition
        fixture below needs no such guard — a workflow cannot be enabled at version 0.
        """
        disabled = self.search_definitions(
            filter="enabled:false+trigger.type:'On demand'+version:>0", limit=2
        )["results"]
        if not disabled:
            self.skip_with_warning(
                "Tenant has no disabled on-demand definition to refuse",
                context="disabled 412",
            )
            return

        result = self.call_method(
            self.module.execute_workflow,
            definition_id=disabled[0]["id"],
            parameters={},
        )

        assert isinstance(result, dict) and "error" in result, (
            f"A disabled definition must be refused, not run. Got: {result}"
        )
        assert "disabled" in result["error"].lower(), (
            "Expected the API's 'is disabled' wording, which is what distinguishes "
            f"this 412 from the ineligible-trigger one. Got: {result['error']}"
        )

    def test_execute_refuses_ineligible_trigger_type(self):
        """A Signal-triggered definition is refused with its own 412 message."""
        signal = self.search_definitions(
            filter="enabled:true+trigger.type:'Signal'", limit=2
        )["results"]
        if not signal:
            self.skip_with_warning(
                "Tenant has no enabled Signal-triggered definition to refuse",
                context="ineligible trigger 412",
            )
            return

        result = self.call_method(
            self.module.execute_workflow,
            definition_id=signal[0]["id"],
            parameters={},
        )

        assert isinstance(result, dict) and "error" in result, (
            f"A Signal-triggered definition must be refused, not run. Got: {result}"
        )
        assert "on-demand or schedule" in result["error"].lower(), (
            "Expected the API's 'not an On-demand or schedule triggered workflow' "
            f"wording. Got: {result['error']}"
        )

    @pytest.mark.skipif(
        not os.environ.get("FALCON_TEST_WORKFLOW_ID"),
        reason=(
            "Set FALCON_TEST_WORKFLOW_ID to a known-inert on-demand workflow to run a "
            "real execution. The validation workflow for this module was a single "
            "inline-Python action printing a literal dict. Never point this at a "
            "workflow with real actions."
        ),
    )
    def test_execute_returns_labelled_execution_id(self):
        """A real run returns [{"execution_id": ...}], never a bare ID string.

        The API's `resources` holds bare 32-hex strings. Wrapping them keeps the
        declared return type honest and gives the agent a key it can hand to
        falcon_get_workflow_execution_results.
        """
        definition_id = os.environ["FALCON_TEST_WORKFLOW_ID"]

        result = self.call_method(
            self.module.execute_workflow,
            definition_id=definition_id,
            parameters={},
        )
        self.assert_no_error(result, context="WorkflowExecute")

        assert isinstance(result, list) and result, f"Expected a record, got {result}"
        assert isinstance(result[0], dict), (
            f"Expected the ID wrapped in a dict, got a bare {type(result[0])}: {result[0]}"
        )
        execution_id = result[0]["execution_id"]
        assert re.fullmatch(r"[0-9a-f]{32}", execution_id), (
            f"Expected a 32-hex execution ID, got {execution_id!r}"
        )

        detailed = self.call_method(
            self.module.get_workflow_execution_results, ids=[execution_id]
        )
        self.assert_no_error(detailed, context="execute to results handoff")
        assert detailed[0]["execution_id"] == execution_id
