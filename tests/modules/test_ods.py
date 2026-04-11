"""
Tests for the ODS module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.ods import ODSModule
from tests.modules.utils.test_modules import TestModules


class TestODSModule(TestModules):
    """Test cases for the ODS module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ODSModule)

    def test_register_tools(self):
        """Test registering ODS tools."""
        expected_tools = [
            "falcon_search_ods_scans",
            "falcon_get_ods_scan_details",
            "falcon_search_ods_scan_hosts",
            "falcon_get_ods_scan_host_details",
            "falcon_launch_ods_scan",
            "falcon_cancel_ods_scans",
            "falcon_search_ods_scheduled_scans",
            "falcon_get_ods_scheduled_scan_details",
            "falcon_schedule_ods_scan",
            "falcon_delete_ods_scheduled_scans",
            "falcon_search_ods_malicious_files",
            "falcon_get_ods_malicious_file_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering ODS resources."""
        expected_resources = [
            "falcon_search_ods_scans_fql_guide",
            "falcon_search_ods_scan_hosts_fql_guide",
            "falcon_search_ods_scheduled_scans_fql_guide",
            "falcon_search_ods_malicious_files_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_read_and_mutating_annotations(self):
        """Test ODS tool annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_ods_scans", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_ods_scan_details", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_ods_scan_hosts", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_ods_scan_host_details", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_ods_scheduled_scans", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_get_ods_scheduled_scan_details",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations("falcon_search_ods_malicious_files", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_get_ods_malicious_file_details",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_launch_ods_scan",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_cancel_ods_scans",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_schedule_ods_scan",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_ods_scheduled_scans",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_search_ods_scans_returns_details(self):
        """Test scan search flow returns full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["scan-1", "scan-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "scan-1", "status": "done"},
                    {"id": "scan-2", "status": "running"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_ods_scans(
            filter="status:'done'",
            limit=20,
            offset=5,
            sort="created_on|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(
            self.mock_client.command.call_args_list[0][1]["parameters"],
            {
                "filter": "status:'done'",
                "limit": 20,
                "offset": 5,
                "sort": "created_on|desc",
            },
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["parameters"],
            {"ids": ["scan-1", "scan-2"]},
        )
        self.assertEqual(result[0]["id"], "scan-1")

    def test_search_ods_scans_error_returns_fql_guide(self):
        """Test ODS scan search returns FQL guide on filter error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_ods_scans(filter="invalid::syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("Filter error occurred", result["hint"])

    def test_get_ods_scan_details(self):
        """Test ODS scan detail lookup by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "scan-1", "status": "done"}]},
        }

        result = self.module.get_ods_scan_details(ids=["scan-1"])

        self.mock_client.command.assert_called_once_with(
            "get_scans_by_scan_ids_v2",
            parameters={"ids": ["scan-1"]},
        )
        self.assertEqual(result[0]["id"], "scan-1")

    def test_get_ods_scan_host_details(self):
        """Test ODS scan-host detail lookup by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "host-1", "scan_id": "scan-1"}]},
        }

        result = self.module.get_ods_scan_host_details(ids=["host-1"])

        self.mock_client.command.assert_called_once_with(
            "get_scan_host_metadata_by_ids",
            parameters={"ids": ["host-1"]},
        )
        self.assertEqual(result[0]["id"], "host-1")

    def test_search_ods_scheduled_scans_empty_returns_fql_guide(self):
        """Test scheduled ODS search returns FQL guide on empty results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_ods_scheduled_scans(filter="status:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_get_ods_scheduled_scan_details(self):
        """Test scheduled ODS detail lookup by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "sched-1", "status": "enabled"}]},
        }

        result = self.module.get_ods_scheduled_scan_details(ids=["sched-1"])

        self.mock_client.command.assert_called_once_with(
            "get_scheduled_scans_by_scan_ids",
            parameters={"ids": ["sched-1"]},
        )
        self.assertEqual(result[0]["id"], "sched-1")

    def test_launch_ods_scan_builds_payload(self):
        """Test ODS create-scan payload construction."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"scan_id": "scan-1"}]},
        }

        result = self.module.launch_ods_scan(
            hosts=["aid-1"],
            host_groups=["hg-1"],
            file_paths=[r"C:\Temp"],
            description="scan now",
            quarantine=True,
            start_timestamp="2026-03-22T18:00:00Z",
            interval=3600,
        )

        self.mock_client.command.assert_called_once_with(
            "create_scan",
            body={
                "hosts": ["aid-1"],
                "host_groups": ["hg-1"],
                "file_paths": [r"C:\Temp"],
                "description": "scan now",
                "quarantine": True,
                "start_timestamp": "2026-03-22T18:00:00Z",
                "interval": 3600,
            },
        )
        self.assertEqual(result[0]["scan_id"], "scan-1")

    def test_schedule_ods_scan_nests_schedule_fields(self):
        """Test ODS schedule payload nests schedule settings."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"scheduled_scan_id": "sched-1"}]},
        }

        self.module.schedule_ods_scan(
            host_groups=["hg-1"],
            description="daily scan",
            start_timestamp="2026-03-23T00:00:00Z",
            interval=86400,
            ignored_by_channelfile=True,
        )

        self.mock_client.command.assert_called_once_with(
            "schedule_scan",
            body={
                "host_groups": ["hg-1"],
                "description": "daily scan",
                "schedule": {
                    "start_timestamp": "2026-03-23T00:00:00Z",
                    "interval": 86400,
                    "ignored_by_channelfile": True,
                },
            },
        )

    def test_delete_scheduled_scans_requires_ids_or_filter(self):
        """Test delete scheduled scans validates selector input."""
        result = self.module.delete_ods_scheduled_scans()

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_scheduled_scans_by_filter(self):
        """Test deleting scheduled scans by filter."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": 2}]},
        }

        result = self.module.delete_ods_scheduled_scans(filter="status:'enabled'")

        self.mock_client.command.assert_called_once_with(
            "delete_scheduled_scans",
            parameters={"filter": "status:'enabled'"},
        )
        self.assertEqual(result[0]["deleted"], 2)

    def test_search_ods_malicious_files_returns_details(self):
        """Test malicious file search flow returns details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["mf-1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "mf-1", "filename": "Shift - Print_d3lsk.exe"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_ods_malicious_files(filter="filename:'Shift*'")

        self.assertEqual(result[0]["filename"], "Shift - Print_d3lsk.exe")

    def test_get_ods_malicious_file_details(self):
        """Test malicious file detail lookup by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "mf-1", "hash": "abc"}]},
        }

        result = self.module.get_ods_malicious_file_details(ids=["mf-1"])

        self.mock_client.command.assert_called_once_with(
            "get_malicious_files_by_ids",
            parameters={"ids": ["mf-1"]},
        )
        self.assertEqual(result[0]["id"], "mf-1")
