"""
Tests for the Dynamic mode (two-tool pattern).
"""

import asyncio
import inspect
import json
import unittest
from collections.abc import Coroutine
from typing import Any, TypeVar
from unittest.mock import MagicMock, patch

from mcp.server.fastmcp import FastMCP

from falcon_mcp import registry
from falcon_mcp.dynamic import DynamicMode, DynamicToolCatalog
from falcon_mcp.filter_hints import FILTER_HINTS, QUERY_STRING_HINTS
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.modules.detections import DetectionsModule
from falcon_mcp.modules.hosts import HostsModule
from falcon_mcp.modules.ngsiem import NGSIEMModule
from falcon_mcp.tool_filter import ToolPolicy

_T = TypeVar("_T")


def run_async(coro: Coroutine[Any, Any, _T]) -> _T:
    return asyncio.run(coro)


class TestDynamicToolCatalog(unittest.TestCase):
    """Test cases for DynamicToolCatalog."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.modules = {
            "detections": DetectionsModule(self.mock_client),
            "hosts": HostsModule(self.mock_client),
        }

    def test_catalog_builds_entries_from_modules(self):
        catalog = DynamicToolCatalog(self.modules)
        self.assertGreater(len(catalog.entries), 0)
        self.assertIn("falcon_search_detections", catalog.entries)
        self.assertIn("falcon_search_hosts", catalog.entries)

    def test_catalog_maps_tools_to_modules(self):
        catalog = DynamicToolCatalog(self.modules)
        self.assertEqual(catalog.entries["falcon_search_detections"].module, "detections")
        self.assertEqual(catalog.entries["falcon_search_hosts"].module, "hosts")

    def test_catalog_clears_module_tools_list(self):
        DynamicToolCatalog(self.modules)
        for module in self.modules.values():
            self.assertEqual(module.tools, [])

    def test_search_matches_keyword_in_name(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_detections")
        names = [r["name"] for r in results]
        self.assertIn("falcon_search_detections", names)

    def test_search_matches_keyword_in_description(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="severity")
        self.assertGreater(len(results), 0)

    def test_search_prefers_entries_matching_every_token(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search detections")
        names = [r["name"] for r in results]
        self.assertIn("falcon_search_detections", names)
        # Every result matches both tokens, so the fallback stayed out of it.
        self.assertFalse(catalog.relaxed(query="search detections"))
        for entry in (catalog.entries[n] for n in names):
            self.assertIn("search", entry.search_corpus)
            self.assertIn("detections", entry.search_corpus)

    def test_search_falls_back_to_any_token_when_no_entry_matches_all(self):
        """A phrase carrying one unknown word must not wipe out the whole result set."""
        catalog = DynamicToolCatalog(self.modules)
        strict = catalog.search(query="detections")
        relaxed = catalog.search(query="detections nonexistent_xyz_token", limit=10_000)
        self.assertTrue(catalog.relaxed(query="detections nonexistent_xyz_token"))
        self.assertTrue(relaxed)
        self.assertIn(strict[0]["name"], [r["name"] for r in relaxed])

    def test_search_returns_nothing_when_no_token_matches_at_all(self):
        catalog = DynamicToolCatalog(self.modules)
        self.assertEqual(catalog.search(query="nonexistent_xyz_module"), [])
        self.assertEqual(catalog.count_matches(query="nonexistent_xyz_module"), 0)

    def test_search_module_filter(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(module="detections")
        for r in results:
            self.assertEqual(r["module"], "detections")

    def test_search_respects_limit(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(limit=1)
        self.assertEqual(len(results), 1)

    def test_search_empty_query_returns_all_up_to_limit(self):
        catalog = DynamicToolCatalog(self.modules)
        total = len(catalog.entries)
        results = catalog.search(query="", limit=100)
        self.assertEqual(len(results), total)

    def test_summarize_parameters_flattens_schema(self):
        schema = {
            "properties": {
                "filter": {"type": "string", "description": "FQL filter"},
                "limit": {"type": "integer", "description": "Max results"},
            },
            "required": ["filter"],
        }
        summary = DynamicToolCatalog.summarize_parameters(schema)
        self.assertEqual(summary["filter"]["type"], "string")
        self.assertTrue(summary["filter"]["required"])
        self.assertFalse(summary["limit"]["required"])

    def test_format_entry_includes_annotations(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_search_detections"])
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        self.assertTrue(detection_result["read_only"])
        self.assertFalse(detection_result["destructive"])

    def test_format_entry_appends_filter_hints(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_search_detections"])
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        filter_desc = detection_result["parameters"]["filter"]["description"]
        self.assertIn("severity_name", filter_desc)
        self.assertIn("Common fields:", filter_desc)
        self.assertIn("falcon://detections/search/fql-guide", filter_desc)

    def test_format_entry_appends_host_filter_hints(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_search_hosts"])
        host_result = next(r for r in results if r["name"] == "falcon_search_hosts")
        filter_desc = host_result["parameters"]["filter"]["description"]
        self.assertIn("hostname", filter_desc)
        self.assertIn("platform_name", filter_desc)
        self.assertIn("Common fields:", filter_desc)

    def test_format_entry_no_hint_for_tools_without_filter(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_get_detection_details"])
        detail_result = next(r for r in results if r["name"] == "falcon_get_detection_details")
        for param in detail_result["parameters"].values():
            self.assertNotIn("Common fields:", param["description"])

    def test_format_entry_includes_examples_when_present(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_search_detections"])
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        filter_param = detection_result["parameters"]["filter"]
        self.assertIn("examples", filter_param)
        self.assertIsInstance(filter_param["examples"], list)
        self.assertGreater(len(filter_param["examples"]), 0)

    def test_format_entry_omits_examples_when_absent(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(tool_names=["falcon_get_detection_details"])
        detail_result = next(r for r in results if r["name"] == "falcon_get_detection_details")
        ids_param = detail_result["parameters"]["ids"]
        self.assertNotIn("examples", ids_param)

    def test_format_entry_appends_cql_hint_to_query_string(self):
        """The NGSIEM CQL hint is injected onto the query_string param, not filter."""
        modules: dict[str, BaseModule] = {"ngsiem": NGSIEMModule(self.mock_client)}
        catalog = DynamicToolCatalog(modules)
        results = catalog.search(tool_names=["falcon_search_ngsiem"])
        ngsiem_result = next(r for r in results if r["name"] == "falcon_search_ngsiem")
        params = ngsiem_result["parameters"]
        # NGSIEM has no FQL filter param — the hint lands on query_string.
        self.assertNotIn("filter", params)
        query_desc = params["query_string"]["description"]
        self.assertIn("pipe-based", query_desc)
        self.assertIn("falcon://ngsiem/search/cql-guide", query_desc)

    def test_query_string_hints_no_orphan_keys(self):
        """Every QUERY_STRING_HINTS key maps to a tool with a query_string param."""
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        all_modules = {
            name: cls(mock_client)
            for name, cls in registry.get_available_modules().items()
        }
        catalog = DynamicToolCatalog(all_modules)
        for hint_key in QUERY_STRING_HINTS:
            entry = catalog.entries.get(hint_key)
            self.assertIsNotNone(
                entry,
                f"QUERY_STRING_HINTS has orphan key '{hint_key}' — no matching tool found.",
            )
            assert entry is not None  # narrow for type checker
            properties = entry.tool.parameters.get("properties", {})
            self.assertIn(
                "query_string",
                properties,
                f"QUERY_STRING_HINTS key '{hint_key}' maps to a tool without a query_string param.",
            )

    def test_filter_hints_registry_covers_search_tools(self):
        """Verify that all tools with FQL filter params have hints registered."""
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        all_modules = {
            name: cls(mock_client)
            for name, cls in registry.get_available_modules().items()
        }
        catalog = DynamicToolCatalog(all_modules)
        for name, entry in catalog.entries.items():
            properties = entry.tool.parameters.get("properties", {})
            filter_schema = properties.get("filter", {})
            if "fql-guide" in filter_schema.get("description", ""):
                self.assertIn(
                    name,
                    FILTER_HINTS,
                    f"Tool '{name}' has FQL filter but no hint in FILTER_HINTS",
                )

    def test_filter_hints_no_orphan_keys(self):
        """Verify every FILTER_HINTS key maps to an actual tool in the catalog.

        Guards against stale entries left behind after a tool rename or removal.
        """
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        all_modules = {
            name: cls(mock_client)
            for name, cls in registry.get_available_modules().items()
        }
        catalog = DynamicToolCatalog(all_modules)
        for hint_key in FILTER_HINTS:
            self.assertIn(
                hint_key,
                catalog.entries,
                f"FILTER_HINTS has orphan key '{hint_key}' — no matching tool found. "
                "Remove or rename the entry in filter_hints.py.",
            )


class TestLeanDiscoveryAndSchemaLookup(unittest.TestCase):
    """The two response shapes falcon_search_tools serves.

    Discovery answers "which tool", so it omits the input schema — most of an entry's
    cost, and not needed to choose. Naming tools answers "how do I call it", so those
    entries carry the schema. Confusing the two either overpays on every search or
    leaves an agent unable to build a call.
    """

    def setUp(self):
        self.mock_client = MagicMock()
        self.modules: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client),
            "hosts": HostsModule(self.mock_client),
        }
        self.catalog = DynamicToolCatalog(self.modules)

    def test_discovery_results_omit_parameters(self):
        for kwargs in ({"query": "detections"}, {"module": "hosts"}, {}):
            with self.subTest(**kwargs):
                results = self.catalog.search(**kwargs)
                self.assertTrue(results)
                for entry in results:
                    self.assertNotIn("parameters", entry)

    def test_discovery_results_carry_name_module_description_and_flags(self):
        results = self.catalog.search(query="search_detections")
        entry = next(r for r in results if r["name"] == "falcon_search_detections")
        self.assertEqual(entry["module"], "detections")
        self.assertTrue(entry["description"])
        self.assertTrue(entry["read_only"])
        self.assertFalse(entry["destructive"])
        self.assertEqual(
            set(entry),
            {"name", "module", "description", "read_only", "destructive"},
            "lean entry grew a field — every discovery result pays for it",
        )

    def test_tool_names_returns_full_schema_for_one_name(self):
        results = self.catalog.search(tool_names=["falcon_search_detections"])
        self.assertEqual([r["name"] for r in results], ["falcon_search_detections"])
        self.assertIn("filter", results[0]["parameters"])

    def test_tool_names_returns_full_schema_for_several_names(self):
        """Comparing two candidates must not cost two round trips."""
        asked = ["falcon_search_detections", "falcon_search_hosts"]
        results = self.catalog.search(tool_names=asked)
        self.assertEqual([r["name"] for r in results], asked)
        for entry in results:
            self.assertIn("filter", entry["parameters"])

    def test_tool_names_keeps_the_fql_hint(self):
        """The curated filter hint is the reason the schema path exists."""
        results = self.catalog.search(tool_names=["falcon_search_detections"])
        desc = results[0]["parameters"]["filter"]["description"]
        self.assertIn("severity_name", desc)
        self.assertIn("falcon://detections/search/fql-guide", desc)

    def test_tool_names_keeps_the_cql_hint(self):
        catalog = DynamicToolCatalog({"ngsiem": NGSIEMModule(self.mock_client)})
        results = catalog.search(tool_names=["falcon_search_ngsiem"])
        desc = results[0]["parameters"]["query_string"]["description"]
        self.assertIn("pipe-based", desc)
        self.assertIn("falcon://ngsiem/search/cql-guide", desc)

    def test_tool_names_ignores_query_module_and_limit(self):
        """Naming tools is a schema lookup, so the search parameters do not apply."""
        results = self.catalog.search(
            query="nothing_matches_this",
            module="nosuchmodule",
            limit=1,
            tool_names=["falcon_search_detections", "falcon_search_hosts"],
        )
        self.assertEqual(
            [r["name"] for r in results],
            ["falcon_search_detections", "falcon_search_hosts"],
        )

    def test_count_matches_describes_discovery_not_the_requested_names(self):
        """total must keep meaning "how many tools match", not "how many I asked for"."""
        self.assertEqual(
            self.catalog.count_matches(query="detections"),
            len(self.catalog.search(query="detections", limit=10_000)),
        )

    def test_tool_names_dedupes_repeated_names(self):
        """A name repeated in tool_names must yield one entry, not inflate the count."""
        results = self.catalog.search(
            tool_names=["falcon_search_hosts", "falcon_search_hosts"]
        )
        self.assertEqual([r["name"] for r in results], ["falcon_search_hosts"])


class TestSearchToolsTwoModeEnvelope(unittest.TestCase):
    """The envelope falcon_search_tools returns in each mode."""

    def setUp(self):
        self.mock_client = MagicMock()
        modules: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client),
            "hosts": HostsModule(self.mock_client),
        }
        self.dynamic = DynamicMode(modules, MagicMock())

    def _search(self, **kwargs: Any) -> dict[str, Any]:
        return run_async(self.dynamic._search_tools(**kwargs))

    def test_discovery_hint_directs_the_agent_to_fetch_the_schema(self):
        """A lean result is unusable unless the agent knows the second call exists."""
        result = self._search(query="detections", module=None, limit=50)
        self.assertTrue(result["results"])
        self.assertIn("tool_names", result["hint"])
        self.assertIn("falcon_execute_tool", result["hint"])

    def test_discovery_hint_survives_the_relaxed_and_truncated_hints(self):
        """The schema instruction must not be crowded out by the other hints.

        The query is a genuine fallback case (no tool matches every word), so all three
        hint fragments — relaxed, truncated, and the schema instruction — are present at
        once, and the schema instruction must survive alongside them.
        """
        query = "find all the iocs added this week"
        self.assertTrue(self.dynamic.catalog.relaxed(query=query))
        result = self._search(query=query, module=None, limit=1)
        self.assertTrue(result["truncated"])
        self.assertIn("match at least one", result["hint"])
        self.assertIn("Showing 1 of", result["hint"])
        self.assertIn("tool_names", result["hint"])

    def test_tool_names_dedupes_and_does_not_inflate_total(self):
        """A repeated name returns one schema and total counts what came back."""
        result = self._search(
            tool_names=["falcon_search_detections", "falcon_search_detections"]
        )
        self.assertEqual(
            [r["name"] for r in result["results"]], ["falcon_search_detections"]
        )
        self.assertEqual(result["total"], 1)

    def test_tool_names_envelope_totals_what_it_returned(self):
        result = self._search(tool_names=["falcon_search_detections"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["total"], 1)
        self.assertFalse(result["truncated"])
        self.assertNotIn("hint", result)

    def test_tool_names_reports_an_unknown_name(self):
        """Silently returning fewer entries reads as a tool with no parameters."""
        result = self._search(
            tool_names=["falcon_search_detections", "falcon_not_a_tool"]
        )
        self.assertEqual([r["name"] for r in result["results"]], ["falcon_search_detections"])
        self.assertIn("falcon_not_a_tool", result["hint"])
        self.assertIn("Not available on this server", result["hint"])

    def test_tool_names_reports_every_unknown_name(self):
        result = self._search(tool_names=["falcon_not_a_tool", "falcon_also_absent"])
        self.assertEqual(result["results"], [])
        self.assertIn("falcon_not_a_tool", result["hint"])
        self.assertIn("falcon_also_absent", result["hint"])

    def test_declared_limit_default_matches_the_catalog_default(self):
        """The schema default is what clients actually get, and it is a second default.

        DynamicToolCatalog.search and the registered tool each carry their own
        default. A client omitting limit is served by the declared one, so if the two
        disagree, every measurement taken against the catalog describes a window no
        client ever sees.
        """
        server = FastMCP("probe")
        self.dynamic.server = server
        self.dynamic.register()
        declared = server._tool_manager._tools["falcon_search_tools"].parameters[
            "properties"
        ]["limit"]["default"]
        catalog_default = inspect.signature(
            DynamicToolCatalog.search
        ).parameters["limit"].default
        self.assertEqual(declared, catalog_default)
        self.assertEqual(declared, 50)


class TestWithheldToolsAreAbsentFromBothModes(unittest.TestCase):
    """The schema path must not become a filtering bypass.

    Filtering is enforced by omitting the tool from the catalog, and tool_names looks
    tools up by exact name — the one call shape that would reach a withheld tool if
    the lookup skipped the catalog.
    """

    _WITHHELD = "falcon_search_detections"

    def setUp(self):
        self.mock_client = MagicMock()
        modules: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client),
        }
        self.dynamic = DynamicMode(
            modules, MagicMock(), ToolPolicy(excluded={self._WITHHELD})
        )
        self.assertTrue(self.dynamic.catalog.entries, "surface must be non-empty")

    def test_withheld_tool_absent_from_discovery(self):
        result = run_async(
            self.dynamic._search_tools(query="detections", module=None, limit=500)
        )
        self.assertNotIn(self._WITHHELD, [r["name"] for r in result["results"]])

    def test_withheld_tool_absent_from_schema_lookup(self):
        result = run_async(self.dynamic._search_tools(tool_names=[self._WITHHELD]))
        self.assertEqual(result["results"], [])

    def test_schema_lookup_attributes_the_withholding_to_configuration(self):
        """An operator's config choice must not read as a missing product capability."""
        result = run_async(self.dynamic._search_tools(tool_names=[self._WITHHELD]))
        self.assertIn("Withheld", result["hint"])
        self.assertIn("deny-list", result["hint"])
        self.assertNotIn("Not available on this server", result["hint"])

    def test_schema_lookup_separates_withheld_from_never_served(self):
        """Both are missing; only one is the operator's doing."""
        result = run_async(
            self.dynamic._search_tools(
                tool_names=[self._WITHHELD, "falcon_not_a_tool"]
            )
        )
        self.assertIn(f"{self._WITHHELD} (deny-list)", result["hint"])
        self.assertIn(
            "Not available on this server: falcon_not_a_tool", result["hint"]
        )


class TestSearchRanking(unittest.TestCase):
    """Result POSITION, not just membership.

    In dynamic mode falcon_search_tools is the only path to a capability, so where a
    tool lands in the list is what decides tool selection. These run against the
    whole catalog because rank is a property of the full field of competitors.
    """

    def setUp(self):
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        self.catalog = DynamicToolCatalog(
            {
                name: cls(mock_client)
                for name, cls in registry.get_available_modules().items()
            }
        )

    def _names(self, query: str, **kwargs: Any) -> list[str]:
        return [r["name"] for r in self.catalog.search(query=query, **kwargs)]

    def test_host_details_ranks_get_host_details_first(self):
        self.assertEqual(self._names("host details")[0], "falcon_get_host_details")

    def test_hosts_ranks_search_hosts_first(self):
        self.assertEqual(self._names("hosts")[0], "falcon_search_hosts")

    def test_vulnerabilities_ranks_search_vulnerabilities_first(self):
        self.assertEqual(
            self._names("vulnerabilities")[0], "falcon_search_vulnerabilities"
        )

    def test_bare_host_at_default_limit_still_contains_host_details(self):
        """'host' matches more tools than the default shows; the intended one must survive."""
        names = self._names("host")
        self.assertIn("falcon_get_host_details", names)

    def test_bare_host_at_default_limit_is_not_truncated_at_all(self):
        """What the wider default buys: 'host' matches 35 tools and all 35 fit.

        Ranking alone already kept falcon_get_host_details in a 20-wide window, so
        asserting only its membership does not pin the default. Asserting the whole
        match set fits does — a narrower default truncates and fails here.
        """
        total = self.catalog.count_matches(query="host")
        self.assertGreater(total, 20, "query must exceed the previous default")
        self.assertEqual(len(self._names("host")), total)

    def test_lean_discovery_at_the_new_default_costs_less_than_full_entries_at_20(self):
        """The wider window is only affordable because entries dropped their schema.

        Compares serialized payloads on the real catalog: a full 50 lean results
        against the 20 full ones the previous default returned. If this inverts, the
        default limit is no longer paid for.
        """
        lean_50 = self.catalog.search(query="")
        self.assertEqual(len(lean_50), 50, "expected the default to fill the window")
        full_20 = [
            self.catalog._format_entry(e)
            for e in self.catalog._matches("", None)[:20]
        ]
        self.assertLess(len(json.dumps(lean_50)), len(json.dumps(full_20)))

    def test_exact_tool_name_ranks_first_with_and_without_prefix(self):
        for query in ("falcon_search_detections", "search_detections"):
            with self.subTest(query=query):
                self.assertEqual(self._names(query)[0], "falcon_search_detections")

    def test_name_match_outranks_description_only_match(self):
        names = self._names("quarantined files")
        top = self.catalog.entries[names[0]]
        self.assertIn("quarantined", top.name_words)

    def test_ranking_is_independent_of_module_iteration_order(self):
        """Catalog order comes from a set of module names, so it varies per process."""
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        available = registry.get_available_modules()
        reversed_catalog = DynamicToolCatalog(
            {name: available[name](mock_client) for name in reversed(list(available))}
        )
        for query in ("host details", "hosts", "vulnerabilities", "host", ""):
            with self.subTest(query=query):
                self.assertEqual(
                    [r["name"] for r in self.catalog.search(query=query)],
                    [r["name"] for r in reversed_catalog.search(query=query)],
                )

    def test_count_matches_equals_len_search_at_large_limit(self):
        """search() and count_matches() must not drift: they share _matches."""
        for query in ("host", "hosts", "detections", "vulnerabilities", "", "no_such_thing"):
            with self.subTest(query=query):
                self.assertEqual(
                    self.catalog.count_matches(query=query),
                    len(self.catalog.search(query=query, limit=10_000)),
                )

    def test_count_matches_equals_len_search_with_module_filter(self):
        for module in ("hosts", "detections", "hostgroups"):
            with self.subTest(module=module):
                self.assertEqual(
                    self.catalog.count_matches(module=module),
                    len(self.catalog.search(module=module, limit=10_000)),
                )

    def test_ranking_does_not_change_the_matched_set(self):
        """Scoring reorders; it must not add or drop a match."""
        for query in ("host", "hosts", "host details", "detections"):
            with self.subTest(query=query):
                tokens = query.lower().split()
                expected = {
                    name
                    for name, entry in self.catalog.entries.items()
                    if all(t in entry.search_corpus for t in tokens)
                }
                self.assertTrue(expected, "query must match under the strict filter")
                self.assertFalse(self.catalog.relaxed(query=query))
                self.assertEqual(set(self._names(query, limit=10_000)), expected)

    def test_fallback_only_engages_when_strict_matching_is_empty(self):
        """Precision is preserved: a query the strict filter can serve is served by it."""
        for query in ("host details", "search detections", "quarantined files"):
            with self.subTest(query=query):
                self.assertFalse(self.catalog.relaxed(query=query))

    def test_fallback_rescues_a_natural_language_phrase(self):
        """The reported zero-hit cases must return a usable, ranked result set."""
        for query, intended in (
            ("hosts detections", "falcon_search_detections"),
            ("top hosts detections", "falcon_aggregate_detections"),
            ("real-time response command", "falcon_execute_rtr_read_only_command"),
        ):
            with self.subTest(query=query):
                self.assertTrue(self.catalog.relaxed(query=query))
                names = self._names(query)
                self.assertIn(
                    intended, names, f"{intended} missing from the default result window"
                )

    def test_fallback_results_stay_ranked_and_deterministic(self):
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        available = registry.get_available_modules()
        reversed_catalog = DynamicToolCatalog(
            {name: available[name](mock_client) for name in reversed(list(available))}
        )
        for query in ("hosts detections", "real-time response command"):
            with self.subTest(query=query):
                self.assertEqual(
                    self._names(query, limit=10_000),
                    [r["name"] for r in reversed_catalog.search(query=query, limit=10_000)],
                )

    def test_read_only_tool_outranks_destructive_sibling_on_nl_query(self):
        """A natural-language read query must not surface the destructive sibling first.

        In the fallback tier the query carries many words the catalog does not use;
        crediting every miss made the read-only and destructive tools tie, and the
        alphabetical tiebreak then put the destructive one first. Coverage — how many
        query words the tool actually matches — is the signal that separates them.
        """
        for query, read_only, destructive in (
            ("find all the iocs that were added this week",
             "falcon_search_iocs", "falcon_remove_iocs"),
            ("find all the exclusions that were created this week",
             "falcon_search_exclusions", "falcon_delete_exclusions"),
            ("find all the policies that were created this week",
             "falcon_search_policies", "falcon_delete_policies"),
        ):
            with self.subTest(query=query):
                self.assertTrue(self.catalog.relaxed(query=query))
                names = self._names(query, limit=10_000)
                self.assertLess(
                    names.index(read_only),
                    names.index(destructive),
                    f"{destructive} ranked above the read-only {read_only}",
                )

    def test_higher_coverage_outranks_lower_coverage_despite_alphabetical(self):
        """Coverage is the primary key: a tool matching more query words wins.

        falcon_remove_iocs sorts before falcon_search_iocs alphabetically, so if the
        tiebreak still decided this the destructive one would win. It must not: the
        read-only tool matches more of the query's words.
        """
        query = "all the iocs added recently"
        names = self._names(query, limit=10_000)
        tokens = query.lower().split()

        def matched(name: str) -> int:
            corpus = self.catalog.entries[name].search_corpus
            return sum(1 for t in tokens if t in corpus)

        self.assertGreater(
            matched("falcon_search_iocs"), matched("falcon_remove_iocs")
        )
        self.assertLess(
            names.index("falcon_search_iocs"), names.index("falcon_remove_iocs")
        )

    def test_free_text_query_is_normalized_like_the_corpus(self):
        """Punctuation and separators in query must tokenize the same as the corpus."""
        baseline_single = self._names("hosts")[0]
        for query in ("hosts?", "hosts!", "searchhosts"):
            with self.subTest(query=query):
                self.assertEqual(self._names(query)[0], baseline_single)

        baseline_two = self._names("search hosts")[0]
        self.assertEqual(self._names("search-hosts")[0], baseline_two)

    def test_short_query_is_not_absorbed_into_a_collapsed_name(self):
        """The glued-name rescue is exact-membership, not substring containment.

        'mass' is a substring of the collapsed 'searchcspmassets' but shares no real
        relevance and does not appear in that tool's description. Substring containment
        would rescue it into the strict tier — a confident, wrong, non-relaxed match.
        Only a query equal to the whole collapsed name (e.g. 'searchhosts') is rescued.
        """
        # A short query with no genuine corpus hit must not surface a tool solely
        # because it is embedded in that tool's collapsed name.
        cspm = self.catalog.entries.get("falcon_search_cspm_assets")
        if cspm is not None and "mass" not in cspm.search_corpus:
            names = self._names("mass", limit=10_000)
            self.assertNotIn("falcon_search_cspm_assets", names)


class TestModuleVocabulary(unittest.TestCase):
    """The module parameter's accepted spellings, and where they are published."""

    def setUp(self):
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        self.catalog = DynamicToolCatalog(
            {
                name: cls(mock_client)
                for name, cls in registry.get_available_modules().items()
            }
        )

    def test_module_match_ignores_case_and_separators(self):
        expected = self.catalog.count_matches(module="hostgroups")
        self.assertGreater(expected, 0)
        for spelling in ("hostgroups", "host_groups", "host-groups", "Host_Groups", "HOSTGROUPS"):
            with self.subTest(spelling=spelling):
                self.assertEqual(self.catalog.count_matches(module=spelling), expected)

    def test_unknown_module_still_returns_nothing(self):
        self.assertEqual(self.catalog.count_matches(module="not_a_module"), 0)

    def test_module_normalization_does_not_merge_distinct_modules(self):
        """'hosts' and 'hostgroups' normalize distinctly, so neither absorbs the other."""
        hosts = {r["name"] for r in self.catalog.search(module="hosts", limit=10_000)}
        groups = {r["name"] for r in self.catalog.search(module="hostgroups", limit=10_000)}
        self.assertTrue(hosts)
        self.assertTrue(groups)
        self.assertEqual(hosts & groups, set())

    def test_empty_query_browse_order_is_stable(self):
        names = [r["name"] for r in self.catalog.search(query="", limit=10_000)]
        self.assertEqual(names, sorted(names))


class TestEmptySurfaceCopy(unittest.TestCase):
    """Agent-facing copy must not misstate an empty tool surface.

    `--tools <mutator> --read-only` withholds everything, leaving a catalog with no
    entries. Telling a model that other tools remain available sends it hunting
    through a server that serves nothing.
    """

    def setUp(self):
        self.mock_client = MagicMock()
        modules: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client),
        }
        # Deny every tool the module has, so the catalog ends up empty.
        probe: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client)
        }
        all_names = set(DynamicToolCatalog(probe).entries)
        self.dynamic = DynamicMode(
            modules, MagicMock(), ToolPolicy(excluded=all_names)
        )
        self.assertEqual(self.dynamic.catalog.entries, {}, "catalog must be empty")

    def test_withheld_error_does_not_promise_other_tools(self):
        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_search_detections", parameters={}
            )
        )
        self.assertIn("withholds it", result["error"])
        self.assertNotIn(
            "other tools remain available",
            result["error"],
            "claimed other tools are available on a server that serves none",
        )

    def test_empty_query_hint_does_not_quote_an_empty_query(self):
        """A module-only browse that matches nothing must not quote an empty query.

        Exercised on a NON-empty surface: an empty catalog is described by its own
        branch, so it would never reach the query wording being asserted here.
        """
        served: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client)
        }
        dynamic = DynamicMode(served, MagicMock())
        self.assertTrue(dynamic.catalog.entries, "surface must be non-empty")

        result = run_async(
            dynamic._search_tools(query="", module="nosuchmodule", limit=20)
        )
        self.assertEqual(result["results"], [])
        self.assertNotIn(
            "matching ''",
            result["hint"],
            "quoted an empty query back at the model",
        )

    def test_module_scoped_miss_blames_the_module_not_the_server(self):
        """A module that matches nothing must not read as an empty server.

        The subject line was built from `query` alone, so `module='incidents'` on a
        server that does serve tools produced "No tool is available on this server" —
        which sends the agent to tell the user the whole server is empty when only
        that one module is absent.
        """
        served: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client)
        }
        dynamic = DynamicMode(served, MagicMock())
        self.assertTrue(dynamic.catalog.entries, "surface must be non-empty")

        result = run_async(dynamic._search_tools(module="incidents", limit=20))

        self.assertEqual(result["results"], [])
        self.assertIn("incidents", result["hint"])
        self.assertNotIn(
            "No tool is available on this server",
            result["hint"],
            "reported an empty server when only the named module was absent",
        )

    def test_module_scoped_miss_with_a_query_names_both(self):
        """Both narrowing terms are why the result is empty, so both must be named."""
        served: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client)
        }
        dynamic = DynamicMode(served, MagicMock())

        result = run_async(
            dynamic._search_tools(query="quarantine", module="incidents", limit=20)
        )

        self.assertEqual(result["results"], [])
        self.assertIn("quarantine", result["hint"])
        self.assertIn("incidents", result["hint"])


class TestExecuteFalconTool(unittest.TestCase):
    """Test cases for DynamicMode execute dispatch."""

    def setUp(self):
        self.mock_client = MagicMock()
        modules: dict[str, BaseModule] = {
            "detections": DetectionsModule(self.mock_client),
        }
        self.mock_server = MagicMock()
        self.dynamic = DynamicMode(modules, self.mock_server)

    def test_execute_dispatches_to_tool_run(self):
        entry = self.dynamic.catalog.get("falcon_get_detection_details")
        self.assertIsNotNone(entry)

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "det1", "severity": 5}]},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": ["det1"]},
            )
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "det1")

    def test_execute_unknown_tool_returns_error(self):
        result = run_async(
            self.dynamic._execute_tool(
                tool_name="nonexistent_tool",
                parameters={},
            )
        )
        self.assertIn("error", result)
        self.assertIn("Unknown tool", result["error"])
        self.assertIn("falcon_search_tools", result["error"])

    def test_execute_validation_error_returns_structured_error(self):
        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": "not_a_list"},
            )
        )
        self.assertIn("error", result)
        self.assertIn("tool", result)
        self.assertEqual(result["tool"], "falcon_get_detection_details")
        self.assertIn("expected_parameters", result)
        self.assertIn("ids", result["expected_parameters"])

    def test_execute_returns_full_result(self):
        """Results are returned in full — no truncation regardless of list size."""
        large_result = [{"id": f"det{i}"} for i in range(20)]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": large_result},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": [f"det{i}" for i in range(20)]},
            )
        )
        # All 20 records come back untouched — no total_count wrapper, no truncation.
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 20)

    def test_execute_empty_list_returns_normalized_dict(self):
        """Empty list results are returned as {results:[], pagination:{total:0,next:None}, hint:...}."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": ["nonexistent"]},
            )
        )
        self.assertIsInstance(result, dict)
        assert isinstance(result, dict)  # narrow type for Pyright
        self.assertEqual(result["results"], [])
        self.assertEqual(result["pagination"]["total"], 0)
        self.assertIsNone(result["pagination"]["next"])
        self.assertIn("hint", result)
        self.assertIn("No records returned", result["hint"])

    def test_normalize_empty_passthrough_for_dict(self):
        """Non-list results (e.g. dicts from non-paginated tools) pass through unchanged."""
        payload = {"id": "abc", "status": "open"}
        result = self.dynamic._normalize_empty(payload)
        self.assertEqual(result, payload)

    def test_search_tools_no_results_returns_hint_with_available_modules(self):
        result = run_async(
            self.dynamic._search_tools(
                query="hosts nonexistent", module=None, limit=20
            )
        )
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertFalse(result["truncated"])
        self.assertIn("hosts nonexistent", result["hint"])
        self.assertIn("falcon_list_enabled_tools", result["hint"])

    def test_search_tools_with_results_returns_envelope(self):
        result = run_async(
            self.dynamic._search_tools(
                query="search_detections", module=None, limit=50
            )
        )
        self.assertGreater(len(result["results"]), 0)
        self.assertEqual(result["total"], len(result["results"]))
        self.assertFalse(result["truncated"])


class TestDynamicServerIntegration(unittest.TestCase):
    """Test cases for dynamic mode server integration."""

    def setUp(self):
        registry.discover_modules()

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_mode_registers_three_tools(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=True,
        )

        tool_names = [
            call.kwargs["name"] for call in mock_server_instance.add_tool.call_args_list
        ]
        self.assertEqual(len(tool_names), 3)
        self.assertIn("falcon_list_enabled_tools", tool_names)
        self.assertIn("falcon_search_tools", tool_names)
        self.assertIn("falcon_execute_tool", tool_names)
        # These must NOT be registered in dynamic mode
        self.assertNotIn("falcon_check_connectivity", tool_names)
        self.assertNotIn("falcon_list_enabled_modules", tool_names)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_normal_mode_does_not_have_dynamic_tools(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=False,
        )

        tool_names = [
            call.kwargs["name"] for call in mock_server_instance.add_tool.call_args_list
        ]
        # Meta-tools must be absent in normal mode
        self.assertNotIn("falcon_search_tools", tool_names)
        self.assertNotIn("falcon_execute_tool", tool_names)
        # All three core tools must be present in normal mode
        self.assertIn("falcon_check_connectivity", tool_names)
        self.assertIn("falcon_list_enabled_modules", tool_names)
        self.assertIn("falcon_list_enabled_tools", tool_names)
        # Module tools must be registered directly
        self.assertIn("falcon_search_detections", tool_names)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_mode_still_registers_resources(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=True,
        )

        mock_server_instance.add_resource.assert_called()

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_instructions_describe_the_three_step_loop(
        self, mock_fastmcp, mock_client
    ):
        """The two-step flow must not depend on the model reading one tool's docstring.

        Discovery deliberately withholds parameters, which is not the shape a client
        expects, so the loop is stated once at the protocol level.
        """
        from falcon_mcp.server import FalconMCPServer

        mock_client.return_value.authenticate.return_value = True
        mock_fastmcp.return_value = MagicMock()

        FalconMCPServer(enabled_modules={"detections"}, dynamic=True)
        instructions = mock_fastmcp.call_args.kwargs["instructions"]

        self.assertIn("tool_names", instructions)
        self.assertIn("falcon_search_tools", instructions)
        self.assertIn("falcon_execute_tool", instructions)
        self.assertIn("falcon_list_enabled_tools", instructions)
        self.assertIn("no parameters", instructions)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_normal_mode_instructions_omit_the_dynamic_loop(
        self, mock_fastmcp, mock_client
    ):
        """Normal mode registers every tool, so describing a search loop would misdirect."""
        from falcon_mcp.server import FalconMCPServer

        mock_client.return_value.authenticate.return_value = True
        mock_fastmcp.return_value = MagicMock()

        FalconMCPServer(enabled_modules={"detections"}, dynamic=False)
        instructions = mock_fastmcp.call_args.kwargs["instructions"]

        self.assertIn("CrowdStrike Falcon", instructions)
        self.assertNotIn("tool_names", instructions)
        self.assertNotIn("falcon_search_tools", instructions)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_normal_mode_instructions_carry_the_cross_cutting_facts(
        self, mock_fastmcp, mock_client
    ):
        """Three facts no normal-mode tool description states on its own.

        Operator syntax reaches dynamic mode through _format_entry and reaches normal
        mode nowhere; the fql-guide URI scheme and the mutation annotations are each
        re-taught per tool or not at all. Stating them once here costs nothing against
        the tools/list payload budget.
        """
        from falcon_mcp.server import FalconMCPServer

        mock_client.return_value.authenticate.return_value = True
        mock_fastmcp.return_value = MagicMock()

        FalconMCPServer(enabled_modules={"detections"}, dynamic=False)
        instructions = mock_fastmcp.call_args.kwargs["instructions"]

        self.assertIn("+ for AND", instructions)
        self.assertIn(", for OR", instructions)
        self.assertIn("single-quoted", instructions)
        self.assertIn("falcon://", instructions)
        # The old synthetic template resolved for no registered resource, so an agent
        # building it 404s on every filter. Point at the tool's own filter param
        # instead, which names the real URI.
        self.assertNotIn("falcon://<module>/<tool>/fql-guide", instructions)
        self.assertNotIn("Every filter-taking tool", instructions)
        self.assertIn("empty result", instructions)
        self.assertIn("readOnlyHint", instructions)
        self.assertIn("destructiveHint", instructions)
        self.assertIn("Confirm", instructions)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_mode_instructions_keep_the_shared_base(
        self, mock_fastmcp, mock_client
    ):
        """Appending the dynamic block must not replace the cross-cutting facts.

        A dynamic-mode agent composes filters through falcon_execute_tool, so it needs
        the FQL and mutation guidance every bit as much as a normal-mode one.
        """
        from falcon_mcp.server import FalconMCPServer

        mock_client.return_value.authenticate.return_value = True
        mock_fastmcp.return_value = MagicMock()

        FalconMCPServer(enabled_modules={"detections"}, dynamic=True)
        instructions = mock_fastmcp.call_args.kwargs["instructions"]

        self.assertIn("+ for AND", instructions)
        self.assertIn("falcon://", instructions)
        self.assertNotIn("falcon://<module>/<tool>/fql-guide", instructions)
        self.assertIn("destructiveHint", instructions)
        # ... alongside the loop, not instead of it.
        self.assertIn("tool_names", instructions)
        self.assertIn("falcon_execute_tool", instructions)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_instructions_reuse_the_dynamic_mode_filter_hint_suffix(
        self, mock_fastmcp, mock_client
    ):
        """The operator sentence has two call sites and must not be paraphrased.

        _format_entry appends FQL_FILTER_HINT_SUFFIX to every filter description in
        dynamic mode. If the instructions restated the same rule in their own words,
        the two could drift and an agent would see two versions of the syntax.
        """
        from falcon_mcp.common.fql import FQL_FILTER_HINT_SUFFIX
        from falcon_mcp.server import FalconMCPServer

        mock_client.return_value.authenticate.return_value = True
        mock_fastmcp.return_value = MagicMock()

        FalconMCPServer(enabled_modules={"detections"}, dynamic=False)
        instructions = mock_fastmcp.call_args.kwargs["instructions"]

        self.assertIn(FQL_FILTER_HINT_SUFFIX, instructions)

    @patch("sys.argv", ["falcon-mcp", "--dynamic"])
    def test_parse_args_dynamic_flag(self):
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertTrue(args.dynamic)

    @patch("sys.argv", ["falcon-mcp"])
    @patch.dict("os.environ", {"FALCON_MCP_DYNAMIC": "true"})
    def test_parse_args_dynamic_env_var(self):
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertTrue(args.dynamic)

    @patch("sys.argv", ["falcon-mcp"])
    @patch.dict("os.environ", {}, clear=False)
    def test_parse_args_dynamic_defaults_false(self):
        import os

        os.environ.pop("FALCON_MCP_DYNAMIC", None)
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertFalse(args.dynamic)


if __name__ == "__main__":
    unittest.main()
