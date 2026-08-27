"""
Recon module for Falcon MCP Server.

This module provides tools for searching Falcon Intelligence Recon notifications,
monitoring rules, and exposed-data records.
"""

from textwrap import dedent
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.recon import (
    AGGREGATE_RECON_EXPOSED_DATA_RECORDS_GUIDE,
    AGGREGATE_RECON_NOTIFICATIONS_GUIDE,
    PREVIEW_RECON_RULE_GUIDE,
    SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION,
    SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION,
    SEARCH_RECON_RULES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)

# Aggregation types both recon aggregate endpoints accept. `sum`, `avg`, and
# `percentiles` are rejected with a 400, so they are deliberately absent.
ReconAggregateType = Literal[
    "terms",
    "date_histogram",
    "date_range",
    "range",
    "cardinality",
    "max",
    "min",
]


class ReconModule(BaseModule):
    """Module for accessing Falcon Intelligence Recon notifications and monitoring data."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_recon_notifications,
            name="search_recon_notifications",
        )

        self._add_tool(
            server=server,
            method=self.search_recon_rules,
            name="search_recon_rules",
        )

        self._add_tool(
            server=server,
            method=self.search_recon_exposed_data_records,
            name="search_recon_exposed_data_records",
        )

        self._add_tool(
            server=server,
            method=self.aggregate_recon_notifications,
            name="aggregate_recon_notifications",
        )

        self._add_tool(
            server=server,
            method=self.aggregate_recon_exposed_data_records,
            name="aggregate_recon_exposed_data_records",
        )

        self._add_tool(
            server=server,
            method=self.preview_recon_rule,
            name="preview_recon_rule",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/notifications/search/fql-guide"),
                name="falcon_search_recon_notifications_fql_guide",
                description=(
                    "Contains the guide for the `filter` param of the "
                    "`falcon_search_recon_notifications` tool."
                ),
                text=SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/rules/search/fql-guide"),
                name="falcon_search_recon_rules_fql_guide",
                description=(
                    "Contains the guide for the `filter` param of the "
                    "`falcon_search_recon_rules` tool."
                ),
                text=SEARCH_RECON_RULES_FQL_DOCUMENTATION,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/exposed-data-records/search/fql-guide"),
                name="falcon_search_recon_exposed_data_records_fql_guide",
                description=(
                    "Contains the guide for the `filter` param of the "
                    "`falcon_search_recon_exposed_data_records` tool."
                ),
                text=SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/notifications/aggregate-guide"),
                name="falcon_aggregate_recon_notifications_guide",
                description=(
                    "Contains the aggregatable fields and usage guide for the "
                    "`falcon_aggregate_recon_notifications` tool."
                ),
                text=AGGREGATE_RECON_NOTIFICATIONS_GUIDE,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/exposed-data-records/aggregate-guide"),
                name="falcon_aggregate_recon_exposed_data_records_guide",
                description=(
                    "Contains the aggregatable fields and usage guide for the "
                    "`falcon_aggregate_recon_exposed_data_records` tool."
                ),
                text=AGGREGATE_RECON_EXPOSED_DATA_RECORDS_GUIDE,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/rules/preview-guide"),
                name="falcon_preview_recon_rule_guide",
                description=(
                    "Contains the rule-filter dialect, valid topics, and lookback values "
                    "for the `falcon_preview_recon_rule` tool."
                ),
                text=PREVIEW_RECON_RULE_GUIDE,
            ),
        )

    def search_recon_notifications(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See "
                "`falcon://recon/notifications/search/fql-guide` for syntax."
            ),
            examples=[
                "status:'new'+rule_priority:'high'",
                "item_site:'telegram.org'",
                "created_date:>'now-7d'",
            ],
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all notification metadata.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description=(
                "Maximum number of notifications to return (default: 10; max: 500). "
                "offset + limit must not exceed 10,000."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination. offset + limit must not exceed 10,000.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort notifications using these options:
                created_date: When the notification was created
                updated_date: When the notification was last updated

                Append .asc or .desc for direction (default desc).

                Both sort fields read back from `notification.<field>`, not the record
                root — a notification record's root holds only `id` and `notification`.

                Examples: 'created_date.desc', 'updated_date.asc'
            """).strip(),
            examples=["created_date.desc", "updated_date.asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon notifications (also called recon alerts)
        and return their full details.

        Use this for dark web matches, leaked credentials, typosquatting matches, and breach
        summaries triggered by your monitoring rules. Consult
        `falcon://recon/notifications/search/fql-guide` before constructing filter expressions.
        This serves the external cyber risk monitoring capability of CrowdStrike Counter Adversary
        Operations (CAO). For endpoint, XDR, or NG-SIEM alerts, use `falcon_search_detections`
        instead. Returns full notification records with a nested `notification` object
        containing status, rule metadata, breach_summary, and item details.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        logger.debug(
            "Searching recon notifications with filter=%s, q=%s, limit=%s, offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        notification_ids, pagination = self._base_search_with_meta(
            operation="QueryNotificationsV1",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search recon notifications",
        )

        if self._is_error(notification_ids):
            return self._format_fql_error_response(
                [notification_ids], filter, SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION
            )

        if not notification_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._base_get_by_ids(
            operation="GetNotificationsDetailedV1",
            ids=notification_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order; GetNotificationsDetailedV1 may reorder.
        details = self._reorder_by_ids(notification_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def search_recon_rules(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://recon/rules/search/fql-guide` "
                "for syntax."
            ),
            examples=[
                "status:'active'+priority:'high'",
                "topic:'SA_TYPOSQUATTING'",
                "breach_monitoring_enabled:true",
            ],
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all rule metadata.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description=(
                "Maximum number of rules to return (default: 10; max: 500). "
                "offset + limit must not exceed 10,000."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination. offset + limit must not exceed 10,000.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort rules using these options:
                created_timestamp: When the rule was created
                last_updated_timestamp: When the rule was last modified
                priority: Rule priority level
                topic: Rule topic category

                Append .asc or .desc for direction (default desc).
                Examples: 'created_timestamp.desc', 'priority.asc'
            """).strip(),
            examples=["created_timestamp.desc", "last_updated_timestamp.desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon monitoring rules and return their full details.

        Use this to list the rules that generate your recon notifications — find rules by
        topic (domain, email, typosquatting, brand), priority, status, or whether breach
        monitoring is enabled. Consult `falcon://recon/rules/search/fql-guide` before
        constructing filter expressions. These monitoring rules power the external cyber risk
        monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full
        rule definitions including topic, priority, filter expressions, and notification settings.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        logger.debug(
            "Searching recon rules with filter=%s, q=%s, limit=%s, offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        rule_ids, pagination = self._base_search_with_meta(
            operation="QueryRulesV1",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search recon rules",
        )

        if self._is_error(rule_ids):
            return self._format_fql_error_response(
                [rule_ids], filter, SEARCH_RECON_RULES_FQL_DOCUMENTATION
            )

        if not rule_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._base_get_by_ids(
            operation="GetRulesV1",
            ids=rule_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order in case GetRulesV1 reorders results.
        details = self._reorder_by_ids(rule_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def search_recon_exposed_data_records(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See "
                "`falcon://recon/exposed-data-records/search/fql-guide` for syntax."
            ),
            examples=[
                "domain:'example.com'+credential_status:'confirmed_active'",
                "notification_id:'abc123def456'",
                "created_date:>'now-7d'",
            ],
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all exposed-data record fields.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description=(
                "Maximum number of records to return (default: 10; max: 500). "
                "offset + limit must not exceed 10,000."
            ),
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index for pagination. offset + limit must not exceed 10,000.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort records using these options:
                created_date: When the record was created
                exposure_date: When the data was exposed/breached

                Append .asc or .desc for direction (default desc).
                Examples: 'created_date.desc', 'exposure_date.desc'
            """).strip(),
            examples=["created_date.desc", "exposure_date.desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon exposed-data records and return their full details.

        Use this to find leaked credential and PII rows associated with recon notifications —
        emails, login IDs, password hashes, domains, and breach metadata. Consult
        `falcon://recon/exposed-data-records/search/fql-guide` before constructing filter
        expressions. These records are part of the external cyber risk monitoring capability of
        CrowdStrike Counter Adversary Operations (CAO). Returns full records including credential
        fields, location data, and associated notification context.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        logger.debug(
            "Searching recon exposed-data records with filter=%s, q=%s, limit=%s, "
            "offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        record_ids, pagination = self._base_search_with_meta(
            operation="QueryNotificationsExposedDataRecordsV1",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search recon exposed-data records",
        )

        if self._is_error(record_ids):
            return self._format_fql_error_response(
                [record_ids], filter, SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION
            )

        if not record_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._base_get_by_ids(
            operation="GetNotificationsExposedDataRecordsV1",
            ids=record_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order; the exposed-data details endpoint may reorder.
        details = self._reorder_by_ids(record_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def aggregate_recon_notifications(
        self,
        field: str = Field(
            description=(
                "Notification field to group by, such as `status`, `rule_topic`, "
                "`rule_priority`, `rule_id`, `item_type`, `item_site`, or `created_date`. "
                "See `falcon://recon/notifications/aggregate-guide` for the full list."
            ),
            examples=["status", "rule_topic", "rule_priority", "created_date"],
        ),
        aggregate_type: ReconAggregateType = Field(
            default="terms",
            description=(
                "Aggregation to run. Use `terms` for top values, `date_histogram` or "
                "`date_range` for time buckets, `cardinality` for a distinct count, and "
                "`max` or `min` for numeric extremes. `date_histogram` requires `interval`, "
                "`date_range` requires `date_ranges`, and `range` requires `ranges`."
            ),
        ),
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter narrowing which notifications are counted. See "
                "`falcon://recon/notifications/search/fql-guide` for syntax."
            ),
            examples=["rule_topic:'SA_TYPOSQUATTING'", "created_date:>'now-30d'"],
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all notification metadata.",
        ),
        name: str = Field(
            default="recon_notification_aggregation",
            description="Label echoed back on the result, identifying this aggregation.",
        ),
        size: int | None = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum number of buckets to return for terms aggregations.",
        ),
        sort: str | None = Field(
            default=None,
            description="Bucket sort order, such as `_count|desc` or `_count|asc`.",
            examples=["_count|desc", "_count|asc"],
        ),
        interval: str | None = Field(
            default=None,
            description=(
                "Bucket width for `date_histogram`: hour, day, week, month, quarter, or year."
            ),
            examples=["day", "week"],
        ),
        date_ranges: list[dict[str, str]] | None = Field(
            default=None,
            description=(
                "Time windows for `date_range` aggregations, for example "
                "`[{'from': 'now-30d', 'to': 'now'}]`."
            ),
            examples=[[{"from": "now-30d", "to": "now"}]],
        ),
        ranges: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Numeric windows for `range` aggregations, for example "
                "`[{'From': 0, 'To': 100}]`. Required when aggregate_type is `range`."
            ),
            examples=[[{"From": 0, "To": 100}]],
        ),
        sub_aggregates: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Nested aggregations run inside each bucket, for a breakdown within a "
                "breakdown. Each entry uses the same shape as the top-level aggregation."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Count and group Falcon Intelligence Recon notifications into summary buckets.

        Use this to answer how many, top, most common, per day, or over time questions about
        recon notifications — the mix of statuses, the noisiest monitoring rules, or the
        typosquatting trend — without retrieving individual records. Consult
        `falcon://recon/notifications/aggregate-guide` for aggregatable fields and
        `falcon://recon/notifications/search/fql-guide` before writing a filter. Returns one
        entry per aggregation, each with a `name` and `buckets` keyed on `label` and `count`.
        """
        return self._base_aggregate(
            operation="AggregateNotificationsV1",
            agg_type=aggregate_type,
            field=field,
            filter=filter,
            q=q,
            name=name,
            size=size,
            sort=sort,
            interval=interval,
            date_ranges=date_ranges,
            ranges=ranges,
            sub_aggregates=sub_aggregates,
            error_message="Failed to aggregate recon notifications",
        )

    def aggregate_recon_exposed_data_records(
        self,
        field: str = Field(
            description=(
                "Exposed-data-record field to group by. This endpoint accepts only: cid, "
                "notification_id, notification_group_id, created_date, rule.id, rule.name, "
                "rule.topic, source_category, site, author, file.name, credential_status, "
                "bot.operating_system.hardware_id, bot.bot_id. Other fields are rejected — "
                "see `falcon://recon/exposed-data-records/aggregate-guide`."
            ),
            examples=["credential_status", "site", "rule.topic", "created_date"],
        ),
        aggregate_type: ReconAggregateType = Field(
            default="terms",
            description=(
                "Aggregation to run. Use `terms` for top values, `date_histogram` or "
                "`date_range` for time buckets, `cardinality` for a distinct count, and "
                "`max` or `min` for numeric extremes. `date_histogram` requires `interval`, "
                "`date_range` requires `date_ranges`, and `range` requires `ranges`."
            ),
        ),
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter narrowing which records are counted. See "
                "`falcon://recon/exposed-data-records/search/fql-guide` for syntax."
            ),
            examples=["credential_status:'newly_reported'", "domain:'example.com'"],
        ),
        q: str | None = Field(
            default=None,
            description="Free text search across all exposed-data record fields.",
        ),
        name: str = Field(
            default="recon_exposed_data_aggregation",
            description="Label echoed back on the result, identifying this aggregation.",
        ),
        size: int | None = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum number of buckets to return for terms aggregations.",
        ),
        sort: str | None = Field(
            default=None,
            description="Bucket sort order, such as `_count|desc` or `_count|asc`.",
            examples=["_count|desc", "_count|asc"],
        ),
        interval: str | None = Field(
            default=None,
            description=(
                "Bucket width for `date_histogram`: hour, day, week, month, quarter, or year."
            ),
            examples=["day", "week"],
        ),
        date_ranges: list[dict[str, str]] | None = Field(
            default=None,
            description=(
                "Time windows for `date_range` aggregations, for example "
                "`[{'from': 'now-30d', 'to': 'now'}]`."
            ),
            examples=[[{"from": "now-30d", "to": "now"}]],
        ),
        ranges: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Numeric windows for `range` aggregations, for example "
                "`[{'From': 0, 'To': 100}]`. Required when aggregate_type is `range`."
            ),
            examples=[[{"From": 0, "To": 100}]],
        ),
        sub_aggregates: list[dict[str, Any]] | None = Field(
            default=None,
            description=(
                "Nested aggregations run inside each bucket, for a breakdown within a "
                "breakdown. Each entry uses the same shape as the top-level aggregation."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Count and group Falcon Intelligence Recon exposed-data records into summary buckets.

        Use this to answer how many, top, most common, per day, or over time questions about
        leaked credentials and PII — which sites leak the most, the newly-versus-previously
        reported mix, or exposure volume over time — without retrieving individual rows.
        Consult `falcon://recon/exposed-data-records/aggregate-guide` for the restricted field
        list and `falcon://recon/exposed-data-records/search/fql-guide` before writing a filter.
        Returns one entry per aggregation, each with a `name` and `buckets` keyed on `label`
        and `count`.
        """
        return self._base_aggregate(
            operation="AggregateNotificationsExposedDataRecordsV1",
            agg_type=aggregate_type,
            field=field,
            filter=filter,
            q=q,
            name=name,
            size=size,
            sort=sort,
            interval=interval,
            date_ranges=date_ranges,
            ranges=ranges,
            sub_aggregates=sub_aggregates,
            error_message="Failed to aggregate recon exposed-data records",
        )

    def preview_recon_rule(
        self,
        topic: Literal[
            "SA_DOMAIN",
            "SA_EMAIL",
            "SA_IP",
            "SA_AUTHOR",
            "SA_BRAND_PRODUCT",
            "SA_THIRD_PARTY",
            "SA_CUSTOM",
            "SA_VIP",
            "SA_CVE",
            "SA_ALIAS",
        ] = Field(
            description=(
                "Topic of the prospective monitoring rule. SA_TYPOSQUATTING cannot be "
                "previewed. Each topic supports different filter conditions — see "
                "`falcon://recon/rules/preview-guide`."
            ),
            examples=["SA_DOMAIN", "SA_BRAND_PRODUCT"],
        ),
        filter: str = Field(
            description=(
                "The prospective rule's own match expression in monitoring-rule FQL, with "
                "each condition parenthesized, e.g. `(domain:'example.com')`. This is not "
                "notification search FQL. See `falcon://recon/rules/preview-guide` for the "
                "condition words each topic supports."
            ),
            examples=[
                "(domain:'example.com')",
                "(phrase:'Acme')+(keyword:'Acme')",
                "(email:'ceo@example.com')",
            ],
        ),
        lookback_days: Literal[7, 30, 180, 365] | None = Field(
            default=None,
            description=(
                "How far back to estimate over. Only 7, 30, 180, and 365 are accepted. "
                "Omit to preview against the full retained window."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Estimate how many notifications a prospective Recon monitoring rule would generate.

        Use this before creating a monitoring rule to judge how noisy it would be, or to
        compare candidate filters — a high total means the rule needs tightening. Consult
        `falcon://recon/rules/preview-guide` for the rule-filter dialect, since `filter` is a
        rule definition rather than a notification search filter; to summarize notifications
        that already exist, use `falcon_aggregate_recon_notifications` instead. Returns a
        fixed breakdown of `channel`, `count`, and `site` aggregations with `label`/`count`
        buckets.
        """
        operation = "PreviewRuleV1"
        body = prepare_api_parameters(
            {
                "topic": topic,
                "filter": filter,
                "lookback_days": lookback_days,
            }
        )

        logger.debug("Executing %s with body: %s", operation, body)

        # A bare object, unlike the list-wrapped body the recon aggregate endpoints take.
        response = self.client.command(operation, body=body)

        result = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to preview recon rule",
            default_result=[],
        )

        # The rule-filter dialect is the usual thing to get wrong here, and the API's
        # rejection names the offending field but not the fix. Hand back the guide.
        if self._is_error(result):
            return self._format_fql_error_response([result], filter, PREVIEW_RECON_RULE_GUIDE)

        return result

