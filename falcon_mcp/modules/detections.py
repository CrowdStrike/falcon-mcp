"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.detections import (
    SEARCH_DETECTIONS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


class DetectionsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon detections."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_detections,
            name="search_detections",
        )

        self._add_tool(
            server=server,
            method=self.get_detection_details,
            name="get_detection_details",
        )

        self._add_tool(
            server=server,
            method=self.update_detections,
            name="update_detections",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_detections_fql_resource = TextResource(
            uri=AnyUrl("falcon://detections/search/fql-guide"),
            name="falcon_search_detections_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_detections` tool.",
            text=SEARCH_DETECTIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_detections_fql_resource,
        )

    def search_detections(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://detections/search/fql-guide` for syntax.",
            examples=["status:'new'+severity_name:'High'", "device.hostname:'DC*'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=9999,
            description="The maximum number of detections to return in this response (default: 10; max: 9999). Use with the offset parameter to manage pagination of results.",
        ),
        offset: int | None = Field(
            default=None,
            description="The first detection to return, where 0 is the latest detection. Use with the offset parameter to manage pagination of results.",
        ),
        q: str | None = Field(
            default=None,
            description="Search all detection metadata for the provided string",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort detections using these options:

                timestamp: Timestamp when the detection occurred
                created_timestamp: When the detection was created
                updated_timestamp: When the detection was last modified
                severity: Severity level of the detection (1-100, recommended when filtering by severity)
                confidence: Confidence level of the detection (1-100)
                agent_id: Agent ID associated with the detection

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'severity.desc' or 'severity|desc'

                When searching for high severity detections, use 'severity.desc' to get the highest severity detections first.
                For chronological ordering, use 'timestamp.desc' for most recent detections first.

                Examples: 'severity.desc', 'timestamp.desc'
            """).strip(),
            examples=["severity.desc", "timestamp.desc"],
        ),
        include_hidden: bool = Field(default=True),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Find detections by criteria and return their complete details.

        Use this to discover detections by severity, status, hostname, time range, or
        other attributes. Consult falcon://detections/search/fql-guide before constructing
        filter expressions. Returns full alert records including process context, device
        info, tactic/technique details, and threat classification.
        """
        detection_ids = self._base_search_api_call(
            operation="GetQueriesAlertsV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "q": q,
                "sort": sort,
            },
            error_message="Failed to search detections",
        )

        # Handle search error - return with FQL guide
        if self._is_error(detection_ids):
            return self._format_fql_error_response(
                [detection_ids], filter, SEARCH_DETECTIONS_FQL_DOCUMENTATION
            )

        # Handle empty results - return with FQL guide
        if not detection_ids:
            return self._format_fql_error_response([], filter, SEARCH_DETECTIONS_FQL_DOCUMENTATION)

        # Get detection details - past FQL concerns, normal API flow
        details = self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=detection_ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_detection_details(
        self,
        ids: list[str] = Field(
            description="Composite ID(s) to retrieve detection details for.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve details for detection IDs you already have.

        Use when you have specific composite detection ID(s). For discovering detections
        by criteria (severity, status, hostname, etc.), use falcon_search_detections
        instead. Returns full detection records.
        """
        logger.debug("Getting detection details for ID(s): %s", ids)

        return self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )

    def update_detections(
        self,
        ids: list[str] = Field(
            description="Composite ID(s) of the detection(s) to update.",
        ),
        status: str | None = Field(
            default=None,
            description="New status for the detection(s). Allowed values: new, in_progress, reopened, closed.",
        ),
        assign_to_uuid: str | None = Field(
            default=None,
            description="UUID of the user to assign the detection(s) to. Example: '00000000-0000-0000-0000-000000000000'.",
        ),
        assign_to_user_id: str | None = Field(
            default=None,
            description="Email address of the user to assign the detection(s) to. Example: 'analyst@example.com'.",
        ),
        assign_to_name: str | None = Field(
            default=None,
            description="Full name of the user to assign the detection(s) to. Example: 'Jane Smith'.",
        ),
        unassign: bool | None = Field(
            default=None,
            description="Pass True to remove the current assignee. False is a no-op; only True has any effect.",
        ),
        append_comment: str | None = Field(
            default=None,
            description="Comment to append to the detection(s). Comments are visible in the Falcon console. Must be a non-empty, non-whitespace string.",
        ),
        show_in_ui: bool | None = Field(
            default=None,
            description="Whether to show the detection(s) in the Falcon UI. Set to False to hide.",
        ),
        verdict: str | None = Field(
            default=None,
            description="Resolution verdict tag to add. Allowed values: true_positive, false_positive, ignored. Tags are additive — calling this tool does not clear a previously set verdict tag.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update the status, assignment, visibility, or verdict of one or more detections.

        Use to change status (new, in_progress, reopened, closed), assign to a user by
        UUID, email address, or full name, append a comment, unassign, hide/show
        detections in the UI, or set a verdict (true_positive, false_positive, ignored).
        At least one update parameter must be provided. Returns `[]` (empty list) on success; returns an error dict on failure.
        """
        # Validate mutually exclusive assignment parameters
        assignment_params = [assign_to_uuid, assign_to_user_id, assign_to_name]
        if sum(p is not None for p in assignment_params) > 1:
            return {"error": "Provide at most one of assign_to_uuid, assign_to_user_id, assign_to_name."}

        if unassign is True and any(p is not None for p in assignment_params):
            return {"error": "Cannot combine unassign with an assignment parameter."}

        if append_comment is not None and append_comment.strip() == "":
            return {"error": "append_comment must not be empty."}

        _valid_verdicts = {"true_positive", "false_positive", "ignored"}
        if verdict is not None and verdict not in _valid_verdicts:
            return {"error": f"verdict must be one of: {', '.join(sorted(_valid_verdicts))}."}

        _valid_statuses = {"new", "in_progress", "reopened", "closed"}
        if status is not None and status not in _valid_statuses:
            return {"error": f"status must be one of: {', '.join(sorted(_valid_statuses))}."}

        if not ids:
            return {"error": "At least one detection ID must be provided."}

        action_parameters: list[dict[str, Any]] = []

        str_params = {
            "update_status": status,
            "assign_to_uuid": assign_to_uuid,
            "assign_to_user_id": assign_to_user_id,
            "assign_to_name": assign_to_name,
            "append_comment": append_comment,
        }
        for name, value in str_params.items():
            if value is not None:
                action_parameters.append({"name": name, "value": value})

        # show_in_ui and unassign must be sent as strings — the API rejects JSON booleans
        if show_in_ui is not None:
            action_parameters.append({"name": "show_in_ui", "value": str(show_in_ui).lower()})
        if unassign is True:
            action_parameters.append({"name": "unassign", "value": "true"})
        if verdict is not None:
            action_parameters.append({"name": "add_tag", "value": verdict})

        if not action_parameters:
            return {"error": "At least one update parameter must be provided."}

        body = {
            "composite_ids": ids,
            "action_parameters": action_parameters,
        }

        return self._base_query_api_call(
            operation="PatchEntitiesAlertsV3",
            body_params=body,
            error_message="Failed to update detections",
            default_result=[],
        )
