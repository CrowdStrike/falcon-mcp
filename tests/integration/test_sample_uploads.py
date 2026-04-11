"""Integration tests for the Sample Uploads module."""

from zipfile import ZipFile

import pytest

from falcon_mcp.modules.sample_uploads import SampleUploadsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSampleUploadsIntegration(BaseIntegrationTest):
    """Integration tests for the Sample Uploads module with real API calls.

    Validates:
    - Correct FalconPy operation names for sample and archive upload workflows
    - Multipart upload handling for sample and archive content
    - Read-after-write archive status and listing workflows
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Sample Uploads module with a real client."""
        self.module = SampleUploadsModule(falcon_client)

    def test_upload_and_delete_sample_round_trip(self, tmp_path):
        """Test uploading and deleting a sample with cleanup."""
        sample_path = tmp_path / "integration-sample.txt"
        sample_path.write_text("falcon-mcp integration sample\n", encoding="utf-8")

        upload_result = self.call_method(
            self.module.upload_sample_for_cloud_analysis,
            file_path=str(sample_path),
            comment="integration test sample upload",
            is_confidential=True,
        )

        self.assert_no_error(upload_result, context="upload_sample_for_cloud_analysis")
        self.assert_valid_list_response(
            upload_result,
            min_length=1,
            context="upload_sample_for_cloud_analysis",
        )

        sample_sha = None
        if isinstance(upload_result[0], dict):
            sample_sha = upload_result[0].get("sha256")

        assert sample_sha, "Expected uploaded sample SHA256 in upload_sample_for_cloud_analysis response"

        delete_result = self.call_method(self.module.delete_uploaded_samples, ids=[sample_sha])

        self.assert_no_error(delete_result, context="delete_uploaded_samples")
        self.assert_valid_list_response(delete_result, min_length=1, context="delete_uploaded_samples")
        assert sample_sha in delete_result, "Expected deleted sample SHA256 in delete_uploaded_samples response"

    def test_archive_upload_status_list_and_delete_round_trip(self, tmp_path):
        """Test archive upload, status lookup, extraction flow, and cleanup."""
        archive_sha = None
        extraction_id = None
        archive_path = tmp_path / "integration-archive.zip"
        inner_file = tmp_path / "integration-archive.txt"
        inner_file.write_text("falcon-mcp integration archive\n", encoding="utf-8")

        with ZipFile(archive_path, "w") as zip_file:
            zip_file.write(inner_file, arcname="integration-archive.txt")

        try:
            upload_result = self.call_method(
                self.module.upload_archive_for_extraction,
                file_path=str(archive_path),
                comment="integration test archive upload",
                is_confidential=True,
            )

            self.assert_no_error(upload_result, context="upload_archive_for_extraction")
            self.assert_valid_list_response(
                upload_result,
                min_length=1,
                context="upload_archive_for_extraction",
            )

            if isinstance(upload_result[0], dict):
                archive_sha = upload_result[0].get("sha256")

            assert archive_sha, "Expected archive SHA256 in upload_archive_for_extraction response"

            status_result = self.call_method(
                self.module.get_archive_upload_status,
                id=archive_sha,
                include_files=True,
            )
            self.assert_no_error(status_result, context="get_archive_upload_status")
            self.assert_valid_list_response(
                status_result,
                min_length=0,
                context="get_archive_upload_status",
            )

            list_result = self.call_method(
                self.module.list_uploaded_archives,
                id=archive_sha,
                limit=5,
            )
            self.assert_no_error(list_result, context="list_uploaded_archives")
            self.assert_valid_list_response(
                list_result,
                min_length=0,
                context="list_uploaded_archives",
            )

            extraction_result = self.call_method(
                self.module.create_archive_extraction,
                archive_sha256=archive_sha,
                extract_all=True,
            )
            self.assert_no_error(extraction_result, context="create_archive_extraction")
            self.assert_valid_list_response(
                extraction_result,
                min_length=1,
                context="create_archive_extraction",
            )

            if isinstance(extraction_result[0], dict):
                extraction_id = extraction_result[0].get("id")

            if not extraction_id:
                self.skip_with_warning(
                    "Archive extraction did not return an extraction ID",
                    context="test_archive_upload_status_list_and_delete_round_trip",
                )

            extraction_status = self.call_method(
                self.module.get_archive_extraction_status,
                id=extraction_id,
                include_files=True,
            )
            self.assert_no_error(extraction_status, context="get_archive_extraction_status")
            self.assert_valid_list_response(
                extraction_status,
                min_length=0,
                context="get_archive_extraction_status",
            )

            extraction_list = self.call_method(
                self.module.list_archive_extractions,
                id=extraction_id,
                limit=5,
            )
            self.assert_no_error(extraction_list, context="list_archive_extractions")
            self.assert_valid_list_response(
                extraction_list,
                min_length=0,
                context="list_archive_extractions",
            )
        finally:
            if archive_sha:
                delete_result = self.call_method(self.module.delete_uploaded_archive, id=archive_sha)
                self.assert_no_error(delete_result, context="delete_uploaded_archive")
