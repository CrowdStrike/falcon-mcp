"""Correlation Rules module for Falcon MCP Server."""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.correlation_rules import SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION

logger = get_logger(__name__)


class CorrelationRulesModule(BaseModule):
    """Module for managing NG-SIEM Correlation Rules."""

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(
            server=server,
            method=self.search_correlation_rules,
            name="search_correlation_rules",
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

    def register_resources(self, server: FastMCP) -> None:
        fql_resource = TextResource(
            uri=AnyUrl("falcon://correlation-rules/search/fql-guide"),
            name="falcon_search_correlation_rules_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.",
            text=SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION,
        )
        self._add_resource(server, fql_resource)

    def search_correlation_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://correlation-rules/search/fql-guide` for syntax.",
            examples={"status:'active'+severity:>50", "tactic:'TA0001'"},
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
            examples={"last_updated_on.desc", "created_on.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search NG-SIEM Correlation Rules and return full rule details.

        Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
        Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions.
        Returns full rule objects including all versions; filter with state:'published' to get
        one result per rule. Returns search logic, schedule, and versioning info.
        """
        result = self._base_search_api_call(
            operation="combined_rules_get_v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
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

    def create_correlation_rule(
        self,
        customer_id: str = Field(
            description="CID of the tenant to create the rule in.",
        ),
        name: str = Field(
            description="Name for the new detection rule.",
            examples={"Suspicious PowerShell Encoding", "Lateral Movement via WMI"},
        ),
        search_filter: str = Field(
            description=(
                "CQL query that defines the detection logic evaluated against NG-SIEM events. "
                "Example: '#event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*'"
            ),
        ),
        severity: int = Field(
            description="Severity score for alerts generated by this rule. Must be one of: 10, 30, 50, 70, 90.",
            examples={10, 30, 50, 70, 90},
        ),
        search_outcome: str = Field(
            default="detection",
            description="Outcome type for rule matches.",
            examples={"detection", "case"},
        ),
        lookback: str = Field(
            default="1h0m",
            description="Lookback window for event aggregation. Example: '1h0m', '24h0m'.",
            examples={"1h0m", "24h0m", "7d0h0m"},
        ),
        schedule: str = Field(
            default="@every 1h0m",
            description="Schedule definition for rule evaluation (minimum: @every 0h5m). Example: '@every 1h0m'.",
            examples={"@every 1h0m", "@every 0h5m", "@every 24h0m"},
        ),
        status: str = Field(
            default="active",
            description="Initial rule status.",
            examples={"active", "inactive"},
        ),
        trigger_mode: str = Field(
            default="summary",
            description="How alerts are triggered per evaluation window.",
            examples={"summary", "per_event"},
        ),
        description: str | None = Field(
            default=None,
            description="Optional description explaining what the rule detects and why.",
        ),
        tactic: str | None = Field(
            default=None,
            description="MITRE ATT&CK tactic ID. Example: 'TA0001'",
            examples={"TA0001", "TA0002", "TA0008"},
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

        Wraps a user-provided CQL query as a scheduled detection rule. The caller must
        supply the CQL query — use falcon_search_ngsiem to test queries before creating rules.
        Returns the created rule record on success.
        """
        body: dict[str, Any] = {
            "customer_id": customer_id,
            "name": name,
            "severity": severity,
            "status": status,
            "search": {
                "filter": search_filter,
                "outcome": search_outcome,
                "lookback": lookback,
                "trigger_mode": trigger_mode,
            },
            "operation": {
                "schedule": {
                    "definition": schedule,
                }
            },
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
        rule_id: str = Field(
            description="Rule ID to update. Retrieve from `falcon_search_correlation_rules`.",
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
            description="New status.",
            examples={"active", "inactive"},
        ),
        severity: int | None = Field(
            default=None,
            description="New severity score. Must be one of: 10, 30, 50, 70, 90.",
        ),
        search_filter: str | None = Field(
            default=None,
            description="Updated CQL query for the detection logic.",
        ),
        lookback: str | None = Field(
            default=None,
            description="Updated lookback window. Example: '1h0m', '24h0m'.",
        ),
        trigger_mode: str | None = Field(
            default=None,
            description="Updated trigger mode.",
            examples={"summary", "per_event"},
        ),
        tactic: str | None = Field(
            default=None,
            description="Updated MITRE ATT&CK tactic ID. Example: 'TA0001'",
        ),
        technique: str | None = Field(
            default=None,
            description="Updated MITRE ATT&CK technique ID. Example: 'T1059'",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the rule is being updated.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update an existing NG-SIEM Correlation Rule.

        Modifies fields on the rule and auto-publishes a new version — no separate publish
        step needed. To enable/disable a rule, set status to 'active' or 'inactive'.
        Only provided fields are changed; omitted fields retain current values.
        """
        # PATCH API takes rule_id in the "id" body field
        body: dict[str, Any] = {"id": rule_id}

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

        if search_filter is not None or lookback is not None or trigger_mode is not None:
            search: dict[str, Any] = {}
            if search_filter is not None:
                search["filter"] = search_filter
            if lookback is not None:
                search["lookback"] = lookback
            if trigger_mode is not None:
                search["trigger_mode"] = trigger_mode
            body["search"] = search

        # PATCH endpoint requires body as a list of rule dicts
        response = self.client.command("entities_rules_patch_v1", body=[body])

        result = handle_api_response(
            response,
            operation="entities_rules_patch_v1",
            error_message="Failed to update Correlation Rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_correlation_rules(
        self,
        ids: list[str] = Field(
            description="Rule IDs to delete. Retrieve from `falcon_search_correlation_rules`.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the rules are being deleted.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Permanently delete NG-SIEM Correlation Rules by rule ID.

        Removes the specified rules and all their versions. This action cannot be undone —
        use falcon_search_correlation_rules to confirm IDs before deleting. Returns an
        empty list on success.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to delete Correlation Rules.",
                    operation="entities_rules_delete_v1",
                )
            ]

        result = self._base_query_api_call(
            operation="entities_rules_delete_v1",
            query_params={"ids": ids, "comment": comment},
            error_message="Failed to delete Correlation Rules",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
