"""
Tests for the Intel module.
"""
import unittest

from src.modules.intel import IntelModule
from tests.modules.utils.test_modules import TestModules


class TestIntelModule(TestModules):
    """Test cases for the Intel module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IntelModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_actors",
        ]
        self.assert_tools_registered(expected_tools)

    def test_search_actors_success(self):
        """Test searching actors with successful response."""
        # Setup mock response with sample actors
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "actor1", "name": "Actor 1", "description": "Description 1"},
                    {"id": "actor2", "name": "Actor 2", "description": "Description 2"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_actors with test parameters
        result = self.module.search_actors(
            filter="name:'Actor*'", 
            limit=100, 
            offset=0, 
            sort="name.asc", 
            q="test"
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryIntelActorEntities",
            parameters={
                "filter": "name:'Actor*'",
                "limit": 100,
                "offset": 0,
                "sort": "name.asc",
                "q": "test"
            }
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "actor1")
        self.assertEqual(result[1]["id"], "actor2")

    def test_search_actors_empty_response(self):
        """Test searching actors with empty response."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_actors
        result = self.module.search_actors()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "QueryIntelActorEntities")

        # Verify result is an empty list
        self.assertEqual(result, [])

    def test_search_actors_error(self):
        """Test searching actors with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid query"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_actors
        result = self.module.search_actors(filter="invalid query")

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(result["error"].startswith("Failed to search actors"))


if __name__ == '__main__':
    unittest.main()
