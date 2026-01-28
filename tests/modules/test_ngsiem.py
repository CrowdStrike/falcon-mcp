"""
Tests for the NGSIEM module.
"""

import tempfile
from unittest.mock import patch

from falcon_mcp.modules.ngsiem import NGSIEMModule
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NGSIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_start_ngsiem_search",
            "falcon_get_ngsiem_event_schema",
            "falcon_search_ngsiem_events",
            "falcon_list_ngsiem_event_tables",
            "falcon_list_ngsiem_event_fields",
            "falcon_upload_ngsiem_lookup_file",
            "falcon_get_ngsiem_lookup_file",
            "falcon_get_ngsiem_lookup_file_from_package",
            "falcon_get_ngsiem_lookup_file_from_package_with_namespace",
            "falcon_get_ngsiem_search_status",
            "falcon_get_ngsiem_search_results",
            "falcon_stop_ngsiem_search",
            "falcon_search_ngsiem_and_wait",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_ngsiem_query_functions_guide",
            "falcon_ngsiem_event_fields_guide",
            "falcon_ngsiem_event_ontology_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_start_ngsiem_search_success(self):
        """Test starting NGSIEM search with successful response."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "abc123"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.start_ngsiem_search(
            repository="events",
            query_string="#event_simpleName=EndOfProcess",
            start="1d",
        )

        self.mock_client.command.assert_called_once_with(
            "StartSearchV1",
            repository="events",
            body={"queryString": "#event_simpleName=EndOfProcess", "start": "1d"},
        )
        self.assertEqual(result, [{"id": "abc123"}])

    def test_start_ngsiem_search_error(self):
        """Test starting NGSIEM search with API error."""
        mock_response = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.start_ngsiem_search(repository="events", query_string="test")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_get_ngsiem_search_status_success(self):
        """Test getting NGSIEM search status with successful response."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "s1", "status": "DONE"}]},
        }
        self.mock_client.command.return_value = mock_response

        result = self.module.get_ngsiem_search_status(
            repository="events",
            search_id="s1",
        )

        self.mock_client.command.assert_called_once_with(
            "GetSearchStatusV1",
            repository="events",
            search_id="s1",
        )
        self.assertEqual(result, [{"id": "s1", "status": "DONE"}])

    def test_upload_ngsiem_lookup_file_success(self):
        """Test uploading NGSIEM lookup file with successful response."""
        mock_response = {
            "status_code": 200,
            "body": {"resources": [{"filename": "lookup.csv"}]},
        }
        self.mock_client.command.return_value = mock_response

        with tempfile.NamedTemporaryFile("w+b") as temp_file:
            temp_file.write(b"col1,col2\n1,2\n")
            temp_file.flush()
            result = self.module.upload_ngsiem_lookup_file(
                repository="events",
                lookup_file_path=temp_file.name,
            )

        self.assertEqual(result, [{"filename": "lookup.csv"}])
        self.assertEqual(self.mock_client.command.call_args[0][0], "UploadLookupV1")

    def test_list_ngsiem_event_tables(self):
        """Test listing NGSIEM event tables from ontology cache."""
        stub_ontology = {
            "endofprocess": {
                "event_simpleName": "EndOfProcess",
                "description": "Process completion event",
                "platforms": ["windows"],
                "fields": [{"name": "TargetProcessId"}],
            },
            "processrollup2": {
                "event_simpleName": "ProcessRollup2",
                "description": "Process rollup event",
                "platforms": ["linux"],
                "fields": [{"name": "FileName"}],
            },
        }

        with patch.object(self.module, "_load_ngsiem_ontology", return_value=stub_ontology):
            results = self.module.list_ngsiem_event_tables(platform="windows")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["event_simpleName"], "EndOfProcess")
        self.assertIn("description_text", results[0])

    def test_list_ngsiem_event_fields(self):
        """Test listing fields for multiple NGSIEM events."""
        stub_ontology = {
            "endofprocess": {
                "event_simpleName": "EndOfProcess",
                "fields": [{"name": "TargetProcessId"}],
            }
        }

        with patch.object(self.module, "_load_ngsiem_ontology", return_value=stub_ontology):
            results = self.module.list_ngsiem_event_fields([
                "EndOfProcess",
                "MissingEvent",
            ])

        self.assertEqual(results[0]["event_simpleName"], "EndOfProcess")
        self.assertEqual(results[0]["fields"], ["TargetProcessId"])
        self.assertEqual(results[1]["event_simpleName"], "MissingEvent")
        self.assertIn("error", results[1])
