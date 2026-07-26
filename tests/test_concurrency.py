"""
Concurrency regression tests for the tool-offload wrapper.

The bug these guard against: sync tool handlers ran inline on the asyncio event
loop, so a single blocking Falcon call froze the loop and serialized every other
in-flight request. `offload_to_thread` (applied in `BaseModule._add_tool` and to
the core tools in `server.py`) runs each sync handler on a worker thread so a
single server instance interleaves concurrent calls.

These tests would fail (wall-clock ≈ N × sleep) if the wrapper were removed.
"""

import asyncio
import threading
import time
import unittest
from collections.abc import Coroutine
from inspect import iscoroutinefunction
from typing import Any, TypeVar
from unittest.mock import MagicMock, patch

from mcp.server.fastmcp import FastMCP

from falcon_mcp.client import FalconClient
from falcon_mcp.dynamic import DynamicMode
from falcon_mcp.modules.base import BaseModule, offload_to_thread

_T = TypeVar("_T")

# Per-call sleep and fan-out. If handlers run serially, total ≈ CONCURRENCY *
# SLEEP_SECONDS; concurrent, total ≈ SLEEP_SECONDS. The threshold sits well
# between the two so timing jitter can't flip the result.
SLEEP_SECONDS = 0.3
CONCURRENCY = 8
SERIAL_TOTAL = SLEEP_SECONDS * CONCURRENCY
CONCURRENT_THRESHOLD = SLEEP_SECONDS * 3  # 0.9s << serial 2.4s


def run_async(coro: Coroutine[Any, Any, _T]) -> _T:
    return asyncio.run(coro)


class _SleepingModule(BaseModule):
    """A module with one sync tool that blocks on client.command (like real handlers)."""

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(server=server, method=self.slow_tool, name="slow_tool")

    def slow_tool(self) -> dict[str, Any]:
        """Sleep, then return a canned result (stands in for a slow Falcon call)."""
        return self.client.command("SlowOperation")


def _make_sleeping_client() -> MagicMock:
    """A mock FalconClient whose command() blocks for SLEEP_SECONDS."""
    client = MagicMock(spec=FalconClient)

    def _blocking_command(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        time.sleep(SLEEP_SECONDS)
        return {"status_code": 200, "body": {"resources": [{"id": "ok"}]}}

    client.command.side_effect = _blocking_command
    return client


class TestOffloadToThread(unittest.TestCase):
    """Unit tests for the wrapper itself."""

    def test_sync_handler_is_wrapped_as_async(self):
        def handler() -> str:
            return "sync"

        wrapped = offload_to_thread(handler)
        self.assertTrue(iscoroutinefunction(wrapped))
        self.assertEqual(run_async(wrapped()), "sync")

    def test_async_handler_returned_untouched(self):
        async def handler() -> str:
            return "async"

        # Already-async handlers (e.g. ngsiem) must not be double-wrapped.
        self.assertIs(offload_to_thread(handler), handler)

    def test_wrapper_preserves_wrapped_reference(self):
        def handler() -> None:
            """Docstring."""

        wrapped = offload_to_thread(handler)
        self.assertIs(wrapped.__wrapped__, handler)
        self.assertEqual(wrapped.__doc__, handler.__doc__)


class TestStandardModeConcurrency(unittest.TestCase):
    """Standard mode: module tools registered via _add_tool run concurrently."""

    def _build_tool(self):
        server = FastMCP("test")
        module = _SleepingModule(_make_sleeping_client())
        module.register_tools(server)
        return server._tool_manager._tools["falcon_slow_tool"]

    def test_registered_tool_is_async(self):
        tool = self._build_tool()
        self.assertTrue(tool.is_async, "wrapped handler must be detected as async")

    def test_concurrent_tool_runs_interleave(self):
        tool = self._build_tool()

        async def fire_all() -> float:
            start = time.monotonic()
            await asyncio.gather(*(tool.run({}) for _ in range(CONCURRENCY)))
            return time.monotonic() - start

        elapsed = run_async(fire_all())
        self.assertLess(
            elapsed,
            CONCURRENT_THRESHOLD,
            f"{CONCURRENCY} calls took {elapsed:.2f}s; expected ~{SLEEP_SECONDS}s "
            f"(serial would be ~{SERIAL_TOTAL:.2f}s) — handlers are not interleaving",
        )


class TestDynamicModeConcurrency(unittest.TestCase):
    """Dynamic mode: falcon_execute_tool dispatches to the same wrapped handlers."""

    def _build_dynamic(self):
        server = FastMCP("test")
        modules = {"sleeping": _SleepingModule(_make_sleeping_client())}
        dynamic = DynamicMode(modules, server)
        return dynamic

    def test_execute_tool_runs_interleave(self):
        dynamic = self._build_dynamic()

        async def fire_all() -> float:
            start = time.monotonic()
            await asyncio.gather(
                *(
                    dynamic._execute_tool(tool_name="falcon_slow_tool", parameters={})
                    for _ in range(CONCURRENCY)
                )
            )
            return time.monotonic() - start

        elapsed = run_async(fire_all())
        self.assertLess(
            elapsed,
            CONCURRENT_THRESHOLD,
            f"dynamic mode: {CONCURRENCY} calls took {elapsed:.2f}s; expected "
            f"~{SLEEP_SECONDS}s (serial would be ~{SERIAL_TOTAL:.2f}s)",
        )


class TestTokenRefreshLock(unittest.TestCase):
    """Only one thread refreshes a stale token; the rest reuse it."""

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_concurrent_stale_token_refreshes_once(self, mock_apiharness, mock_environ_get):
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "id",
            "FALCON_CLIENT_SECRET": "secret",
        }.get(key, default)

        underlying = MagicMock()
        underlying.refreshable = True
        # Token starts stale; the first login() clears it. A small sleep inside
        # login widens the race window so an unlocked implementation would let
        # multiple threads in.
        underlying.token_stale = True

        def _login() -> bool:
            time.sleep(0.05)
            underlying.token_stale = False
            return True

        underlying.login.side_effect = _login
        underlying.command.return_value = {"status_code": 200, "body": {}}
        mock_apiharness.return_value = underlying

        client = FalconClient()

        barrier = threading.Barrier(CONCURRENCY)

        def _call() -> None:
            barrier.wait()  # release all threads at once
            client.command("SomeOperation")

        threads = [threading.Thread(target=_call) for _ in range(CONCURRENCY)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(
            underlying.login.call_count,
            1,
            "stale-token refresh should fire exactly once under concurrency",
        )
        self.assertEqual(underlying.command.call_count, CONCURRENCY)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_valid_token_skips_refresh(self, mock_apiharness, mock_environ_get):
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "id",
            "FALCON_CLIENT_SECRET": "secret",
        }.get(key, default)

        underlying = MagicMock()
        underlying.refreshable = True
        underlying.token_stale = False  # already valid
        underlying.command.return_value = {"status_code": 200, "body": {}}
        mock_apiharness.return_value = underlying

        client = FalconClient()
        client.command("SomeOperation")

        underlying.login.assert_not_called()


class TestCommandAsync(unittest.TestCase):
    """command_async offloads the blocking call to a worker thread."""

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_command_async_returns_result_off_loop(self, mock_apiharness, mock_environ_get):
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "id",
            "FALCON_CLIENT_SECRET": "secret",
        }.get(key, default)

        underlying = MagicMock()
        underlying.refreshable = True
        underlying.token_stale = False
        loop_thread = threading.get_ident()
        seen: dict[str, int] = {}

        def _command(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
            seen["thread"] = threading.get_ident()
            return {"status_code": 200, "body": {"resources": []}}

        underlying.command.side_effect = _command
        mock_apiharness.return_value = underlying

        client = FalconClient()

        async def call() -> dict[str, Any]:
            return await client.command_async("Op")

        result = run_async(call())
        self.assertEqual(result["status_code"], 200)
        # The blocking call ran on a worker thread, not the calling thread.
        self.assertNotEqual(seen["thread"], loop_thread)


if __name__ == "__main__":
    unittest.main()
