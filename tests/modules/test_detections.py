"""
Tests for the Detections module.
"""
import unittest

from src.modules.detections import DetectionsModule
from tests.modules.utils.test_modules import TestModules


class TestDetectionsModule(TestModules):
    """Test cases for the Detections module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DetectionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_detections",
            "falcon_search_detections_fql_filter_guide",
            "falcon_get_detection_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_search_detections(self):
        """Test searching for detections."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": []  # Empty resources for PostEntitiesAlertsV2
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(filter="test query", limit=10, include_hidden=True)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"], "include_hidden": True}
        )

        # Verify result
        self.assertEqual(result, [])  # Empty list because PostEntitiesAlertsV2 returned empty resources

    def test_search_detections_with_details(self):
        """Test searching for detections with details."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "detection1", "name": "Test Detection 1"},
                    {"id": "detection2", "name": "Test Detection 2"}
                ]
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(filter="test query", limit=10, include_hidden=True)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to GetQueriesAlertsV2 with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "test query")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"], "include_hidden": True}
        )

        # Verify result
        expected_result = [
            {"id": "detection1", "name": "Test Detection 1"},
            {"id": "detection2", "name": "Test Detection 2"}
        ]
        self.assertEqual(result, expected_result)

    def test_search_detections_error(self):
        """Test searching for detections with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid query"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call search_detections
        result = self.module.search_detections(filter="invalid query")

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("details", result[0])

    def test_get_detection_details(self):
        """Test getting detection details."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "detection1", "name": "Test Detection 1"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["detection1"], include_hidden=True)

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"], "include_hidden": True}
        )

        # Verify result - handle_api_response returns a list of resources
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)

    def test_get_detection_details_not_found(self):
        """Test getting detection details for non-existent detection."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details
        result = self.module.get_detection_details(["nonexistent"])

        # For empty resources, handle_api_response returns the default_result (empty list)
        # We should check that the result is empty
        self.assertEqual(result, [])

    def test_search_detections_include_hidden_false(self):
        """Test searching for detections with include_hidden=False."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2"]
            }
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "detection1", "name": "Test Detection 1"}
                ]
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections with include_hidden=False
        result = self.module.search_detections(filter="test query", include_hidden=False)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the second call includes include_hidden=False
        self.mock_client.command.assert_any_call(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1", "detection2"], "include_hidden": False}
        )

        # Verify result
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)

    def test_get_detection_details_include_hidden_false(self):
        """Test getting detection details with include_hidden=False."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "detection1", "name": "Test Detection 1"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_details with include_hidden=False
        result = self.module.get_detection_details(["detection1"], include_hidden=False)

        # Verify client command was called correctly with include_hidden=False
        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["detection1"], "include_hidden": False}
        )

        # Verify result
        expected_result = [{"id": "detection1", "name": "Test Detection 1"}]
        self.assertEqual(result, expected_result)



if __name__ == '__main__':
    unittest.main()
