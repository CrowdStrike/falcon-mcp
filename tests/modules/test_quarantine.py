"""
Tests for the Quarantine module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.quarantine import QuarantineModule
from tests.modules.utils.test_modules import TestModules


class TestQuarantineModule(TestModules):
    """Test cases for the Quarantine module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(QuarantineModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_quarantined_files",
            "falcon_get_quarantined_file_details",
            "falcon_preview_quarantine_action_counts",
            "falcon_update_quarantined_files_by_ids",
            "falcon_update_quarantined_files_by_filter",
        ]
        self.assert_tools_registered(expected_tools)

    def test_tool_annotations(self):
        """Test quarantine tool annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_quarantined_files", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_get_quarantined_file_details",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_preview_quarantine_action_counts",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_update_quarantined_files_by_ids",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_update_quarantined_files_by_filter",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_search_quarantined_files_returns_details(self):
        """Test search flow returns full quarantine metadata."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["qf-1", "qf-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "qf-1", "status": "released"},
                    {"id": "qf-2", "status": "quarantined"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_quarantined_files(
            filter="device.hostname:'BRR-WB-LIB-22'",
            q="Shift - Print_d3lsk.exe",
            limit=25,
            offset="0",
            sort="date_updated|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "QueryQuarantineFiles")
        self.assertEqual(
            first_call[1]["parameters"],
            {
                "filter": "device.hostname:'BRR-WB-LIB-22'",
                "q": "Shift - Print_d3lsk.exe",
                "limit": 25,
                "offset": "0",
                "sort": "date_updated|desc",
            },
        )

        self.assertEqual(second_call[0][0], "GetQuarantineFiles")
        self.assertEqual(second_call[1]["body"], {"ids": ["qf-1", "qf-2"]})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["status"], "quarantined")

    def test_preview_quarantine_action_counts(self):
        """Test quarantine action count preview."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"delete": 1, "release": 2}]},
        }

        result = self.module.preview_quarantine_action_counts(filter="*")

        self.mock_client.command.assert_called_once_with(
            "ActionUpdateCount",
            parameters={"filter": "*"},
        )
        self.assertEqual(result[0]["delete"], 1)

    def test_update_quarantined_files_by_ids(self):
        """Test updating quarantined files by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 2}]},
        }

        result = self.module.update_quarantined_files_by_ids(
            ids=["qf-1", "qf-2"],
            action="delete",
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQuarantinedDetectsByIds",
            body={"ids": ["qf-1", "qf-2"], "action": "delete", "comment": "cleanup"},
        )
        self.assertEqual(result[0]["updated"], 2)

    def test_update_quarantined_files_by_filter_requires_scope(self):
        """Test updating by filter requires filter or q."""
        result = self.module.update_quarantined_files_by_filter(action="release")

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()
