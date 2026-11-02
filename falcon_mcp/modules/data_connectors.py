"""Module for managing Next-Gen SIEM Data Connectors.

Covers discovering available connector types, listing/searching active connections,
creating and managing connections, retrieving and regenerating ingest tokens,
and managing connector configurations for pull-based connectors.
"""

from __future__ import annotations

from typing import Any

from mcp.types import ToolAnnotations
from pydantic import Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.data_connectors import (
    DATA_CONNECTORS_TROUBLESHOOTING_GUIDE,
    DATA_SOURCE_MAPPING_GUIDE,
    SEARCH_DATA_CONNECTIONS_FQL_DOCUMENTATION,
    SEARCH_DATA_CONNECTORS_FQL_DOCUMENTATION,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    from mcp.server import FastMCP  # type: ignore[assignment]

try:
    from mcp.server.fastmcp.resources import TextResource
    from pydantic import AnyUrl
except ImportError:  # pragma: no cover
    TextResource = None  # type: ignore[assignment,misc]
    AnyUrl = None  # type: ignore[assignment,misc]

logger = get_logger(__name__)


class DataConnectorsModule(BaseModule):
    """Module for managing Next-Gen SIEM Data Connectors."""

    def register_tools(self, server: FastMCP) -> None:
        # Read-only tools
        self._add_tool(
            server=server,
            method=self.search_data_connectors,
            name="search_data_connectors",
        )
        self._add_tool(
            server=server,
            method=self.search_data_connections,
            name="search_data_connections",
        )
        self._add_tool(
            server=server,
            method=self.get_data_connection,
            name="get_data_connection",
        )

        # Write tools
        self._add_tool(
            server=server,
            method=self.create_data_connection,
            name="create_data_connection",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.manage_data_connection,
            name="manage_data_connection",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_data_connection,
            name="delete_data_connection",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.regenerate_data_connection_token,
            name="regenerate_data_connection_token",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.manage_connector_config,
            name="manage_connector_config",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://data-connectors/connections/search/fql-guide"),
            name="falcon_search_data_connections_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_data_connections` tool.",
            text=SEARCH_DATA_CONNECTIONS_FQL_DOCUMENTATION,
        ))
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://data-connectors/connectors/search/fql-guide"),
            name="falcon_search_data_connectors_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_data_connectors` tool.",
            text=SEARCH_DATA_CONNECTORS_FQL_DOCUMENTATION,
        ))
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://data-connectors/data-sources/mapping-guide"),
            name="falcon_data_connectors_data_source_mapping_guide",
            description=(
                "Maps correlation rule template vendors to data connectors. "
                "Use to answer 'what rules can I enable?' and 'what data do I need for this rule?'. "
                "Explains that Falcon sensor data (CrowdStrike vendor) is always available without a connector."
            ),
            text=DATA_SOURCE_MAPPING_GUIDE,
        ))
        self._add_resource(server, TextResource(
            uri=AnyUrl("falcon://data-connectors/troubleshooting/troubleshooting-guide"),
            name="falcon_data_connectors_troubleshooting_guide",
            description="Troubleshooting guide for data connector connection issues, status meanings, and push connector HTTP errors.",
            text=DATA_CONNECTORS_TROUBLESHOOTING_GUIDE,
        ))

    # -------------------------------------------------------------------------
    # Read-only tools
    # -------------------------------------------------------------------------

    def search_data_connectors(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://data-connectors/connectors/search/fql-guide` for syntax. "
                "Use to find available connector types (the catalog), not active connections."
            ),
            examples={
                "vendor:~*'*aws*'",
                "connector_type:'push'",
                "name:~*'*cloudtrail*'",
            },
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of connectors to return.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting position for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort field and direction.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List available data connector types from the Falcon catalog.

        Returns the catalog of connector types (e.g. Okta, AWS CloudTrail, Microsoft Entra ID).
        Each connector includes: id, name, description, vendor_name, vendor_product_name, type
        (PUSH/PULL), parsers, and subscription.

        Use this to discover what connectors are available before creating a connection, or to
        find which connector provides data from a specific vendor.
        To determine which correlation rules you can enable with your current data, see
        falcon://data-connectors/data-sources/mapping-guide for the cross-referencing workflow.
        """
        result, pagination = self._base_search_with_meta(
            operation="ExternalListDataConnectors",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to list available data connectors",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result], filter, SEARCH_DATA_CONNECTORS_FQL_DOCUMENTATION
            )

        return self._build_pagination_envelope(result or [], pagination, filter)

    def search_data_connections(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://data-connectors/connections/search/fql-guide` for syntax. "
                "Use to find active data connections and their status."
            ),
            examples={
                "status:'Active'",
                "status:'Error',status:'Disconnected'",
                "status:'Active'+vendor_name:'Microsoft'",
                "name:*'*okta*'",
            },
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of connections to return.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting position for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort field and direction.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search active data connections and return full details including status.

        Use this to find deployed data connections, check their health, and identify
        connections with errors or that are idle/disconnected.
        Each connection includes: id, name, vendor_name, vendor_product_name, parser_name,
        status, source_type, last_ingested_volume_one_day, and ingest_url (for push).
        Consult falcon://data-connectors/connections/search/fql-guide before constructing filters.
        For troubleshooting, see falcon://data-connectors/troubleshooting/troubleshooting-guide.
        To determine which correlation rules match your onboarded data, see
        falcon://data-connectors/data-sources/mapping-guide.

        Connection status values (title-case required — lowercase is rejected by the API):
        - Active: Receiving data, no errors in the last hour
        - Idle: No data received in the last hour
        - Disconnected: Connection is down
        - Paused: Paused by user
        - Pending: Configuration in progress
        - Error: Errors in the last hour
        """
        result, pagination = self._base_search_with_meta(
            operation="ExternalListDataConnections",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search data connections",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result], filter, SEARCH_DATA_CONNECTIONS_FQL_DOCUMENTATION
            )

        return self._build_pagination_envelope(result or [], pagination, filter)

    def get_data_connection(
        self,
        id: str = Field(
            description="Data connection ID to retrieve details for.",
        ),
        include_token: bool = Field(
            default=False,
            description="Also retrieve the ingest token and URL. Only works for push-based connections.",
        ),
    ) -> dict[str, Any]:
        """Get full details for a data connection: configuration, status, and optionally ingest token.

        Returns connection details, provisioning status, and (if include_token=True) the
        ingest API token and URL for push-based connections. Use this to drill into a
        specific connection for troubleshooting or to get the push ingest credentials.
        A 202 on the token means the connection is still provisioning — retry shortly.
        """
        # Fetch connection details
        details = self._base_get_by_ids(
            operation="ExternalGetDataConnectionByID",
            ids=[id],
            use_params=True,
        )

        if self._is_error(details):
            return details

        # Fetch provisioning status
        status = self._base_get_by_ids(
            operation="ExternalGetDataConnectionStatus",
            ids=[id],
            use_params=True,
        )

        result: dict[str, Any] = {
            "connection": details[0] if isinstance(details, list) and details else details,
            "provisioning_status": status[0] if isinstance(status, list) and status else status,
        }

        # Optionally fetch ingest token (push connectors only)
        if include_token:
            token_resp = self._base_search_api_call(
                operation="ExternalGetDataConnectionToken",
                search_params={"ids": id},
                error_message="Failed to get data connection token",
            )
            result["token"] = token_resp

        return result

    # -------------------------------------------------------------------------
    # Write tools
    # -------------------------------------------------------------------------

    def create_data_connection(
        self,
        connector_id: str = Field(
            description=(
                "Connector type ID from the catalog. Use `falcon_search_data_connectors` "
                "to find available connector IDs."
            ),
        ),
        name: str | None = Field(
            default=None,
            description="Display name for the new connection.",
        ),
        description: str | None = Field(
            default=None,
            description="Optional description of the connection.",
        ),
        config_id: str | None = Field(
            default=None,
            description=(
                "ID of an existing data source configuration to use (pull-based connectors). "
                "Use `falcon_manage_connector_config` with action='list' to find config IDs."
            ),
        ),
        connector_type: str | None = Field(
            default=None,
            description="Connector type: 'push' or 'pull'.",
            examples={"push", "pull"},
        ),
        parser: str | None = Field(
            default=None,
            description="Parser to use for transforming incoming data.",
        ),
        vendor_name: str | None = Field(
            default=None,
            description="Vendor name for the data source.",
        ),
        vendor_product_name: str | None = Field(
            default=None,
            description="Vendor product name.",
        ),
        enable_host_enrichment: bool | None = Field(
            default=None,
            description="Enable host enrichment on ingested events. Enabled by default in the UI.",
        ),
        enable_user_enrichment: bool | None = Field(
            default=None,
            description="Enable user enrichment on ingested events. Enabled by default in the UI.",
        ),
        log_sources: list[str] | None = Field(
            default=None,
            description="List of log source identifiers to ingest from.",
        ),
        custom: dict[str, str] | None = Field(
            default=None,
            description=(
                "Connector-specific custom properties (e.g. API tokens). "
                "Keys are connector-defined (e.g. 'dcc1'). Use the Falcon UI to discover "
                "required custom fields for a connector."
            ),
        ),
        config: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Inline credential configuration for pull-based connectors. "
                "Object with `auth` (dict), `name` (str), and `params` (dict). "
                "Alternative to creating a config separately with `falcon_manage_connector_config` "
                "then passing `config_id`."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a new data connection.

        Creates a connection for a specified connector type. For push-based connectors,
        after creation use `falcon_get_data_connection` with include_token=True to get
        the ingest URL and API key. For pull-based connectors, provide a config_id with
        data source credentials. Returns the created connection record on success.
        """
        name = unwrap_field_default(name)
        description = unwrap_field_default(description)
        config_id = unwrap_field_default(config_id)
        connector_type = unwrap_field_default(connector_type)
        parser = unwrap_field_default(parser)
        vendor_name = unwrap_field_default(vendor_name)
        vendor_product_name = unwrap_field_default(vendor_product_name)
        enable_host_enrichment = unwrap_field_default(enable_host_enrichment)
        enable_user_enrichment = unwrap_field_default(enable_user_enrichment)
        log_sources = unwrap_field_default(log_sources)
        custom = unwrap_field_default(custom)
        config = unwrap_field_default(config)

        body: dict[str, Any] = {"connector_id": connector_id}

        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if config_id is not None:
            body["config_id"] = config_id
        if connector_type is not None:
            body["connector_type"] = connector_type
        if parser is not None:
            body["parser"] = parser
        if vendor_name is not None:
            body["vendor_name"] = vendor_name
        if vendor_product_name is not None:
            body["vendor_product_name"] = vendor_product_name
        if enable_host_enrichment is not None:
            body["enable_host_enrichment"] = enable_host_enrichment
        if enable_user_enrichment is not None:
            body["enable_user_enrichment"] = enable_user_enrichment
        if log_sources is not None:
            body["log_sources"] = log_sources
        if custom is not None:
            body["custom"] = custom
        if config is not None:
            body["config"] = config

        result = self._base_query_api_call(
            operation="ExternalCreateDataConnection",
            body_params=body,
            error_message="Failed to create data connection",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def manage_data_connection(
        self,
        ids: str = Field(
            description="ID of the data connection to manage.",
        ),
        name: str | None = Field(
            default=None,
            description="New display name for the connection.",
        ),
        description: str | None = Field(
            default=None,
            description="New description.",
        ),
        status: str | None = Field(
            default=None,
            description="Set to 'paused' to pause or 'active' to resume. Only for push connectors with Active/Error/Idle status.",
            examples={"paused", "active"},
        ),
        config_id: str | None = Field(
            default=None,
            description="New data source configuration ID (pull-based connectors only).",
        ),
        parser: str | None = Field(
            default=None,
            description="New parser for the connection.",
        ),
        enable_host_enrichment: bool | None = Field(
            default=None,
            description="Enable or disable host enrichment.",
        ),
        enable_user_enrichment: bool | None = Field(
            default=None,
            description="Enable or disable user enrichment.",
        ),
        log_sources: list[str] | None = Field(
            default=None,
            description="Updated list of log sources. Deselecting a source stops ingestion immediately.",
        ),
        custom: dict[str, str] | None = Field(
            default=None,
            description=(
                "Connector-specific custom properties to update (e.g. API tokens). "
                "Keys are connector-defined (e.g. 'dcc1'). Use the Falcon UI to discover "
                "required custom fields for a connector."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update a data connection: rename, change parser, toggle enrichment, or pause/resume.

        Only provided fields are changed; omitted fields keep their current values.
        To pause a push connection, set status='paused'. To resume, set status='active'.
        The connector type and API URL (push-based) cannot be changed.
        """
        # Unwrap FieldInfo defaults for optional params
        name = unwrap_field_default(name)
        description = unwrap_field_default(description)
        status = unwrap_field_default(status)
        config_id = unwrap_field_default(config_id)
        parser = unwrap_field_default(parser)
        enable_host_enrichment = unwrap_field_default(enable_host_enrichment)
        enable_user_enrichment = unwrap_field_default(enable_user_enrichment)
        log_sources = unwrap_field_default(log_sources)
        custom = unwrap_field_default(custom)

        results: list[dict[str, Any]] = []

        # Handle status change (pause/resume) via dedicated endpoint
        if status is not None:
            status_resp = self.client.command(
                "ExternalUpdateDataConnectionStatus",
                parameters={"ids": ids},
                body={"status": status},
            )
            status_result = handle_api_response(
                status_resp,
                operation="ExternalUpdateDataConnectionStatus",
                error_message="Failed to update connection status",
                default_result=[],
            )
            if self._is_error(status_result):
                return [status_result]
            results.append({"status_update": status_result})

        # Handle field updates via the update endpoint
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if config_id is not None:
            body["config_id"] = config_id
        if parser is not None:
            body["parser"] = parser
        if enable_host_enrichment is not None:
            body["enable_host_enrichment"] = enable_host_enrichment
        if enable_user_enrichment is not None:
            body["enable_user_enrichment"] = enable_user_enrichment
        if log_sources is not None:
            body["log_sources"] = log_sources
        if custom is not None:
            body["custom"] = custom

        if body:
            update_resp = self.client.command(
                "ExternalUpdateDataConnection",
                parameters={"ids": ids},
                body=body,
            )
            update_result = handle_api_response(
                update_resp,
                operation="ExternalUpdateDataConnection",
                error_message="Failed to update data connection",
                default_result=[],
            )
            if self._is_error(update_result):
                return [update_result]
            results.append({"connection_update": update_result})

        return results if results else [{"message": "No changes requested"}]

    def delete_data_connection(
        self,
        ids: str = Field(
            description="ID of the data connection to delete. This action is permanent and cannot be undone.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Permanently delete a data connection.

        Removes the connection and stops all data ingestion. This cannot be undone.
        Use falcon_search_data_connections to confirm the connection ID before deleting.
        """
        result = self._base_query_api_call(
            operation="ExternalDeleteDataConnection",
            query_params={"ids": ids},
            error_message="Failed to delete data connection",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def regenerate_data_connection_token(
        self,
        ids: str = Field(
            description="ID of the push-based data connection to regenerate the token for.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Regenerate the ingest API token for a push-based data connection.

        The old token is immediately invalidated. You must update any data shippers
        or third-party systems with the new token. All access tokens issued before
        regeneration are immediately revoked.
        """
        result = self._base_query_api_call(
            operation="ExternalRegenerateDataConnectionToken",
            query_params={"ids": ids},
            error_message="Failed to regenerate data connection token",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def manage_connector_config(
        self,
        action: str = Field(
            description="Action to perform: 'list', 'create', 'update', or 'delete'.",
            examples={"list", "create", "update", "delete"},
        ),
        connector_id: str = Field(
            description="Connector type ID (for list/create/delete).",
        ),
        config_id: str | None = Field(
            default=None,
            description="Configuration ID (required for update and delete).",
        ),
        config_ids: list[str] | None = Field(
            default=None,
            description="Configuration IDs to delete (for delete action, max 20).",
        ),
        config: dict[str, Any] | None = Field(
            default=None,
            description=(
                "Configuration object with provider-specific fields (for create/update). "
                "Use action='list' first to see existing configs and understand the expected structure."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Manage data source configurations for pull-based connectors.

        Configurations define how Falcon accesses a third-party data source (credentials,
        endpoints, etc.) and can be reused across multiple connections.

        Actions:
        - list: List configs for a connector type (requires connector_id)
        - create: Create a new config (requires connector_id + config)
        - update: Update an existing config (requires config_id + connector_id + config)
        - delete: Delete configs (requires connector_id + config_ids)
        """
        if action == "list":
            result = self._base_search_api_call(
                operation="ExternalListConnectorConfigs",
                search_params={"ids": connector_id},
                error_message="Failed to list connector configurations",
            )
            if self._is_error(result):
                return [result]
            return result

        if action == "create":
            if not config:
                return [_format_error_response("`config` is required for create action.")]
            result = self._base_query_api_call(
                operation="ExternalCreateConnectorConfig",
                body_params={"connector_id": connector_id, "config": config},
                error_message="Failed to create connector configuration",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        if action == "update":
            if not config_id:
                return [_format_error_response("`config_id` is required for update action.")]
            if not config:
                return [_format_error_response("`config` is required for update action.")]
            response = self.client.command(
                "ExternalPatchConnectorConfig",
                parameters={"ids": config_id},
                body={"connector_id": connector_id, "config": config},
            )
            return handle_api_response(
                response,
                operation="ExternalPatchConnectorConfig",
                error_message="Failed to update connector configuration",
                default_result=[],
            )

        if action == "delete":
            ids_to_delete = config_ids or ([config_id] if config_id else [])
            if not ids_to_delete:
                return [_format_error_response("`config_ids` or `config_id` is required for delete action.")]
            result = self._base_query_api_call(
                operation="ExternalDeleteConnectorConfigs",
                query_params={"connector_id": connector_id, "ids": ids_to_delete},
                error_message="Failed to delete connector configurations",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        return [_format_error_response(f"Unknown action '{action}'. Use: list, create, update, or delete.")]
