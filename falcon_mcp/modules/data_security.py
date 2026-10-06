"""
Data Security module for Falcon MCP Server.

Provides access to Data Security configuration data — classifications,
policies, content patterns, cloud/local applications, enterprise accounts, web
locations, sensitivity labels, and file types — so an LLM can inspect, create,
and update Data Security rule definitions.

For Data Security detections, use falcon_search_detections with
product:'data-protection'. For EDD scan results, use falcon_search_ngsiem with
#event_simpleName=Event_DataProtectionClassifiedFileEvent.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.data_security import (
    DATA_MODEL_DOCUMENTATION,
    SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION,
    SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION,
    SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION,
    SEARCH_ENTERPRISE_ACCOUNTS_FQL_DOCUMENTATION,
    SEARCH_FILE_TYPES_FQL_DOCUMENTATION,
    SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION,
    SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION,
    SEARCH_POLICIES_FQL_DOCUMENTATION,
    SEARCH_SENSITIVITY_LABELS_FQL_DOCUMENTATION,
    SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION,
    WORKFLOW_GUIDE_DOCUMENTATION,
)

# Body-parameter documentation shared by the generic create/update tools. The
# body is an opaque dict whose shape depends on entity_type.
_WRITE_BODY_DOC = """JSON object with the entity's fields. Shape depends on entity_type:

- classification: {name, classification_properties:{content_patterns, content_patterns_operator,
  file_types, sensitivity_labels, web_sources, win_file_path_patterns, mac_file_path_patterns,
  protection_mode ('monitor'|'simulate'|'enforce'), rules:[{user_scope, ad_users, ad_groups,
  detection_severity, response_action ('allow'|'block'|'justify'), trigger_detection,
  notify_end_user, enable_usb_devices, enable_printer_egress, enable_web_locations,
  enable_local_application_groups, web_locations_scope, web_locations, local_application_groups}]}}
- policy: {name, description, is_enabled, precedence, host_groups, policy_properties:{classifications,
  enable_content_inspection, inspection_depth, min_confidence_level, ...}}. Requires the
  platform_name argument ('win' or 'mac').
- content_pattern: {name, category ('PII'|'PCI DSS'|'PHI'|'Custom'|'ITAR'|'Secret'), description,
  example, regexes:[...], min_match_threshold, region}
- cloud_application: {name, urls:[{fqdn, path}], description}
- enterprise_account: {name, application_group_id ('google'|'microsoft'|'box'), domains:[...],
  plugin_config_id}
- web_location: {name, application_id, location_type, type, enterprise_account_id,
  provider_location_id, provider_location_name, web_location_group_ids}
- local_application: {name, executable_name, group_ids, apply_rules_for_children_processes,
  enable_rename_detection, emit_rule_matched_events_only}
- local_application_group: {name, local_application_ids, description}
- sensitivity_label: {name, display_name, external_id, label_provider ('microsoft'|'google'),
  plugins_configuration_id, co_authoring, synced} (create only; update unsupported)

All referenced IDs must be real IDs obtained via search/get — never guess them.
For UPDATES, include the entity "id" inside this object. See
falcon://data-security/entities/model-guide for entity relationships."""


# Ordered tuple of supported entity_type discriminator values. Also drives the
# accepted-values list surfaced in guiding errors.
DP_ENTITY_TYPES = (
    "classification",
    "policy",
    "content_pattern",
    "cloud_application",
    "enterprise_account",
    "web_location",
    "local_application",
    "local_application_group",
    "sensitivity_label",
    "file_type",
)


class DataSecurityModule(BaseModule):
    """CrowdStrike Data Security configuration module.

    Read and write access to Data Security rule definitions — classifications,
    policies, content patterns, cloud/local applications, enterprise accounts,
    web locations, sensitivity labels, and file types.

    Required API Scopes:
    - Data Protection:read (search and get tools)
    - Data Protection:write (create and update tools)
    """

    # Per-entity dispatch table. FalconPy operation IDs are recorded verbatim
    # (note the inconsistent _v2 suffixes). Unsupported operations are None.
    #   query / get / create / update: FalconPy operation IDs
    #   create_wrapper / update_wrapper: how the create / update body is wrapped
    #                 ("resources", "web_locations", or None for a direct body)
    #   update_id_query: True when update passes the id as a query param (flat entities)
    #   update_merge: True when update replaces the whole entity, so the current
    #                 entity is fetched and the caller's fields overlaid onto it
    #   platform: True when the entity requires platform_name
    _OPERATIONS: dict[str, dict[str, Any]] = {
        "classification": {
            "query": "queries_classification_get_v2",
            "get": "entities_classification_get_v2",
            "create": "entities_classification_post_v2",
            "update": "entities_classification_patch_v2",
            "create_wrapper": "resources",
            "update_wrapper": "resources",
            "update_id_query": False,
            "update_merge": False,
            "platform": False,
        },
        "policy": {
            "query": "queries_policy_get_v2",
            "get": "entities_policy_get_v2",
            "create": "entities_policy_post_v2",
            "update": "entities_policy_patch_v2",
            "create_wrapper": "resources",
            "update_wrapper": "resources",
            "update_id_query": False,
            "update_merge": False,
            "platform": True,
        },
        "content_pattern": {
            "query": "queries_content_pattern_get_v2",
            "get": "entities_content_pattern_get",
            "create": "entities_content_pattern_create",
            "update": "entities_content_pattern_patch",
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
        "cloud_application": {
            "query": "queries_cloud_application_get_v2",
            "get": "entities_cloud_application_get",
            "create": "entities_cloud_application_create",
            "update": "entities_cloud_application_patch",
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
        "enterprise_account": {
            "query": "queries_enterprise_account_get_v2",
            "get": "entities_enterprise_account_get",
            "create": "entities_enterprise_account_create",
            "update": "entities_enterprise_account_patch",
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
        "web_location": {
            "query": "queries_web_location_get_v2",
            "get": "entities_web_location_get_v2",
            "create": "entities_web_location_create_v2",
            "update": "entities_web_location_patch_v2",
            "create_wrapper": "web_locations",
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
        "local_application": {
            "query": "queries_local_application_get",
            "get": "entities_local_application_get",
            "create": "entities_local_application_create",
            "update": "entities_local_application_patch",
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": True,
            "platform": False,
        },
        "local_application_group": {
            "query": "queries_local_application_group_get",
            "get": "entities_local_application_group_get",
            "create": "entities_local_application_group_create",
            "update": "entities_local_application_group_patch",
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": True,
            "platform": False,
        },
        "sensitivity_label": {
            "query": "queries_sensitivity_label_get_v2",
            "get": "entities_sensitivity_label_get_v2",
            "create": "entities_sensitivity_label_create_v2",
            "update": None,
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
        "file_type": {
            "query": "queries_file_type_get_v2",
            "get": "entities_file_type_get",
            "create": None,
            "update": None,
            "create_wrapper": None,
            "update_wrapper": None,
            "update_id_query": True,
            "update_merge": False,
            "platform": False,
        },
    }

    _FQL_DOCS = {
        "classification": SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION,
        "policy": SEARCH_POLICIES_FQL_DOCUMENTATION,
        "content_pattern": SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION,
        "cloud_application": SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION,
        "enterprise_account": SEARCH_ENTERPRISE_ACCOUNTS_FQL_DOCUMENTATION,
        "web_location": SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION,
        "local_application": SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION,
        "local_application_group": SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION,
        "sensitivity_label": SEARCH_SENSITIVITY_LABELS_FQL_DOCUMENTATION,
        "file_type": SEARCH_FILE_TYPES_FQL_DOCUMENTATION,
    }

    # Server-managed fields dropped from a fetched entity before it is sent back
    # as an update_merge body.
    _SERVER_MANAGED_FIELDS = frozenset(
        {"id", "cid", "created_at", "updated_at", "deleted", "deleted_at"}
    )

    def _validate_entity_type(self, entity_type):
        """Validate the entity_type discriminator.

        Returns None when valid, or a guiding error response dict when invalid.
        """
        if entity_type not in self._OPERATIONS:
            return _format_error_response(
                f"Invalid entity_type: '{entity_type}'. "
                f"Accepted values: {', '.join(DP_ENTITY_TYPES)}."
            )
        return None

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        # --- Search & get (read-only) ---
        self._add_tool(
            server=server,
            method=self.search_data_security_entities,
            name="search_data_security_entities",
        )
        self._add_tool(
            server=server,
            method=self.get_data_security_entities,
            name="get_data_security_entities",
        )

        # --- Create / update (write) ---
        self._add_tool(
            server=server,
            method=self.create_data_security_entity,
            name="create_data_security_entity",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.update_data_security_entity,
            name="update_data_security_entity",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/classifications/fql-guide"),
                name="falcon_search_data_security_classifications_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='classification'`.",
                text=SEARCH_CLASSIFICATIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/policies/fql-guide"),
                name="falcon_search_data_security_policies_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='policy'`.",
                text=SEARCH_POLICIES_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/content-patterns/fql-guide"),
                name="falcon_search_data_security_content_patterns_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='content_pattern'`.",
                text=SEARCH_CONTENT_PATTERNS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/cloud-applications/fql-guide"),
                name="falcon_search_data_security_cloud_applications_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='cloud_application'`.",
                text=SEARCH_CLOUD_APPLICATIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/enterprise-accounts/fql-guide"),
                name="falcon_search_data_security_enterprise_accounts_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='enterprise_account'`.",
                text=SEARCH_ENTERPRISE_ACCOUNTS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/web-locations/fql-guide"),
                name="falcon_search_data_security_web_locations_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='web_location'`.",
                text=SEARCH_WEB_LOCATIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/local-applications/fql-guide"),
                name="falcon_search_data_security_local_applications_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='local_application'`.",
                text=SEARCH_LOCAL_APPLICATIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/local-application-groups/fql-guide"),
                name="falcon_search_data_security_local_application_groups_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='local_application_group'`.",
                text=SEARCH_LOCAL_APPLICATION_GROUPS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/sensitivity-labels/fql-guide"),
                name="falcon_search_data_security_sensitivity_labels_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='sensitivity_label'`.",
                text=SEARCH_SENSITIVITY_LABELS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/file-types/fql-guide"),
                name="falcon_search_data_security_file_types_fql_guide",
                description="Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='file_type'`.",
                text=SEARCH_FILE_TYPES_FQL_DOCUMENTATION,
            ),
        )

        # Non-FQL guide resources — agent behavioral guidance delivered via MCP
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/entities/model-guide"),
                name="falcon_data_security_entity_model",
                description="Data Security entity relationship model. Shows how Policies reference Classifications, which combine Content Patterns, File Types, Web Origins, Sensitivity Labels, and Rules.",
                text=DATA_MODEL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/agent/behavioral-guide"),
                name="falcon_data_security_behavioral_guide",
                description="Behavioral guidance for working with Data Security entities: domain context and operational rules.",
                text=WORKFLOW_GUIDE_DOCUMENTATION,
            ),
        )

    # ── Shared helpers ────────────────────────────────────────────────────

    def _search_entity(
        self,
        query_op: str,
        get_op: str,
        fql_documentation: str,
        search_params: dict[str, Any],
        error_message: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search (query IDs) then hydrate (get by IDs) in one round-trip."""
        filter_used = search_params.get("filter")

        ids, pagination = self._base_search_with_meta(
            operation=query_op,
            search_params=search_params,
            error_message=error_message,
        )
        if self._is_error(ids):
            return self._format_fql_error_response([ids], filter_used, fql_documentation)
        if not ids:
            return self._build_pagination_envelope([], pagination, filter_used)

        details = self._base_get_by_ids(get_op, ids, use_params=True)
        if self._is_error(details):
            return [details]
        details = self._reorder_by_ids(ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter_used)

    def _write_entity(
        self,
        operation: str,
        body: dict[str, Any],
        query_params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Execute a create/update call, wrapping errors in a list per convention."""
        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            body_params=body,
            error_message=f"Failed to execute {operation}",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    # ── Search / get tools (generic, entity_type-keyed) ───────────────────

    def search_data_security_entities(
        self,
        entity_type: str = Field(
            description=(
                "Data Security entity type to search. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group, "
                "sensitivity_label, file_type."
            ),
        ),
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. Supported fields vary by entity_type; see "
                "falcon://data-security/<entity>/fql-guide (e.g. "
                "falcon://data-security/classifications/fql-guide) for syntax."
            ),
        ),
        limit: int = Field(
            default=100, ge=1, le=500, description="Maximum number of records to return."
        ),
        offset: int = Field(default=0, ge=0, description="Pagination offset."),
        sort: str | None = Field(
            default=None,
            description=(
                "Sort order as field.direction, e.g. name.asc or created.desc. "
                "Valid fields vary by entity_type; see its FQL guide."
            ),
        ),
        platform_name: str | None = Field(
            default=None,
            description="Required only for entity_type='policy': 'win' or 'mac'.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Data Security (DLP, formerly Data Protection) configuration entities.

        Covers classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, local application
        groups, sensitivity labels, and file types; a policy search also needs
        platform_name. Consult the entity's FQL guide before constructing filter
        expressions, e.g. falcon://data-security/policies/fql-guide (all ten are
        listed in falcon://data-security/entities/model-guide). Returns full entity
        details in a pagination envelope whose `pagination.total` is the API's count
        of matches, or null when the API does not report one.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        ops = self._OPERATIONS[entity_type]
        if ops["platform"] and not platform_name:
            return [_format_error_response(
                f"platform_name is required for entity_type='{entity_type}' ('win' or 'mac')."
            )]

        search_params: dict[str, Any] = {
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        if ops["platform"]:
            search_params["platform_name"] = platform_name

        return self._search_entity(
            ops["query"],
            ops["get"],
            self._FQL_DOCS[entity_type],
            search_params,
            f"Failed to search Data Security {entity_type} entities",
        )

    def get_data_security_entities(
        self,
        entity_type: str = Field(
            description=(
                "Data Security entity type to retrieve. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group, "
                "sensitivity_label, file_type."
            ),
        ),
        ids: list[str] = Field(
            description="Entity IDs to retrieve (from a search or create response)."
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve full details of Data Security entities of one entity_type by ID.

        Use when you already hold IDs, such as the ones one entity lists for the
        entities it references; to find entities by their attributes, use
        falcon_search_data_security_entities instead. See
        falcon://data-security/entities/model-guide for how the entities reference
        each other. Returns a list of the matching entities.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        ops = self._OPERATIONS[entity_type]
        result = self._base_get_by_ids(ops["get"], ids, use_params=True)
        if self._is_error(result):
            return [result]
        return result

    # ── Create / update tools (generic, entity_type-keyed) ────────────────

    @staticmethod
    def _wrap_body(wrapper: str | None, body: dict[str, Any]) -> dict[str, Any]:
        """Wrap a write body per the entity's envelope convention."""
        if wrapper is None:
            return body
        return {wrapper: [body]}

    def create_data_security_entity(
        self,
        entity_type: str = Field(
            description=(
                "Data Security entity type to create. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group, "
                "sensitivity_label. (file_type is read-only and cannot be created.)"
            ),
        ),
        body: dict[str, Any] = Field(description=_WRITE_BODY_DOC),
        platform_name: str | None = Field(
            default=None,
            description="Required only for entity_type='policy': 'win' or 'mac'.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a Data Security entity of the chosen entity_type.

        Creates classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, local application
        groups, and sensitivity labels; policies also need platform_name. Bodies
        reference other entities by ID, so look those IDs up with search first and
        never guess them. Returns a list containing the created entity.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        ops = self._OPERATIONS[entity_type]
        create_op = ops["create"]
        if create_op is None:
            return [_format_error_response(
                f"entity_type='{entity_type}' is read-only and does not support create."
            )]
        if ops["platform"] and not platform_name:
            return [_format_error_response(
                f"platform_name is required for entity_type='{entity_type}' ('win' or 'mac')."
            )]

        query_params = {"platform_name": platform_name} if ops["platform"] else None
        return self._write_entity(
            create_op,
            self._wrap_body(ops["create_wrapper"], body),
            query_params=query_params,
        )

    def update_data_security_entity(
        self,
        entity_type: str = Field(
            description=(
                "Data Security entity type to update. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group. "
                "(sensitivity_label and file_type do not support update.)"
            ),
        ),
        body: dict[str, Any] = Field(description=_WRITE_BODY_DOC),
        platform_name: str | None = Field(
            default=None,
            description="Required only for entity_type='policy': 'win' or 'mac'.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update an existing Data Security entity of the chosen entity_type.

        Updates classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, and local
        application groups; policies also need platform_name. Find the entity with
        search, then send its "id" plus only the fields to change. Returns a list
        containing the updated entity.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        ops = self._OPERATIONS[entity_type]
        update_op = ops["update"]
        if update_op is None:
            return [_format_error_response(
                f"entity_type='{entity_type}' does not support update."
            )]
        if ops["platform"] and not platform_name:
            return [_format_error_response(
                f"platform_name is required for entity_type='{entity_type}' ('win' or 'mac')."
            )]

        query_params = None
        body_for_wrap = body
        if ops["update_id_query"]:
            entity_id = body.get("id")
            if not entity_id:
                return [_format_error_response(
                    f"body must include an 'id' field to update entity_type='{entity_type}'."
                )]
            body_for_wrap = {k: v for k, v in body.items() if k != "id"}
            query_params = {"id": entity_id}
            if ops["update_merge"]:
                current = self._base_get_by_ids(ops["get"], [entity_id], use_params=True)
                if self._is_error(current):
                    return [current]
                if not isinstance(current, list) or not current:
                    return [_format_error_response(
                        f"No {entity_type} found with id '{entity_id}'. "
                        "Use falcon_search_data_security_entities to find a valid id."
                    )]
                existing = {
                    k: v for k, v in current[0].items() if k not in self._SERVER_MANAGED_FIELDS
                }
                body_for_wrap = {**existing, **body_for_wrap}
        else:
            if not body.get("id"):
                return [_format_error_response(
                    f"body must include an 'id' field to update entity_type='{entity_type}'."
                )]
            if ops["platform"]:
                query_params = {"platform_name": platform_name}

        return self._write_entity(
            update_op,
            self._wrap_body(ops["update_wrapper"], body_for_wrap),
            query_params=query_params,
        )
