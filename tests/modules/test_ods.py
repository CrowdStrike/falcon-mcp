"""Tests for the On-Demand Scan module."""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.ods import ODSModule
from tests.modules.utils.test_modules import TestModules


class TestODSModule(TestModules):
    """Test On-Demand Scan tools and resources."""

    def setUp(self):
        self.setup_module(ODSModule)

    def test_register_tools_and_resources(self):
        self.assert_tools_registered([
            "falcon_search_ods_scans",
            "falcon_search_ods_scan_hosts",
            "falcon_search_ods_malicious_files",
            "falcon_search_ods_scheduled_scans",
            "falcon_launch_ods_scan",
            "falcon_cancel_ods_scans",
            "falcon_schedule_ods_scan",
            "falcon_delete_ods_scheduled_scans",
        ])
        self.assert_resources_registered([
            "falcon_search_ods_scans_fql_guide",
            "falcon_search_ods_scan_hosts_fql_guide",
            "falcon_search_ods_malicious_files_fql_guide",
            "falcon_search_ods_scheduled_scans_fql_guide",
        ])

    def test_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_ods_scans", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_launch_ods_scan",
            ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True),
        )
        self.assert_tool_annotations(
            "falcon_cancel_ods_scans",
            ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True),
        )

    def test_search_scans_hydrates_and_preserves_query_order(self):
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": ["scan-2", "scan-1"],
                    "meta": {"pagination": {"offset": 0, "limit": 10, "total": 2}},
                },
            },
            {
                "status_code": 200,
                "body": {"resources": [{"id": "scan-1"}, {"id": "scan-2"}]},
            },
        ]

        result = self.module.search_ods_scans(filter="status:'completed'", limit=10, offset=0)

        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "query_scans")
        self.assertEqual(
            self.mock_client.command.call_args_list[1],
            (("get_scans_by_scan_ids_v2",), {"parameters": {"ids": ["scan-2", "scan-1"]}}),
        )
        self.assertEqual([item["id"] for item in result["results"]], ["scan-2", "scan-1"])
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_filter_error_includes_fql_guide(self):
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        result = self.module.search_ods_malicious_files(filter="bad::filter")
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "bad::filter")

    def test_launch_scan_builds_expected_body(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "scan-1"}]},
        }
        result = self.module.launch_ods_scan(
            file_paths=["C:\\Temp"],
            hosts=["aid-1"],
            host_groups=None,
            quarantine=False,
            endpoint_notification=False,
            max_duration=None,
            max_file_size=None,
            pause_duration=None,
        )
        self.mock_client.command.assert_called_once_with(
            "create_scan",
            body={
                "hosts": ["aid-1"],
                "file_paths": ["C:\\Temp"],
                "quarantine": False,
                "endpoint_notification": False,
                "initiated_from": "falcon-mcp",
            },
        )
        self.assertEqual(result[0]["id"], "scan-1")

    def test_launch_requires_target_and_path(self):
        result = self.module.launch_ods_scan(file_paths=[], hosts=None, host_groups=None)
        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_schedule_and_delete(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        self.module.schedule_ods_scan(
            file_paths=["/tmp"],
            hosts=["aid-1"],
            schedule={"start_timestamp": "2026-09-03T00:00:00Z", "interval": 86400},
        )
        body = self.mock_client.command.call_args.kwargs["body"]
        self.assertEqual(body["schedule"]["interval"], 86400)
        self.mock_client.reset_mock()
        self.module.delete_ods_scheduled_scans(ids=["schedule-1"])
        self.mock_client.command.assert_called_once_with(
            "delete_scheduled_scans", parameters={"ids": ["schedule-1"]}
        )
