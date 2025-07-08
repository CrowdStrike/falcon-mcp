"""
Tests for the Incidents module.
"""
import unittest

from falcon_mcp.modules.incidents import IncidentsModule
from tests.modules.utils.test_modules import TestModules


class TestIncidentsModule(TestModules):
    """Test cases for the Incidents module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IncidentsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_show_crowd_score",
            "falcon_show_crowd_score_fql_filter_guide",
            "falcon_get_incident_details",
            "falcon_search_incidents",
            "falcon_search_incidents_fql_filter_guide",
            "falcon_get_behavior_details",
            "falcon_search_behaviors",
            "falcon_search_behaviors_fql_filter_guide",
        ]
        self.assert_tools_registered(expected_tools)

    def test_crowd_score(self):
        """Test querying CrowdScore with successful response."""
        # Setup mock response with sample scores
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "score1", "score": 50, "adjusted_score": 60},
                    {"id": "score2", "score": 70, "adjusted_score": 80}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call crowd_score with test parameters
        result = self.module.show_crowd_score(filter="test filter", limit=100, offset=0, sort="modified_timestamp.desc")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "CrowdScore",
            parameters={
                "filter": "test filter",
                "limit": 100,
                "offset": 0,
                "sort": "modified_timestamp.desc"
            }
        )

        # Verify result contains expected values
        self.assertEqual(result["average_score"], 60)  # (50 + 70) / 2
        self.assertEqual(result["average_adjusted_score"], 70)  # (60 + 80) / 2
        self.assertEqual(len(result["scores"]), 2)
        self.assertEqual(result["scores"][0]["id"], "score1")
        self.assertEqual(result["scores"][1]["id"], "score2")

    def test_crowd_score_empty_response(self):
        """Test querying CrowdScore with empty response."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call crowd_score
        result = self.module.show_crowd_score()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "CrowdScore")

        # Verify result contains expected default values
        self.assertEqual(result["average_score"], 0)
        self.assertEqual(result["average_adjusted_score"], 0)
        self.assertEqual(result["scores"], [])

    def test_crowd_score_error(self):
        """Test querying CrowdScore with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid query"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call crowd_score
        result = self.module.show_crowd_score(filter="invalid query")

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(result["error"].startswith("Failed to perform operation"))

    def test_crowd_score_with_default_parameters_and_rounding(self):
        """Test querying CrowdScore with default parameters and rounding"""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "score1", "score": 30, "adjusted_score": 40},
                    {"id": "score1", "score": 31, "adjusted_score": 41},
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call crowd_score with no parameters (using defaults)
        result = self.module.show_crowd_score()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "CrowdScore")

        # Verify result
        self.assertEqual(result["average_score"], 30)
        self.assertEqual(result["average_adjusted_score"], 40)


if __name__ == '__main__':
    unittest.main()
