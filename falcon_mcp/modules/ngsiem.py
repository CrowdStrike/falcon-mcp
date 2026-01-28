"""
NGSIEM module for Falcon MCP Server

This module provides tools for initiating NGSIEM searches.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from importlib import resources

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ngsiem import (
    NGSIEM_EVENT_FIELDS_DOCUMENTATION,
    NGSIEM_EVENT_ONTOLOGY_DOCUMENTATION,
    NGSIEM_QUERY_FUNCTIONS_DOCUMENTATION,
)

logger = get_logger(__name__)

DEFAULT_NGSIEM_REPOSITORY = os.getenv("FALCON_NGSIEM_REPOSITORY", "base_sensor")


class NGSIEMModule(BaseModule):
    """Module for initiating NGSIEM searches."""

    def __init__(self, client):
        super().__init__(client)
        self._ontology_cache: dict[str, dict[str, Any]] | None = None

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.start_ngsiem_search,
            name="start_ngsiem_search",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_event_schema,
            name="get_ngsiem_event_schema",
        )
        self._add_tool(
            server=server,
            method=self.search_ngsiem_events,
            name="search_ngsiem_events",
        )
        self._add_tool(
            server=server,
            method=self.list_ngsiem_event_tables,
            name="list_ngsiem_event_tables",
        )
        self._add_tool(
            server=server,
            method=self.list_ngsiem_event_fields,
            name="list_ngsiem_event_fields",
        )
        self._add_tool(
            server=server,
            method=self.upload_ngsiem_lookup_file,
            name="upload_ngsiem_lookup_file",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_lookup_file,
            name="get_ngsiem_lookup_file",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_lookup_file_from_package,
            name="get_ngsiem_lookup_file_from_package",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_lookup_file_from_package_with_namespace,
            name="get_ngsiem_lookup_file_from_package_with_namespace",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_search_status,
            name="get_ngsiem_search_status",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_search_results,
            name="get_ngsiem_search_results",
        )
        self._add_tool(
            server=server,
            method=self.stop_ngsiem_search,
            name="stop_ngsiem_search",
        )
        self._add_tool(
            server=server,
            method=self.search_ngsiem_and_wait,
            name="search_ngsiem_and_wait",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        ngsiem_query_functions_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/query/functions-guide"),
            name="falcon_ngsiem_query_functions_guide",
            description="Reference for NGSIEM query functions used in queryString.",
            text=NGSIEM_QUERY_FUNCTIONS_DOCUMENTATION,
        )

        ngsiem_event_fields_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/events/fields-guide"),
            name="falcon_ngsiem_event_fields_guide",
            description="Sample queries and key NGSIEM event fields.",
            text=NGSIEM_EVENT_FIELDS_DOCUMENTATION,
        )

        ngsiem_event_ontology_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/events/ontology-guide"),
            name="falcon_ngsiem_event_ontology_guide",
            description="NGSIEM event ontology reference (event tables and fields).",
            text=NGSIEM_EVENT_ONTOLOGY_DOCUMENTATION,
        )

        self._add_resource(
            server,
            ngsiem_query_functions_resource,
        )
        self._add_resource(
            server,
            ngsiem_event_fields_resource,
        )
        self._add_resource(
            server,
            ngsiem_event_ontology_resource,
        )

    def start_ngsiem_search(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description=(
                "Target repository for the search. Common values: 'alerts', 'events', "
                "or 'simulated'."
            ),
            examples=["base_sensor", "events", "alerts"],
        ),
        search: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Complete search payload. Use this to provide the full NGSIEM search body. "
                "If provided, other search parameters are ignored unless `body` is set."
            ),
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Full body payload as a dict. If provided, this is sent verbatim and "
                "overrides all other parameters."
            ),
        ),
        query_string: str | None = Field(
            default=None,
            description="Search query string to execute.",
            examples=["#event_simpleName=*"],
        ),
        start: str | None = Field(
            default=None,
            description="Search starting time range.",
            examples=["1d"],
        ),
        end: str | None = Field(
            default=None,
            description="Search end time range.",
        ),
        ingest_start: int | None = Field(
            default=None,
            description="Ingest start.",
        ),
        ingest_end: int | None = Field(
            default=None,
            description="Ingest maximum.",
        ),
        timezone: str | None = Field(
            default=None,
            description="Timezone applied to the search.",
        ),
        timezone_offset_minutes: int | None = Field(
            default=None,
            description="Timezone offset.",
        ),
        is_live: bool | None = Field(
            default=None,
            description="Flag indicating if this is a live search.",
        ),
        allow_event_skipping: bool | None = Field(
            default=None,
            description="Flag indicating if event skipping is allowed.",
        ),
        around: dict[str, Any] | None = Field(
            default=None,
            description="Search proximity arguments.",
        ),
        autobucket_count: int | None = Field(
            default=None,
            description="Number of events per bucket.",
        ),
        arguments: dict[str, Any] | None = Field(
            default=None,
            description="Search arguments in JSON format.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Start an NGSIEM search job.

        Use this to initiate a search against NGSIEM repositories (alerts/events).
        If you already have a full NGSIEM payload, provide it via `body` (highest
        precedence) or `search` (next precedence).
        """
        body = self._normalize_field_default(body)
        search = self._normalize_field_default(search)
        query_string = self._normalize_field_default(query_string)
        start = self._normalize_field_default(start)
        end = self._normalize_field_default(end)
        ingest_start = self._normalize_field_default(ingest_start)
        ingest_end = self._normalize_field_default(ingest_end)
        timezone = self._normalize_field_default(timezone)
        timezone_offset_minutes = self._normalize_field_default(timezone_offset_minutes)
        is_live = self._normalize_field_default(is_live)
        allow_event_skipping = self._normalize_field_default(allow_event_skipping)
        around = self._normalize_field_default(around)
        autobucket_count = self._normalize_field_default(autobucket_count)
        arguments = self._normalize_field_default(arguments)

        if body is not None:
            payload = body
        elif search is not None:
            payload = search
        else:
            payload = {
                "queryString": query_string,
                "start": start,
                "end": end,
                "ingestStart": ingest_start,
                "ingestEnd": ingest_end,
                "timezone": timezone,
                "timezoneOffsetMinutes": timezone_offset_minutes,
                "isLive": is_live,
                "allowEventSkipping": allow_event_skipping,
                "around": around,
                "autobucketCount": autobucket_count,
                "arguments": arguments,
            }

        prepared_payload = prepare_api_parameters(payload)
        logger.debug("Starting NGSIEM search in repository %s", repository)

        response = self.client.command(
            "StartSearchV1",
            repository=repository,
            body=prepared_payload,
        )

        response = self._normalize_ngsiem_response(response)

        return handle_api_response(
            response,
            operation="StartSearchV1",
            error_message="Failed to start NGSIEM search",
            default_result=response.get("body", {}),
        )

    def get_ngsiem_event_schema(
        self,
        event_simple_name: str = Field(
            description="Event table (event_simpleName) to look up.",
            examples=["EndOfProcess", "ProcessRollup2"],
        ),
        include_fields: bool = Field(
            default=True,
            description="Include the full list of fields for the event.",
        ),
        include_description: bool = Field(
            default=True,
            description="Include the event description details.",
        ),
        include_variants: bool = Field(
            default=False,
            description="Include event variants metadata.",
        ),
        include_metadata: bool = Field(
            default=True,
            description="Include metadata such as platforms and event IDs.",
        ),
    ) -> dict[str, Any]:
        """Get schema details for an NGSIEM event (event_simpleName)."""
        include_fields = self._normalize_field_default(include_fields, True)
        include_description = self._normalize_field_default(include_description, True)
        include_variants = self._normalize_field_default(include_variants, False)
        include_metadata = self._normalize_field_default(include_metadata, True)

        ontology = self._load_ngsiem_ontology()
        key = event_simple_name.strip().lower()
        entry = ontology.get(key)
        if not entry:
            return {
                "error": f"Event '{event_simple_name}' not found in ontology.",
            }

        response: dict[str, Any] = {"event_simpleName": entry.get("event_simpleName")}
        if include_description:
            response["description"] = entry.get("description")
            response["description_text"] = self._extract_description_text(
                entry.get("description")
            )
        if include_fields:
            response["fields"] = entry.get("fields", [])
            response["field_names"] = [field.get("name") for field in entry.get("fields", [])]
        if include_variants:
            response["variants"] = entry.get("variants", [])
        if include_metadata:
            for field in (
                "event_ids",
                "platforms",
                "transmission_classes",
                "cloudable",
                "status",
                "released_versions",
                "primary_process_field",
            ):
                if field in entry:
                    response[field] = entry[field]

        return response

    def search_ngsiem_events(
        self,
        query: str | None = Field(
            default=None,
            description="Case-insensitive substring to match event_simpleName.",
        ),
        field_name: str | None = Field(
            default=None,
            description="Filter events that include the specified field name.",
        ),
        platform: str | None = Field(
            default=None,
            description="Filter by platform (windows/linux/mac).",
            examples=["windows", "linux", "mac"],
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of events to return.",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset into the result set.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search NGSIEM event ontology entries by name and field criteria."""
        query = self._normalize_field_default(query)
        field_name = self._normalize_field_default(field_name)
        platform = self._normalize_field_default(platform)
        limit = self._normalize_field_default(limit, 50)
        offset = self._normalize_field_default(offset, 0)

        ontology = self._load_ngsiem_ontology()
        events = list(ontology.values())
        query_normalized = query.strip().lower() if query else None
        field_normalized = field_name.strip().lower() if field_name else None
        platform_normalized = platform.strip().lower() if platform else None

        results: list[dict[str, Any]] = []
        for entry in events:
            name = entry.get("event_simpleName", "")
            if query_normalized and query_normalized not in name.lower():
                continue
            if platform_normalized:
                platforms = [p.lower() for p in entry.get("platforms", [])]
                if platform_normalized not in platforms:
                    continue
            if field_normalized:
                field_names = [field.get("name", "").lower() for field in entry.get("fields", [])]
                if field_normalized not in field_names:
                    continue
            results.append(
                {
                    "event_simpleName": name,
                    "description_text": self._extract_description_text(
                        entry.get("description")
                    ),
                    "platforms": entry.get("platforms", []),
                    "fields_count": len(entry.get("fields", [])),
                }
            )

        return results[offset : offset + limit]

    def list_ngsiem_event_tables(
        self,
        query: str | None = Field(
            default=None,
            description="Case-insensitive substring to match event_simpleName.",
        ),
        platform: str | None = Field(
            default=None,
            description="Filter by platform (windows/linux/mac).",
            examples=["windows", "linux", "mac"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of event tables to return.",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset into the result set.",
        ),
    ) -> list[dict[str, Any]]:
        """List NGSIEM event tables with names and descriptions only."""
        query = self._normalize_field_default(query)
        platform = self._normalize_field_default(platform)
        limit = self._normalize_field_default(limit, 100)
        offset = self._normalize_field_default(offset, 0)

        ontology = self._load_ngsiem_ontology()
        events = list(ontology.values())
        query_normalized = query.strip().lower() if query else None
        platform_normalized = platform.strip().lower() if platform else None

        results: list[dict[str, Any]] = []
        for entry in events:
            name = entry.get("event_simpleName", "")
            if query_normalized and query_normalized not in name.lower():
                continue
            if platform_normalized:
                platforms = [p.lower() for p in entry.get("platforms", [])]
                if platform_normalized not in platforms:
                    continue
            results.append(
                {
                    "event_simpleName": name,
                    "description_text": self._extract_description_text(
                        entry.get("description")
                    ),
                }
            )

        return results[offset : offset + limit]

    def list_ngsiem_event_fields(
        self,
        event_simple_names: list[str] = Field(
            description="List of event tables (event_simpleName) to list fields for.",
            examples=[["EndOfProcess", "ProcessRollup2"]],
        ),
        include_metadata: bool = Field(
            default=False,
            description="Include full field metadata entries instead of names only.",
        ),
    ) -> list[dict[str, Any]]:
        """List fields for multiple NGSIEM event tables."""
        include_metadata = self._normalize_field_default(include_metadata, False)

        ontology = self._load_ngsiem_ontology()
        results: list[dict[str, Any]] = []
        for name in event_simple_names:
            entry = ontology.get(name.strip().lower())
            if not entry:
                results.append(
                    {
                        "event_simpleName": name,
                        "error": "Event not found in ontology.",
                    }
                )
                continue
            fields = entry.get("fields", [])
            if include_metadata:
                field_output: list[Any] = fields
            else:
                field_output = [field.get("name") for field in fields]
            results.append(
                {
                    "event_simpleName": entry.get("event_simpleName", name),
                    "fields": field_output,
                }
            )
        return results

    def upload_ngsiem_lookup_file(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the lookup file upload.",
            examples=["base_sensor", "events", "alerts"],
        ),
        lookup_file_path: str = Field(
            description="Path to the lookup file to upload.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Upload a lookup file to NGSIEM."""
        logger.debug("Uploading NGSIEM lookup file to %s", repository)

        with open(lookup_file_path, "rb") as upload_file:
            response = self.client.command(
                "UploadLookupV1",
                repository=repository,
                files={"file": upload_file},
            )

        return handle_api_response(
            response,
            operation="UploadLookupV1",
            error_message="Failed to upload NGSIEM lookup file",
            default_result=response.get("body", {}),
        )

    def get_ngsiem_lookup_file(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the lookup file download.",
            examples=["base_sensor", "events", "alerts"],
        ),
        filename: str = Field(
            description="Lookup filename to download.",
        ),
        stream: bool | None = Field(
            default=None,
            description="Enable streaming download of the returned file.",
        ),
    ) -> str | dict[str, Any]:
        """Download a lookup file from NGSIEM."""
        response = self.client.command(
            "GetLookupV1",
            repository=repository,
            filename=filename,
            stream=stream,
        )
        return self._format_lookup_download_response(
            response=response,
            operation="GetLookupV1",
            error_message="Failed to download NGSIEM lookup file",
        )

    def get_ngsiem_lookup_file_from_package(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the lookup file download.",
            examples=["base_sensor", "events", "alerts"],
        ),
        package: str = Field(
            description="Package name containing the lookup file.",
        ),
        filename: str = Field(
            description="Lookup filename to download.",
        ),
        stream: bool | None = Field(
            default=None,
            description="Enable streaming download of the returned file.",
        ),
    ) -> str | dict[str, Any]:
        """Download a lookup file from a package in NGSIEM."""
        response = self.client.command(
            "GetLookupFromPackageV1",
            repository=repository,
            package=package,
            filename=filename,
            stream=stream,
        )
        return self._format_lookup_download_response(
            response=response,
            operation="GetLookupFromPackageV1",
            error_message="Failed to download NGSIEM lookup file from package",
        )

    def get_ngsiem_lookup_file_from_package_with_namespace(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the lookup file download.",
            examples=["base_sensor", "events", "alerts"],
        ),
        namespace: str = Field(
            description="Namespace for the package.",
        ),
        package: str = Field(
            description="Package name containing the lookup file.",
        ),
        filename: str = Field(
            description="Lookup filename to download.",
        ),
        stream: bool | None = Field(
            default=None,
            description="Enable streaming download of the returned file.",
        ),
    ) -> str | dict[str, Any]:
        """Download a lookup file from a namespaced package in NGSIEM."""
        response = self.client.command(
            "GetLookupFromPackageWithNamespaceV1",
            repository=repository,
            namespace=namespace,
            package=package,
            filename=filename,
            stream=stream,
        )
        return self._format_lookup_download_response(
            response=response,
            operation="GetLookupFromPackageWithNamespaceV1",
            error_message=(
                "Failed to download NGSIEM lookup file from namespaced package"
            ),
        )

    def get_ngsiem_search_status(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the search status request.",
            examples=["base_sensor", "events", "alerts"],
        ),
        search_id: str = Field(
            description="ID of the NGSIEM search job.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get status information for a running or completed NGSIEM search."""
        logger.debug("Getting NGSIEM search status for %s in %s", search_id, repository)

        response = self.client.command(
            "GetSearchStatusV1",
            repository=repository,
            search_id=search_id,
        )

        response = self._normalize_ngsiem_response(response)

        return handle_api_response(
            response,
            operation="GetSearchStatusV1",
            error_message="Failed to get NGSIEM search status",
            default_result=response.get("body", {}),
        )

    def get_ngsiem_search_results(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the search results request.",
            examples=["base_sensor", "events", "alerts"],
        ),
        search_id: str = Field(
            description="ID of the NGSIEM search job.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve results for an NGSIEM search job."""
        result = self.get_ngsiem_search_status(
            repository=repository,
            search_id=search_id,
        )

        if isinstance(result, dict):
            if "events" in result:
                return result.get("events", [])
            if "results" in result:
                return result.get("results", [])

        return result

    def _format_lookup_download_response(
        self,
        response: dict[str, Any] | bytes,
        operation: str,
        error_message: str,
    ) -> str | dict[str, Any]:
        # FalconPy returns raw bytes for lookup file downloads.
        if isinstance(response, bytes):
            try:
                return response.decode("utf-8")
            except UnicodeDecodeError:
                return {
                    "error": "Lookup file is not UTF-8 text. Please download as binary.",
                    "size_bytes": len(response),
                }

        if isinstance(response, dict):
            response = self._normalize_ngsiem_response(response)
            return handle_api_response(
                response,
                operation=operation,
                error_message=error_message,
                default_result=response.get("body", {}),
            )

        return {"error": f"Unexpected response type: {type(response).__name__}"}

    def _normalize_field_default(self, value: Any, default: Any | None = None) -> Any:
        if isinstance(value, FieldInfo):
            return default
        return value

    def _normalize_ngsiem_response(self, response: Any) -> Any:
        if isinstance(response, dict) and "resources" in response and "body" not in response:
            normalized = dict(response)
            normalized["body"] = {"resources": response.get("resources")}
            return normalized
        return response

    def _load_ngsiem_ontology(self) -> dict[str, dict[str, Any]]:
        if self._ontology_cache is not None:
            return self._ontology_cache

        override_path = os.getenv("FALCON_NGSIEM_ONTOLOGY_EVENTS_PATH")
        ontology_path = None
        if override_path:
            ontology_path = override_path
        else:
            try:
                ontology_path = resources.files("falcon_mcp.resources").joinpath(
                    "data/ontology_events.json"
                )
            except Exception:  # pragma: no cover - defensive
                ontology_path = None

        try:
            if ontology_path is None:
                raise FileNotFoundError("Ontology path is not set")
            with open(ontology_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to load NGSIEM ontology events data: %s", exc)
            self._ontology_cache = {}
            return self._ontology_cache

        if not isinstance(data, list):
            logger.error("NGSIEM ontology data is not a list")
            self._ontology_cache = {}
            return self._ontology_cache

        self._ontology_cache = {
            entry.get("event_simpleName", "").lower(): entry for entry in data
        }
        return self._ontology_cache

    def _extract_description_text(self, description: Any) -> str:
        if description is None:
            return ""
        if isinstance(description, str):
            desc = description.strip()
            if desc.startswith("{") and desc.endswith("}"):
                try:
                    parsed = json.loads(desc)
                    return self._flatten_description(parsed)
                except json.JSONDecodeError:
                    return desc
            return desc
        if isinstance(description, dict):
            return self._flatten_description(description)
        return str(description)

    def _flatten_description(self, value: Any) -> str:
        parts: list[str] = []

        def walk(item: Any) -> None:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                for v in item.values():
                    walk(v)
            elif isinstance(item, list):
                for v in item:
                    walk(v)

        walk(value)
        return " ".join(part.strip() for part in parts if part.strip())

    def stop_ngsiem_search(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description="Target repository for the search stop request.",
            examples=["base_sensor", "events", "alerts"],
        ),
        search_id: str = Field(
            description="ID of the NGSIEM search job to stop.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Stop a running NGSIEM search job."""
        logger.debug("Stopping NGSIEM search %s in %s", search_id, repository)

        response = self.client.command(
            "StopSearchV1",
            repository=repository,
            id=search_id,
        )

        response = self._normalize_ngsiem_response(response)

        return handle_api_response(
            response,
            operation="StopSearchV1",
            error_message="Failed to stop NGSIEM search",
            default_result=response.get("body", {}),
        )

    def search_ngsiem_and_wait(
        self,
        repository: str = Field(
            default=DEFAULT_NGSIEM_REPOSITORY,
            description=(
                "Target repository for the search. Common values: 'alerts', 'events', "
                "or 'simulated'."
            ),
            examples=["base_sensor", "events", "alerts"],
        ),
        search: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Complete search payload. Use this to provide the full NGSIEM search body. "
                "If provided, other search parameters are ignored unless `body` is set."
            ),
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Full body payload as a dict. If provided, this is sent verbatim and "
                "overrides all other parameters."
            ),
        ),
        query_string: str | None = Field(
            default=None,
            description="Search query string to execute.",
            examples=["#event_simpleName=*"],
        ),
        start: str | None = Field(
            default=None,
            description="Search starting time range.",
            examples=["1d"],
        ),
        end: str | None = Field(
            default=None,
            description="Search end time range.",
        ),
        ingest_start: int | None = Field(
            default=None,
            description="Ingest start.",
        ),
        ingest_end: int | None = Field(
            default=None,
            description="Ingest maximum.",
        ),
        timezone: str | None = Field(
            default=None,
            description="Timezone applied to the search.",
        ),
        timezone_offset_minutes: int | None = Field(
            default=None,
            description="Timezone offset.",
        ),
        is_live: bool | None = Field(
            default=None,
            description="Flag indicating if this is a live search.",
        ),
        allow_event_skipping: bool | None = Field(
            default=None,
            description="Flag indicating if event skipping is allowed.",
        ),
        around: dict[str, Any] | None = Field(
            default=None,
            description="Search proximity arguments.",
        ),
        autobucket_count: int | None = Field(
            default=None,
            description="Number of events per bucket.",
        ),
        arguments: dict[str, Any] | None = Field(
            default=None,
            description="Search arguments in JSON format.",
        ),
        poll_interval_seconds: float = Field(
            default=2.0,
            ge=0.1,
            le=30.0,
            description="Polling interval in seconds.",
        ),
        timeout_seconds: float = Field(
            default=60.0,
            ge=1.0,
            le=600.0,
            description="Maximum time to wait for results.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Start an NGSIEM search and wait for results.

        This helper starts a search job, polls status until results are available
        or timeout is reached, then returns the events/results if present.
        """
        start_result = self.start_ngsiem_search(
            repository=repository,
            search=search,
            body=body,
            query_string=query_string,
            start=start,
            end=end,
            ingest_start=ingest_start,
            ingest_end=ingest_end,
            timezone=timezone,
            timezone_offset_minutes=timezone_offset_minutes,
            is_live=is_live,
            allow_event_skipping=allow_event_skipping,
            around=around,
            autobucket_count=autobucket_count,
            arguments=arguments,
        )

        if self._is_error(start_result):
            return start_result

        search_id = None
        if isinstance(start_result, list) and start_result:
            search_id = start_result[0].get("search_id") or start_result[0].get("id")
        elif isinstance(start_result, dict):
            search_id = start_result.get("search_id") or start_result.get("id")

        if not search_id:
            return {
                "error": "NGSIEM search response missing search_id",
                "details": {"response": start_result},
            }

        deadline = time.time() + timeout_seconds
        last_status: dict[str, Any] | list[dict[str, Any]] | None = None
        while time.time() < deadline:
            status = self.get_ngsiem_search_status(
                repository=repository,
                search_id=search_id,
            )

            if self._is_error(status):
                return status

            last_status = status

            if isinstance(status, dict):
                if status.get("events"):
                    return status.get("events", [])
                if status.get("results"):
                    return status.get("results", [])

            time.sleep(poll_interval_seconds)

        return {
            "error": "Timed out waiting for NGSIEM search results",
            "search_id": search_id,
            "last_status": last_status,
        }
