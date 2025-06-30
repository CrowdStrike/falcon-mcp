"""
Tests for the registry module.
"""
import unittest
from unittest.mock import patch, MagicMock

from src import registry


class TestRegistry(unittest.TestCase):
    """Test cases for the registry module."""

    def setUp(self):
        """Set up test fixtures."""
        # Save original AVAILABLE_MODULES to restore after tests
        self.original_modules = registry.AVAILABLE_MODULES.copy()
        # Clear AVAILABLE_MODULES for tests
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original AVAILABLE_MODULES after tests
        registry.AVAILABLE_MODULES.clear()
        registry.AVAILABLE_MODULES.update(self.original_modules)

    def test_is_modules_discovered_empty(self):
        """Test is_modules_discovered when no modules are discovered."""
        # Ensure AVAILABLE_MODULES is empty
        registry.AVAILABLE_MODULES.clear()

        # Test the function
        result = registry.is_modules_discovered()

        # Verify result is False when no modules are discovered
        self.assertFalse(result)

    def test_is_modules_discovered_with_modules(self):
        """Test is_modules_discovered when modules are discovered."""
        # Add a mock module to AVAILABLE_MODULES
        mock_module = MagicMock()
        registry.AVAILABLE_MODULES["test_module"] = mock_module

        # Test the function
        result = registry.is_modules_discovered()

        # Verify result is True when modules are discovered
        self.assertTrue(result)

    def test_discover_modules(self):
        """Test discover_modules function."""
        # Mock pkgutil.iter_modules to return a test module
        mock_module_info = ("path", "test_module", False)

        with patch("pkgutil.iter_modules", return_value=[mock_module_info]), \
             patch("importlib.import_module") as mock_import, \
             patch("os.path.dirname", return_value="/fake/path"):

            # Setup mock module with a TestModule class
            mock_module = MagicMock()
            mock_module_class = MagicMock()
            # Set TestModule as an attribute on the mock module
            setattr(mock_module, "TestModule", mock_module_class)
            # Configure dir to return TestModule
            type(mock_module).__dir__ = lambda x: ["TestModule"]

            # Make importlib.import_module return our mock module
            mock_import.return_value = mock_module

            # Call discover_modules
            registry.discover_modules()

            # Verify module was imported
            mock_import.assert_any_call("src.modules.test_module")

            # Verify module was registered
            self.assertIn("test", registry.AVAILABLE_MODULES)
            self.assertEqual(registry.AVAILABLE_MODULES["test"], mock_module_class)

    def test_get_module_names(self):
        """Test get_module_names function."""
        # Add mock modules to AVAILABLE_MODULES
        registry.AVAILABLE_MODULES.clear()
        registry.AVAILABLE_MODULES["module1"] = MagicMock()
        registry.AVAILABLE_MODULES["module2"] = MagicMock()

        # Call get_module_names
        result = registry.get_module_names()

        # Verify result contains the module names
        self.assertEqual(set(result), {"module1", "module2"})

    def test_get_available_modules(self):
        """Test get_available_modules function."""
        # Add mock modules to AVAILABLE_MODULES
        registry.AVAILABLE_MODULES.clear()
        mock_module1 = MagicMock()
        mock_module2 = MagicMock()
        registry.AVAILABLE_MODULES["module1"] = mock_module1
        registry.AVAILABLE_MODULES["module2"] = mock_module2

        # Call get_available_modules
        result = registry.get_available_modules()

        # Verify result is the same dictionary
        self.assertEqual(result, registry.AVAILABLE_MODULES)
        self.assertEqual(result["module1"], mock_module1)
        self.assertEqual(result["module2"], mock_module2)


if __name__ == "__main__":
    unittest.main()
