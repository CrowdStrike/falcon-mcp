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

import anyio
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

# anyio's default CapacityLimiter for to_thread.run_sync, i.e. the ceiling on how
# many offloaded handlers run at once. Asserted (not just referenced) in
# TestThreadPoolBackpressure so an upstream change surfaces as a clear failure.
DEFAULT_THREAD_LIMIT = 40


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

    @staticmethod
    def _stub_env(mock_environ_get) -> None:
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "id",
            "FALCON_CLIENT_SECRET": "secret",
        }.get(key, default)

    @staticmethod
    def _fire_concurrently(client: FalconClient) -> None:
        """Release CONCURRENCY threads into client.command() simultaneously."""
        barrier = threading.Barrier(CONCURRENCY)

        def _call() -> None:
            barrier.wait()  # release all threads at once
            client.command("SomeOperation")

        threads = [threading.Thread(target=_call) for _ in range(CONCURRENCY)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_concurrent_stale_token_refreshes_once(self, mock_apiharness, mock_environ_get):
        self._stub_env(mock_environ_get)

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
        self._fire_concurrently(client)

        self.assertEqual(
            underlying.login.call_count,
            1,
            "stale-token refresh should fire exactly once under concurrency",
        )
        self.assertEqual(underlying.command.call_count, CONCURRENCY)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_failed_refresh_retries_serially_not_in_parallel(
        self, mock_apiharness, mock_environ_get
    ):
        """A failing login degrades to serial retries, never a parallel stampede.

        The double-check collapses callers only because a successful login clears
        `token_stale`. When login fails the token stays stale, so each waiting
        thread retries in turn. That is the documented trade-off (see
        `_ensure_token_fresh`): N serial attempts instead of N simultaneous ones,
        so a broken credential cannot fan out into a burst against the token
        endpoint. This pins that behavior — and that the lock is still released on
        the failure path rather than deadlocking the remaining callers.
        """
        self._stub_env(mock_environ_get)

        underlying = MagicMock()
        underlying.refreshable = True
        underlying.token_stale = True  # login never clears it: bad credentials

        overlap = []
        in_login = 0
        overlap_guard = threading.Lock()

        def _login() -> bool:
            nonlocal in_login
            with overlap_guard:
                in_login += 1
                overlap.append(in_login)
            time.sleep(0.02)
            with overlap_guard:
                in_login -= 1
            return False

        underlying.login.side_effect = _login
        underlying.command.return_value = {"status_code": 401, "body": {}}
        mock_apiharness.return_value = underlying

        client = FalconClient()
        self._fire_concurrently(client)

        # Never two logins in flight at once — the lock serializes the retries.
        self.assertEqual(
            max(overlap),
            1,
            f"token logins overlapped ({max(overlap)} concurrent); the refresh lock "
            "must serialize retries even when login fails",
        )
        # Every caller still reaches the API and gets the 401 back.
        self.assertEqual(underlying.command.call_count, CONCURRENCY)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_valid_token_skips_refresh(self, mock_apiharness, mock_environ_get):
        self._stub_env(mock_environ_get)

        underlying = MagicMock()
        underlying.refreshable = True
        underlying.token_stale = False  # already valid
        underlying.command.return_value = {"status_code": 200, "body": {}}
        mock_apiharness.return_value = underlying

        client = FalconClient()
        client.command("SomeOperation")

        underlying.login.assert_not_called()


class TestThreadPoolBackpressure(unittest.TestCase):
    """The offload path is bounded by anyio's default thread limiter, not unbounded."""

    def test_offload_shares_default_limiter(self):
        """Offloaded handlers borrow from the 40-token default limiter.

        Concurrency is capped rather than unbounded: calls past the limit queue for
        a worker instead of opening a thread (and a Falcon connection) per request.
        This pins both the cap's existence and that our wrapper uses the shared
        default limiter rather than an unbounded pool.
        """
        peak = 0
        current = 0
        guard = threading.Lock()
        released = threading.Event()

        def handler() -> int:
            nonlocal peak, current
            with guard:
                current += 1
                peak = max(peak, current)
            released.wait(timeout=5)
            with guard:
                current -= 1
            return 1

        wrapped = offload_to_thread(handler)
        oversubscribe = 2 * DEFAULT_THREAD_LIMIT + 5

        async def fire_all() -> None:
            async with anyio.create_task_group() as tg:
                limiter = anyio.to_thread.current_default_thread_limiter()
                self.assertEqual(
                    limiter.total_tokens,
                    DEFAULT_THREAD_LIMIT,
                    "anyio's default thread limiter changed; revisit the cap "
                    "documented on offload_to_thread",
                )
                for _ in range(oversubscribe):
                    tg.start_soon(wrapped)
                # Let the first wave saturate the pool, then drain everything.
                await anyio.sleep(0.2)
                released.set()

        anyio.run(fire_all)

        self.assertEqual(
            peak,
            DEFAULT_THREAD_LIMIT,
            f"{oversubscribe} concurrent calls ran {peak} handlers at once; expected "
            f"the pool to cap at {DEFAULT_THREAD_LIMIT} and queue the rest",
        )

    def test_cancelled_call_still_completes_its_thread(self):
        """Cancellation does not abandon the worker mid-call.

        We keep anyio's default `abandon_on_cancel=False`, so a client disconnect
        or the MCP 60s timeout waits for the in-flight blocking call instead of
        orphaning the thread. Abandoning would free the slot sooner but leak
        threads without bound under repeated timeouts.
        """
        finished = threading.Event()

        def handler() -> int:
            time.sleep(SLEEP_SECONDS)
            finished.set()
            return 1

        wrapped = offload_to_thread(handler)

        async def cancel_early() -> float:
            start = time.monotonic()
            with anyio.move_on_after(SLEEP_SECONDS / 10):
                await wrapped()
            return time.monotonic() - start

        elapsed = anyio.run(cancel_early)

        self.assertTrue(
            finished.is_set(),
            "handler should run to completion even though the caller cancelled",
        )
        self.assertGreaterEqual(
            elapsed,
            SLEEP_SECONDS,
            "cancel scope should wait for the blocking call rather than abandon it; "
            f"returned after {elapsed:.2f}s",
        )


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
