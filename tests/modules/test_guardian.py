"""
Tests for the Guardian module.

Mocking boundary: every test mocks `self.mock_client.command` (sync tools) and/or
`self.mock_client.command_async` (the async fan-out tools), the same seam used
by tests/modules/test_agentworks.py and tests/modules/test_hosts.py. This exercises
the real `_plan`, `_parse_response`, time-range clamping, and 504-narrowing-ladder
code paths instead of stubbing them out.
"""

import asyncio
import inspect
import re
import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from falcon_mcp.client import FalconClient
from falcon_mcp.modules import guardian
from falcon_mcp.modules.guardian import GuardianModule, GuardianResponse
from falcon_mcp.resources import guardian as guardian_resources
from tests.modules.utils.test_modules import TestModules


def _envelope(
    status_code: int = 200,
    resources: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a FalconPy `command`/`command_async` envelope."""
    body: dict[str, Any] = {}
    if resources is not None:
        body["resources"] = resources
    if errors is not None:
        body["errors"] = errors
    if meta is not None:
        body["meta"] = meta
    return {"status_code": status_code, "body": body}


def _call_kwargs(call: Any) -> dict[str, Any]:
    """Extract the {override, parameters} kwargs from a `command` mock call."""
    return call.kwargs


class GuardianToolTestCase(unittest.TestCase):
    """Base fixture for tool-level tests: a module wired to a mock FalconClient.

    Sync tools call `self.mock_client.command`; the async fan-out tools call
    `self.mock_client.command_async`. Both are stubbed here so either kind of test
    can set whichever one it needs.
    """

    def setUp(self) -> None:
        self.mock_client = MagicMock(spec=FalconClient)
        self.mock_client.command_async = AsyncMock()
        self.module = GuardianModule(self.mock_client)


class TestGuardianModuleRegistration(TestModules):
    """Test tool and resource registration."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(GuardianModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_guardian_agents",
            "falcon_get_guardian_agent",
            "falcon_search_guardian_mcp_servers",
            "falcon_get_guardian_agent_sessions",
            "falcon_get_guardian_session_detail",
            "falcon_get_guardian_session_activity",
            "falcon_search_guardian_tools",
            "falcon_search_guardian_tool_usage",
            "falcon_search_guardian_executions",
            "falcon_search_guardian_prompts",
            "falcon_get_guardian_inventory",
            "falcon_search_guardian_skills",
            "falcon_search_guardian_skill_usage",
            "falcon_get_guardian_fleet_skill_inventory",
            "falcon_search_guardian_os_users",
            "falcon_pivot_on_guardian_attribute",
            "falcon_get_guardian_process_tree",
            "falcon_get_guardian_network_events",
            "falcon_get_guardian_file_events",
            "falcon_get_guardian_classified_file_access",
            "falcon_generate_guardian_report",
            "falcon_search_guardian_detections",
            "falcon_get_guardian_detection_scores",
            "falcon_search_guardian_installs",
            "falcon_search_guardian_models",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_guardian_query_guide",
            "falcon_guardian_entity_schema",
            "falcon_guardian_inventory_schema",
            "falcon_guardian_example_queries",
        ]
        self.assert_resources_registered(expected_resources)


class TestSchemaGuideMatchesTheMeasuredApi(unittest.TestCase):
    """Pin the graph-schema facts that were verified against the live API.

    Every claim here was wrong in the guide before, and each one sends a caller to
    a dead end: an ordinal presented as a name, a vertex keyed on `Id` that has no
    `Id`, and an agent vertex that never arrives. Tool-level tests cannot catch any
    of it, because a mock returns whatever shape the fixture author imagined — that
    is precisely how the false claims survived. So assert on the guide text.

    Match on facts, not phrasing, so the wording stays free to improve.
    """

    def _ai_graph_section(self) -> str:
        """Just the AI vertex tables.

        The later threat-graph vertices (UserIdVertex, ModuleVertex and friends)
        were not measured and keep their original wording, so every assertion is
        scoped to the part that was.
        """
        text = guardian_resources.ENTITY_SCHEMA_DOCUMENTATION
        return text[
            text.index("## AiAgentVertex") : text.index("### Outgoing Edges from ProcessVertex")
        ]

    def _table(self, heading: str, next_heading: str) -> str:
        section = self._ai_graph_section()
        return section[section.index(heading) : section.index(next_heading)]

    def test_ai_vertices_are_documented_as_keying_on_dunder_id(self):
        """No AI vertex carries `Id`; all 15 measured graphs keyed on `__id`."""
        section = self._ai_graph_section()
        self.assertNotIn(
            "| `Id` |", section, "AI graph vertices key on `__id` — there is no `Id` field"
        )
        self.assertIn("`__id`", section)

    def test_agentic_tool_is_not_documented_as_a_name(self):
        """It is an int ordinal (3, 4, 6, 7, 8) and the vertex carries no name."""
        table = self._table("## AiToolVertex", "## AiModelVertex")
        # The old row read: AgenticTool | Tool type/name (e.g., "Bash", "Read", ...)
        # Names may still appear here as examples of what AgenticToolName holds, so
        # assert on the false claim itself rather than on the word "Bash".
        self.assertNotIn(
            "Tool type/name", table, "AgenticTool holds an ordinal on this vertex, never a name"
        )
        self.assertIn("ordinal", table.lower())
        self.assertIn(
            "AgenticToolName", table, "must redirect to the key that does carry tool names"
        )

    def test_agentic_product_is_documented_as_an_ordinal_on_the_graph_too(self):
        """The old text sent callers to the graph layer for a name. It has none."""
        table = self._table("## AiSessionVertex", "### Outgoing Edges")
        self.assertIn("ordinal", table.lower())
        self.assertIn(
            "get_guardian_agent_sessions", table, "must name where a real product name lives"
        )

    def test_ai_agent_vertex_is_marked_as_not_populated(self):
        """The SessionRunByAiagent edge returned an empty AiAgent in every graph."""
        table = self._table("## AiAgentVertex", "## AiSessionVertex")
        self.assertIn("not populated", table.lower())
        self.assertIn("search_guardian_agents", table, "must name the working alternative")

    def test_edge_nesting_key_is_documented(self):
        """`UsedToolAitool[].AiTool` — the wrapper key differs from the edge name."""
        text = guardian_resources.ENTITY_SCHEMA_DOCUMENTATION
        self.assertIn("UsedToolAitool[].AiTool", text)

    def test_mcp_server_vertex_has_no_name_field(self):
        """Only `__id`/`DisplayName`; the name is the suffix after the last pipe."""
        table = self._table("## McpServerVertex", "## ProcessVertex")
        self.assertIn("No name field", table)
        self.assertIn("search_guardian_mcp_servers", table)


class TestEveryReferencedToolNameExists(unittest.TestCase):
    """No text may point at a tool that does not exist.

    Guardian's descriptions and guides lean hard on cross-references — "use
    search_guardian_executions(aid=...) instead" is how several traps are steered
    around. A stale or invented name turns that help into a dead end, and nothing
    else in the suite would notice. Written after a guide edit shipped a reference
    to a `processes` module that has never existed.
    """

    _PATTERN = re.compile(r"\b((?:search|get|generate|pivot)_guardian_[a-z_]+?)(?=[^a-z_]|$)")

    def _real_names(self) -> set[str]:
        return {n for n in dir(GuardianModule) if not n.startswith("_")}

    def _assert_all_exist(self, text: str, where: str) -> None:
        real = self._real_names()
        missing = sorted({m for m in self._PATTERN.findall(text) if m not in real})
        self.assertEqual(missing, [], f"{where} references tools that do not exist: {missing}")

    def test_resource_documents_reference_real_tools(self):
        # Discover the documents rather than listing them: a hand-written list of
        # constant names silently skips anything it spells wrong, which is a test
        # that passes without checking anything.
        docs = {
            name: value
            for name in dir(guardian_resources)
            if name.isupper() and isinstance(value := getattr(guardian_resources, name), str)
        }
        self.assertGreaterEqual(
            len(docs), 4, f"expected every guide document to be discovered, found {sorted(docs)}"
        )
        for name, text in sorted(docs.items()):
            with self.subTest(document=name):
                self._assert_all_exist(text, name)

    def test_tool_docstrings_and_field_descriptions_reference_real_tools(self):
        for tool in sorted(self._real_names()):
            method = getattr(GuardianModule, tool)
            if not callable(method):
                continue
            with self.subTest(tool=tool):
                self._assert_all_exist(method.__doc__ or "", f"{tool} docstring")
                for pname, param in inspect.signature(method).parameters.items():
                    description = getattr(param.default, "description", None)
                    if isinstance(description, str):
                        self._assert_all_exist(description, f"{tool}.{pname} description")


class TestNoMeasurementDataInShippedText(unittest.TestCase):
    """Descriptions and guides must not carry row counts from a test tenant.

    "The store held only 11 distinct host sensors over 7 days when measured" tells
    a model nothing it can act on, ages badly, and spends attention that the
    actionable instruction needs. Say the qualitative fact — the store is thinly
    populated, so expect an empty result — and keep the numbers in test docstrings
    and commit messages, where a maintainer can see the provenance.

    Applies to every model-facing string: tool docstrings, field descriptions, and
    the four resource documents. Code comments are exempt and not scanned; they
    explain the code to maintainers and never reach a client.
    """

    _BANNED = (
        re.compile(r"\bmeasured\b", re.I),
        re.compile(r"\bverified live\b", re.I),
        re.compile(r"\bsampled\b", re.I),
        re.compile(r"\bwhen we (?:checked|measured|tested)\b", re.I),
    )

    def _assert_clean(self, text: str, where: str) -> None:
        for pattern in self._BANNED:
            hit = pattern.search(text)
            if hit is None:
                continue
            context = text[max(0, hit.start() - 60) : hit.end() + 60]
            self.fail(
                f"{where} carries measurement data ({hit.group(0)!r}): ...{context}... "
                "State the qualitative fact instead; counts belong in a test or commit message."
            )

    def test_resource_documents_are_clean(self):
        docs = {
            name: value
            for name in dir(guardian_resources)
            if name.isupper() and isinstance(value := getattr(guardian_resources, name), str)
        }
        self.assertGreaterEqual(len(docs), 4, f"documents not discovered: {sorted(docs)}")
        for name, text in sorted(docs.items()):
            with self.subTest(document=name):
                self._assert_clean(text, name)

    def test_tool_docstrings_and_field_descriptions_are_clean(self):
        for tool in sorted(n for n in dir(GuardianModule) if not n.startswith("_")):
            method = getattr(GuardianModule, tool)
            if not callable(method):
                continue
            with self.subTest(tool=tool):
                self._assert_clean(method.__doc__ or "", f"{tool} docstring")
                for pname, param in inspect.signature(method).parameters.items():
                    description = getattr(param.default, "description", None)
                    if isinstance(description, str):
                        self._assert_clean(description, f"{tool}.{pname} description")


class TestSkillUsageNameDescription(unittest.TestCase):
    """The `name` filter must warn about the empty window and name the action.

    Two things this pins. First, skills carry no cross-store spelling split, so
    this field must not pick up `tool_name`'s capitalization warning — that would
    be a false claim here. Second, its real trap is the window: most inventory
    skills have no events in the 2h default, so a bare zero reads as "never used".

    Match on facts, not phrasing, and keep the provenance in this docstring rather
    than in the shipped description — a row count from one tenant on one day is
    not a durable fact and the model cannot act on it.
    """

    def _description(self) -> str:
        params = inspect.signature(GuardianModule.search_guardian_skill_usage).parameters
        return params["name"].default.description

    def test_states_case_sensitivity_and_the_silent_zero(self):
        text = self._description().lower()
        self.assertIn("case-sensitive", text)
        self.assertIn("zero rows", text)

    def test_names_the_recovery_action(self):
        """A constraint with no action gets ignored — the lesson from tool_name."""
        text = self._description()
        self.assertIn("time_range", text)
        self.assertIn("search_guardian_skills", text)

    def test_does_not_mention_capitalization(self):
        """Skills agree across stores, so any casing warning here would mislead."""
        text = self._description().lower()
        for word in ("capitalization", "capitalisation", "lowercase", "uppercase"):
            self.assertNotIn(word, text, f"skills have no casing split; drop {word!r}")

    def test_carries_no_measured_row_counts(self):
        """Tenant row counts are not durable facts and the model cannot act on them."""
        text = self._description()
        self.assertNotIn("measured", text.lower())
        self.assertFalse(
            re.search(r"\b\d{2,}\s+skills\b", text),
            f"drop the sampled skill counts from the description: {text}",
        )


class TestSanitizeGuardianValue(unittest.TestCase):
    """Test sanitize_guardian_value: rejects single quotes, backslashes, newlines."""

    def test_clean_value_passes(self):
        self.assertEqual(guardian.sanitize_guardian_value("Claude Code"), "Claude Code")

    def test_hex_value_passes(self):
        self.assertEqual(guardian.sanitize_guardian_value("abc123def456"), "abc123def456")

    def test_wildcard_passes(self):
        self.assertEqual(guardian.sanitize_guardian_value("*mcp*"), "*mcp*")

    def test_single_quote_rejected(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            guardian.sanitize_guardian_value("x' OR __id like '*")

    def test_backslash_rejected(self):
        with self.assertRaisesRegex(ValueError, "backslashes"):
            guardian.sanitize_guardian_value("value\\x00")

    def test_newline_rejected(self):
        with self.assertRaisesRegex(ValueError, "newlines"):
            guardian.sanitize_guardian_value("line1\nline2")

    def test_carriage_return_rejected(self):
        with self.assertRaisesRegex(ValueError, "newlines"):
            guardian.sanitize_guardian_value("line1\rline2")


class TestParseTimeRangeDays(unittest.TestCase):
    """Test _parse_time_range_days window parsing."""

    def test_parse_hours(self):
        self.assertAlmostEqual(guardian._parse_time_range_days("2h"), 2 / 24)

    def test_parse_days(self):
        self.assertEqual(guardian._parse_time_range_days("7d"), 7)
        self.assertEqual(guardian._parse_time_range_days("90d"), 90)

    def test_parse_minutes_no_longer_supported(self):
        # The API dropped the minutes unit, so "30m" no longer parses.
        self.assertIsNone(guardian._parse_time_range_days("30m"))

    def test_parse_unparseable_returns_none(self):
        self.assertIsNone(guardian._parse_time_range_days("garbage"))
        self.assertIsNone(guardian._parse_time_range_days(""))

    def test_parse_none_input_returns_none(self):
        self.assertIsNone(guardian._parse_time_range_days(None))


class TestClampTimeRange(unittest.TestCase):
    """Test _clamp_time_range: drops time_range on no-time-range routes, and
    otherwise passes the value through untouched.

    Only the entity fetch-by-id and threat-graph routes reject time_range now;
    every queries/* and aggregates/* route accepts it. The API is the sole
    authority on what window it serves; there is no client-side ceiling.
    """

    def test_wide_window_passes_through_unchanged_on_a_query_route(self):
        """No ceiling: a queries/* route gets the caller's window verbatim."""
        value, notice = guardian._clamp_time_range(guardian._AGENT_SESSIONS_QUERY_ROUTE, "30d")
        self.assertEqual(value, "30d")
        self.assertIsNone(notice)

    def test_very_wide_window_passes_through_unchanged(self):
        value, notice = guardian._clamp_time_range(guardian._AGENTS_QUERY_ROUTE, "365d")
        self.assertEqual(value, "365d")
        self.assertIsNone(notice)

    def test_no_time_range_route_drops_value_with_notice(self):
        value, notice = guardian._clamp_time_range(guardian._AGENTS_ENTITIES_ROUTE, "7d")
        self.assertIsNone(value)
        self.assertIsNotNone(notice)
        self.assertIn("time_range", notice)

    def test_unparseable_passes_through_untouched(self):
        value, notice = guardian._clamp_time_range(guardian._AGENT_SESSIONS_QUERY_ROUTE, "garbage")
        self.assertEqual(value, "garbage")
        self.assertIsNone(notice)

    def test_none_stays_none_without_notice(self):
        self.assertEqual(
            guardian._clamp_time_range(guardian._AGENT_SESSIONS_QUERY_ROUTE, None), (None, None)
        )


class TestNarrowingRungs(unittest.TestCase):
    """Test _narrowing_rungs: the reactive retry ladder offered below a given
    window. Takes only the effective window — there is no per-route ceiling
    left to vary the ladder by route.
    """

    def test_rungs_below_7d(self):
        self.assertEqual(guardian._narrowing_rungs("7d"), ["24h", "6h", "1h"])

    def test_rungs_below_24h(self):
        self.assertEqual(guardian._narrowing_rungs("24h"), ["6h", "1h"])

    def test_no_rungs_below_1h(self):
        self.assertEqual(guardian._narrowing_rungs("1h"), [])

    def test_unparseable_effective_returns_no_rungs(self):
        self.assertEqual(guardian._narrowing_rungs("garbage"), [])


class TestNormalizeProductName(unittest.TestCase):
    """Test _normalize_product_name human-name normalization."""

    def test_spaces_become_underscores_and_upper(self):
        self.assertEqual(guardian._normalize_product_name("Claude Code"), "CLAUDE_CODE")

    def test_hyphens_become_underscores(self):
        self.assertEqual(guardian._normalize_product_name("some-product"), "SOME_PRODUCT")

    def test_already_normalized_passes_through(self):
        self.assertEqual(guardian._normalize_product_name("CLAUDE_CODE"), "CLAUDE_CODE")

    def test_single_word_is_uppercased(self):
        self.assertEqual(guardian._normalize_product_name("cursor"), "CURSOR")


class TestAsInt(unittest.TestCase):
    """Test _as_int: coerces aggregate counts, degrading to 0 rather than raising."""

    def test_int_passthrough(self):
        self.assertEqual(guardian._as_int(7), 7)

    def test_numeric_string_coerced(self):
        self.assertEqual(guardian._as_int("7"), 7)

    def test_none_becomes_zero(self):
        self.assertEqual(guardian._as_int(None), 0)

    def test_non_numeric_string_becomes_zero(self):
        self.assertEqual(guardian._as_int("bogus"), 0)


class TestTagKey(unittest.TestCase):
    """Test _tag_key: renders a product tag ID as a comparable string.

    A JSON number decodes to float, whose str() is exponent notation; a plain
    integer string must compare equal to it, or the detections join misses.
    """

    def test_float_and_string_encodings_match(self):
        self.assertEqual(
            guardian._tag_key(213584428666201.0), guardian._tag_key("213584428666201")
        )

    def test_float_renders_without_exponent(self):
        self.assertEqual(guardian._tag_key(213584428666201.0), "213584428666201")

    def test_int_renders_plainly(self):
        self.assertEqual(guardian._tag_key(213584428666201), "213584428666201")

    def test_none_is_empty_string(self):
        self.assertEqual(guardian._tag_key(None), "")

    def test_string_passthrough(self):
        self.assertEqual(guardian._tag_key("CLAUDE_CODE"), "CLAUDE_CODE")


class TestIsUnattributedTag(unittest.TestCase):
    """Test _is_unattributed_tag: 0 and null both mean "no product"."""

    def test_none_is_unattributed(self):
        self.assertTrue(guardian._is_unattributed_tag(None))

    def test_empty_string_is_unattributed(self):
        self.assertTrue(guardian._is_unattributed_tag(""))

    def test_zero_int_is_unattributed(self):
        self.assertTrue(guardian._is_unattributed_tag(0))

    def test_zero_string_is_unattributed(self):
        self.assertTrue(guardian._is_unattributed_tag("0"))

    def test_real_tag_is_attributed(self):
        self.assertFalse(guardian._is_unattributed_tag("213584428666201"))

    def test_real_tag_int_is_attributed(self):
        self.assertFalse(guardian._is_unattributed_tag(213584428666201))

    def test_non_numeric_garbage_is_attributed(self):
        self.assertFalse(guardian._is_unattributed_tag("garbage"))


class TestGuardianResponseDataclass(unittest.TestCase):
    """Test the GuardianResponse dataclass."""

    def test_ok_when_no_errors(self):
        self.assertTrue(GuardianResponse(resources=[{"a": 1}]).ok)

    def test_not_ok_when_errors(self):
        self.assertFalse(GuardianResponse(errors=[{"message": "x"}]).ok)

    def test_count(self):
        self.assertEqual(GuardianResponse(resources=[{"a": 1}, {"b": 2}]).count, 2)

    def test_empty_response_defaults(self):
        r = GuardianResponse()
        self.assertEqual(r.resources, [])
        self.assertEqual(r.errors, [])
        self.assertEqual(r.notices, [])
        self.assertTrue(r.ok)

    def test_is_timeout_on_504_only(self):
        self.assertTrue(GuardianResponse(status_code=504).is_timeout)
        self.assertFalse(GuardianResponse(status_code=400).is_timeout)


class TestParseResponse(GuardianToolTestCase):
    """Test _parse_response envelope handling."""

    def test_parse_success_envelope(self):
        response = _envelope(200, resources=[{"a": 1}], errors=[])
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertTrue(result.ok)
        self.assertEqual(result.count, 1)

    def test_parse_non_dict_body_records_status_code(self):
        response = {"status_code": 200, "body": "not a dict"}
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.resources, [])

    def test_parse_body_errors_at_200_marks_not_ok(self):
        response = _envelope(200, resources=[], errors=[{"message": "partial"}])
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertFalse(result.ok)

    def test_parse_non_200_builds_error_entry(self):
        response = _envelope(500, errors=[{"message": "boom"}])
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertFalse(result.ok)
        self.assertEqual(result.status_code, 500)
        self.assertIn("boom", result.errors[0]["message"])

    def test_parse_403_enriched_with_scope_info(self):
        response = _envelope(403, errors=[{"message": "forbidden"}])
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertEqual(result.errors[0]["required_scopes"], ["AIDR:read"])

    def test_parse_missing_status_code_defaults_to_500(self):
        result = self.module._parse_response({"body": {}}, guardian._AGENTS_QUERY_ROUTE)
        self.assertEqual(result.status_code, 500)

    def test_empty_error_body_keeps_fallback_message(self):
        response = _envelope(500, errors=[])
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertIn("HTTP 500", result.errors[0]["message"])

    def test_full_page_on_aggregate_route_gets_truncation_notice(self):
        response = _envelope(200, resources=[{"i": i} for i in range(500)], errors=[])
        result = self.module._parse_response(response, guardian._AGENT_SESSIONS_AGGREGATES_ROUTE)
        self.assertTrue(any("truncated" in n.lower() for n in result.notices))

    def test_partial_page_on_aggregate_route_gets_no_notice(self):
        response = _envelope(200, resources=[{"i": i} for i in range(10)], errors=[])
        result = self.module._parse_response(response, guardian._AGENT_SESSIONS_AGGREGATES_ROUTE)
        self.assertEqual(result.notices, [])

    def test_full_page_on_query_route_gets_no_notice(self):
        response = _envelope(200, resources=[{"i": i} for i in range(500)], errors=[])
        result = self.module._parse_response(response, guardian._AGENT_SESSIONS_QUERY_ROUTE)
        self.assertEqual(result.notices, [])

    def test_pagination_extracted_from_meta(self):
        response = _envelope(
            200,
            resources=[{"a": 1}],
            errors=[],
            meta={"pagination": {"offset": 0, "limit": 50, "total": 1}},
        )
        result = self.module._parse_response(response, guardian._AGENTS_QUERY_ROUTE)
        self.assertEqual(result.pagination["total"], 1)


class TestRequestOnce(GuardianToolTestCase):
    """Test _request_once / _request_once_async build the override string."""

    def test_request_once_builds_override_string(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])
        self.module._request_once(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "24h"})
        kwargs = _call_kwargs(self.mock_client.command.call_args)
        self.assertEqual(kwargs["override"], f"GET,{guardian._AGENT_SESSIONS_QUERY_ROUTE}")

    def test_request_once_async_builds_override_string(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])
        asyncio.run(
            self.module._request_once_async(
                guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "24h"}
            )
        )
        kwargs = _call_kwargs(self.mock_client.command_async.call_args)
        self.assertEqual(kwargs["override"], f"GET,{guardian._AGENT_SESSIONS_QUERY_ROUTE}")


class TestPlan(GuardianToolTestCase):
    """Test _plan: param prep, window fit, retry-rung selection."""

    def test_drops_none_values(self):
        prepared, _, _, _ = self.module._plan(
            guardian._AGENTS_QUERY_ROUTE, {"product": "X", "hostname": None}
        )
        self.assertIn("product", prepared)
        self.assertNotIn("hostname", prepared)

    def test_wide_window_passes_through_and_still_offers_narrowing_rungs(self):
        prepared, notices, effective, rungs = self.module._plan(
            guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "30d"}
        )
        self.assertEqual(prepared["time_range"], "30d")
        self.assertEqual(effective, "30d")
        self.assertEqual(notices, [])
        self.assertTrue(rungs)

    def test_drops_time_range_on_no_time_range_route(self):
        prepared, notices, effective, rungs = self.module._plan(
            guardian._AGENTS_ENTITIES_ROUTE, {"time_range": "7d"}
        )
        self.assertNotIn("time_range", prepared)
        self.assertIsNone(effective)
        self.assertTrue(notices)
        self.assertEqual(rungs, [])

    def test_none_params_becomes_empty_dict(self):
        prepared, _, _, _ = self.module._plan(guardian._AGENTS_QUERY_ROUTE, None)
        self.assertEqual(prepared, {})


class TestQueryRetryLadder(GuardianToolTestCase):
    """Test the reactive narrowing ladder in _query / _query_async."""

    def test_retries_until_success_and_reports_window(self):
        self.mock_client.command.side_effect = [
            _envelope(504, errors=[{"message": "timeout"}]),
            _envelope(200, resources=[{"a": 1}], errors=[]),
        ]
        result = self.module._query(
            guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d", "limit": 50}
        )
        self.assertTrue(result.ok)
        self.assertTrue(any("24h" in n for n in result.notices))

    def test_400_does_not_retry(self):
        self.mock_client.command.return_value = _envelope(400, errors=[{"message": "bad product"}])
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        self.assertFalse(result.ok)
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_400_naming_time_range_reaches_ladder_and_narrows(self):
        """A 400 whose message names `time_range` is a window rejection, not a
        generic error: some deployments answer this way instead of a 504 (both
        shapes have been seen live), and it must still reach the narrowing
        ladder rather than being returned as a hard failure."""
        self.mock_client.command.side_effect = [
            _envelope(400, errors=[{"message": "time_range too wide"}]),
            _envelope(200, resources=[{"a": 1}], errors=[]),
        ]
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "30d"})
        self.assertTrue(result.ok)
        # The ladder must actually fire and pick the first rung below 30d, 7d —
        # not merely pass because nothing was retried.
        self.assertEqual(self.mock_client.command.call_count, 2)
        second_window = _call_kwargs(self.mock_client.command.call_args_list[1])[
            "parameters"
        ]["time_range"]
        self.assertEqual(second_window, "7d")
        self.assertTrue(any("7d" in n for n in result.notices))

    def test_minutes_rejected_before_request_with_real_cause(self):
        # "30m" must not reach the API, and must not emit the add-a-filter
        # ladder notice — the real cause is the unsupported unit.
        result = self.module._query(
            guardian._TOOL_USAGE_QUERY_ROUTE, {"time_range": "30m"}
        )
        self.assertFalse(result.ok)
        self.assertEqual(self.mock_client.command.call_count, 0)
        self.assertTrue(
            any("invalid time_range unit" in str(e.get("message", "")) for e in result.errors)
        )
        self.assertTrue(
            any("'h' (hours)" in str(e.get("message", "")) for e in result.errors)
        )
        self.assertFalse(any("Add a" in n for n in result.notices))

    def test_narrowest_window_exhausted_notice_names_no_untried_rung(self):
        # A rejected 1h has no narrower rung; the notice must not claim one was tried.
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "timeout"}])
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "1h"})
        self.assertTrue(any("no narrower one was available" in n for n in result.notices))
        self.assertFalse(any("down to" in n for n in result.notices))

    def test_400_about_other_parameter_does_not_reach_ladder(self):
        self.mock_client.command.return_value = _envelope(
            400, errors=[{"message": "unknown parameter foo"}]
        )
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        self.assertFalse(result.ok)
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_500_does_not_retry(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])
        self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_exhausted_ladder_returns_final_504(self):
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "timeout"}])
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        self.assertFalse(result.ok)
        self.assertTrue(any("refused every window" in n for n in result.notices))

    def test_budget_exhausted_stops_the_ladder_and_reports_the_budget_notice(self):
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "timeout"}])
        # Force the monotonic clock past the deadline after the first attempt.
        real_monotonic = guardian.time.monotonic
        calls = {"n": 0}

        def fake_monotonic():
            calls["n"] += 1
            # First read sets the deadline; subsequent reads are far in the future.
            return 0.0 if calls["n"] == 1 else 10_000.0

        with patch.object(guardian.time, "monotonic", fake_monotonic):
            result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        guardian.time.monotonic = real_monotonic
        self.assertTrue(any("Stopped narrowing" in n for n in result.notices))

    def test_narrowest_window_does_not_retry(self):
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "timeout"}])
        self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "1h"})
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_no_time_range_route_does_not_retry(self):
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "timeout"}])
        self.module._query(guardian._AGENTS_ENTITIES_ROUTE, {"ids": "abc"})
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_400_unknown_parameter_message_preserved(self):
        self.mock_client.command.return_value = _envelope(
            400, errors=[{"message": "unknown parameter foo"}]
        )
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {})
        self.assertIn("unknown parameter foo", result.errors[0]["message"])

    def test_504_message_preserved_after_exhausted_ladder(self):
        self.mock_client.command.return_value = _envelope(504, errors=[{"message": "engine timeout"}])
        result = self.module._query(guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d"})
        self.assertIn("engine timeout", result.errors[0]["message"])

    def test_query_async_retries_on_504(self):
        self.mock_client.command_async.side_effect = [
            _envelope(504, errors=[{"message": "timeout"}]),
            _envelope(200, resources=[{"a": 1}], errors=[]),
        ]
        result = asyncio.run(
            self.module._query_async(
                guardian._AGENT_SESSIONS_QUERY_ROUTE, {"time_range": "7d", "limit": 50}
            )
        )
        self.assertTrue(result.ok)


class TestListAiAgents(GuardianToolTestCase):
    """Test search_guardian_agents tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"Id": "inst-1", "SensorId": "aid-1", "AgentProduct": "213584428666146"},
                {"Id": "inst-2", "SensorId": "aid-2", "AgentProduct": "213584428666201"},
            ],
            errors=[],
        )

        result = self.module.search_guardian_agents(time_range="7d")

        self.assertEqual(len(result["results"]), 2)
        call = self.mock_client.command.call_args
        kwargs = _call_kwargs(call)
        self.assertEqual(kwargs["override"], f"GET,{guardian._AGENTS_QUERY_ROUTE}")
        params = kwargs["parameters"]
        self.assertEqual(params["time_range"], "7d")
        self.assertNotIn("product", params)
        self.assertNotIn("hostname", params)

    def test_product_filter_is_normalized(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"Id": "inst-1", "SensorId": "aid-1"}], errors=[]
        )

        result = self.module.search_guardian_agents(product="Claude Code", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "CLAUDE_CODE")
        self.assertEqual(len(result["results"]), 1)

    def test_hostname_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents(hostname="my-host", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["hostname"], "my-host")

    def test_no_working_directory_parameter_exists(self):
        """The agents endpoint no longer accepts working_directory."""
        self.assertNotIn(
            "working_directory",
            inspect.signature(self.module.search_guardian_agents).parameters,
        )

    def test_time_range_passed(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents(time_range="24h")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "24h")

    def test_wide_time_range_passes_through_verbatim(self):
        """No client-side ceiling: a wide window is sent to the API unchanged."""
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.search_guardian_agents(time_range="365d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "365d")
        self.assertNotIn("notices", result)

    def test_limit_passed(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents(time_range="7d", limit=10)

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["limit"], 10)

    def test_limit_truncates_results_client_side(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"Id": str(i)} for i in range(5)], errors=[]
        )

        result = self.module.search_guardian_agents(time_range="7d", limit=2)

        self.assertEqual(len(result["results"]), 2)

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(
            500, errors=[{"message": "query failed"}]
        )

        result = self.module.search_guardian_agents(time_range="7d")

        self.assertIn("error", result)

    def test_default_time_range_is_7d(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "7d")


class TestListAiSessions(GuardianToolTestCase):
    """Test get_guardian_agent_sessions tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"Id": "sess-1", "SensorId": "aid-1", "Product": "213584428666146"},
                {"Id": "sess-2", "SensorId": "aid-2", "Product": "213584428666201"},
            ],
            errors=[],
        )

        result = self.module.get_guardian_agent_sessions(time_range="7d")

        self.assertEqual(len(result["results"]), 2)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._AGENT_SESSIONS_QUERY_ROUTE}"
        )
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_success_carries_the_fleet_wide_note_first(self):
        """The scope warning travels with the rows, and must be the FIRST key.

        Measured live: when a caller raises `limit` to count rows, the envelope
        blows the client's tool-output budget and is persisted to a file, of
        which only a ~2KB preview reaches the model. Appended, the note sat
        ~240KB deep and was never read; as the first key it lands inside that
        preview. So key order is load-bearing here, not cosmetic — assert it.

        The assertions below check the facts, not the phrasing, so the note can
        be reworded without a false failure.
        """
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"Id": "sess-1"}], errors=[]
        )

        result = self.module.get_guardian_agent_sessions(time_range="7d")

        self.assertEqual(next(iter(result)), "note", f"note must come first: {list(result)}")
        self.assertIn("fleet-wide", result["note"].lower())
        # Both wrong counts the rows invite, and the query that answers each.
        self.assertIn("search_guardian_executions", result["note"])
        self.assertIn("per-agent ranking", result["note"])
        self.assertIn("get_guardian_inventory", result["note"])

    def test_error_carries_no_note(self):
        """An error dict has no rows to misattribute, so it gets no note."""
        self.mock_client.command.return_value = _envelope(
            400, errors=[{"message": "bad param"}]
        )

        result = self.module.get_guardian_agent_sessions(time_range="7d")

        self.assertIn("error", result)
        self.assertNotIn("note", result)

    def test_product_filter_is_normalized(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_agent_sessions(product="Claude Code", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "CLAUDE_CODE")

    def test_no_model_parameter_exists(self):
        """The sessions endpoint no longer accepts a model filter."""
        self.assertNotIn(
            "model", inspect.signature(self.module.get_guardian_agent_sessions).parameters
        )

    def test_no_sensor_id_parameter_exists(self):
        """The sessions endpoint dropped the sensor_id filter (server 400s on it)."""
        self.assertNotIn(
            "sensor_id",
            inspect.signature(self.module.get_guardian_agent_sessions).parameters,
        )

    def test_default_time_range_is_7d(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_agent_sessions()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "7d")


class TestListAiTools(GuardianToolTestCase):
    """Test search_guardian_tools tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"Id": "t-1", "Name": "Bash", "SensorId": "aid-1"}],
            errors=[],
        )

        result = self.module.search_guardian_tools(time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._TOOLS_QUERY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_sensor_id_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tools(sensor_id="aid-1", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["sensor_id"], "aid-1")

    def test_default_time_range_is_7d(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tools()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "7d")


class TestListAiToolUsage(GuardianToolTestCase):
    """Test search_guardian_tool_usage tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"AgenticToolName": "Bash", "AgenticToolUseId": "tu-1"},
                {"AgenticToolName": "Read", "AgenticToolUseId": "tu-2"},
            ],
            errors=[],
        )

        result = self.module.search_guardian_tool_usage(time_range="7d")

        self.assertEqual(len(result["results"]), 2)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_tool_name_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tool_usage(tool_name="Bash", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["tool_name"], "Bash")

    def test_session_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tool_usage(session_id="sess-1", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["session_id"], "sess-1")

    def test_aid_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tool_usage(aid="aid-1", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["aid"], "aid-1")

    def test_default_time_range_is_2h(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tool_usage()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "2h")


class TestListAiExecutions(GuardianToolTestCase):
    """Test search_guardian_executions tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"AgenticSessionId": "sess-1", "AgenticModel": "claude-sonnet-4-6"}],
            errors=[],
        )

        result = self.module.search_guardian_executions(time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._EXECUTIONS_QUERY_ROUTE}")

    def test_session_and_aid_filters(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_executions(session_id="sess-1", aid="aid-1", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["session_id"], "sess-1")
        self.assertEqual(params["aid"], "aid-1")

    def test_default_time_range_is_2h(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_executions()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "2h")


class TestSearchAiPrompts(GuardianToolTestCase):
    """Test search_guardian_prompts tool (sync)."""

    def test_by_session(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"AgenticPrompt": "Fix the bug", "AgenticSessionId": "sess-1", "aid": "aid-1"},
            ],
            errors=[],
        )

        result = self.module.search_guardian_prompts(session_id="sess-1", time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["AgenticPrompt"], "Fix the bug")
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._PROMPTS_QUERY_ROUTE}")
        params = _call_kwargs(call)["parameters"]
        self.assertEqual(params["session_id"], "sess-1")
        self.assertEqual(params["time_range"], "7d")

    def test_with_aid_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_prompts(session_id="sess-1", aid="aid-1")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["session_id"], "sess-1")
        self.assertEqual(params["aid"], "aid-1")

    def test_default_time_range_is_2h(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_prompts(session_id="sess-1")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "2h")


class TestListAiDetections(GuardianToolTestCase):
    """Test search_guardian_detections tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {
                    "AgentId": "03dd8b60284d402a9a4ae72d3a9cacbc",
                    "AgenticProductTag": "213584428666190",
                    "Name": "HiveCredTheft",
                    "Severity": 90,
                    "RiskScore": 57,
                },
            ],
            errors=[],
        )

        result = self.module.search_guardian_detections()

        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Severity"], 90)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._DETECTIONS_QUERY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_agent_id_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_detections(agent_id="03dd8b60284d402a9a4ae72d3a9cacbc")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["agent_id"], "03dd8b60284d402a9a4ae72d3a9cacbc")

    def test_product_is_normalized(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_detections(product="Kiro")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "KIRO")

    def test_time_range_and_limit_forwarded(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_detections(time_range="24h", limit=10)

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "24h")
        self.assertEqual(params["limit"], 10)

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])

        result = self.module.search_guardian_detections()

        self.assertIn("error", result)

    def test_rejects_64_hex_agent_id_without_calling_api(self):
        # A 64-hex value is the AIAgent.Id / AgentIds[] token, not the 32-hex
        # SensorId this param wants. Forwarding it returns zero rows silently, so
        # guard it with a clear error instead of a false-empty result.
        bad_id = "0bed3a54f986d03a" * 4  # 64 hex chars

        result = self.module.search_guardian_detections(agent_id=bad_id)

        self.assertIn("error", result)
        self.assertIn("32-hex", result["error"])
        self.mock_client.command.assert_not_called()

    def test_accepts_32_hex_agent_id(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.search_guardian_detections(
            agent_id="03dd8b60284d402a9a4ae72d3a9cacbc"
        )

        self.assertNotIn("error", result)
        self.mock_client.command.assert_called_once()


class TestGetDetectionScores(GuardianToolTestCase):
    """Test get_guardian_detection_scores tool (sync)."""

    def test_success(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {
                    "AgentId": "52531c67ed354be5bf063c66c5999f59",
                    "AgenticProductTag": "213584428666200",
                    "maxDetectionScore": 90,
                },
            ],
            errors=[],
        )

        result = self.module.get_guardian_detection_scores()

        self.assertEqual(result["results"][0]["maxDetectionScore"], 90)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._DETECTIONS_AGGREGATES_ROUTE}"
        )
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_no_limit_parameter_sent(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_detection_scores()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertNotIn("limit", params)

    def test_product_is_normalized(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_detection_scores(product="Claude Code")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "CLAUDE_CODE")

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])

        result = self.module.get_guardian_detection_scores()

        self.assertIn("error", result)

    def test_rejects_64_hex_agent_id_without_calling_api(self):
        bad_id = "0bed3a54f986d03a" * 4  # 64 hex chars

        result = self.module.get_guardian_detection_scores(agent_id=bad_id)

        self.assertIn("error", result)
        self.assertIn("32-hex", result["error"])
        self.mock_client.command.assert_not_called()


class TestListAiInstalls(GuardianToolTestCase):
    """Test search_guardian_installs tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{
                "Id": "052c476f847c609e",
                "SensorId": "52531c67ed354be5bf063c66c5999f59",
                "AgentProduct": "213584428666200",
                "Hostname": "dev1",
            }],
            errors=[],
        )

        result = self.module.search_guardian_installs()

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._AGENT_INSTALLATIONS_QUERY_ROUTE}"
        )

    def test_sensor_id_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_installs(sensor_id="aid-1")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["sensor_id"], "aid-1")

    def test_hostname_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_installs(hostname="dev1")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["hostname"], "dev1")

    def test_product_is_normalized(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_installs(product="Codex")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "CODEX")

    def test_sends_time_range(self):
        """agent-installations now accepts time_range (filters LastSeen)."""
        self.assertIn(
            "time_range", inspect.signature(self.module.search_guardian_installs).parameters
        )
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])
        self.module.search_guardian_installs(sensor_id="aid-1")
        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "7d")

    def test_empty_is_not_an_error(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.search_guardian_installs()

        self.assertEqual(result["results"], [])

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])

        self.assertIn("error", self.module.search_guardian_installs())


class TestListAiModels(GuardianToolTestCase):
    """Test search_guardian_models tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"Id": "m-1"}],
            errors=[],
        )

        result = self.module.search_guardian_models()

        self.assertEqual(result["results"][0]["Id"], "m-1")
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._MODEL_NAMES_QUERY_ROUTE}")

    def test_sends_time_range(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_models(time_range="24h")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "24h")

    def test_no_name_product_sensor_parameters(self):
        """The model-names entity exposes no scalar filters."""
        sig = inspect.signature(self.module.search_guardian_models).parameters
        self.assertNotIn("name", sig)
        self.assertNotIn("product", sig)
        self.assertNotIn("sensor_id", sig)

    def test_empty_is_not_an_error(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.assertEqual(self.module.search_guardian_models()["results"], [])

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])

        self.assertIn("error", self.module.search_guardian_models())


class TestSearchMCPServers(GuardianToolTestCase):
    """Test search_guardian_mcp_servers tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"Id": "mcp-1"}],
            errors=[],
        )

        result = self.module.search_guardian_mcp_servers()

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._MCP_SERVER_NAMES_QUERY_ROUTE}"
        )
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_no_agent_filter(self):
        """MCP server names are fleet-wide — no agent/sensor filter."""
        sig = inspect.signature(self.module.search_guardian_mcp_servers).parameters
        self.assertNotIn("agent_id", sig)
        self.assertNotIn("sensor_id", sig)


class TestSearchSkills(GuardianToolTestCase):
    """Test search_guardian_skills tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"Id": "sk-1", "SkillName": "code-review"}],
            errors=[],
        )

        result = self.module.search_guardian_skills(time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._SKILLS_QUERY_ROUTE}")

    def test_name_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_skills(name_filter="review")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["name_filter"], "review")


class TestSearchSkillUsage(GuardianToolTestCase):
    """Test search_guardian_skill_usage tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"AgenticSkill": "code-review", "AgenticSessionId": "sess-1"}],
            errors=[],
        )

        result = self.module.search_guardian_skill_usage(time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._SKILL_USAGE_QUERY_ROUTE}")

    def test_filters(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_skill_usage(
            name="code-review", session_id="sess-1", aid="aid-1", time_range="7d"
        )

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["name"], "code-review")
        self.assertEqual(params["session_id"], "sess-1")
        self.assertEqual(params["aid"], "aid-1")

    def test_default_time_range_is_2h(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_skill_usage()

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["time_range"], "2h")


class TestGetFleetSkillInventory(GuardianToolTestCase):
    """Test get_guardian_fleet_skill_inventory tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"SkillName": "commit", "count": 10}, {"SkillName": "review", "count": 5}],
            errors=[],
        )

        result = self.module.get_guardian_fleet_skill_inventory()

        self.assertEqual(len(result["results"]), 2)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._SKILLS_AGGREGATES_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_name_filter(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_fleet_skill_inventory(name_filter="commit")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["name_filter"], "commit")

    def test_no_agent_id_parameter(self):
        self.assertNotIn(
            "agent_id",
            inspect.signature(self.module.get_guardian_fleet_skill_inventory).parameters,
        )

    def test_limit_truncates_client_side_and_pagination_reflects_it(self):
        # The skills aggregate does not paginate; limit is applied client-side.
        # The envelope must report the client-side view (limit + a real total),
        # not echo the API's own pagination block.
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"SkillName": "a", "count": 3},
                {"SkillName": "b", "count": 2},
                {"SkillName": "c", "count": 1},
            ],
            meta={"pagination": {"limit": 500, "total": 3, "offset": 0}},
        )

        result = self.module.get_guardian_fleet_skill_inventory(limit=2)

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["pagination"]["limit"], 2)
        self.assertEqual(result["pagination"]["total"], 3)


class TestSearchOSUsers(GuardianToolTestCase):
    """Test search_guardian_os_users tool (sync)."""

    def test_no_filter(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"Aid": "aid-1", "Username": "alice"}],
            errors=[],
        )

        result = self.module.search_guardian_os_users(time_range="7d")

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._AGENT_OS_USERS_QUERY_ROUTE}"
        )

    def test_filters(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_os_users(
            aid="aid-1", username="alice", object_sid="S-1-5-21", time_range="7d"
        )

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["aid"], "aid-1")
        self.assertEqual(params["username"], "alice")
        self.assertEqual(params["object_sid"], "S-1-5-21")


class TestGetSessionActivity(GuardianToolTestCase):
    """Test get_guardian_session_activity tool (sync)."""

    def test_with_vertex_id(self):
        vertex_id = "aisess:abc123:eb5ca156-1128-44ab-b933-3154a36e8a54"
        # Measured shapes, not plausible ones. `AgenticProduct` and `AgenticTool`
        # are integer enum ordinals on the graph, and the AiTool vertex carries no
        # name at all. Earlier fixtures used "Claude Code" and "Bash" here, which
        # is exactly the mock that let the false schema-guide claim survive.
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{
                "__id": vertex_id,
                "AgenticProduct": 14,
                "UsedToolAitool": [
                    {"EventCloudTime": "2026-05-01T10:00:00Z", "AiTool": {"AgenticTool": 8}}
                ],
            }],
            errors=[],
        )

        result = self.module.get_guardian_session_activity(session_id=vertex_id)

        self.assertEqual(result["__id"], vertex_id)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._SESSION_ACTIVITY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["ids"], [vertex_id])

    def test_with_multiple_vertex_ids(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[
                {"__id": "aisess:abc123:aaa111", "AgenticSessionId": "aaa111"},
                {"__id": "aisess:abc123:bbb222", "AgenticSessionId": "bbb222"},
            ],
            errors=[],
        )

        result = self.module.get_guardian_session_activity(
            session_id="aisess:abc123:aaa111,aisess:abc123:bbb222"
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["ids"], ["aisess:abc123:aaa111", "aisess:abc123:bbb222"])

    def test_with_inventory_session_id(self):
        """UUID session IDs are passed directly — server resolves vertex key."""
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"__id": "aisess:aaaa0000:eb5ca156", "AgenticProduct": 14}],
            errors=[],
        )

        result = self.module.get_guardian_session_activity(session_id="eb5ca156")

        self.assertEqual(result["AgenticProduct"], 14)
        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["ids"], ["eb5ca156"])

    def test_no_ids_short_circuits(self):
        result = self.module.get_guardian_session_activity(session_id="  ,  ,")

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_not_found(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.get_guardian_session_activity(session_id="aisess:abc123:def456")

        self.assertIn("error", result)
        self.assertIn("No session(s) found", result["error"])

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "server error"}])

        result = self.module.get_guardian_session_activity(session_id="aisess:abc:123")

        self.assertIn("error", result)


class TestGetProcessTree(GuardianToolTestCase):
    """Test get_guardian_process_tree tool (sync)."""

    def test_with_vertex_key(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156-1128-44ab-b933-3154a36e8a54"
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{
                "__id": vertex_key,
                "SessionProcessPid": [{
                    "EventCloudTime": "2026-05-01T10:00:00Z",
                    "Process": {
                        "__id": "pid:abc123:1234",
                        "CommandLine": "node index.js",
                        "ImageFileName": "/usr/bin/node",
                    },
                }],
            }],
            errors=[],
        )

        result = self.module.get_guardian_process_tree(session_id=vertex_key, depth=2)

        self.assertEqual(result["__id"], vertex_key)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._PROCESS_TREE_ROUTE}")
        params = _call_kwargs(call)["parameters"]
        self.assertEqual(params["id"], vertex_key)
        self.assertEqual(params["depth"], 2)

    def test_with_uuid(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"__id": "aisess:abc:sess-uuid", "SessionProcessPid": []}], errors=[]
        )

        self.module.get_guardian_process_tree(session_id="sess-uuid", depth=1)

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["id"], "sess-uuid")
        self.assertEqual(params["depth"], 1)

    def test_not_found(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.get_guardian_process_tree(session_id="nonexistent")

        self.assertIn("error", result)

    def test_depth_default(self):
        self.mock_client.command.return_value = _envelope(200, resources=[{"__id": "x"}], errors=[])

        self.module.get_guardian_process_tree(session_id="sess-1")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["depth"], 2)

    def test_partial_failure_with_resources_surfaces_warnings(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"__id": "x"}], errors=[{"message": "partial degradation"}]
        )

        result = self.module.get_guardian_process_tree(session_id="sess-1")

        self.assertEqual(result["__id"], "x")
        self.assertIn("_warnings", result)


class TestGetNetworkEvents(GuardianToolTestCase):
    """Test get_guardian_network_events tool (sync)."""

    def test_success(self):
        vertex_key = "aisess:abc123:sess-uuid"
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{"__id": vertex_key, "SessionProcessPid": []}],
            errors=[],
        )

        result = self.module.get_guardian_network_events(session_id=vertex_key)

        self.assertEqual(result["__id"], vertex_key)
        call = self.mock_client.command.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._NETWORK_EVENTS_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["id"], vertex_key)

    def test_not_found(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.get_guardian_network_events(session_id="nonexistent")

        self.assertIn("error", result)

    def test_partial_failure_with_resources_surfaces_warnings(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"__id": "x"}], errors=[{"message": "partial degradation"}]
        )

        result = self.module.get_guardian_network_events(session_id="sess-1")

        self.assertEqual(result["__id"], "x")
        self.assertIn("_warnings", result)


class TestGetClassifiedFileAccess(GuardianToolTestCase):
    """Test get_guardian_classified_file_access tool (sync)."""

    def test_success(self):
        self.mock_client.command.return_value = _envelope(
            200,
            resources=[{
                "process_id": "pid:abc123:18394183048",
                "command_line": "claude --model opus",
                "classified_file_accesses": [{
                    "rule_actions": "blocked",
                    "files": [{"fileName": "credentials.env"}],
                }],
            }],
            errors=[],
        )

        result = self.module.get_guardian_classified_file_access(process_id="pid:abc123:18394183048")

        self.assertEqual(result["process_id"], "pid:abc123:18394183048")
        self.assertEqual(len(result["classified_file_accesses"]), 1)
        call = self.mock_client.command.call_args
        self.assertEqual(
            _call_kwargs(call)["override"], f"GET,{guardian._CLASSIFIED_FILE_ACCESS_ROUTE}"
        )
        self.assertEqual(_call_kwargs(call)["parameters"]["id"], "pid:abc123:18394183048")

    def test_not_found(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        result = self.module.get_guardian_classified_file_access(process_id="pid:abc:nonexistent")

        self.assertIn("error", result)
        self.assertIn("No classified file access", result["error"])

    def test_error_response(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "server error"}])

        result = self.module.get_guardian_classified_file_access(process_id="pid:abc:123")

        self.assertIn("error", result)

    def test_required_field_unwraps_for_a_direct_python_call(self):
        self.mock_client.command.return_value = _envelope(500, errors=[{"message": "boom"}])

        result = self.module.get_guardian_classified_file_access(process_id="pid:abc:123")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["id"], "pid:abc:123")
        self.assertIn("error", result)
        self.assertNotIn("FieldInfo", str(result))


class TestGetAiAgent(GuardianToolTestCase):
    """Test get_guardian_agent tool (async entity lookup — no fan-out)."""

    def test_success_returns_record(self):
        self.mock_client.command_async.return_value = _envelope(
            200,
            resources=[{"Id": "inst-1", "SensorId": "aid-1", "AgentProduct": "213584428666200"}],
            errors=[],
        )

        result = asyncio.run(self.module.get_guardian_agent(agent_id="inst-1"))

        self.assertEqual(result["Id"], "inst-1")
        self.assertEqual(result["SensorId"], "aid-1")
        # A single entities/agents lookup, no fan-out.
        self.assertEqual(self.mock_client.command_async.call_count, 1)
        call = self.mock_client.command_async.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._AGENTS_ENTITIES_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["ids"], "inst-1")

    def test_not_found(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module.get_guardian_agent(agent_id="nonexistent"))

        self.assertIn("error", result)
        self.assertIn("nonexistent", result["error"])

    def test_error_response(self):
        self.mock_client.command_async.return_value = _envelope(500, errors=[{"message": "boom"}])

        result = asyncio.run(self.module.get_guardian_agent(agent_id="inst-1"))

        self.assertIn("error", result)

    def test_injection_rejected(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(self.module.get_guardian_agent(agent_id="x' OR 1==1 --"))
        self.mock_client.command_async.assert_not_called()


class TestAgentProfile(GuardianToolTestCase):
    """Test the _agent_profile helper (fan-out backing agent_detail)."""

    def test_success(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{
                "Id": "inst-1",
                "SensorId": "aid-1",
                "AgentProduct": "213584428666200",
            }], errors=[]),
            # tools: scoped to the host sensor (the entity has no agent filter)
            _envelope(200, resources=[{
                "Id": "t-1",
                "Name": "Bash",
                "SensorId": "aid-1",
            }], errors=[]),
            _envelope(200, resources=[{"AgenticSessionId": "sess-1"}], errors=[]),  # executions
            _envelope(200, resources=[{"AgenticToolName": "Bash"}], errors=[]),  # tool_usage
            _envelope(200, resources=[{"AgenticSkill": "review"}], errors=[]),  # skill_usage
            _envelope(200, resources=[{"Name": "HiveCredTheft", "AgentId": "aid-1"}], errors=[]),
            _envelope(200, resources=[{
                "AgentId": "aid-1", "AgenticProductTag": "213584428666200", "maxDetectionScore": 90,
            }], errors=[]),
        ]

        result = asyncio.run(self.module._agent_profile("inst-1"))

        self.assertEqual(result["instance"]["Id"], "inst-1")
        self.assertEqual(len(result["tools"]), 1)
        self.assertNotIn("sessions", result)
        self.assertEqual(len(result["executions"]), 1)
        self.assertEqual(len(result["tool_usage"]), 1)
        self.assertEqual(len(result["skill_usage"]), 1)
        self.assertEqual(len(result["detections"]), 1)
        self.assertEqual(result["max_detection_score"], 90)
        # 1 verify + 6 fan-out = 7
        self.assertEqual(self.mock_client.command_async.call_count, 7)

    def test_tools_leg_is_scoped_to_the_host_sensor(self):
        """The tools leg must send sensor_id.

        It used to join the AITool inventory client-side on the agent's
        AgentIds[] against each row's UsedByAIAgents[].Agent.Id. The API stopped
        returning that array, so the join matched nothing and the leg was empty
        for every agent. `sensor_id` is the only scope the entity still offers.
        """
        self.mock_client.command_async.side_effect = (
            [
                _envelope(
                    200,
                    resources=[{"Id": "inst-1", "SensorId": "aid-1"}],
                    errors=[],
                )
            ]
            + [_envelope(200, resources=[], errors=[]) for _ in range(6)]
        )

        asyncio.run(self.module._agent_profile("inst-1"))

        tools_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._TOOLS_QUERY_ROUTE}"
        ]
        self.assertEqual(len(tools_calls), 1)
        params = _call_kwargs(tools_calls[0])["parameters"]
        self.assertEqual(params["sensor_id"], "aid-1")

    def test_no_sensor_id_reports_instead_of_querying_fleet_wide(self):
        """With no aid, every leg reports — including tools.

        An unfiltered tools query would return the whole fleet's inventory under
        an agent-scoped key, which reads as this agent's tools.
        """
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"Id": "inst-1"}], errors=[]),
        ]

        result = asyncio.run(self.module._agent_profile("inst-1"))

        # Only the verify call goes out; no leg is queried.
        self.assertEqual(self.mock_client.command_async.call_count, 1)
        for leg in ("tools", "executions", "tool_usage", "skill_usage", "detections"):
            self.assertIn("error", result[leg], f"{leg} should report the missing aid")

    def test_detection_legs_scoped_to_sensor_id(self):
        self.mock_client.command_async.side_effect = (
            [
                _envelope(
                    200,
                    resources=[{"Id": "inst-1", "SensorId": "aid-1"}],
                    errors=[],
                )
            ]
            + [_envelope(200, resources=[], errors=[]) for _ in range(6)]
        )

        asyncio.run(self.module._agent_profile("inst-1"))

        detection_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"]
            in (
                f"GET,{guardian._DETECTIONS_QUERY_ROUTE}",
                f"GET,{guardian._DETECTIONS_AGGREGATES_ROUTE}",
            )
        ]
        self.assertEqual(len(detection_calls), 2)
        for call in detection_calls:
            params = _call_kwargs(call)["parameters"]
            self.assertEqual(params["agent_id"], "aid-1")
            self.assertEqual(params["time_range"], "7d")

    def test_event_queries_send_explicit_7d(self):
        self.mock_client.command_async.side_effect = (
            [
                _envelope(
                    200,
                    resources=[{"Id": "inst-1", "SensorId": "aid-1"}],
                    errors=[],
                )
            ]
            + [_envelope(200, resources=[], errors=[]) for _ in range(6)]
        )

        asyncio.run(self.module._agent_profile("inst-1"))

        event_overrides = (
            f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}",
            f"GET,{guardian._EXECUTIONS_QUERY_ROUTE}",
            f"GET,{guardian._SKILL_USAGE_QUERY_ROUTE}",
            f"GET,{guardian._TOOLS_QUERY_ROUTE}",
        )
        checked = 0
        for call in self.mock_client.command_async.call_args_list:
            kwargs = _call_kwargs(call)
            if kwargs["override"] in event_overrides:
                self.assertEqual(kwargs["parameters"].get("time_range"), "7d")
                checked += 1
        self.assertEqual(checked, 4)

    def test_not_found(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module._agent_profile("nonexistent"))

        self.assertIn("error", result)
        self.assertEqual(self.mock_client.command_async.call_count, 1)

    def test_missing_sensor_id_does_not_query_unscoped(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"Id": "inst-1", "AgentProduct": "213584428666146"}], errors=[]),
        ]

        result = asyncio.run(self.module._agent_profile("inst-1"))

        # No fan-out queries were issued (only the verify call): every leg is
        # keyed by aid, including tools, and there is no aid.
        self.assertEqual(self.mock_client.command_async.call_count, 1)
        # Host-scoped legs are reported as unavailable, not empty activity.
        self.assertNotIn("sessions", result)
        self.assertIn("error", result["tools"])
        self.assertIn("error", result["executions"])

    def test_sub_query_errors_are_surfaced(self):
        self.mock_client.command_async.side_effect = [
            _envelope(
                200,
                resources=[{"Id": "inst-1", "SensorId": "aid-1"}],
                errors=[],
            ),
            _envelope(
                200,
                resources=[{"Id": "t-1", "Name": "Bash", "SensorId": "aid-1"}],
                errors=[],
            ),  # tools
            _envelope(500, errors=[{"message": "boom"}]),  # executions fails
            _envelope(200, resources=[{"AgenticToolName": "Bash"}], errors=[]),  # tool_usage
            _envelope(200, resources=[{"AgenticSkill": "review"}], errors=[]),  # skill_usage
            _envelope(200, resources=[], errors=[]),  # detections
            _envelope(200, resources=[], errors=[]),  # detection score
        ]

        result = asyncio.run(self.module._agent_profile("inst-1"))

        self.assertIsInstance(result["executions"], dict)
        self.assertIn("error", result["executions"])
        self.assertEqual(
            result["tools"], [{"Id": "t-1", "Name": "Bash", "SensorId": "aid-1"}]
        )
        self.assertEqual(result["tool_usage"], [{"AgenticToolName": "Bash"}])


class TestGetAiSessionDetail(GuardianToolTestCase):
    """Test get_guardian_session_detail tool (async fan-out)."""

    def test_without_activity(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgenticSessionId": "sess-1", "AgenticModel": "claude"}], errors=[]),
            _envelope(200, resources=[{"AgenticToolName": "Bash", "AgenticToolUseId": "tu-1"}], errors=[]),
            _envelope(200, resources=[{"AgenticSkill": "brainstorming"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.get_guardian_session_detail(session_id="sess-1", include_activity=False)
        )

        self.assertEqual(result["executions"][0]["AgenticSessionId"], "sess-1")
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(len(result["skills"]), 1)
        self.assertNotIn("activity", result)
        # 1 verify (executions entity) + 2 fan-out = 3
        self.assertEqual(self.mock_client.command_async.call_count, 3)
        verify_call = self.mock_client.command_async.call_args_list[0]
        self.assertEqual(
            _call_kwargs(verify_call)["override"], f"GET,{guardian._EXECUTIONS_ENTITIES_ROUTE}"
        )
        self.assertEqual(_call_kwargs(verify_call)["parameters"]["id"], "sess-1")

    def test_with_activity(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgenticSessionId": "eb5ca156"}], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[{"__id": "aisess:aaaa:eb5ca156", "AgenticProduct": "Claude Code"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.get_guardian_session_detail(session_id="eb5ca156", include_activity=True)
        )

        self.assertIn("activity", result)
        self.assertEqual(result["activity"]["__id"], "aisess:aaaa:eb5ca156")
        # The graph leg passes the raw session_id to session-activity.
        activity_call = self.mock_client.command_async.call_args_list[3]
        self.assertEqual(
            _call_kwargs(activity_call)["override"], f"GET,{guardian._SESSION_ACTIVITY_ROUTE}"
        )
        self.assertEqual(_call_kwargs(activity_call)["parameters"]["ids"], "eb5ca156")

    def test_include_activity_defaults_true(self):
        self.assertIs(
            inspect.signature(self.module.get_guardian_session_detail)
            .parameters["include_activity"].default.default,
            True,
        )

    def test_sub_queries_send_explicit_7d(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgenticSessionId": "sess-1"}], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        asyncio.run(self.module.get_guardian_session_detail(session_id="sess-1"))

        event_overrides = (
            f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}",
            f"GET,{guardian._SKILL_USAGE_QUERY_ROUTE}",
        )
        event_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] in event_overrides
        ]
        self.assertEqual(len(event_calls), 2)
        for call in event_calls:
            self.assertEqual(_call_kwargs(call)["parameters"].get("time_range"), "7d")

    def test_not_found(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module.get_guardian_session_detail(session_id="nonexistent"))

        self.assertIn("error", result)
        self.assertIn("nonexistent", result["error"])

    def test_injection_rejected(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(self.module.get_guardian_session_detail(session_id="x' OR 1==1 --"))
        self.mock_client.command_async.assert_not_called()


class TestGetAiInventory(GuardianToolTestCase):
    """Test get_guardian_inventory tool (async fan-out)."""

    def test_detections_rollup(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[
                {"AgentId": "a1", "AgenticProductTag": "213584428666200", "maxDetectionScore": 90},
                {"AgentId": "a2", "AgenticProductTag": "213584428666201", "maxDetectionScore": 40},
                {"AgentId": "a3", "AgenticProductTag": 0, "maxDetectionScore": 55},
                {"AgentId": "a4", "AgenticProductTag": None, "maxDetectionScore": 30},
            ], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_inventory())

        self.assertEqual(result["detections"]["hosts_with_detections"], 4)
        self.assertEqual(result["detections"]["max_score"], 90)
        self.assertEqual(result["detections"]["unattributed_rows"], 2)
        self.assertFalse(result["detections"]["truncated"])

    def test_all_legs_use_the_same_window(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.get_guardian_inventory(time_range="24h"))

        for call in self.mock_client.command_async.call_args_list:
            self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "24h")

    def test_aggregation(self):
        self.mock_client.command_async.side_effect = [
            # Agents by product tag
            _envelope(200, resources=[
                {"AgentProduct": "213584428666146", "count": 5},
                {"AgentProduct": "213584428666201", "count": 3},
            ], errors=[]),
            # Sessions by product tag — count arrives as a JSON string
            _envelope(200, resources=[
                {"Product": "213584428666146", "count": "7"},
                {"Product": "213584428666201", "count": "1"},
            ], errors=[]),
            # Tools by name
            _envelope(200, resources=[
                {"Name": "Bash", "count": 100},
                {"Name": "Read", "count": 80},
            ], errors=[]),
            # Detections aggregate
            _envelope(200, resources=[], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_inventory())

        self.assertEqual(result["agents"]["total"], 8)
        self.assertEqual(result["agents"]["by_product"]["213584428666146"], 5)
        self.assertEqual(result["agents"]["by_product"]["213584428666201"], 3)
        # Sessions are now grouped by product; "7" coerces to int 7.
        self.assertEqual(result["sessions"]["by_product"]["213584428666146"], 7)
        self.assertEqual(result["sessions"]["by_product"]["213584428666201"], 1)
        self.assertEqual(result["sessions"]["total"], 8)
        self.assertEqual(result["sessions"]["products_reporting"], 2)
        self.assertNotIn("by_host", result["sessions"])
        self.assertIn("note", result["sessions"])
        self.assertEqual(result["tools"]["by_name"]["Bash"], 100)

    def test_product_tag_float_does_not_collapse_buckets(self):
        """A JSON-number tag must key by plain integer, not exponent form."""
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[
                {"AgentProduct": 213584428666146.0, "count": 5},
                {"AgentProduct": 213584428666201.0, "count": 3},
            ], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_inventory())

        self.assertEqual(result["agents"]["by_product"]["213584428666146"], 5)
        self.assertEqual(result["agents"]["by_product"]["213584428666201"], 3)
        self.assertNotIn("unknown", result["agents"]["by_product"])

    def test_friendly_product_name_preferred_with_numeric_fallback(self):
        """Buckets decorated with a friendly name key on it; undecorated tags fall back."""
        self.mock_client.command_async.side_effect = [
            # Agents: one decorated bucket, one bare (unresolved tag)
            _envelope(200, resources=[
                {"AgentProduct": "213584428666146", "AgentProductName": "Claude Code", "count": 5},
                {"AgentProduct": "999999999999999", "count": 2},
            ], errors=[]),
            # Sessions: decorated with the ProductName sibling
            _envelope(200, resources=[
                {"Product": "213584428666146", "ProductName": "Claude Code", "count": "7"},
            ], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_inventory())

        # Friendly name is the key when present.
        self.assertEqual(result["agents"]["by_product"]["Claude Code"], 5)
        self.assertEqual(result["sessions"]["by_product"]["Claude Code"], 7)
        # Undecorated tag falls back to the plain integer string.
        self.assertEqual(result["agents"]["by_product"]["999999999999999"], 2)

    def test_sessions_aggregate_uses_the_window(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.get_guardian_inventory())

        sessions_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._AGENT_SESSIONS_AGGREGATES_ROUTE}"
        ]
        self.assertEqual(len(sessions_calls), 1)
        self.assertEqual(_call_kwargs(sessions_calls[0])["parameters"]["time_range"], "7d")

    def test_non_numeric_count_becomes_zero(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgentProduct": "213584428666201", "count": "bogus"}], errors=[]),
            _envelope(200, resources=[{"Product": "213584428666146", "count": None}], errors=[]),
            _envelope(200, resources=[{"Name": "Bash", "count": "x"}], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_inventory())

        self.assertEqual(result["agents"]["by_product"]["213584428666201"], 0)
        self.assertEqual(result["sessions"]["by_product"]["213584428666146"], 0)
        self.assertEqual(result["tools"]["by_name"]["Bash"], 0)

    def test_no_notices_key_when_clean(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module.get_guardian_inventory())

        self.assertNotIn("notices", result)

    def test_parallel_execution(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.get_guardian_inventory())

        self.assertEqual(self.mock_client.command_async.call_count, 4)

    def test_tools_aggregate_sends_time_range(self):
        """The tools aggregate now accepts time_range."""
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.get_guardian_inventory())

        tools_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._TOOLS_AGGREGATES_ROUTE}"
        ]
        self.assertEqual(len(tools_calls), 1)
        self.assertEqual(_call_kwargs(tools_calls[0])["parameters"]["time_range"], "7d")

    def test_single_time_range_parameter(self):
        """The separate logscale_time_range parameter was removed."""
        sig = inspect.signature(self.module.get_guardian_inventory).parameters
        self.assertIn("time_range", sig)
        self.assertNotIn("logscale_time_range", sig)


class TestPivotOnAttribute(GuardianToolTestCase):
    """Test pivot_on_guardian_attribute tool (async)."""

    def test_product_field(self):
        self.mock_client.command_async.return_value = _envelope(
            200, resources=[{"Id": "inst-1", "AgentProduct": "213584428666146"}], errors=[]
        )

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(
                attribute="Product", value="Claude Code", time_range="7d"
            )
        )

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command_async.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._AGENTS_QUERY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["product"], "CLAUDE_CODE")

    def test_hostname_field(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="HostName", value="dev1", time_range="7d")
        )

        params = _call_kwargs(self.mock_client.command_async.call_args)["parameters"]
        self.assertEqual(params["hostname"], "dev1")

    def test_skill_field(self):
        self.mock_client.command_async.return_value = _envelope(
            200, resources=[{"Id": "sk-1", "SkillName": "review"}], errors=[]
        )

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="Skill", value="review", time_range="7d")
        )

        self.assertEqual(len(result["results"]), 1)
        call = self.mock_client.command_async.call_args
        self.assertEqual(_call_kwargs(call)["override"], f"GET,{guardian._SKILLS_QUERY_ROUTE}")
        self.assertEqual(_call_kwargs(call)["parameters"]["name_filter"], "review")

    def test_name_field(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"aid": "a1", "AgenticSkill": "review"}], errors=[]),
            _envelope(200, resources=[{"aid": "a2", "AgenticToolName": "Bash"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="Name", value="Bash", time_range="7d")
        )

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(self.mock_client.command_async.call_count, 2)
        for call in self.mock_client.command_async.call_args_list:
            self.assertEqual(_call_kwargs(call)["parameters"].get("time_range"), "7d")

    def test_invalid_attribute(self):
        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="BadField", value="x", time_range="7d")
        )

        self.assertIn("error", result)
        self.assertIn("Invalid attribute", result["error"])
        self.mock_client.command_async.assert_not_called()

    def test_working_directory_no_longer_allowed(self):
        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(
                attribute="WorkingDirectory", value="/src", time_range="7d"
            )
        )
        self.assertIn("error", result)

    def test_agentic_model_no_longer_allowed(self):
        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(
                attribute="AgenticModel", value="claude", time_range="7d"
            )
        )
        self.assertIn("error", result)

    def test_name_deduplicates_by_sensor_id(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"aid": "a1", "AgenticSkill": "x"}], errors=[]),
            _envelope(200, resources=[{"aid": "a1", "AgenticToolName": "Bash"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="Name", value="Bash", time_range="7d")
        )

        self.assertEqual(len(result["results"]), 1)

    def test_name_keeps_rows_without_aid(self):
        # A row lacking `aid` cannot participate in sensor dedup, but it must not
        # be silently dropped — the tool would otherwise hide real tool-usage rows.
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgenticSkill": "x"}], errors=[]),
            _envelope(200, resources=[{"AgenticToolName": "Bash"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="Name", value="Bash", time_range="7d")
        )

        self.assertEqual(len(result["results"]), 2)

    def test_name_dedupes_by_aid_but_keeps_distinct_and_aidless_rows(self):
        # Two rows share aid a1 (collapse to one); a2 is distinct; the aid-less row
        # is kept. Expect 3 results.
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[
                {"aid": "a1", "AgenticSkill": "x"},
                {"aid": "a2", "AgenticSkill": "y"},
            ], errors=[]),
            _envelope(200, resources=[
                {"aid": "a1", "AgenticToolName": "Bash"},
                {"AgenticToolName": "Read"},
            ], errors=[]),
        ]

        result = asyncio.run(
            self.module.pivot_on_guardian_attribute(attribute="Name", value="Bash", time_range="7d")
        )

        self.assertEqual(len(result["results"]), 3)

    def test_every_allowed_attribute_returns_the_same_envelope_shape(self):
        self.mock_client.command_async.return_value = _envelope(
            200, resources=[{"aid": "a1"}], errors=[]
        )

        for attribute in ("Product", "HostName", "Skill", "Name"):
            with self.subTest(attribute=attribute):
                result = asyncio.run(
                    self.module.pivot_on_guardian_attribute(
                        attribute=attribute, value="x", time_range="7d"
                    )
                )
                self.assertIsInstance(result, dict)
                self.assertIn("results", result)


class TestGetFileEvents(GuardianToolTestCase):
    """Test get_guardian_file_events tool (async fan-out)."""

    def test_combined_sources(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156-1128-44ab-b933-3154a36e8a54"
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{
                "__id": vertex_key,
                "SessionProcessPid": [{
                    "Process": {
                        "ImageFileName": "/usr/bin/node",
                        "__id": "pid:abc:1234",
                        "ModuleWrittenMod": [{
                            "EventCloudTime": "2026-05-01T10:00:00Z",
                            "Module": {"TargetFileName": "/tmp/output.js", "SHA256HashData": "abc123"},
                        }],
                    },
                }],
            }], errors=[]),
            _envelope(200, resources=[
                {"AgenticToolName": "Write", "AgenticPath": "/home/user/file.py", "CommandLine": "write file.py"},
                {"AgenticToolName": "Read", "AgenticPath": "/etc/passwd", "CommandLine": None},
                {"AgenticToolName": "Bash", "AgenticPath": None, "CommandLine": "ls -la"},
            ], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_file_events(session_id=vertex_key))

        self.assertEqual(len(result["module_writes"]), 1)
        self.assertEqual(result["module_writes"][0]["file"], "/tmp/output.js")
        self.assertEqual(len(result["tool_file_access"]), 2)
        self.assertEqual(result["tool_file_access"][0]["tool"], "Write")

    def test_sensitive_only(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156-1128-44ab-b933-3154a36e8a54"
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{
                "__id": vertex_key,
                "SessionProcessPid": [{
                    "Process": {
                        "ImageFileName": "/usr/bin/node",
                        "__id": "pid:abc:1234",
                        "ModuleWrittenMod": [
                            {"EventCloudTime": "t", "Module": {"TargetFileName": "/tmp/output.js", "SHA256HashData": "a"}},
                            {"EventCloudTime": "t", "Module": {"TargetFileName": "/home/user/.env.local", "SHA256HashData": "b"}},
                        ],
                    },
                }],
            }], errors=[]),
            _envelope(200, resources=[
                {"AgenticToolName": "Read", "AgenticPath": "/home/user/.env.local", "CommandLine": None},
                {"AgenticToolName": "Read", "AgenticPath": "/tmp/normal.txt", "CommandLine": None},
            ], errors=[]),
        ]

        result = asyncio.run(
            self.module.get_guardian_file_events(session_id=vertex_key, sensitive_only=True)
        )

        self.assertEqual(len(result["module_writes"]), 1)
        self.assertEqual(result["module_writes"][0]["file"], "/home/user/.env.local")
        self.assertEqual(len(result["tool_file_access"]), 1)
        self.assertEqual(result["tool_file_access"][0]["path"], "/home/user/.env.local")

    def test_none_path_values_coerced_to_empty_string(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156"
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"__id": vertex_key, "SessionProcessPid": []}], errors=[]),
            _envelope(200, resources=[
                {"AgenticToolName": "Glob", "AgenticPath": None, "CommandLine": None},
                {"AgenticToolName": "Read", "AgenticPath": "/tmp/test.txt", "CommandLine": None},
            ], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_file_events(session_id=vertex_key))

        self.assertEqual(len(result["tool_file_access"]), 2)
        self.assertEqual(result["tool_file_access"][0]["path"], "")
        self.assertEqual(result["tool_file_access"][0]["command_line"], "")

    def test_null_session_process_edge_is_skipped(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156"
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"__id": vertex_key, "SessionProcessPid": [None]}], errors=[]),
            _envelope(200, resources=[
                {"AgenticToolName": "Read", "AgenticPath": "/tmp/test.txt", "CommandLine": None},
            ], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_file_events(session_id=vertex_key))

        self.assertEqual(result["module_writes"], [])
        self.assertEqual(len(result["tool_file_access"]), 1)

    def test_null_module_written_edge_is_skipped(self):
        vertex_key = "aisess:abc123def456abc123def456abc123de:eb5ca156"
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{
                "__id": vertex_key,
                "SessionProcessPid": [{
                    "Process": {"ImageFileName": "/usr/bin/node", "__id": "pid:abc:1234", "ModuleWrittenMod": [None]},
                }],
            }], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        result = asyncio.run(self.module.get_guardian_file_events(session_id=vertex_key))

        self.assertEqual(result["module_writes"], [])

    def test_default_time_range_is_2h(self):
        vertex_key = "aisess:abc:sess-1"
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.get_guardian_file_events(session_id=vertex_key))

        tool_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}"
        ]
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(_call_kwargs(tool_calls[0])["parameters"]["time_range"], "2h")


class TestGenerateReport(GuardianToolTestCase):
    """Test generate_guardian_report tool (async; composes sync and async tools)."""

    def test_invalid_type(self):
        result = asyncio.run(self.module.generate_guardian_report(report_type="invalid"))

        self.assertIn("error", result)
        self.assertIn("Invalid report_type", result["error"])
        self.mock_client.command.assert_not_called()
        self.mock_client.command_async.assert_not_called()

    def test_fleet_summary(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"SkillName": "commit", "count": 5}], errors=[]
        )
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module.generate_guardian_report(report_type="fleet_summary"))

        self.assertEqual(result["report_type"], "fleet_summary")
        self.assertIn("generated_at", result)
        self.assertIn("inventory", result["data"])
        self.assertIn("skills", result["data"])
        # inventory: 4 async calls; fleet skill inventory: 1 sync (offloaded)
        self.assertEqual(self.mock_client.command_async.call_count, 4)
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_fleet_summary_threads_time_range(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        asyncio.run(self.module.generate_guardian_report(report_type="fleet_summary", time_range="30d"))

        agents_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._AGENTS_AGGREGATES_ROUTE}"
        ]
        self.assertEqual(len(agents_calls), 1)
        self.assertEqual(_call_kwargs(agents_calls[0])["parameters"]["time_range"], "30d")

    def test_skill_threat(self):
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"SkillName": "suspicious-skill", "count": 3}], errors=[]
        )

        result = asyncio.run(self.module.generate_guardian_report(report_type="skill_threat"))

        self.assertEqual(result["report_type"], "skill_threat")
        self.assertIn("skills", result["data"])
        self.mock_client.command_async.assert_not_called()

    def test_sensitive_access(self):
        # search_guardian_executions leg (sync)
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"AgenticSessionId": "sess-1"}], errors=[]
        )
        # get_guardian_file_events legs (async): graph + inventory
        self.mock_client.command_async.return_value = _envelope(
            200, resources=[{"__id": "aisess:s1:sess-1", "SessionProcessPid": []}], errors=[]
        )

        result = asyncio.run(self.module.generate_guardian_report(report_type="sensitive_access"))

        self.assertEqual(result["report_type"], "sensitive_access")
        self.assertIn("data", result)

    def test_sensitive_access_drives_from_executions(self):
        """Session IDs come from search_guardian_executions (flat AgenticSessionId)."""
        self.mock_client.command.return_value = _envelope(
            200, resources=[{"AgenticSessionId": "sess-1"}], errors=[]
        )
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"__id": "aisess:s1:sess-1", "SessionProcessPid": []}], errors=[]),
            _envelope(200, resources=[{"AgenticToolName": "Read", "AgenticPath": "/app/.env"}], errors=[]),
        ]

        result = asyncio.run(
            self.module.generate_guardian_report(report_type="sensitive_access", time_range="7d")
        )

        self.assertEqual(len(result["data"]["sensitive_sessions"]), 1)
        self.assertEqual(result["data"]["sensitive_sessions"][0]["session_id"], "sess-1")
        # The executions leg is the source, not agent-sessions.
        exec_calls = [
            c
            for c in self.mock_client.command.call_args_list
            if _call_kwargs(c)["override"] == f"GET,{guardian._EXECUTIONS_QUERY_ROUTE}"
        ]
        self.assertEqual(len(exec_calls), 1)

    def test_agent_detail_requires_agent_id(self):
        result = asyncio.run(self.module.generate_guardian_report(report_type="agent_detail"))

        self.assertIn("error", result)
        self.assertIn("agent_id is required", result["error"])

    def test_agent_detail_injection_rejected(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(
                self.module.generate_guardian_report(
                    report_type="agent_detail", agent_id="x' OR 1==1 --"
                )
            )
        self.mock_client.command_async.assert_not_called()

    def test_agent_detail(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{
                "Id": "inst-1", "SensorId": "aid-1", "AgentProduct": "213584428666146",
            }], errors=[]),
            *[_envelope(200, resources=[], errors=[]) for _ in range(6)],
        ]

        result = asyncio.run(
            self.module.generate_guardian_report(report_type="agent_detail", agent_id="inst-1")
        )

        self.assertEqual(result["report_type"], "agent_detail")
        self.assertEqual(result["data"]["agent"]["instance"]["Id"], "inst-1")
        self.mock_client.command.assert_not_called()

    def test_time_range_present_for_fleet_summary_and_sensitive_access(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        fleet = asyncio.run(self.module.generate_guardian_report(report_type="fleet_summary"))
        sensitive = asyncio.run(self.module.generate_guardian_report(report_type="sensitive_access"))

        self.assertIn("time_range", fleet)
        self.assertIn("time_range", sensitive)

    def test_time_range_absent_for_agent_detail_and_skill_threat(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])
        self.mock_client.command_async.return_value = _envelope(
            200, resources=[{"Id": "inst-1", "SensorId": "aid-1"}], errors=[]
        )

        agent_detail = asyncio.run(
            self.module.generate_guardian_report(report_type="agent_detail", agent_id="inst-1")
        )
        skill_threat = asyncio.run(self.module.generate_guardian_report(report_type="skill_threat"))

        self.assertNotIn("time_range", agent_detail)
        self.assertNotIn("time_range", skill_threat)


class TestExtractSessionIdFromVertexKey(GuardianToolTestCase):
    """Test _extract_session_id_from_vertex_key helper."""

    def test_extracts_uuid_from_vertex_key(self):
        result = self.module._extract_session_id_from_vertex_key(
            "aisess:abc123def456:550e8400-e29b-41d4-a716-446655440000"
        )
        self.assertEqual(result, "550e8400-e29b-41d4-a716-446655440000")

    def test_raw_uuid_passthrough(self):
        result = self.module._extract_session_id_from_vertex_key(
            "550e8400-e29b-41d4-a716-446655440000"
        )
        self.assertEqual(result, "550e8400-e29b-41d4-a716-446655440000")

    def test_vertex_key_with_only_two_parts(self):
        result = self.module._extract_session_id_from_vertex_key("aisess:abc123")
        self.assertEqual(result, "aisess:abc123")

    def test_uuid_in_session_id_part_preserved(self):
        result = self.module._extract_session_id_from_vertex_key("aisess:abc123:uuid-with:colon")
        self.assertEqual(result, "uuid-with:colon")


class TestPickDetectionScore(GuardianToolTestCase):
    """Test the two-key detections join, keyed via _tag_key."""

    def test_exact_two_key_match(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": "213584428666200", "maxDetectionScore": 90},
        ])
        self.assertEqual(
            self.module._pick_detection_score(response, "aid-1", "213584428666200"), 90
        )

    def test_same_host_different_product_does_not_match(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": "213584428666201", "maxDetectionScore": 90},
        ])
        self.assertIsNone(self.module._pick_detection_score(response, "aid-1", "213584428666200"))

    def test_different_host_same_product_does_not_match(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-2", "AgenticProductTag": "213584428666200", "maxDetectionScore": 90},
        ])
        self.assertIsNone(self.module._pick_detection_score(response, "aid-1", "213584428666200"))

    def test_float_versus_string_tag_still_matches(self):
        """The float-exponent bug: a JSON-number tag must match a string product."""
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": 213584428666200.0, "maxDetectionScore": 75},
        ])
        self.assertEqual(
            self.module._pick_detection_score(response, "aid-1", "213584428666200"), 75
        )

    def test_int_versus_string_tag_still_matches(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": 213584428666200, "maxDetectionScore": 75},
        ])
        self.assertEqual(
            self.module._pick_detection_score(response, "aid-1", "213584428666200"), 75
        )

    def test_unattributed_tag_falls_back_to_host_scope(self):
        for absent_tag in (None, 0, "0"):
            response = GuardianResponse(resources=[
                {"AgentId": "aid-1", "AgenticProductTag": absent_tag, "maxDetectionScore": 90},
            ])
            result = self.module._pick_detection_score(response, "aid-1", "213584428666200")
            self.assertEqual(result["host_max_score"], 90, f"tag={absent_tag!r}")
            self.assertEqual(result["scope"], "host", f"tag={absent_tag!r}")
            self.assertIn("note", result)

    def test_exact_match_preferred_over_host_fallback(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": 0, "maxDetectionScore": 99},
            {"AgentId": "aid-1", "AgenticProductTag": "213584428666200", "maxDetectionScore": 55},
        ])
        self.assertEqual(
            self.module._pick_detection_score(response, "aid-1", "213584428666200"), 55
        )

    def test_no_row_for_host_returns_none(self):
        response = GuardianResponse(resources=[
            {"AgentId": "aid-9", "AgenticProductTag": 0, "maxDetectionScore": 90},
        ])
        self.assertIsNone(self.module._pick_detection_score(response, "aid-1", "213584428666200"))

    def test_error_response_surfaces_error(self):
        response = GuardianResponse(errors=[{"message": "boom"}])
        result = self.module._pick_detection_score(response, "aid-1", "213584428666200")
        self.assertIn("error", result)

    def test_empty_product_matches_nothing(self):
        """An agent with no product tag matches nothing, not every tag-less row."""
        response = GuardianResponse(resources=[
            {"AgentId": "aid-1", "AgenticProductTag": "213584428666200", "maxDetectionScore": 90},
        ])
        self.assertIsNone(self.module._pick_detection_score(response, "aid-1", None))


class TestMissingAidResponse(GuardianToolTestCase):
    """Test _missing_aid_response: the stand-in for an unscoped event query."""

    def test_returns_error_not_empty_activity(self):
        response = self.module._missing_aid_response()

        self.assertFalse(response.ok)
        self.assertEqual(response.count, 0)
        self.assertIn("SensorId", response.errors[0]["message"])


class TestFormatResponseAndSubResult(GuardianToolTestCase):
    """Test _format_response / _sub_result / _with_notices / _unwrap_results."""

    def test_success_returns_results_and_pagination_envelope(self):
        response = GuardianResponse(resources=[{"id": "1"}, {"id": "2"}])
        result = self.module._format_response(response)
        self.assertEqual(result["results"], [{"id": "1"}, {"id": "2"}])
        self.assertIn("pagination", result)

    def test_error_returns_error_dict(self):
        response = GuardianResponse(resources=[], errors=[{"message": "x"}])
        result = self.module._format_response(response)
        self.assertEqual(result["error"], [{"message": "x"}])
        self.assertNotIn("results", result)

    def test_limit_truncates_results(self):
        response = GuardianResponse(resources=[{"id": str(i)} for i in range(5)])
        result = self.module._format_response(response, limit=3)
        self.assertEqual(len(result["results"]), 3)

    def test_limit_none_returns_all(self):
        response = GuardianResponse(resources=[{"id": str(i)} for i in range(10)])
        result = self.module._format_response(response, limit=None)
        self.assertEqual(len(result["results"]), 10)

    def test_empty_resources(self):
        result = self.module._format_response(GuardianResponse(resources=[]))
        self.assertEqual(result["results"], [])

    def test_notices_added_alongside_envelope(self):
        response = GuardianResponse(resources=[{"id": "1"}], notices=["narrowed"])
        result = self.module._format_response(response)
        self.assertEqual(result["notices"], ["narrowed"])

    def test_no_notices_omits_notices_key(self):
        result = self.module._format_response(GuardianResponse(resources=[{"id": "1"}]))
        self.assertNotIn("notices", result)

    def test_error_includes_notices(self):
        response = GuardianResponse(errors=[{"message": "timed out"}], notices=["ladder exhausted"])
        result = self.module._format_response(response)
        self.assertEqual(result["notices"], ["ladder exhausted"])

    def test_pagination_total_blanked_on_full_page(self):
        response = GuardianResponse(
            resources=[{"id": str(i)} for i in range(50)],
            pagination={"offset": 0, "limit": 50, "total": 50},
        )
        result = self.module._format_response(response, limit=50)
        self.assertIsNone(result["pagination"]["total"])

    def test_pagination_total_kept_on_short_page(self):
        response = GuardianResponse(
            resources=[{"id": str(i)} for i in range(3)],
            pagination={"offset": 20, "limit": 50, "total": 23},
        )
        result = self.module._format_response(response, limit=50)
        self.assertEqual(result["pagination"]["total"], 23)

    def test_no_pagination_metadata_reports_none(self):
        result = self.module._format_response(GuardianResponse(resources=[{"id": "1"}], pagination=None))
        self.assertEqual(result["pagination"], {"total": None, "next": None})

    def test_sub_result_includes_notices(self):
        response = GuardianResponse(resources=[{"id": "1"}], notices=["narrowed"])
        result = self.module._sub_result(response, 50)
        self.assertEqual(result["results"], [{"id": "1"}])
        self.assertEqual(result["notices"], ["narrowed"])

    def test_sub_result_without_notices_is_bare_list(self):
        response = GuardianResponse(resources=[{"id": "1"}])
        self.assertEqual(self.module._sub_result(response, 50), [{"id": "1"}])

    def test_sub_result_error_returns_error_dict(self):
        result = self.module._sub_result(GuardianResponse(errors=[{"message": "boom"}]), 50)
        self.assertEqual(result["error"], [{"message": "boom"}])

    def test_sub_result_truncates_client_side(self):
        response = GuardianResponse(resources=[{"id": str(i)} for i in range(10)])
        self.assertEqual(len(self.module._sub_result(response, 3)), 3)

    def test_with_notices_attaches_when_present(self):
        payload = self.module._with_notices({"error": []}, GuardianResponse(notices=["a notice"]))
        self.assertEqual(payload["notices"], ["a notice"])

    def test_with_notices_leaves_payload_untouched_when_empty(self):
        payload = self.module._with_notices({"error": []}, GuardianResponse(notices=[]))
        self.assertNotIn("notices", payload)

    def test_unwrap_results_splits_wrapped_value(self):
        payload, notices = self.module._unwrap_results(
            {"results": [{"id": "1"}], "notices": ["narrowed"]}
        )
        self.assertEqual(payload, [{"id": "1"}])
        self.assertEqual(notices, ["narrowed"])

    def test_unwrap_results_passes_bare_list_through(self):
        payload, notices = self.module._unwrap_results([{"id": "1"}])
        self.assertEqual(payload, [{"id": "1"}])
        self.assertEqual(notices, [])

    def test_unwrap_results_passes_error_dict_through(self):
        error_payload = {"error": [{"message": "boom"}]}
        payload, notices = self.module._unwrap_results(error_payload)
        self.assertEqual(payload, error_payload)
        self.assertEqual(notices, [])


class TestLogscaleDefaultWindow(GuardianToolTestCase):
    """LogScale-backed tools default to the API's own 2h window; entity-backed
    tools default to 7d; internal fan-out legs state 7d explicitly."""

    def _default_of(self, method, name="time_range"):
        return inspect.signature(method).parameters[name].default.default

    def test_tool_usage_default_is_2h(self):
        self.assertEqual(self._default_of(self.module.search_guardian_tool_usage), "2h")

    def test_executions_default_is_2h(self):
        self.assertEqual(self._default_of(self.module.search_guardian_executions), "2h")

    def test_skill_usage_default_is_2h(self):
        self.assertEqual(self._default_of(self.module.search_guardian_skill_usage), "2h")

    def test_prompts_default_is_2h(self):
        self.assertEqual(self._default_of(self.module.search_guardian_prompts), "2h")

    def test_file_events_default_is_2h(self):
        self.assertEqual(self._default_of(self.module.get_guardian_file_events), "2h")

    def test_agents_default_is_7d(self):
        self.assertEqual(self._default_of(self.module.search_guardian_agents), "7d")

    def test_agent_sessions_default_is_7d(self):
        """Now entity-backed (filters LastSeen), so 7d, not the old 2h."""
        self.assertEqual(self._default_of(self.module.get_guardian_agent_sessions), "7d")

    def test_tools_default_is_7d(self):
        self.assertEqual(self._default_of(self.module.search_guardian_tools), "7d")

    def test_agent_profile_fanout_uses_7d(self):
        self.mock_client.command_async.side_effect = (
            [_envelope(200, resources=[{"Id": "i1", "SensorId": "aid-1"}], errors=[])]
            + [_envelope(200, resources=[], errors=[]) for _ in range(6)]
        )

        asyncio.run(self.module._agent_profile("i1"))

        event_overrides = (
            f"GET,{guardian._EXECUTIONS_QUERY_ROUTE}",
            f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}",
        )
        event_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"] in event_overrides
        ]
        self.assertEqual(len(event_calls), 2)
        for call in event_calls:
            self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")

    def test_session_detail_fanout_uses_7d(self):
        self.mock_client.command_async.side_effect = [
            _envelope(200, resources=[{"AgenticSessionId": "s1"}], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
            _envelope(200, resources=[], errors=[]),
        ]

        asyncio.run(self.module.get_guardian_session_detail(session_id="s1"))

        usage_calls = [
            c
            for c in self.mock_client.command_async.call_args_list
            if _call_kwargs(c)["override"]
            in (f"GET,{guardian._TOOL_USAGE_QUERY_ROUTE}", f"GET,{guardian._SKILL_USAGE_QUERY_ROUTE}")
        ]
        for call in usage_calls:
            self.assertEqual(_call_kwargs(call)["parameters"]["time_range"], "7d")


class TestSecurity(GuardianToolTestCase):
    """Test security controls across tools."""

    def test_list_agents_normalizes_then_passes_product_to_server(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents(product="x' OR 1==1 --", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "X'_OR_1==1___")

    def test_list_agents_passes_hostname_to_server(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_agents(hostname="x' OR 1==1 --", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["hostname"], "x' OR 1==1 --")

    def test_list_sessions_passes_product_to_server(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.get_guardian_agent_sessions(product="CLAUDE_CODE", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["product"], "CLAUDE_CODE")
        self.assertNotIn("sensor_id", params)

    def test_list_tool_usage_passes_tool_name_to_server(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_tool_usage(tool_name="x' OR 1==1 --", time_range="7d")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["tool_name"], "x' OR 1==1 --")

    def test_search_prompts_passes_session_id_to_server(self):
        self.mock_client.command.return_value = _envelope(200, resources=[], errors=[])

        self.module.search_guardian_prompts(session_id="x' OR 1==1 --")

        params = _call_kwargs(self.mock_client.command.call_args)["parameters"]
        self.assertEqual(params["session_id"], "x' OR 1==1 --")

    def test_get_agent_rejects_single_quote(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(self.module.get_guardian_agent(agent_id="x' OR 1==1 --"))

    def test_get_agent_rejects_backslash(self):
        with self.assertRaisesRegex(ValueError, "backslashes"):
            asyncio.run(self.module.get_guardian_agent(agent_id="abc\\def"))

    def test_get_agent_rejects_newline(self):
        with self.assertRaisesRegex(ValueError, "newlines"):
            asyncio.run(self.module.get_guardian_agent(agent_id="abc\ndef"))

    def test_get_agent_accepts_clean_id(self):
        self.mock_client.command_async.return_value = _envelope(200, resources=[], errors=[])

        result = asyncio.run(self.module.get_guardian_agent(agent_id="abc123def456"))

        self.assertIn("error", result)  # not found, but no ValueError

    def test_session_detail_rejects_single_quote(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(self.module.get_guardian_session_detail(session_id="x' OR 1==1 --"))

    def test_generate_report_agent_detail_rejects_injection(self):
        with self.assertRaisesRegex(ValueError, "single quotes"):
            asyncio.run(
                self.module.generate_guardian_report(report_type="agent_detail", agent_id="a' OR 1=1")
            )


if __name__ == "__main__":
    unittest.main()
