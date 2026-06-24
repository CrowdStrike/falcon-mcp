"""
Recon module for Falcon MCP Server.

This module provides tools for searching Falcon Intelligence Recon notifications,
monitoring rules, and exposed-data records.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.recon import (
    SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION,
    SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION,
    SEARCH_RECON_RULES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


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
                description="Contains the guide for the `filter` param of the `falcon_search_recon_notifications` tool.",
                text=SEARCH_RECON_NOTIFICATIONS_FQL_DOCUMENTATION,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/rules/search/fql-guide"),
                name="falcon_search_recon_rules_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_recon_rules` tool.",
                text=SEARCH_RECON_RULES_FQL_DOCUMENTATION,
            ),
        )

        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://recon/exposed-data-records/search/fql-guide"),
                name="falcon_search_recon_exposed_data_records_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_recon_exposed_data_records` tool.",
                text=SEARCH_RECON_EXPOSED_DATA_RECORDS_FQL_DOCUMENTATION,
            ),
        )

    def search_recon_notifications(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://recon/notifications/search/fql-guide` for syntax.",
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
            description="Maximum number of notifications to return (default: 10; max: 500). offset + limit must not exceed 10,000.",
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

                Append |asc or |desc for direction (default desc).
                Examples: 'created_date|desc', 'updated_date|asc'
            """).strip(),
            examples=["created_date|desc", "updated_date|asc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon notifications (also called recon alerts) and return their full details.

        Use this for dark web matches, leaked credentials, typosquatting matches, and breach
        summaries triggered by your monitoring rules. Consult
        `falcon://recon/notifications/search/fql-guide` before constructing filter expressions.
        This serves the external cyber risk monitoring capability of CrowdStrike Counter Adversary
        Operations (CAO). For endpoint, XDR, or NG-SIEM alerts, use `falcon_search_detections`
        instead. Returns full notification records with a nested `notification` object
        containing status, rule metadata, breach_summary, and item details.
        """
        logger.debug(
            "Searching recon notifications with filter=%s, q=%s, limit=%s, offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        notification_ids = self._base_search_api_call(
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
            return self._format_empty_response(filter)

        details = self._base_get_by_ids(
            operation="GetNotificationsDetailedV1",
            ids=notification_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_recon_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://recon/rules/search/fql-guide` for syntax.",
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
            description="Maximum number of rules to return (default: 10; max: 500). offset + limit must not exceed 10,000.",
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

                Append |asc or |desc for direction (default desc).
                Examples: 'created_timestamp|desc', 'priority|asc'
            """).strip(),
            examples=["created_timestamp|desc", "last_updated_timestamp|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon monitoring rules and return their full details.

        Use this to list the rules that generate your recon notifications — find rules by
        topic (domain, email, typosquatting, brand), priority, status, or whether breach
        monitoring is enabled. Consult `falcon://recon/rules/search/fql-guide` before
        constructing filter expressions. These monitoring rules power the external cyber risk
        monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full
        rule definitions including topic, priority, filter expressions, and notification settings.
        """
        logger.debug(
            "Searching recon rules with filter=%s, q=%s, limit=%s, offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        rule_ids = self._base_search_api_call(
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
            return self._format_empty_response(filter)

        details = self._base_get_by_ids(
            operation="GetRulesV1",
            ids=rule_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_recon_exposed_data_records(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://recon/exposed-data-records/search/fql-guide` for syntax.",
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
            description="Maximum number of records to return (default: 10; max: 500). offset + limit must not exceed 10,000.",
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
                updated_date: When the record was last updated

                Append |asc or |desc for direction (default desc).
                Examples: 'created_date|desc', 'exposure_date|desc'
            """).strip(),
            examples=["created_date|desc", "exposure_date|desc"],
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Intelligence Recon exposed-data records and return their full details.

        Use this to find leaked credential and PII rows associated with recon notifications —
        emails, login IDs, password hashes, domains, and breach metadata. Consult
        `falcon://recon/exposed-data-records/search/fql-guide` before constructing filter
        expressions. These records are part of the external cyber risk monitoring capability of
        CrowdStrike Counter Adversary Operations (CAO). Returns full records including credential
        fields, location data, and associated notification context.
        """
        logger.debug(
            "Searching recon exposed-data records with filter=%s, q=%s, limit=%s, offset=%s, sort=%s",
            filter, q, limit, offset, sort,
        )

        record_ids = self._base_search_api_call(
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
            return self._format_empty_response(filter)

        details = self._base_get_by_ids(
            operation="GetNotificationsExposedDataRecordsV1",
            ids=record_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details
