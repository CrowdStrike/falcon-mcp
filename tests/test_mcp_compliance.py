"""MCP protocol compliance tests for falcon-mcp.

Asserts conformance to MCP spec revision 2025-06-18 and JSON-RPC 2.0.
Each assertion cites the spec section it enforces.

Resolves #235.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session
from starlette.testclient import TestClient

from falcon_mcp.common.auth import (
    ASGIApp,
    normalize_content_type_middleware,
    strip_trailing_slash_middleware,
)
from falcon_mcp.server import FalconMCPServer

MCP_SPEC_REVISION = "2025-06-18"

# Tools intentionally allowed to declare destructiveHint=True or readOnlyHint=False.
# Add a name here only after explicit security review confirms the tool mutates
# tenant state. The default-deny posture catches new tools added without an
# explicit readOnlyHint decision.
#
# Each entry below was confirmed against the module source: the annotation is
# set explicitly to readOnlyHint=False (and destructiveHint=True for delete
# operations), so the contributor made a conscious mutation decision.
MUTATING_TOOL_ALLOWLIST: set[str] = {
    # ioc module: tenant IOC inventory mutations
    "falcon_add_ioc",
    "falcon_remove_iocs",
    # firewall module: tenant firewall policy mutations
    "falcon_create_firewall_rule_group",
    "falcon_delete_firewall_rule_groups",
    # custom_ioa module: tenant IOA rule mutations
    "falcon_create_ioa_rule_group",
    "falcon_update_ioa_rule_group",
    "falcon_delete_ioa_rule_groups",
    "falcon_create_ioa_rule",
    "falcon_update_ioa_rule",
    "falcon_delete_ioa_rules",
    # rtr module: real-time-response session lifecycle and command execution
    "falcon_init_rtr_session",
    "falcon_pulse_rtr_session",
    "falcon_execute_rtr_read_only_command",
    "falcon_delete_rtr_session",
    # shield module: dismisses tenant compliance findings
    "falcon_dismiss_shield_check",
    # scheduled_reports module: kicks off a tenant report job
    "falcon_launch_scheduled_report",
}

# Project convention: every guide URI is falcon://{module}/{path}/{kind}-guide.
# Most modules use fql-guide; the shield module uses query-guide because it
# does not use FQL. The pattern accepts any [a-z]+-guide suffix to accommodate
# future query languages without forcing a regex update.
RESOURCE_URI_PATTERN = re.compile(r"^falcon://[a-z0-9-]+(/[a-z0-9-]+)+/[a-z]+-guide$")

# TestClient default Host is "testserver"; mcp's DNS rebinding middleware rejects
# any host outside its localhost allowlist (127.0.0.1:*, localhost:*, [::1]:*).
# Pin a port so the Host header matches the wildcard pattern, freeing each test
# to exercise the behavior under test rather than failing on Host validation.
LOCALHOST_BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mcp_server() -> Iterator[FalconMCPServer]:
    """Build a FalconMCPServer with a stubbed FalconClient."""
    with patch("falcon_mcp.server.FalconClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        mock_client_cls.return_value = mock_client
        yield FalconMCPServer()


@pytest.fixture
def http_client(mcp_server: FalconMCPServer) -> Iterator[TestClient]:
    """Wrap the streamable-http ASGI app with a starlette TestClient.

    Resets sse_starlette's module-level should_exit_event so each test owns a
    fresh Event bound to its own event loop. Without this reset, the second
    sync test reuses an Event bound to the first test's (now-closed) loop and
    fails with "bound to a different event loop".
    """
    from sse_starlette.sse import AppStatus

    AppStatus.should_exit_event = None
    base_app = mcp_server.server.streamable_http_app()
    wrapped: ASGIApp = strip_trailing_slash_middleware(base_app)
    wrapped = normalize_content_type_middleware(wrapped)
    with TestClient(wrapped, base_url=LOCALHOST_BASE_URL) as client:
        yield client
    AppStatus.should_exit_event = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _accept_headers() -> dict[str, str]:
    """Streamable-http requires both JSON and SSE accept types per spec 2025-06-18."""
    return {"Accept": "application/json, text/event-stream"}


def _initialize_payload(req_id: int = 1) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_SPEC_REVISION,
            "capabilities": {},
            "clientInfo": {"name": "falcon-mcp-compliance-tests", "version": "0.0.0"},
        },
    }


def _parse_jsonrpc(response: Any) -> dict[str, Any]:
    """Parse a streamable-http response (application/json or text/event-stream)."""
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for raw_line in response.text.splitlines():
            if raw_line.startswith("data: "):
                return json.loads(raw_line[len("data: "):])
        raise AssertionError(f"No data event in SSE response body: {response.text!r}")
    return response.json()


def _initialize_session(client: TestClient) -> tuple[str, dict[str, Any]]:
    """Initialize a streamable-http session, returning (session_id, init_result)."""
    response = client.post("/mcp", json=_initialize_payload(), headers=_accept_headers())
    assert response.status_code == 200, (
        f"initialize failed: {response.status_code} {response.text}"
    )
    session_id = response.headers.get("Mcp-Session-Id", "")
    body = _parse_jsonrpc(response)
    # Spec lifecycle: send initialized notification before further requests.
    client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers={**_accept_headers(), "Mcp-Session-Id": session_id},
    )
    return session_id, body


# ---------------------------------------------------------------------------
# Test 1: Origin header validation (spec 2025-06-18 transport security)
# ---------------------------------------------------------------------------


def test_streamable_http_rejects_foreign_origin(http_client: TestClient) -> None:
    """Spec 2025-06-18 transport security: SHOULD validate Origin header.

    Sends an initialize request with a foreign Origin and a valid Host. The
    server's DNS-rebinding middleware MUST reject the request because the
    Origin is not in the allowlist; if it accepts, a malicious page on
    evil.example.com could drive the local server via a victim's browser.
    """
    response = http_client.post(
        "/mcp",
        json=_initialize_payload(),
        headers={**_accept_headers(), "Origin": "http://evil.example.com"},
    )
    assert response.status_code >= 400, (
        f"Server accepted request with foreign Origin (status={response.status_code}, "
        f"body={response.text!r}). This is a DNS-rebinding vector per MCP spec "
        f"{MCP_SPEC_REVISION} transport security considerations."
    )


# ---------------------------------------------------------------------------
# Test 2: tools/list immutability across sessions (rug-pull guard)
# ---------------------------------------------------------------------------


async def test_tools_list_immutable_across_sessions(mcp_server: FalconMCPServer) -> None:
    """Spec 2025-06-18 tools: tool definitions MUST be stable across sessions.

    Per-session tampering of name, description, inputSchema, or annotations is a
    tool-poisoning vector. This guard catches drift between two fresh sessions.
    """

    def _tuple_for(tool: Any) -> tuple[str, str | None, str, str | None]:
        annotations_dump = (
            tool.annotations.model_dump_json() if tool.annotations is not None else None
        )
        return (
            tool.name,
            tool.description,
            json.dumps(tool.inputSchema, sort_keys=True),
            annotations_dump,
        )

    async with create_connected_server_and_client_session(mcp_server.server) as session:
        snap1 = sorted(_tuple_for(tool) for tool in (await session.list_tools()).tools)

    async with create_connected_server_and_client_session(mcp_server.server) as session:
        snap2 = sorted(_tuple_for(tool) for tool in (await session.list_tools()).tools)

    assert snap1 == snap2, "tools/list output differs between sessions"


# ---------------------------------------------------------------------------
# Test 3: JSON-RPC error code conformance
# ---------------------------------------------------------------------------


def test_jsonrpc_error_codes(http_client: TestClient) -> None:
    """JSON-RPC 2.0 §5.1 + MCP 2025-06-18: standard error codes for unknown method and invalid params.

    Strict per JSON-RPC 2.0 §5.1: unknown method MUST be -32601, invalid params MUST be -32602.
    The mcp library validates incoming requests against the union of all known
    method types via pydantic, which conflates "method does not exist" with
    "params are invalid" and returns -32602 for both cases. Until upstream
    distinguishes the two, this test accepts either code for the unknown-method
    case but still asserts a JSON-RPC error envelope is returned.
    """
    session_id, _ = _initialize_session(http_client)

    unknown = {
        "jsonrpc": "2.0",
        "id": 100,
        "method": "compliance/does-not-exist",
        "params": {},
    }
    response = http_client.post(
        "/mcp",
        json=unknown,
        headers={**_accept_headers(), "Mcp-Session-Id": session_id},
    )
    body = _parse_jsonrpc(response)
    assert "error" in body, f"Unknown method returned no error envelope: {body!r}"
    assert body["error"]["code"] in (-32601, -32602), (
        f"Unknown method MUST return -32601 (preferred per JSON-RPC 2.0 §5.1) or "
        f"-32602 (current mcp behavior); got {body['error']!r}"
    )

    # tools/call with params that fail JSON-RPC-level validation (missing the
    # required `name` field) MUST return -32602 Invalid params per spec.
    bad_params = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {},
    }
    response = http_client.post(
        "/mcp",
        json=bad_params,
        headers={**_accept_headers(), "Mcp-Session-Id": session_id},
    )
    body = _parse_jsonrpc(response)
    assert "error" in body, (
        f"tools/call with missing required `name` should return JSON-RPC error; got {body!r}"
    )
    assert body["error"]["code"] == -32602, (
        f"Invalid params MUST return -32602 per JSON-RPC 2.0 §5.1; got {body['error']!r}"
    )


# ---------------------------------------------------------------------------
# Test 4: Mcp-Session-Id binding and entropy
# ---------------------------------------------------------------------------


def test_mcp_session_id_binding_and_entropy(http_client: TestClient) -> None:
    """Spec 2025-06-18 streamable-http: session id MUST bind subsequent requests.

    The server MUST issue a session id on initialize, MUST reject mismatched ids
    on subsequent requests, and SHOULD use ids with sufficient entropy.
    """
    session_id, _ = _initialize_session(http_client)
    assert session_id, "initialize did not return Mcp-Session-Id header"
    # Entropy floor: 22 base64 chars carries ~128 bits.
    assert len(session_id) >= 22, (
        f"Mcp-Session-Id is too short for 128-bit entropy: len={len(session_id)} "
        f"(spec 2025-06-18 SHOULD use unguessable session ids)"
    )

    # Tampered id MUST be rejected. Mutate the first character to keep length stable.
    tampered = ("0" if session_id[0] != "0" else "1") + session_id[1:]
    assert tampered != session_id

    response = http_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 200, "method": "tools/list"},
        headers={**_accept_headers(), "Mcp-Session-Id": tampered},
    )
    assert response.status_code in (400, 401, 403, 404), (
        f"Server accepted request with tampered Mcp-Session-Id (status={response.status_code}, "
        f"body={response.text!r}). Spec 2025-06-18 streamable-http MUST reject mismatched ids."
    )


# ---------------------------------------------------------------------------
# Test 5: Capability negotiation honesty (listChanged matches reality)
# ---------------------------------------------------------------------------


async def test_capabilities_match_actual_behavior(mcp_server: FalconMCPServer) -> None:
    """Spec 2025-06-18 capabilities: listChanged MUST reflect server behavior.

    falcon-mcp registers tools and resources at startup and never adds, removes,
    or relabels them at runtime. Declaring listChanged=True would be a rug-pull
    surface: clients that trust the capability skip polling and miss updates,
    or wait forever for notifications that never arrive.
    """
    async with create_connected_server_and_client_session(mcp_server.server) as session:
        caps = session.get_server_capabilities()

    assert caps is not None, "ClientSession returned no server capabilities"

    # tools capability MUST be present because tools are registered.
    assert caps.tools is not None, "Server registers tools but declares no tools capability"
    assert caps.tools.listChanged is False, (
        f"Server declares tools.listChanged={caps.tools.listChanged} but never emits "
        "list_changed notifications; this is a capability-negotiation rug-pull surface."
    )

    # resources capability MUST be present because FQL guides are registered.
    has_any_resource = any(getattr(mod, "resources", []) for mod in mcp_server.modules.values())
    if has_any_resource:
        assert caps.resources is not None, (
            "Server registers FQL guide resources but declares no resources capability"
        )
        assert caps.resources.listChanged is False, (
            f"Server declares resources.listChanged={caps.resources.listChanged} but "
            "never emits list_changed notifications."
        )


# ---------------------------------------------------------------------------
# Test 6: Resource URI format compliance
# ---------------------------------------------------------------------------


async def test_resource_uri_format(mcp_server: FalconMCPServer) -> None:
    """Project convention: every guide URI is falcon://{module}/{path}/{kind}-guide.

    Also asserts that every module owning a tool with a `filter` parameter
    registers at least one guide resource.
    """
    async with create_connected_server_and_client_session(mcp_server.server) as session:
        list_result = await session.list_resources()
        tools_result = await session.list_tools()

    bad_uris = [
        str(resource.uri)
        for resource in list_result.resources
        if not RESOURCE_URI_PATTERN.match(str(resource.uri))
    ]
    assert not bad_uris, (
        "Resource URIs do not match falcon://{module}/{path}/{kind}-guide:\n"
        + "\n".join(f"  - {uri}" for uri in bad_uris)
    )

    module_tools: dict[str, set[str]] = {
        name: set(getattr(mod, "tools", [])) for name, mod in mcp_server.modules.items()
    }
    module_resources: dict[str, set[str]] = {
        name: set(getattr(mod, "resources", [])) for name, mod in mcp_server.modules.items()
    }

    missing: list[tuple[str, str]] = []
    for tool in tools_result.tools:
        properties = (tool.inputSchema or {}).get("properties", {}) or {}
        if "filter" not in properties:
            continue
        owning_module = next(
            (mod_name for mod_name, names in module_tools.items() if tool.name in names),
            None,
        )
        if owning_module is None:
            continue  # core tools (falcon_check_connectivity, etc.) have no module owner
        if not module_resources.get(owning_module):
            missing.append((tool.name, owning_module))

    assert not missing, (
        "Tools accept a `filter` parameter but their module registers no guide resource:\n"
        + "\n".join(f"  - tool={tool} module={mod}" for tool, mod in missing)
    )


# ---------------------------------------------------------------------------
# Test 7: Read-only annotation correctness across all modules
# ---------------------------------------------------------------------------


async def test_tool_annotations_across_all_modules(mcp_server: FalconMCPServer) -> None:
    """Spec 2025-06-18 tool annotations: readOnlyHint and destructiveHint MUST be honest.

    Default-deny posture: every tool not in MUTATING_TOOL_ALLOWLIST MUST declare
    readOnlyHint=True and destructiveHint=False. A new tool added later without
    an explicit readOnlyHint decision will fail this assertion and force the
    contributor to either set the right annotations or update the allowlist.
    """
    async with create_connected_server_and_client_session(mcp_server.server) as session:
        tools = (await session.list_tools()).tools

    violations: list[tuple[str, str]] = []
    for tool in tools:
        if tool.name in MUTATING_TOOL_ALLOWLIST:
            continue
        annotations = tool.annotations
        if annotations is None:
            violations.append((tool.name, "annotations=None"))
            continue
        if annotations.readOnlyHint is not True:
            violations.append((tool.name, f"readOnlyHint={annotations.readOnlyHint!r}"))
        if annotations.destructiveHint is not False:
            violations.append(
                (tool.name, f"destructiveHint={annotations.destructiveHint!r}")
            )

    assert not violations, (
        "Tools missing read-only annotations (and not in MUTATING_TOOL_ALLOWLIST):\n"
        + "\n".join(f"  - {name}: {reason}" for name, reason in violations)
    )
