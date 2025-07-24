"""
Tests for the Base module.
"""

import unittest

from falcon_mcp.modules.base import BaseModule
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

    def test_base_get_by_ids_default_behavior(self):
        """Test _base_get_by_ids with default parameters (backward compatibility)."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "test1", "name": "Test Item 1"},
                    {"id": "test2", "name": "Test Item 2"},
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_by_ids with default parameters
        result = self.module._base_get_by_ids("TestOperation", ["test1", "test2"])

        # Verify client command was called correctly with default "ids" key
        self.mock_client.command.assert_called_once_with(
            "TestOperation", body={"ids": ["test1", "test2"]}
        )

        # Verify result
        expected_result = [
            {"id": "test1", "name": "Test Item 1"},
            {"id": "test2", "name": "Test Item 2"},
        ]
        self.assertEqual(result, expected_result)

    def test_base_get_by_ids_custom_id_key(self):
        """Test _base_get_by_ids with custom id_key parameter."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": "alert1", "status": "new"},
                    {"composite_id": "alert2", "status": "closed"},
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_by_ids with custom id_key
        result = self.module._base_get_by_ids(
            "PostEntitiesAlertsV2", ["alert1", "alert2"], id_key="composite_ids"
        )

        # Verify client command was called correctly with custom key
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2", body={"composite_ids": ["alert1", "alert2"]}
        )

        # Verify result
        expected_result = [
            {"composite_id": "alert1", "status": "new"},
            {"composite_id": "alert2", "status": "closed"},
        ]
        self.assertEqual(result, expected_result)

    def test_base_get_by_ids_with_additional_params(self):
        """Test _base_get_by_ids with additional parameters."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": "alert1", "status": "new", "hidden": False}
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_by_ids with additional parameters
        result = self.module._base_get_by_ids(
            "PostEntitiesAlertsV2",
            ["alert1"],
            id_key="composite_ids",
            include_hidden=True,
            sort_by="created_timestamp",
        )

        # Verify client command was called correctly with all parameters
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={
                "composite_ids": ["alert1"],
                "include_hidden": True,
                "sort_by": "created_timestamp",
            },
        )

        # Verify result
        expected_result = [{"composite_id": "alert1", "status": "new", "hidden": False}]
        self.assertEqual(result, expected_result)

    def test_base_get_by_ids_error_handling(self):
        """Test _base_get_by_ids error handling."""
        # Setup mock error response
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid request"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_by_ids
        result = self.module._base_get_by_ids("TestOperation", ["invalid_id"])

        # Verify error handling - should return error dict
        self.assertIn("error", result)
        self.assertIn("Failed to perform operation", result["error"])

    def test_base_get_by_ids_empty_response(self):
        """Test _base_get_by_ids with empty resources."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call _base_get_by_ids
        result = self.module._base_get_by_ids("TestOperation", ["nonexistent"])

        # Verify result is empty list
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
