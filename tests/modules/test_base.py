# pylint: disable=protected-access
"""
Tests for the Base module.
"""
import unittest

from src.modules.base import BaseModule
from tests.modules.utils.test_modules import TestModules


class ConcreteBaseModule(BaseModule):
    """Concrete implementation of BaseModule for testing."""

    def register_tools(self, server):
        """Implement abstract method."""


class TestBaseModule(TestModules):
    """Test cases for the Base module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def test_is_error_with_error_dict(self):
        """Test _is_error with a dictionary containing an error key."""
        response = {"error": "Something went wrong", "details": "Error details"}
        result = self.module._is_error(response)
        self.assertTrue(result)

    def test_is_error_with_non_error_dict(self):
        """Test _is_error with a dictionary not containing an error key."""
        response = {"status": "success", "data": "Some data"}
        result = self.module._is_error(response)
        self.assertFalse(result)

    def test_is_error_with_non_dict(self):
        """Test _is_error with a non-dictionary value."""
        # Test with a list
        response = ["item1", "item2"]
        result = self.module._is_error(response)
        self.assertFalse(result)

        # Test with a string
        response = "This is a string response"
        result = self.module._is_error(response)
        self.assertFalse(result)

        # Test with None
        response = None
        result = self.module._is_error(response)
        self.assertFalse(result)

        # Test with an integer
        response = 42
        result = self.module._is_error(response)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
