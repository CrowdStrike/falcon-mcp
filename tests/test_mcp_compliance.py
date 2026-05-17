"""MCP protocol compliance tests for falcon-mcp.

Asserts conformance to MCP specification and JSON-RPC 2.0.
Each assertion cites the spec section it enforces.

Resolves #235.
"""

import json
import re
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from httpx import Response
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import LATEST_PROTOCOL_VERSION
from starlette.testclient import TestClient

from falcon_mcp.common.auth import (
    ASGIApp,
    normalize_content_type_middleware,
    strip_trailing_slash_middleware,
)
from falcon_mcp.server import FalconMCPServer

# Tools intentionally allowed to declare readOnlyHint=False.
# Add a name here only after explicit security review confirms the tool mutates
# tenant state. The test enforces bidirectional correctness: new mutating tools
# not in this set fail, AND stale entries (deleted/reverted tools) also fail.
MUTATING_TOOL_ALLOWLIST: set[str] = {
    # ioc module
    "falcon_add_ioc",
    "falcon_remove_iocs",
    # firewall module
    "falcon_create_firewall_rule_group",
    "falcon_delete_firewall_rule_groups",
    # custom_ioa module
    "falcon_create_ioa_rule_group",
    "falcon_update_ioa_rule_group",
    "falcon_delete_ioa_rule_groups",
    "falcon_create_ioa_rule",
    "falcon_update_ioa_rule",
    "falcon_delete_ioa_rules",
    # rtr module
    "falcon_init_rtr_session",
    "falcon_pulse_rtr_session",
    "falcon_execute_rtr_read_only_command",
    "falcon_delete_rtr_session",
    # shield module
    "falcon_dismiss_shield_check",
    # scheduled_reports module
    "falcon_launch_scheduled_report",
    # cloud module (cspm suppression rules)
    "falcon_create_cspm_suppression_rule",
    "falcon_delete_cspm_suppression_rules",
    # cases module
    "falcon_create_case",
    "falcon_update_case",
    "falcon_add_case_alert_evidence",
    "falcon_add_case_event_evidence",
    "falcon_manage_case_tags",
}

RESOURCE_URI_PATTERN = re.compile(r"^falcon://[a-z0-9-]+(/[a-z0-9-]+)+/[a-z]+-guide$")

LOCALHOST_BASE_URL = "http://127.0.0.1:8000"

ACCEPT_HEADERS: dict[str, str] = {"Accept": "application/json, text/event-stream"}


def _initialize_payload(req_id: int = 1) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "initialize",
        "params": {
            "protocolVersion": LATEST_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "falcon-mcp-compliance-tests", "version": "0.0.0"},
        },
    }


def _parse_jsonrpc(response: Response) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for raw_line in response.text.splitlines():
            if raw_line.startswith("data: "):
                return json.loads(raw_line[len("data: "):])
        raise AssertionError(f"No data event in SSE response body: {response.text!r}")
    return response.json()


def _initialize_session(client: TestClient) -> tuple[str, dict[str, Any]]:
    response = client.post("/mcp", json=_initialize_payload(), headers=ACCEPT_HEADERS)
    assert response.status_code == 200, (
        f"initialize failed: {response.status_code} {response.text}"
    )
    session_id = response.headers.get("Mcp-Session-Id", "")
    body = _parse_jsonrpc(response)
    client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers={**ACCEPT_HEADERS, "Mcp-Session-Id": session_id},
    )
    return session_id, body


class TestMCPComplianceTransport(unittest.TestCase):
    """Transport-level MCP protocol compliance tests using starlette TestClient."""

    def setUp(self):
        patcher = patch("falcon_mcp.server.FalconClient")
        self.mock_client_cls = patcher.start()
        self.addCleanup(patcher.stop)

        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        self.mock_client_cls.return_value = mock_client

        self.mcp_server = FalconMCPServer()

        from sse_starlette.sse import AppStatus

        AppStatus.should_exit = False
        AppStatus.should_exit_event = None

        base_app = self.mcp_server.server.streamable_http_app()
        wrapped: ASGIApp = strip_trailing_slash_middleware(base_app)
        wrapped = normalize_content_type_middleware(wrapped)
        self.http_client = TestClient(wrapped, base_url=LOCALHOST_BASE_URL)
        self.http_client.__enter__()

    def tearDown(self):
        self.http_client.__exit__(None, None, None)

        from sse_starlette.sse import AppStatus

        AppStatus.should_exit = False
        AppStatus.should_exit_event = None

    def test_streamable_http_rejects_foreign_origin(self):
        """Spec transport security: SHOULD validate Origin header.

        A foreign Origin on a valid Host is a DNS-rebinding vector.
        """
        response = self.http_client.post(
            "/mcp",
            json=_initialize_payload(),
            headers={**ACCEPT_HEADERS, "Origin": "http://evil.example.com"},
        )
        self.assertGreaterEqual(
            response.status_code,
            400,
            f"Server accepted request with foreign Origin (status={response.status_code}). "
            f"This is a DNS-rebinding vector per MCP spec transport security.",
        )

    def test_jsonrpc_error_codes(self):
        """JSON-RPC 2.0 §5.1: unknown method → -32601, invalid params → -32602.

        The mcp library returns -32602 for unknown methods due to pydantic union
        validation. This test accepts either code for the unknown-method case
        until upstream distinguishes the two.
        """
        session_id, _ = _initialize_session(self.http_client)

        unknown = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "compliance/does-not-exist",
            "params": {},
        }
        response = self.http_client.post(
            "/mcp",
            json=unknown,
            headers={**ACCEPT_HEADERS, "Mcp-Session-Id": session_id},
        )
        body = _parse_jsonrpc(response)
        self.assertIn("error", body, f"Unknown method returned no error envelope: {body!r}")
        self.assertIn(
            body["error"]["code"],
            (-32601, -32602),
            f"Unknown method MUST return -32601 or -32602; got {body['error']!r}",
        )

        bad_params = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {},
        }
        response = self.http_client.post(
            "/mcp",
            json=bad_params,
            headers={**ACCEPT_HEADERS, "Mcp-Session-Id": session_id},
        )
        body = _parse_jsonrpc(response)
        self.assertIn(
            "error",
            body,
            f"tools/call with missing `name` should return JSON-RPC error; got {body!r}",
        )
        self.assertEqual(
            body["error"]["code"],
            -32602,
            f"Invalid params MUST return -32602 per JSON-RPC 2.0 §5.1; got {body['error']!r}",
        )

    def test_mcp_session_id_binding_and_entropy(self):
        """Spec streamable-http: session id MUST bind requests, SHOULD have sufficient entropy."""
        session_id, _ = _initialize_session(self.http_client)
        self.assertTrue(session_id, "initialize did not return Mcp-Session-Id header")
        # 22 base64 chars ≥ 128 bits of entropy (6 bits/char × 22 = 132 bits)
        self.assertGreaterEqual(
            len(session_id),
            22,
            f"Mcp-Session-Id too short for 128-bit entropy: len={len(session_id)}",
        )

        tampered = ("0" if session_id[0] != "0" else "1") + session_id[1:]
        self.assertNotEqual(tampered, session_id)

        response = self.http_client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 200, "method": "tools/list"},
            headers={**ACCEPT_HEADERS, "Mcp-Session-Id": tampered},
        )
        self.assertIn(
            response.status_code,
            (400, 401, 403, 404),
            f"Server accepted tampered Mcp-Session-Id (status={response.status_code}). "
            f"Spec MUST reject mismatched session ids.",
        )


class TestMCPComplianceProtocol(unittest.IsolatedAsyncioTestCase):
    """Protocol-level MCP compliance tests using in-process client sessions."""

    def setUp(self):
        patcher = patch("falcon_mcp.server.FalconClient")
        self.mock_client_cls = patcher.start()
        self.addCleanup(patcher.stop)

        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        self.mock_client_cls.return_value = mock_client

        self.mcp_server = FalconMCPServer()

    async def test_tools_list_immutable_across_sessions(self):
        """Tool definitions MUST be stable across sessions (rug-pull guard)."""

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

        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            snap1 = sorted(
                _tuple_for(tool) for tool in (await session.list_tools()).tools
            )

        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            snap2 = sorted(
                _tuple_for(tool) for tool in (await session.list_tools()).tools
            )

        self.assertEqual(snap1, snap2, "tools/list output differs between sessions")

    async def test_capabilities_match_actual_behavior(self):
        """Capabilities: listChanged MUST reflect server behavior.

        falcon-mcp registers tools and resources at startup and never changes
        them at runtime. Declaring listChanged=True would mislead clients.
        """
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            caps = session.get_server_capabilities()

        self.assertIsNotNone(caps, "ClientSession returned no server capabilities")

        self.assertIsNotNone(
            caps.tools, "Server registers tools but declares no tools capability"
        )
        self.assertFalse(
            caps.tools.listChanged,
            f"Server declares tools.listChanged={caps.tools.listChanged} but "
            "never emits list_changed notifications.",
        )

        has_any_resource = any(
            len(getattr(mod, "resources", [])) > 0
            for mod in self.mcp_server.modules.values()
        )
        if has_any_resource:
            self.assertIsNotNone(
                caps.resources,
                "Server registers resources but declares no resources capability",
            )
            self.assertFalse(
                caps.resources.listChanged,
                f"Server declares resources.listChanged={caps.resources.listChanged} "
                "but never emits list_changed notifications.",
            )

    async def test_resource_uri_format(self):
        """Every guide URI MUST match falcon://{module}/{path}/{kind}-guide.

        Also asserts that every module with a filter-accepting tool registers
        at least one guide resource.
        """
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            list_result = await session.list_resources()
            tools_result = await session.list_tools()

        bad_uris = [
            str(resource.uri)
            for resource in list_result.resources
            if not RESOURCE_URI_PATTERN.match(str(resource.uri))
        ]
        self.assertFalse(
            bad_uris,
            "Resource URIs do not match falcon://{module}/{path}/{kind}-guide:\n"
            + "\n".join(f"  - {uri}" for uri in bad_uris),
        )

        module_tools: dict[str, set[str]] = {
            name: set(getattr(mod, "tools", []))
            for name, mod in self.mcp_server.modules.items()
        }
        module_resources: dict[str, set[str]] = {
            name: set(getattr(mod, "resources", []))
            for name, mod in self.mcp_server.modules.items()
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
                continue
            if not module_resources.get(owning_module):
                missing.append((tool.name, owning_module))

        self.assertFalse(
            missing,
            "Tools accept a `filter` parameter but their module registers no guide resource:\n"
            + "\n".join(f"  - tool={tool} module={mod}" for tool, mod in missing),
        )

    async def test_tool_annotations_across_all_modules(self):
        """Tool annotations: readOnlyHint and destructiveHint MUST be honest.

        Default-deny posture: every tool not in MUTATING_TOOL_ALLOWLIST MUST
        declare readOnlyHint=True and destructiveHint=False. The allowlist is
        enforced bidirectionally — stale entries and reverted tools also fail.
        """
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        tool_map = {t.name: t.annotations for t in tools}
        registered_names = set(tool_map)

        # Catch stale allowlist entries (deleted or renamed tools)
        ghost_entries = MUTATING_TOOL_ALLOWLIST - registered_names
        self.assertFalse(
            ghost_entries,
            "MUTATING_TOOL_ALLOWLIST contains tool names that no longer exist. "
            "Remove stale entries:\n"
            + "\n".join(f"  - {name}" for name in sorted(ghost_entries)),
        )

        # Catch allowlisted tools that were reverted to read-only
        still_read_only: list[tuple[str, str]] = []
        for name in MUTATING_TOOL_ALLOWLIST:
            annotations = tool_map[name]
            if annotations is None or annotations.readOnlyHint is not False:
                read_only_val = None if annotations is None else annotations.readOnlyHint
                still_read_only.append((name, f"readOnlyHint={read_only_val!r}"))

        self.assertFalse(
            still_read_only,
            "MUTATING_TOOL_ALLOWLIST contains tools that are now read-only. "
            "Remove them from the allowlist or restore their mutating annotations:\n"
            + "\n".join(f"  - {name}: {reason}" for name, reason in still_read_only),
        )

        # Catch non-allowlisted tools that are missing read-only annotations
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

        self.assertFalse(
            violations,
            "Tools missing read-only annotations (add to MUTATING_TOOL_ALLOWLIST "
            "only after security review confirms the tool mutates tenant state):\n"
            + "\n".join(f"  - {name}: {reason}" for name, reason in violations),
        )


if __name__ == "__main__":
    unittest.main()
