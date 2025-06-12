"""
Tests for the Detections module.
"""
import unittest
from unittest.mock import MagicMock

from mcp.server import FastMCP

from src.client import FalconClient
from src.modules.detections import DetectionsModule


class TestDetectionsModule(unittest.TestCase):
    """Test cases for the Detections module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock client
        self.mock_client = MagicMock(spec=FalconClient)

        # Create the module
        self.module = DetectionsModule(self.mock_client)

        # Create a mock server
        self.mock_server = MagicMock(spec=FastMCP)

    def test_register_tools(self):
        """Test registering tools with the server."""
        # Call register_tools
        self.module.register_tools(self.mock_server)

        # Verify that add_tool was called for each tool
        self.assertEqual(self.mock_server.add_tool.call_count, 3)

        # Get the tool names that were registered
        registered_tools = [
            call.kwargs['name']
            for call in self.mock_server.add_tool.call_args_list
        ]

        # Verify that all expected tools were registered
        expected_tools = [
            "search_detections",
            "get_detection_details",
            "get_detection_count"
        ]
        for tool in expected_tools:
            self.assertIn(tool, registered_tools)

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
                "resources": []  # Empty resources for GetDetectSummaries
            }
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_detections
        result = self.module.search_detections(query="test query", limit=10)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "QueryDetects",
            parameters={"filter": "test query", "limit": 10}
        )
        self.mock_client.command.assert_any_call(
            "GetDetectSummaries",
            body={"ids": ["detection1", "detection2"]}
        )

        # Verify result
        self.assertEqual(result, [])  # Empty list because GetDetectSummaries returned empty resources

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
        result = self.module.search_detections(query="test query", limit=10)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "QueryDetects",
            parameters={"filter": "test query", "limit": 10}
        )
        self.mock_client.command.assert_any_call(
            "GetDetectSummaries",
            body={"ids": ["detection1", "detection2"]}
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
        result = self.module.search_detections(query="invalid query")

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
        result = self.module.get_detection_details("detection1")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetDetectSummaries",
            body={"ids": ["detection1"]}
        )

        # Verify result
        expected_result = {"id": "detection1", "name": "Test Detection 1"}
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
        result = self.module.get_detection_details("nonexistent")

        # Verify result contains error
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Detection not found")

    def test_get_detection_count(self):
        """Test getting detection count."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": ["detection1", "detection2", "detection3"]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call get_detection_count
        result = self.module.get_detection_count(query="test query")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryDetects",
            parameters={"filter": "test query"}
        )

        # Verify result
        expected_result = {"count": 3}
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
