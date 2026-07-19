"""
Policies module for Falcon MCP Server.

This module provides a unified set of tools for managing CrowdStrike host-based
policies across all six policy types — prevention, sensor_update, firewall,
device_control, response, and content_update — behind a single `policy_type`
discriminator. Per-type operation maps and behavior flags absorb the API
differences (search mode, body wrapper, platform requirements, valid actions) so
the tool surface stays clean for the calling agent.

This module manages the policy *container* (assignment, precedence,
enable/disable). It does not manage firewall rules or rule groups — those live in
the Firewall module, which operates on what is *inside* a firewall policy.

Required API Scopes:
- Prevention Policies: read, write
- Sensor Update Policies: read, write
- Firewall Management: read, write
- Device Control Policies: read, write
- Response Policies: read, write
- Content Update Policies: read, write
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.policies import SEARCH_POLICIES_FQL_DOCUMENTATION

logger = get_logger(__name__)

# Valid policy types (the discriminator values exposed to the agent).
POLICY_TYPES = (
    "prevention",
    "sensor_update",
    "firewall",
    "device_control",
    "response",
    "content_update",
)


class PoliciesModule(BaseModule):
    """Module for managing CrowdStrike host-based policies across all six types."""

    # Per-type operation names, verified against the installed FalconPy SDK
    # (1.6.2) and the live API on 2026-06-06. All operation-name string literals
    # are kept inside the class body so the doc-scope extractor can find them.
    #
    # The `get` op is exposed only indirectly: device_control search is a two-step
    # query->getV2 flow (the V1 combined op drops V2-only fields). There is no
    # standalone get tool — search_policies returns full policy objects.
    #
    # NOTE: revealUninstallToken / incrementUninstallToken are intentionally NOT
    # wrapped — they reveal/rotate device uninstall tokens (sensitive).
    _OPERATIONS: dict[str, dict[str, str]] = {
        "prevention": {
            "combined": "queryCombinedPreventionPolicies",
            "query": "queryPreventionPolicies",
            "get": "getPreventionPolicies",
            "members": "queryCombinedPreventionPolicyMembers",
            "create": "createPreventionPolicies",
            "update": "updatePreventionPolicies",
            "delete": "deletePreventionPolicies",
            "action": "performPreventionPoliciesAction",
            "precedence": "setPreventionPoliciesPrecedence",
        },
        "sensor_update": {
            "combined": "queryCombinedSensorUpdatePoliciesV2",
            "query": "querySensorUpdatePolicies",
            "get": "getSensorUpdatePoliciesV2",
            "members": "queryCombinedSensorUpdatePolicyMembers",
            "create": "createSensorUpdatePoliciesV2",
            "update": "updateSensorUpdatePoliciesV2",
            "delete": "deleteSensorUpdatePolicies",
            "action": "performSensorUpdatePoliciesAction",
            "precedence": "setSensorUpdatePoliciesPrecedence",
        },
        "firewall": {
            "combined": "queryCombinedFirewallPolicies",
            "query": "queryFirewallPolicies",
            "get": "getFirewallPolicies",
            "members": "queryCombinedFirewallPolicyMembers",
            "create": "createFirewallPolicies",
            "update": "updateFirewallPolicies",
            "delete": "deleteFirewallPolicies",
            "action": "performFirewallPoliciesAction",
            "precedence": "setFirewallPoliciesPrecedence",
        },
        "device_control": {
            "combined": "queryCombinedDeviceControlPolicies",
            "query": "queryDeviceControlPolicies",
            "get": "getDeviceControlPoliciesV2",
            "members": "queryCombinedDeviceControlPolicyMembers",
            "create": "postDeviceControlPoliciesV2",
            "update": "patchDeviceControlPoliciesV2",
            "delete": "deleteDeviceControlPolicies",
            "action": "performDeviceControlPoliciesAction",
            "precedence": "setDeviceControlPoliciesPrecedence",
        },
        "response": {
            "combined": "queryCombinedRTResponsePolicies",
            "query": "queryRTResponsePolicies",
            "get": "getRTResponsePolicies",
            "members": "queryCombinedRTResponsePolicyMembers",
            "create": "createRTResponsePolicies",
            "update": "updateRTResponsePolicies",
            "delete": "deleteRTResponsePolicies",
            "action": "performRTResponsePoliciesAction",
            "precedence": "setRTResponsePoliciesPrecedence",
        },
        "content_update": {
            "combined": "queryCombinedContentUpdatePolicies",
            "query": "queryContentUpdatePolicies",
            "get": "getContentUpdatePolicies",
            "members": "queryCombinedContentUpdatePolicyMembers",
            "create": "createContentUpdatePolicies",
            "update": "updateContentUpdatePolicies",
            "delete": "deleteContentUpdatePolicies",
            "action": "performContentUpdatePoliciesAction",
            "precedence": "setContentUpdatePoliciesPrecedence",
        },
    }

    # Search dispatch mode. device_control is two-step (query for IDs, then getV2
    # for full details) because its combined op has no V2 and drops V2-only
    # fields. Every other type returns full objects from its combined op.
    _SEARCH_MODE = {
        "prevention": "combined",
        "sensor_update": "combined",
        "firewall": "combined",
        "device_control": "two_step",
        "response": "combined",
        "content_update": "combined",
    }

    # Whether a create requires platform_name. content_update is platform-agnostic
    # (platform_name is always 'all') and rejects platform_name in the body.
    _CREATE_NEEDS_PLATFORM = {
        "prevention": True,
        "sensor_update": True,
        "firewall": True,
        "device_control": True,
        "response": True,
        "content_update": False,
    }

    # Whether set-precedence requires platform_name (same rule as create).
    _PRECEDENCE_NEEDS_PLATFORM = {
        "prevention": True,
        "sensor_update": True,
        "firewall": True,
        "device_control": True,
        "response": True,
        "content_update": False,
    }

    # Request-body wrapper key. device_control v2 uses "policies"; all others use
    # the standard "resources" wrapper.
    _BODY_WRAPPER = {
        "prevention": "resources",
        "sensor_update": "resources",
        "firewall": "resources",
        "device_control": "policies",
        "response": "resources",
        "content_update": "resources",
    }

    # Valid action_name values per type for perform_policy_action. The SDK rejects
    # rule-group actions for firewall/device_control; content_update has unique
    # pin/override actions.
    _VALID_ACTIONS: dict[str, set[str]] = {
        "prevention": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
            "add-rule-group",
            "remove-rule-group",
        },
        "sensor_update": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
            "add-rule-group",
            "remove-rule-group",
        },
        "response": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
            "add-rule-group",
            "remove-rule-group",
        },
        "firewall": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
        },
        "device_control": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
        },
        "content_update": {
            "enable",
            "disable",
            "add-host-group",
            "remove-host-group",
            "override-allow",
            "override-pause",
            "override-revert",
            # NOTE: set-pinned-content-version / remove-pinned-content-version are
            # intentionally omitted for v1. They require a content-version value
            # passed via action_parameters, and this tool has no parameter to carry
            # one — exposing them would advertise a capability that cannot execute.
            # Pinning a specific content version is out of scope until a dedicated
            # parameter is wired in.
        },
    }

    # Sort field bases that the API accepts (each with a .asc/.desc direction).
    # platform_name is deliberately excluded — it returns HTTP 500 on every type.
    _SAFE_SORT_FIELDS = {
        "name",
        "created_timestamp",
        "modified_timestamp",
        "enabled",
        "created_by",
        "modified_by",
        "precedence",
    }

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_policies,
            name="search_policies",
        )

        self._add_tool(
            server=server,
            method=self.search_policy_members,
            name="search_policy_members",
        )

        self._add_tool(
            server=server,
            method=self.create_policy,
            name="create_policy",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_policy,
            name="update_policy",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_policies,
            name="delete_policies",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.perform_policy_action,
            name="perform_policy_action",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.set_policy_precedence,
            name="set_policy_precedence",
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
        search_policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://policies/search/fql-guide"),
            name="falcon_search_policies_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_policies` tool.",
            text=SEARCH_POLICIES_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_policies_fql_resource,
        )

    # ---- Validators ---------------------------------------------------------------

    def _validate_policy_type(self, policy_type: str) -> dict[str, Any] | None:
        """Return an error dict if policy_type is invalid, else None."""
        if policy_type not in self._OPERATIONS:
            return _format_error_response(
                f"Invalid policy_type '{policy_type}'. "
                f"Valid values are: {', '.join(POLICY_TYPES)}.",
            )
        return None

    def _validate_sort(self, sort: str | None) -> dict[str, Any] | None:
        """Reject platform_name sorts (HTTP 500) and unknown sort fields.

        Returns an error dict if the sort base is platform_name or not in the
        allowed set, else None. Accepts an optional `.asc`/`.desc`/`|asc`/`|desc`
        direction suffix.
        """
        if not sort:
            return None

        base = sort.split(".")[0].split("|")[0].strip()
        if base == "platform_name":
            return _format_error_response(
                "Sorting by 'platform_name' is not supported (the API returns "
                "HTTP 500). Use one of: "
                f"{', '.join(sorted(self._SAFE_SORT_FIELDS))}.",
            )
        if base not in self._SAFE_SORT_FIELDS:
            return _format_error_response(
                f"Invalid sort field '{base}'. Valid sort fields are: "
                f"{', '.join(sorted(self._SAFE_SORT_FIELDS))}.",
            )
        return None

    # ---- Search -------------------------------------------------------------------

    def search_policies(
        self,
        policy_type: str = Field(
            description=(
                "Policy type to search. One of: 'prevention', 'sensor_update', "
                "'firewall', 'device_control', 'response', 'content_update'."
            ),
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. For name matching use the contains operator `name:~'value'` (a `name:'*value*'` glob is treated literally and returns nothing); name is not filterable for sensor_update/content_update. See `falcon://policies/search/fql-guide` for full syntax (operators differ by type).",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of policies to return. [1-500]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of the result set from which to return policies.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression (e.g. 'modified_timestamp.desc'). See `falcon://policies/search/fql-guide`. Do NOT sort by platform_name (returns HTTP 500).",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search host-based policies of a given type and return full policy records.

        Use this to find prevention, sensor update, firewall, device control,
        response, or content update policies by name, platform, enabled state, or
        timestamp — the `policy_type` parameter selects which policy API is
        queried. Consult falcon://policies/search/fql-guide before constructing
        filter expressions; the `name` match operator differs per type. Returns
        full policy records including id, name, platform_name, enabled, settings,
        and assigned host groups.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        sort_error = self._validate_sort(sort)
        if sort_error is not None:
            return [sort_error]

        return self._search_by_type(policy_type, filter, limit, offset, sort)

    def _search_by_type(
        self,
        policy_type: str,
        filter: str | None,
        limit: int,
        offset: int | None,
        sort: str | None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Dispatch search to the combined op or the device_control two-step flow."""
        if self._SEARCH_MODE[policy_type] == "two_step":
            ids, pagination = self._base_search_with_meta(
                operation=self._OPERATIONS[policy_type]["query"],
                search_params={
                    "filter": filter,
                    "limit": limit,
                    "offset": offset,
                    "sort": sort,
                },
                error_message=f"Failed to search {policy_type} policies",
            )

            if self._is_error(ids):
                return self._format_fql_error_response(
                    [ids], filter, SEARCH_POLICIES_FQL_DOCUMENTATION
                )

            if not ids:
                return self._build_pagination_envelope([], pagination, filter)

            details = self._base_get_by_ids(
                operation=self._OPERATIONS[policy_type]["get"],
                ids=ids,
                use_params=True,
            )

            if self._is_error(details):
                return [details]

            # Restore the query-step sort order in case the get endpoint reorders results.
            details = self._reorder_by_ids(ids, details, id_field="id")
            return self._build_pagination_envelope(details, pagination, filter)

        # Combined single-call path for the other five types.
        policies, pagination = self._base_search_with_meta(
            operation=self._OPERATIONS[policy_type]["combined"],
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message=f"Failed to search {policy_type} policies",
        )

        if self._is_error(policies):
            return self._format_fql_error_response(
                [policies], filter, SEARCH_POLICIES_FQL_DOCUMENTATION
            )

        return self._build_pagination_envelope(policies or [], pagination, filter)

    # ---- Members ------------------------------------------------------------------

    def search_policy_members(
        self,
        policy_type: str = Field(
            description=(
                "Policy type. One of: 'prevention', 'sensor_update', 'firewall', "
                "'device_control', 'response', 'content_update'."
            ),
        ),
        id: str = Field(
            description="The policy ID whose host members should be retrieved. If you don't already have it, use falcon_search_policies to look it up.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression on HOST attributes. See `falcon://hosts/search/fql-guide` for syntax.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="The maximum records to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort members using host FQL sort syntax (e.g. 'hostname.asc', 'last_seen.desc').",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for the host members governed by a specific policy.

        Use this to list the devices a policy is applied to — answering "which
        machines does this policy govern?". This differs from falcon_search_policies
        (which returns the policy object, whose groups[] lists host GROUPS, not
        resolved hosts) and from falcon_search_host_group_members (which lists one
        group's hosts; a policy may target several groups or apply globally).
        Requires the policy `id`; filters on HOST attributes — consult
        falcon://hosts/search/fql-guide for the filter syntax. Returns full host
        device entities including device_id, hostname, platform_name, and network
        context.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        if not id:
            return [
                _format_error_response(
                    "A policy 'id' is required to search policy members.",
                    operation=self._OPERATIONS[policy_type]["members"],
                )
            ]

        members, pagination = self._base_search_with_meta(
            operation=self._OPERATIONS[policy_type]["members"],
            search_params={
                "id": id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message=f"Failed to search {policy_type} policy members",
        )

        if self._is_error(members):
            return [members]

        return self._build_pagination_envelope(members or [], pagination, filter)

    # ---- Body builder -------------------------------------------------------------

    def _build_policy_body(
        self,
        policy_type: str,
        *,
        is_update: bool,
        policy_id: str | None,
        name: str | None,
        platform_name: str | None,
        description: str | None,
        settings: Any | None,
        clone_id: str | None,
    ) -> dict[str, Any]:
        """Build the wrapped request body for create/update, or an error dict.

        On create, `name` is required and `platform_name` is required for every
        type except content_update (which is platform-agnostic and rejects
        platform_name). On update, `id` is required and placed inside the resource
        object; platform_name is not updatable post-create. The wrapper key is
        "policies" for device_control v2 and "resources" for all other types.
        """
        if is_update:
            if not policy_id:
                return _format_error_response(
                    "A policy 'id' is required to update a policy.",
                    operation=self._OPERATIONS[policy_type]["update"],
                )
        else:
            if not name:
                return _format_error_response(
                    f"Creating a {policy_type} policy requires a 'name'.",
                    operation=self._OPERATIONS[policy_type]["create"],
                )
            if self._CREATE_NEEDS_PLATFORM[policy_type] and not platform_name:
                return _format_error_response(
                    f"Creating a {policy_type} policy requires a 'platform_name' "
                    "(e.g. 'Windows', 'Mac', 'Linux').",
                    operation=self._OPERATIONS[policy_type]["create"],
                )

        resource: dict[str, Any] = {}
        # id is only placed in the body on update (create never carries an id).
        if is_update and policy_id is not None:
            resource["id"] = policy_id
        if name is not None:
            resource["name"] = name
        # platform_name is only meaningful at create time and never for
        # content_update (it is always 'all').
        if (
            not is_update
            and self._CREATE_NEEDS_PLATFORM[policy_type]
            and platform_name is not None
        ):
            resource["platform_name"] = platform_name
        if description is not None:
            resource["description"] = description
        if settings is not None:
            resource["settings"] = settings
        if not is_update and clone_id is not None:
            resource["clone_id"] = clone_id

        wrapper = self._BODY_WRAPPER[policy_type]
        return {wrapper: [resource]}

    # ---- Create / Update ----------------------------------------------------------

    def create_policy(
        self,
        policy_type: str = Field(
            description=(
                "Policy type to create. One of: 'prevention', 'sensor_update', "
                "'firewall', 'device_control', 'response', 'content_update'."
            ),
        ),
        name: str | None = Field(
            default=None,
            description="Name for the new policy. Must be supplied — omitting it returns a guiding error.",
        ),
        platform_name: str | None = Field(
            default=None,
            description="Target platform ('Windows', 'Mac', 'Linux'). Must be supplied for all types except content_update (which is platform-agnostic); omitting it for those types returns a guiding error.",
        ),
        description: str | None = Field(
            default=None,
            description="Description for the policy.",
        ),
        settings: Any | None = Field(
            default=None,
            description="Opaque per-type settings object (dict or list), passed through unchanged. Building detailed settings is out of scope for v1 — prefer cloning an existing policy via clone_id then tweaking with falcon_update_policy.",
        ),
        clone_id: str | None = Field(
            default=None,
            description="ID of an existing policy to clone settings from. An alternative to supplying settings directly.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a host-based policy of the given type.

        Provide a name and (for every type except content_update) a platform_name.
        Detailed per-type settings construction is out of scope for v1 — the
        typical flow is to clone an existing policy with clone_id and then adjust
        it via falcon_update_policy, or pass an opaque settings object. New
        policies are created disabled. Returns the created policy record.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        body = self._build_policy_body(
            policy_type,
            is_update=False,
            policy_id=None,
            name=name,
            platform_name=platform_name,
            description=description,
            settings=settings,
            clone_id=clone_id,
        )

        if self._is_error(body):
            return [body]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[policy_type]["create"],
            body_params=body,
            error_message=f"Failed to create {policy_type} policy",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_policy(
        self,
        policy_type: str = Field(
            description=(
                "Policy type to update. One of: 'prevention', 'sensor_update', "
                "'firewall', 'device_control', 'response', 'content_update'."
            ),
        ),
        id: str | None = Field(
            default=None,
            description="ID of the policy to update. Required.",
        ),
        name: str | None = Field(
            default=None,
            description="New name for the policy.",
        ),
        description: str | None = Field(
            default=None,
            description="New description for the policy.",
        ),
        settings: Any | None = Field(
            default=None,
            description="Opaque per-type settings object (dict or list), passed through unchanged. Unspecified fields are left unchanged.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an existing host-based policy of the given type.

        Provide the policy `id` plus any fields to change (name, description,
        settings). platform_name is not updatable after creation. Uses HTTP PATCH
        semantics — unspecified fields are left unchanged. Returns the updated
        policy record.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        body = self._build_policy_body(
            policy_type,
            is_update=True,
            policy_id=id,
            name=name,
            platform_name=None,
            description=description,
            settings=settings,
            clone_id=None,
        )

        if self._is_error(body):
            return [body]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[policy_type]["update"],
            body_params=body,
            error_message=f"Failed to update {policy_type} policy",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    # ---- Delete -------------------------------------------------------------------

    def delete_policies(
        self,
        policy_type: str = Field(
            description=(
                "Policy type to delete. One of: 'prevention', 'sensor_update', "
                "'firewall', 'device_control', 'response', 'content_update'."
            ),
        ),
        ids: list[str] | None = Field(
            default=None,
            description="IDs of the policies to delete. Required (non-empty).",
        ),
    ) -> list[dict[str, Any]]:
        """Delete one or more host-based policies of the given type.

        Provide the policy_type and a non-empty list of policy `ids`. A policy
        usually must be DISABLED before it can be deleted — an enabled policy
        returns an HTTP 400. Disable it first with
        falcon_perform_policy_action(action_name="disable"); this tool does not
        auto-disable. The Default policy of each type cannot be deleted. Returns
        the API response for the deletion.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        if not ids:
            return [
                _format_error_response(
                    "A non-empty 'ids' list is required to delete policies.",
                    operation=self._OPERATIONS[policy_type]["delete"],
                )
            ]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[policy_type]["delete"],
            query_params={"ids": ids},
            error_message=f"Failed to delete {policy_type} policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    # ---- Action -------------------------------------------------------------------

    def perform_policy_action(
        self,
        policy_type: str = Field(
            description=(
                "Policy type. One of: 'prevention', 'sensor_update', 'firewall', "
                "'device_control', 'response', 'content_update'."
            ),
        ),
        action_name: str = Field(
            description="The action to perform. Common to all types: 'enable', 'disable', 'add-host-group', 'remove-host-group'. prevention/sensor_update/response also allow 'add-rule-group'/'remove-rule-group'; content_update also allows 'override-allow'/'override-pause'/'override-revert'. The valid set is validated per type.",
        ),
        ids: list[str] = Field(
            description="IDs of the policies to act on.",
        ),
        group_id: str | None = Field(
            default=None,
            description="Group ID for group actions. Required for 'add-host-group'/'remove-host-group' (a host group ID) and 'add-rule-group'/'remove-rule-group' (a rule group ID); omit for other actions.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action on one or more policies of the given type.

        Use this to enable/disable policies or attach/detach host groups and rule
        groups (and, for content_update, content overrides). action_name is
        validated against the actions valid for that policy_type. The
        add/remove-host-group and add/remove-rule-group actions require a group_id.
        Returns the updated policy records.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        valid_actions = self._VALID_ACTIONS[policy_type]
        if action_name not in valid_actions:
            return [
                _format_error_response(
                    f"Invalid action_name '{action_name}' for {policy_type}. "
                    f"Valid actions are: {', '.join(sorted(valid_actions))}.",
                    operation=self._OPERATIONS[policy_type]["action"],
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "A non-empty 'ids' list is required to perform a policy action.",
                    operation=self._OPERATIONS[policy_type]["action"],
                )
            ]

        body: dict[str, Any] = {"ids": ids}
        if action_name in (
            "add-host-group",
            "remove-host-group",
            "add-rule-group",
            "remove-rule-group",
        ):
            if not group_id:
                return [
                    _format_error_response(
                        f"action_name '{action_name}' requires a 'group_id' "
                        "(the host group ID for host-group actions, or the rule "
                        "group ID for rule-group actions).",
                        operation=self._OPERATIONS[policy_type]["action"],
                    )
                ]
            body["action_parameters"] = [{"name": "group_id", "value": group_id}]

        result = self._base_query_api_call(
            operation=self._OPERATIONS[policy_type]["action"],
            query_params={"action_name": action_name},
            body_params=body,
            error_message=f"Failed to perform {action_name} on {policy_type} policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    # ---- Precedence ---------------------------------------------------------------

    def set_policy_precedence(
        self,
        policy_type: str = Field(
            description=(
                "Policy type. One of: 'prevention', 'sensor_update', 'firewall', "
                "'device_control', 'response', 'content_update'."
            ),
        ),
        ids: list[str] = Field(
            description="The COMPLETE ordered list of non-Default policy IDs for the platform, highest precedence first.",
        ),
        platform_name: str | None = Field(
            default=None,
            description="Target platform ('Windows', 'Mac', 'Linux'). Required for all types EXCEPT content_update.",
        ),
    ) -> list[dict[str, Any]]:
        """Set the precedence (evaluation order) of policies for a platform.

        The `ids` list must be the COMPLETE ordered set of non-Default policies for
        the given platform — the first id is highest precedence. Partial lists are
        rejected by the API. platform_name is required for every type except
        content_update. Returns the API response.
        """
        type_error = self._validate_policy_type(policy_type)
        if type_error is not None:
            return [type_error]

        if not ids:
            return [
                _format_error_response(
                    "A non-empty 'ids' list is required to set policy precedence.",
                    operation=self._OPERATIONS[policy_type]["precedence"],
                )
            ]

        body: dict[str, Any] = {"ids": ids}
        if self._PRECEDENCE_NEEDS_PLATFORM[policy_type]:
            if not platform_name:
                return [
                    _format_error_response(
                        f"Setting precedence for {policy_type} policies requires a "
                        "'platform_name'.",
                        operation=self._OPERATIONS[policy_type]["precedence"],
                    )
                ]
            body["platform_name"] = platform_name

        result = self._base_query_api_call(
            operation=self._OPERATIONS[policy_type]["precedence"],
            body_params=body,
            error_message=f"Failed to set {policy_type} policy precedence",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
