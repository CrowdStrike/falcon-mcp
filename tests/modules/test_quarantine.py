"""
Tests for the Quarantine module.
"""

import unittest

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
            "falcon_preview_quarantine_actions",
            "falcon_update_quarantined_files",
            "falcon_delete_quarantined_files",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering quarantine resources with the server."""
        expected_resources = [
            "falcon_search_quarantined_files_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test quarantine tool annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_quarantined_files", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_preview_quarantine_actions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_update_quarantined_files",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_quarantined_files",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
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
            filter="hostname:'BRR-WB-LIB-22'",
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
                "filter": "hostname:'BRR-WB-LIB-22'",
                "limit": 25,
                "offset": "0",
                "sort": "date_updated|desc",
            },
        )

        self.assertEqual(second_call[0][0], "GetQuarantineFiles")
        self.assertEqual(second_call[1]["body"], {"ids": ["qf-1", "qf-2"]})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["status"], "quarantined")

    def test_search_quarantined_files_error_returns_fql_guide(self):
        """Test quarantine search returns FQL guide on filter error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_quarantined_files(filter="invalid::syntax")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertIn("hint", result)
        self.assertIn("Filter error occurred", result["hint"])

    def test_search_quarantined_files_empty_returns_fql_guide(self):
        """Test quarantine search returns FQL guide on empty results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_quarantined_files(filter="status:'nonexistent'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_preview_quarantine_actions(self):
        """Test quarantine action preview with correct live response shape."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "affected_files_by_action",
                        "buckets": [
                            {"label": "release", "count": 2},
                            {"label": "delete", "count": 1},
                            {"label": "unrelease", "count": 3},
                        ],
                    }
                ]
            },
        }

        result = self.module.preview_quarantine_actions(filter="state:'quarantined'")

        self.mock_client.command.assert_called_once_with(
            "ActionUpdateCount",
            parameters={"filter": "state:'quarantined'"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "affected_files_by_action")
        self.assertIn("buckets", result[0])
        self.assertEqual(result[0]["buckets"][0]["label"], "release")

    def test_preview_quarantine_actions_error(self):
        """Test quarantine action count returns error on API failure."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter expression"}]},
        }

        result = self.module.preview_quarantine_actions(filter="invalid::syntax")

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_update_quarantined_files_by_ids(self):
        """Test updating quarantined files by IDs uses UpdateQuarantinedDetectsByIds."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 2}]},
        }

        result = self.module.update_quarantined_files(
            action="release",
            ids=["qf-1", "qf-2"],
            comment="restore for investigation",
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQuarantinedDetectsByIds",
            body={
                "ids": ["qf-1", "qf-2"],
                "action": "release",
                "comment": "restore for investigation",
            },
        )
        self.assertEqual(result[0]["updated"], 2)

    def test_update_quarantined_files_by_filter(self):
        """Test updating quarantined files by filter uses UpdateQfByQuery."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 3}]},
        }

        result = self.module.update_quarantined_files(
            action="unrelease",
            ids=None,
            filter="status:'quarantined'",
            comment="restore access",
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQfByQuery",
            body={
                "action": "unrelease",
                "filter": "status:'quarantined'",
                "comment": "restore access",
            },
        )
        self.assertEqual(result[0]["updated"], 3)

    def test_update_quarantined_files_rejects_invalid_action(self):
        """Test invalid quarantine actions are rejected before the API call."""
        result = self.module.update_quarantined_files(
            action="restore",
            ids=["qf-1"],
            filter=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_quarantined_files_requires_selector(self):
        """Test updating quarantined files requires at least one of ids/filter."""
        result = self.module.update_quarantined_files(action="release", ids=None, filter=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_quarantined_files_empty_ids_guard(self):
        """Test updating with empty ids list returns error without API call."""
        result = self.module.update_quarantined_files(action="release", ids=[], filter=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_quarantined_files_case_insensitive(self):
        """Test that action names are case-insensitive (RELEASE works like release)."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.update_quarantined_files(
            action="RELEASE",
            ids=["qf-1"],
            filter=None,
        )

        self.assertEqual(len(result), 1)
        self.assertNotIn("error", result[0])
        self.mock_client.command.assert_called_once()
        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(call_body["action"], "release")

    def test_delete_quarantined_files_by_ids(self):
        """Test deleting quarantined files by IDs hardcodes action=delete."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 2}]},
        }

        result = self.module.delete_quarantined_files(
            ids=["qf-1", "qf-2"],
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQuarantinedDetectsByIds",
            body={"ids": ["qf-1", "qf-2"], "action": "delete", "comment": "cleanup"},
        )
        self.assertEqual(result[0]["updated"], 2)

    def test_delete_quarantined_files_by_filter(self):
        """Test deleting quarantined files by filter uses UpdateQfByQuery with action=delete."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 3}]},
        }

        result = self.module.delete_quarantined_files(
            ids=None,
            filter="status:'quarantined'",
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQfByQuery",
            body={
                "action": "delete",
                "filter": "status:'quarantined'",
                "comment": "cleanup",
            },
        )
        self.assertEqual(result[0]["updated"], 3)

    def test_delete_quarantined_files_requires_selector(self):
        """Test deleting quarantined files requires at least one of ids/filter."""
        result = self.module.delete_quarantined_files(ids=None, filter=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_quarantined_files_empty_ids_guard(self):
        """Test deleting with empty ids list returns error without API call."""
        result = self.module.delete_quarantined_files(ids=[], filter=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
