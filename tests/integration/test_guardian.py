"""Integration tests for the Guardian module.

Each test maps to a specific breaking change from the falconguardianmcpapi
migration, so an API-side regression is caught rather than silently returning
wrong data.

Requires the AIDR:read scope and the
`cloud.falcon-guardian.mcp-api.enable-query` feature flag for the CID.
"""

import inspect

import pytest

from falcon_mcp.modules.guardian import (
    _AGENT_SESSIONS_AGGREGATES_ROUTE,
    _AGENTS_ENTITIES_ROUTE,
    GuardianModule,
)
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestGuardianIntegration(BaseIntegrationTest):
    """Integration tests for the Guardian module with real API calls.

    Validates:
    - The reshaped routes are reachable (agent-sessions, executions, tools,
      skills, agent-os-users, mcp-server-names, agent-installations,
      model-names)
    - Wide LogScale windows pass through unclamped, narrowed reactively only
      if the API itself refuses them
    - The sessions aggregate groups by product tag
    - Entity fetch-by-id routes reject time_range
    - Agent detail (via the agent_detail report) composes without a 400
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Guardian module with a real client."""
        self.module = GuardianModule(falcon_client)

    def _raw_get(self, route, params):
        """Issue a raw /aidr GET, bypassing tool-level parameter filtering."""
        return self.module._query(route, params)

    @staticmethod
    def _notices(result):
        """The `notices` list a Guardian tool attaches to its envelope, if any.

        Row extraction goes through `BaseIntegrationTest.records` /
        `skip_unless_tenant_has`; only the notices are Guardian-specific, so only
        they need a local reader.
        """
        return (result.get("notices") or []) if isinstance(result, dict) else []

    # --- 1. Agent records carry the reshaped identity fields ---

    def test_search_agents_returns_identity_fields(self):
        """The opaque `Id` (passed to get_guardian_agent) and `SensorId` (the
        host key for follow-up tools) must both be present."""
        result = self.call_method(self.module.search_guardian_agents, limit=5)
        self.assert_no_error(result, context="search_guardian_agents")

        agents = self.skip_unless_tenant_has(
            result, "AI agents", context="test_search_agents_returns_identity_fields"
        )

        assert "Id" in agents[0], (
            f"Expected 'Id' on the agent record. Available: {list(agents[0].keys())}"
        )
        assert "SensorId" in agents[0], (
            f"Expected 'SensorId' on the agent record. Available: {list(agents[0].keys())}"
        )

    # --- 2. Sessions take product, not sensor_id or model ---

    def test_sessions_tool_takes_product_not_sensor_id(self):
        """Pure signature check — runs even with no telemetry in the CID."""
        params = inspect.signature(self.module.get_guardian_agent_sessions).parameters
        assert "product" in params, "get_guardian_agent_sessions must expose 'product'"
        assert "sensor_id" not in params, (
            "get_guardian_agent_sessions must not expose 'sensor_id' — the route "
            f"dropped the host filter. Current params: {list(params)}"
        )
        assert "model" not in params, (
            "get_guardian_agent_sessions must not expose 'model' — it was removed. "
            f"Current params: {list(params)}"
        )

    # --- 3. Entity fetch-by-id routes reject time_range ---

    def test_entities_agents_rejects_time_range(self):
        """entities/* routes have no time dimension; time_range is dropped
        client-side, so a raw call that includes it still succeeds because the
        clamp strips it. Assert the clamp removes it rather than 400ing."""
        # _query strips time_range for no-time-range routes; a bogus id simply
        # returns empty. The point is that no 400 about time_range comes back.
        response = self._raw_get(_AGENTS_ENTITIES_ROUTE, {"ids": "deadbeef", "time_range": "7d"})
        assert "time_range" not in str(response.errors).lower(), (
            f"time_range should have been dropped for an entities route, got: {response.errors}"
        )

    # --- 4. Sessions aggregate groups by product tag ---

    def test_sessions_aggregate_groups_by_product(self):
        """The AIAgentSession aggregate groups by `Product`; `count` is a JSON string."""
        response = self._raw_get(_AGENT_SESSIONS_AGGREGATES_ROUTE, {"time_range": "1h"})
        assert response.ok, f"Sessions aggregate failed: {response.errors}"

        if not response.resources:
            self.skip_with_warning(
                "no session activity in the last hour",
                context="test_sessions_aggregate_groups_by_product",
            )

        for row in response.resources:
            assert "Product" in row, f"Expected 'Product' grouping key, got: {list(row.keys())}"
            # Must parse as an int even though it arrives as a string
            int(row["count"])

    # --- 5. Over-wide LogScale windows are refused server-side and narrowed ---

    def test_logscale_over_wide_window_is_refused_and_narrowed(self):
        """The executions API refuses any window wider than 7d. An 8d request
        must come back without an error, narrowed by the reactive ladder (not a
        client-side clamp), with a notice that names the fallback window."""
        result = self.call_method(
            self.module.search_guardian_executions, time_range="8d", limit=5
        )

        self.assert_no_error(result, context="search_guardian_executions(time_range='8d')")

        notices = self._notices(result)
        assert notices, (
            "Expected a window-narrowing notice: the API refuses 8d and the "
            "retry ladder must report the fallback"
        )
        assert any("refused" in n.lower() for n in notices), (
            f"Expected a window-refusal notice from the retry ladder, got: {notices}"
        )
        assert any("7d" in n for n in notices), (
            f"Expected the notice to name the 7d fallback window, got: {notices}"
        )

    # --- 6. Reshaped and new endpoints are reachable ---

    @pytest.mark.parametrize(
        "tool_name,kwargs,empty_is_pass",
        [
            ("search_guardian_tools", {"limit": 5}, True),
            ("search_guardian_executions", {"limit": 5}, True),
            ("search_guardian_skills", {"limit": 5}, True),
            ("search_guardian_skill_usage", {"limit": 5}, True),
            ("search_guardian_os_users", {"limit": 5}, True),
            ("search_guardian_mcp_servers", {"limit": 5}, True),
            ("search_guardian_detections", {"limit": 5}, False),
            ("get_guardian_detection_scores", {}, False),
            ("search_guardian_installs", {"limit": 5}, True),
            ("search_guardian_models", {"limit": 5}, True),
        ],
    )
    def test_endpoints_reachable(self, tool_name, kwargs, empty_is_pass):
        """Each endpoint answers without a parameter or scope error."""
        method = getattr(self.module, tool_name)
        result = self.call_method(method, **kwargs)

        self.assert_no_error(result, context=tool_name)

        if empty_is_pass:
            self.records(result, context=tool_name)
        else:
            # skip_unless_tenant_has fails, rather than skips, when the query step
            # reports a non-zero pagination.total against an empty page.
            self.skip_unless_tenant_has(result, "rows", context=tool_name)

    # --- 7. Inventory shape ---

    def test_inventory_shape(self):
        """Sessions are keyed by product tag now; agents keep their product rollup."""
        result = self.call_method(self.module.get_guardian_inventory)
        self.assert_no_error(result, context="get_guardian_inventory")

        assert "by_product" in result["sessions"], (
            f"Expected sessions.by_product, got: {list(result['sessions'].keys())}"
        )
        assert "by_host" not in result["sessions"], (
            "sessions.by_host no longer exists — the aggregate groups by product tag now"
        )
        assert "by_product" in result["agents"], (
            f"Expected agents.by_product, got: {list(result['agents'].keys())}"
        )
        for product, count in result["sessions"]["by_product"].items():
            assert isinstance(count, int), (
                f"Expected an int count for product {product}, got {type(count)}: {count!r}"
            )

    # --- 8. Agent detail end to end (via the agent_detail report) ---

    def test_agent_detail_end_to_end(self):
        """A 400 on any leg means we are still sending a rejected parameter."""
        agents_result = self.call_method(self.module.search_guardian_agents, limit=1)
        self.assert_no_error(agents_result, context="search_guardian_agents")

        agents = self.skip_unless_tenant_has(
            agents_result, "AI agents", context="test_agent_detail_end_to_end"
        )

        agent_id = agents[0].get("Id")
        if not agent_id:
            self.skip_with_warning(
                "agent record has no Id", context="test_agent_detail_end_to_end"
            )

        report = self.call_method(
            self.module.generate_guardian_report,
            report_type="agent_detail",
            agent_id=agent_id,
        )
        self.assert_no_error(report, context=f"agent_detail report({agent_id})")

        detail = report["data"]["agent"]
        # No "sessions" key: the agent-sessions entity exposes no host filter, so
        # that leg was dropped rather than report a fleet-wide count as this
        # agent's. `executions` is the host-scoped session grain instead.
        expected_keys = {
            "instance",
            "tools",
            "executions",
            "tool_usage",
            "skill_usage",
            "detections",
            "max_detection_score",
        }
        assert expected_keys <= set(detail), (
            f"Missing keys: {expected_keys - set(detail)}"
        )

        # No sub-value may be a 400 — that would mean a parameter we send is no
        # longer allowed, which is exactly what this migration is about.
        for key, value in detail.items():
            if not isinstance(value, dict):
                continue
            for err in value.get("error") or []:
                if isinstance(err, dict):
                    assert err.get("status_code") != 400, (
                        f"Leg '{key}' returned HTTP 400 — a parameter we send is "
                        f"rejected by the API: {err}"
                    )

        # The tools leg is HOST-scoped by `sensor_id` — the AITool entity carries no
        # agent filter and no longer returns any reverse-relationship array, so a
        # tool cannot be attributed to one agent at all. Assert the leg is a list
        # and that any row it does return belongs to this agent's host. The store
        # is thin (11 host sensors over 7 days when measured), so an empty leg is
        # normal and is NOT a failure.
        tools = detail["tools"]
        if isinstance(tools, dict):
            # `.get("results", [])` on an error dict yields [], which reads as "zero
            # tools" and passes the host-scoping loop below vacuously. Any status
            # other than 400 (checked above) has to surface here instead.
            assert "error" not in tools, (
                f"tools leg returned an error rather than rows: {tools['error']}"
            )
            tools = tools.get("results", [])
        assert isinstance(tools, list), f"tools leg should be a list, got {type(tools)}"

        aid = agents[0].get("SensorId")
        for row in tools:
            got = row.get("SensorId")
            assert got == aid, (
                f"tools leg returned a row for sensor {got!r}, but the requested "
                f"agent's host is {aid!r} — the leg is not host-scoped"
            )

    def test_tools_leg_is_scoped_and_reports_coverage(self):
        """The tools leg must send sensor_id, and we must know its coverage.

        Two things this guards. First, `sensor_id` is now the only scope the
        AITool entity offers, so the leg has to use it — a client-side join on
        `UsedByAIAgents[]` returned nothing once the API dropped that array, and
        the unit tests could not see it because they mock the array.

        Second, the store is thin, so a passing `test_agent_detail_end_to_end`
        proves little on its own: "every returned row belongs to this host" is
        vacuously true for an empty list. Measure and report the overlap here so a
        drop to zero is visible rather than silent.
        """
        tools_result = self.call_method(self.module.search_guardian_tools, limit=500)
        self.assert_no_error(tools_result, context="search_guardian_tools")
        tools = self.skip_unless_tenant_has(
            tools_result, "AITool records", context="tools scoping"
        )

        # The reverse-relationship array is gone; nothing may depend on it again.
        assert not any("UsedByAIAgents" in row for row in tools), (
            "AITool rows carry UsedByAIAgents again — per-agent attribution may be "
            "possible once more; re-check the agent_detail tools leg"
        )

        agents_result = self.call_method(self.module.search_guardian_agents, limit=500)
        self.assert_no_error(agents_result, context="search_guardian_agents")
        agents = self.skip_unless_tenant_has(
            agents_result, "AI agents", context="tools scoping"
        )

        tool_sensors = {r.get("SensorId") for r in tools} - {None}
        agent_sensors = {a.get("SensorId") for a in agents} - {None}
        overlap = tool_sensors & agent_sensors

        # Not an assertion on the count — it is genuinely small and varies. Surface
        # it so a reviewer sees how much of the fleet this leg can ever cover.
        print(
            f"\ntools-leg coverage: {len(tool_sensors)} tool-store sensors, "
            f"{len(agent_sensors)} agent sensors sampled, {len(overlap)} overlap"
        )
        assert tool_sensors, "AITool rows carry no SensorId — the leg has no scope left"

    # --- 9. Detections aggregate with a wide window ---

    def test_detection_scores_with_a_wide_window(self):
        """aggregates/detections + time_range must return real data."""
        result = self.call_method(self.module.get_guardian_detection_scores, time_range="30d")

        self.assert_no_error(result, context="get_guardian_detection_scores(time_range='30d')")

    # --- 10. Typed narrowing parameters actually narrow ---

    @staticmethod
    def _read_back(row, *paths):
        """Read the first dotted path that resolves to a usable value."""
        for path in paths:
            cur = row
            for part in path.split("."):
                if not isinstance(cur, dict):
                    cur = None
                    break
                cur = cur.get(part)
            if isinstance(cur, list):
                cur = cur[0] if cur else None
            if cur not in (None, "", [], {}):
                return cur
        return None

    @pytest.mark.parametrize(
        "tool_name,param,paths",
        [
            ("search_guardian_agents", "product", ("ProductName", "AgentProductName")),
            ("search_guardian_agents", "hostname", ("HostName", "Hostname")),
            ("get_guardian_agent_sessions", "product", ("ProductName",)),
            ("search_guardian_installs", "product", ("ProductName", "AgentProductName")),
            ("search_guardian_installs", "sensor_id", ("SensorId",)),
            ("search_guardian_tools", "sensor_id", ("SensorId",)),
            ("search_guardian_os_users", "username", ("Username",)),
            ("search_guardian_os_users", "object_sid", ("ObjectSid",)),
            ("search_guardian_os_users", "aid", ("Aid",)),
            ("search_guardian_skills", "name_filter", ("SkillName",)),
            ("search_guardian_detections", "product", ("AgenticProductTagName",)),
            ("search_guardian_detections", "agent_id", ("AgentId",)),
        ],
    )
    def test_typed_parameter_narrows(self, tool_name, param, paths):
        """A typed narrowing parameter must both match and exclude.

        Guardian exposes no FQL `filter`, so upstream's `assert_filter_matches`
        does not apply — but the contract it enforces does. Learn a real value
        from an unfiltered page, then require that every row of the filtered page
        carries it, and that a value which cannot exist yields nothing.

        Without the second half a tool that stopped forwarding the parameter
        would still pass: these query routes answer an ignored parameter with an
        empty HTTP 200 or with the unfiltered page, never with an error. The
        `product` parameter is the one exception — the API validates it and
        returns HTTP 400 for an unknown name, which is itself proof the value
        reached the server.
        """
        method = getattr(self.module, tool_name)

        unfiltered = self.call_method(method, limit=25)
        self.assert_no_error(unfiltered, context=f"{tool_name} unfiltered")
        rows = self.skip_unless_tenant_has(
            unfiltered, f"{tool_name} rows", context=f"{tool_name}.{param}"
        )

        value = next(
            (v for v in (self._read_back(r, *paths) for r in rows if isinstance(r, dict)) if v),
            None,
        )
        if value is None:
            self.skip_with_warning(
                f"no row carries any of {paths}", context=f"{tool_name}.{param}"
            )

        matched = self.call_method(method, limit=25, **{param: value})
        self.assert_no_error(matched, context=f"{tool_name}({param}={value!r})")
        mrows = self.records(matched, context=f"{tool_name}({param}={value!r})")
        assert mrows, (
            f"{tool_name} returned zero rows for {param}={value!r}, a value read "
            f"straight off an unfiltered row — the parameter is not being served"
        )
        wrong = [r for r in mrows if str(self._read_back(r, *paths)) != str(value)]
        assert not wrong, (
            f"{len(wrong)} of {len(mrows)} rows do not carry {param}={value!r} "
            f"at {paths} — the parameter is accepted but not applied. "
            f"First offender: {wrong[0]}"
        )

        # A value that cannot exist must return nothing, or be rejected outright.
        absent = self.call_method(method, limit=25, **{param: "zzz-no-such-value-zzz"})
        if isinstance(absent, dict) and absent.get("error"):
            # `product` is validated server-side: HTTP 400 "unknown product",
            # surfaced as a data result. A rejection proves the value was sent.
            return
        arows = self.records(absent, context=f"{tool_name}({param}=nonsense)")
        assert not arows, (
            f"{tool_name} returned {len(arows)} rows for {param}='zzz-no-such-value-zzz'. "
            f"The parameter is being dropped rather than applied."
        )

