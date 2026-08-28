"""IOM findings and CSPM suppression rule tools mixin for the Cloud Security module."""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from falcon_mcp.resources.cloud import CSPM_IOM_FINDINGS_FQL_DOCUMENTATION


class _CloudIomMixin(_CloudBase):
    """Tools for querying IOM findings and managing CSPM suppression rules."""

    def register_tools(self, server: FastMCP) -> None:
        super().register_tools(server)
        self._add_tool(server=server, method=self.search_iom_findings, name="search_iom_findings")
        self._add_tool(server=server, method=self.search_cspm_suppression_rules, name="search_cspm_suppression_rules")
        self._add_tool(
            server=server,
            method=self.create_cspm_suppression_rule,
            name="create_cspm_suppression_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_cspm_suppression_rules,
            name="delete_cspm_suppression_rules",
            annotations=ToolAnnotations(
                readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        super().register_resources(server)
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://cloud/cspm-iom-findings/fql-guide"),
            name="falcon_search_iom_findings_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.",
            text=CSPM_IOM_FINDINGS_FQL_DOCUMENTATION,
        ))

    def search_iom_findings(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression."
                " See `falcon://cloud/cspm-iom-findings/fql-guide` for syntax."
            ),
            examples=["severity:'critical'+status:'open'", "cloud_provider:'aws'+service:'S3'"],
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description=(
                "The maximum number of IOM findings to return (default: 100; max: 1000)."
                " Use with the offset parameter to manage pagination."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return findings.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent(
                """
                Sort IOM findings. Use a .asc or .desc suffix to specify direction.
                Prefer the dot separator, supported on every Falcon sort endpoint.

                Common sort fields:
                severity: Finding severity level
                first_detected: When the finding was first detected
                last_detected: When the finding was last seen
                cloud_provider: Cloud provider name
                service: Cloud service name
                status: Finding status

                Sort field names do NOT match where the value lands in the response —
                none of them are at the record root. Read them back from:
                severity, status, first_detected, last_detected -> evaluation.<field>
                cloud_provider -> cloud.provider
                service -> resource.service

                severity sorts by the underlying severity code, where critical is the
                lowest value, so 'severity.asc' returns the MOST severe findings first.

                Examples: 'severity.desc', 'last_detected.desc', 'first_detected.asc'
            """
            ).strip(),
            examples=["severity.desc", "last_detected.desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for CSPM Indicators of Misconfiguration (IOM) findings.

        Use this to find specific compliance rule failures on individual cloud resources —
        each IOM is a single rule-against-resource violation (e.g. "S3 bucket ACL allows
        public write" on a named bucket). For aggregated risk posture combining multiple
        IOMs and IOAs across assets, use falcon_search_cloud_risks instead. For runtime
        behavioral threats, use falcon_search_detections. Consult
        falcon://cloud/cspm-iom-findings/fql-guide before constructing filter expressions.
        Returns IOM entities with cloud context, evaluation details, and resource information.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        iom_ids, pagination = self._base_search_with_meta(
            operation="cspm_evaluations_iom_queries",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to query IOM findings",
        )

        if self._is_error(iom_ids):
            return self._format_fql_error_response([iom_ids], filter, CSPM_IOM_FINDINGS_FQL_DOCUMENTATION)

        if not iom_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._batch_get_iom_entities(iom_ids)

        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(iom_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def _batch_get_iom_entities(self, iom_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch IOM entity details in batches of 100 (API limit)."""
        BATCH_SIZE = 100
        all_entities: list[dict[str, Any]] = []

        for i in range(0, len(iom_ids), BATCH_SIZE):
            batch = iom_ids[i : i + BATCH_SIZE]
            result = self._base_get_by_ids(
                operation="cspm_evaluations_iom_entities",
                ids=batch,
                id_key="ids",
                use_params=True,
            )
            if self._is_error(result):
                return result
            if isinstance(result, list):
                all_entities.extend(result)

        return all_entities

    def search_cspm_suppression_rules(
        self,
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of suppression rules to return (default: 100; max: 500).",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for CSPM IOM suppression rules.

        Use this to review existing suppressions before creating new ones. Returns
        suppression rule objects including scope, reason, and expiration details.
        Returns an empty list if no rules exist.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        params = prepare_api_parameters({"limit": limit, "offset": offset})
        query_response = self.client.command(
            "QuerySuppressionRules",
            override="GET,/cloud-policies/queries/suppression-rules/v1",
            parameters=params,
        )

        pagination = self._extract_pagination(query_response)

        query_result = handle_api_response(
            query_response,
            operation="QuerySuppressionRules",
            error_message="Failed to query suppression rules",
            default_result=[],
        )

        if self._is_error(query_result):
            return query_result

        if not query_result:
            return self._build_pagination_envelope([], pagination)

        detail_params = prepare_api_parameters({"ids": query_result})
        detail_response = self.client.command(
            "GetSuppressionRules",
            override="GET,/cloud-policies/entities/suppression-rules/v1",
            parameters=detail_params,
        )

        details = handle_api_response(
            detail_response,
            operation="GetSuppressionRules",
            error_message="Failed to get suppression rule details",
            default_result=[],
        )

        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(query_result, details, id_field="id")
        return self._build_pagination_envelope(details, pagination)

    def create_cspm_suppression_rule(
        self,
        name: str = Field(
            description="Name for the suppression rule. Should be descriptive.",
            examples=["Suppress S3 public access for dev accounts"],
        ),
        suppression_reason: str = Field(
            description=(
                "Reason for suppression. Required."
                " Values: 'accept-risk', 'compensating-control', 'false-positive'."
            ),
            examples=["accept-risk", "compensating-control", "false-positive"],
        ),
        rule_ids: list[str] | None = Field(
            default=None,
            description=(
                "Specific rule IDs to suppress."
                " If not provided, use rule_severities or rule_names to scope."
            ),
        ),
        rule_names: list[str] | None = Field(
            default=None,
            description="Rule names to suppress (supports wildcards).",
        ),
        rule_severities: list[str] | None = Field(
            default=None,
            description=(
                "Rule severities to suppress."
                " Values: 'critical', 'high', 'medium', 'low', 'informational'."
            ),
        ),
        cloud_providers: list[str] | None = Field(
            default=None,
            description=(
                "Limit suppression to specific cloud providers. Values: 'aws', 'azure', 'gcp'."
            ),
        ),
        account_ids: list[str] | None = Field(
            default=None,
            description="Limit suppression to specific cloud account IDs.",
        ),
        regions: list[str] | None = Field(
            default=None,
            description=(
                "Limit suppression to specific cloud regions. Ex: ['us-east-1', 'eu-west-1']."
            ),
        ),
        resource_ids: list[str] | None = Field(
            default=None,
            description="Limit suppression to specific resource IDs.",
        ),
        resource_types: list[str] | None = Field(
            default=None,
            description=("Limit suppression to specific resource types. Ex: ['AWS::S3::Bucket']."),
        ),
        expiration_date: str | None = Field(
            default=None,
            description=(
                "Optional expiration date in RFC 3339 format"
                " (e.g., '2025-12-31T23:59:59Z')."
                " WARNING: Omitting this creates a PERMANENT suppression."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a CSPM IOM suppression rule to hide matching findings.

        Suppressed findings are still assessed but not surfaced in compliance scores.
        Requires at least one rule selection (rule_ids, rule_names, or rule_severities)
        and a suppression reason. Setting an expiration_date is strongly recommended to
        avoid permanent suppressions. Returns the created suppression rule object.
        """
        valid_reasons = {"accept-risk", "compensating-control", "false-positive"}
        if suppression_reason not in valid_reasons:
            return {
                "error": f"Invalid suppression_reason: '{suppression_reason}'",
                "details": f"Must be one of: {', '.join(sorted(valid_reasons))}",
            }

        rule_filter: dict[str, Any] = {}
        if rule_ids:
            rule_filter["rule_ids"] = rule_ids
        if rule_names:
            rule_filter["rule_names"] = rule_names
        if rule_severities:
            rule_filter["rule_severities"] = rule_severities
        if not rule_filter:
            return {
                "error": "At least one rule selection parameter is required",
                "details": "Provide rule_ids, rule_names, or rule_severities to scope the suppression.",
            }

        asset_filter: dict[str, Any] = {}
        if cloud_providers:
            asset_filter["cloud_providers"] = cloud_providers
        if account_ids:
            asset_filter["account_ids"] = account_ids
        if regions:
            asset_filter["regions"] = regions
        if resource_ids:
            asset_filter["resource_ids"] = resource_ids
        if resource_types:
            asset_filter["resource_types"] = resource_types

        body: dict[str, Any] = {
            "name": name,
            "domain": "CSPM",
            "subdomain": "IOM",
            "suppression_reason": suppression_reason,
            "rule_selection_type": "rule_selection_filter",
            "rule_selection_filter": rule_filter,
            "scope_type": "asset_filter" if asset_filter else "all_assets",
        }

        if asset_filter:
            body["scope_asset_filter"] = asset_filter

        if expiration_date:
            body["suppression_expiration_date"] = expiration_date

        response = self.client.command(
            "CreateSuppressionRule",
            override="POST,/cloud-policies/entities/suppression-rules/v1",
            body=body,
        )

        create_result = handle_api_response(
            response,
            operation="CreateSuppressionRule",
            error_message="Failed to create suppression rule",
            default_result=[],
        )

        if self._is_error(create_result):
            return create_result

        if not create_result:
            return []

        detail_params = prepare_api_parameters({"ids": create_result})
        detail_response = self.client.command(
            "GetSuppressionRules",
            override="GET,/cloud-policies/entities/suppression-rules/v1",
            parameters=detail_params,
        )

        return handle_api_response(
            detail_response,
            operation="GetSuppressionRules",
            error_message="Failed to get created suppression rule details",
            default_result=[],
        )

    def delete_cspm_suppression_rules(
        self,
        ids: list[str] = Field(
            description=(
                "List of suppression rule IDs to delete."
                " Use falcon_search_cspm_suppression_rules to find rule IDs."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete CSPM IOM suppression rules by ID.

        Deleting a suppression rule re-activates all findings that were previously
        suppressed by it. Use falcon_search_cspm_suppression_rules to find rule IDs
        first. Returns a confirmation response.
        """
        params = prepare_api_parameters({"ids": ids})
        response = self.client.command(
            "DeleteSuppressionRules",
            override="DELETE,/cloud-policies/entities/suppression-rules/v1",
            parameters=params,
        )

        return handle_api_response(
            response,
            operation="DeleteSuppressionRules",
            error_message="Failed to delete suppression rules",
            default_result=[],
        )
