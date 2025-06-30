"""
Tests for the module registry.
"""
import unittest
from unittest.mock import MagicMock

from src import registry
from src.modules.base import BaseModule


class TestRegistry(unittest.TestCase):
    """Test cases for the module registry."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear the AVAILABLE_MODULES dictionary before each test
        registry.AVAILABLE_MODULES.clear()

    def tearDown(self):
        """Clean up after each test method."""
        # Restore the original AVAILABLE_MODULES dictionary
        registry.AVAILABLE_MODULES.clear()
        # Re-discover modules to restore the original state
        registry.discover_modules()

    def test_discover_modules(self):
        """Test that discover_modules correctly populates AVAILABLE_MODULES."""
        # Call discover_modules
        registry.discover_modules()

        # Verify that AVAILABLE_MODULES is not empty
        self.assertGreater(len(registry.AVAILABLE_MODULES), 0)

        # Verify that all registered modules are subclasses of BaseModule
        for module_class in registry.AVAILABLE_MODULES.values():
            self.assertTrue(issubclass(module_class, BaseModule))

    def test_get_module_names(self):
        """Test that get_module_names returns the correct list of module names."""
        # Manually populate AVAILABLE_MODULES with some test modules
        registry.AVAILABLE_MODULES = {
            'test1': MagicMock(),
            'test2': MagicMock(),
            'test3': MagicMock()
        }

        # Call get_module_names
        module_names = registry.get_module_names()

        # Verify that the returned list contains all the expected module names
        self.assertEqual(set(module_names), {'test1', 'test2', 'test3'})
        self.assertEqual(len(module_names), 3)

    def test_get_module_names_empty(self):
        """Test that get_module_names returns an empty list when no modules are registered."""
        # Ensure AVAILABLE_MODULES is empty
        registry.AVAILABLE_MODULES.clear()

        # Call get_module_names
        module_names = registry.get_module_names()

        # Verify that the returned list is empty
        self.assertEqual(module_names, [])

    def test_actual_modules_discovery(self):
        """Test that actual modules in the project are discovered correctly."""
        # Clear the AVAILABLE_MODULES dictionary
        registry.AVAILABLE_MODULES.clear()

        # Call discover_modules
        registry.discover_modules()

        # Get the list of expected module names based on the project structure
        # This assumes that the project has modules like 'incidents', 'intel'
        expected_modules = ['incidents', 'intel']

        # Verify that all expected modules are discovered
        for module_name in expected_modules:
            self.assertIn(module_name, registry.AVAILABLE_MODULES)

        # Verify that all discovered modules are subclasses of BaseModule
        for module_class in registry.AVAILABLE_MODULES.values():
            self.assertTrue(issubclass(module_class, BaseModule))


if __name__ == '__main__':
    unittest.main()
