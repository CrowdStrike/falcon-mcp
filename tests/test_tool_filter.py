"""
Tests for tool-level filtering (read-only mode, allow-list, deny-list).
"""

import argparse
import asyncio
import os
import re
import sys
import unittest
from collections.abc import Coroutine
from typing import Any, TypeVar
from unittest.mock import MagicMock, patch

from mcp.types import ToolAnnotations

from falcon_mcp import registry
from falcon_mcp.server import FalconMCPServer, main, parse_args, parse_tools_list
from falcon_mcp.tool_filter import ToolPolicy, ToolRecord

_T = TypeVar("_T")

# hostgroups carries a mix of read-only and mutating tools, which makes it the
# cheapest module to assert precedence against.
_MODULE = "hostgroups"
_READ_ONLY_TOOL = "falcon_search_host_groups"
_MUTATING_TOOL = "falcon_delete_host_groups"

# A tool from a module that is NOT enabled in these tests, used to prove the
# allow-list is additive across the module gate.
_FOREIGN_TOOL = "falcon_search_applications"

# Always registered regardless of filtering, so tests subtract them out.
_META_TOOLS = {
    "falcon_list_enabled_modules",
    "falcon_list_enabled_tools",
    "falcon_check_connectivity",
}

_MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)

_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

# Trailing punctuation is excluded so "…fql-guide." yields the bare URI.
_URI_PATTERN = re.compile(r"falcon://[A-Za-z0-9\-_/]+")


def run_async(coro: Coroutine[Any, Any, _T]) -> _T:
    return asyncio.run(coro)


def _catalog(*specs: tuple[str, str, ToolAnnotations | None]) -> dict[str, ToolRecord]:
    """Build a catalog from (name, module, annotations) triples."""
    return {
        name: ToolRecord(module=module, annotations=annotations)
        for name, module, annotations in specs
    }


class TestToolPolicy(unittest.TestCase):
    """Unit tests for the ToolPolicy precedence rules in isolation."""

    def test_no_configuration_keeps_everything(self):
        p = ToolPolicy()
        self.assertFalse(p.active)
        resolved = p.resolve(_catalog(("falcon_a", "m", _MUTATING_ANNOTATIONS)))
        self.assertEqual(resolved.keep, {"falcon_a"})
        self.assertEqual(resolved.removed, frozenset())

    def test_deny_list_wins_over_allow_list(self):
        p = ToolPolicy(allowed={"falcon_a"}, excluded={"falcon_a"})
        resolved = p.resolve(_catalog(("falcon_a", "m", _READ_ONLY_ANNOTATIONS)))
        self.assertEqual(resolved.removed, {"falcon_a"})

    def test_read_only_wins_over_allow_list(self):
        p = ToolPolicy(read_only=True, allowed={_MUTATING_TOOL})
        resolved = p.resolve(_catalog((_MUTATING_TOOL, "m", _MUTATING_ANNOTATIONS)))
        self.assertEqual(resolved.removed, {_MUTATING_TOOL})

    def test_allow_list_is_additive_not_intersecting(self):
        """A named tool survives; unnamed tools in enabled modules also survive."""
        p = ToolPolicy(allowed={"falcon_a"}, enabled_modules={"m"})
        resolved = p.resolve(
            _catalog(
                ("falcon_a", "m", _READ_ONLY_ANNOTATIONS),
                ("falcon_b", "m", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(resolved.keep, {"falcon_a", "falcon_b"})

    def test_allow_list_crosses_the_module_gate(self):
        """A module loaded solely for the allow-list contributes only named tools."""
        p = ToolPolicy(allowed={"falcon_a"}, enabled_modules={"enabled"})
        resolved = p.resolve(
            _catalog(
                ("falcon_a", "gated", _READ_ONLY_ANNOTATIONS),
                ("falcon_b", "gated", _READ_ONLY_ANNOTATIONS),
                ("falcon_c", "enabled", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(resolved.keep, {"falcon_a", "falcon_c"})
        self.assertEqual(resolved.removed, {"falcon_b"})

    def test_no_enabled_modules_disables_the_module_gate(self):
        """enabled_modules=None means every module contributes its full surface."""
        p = ToolPolicy(read_only=True)
        resolved = p.resolve(_catalog(("falcon_a", "anything", _READ_ONLY_ANNOTATIONS)))
        self.assertEqual(resolved.keep, {"falcon_a"})

    def test_read_only_keeps_read_only_tools(self):
        p = ToolPolicy(read_only=True, enabled_modules={"m"})
        resolved = p.resolve(_catalog(("falcon_a", "m", _READ_ONLY_ANNOTATIONS)))
        self.assertEqual(resolved.keep, {"falcon_a"})

    def test_read_only_withholds_tools_with_no_annotations(self):
        """An unclassified tool is withheld, not assumed safe."""
        p = ToolPolicy(read_only=True, enabled_modules={"m"})
        resolved = p.resolve(_catalog(("falcon_a", "m", None)))
        self.assertEqual(resolved.removed, {"falcon_a"})

    def test_resolution_partitions_the_catalog(self):
        """Every catalog entry lands in exactly one of keep/removed."""
        p = ToolPolicy(read_only=True, enabled_modules={"m"})
        catalog = _catalog(
            ("falcon_keep", "m", _READ_ONLY_ANNOTATIONS),
            ("falcon_drop", "m", _MUTATING_ANNOTATIONS),
        )
        resolved = p.resolve(catalog)
        self.assertEqual(resolved.keep, {"falcon_keep"})
        self.assertEqual(resolved.removed, {"falcon_drop"})
        self.assertEqual(resolved.keep | resolved.removed, set(catalog))
        self.assertEqual(resolved.keep & resolved.removed, set())

    def test_never_requested_tool_is_removed_but_not_withheld_by_rule(self):
        """A sibling of an allow-listed tool was never a candidate, not withheld.

        Counting it as withheld reads as though a decision was made about it, when
        the operator simply never asked for it.
        """
        p = ToolPolicy(allowed={"falcon_a"}, enabled_modules={"enabled"})
        resolved = p.resolve(
            _catalog(
                ("falcon_a", "gated", _READ_ONLY_ANNOTATIONS),
                ("falcon_sibling", "gated", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(resolved.removed, {"falcon_sibling"})
        self.assertEqual(resolved.withheld_by_rule, frozenset())

    def test_deny_list_and_read_only_removals_are_withheld_by_rule(self):
        """Both explicit rules count as withheld; each is a decision made."""
        p = ToolPolicy(
            read_only=True, excluded={"falcon_denied"}, enabled_modules={"m"}
        )
        resolved = p.resolve(
            _catalog(
                ("falcon_denied", "m", _READ_ONLY_ANNOTATIONS),
                ("falcon_mutator", "m", _MUTATING_ANNOTATIONS),
                ("falcon_sibling", "off", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(resolved.withheld_by_rule, {"falcon_denied", "falcon_mutator"})
        self.assertEqual(resolved.removed, resolved.withheld_by_rule | {"falcon_sibling"})

    def test_reasons_name_the_rule_that_decided_each_tool(self):
        """falcon_denied is read-only, so only the deny-list can have withheld it.

        Attribution follows the documented precedence rather than reporting every
        active rule, which would misdirect an operator debugging their config. A tool
        the module gate dropped is not attributed at all.
        """
        p = ToolPolicy(
            read_only=True, excluded={"falcon_denied"}, enabled_modules={"m"}
        )
        resolved = p.resolve(
            _catalog(
                ("falcon_denied", "m", _READ_ONLY_ANNOTATIONS),
                ("falcon_mutator", "m", _MUTATING_ANNOTATIONS),
                ("falcon_sibling", "off", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(
            dict(resolved.reasons),
            {"falcon_denied": "deny-list", "falcon_mutator": "read-only"},
        )
        self.assertNotIn("falcon_sibling", resolved.reasons)

    def test_reasons_keys_match_withheld_by_rule(self):
        """The two must not drift — an unattributed withholding cites no cause."""
        p = ToolPolicy(
            read_only=True, excluded={"falcon_denied"}, enabled_modules={"m"}
        )
        resolved = p.resolve(
            _catalog(
                ("falcon_denied", "m", _READ_ONLY_ANNOTATIONS),
                ("falcon_mutator", "m", _MUTATING_ANNOTATIONS),
                ("falcon_kept", "m", _READ_ONLY_ANNOTATIONS),
                ("falcon_sibling", "off", _READ_ONLY_ANNOTATIONS),
            )
        )
        self.assertEqual(set(resolved.reasons), resolved.withheld_by_rule)

    def test_mutating_tool_is_not_withheld_by_rule_when_read_only_is_off(self):
        """A mutator dropped by the module gate must not be blamed on read-only."""
        p = ToolPolicy(allowed={"falcon_a"}, enabled_modules={"enabled"})
        resolved = p.resolve(
            _catalog(("falcon_mutator", "gated", _MUTATING_ANNOTATIONS))
        )
        self.assertEqual(resolved.removed, {"falcon_mutator"})
        self.assertEqual(resolved.withheld_by_rule, frozenset())

    def test_resolve_is_pure(self):
        """Resolving twice yields the same answer; no state accumulates."""
        p = ToolPolicy(read_only=True, enabled_modules={"m"})
        catalog = _catalog(
            ("falcon_keep", "m", _READ_ONLY_ANNOTATIONS),
            ("falcon_drop", "m", _MUTATING_ANNOTATIONS),
        )
        self.assertEqual(p.resolve(catalog), p.resolve(catalog))

    def test_never_requested_sibling_is_not_attributed_to_read_only(self):
        """A mutator the allow-list never named was not withheld by --read-only.

        --tools X --read-only loads X's whole module to reach X, so its siblings get
        registered as candidates. Attributing them to read-only inflates the startup
        count and makes falcon_execute_tool call a never-requested tool "withheld
        (read-only)" when the same tool without --read-only reports Unknown tool.
        """
        catalog = {
            "falcon_wanted": ToolRecord(_MODULE, _MUTATING_ANNOTATIONS),
            "falcon_sibling_mutator": ToolRecord(_MODULE, _MUTATING_ANNOTATIONS),
            "falcon_sibling_reader": ToolRecord(_MODULE, _READ_ONLY_ANNOTATIONS),
        }
        # --tools falcon_wanted --read-only: no module is enabled in its own right.
        resolution = ToolPolicy(
            read_only=True, allowed={"falcon_wanted"}, enabled_modules=set()
        ).resolve(catalog)

        self.assertEqual(
            dict(resolution.reasons),
            {"falcon_wanted": "read-only"},
            "only the requested tool was decided by read-only",
        )
        self.assertEqual(resolution.withheld_by_rule, frozenset({"falcon_wanted"}))
        # Both siblings are still gone, just not blamed on a rule.
        self.assertEqual(
            resolution.removed,
            frozenset(catalog),
            "every unrequested tool is still removed",
        )

    def test_describe_reports_active_rules(self):
        self.assertEqual(ToolPolicy().describe(), "none")
        self.assertIn("read-only", ToolPolicy(read_only=True).describe())
        self.assertIn("deny-list", ToolPolicy(excluded={"falcon_a"}).describe())


class TestParseToolsList(unittest.TestCase):
    """Tests for the CLI list parser."""

    def test_empty_string_yields_empty_list(self):
        self.assertEqual(parse_tools_list(""), [])

    def test_strips_whitespace_and_blanks(self):
        self.assertEqual(
            parse_tools_list(" falcon_a , falcon_b ,, "), ["falcon_a", "falcon_b"]
        )


class TestCLIDefaultsReachTheServer(unittest.TestCase):
    """The CLI must hand the server the same thing the tests construct directly.

    Unit tests call FalconMCPServer(allowed_tools=...) with enabled_modules unset,
    but argparse supplies a default for --modules. If that default is a fully
    expanded module list, `--tools X` alone silently serves every tool: the server
    sees a truthy enabled_modules and never takes the "--tools alone" branch. Caught
    by an agent-level run, invisible to every direct-construction test.
    """

    def setUp(self):
        self._saved = {
            k: os.environ.pop(k, None)
            for k in ("FALCON_MCP_MODULES", "FALCON_MCP_TOOLS", "FALCON_MCP_EXCLUDE_TOOLS")
        }

    def tearDown(self):
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def _args(self, argv: list[str]) -> argparse.Namespace:
        with patch.object(sys, "argv", ["falcon-mcp", *argv]):
            return parse_args()

    def test_tools_alone_does_not_preselect_every_module(self):
        args = self._args(["--tools", "falcon_search_detections"])
        self.assertEqual(args.tools, ["falcon_search_detections"])
        self.assertFalse(
            args.modules,
            "--modules defaulted to a populated list, so --tools alone cannot "
            f"restrict the surface: {args.modules}",
        )

    def test_no_flags_still_means_all_modules(self):
        """The default must stay 'everything' when no restriction is requested."""
        args = self._args([])
        mock = MagicMock()
        mock.return_value.authenticate.return_value = True
        with patch("falcon_mcp.server.FalconClient", mock):
            server = FalconMCPServer(enabled_modules=set(args.modules))
        self.assertEqual(server.enabled_modules, set(registry.get_module_names()))

    def test_main_forwards_every_filter_flag_to_the_server(self):
        """main() must hand each parsed filter flag to the constructor.

        The tests above stop at parse_args() and re-thread the namespace by hand, so
        none of them cover the args-to-kwargs mapping in main(). Dropping
        read_only=args.read_only there serves every mutator on a server the operator
        asked to be read-only, with the rest of the suite still green.
        """
        argv = [
            "--read-only",
            "--tools",
            _FOREIGN_TOOL,
            "--exclude-tools",
            _MUTATING_TOOL,
        ]
        with patch.object(sys, "argv", ["falcon-mcp", *argv]):
            with patch("falcon_mcp.server.FalconMCPServer") as mock_server:
                main()

        kwargs = mock_server.call_args.kwargs
        self.assertTrue(kwargs["read_only"], "--read-only never reached the server")
        self.assertEqual(kwargs["allowed_tools"], {_FOREIGN_TOOL})
        self.assertEqual(kwargs["excluded_tools"], {_MUTATING_TOOL})

    def test_explicit_modules_are_honored(self):
        args = self._args(["--modules", "detections"])
        self.assertEqual(args.modules, ["detections"])

    def test_tools_alone_through_the_cli_path_registers_only_that_tool(self):
        """End-to-end through argparse: the surface must be just the named tool."""
        args = self._args(["--tools", _FOREIGN_TOOL])
        mock = MagicMock()
        mock.return_value.authenticate.return_value = True
        with patch("falcon_mcp.server.FalconClient", mock):
            server = FalconMCPServer(
                enabled_modules=set(args.modules), allowed_tools=set(args.tools)
            )
        self.assertEqual(
            set(server.server._tool_manager._tools) - _META_TOOLS, {_FOREIGN_TOOL}
        )


@patch("falcon_mcp.server.FalconClient")
class TestServerToolFiltering(unittest.TestCase):
    """End-to-end tests asserting the registered tool surface."""

    def setUp(self):
        registry.discover_modules()

    def _server(self, mock_client, **kwargs) -> FalconMCPServer:
        mock_client.return_value.authenticate.return_value = True
        return FalconMCPServer(enabled_modules={_MODULE}, **kwargs)

    def _module_tools(self, server: FalconMCPServer) -> set[str]:
        return set(server.server._tool_manager._tools) - _META_TOOLS

    def test_unfiltered_registers_all_module_tools(self, mock_client):
        tools = self._module_tools(self._server(mock_client))
        self.assertIn(_READ_ONLY_TOOL, tools)
        self.assertIn(_MUTATING_TOOL, tools)

    def test_read_only_withholds_mutating_tools(self, mock_client):
        tools = self._module_tools(self._server(mock_client, read_only=True))
        self.assertIn(_READ_ONLY_TOOL, tools)
        self.assertNotIn(_MUTATING_TOOL, tools)

    def test_deny_list_removes_named_tool(self, mock_client):
        tools = self._module_tools(
            self._server(mock_client, excluded_tools={_READ_ONLY_TOOL})
        )
        self.assertNotIn(_READ_ONLY_TOOL, tools)
        self.assertIn(_MUTATING_TOOL, tools)

    def test_deny_list_overrides_allow_list(self, mock_client):
        """Precedence rule 1: deny wins even when the allow-list names the tool."""
        tools = self._module_tools(
            self._server(
                mock_client,
                allowed_tools={_READ_ONLY_TOOL},
                excluded_tools={_READ_ONLY_TOOL},
            )
        )
        self.assertNotIn(_READ_ONLY_TOOL, tools)

    def test_read_only_overrides_allow_list(self, mock_client):
        """Precedence rule 2: read-only wins even when the allow-list names the tool."""
        tools = self._module_tools(
            self._server(mock_client, read_only=True, allowed_tools={_MUTATING_TOOL})
        )
        self.assertNotIn(_MUTATING_TOOL, tools)

    def test_allow_list_does_not_restrict_an_enabled_module(self, mock_client):
        """Precedence rule 3: the allow-list adds, it does not subtract.

        An explicitly enabled module keeps its full surface; the allow-list only
        widens it. Use --exclude-tools or --read-only to subtract.
        """
        tools = self._module_tools(
            self._server(mock_client, allowed_tools={_READ_ONLY_TOOL})
        )
        self.assertIn(_READ_ONLY_TOOL, tools)
        self.assertIn(_MUTATING_TOOL, tools)

    def test_allow_list_pulls_in_tool_from_disabled_module(self, mock_client):
        """Precedence rule 4: the allow-list is additive across the module gate.

        Reproduces `--modules detections --tools falcon_search_applications`, which
        must yield every detections tool plus the named discover tool.
        """
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        tools = self._module_tools(server)
        self.assertIn(_FOREIGN_TOOL, tools)
        self.assertIn("falcon_search_detections", tools)
        self.assertIn("falcon_update_detections", tools)

    def test_pulled_in_module_contributes_only_named_tools(self, mock_client):
        """A module loaded solely for the allow-list does not bring its whole surface."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        tools = self._module_tools(server)
        discover_tools = {
            name for name, mod in registry.get_tool_module_map().items() if mod == "discover"
        }
        self.assertEqual(tools & discover_tools, {_FOREIGN_TOOL})

    def test_pulled_in_module_still_registers_its_resources(self, mock_client):
        """A module pulled in for one tool keeps its guides.

        Most tool descriptions name a falcon:// URI, so withholding a guide while
        keeping its tool would point the model at a resource that does not exist.
        See test_every_referenced_guide_uri_resolves for the general guard.
        """
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        uris = {str(u) for u in server.server._resource_manager._resources}
        self.assertIn("falcon://discover/applications/fql-guide", uris)
        self.assertIn("falcon://detections/search/fql-guide", uris)

    def test_enabled_module_still_registers_its_resources(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(enabled_modules={"discover"})
        uris = {str(u) for u in server.server._resource_manager._resources}
        self.assertIn("falcon://discover/applications/fql-guide", uris)
        self.assertIn("falcon://discover/hosts/fql-guide", uris)

    def test_startup_counts_match_what_was_registered(self, mock_client):
        """The logged module/tool/resource counts must reflect reality, not arithmetic."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        # One module enabled, even though two are loaded.
        self.assertEqual(len(server.modules), 2)
        self.assertEqual(server.list_enabled_modules(), {"modules": ["detections"]})
        self.assertEqual(
            server._register_tools(), len(server.server._tool_manager._tools)
        )
        self.assertEqual(
            server._register_resources(),
            len(server.server._resource_manager._resources),
        )

    def test_startup_log_counts_only_enabled_modules(self, mock_client):
        """The startup summary must not count a module pulled in for one tool."""
        mock_client.return_value.authenticate.return_value = True
        with self.assertLogs("falcon_mcp.server", level="INFO") as captured:
            FalconMCPServer(enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL})
        summary = next(m for m in captured.output if "Falcon MCP v" in m)
        self.assertIn("1 module,", summary)

    def _policy_log(self, **kwargs) -> str:
        with self.assertLogs("falcon_mcp.server", level="INFO") as captured:
            FalconMCPServer(**kwargs)
        return next(m for m in captured.output if "Tool policy active" in m)

    def test_allow_list_alone_reports_nothing_withheld(self, mock_client):
        """--modules X --tools Y removed nothing the operator asked to remove.

        The siblings of Y that came along with its module were never candidates, so
        reporting them as withheld would invent a decision.
        """
        mock_client.return_value.authenticate.return_value = True
        line = self._policy_log(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        self.assertIn("0 tools withheld", line)

    def test_deny_list_reports_only_its_own_removal(self, mock_client):
        """With an allow-list and a deny-list, only the denied tool is withheld."""
        mock_client.return_value.authenticate.return_value = True
        line = self._policy_log(
            enabled_modules={"detections"},
            allowed_tools={_FOREIGN_TOOL, "falcon_search_hosts"},
            excluded_tools={"falcon_search_detections"},
        )
        self.assertIn("1 tool withheld", line)
        self.assertIn("deny-list", line)

    def test_read_only_reports_the_mutators_it_withheld(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        line = self._policy_log(enabled_modules={_MODULE}, read_only=True)
        self.assertRegex(line, r"read-only.*\d+ tools withheld")
        self.assertNotIn("0 tools withheld", line)

    def test_withheld_names_appear_at_debug_level(self, mock_client):
        """The INFO line gives counts; --debug must supply the names behind them."""
        mock_client.return_value.authenticate.return_value = True
        with self.assertLogs("falcon_mcp.server", level="DEBUG") as captured:
            FalconMCPServer(enabled_modules={_MODULE}, excluded_tools={_MUTATING_TOOL})
        self.assertTrue(
            any(f"Withheld tool: {_MUTATING_TOOL}" in m for m in captured.output),
            captured.output,
        )

    def test_pulled_in_module_is_not_reported_as_enabled(self, mock_client):
        """A gated module is loaded but not advertised by falcon_list_enabled_modules.

        Matches the reference implementation, where an additively-named tool resolves
        while isToolsetEnabled() on its owning toolset stays false.
        """
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        self.assertEqual(server.list_enabled_modules(), {"modules": ["detections"]})
        self.assertIn("discover", server.modules)
        self.assertIn(_FOREIGN_TOOL, server.server._tool_manager._tools)

    def test_enabled_modules_reported_normally_without_a_filter(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(enabled_modules={"detections", _MODULE})
        self.assertEqual(
            server.list_enabled_modules(), {"modules": sorted(["detections", _MODULE])}
        )

    def test_tools_alone_reports_no_enabled_modules(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(allowed_tools={_FOREIGN_TOOL})
        self.assertEqual(server.list_enabled_modules(), {"modules": []})

    def test_tools_alone_supplies_the_entire_surface(self, mock_client):
        """--tools with no --modules registers only the named tools."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(allowed_tools={_FOREIGN_TOOL})
        self.assertEqual(self._module_tools(server), {_FOREIGN_TOOL})

    def test_read_only_overrides_additive_allow_list(self, mock_client):
        """A mutating tool pulled in from a disabled module is still withheld."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, read_only=True, allowed_tools={_MUTATING_TOOL}
        )
        self.assertNotIn(_MUTATING_TOOL, self._module_tools(server))

    def test_deny_list_overrides_additive_allow_list(self, mock_client):
        """Naming a tool in both lists withholds it even across the module gate."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"},
            allowed_tools={_FOREIGN_TOOL},
            excluded_tools={_FOREIGN_TOOL},
        )
        self.assertNotIn(_FOREIGN_TOOL, self._module_tools(server))

    def test_all_three_controls_compose(self, mock_client):
        """read-only and deny both override the allow-list in one configuration."""
        tools = self._module_tools(
            self._server(
                mock_client,
                read_only=True,
                allowed_tools={
                    _READ_ONLY_TOOL,
                    _MUTATING_TOOL,
                    "falcon_search_host_group_members",
                },
                excluded_tools={"falcon_search_host_group_members"},
            )
        )
        # _MUTATING_TOOL dropped by read-only, the members search dropped by the
        # deny-list, leaving the allow-listed read-only survivor.
        self.assertEqual(tools, {_READ_ONLY_TOOL})

    def test_name_from_disabled_module_survives_read_only_if_read_only(self, mock_client):
        """Additive pull-in plus read-only: a read-only foreign tool is kept."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={_MODULE}, read_only=True, allowed_tools={_FOREIGN_TOOL}
        )
        tools = self._module_tools(server)
        self.assertIn(_FOREIGN_TOOL, tools)
        self.assertNotIn(_MUTATING_TOOL, tools)

    def test_modules_still_gate_the_candidate_set(self, mock_client):
        """An unnamed tool from a module that is off is not registered."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(enabled_modules={_MODULE})
        self.assertNotIn(_FOREIGN_TOOL, self._module_tools(server))

    def test_meta_tools_survive_read_only_and_allow_list(self, mock_client):
        """Server meta-tools stay registered so the server remains usable."""
        server = self._server(mock_client, read_only=True, allowed_tools={_READ_ONLY_TOOL})
        self.assertTrue(_META_TOOLS.issubset(set(server.server._tool_manager._tools)))

    def test_tool_count_reflects_actual_registrations(self, mock_client):
        """The startup count must not be derived arithmetically once filtering exists."""
        server = self._server(mock_client, excluded_tools={_MUTATING_TOOL})
        registered = server.server._tool_manager._tools
        self.assertEqual(server._register_tools(), len(registered))
        self.assertNotIn(_MUTATING_TOOL, registered)

    def test_repeated_registration_keeps_filter_counts_accurate(self, mock_client):
        """Re-running registration must not inflate the logged filter summary."""
        server = self._server(mock_client, excluded_tools={_MUTATING_TOOL})
        before = server._resolution
        server._register_tools()
        self.assertEqual(before, server._resolution)
        self.assertNotIn(_MUTATING_TOOL, server.server._tool_manager._tools)

    def test_module_tools_mirrors_the_served_surface(self, mock_client):
        """module.tools must not advertise a tool the server no longer serves."""
        server = self._server(mock_client, excluded_tools={_MUTATING_TOOL})
        tracked = set(server.modules[_MODULE].tools)
        self.assertNotIn(_MUTATING_TOOL, tracked)
        self.assertEqual(tracked, tracked & set(server.server._tool_manager._tools))

    def _list_enabled_tools(self, server: FalconMCPServer) -> list[str]:
        tool = server.server._tool_manager._tools["falcon_list_enabled_tools"]
        return run_async(tool.run({}))["tools"]

    def test_list_enabled_tools_is_exactly_the_served_module_tools(self, mock_client):
        """Regression guard for the falcon_list_modules bug: it reported every
        installed module regardless of filtering."""
        server = self._server(mock_client)
        self.assertEqual(
            set(self._list_enabled_tools(server)), self._module_tools(server)
        )

    def test_list_enabled_tools_omits_read_only_withheld(self, mock_client):
        names = self._list_enabled_tools(self._server(mock_client, read_only=True))
        self.assertIn(_READ_ONLY_TOOL, names)
        self.assertNotIn(_MUTATING_TOOL, names)

    def test_list_enabled_tools_omits_denied_tool(self, mock_client):
        names = self._list_enabled_tools(
            self._server(mock_client, excluded_tools={_READ_ONLY_TOOL})
        )
        self.assertNotIn(_READ_ONLY_TOOL, names)

    def test_list_enabled_tools_omits_absent_sibling_of_allowed_tool(self, mock_client):
        """Both live in `discover`, so allow-listing one must not imply the other."""
        names = self._list_enabled_tools(
            self._server(mock_client, allowed_tools={_FOREIGN_TOOL})
        )
        self.assertIn(_FOREIGN_TOOL, names)
        self.assertNotIn("falcon_search_unmanaged_assets", names)

    def test_list_enabled_tools_reports_a_matching_total(self, mock_client):
        server = self._server(mock_client, read_only=True)
        tool = server.server._tool_manager._tools["falcon_list_enabled_tools"]
        result = run_async(tool.run({}))
        self.assertEqual(result["total"], len(result["tools"]))
        self.assertEqual(result["tools"], sorted(result["tools"]))

    def test_list_enabled_tools_excludes_meta_tools(self, mock_client):
        """Capability tools only, as the docstring promises — meta-tools are always
        present and would be noise in a capability inventory."""
        names = set(self._list_enabled_tools(self._server(mock_client)))
        self.assertEqual(names & _META_TOOLS, set())
        self.assertIn(_READ_ONLY_TOOL, names)

    def test_fql_resources_survive_tool_level_filtering(self, mock_client):
        """A withheld tool's guide stays readable.

        Guides are static docs and confer no capability. They also outlive the tools
        that name them — see TestGuideReferencesResolve.
        """
        server = self._server(mock_client, excluded_tools={_READ_ONLY_TOOL})
        self.assertNotIn(_READ_ONLY_TOOL, self._module_tools(server))
        resources = server.server._resource_manager._resources
        self.assertIn("falcon://host-groups/search/fql-guide", resources)

    def test_unknown_allow_list_name_aborts_startup(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        with self.assertRaises(ValueError) as ctx:
            FalconMCPServer(allowed_tools={"falcon_not_a_real_tool"})
        self.assertIn("falcon_not_a_real_tool", str(ctx.exception))

    def test_unknown_deny_list_name_aborts_startup(self, mock_client):
        """A typo in a deny-list would silently leave a tool exposed."""
        mock_client.return_value.authenticate.return_value = True
        with self.assertRaises(ValueError) as ctx:
            FalconMCPServer(excluded_tools={"falcon_serch_hosts"})
        self.assertIn("falcon_serch_hosts", str(ctx.exception))

    def test_unprefixed_name_is_rejected(self, mock_client):
        """Names are the prefixed form clients see; the bare name is a typo."""
        mock_client.return_value.authenticate.return_value = True
        with self.assertRaises(ValueError):
            FalconMCPServer(excluded_tools={"search_hosts"})

    def test_name_from_disabled_module_is_accepted(self, mock_client):
        """Validation spans all available modules, not just the enabled ones."""
        self._server(mock_client, excluded_tools={"falcon_search_hosts"})

    def test_validation_precedes_authentication(self, mock_client):
        """A bad name fails fast, without spending a Falcon round-trip."""
        mock_client.return_value.authenticate.return_value = True
        with self.assertRaises(ValueError):
            FalconMCPServer(excluded_tools={"falcon_bogus"})
        mock_client.return_value.authenticate.assert_not_called()


@patch("falcon_mcp.server.FalconClient")
class TestGuideReferencesResolve(unittest.TestCase):
    """Every falcon:// URI a live tool names must resolve to a registered resource.

    Tool descriptions go to the model verbatim. A description that says "consult
    falcon://x/fql-guide" while that resource is unregistered instructs the model to
    read something absent — the failure mode that killed module-level resource
    gating. This catches the class, not just the one case.
    """

    def setUp(self):
        registry.discover_modules()

    def _dangling(self, server: FalconMCPServer) -> set[str]:
        registered = {str(u) for u in server.server._resource_manager._resources}
        referenced = {
            uri
            for tool in server.server._tool_manager._tools.values()
            for uri in _URI_PATTERN.findall(tool.description or "")
        }
        return referenced - registered

    def test_every_referenced_guide_uri_resolves(self, mock_client):
        """The default surface: all modules, no filtering."""
        mock_client.return_value.authenticate.return_value = True
        self.assertEqual(self._dangling(FalconMCPServer()), set())

    def test_references_resolve_for_an_additively_pulled_in_module(self, mock_client):
        """The original break: --modules detections --tools falcon_search_applications."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, allowed_tools={_FOREIGN_TOOL}
        )
        self.assertEqual(self._dangling(server), set())

    def test_references_resolve_under_read_only(self, mock_client):
        mock_client.return_value.authenticate.return_value = True
        self.assertEqual(self._dangling(FalconMCPServer(read_only=True)), set())

    def test_the_guard_sees_a_real_reference(self, mock_client):
        """Guard against passing vacuously: a real tool must name a real URI."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(enabled_modules={"discover"})
        tool = server.server._tool_manager._tools[_FOREIGN_TOOL]
        self.assertIn(
            "falcon://discover/applications/fql-guide",
            _URI_PATTERN.findall(tool.description or ""),
        )


@patch("falcon_mcp.server.FalconClient")
class TestDynamicModeToolFiltering(unittest.TestCase):
    """Filtered tools must vanish from the search surface AND the executor.

    Filtering only the search results would leave falcon_execute_tool as a bypass.
    """

    def setUp(self):
        registry.discover_modules()

    def _dynamic_server(self, mock_client, **kwargs) -> FalconMCPServer:
        mock_client.return_value.authenticate.return_value = True
        return FalconMCPServer(enabled_modules={_MODULE}, dynamic=True, **kwargs)

    def _search(self, server: FalconMCPServer, query: str = "") -> list[str]:
        tool = server.server._tool_manager._tools["falcon_search_tools"]
        result = run_async(tool.run({"query": query, "limit": 100}))
        return [entry["name"] for entry in result["results"]]

    def _list_enabled_tools(self, server: FalconMCPServer) -> list[str]:
        tool = server.server._tool_manager._tools["falcon_list_enabled_tools"]
        return run_async(tool.run({}))["tools"]

    def _execute(self, server: FalconMCPServer, tool_name: str) -> Any:
        tool = server.server._tool_manager._tools["falcon_execute_tool"]
        return run_async(tool.run({"tool_name": tool_name, "parameters": {}}))

    def test_dynamic_mode_exposes_only_meta_tools(self, mock_client):
        server = self._dynamic_server(mock_client)
        self.assertEqual(
            set(server.server._tool_manager._tools),
            {"falcon_list_enabled_tools", "falcon_search_tools", "falcon_execute_tool"},
        )

    def test_dynamic_mode_omits_list_enabled_modules(self, mock_client):
        """Module info stays reachable via falcon_search_tools' module field/filter."""
        server = self._dynamic_server(mock_client)
        self.assertNotIn(
            "falcon_list_enabled_modules", server.server._tool_manager._tools
        )

    def test_list_enabled_tools_matches_dynamic_catalog(self, mock_client):
        """The enumeration must equal what falcon_execute_tool will actually accept."""
        server = self._dynamic_server(mock_client)
        served = self._list_enabled_tools(server)
        self.assertIn(_READ_ONLY_TOOL, served)
        self.assertIn(_MUTATING_TOOL, served)
        # Not enabled here, so it must not be advertised.
        self.assertNotIn(_FOREIGN_TOOL, served)

    def _by_module(self, server: FalconMCPServer) -> dict[str, list[str]]:
        tool = server.server._tool_manager._tools["falcon_list_enabled_tools"]
        return run_async(tool.run({}))["by_module"]

    def test_by_module_publishes_names_the_module_filter_accepts(self, mock_client):
        """Every published module name must return hits when passed as module=."""
        server = self._dynamic_server(mock_client)
        by_module = self._by_module(server)
        self.assertTrue(by_module)
        for module_name, tools in by_module.items():
            with self.subTest(module=module_name):
                self.assertEqual(set(self._search_module(server, module_name)), set(tools))

    def _search_module(self, server: FalconMCPServer, module: str) -> list[str]:
        tool = server.server._tool_manager._tools["falcon_search_tools"]
        result = run_async(tool.run({"module": module, "limit": 500}))
        return [entry["name"] for entry in result["results"]]

    def test_by_module_partitions_the_served_surface(self, mock_client):
        """Grouping must account for every served tool exactly once."""
        server = self._dynamic_server(mock_client)
        by_module = self._by_module(server)
        grouped = [name for tools in by_module.values() for name in tools]
        self.assertEqual(sorted(grouped), sorted(self._list_enabled_tools(server)))
        self.assertEqual(len(grouped), len(set(grouped)))

    def test_by_module_omits_withheld_tool(self, mock_client):
        server = self._dynamic_server(mock_client, excluded_tools={_MUTATING_TOOL})
        grouped = [
            name for tools in self._by_module(server).values() for name in tools
        ]
        self.assertNotIn(_MUTATING_TOOL, grouped)

    def test_by_module_key_means_ownership_not_an_enabled_module(self, mock_client):
        """An allow-listed tool publishes its owning module, which is not enabled.

        `--tools falcon_search_applications` loads `discover` for that one tool, so
        `by_module` gains a `discover` key while `falcon_list_enabled_modules` still
        reports no such module. The key describes which module a tool belongs to, not
        that the module's surface is available — and `module=` must return only the
        granted tool, never the module's other tools.
        """
        server = self._dynamic_server(mock_client, allowed_tools={_FOREIGN_TOOL})
        by_module = self._by_module(server)

        owning_module = registry.get_tool_module_map()[_FOREIGN_TOOL]
        self.assertIn(owning_module, by_module)
        self.assertEqual(by_module[owning_module], [_FOREIGN_TOOL])
        # The module is a grouping label here, not an enabled module.
        self.assertNotIn(owning_module, server.enabled_modules)
        # And searching it must not reach the tools that were never granted.
        self.assertEqual(self._search_module(server, owning_module), [_FOREIGN_TOOL])

    def test_list_enabled_tools_omits_absent_sibling_of_allowed_tool(self, mock_client):
        """Both live in `discover`, so allow-listing one must not imply the other."""
        server = self._dynamic_server(mock_client, allowed_tools={_FOREIGN_TOOL})
        served = self._list_enabled_tools(server)
        self.assertIn(_FOREIGN_TOOL, served)
        self.assertNotIn("falcon_search_unmanaged_assets", served)

    def test_list_enabled_tools_omits_read_only_withheld(self, mock_client):
        names = self._list_enabled_tools(self._dynamic_server(mock_client, read_only=True))
        self.assertIn(_READ_ONLY_TOOL, names)
        self.assertNotIn(_MUTATING_TOOL, names)

    def test_list_enabled_tools_omits_denied_tool(self, mock_client):
        names = self._list_enabled_tools(
            self._dynamic_server(mock_client, excluded_tools={_READ_ONLY_TOOL})
        )
        self.assertNotIn(_READ_ONLY_TOOL, names)

    def test_search_tools_reports_total_and_truncation(self, mock_client):
        """A capped result set must say so rather than silently dropping matches."""
        server = self._dynamic_server(mock_client)
        tool = server.server._tool_manager._tools["falcon_search_tools"]
        served = len(self._list_enabled_tools(server))

        capped = run_async(tool.run({"query": "", "limit": 2}))
        self.assertEqual(capped["total"], served)
        self.assertEqual(len(capped["results"]), 2)
        self.assertTrue(capped["truncated"])
        self.assertIn("falcon_list_enabled_tools", capped["hint"])

        full = run_async(tool.run({"query": "", "limit": 500}))
        self.assertEqual(full["total"], served)
        self.assertEqual(len(full["results"]), served)
        self.assertFalse(full["truncated"])

    def test_search_tools_zero_hit_hint_names_the_absent_capability(self, mock_client):
        """The dead-end hint must steer to enumeration and to telling the user."""
        server = self._dynamic_server(mock_client)
        tool = server.server._tool_manager._tools["falcon_search_tools"]
        result = run_async(tool.run({"query": "unmanaged assets", "limit": 20}))

        self.assertEqual(result["results"], [])
        self.assertEqual(result["total"], 0)
        self.assertFalse(result["truncated"])
        self.assertIn("unmanaged assets", result["hint"])
        self.assertIn("falcon_list_enabled_tools", result["hint"])
        self.assertIn("tell the user", result["hint"])

    def test_read_only_hides_mutating_tool_from_search(self, mock_client):
        names = self._search(self._dynamic_server(mock_client, read_only=True))
        self.assertIn(_READ_ONLY_TOOL, names)
        self.assertNotIn(_MUTATING_TOOL, names)

    def test_read_only_rejects_mutating_tool_in_executor(self, mock_client):
        """The executor must refuse it; TestWithheldToolsAreAttributable covers wording."""
        result = self._execute(
            self._dynamic_server(mock_client, read_only=True), _MUTATING_TOOL
        )
        self.assertIn("error", result)
        self.assertIn("withholds it", result["error"])

    def test_deny_list_rejects_tool_in_executor(self, mock_client):
        server = self._dynamic_server(mock_client, excluded_tools={_READ_ONLY_TOOL})
        self.assertNotIn(_READ_ONLY_TOOL, self._search(server))
        result = self._execute(server, _READ_ONLY_TOOL)
        self.assertIn("error", result)

    def test_allow_list_gated_module_hides_unnamed_tool_from_executor(self, mock_client):
        """A pulled-in module's unnamed tools stay unreachable via the executor."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, dynamic=True, allowed_tools={_FOREIGN_TOOL}
        )
        # falcon_search_applications was named; other discover tools were not.
        unnamed_discover = next(
            name
            for name, mod in registry.get_tool_module_map().items()
            if mod == "discover" and name != _FOREIGN_TOOL
        )
        self.assertNotIn(unnamed_discover, self._search(server))
        result = self._execute(server, unnamed_discover)
        self.assertIn("error", result)
        self.assertIn("Unknown tool", result["error"])

    def test_additively_pulled_tool_is_reachable_in_dynamic_mode(self, mock_client):
        """A tool pulled in from a disabled module must be searchable and executable."""
        mock_client.return_value.authenticate.return_value = True
        server = FalconMCPServer(
            enabled_modules={"detections"}, dynamic=True, allowed_tools={_FOREIGN_TOOL}
        )
        self.assertIn(_FOREIGN_TOOL, self._search(server))
        result = self._execute(server, _FOREIGN_TOOL)
        self.assertNotIn("Unknown tool", str(result))

    def test_withheld_names_appear_at_debug_level(self, mock_client):
        """Dynamic mode omits tools silently, so it must log its own names.

        This path never calls server.remove_tool, so without an explicit debug line
        --debug would report a count with nothing behind it.
        """
        mock_client.return_value.authenticate.return_value = True
        with self.assertLogs("falcon_mcp.dynamic", level="DEBUG") as captured:
            FalconMCPServer(
                enabled_modules={_MODULE}, dynamic=True, excluded_tools={_MUTATING_TOOL}
            )
        self.assertTrue(
            any(f"Withheld tool: {_MUTATING_TOOL}" in m for m in captured.output),
            captured.output,
        )

    def test_allowed_tool_still_reaches_its_handler(self, mock_client):
        """The filter withholds tools; it must not break the ones it keeps."""
        server = self._dynamic_server(mock_client, allowed_tools={_READ_ONLY_TOOL})
        module = server.modules[_MODULE]
        module.client.command = MagicMock(
            return_value={"status_code": 200, "body": {"resources": [], "meta": {}}}
        )
        result = self._execute(server, _READ_ONLY_TOOL)
        self.assertNotIn("error", result)


@patch("falcon_mcp.server.FalconClient")
class TestWithheldToolsAreAttributable(unittest.TestCase):
    """A config-withheld tool must not read as a missing product capability.

    Withholding removes the tool from the catalog, so its name lands in the same
    unknown-tool branch as a name that was never served. Left alone, the model tells
    the user the capability does not exist when the operator merely disabled it.
    """

    def setUp(self):
        registry.discover_modules()

    def _server(self, mock_client, **kwargs) -> FalconMCPServer:
        mock_client.return_value.authenticate.return_value = True
        return FalconMCPServer(enabled_modules={_MODULE}, **kwargs)

    def _execute(self, server: FalconMCPServer, tool_name: str) -> Any:
        tool = server.server._tool_manager._tools["falcon_execute_tool"]
        return run_async(tool.run({"tool_name": tool_name, "parameters": {}}))

    def _inventory(self, server: FalconMCPServer) -> dict[str, Any]:
        tool = server.server._tool_manager._tools["falcon_list_enabled_tools"]
        return run_async(tool.run({}))

    def test_read_only_withheld_tool_cites_the_rule(self, mock_client):
        server = self._server(mock_client, dynamic=True, read_only=True)
        error = self._execute(server, _MUTATING_TOOL)["error"]

        self.assertIn(_MUTATING_TOOL, error)
        self.assertIn("read-only", error)
        self.assertNotIn("Unknown tool", error)

    def test_denied_tool_cites_the_rule(self, mock_client):
        server = self._server(
            mock_client, dynamic=True, excluded_tools={_MUTATING_TOOL}
        )
        error = self._execute(server, _MUTATING_TOOL)["error"]

        self.assertIn("deny-list", error)
        self.assertNotIn("Unknown tool", error)

    def test_error_cites_only_the_rule_that_withheld_this_tool(self, mock_client):
        """With both rules on, each tool must name its own cause, not the server's.

        _READ_ONLY_TOOL is read-only, so --read-only cannot have withheld it; only the
        deny-list did. Citing every active rule would send an operator debugging their
        config to the wrong flag.
        """
        server = self._server(
            mock_client,
            dynamic=True,
            read_only=True,
            excluded_tools={_READ_ONLY_TOOL},
        )

        denied = self._execute(server, _READ_ONLY_TOOL)["error"]
        self.assertIn("deny-list", denied)
        self.assertNotIn("read-only", denied)

        mutating = self._execute(server, _MUTATING_TOOL)["error"]
        self.assertIn("read-only", mutating)
        self.assertNotIn("deny-list", mutating)

    def test_error_does_not_suppress_unrelated_tool_use(self, mock_client):
        """Blanket 'do not look for another tool' would stall legitimate work.

        On a read-only server the agent often guesses a mutator when a served read
        tool answers the real question, so the message must scope its warning to
        reproducing the withheld effect rather than to using tools at all.
        """
        server = self._server(mock_client, dynamic=True, read_only=True)
        error = self._execute(server, _MUTATING_TOOL)["error"]

        self.assertNotIn("do not look for another tool", error)
        self.assertIn("other tools remain available", error)

    def test_withheld_tool_is_still_not_executed(self, mock_client):
        """Naming the cause must not resurrect the tool — omission is the enforcement."""
        server = self._server(mock_client, dynamic=True, read_only=True)
        module = server.modules[_MODULE]
        module.client.command = MagicMock()

        self._execute(server, _MUTATING_TOOL)

        module.client.command.assert_not_called()

    def test_never_served_name_keeps_the_unknown_tool_error(self, mock_client):
        """The two cases must be distinguishable in both directions."""
        server = self._server(mock_client, dynamic=True, read_only=True)
        error = self._execute(server, "falcon_not_a_real_tool")["error"]

        self.assertIn("Unknown tool", error)
        self.assertNotIn("withholds it", error)

    def test_module_gate_is_not_reported_as_a_policy_withholding(self, mock_client):
        """--modules leaves the catalog smaller, not withheld.

        A tool from an unloaded module never enters the catalog, so it must fall
        through to the plain unknown-tool message rather than claiming a filter
        withheld it.
        """
        server = self._server(mock_client, dynamic=True)
        error = self._execute(server, _FOREIGN_TOOL)["error"]

        self.assertIn("Unknown tool", error)
        self.assertNotIn("withholds it", error)
        self.assertNotIn("filters_active", self._inventory(server))

    def test_zero_hit_hint_names_the_active_filter(self, mock_client):
        server = self._server(mock_client, dynamic=True, read_only=True)
        tool = server.server._tool_manager._tools["falcon_search_tools"]
        hint = run_async(tool.run({"query": "zzqqxx", "limit": 20}))["hint"]

        self.assertIn("tool filter", hint)
        self.assertIn("read-only", hint)
        self.assertIn("falcon_list_enabled_tools", hint)

    def test_inventory_names_the_active_filter_in_both_modes(self, mock_client):
        for dynamic in (True, False):
            with self.subTest(dynamic=dynamic):
                server = self._server(mock_client, dynamic=dynamic, read_only=True)
                self.assertEqual(
                    self._inventory(server)["filters_active"], "read-only"
                )

    def test_inventory_omits_the_key_when_no_filter_is_configured(self, mock_client):
        """Presence of the key is the signal, so an unfiltered server must not carry it."""
        for dynamic in (True, False):
            with self.subTest(dynamic=dynamic):
                inventory = self._inventory(self._server(mock_client, dynamic=dynamic))
                self.assertNotIn("filters_active", inventory)


if __name__ == "__main__":
    unittest.main()
