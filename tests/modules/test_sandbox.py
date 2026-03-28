"""
Tests for the Sandbox module.
"""

import base64

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.sandbox import SandboxModule
from tests.modules.utils.test_modules import TestModules


class TestSandboxModule(TestModules):
    """Test cases for the Sandbox module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SandboxModule)

    def test_register_tools(self):
        """Test registering sandbox tools."""
        expected_tools = [
            "falcon_upload_sandbox_sample",
            "falcon_check_sandbox_samples",
            "falcon_submit_sandbox_analysis",
            "falcon_search_sandbox_submissions",
            "falcon_get_sandbox_submission_details",
            "falcon_search_sandbox_reports",
            "falcon_get_sandbox_report_summaries",
            "falcon_get_sandbox_report_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_tool_annotations(self):
        """Test sandbox tool annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_check_sandbox_samples", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_sandbox_submissions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_sandbox_submission_details", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_sandbox_reports", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_upload_sandbox_sample",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_upload_sandbox_sample_from_base64(self):
        """Test sandbox sample upload from base64 input."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "sandbox-sha"}]},
        }

        result = self.module.upload_sandbox_sample(
            file_name="test.exe",
            file_base64=base64.b64encode(b"sandbox").decode("ascii"),
            comment="sandbox upload",
        )

        self.mock_client.command.assert_called_once_with(
            "UploadSampleV2",
            files=[("sample", ("test.exe", b"sandbox"))],
            data={
                "file_name": "test.exe",
                "comment": "sandbox upload",
                "is_confidential": True,
            },
        )
        self.assertEqual(result[0]["sha256"], "sandbox-sha")

    def test_submit_sandbox_analysis_requires_sha_or_url(self):
        """Test sandbox submit validation."""
        result = self.module.submit_sandbox_analysis()

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_submit_sandbox_analysis_builds_payload(self):
        """Test sandbox submit payload construction."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"submission_id": "sub-1"}]},
        }

        result = self.module.submit_sandbox_analysis(
            sha256="abc123",
            environment_id=140,
            network_settings="offline",
            action_script="default",
            user_tags=["triage"],
            send_email_notification=False,
            aid="aid-1",
        )

        self.mock_client.command.assert_called_once_with(
            "Submit",
            parameters={"aid": "aid-1"},
            body={
                "sandbox": [
                    {
                        "sha256": "abc123",
                        "environment_id": 140,
                        "network_settings": "offline",
                        "action_script": "default",
                    }
                ],
                "user_tags": ["triage"],
                "send_email_notification": False,
            },
        )
        self.assertEqual(result[0]["submission_id"], "sub-1")

    def test_search_sandbox_submissions_returns_details(self):
        """Test sandbox submission search flow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["sub-1"]},
        }
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "sub-1", "status": "in_progress"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_sandbox_submissions(filter="sha256:'abc123'")

        self.assertEqual(result[0]["status"], "in_progress")

    def test_search_sandbox_reports_returns_summaries(self):
        """Test sandbox report search flow returns summaries."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["report-1"]},
        }
        summary_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "report-1", "verdict": "malicious"}]},
        }
        self.mock_client.command.side_effect = [query_response, summary_response]

        result = self.module.search_sandbox_reports(filter="sha256:'abc123'")

        self.assertEqual(result[0]["verdict"], "malicious")
