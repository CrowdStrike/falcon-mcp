"""
Tests for the Sample Uploads module.
"""

import base64
import tempfile
from pathlib import Path

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.sample_uploads import SampleUploadsModule
from tests.modules.utils.test_modules import TestModules


class TestSampleUploadsModule(TestModules):
    """Test cases for the Sample Uploads module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SampleUploadsModule)

    def test_register_tools(self):
        """Test registering sample-upload tools."""
        expected_tools = [
            "falcon_upload_sample_for_cloud_analysis",
            "falcon_delete_uploaded_samples",
            "falcon_list_uploaded_archives",
            "falcon_get_archive_upload_status",
            "falcon_upload_archive_for_extraction",
            "falcon_delete_uploaded_archive",
            "falcon_list_archive_extractions",
            "falcon_get_archive_extraction_status",
            "falcon_create_archive_extraction",
        ]
        self.assert_tools_registered(expected_tools)

    def test_tool_annotations(self):
        """Test sample upload annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_list_uploaded_archives", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_archive_upload_status", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_list_archive_extractions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_archive_extraction_status", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_upload_sample_for_cloud_analysis",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_uploaded_samples",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_upload_archive_for_extraction",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_uploaded_archive",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_create_archive_extraction",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_upload_sample_from_base64(self):
        """Test uploading a sample from base64 input."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "abc"}]},
        }

        result = self.module.upload_sample_for_cloud_analysis(
            file_name="test.exe",
            file_base64=base64.b64encode(b"hello").decode("ascii"),
            comment="triage",
            is_confidential=True,
        )

        self.mock_client.command.assert_called_once_with(
            "UploadSampleV3",
            files=[("sample", ("test.exe", b"hello"))],
            data={
                "file_name": "test.exe",
                "comment": "triage",
                "is_confidential": True,
            },
        )
        self.assertEqual(result[0]["sha256"], "abc")

    def test_upload_sample_requires_filename_with_base64(self):
        """Test base64 uploads require file_name."""
        result = self.module.upload_sample_for_cloud_analysis(
            file_base64=base64.b64encode(b"hello").decode("ascii"),
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_upload_archive_from_file_path(self):
        """Test uploading an archive from disk."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "archive-sha"}]},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "payload.zip"
            archive_path.write_bytes(b"zip-bytes")

            result = self.module.upload_archive_for_extraction(
                file_path=str(archive_path),
                file_type="zip",
                comment="archive upload",
            )

        self.mock_client.command.assert_called_once_with(
            "ArchiveUploadV2",
            files=[("file", ("payload.zip", b"zip-bytes", "application/zip"))],
            data={
                "name": "payload.zip",
                "comment": "archive upload",
                "is_confidential": True,
            },
        )
        self.assertEqual(result[0]["sha256"], "archive-sha")

    def test_upload_archive_uses_default_file_type_for_direct_calls(self):
        """Test archive uploads normalize the default file_type value."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "archive-sha"}]},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "payload.zip"
            archive_path.write_bytes(b"zip-bytes")

            result = self.module.upload_archive_for_extraction(
                file_path=str(archive_path),
                comment="archive upload",
            )

        self.mock_client.command.assert_called_once_with(
            "ArchiveUploadV2",
            files=[("file", ("payload.zip", b"zip-bytes", "application/zip"))],
            data={
                "name": "payload.zip",
                "comment": "archive upload",
                "is_confidential": True,
            },
        )
        self.assertEqual(result[0]["sha256"], "archive-sha")

    def test_upload_archive_rejects_invalid_file_type(self):
        """Test archive uploads reject unsupported file_type values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "payload.zip"
            archive_path.write_bytes(b"zip-bytes")

            result = self.module.upload_archive_for_extraction(
                file_path=str(archive_path),
                file_type="rar",
            )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_archive_extraction_requires_selection(self):
        """Test archive extraction requires extract_all or files."""
        result = self.module.create_archive_extraction(archive_sha256="archive-sha")

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_archive_extraction(self):
        """Test archive extraction payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "extract-1"}]},
        }

        result = self.module.create_archive_extraction(
            archive_sha256="archive-sha",
            extract_all=True,
        )

        self.mock_client.command.assert_called_once_with(
            "ExtractionCreateV1",
            body={"sha256": "archive-sha", "extract_all": True},
        )
        self.assertEqual(result[0]["id"], "extract-1")

    def test_delete_uploaded_archive(self):
        """Test deleting an uploaded archive by SHA256."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": True}]},
        }

        result = self.module.delete_uploaded_archive(id="archive-sha")

        self.mock_client.command.assert_called_once_with(
            "ArchiveDeleteV1",
            parameters={"id": "archive-sha"},
        )
        self.assertTrue(result[0]["deleted"])
