"""
Sample Uploads module for Falcon MCP Server.

This module provides tools for uploading suspicious files and archives, polling
archive processing state, and extracting files for downstream analysis.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import (
    normalize_field_value,
    prepare_api_parameters,
    resolve_binary_upload_input,
)
from falcon_mcp.modules.base import BaseModule

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)


class SampleUploadsModule(BaseModule):
    """Module for Falcon sample and archive upload workflows."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.upload_sample_for_cloud_analysis,
            name="upload_sample_for_cloud_analysis",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_uploaded_samples,
            name="delete_uploaded_samples",
            annotations=DESTRUCTIVE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.list_uploaded_archives,
            name="list_uploaded_archives",
        )
        self._add_tool(
            server=server,
            method=self.get_archive_upload_status,
            name="get_archive_upload_status",
        )
        self._add_tool(
            server=server,
            method=self.upload_archive_for_extraction,
            name="upload_archive_for_extraction",
            annotations=MUTATING_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_uploaded_archive,
            name="delete_uploaded_archive",
            annotations=DESTRUCTIVE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.list_archive_extractions,
            name="list_archive_extractions",
        )
        self._add_tool(
            server=server,
            method=self.get_archive_extraction_status,
            name="get_archive_extraction_status",
        )
        self._add_tool(
            server=server,
            method=self.create_archive_extraction,
            name="create_archive_extraction",
            annotations=MUTATING_ANNOTATIONS,
        )

    def upload_sample_for_cloud_analysis(
        self,
        file_name: str | None = Field(
            default=None,
            description="Name of the sample file. Required when using `file_base64`. Optional when `file_path` is provided.",
        ),
        file_path: str | None = Field(
            default=None,
            description="Absolute or relative path to a local file to upload.",
        ),
        file_base64: str | None = Field(
            default=None,
            description="Base64-encoded sample content. Provide this instead of `file_path` when the file is already in memory.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional analyst comment stored with the uploaded sample.",
        ),
        is_confidential: bool | None = Field(
            default=True,
            description="Whether the uploaded sample should remain visible only to your tenant.",
        ),
    ) -> list[dict[str, Any]]:
        """Upload a sample for cloud analysis using the Sample Uploads service."""
        try:
            sample_bytes, upload_name = resolve_binary_upload_input(
                file_path=file_path,
                file_base64=file_base64,
                file_name=file_name,
            )
        except ValueError as exc:
            return [_format_error_response(str(exc))]

        response = self.client.command(
            "UploadSampleV3",
            files=[("sample", (upload_name, sample_bytes))],
            data=prepare_api_parameters(
                {
                    "file_name": upload_name,
                    "comment": comment,
                    "is_confidential": is_confidential,
                }
            ),
        )

        result = handle_api_response(
            response,
            operation="UploadSampleV3",
            error_message="Failed to upload sample",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_uploaded_samples(
        self,
        ids: list[str] = Field(description="Sample SHA256 value(s) to delete from the uploaded sample store."),
    ) -> list[dict[str, Any]]:
        """Delete previously uploaded samples from the Sample Uploads service."""
        result = self._base_query_api_call(
            operation="DeleteSampleV3",
            query_params={"ids": ids},
            error_message="Failed to delete uploaded samples",
        )

        if self._is_error(result):
            return [result]

        return result

    def list_uploaded_archives(
        self,
        id: str = Field(description="Archive SHA256 to list extracted archive file entries for."),
        limit: int | None = Field(default=None, description="Maximum number of archive file entries to return."),
        offset: str | None = Field(default=None, description="Offset for paginating archive file entries."),
    ) -> list[dict[str, Any]]:
        """List files discovered inside an uploaded archive."""
        result = self._base_query_api_call(
            operation="ArchiveListV1",
            query_params={
                "id": id,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to list uploaded archive contents",
        )

        if self._is_error(result):
            return [result]

        return result

    def get_archive_upload_status(
        self,
        id: str = Field(description="Archive SHA256 to retrieve upload and processing status for."),
        include_files: bool | None = Field(
            default=None,
            description="Whether to include processed archive file entries in the response.",
        ),
    ) -> list[dict[str, Any]]:
        """Get processing status for an uploaded archive."""
        result = self._base_query_api_call(
            operation="ArchiveGetV1",
            query_params={
                "id": id,
                "include_files": include_files,
            },
            error_message="Failed to get archive upload status",
        )

        if self._is_error(result):
            return [result]

        return result

    def upload_archive_for_extraction(
        self,
        file_name: str | None = Field(
            default=None,
            description="Name of the archive. Required when using `file_base64`. Optional when `file_path` is provided.",
        ),
        file_path: str | None = Field(
            default=None,
            description="Absolute or relative path to a local archive to upload.",
        ),
        file_base64: str | None = Field(
            default=None,
            description="Base64-encoded archive content. Provide this instead of `file_path` when the archive is already in memory.",
        ),
        file_type: str = Field(
            default="zip",
            description="Archive format. Supported values are `zip`, `7zip`, or `7z`.",
        ),
        password: str | None = Field(
            default=None,
            description="Optional archive password.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional analyst comment stored with the uploaded archive.",
        ),
        is_confidential: bool | None = Field(
            default=True,
            description="Whether the uploaded archive should remain visible only to your tenant.",
        ),
    ) -> list[dict[str, Any]]:
        """Upload an archive and queue it for extraction-aware analysis workflows."""
        try:
            archive_bytes, upload_name = resolve_binary_upload_input(
                file_path=file_path,
                file_base64=file_base64,
                file_name=file_name,
            )
        except ValueError as exc:
            return [_format_error_response(str(exc))]

        normalized_type = (normalize_field_value(file_type) or "zip").lower()
        content_type_map = {
            "zip": "application/zip",
            "7zip": "application/x-7z-compressed",
            "7z": "application/x-7z-compressed",
        }

        response = self.client.command(
            "ArchiveUploadV2",
            files=[
                (
                    "file",
                    (
                        upload_name,
                        archive_bytes,
                        content_type_map.get(normalized_type, "application/zip"),
                    ),
                )
            ],
            data=prepare_api_parameters(
                {
                    "name": upload_name,
                    "password": password,
                    "comment": comment,
                    "is_confidential": is_confidential,
                }
            ),
        )

        result = handle_api_response(
            response,
            operation="ArchiveUploadV2",
            error_message="Failed to upload archive",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_uploaded_archive(
        self,
        id: str = Field(description="Archive SHA256 to delete."),
    ) -> list[dict[str, Any]]:
        """Delete an uploaded archive from the Sample Uploads service."""
        result = self._base_query_api_call(
            operation="ArchiveDeleteV1",
            query_params={"id": id},
            error_message="Failed to delete uploaded archive",
        )

        if self._is_error(result):
            return [result]

        return result

    def list_archive_extractions(
        self,
        id: str = Field(description="Archive extraction operation ID to list extracted file entries for."),
        limit: int | None = Field(default=None, description="Maximum number of extraction file entries to return."),
        offset: str | None = Field(default=None, description="Offset for paginating extraction file entries."),
    ) -> list[dict[str, Any]]:
        """List files associated with an archive extraction operation."""
        result = self._base_query_api_call(
            operation="ExtractionListV1",
            query_params={
                "id": id,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to list archive extraction files",
        )

        if self._is_error(result):
            return [result]

        return result

    def get_archive_extraction_status(
        self,
        id: str = Field(description="Archive extraction operation ID to retrieve."),
        include_files: bool | None = Field(
            default=None,
            description="Whether to include processed extraction file entries in the response.",
        ),
    ) -> list[dict[str, Any]]:
        """Get status for an archive extraction job."""
        result = self._base_query_api_call(
            operation="ExtractionGetV1",
            query_params={
                "id": id,
                "include_files": include_files,
            },
            error_message="Failed to get archive extraction status",
        )

        if self._is_error(result):
            return [result]

        return result

    def create_archive_extraction(
        self,
        archive_sha256: str = Field(description="Archive SHA256 returned by the archive upload workflow."),
        extract_all: bool = Field(
            default=False,
            description="Whether to extract every file found in the archive.",
        ),
        files: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional list of specific files to extract. Each entry may include `name`, `comment`, and `is_confidential`.",
        ),
    ) -> list[dict[str, Any]]:
        """Extract files from an uploaded archive into Falcon internal storage."""
        extract_all = normalize_field_value(extract_all)
        files = normalize_field_value(files)

        if not extract_all and not files:
            return [
                _format_error_response(
                    "Provide `extract_all=true` or a non-empty `files` list when creating an archive extraction."
                )
            ]

        result = self._base_query_api_call(
            operation="ExtractionCreateV1",
            body_params={
                "sha256": archive_sha256,
                "extract_all": extract_all,
                "files": files,
            },
            error_message="Failed to create archive extraction",
        )

        if self._is_error(result):
            return [result]

        return result
