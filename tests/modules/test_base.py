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

    def test_base_search_api_call_success(self):
        """Test _base_search_api_call with successful response."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "dev1", "hostname": "host1"},
                    {"device_id": "dev2", "hostname": "host2"},
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_search_api_call
        result = self.module._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={
                "filter": "platform_name:'Windows'",
                "limit": 50,
                "offset": 0,
                "sort": "hostname.asc",
            },
            error_message="Failed to search devices",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryDevicesByFilter",
            parameters={
                "filter": "platform_name:'Windows'",
                "limit": 50,
                "offset": 0,
                "sort": "hostname.asc",
            }
        )

        # Verify result
        expected_result = [
            {"device_id": "dev1", "hostname": "host1"},
            {"device_id": "dev2", "hostname": "host2"},
        ]
        self.assertEqual(result, expected_result)

    def test_base_search_api_call_with_none_values(self):
        """Test _base_search_api_call filters None values from parameters."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_search_api_call with None values
        result = self.module._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={
                "filter": None,  # Should be filtered out
                "limit": 10,
                "offset": None,  # Should be filtered out
                "sort": "hostname.asc",
            },
        )

        # Verify None values were filtered out
        self.mock_client.command.assert_called_once_with(
            "QueryDevicesByFilter",
            parameters={
                "limit": 10,
                "sort": "hostname.asc",
            }
        )
        self.assertEqual(result, [])

    def test_base_search_api_call_error_handling(self):
        """Test _base_search_api_call error handling."""
        # Setup mock error response
        mock_response = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_search_api_call
        result = self.module._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={"limit": 10},
            error_message="Custom error message",
        )

        # Verify error handling
        self.assertIn("error", result)
        self.assertIn("Custom error message", result["error"])

    def test_base_search_api_call_custom_default_result(self):
        """Test _base_search_api_call with custom default result."""
        # Setup mock empty response
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call with custom default result
        result = self.module._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={"limit": 10},
            default_result={"message": "No results found"},
        )

        # Verify custom default is returned for empty results
        self.assertEqual(result, {"message": "No results found"})

    def test_base_query_api_call_parameters_only(self):
        """Test _base_query_api_call with parameters only."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test1", "name": "Test"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_query_api_call with parameters only
        result = self.module._base_query_api_call(
            operation="GetTestData",
            query_params={"limit": 10, "filter": "active:true"},
            error_message="Failed to get test data",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetTestData", parameters={"limit": 10, "filter": "active:true"}
        )

        # Verify result
        expected_result = [{"id": "test1", "name": "Test"}]
        self.assertEqual(result, expected_result)

    def test_base_query_api_call_body_only(self):
        """Test _base_query_api_call with body only."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test2", "name": "Test2"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_query_api_call with body only
        result = self.module._base_query_api_call(
            operation="PostTestData",
            body_params={"ids": ["test1", "test2"], "include_metadata": True},
            error_message="Failed to post test data",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostTestData", body={"ids": ["test1", "test2"], "include_metadata": True}
        )

        # Verify result
        expected_result = [{"id": "test2", "name": "Test2"}]
        self.assertEqual(result, expected_result)

    def test_base_query_api_call_both_parameters_and_body(self):
        """Test _base_query_api_call with both parameters and body."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test3", "name": "Test3"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_query_api_call with both
        result = self.module._base_query_api_call(
            operation="ComplexOperation",
            query_params={"limit": 5},
            body_params={"filter_config": {"active": True}},
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "ComplexOperation",
            parameters={"limit": 5},
            body={"filter_config": {"active": True}},
        )

        # Verify result
        expected_result = [{"id": "test3", "name": "Test3"}]
        self.assertEqual(result, expected_result)

    def test_base_query_api_call_no_parameters(self):
        """Test _base_query_api_call with no parameters."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "default", "name": "Default"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_query_api_call with no parameters
        result = self.module._base_query_api_call(operation="GetDefaults")

        # Verify client command was called with no additional arguments
        self.mock_client.command.assert_called_once_with("GetDefaults")

        # Verify result
        expected_result = [{"id": "default", "name": "Default"}]
        self.assertEqual(result, expected_result)

    def test_base_query_api_call_error_handling(self):
        """Test _base_query_api_call error handling."""
        # Setup mock error response
        mock_response = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_query_api_call
        result = self.module._base_query_api_call(
            operation="FailingOperation",
            query_params={"test": "value"},
            error_message="Operation failed unexpectedly",
        )

        # Verify error handling
        self.assertIn("error", result)
        self.assertIn("Operation failed unexpectedly", result["error"])

    def test_base_query_api_call_graphql_operation(self):
        """Test _base_query_api_call with GraphQL operation (like IDP module uses)."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "data": {
                    "entities": {
                        "nodes": [
                            {"entityId": "entity1", "primaryDisplayName": "Entity 1"},
                            {"entityId": "entity2", "primaryDisplayName": "Entity 2"},
                        ]
                    }
                }
            },
        }
        self.mock_client.command.return_value = mock_response

        # GraphQL query similar to what IDP module uses
        graphql_query = """
        query GetEntities {
            entities(filter: {entityType: "USER"}) {
                nodes {
                    entityId
                    primaryDisplayName
                }
            }
        }
        """

        # Call _base_query_api_call with GraphQL body
        result = self.module._base_query_api_call(
            operation="api_preempt_proxy_post_graphql",
            body_params={"query": graphql_query},
            error_message="Failed to execute GraphQL query",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "api_preempt_proxy_post_graphql",
            body={"query": graphql_query}
        )

        # Verify result structure
        self.assertIn("data", result)
        self.assertIn("entities", result["data"])
        self.assertEqual(len(result["data"]["entities"]["nodes"]), 2)


if __name__ == "__main__":
    unittest.main()
