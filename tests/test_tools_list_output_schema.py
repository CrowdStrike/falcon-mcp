"""Regression tests for issue #325.

Assert that tools/list responses omit outputSchema. The unconditional
emission inflated per-tool payload and caused context-budget-constrained
clients (VS Code Copilot) to silently drop tools.
"""

import unittest
from unittest.mock import MagicMock, patch

from mcp.shared.memory import create_connected_server_and_client_session

from falcon_mcp.server import FalconMCPServer


class TestToolsListOutputSchema(unittest.IsolatedAsyncioTestCase):
    """In-process tools/list assertions for issue #325."""

    def setUp(self):
        patcher = patch("falcon_mcp.server.FalconClient")
        self.mock_client_cls = patcher.start()
        self.addCleanup(patcher.stop)

        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        self.mock_client_cls.return_value = mock_client

        self.mcp_server = FalconMCPServer()

    async def test_every_tool_omits_output_schema(self):
        """No tool returned by tools/list may declare outputSchema.

        outputSchema is intended for post-call structured output validation
        per MCP 2025-11-25, not tool selection. Including it in tools/list
        doubles per-tool payload for typed return values and pushes the
        full catalogue past VS Code Copilot's context budget.
        """
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        self.assertGreater(len(tools), 0, "FalconMCPServer registered no tools")

        offenders = [t.name for t in tools if t.outputSchema is not None]
        self.assertFalse(
            offenders,
            "Tools must not declare outputSchema in tools/list (issue #325). "
            "Offending tools:\n"
            + "\n".join(f"  - {name}" for name in sorted(offenders)),
        )

    async def test_every_tool_still_has_input_schema(self):
        """Disabling structured output must not affect inputSchema emission."""
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        missing = [t.name for t in tools if not t.inputSchema]
        self.assertFalse(
            missing,
            "Tools missing inputSchema (regression of issue #325 fix):\n"
            + "\n".join(f"  - {name}" for name in sorted(missing)),
        )

    async def test_tools_list_payload_within_budget(self):
        """Guard against tools/list payload exceeding client context budgets."""
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        total = sum(
            len(t.model_dump_json(by_alias=True, exclude_none=True))
            for t in tools
        )
        budget = 120_000
        self.assertLess(
            total,
            budget,
            f"tools/list payload is {total:,} bytes, exceeding {budget:,} byte budget",
        )


if __name__ == "__main__":
    unittest.main()
