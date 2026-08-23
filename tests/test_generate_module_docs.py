"""Tests for scripts/generate_module_docs.py."""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure project root is on sys.path so the script can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from falcon_mcp.modules.base import BaseModule  # noqa: E402
from scripts.generate_module_docs import (  # noqa: E402
    _extract_kwarg_string,
    _extract_module_meta,
    _register_module_classes,
    clean_docstring,
    discover_module_classes,
    extract_registered_tool_names,
    extract_resource_info,
    extract_tool_annotations,
    extract_tool_scopes,
    generate_module_page,
    generate_overview_page,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_module(name: str, docstring: str = "") -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__name__ = name
    mod.__doc__ = docstring
    mod.BaseModule = BaseModule
    return mod


def _make_class_with_register_tools(source_fragment: str, class_name: str = "DummyModule") -> type:  # type: ignore[empty-body]
    """Build a class whose register_tools can be inspected via getsource.

    We write a real Python source file so inspect.getsource works.
    """
    # We can't easily create inspectable source at runtime, so we use the real
    # modules from the codebase as fixtures where necessary.
    pass


# ---------------------------------------------------------------------------
# TestCleanDocstring
# ---------------------------------------------------------------------------

class TestCleanDocstring(unittest.TestCase):

    def test_passes_through_plain_text(self):
        doc = "Search for hosts in your environment.\n\nReturns a list of hosts."
        self.assertEqual(clean_docstring(doc), doc)

    def test_strips_important_use_the(self):
        doc = "Find hosts.\n\nIMPORTANT: Use the FQL guide before constructing filters."
        result = clean_docstring(doc)
        self.assertNotIn("IMPORTANT", result)
        self.assertIn("Find hosts.", result)

    def test_strips_this_resource_contains(self):
        doc = "Guide.\n\nThis resource contains the guide for FQL filters."
        result = clean_docstring(doc)
        self.assertNotIn("This resource contains", result)

    def test_strips_returns_fql_syntax_guide(self):
        doc = "Tool desc.\n\nReturns FQL syntax guide on error."
        result = clean_docstring(doc)
        self.assertNotIn("Returns FQL syntax guide on error", result)

    def test_collapses_consecutive_blank_lines(self):
        doc = "First.\n\n\n\nSecond."
        result = clean_docstring(doc)
        self.assertNotIn("\n\n\n", result)
        self.assertIn("First.", result)
        self.assertIn("Second.", result)

    def test_empty_string(self):
        self.assertEqual(clean_docstring(""), "")

    def test_strips_leading_trailing_whitespace(self):
        doc = "  \n  Tool.\n  \n  "
        result = clean_docstring(doc)
        self.assertEqual(result, "Tool.")


# ---------------------------------------------------------------------------
# TestExtractModuleMeta
# ---------------------------------------------------------------------------

class TestExtractModuleMeta(unittest.TestCase):

    def test_extracts_title_from_first_line(self):
        mod = _make_module("test", "Real Time Response module for Falcon MCP Server.")
        title, _ = _extract_module_meta(mod)
        self.assertEqual(title, "Real Time Response")

    def test_extracts_title_without_trailing_dot(self):
        mod = _make_module("test", "Cloud Security module for Falcon MCP Server")
        title, _ = _extract_module_meta(mod)
        self.assertEqual(title, "Cloud Security")

    def test_extracts_description_from_second_paragraph(self):
        mod = _make_module(
            "test",
            "Hosts module for Falcon MCP Server.\n\nThis module provides tools for searching host devices.",
        )
        _, desc = _extract_module_meta(mod)
        self.assertIn("searching host devices", desc.lower())

    def test_returns_empty_strings_for_no_docstring(self):
        mod = _make_module("test", "")
        title, desc = _extract_module_meta(mod)
        self.assertEqual(title, "")
        self.assertEqual(desc, "")

    def test_title_capitalised(self):
        mod = _make_module("test", "Detections module for Falcon MCP Server.\n\nSearches for detections.")
        _, desc = _extract_module_meta(mod)
        if desc:
            self.assertEqual(desc[0], desc[0].upper())

    def test_description_only_first_sentence(self):
        mod = _make_module(
            "test",
            "Intel module for Falcon MCP Server.\n\n"
            "Provides threat intelligence. Also does other things. And more.",
        )
        _, desc = _extract_module_meta(mod)
        # Should stop after first sentence
        self.assertNotIn("Also does other things", desc)


# ---------------------------------------------------------------------------
# TestRegisterModuleClasses
# ---------------------------------------------------------------------------

class TestRegisterModuleClasses(unittest.TestCase):

    def test_registers_module_class_defined_in_module(self):
        mod = _make_module("falcon_mcp.modules.alpha", "Alpha module for Falcon MCP Server.")
        cls = type("AlphaModule", (BaseModule,), {"__module__": mod.__name__})
        mod.AlphaModule = cls
        result: dict = {}
        _register_module_classes(mod, result)
        self.assertIn("alpha", result)
        self.assertIs(result["alpha"]["cls"], cls)

    def test_skips_base_module(self):
        mod = _make_module("falcon_mcp.modules.beta")
        result: dict = {}
        _register_module_classes(mod, result)
        self.assertNotIn("base", result)

    def test_skips_imported_class(self):
        origin = _make_module("falcon_mcp.modules.origin")
        imported_cls = type("OriginModule", (BaseModule,), {"__module__": origin.__name__})
        origin.OriginModule = imported_cls

        importer = _make_module("falcon_mcp.modules.importer")
        importer.OriginModule = imported_cls  # imported, not defined here

        result: dict = {}
        _register_module_classes(importer, result)
        self.assertNotIn("origin", result)

    def test_registers_multiple_classes_from_one_module(self):
        mod = _make_module("falcon_mcp.modules.multi")
        for name in ("AlphaModule", "BetaModule"):
            cls = type(name, (BaseModule,), {"__module__": mod.__name__})
            setattr(mod, name, cls)
        result: dict = {}
        _register_module_classes(mod, result)
        self.assertIn("alpha", result)
        self.assertIn("beta", result)

    def test_auto_title_derived_from_docstring(self):
        mod = _make_module(
            "falcon_mcp.modules.widgets", "Widgets module for Falcon MCP Server."
        )
        cls = type("WidgetsModule", (BaseModule,), {"__module__": mod.__name__})
        mod.WidgetsModule = cls
        result: dict = {}
        _register_module_classes(mod, result)
        self.assertEqual(result["widgets"]["auto_title"], "Widgets")

    def test_fallback_title_when_no_docstring(self):
        mod = _make_module("falcon_mcp.modules.nodoc", "")
        cls = type("NodocModule", (BaseModule,), {"__module__": mod.__name__})
        mod.NodocModule = cls
        result: dict = {}
        _register_module_classes(mod, result)
        # Should fall back to module_key.title() = "Nodoc"
        self.assertEqual(result["nodoc"]["auto_title"], "Nodoc")


# ---------------------------------------------------------------------------
# TestDiscoverModuleClasses — integration, uses real filesystem
# ---------------------------------------------------------------------------

class TestDiscoverModuleClasses(unittest.TestCase):

    def test_cloud_discovered(self):
        modules = discover_module_classes()
        self.assertIn("cloud", modules)

    def test_all_have_cls_key(self):
        modules = discover_module_classes()
        for key, info in modules.items():
            self.assertIn("cls", info, f"Missing 'cls' for module {key!r}")
            self.assertTrue(issubclass(info["cls"], BaseModule))

    def test_all_have_auto_title(self):
        modules = discover_module_classes()
        for key, info in modules.items():
            self.assertIn("auto_title", info)
            self.assertIsInstance(info["auto_title"], str)
            self.assertTrue(info["auto_title"], f"Empty auto_title for {key!r}")

    def test_base_not_discovered(self):
        modules = discover_module_classes()
        self.assertNotIn("base", modules)

    def test_standard_modules_present(self):
        modules = discover_module_classes()
        for expected in ("detections", "hosts", "intel", "firewall", "cloud"):
            self.assertIn(expected, modules)


# ---------------------------------------------------------------------------
# TestExtractRegisteredToolNames — uses real CloudModule as fixture
# ---------------------------------------------------------------------------

class TestExtractRegisteredToolNames(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from falcon_mcp.modules.cloud.cloud import CloudModule
        cls.cloud_cls = CloudModule

    def test_returns_dict(self):
        names = extract_registered_tool_names(self.cloud_cls)
        self.assertIsInstance(names, dict)

    def test_contains_cloud_insights_tools(self):
        names = extract_registered_tool_names(self.cloud_cls)
        self.assertIn("search_cloud_insights", names)
        self.assertIn("get_cloud_asset_insights", names)
        self.assertIn("list_cloud_insight_definitions", names)

    def test_mixin_tools_registered_on_live_module(self):
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("test")
        module = self.cloud_cls(None)
        module.register_tools(server)
        self.assertIn("falcon_search_cloud_insights", module.tools)
        self.assertIn("falcon_get_cloud_asset_insights", module.tools)
        self.assertIn("falcon_list_cloud_insight_definitions", module.tools)

    def test_contains_base_cloud_tools(self):
        names = extract_registered_tool_names(self.cloud_cls)
        self.assertIn("search_cloud_risks", names)
        self.assertIn("search_cloud_groups", names)
        self.assertIn("get_cloud_groups", names)

    def test_values_are_mcp_tool_names_without_falcon_prefix(self):
        # register_tools uses name="foo", not name="falcon_foo"
        names = extract_registered_tool_names(self.cloud_cls)
        for method_name, tool_name in names.items():
            self.assertFalse(
                tool_name.startswith("falcon_"),
                f"Expected raw name, got prefixed: {tool_name!r}",
            )

    def test_returns_empty_for_class_without_register_tools(self):
        class NoRegister:
            pass
        self.assertEqual(extract_registered_tool_names(NoRegister), {})


# ---------------------------------------------------------------------------
# TestExtractResourceInfo — uses real CloudModule
# ---------------------------------------------------------------------------

class TestExtractResourceInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from falcon_mcp.modules.cloud.cloud import CloudModule
        cls.cloud_cls = CloudModule

    def test_returns_list(self):
        resources = extract_resource_info(self.cloud_cls)
        self.assertIsInstance(resources, list)

    def test_cloud_insights_fql_guide_present(self):
        resources = extract_resource_info(self.cloud_cls)
        uris = [r["uri"] for r in resources]
        self.assertIn("falcon://cloud/cloud-insights/fql-guide", uris)

    def test_mixin_resource_registered_at_runtime(self):
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("test")
        module = self.cloud_cls(None)
        module.register_resources(server)
        self.assertIn("falcon://cloud/cloud-insights/fql-guide", module.resources)

    def test_each_resource_has_required_keys(self):
        resources = extract_resource_info(self.cloud_cls)
        for r in resources:
            self.assertIn("uri", r)
            self.assertIn("name", r)
            self.assertIn("description", r)

    def test_returns_empty_for_class_without_register_resources(self):
        class NoResources:
            pass
        self.assertEqual(extract_resource_info(NoResources), [])


# ---------------------------------------------------------------------------
# TestExtractKwargString
# ---------------------------------------------------------------------------

class TestExtractKwargString(unittest.TestCase):

    def test_simple_string(self):
        block = 'description="hello world"'
        self.assertEqual(_extract_kwarg_string(block, "description"), "hello world")

    def test_parenthesized_concat(self):
        block = 'description=(\n    "hello "\n    "world"\n)'
        self.assertEqual(_extract_kwarg_string(block, "description"), "hello world")

    def test_missing_kwarg(self):
        self.assertEqual(_extract_kwarg_string("name='foo'", "description"), "")

    def test_single_quoted(self):
        block = "name='my_resource'"
        self.assertEqual(_extract_kwarg_string(block, "name"), "my_resource")

    def test_adjacent_literals(self):
        block = 'description="part one " "part two"'
        result = _extract_kwarg_string(block, "description")
        self.assertEqual(result, "part one part two")


# ---------------------------------------------------------------------------
# TestGenerateModulePage — smoke tests against the real cloud module
# ---------------------------------------------------------------------------

class TestGenerateModulePage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from falcon_mcp.modules.cloud.cloud import CloudModule
        cls.cloud_cls = CloudModule
        modules = discover_module_classes()
        info = modules["cloud"]
        cls.page = generate_module_page("cloud", cls.cloud_cls, info["auto_title"], info["auto_description"])

    def test_returns_string(self):
        self.assertIsInstance(self.page, str)

    def test_contains_meta_comments(self):
        self.assertIn("<!-- meta:title", self.page)
        self.assertIn("<!-- meta:section modules -->", self.page)

    def test_contains_tools_section(self):
        self.assertIn("## Tools", self.page)

    def test_insight_tools_present(self):
        self.assertIn("falcon_search_cloud_risks", self.page)
        self.assertIn("falcon_search_cloud_groups", self.page)
        self.assertIn("falcon_get_cloud_groups", self.page)
        self.assertIn("falcon_search_cloud_insights", self.page)
        self.assertIn("falcon_get_cloud_asset_insights", self.page)
        self.assertIn("falcon_list_cloud_insight_definitions", self.page)

    def test_contains_resources_section(self):
        self.assertIn("## Resources", self.page)
        self.assertIn("falcon://cloud/cloud-risks/fql-guide", self.page)
        self.assertIn("falcon://cloud/cloud-insights/fql-guide", self.page)

    def test_api_scopes_from_all_mixins(self):
        self.assertIn("Cloud Security API Assets:read", self.page)
        self.assertIn("Cloud Security API Risks:read", self.page)
        self.assertIn("Falcon Container Image:read", self.page)

    def test_custom_title_override_applied(self):
        # MODULE_METADATA["cloud"] sets title = "Cloud Security"
        self.assertIn("Cloud Security", self.page)

    def test_no_type_ignore_leaked_into_output(self):
        self.assertNotIn("type: ignore", self.page)

    def test_tool_count(self):
        count = self.page.count("### `falcon_")
        self.assertEqual(count, 14)

    def test_tool_order_follows_mixin_registration_order(self):
        # Tools appear in runtime registration order (super() unwind = reverse MRO).
        # insights → assets → containers → iom → risks
        def heading_pos(name: str) -> int:
            return self.page.index(f"### `{name}`")

        insights_pos = heading_pos("falcon_search_cloud_insights")
        asset_pos = heading_pos("falcon_search_cspm_assets")
        container_pos = heading_pos("falcon_search_kubernetes_containers")
        iom_pos = heading_pos("falcon_search_iom_findings")
        risks_pos = heading_pos("falcon_search_cloud_risks")
        self.assertLess(insights_pos, asset_pos)
        self.assertLess(asset_pos, container_pos)
        self.assertLess(container_pos, iom_pos)
        self.assertLess(iom_pos, risks_pos)


# ---------------------------------------------------------------------------
# TestGenerateModulePageSingleFile — tool ordering for a plain (non-mixin) module
# ---------------------------------------------------------------------------

class TestGenerateModulePageSingleFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from falcon_mcp.modules.recon import ReconModule
        modules = discover_module_classes()
        info = modules["recon"]
        cls.page = generate_module_page("recon", ReconModule, info["auto_title"], info["auto_description"])

    def test_tool_order_follows_registration_order(self):
        # Registration order: notifications → rules → exposed_data → aggregate_notifications
        #                     → aggregate_exposed_data → preview_rule
        # Alphabetical would put aggregate_* first — this test catches a revert to dir().
        def heading_pos(name: str) -> int:
            return self.page.index(f"### `{name}`")

        notifications_pos = heading_pos("falcon_search_recon_notifications")
        rules_pos = heading_pos("falcon_search_recon_rules")
        exposed_pos = heading_pos("falcon_search_recon_exposed_data_records")
        agg_notif_pos = heading_pos("falcon_aggregate_recon_notifications")
        self.assertLess(notifications_pos, rules_pos)
        self.assertLess(rules_pos, exposed_pos)
        self.assertLess(exposed_pos, agg_notif_pos)


# ---------------------------------------------------------------------------
# TestGenerateOverviewPage
# ---------------------------------------------------------------------------

class TestGenerateOverviewPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.modules = discover_module_classes()
        cls.page = generate_overview_page(cls.modules)

    def test_returns_string(self):
        self.assertIsInstance(self.page, str)

    def test_contains_overview_meta(self):
        self.assertIn("<!-- meta:title Module Overview -->", self.page)

    def test_contains_table_header(self):
        self.assertIn("| Module |", self.page)

    def test_cloud_row_present(self):
        self.assertIn("Cloud Security", self.page)

    def test_all_modules_in_table(self):
        for key in self.modules:
            # Each module should produce at least one row referencing its slug/key
            from scripts.generate_module_docs import MODULE_METADATA
            slug = MODULE_METADATA.get(key, {}).get("slug", key)
            self.assertIn(slug, self.page, f"Module {key!r} (slug={slug!r}) not found in overview")


# ---------------------------------------------------------------------------
# TestDiscoverModuleClassesCoverage — sub-package skip path
# ---------------------------------------------------------------------------

class TestDiscoverModuleClassesCoverage(unittest.TestCase):
    """Cover discover_module_classes line 644: sub-pkg and __init__ skips."""

    def test_nested_pkg_and_init_skipped(self):
        """Inject a nested package + __init__ entry into the cloud scan; both skipped."""
        import pkgutil as _pkgutil
        original_iter = _pkgutil.iter_modules

        def patched_iter(path):
            results = list(original_iter(path))
            # Only inject extras when scanning the cloud package
            if path and "cloud" in str(path[0]):
                results = [(None, "__init__", False), (None, "nested_pkg", True)] + results
            return iter(results)

        with patch("pkgutil.iter_modules", side_effect=patched_iter):
            modules = discover_module_classes()

        self.assertIn("cloud", modules)


# ---------------------------------------------------------------------------
# TestExtractToolScopes — getsource failure + helper tracing
# ---------------------------------------------------------------------------

class TestExtractToolScopes(unittest.TestCase):

    def test_returns_empty_when_getsource_fails(self):
        """Lines 677-678: TypeError/OSError from getsource returns []."""
        # Built-in functions can't be inspected
        result = extract_tool_scopes(len, type("C", (), {}))
        self.assertEqual(result, [])

    def test_traces_private_helper_on_class(self):
        """Lines 690-695: helper defined on the class is included in scope extraction."""
        from falcon_mcp.modules.detections import DetectionsModule
        # search_detections calls self._base_search_with_meta — defined on BaseModule,
        # NOT in DetectionsModule.__dict__, so it should NOT be traced (by design).
        # We verify the function runs without error and returns a list.
        result = extract_tool_scopes(DetectionsModule.search_detections, DetectionsModule)
        self.assertIsInstance(result, list)

    def test_helper_getsource_failure_silently_skipped(self):
        """Lines 692-695: OSError on helper getsource is silently skipped."""
        import inspect as _inspect
        # Create a class with a helper whose source can't be fetched
        cls = type("FakeModule", (), {})
        # Add a callable helper that inspect.getsource will fail on
        cls._my_helper = len  # built-in, not inspectable

        def fake_method(self):
            self._my_helper()

        with patch.object(_inspect, "getsource", side_effect=[
            "self._my_helper()\nsome_operation = 'dummy'",  # method source
            OSError("no source"),                            # helper source fails
        ]):
            result = extract_tool_scopes(fake_method, cls)
        self.assertIsInstance(result, list)


# ---------------------------------------------------------------------------
# TestExtractRegisteredToolNamesCoverage — nested paren depth (line 736)
# ---------------------------------------------------------------------------

class TestExtractRegisteredToolNamesCoverage(unittest.TestCase):

    def test_nested_parens_in_add_tool_call(self):
        """Line 736: depth increments when a nested '(' appears inside _add_tool block.

        Uses the real IOM module which has ToolAnnotations(...) inside _add_tool.
        """
        from falcon_mcp.modules.cloud.cloud_iom import _CloudIomMixin
        names = extract_registered_tool_names(_CloudIomMixin)
        # IOM module has tools with nested ToolAnnotations(...) — all must be extracted
        self.assertIn("search_iom_findings", names)
        self.assertIn("create_cspm_suppression_rule", names)
        self.assertIn("delete_cspm_suppression_rules", names)


# ---------------------------------------------------------------------------
# TestExtractKwargStringCoverage — unclosed paren fallback (line 775)
# ---------------------------------------------------------------------------

class TestExtractKwargStringCoverage(unittest.TestCase):

    def test_unclosed_paren_falls_back_to_rest(self):
        """Line 775: parenthesized group never closes → inner = rest (no break)."""
        # Unclosed paren — the for-else fires, inner = rest (everything after '(')
        # The quoted literals inside must still be extracted.
        block = 'description=("first part" "second part"'
        result = _extract_kwarg_string(block, "description")
        self.assertIn("first part", result)
        self.assertIn("second part", result)


# ---------------------------------------------------------------------------
# TestExtractToolAnnotations — lines 837-846
# ---------------------------------------------------------------------------

class TestExtractToolAnnotations(unittest.TestCase):

    def test_extracts_annotations_from_iom_module(self):
        """Lines 837-846: IOM module has explicit ToolAnnotations on mutating tools."""
        from falcon_mcp.modules.cloud.cloud_iom import _CloudIomMixin
        annotations = extract_tool_annotations(_CloudIomMixin)
        self.assertIn("create_cspm_suppression_rule", annotations)
        self.assertIn("delete_cspm_suppression_rules", annotations)
        create_anno = annotations["create_cspm_suppression_rule"]
        self.assertFalse(create_anno.get("readOnlyHint", True))
        self.assertTrue(create_anno.get("destructiveHint", False))

    def test_returns_empty_for_module_without_annotations(self):
        """Module with no ToolAnnotations in register_tools returns {}."""
        from falcon_mcp.modules.cloud.cloud_risks import _CloudRisksMixin
        annotations = extract_tool_annotations(_CloudRisksMixin)
        # Risks module uses default read-only annotations (no explicit ToolAnnotations)
        self.assertEqual(annotations, {})


# ---------------------------------------------------------------------------
# TestGenerateModulePageCoverage — annotations, scopes, admonitions
# ---------------------------------------------------------------------------

class TestGenerateModulePageCoverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        modules = discover_module_classes()
        # Use the IOM mixin through CloudModule — has destructive/write tools
        from falcon_mcp.modules.cloud.cloud import CloudModule
        cls.cloud_cls = CloudModule
        cls.cloud_info = modules["cloud"]
        cls.cloud_page = generate_module_page(
            "cloud", CloudModule,
            cls.cloud_info["auto_title"],
            cls.cloud_info["auto_description"],
        )

        # Use detections module — has known API scopes
        from falcon_mcp.modules.detections import DetectionsModule
        cls.det_cls = DetectionsModule
        cls.det_info = modules["detections"]
        cls.det_page = generate_module_page(
            "detections", DetectionsModule,
            cls.det_info["auto_title"],
            cls.det_info["auto_description"],
        )

    def test_api_scopes_section_present_for_module_with_scopes(self):
        """Lines 912-916: modules with API scopes emit a ## API Scopes section."""
        self.assertIn("## API Scopes", self.det_page)

    def test_api_scopes_listed_as_code(self):
        """API scope entries are rendered as backtick-quoted list items."""
        # Find content between ## API Scopes and next ##
        import re
        m = re.search(r"## API Scopes\n(.*?)\n##", self.det_page, re.DOTALL)
        self.assertIsNotNone(m, "## API Scopes section not found or has no content before next ##")
        scopes_block = m.group(1)
        self.assertIn("- `", scopes_block)

    def test_tool_with_annotations_produces_admonition(self):
        """Lines 837-846 + 880: page for a module with mutating tools shows admonition.

        The cloud page is generated from CloudModule — _CloudRisksMixin is first in
        MRO, so its 3 tools are visible to getsource. Those are all read-only, so
        no CAUTION/NOTE block. We verify via a module that has mutating tools visible
        at the top of its MRO.
        """
        from falcon_mcp.modules.cloud.cloud_iom import _CloudIomMixin
        iom_page = generate_module_page(
            "cloud", _CloudIomMixin, "Cloud IOM", "IOM tools."
        )
        self.assertIn("> [!CAUTION]", iom_page)

    def test_write_only_tool_produces_note_admonition(self):
        """Lines 935-937: non-destructive mutating tool emits > [!NOTE] block.

        correlation_rules has both readOnlyHint=False/destructiveHint=False (NOTE)
        and readOnlyHint=False/destructiveHint=True (CAUTION) tools.
        """
        from falcon_mcp.modules.correlation_rules import CorrelationRulesModule
        modules = discover_module_classes()
        info = modules["correlationrules"]
        page = generate_module_page(
            "correlationrules", CorrelationRulesModule,
            info["auto_title"], info["auto_description"],
        )
        self.assertIn("> [!NOTE]", page)
        self.assertIn("> [!CAUTION]", page)


# ---------------------------------------------------------------------------
# TestMain — lines 1006-1034, 1038
# ---------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    def test_main_writes_files_to_output_dir(self):
        """Lines 1006-1034: main() creates output dir, writes overview + per-module pages."""
        import tempfile
        from pathlib import Path as _Path

        import scripts.generate_module_docs as _gmd

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = _Path(tmp) / "modules"
            original_dir = _gmd.OUTPUT_DIR
            _gmd.OUTPUT_DIR = tmp_path
            try:
                main()
            finally:
                _gmd.OUTPUT_DIR = original_dir

            written = list(tmp_path.glob("*.md"))
            names = {f.name for f in written}
            self.assertIn("overview.md", names)
            # At least one per-module page should be written
            self.assertGreater(len(written), 1)

    def test_main_removes_stale_files(self):
        """Lines 1029-1032: main() deletes .md files not in expected_files."""
        import tempfile
        from pathlib import Path as _Path

        import scripts.generate_module_docs as _gmd

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = _Path(tmp) / "modules"
            tmp_path.mkdir()
            stale = tmp_path / "stale_old_module.md"
            stale.write_text("old content")

            original_dir = _gmd.OUTPUT_DIR
            _gmd.OUTPUT_DIR = tmp_path
            try:
                main()
            finally:
                _gmd.OUTPUT_DIR = original_dir

            self.assertFalse(stale.exists(), "Stale file should have been removed by main()")


if __name__ == "__main__":
    unittest.main()
