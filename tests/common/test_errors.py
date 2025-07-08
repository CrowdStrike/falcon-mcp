"""
Tests for the error handling utilities.
"""

import unittest
from unittest.mock import patch

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS, get_required_scopes
from falcon_mcp.common.errors import (
    FalconError,
    AuthenticationError,
    APIError,
    is_success_response,
    handle_api_response,
    _format_error_response,
)


class TestErrorClasses(unittest.TestCase):
    """Test cases for the error classes."""

    def test_falcon_error(self):
        """Test FalconError class."""
        error = FalconError("Test error")
        self.assertEqual(str(error), "Test error")

    def test_authentication_error(self):
        """Test AuthenticationError class."""
        error = AuthenticationError("Authentication failed")
        self.assertEqual(str(error), "Authentication failed")
        self.assertIsInstance(error, FalconError)

    def test_api_error(self):
        """Test APIError class."""
        error = APIError(
            "API request failed",
            status_code=403,
            body={"errors": [{"message": "Access denied"}]},
            operation="TestOperation",
        )
        self.assertEqual(str(error), "API request failed")
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.body, {"errors": [{"message": "Access denied"}]})
        self.assertEqual(error.operation, "TestOperation")
        self.assertIsInstance(error, FalconError)


class TestErrorUtils(unittest.TestCase):
    """Test cases for the error utility functions."""

    def test_is_success_response(self):
        """Test is_success_response function."""
        # Success response
        self.assertTrue(is_success_response({"status_code": 200}))

        # Error responses
        self.assertFalse(is_success_response({"status_code": 400}))
        self.assertFalse(is_success_response({"status_code": 403}))
        self.assertFalse(is_success_response({"status_code": 500}))
        self.assertFalse(is_success_response({}))  # Missing status_code

    def test_get_required_scopes(self):
        """Test get_required_scopes function."""
        # Known operation
        self.assertEqual(get_required_scopes("GetQueriesAlertsV2"), ["alerts:read"])

        # Unknown operation
        self.assertEqual(get_required_scopes("UnknownOperation"), [])

    @patch("falcon_mcp.common.errors.logger")
    def test_format_error_response(self, mock_logger):
        """Test format_error_response function."""
        # Basic error
        response = _format_error_response("Test error")
        self.assertEqual(response, {"error": "Test error"})
        mock_logger.error.assert_called_with("Error: %s", "Test error")

        # Error with details
        details = {"status_code": 400, "body": {"errors": [{"message": "Bad request"}]}}
        response = _format_error_response("Test error", details=details)
        self.assertEqual(response["error"], "Test error")
        self.assertEqual(response["details"], details)

        # Permission error with operation
        details = {"status_code": 403, "body": {"errors": [{"message": "Access denied"}]}}
        response = _format_error_response(
            "Permission denied", details=details, operation="GetQueriesAlertsV2"
        )
        self.assertEqual(response["error"], "Permission denied")
        self.assertEqual(response["details"], details)
        self.assertEqual(response["required_scopes"], ["alerts:read"])
        self.assertIn("resolution", response)
        self.assertIn("alerts:read", response["resolution"])

    def test_handle_api_response_success(self):
        """Test handle_api_response function with success response."""
        # Success response with resources
        response = {
            "status_code": 200,
            "body": {"resources": [{"id": "test", "name": "Test Resource"}]},
        }
        result = handle_api_response(response, "TestOperation")
        self.assertEqual(result, [{"id": "test", "name": "Test Resource"}])

        # Success response with empty resources
        response = {"status_code": 200, "body": {"resources": []}}
        result = handle_api_response(response, "TestOperation")
        self.assertEqual(result, [])

        # Success response with empty resources and default
        response = {"status_code": 200, "body": {"resources": []}}
        result = handle_api_response(response, "TestOperation", default_result={"default": True})
        self.assertEqual(result, {"default": True})

    def test_handle_api_response_error(self):
        """Test handle_api_response function with error response."""
        # Error response
        response = {"status_code": 400, "body": {"errors": [{"message": "Bad request"}]}}
        result = handle_api_response(response, "TestOperation", error_message="Test failed")
        self.assertIn("error", result)
        self.assertIn("Test failed", result["error"])
        self.assertEqual(result["details"], response)

        # Permission error
        response = {"status_code": 403, "body": {"errors": [{"message": "Access denied"}]}}
        # Add a test operation to API_SCOPE_REQUIREMENTS
        original_scopes = API_SCOPE_REQUIREMENTS.copy()
        API_SCOPE_REQUIREMENTS["TestOperation"] = ["test:read"]

        try:
            result = handle_api_response(
                response, "TestOperation", error_message="Permission denied"
            )
            self.assertIn("error", result)
            self.assertIn("Permission denied", result["error"])
            self.assertIn("Required scopes: test:read", result["error"])
            self.assertEqual(result["details"], response)
        finally:
            # Restore original API_SCOPE_REQUIREMENTS
            API_SCOPE_REQUIREMENTS.clear()
            API_SCOPE_REQUIREMENTS.update(original_scopes)


if __name__ == "__main__":
    unittest.main()
