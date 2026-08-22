"""Integration tests for the AgentWorks module."""

import pytest

from falcon_mcp.modules.agentworks import AgentworksModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestAgentWorksIntegration(BaseIntegrationTest):
    """Integration tests for the AgentWorks module with real API calls.

    Validates:
    - Correct agentic-studio routes and operation names for every read tool
    - Two-step search pattern returns full details, not just IDs
    - The pagination envelope shape search tools promise

    This file is the baseline for the planned migration off FalconPy's
    `override="METHOD,/route"` escape hatch onto named operations. Every read tool
    here must stay green across that change; a wrong operation name is invisible to
    the mocked unit tests and surfaces only against the live API.

    Two tools are deliberately NOT covered, so the migration must validate them by hand:

    - `invoke_agentworks_agent` really runs an agent and consumes account credits, so
      it does not belong in a suite meant to run repeatedly.
    - `get_agentworks_agent_invocation` (GetAgentInvocationV3) needs an invocation ID,
      and there is no read-only way to obtain one that resolves. Spans expose
      `attributes["aiplatform_agent.invocation_id"]`, but those belong to a different
      ID space — every one tested returned 404 from this endpoint, including invocations
      only minutes old. The only source of a usable ID is invoking an agent.

    Both are recorded gaps rather than always-skipping tests: a test that can only skip
    looks like coverage while being unable to catch a regression.

    Requires an AgentWorks-enabled tenant with the charlotte-ai-agent-definition:read
    scope. Tests skip gracefully when the tenant has no agents, versions, or spans.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the AgentWorks module with a real client."""
        self.module = AgentworksModule(falcon_client)

    # ------------------------------------------------------------------
    # Agents — QueryAgentsV2 / GetAgentsV2
    # ------------------------------------------------------------------

    def test_search_agents_operation_names(self):
        """Validate the QueryAgentsV2 and GetAgentsV2 routes against the live API."""
        result = self.call_method(self.module.search_agentworks_agents, limit=1)
        self.assert_no_error(result, context="QueryAgentsV2 / GetAgentsV2 validation")

    def test_search_agents_returns_full_details(self):
        """Search must return whole agent records, not just the IDs it queried."""
        result = self.call_method(self.module.search_agentworks_agents, limit=3)
        self.assert_no_error(result, context="search_agentworks_agents")
        self.assert_valid_list_response(
            result, min_length=0, context="search_agentworks_agents"
        )

        agents = self._unwrap_results(result)
        if not agents:
            self.skip_with_warning(
                "No AgentWorks agents in this tenant",
                context="search_agentworks_agents full details",
            )
            return

        assert len(agents[0]) > 1, f"Expected full agent detail, got only {list(agents[0])}"

    # ------------------------------------------------------------------
    # Agent versions — QueryAgentVersionsV1 / GetAgentVersionsV1
    # ------------------------------------------------------------------

    def test_search_agent_versions_operation_names(self):
        """Validate QueryAgentVersionsV1 and GetAgentVersionsV1 against the live API."""
        result = self.call_method(self.module.search_agentworks_agent_versions, limit=1)
        self.assert_no_error(
            result, context="QueryAgentVersionsV1 / GetAgentVersionsV1 validation"
        )

    def test_search_agent_versions_returns_full_details(self):
        """Version search must hydrate to whole records."""
        result = self.call_method(self.module.search_agentworks_agent_versions, limit=3)
        self.assert_no_error(result, context="search_agentworks_agent_versions")
        self.assert_valid_list_response(
            result, min_length=0, context="search_agentworks_agent_versions"
        )

        versions = self._unwrap_results(result)
        if not versions:
            self.skip_with_warning(
                "No AgentWorks agent versions in this tenant",
                context="search_agentworks_agent_versions full details",
            )
            return

        assert len(versions[0]) > 1, (
            f"Expected full version detail, got only {list(versions[0])}"
        )

    def test_search_agent_versions_accepts_documented_filter(self):
        """`agent_id` is the documented way to scope versions to one agent.

        Discovering the agent through the agents tool rather than through a versions
        filter keeps this from skipping silently if version filtering regresses.
        """
        agents = self._unwrap_results(
            self.call_method(self.module.search_agentworks_agents, limit=1)
        )
        if not agents:
            self.skip_with_warning(
                "No AgentWorks agents in this tenant",
                context="search_agentworks_agent_versions filter",
            )
            return

        agent_id = agents[0].get("id")
        assert agent_id, f"Agent record carried no id: {list(agents[0])}"

        result = self.call_method(
            self.module.search_agentworks_agent_versions,
            filter=f"agent_id:'{agent_id}'",
            limit=5,
        )
        self.assert_no_error(result, context="search_agentworks_agent_versions filter")

    # ------------------------------------------------------------------
    # Spans — QueriesSpansV1 / EntitiesSpansV1
    # ------------------------------------------------------------------

    def test_search_spans_operation_names(self):
        """Validate QueriesSpansV1 and EntitiesSpansV1 against the live API."""
        result = self.call_method(self.module.search_agentworks_spans, limit=1)
        self.assert_no_error(result, context="QueriesSpansV1 / EntitiesSpansV1 validation")

    def test_search_spans_returns_full_details(self):
        """Span search must hydrate to whole records."""
        result = self.call_method(self.module.search_agentworks_spans, limit=3)
        self.assert_no_error(result, context="search_agentworks_spans")
        self.assert_valid_list_response(
            result, min_length=0, context="search_agentworks_spans"
        )

        spans = self._unwrap_results(result)
        if not spans:
            self.skip_with_warning(
                "No AgentWorks spans in this tenant",
                context="search_agentworks_spans full details",
            )
            return

        assert len(spans[0]) > 1, f"Expected full span detail, got only {list(spans[0])}"

    # ------------------------------------------------------------------
    # Get invocation — GetAgentInvocationV3 — NOT COVERED, see class docstring
    # ------------------------------------------------------------------

