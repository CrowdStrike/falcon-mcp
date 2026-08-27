"""Tests for scripts/generate_module_docs.py."""

import importlib
import shutil
import sys
import tempfile
import textwrap
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
    validate_hosted_mcp_notes,
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

    def test_does_not_trace_basemodule_helpers(self):
        """Helpers inherited from BaseModule contribute no scopes.

        search_detections reaches the API through self._base_search_with_meta and
        self._base_get_by_ids, both defined on BaseModule. BaseModule's source mentions
        operation names belonging to every module, so tracing into it would attribute
        unrelated scopes here. The assertion is exact: only the two operations named
        inline in search_detections itself may contribute, and both map to Alerts:read.
        """
        from falcon_mcp.modules.detections import DetectionsModule

        result = extract_tool_scopes(DetectionsModule.search_detections, DetectionsModule)
        self.assertEqual(result, ["Alerts:read"])

    def test_traces_helper_chain_on_own_class(self):
        """A tool reaching the API only through a sibling method gets that method's scopes.

        invoke_agentworks_agent writes, then polls get_agentworks_agent_invocation for
        the result. Its own read scope therefore has to come from following that call,
        whose operation name is itself held in a module-level constant.
        """
        from falcon_mcp.modules.agentworks import AgentworksModule

        result = extract_tool_scopes(AgentworksModule.invoke_agentworks_agent, AgentworksModule)
        self.assertEqual(
            result,
            ["Charlotte AI Agent Definition:read", "Charlotte AI Agent Definition:write"],
        )

    def test_helper_getsource_failure_silently_skipped(self):
        """An OSError fetching a helper's source is skipped rather than raised.

        The mock dispatches on the object rather than counting calls. Scope detection
        calls getsource once per candidate — the tool method, each own-class method, and
        the module itself when resolving operation-name constants — and that count is an
        implementation detail a fixed side_effect list would pin.
        """
        import inspect as _inspect

        cls = type("FakeModule", (), {})
        cls._my_helper = len  # built-in, not inspectable

        def fake_method(self):
            self._my_helper()

        def fake_getsource(obj):
            if obj is fake_method:
                return "self._my_helper()\nsome_operation = 'dummy'"
            raise OSError("no source")

        with patch.object(_inspect, "getsource", side_effect=fake_getsource):
            result = extract_tool_scopes(fake_method, cls)
        self.assertIsInstance(result, list)


# ---------------------------------------------------------------------------
# TestClassContainerOperations — operation names held in a class-level dict
# ---------------------------------------------------------------------------

class TestClassContainerOperations(unittest.TestCase):
    """Modules that dispatch on a discriminator keep their operations in a class dict.

    `policies.py` and `exclusions.py` both hold every operation in an `_OPERATIONS`
    class attribute and select one with `self._OPERATIONS[type]["verb"]`. A dict is not
    callable, so helper tracing skips it, and every one of those tools documented no
    scopes at all. These are real modules rather than fixtures because the bug is live.
    """

    def test_policies_tools_all_document_scopes(self):
        from falcon_mcp.modules.policies import PoliciesModule

        blank = [
            name
            for name in extract_registered_tool_names(PoliciesModule)
            if not extract_tool_scopes(getattr(PoliciesModule, name), PoliciesModule)
        ]
        self.assertEqual(blank, [], f"policies tools documenting no scopes: {blank}")

    def test_exclusions_tools_all_document_scopes(self):
        from falcon_mcp.modules.exclusions import ExclusionsModule

        blank = [
            name
            for name in extract_registered_tool_names(ExclusionsModule)
            if not extract_tool_scopes(getattr(ExclusionsModule, name), ExclusionsModule)
        ]
        self.assertEqual(blank, [], f"exclusions tools documenting no scopes: {blank}")

    def test_subscript_key_selects_only_that_verb(self):
        """A literal subscript key narrows to that verb; it must not pull in every op.

        falcon_delete_policies reaches `_OPERATIONS[policy_type]["delete"]`, so it needs
        write scopes. It must not acquire a scope that only a *different* verb's endpoint
        would need — resolving the whole container instead of the path would do that.
        """
        from falcon_mcp.modules.policies import PoliciesModule

        scopes = extract_tool_scopes(PoliciesModule.delete_policies, PoliciesModule)
        self.assertTrue(scopes, "delete_policies must document scopes")
        self.assertEqual([s for s in scopes if s.endswith(":read")], [])
        self.assertTrue(all(s.endswith(":write") for s in scopes), scopes)

    def test_variable_subscript_key_narrows_to_its_assigned_literals(self):
        """A variable key resolves through the literals assigned to it, not by widening.

        create_policy and update_policy share _build_policy_body, which selects
        `_OPERATIONS[policy_type][op_key]` where `op_key` is `"update" if is_update else
        "create"`. Both are writes, so neither tool may claim a read scope; widening to
        every verb at that level would hand them the query/get endpoints' read scopes and
        over-state what a caller has to grant.
        """
        from falcon_mcp.modules.policies import PoliciesModule

        for name in ("create_policy", "update_policy"):
            scopes = extract_tool_scopes(getattr(PoliciesModule, name), PoliciesModule)
            with self.subTest(tool=name):
                self.assertTrue(scopes)
                self.assertEqual([s for s in scopes if s.endswith(":read")], [])

    def test_read_only_dispatching_tool_gets_no_write_scope(self):
        """The converse: a search tool over the same container stays read-only."""
        from falcon_mcp.modules.policies import PoliciesModule

        scopes = extract_tool_scopes(PoliciesModule.search_policies, PoliciesModule)
        self.assertTrue(scopes)
        self.assertEqual([s for s in scopes if s.endswith(":write")], [])

    def test_no_tool_in_any_module_documents_zero_scopes(self):
        """Every registered tool in every module resolves to at least one scope.

        A tool that reaches the API but documents nothing is the silent failure mode this
        whole area keeps regressing into, so assert it globally rather than per module.
        """
        blank: list[str] = []
        for key, info in discover_module_classes().items():
            module_cls = info["cls"]
            for name, tool_name in extract_registered_tool_names(module_cls).items():
                method = getattr(module_cls, name, None)
                if method is None:
                    continue
                if not extract_tool_scopes(method, module_cls):
                    blank.append(f"{key}/falcon_{tool_name}")
        self.assertEqual(sorted(blank), [], f"tools documenting no scopes: {sorted(blank)}")


# ---------------------------------------------------------------------------
# TestMixinDeclaredConstants — operation name behind a constant in a mixin file
# ---------------------------------------------------------------------------

class TestMixinDeclaredConstants(unittest.TestCase):
    """A mixin may name its operation in a constant declared in the mixin's own file.

    Scope detection has to read every file the module owns, and resolve each file's
    constants against that file. No shipped module does this yet — the cloud mixins hold
    only an FQL filter in a constant — so the fixtures are synthetic. They write real
    files because inspect.getsource reads them off disk.
    """

    def _build(self, files: dict[str, str], root_module: str, class_name: str) -> type:
        """Write files to a throwaway importable directory and return one of their classes."""
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, True)
        for filename, source in files.items():
            Path(tmpdir, filename).write_text(textwrap.dedent(source).lstrip())

        # Scope detection resolves a class's constants through sys.modules, so the fixture
        # has to be really imported. Unimport it again so the next test starts clean.
        preexisting = set(sys.modules)

        def _restore() -> None:
            for name in set(sys.modules) - preexisting:
                del sys.modules[name]
            if tmpdir in sys.path:
                sys.path.remove(tmpdir)

        self.addCleanup(_restore)
        sys.path.insert(0, tmpdir)
        importlib.invalidate_caches()

        return getattr(importlib.import_module(root_module), class_name)

    def test_constant_declared_in_mixin_file_resolves(self):
        """The operation name lives in the mixin's file, the concrete class is elsewhere."""
        cls = self._build(
            {
                "t552a_mixin.py": '''
                    """Mixin naming its operation once, in a module-level constant."""

                    _T552A_OP = "QueryRule"  # requires Cloud Security Policies:read


                    class T552AMixin:
                        def _do_query(self):
                            return self.client.command(_T552A_OP)
                ''',
                "t552a_concrete.py": '''
                    """Concrete module assembled from the mixin."""

                    from t552a_mixin import T552AMixin


                    class T552AModule(T552AMixin):
                        def my_tool(self):
                            return self._do_query()
                ''',
            },
            "t552a_concrete",
            "T552AModule",
        )

        self.assertEqual(
            extract_tool_scopes(cls.my_tool, cls),
            ["Cloud Security Policies:read"],
        )

    def test_collision_resolves_against_the_method_s_own_file(self):
        """Two mixin files declare the same constant name; the method's own file wins.

        The method that reads the constant lives in the file holding the *second* value,
        while an unrelated sibling earlier in the MRO happens to reuse the name. Python
        resolves the reference through the defining module's globals, so the operation
        really invoked is the second one. Anything that merges both files into a single
        map picks by MRO position instead and reports the sibling's unrelated scope.
        """
        cls = self._build(
            {
                "t552b_first.py": '''
                    """Earlier in the MRO, reusing the name for an unrelated operation."""

                    _T552B_OP = "QueryRule"  # requires Cloud Security Policies:read


                    class T552BFirst:
                        def _unrelated(self):
                            return self.client.command(_T552B_OP)
                ''',
                "t552b_second.py": '''
                    """Later in the MRO, and the file that actually defines _do_query."""

                    _T552B_OP = "QueryDevicesByFilter"  # requires Hosts:read


                    class T552BSecond:
                        def _do_query(self):
                            return self.client.command(_T552B_OP)
                ''',
                "t552b_concrete.py": '''
                    """Concrete module assembled from both mixins."""

                    from t552b_first import T552BFirst
                    from t552b_second import T552BSecond


                    class T552BModule(T552BFirst, T552BSecond):
                        def my_tool(self):
                            return self._do_query()
                ''',
            },
            "t552b_concrete",
            "T552BModule",
        )

        # Guard the premise: confirm which operation Python itself reaches, so this test
        # cannot drift into asserting the generator agrees with the wrong answer.
        instance = cls.__new__(cls)
        instance.client = types.SimpleNamespace(command=lambda op: op)
        self.assertEqual(instance.my_tool(), "QueryDevicesByFilter")

        self.assertEqual(extract_tool_scopes(cls.my_tool, cls), ["Hosts:read"])


    def test_annotated_module_constant_resolves(self):
        """A module constant spelled with a type annotation still resolves.

        `NAME: str = "op"` is an ast.AnnAssign, a different node type from `NAME = "op"`,
        though the annotation means nothing at runtime. Both _OPERATIONS dicts in the tree
        are written this way, so missing the node type would reopen the blank-scope hole
        for any module that types its constant.
        """
        cls = self._build(
            {
                "t552c_mixin.py": '''
                    """Mixin whose operation constant carries a type annotation."""

                    _T552C_OP: str = "QueryRule"  # requires Cloud Security Policies:read


                    class T552CMixin:
                        def _do_query(self):
                            return self.client.command(_T552C_OP)
                ''',
                "t552c_concrete.py": '''
                    """Concrete module assembled from the mixin."""

                    from t552c_mixin import T552CMixin


                    class T552CModule(T552CMixin):
                        def my_tool(self):
                            return self._do_query()
                ''',
            },
            "t552c_concrete",
            "T552CModule",
        )

        self.assertEqual(
            extract_tool_scopes(cls.my_tool, cls),
            ["Cloud Security Policies:read"],
        )

    def test_module_level_function_in_the_same_file_is_followed(self):
        """A tool that reaches the API through a plain function, not a method.

        `hosts.py` and `ngsiem.py` both name an operation inside a module-level helper
        (`_tag_error`, `_validate_repository`) rather than a method. Helper tracing keys on
        `self.<name>`, so a bare call is invisible; today those two are correct only
        because the calling tool repeats the literal.
        """
        cls = self._build(
            {
                "t552d_mod.py": '''
                    """Module whose operation name lives in a free function."""


                    def _build_error():
                        return {"operation": "QueryRule"}


                    class T552DModule:
                        def my_tool(self):
                            return _build_error()
                ''',
            },
            "t552d_mod",
            "T552DModule",
        )

        self.assertEqual(
            extract_tool_scopes(cls.my_tool, cls),
            ["Cloud Security Policies:read"],
        )

    def test_imported_function_is_not_followed(self):
        """A function imported from elsewhere contributes nothing.

        Shared helpers live outside the module and mention operations belonging to other
        modules, exactly like BaseModule. Following them would attribute unrelated scopes,
        so only functions defined in the module's own file may be traced.
        """
        cls = self._build(
            {
                "t552e_shared.py": '''
                    """Stands in for a shared helper module naming many operations."""


                    def shared_helper():
                        return {"operation": "QueryDevicesByFilter"}
                ''',
                "t552e_mod.py": '''
                    """Module that only calls the shared helper."""

                    from t552e_shared import shared_helper


                    class T552EModule:
                        def my_tool(self):
                            return shared_helper()
                ''',
            },
            "t552e_mod",
            "T552EModule",
        )

        self.assertEqual(extract_tool_scopes(cls.my_tool, cls), [])


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


# ---------------------------------------------------------------------------
# TestHostedMcpNotes — note keys must track real module and tool names
# ---------------------------------------------------------------------------

class TestHostedMcpNotes(unittest.TestCase):
    """Both hosted-MCP note dicts are keyed by name, so a rename silently drops the note.

    The docs freshness check cannot catch that: regenerating after a rename removes the
    note from the committed page too, so committed and generated agree. These tests are
    the guard instead, mirroring the bidirectional coverage test for filter hints.
    """

    @classmethod
    def setUpClass(cls):
        cls.modules = discover_module_classes()
        cls.tool_names = {
            f"falcon_{registered}"
            for mod_info in cls.modules.values()
            for registered in extract_registered_tool_names(mod_info["cls"]).values()
        }

    def test_module_note_keys_are_real_modules(self):
        from scripts.generate_module_docs import HOSTED_MCP_MODULE_NOTES

        for key in HOSTED_MCP_MODULE_NOTES:
            self.assertIn(key, self.modules, f"HOSTED_MCP_MODULE_NOTES key {key!r} is not a module")

    def test_tool_note_keys_are_registered_tools(self):
        from scripts.generate_module_docs import HOSTED_MCP_TOOL_NOTES

        for name in HOSTED_MCP_TOOL_NOTES:
            self.assertIn(
                name, self.tool_names, f"HOSTED_MCP_TOOL_NOTES key {name!r} is not a registered tool"
            )

    def test_live_registry_passes_validation(self):
        validate_hosted_mcp_notes(self.modules)  # must not raise

    def test_stale_module_key_raises(self):
        import scripts.generate_module_docs as _gmd

        with patch.dict(_gmd.HOSTED_MCP_MODULE_NOTES, {"zero_trust_assessment": "x"}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                validate_hosted_mcp_notes(self.modules)
        self.assertIn("zero_trust_assessment", str(ctx.exception))

    def test_stale_tool_key_raises(self):
        import scripts.generate_module_docs as _gmd

        with patch.dict(_gmd.HOSTED_MCP_TOOL_NOTES, {"falcon_search_cloud_insight": "x"}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                validate_hosted_mcp_notes(self.modules)
        self.assertIn("falcon_search_cloud_insight", str(ctx.exception))

    def test_overview_mentions_every_noted_module_and_tool(self):
        """The overview summary is hand-written prose; keep it in step with the note dicts."""
        from scripts.generate_module_docs import (
            HOSTED_MCP_MODULE_NOTES,
            HOSTED_MCP_TOOL_NOTES,
            MODULE_METADATA,
        )

        page = generate_overview_page(self.modules)
        section = page.split("## CrowdStrike-hosted MCP differences", 1)[1]

        for key in HOSTED_MCP_MODULE_NOTES:
            slug = MODULE_METADATA.get(key, {}).get("slug", key)
            self.assertIn(
                f"/modules/{slug}/",
                section,
                f"Module {key!r} has a hosted-MCP note but is not linked in the overview summary",
            )
        for name in HOSTED_MCP_TOOL_NOTES:
            self.assertIn(
                name,
                section,
                f"Tool {name!r} has a hosted-MCP note but is not named in the overview summary",
            )


if __name__ == "__main__":
    unittest.main()
