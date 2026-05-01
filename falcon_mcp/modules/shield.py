"""Falcon Shield (SaaS Security) module for querying SaaS security posture."""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.shield import SHIELD_QUERY_DOCUMENTATION

logger = get_logger(__name__)

IMPACT_NAMES = {"low": "Low", "medium": "Medium", "high": "High"}


class ShieldModule(BaseModule):
    """Module for CrowdStrike Falcon Shield (SaaS Security) API operations."""

    @staticmethod
    def _normalize_impact(impact: str | None) -> str | None:
        """Normalize impact to title-case for endpoints that accept named values."""
        if not isinstance(impact, str):
            return None
        normalized = IMPACT_NAMES.get(impact.lower())
        if normalized is None:
            logger.warning(
                "Unknown impact value '%s'; expected one of: %s", impact, ", ".join(IMPACT_NAMES)
            )
        return normalized

    def _format_empty_or_error(
        self,
        results: list[Any],
    ) -> dict[str, Any]:
        if results and "error" in results[0]:
            hint = "Query error occurred. Review your parameters using the query guide."
        else:
            hint = "No results matched your query. Review available parameters in the query guide."
        return {
            "results": results,
            "query_guide": SHIELD_QUERY_DOCUMENTATION,
            "hint": hint,
        }

    def _search_with_docs(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params=search_params,
            error_message=error_message,
        )
        if self._is_error(result):
            return self._format_empty_or_error([result])
        if not result:
            return self._format_empty_or_error([])
        return result

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(
            server=server,
            method=self.search_shield_checks,
            name="search_shield_checks",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_check_affected_entities,
            name="get_shield_check_affected_entities",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_posture_metrics,
            name="get_shield_posture_metrics",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_check_compliance,
            name="get_shield_check_compliance",
        )
        self._add_tool(
            server=server,
            method=self.search_shield_alerts,
            name="search_shield_alerts",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_activity_monitor,
            name="get_shield_activity_monitor",
        )
        self._add_tool(
            server=server,
            method=self.search_shield_users,
            name="search_shield_users",
        )
        self._add_tool(
            server=server,
            method=self.search_shield_devices,
            name="search_shield_devices",
        )
        self._add_tool(
            server=server,
            method=self.search_shield_apps,
            name="search_shield_apps",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_app_users,
            name="get_shield_app_users",
        )
        self._add_tool(
            server=server,
            method=self.search_shield_data_shares,
            name="search_shield_data_shares",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_integrations,
            name="get_shield_integrations",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_system_users,
            name="get_shield_system_users",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_supported_saas,
            name="get_shield_supported_saas",
        )
        self._add_tool(
            server=server,
            method=self.get_shield_system_logs,
            name="get_shield_system_logs",
        )
        self._add_tool(
            server=server,
            method=self.dismiss_shield_check,
            name="dismiss_shield_check",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        resource = TextResource(
            uri=AnyUrl("falcon://shield/search/query-guide"),
            name="falcon_shield_query_guide",
            description="Query parameter guide for Falcon Shield (SaaS Security) tools.",
            text=SHIELD_QUERY_DOCUMENTATION,
        )
        self._add_resource(server, resource)

    # --- Read-only tools ---

    def search_shield_checks(
        self,
        id: str | None = Field(
            default=None,
            description="Specific security check ID.",
        ),
        status: str | None = Field(
            default=None,
            description="Filter by status: Passed, Failed, Dismissed, Pending, Can't Run, Stale.",
        ),
        impact: str | None = Field(
            default=None,
            description="Filter by impact: Low, Medium, High.",
        ),
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        compliance: bool | None = Field(
            default=None,
            description=(
                "If true, return only checks that are defined as part of a compliance framework"
                " (SOC 2, CIS, NIST, etc.) at the catalog level."
                " Note: a check can be compliance-mapped yet still return no compliance criteria"
                " via `get_shield_check_compliance` if the tenant has not followed the relevant"
                " framework or compliance data has not yet been populated."
            ),
        ),
        check_type: str | None = Field(
            default=None,
            description="Filter by type: apps, devices, users, assets, permissions, custom, Falcon Shield Security Check.",
        ),
        check_tags: str | None = Field(
            default=None,
            description="Comma-separated tag filters.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search individual Falcon Shield (SaaS Security) posture checks with filtering.

        Use the check id from results to call `get_shield_check_affected_entities` for
        violating entities, `get_shield_check_compliance` for compliance mappings, or
        `dismiss_shield_check` to dismiss.

        For an aggregated posture summary (total score, status breakdown), use
        `get_shield_posture_metrics` instead.

        IMPORTANT: Consult the falcon://shield/search/query-guide resource for valid
        filter parameter values.

        Returns check records containing id, name, status, impact level, affected entity
        count, and remediation plan."""
        return self._search_with_docs(
            operation="GetSecurityChecksV3",
            search_params={
                "id": id,
                "status": status,
                "impact": self._normalize_impact(impact),
                "integration_id": integration_id,
                "compliance": compliance,
                "check_type": check_type,
                "check_tags": check_tags,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search Shield security checks",
        )

    def get_shield_check_affected_entities(
        self,
        id: str = Field(
            description="Security check ID. Obtain from the id field in results returned by `search_shield_checks`.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve the specific entities (users, apps, or devices) that are violating
        a given Falcon Shield (SaaS Security) posture check.

        Use this after `search_shield_checks` to drill into which entities are failing
        a specific check.

        Returns entity objects with entity name, type, and relevant security details."""
        return self._search_with_docs(
            operation="GetSecurityCheckAffectedV3",
            search_params={"id": id, "limit": limit, "offset": offset},
            error_message="Failed to get affected entities",
        )

    def get_shield_posture_metrics(
        self,
        status: str | None = Field(
            default=None,
            description="Filter by status: Passed, Failed, Dismissed, Pending, Can't Run, Stale.",
        ),
        impact: str | None = Field(
            default=None,
            description="Filter by impact: Low, Medium, High.",
        ),
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        compliance: bool | None = Field(
            default=None,
            description=(
                "If true, return only metrics for checks that are defined as part of a compliance"
                " framework (SOC 2, CIS, NIST, etc.) at the catalog level."
            ),
        ),
        check_type: str | None = Field(
            default=None,
            description="Filter by type: apps, devices, users, assets, permissions, custom, Falcon Shield Security Check.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get aggregated Falcon Shield (SaaS Security) posture metrics.

        Use this for a summary/dashboard view of your security posture. To retrieve
        individual check records with remediation details, use `search_shield_checks`
        instead.

        Returns total check counts, overall score percentage, and breakdown of checks
        by status (Passed, Failed, Dismissed, etc.) across connected SaaS applications."""
        return self._search_with_docs(
            operation="GetMetricsV3",
            search_params={
                "status": status,
                "impact": self._normalize_impact(impact),
                "integration_id": integration_id,
                "compliance": compliance,
                "check_type": check_type,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to get posture metrics",
        )

    def get_shield_check_compliance(
        self,
        id: str = Field(
            description="Security check ID. Obtain from the id field in results returned by `search_shield_checks`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve the compliance framework mappings for a specific Falcon Shield
        (SaaS Security) posture check.

        Use this to understand the regulatory impact of a failing check.

        Returns compliance objects identifying the framework (e.g., SOC 2, CIS, NIST,
        PCI DSS), control ID, and control description that the check satisfies."""
        return self._search_with_docs(
            operation="GetSecurityCheckComplianceV3",
            search_params={"id": id},
            error_message="Failed to get compliance data",
        )

    def search_shield_alerts(
        self,
        id: str | None = Field(
            default=None,
            description="Specific alert ID.",
        ),
        type: str | None = Field(
            default=None,
            description="Filter by type: configuration_drift, check_degraded, integration_failure, threat.",
        ),
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        from_date: str | None = Field(
            default=None,
            description="Start date (YYYY-MM-DD).",
        ),
        to_date: str | None = Field(
            default=None,
            description="End date (YYYY-MM-DD).",
        ),
        ascending: bool | None = Field(
            default=None,
            description="If true, return oldest alerts first. If false or omitted, return newest first.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
        last_id: str | None = Field(
            default=None,
            description="Cursor-based pagination token from the last result (alternative to offset).",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon Shield (SaaS Security) alerts for monitored SaaS applications.

        Alert types: configuration_drift (a previously passing check now fails),
        check_degraded (check status worsened), integration_failure (connectivity issue
        with a SaaS platform), threat (active threat indicator).

        Pagination: use last_id from the last result for cursor-based pagination, or
        use offset for offset-based pagination.

        Returns alert objects containing id, type, integration details, timestamp,
        and severity."""
        return self._search_with_docs(
            operation="GetAlertsV3",
            search_params={
                "id": id,
                "type": type,
                "integration_id": integration_id,
                "from_date": from_date,
                "to_date": to_date,
                "ascending": ascending,
                "limit": limit,
                "offset": offset,
                "last_id": last_id,
            },
            error_message="Failed to search Shield alerts",
        )

    def get_shield_activity_monitor(
        self,
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        actor: str | None = Field(
            default=None,
            description=(
                "Filter by the identity that performed the activity (e.g., user email, service account name)."
                " This is not a threat actor name."
            ),
        ),
        category: str | None = Field(
            default=None,
            description="Comma-separated activity categories: Events, Threat, IoC.",
        ),
        projection: str | None = Field(
            default=None,
            description=(
                "Comma-separated list of fields to include in each event."
                " Valid fields: timestamp_utc, severity, datetime, event_name, actor, integration_id,"
                " integration_name, type, category, created_by, ip, asn_name, country, browser, os,"
                " target, object_type, object, status. Omit for default fields."
            ),
        ),
        from_date: str | None = Field(
            default=None,
            description="Start datetime (ISO 8601).",
        ),
        to_date: str | None = Field(
            default=None,
            description="End datetime (ISO 8601).",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=10000,
            description="Maximum number of results to return (default: 100, max: 10000).",
        ),
        skip: int | None = Field(
            default=None,
            description=(
                "Pagination offset. Use meta.pagination.offset from the previous response"
                " for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get events from the Falcon Shield (SaaS Security) activity monitor.
        Data retained for 180 days.

        Note: When using integration_id, category, or actor filters, the date range
        (from_date to to_date) must be within 24 hours.

        Pagination: Use meta.pagination.next as to_date and meta.pagination.offset as
        skip for subsequent pages.

        IMPORTANT: Consult the falcon://shield/search/query-guide resource for valid
        category, actor, and projection values.

        Returns activity event objects including timestamp, event name, actor identity,
        integration, category, and location details."""
        return self._search_with_docs(
            operation="GetActivityMonitorV3",
            search_params={
                "integration_id": integration_id,
                "actor": actor,
                "category": category,
                "projection": projection,
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
                "skip": skip,
            },
            error_message="Failed to get activity monitor events",
        )

    def search_shield_users(
        self,
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        email: str | None = Field(
            default=None,
            description="Filter results to users matching this email address.",
        ),
        privileged_only: bool | None = Field(
            default=None,
            description="If true, return only users with privileged or administrative roles.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List end-users discovered across Falcon Shield (SaaS Security) connected
        SaaS applications.

        Use this to audit user access across your SaaS estate or to identify
        over-privileged or stale accounts.

        To list Shield platform administrators instead of SaaS app end-users, use
        `get_shield_system_users`.

        Returns user objects containing email, display name, connected application
        details, privilege status, and exposure metrics."""
        return self._search_with_docs(
            operation="GetUserInventoryV3",
            search_params={
                "integration_id": integration_id,
                "email": email,
                "privileged_only": privileged_only,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search Shield users",
        )

    def search_shield_devices(
        self,
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        email: str | None = Field(
            default=None,
            description="Filter by user email associated with the device.",
        ),
        privileged_only: bool | None = Field(
            default=None,
            description="If true, return only devices belonging to users with privileged roles.",
        ),
        unassociated_devices: bool | None = Field(
            default=None,
            description="If true, include devices not associated with a known user.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List devices registered to users in Falcon Shield (SaaS Security) connected
        SaaS applications.

        Note: This returns devices from SaaS provider records, not from the Falcon
        sensor inventory. To search Falcon-sensor-enrolled hosts, use `search_hosts`
        instead.

        Returns device objects containing device name, owner email, compliance posture,
        and management status."""
        return self._search_with_docs(
            operation="GetDeviceInventoryV3",
            search_params={
                "integration_id": integration_id,
                "email": email,
                "privileged_only": privileged_only,
                "unassociated_devices": unassociated_devices,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search Shield devices",
        )

    def search_shield_apps(
        self,
        type: str | None = Field(
            default=None,
            description="App type: oauth, sign_in, api_token, browser_extension, etc.",
        ),
        status: str | None = Field(
            default=None,
            description="Status: approved, in review, rejected, unclassified.",
        ),
        access_level: str | None = Field(
            default=None,
            description="Access level: high, medium, low, none.",
        ),
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        scopes: str | None = Field(
            default=None,
            description="Comma-separated OAuth scope filter.",
        ),
        users: str | None = Field(
            default=None,
            description=(
                "Filter by user association. Format: 'is equal <email>' for exact match,"
                " or 'contains <value>' for partial match. Example: 'is equal user@example.com'."
            ),
        ),
        groups: str | None = Field(
            default=None,
            description="Group filter.",
        ),
        last_activity: str | None = Field(
            default=None,
            description=(
                "Filter by time since the app was last active."
                " Format: 'was N' (active within N days) or 'was not N' (inactive for more than N days)."
                " Example: 'was not 90'."
            ),
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List third-party applications (OAuth apps, API tokens, browser extensions,
        service principals) with access to Falcon Shield (SaaS Security) monitored
        platforms.

        Use the item_id from results with `get_shield_app_users` to retrieve the users
        of a specific app.

        Returns app objects containing item_id, name, type, status, access_level,
        granted scopes, and user count."""
        return self._search_with_docs(
            operation="GetAppInventory",
            search_params={
                "type": type,
                "status": status,
                "access_level": access_level,
                "integration_id": integration_id,
                "scopes": scopes,
                "users": users,
                "groups": groups,
                "last_activity": last_activity,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search Shield apps",
        )

    def get_shield_app_users(
        self,
        item_id: str = Field(
            description=(
                "Composite app identifier in the format integration_id|||app_id."
                " Obtain from the item_id field in results returned by `search_shield_apps`."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve the users who have authorized or are associated with a specific
        third-party app in Falcon Shield (SaaS Security).

        Use this after `search_shield_apps` to drill into a specific app's user
        population.

        Returns user objects including email, display name, and granted permissions."""
        return self._search_with_docs(
            operation="GetAppInventoryUsers",
            search_params={"item_id": item_id},
            error_message="Failed to get app users",
        )

    def search_shield_data_shares(
        self,
        integration_id: str | None = Field(
            default=None,
            description=(
                "Comma-separated IDs of SaaS integrations to filter by."
                " Use `get_shield_integrations` to retrieve available integration IDs."
            ),
        ),
        resource_type: str | None = Field(
            default=None,
            description="File type filter (e.g., PDF, XLSX).",
        ),
        access_level: str | None = Field(
            default=None,
            description=(
                "Sharing access level filter (comma-separated)."
                " Values: public_link, external_user, org_wide, internal."
            ),
        ),
        resource_name: str | None = Field(
            default=None,
            description="Filter to resources whose name contains this value.",
        ),
        resource_owner: str | None = Field(
            default=None,
            description="Filter to resources whose owner name or email contains this value.",
        ),
        resource_owner_enabled: bool | None = Field(
            default=None,
            description=(
                "If true, return only resources with an active owner account."
                " If false, only disabled owner accounts."
            ),
        ),
        password_protected: bool | None = Field(
            default=None,
            description="If true, return only password-protected resources. If false, only unprotected resources.",
        ),
        last_accessed: str | None = Field(
            default=None,
            description=(
                "Filter by time since the resource was last accessed."
                " Format: 'was N' (within N days) or 'was not N' (not accessed in more than N days)."
                " Example: 'was not 30'."
            ),
        ),
        last_modified: str | None = Field(
            default=None,
            description=(
                "Filter by time since the resource was last modified."
                " Format: 'was N' (within N days) or 'was not N' (not modified in more than N days)."
                " Example: 'was not 30'."
            ),
        ),
        unmanaged_domain: str | None = Field(
            default=None,
            description=(
                "Filter to resources shared with external (non-organization) domains."
                " Comma-separated domain names (e.g., 'gmail.com,yahoo.com')."
            ),
        ),
        limit: int = Field(
            default=10,
            ge=1,
            description="Maximum number of results to return (default: 10).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List files and resources shared externally across Falcon Shield (SaaS
        Security) monitored SaaS applications.

        Use this to identify overshared or externally exposed files (e.g., Google
        Drive documents shared outside the organization).

        Returns resource objects containing resource name, type, owner, sharing access
        level, password protection status, and last access/modification timestamps."""
        return self._search_with_docs(
            operation="GetAssetInventoryV3",
            search_params={
                "integration_id": integration_id,
                "resource_type": resource_type,
                "access_level": access_level,
                "resource_name": resource_name,
                "resource_owner": resource_owner,
                "resource_owner_enabled": resource_owner_enabled,
                "password_protected": password_protected,
                "last_accessed": last_accessed,
                "last_modified": last_modified,
                "unmanaged_domain": unmanaged_domain,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search Shield data shares",
        )

    def get_shield_integrations(
        self,
        saas_id: str | None = Field(
            default=None,
            description="Comma-separated SaaS platform IDs to filter by.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List all SaaS integrations connected to Falcon Shield (SaaS Security) and
        their current connection status.

        The integration_id values returned here are used as input to most other Shield
        tools. Call this tool first when starting a Shield investigation to discover
        available integrations.

        Returns integration objects containing integration_id, SaaS platform name,
        connection health, and last sync time."""
        return self._search_with_docs(
            operation="GetIntegrationsV3",
            search_params={"saas_id": saas_id},
            error_message="Failed to get Shield integrations",
        )

    def get_shield_system_users(self) -> list[dict[str, Any]] | dict[str, Any]:
        """List Falcon Shield (SaaS Security) platform administrators.

        These are Shield console administrators, not end-users of connected SaaS
        applications. For SaaS app end-users, use `search_shield_users`.

        Returns system-level user objects including email, role, and MFA status."""
        return self._search_with_docs(
            operation="GetSystemUsersV3",
            search_params={},
            error_message="Failed to get Shield system users",
        )

    def get_shield_supported_saas(self) -> list[dict[str, Any]] | dict[str, Any]:
        """List SaaS platforms supported by Falcon Shield (SaaS Security) for integration.

        Use this to discover which SaaS applications can be connected to Shield
        before setting up new integrations.

        Returns supported SaaS platform objects including platform name and ID."""
        return self._search_with_docs(
            operation="GetSupportedSaasV3",
            search_params={},
            error_message="Failed to get supported SaaS platforms",
        )

    def get_shield_system_logs(
        self,
        from_date: str | None = Field(
            default=None,
            description="Start date (YYYY-MM-DD).",
        ),
        to_date: str | None = Field(
            default=None,
            description="End date (YYYY-MM-DD).",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            description="Maximum number of results to return (default: 100).",
        ),
        offset: int | None = Field(
            default=None,
            description=(
                "Zero-based offset for pagination. Omit or set to 0 for the first page."
                " Increment by limit for subsequent pages."
            ),
        ),
        total_count: bool | None = Field(
            default=None,
            description="If true, include total count of matching logs in the response metadata.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve Falcon Shield (SaaS Security) system audit logs. Data retained
        for 90 days.

        Logs include integration creates/updates, check dismissals, and data syncs.

        Use date range filters to narrow results. Without filters, returns the most
        recent logs up to the limit.

        Returns log objects containing timestamp, event type, actor, and details."""
        return self._search_with_docs(
            operation="GetSystemLogsV3",
            search_params={
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
                "offset": offset,
                "total_count": total_count,
            },
            error_message="Failed to get Shield system logs",
        )

    # --- Mutating tools ---

    def dismiss_shield_check(
        self,
        id: str = Field(
            description="Security check ID. Obtain from the id field in results returned by `search_shield_checks`.",
        ),
        reason: str = Field(
            description=(
                "Required explanation for the dismissal."
                " This is written to the audit log and visible to other administrators."
            ),
        ),
        entities: str | None = Field(
            default=None,
            description=(
                "Comma-separated entity names to dismiss."
                " If omitted, dismisses the entire check for all entities."
                " If provided, only the specified entities are dismissed and the check remains active for others."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Dismiss a Falcon Shield (SaaS Security) posture check to suppress it from
        the failed checks list.

        WARNING: This action is permanent and cannot be undone from the API. The
        dismissal reason is recorded in audit logs.

        When entities is omitted, the entire check is dismissed for all entities.
        When entities is provided, only the specified entities are dismissed and the
        check remains active for others."""
        if isinstance(entities, str):
            operation = "DismissAffectedEntityV3"
            body = {
                "reason": reason,
                "entities": [e.strip() for e in entities.split(",")],
            }
        else:
            operation = "DismissSecurityCheckV3"
            body = {"reason": reason}

        return self._base_query_api_call(
            operation=operation,
            query_params={"id": id},
            body_params=body,
            error_message="Failed to dismiss Shield check",
        )
