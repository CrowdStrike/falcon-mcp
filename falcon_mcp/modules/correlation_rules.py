"""
Correlation Rules module for Falcon MCP Server.

This module provides tools for searching, creating, updating, publishing, and deleting
NG-SIEM Correlation Rules using the CrowdStrike Correlation Rules API.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.correlation_rules import SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION

logger = get_logger(__name__)


class CorrelationRulesModule(BaseModule):
    """Module for managing NG-SIEM Correlation Rules."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_correlation_rules,
            name="search_correlation_rules",
        )

        self._add_tool(
            server=server,
            method=self.get_correlation_rules,
            name="get_correlation_rules",
        )

        self._add_tool(
            server=server,
            method=self.create_correlation_rule,
            name="create_correlation_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_correlation_rule,
            name="update_correlation_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_correlation_rules,
            name="delete_correlation_rules",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.publish_correlation_rule,
            name="publish_correlation_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.export_correlation_rules,
            name="export_correlation_rules",
        )

        self._add_tool(
            server=server,
            method=self.import_correlation_rule,
            name="import_correlation_rule",
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
        fql_resource = TextResource(
            uri=AnyUrl("falcon://correlation-rules/fql-guide"),
            name="falcon_search_correlation_rules_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.",
            text=SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION,
        )
        self._add_resource(server, fql_resource)

    def search_correlation_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://correlation-rules/fql-guide` for syntax.",
            examples={"status:'enabled'+severity:>50", "tactic:'Execution'"},
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of rules to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort rules using FQL sort syntax. Example: 'last_updated_on.desc'",
            examples={"last_updated_on.desc", "name.asc", "severity.desc"},
        ),
        q: str | None = Field(
            default=None,
            description="Free-text match query that searches across all string fields.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search NG-SIEM Correlation Rules and return full rule details.

        Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
        Consult falcon://correlation-rules/fql-guide before constructing filter expressions.
        Returns full rule objects including search logic, notifications, and versioning info.
        """
        result = self._base_search_api_call(
            operation="combined_rules_get_v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search Correlation Rules",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result], filter, SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION
            )

        if not result:
            return self._format_fql_error_response(
                [], filter, SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION
            )

        return result

    def get_correlation_rules(
        self,
        ids: list[str] = Field(
            description="Rule IDs to retrieve. Use `falcon_search_correlation_rules` to find IDs.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve NG-SIEM Correlation Rules by ID.

        Use this when you already have rule IDs and need full details. For discovery by name,
        status, or severity use falcon_search_correlation_rules instead.
        Returns full rule objects including search logic, notifications, and version history.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to retrieve Correlation Rules.",
                    operation="entities_rules_get_v2",
                )
            ]

        result = self._base_get_by_ids(
            operation="entities_rules_get_v2",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_correlation_rule(
        self,
        name: str = Field(
            description="Name for the new detection rule.",
            examples={"Suspicious PowerShell Encoding", "Lateral Movement via WMI"},
        ),
        filter: str = Field(
            description=(
                "CQL (LogScale) query that defines the detection logic. "
                "This is the search expression evaluated against NG-SIEM events. "
                "Example: '#event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*'"
            ),
        ),
        severity: int = Field(
            ge=0,
            le=100,
            description="Severity score for alerts generated by this rule (0-100). Higher is more severe.",
            examples={25, 50, 75, 100},
        ),
        status: str = Field(
            default="enabled",
            description="Initial rule status. Allowed values: enabled, disabled.",
            examples={"enabled", "disabled"},
        ),
        lookback: str = Field(
            default="1h",
            description=(
                "Lookback window for event aggregation. "
                "Examples: '15m', '1h', '24h', '7d'."
            ),
            examples={"15m", "1h", "6h", "24h"},
        ),
        trigger_mode: str = Field(
            default="match_all",
            description=(
                "When to trigger an alert. Allowed values: match_all (trigger on every match), "
                "threshold (trigger when match count exceeds a threshold)."
            ),
            examples={"match_all", "threshold"},
        ),
        description: str | None = Field(
            default=None,
            description="Optional description explaining what the rule detects and why.",
        ),
        tactic: str | None = Field(
            default=None,
            description="MITRE ATT&CK tactic name. Example: 'Execution'",
            examples={"Execution", "Persistence", "Lateral Movement", "Exfiltration"},
        ),
        technique: str | None = Field(
            default=None,
            description="MITRE ATT&CK technique ID. Example: 'T1059'",
            examples={"T1059", "T1078", "T1021"},
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the rule is being created.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a new NG-SIEM Correlation Rule.

        Defines a CQL-based detection rule that runs continuously against NG-SIEM event data.
        The filter field contains the LogScale/CQL query — consult NG-SIEM query syntax before
        submitting. After creation, use falcon_publish_correlation_rule to make it active.
        """
        body: dict[str, Any] = {
            "name": name,
            "search": {
                "filter": filter,
                "lookback": lookback,
                "trigger_mode": trigger_mode,
            },
            "severity": severity,
            "status": status,
        }
        if description is not None:
            body["description"] = description
        if tactic is not None:
            body["tactic"] = tactic
        if technique is not None:
            body["technique"] = technique
        if comment is not None:
            body["comment"] = comment

        result = self._base_query_api_call(
            operation="entities_rules_post_v1",
            body_params=body,
            error_message="Failed to create Correlation Rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_correlation_rule(
        self,
        id: str = Field(
            description="ID of the rule to update. Retrieve from `falcon_search_correlation_rules`.",
        ),
        name: str | None = Field(
            default=None,
            description="New name for the rule.",
        ),
        description: str | None = Field(
            default=None,
            description="New description for the rule.",
        ),
        status: str | None = Field(
            default=None,
            description="New status. Allowed values: enabled, disabled.",
            examples={"enabled", "disabled"},
        ),
        severity: int | None = Field(
            default=None,
            ge=0,
            le=100,
            description="New severity score (0-100).",
        ),
        filter: str | None = Field(
            default=None,
            description="Updated CQL query for the detection logic.",
        ),
        lookback: str | None = Field(
            default=None,
            description="Updated lookback window. Examples: '1h', '24h'.",
        ),
        tactic: str | None = Field(
            default=None,
            description="Updated MITRE ATT&CK tactic name.",
        ),
        technique: str | None = Field(
            default=None,
            description="Updated MITRE ATT&CK technique ID.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the rule is being updated.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update an existing NG-SIEM Correlation Rule.

        Modify rule properties such as name, severity, status, or detection logic.
        Only fields provided are updated; omitted fields retain their current values.
        Use falcon_search_correlation_rules to retrieve the rule ID.
        """
        body: dict[str, Any] = {"id": id}

        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        if severity is not None:
            body["severity"] = severity
        if comment is not None:
            body["comment"] = comment
        if tactic is not None:
            body["tactic"] = tactic
        if technique is not None:
            body["technique"] = technique

        if filter is not None or lookback is not None:
            search: dict[str, Any] = {}
            if filter is not None:
                search["filter"] = filter
            if lookback is not None:
                search["lookback"] = lookback
            body["search"] = search

        result = self._base_query_api_call(
            operation="entities_rules_patch_v1",
            body_params=body,
            error_message="Failed to update Correlation Rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_correlation_rules(
        self,
        ids: list[str] = Field(
            description="IDs of the rules to delete. Retrieve from `falcon_search_correlation_rules`.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the rules are being deleted.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete NG-SIEM Correlation Rules by ID.

        Permanently removes the specified rules. Use falcon_search_correlation_rules to find
        rule IDs before deleting. This action cannot be undone.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to delete Correlation Rules.",
                    operation="entities_rules_delete_v1",
                )
            ]

        query_params: dict[str, Any] = {"ids": ids}
        if comment is not None:
            query_params["comment"] = comment

        result = self._base_query_api_call(
            operation="entities_rules_delete_v1",
            query_params=query_params,
            error_message="Failed to delete Correlation Rules",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def publish_correlation_rule(
        self,
        id: str = Field(
            description=(
                "Version ID of the rule to publish. "
                "Retrieve the version ID from `falcon_search_correlation_rules` or `falcon_get_correlation_rules`."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Publish an NG-SIEM Correlation Rule version to make it active.

        Promotes a draft or updated rule version so it begins evaluating live event data.
        Use falcon_search_correlation_rules to find the rule version ID to publish.
        """
        result = self._base_query_api_call(
            operation="entities_rule_versions_publish_patch_v1",
            body_params={"id": id},
            error_message="Failed to publish Correlation Rule version",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def export_correlation_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to select which rules to export. Exports all rules if omitted.",
            examples={"status:'enabled'", "tactic:'Execution'"},
        ),
        get_latest: bool = Field(
            default=True,
            description="Export only the latest version of each rule.",
        ),
        report_format: str = Field(
            default="json",
            description="Export format. Allowed values: json, yaml.",
            examples={"json", "yaml"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Export NG-SIEM Correlation Rules in JSON or YAML format.

        Use this to back up rules, migrate them between environments, or review rule
        logic in bulk. Returns the exported rule data as structured content.
        """
        body: dict[str, Any] = {
            "get_latest": get_latest,
            "report_format": report_format,
        }
        if filter is not None:
            body["filter"] = filter

        result = self._base_query_api_call(
            operation="entities_rule_versions_export_post_v1",
            body_params=body,
            error_message="Failed to export Correlation Rules",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def import_correlation_rule(
        self,
        rule: dict[str, Any] = Field(
            description=(
                "Rule definition to import. Must be a valid Correlation Rule object, "
                "such as one produced by `falcon_export_correlation_rules`."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Import an NG-SIEM Correlation Rule from a rule definition object.

        Use this to restore a previously exported rule or migrate a rule from another
        environment. The rule object should match the format produced by
        falcon_export_correlation_rules.
        """
        result = self._base_query_api_call(
            operation="entities_rule_versions_import_post_v1",
            body_params=rule,
            error_message="Failed to import Correlation Rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
