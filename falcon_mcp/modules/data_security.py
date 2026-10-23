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

import re
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import (
    ERROR_CODE_DESCRIPTIONS,
    _format_error_response,
    handle_api_response,
)
from falcon_mcp.common.utils import prepare_api_parameters, unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.data_security import (
    BODY_GUIDE_NOTATION,
    CLASSIFICATION_BODY_GUIDE,
    CLOUD_APPLICATION_BODY_GUIDE,
    CONTENT_PATTERN_BODY_GUIDE,
    DATA_MODEL_DOCUMENTATION,
    ENTERPRISE_ACCOUNT_BODY_GUIDE,
    LOCAL_APPLICATION_BODY_GUIDE,
    LOCAL_APPLICATION_GROUP_BODY_GUIDE,
    POLICY_BODY_GUIDE,
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
    SENSITIVITY_LABEL_BODY_GUIDE,
    WEB_LOCATION_BODY_GUIDE,
    WORKFLOW_GUIDE_DOCUMENTATION,
)

# Shared reference-ID guidance for the create/update body parameter.
_BODY_REFERENCES_DOC = (
    "Referenced IDs must be real IDs from search/get, never guessed. Rule ad_users / "
    "ad_groups SIDs cannot be looked up: ask the user for them, never invent them."
)

_CREATE_BODY_DOC = (
    "The entity's fields, shaped as its body guide (falcon_get_data_security_entity_schema): "
    "classification fields under classification_properties (rules inside it), policy "
    "fields under policy_properties. " + _BODY_REFERENCES_DOC
)

_UPDATE_BODY_DOC = (
    '"id" plus only the fields to change; omitted fields keep their value. Nesting as for '
    'create. Never copy an "<elided …>" placeholder from a result into the body; leave '
    "that field out. " + _BODY_REFERENCES_DOC
)

_WRITE_PLATFORM_DOC = "Required for entity_type 'policy' ('win' or 'mac'); never put it in the body."

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

# entity_type values each tool accepts, as JSON-schema enums. Every type can be
# read; file_type is read-only, so create leaves it out, and update also leaves out
# create-only sensitivity_label.
ReadEntityType = Literal[
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
]
WriteEntityType = Literal[
    "classification",
    "policy",
    "content_pattern",
    "cloud_application",
    "enterprise_account",
    "web_location",
    "local_application",
    "local_application_group",
    "sensitivity_label",
]
UpdateEntityType = Literal[
    "classification",
    "policy",
    "content_pattern",
    "cloud_application",
    "enterprise_account",
    "web_location",
    "local_application",
    "local_application_group",
]
PlatformName = Literal["win", "mac"]
DeletedMode = Literal["exclude", "include", "only"]

# A `deleted` field term in a caller's FQL filter (deleted:true, deleted:!false, ...).
# Quoted values are blanked first so text such as name:~'deleted: old' is not a match.
_DELETED_FIELD = re.compile(r"\bdeleted\s*:")
_QUOTED_VALUE = re.compile(r"'(?:[^'\\]|\\.)*'")

# Upper bound on the IDs one get-by-IDs call takes: a parity cap with agentgateway,
# not a documented API limit. Search hydrates every ID its query step returns, so
# the search limit shares it.
_MAX_IDS = 100

# Appended to a failed write whose outcome is unknown: a blind retry of a create
# could duplicate the entity.
_MAY_HAVE_APPLIED = (
    "The request may have been applied, so verify its effect (e.g. search for the "
    "entity) before retrying."
)

# Data Security records can carry inline binary data: a policy's
# policy_properties.euj_dialog_box_logo is a base64 PNG data URI of 10-20 KB, about
# two thirds of the record. Results replace large data URIs with a placeholder that
# starts with _ELIDED_PREFIX, and a write body that echoes one is rejected, as
# sending it back would overwrite the stored value with the placeholder.
_ELIDED_PREFIX = "<elided "
# Shorter data URIs cost little and may be meaningful to show as-is.
_ELIDE_MIN_LEN = 256

# The fields value that asks a search for full records.
_ALL_FIELDS = "*"


def _elide_binary(value: Any) -> Any:
    """Return value with every data URI of at least _ELIDE_MIN_LEN characters, at
    any depth, replaced by a placeholder naming its media type and size."""
    if isinstance(value, dict):
        return {k: _elide_binary(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_elide_binary(v) for v in value]
    if isinstance(value, str) and len(value) >= _ELIDE_MIN_LEN and value.startswith("data:"):
        media = value[len("data:"):].split(",", 1)[0]
        return (
            f"{_ELIDED_PREFIX}data URI ({media}), {len(value)} bytes: omitted from results; "
            "never send this placeholder back in a write>"
        )
    return value


def _elided_paths(value: Any, path: str = "") -> list[str]:
    """Return the dotted paths of the elision placeholders in a write body, in key order."""
    if isinstance(value, dict):
        return [
            found
            for key in sorted(value)
            for found in _elided_paths(value[key], f"{path}.{key}" if path else key)
        ]
    if isinstance(value, list):
        return [found for i, v in enumerate(value) for found in _elided_paths(v, f"{path}[{i}]")]
    if isinstance(value, str) and value.startswith(_ELIDED_PREFIX):
        return [path]
    return []


def _project(records: list[Any], fields: list[str] | None) -> list[Any]:
    """Return each record reduced to "id" plus the dotted field paths in fields (e.g.
    "name", "policy_properties.classifications"), keeping their nesting.

    Paths a record does not have are skipped; no fields keeps every field.
    """
    if not fields:
        return records
    projected = []
    for record in records:
        if not isinstance(record, dict):
            projected.append(record)
            continue
        kept = {"id": record["id"]} if "id" in record else {}
        for field in fields:
            _copy_path(record, kept, field.split("."))
        projected.append(kept)
    return projected


def _copy_path(src: dict[str, Any], dst: dict[str, Any], path: list[str]) -> None:
    """Copy the value at path from src into dst, creating the intermediate dicts,
    when every step of the path exists in src."""
    if path[0] not in src:
        return
    value = src[path[0]]
    if len(path) == 1:
        dst[path[0]] = value
        return
    if not isinstance(value, dict):
        return
    sub = dst[path[0]] if isinstance(dst.get(path[0]), dict) else {}
    _copy_path(value, sub, path[1:])
    if sub:
        dst[path[0]] = sub


class DataSecurityModule(BaseModule):
    """CrowdStrike Data Security configuration module.

    Read and write access to Data Security rule definitions — classifications,
    policies, content patterns, cloud/local applications, enterprise accounts,
    web locations, sensitivity labels, and file types.

    Required API Scopes:
    - Data Protection:read (search and get tools)
    - Data Protection:write (create tool)
    - Data Protection:read and Data Protection:write (update tool)

    Searches of policies and classifications return summary records unless the
    caller names fields: a deliberate exception to returning full entity details,
    as a page of full policies (5-20 KB each) outgrows client output limits.
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
    #   soft_delete: True when deleted entities are kept with deleted:true, which
    #                search hides unless the deleted argument asks for them
    #   summary_fields: the fields a search returns when the caller names none (the
    #                   records are several KB each), or None for full records
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
            "soft_delete": False,
            "summary_fields": (
                "name",
                "classification_properties.protection_mode",
                "classification_properties.content_patterns",
                "classification_properties.content_patterns_operator",
                "classification_properties.file_types",
                "classification_properties.sensitivity_labels",
                "classification_properties.web_sources",
                "classification_properties.win_file_path_patterns",
                "classification_properties.mac_file_path_patterns",
                "modified_at",
            ),
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
            "soft_delete": False,
            "summary_fields": (
                "name",
                "description",
                "platform_name",
                "is_enabled",
                "is_default",
                "precedence",
                "host_groups",
                "policy_properties.classifications",
                "modified_at",
            ),
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": True,
            "summary_fields": None,
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
            "soft_delete": False,
            "summary_fields": None,
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

    # Write body guide per writable entity type; file_type is read-only and has none.
    _BODY_GUIDES = {
        "classification": CLASSIFICATION_BODY_GUIDE,
        "policy": POLICY_BODY_GUIDE,
        "content_pattern": CONTENT_PATTERN_BODY_GUIDE,
        "cloud_application": CLOUD_APPLICATION_BODY_GUIDE,
        "enterprise_account": ENTERPRISE_ACCOUNT_BODY_GUIDE,
        "web_location": WEB_LOCATION_BODY_GUIDE,
        "local_application": LOCAL_APPLICATION_BODY_GUIDE,
        "local_application_group": LOCAL_APPLICATION_GROUP_BODY_GUIDE,
        "sensitivity_label": SENSITIVITY_LABEL_BODY_GUIDE,
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
        # --- Search, get & schema (read-only) ---
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
        self._add_tool(
            server=server,
            method=self.get_data_security_entity_schema,
            name="get_data_security_entity_schema",
            annotations=ToolAnnotations(
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
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

        # Write body guides — the same text falcon_get_data_security_entity_schema serves
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/classifications/body-guide"),
                name="falcon_data_security_classification_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='classification'`.",
                text=CLASSIFICATION_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/policies/body-guide"),
                name="falcon_data_security_policy_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='policy'`.",
                text=POLICY_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/content-patterns/body-guide"),
                name="falcon_data_security_content_pattern_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='content_pattern'`.",
                text=CONTENT_PATTERN_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/cloud-applications/body-guide"),
                name="falcon_data_security_cloud_application_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='cloud_application'`.",
                text=CLOUD_APPLICATION_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/enterprise-accounts/body-guide"),
                name="falcon_data_security_enterprise_account_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='enterprise_account'`.",
                text=ENTERPRISE_ACCOUNT_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/web-locations/body-guide"),
                name="falcon_data_security_web_location_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='web_location'`.",
                text=WEB_LOCATION_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/local-applications/body-guide"),
                name="falcon_data_security_local_application_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='local_application'`.",
                text=LOCAL_APPLICATION_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/local-application-groups/body-guide"),
                name="falcon_data_security_local_application_group_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='local_application_group'`.",
                text=LOCAL_APPLICATION_GROUP_BODY_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/sensitivity-labels/body-guide"),
                name="falcon_data_security_sensitivity_label_body_guide",
                description="Contains the guide for the `body` param of the `falcon_create_data_security_entity` tool with `entity_type='sensitivity_label'`.",
                text=SENSITIVITY_LABEL_BODY_GUIDE,
            ),
        )

        # Non-FQL guide resources — agent behavioral guidance delivered via MCP
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://data-security/entities/model-guide"),
                name="falcon_data_security_entity_model",
                description="Data Security entity relationship model. Policies reference ordered Classifications, which combine detection criteria (Content Patterns, File Types, Sensitivity Labels, Web Origins, File Paths), a protection mode, and nested Rules (channels, Web Destinations, Local Application Groups, user scope, response action). Also covers the supporting Cloud Applications, Enterprise Accounts, Web Locations, and Local Applications.",
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

    def _command(
        self,
        operation: str,
        parameters: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call an operation and return the raw response.

        The shared helpers keep only `body.resources`; these tools also need
        `body.errors`, which a 2xx can carry next to (or instead of) resources.
        The body is sent as-is, so a value the caller set to null reaches the API.
        """
        call_args: dict[str, Any] = {}
        if parameters:
            call_args["parameters"] = prepare_api_parameters(parameters)
        if body is not None:
            call_args["body"] = body
        return self.client.command(operation, **call_args)

    def _split_result(
        self,
        response: dict[str, Any],
        operation: str,
        error_message: str,
        entity_type: str,
        verb: str | None = None,
    ) -> tuple[list[Any], list[Any] | None, dict[str, Any] | None]:
        """Split a response into (resources, warnings, error).

        A non-2xx is an error. A 2xx whose errors sit next to resources returns
        the resources with the errors as warnings, so per-item failures (e.g. a
        get where some IDs do not exist) reach the caller. A 2xx with errors and
        no resources failed as a whole and is an error. verb is "create" or
        "update" for writes and None for reads.
        """
        status_code = response.get("status_code")
        if status_code is None or status_code >= 300:
            if verb is None:
                error = handle_api_response(
                    response, operation=operation, error_message=error_message
                )
                return [], None, error
            body = response.get("body") or {}
            errors = body.get("errors") if isinstance(body, dict) else None
            return [], None, self._write_error(
                response, errors or [], status_code, operation, error_message, entity_type, verb
            )

        body = response.get("body") or {}
        resources = body.get("resources") or []
        errors = body.get("errors") or []
        if not errors:
            return resources, None, None
        if resources:
            return resources, errors, None
        return [], None, self._errors_only_error(
            response, errors, operation, error_message, entity_type, verb
        )

    def _errors_only_error(
        self,
        response: dict[str, Any],
        errors: list[Any],
        operation: str,
        error_message: str,
        entity_type: str,
        verb: str | None,
    ) -> dict[str, Any]:
        """Build the error for a 2xx that carries errors and no resources.

        The HTTP status says nothing about the failure, so the status code is
        taken from the first error that carries one.
        """
        status_code = response.get("status_code")
        for e in errors:
            code = e.get("code") if isinstance(e, dict) else None
            if isinstance(code, int) and code >= 400:
                status_code = code
                break
        if verb is not None:
            return self._write_error(
                response, errors, status_code, operation, error_message, entity_type, verb
            )
        return _format_error_response(
            f"{error_message}: {self._status_message(status_code, errors, verb)}",
            details={**response, "status_code": status_code},
            operation=operation,
        )

    @staticmethod
    def _status_message(status_code: int | None, errors: list[Any], verb: str | None) -> str:
        """Describe a failed status, followed by the API's own error messages.

        A write rejected as a bad request gets write wording: the shared 400 text is
        about FQL filter syntax, which a create/update body does not have.
        """
        if verb is not None and status_code in (400, 422):
            message = "The API rejected the request body."
        elif status_code is not None and status_code >= 300:
            message = ERROR_CODE_DESCRIPTIONS.get(
                status_code, f"Request failed with status code {status_code}"
            )
        else:
            message = f"The API answered HTTP {status_code} but the request did not succeed."
        api_messages = [e["message"] for e in errors if isinstance(e, dict) and e.get("message")]
        if api_messages:
            message += f" API said: {'; '.join(m.rstrip('.') for m in api_messages)}."
        return message

    def _write_error(
        self,
        response: dict[str, Any],
        errors: list[Any],
        status_code: int | None,
        operation: str,
        error_message: str,
        entity_type: str,
        verb: str,
    ) -> dict[str, Any]:
        """Build the error for a failed create/update.

        A 400/422 gets the entity's body guide. A failure whose outcome is unknown
        — a server error, no status, or a 2xx with no error code to go by — also
        says the write may have been applied, so the caller verifies before
        retrying; a clean 4xx means it was not.
        """
        message = f"{error_message}: {self._status_message(status_code, errors, verb)}"
        if status_code is None or status_code >= 500 or status_code < 300:
            message += f" {_MAY_HAVE_APPLIED}"
        error = _format_error_response(
            message, details={**response, "status_code": status_code}, operation=operation
        )
        return self._with_body_guide(error, status_code, entity_type, verb)

    def _with_body_guide(
        self,
        error: dict[str, Any],
        status_code: int | None,
        entity_type: str,
        verb: str | None,
    ) -> dict[str, Any]:
        """Attach the entity's body guide to a write the API rejected as a bad request.

        Only a 400/422 means the body itself was wrong; for any other status (auth,
        not found, conflict, rate limit, server) the guide would not help fix it.
        """
        guide = self._BODY_GUIDES.get(entity_type)
        if verb is None or guide is None or status_code not in (400, 422):
            return error
        return {
            **error,
            "body_guide": guide,
            "hint": (
                "The API rejected the body. Rebuild it using body_guide (exact field names, "
                f"nesting and values for entity_type '{entity_type}') and retry. "
                + BODY_GUIDE_NOTATION
            ),
        }

    def _fetch_by_ids(
        self, entity_type: str, ids: list[str]
    ) -> tuple[list[Any], list[Any] | None, dict[str, Any] | None]:
        """Fetch entities by ID (GET with the IDs as query params)."""
        get_op = self._OPERATIONS[entity_type]["get"]
        return self._split_result(
            self._command(get_op, parameters={"ids": ids}),
            get_op,
            f"Failed to get Data Security {entity_type} entities",
            entity_type,
        )

    def _effective_filter(
        self, entity_type: str, filter: str | None, deleted: str
    ) -> tuple[str | None, dict[str, Any] | None]:
        """Return (filter to send, error) for the caller's filter and deleted argument.

        A blank filter is no filter. Soft-delete entity types return deleted entities
        by default, so the tool adds the clause itself rather than relying on the
        caller to; the caller's filter is parenthesized so its OR terms stay inside the
        AND. A policy filter is parenthesized too: the policy API ANDs platform_name
        with the first OR term only, so the other platform's policies leak in.
        """
        if deleted not in ("exclude", "include", "only"):
            return None, _format_error_response(
                f"Invalid deleted: '{deleted}'. Accepted values: exclude, include, only."
            )
        filter = (filter or "").strip() or None
        ops = self._OPERATIONS[entity_type]
        if not ops["soft_delete"]:
            if deleted == "only":
                return None, _format_error_response(
                    f"entity_type='{entity_type}' has no deleted entities; omit deleted "
                    "or use 'exclude'."
                )
            if filter and ops["platform"]:
                return f"({filter})", None
            return filter, None
        if deleted == "include":
            return filter, None
        if filter and _DELETED_FIELD.search(_QUOTED_VALUE.sub("''", filter)):
            # ANDed with the tool's own clause it can only narrow to nothing, and an
            # empty result would read as "no match" rather than as a misuse.
            return None, _format_error_response(
                "Do not filter on deleted: set the deleted argument instead "
                "('exclude' by default, 'include', or 'only')."
            )
        clause = "deleted:true" if deleted == "only" else "deleted:false"
        return (f"{clause}+({filter})" if filter else clause), None

    def _write_result(
        self,
        response: dict[str, Any],
        operation: str,
        entity_type: str,
        verb: str,
        entity_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Render a create/update response.

        Returns the resources list; `{results, _warnings}` when the API also
        reported per-item errors; or an acknowledgement when a 2xx carries neither,
        so an accepted write is not mistaken for a failure and retried.
        """
        resources, warnings, error = self._split_result(
            response, operation, f"Failed to {verb} {entity_type}", entity_type, verb
        )
        if error:
            return [error]
        resources = _elide_binary(resources)
        if warnings:
            return {"results": resources, "_warnings": warnings}
        if resources:
            return resources
        if verb == "create":
            return {
                "status": "created",
                "entity_type": entity_type,
                "message": (
                    "The API accepted the create but returned no entity. Do not retry the "
                    "create; find the new entity with falcon_search_data_security_entities "
                    "(e.g. by name) to get its id."
                ),
            }
        return {
            "status": "updated",
            "entity_type": entity_type,
            "id": entity_id,
            "message": (
                "The API accepted the update but returned no entity. Use "
                "falcon_get_data_security_entities with this id to see the result."
            ),
        }

    @staticmethod
    def _search_page(
        pagination: dict[str, Any] | None, offset: int, limit: int, n: int
    ) -> dict[str, Any]:
        """Build the pagination of a search page that started at offset and whose
        query step returned n IDs.

        The tool's own, not the API's: the classification and policy APIs report
        offset+limit as the offset, and no entity type sends a next cursor. total
        is the API's count, or None when it sent none. next counts the IDs, not the
        hydrated records, so an ID that fails to hydrate does not shift the
        following pages; without a total, a full page is taken to have a next one.
        """
        total = (pagination or {}).get("total")
        next_offset = offset + n
        has_next = n > 0 and (
            (total is not None and next_offset < total) or (total is None and n == limit)
        )
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "next": next_offset if has_next else None,
        }

    def _search_fields(
        self, entity_type: str, fields: list[str] | None
    ) -> tuple[list[str] | None, str | None]:
        """Return (fields to project search records to, hint).

        None keeps records whole. Fields the caller names win, and "*" among them
        asks for full records; otherwise the entity's summary fields apply, with a
        hint saying so.
        """
        summary = self._OPERATIONS[entity_type]["summary_fields"]
        if fields and _ALL_FIELDS in fields:
            return None, None
        if fields or not summary:
            return fields or None, None
        return list(summary), (
            f"These are summary records (id plus {', '.join(summary)}), as no fields were "
            "named. For full records pass their ids to falcon_get_data_security_entities, "
            f'or search again with fields ["{_ALL_FIELDS}"] and a small limit (about 5).'
        )

    # ── Search / get tools (generic, entity_type-keyed) ───────────────────

    def search_data_security_entities(
        self,
        entity_type: ReadEntityType = Field(
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
                "FQL filter. Fields vary by entity_type; full guide: "
                "falcon://data-security/<type>/fql-guide, <type> = plural hyphenated "
                "entity_type (e.g. falcon://data-security/content-patterns/fql-guide). "
                "id and deleted are not filter fields: fetch known IDs with "
                "falcon_get_data_security_entities; use the deleted argument."
            ),
        ),
        limit: int = Field(
            default=25,
            ge=1,
            le=_MAX_IDS,
            description=(
                "Maximum number of entities to return. Keep it small with a filter; "
                'limit 1 with pagination.total answers "how many".'
            ),
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description=(
                "Offset of the first entity. For the next page pass pagination.next; "
                "a null next means the last page."
            ),
        ),
        sort: str | None = Field(
            default=None,
            description=(
                "Sort order as field.direction, e.g. name.asc or created.desc. "
                "Valid fields vary by entity_type; see its FQL guide."
            ),
        ),
        platform_name: PlatformName | None = Field(
            default=None,
            description="Required for entity_type 'policy': 'win' or 'mac'.",
        ),
        deleted: DeletedMode = Field(
            default="exclude",
            description=(
                "'exclude' hides deleted entities, 'include' adds them, 'only' returns "
                "just them; use 'include' or 'only' just when the user asks about deleted "
                "entities. classification, policy and file_type have none: 'only' is "
                "rejected, the other values are ignored."
            ),
        ),
        fields: list[str] | None = Field(
            default=None,
            description=(
                'Return only these fields (plus id), as dotted paths, e.g. ["name", '
                '"is_enabled", "host_groups"] or ["name", "policy_properties.classifications"]. '
                "Omitted: summaries for policy and classification (the hint lists their "
                'fields), full records otherwise. ["*"] returns full records, several KB '
                "each for a policy or classification: keep limit to about 5, or get chosen "
                "ids with falcon_get_data_security_entities."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Data Security (DLP, formerly Data Protection) configuration entities.

        Covers classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, local application
        groups, sensitivity labels, and file types; a policy search also needs
        platform_name. Read falcon://data-security/agent/behavioral-guide once first:
        it holds the operating rules. Search narrowly: filter on what the user named
        and keep limit small; for a listing, show the first page with its total and
        offer the next. Consult the entity's FQL guide before composing a filter,
        e.g. falcon://data-security/policies/fql-guide.

        Returns a pagination envelope: `pagination.total` is the API's count of
        matches (null when it reports none) and `pagination.next` the offset of the
        next page (null on the last); `_warnings` lists per-entity errors the API
        reported. Policy and classification results are summary records unless you
        pass fields (a `hint` names the summary fields); other types return full
        records. Large inline images (e.g. a policy's euj_dialog_box_logo) come back
        as an "<elided …>" placeholder. With child CIDs, results span every CID (each
        record's cid says which); policy precedence and the default policy are per
        CID, so group policies by cid. Rule ad_users / ad_groups are AD SIDs: show
        them as-is, names cannot be resolved.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        ops = self._OPERATIONS[entity_type]
        if ops["platform"] and not platform_name:
            return [_format_error_response(
                f"platform_name is required for entity_type='{entity_type}' ('win' or 'mac')."
            )]

        filter_used, error = self._effective_filter(
            entity_type, filter, unwrap_field_default(deleted)
        )
        if error:
            return [error]

        search_params: dict[str, Any] = {
            "filter": filter_used,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        if ops["platform"]:
            search_params["platform_name"] = platform_name

        ids, pagination = self._base_search_with_meta(
            operation=ops["query"],
            search_params=search_params,
            error_message=f"Failed to search Data Security {entity_type} entities",
        )
        if self._is_error(ids):
            # The FQL guide rides along only when the API rejected the request
            # (400/422), where the filter or sort is the likely cause; auth,
            # rate-limit and server failures get the plain error.
            status_code: int | None = (ids.get("details") or {}).get("status_code")
            if status_code not in (400, 422):
                return [ids]
            return self._format_fql_error_response([ids], filter_used, self._FQL_DOCS[entity_type])

        page = self._search_page(pagination, offset, limit, len(ids))
        if not ids:
            envelope = self._build_pagination_envelope([], page, filter_used)
            if offset > 0 and page["total"]:
                # Past the last page the query matches entities but returns none.
                envelope["hint"] = (
                    f"offset {offset} is past the end: {page['total']} entities match, so "
                    "there is no page here. The filter is fine; page from a lower offset "
                    "(0 for the first page)."
                )
            return envelope

        details, warnings, error = self._fetch_by_ids(entity_type, ids)
        if error:
            return [error]
        project_to, hint = self._search_fields(entity_type, unwrap_field_default(fields))
        details = _project(
            _elide_binary(self._reorder_by_ids(ids, details, id_field="id")), project_to
        )
        envelope = self._build_pagination_envelope(details, page, filter_used)
        if warnings:
            envelope["_warnings"] = warnings
        if hint:
            envelope["hint"] = hint
        return envelope

    def get_data_security_entities(
        self,
        entity_type: ReadEntityType = Field(
            description=(
                "Data Security entity type to retrieve. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group, "
                "sensitivity_label, file_type."
            ),
        ),
        ids: list[str] = Field(
            min_length=1,
            max_length=_MAX_IDS,
            description=(
                "Entity IDs to retrieve (from a search or create response). At most 100 "
                "per call; duplicates are ignored."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve full Data Security entities of one entity_type by ID.

        Use it for IDs you already hold, e.g. the IDs another entity references
        (relationships: falcon://data-security/entities/model-guide). To find entities
        by attribute, use falcon_search_data_security_entities. Returns a list of the
        matching entities, or `{results, _warnings}` when some IDs failed. Large
        inline images (e.g. a policy's euj_dialog_box_logo) come back as an
        "<elided …>" placeholder. Rule ad_users / ad_groups are AD SIDs: show them
        as-is, names cannot be resolved.
        """
        error = self._validate_entity_type(entity_type)
        if error:
            return [error]

        unique_ids = list(dict.fromkeys(ids))
        if not unique_ids or len(unique_ids) > _MAX_IDS:
            return [_format_error_response(
                f"ids must hold between 1 and {_MAX_IDS} IDs; got {len(unique_ids)}."
            )]

        resources, warnings, error = self._fetch_by_ids(entity_type, unique_ids)
        if error:
            return [error]
        resources = _elide_binary(resources)
        if warnings:
            return {"results": resources, "_warnings": warnings}
        return resources

    def get_data_security_entity_schema(
        self,
        entity_types: list[WriteEntityType] = Field(
            min_length=1,
            description=(
                'Entity types whose body guide to return, e.g. ["classification", '
                '"policy"]. Duplicates are ignored.'
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Return the write-body guide of one or more Data Security entity types.

        Each guide gives the field names, types, allowed values, nesting and required
        fields. Covers every type except file_type, which is read-only. Reads embedded
        docs only, no API call. Call it before building a create or update body,
        batching every type you will write (e.g. ["classification", "policy"]); never
        guess field names. Returns one body guide per entity type plus a usage hint.
        """
        unique_types = list(dict.fromkeys(entity_types))
        if not unique_types:
            return [_format_error_response("entity_types must not be empty.")]

        schemas = []
        for entity_type in unique_types:
            error = self._validate_entity_type(entity_type)
            if error:
                return [error]
            guide = self._BODY_GUIDES.get(entity_type)
            if guide is None:
                return [_format_error_response(
                    f"entity_type='{entity_type}' is read-only and has no body."
                )]
            schemas.append({"entity_type": entity_type, "body_guide": guide})

        return {
            "schemas": schemas,
            "hint": (
                "Use these exact field names and nesting in the body of "
                "falcon_create_data_security_entity / falcon_update_data_security_entity. "
                "For updates send the id plus only the fields to change; a list you send "
                "replaces the stored list. " + BODY_GUIDE_NOTATION
            ),
        }

    # ── Create / update tools (generic, entity_type-keyed) ────────────────

    @staticmethod
    def _wrap_body(wrapper: str | None, body: dict[str, Any]) -> dict[str, Any]:
        """Wrap a write body per the entity's envelope convention."""
        if wrapper is None:
            return body
        return {wrapper: [body]}

    @staticmethod
    def _elided_error(body: dict[str, Any]) -> dict[str, Any] | None:
        """Return the error for a write body that echoes an elision placeholder, or None."""
        paths = _elided_paths(body)
        if not paths:
            return None
        return _format_error_response(
            f"body field(s) {', '.join(paths)} hold an \"{_ELIDED_PREFIX}…>\" placeholder "
            "copied from a result, not the real value; remove them from the body (omitted "
            "fields keep their stored value)."
        )

    def create_data_security_entity(
        self,
        entity_type: WriteEntityType = Field(
            description=(
                "Data Security entity type to create. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group, "
                "sensitivity_label. (file_type is read-only and cannot be created.)"
            ),
        ),
        body: dict[str, Any] = Field(description=_CREATE_BODY_DOC),
        platform_name: PlatformName | None = Field(default=None, description=_WRITE_PLATFORM_DOC),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create a Data Security entity of the chosen entity_type.

        Creates classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, local application
        groups, and sensitivity labels; policies also need platform_name. Build the
        body from falcon_get_data_security_entity_schema and follow
        falcon://data-security/agent/behavioral-guide (ask rather than assume a
        setting). Returns a list with the created entity, `{results, _warnings}` when
        the API also reported errors, or an acknowledgement {status, entity_type,
        message} when it accepted the write but returned no entity (do not retry). If
        the API rejects the body, the error includes its body_guide.

        Rules (the API accepts violations silently):

        - Create bottom-up, referencing only real IDs from search/get, never guessed:
          cloud application / enterprise account → web location → classification →
          policy.
        - Enforcement is only on the classification: rule response_action applies
          only when protection_mode is 'enforce' ('simulate' runs silently, 'monitor'
          only observes). Policy settings control inspection.
        - "Upload TO X" is a rule destination (web_locations, scope 'specific');
          "data FROM X" is a classification origin (web_sources). Ask when unclear.
        - A policy's classifications are ordered: the first match with a rule
          covering the egress wins; classifications without detection criteria go last.
        - One policy per host per platform (they never stack): extend the hosts'
          existing policy. Windows and macOS each need their own.
        - A classification has no effect until a policy references it.
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
        if not body:
            return [_format_error_response("body must not be empty.")]
        error = self._elided_error(body)
        if error:
            return [error]

        query_params = {"platform_name": platform_name} if ops["platform"] else None
        response = self._command(
            create_op,
            parameters=query_params,
            body=self._wrap_body(ops["create_wrapper"], body),
        )
        return self._write_result(response, create_op, entity_type, "create")

    def update_data_security_entity(
        self,
        entity_type: UpdateEntityType = Field(
            description=(
                "Data Security entity type to update. One of: classification, "
                "policy, content_pattern, cloud_application, enterprise_account, "
                "web_location, local_application, local_application_group. "
                "(sensitivity_label and file_type do not support update.)"
            ),
        ),
        body: dict[str, Any] = Field(description=_UPDATE_BODY_DOC),
        platform_name: PlatformName | None = Field(default=None, description=_WRITE_PLATFORM_DOC),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update an existing Data Security entity of the chosen entity_type.

        Updates classifications, policies, content patterns, cloud applications,
        enterprise accounts, web locations, local applications, and local
        application groups; policies also need platform_name. Send the entity's "id"
        (from search/get) plus only the fields to change; its body guide
        (falcon_get_data_security_entity_schema) says which fields are updatable.
        Returns a list with the updated entity, `{results, _warnings}` when the API
        also reported errors, or an acknowledgement {status, entity_type, id, message}
        when it accepted the write but returned no entity. If the API rejects the
        body, the error includes its body_guide.

        Rules (the API accepts violations silently):

        - A list you send replaces the stored list: to add or remove an item (e.g. a
          policy's classification), get the entity and send its full list with your
          change.
        - The rules of falcon_create_data_security_entity apply (IDs and SIDs,
          destinations vs origins, classification order, enforcement).
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

        if "id" not in body:
            return [_format_error_response(
                f"body must include an 'id' field to update entity_type='{entity_type}'."
            )]
        entity_id = body["id"]
        if not isinstance(entity_id, str) or not entity_id:
            return [_format_error_response("body 'id' must be a non-empty string.")]
        if all(k == "id" for k in body):
            return [_format_error_response(
                f"body must include at least one field to change besides 'id' for "
                f"entity_type='{entity_type}'."
            )]
        error = self._elided_error(body)
        if error:
            return [error]

        query_params: dict[str, Any] = {}
        update_body = body
        if ops["update_id_query"]:
            query_params["id"] = entity_id
            update_body = {k: v for k, v in body.items() if k != "id"}
        if ops["platform"]:
            query_params["platform_name"] = platform_name

        # Independent of update_id_query: for an in-body-id type the caller's id is
        # laid back on top after the server-managed fields strip the fetched one.
        if ops["update_merge"]:
            update_body, error = self._merge_onto_current(entity_type, entity_id, update_body)
            if error:
                return [error]

        response = self._command(
            update_op,
            parameters=query_params,
            body=self._wrap_body(ops["update_wrapper"], update_body),
        )
        return self._write_result(response, update_op, entity_type, "update", entity_id)

    def _merge_onto_current(
        self, entity_type: str, entity_id: str, body: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Return (merged body, error): the caller's fields overlaid onto the stored
        entity, minus server-managed fields.

        For the entity types whose PATCH clears every field the body leaves out.
        Only the fetched record whose id matches is used. A missing or deleted
        entity, or a failed fetch, is returned as an error, so no PATCH is sent.
        """
        resources, _, error = self._fetch_by_ids(entity_type, [entity_id])
        if error:
            return body, error
        existing = next(
            (r for r in resources if isinstance(r, dict) and r.get("id") == entity_id), None
        )
        if existing is None:
            return body, _format_error_response(
                f"No {entity_type} found with id '{entity_id}'. "
                "Use falcon_search_data_security_entities to find a valid id."
            )
        if existing.get("deleted") is True:
            return body, _format_error_response(
                f"{entity_type} '{entity_id}' is deleted and cannot be updated. Use "
                "falcon_search_data_security_entities to find a live one."
            )
        kept = {k: v for k, v in existing.items() if k not in self._SERVER_MANAGED_FIELDS}
        return {**kept, **body}, None
