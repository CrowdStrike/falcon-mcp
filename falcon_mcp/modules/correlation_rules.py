"""Correlation Rules module for Falcon MCP Server."""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.correlation_rules import (
    SEARCH_CORRELATION_RULE_TEMPLATES_FQL_DOCUMENTATION,
    SEARCH_CORRELATION_RULES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)

_RULE_SEARCH_FIELDS = {
    "rule_id", "id", "name", "description", "severity", "status", "state",
    "template_id", "mitre_attack", "created_on", "last_updated_on", "user_id",
}

_TEMPLATE_SEARCH_FIELDS = {
    "id", "name", "description", "severity", "vendors", "mitre_attack",
    "author", "created_on", "last_updated_on",
}


def _slim(entity: dict, fields: set) -> dict:
    """Project an entity dict down to a specific set of fields."""
    return {k: v for k, v in entity.items() if k in fields}


class CorrelationRulesModule(BaseModule):
    """Module for managing NG-SIEM Correlation Rules."""

    def _find_existing_rule_by_name(self, name: str) -> dict | None:
        """Search for an existing published correlation rule with the given exact name.

        Returns the first matching rule dict, or None if no match is found.
        Returns None on API errors to avoid blocking deployment.
        """
        result, _ = self._base_search_with_meta(
            operation="combined_rules_get_v2",
            search_params={
                "filter": f"name:'{name}'+state:'published'",
                "limit": 1,
            },
            error_message="Failed to check for existing correlation rules",
        )

        if self._is_error(result) or not result:
            return None

        return result[0]

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
                destructiveHint=True,
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
            method=self.search_correlation_rule_templates,
            name="search_correlation_rule_templates",
        )

        self._add_tool(
            server=server,
            method=self.get_correlation_rule,
            name="get_correlation_rule",
        )

        self._add_tool(
            server=server,
            method=self.get_correlation_rule_template,
            name="get_correlation_rule_template",
        )

        self._add_tool(
            server=server,
            method=self.deploy_correlation_rule_template,
            name="deploy_correlation_rule_template",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
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

        template_fql_resource = TextResource(
            uri=AnyUrl("falcon://correlation-rule-templates/search/fql-guide"),
            name="falcon_search_correlation_rule_templates_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_correlation_rule_templates` tool.",
            text=SEARCH_CORRELATION_RULE_TEMPLATES_FQL_DOCUMENTATION,
        )
        self._add_resource(server, template_fql_resource)

    def search_correlation_rules(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://correlation-rules/search/fql-guide` for syntax. "
                "IMPORTANT: name/description substring searches require the ~* operator with * wildcards — "
                "e.g. name:~*'*powershell*' NOT name:'*powershell*'."
            ),
            examples={
                "status:'active'+severity:>50",
                "mitre_attack.tactic_id:'TA0001'",
                "name:~*'*powershell*'+status:'active'",
                "description:~*'*lateral movement*'",
            },
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
        """Search NG-SIEM Correlation Rules and return summary rule details.

        Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
        Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions.
        Returns summary rule objects (rule_id, name, description, severity, status, state, mitre_attack, template_id, user_id, created_on, last_updated_on); use the `rule_id` field when passing results to update or
        delete tools. Filter with state:'published' to get one result per rule.
        Use falcon_get_correlation_rule to retrieve the full rule object including the CQL query, schedule, and execution details.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

        IMPORTANT: This tool only returns rules that have already been deployed in the tenant.
        When results are empty or the user asks what rules they *can* or *should* enable,
        always follow up with falcon_search_correlation_rule_templates to surface pre-built
        detection templates that can be deployed. Templates represent the full catalog of
        available detections — a tenant with zero matching rules may still have many
        relevant templates ready to deploy.

        Severity mapping — use integers in API/FQL calls, show ONLY the name (never the integer) when presenting to the user:
        10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.
        """
        result, pagination = self._base_search_with_meta(
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

        slimmed = [_slim(r, _RULE_SEARCH_FIELDS) for r in (result or [])]
        return self._build_pagination_envelope(slimmed, pagination, filter)

    def get_correlation_rule(
        self,
        rule_id: str = Field(
            description=(
                "The rule_id of the correlation rule to retrieve. "
                "Use the rule_id field from falcon_search_correlation_rules results."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get full details for a single NG-SIEM Correlation Rule.

        Returns the complete rule object including the CQL query, schedule, execution
        history, notification config, and all metadata. Use this to inspect a rule
        before modifying it or to troubleshoot execution details.

        Severity mapping — use integers in API/FQL calls, show ONLY the name (never the integer) when presenting to the user:
        10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.
        """
        result, _ = self._base_search_with_meta(
            operation="combined_rules_get_v2",
            search_params={
                "filter": f"rule_id:'{rule_id}'",
                "limit": 1,
            },
            error_message="Failed to get Correlation Rule",
        )

        if self._is_error(result):
            return [result]

        if not result:
            return [_format_error_response(
                f"Correlation rule with rule_id '{rule_id}' not found.",
                operation="combined_rules_get_v2",
            )]

        return result

    def create_correlation_rule(
        self,
        customer_id: str | None = Field(
            default=None,
            description="CID of the tenant to create the rule in. Auto-resolved from the authenticated session when omitted.",
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
            examples={"summary", "verbose"},
        ),
        use_ingest_time: bool = Field(
            default=False,
            description="Use event ingest time instead of event timestamp for the lookback window.",
        ),
        description: str | None = Field(
            default=None,
            description="Optional description explaining what the rule detects and why.",
        ),
        mitre_attack: list[dict[str, str]] | None = Field(
            default=None,
            description=(
                "MITRE ATT&CK mapping as a list of objects with tactic_id and technique_id. "
                "Example: [{'tactic_id': 'TA0002', 'technique_id': 'T1059'}]"
            ),
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
        if customer_id is None:
            customer_id = self.client.cid
            if customer_id is None:
                return [_format_error_response(
                    "customer_id is required but was not provided and FALCON_CID "
                    "is not set. Set the FALCON_CID environment variable or pass "
                    "customer_id explicitly.",
                )]

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
                "use_ingest_time": use_ingest_time,
            },
            "operation": {
                "schedule": {
                    "definition": schedule,
                }
            },
        }

        if description is not None:
            body["description"] = description
        if mitre_attack is not None:
            body["mitre_attack"] = mitre_attack
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
            description="Rule ID to update. Use the `rule_id` field from `falcon_search_correlation_rules` results.",
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
            examples={"summary", "verbose"},
        ),
        use_ingest_time: bool | None = Field(
            default=None,
            description="Use event ingest time instead of event timestamp for the lookback window.",
        ),
        schedule: str | None = Field(
            default=None,
            description="Updated schedule definition (minimum: @every 0h5m). Example: '@every 1h30m'.",
            examples={"@every 1h0m", "@every 0h5m", "@every 1h30m", "@every 24h0m"},
        ),
        mitre_attack: list[dict[str, str]] | None = Field(
            default=None,
            description=(
                "Updated MITRE ATT&CK mapping as a list of objects with tactic_id and technique_id. "
                "Example: [{'tactic_id': 'TA0002', 'technique_id': 'T1059'}]"
            ),
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

        IMPORTANT — schedule and lookback interaction: when changing the schedule to a
        longer interval (less frequent), also update the lookback to preserve the original
        overlap (overlap = lookback − schedule interval). Otherwise the unchanged lookback
        becomes shorter than the new schedule, introducing gaps in detection coverage.
        For example, a rule with schedule=30m and lookback=40m has a 10m overlap; changing
        the schedule to 1h requires setting lookback to 1h10m to keep that 10m overlap.
        """
        schedule = unwrap_field_default(schedule)
        lookback = unwrap_field_default(lookback)

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
        if mitre_attack is not None:
            body["mitre_attack"] = mitre_attack
        if schedule is not None:
            body["operation"] = {"schedule": {"definition": schedule}}

        search_fields_set = (
            search_filter is not None
            or lookback is not None
            or trigger_mode is not None
            or use_ingest_time is not None
        )
        if search_fields_set:
            search: dict[str, Any] = {}
            if search_filter is not None:
                search["filter"] = search_filter
            if lookback is not None:
                search["lookback"] = lookback
            if trigger_mode is not None:
                search["trigger_mode"] = trigger_mode
            if use_ingest_time is not None:
                search["use_ingest_time"] = use_ingest_time
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
            description="Rule IDs to delete. Use the `rule_id` field from `falcon_search_correlation_rules` results.",
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

    def search_correlation_rule_templates(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://correlation-rule-templates/search/fql-guide` "
                "for syntax, MITRE ATT&CK tactic/technique ID mappings, and natural-language "
                "search strategies."
            ),
            examples={
                "mitre_attack.tactic_id:'TA0008'",
                "description:~*'*ransomware*'",
                "name:~*'*powershell*'",
            },
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of templates to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort templates. Options: 'created_on', 'created_on|desc', 'last_updated_on', 'last_updated_on|desc'.",
            examples={"last_updated_on|desc", "created_on"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search pre-built Correlation Rule templates and return summary template details.

        Use this to discover detection rule templates that can be deployed as live correlation
        rules. Describe what you want to detect — lateral movement, credential theft, ransomware,
        phishing, etc. — and consult falcon://correlation-rule-templates/search/fql-guide for
        MITRE ATT&CK tactic/technique ID mappings and natural-language search strategies.
        Returns summary template objects (id, name, description, severity, vendors, mitre_attack, author, created_on, last_updated_on); use the `id` field when passing results to the deploy tool.
        Responses include `pagination.total` (the total number of records matching the filter,
        or null when the API does not report a count) — use it to answer "how many" questions.
        Use falcon_get_correlation_rule_template to retrieve the full template including the CQL query, schedule, lookback, and trigger configuration.

        Each template object in the response has a `vendors` array listing which data sources
        it requires (e.g. vendors: ['CrowdStrike']). Note: `vendors` is a response field only —
        it is NOT a valid FQL filter field. To filter by vendor use the `vendor` field (singular):
        vendor:'Zscaler'. Templates with vendors: ['CrowdStrike'] use native Falcon sensor data
        and need no data connector. Other vendors require an active data connector. To check what
        data is available or what connectors are needed, see
        falcon://data-connectors/data-sources/mapping-guide.

        Severity mapping — use integers in API/FQL calls, show ONLY the name (never the integer) when presenting to the user:
        10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.
        """
        ids_result, pagination = self._base_search_with_meta(
            operation="queries_templates_get_v1Mixin0",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search Correlation Rule Templates",
        )

        if self._is_error(ids_result):
            return self._format_fql_error_response(
                [ids_result], filter, SEARCH_CORRELATION_RULE_TEMPLATES_FQL_DOCUMENTATION
            )

        if not ids_result:
            return self._build_pagination_envelope([], pagination, filter)

        entities = self._base_get_by_ids(
            operation="entities_templates_get_v1Mixin0",
            ids=ids_result,
            use_params=True,
        )

        if self._is_error(entities):
            return [entities]

        ordered = self._reorder_by_ids(ids_result, entities, id_field="id")

        slimmed = [_slim(e, _TEMPLATE_SEARCH_FIELDS) for e in ordered]
        return self._build_pagination_envelope(slimmed, pagination, filter)

    def get_correlation_rule_template(
        self,
        id: str = Field(
            description=(
                "The template ID to retrieve. "
                "Use the id field from falcon_search_correlation_rule_templates results."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get full details for a single Correlation Rule template.

        Returns the complete template object including the CQL query, schedule, lookback,
        trigger configuration, and license details. Use this to inspect a template's
        detection logic before deploying it.

        Severity mapping — use integers in API/FQL calls, show ONLY the name (never the integer) when presenting to the user:
        10=Informational, 30=Low, 50=Medium, 70=High, 90=Critical.
        """
        result = self._base_get_by_ids(
            operation="entities_templates_get_v1Mixin0",
            ids=[id],
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        if not result:
            return [_format_error_response(
                f"Correlation rule template with id '{id}' not found.",
                operation="entities_templates_get_v1Mixin0",
            )]

        return result

    def deploy_correlation_rule_template(
        self,
        template_id: str = Field(
            description=(
                "Template ID to deploy. Use the `id` field from "
                "`falcon_search_correlation_rule_templates` results."
            ),
        ),
        customer_id: str | None = Field(
            default=None,
            description="CID of the tenant to deploy the rule in. Auto-resolved from the authenticated session when omitted.",
        ),
        name: str | None = Field(
            default=None,
            description="Override the template's default rule name.",
        ),
        severity: int | None = Field(
            default=None,
            description="Override severity score. Must be one of: 10, 30, 50, 70, 90.",
            examples={10, 30, 50, 70, 90},
        ),
        status: str = Field(
            default="active",
            description="Initial rule status.",
            examples={"active", "inactive"},
        ),
        schedule: str | None = Field(
            default=None,
            description="Override the schedule (e.g. '@every 1h0m'). Uses template default if omitted.",
            examples={"@every 1h0m", "@every 0h5m", "@every 24h0m"},
        ),
        lookback: str | None = Field(
            default=None,
            description="Override the lookback window (e.g. '1h0m'). Uses template default if omitted.",
            examples={"1h0m", "24h0m"},
        ),
        trigger_mode: str | None = Field(
            default=None,
            description="Override trigger mode. Uses template default if omitted.",
            examples={"summary", "verbose"},
        ),
        description: str | None = Field(
            default=None,
            description="Override the template's default description.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment explaining why the template is being deployed.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Deploy a Correlation Rule template as a live detection rule.

        First fetches the template to get its defaults (CQL query, schedule, severity,
        MITRE mappings, etc.), then checks whether a rule with the same name already
        exists. If a duplicate is found, returns a structured response with the existing
        rule's details instead of creating a duplicate — the caller should ask the user
        whether to update the existing rule. Only template_id and customer_id are
        required — all other fields use the template's built-in values when omitted.

        Typical workflow:
        1. Use falcon_search_correlation_rule_templates to find a template
        2. Pass the template's `id` here along with your `customer_id`
        3. Optionally override name, severity, status, schedule, etc.
        Returns the created rule record on success, or a duplicate_found response
        when a rule with the same name already exists.
        """
        name = unwrap_field_default(name)
        severity = unwrap_field_default(severity)
        status = unwrap_field_default(status)
        schedule = unwrap_field_default(schedule)
        lookback = unwrap_field_default(lookback)
        trigger_mode = unwrap_field_default(trigger_mode)
        description = unwrap_field_default(description)
        comment = unwrap_field_default(comment)
        customer_id = unwrap_field_default(customer_id)

        if customer_id is None:
            customer_id = self.client.cid
            if customer_id is None:
                return [_format_error_response(
                    "customer_id is required but was not provided and FALCON_CID "
                    "is not set. Set the FALCON_CID environment variable or pass "
                    "customer_id explicitly.",
                )]

        template_result = self._base_get_by_ids(
            operation="entities_templates_get_v1Mixin0",
            ids=[template_id],
            use_params=True,
        )

        if self._is_error(template_result):
            return [template_result]

        if not template_result:
            return [
                _format_error_response(
                    f"Template '{template_id}' not found.",
                    operation="entities_templates_get_v1Mixin0",
                )
            ]

        template = template_result[0]
        effective_name = name if name is not None else template.get("name", "")

        # Check for an existing rule with the same name to avoid duplicates.
        existing_rule = self._find_existing_rule_by_name(effective_name)
        if existing_rule is not None:
            existing_id = existing_rule.get("rule_id", existing_rule.get("id", ""))
            return {
                "duplicate_found": True,
                "message": (
                    f"A correlation rule named '{effective_name}' already exists "
                    f"(rule_id: '{existing_id}'). To update the existing rule with "
                    f"the latest template settings, use falcon_update_correlation_rule "
                    f"with rule_id='{existing_id}'."
                ),
                "existing_rule": _slim(existing_rule, _RULE_SEARCH_FIELDS),
                "template_id": template_id,
            }

        template_search = template.get("search", {})
        template_operation = template.get("operation", {})
        template_schedule = template_operation.get("schedule", {})

        deploy_template: dict[str, Any] = {
            "template_id": template_id,
            "name": effective_name,
            "severity": severity if severity is not None else template.get("severity", 50),
            "status": status,
            "search": {
                "filter": template_search.get("filter", ""),
                "outcome": template_search.get("outcome", "detection"),
                "lookback": lookback
                if lookback is not None
                else template_search.get("lookback", "1h0m"),
                "trigger_mode": trigger_mode
                if trigger_mode is not None
                else template_search.get("trigger_mode", "summary"),
                "execution_mode": template_search.get("execution_mode", ""),
            },
            "operation": {
                "schedule": {
                    "definition": schedule
                    if schedule is not None
                    else template_schedule.get("definition", "@every 1h0m"),
                },
            },
        }

        if template.get("mitre_attack"):
            deploy_template["mitre_attack"] = template["mitre_attack"]

        if template.get("anomaly"):
            deploy_template["anomaly"] = template["anomaly"]

        if description is not None:
            deploy_template["description"] = description
        elif template.get("description"):
            deploy_template["description"] = template["description"]

        if comment is not None:
            deploy_template["comment"] = comment

        body = [{"customer_id": customer_id, "templates": [deploy_template]}]

        response = self.client.command("entities_templates_rules_post_v1", body=body)

        result = handle_api_response(
            response,
            operation="entities_templates_rules_post_v1",
            error_message="Failed to deploy Correlation Rule Template",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
