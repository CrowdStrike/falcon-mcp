"""
Tests for the Intel module.
"""
import unittest

from falcon_mcp.modules.intel import IntelModule
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
            "falcon_search_actors_fql_filter_guide",
            "falcon_search_indicators",
            "falcon_search_indicators_fql_filter_guide",
            "falcon_search_reports",
            "falcon_search_reports_fql_filter_guide",
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
        result = self.module.query_actor_entities(
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
        result = self.module.query_actor_entities()

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
        results = self.module.query_actor_entities(filter="invalid query")
        result = results[0]

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
        # Check that the error message starts with the expected prefix
        self.assertTrue(result["error"].startswith("Failed to search actors"))

    def test_query_indicator_entities_success(self):
        """Test querying indicator entities with successful response."""
        # Setup mock response with sample indicators
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "indicator1", "indicator": "malicious.com", "type": "domain"},
                    {"id": "indicator2", "indicator": "192.168.1.1", "type": "ip_address"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_indicator_entities with test parameters
        result = self.module.query_indicator_entities(
            filter="type:'domain'",
            limit=100,
            offset=0,
            sort="published_date.desc",
            q="malicious",
            include_deleted=True,
            include_relations=True
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryIntelIndicatorEntities",
            parameters={
                "filter": "type:'domain'",
                "limit": 100,
                "offset": 0,
                "sort": "published_date.desc",
                "q": "malicious",
                "include_deleted": True,
                "include_relations": True
            }
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "indicator1")
        self.assertEqual(result[1]["id"], "indicator2")

    def test_query_indicator_entities_empty_response(self):
        """Test querying indicator entities with empty response."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_indicator_entities
        result = self.module.query_indicator_entities()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "QueryIntelIndicatorEntities")

        # Verify result is an empty list
        self.assertEqual(result, [])

    def test_query_indicator_entities_error(self):
        """Test querying indicator entities with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid query"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_indicator_entities
        result = self.module.query_indicator_entities(filter="invalid query")

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("details", result[0])
        # Check that the error message starts with the expected prefix
        self.assertTrue(result[0]["error"].startswith("Failed to search indicators"))

    def test_query_report_entities_success(self):
        """Test querying report entities with successful response."""
        # Setup mock response with sample reports
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "report1", "name": "Report 1", "description": "Description 1"},
                    {"id": "report2", "name": "Report 2", "description": "Description 2"}
                ]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_report_entities with test parameters
        result = self.module.query_report_entities(
            filter="name:'Report*'",
            limit=100,
            offset=0,
            sort="created_date.desc",
            q="test",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryIntelReportEntities",
            parameters={
                "filter": "name:'Report*'",
                "limit": 100,
                "offset": 0,
                "sort": "created_date.desc",
                "q": "test",
            }
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "report1")
        self.assertEqual(result[1]["id"], "report2")

    def test_query_report_entities_empty_response(self):
        """Test querying report entities with empty response."""
        # Setup mock response with empty resources
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": []
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_report_entities
        result = self.module.query_report_entities()

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "QueryIntelReportEntities")

        # Verify result is an empty list
        self.assertEqual(result, [])

    def test_query_report_entities_error(self):
        """Test querying report entities with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {
                "errors": [{"message": "Invalid query"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call query_report_entities
        result = self.module.query_report_entities(filter="invalid query")

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("details", result[0])
        # Check that the error message starts with the expected prefix
        self.assertTrue(result[0]["error"].startswith("Failed to search reports"))


if __name__ == '__main__':
    unittest.main()
