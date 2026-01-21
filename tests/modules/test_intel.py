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
            "falcon_search_indicators",
            "falcon_search_reports",
            "falcon_get_mitre_report",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_actors_fql_guide",
            "falcon_search_indicators_fql_guide",
            "falcon_search_reports_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_actors_success(self):
        """Test searching actors with successful response."""
        # Setup mock response with sample actors
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "actor1", "name": "Actor 1", "description": "Description 1"},
                    {"id": "actor2", "name": "Actor 2", "description": "Description 2"},
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call search_actors with test parameters
        result = self.module.query_actor_entities(
            filter="name:'Actor*'",
            limit=100,
            offset=0,
            sort="name.asc",
            q="test",
        )

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "QueryIntelActorEntities",
            parameters={
                "filter": "name:'Actor*'",
                "limit": 100,
                "offset": 0,
                "sort": "name.asc",
                "q": "test",
            },
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "actor1")
        self.assertEqual(result[1]["id"], "actor2")

    def test_search_actors_empty_response(self):
        """Test searching actors with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
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
            "body": {"errors": [{"message": "Invalid query"}]},
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
                    {
                        "id": "indicator1",
                        "indicator": "malicious.com",
                        "type": "domain",
                    },
                    {
                        "id": "indicator2",
                        "indicator": "192.168.1.1",
                        "type": "ip_address",
                    },
                ]
            },
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
            include_relations=True,
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
                "include_relations": True,
            },
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "indicator1")
        self.assertEqual(result[1]["id"], "indicator2")

    def test_query_indicator_entities_empty_response(self):
        """Test querying indicator entities with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
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
            "body": {"errors": [{"message": "Invalid query"}]},
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
                    {
                        "id": "report1",
                        "name": "Report 1",
                        "description": "Description 1",
                    },
                    {
                        "id": "report2",
                        "name": "Report 2",
                        "description": "Description 2",
                    },
                ]
            },
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
            },
        )

        # Verify result contains expected values
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "report1")
        self.assertEqual(result[1]["id"], "report2")

    def test_query_report_entities_empty_response(self):
        """Test querying report entities with empty response."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
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
            "body": {"errors": [{"message": "Invalid query"}]},
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

    def test_get_mitre_report_success(self):
        """Test getting MITRE report with successful response.

        FalconPy returns raw bytes directly for binary endpoints like GetMitreReport.
        """
        # Setup mock response with fake MITRE JSON data as binary content
        fake_json_content = '''[
            {
                "id": "my_id",
                "tactic_id": "my_tactic_id",
                "tactic_name": "Fake Tactic",
                "technique_id": "technique_id",
                "technique_name": "Fake Technique",
                "reports": ["FAKE001"],
                "observables": ["This is fake observable data for testing purposes."]
            },
            {
                "id": "my_id2",
                "tactic_id": "my_tactic_id2",
                "tactic_name": "Another Fake Tactic",
                "technique_id": "technique_id2",
                "technique_name": "Another Fake Technique",
                "reports": ["FAKE002"],
                "observables": ["This is another fake observable for testing."]
            }
        ]'''

        # FalconPy returns raw bytes directly for binary endpoints
        self.mock_client.command.return_value = fake_json_content.encode('utf-8')

        # Call get_mitre_report with numeric actor ID
        result = self.module.get_mitre_report(actor="123456", format="json")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetMitreReport",
            parameters={
                "actor_id": "123456",
                "format": "json",
            },
        )

        # Verify result is decoded string content
        self.assertIsInstance(result, str)
        self.assertIn("my_id", result)
        self.assertIn("Fake Tactic", result)
        self.assertIn("Fake Technique", result)
        self.assertIn("FAKE001", result)
        self.assertIn("technique_id2", result)

    def test_get_mitre_report_csv_format(self):
        """Test getting MITRE report with CSV format.

        FalconPy returns raw bytes directly for binary endpoints like GetMitreReport.
        """
        # Setup mock response for CSV format using fake CSV structure
        fake_csv = (
            "id,tactic_id,tactic_name,technique_id,technique_name,reports,observables\n"
            "fake_id1,fake_tactic_id1,Fake Tactic,fake_technique_id1,Fake Technique,FAKE001,"
            "This is fake observable data for CSV testing.\n"
            "fake_id2,fake_tactic_id2,Another Fake Tactic,fake_technique_id2,Another Fake Technique,"
            "FAKE002,This is another fake observable for CSV testing."
        )
        # FalconPy returns raw bytes directly for binary endpoints
        self.mock_client.command.return_value = fake_csv.encode('utf-8')

        # Call get_mitre_report with CSV format
        result = self.module.get_mitre_report(actor="123456", format="csv")

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "GetMitreReport",
            parameters={
                "actor_id": "123456",
                "format": "csv",
            },
        )

        # Verify result is decoded CSV string content
        self.assertIsInstance(result, str)
        self.assertIn("fake_id1", result)
        self.assertIn("Fake Tactic", result)
        self.assertIn("fake_technique_id2", result)

    def test_get_mitre_report_error(self):
        """Test getting MITRE report with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 404,
            "body": {"errors": [{"message": "Actor not found"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_mitre_report
        result = self.module.get_mitre_report(actor="invalid_id", format="json")

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        # The error structure includes details from the failed search
        self.assertIn("details", result[0])

    def test_get_mitre_report_empty_response(self):
        """Test getting MITRE report with empty response.

        FalconPy returns raw bytes directly for binary endpoints like GetMitreReport.
        """
        # FalconPy returns raw bytes directly for binary endpoints
        self.mock_client.command.return_value = b""

        # Call get_mitre_report
        result = self.module.get_mitre_report(actor="123456", format="json")

        # Verify client command was called with the correct operation
        self.assertEqual(self.mock_client.command.call_count, 1)
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "GetMitreReport")

        # Verify result is empty string
        self.assertEqual(result, "")

    def test_get_mitre_report_default_format(self):
        """Test that default format is JSON when not specified.

        FalconPy returns raw bytes directly for binary endpoints like GetMitreReport.
        """
        # Setup mock response with binary content
        fake_json_content = '{"actor_id": "123456", "format": "JSON"}'
        # FalconPy returns raw bytes directly for binary endpoints
        self.mock_client.command.return_value = fake_json_content.encode('utf-8')

        # Call get_mitre_report without format parameter - should use default json
        self.module.get_mitre_report(actor="123456", format="json")

        # Verify the API call was made with json as the default format
        self.mock_client.command.assert_called_once_with(
            "GetMitreReport",
            parameters={
                "actor_id": "123456",
                "format": "json",  # Should default to json
            },
        )

    def test_get_mitre_report_by_actor_name(self):
        """Test getting MITRE report using actor name (automatically resolves to ID).

        FalconPy returns raw bytes directly for binary endpoints like GetMitreReport,
        but returns dict for standard endpoints like QueryIntelActorEntities.
        """
        # Setup mock response for actor search (standard dict response)
        search_mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "789012",
                        "name": "FAKE BEAR",
                        "short_description": "Fake test actor",
                        "animal_classifier": "BEAR",
                    }
                ]
            },
        }

        # Setup mock response for MITRE report (raw bytes)
        fake_json_content = '''[
            {
                "id": "fake_id_1",
                "tactic_id": "fake_tactic_001",
                "tactic_name": "Fake Tactic",
                "technique_id": "fake_technique_001",
                "technique_name": "Fake Technique",
                "reports": ["FAKE001"],
                "observables": ["This is fake observable data for testing."]
            }
        ]'''

        # Configure mock to return different responses for different operations
        def mock_command_side_effect(operation, **_):
            if operation == "QueryIntelActorEntities":
                return search_mock_response
            elif operation == "GetMitreReport":
                # FalconPy returns raw bytes directly for binary endpoints
                return fake_json_content.encode('utf-8')
            return {"status_code": 404, "body": {"errors": [{"message": "Unknown operation"}]}}

        self.mock_client.command.side_effect = mock_command_side_effect

        # Call get_mitre_report with actor name
        result = self.module.get_mitre_report(actor="FAKE BEAR", format="json")

        # Verify both API calls were made
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Verify first call was actor search
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryIntelActorEntities")
        self.assertIn("name:'FAKE BEAR'", first_call[1]["parameters"]["filter"])
        self.assertEqual(first_call[1]["parameters"]["limit"], 1)

        # Verify second call was MITRE report with resolved ID
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "GetMitreReport")
        self.assertEqual(second_call[1]["parameters"]["actor_id"], "789012")
        self.assertEqual(second_call[1]["parameters"]["format"], "json")

        # Verify result is decoded JSON string content
        self.assertIsInstance(result, str)
        self.assertIn("fake_id_1", result)
        self.assertIn("Fake Tactic", result)
        self.assertIn("fake_technique_001", result)

    def test_get_mitre_report_actor_name_not_found(self):
        """Test getting MITRE report when actor name is not found."""
        # Setup mock response for empty actor search
        search_mock_response = {
            "status_code": 200,
            "body": {"resources": []}
        }

        self.mock_client.command.return_value = search_mock_response

        # Call get_mitre_report with non-existent actor name
        result = self.module.get_mitre_report(actor="NONEXISTENT ACTOR", format="json")

        # Verify only one API call was made (actor search)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify it was an actor search
        call_args = self.mock_client.command.call_args
        self.assertEqual(call_args[0][0], "QueryIntelActorEntities")
        self.assertIn("name:'NONEXISTENT ACTOR'", call_args[1]["parameters"]["filter"])

        # Verify result contains error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("Actor not found", result[0]["error"])
        self.assertIn("NONEXISTENT ACTOR", result[0]["message"])

    def test_get_mitre_report_actor_search_error(self):
        """Test getting MITRE report when actor search returns an error."""
        # Setup mock response for actor search error
        search_mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid search query"}]}
        }

        self.mock_client.command.return_value = search_mock_response

        # Call get_mitre_report with actor name
        result = self.module.get_mitre_report(actor="FAKE ACTOR", format="json")

        # Verify only one API call was made (actor search)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify result contains the search error
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
