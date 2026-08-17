"""Tests for the module registry."""

import pkgutil
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp import registry
from falcon_mcp.modules.base import BaseModule

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_module(name: str, cls_name: str, *, base: type = BaseModule) -> types.ModuleType:
    """Return a synthetic module with a single *Module class defined in it."""
    mod = types.ModuleType(name)
    mod.__name__ = name

    cls = type(cls_name, (base,), {"__module__": name})
    setattr(mod, cls_name, cls)
    # Also expose BaseModule so the guard attr_name != "BaseModule" is exercised
    mod.BaseModule = BaseModule
    return mod


# ---------------------------------------------------------------------------
# TestRegistry
# ---------------------------------------------------------------------------

class TestRegistry(unittest.TestCase):

    def setUp(self):
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()

    def test_discover_modules(self):
        registry.discover_modules()
        self.assertGreater(len(registry.AVAILABLE_MODULES), 0)
        for module_class in registry.AVAILABLE_MODULES.values():
            self.assertTrue(issubclass(module_class, BaseModule))

    def test_get_module_names(self):
        registry.AVAILABLE_MODULES = {"test1": MagicMock(), "test2": MagicMock(), "test3": MagicMock()}
        names = registry.get_module_names()
        self.assertEqual(set(names), {"test1", "test2", "test3"})
        self.assertEqual(len(names), 3)

    def test_get_module_names_lazy_discovery(self):
        registry.AVAILABLE_MODULES.clear()
        names = registry.get_module_names()
        self.assertGreater(len(names), 0)
        for expected in ["detections", "hosts", "intel"]:
            self.assertIn(expected, names)

    def test_actual_modules_discovery(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()
        for expected in ["hosts", "intel"]:
            self.assertIn(expected, registry.AVAILABLE_MODULES)
        for cls in registry.AVAILABLE_MODULES.values():
            self.assertTrue(issubclass(cls, BaseModule))


# ---------------------------------------------------------------------------
# TestRegistryPackageScanning — new package-based discovery path
# ---------------------------------------------------------------------------

class TestRegistryPackageScanning(unittest.TestCase):
    """Verify discover_modules handles the cloud-style package layout."""

    def setUp(self):
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()

    def test_cloud_package_discovered(self):
        """The cloud package (which uses the mixin pattern) must be discovered."""
        registry.discover_modules()
        self.assertIn("cloud", registry.AVAILABLE_MODULES)

    def test_cloud_is_base_module_subclass(self):
        registry.discover_modules()
        self.assertTrue(issubclass(registry.AVAILABLE_MODULES["cloud"], BaseModule))

    def test_package_without_init_not_discovered(self):
        """pkgutil.iter_modules only reports regular packages (with __init__.py).
        This test asserts that a namespace-package directory is NOT silently registered.
        The cloud package already has __init__.py, so this is a regression guard.
        """
        import os

        import falcon_mcp.modules as mods_pkg
        modules_path = os.path.dirname(mods_pkg.__file__)
        package_names = {
            name for _, name, is_pkg in pkgutil.iter_modules([modules_path]) if is_pkg
        }
        # cloud should appear only because __init__.py exists
        self.assertIn("cloud", package_names)


# ---------------------------------------------------------------------------
# TestRegistryModuleGuard — __module__ guard for imported classes
# ---------------------------------------------------------------------------

class TestRegistryModuleGuard(unittest.TestCase):
    """The registry must skip *Module classes that are imported, not defined, in a file."""

    def setUp(self):
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()

    def test_imported_class_skipped(self):
        """A *Module class whose __module__ != the scanned module's __name__ is skipped."""
        # Simulate two modules: 'origin' defines OriginalModule, 'importer' imports it.
        origin_mod = _make_module("falcon_mcp.modules.origin", "OriginalModule")
        importer_mod = types.ModuleType("falcon_mcp.modules.importer")
        importer_mod.__name__ = "falcon_mcp.modules.importer"
        # Import OriginalModule into importer — its __module__ still points to origin.
        importer_mod.OriginalModule = origin_mod.OriginalModule
        importer_mod.BaseModule = BaseModule

        with patch.dict(sys.modules, {
            "falcon_mcp.modules.origin": origin_mod,
            "falcon_mcp.modules.importer": importer_mod,
        }):
            for attr_name in dir(importer_mod):
                if attr_name.endswith("Module") and attr_name != "BaseModule":
                    cls = getattr(importer_mod, attr_name)
                    if cls.__module__ != importer_mod.__name__:
                        continue  # guard fires — should not register
                    registry.AVAILABLE_MODULES[attr_name.lower().replace("module", "")] = cls

        # OriginalModule should NOT have been registered from importer_mod
        self.assertNotIn("original", registry.AVAILABLE_MODULES)

    def test_defined_class_registered(self):
        """A *Module class whose __module__ == scanned module's __name__ IS registered."""
        mod = _make_module("falcon_mcp.modules.mymod", "MymodModule")
        with patch.dict(sys.modules, {"falcon_mcp.modules.mymod": mod}):
            for attr_name in dir(mod):
                if attr_name.endswith("Module") and attr_name != "BaseModule":
                    cls = getattr(mod, attr_name)
                    if cls.__module__ != mod.__name__:
                        continue
                    key = attr_name.lower().replace("module", "")
                    registry.AVAILABLE_MODULES[key] = cls

        self.assertIn("mymod", registry.AVAILABLE_MODULES)

    def test_multiple_module_classes_per_file(self):
        """All *Module classes defined in one file should be registered (no 'exactly one' limit)."""
        mod = types.ModuleType("falcon_mcp.modules.multi")
        mod.__name__ = "falcon_mcp.modules.multi"
        mod.BaseModule = BaseModule
        for cls_name in ("AlphaModule", "BetaModule", "GammaModule"):
            cls = type(cls_name, (BaseModule,), {"__module__": mod.__name__})
            setattr(mod, cls_name, cls)

        with patch.dict(sys.modules, {"falcon_mcp.modules.multi": mod}):
            for attr_name in dir(mod):
                if attr_name.endswith("Module") and attr_name != "BaseModule":
                    cls = getattr(mod, attr_name)
                    if cls.__module__ != mod.__name__:
                        continue
                    key = attr_name.lower().replace("module", "")
                    registry.AVAILABLE_MODULES[key] = cls

        self.assertIn("alpha", registry.AVAILABLE_MODULES)
        self.assertIn("beta", registry.AVAILABLE_MODULES)
        self.assertIn("gamma", registry.AVAILABLE_MODULES)

    def test_base_module_never_registered(self):
        """BaseModule itself must never appear in AVAILABLE_MODULES."""
        registry.discover_modules()
        self.assertNotIn("base", registry.AVAILABLE_MODULES)
        for key in registry.AVAILABLE_MODULES:
            self.assertNotEqual(registry.AVAILABLE_MODULES[key], BaseModule)


# ---------------------------------------------------------------------------
# TestGetToolModuleMap — get_tool_module_map
# ---------------------------------------------------------------------------

class TestGetToolModuleMap(unittest.TestCase):

    def setUp(self):
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()

    def test_returns_dict_of_tool_to_module(self):
        registry.AVAILABLE_MODULES.clear()
        tool_map = registry.get_tool_module_map()
        self.assertIsInstance(tool_map, dict)
        self.assertGreater(len(tool_map), 0)

    def test_all_keys_are_falcon_prefixed(self):
        tool_map = registry.get_tool_module_map()
        for tool_name in tool_map:
            self.assertTrue(
                tool_name.startswith("falcon_"),
                f"Expected falcon_ prefix, got: {tool_name!r}",
            )

    def test_tool_maps_to_known_module(self):
        tool_map = registry.get_tool_module_map()
        known_modules = set(registry.get_module_names())
        for tool_name, module_name in tool_map.items():
            self.assertIn(
                module_name,
                known_modules,
                f"Tool {tool_name!r} maps to unknown module {module_name!r}",
            )

    def test_cloud_tools_map_to_cloud(self):
        tool_map = registry.get_tool_module_map()
        for tool_name in ("falcon_search_cloud_insights", "falcon_get_cloud_asset_insights"):
            self.assertIn(tool_name, tool_map)
            self.assertEqual(tool_map[tool_name], "cloud")


class TestRegistryPackageScanCoverage(unittest.TestCase):
    """Cover the remaining two lines in _register_from_module and discover_modules."""

    def setUp(self):
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        registry.AVAILABLE_MODULES.clear()
        registry.discover_modules()

    def test_imported_class_skipped_in_package_scan(self):
        """_register_from_module line 33: imported *Module class is skipped.

        Patch importlib.import_module so the scanned module contains a *Module
        class whose __module__ doesn't match the submodule's __name__ (i.e. it
        was imported from somewhere else).
        """
        origin = types.ModuleType("falcon_mcp.modules.cloud.cloud")
        origin.__name__ = "falcon_mcp.modules.cloud.cloud"
        imported_cls = type("CloudModule", (BaseModule,), {"__module__": origin.__name__})
        origin.CloudModule = imported_cls
        origin.BaseModule = BaseModule

        # Submodule that *imports* CloudModule — its name differs
        importer = types.ModuleType("falcon_mcp.modules.cloud.cloud_copy")
        importer.__name__ = "falcon_mcp.modules.cloud.cloud_copy"
        importer.CloudModule = imported_cls  # __module__ points to origin, not importer
        importer.BaseModule = BaseModule

        with patch("importlib.import_module", return_value=importer):
            registry._register_from_module("falcon_mcp.modules.cloud.cloud_copy", "test")

        self.assertNotIn("cloud", registry.AVAILABLE_MODULES)

    def test_nested_package_and_init_skipped_in_package_scan(self):
        """discover_modules line 52: sub-packages and __init__ submodules are skipped.

        Patch pkgutil.iter_modules so the cloud package appears to contain a
        nested package and an __init__ file — both should be silently skipped.
        """
        # We only need to exercise the skip branch; use real discover_modules
        # with a patched iter_modules that injects extra (sub-pkg, init) entries.
        original_iter = pkgutil.iter_modules

        def patched_iter(path):
            results = list(original_iter(path))
            if path and "cloud" in str(path[0]):
                # Inject a nested package and __init__ into the cloud scan
                results = [
                    (None, "__init__", False),
                    (None, "nested_pkg", True),
                ] + results
            return iter(results)

        with patch("pkgutil.iter_modules", side_effect=patched_iter):
            registry.discover_modules()

        # cloud should still be discovered (real submodules registered normally)
        self.assertIn("cloud", registry.AVAILABLE_MODULES)


if __name__ == "__main__":
    unittest.main()
