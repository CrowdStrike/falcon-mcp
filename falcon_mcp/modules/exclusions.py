"""
Exclusions module for Falcon MCP Server.

This module provides a unified set of tools for managing CrowdStrike exclusions
across four types — IOA, Machine Learning, Sensor Visibility, and
Certificate-Based — behind a single `exclusion_type` discriminator. Per-type
helper methods absorb the body, field, sort, and limit differences so the tool
surface stays clean for the calling agent.

Required API Scopes:
- IOA Exclusions: read, write
- Machine Learning Exclusions: read, write (also covers certificate-based exclusions)
- Sensor Visibility Exclusions: read, write
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.exclusions import SEARCH_EXCLUSIONS_FQL_DOCUMENTATION

logger = get_logger(__name__)

# Valid exclusion types (the discriminator values exposed to the agent).
EXCLUSION_TYPES = ("ioa", "ml", "sensor_visibility", "certificate")


class ExclusionsModule(BaseModule):
    """Module for managing CrowdStrike exclusions across all four types."""

    # Per-type operation names, verified against the installed FalconPy SDK (1.6.2)
    # and the live API on 2026-06-03. IOA and ML use the latest v2 operations;
    # Sensor Visibility and Certificate-Based have no v2 and use v1.
    _OPERATIONS: dict[str, dict[str, str]] = {
        "ioa": {
            "query": "ss_ioa_exclusions_search_v2",
            "get": "ss_ioa_exclusions_get_v2",
            "create": "ss_ioa_exclusions_create_v2",
            "update": "ss_ioa_exclusions_update_v2",
            "delete": "ss_ioa_exclusions_delete_v2",
        },
        "ml": {
            "query": "exclusions_search_v2",
            "get": "exclusions_get_v2",
            "create": "exclusions_create_v2",
            "update": "exclusions_update_v2",
            "delete": "exclusions_delete_v2",
        },
        "sensor_visibility": {
            "query": "querySensorVisibilityExclusionsV1",
            "get": "getSensorVisibilityExclusionsV1",
            "create": "createSVExclusionsV1",
            "update": "updateSensorVisibilityExclusionsV1",
            "delete": "deleteSensorVisibilityExclusionsV1",
        },
        "certificate": {
            "query": "cb_exclusions_query_v1",
            "get": "cb_exclusions_get_v1",
            "create": "cb_exclusions_create_v1",
            "update": "cb_exclusions_update_v1",
            "delete": "cb_exclusions_delete_v1",
        },
    }

    # Body key used for host-group scoping, per type. The public tool exposes a
    # single ``host_groups`` param that maps to the right key here.
    _GROUP_BODY_KEY = {
        "ioa": "host_groups",
        "ml": "groups",
        "sensor_visibility": "groups",
        "certificate": "host_groups",
    }

    # Limit caps per type (certificate query caps at 100; others at 500).
    _LIMIT_CAP = {
        "ioa": 500,
        "ml": 500,
        "sensor_visibility": 500,
        "certificate": 100,
    }

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_exclusions,
            name="search_exclusions",
        )

        self._add_tool(
            server=server,
            method=self.create_exclusion,
            name="create_exclusion",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_exclusion,
            name="update_exclusion",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_exclusions,
            name="delete_exclusions",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.get_certificate_details,
            name="get_certificate_details",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_exclusions_fql_resource = TextResource(
            uri=AnyUrl("falcon://exclusions/search/fql-guide"),
            name="falcon_search_exclusions_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_exclusions` tool.",
            text=SEARCH_EXCLUSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_exclusions_fql_resource,
        )

    # ---- Normalizers / validators -------------------------------------------------

    def _validate_exclusion_type(self, exclusion_type: str) -> dict[str, Any] | None:
        """Return an error dict if exclusion_type is invalid, else None."""
        if exclusion_type not in self._OPERATIONS:
            return _format_error_response(
                f"Invalid exclusion_type '{exclusion_type}'. "
                f"Valid values are: {', '.join(EXCLUSION_TYPES)}.",
            )
        return None

    def _normalize_sort(self, exclusion_type: str, sort: str | None) -> str | None:
        """Append a `.desc` direction for types that require one.

        IOA, ML, and Sensor Visibility expect a direction suffix; certificate
        tolerates a bare field name and is passed through unchanged.
        """
        if not sort or exclusion_type == "certificate":
            return sort

        lowered = sort.lower()
        has_direction = (
            lowered.endswith(".asc")
            or lowered.endswith(".desc")
            or lowered.endswith("|asc")
            or lowered.endswith("|desc")
        )
        if has_direction:
            return sort
        return f"{sort}.desc"

    def _clamp_limit(self, exclusion_type: str, limit: int) -> int:
        """Clamp limit to the per-type cap (certificate caps at 100, others 500)."""
        cap = self._LIMIT_CAP[exclusion_type]
        if limit > cap:
            return cap
        return limit

    def _resolve_groups(
        self, exclusion_type: str, host_groups: list[str] | None
    ) -> tuple[str, list[str]] | None:
        """Map the unified host_groups param to the per-type body key.

        Returns a (body_key, value) tuple, or None when no host groups were
        provided.
        """
        if host_groups is None:
            return None
        return self._GROUP_BODY_KEY[exclusion_type], host_groups

    # ---- Search -------------------------------------------------------------------

    def search_exclusions(
        self,
        exclusion_type: str = Field(
            description=(
                "Exclusion type to search. One of: 'ioa' (indicator of attack), "
                "'ml' (machine learning), 'sensor_visibility', 'certificate' "
                "(certificate-based)."
            ),
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://exclusions/search/fql-guide` for syntax (fields vary by type).",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of exclusions to return. Capped at 100 for 'certificate', 500 otherwise.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression. See `falcon://exclusions/search/fql-guide`. A `.desc` direction is added automatically for ioa/ml/sensor_visibility when omitted.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of the result set from which to return IDs.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search exclusions of a given type and return full exclusion records.

        Use this to find IOA, machine learning, sensor visibility, or
        certificate-based exclusions by name, value, scope, or timestamp. The
        `exclusion_type` parameter selects which exclusion API is queried.
        Consult falcon://exclusions/search/fql-guide before constructing filter
        expressions — the available fields differ per type. Returns full
        exclusion records including id, scope, and timestamps.
        """
        type_error = self._validate_exclusion_type(exclusion_type)
        if type_error is not None:
            return [type_error]

        return self._search_by_type(exclusion_type, filter, limit, sort, offset)

    def _search_by_type(
        self,
        exclusion_type: str,
        filter: str | None,
        limit: int,
        sort: str | None,
        offset: int | None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Shared two-step search (query IDs -> fetch details) for an exclusion type."""
        ids = self._base_search_api_call(
            operation=self._OPERATIONS[exclusion_type]["query"],
            search_params={
                "filter": filter,
                "limit": self._clamp_limit(exclusion_type, limit),
                "sort": self._normalize_sort(exclusion_type, sort),
                "offset": offset,
            },
            error_message=f"Failed to search {exclusion_type} exclusions",
        )

        if self._is_error(ids):
            return self._format_fql_error_response(
                [ids], filter, SEARCH_EXCLUSIONS_FQL_DOCUMENTATION
            )

        if not ids:
            return self._format_fql_error_response(
                [], filter, SEARCH_EXCLUSIONS_FQL_DOCUMENTATION
            )

        details = self._base_get_by_ids(
            operation=self._OPERATIONS[exclusion_type]["get"],
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order in case the get endpoint reorders results.
        return self._reorder_by_ids(ids, details, id_field="id")

    # ---- Body builders ------------------------------------------------------------

    def _build_ioa_body(
        self,
        *,
        name: str | None,
        pattern_id: str | None,
        ifn_regex: str | None,
        cl_regex: str | None,
        parent_ifn_regex: str | None,
        parent_cl_regex: str | None,
        grandparent_ifn_regex: str | None,
        grandparent_cl_regex: str | None,
        host_groups: list[str] | None,
        applied_globally: bool | None,
        description: str | None,
        comment: str | None,
        exclusion_id: str | None = None,
    ) -> dict[str, Any]:
        """Build the IOA v2 exclusion object (returned wrapped) or an error dict."""
        if not name or not pattern_id or not ifn_regex or not cl_regex:
            return _format_error_response(
                "IOA exclusions require 'name', 'pattern_id' (a real existing IOA "
                "rule pattern), 'ifn_regex' (non-empty), and 'cl_regex' (non-empty).",
                operation=self._OPERATIONS["ioa"]["create"],
            )

        if ifn_regex == ".*" and cl_regex == ".*":
            return _format_error_response(
                "IOA exclusion rejected: 'ifn_regex' and 'cl_regex' cannot both be "
                "'.*' (this would exclude everything). Provide more specific regexes.",
                operation=self._OPERATIONS["ioa"]["create"],
            )

        exclusion: dict[str, Any] = {
            "name": name,
            "pattern_id": pattern_id,
            "ifn_regex": ifn_regex,
            "cl_regex": cl_regex,
        }
        optional = {
            "parent_ifn_regex": parent_ifn_regex,
            "parent_cl_regex": parent_cl_regex,
            "grandparent_ifn_regex": grandparent_ifn_regex,
            "grandparent_cl_regex": grandparent_cl_regex,
            "applied_globally": applied_globally,
            "description": description,
            "comment": comment,
        }
        for key, value in optional.items():
            if value is not None:
                exclusion[key] = value

        groups = self._resolve_groups("ioa", host_groups)
        if groups is not None:
            exclusion[groups[0]] = groups[1]

        if exclusion_id is not None:
            exclusion["id"] = exclusion_id

        return {"exclusions": [exclusion]}

    def _build_ml_body(
        self,
        *,
        value: str | None,
        excluded_from: list[str] | None,
        host_groups: list[str] | None,
        applied_globally: bool | None,
        is_descendant_process: bool | None,
        comment: str | None,
        exclusion_id: str | None = None,
    ) -> dict[str, Any]:
        """Build the ML v2 exclusion object (returned wrapped) or an error dict."""
        if not value:
            return _format_error_response(
                "Machine learning exclusions require a 'value' (the path or pattern "
                "to exclude).",
                operation=self._OPERATIONS["ml"]["create"],
            )

        exclusion: dict[str, Any] = {"value": value}
        optional = {
            "excluded_from": excluded_from,
            "applied_globally": applied_globally,
            "is_descendant_process": is_descendant_process,
            "comment": comment,
        }
        for key, opt_value in optional.items():
            if opt_value is not None:
                exclusion[key] = opt_value

        groups = self._resolve_groups("ml", host_groups)
        if groups is not None:
            exclusion[groups[0]] = groups[1]

        if exclusion_id is not None:
            exclusion["id"] = exclusion_id

        return {"exclusions": [exclusion]}

    def _build_sv_body(
        self,
        *,
        value: str | None,
        host_groups: list[str] | None,
        applied_globally: bool | None,
        comment: str | None,
        exclusion_id: str | None = None,
    ) -> dict[str, Any]:
        """Build the Sensor Visibility v1 flat body or an error dict."""
        if not value:
            return _format_error_response(
                "Sensor visibility exclusions require a 'value' (the path or pattern "
                "to exclude).",
                operation=self._OPERATIONS["sensor_visibility"]["create"],
            )

        if not host_groups:
            return _format_error_response(
                "Sensor visibility exclusions require a non-empty 'host_groups' list, "
                "even when applied_globally is true.",
                operation=self._OPERATIONS["sensor_visibility"]["create"],
            )

        body: dict[str, Any] = {"value": value}
        if applied_globally is not None:
            body["applied_globally"] = applied_globally
        if comment is not None:
            body["comment"] = comment

        groups = self._resolve_groups("sensor_visibility", host_groups)
        if groups is not None:
            body[groups[0]] = groups[1]

        if exclusion_id is not None:
            body["id"] = exclusion_id

        return body

    def _build_cert_body(
        self,
        *,
        name: str | None,
        certificate: dict[str, Any] | None,
        status: str | None,
        host_groups: list[str] | None,
        applied_globally: bool | None,
        description: str | None,
        comment: str | None,
        exclusion_id: str | None = None,
    ) -> dict[str, Any]:
        """Build the Certificate-Based v1 exclusion object (returned wrapped) or an error dict."""
        if not name or not certificate:
            return _format_error_response(
                "Certificate-based exclusions require a 'name' and a 'certificate' "
                "dict (with issuer, subject, serial, thumbprint, valid_from, valid_to). "
                "Use falcon_get_certificate_details to look up a certificate first.",
                operation=self._OPERATIONS["certificate"]["create"],
            )

        if status not in ("enabled", "disabled"):
            return _format_error_response(
                "Certificate-based exclusions require 'status' to be either "
                "'enabled' or 'disabled'.",
                operation=self._OPERATIONS["certificate"]["create"],
            )

        exclusion: dict[str, Any] = {
            "name": name,
            "certificate": certificate,
            "status": status,
        }
        optional = {
            "applied_globally": applied_globally,
            "description": description,
            "comment": comment,
        }
        for key, value in optional.items():
            if value is not None:
                exclusion[key] = value

        groups = self._resolve_groups("certificate", host_groups)
        if groups is not None:
            exclusion[groups[0]] = groups[1]

        if exclusion_id is not None:
            exclusion["id"] = exclusion_id

        return {"exclusions": [exclusion]}

    def _build_body(
        self,
        exclusion_type: str,
        *,
        exclusion_id: str | None,
        name: str | None,
        value: str | None,
        pattern_id: str | None,
        ifn_regex: str | None,
        cl_regex: str | None,
        parent_ifn_regex: str | None,
        parent_cl_regex: str | None,
        grandparent_ifn_regex: str | None,
        grandparent_cl_regex: str | None,
        certificate: dict[str, Any] | None,
        status: str | None,
        excluded_from: list[str] | None,
        is_descendant_process: bool | None,
        host_groups: list[str] | None,
        applied_globally: bool | None,
        description: str | None,
        comment: str | None,
    ) -> dict[str, Any]:
        """Dispatch to the matching per-type body builder."""
        if exclusion_type == "ioa":
            return self._build_ioa_body(
                name=name,
                pattern_id=pattern_id,
                ifn_regex=ifn_regex,
                cl_regex=cl_regex,
                parent_ifn_regex=parent_ifn_regex,
                parent_cl_regex=parent_cl_regex,
                grandparent_ifn_regex=grandparent_ifn_regex,
                grandparent_cl_regex=grandparent_cl_regex,
                host_groups=host_groups,
                applied_globally=applied_globally,
                description=description,
                comment=comment,
                exclusion_id=exclusion_id,
            )
        if exclusion_type == "ml":
            return self._build_ml_body(
                value=value,
                excluded_from=excluded_from,
                host_groups=host_groups,
                applied_globally=applied_globally,
                is_descendant_process=is_descendant_process,
                comment=comment,
                exclusion_id=exclusion_id,
            )
        if exclusion_type == "sensor_visibility":
            return self._build_sv_body(
                value=value,
                host_groups=host_groups,
                applied_globally=applied_globally,
                comment=comment,
                exclusion_id=exclusion_id,
            )
        return self._build_cert_body(
            name=name,
            certificate=certificate,
            status=status,
            host_groups=host_groups,
            applied_globally=applied_globally,
            description=description,
            comment=comment,
            exclusion_id=exclusion_id,
        )

    # ---- Create / Update ----------------------------------------------------------

    def create_exclusion(
        self,
        exclusion_type: str = Field(
            description=(
                "Exclusion type to create. One of: 'ioa', 'ml', "
                "'sensor_visibility', 'certificate'."
            ),
        ),
        name: str | None = Field(
            default=None,
            description="Exclusion name. Required for 'ioa' and 'certificate'.",
        ),
        value: str | None = Field(
            default=None,
            description="Excluded path or pattern. Required for 'ml' and 'sensor_visibility'.",
        ),
        pattern_id: str | None = Field(
            default=None,
            description="IOA rule pattern ID to exclude (a real existing pattern). Required for 'ioa'.",
        ),
        ifn_regex: str | None = Field(
            default=None,
            description="IOA image file name regex. Required (non-empty) for 'ioa'.",
        ),
        cl_regex: str | None = Field(
            default=None,
            description="IOA command line regex. Required (non-empty) for 'ioa'.",
        ),
        parent_ifn_regex: str | None = Field(
            default=None,
            description="IOA parent image file name regex. Optional, 'ioa' only.",
        ),
        parent_cl_regex: str | None = Field(
            default=None,
            description="IOA parent command line regex. Optional, 'ioa' only.",
        ),
        grandparent_ifn_regex: str | None = Field(
            default=None,
            description="IOA grandparent image file name regex. Optional, 'ioa' only.",
        ),
        grandparent_cl_regex: str | None = Field(
            default=None,
            description="IOA grandparent command line regex. Optional, 'ioa' only.",
        ),
        certificate: dict[str, Any] | None = Field(
            default=None,
            description="Certificate dict (issuer, subject, serial, thumbprint, valid_from, valid_to). Required for 'certificate'.",
        ),
        status: str | None = Field(
            default=None,
            description="Certificate exclusion status: 'enabled' or 'disabled'. Required for 'certificate'.",
        ),
        excluded_from: list[str] | None = Field(
            default=None,
            description="ML exclusion targets, e.g. ['blocking']. Optional, 'ml' only.",
        ),
        is_descendant_process: bool | None = Field(
            default=None,
            description="Whether the ML exclusion applies to descendant processes. Optional, 'ml' only.",
        ),
        host_groups: list[str] | None = Field(
            default=None,
            description="Host group IDs to scope the exclusion. Required (non-empty) for 'sensor_visibility'; optional for other types.",
        ),
        applied_globally: bool | None = Field(
            default=None,
            description="Whether the exclusion applies to all hosts.",
        ),
        description: str | None = Field(
            default=None,
            description="Exclusion description. Applies to 'ioa' and 'certificate'.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment for the exclusion.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an exclusion of the given type.

        The `exclusion_type` selects which fields are required: 'ioa' needs name,
        pattern_id, ifn_regex, and cl_regex; 'ml' and 'sensor_visibility' need
        value (sensor_visibility also needs host_groups); 'certificate' needs
        name, certificate, and status. Invalid or missing fields return a guiding
        error before any API call. Returns the created exclusion record(s).
        """
        type_error = self._validate_exclusion_type(exclusion_type)
        if type_error is not None:
            return [type_error]

        body = self._build_body(
            exclusion_type,
            exclusion_id=None,
            name=name,
            value=value,
            pattern_id=pattern_id,
            ifn_regex=ifn_regex,
            cl_regex=cl_regex,
            parent_ifn_regex=parent_ifn_regex,
            parent_cl_regex=parent_cl_regex,
            grandparent_ifn_regex=grandparent_ifn_regex,
            grandparent_cl_regex=grandparent_cl_regex,
            certificate=certificate,
            status=status,
            excluded_from=excluded_from,
            is_descendant_process=is_descendant_process,
            host_groups=host_groups,
            applied_globally=applied_globally,
            description=description,
            comment=comment,
        )

        if self._is_error(body):
            return [body]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[exclusion_type]["create"],
            body_params=body,
            error_message=f"Failed to create {exclusion_type} exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_exclusion(
        self,
        exclusion_type: str = Field(
            description=(
                "Exclusion type to update. One of: 'ioa', 'ml', "
                "'sensor_visibility', 'certificate'."
            ),
        ),
        id: str | None = Field(
            default=None,
            description="ID of the exclusion to update. Required.",
        ),
        name: str | None = Field(
            default=None,
            description="Exclusion name. Required for 'ioa' and 'certificate'.",
        ),
        value: str | None = Field(
            default=None,
            description="Excluded path or pattern. Required for 'ml' and 'sensor_visibility'.",
        ),
        pattern_id: str | None = Field(
            default=None,
            description="IOA rule pattern ID. Required for 'ioa'.",
        ),
        ifn_regex: str | None = Field(
            default=None,
            description="IOA image file name regex. Required (non-empty) for 'ioa'.",
        ),
        cl_regex: str | None = Field(
            default=None,
            description="IOA command line regex. Required (non-empty) for 'ioa'.",
        ),
        parent_ifn_regex: str | None = Field(
            default=None,
            description="IOA parent image file name regex. Optional, 'ioa' only.",
        ),
        parent_cl_regex: str | None = Field(
            default=None,
            description="IOA parent command line regex. Optional, 'ioa' only.",
        ),
        grandparent_ifn_regex: str | None = Field(
            default=None,
            description="IOA grandparent image file name regex. Optional, 'ioa' only.",
        ),
        grandparent_cl_regex: str | None = Field(
            default=None,
            description="IOA grandparent command line regex. Optional, 'ioa' only.",
        ),
        certificate: dict[str, Any] | None = Field(
            default=None,
            description="Certificate dict. Required for 'certificate'.",
        ),
        status: str | None = Field(
            default=None,
            description="Certificate exclusion status: 'enabled' or 'disabled'. Required for 'certificate'.",
        ),
        excluded_from: list[str] | None = Field(
            default=None,
            description="ML exclusion targets, e.g. ['blocking']. Optional, 'ml' only.",
        ),
        is_descendant_process: bool | None = Field(
            default=None,
            description="Whether the ML exclusion applies to descendant processes. Optional, 'ml' only.",
        ),
        host_groups: list[str] | None = Field(
            default=None,
            description="Host group IDs to scope the exclusion. Required (non-empty) for 'sensor_visibility'; optional for other types.",
        ),
        applied_globally: bool | None = Field(
            default=None,
            description="Whether the exclusion applies to all hosts.",
        ),
        description: str | None = Field(
            default=None,
            description="Exclusion description. Applies to 'ioa' and 'certificate'.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment for the exclusion.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an existing exclusion of the given type.

        Provide the `id` of the exclusion plus the same fields used when creating
        that type. All four types update via HTTP PATCH. Invalid or missing
        fields return a guiding error before any API call. Returns the updated
        exclusion record(s).
        """
        type_error = self._validate_exclusion_type(exclusion_type)
        if type_error is not None:
            return [type_error]

        if not id:
            return [
                _format_error_response(
                    "An exclusion 'id' is required to update an exclusion.",
                    operation=self._OPERATIONS[exclusion_type]["update"],
                )
            ]

        body = self._build_body(
            exclusion_type,
            exclusion_id=id,
            name=name,
            value=value,
            pattern_id=pattern_id,
            ifn_regex=ifn_regex,
            cl_regex=cl_regex,
            parent_ifn_regex=parent_ifn_regex,
            parent_cl_regex=parent_cl_regex,
            grandparent_ifn_regex=grandparent_ifn_regex,
            grandparent_cl_regex=grandparent_cl_regex,
            certificate=certificate,
            status=status,
            excluded_from=excluded_from,
            is_descendant_process=is_descendant_process,
            host_groups=host_groups,
            applied_globally=applied_globally,
            description=description,
            comment=comment,
        )

        if self._is_error(body):
            return [body]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[exclusion_type]["update"],
            body_params=body,
            error_message=f"Failed to update {exclusion_type} exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    # ---- Delete -------------------------------------------------------------------

    def delete_exclusions(
        self,
        exclusion_type: str = Field(
            description=(
                "Exclusion type to delete. One of: 'ioa', 'ml', "
                "'sensor_visibility', 'certificate'."
            ),
        ),
        ids: list[str] | None = Field(
            default=None,
            description="IDs of the exclusions to delete. Required (non-empty).",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment describing why the exclusions are being deleted.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete one or more exclusions of the given type.

        Provide the `exclusion_type` and a non-empty list of exclusion `ids`.
        Returns the API response for the deletion.
        """
        type_error = self._validate_exclusion_type(exclusion_type)
        if type_error is not None:
            return [type_error]

        if not ids:
            return [
                _format_error_response(
                    "A non-empty 'ids' list is required to delete exclusions.",
                    operation=self._OPERATIONS[exclusion_type]["delete"],
                )
            ]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[exclusion_type]["delete"],
            query_params={"ids": ids, "comment": comment},
            error_message=f"Failed to delete {exclusion_type} exclusions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_certificate_details(
        self,
        sha256: str = Field(
            description="SHA256 hash of the file whose code-signing certificate should be looked up.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve the code-signing certificate metadata for a file by SHA256.

        Use this as the pre-flight lookup before building a certificate-based
        exclusion: it returns the file's signing certificate details (issuer,
        subject, serial, thumbprint, validity window) which you then pass as the
        `certificate` argument to falcon_create_exclusion. Returns certificate
        metadata for the given hash.
        """
        details = self._base_get_by_ids(
            operation="certificates_get_v1",
            ids=[sha256],
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details
