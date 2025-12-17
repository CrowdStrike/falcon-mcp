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

    def test_base_get_api_call_binary_to_string_success(self):
        """Test _base_get_api_call successfully converts binary response to string."""
        # Setup mock response with binary content
        binary_content = b'{"test": "binary_conversion", "status": "success"}'
        mock_response = {
            "status_code": 200,
            "body": binary_content
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call with decode_binary=True (default)
        result = self.module._base_get_api_call(
            operation="GetBinaryData",
            api_params={"param1": "value1"},
            error_message="Failed to get binary data"
        )

        # Verify result is decoded as string
        self.assertIsInstance(result, str, "Result should be decoded as string")
        self.assertNotIsInstance(result, bytes, "Result should not be binary")
        self.assertEqual(result, '{"test": "binary_conversion", "status": "success"}')

        # Verify API was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetBinaryData",
            parameters={"param1": "value1"}
        )

    def test_base_get_api_call_binary_to_string_disabled(self):
        """Test _base_get_api_call with decode_binary=False uses standard response handling."""
        # Setup mock response with binary content
        binary_content = b'{"test": "no_conversion"}'
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"decoded": "standard_handling"}]}  # Standard JSON response
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call with decode_binary=False
        result = self.module._base_get_api_call(
            operation="GetStandardData",
            api_params={"param1": "value1"},
            decode_binary=False
        )

        # Verify result uses standard response handling (returns resources list)
        self.assertIsInstance(result, list, "Result should be list from standard handling")
        self.assertEqual(result, [{"decoded": "standard_handling"}])

    def test_base_get_api_call_empty_binary_response(self):
        """Test _base_get_api_call handles empty binary response correctly."""
        # Setup mock response with empty binary
        mock_response = {
            "status_code": 200,
            "body": b""  # Empty binary
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="GetEmptyData",
            api_params={}
        )

        # Verify empty binary becomes empty string
        self.assertIsInstance(result, str, "Empty binary should become empty string")
        self.assertEqual(result, "", "Empty binary should decode to empty string")

    def test_base_get_api_call_large_binary_response(self):
        """Test _base_get_api_call handles large binary responses."""
        # Create a large binary content (simulating large MITRE report)
        large_json = '{"data": "' + "x" * 10000 + '", "size": "large"}'
        large_binary = large_json.encode('utf-8')

        mock_response = {
            "status_code": 200,
            "body": large_binary
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="GetLargeReport",
            api_params={"format": "json"}
        )

        # Verify large binary is properly decoded
        self.assertIsInstance(result, str, "Large binary should be decoded as string")
        self.assertEqual(len(result), len(large_json), "Decoded string should match original length")
        self.assertIn('"size": "large"', result, "Content should be preserved")

    def test_base_get_api_call_csv_binary_response(self):
        """Test _base_get_api_call handles CSV binary responses."""
        # Setup mock CSV response as binary
        csv_content = "id,name,status\n1,Test Item,active\n2,Another Item,inactive"
        csv_binary = csv_content.encode('utf-8')

        mock_response = {
            "status_code": 200,
            "body": csv_binary
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="ExportDataAsCsv",
            api_params={"format": "csv"}
        )

        # Verify CSV binary is properly decoded
        self.assertIsInstance(result, str, "CSV binary should be decoded as string")
        self.assertIn("id,name,status", result, "CSV headers should be preserved")
        self.assertIn("Test Item,active", result, "CSV data should be preserved")

    def test_base_get_api_call_utf8_special_characters(self):
        """Test _base_get_api_call handles UTF-8 special characters in binary responses."""
        # Setup mock response with UTF-8 special characters
        special_content = '{"message": "Special chars: áéíóú ñ 中文 🚀"}'
        special_binary = special_content.encode('utf-8')

        mock_response = {
            "status_code": 200,
            "body": special_binary
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="GetInternationalData",
            api_params={}
        )

        # Verify UTF-8 characters are properly decoded
        self.assertIsInstance(result, str, "UTF-8 binary should be decoded as string")
        self.assertIn("áéíóú", result, "Accented characters should be preserved")
        self.assertIn("中文", result, "Chinese characters should be preserved")
        self.assertIn("🚀", result, "Emoji should be preserved")

    def test_base_get_api_call_non_binary_response_with_decode_true(self):
        """Test _base_get_api_call with non-binary response body when decode_binary=True."""
        # Setup mock response with non-binary body (dict)
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test", "type": "non_binary"}]}  # Dict, not binary
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call with decode_binary=True
        result = self.module._base_get_api_call(
            operation="GetJsonData",
            api_params={},
            decode_binary=True  # Should fall back to standard handling for non-binary
        )

        # Verify falls back to standard response handling
        self.assertIsInstance(result, list, "Non-binary response should use standard handling")
        self.assertEqual(result, [{"id": "test", "type": "non_binary"}])

    def test_base_get_api_call_error_response(self):
        """Test _base_get_api_call handles error responses correctly."""
        # Setup mock error response
        mock_response = {
            "status_code": 404,
            "body": {"errors": [{"message": "Resource not found"}]}
        }
        self.mock_client.command.return_value = mock_response

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="GetMissingData",
            api_params={"id": "nonexistent"},
            error_message="Custom error message"
        )

        # Verify error handling (returns error dict, not decoded string)
        self.assertIsInstance(result, dict, "Error response should be dict")
        self.assertIn("error", result, "Error dict should contain error key")
        self.assertIn("Custom error message", result["error"])

    def test_base_get_api_call_parameter_preparation(self):
        """Test _base_get_api_call properly prepares API parameters."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": b'{"prepared": true}'
        }
        self.mock_client.command.return_value = mock_response

        # Call with parameters that need preparation (None values should be filtered)
        result = self.module._base_get_api_call(
            operation="TestParameterPrep",
            api_params={
                "valid_param": "keep_this",
                "none_param": None,  # Should be filtered out
                "empty_param": "",   # Should be kept
                "zero_param": 0,     # Should be kept
            }
        )

        # Verify parameters were prepared (None filtered out)
        self.mock_client.command.assert_called_once_with(
            "TestParameterPrep",
            parameters={
                "valid_param": "keep_this",
                "empty_param": "",
                "zero_param": 0,
                # none_param should be filtered out
            }
        )

        # Verify result
        self.assertEqual(result, '{"prepared": true}')


if __name__ == "__main__":
    unittest.main()
