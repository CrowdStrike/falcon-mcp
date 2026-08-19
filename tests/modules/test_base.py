"""
Tests for the Base module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS, BaseModule
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

    def test_base_get_by_ids_with_query_parameters(self):
        """Test _base_get_by_ids sends `parameters` as query params, separate from the body."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"composite_id": "alert1", "status": "new"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module._base_get_by_ids(
            "PostEntitiesAlertsV2",
            ["alert1"],
            id_key="composite_ids",
            parameters={"include_hidden": False},
        )

        # The query param must not be folded into the POST body — some endpoints
        # declare it `in: query` and silently ignore a body copy.
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["alert1"]},
            parameters={"include_hidden": False},
        )
        self.assertEqual(result, [{"composite_id": "alert1", "status": "new"}])

    def test_base_get_by_ids_omits_empty_parameters(self):
        """Test that no `parameters` argument leaves existing callers' calls unchanged."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "test1"}]},
        }

        for parameters in (None, {}):
            with self.subTest(parameters=parameters):
                self.mock_client.command.reset_mock()

                self.module._base_get_by_ids(
                    "TestOperation", ["test1"], parameters=parameters
                )

                self.mock_client.command.assert_called_once_with(
                    "TestOperation", body={"ids": ["test1"]}
                )

    def test_base_get_by_ids_query_parameters_with_use_params(self):
        """Test that `parameters` merges into the query string when use_params=True."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "test1"}]},
        }

        self.module._base_get_by_ids(
            "TestGetOperation",
            ["test1"],
            use_params=True,
            parameters={"include_hidden": False},
        )

        self.mock_client.command.assert_called_once_with(
            "TestGetOperation",
            parameters={"ids": ["test1"], "include_hidden": False},
        )

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
        """Test _base_get_api_call successfully converts binary response to string.

        FalconPy returns raw bytes directly for binary download endpoints like GetMitreReport.
        """
        # Setup mock response - FalconPy returns raw bytes directly for binary endpoints
        binary_content = b'{"test": "binary_conversion", "status": "success"}'
        self.mock_client.command.return_value = binary_content

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
        """Test _base_get_api_call with decode_binary=False returns raw bytes.

        When decode_binary=False, FalconPy's raw bytes response should be returned as-is.
        """
        # Setup mock response - FalconPy returns raw bytes directly
        binary_content = b'{"raw": "bytes_data"}'
        self.mock_client.command.return_value = binary_content

        # Call _base_get_api_call with decode_binary=False
        result = self.module._base_get_api_call(
            operation="GetRawBinaryData",
            api_params={"param1": "value1"},
            decode_binary=False
        )

        # Verify result is raw bytes (not decoded)
        self.assertIsInstance(result, bytes, "Result should be raw bytes when decode_binary=False")
        self.assertEqual(result, binary_content)

    def test_base_get_api_call_empty_binary_response(self):
        """Test _base_get_api_call handles empty binary response correctly.

        FalconPy returns raw bytes directly for binary endpoints.
        """
        # Setup mock response - FalconPy returns raw bytes directly
        self.mock_client.command.return_value = b""  # Empty binary

        # Call _base_get_api_call
        result = self.module._base_get_api_call(
            operation="GetEmptyData",
            api_params={}
        )

        # Verify empty binary becomes empty string
        self.assertIsInstance(result, str, "Empty binary should become empty string")
        self.assertEqual(result, "", "Empty binary should decode to empty string")

    def test_base_get_api_call_large_binary_response(self):
        """Test _base_get_api_call handles large binary responses.

        FalconPy returns raw bytes directly for binary endpoints.
        """
        # Create a large binary content (simulating large MITRE report)
        large_json = '{"data": "' + "x" * 10000 + '", "size": "large"}'
        large_binary = large_json.encode('utf-8')

        # FalconPy returns raw bytes directly
        self.mock_client.command.return_value = large_binary

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
        """Test _base_get_api_call handles CSV binary responses.

        FalconPy returns raw bytes directly for binary endpoints.
        """
        # Setup mock CSV response - FalconPy returns raw bytes directly
        csv_content = "id,name,status\n1,Test Item,active\n2,Another Item,inactive"
        csv_binary = csv_content.encode('utf-8')

        self.mock_client.command.return_value = csv_binary

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
        """Test _base_get_api_call handles UTF-8 special characters in binary responses.

        FalconPy returns raw bytes directly for binary endpoints.
        """
        # Setup mock response with UTF-8 special characters
        special_content = '{"message": "Special chars: áéíóú ñ 中文 🚀"}'
        special_binary = special_content.encode('utf-8')

        # FalconPy returns raw bytes directly
        self.mock_client.command.return_value = special_binary

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
        """Test _base_get_api_call with dict response uses standard handling.

        For non-binary endpoints, FalconPy returns a dict with status_code and body.
        The decode_binary flag only applies to raw bytes responses.
        """
        # Setup mock response with non-binary body (dict) - standard FalconPy response
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test", "type": "non_binary"}]}
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
        """Test _base_get_api_call handles error responses correctly.

        For error responses, FalconPy returns a dict with status_code and body.
        """
        # Setup mock error response - dict format for errors
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
        """Test _base_get_api_call properly prepares API parameters.

        FalconPy returns raw bytes directly for binary endpoints.
        """
        # Setup mock response - FalconPy returns raw bytes directly
        self.mock_client.command.return_value = b'{"prepared": true}'

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

    def test_add_tool_applies_default_annotations(self):
        """Test that _add_tool applies READ_ONLY_ANNOTATIONS when no annotations provided."""
        self.module._add_tool(
            server=self.mock_server,
            method=lambda: None,
            name="test_tool",
        )

        self.mock_server.add_tool.assert_called_once()
        call_kwargs = self.mock_server.add_tool.call_args[1]
        self.assertEqual(call_kwargs["annotations"], READ_ONLY_ANNOTATIONS)

    def test_add_tool_passes_custom_annotations(self):
        """Test that _add_tool passes through custom annotations when provided."""
        custom_annotations = ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )

        self.module._add_tool(
            server=self.mock_server,
            method=lambda: None,
            name="mutating_tool",
            annotations=custom_annotations,
        )

        self.mock_server.add_tool.assert_called_once()
        call_kwargs = self.mock_server.add_tool.call_args[1]
        self.assertEqual(call_kwargs["annotations"], custom_annotations)

    def test_add_tool_disables_structured_output(self):
        """Verify _add_tool passes structured_output=False to prevent outputSchema emission."""
        self.module._add_tool(
            server=self.mock_server,
            method=lambda: None,
            name="test_tool",
        )

        self.mock_server.add_tool.assert_called_once()
        call_kwargs = self.mock_server.add_tool.call_args[1]
        self.assertFalse(call_kwargs["structured_output"])


class TestBaseModuleReorderByIds(TestModules):
    """Test cases for BaseModule._reorder_by_ids."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def test_reorder_restores_sorted_order(self):
        """Entities are reordered to match the query-step ID order."""
        ordered_ids = ["c", "a", "b"]
        entities = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["c", "a", "b"])

    def test_reorder_custom_id_field(self):
        """The id_field argument selects which key to match on."""
        ordered_ids = ["dev2", "dev1"]
        entities = [{"device_id": "dev1"}, {"device_id": "dev2"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "device_id")
        self.assertEqual([e["device_id"] for e in result], ["dev2", "dev1"])

    def test_reorder_extra_entity_appended_at_end(self):
        """Entities not present in ordered_ids are appended, never dropped."""
        ordered_ids = ["a", "b"]
        entities = [{"id": "b"}, {"id": "a"}, {"id": "extra"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b", "extra"])

    def test_reorder_missing_entity_skipped(self):
        """IDs with no matching entity are skipped silently."""
        ordered_ids = ["a", "missing", "b"]
        entities = [{"id": "b"}, {"id": "a"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b"])

    def test_reorder_empty_entities_returns_empty(self):
        """An empty entity list returns an empty list."""
        result = self.module._reorder_by_ids(["a", "b"], [], "id")
        self.assertEqual(result, [])

    def test_reorder_empty_ordered_ids_appends_all(self):
        """With no ordered IDs, all entities are returned in original order."""
        entities = [{"id": "a"}, {"id": "b"}]
        result = self.module._reorder_by_ids([], entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b"])

    def test_reorder_duplicate_id_in_ordered_ids_yields_no_extra_slot(self):
        """A duplicate ID in ordered_ids yields one slot, not a repeated entity.

        Query endpoints return primary-key IDs, so a repeat is degenerate; the
        second occurrence is skipped like a missing-entity ID.
        """
        ordered_ids = ["a", "a", "b"]
        entities = [{"id": "a"}, {"id": "b"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b"])

    def test_reorder_extra_entity_appended_even_when_first_in_input(self):
        """An unmatched entity is appended at the tail regardless of input position."""
        ordered_ids = ["a", "b"]
        entities = [{"id": "extra"}, {"id": "b"}, {"id": "a"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b", "extra"])

    def test_reorder_already_ordered_is_noop(self):
        """When entities already match ordered_ids, output is unchanged."""
        ordered_ids = ["a", "b", "c"]
        entities = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        result = self.module._reorder_by_ids(ordered_ids, entities, "id")
        self.assertEqual([e["id"] for e in result], ["a", "b", "c"])


class TestBuildPaginationEnvelope(TestModules):
    """Test cases for _build_pagination_envelope, focused on total honesty and cursors."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def test_offset_pagination_round_trips(self):
        """offset/limit/total from the API are surfaced verbatim; next is null."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}],
            {"total": 42, "offset": 0, "limit": 10},
            filter_used="name:'x'",
        )
        self.assertEqual(
            envelope["pagination"],
            {"total": 42, "offset": 0, "limit": 10, "next": None},
        )
        self.assertEqual(envelope["filter_used"], "name:'x'")

    def test_cursor_after_maps_to_next(self):
        """A non-null `after` cursor round-trips into `next`."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}],
            {"total": 500, "after": "CURSOR_TOKEN"},
        )
        self.assertEqual(envelope["pagination"]["next"], "CURSOR_TOKEN")
        self.assertEqual(envelope["pagination"]["total"], 500)
        # No offset/limit keys when the API doesn't send them (cursor endpoints).
        self.assertNotIn("offset", envelope["pagination"])
        self.assertNotIn("limit", envelope["pagination"])

    def test_cursor_nested_next_maps_to_next(self):
        """A nested `meta.pagination.next` cursor (Shield) round-trips into `next`."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}],
            {"total": 30, "next": "SHIELD_CURSOR"},
        )
        self.assertEqual(envelope["pagination"]["next"], "SHIELD_CURSOR")

    def test_cursor_nested_next_wins_over_after(self):
        """Precedence: nested `next` beats nested `after` when both are present."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}],
            {"next": "NESTED_NEXT", "after": "NESTED_AFTER"},
        )
        self.assertEqual(envelope["pagination"]["next"], "NESTED_NEXT")

    def test_empty_string_cursor_reports_none(self):
        """An empty-string cursor is not a real next page, so `next` is None."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}],
            {"total": 1, "next": "", "after": ""},
        )
        self.assertIsNone(envelope["pagination"]["next"])

    def test_missing_total_key_reports_none_not_page_size(self):
        """A pagination dict without a `total` key reports None, never the page size."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}, {"id": "b"}],
            {"offset": 0, "limit": 2},
        )
        self.assertIsNone(envelope["pagination"]["total"])

    def test_no_meta_nonempty_page_reports_none(self):
        """No pagination meta + a non-empty page: total is unknown, so None (not len)."""
        envelope = self.module._build_pagination_envelope(
            [{"id": "a"}, {"id": "b"}, {"id": "c"}],
            None,
        )
        self.assertIsNone(envelope["pagination"]["total"])
        self.assertIsNone(envelope["pagination"]["next"])

    def test_no_meta_empty_page_reports_none(self):
        """No pagination meta: the API gave no count, so total is None even when empty."""
        envelope = self.module._build_pagination_envelope([], None)
        self.assertIsNone(envelope["pagination"]["total"])

    def test_filter_used_omitted_when_none(self):
        """Tools with no filter param omit filter_used entirely."""
        envelope = self.module._build_pagination_envelope([{"id": "a"}], {"total": 1})
        self.assertNotIn("filter_used", envelope)


class TestExtractPagination(TestModules):
    """Cursor lives in three mutually-exclusive spots across endpoints; all fold to `next`."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def _envelope_next(self, response: dict) -> str | None:
        pagination = self.module._extract_pagination(response)
        return self.module._build_pagination_envelope([], pagination)["pagination"]["next"]

    def test_nested_after_folds_into_next(self):
        """IOC/Spotlight place the cursor at `meta.pagination.after`."""
        response = {"body": {"meta": {"pagination": {"total": 5, "after": "AFTER_TOK"}}}}
        self.assertEqual(self._envelope_next(response), "AFTER_TOK")

    def test_nested_next_folds_into_next(self):
        """Shield places the cursor at `meta.pagination.next`."""
        response = {"body": {"meta": {"pagination": {"total": 5, "next": "NEXT_TOK"}}}}
        self.assertEqual(self._envelope_next(response), "NEXT_TOK")

    def test_top_level_meta_next_folds_into_next(self):
        """CSPM assets/IOM place the cursor at the top-level `meta.next`."""
        response = {
            "body": {"meta": {"next": "TOP_TOK", "pagination": {"limit": 100, "total": 500}}}
        }
        pagination = self.module._extract_pagination(response)
        envelope = self.module._build_pagination_envelope([], pagination)
        self.assertEqual(envelope["pagination"]["next"], "TOP_TOK")
        # The nested limit/total still surface alongside the top-level cursor.
        self.assertEqual(envelope["pagination"]["limit"], 100)
        self.assertEqual(envelope["pagination"]["total"], 500)

    def test_top_level_meta_next_without_nested_pagination(self):
        """CSPM can return `meta.next` with no nested `pagination` block at all."""
        response = {"body": {"meta": {"next": "TOP_TOK"}}}
        self.assertEqual(self._envelope_next(response), "TOP_TOK")

    def test_nested_cursor_wins_over_top_level_meta_next(self):
        """Precedence: a nested cursor beats top-level `meta.next` when both exist."""
        response = {
            "body": {"meta": {"next": "TOP_TOK", "pagination": {"after": "AFTER_TOK"}}}
        }
        self.assertEqual(self._envelope_next(response), "AFTER_TOK")

    def test_no_meta_yields_no_cursor(self):
        """Empty-result / no-meta path: no cursor, `next` is None."""
        self.assertIsNone(self.module._extract_pagination({"body": {}}))
        self.assertIsNone(self._envelope_next({"body": {}}))


class TestBuildAggregateSpec(TestModules):
    """Body construction for aggregate queries — pure, no API calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def test_minimal_spec_is_type_and_field_only(self):
        """Live-verified minimal body: `type` + `field`. Nothing else leaks in.

        Swagger marks 16 fields `required`; live, only these two matter (omitting
        either returns HTTP 500). Unset kwargs must not appear as None/empty keys.
        """
        spec = self.module._build_aggregate_spec(agg_type="terms", field="status")
        self.assertEqual(spec, {"type": "terms", "field": "status"})

    def test_agg_type_maps_to_type_key(self):
        """`agg_type` is renamed to the wire key `type` (avoids shadowing the builtin)."""
        spec = self.module._build_aggregate_spec(agg_type="cardinality", field="agent_id")
        self.assertEqual(spec["type"], "cardinality")
        self.assertNotIn("agg_type", spec)

    def test_from_underscore_maps_to_from_key(self):
        """`from_` is renamed to the wire key `from` (a Python keyword)."""
        spec = self.module._build_aggregate_spec(agg_type="terms", field="status", from_=25)
        self.assertEqual(spec["from"], 25)
        self.assertNotIn("from_", spec)

    def test_msa_dialect_full_superset(self):
        """msa.AggregateQueryRequest: all 21 fields round-trip with correct values.

        Asserts full dict equality, not just the key set: two same-typed fields
        wired to each other's kwarg (e.g. `sort`/`interval` swapped in the dict
        literal) would satisfy a key-set check but corrupt every request.
        """
        spec = self.module._build_aggregate_spec(
            agg_type="terms",
            field="status",
            filter="status:'new'",
            name="by_status",
            size=10,
            sort="_count.desc",
            interval="day",
            time_zone="+00:00",
            from_=0,
            q="search",
            missing="N/A",
            include="a*",
            exclude="b*",
            date_ranges=[{"from": "2026-01-01", "to": "2026-02-01"}],
            ranges=[{"From": 0, "To": 10}],
            percents=[50.0, 95.0],
            filters_spec={"filters": [{"label": "x", "filter": "status:'new'"}]},
            extended_bounds={"min": 0, "max": 100},
            min_doc_count=1,
            max_doc_count=1000,
            sub_aggregates=[{"type": "terms", "field": "severity"}],
        )
        self.assertEqual(
            spec,
            {
                "type": "terms",
                "field": "status",
                "filter": "status:'new'",
                "name": "by_status",
                "size": 10,
                "sort": "_count.desc",
                "interval": "day",
                "time_zone": "+00:00",
                "from": 0,
                "q": "search",
                "missing": "N/A",
                "include": "a*",
                "exclude": "b*",
                "date_ranges": [{"from": "2026-01-01", "to": "2026-02-01"}],
                "ranges": [{"From": 0, "To": 10}],
                "percents": [50.0, 95.0],
                "filters_spec": {"filters": [{"label": "x", "filter": "status:'new'"}]},
                "extended_bounds": {"min": 0, "max": 100},
                "min_doc_count": 1,
                "max_doc_count": 1000,
                "sub_aggregates": [{"type": "terms", "field": "severity"}],
            },
        )
        self.assertEqual(len(spec), 21)

    def test_fwmgr_dialect_matches_msa_superset(self):
        """fwmgr.msa.AggregateQueryRequest is field-identical to the msa superset.

        SPEC-DERIVED, NOT LIVE-VERIFIED: every fwmgr aggregate operation was
        blocked on the probe tenant with `authorization failed` (not a scope
        problem — the read siblings return 200 on the same scope). This asserts
        that the two swagger definitions share the same 21 fields, which is why
        the helper needs no fwmgr-specific code path. The first downstream fwmgr
        aggregate tool should re-probe live.
        """
        kwargs = dict(
            agg_type="terms",
            field="rule_group",
            filter="enabled:true",
            name="by_group",
            size=10,
            sort="_count.desc",
            interval="day",
            time_zone="-05:00",
            from_=0,
            q="search",
            missing="N/A",
            include="a*",
            exclude="b*",
            date_ranges=[{"from": "2026-01-01", "to": "2026-02-01"}],
            ranges=[{"From": 0, "To": 10}],
            percents=[99.0],
            filters_spec={"filters": [{"label": "x", "filter": "enabled:true"}]},
            extended_bounds={"min": 0, "max": 100},
            min_doc_count=1,
            max_doc_count=1000,
            sub_aggregates=[{"type": "terms", "field": "platform"}],
        )
        spec = self.module._build_aggregate_spec(**kwargs)
        self.assertEqual(len(spec), 21)

    def test_api_msa_dialect_subset(self):
        """api.MSAAggregateQueryRequest is an 8-field subset; only those keys appear.

        Live-verified via `aggregates.slas.post.v1`.
        """
        spec = self.module._build_aggregate_spec(
            agg_type="terms",
            field="status",
            filter="status:'open'",
            name="by_status",
            size=5,
            sort="_count.desc",
            from_=0,
            date_ranges=[{"from": "2026-01-01", "to": "2026-02-01"}],
        )
        self.assertEqual(
            set(spec),
            {"type", "field", "filter", "name", "size", "sort", "from", "date_ranges"},
        )

    def test_detectsapi_dialect_subset(self):
        """detectsapi.AggregateAlertQueryRequest drops filters_spec/percents/extended_bounds.

        Live-verified via `PostAggregatesAlertsV2`. Staying in-dialect is the
        caller's job: the API silently ignores unknown keys (live, even a
        fabricated field returns HTTP 200 with unchanged buckets), so an
        out-of-dialect field is never reported back as an error.
        """
        spec = self.module._build_aggregate_spec(
            agg_type="date_histogram",
            field="created_timestamp",
            filter="status:'new'",
            name="over_time",
            size=10,
            sort="_count.desc",
            interval="day",
            time_zone="+00:00",
            from_=0,
            q="search",
            missing="N/A",
            include="a*",
            exclude="b*",
            date_ranges=[{"from": "2026-01-01", "to": "2026-02-01"}],
            ranges=[{"From": 0, "To": 10}],
            min_doc_count=1,
            max_doc_count=1000,
            sub_aggregates=[{"type": "terms", "field": "severity"}],
        )
        self.assertEqual(
            set(spec),
            {
                "type", "field", "filter", "name", "size", "sort", "interval",
                "time_zone", "from", "q", "missing", "include", "exclude",
                "date_ranges", "ranges", "min_doc_count", "max_doc_count",
                "sub_aggregates",
            },
        )
        # The three out-of-dialect fields stay absent when the caller omits them.
        for key in ("filters_spec", "percents", "extended_bounds"):
            self.assertNotIn(key, spec)

    def test_nested_structures_pass_through_unmodified(self):
        """date_ranges/ranges/filters_spec/extended_bounds are forwarded byte-for-byte."""
        date_ranges = [{"from": "2026-01-01T00:00:00Z", "to": "2026-02-01T00:00:00Z"}]
        ranges = [{"From": 0, "To": 10}, {"From": 10, "To": 100}]
        filters_spec = {"filters": [{"label": "critical", "filter": "severity:>=70"}]}
        extended_bounds = {"min": 1735689600, "max": 1738368000}

        spec = self.module._build_aggregate_spec(
            agg_type="range",
            field="severity",
            date_ranges=date_ranges,
            ranges=ranges,
            filters_spec=filters_spec,
            extended_bounds=extended_bounds,
        )

        self.assertEqual(spec["date_ranges"], date_ranges)
        self.assertEqual(spec["ranges"], ranges)
        self.assertEqual(spec["filters_spec"], filters_spec)
        self.assertEqual(spec["extended_bounds"], extended_bounds)

    def test_sub_aggregates_nest_recursively(self):
        """A sub_aggregates list built by the same helper nests unmodified.

        Live, sub-aggregate results come back as `buckets[].sub_aggregates[]` with
        the same bucket shape, recursively.
        """
        inner = self.module._build_aggregate_spec(
            agg_type="terms",
            field="severity",
            size=5,
            sub_aggregates=[
                self.module._build_aggregate_spec(agg_type="cardinality", field="agent_id")
            ],
        )
        outer = self.module._build_aggregate_spec(
            agg_type="terms", field="status", sub_aggregates=[inner]
        )

        self.assertEqual(outer["sub_aggregates"], [inner])
        self.assertEqual(
            outer["sub_aggregates"][0]["sub_aggregates"],
            [{"type": "cardinality", "field": "agent_id"}],
        )

    def test_falsy_but_meaningful_values_survive(self):
        """size=0, min_doc_count=0, from_=0 are real values, not "unset" — keep them."""
        spec = self.module._build_aggregate_spec(
            agg_type="terms",
            field="status",
            size=0,
            from_=0,
            min_doc_count=0,
            max_doc_count=0,
        )
        self.assertEqual(spec["size"], 0)
        self.assertEqual(spec["from"], 0)
        self.assertEqual(spec["min_doc_count"], 0)
        self.assertEqual(spec["max_doc_count"], 0)

    def test_empty_string_filter_survives(self):
        """An empty-string filter is a caller-supplied value, not an omission."""
        spec = self.module._build_aggregate_spec(agg_type="terms", field="status", filter="")
        self.assertIn("filter", spec)
        self.assertEqual(spec["filter"], "")


class TestBaseAggregate(TestModules):
    """The aggregate API call path — mocked client."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ConcreteBaseModule)

    def test_single_spec_is_still_list_wrapped(self):
        """A single aggregation must be sent as a one-element list, never a bare dict.

        Live, every dialect rejects a bare object: `cannot unmarshal object into
        Go value of type []*msa.AggregateQueryRequest`. Swagger marks 6 ops as
        bare objects; that is wrong. Do not "simplify" this to body={...}.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "by_status", "buckets": []}]},
        }

        self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.mock_client.command.assert_called_once_with(
            "PostAggregatesAlertsV2", body=[{"type": "terms", "field": "status"}]
        )

    def test_parameters_are_sent_alongside_the_body(self):
        """A few aggregate endpoints take query params as well as the body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "t", "buckets": []}]},
        }

        self.module._base_aggregate(
            "PostAggregatesFileDetailsV1",
            agg_type="terms",
            field="name",
            parameters={"ids": ["case-a"]},
        )

        self.mock_client.command.assert_called_once_with(
            "PostAggregatesFileDetailsV1",
            body=[{"type": "terms", "field": "name"}],
            parameters={"ids": ["case-a"]},
        )

    def test_parameters_omitted_when_not_given(self):
        """Endpoints without query params get a body-only call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "t", "buckets": []}]},
        }

        self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.assertNotIn("parameters", self.mock_client.command.call_args[1])

    def test_multi_spec_passes_through_in_one_list(self):
        """N specs go out in a single list body; N results come back."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "by_severity", "buckets": []},
                    {"name": "by_status", "buckets": []},
                ]
            },
        }

        specs = [
            {"type": "terms", "field": "status", "name": "by_status"},
            {"type": "terms", "field": "severity", "name": "by_severity"},
        ]
        result = self.module._base_aggregate("PostAggregatesAlertsV2", specs=specs)

        self.mock_client.command.assert_called_once_with(
            "PostAggregatesAlertsV2", body=specs
        )
        # Response order is NOT preserved live (sent good,bad → got bad,good); each
        # result carries its own `name`, so callers identify results by name.
        self.assertEqual({r["name"] for r in result}, {"by_status", "by_severity"})

    def test_success_returns_resources_list_directly(self):
        """Aggregates have no meta.pagination, so return bare resources — no envelope."""
        buckets = [{"label": "new", "count": 12}, {"label": "closed", "count": 3}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "by_status", "buckets": buckets, "sum_other_doc_count": 0}
                ]
            },
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.assertIsInstance(result, list)
        self.assertEqual(
            result,
            [{"name": "by_status", "buckets": buckets, "sum_other_doc_count": 0}],
        )
        # Buckets key on `label`, not `key` — swagger's item schema omits `label`.
        self.assertEqual(result[0]["buckets"][0]["label"], "new")
        self.assertNotIn("results", result[0])
        self.assertNotIn("pagination", result[0])

    def test_http_200_with_body_errors_returns_error_not_empty_list(self):
        """Regression guard: a 200 carrying errors[] must not silently become [].

        Live, casemgmt + `date_histogram` returns HTTP 200 with
        {"errors":[{"code":400,"message":"invalid aggregate type"}],"resources":null}.
        `handle_api_response` only inspects the HTTP status, so without an explicit
        body-level check the real cause is discarded.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "errors": [{"code": 400, "message": "invalid aggregate type"}],
                "resources": None,
            },
        }

        result = self.module._base_aggregate(
            "AggregateCases",
            agg_type="date_histogram",
            field="created_timestamp",
            interval="day",
            error_message="Failed to aggregate cases",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to aggregate cases", result["error"])
        self.assertIn("invalid aggregate type", result["error"])

    def test_http_200_with_body_errors_missing_code_still_errors(self):
        """A body-level error with no usable `code` still surfaces as an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"errors": [{"message": "something is wrong"}], "resources": None},
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("something is wrong", result["error"])

    def test_http_error_returns_error_dict(self):
        """A real HTTP 4xx routes through handle_api_response as an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "invalid interval"}]},
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2",
            agg_type="date_histogram",
            field="created_timestamp",
            interval="1d",
            error_message="Failed to aggregate alerts",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to aggregate alerts", result["error"])

    def test_http_500_bogus_type_returns_error_dict(self):
        """A bogus `type` yields HTTP 500 live (not a clean 400); still an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "trace-id: abc123"}]},
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="not_a_real_type", field="status"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_empty_resources_returns_empty_list(self):
        """No aggregations returned is an empty list, not an error."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.assertEqual(result, [])

    def test_null_resources_on_clean_200_returns_empty_list(self):
        """`resources: null` with no errors[] is an empty result, not an error.

        Live trap: an invalid FQL filter or bogus `field` returns HTTP 200 with
        null buckets and no error — an empty result never proves the query was right.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": None},
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="bogus_field"
        )

        self.assertEqual(result, [])

    def test_empty_specs_list_is_a_caller_error(self):
        """`specs=[]` must not burn an API round trip on a zero-spec request.

        An empty list is falsy but not None, so it would otherwise slip past the
        `specs is None` guard and POST `body=[]`. Realistic upstream cause: a list
        comprehension that filtered down to nothing.
        """
        with self.assertRaises(ValueError):
            self.module._base_aggregate("PostAggregatesAlertsV2", specs=[])
        self.mock_client.command.assert_not_called()

    def test_missing_type_companion_short_circuits(self):
        """A spec missing its type's companion key never reaches the API.

        The API answers these with an opaque 500, so they are caught locally.
        """
        cases = [
            ({"type": "date_histogram", "field": "timestamp"}, "interval"),
            ({"type": "date_range", "field": "timestamp"}, "date_ranges"),
            ({"type": "range", "field": "severity"}, "ranges"),
        ]
        for spec, companion in cases:
            with self.subTest(agg_type=spec["type"]):
                self.mock_client.command.reset_mock()
                result = self.module._base_aggregate(
                    "PostAggregatesAlertsV2", specs=[spec]
                )
                self.assertIn("error", result)
                self.assertIn(companion, result["error"])
                self.mock_client.command.assert_not_called()

    def test_missing_companion_found_in_nested_specs(self):
        """The companion check recurses into `sub_aggregates` at any depth."""
        deep = {
            "type": "terms",
            "field": "status",
            "sub_aggregates": [
                {
                    "type": "terms",
                    "field": "product",
                    "sub_aggregates": [{"type": "range", "field": "severity"}],
                }
            ],
        }

        result = self.module._base_aggregate("PostAggregatesAlertsV2", specs=[deep])

        self.assertIn("error", result)
        self.assertIn("ranges", result["error"])
        self.mock_client.command.assert_not_called()

    def test_complete_companions_reach_the_api(self):
        """Supplying each companion key lets the request through untouched."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "ok", "buckets": []}]},
        }
        spec = {
            "type": "date_histogram",
            "field": "timestamp",
            "interval": "day",
            "sub_aggregates": [
                {"type": "range", "field": "severity", "ranges": [{"From": 0, "To": 50}]}
            ],
        }

        result = self.module._base_aggregate("PostAggregatesAlertsV2", specs=[spec])

        self.assertEqual(result[0]["name"], "ok")
        self.mock_client.command.assert_called_once()

    def test_malformed_nested_specs_do_not_crash_the_check(self):
        """Malformed `sub_aggregates` values reach the API instead of raising.

        The check inspects caller-supplied dicts whose values are untyped, so a
        non-dict entry must not turn into an AttributeError.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "ok", "buckets": []}]},
        }
        malformed = [
            "not-a-list",
            [123],
            [{"type": "terms", "field": "x", "sub_aggregates": "nope"}],
            [{"type": ["terms"], "field": "x"}],
            [{"type": {"a": 1}, "field": "x"}],
        ]
        for nested in malformed:
            with self.subTest(nested=nested):
                self.mock_client.command.reset_mock()
                result = self.module._base_aggregate(
                    "PostAggregatesAlertsV2",
                    specs=[{"type": "terms", "field": "status", "sub_aggregates": nested}],
                )
                self.assertEqual(result[0]["name"], "ok")
                self.mock_client.command.assert_called_once()

    def test_body_errors_with_no_status_code_does_not_crash(self):
        """A missing `status_code` skips the 2xx gate and still yields an error dict.

        `handle_api_response` already treats a None status as a failure; this
        confirms the new gate degrades into that path rather than raising.
        """
        self.mock_client.command.return_value = {
            "body": {"errors": [{"message": "no status at all"}], "resources": None}
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2", agg_type="terms", field="status"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_body_error_preserves_true_transport_status_in_details(self):
        """The error dict must report the REAL status (200), not a fabricated 400.

        `details` is the only artifact a client or log line sees. Stamping a
        synthetic 400 there would tell whoever is debugging that the transport
        returned 400 when it actually returned 200 — and would drag in
        `handle_api_response`'s 400 blurb about FQL syntax, which has nothing to
        do with an `invalid aggregate type`.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "errors": [
                    {"code": 400, "message": 'invalid aggregate type: "date_histogram"'}
                ],
                "resources": None,
            },
        }

        result = self.module._base_aggregate(
            "aggregates.slas.post.v1",
            agg_type="date_histogram",
            field="created_timestamp",
            interval="day",
            error_message="Failed to aggregate SLAs",
        )

        self.assertIn("error", result)
        # The real cause is named.
        self.assertIn('invalid aggregate type: "date_histogram"', result["error"])
        # No invented filter-syntax advice.
        self.assertNotIn("FQL uses", result["error"])
        # The true transport status survives for whoever is debugging.
        self.assertEqual(result["details"]["status_code"], 200)

    def test_http_403_keeps_status_and_scope_guidance(self):
        """A real 403 must NOT be re-stamped — that would strip the scope hint.

        The body-level-error check only exists for 2xx responses. A 403 also
        carries `errors[]`, so a blanket re-stamp to 400 would both mangle the
        message into FQL-syntax advice and bypass `handle_api_response`'s 403
        branch, which attaches `required_scopes` and a resolution. Downstream
        aggregate tasks rely on that hint to tell a genuine missing scope
        (`access denied, scope not permitted`) from the non-scope-fixable
        `authorization failed`.
        """
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"code": 403, "message": "access denied, scope not permitted"}]
            },
        }

        result = self.module._base_aggregate(
            "QueryDevicesByFilter", agg_type="terms", field="status"
        )

        self.assertIn("error", result)
        self.assertIn("access denied, scope not permitted", result["error"])
        # 403-specific handling survives.
        self.assertEqual(result["required_scopes"], ["Hosts:read"])
        self.assertIn("resolution", result)
        # And the message is not mislabeled as a filter-syntax problem.
        self.assertNotIn("FQL uses", result["error"])
        self.assertEqual(result["details"]["status_code"], 403)

    def test_resource_without_sum_other_doc_count_passes_through(self):
        """`sum_other_doc_count` is not universal — the SLA endpoint omits it.

        Live-verified on `aggregates.slas.post.v1`, whose resources carry only
        `name` and `buckets`. Nothing is normalized or back-filled here.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"name": "", "buckets": [{"label": "Corp SLA", "count": 1}]}
                ]
            },
        }

        result = self.module._base_aggregate(
            "aggregates.slas.post.v1", agg_type="terms", field="name"
        )

        self.assertEqual(set(result[0]), {"name", "buckets"})

    def test_date_histogram_bucket_label_is_epoch_millis(self):
        """date_histogram buckets carry an int `label` plus `key_as_string`.

        Live-verified on `PostAggregatesAlertsV2`: `label` is epoch milliseconds,
        not a display string, so callers must not assume `label` is a str.
        """
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "",
                        "buckets": [
                            {
                                "label": 1680566400000,
                                "key_as_string": "2023-04-04T00:00:00.000Z",
                                "count": 1,
                            }
                        ],
                    }
                ]
            },
        }

        result = self.module._base_aggregate(
            "PostAggregatesAlertsV2",
            agg_type="date_histogram",
            field="created_timestamp",
            interval="day",
        )

        bucket = result[0]["buckets"][0]
        self.assertIsInstance(bucket["label"], int)
        self.assertEqual(bucket["key_as_string"], "2023-04-04T00:00:00.000Z")

    def test_no_specs_and_no_kwargs_is_a_caller_error(self):
        """Calling with neither `specs` nor spec kwargs fails before any API call."""
        with self.assertRaises(ValueError):
            self.module._base_aggregate("PostAggregatesAlertsV2")
        self.mock_client.command.assert_not_called()

    def test_specs_and_spec_kwargs_together_is_a_caller_error(self):
        """Passing both `specs` and single-spec kwargs is ambiguous — fail loudly."""
        with self.assertRaises(ValueError):
            self.module._base_aggregate(
                "PostAggregatesAlertsV2",
                specs=[{"type": "terms", "field": "status"}],
                agg_type="terms",
                field="severity",
            )
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()

