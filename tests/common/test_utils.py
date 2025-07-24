"""
Tests for the utility functions.
"""
import unittest
from unittest.mock import patch

from falcon_mcp.common.utils import (
    extract_first_resource,
    extract_resources,
    filter_none_values,
    prepare_api_parameters,
)


class TestUtilFunctions(unittest.TestCase):
    """Test cases for the utility functions."""

    def test_filter_none_values(self):
        """Test filter_none_values function."""
        # Dictionary with None values
        data = {
            "key1": "value1",
            "key2": None,
            "key3": 0,
            "key4": False,
            "key5": "",
            "key6": None
        }

        filtered = filter_none_values(data)

        # Verify None values were removed
        self.assertEqual(filtered, {
            "key1": "value1",
            "key3": 0,
            "key4": False,
            "key5": ""
        })

        # Empty dictionary
        self.assertEqual(filter_none_values({}), {})

        # Dictionary without None values
        data = {"key1": "value1", "key2": 2}
        self.assertEqual(filter_none_values(data), data)

    def test_prepare_api_parameters(self):
        """Test prepare_api_parameters function."""
        # Parameters with None values
        params = {
            "filter": "name:test",
            "limit": 100,
            "offset": None,
            "sort": None
        }

        prepared = prepare_api_parameters(params)

        # Verify None values were removed
        self.assertEqual(prepared, {
            "filter": "name:test",
            "limit": 100
        })

        # Empty parameters
        self.assertEqual(prepare_api_parameters({}), {})

        # Parameters without None values
        params = {"filter": "name:test", "limit": 100}
        self.assertEqual(prepare_api_parameters(params), params)

    def test_extract_resources(self):
        """Test extract_resources function."""
        # Success response with resources
        response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"}
                ]
            }
        }

        resources = extract_resources(response)

        # Verify resources were extracted
        self.assertEqual(resources, [
            {"id": "resource1", "name": "Resource 1"},
            {"id": "resource2", "name": "Resource 2"}
        ])

        # Success response with empty resources
        response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }

        resources = extract_resources(response)

        # Verify empty list was returned
        self.assertEqual(resources, [])

        # Success response with empty resources and default
        default = [{"id": "default", "name": "Default Resource"}]
        resources = extract_resources(response, default=default)

        # Verify default was returned
        self.assertEqual(resources, default)

        # Error response
        response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Bad request"}]
            }
        }

        resources = extract_resources(response)

        # Verify empty list was returned
        self.assertEqual(resources, [])

        # Error response with default
        resources = extract_resources(response, default=default)

        # Verify default was returned
        self.assertEqual(resources, default)

    @patch('falcon_mcp.common.utils._format_error_response')
    def test_extract_first_resource(self, mock_format_error):
        """Test extract_first_resource function."""
        # Mock format_error_response
        mock_format_error.return_value = {"error": "Resource not found"}

        # Success response with resources
        response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"}
                ]
            }
        }

        resource = extract_first_resource(response, "TestOperation")

        # Verify first resource was returned
        self.assertEqual(resource, {"id": "resource1", "name": "Resource 1"})

        # Success response with empty resources
        response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }

        resource = extract_first_resource(response, "TestOperation", not_found_error="Custom error")

        # Verify error response was returned
        mock_format_error.assert_called_with("Custom error", operation="TestOperation")
        self.assertEqual(resource, {"error": "Resource not found"})

        # Error response
        response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Bad request"}]
            }
        }

        resource = extract_first_resource(response, "TestOperation")

        # Verify error response was returned
        mock_format_error.assert_called_with("Resource not found", operation="TestOperation")
        self.assertEqual(resource, {"error": "Resource not found"})


if __name__ == '__main__':
    unittest.main()
