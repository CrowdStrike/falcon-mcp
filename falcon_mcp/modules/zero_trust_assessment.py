"""
Zero Trust Assessment module for Falcon MCP Server

This module provides tools for retrieving Zero Trust Assessment posture scores and sensor and OS
hardening signals for hosts.
"""

from typing import Any

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.base import BaseModule

SORT_ORDERS = ("asc", "desc")


def _build_score_filter(min_score: int | None, max_score: int | None) -> str:
    """Build the FQL the query endpoint requires from typed score bounds."""
    parts = []
    if min_score is not None:
        parts.append(f"score:>={min_score}")
    if max_score is not None:
        parts.append(f"score:<={max_score}")
    # The endpoint rejects a missing filter, and score:>=0 matches every assessed host.
    return "+".join(parts) if parts else "score:>=0"


def _missing_aids(requested: list[str], records: list[dict[str, Any]]) -> list[str]:
    """AIDs that came back with no assessment, preserving request order."""
    found = {r.get("aid") for r in records}
    return [aid for aid in requested if aid not in found]


class ZeroTrustAssessmentModule(BaseModule):
    """Module for Zero Trust Assessment operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_zta_assessments,
            name="search_zta_assessments",
        )

        self._add_tool(
            server=server,
            method=self.get_zta_assessments,
            name="get_zta_assessments",
        )

        self._add_tool(
            server=server,
            method=self.get_zta_audit,
            name="get_zta_audit",
        )

    def search_zta_assessments(
        self,
        min_score: int | None = Field(
            default=None,
            ge=0,
            le=100,
            description="Lowest Zero Trust score to include (0-100). Omit for no lower bound.",
        ),
        max_score: int | None = Field(
            default=None,
            ge=0,
            le=100,
            description=(
                "Highest Zero Trust score to include (0-100). Combine with `min_score` "
                "to select a range."
            ),
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of hosts to return. (Max: 1000)",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from a previous response's `pagination.next`.",
        ),
        sort_order: str = Field(
            default="asc",
            description="'asc' for weakest first, 'desc' for strongest first.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Zero Trust Assessment scores and return full assessment details.

        Use this to rank hosts by security posture: pass `max_score` to list the weakest
        hosts, `min_score` to list the strongest. Score is the only attribute this tool can
        select on, so start from `falcon_get_zta_assessments` when you already have an agent
        ID (AID) and from `falcon_search_hosts` when you have a hostname.
        Returns each host's Zero Trust score with its full sensor and OS hardening signals,
        in the standard pagination envelope; feed `pagination.next` back as `after`.

        Results name hosts only by AID, so pair this with `falcon_search_hosts` to report
        hostnames. Each record carries a long signal list, so raise `limit` deliberately.
        """
        # Resolve unset Pydantic Field defaults to avoid leaking FieldInfo objects (issue #384)
        min_score = unwrap_field_default(min_score)
        max_score = unwrap_field_default(max_score)
        limit = unwrap_field_default(limit)
        after = unwrap_field_default(after)
        sort_order = unwrap_field_default(sort_order)

        if sort_order not in SORT_ORDERS:
            return _format_error_response(
                f"Invalid sort_order '{sort_order}'. Valid values are: {', '.join(SORT_ORDERS)}."
            )

        if min_score is not None and max_score is not None and min_score > max_score:
            return _format_error_response(
                f"min_score ({min_score}) is greater than max_score ({max_score}), "
                "so no host can match."
            )

        fql = _build_score_filter(min_score, max_score)

        assessments, pagination = self._base_search_with_meta(
            operation="getAssessmentsByScoreV1",
            search_params={
                "filter": fql,
                "limit": limit,
                "after": after,
                "sort": f"score|{sort_order}",
            },
            error_message="Failed to search Zero Trust Assessment scores",
        )

        if self._is_error(assessments):
            return [assessments]

        # The query returns {aid, score} pairs rather than bare IDs.
        aids = [aid for record in assessments if (aid := record.get("aid"))]

        if not aids:
            return self._build_pagination_envelope([], pagination, fql)

        details = self._base_get_by_ids(
            operation="getAssessmentV1",
            ids=aids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(aids, details, id_field="aid")
        envelope = self._build_pagination_envelope(details, pagination, fql)

        # A miss here means the host stopped being assessed between the two calls.
        missing = _missing_aids(aids, details)
        if missing:
            envelope["not_found"] = missing

        return envelope

    def get_zta_assessments(
        self,
        ids: list[str] = Field(
            min_length=1,
            max_length=1000,
            description="One or more agent IDs (AIDs), 1-1000. Lowercase hex, case-sensitive.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get Zero Trust Assessment details for specific hosts by agent ID (AID).

        Use this when you already hold an AID: a detection reports one as its `device_id`, and
        `falcon_search_hosts` resolves a hostname to one. No Zero Trust tool accepts a
        hostname, so resolve the name with `falcon_search_hosts` first.
        Returns `results` holding one record per assessed host — the Zero Trust score plus the
        full sensor and OS hardening signals — and `not_found` listing the AIDs with no
        assessment.

        `not_found` is always present, even when empty, because the API reports an unknown or
        never-assessed AID by omitting its record from an otherwise successful response.
        """
        # Resolve unset Pydantic Field defaults to avoid leaking FieldInfo objects (issue #384)
        ids = unwrap_field_default(ids)

        details = self._base_get_by_ids(
            operation="getAssessmentV1",
            ids=ids,
            use_params=True,
        )

        if self._is_error(details):
            return details

        return {"results": details, "not_found": _missing_aids(ids, details)}

    def get_zta_audit(self) -> list[dict[str, Any]] | dict[str, Any]:
        """Get the tenant-wide Zero Trust Assessment summary.

        Use this to answer how the whole tenant scores, rather than which hosts score badly —
        it is a single CID-level rollup and carries no per-host data, so reach for
        `falcon_search_zta_assessments` when you need individual hosts.
        Returns one record with the assessed host count and average Zero Trust score for the
        tenant, broken down by platform.
        """
        result = self._base_search_api_call(
            operation="getAuditV1",
            search_params={},
            error_message="Failed to get the Zero Trust Assessment audit summary",
        )

        if self._is_error(result):
            return [result]

        return result
