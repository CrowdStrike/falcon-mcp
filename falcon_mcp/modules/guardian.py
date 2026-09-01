"""
Guardian module for Falcon MCP Server.

Provides tools for querying AI agent inventory and activity data.

FalconPy models no AIDR service class, so every call here uses the
`override="METHOD,/route"` raw-request escape hatch (precedent: cloud.py,
agentworks.py). Note the deliberate naming split: the MCP tools and this module are
named "Guardian", but the platform names the underlying API surface "AIDR" — hence
the `/aidr/*` routes, the `aidr_events_query` operation label, and the `AIDR:read`
scope. That is intentional, not a leftover rename.
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
from typing import Any

import anyio
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.guardian import (
    AGENTIC_INVENTORY_SCHEMA_DOCUMENTATION,
    ENTITY_SCHEMA_DOCUMENTATION,
    EXAMPLE_QUERIES_DOCUMENTATION,
    QUERY_GUIDE_DOCUMENTATION,
)

logger = get_logger(__name__)

# Single operation label for every /aidr route. This is not a FalconPy operation —
# all calls go through `override=` — so it only drives scope hints (AIDR:read, see
# common/api_scopes.py) and log lines, exactly as agentworks.py uses its labels.
_AIDR_OPERATION = "aidr_events_query"

# --- Query routes: return matching records directly, no separate hydration step ---
# Most are entity-store backed (filter LastSeen); the LogScale-backed ones
# (executions, tool-usage, skill-usage, prompts) take a relative store-header window.
_AGENTS_QUERY_ROUTE = "/aidr/queries/agents/v1"
_AGENT_SESSIONS_QUERY_ROUTE = "/aidr/queries/agent-sessions/v1"
_EXECUTIONS_QUERY_ROUTE = "/aidr/queries/executions/v1"
_TOOLS_QUERY_ROUTE = "/aidr/queries/tools/v1"
_TOOL_USAGE_QUERY_ROUTE = "/aidr/queries/tool-usage/v1"
_SKILLS_QUERY_ROUTE = "/aidr/queries/skills/v1"
_SKILL_USAGE_QUERY_ROUTE = "/aidr/queries/skill-usage/v1"
_AGENT_OS_USERS_QUERY_ROUTE = "/aidr/queries/agent-os-users/v1"
_PROMPTS_QUERY_ROUTE = "/aidr/queries/prompts/v1"
_DETECTIONS_QUERY_ROUTE = "/aidr/queries/detections/v1"
_MCP_SERVER_NAMES_QUERY_ROUTE = "/aidr/queries/mcp-server-names/v1"
_AGENT_INSTALLATIONS_QUERY_ROUTE = "/aidr/queries/agent-installations/v1"
_MODEL_NAMES_QUERY_ROUTE = "/aidr/queries/model-names/v1"

# --- Entity routes: fetch one record or graph by id, no time dimension ---
_AGENTS_ENTITIES_ROUTE = "/aidr/entities/agents/v1"
_EXECUTIONS_ENTITIES_ROUTE = "/aidr/entities/executions/v1"
_SESSION_ACTIVITY_ROUTE = "/aidr/entities/session-activity/v1"
_PROCESS_TREE_ROUTE = "/aidr/entities/process-tree/v1"
_NETWORK_EVENTS_ROUTE = "/aidr/entities/network-events/v1"
_FILE_EVENTS_ROUTE = "/aidr/entities/file-events/v1"
_CLASSIFIED_FILE_ACCESS_ROUTE = "/aidr/entities/classified-file-access/v1"

# --- Aggregate routes: grouped counts, no pagination. All accept time_range. ---
_AGENTS_AGGREGATES_ROUTE = "/aidr/aggregates/agents/v1"
_AGENT_SESSIONS_AGGREGATES_ROUTE = "/aidr/aggregates/agent-sessions/v1"
_TOOLS_AGGREGATES_ROUTE = "/aidr/aggregates/tools/v1"
_SKILLS_AGGREGATES_ROUTE = "/aidr/aggregates/skills/v1"
_DETECTIONS_AGGREGATES_ROUTE = "/aidr/aggregates/detections/v1"

# A 64-hex string is the AIAgent.Id / AgentIds[] token. The detection routes'
# agent_id param wants the 32-hex SensorId instead; the API silently returns zero
# rows for the 64-hex form, so we reject it up front with a guiding error.
_AGENT_IDS_TOKEN_PATTERN = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)

# Progressively narrower windows tried when the API refuses the requested one.
_NARROWING_LADDER: tuple[str, ...] = ("7d", "24h", "6h", "1h")

# Wall-clock cap on the narrowing ladder. Deliberately below the 60s MCP client
# request timeout, matching the reasoning in agentworks.py: a call that outlives the
# client is killed mid-flight, so it is better to answer with a notice. Several tools
# fan out and run this ladder on multiple legs at once, so the cap is per request.
_LADDER_BUDGET_SECONDS = 30.0

# Aggregate routes group at most this many buckets and offer no pagination, so a
# full page is indistinguishable from a truncated one without a warning.
_AGGREGATE_GROUP_LIMIT = 500

_TIME_UNIT_DAYS: dict[str, float] = {"h": 1 / 24, "d": 1.0}
_TIME_RANGE_PATTERN = re.compile(r"^(\d+)([hd])$")

# Units the /aidr time_range accepts. Minutes were dropped by the API
# ("invalid time_range unit: \"m\"; supported: 'h' (hours), 'd' (days)"), so a
# value like "30m" is rejected up front rather than sent and 400'd — see
# _reject_bad_time_range.
_SUPPORTED_TIME_RANGE_UNITS = "'h' (hours), 'd' (days)"

# Routes with no time dimension: time_range is absent from their parameter
# allowlists, so sending it is a 400 rather than a no-op. It is dropped instead.
# These are the entity fetch-by-id endpoints and the threat-graph endpoints; every
# queries/* and aggregates/* endpoint now accepts time_range (this changed with the
# reshaped API — installs, models, and the skills aggregate previously rejected it).
_NO_TIME_RANGE_ROUTES = frozenset({
    _AGENTS_ENTITIES_ROUTE,
    _EXECUTIONS_ENTITIES_ROUTE,
    _SESSION_ACTIVITY_ROUTE,
    _PROCESS_TREE_ROUTE,
    _NETWORK_EVENTS_ROUTE,
    _FILE_EVENTS_ROUTE,
    _CLASSIFIED_FILE_ACCESS_ROUTE,
})


def sanitize_guardian_value(value: str) -> str:
    """Sanitize a user-supplied value before use in Guardian queries.

    Raises ValueError if the value contains dangerous characters
    (single quotes, backslashes, newlines).
    """
    if "'" in value:
        raise ValueError(f"Invalid value: single quotes are not allowed: {value!r}")
    if "\\" in value:
        raise ValueError(f"Invalid value: backslashes are not allowed: {value!r}")
    if "\n" in value or "\r" in value:
        raise ValueError(f"Invalid value: newlines are not allowed: {value!r}")
    return value


def _reject_agent_ids_token(agent_id: str | None) -> dict[str, Any] | None:
    """Guard an ``agent_id`` filter against the 64-hex AIAgent.Id / AgentIds token.

    The detection routes filter on the 32-hex ``SensorId`` (``aid``). A 64-hex value
    is the AgentIds[]/Id token instead, and the API answers it with an empty result
    rather than an error — indistinguishable from a real no-match. Returns an error
    payload to short-circuit on that mistake, or None when the value is fine.
    """
    if agent_id and _AGENT_IDS_TOKEN_PATTERN.match(agent_id):
        return {
            "error": (
                f"agent_id {agent_id!r} looks like a 64-hex AIAgent.Id/AgentIds "
                f"value. This filter wants the 32-hex SensorId (aid); the API "
                f"silently returns zero rows for the 64-hex form. Use the "
                f"SensorId from a search_guardian_agents result."
            )
        }
    return None


def _parse_time_range_days(value: str) -> float | None:
    """Convert a window like "24h" or "7d" to a number of days.

    Returns None when the value cannot be parsed, so it passes through to the
    API untouched and the API returns its own validation error rather than us
    guessing at an unfamiliar format.
    """
    match = _TIME_RANGE_PATTERN.match(value.strip()) if value else None
    if not match:
        return None
    amount, unit = match.groups()
    return int(amount) * _TIME_UNIT_DAYS[unit]


def _bad_time_range_unit(value: str | None) -> str | None:
    """Return the offending unit when ``value`` uses a unit the API rejects.

    The /aidr time_range accepts only hours and days. A minutes value like
    "30m" is a plausible window a caller may try, but the API 400s it, and that
    400 names ``time_range`` — which trips the reactive narrowing ladder into
    retrying and then emitting a filter-the-query notice that has nothing to do
    with the real cause. So a recognizable-but-unsupported unit is caught before
    the request. A value we cannot parse at all still passes through, so the API
    stays the authority on genuinely unfamiliar formats.
    """
    if not value:
        return None
    m = re.match(r"^(\d+)([a-zA-Z]+)$", value.strip())
    if m and m.group(2) not in _TIME_UNIT_DAYS:
        return m.group(2)
    return None


def _clamp_time_range(route: str, value: str | None) -> tuple[str | None, str | None]:
    """Drop a time_range the route does not accept at all.

    Returns (effective_value, notice). No ceiling is applied here on purpose: the
    /aidr lookback limits differ between deployments, so the requested window goes
    to the API as asked and the API is the authority on what it will serve. When it
    refuses, `_query` narrows reactively and says so.
    """
    if value is None:
        return None, None

    if route in _NO_TIME_RANGE_ROUTES:
        return None, (
            f"time_range is not accepted by {route} and was dropped, so all matching "
            f"records are returned rather than a windowed subset."
        )

    return value, None


def _narrowing_rungs(effective: str) -> list[str]:
    """Ladder rungs strictly narrower than ``effective``."""
    current_days = _parse_time_range_days(effective)
    if current_days is None:
        return []

    rungs = []
    for rung in _NARROWING_LADDER:
        rung_days = _parse_time_range_days(rung)
        if rung_days is None:
            continue
        if rung_days < current_days:
            rungs.append(rung)
    return rungs


@dataclass
class GuardianResponse:
    """Parsed response from a single /aidr call.

    Carries `notices` because Guardian adjusts requests the caller did not ask for
    (narrowing a too-wide time_range, dropping an unsupported one, flagging a
    truncated aggregate). Those adjustments change what the numbers mean, so they
    travel with the data rather than being applied silently.
    """

    resources: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    status_code: int | None = None
    notices: list[str] = field(default_factory=list)
    pagination: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    @property
    def count(self) -> int:
        return len(self.resources)

    @property
    def is_timeout(self) -> bool:
        """True when the API aborted the query for taking too long.

        Checked against the status code rather than the error text so a
        reworded API message cannot silently disable the retry ladder.
        """
        return self.status_code == 504

    @property
    def rejects_window(self) -> bool:
        """True when the API refused the request because of its time window.

        Two observed forms: a 504 when the engine gives up, and — defensively — a
        400 that names `time_range`. The /aidr lookback limits differ between
        deployments, so a deployment that answers 400 rather than 504 must still
        reach the narrowing ladder. The 400 text was not observed in any tenant
        tested, so the match is kept deliberately broad rather than pinned to a
        phrase; a 400 about any other parameter is left alone.
        """
        if self.is_timeout:
            return True
        if self.status_code != 400:
            return False
        return any(
            "time_range" in str(err.get("message", "")).lower() for err in self.errors
        )


# Default time window for inventory aggregation queries.
_INVENTORY_DEFAULT_LOOKBACK = "7d"

# Default window for LogScale-backed sub-queries. These endpoints default to 2h when
# the parameter is omitted, so internal fan-out legs state a window explicitly rather
# than inheriting a near-empty one.
_LOGSCALE_DEFAULT_LOOKBACK = "7d"

# Default window exposed on LogScale-backed tool parameters. Matches the API's own
# default, so a caller who does not choose a window gets the cheap query the server
# would have run anyway and widens it deliberately.
_LOGSCALE_TOOL_DEFAULT = "2h"

# Default window for detection queries.
_DETECTIONS_DEFAULT_LOOKBACK = "7d"


def _normalize_product_name(product: str) -> str:
    """Normalize a human-readable product name to the stored UPPER_SNAKE_CASE format.

    The AI agent inventory stores product names like "CLAUDE_CODE" rather than
    "Claude Code". This normalizes common variations.
    """
    if product == product.upper() and "_" in product:
        return product
    return product.strip().upper().replace(" ", "_").replace("-", "_")


def _as_int(value: Any) -> int:
    """Coerce an aggregate count to int, degrading to 0 rather than raising.

    Some aggregates return ``count`` as a JSON string ("7") and a malformed or
    absent value must not abort the whole rollup.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _tag_key(value: Any) -> str:
    """Render a product tag ID as a comparable string.

    Both sides of the detections join and the agent/session rollups hold the
    same numeric product tag IDs, but they disagree on encoding: one side
    arrives as a JSON string (e.g. ``"213584428666221"``) and the other as a
    JSON int (e.g. the unattributed ``0``). Coercing both through ``str()``
    makes the two encodings comparable. A JSON int literal already decodes to
    ``int``, so no float or exponent form is involved; the ``float`` branch
    below is belt-and-suspenders for a value that somehow arrives as one.

    A ``None`` or absent value returns ``""``, which callers treat as "matches
    nothing" rather than as a key.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        # Whole-number floats render without a trailing ".0" or exponent.
        if value.is_integer():
            return str(int(value))
        return repr(value)
    return str(value)


def _is_unattributed_tag(value: Any) -> bool:
    """Whether a product tag means "could not be attributed to a product".

    The detection endpoints disagree on how they encode this:
    ``queries/detections`` returns a real ``null`` while
    ``aggregates/detections`` returns ``0``. Neither is a member of the product
    taxonomy: every observed tag is a 15-digit value (for example
    ``213584428666201``), so both encodings are treated as absent.

    Written against the concept rather than either specific encoding so a
    subsequent model change cannot silently reintroduce the mismatch.
    """
    if value is None or value == "":
        return True
    try:
        return int(value) == 0
    except (TypeError, ValueError):
        return False


class GuardianModule(BaseModule):
    """Module for querying AI agent activity and inventory via the Guardian API."""

    def _plan(
        self, route: str, params: dict[str, Any] | None
    ) -> tuple[dict[str, Any], list[str], str | None, list[str]]:
        """Prepare one request: drop Nones, fit the window, and pick retry rungs.

        Returns (params, notices, effective_window, narrowing_rungs). Split out so
        the sync and async drivers share every decision and only differ in how they
        await the HTTP call.
        """
        prepared = {k: v for k, v in (params or {}).items() if v is not None}

        notices: list[str] = []
        effective, clamp_notice = _clamp_time_range(route, prepared.get("time_range"))
        if clamp_notice:
            notices.append(clamp_notice)
        if effective is None:
            prepared.pop("time_range", None)
        else:
            prepared["time_range"] = effective

        rungs = _narrowing_rungs(effective) if effective is not None else []
        return prepared, notices, effective, rungs

    def _query(
        self, route: str, params: dict[str, Any] | None = None
    ) -> GuardianResponse:
        """Run one /aidr query, narrowing the window if the API refuses it.

        Every route (/aidr/queries/*, /aidr/entities/*, /aidr/aggregates/*) is
        reached with `override=` under the single `aidr_events_query` label and needs
        the AIDR:read scope, so all tools funnel through here.

        Blocking by design: `BaseModule._add_tool` offloads sync tool handlers to a
        worker thread, so the event loop stays free without this being async.

        Keep the retry ladder in sync with `_query_async`.
        """
        prepared, notices, effective, rungs = self._plan(route, params)
        bad_unit = _bad_time_range_unit(prepared.get("time_range"))
        if bad_unit is not None:
            return self._bad_time_range_response(bad_unit, notices)
        deadline = time.monotonic() + _LADDER_BUDGET_SECONDS

        response = self._request_once(route, prepared)
        if response.rejects_window and effective is not None:
            attempted = response
            ladder_notice = self._exhausted_notice(rungs)
            for rung in rungs:
                if time.monotonic() >= deadline:
                    ladder_notice = self._budget_notice()
                    break
                attempted = self._request_once(route, dict(prepared, time_range=rung))
                if not attempted.rejects_window:
                    ladder_notice = self._narrowed_notice(effective, rung)
                    break
            response = attempted
            notices.append(ladder_notice)

        response.notices = notices + response.notices
        return response

    async def _query_async(
        self, route: str, params: dict[str, Any] | None = None
    ) -> GuardianResponse:
        """Async twin of `_query`, for fan-out legs run under `asyncio.gather`.

        Awaits `FalconClient.command_async`, which offloads onto the *same* anyio
        thread pool as the sync path — so both share one 40-token limiter and one
        token-refresh lock. Only the six fan-out tools use this; every other tool is
        sync (see the module's tool handlers).

        Keep the retry ladder in sync with `_query`.
        """
        prepared, notices, effective, rungs = self._plan(route, params)
        bad_unit = _bad_time_range_unit(prepared.get("time_range"))
        if bad_unit is not None:
            return self._bad_time_range_response(bad_unit, notices)
        deadline = time.monotonic() + _LADDER_BUDGET_SECONDS

        response = await self._request_once_async(route, prepared)
        if response.rejects_window and effective is not None:
            attempted: GuardianResponse = response
            ladder_notice = self._exhausted_notice(rungs)
            for rung in rungs:
                if time.monotonic() >= deadline:
                    ladder_notice = self._budget_notice()
                    break
                attempted = await self._request_once_async(
                    route, dict(prepared, time_range=rung)
                )
                if not attempted.rejects_window:
                    ladder_notice = self._narrowed_notice(effective, rung)
                    break
            response = attempted
            notices.append(ladder_notice)

        response.notices = notices + response.notices
        return response

    @staticmethod
    def _budget_notice() -> str:
        return (
            f"Stopped narrowing the window after {_LADDER_BUDGET_SECONDS}s so the call "
            f"returns before the MCP client times out. Retry with a smaller time_range."
        )

    @staticmethod
    def _bad_time_range_response(unit: str, notices: list[str]) -> "GuardianResponse":
        """Synthetic 400 for a time_range unit the API rejects.

        Answers before the request so the caller gets the real cause — use hours
        or days — instead of a 400 that trips the narrowing ladder and returns a
        misleading add-a-filter notice.
        """
        return GuardianResponse(
            errors=[
                {
                    "message": (
                        f"invalid time_range unit: {unit!r}; "
                        f"supported: {_SUPPORTED_TIME_RANGE_UNITS}"
                    )
                }
            ],
            status_code=400,
            notices=notices,
        )

    @staticmethod
    def _narrowed_notice(effective: str, rung: str) -> str:
        return (
            f"The API refused the {effective} window; results are from a narrower "
            f"{rung} window instead. Counts cover {rung}, not the window you asked for."
        )

    @staticmethod
    def _exhausted_notice(rungs: list[str]) -> str:
        """Notice when the window was refused and no narrower rung succeeded.

        ``rungs`` is the set actually attempted, so the text names the narrowest
        window really tried instead of a hardcoded ladder rung. When no rung was
        narrower than the request (``rungs`` empty), nothing was retried, so say
        that plainly rather than claiming a window that was never sent.
        """
        if rungs:
            return (
                f"The API refused every window down to {rungs[-1]}. Add a "
                f"filter (aid, product, or session_id) to narrow the query instead of "
                f"widening time."
            )
        return (
            "The API refused this time window and no narrower one was available "
            "to retry. Add a filter (aid, product, or session_id) to narrow the "
            "query instead of widening time."
        )

    def _request_once(self, route: str, params: dict[str, Any]) -> GuardianResponse:
        """Issue exactly one GET against an /aidr route and parse the envelope."""
        logger.debug("Guardian GET %s params=%s", route, params)
        # FalconClient.command, not the raw APIHarnessV2: the wrapper collapses
        # concurrent stale-token refreshes behind a single lock.
        response = self.client.command(
            _AIDR_OPERATION, override=f"GET,{route}", parameters=params
        )
        return self._parse_response(response, route)

    async def _request_once_async(
        self, route: str, params: dict[str, Any]
    ) -> GuardianResponse:
        """Async twin of `_request_once`; see `_query_async` for why it exists."""
        logger.debug("Guardian GET %s params=%s", route, params)
        response = await self.client.command_async(
            _AIDR_OPERATION, override=f"GET,{route}", parameters=params
        )
        return self._parse_response(response, route)

    async def _offload(self, method: Any, **kwargs: Any) -> Any:
        """Call a sync tool handler from an async one without blocking the loop.

        `generate_guardian_report` composes other Guardian tools. Most of them are sync, and
        calling one inline from a coroutine would block the event loop for the whole
        Falcon round trip. Routing through anyio's thread pool keeps the loop free and
        keeps the call inside the same 40-token limiter as every other Falcon request.

        This is not `base.offload_to_thread`: that decorator wraps a whole handler once
        at registration time, while this forwards keyword arguments to an ad-hoc
        internal call. Both end up on the same anyio pool.
        """
        return await anyio.to_thread.run_sync(partial(method, **kwargs))

    def _parse_response(
        self, response: dict[str, Any], route: str
    ) -> GuardianResponse:
        """Turn a FalconPy envelope into a GuardianResponse.

        FalconPy returns {"status_code": int, "headers": {...}, "body": {...}}.
        """
        status_code = response.get("status_code", 500)

        if status_code != 200:
            body = response.get("body", {})
            errors_list = body.get("errors", []) if isinstance(body, dict) else []

            # Prefer the API's own message — it names the offending parameter or
            # explains the timeout, which a generic status line cannot.
            api_messages = [
                e["message"]
                for e in errors_list
                if isinstance(e, dict) and e.get("message")
            ]
            error_msg = (
                "; ".join(api_messages) or f"Guardian API returned HTTP {status_code}"
            )

            if errors_list:
                logger.error(
                    "Guardian API request failed: route=%s status=%d errors=%s",
                    route,
                    status_code,
                    errors_list,
                )
            else:
                logger.error(
                    "Guardian API request failed: route=%s status=%d",
                    route,
                    status_code,
                )

            error_entry: dict[str, Any] = {
                "message": error_msg,
                "status_code": status_code,
            }
            if errors_list:
                error_entry["api_errors"] = errors_list
            if status_code == 403:
                error_entry["required_scopes"] = ["AIDR:read"]
                error_entry["resolution"] = (
                    "This operation requires the AIDR:read API scope. Ensure your API "
                    "client has been granted it in the CrowdStrike Falcon console."
                )
            return GuardianResponse(
                resources=[], errors=[error_entry], status_code=status_code
            )

        body = response.get("body", {})
        if not isinstance(body, dict):
            return GuardianResponse(resources=[], errors=[], status_code=status_code)

        resources = body.get("resources", []) or []
        errors = body.get("errors", []) or []

        notices: list[str] = []
        if "/aggregates/" in route and len(resources) == _AGGREGATE_GROUP_LIMIT:
            notices.append(
                f"Aggregate returned exactly {_AGGREGATE_GROUP_LIMIT} groups, the "
                f"server-side maximum, and these routes do not paginate. Results are "
                f"likely truncated — narrow with aid, product, or a shorter time_range."
            )

        return GuardianResponse(
            resources=resources,
            errors=errors,
            status_code=status_code,
            notices=notices,
            pagination=self._extract_pagination(response),
        )

    def register_tools(self, server: FastMCP) -> None:
        """Register Guardian tools with the MCP server."""
        self._add_tool(server=server, method=self.search_guardian_agents, name="search_guardian_agents")
        self._add_tool(server=server, method=self.get_guardian_agent, name="get_guardian_agent")
        self._add_tool(
            server=server, method=self.search_guardian_mcp_servers, name="search_guardian_mcp_servers"
        )
        self._add_tool(server=server, method=self.get_guardian_agent_sessions, name="get_guardian_agent_sessions")
        self._add_tool(
            server=server, method=self.get_guardian_session_detail, name="get_guardian_session_detail"
        )
        self._add_tool(
            server=server, method=self.get_guardian_session_activity, name="get_guardian_session_activity"
        )
        self._add_tool(server=server, method=self.search_guardian_tools, name="search_guardian_tools")
        self._add_tool(server=server, method=self.search_guardian_tool_usage, name="search_guardian_tool_usage")
        self._add_tool(server=server, method=self.search_guardian_executions, name="search_guardian_executions")
        self._add_tool(server=server, method=self.search_guardian_prompts, name="search_guardian_prompts")
        self._add_tool(server=server, method=self.get_guardian_inventory, name="get_guardian_inventory")
        self._add_tool(server=server, method=self.search_guardian_skills, name="search_guardian_skills")
        self._add_tool(
            server=server, method=self.search_guardian_skill_usage, name="search_guardian_skill_usage"
        )
        self._add_tool(
            server=server, method=self.get_guardian_fleet_skill_inventory, name="get_guardian_fleet_skill_inventory"
        )
        self._add_tool(server=server, method=self.search_guardian_os_users, name="search_guardian_os_users")
        self._add_tool(
            server=server, method=self.pivot_on_guardian_attribute, name="pivot_on_guardian_attribute"
        )
        self._add_tool(server=server, method=self.get_guardian_process_tree, name="get_guardian_process_tree")
        self._add_tool(server=server, method=self.get_guardian_network_events, name="get_guardian_network_events")
        self._add_tool(server=server, method=self.get_guardian_file_events, name="get_guardian_file_events")
        self._add_tool(
            server=server, method=self.get_guardian_classified_file_access, name="get_guardian_classified_file_access"
        )
        self._add_tool(server=server, method=self.generate_guardian_report, name="generate_guardian_report")
        self._add_tool(
            server=server, method=self.search_guardian_detections, name="search_guardian_detections"
        )
        self._add_tool(
            server=server, method=self.get_guardian_detection_scores, name="get_guardian_detection_scores"
        )
        self._add_tool(
            server=server, method=self.search_guardian_installs, name="search_guardian_installs"
        )
        self._add_tool(server=server, method=self.search_guardian_models, name="search_guardian_models")

    def register_resources(self, server: FastMCP) -> None:
        """Register Guardian resources with the MCP server."""
        query_guide_resource = TextResource(
            uri=AnyUrl("falcon://guardian/events/query-guide"),
            name="falcon_guardian_query_guide",
            description="Guardian API reference for the AI entity and LogScale event query endpoints. Use this when choosing endpoints and parameters for the Guardian tools.",
            text=QUERY_GUIDE_DOCUMENTATION,
        )
        self._add_resource(server, query_guide_resource)

        schema_resource = TextResource(
            uri=AnyUrl("falcon://guardian/entities/schema-guide"),
            name="falcon_guardian_entity_schema",
            description="AI vertex and edge field reference. Shows available fields for AIAgent, AISession, AITool, AIModel, AISkill, MCPServer, AIPrompt entities.",
            text=ENTITY_SCHEMA_DOCUMENTATION,
        )
        self._add_resource(server, schema_resource)

        inventory_schema_resource = TextResource(
            uri=AnyUrl("falcon://guardian/inventory/schema-guide"),
            name="falcon_guardian_inventory_schema",
            description="AI entity and LogScale event field reference. Shows available fields for the AIAgent/AIAgentSession/AITool/AISkillFrontmatter/MCPServerName/AIAgentInstallation/AIModelName/AIAgentOSUser entity store and the LogScale AgenticSessionStart/AgenticToolRequest/AgenticUserPromptSubmit events.",
            text=AGENTIC_INVENTORY_SCHEMA_DOCUMENTATION,
        )
        self._add_resource(server, inventory_schema_resource)

        examples_resource = TextResource(
            uri=AnyUrl("falcon://guardian/events/examples-guide"),
            name="falcon_guardian_example_queries",
            description="Example Guardian queries for common AI activity questions. Reference these when choosing Guardian tools and parameters.",
            text=EXAMPLE_QUERIES_DOCUMENTATION,
        )
        self._add_resource(server, examples_resource)

    # --- Inventory Tools ---

    def search_guardian_agents(
        self,
        product: str | None = Field(
            default=None,
            description="Filter by AI product name (e.g., 'CLAUDE_CODE', 'CURSOR'). Human-readable names are auto-normalized.",
        ),
        hostname: str | None = Field(
            default=None,
            description="Filter by hostname of the device running the agent.",
        ),
        time_range: str = Field(
            default="7d",
            description="Lookback window (e.g., '1h', '24h', '7d', '30d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI agents from the AIAgent entity store.

        Use this to find agents by product or hostname. Returns full agent
        records, including the opaque record token `Id` (pass to
        get_guardian_agent), the 32-hex `SensorId` (`== aid`, identifies the
        HOST), and the `AgentIds[]` content hash(es) (width varies). See
        falcon://guardian/inventory/schema-guide for the full field reference
        and the `Id` vs `SensorId` vs `AgentIds` distinction.
        """
        product = unwrap_field_default(product)
        hostname = unwrap_field_default(hostname)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        if product:
            product = _normalize_product_name(product)

        response = self._query(_AGENTS_QUERY_ROUTE, {
            "product": product,
            "hostname": hostname,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    async def get_guardian_agent(
        self,
        agent_id: str = Field(
            description="The AIAgent Id (the opaque record token from a search result's `Id` field, e.g. 'ASCWQseSk3b76g...'), NOT the 32-hex SensorId and NOT the AgentIds[] content-hash value.",
        ),
    ) -> dict[str, Any]:
        """Get a specific AI agent's record from the AIAgent entity store.

        Use when you have an AIAgent `Id` (the opaque record token from a
        search result, not the 32-hex `SensorId`/`aid` and not the
        `AgentIds[]` content-hash value) and want the full agent record. The record carries
        `SensorId`, which the host-scoped follow-up tools
        (get_guardian_agent_sessions, search_guardian_tools,
        search_guardian_tool_usage, search_guardian_detections) take as
        `aid`/`sensor_id`. For a one-shot overview of every facet, use
        generate_guardian_report with report_type='agent_detail'. For
        discovering agents by criteria, use search_guardian_agents instead.
        """
        sanitize_guardian_value(agent_id)

        instance_resp = await self._query_async(
            _AGENTS_ENTITIES_ROUTE,
            {"ids": agent_id},
        )

        if not instance_resp.ok:
            return {"error": instance_resp.errors}
        if instance_resp.count == 0:
            return {"error": f"No agent found with agent_id: {agent_id}"}

        return instance_resp.resources[0]

    async def _agent_profile(self, agent_id: str) -> dict[str, Any]:
        """Full agent fan-out: verify the agent, then gather its activity.

        Backs the ``agent_detail`` report, where a one-shot overview is worth the
        several backend queries. The standalone get_guardian_agent tool no longer
        fans out (see that method).

        Every leg is HOST-scoped by ``SensorId`` (`aid`), and that matters when
        reporting a count: a host usually runs several AI agents, so every number
        here covers all of them, not just the requested agent. Nothing in the
        reshaped API can scope these to one agent — the entities carry no agent
        filter and no longer return any reverse-relationship array, so a
        client-side join has nothing to join on.

        ``tools`` is the thinnest leg by far. The AITool store covers few hosts, so
        it is empty for most agents; ``tool_usage`` answers the same question from
        the event side and is far better populated.

        There is no ``sessions`` leg — the agent-sessions route has no host filter,
        and ``executions`` (keyed by `aid`, carrying ``AgenticSessionId``) already
        covers the host's sessions.

        The LogScale legs state 7d explicitly — the server default is 2h, which
        would make an idle-for-2h agent look empty.
        """
        sanitize_guardian_value(agent_id)

        instance_resp = await self._query_async(
            _AGENTS_ENTITIES_ROUTE,
            {"ids": agent_id},
        )
        if not instance_resp.ok:
            return {"error": instance_resp.errors}
        if instance_resp.count == 0:
            return {"error": f"No agent found with agent_id: {agent_id}"}

        agent = instance_resp.resources[0]
        aid = agent.get("SensorId", "")

        if aid:
            (
                tools_resp,
                executions_resp,
                tool_usage_resp,
                skill_usage_resp,
                detections_resp,
                detection_score_resp,
            ) = await asyncio.gather(
                self._query_async(
                    _TOOLS_QUERY_ROUTE,
                    {"sensor_id": aid, "time_range": _LOGSCALE_DEFAULT_LOOKBACK, "limit": 100},
                ),
                # Executions are the host-scoped session grain: keyed by aid and
                # carrying AgenticSessionId, so this covers the host's sessions.
                # (The agent-sessions entity has no host filter, so it cannot be
                # scoped to this agent's host.)
                self._query_async(
                    _EXECUTIONS_QUERY_ROUTE,
                    {"aid": aid, "time_range": _LOGSCALE_DEFAULT_LOOKBACK, "limit": 100},
                ),
                self._query_async(
                    _TOOL_USAGE_QUERY_ROUTE,
                    {"aid": aid, "time_range": _LOGSCALE_DEFAULT_LOOKBACK, "limit": 100},
                ),
                self._query_async(
                    _SKILL_USAGE_QUERY_ROUTE,
                    {"aid": aid, "time_range": _LOGSCALE_DEFAULT_LOOKBACK, "limit": 100},
                ),
                # Detections are alert-backed and keyed by sensor ID despite the
                # parameter being named agent_id.
                self._query_async(
                    _DETECTIONS_QUERY_ROUTE,
                    {
                        "agent_id": aid,
                        "time_range": _DETECTIONS_DEFAULT_LOOKBACK,
                        "limit": 50,
                    },
                ),
                self._query_async(
                    _DETECTIONS_AGGREGATES_ROUTE,
                    {"agent_id": aid, "time_range": _DETECTIONS_DEFAULT_LOOKBACK},
                ),
            )
        else:
            # Without an aid every leg would go out unfiltered and return
            # fleet-wide activity under an agent-scoped key, so report that
            # instead. That now includes `tools`: since the API stopped returning
            # UsedByAIAgents[], `sensor_id` is its only scope.
            missing = self._missing_aid_response()
            tools_resp = missing
            executions_resp = tool_usage_resp = skill_usage_resp = missing
            detections_resp = detection_score_resp = missing

        return {
            "instance": agent,
            "tools": self._sub_result(tools_resp, 50),
            "executions": self._sub_result(executions_resp, 100),
            "tool_usage": self._sub_result(tool_usage_resp, 100),
            "skill_usage": self._sub_result(skill_usage_resp, 100),
            "detections": self._sub_result(detections_resp, 50),
            "max_detection_score": self._pick_detection_score(
                detection_score_resp, aid, agent.get("AgentProduct")
            ),
        }

    def get_guardian_agent_sessions(
        self,
        product: str | None = Field(
            default=None,
            description="Filter by AI product name (e.g., 'CLAUDE_CODE', 'CURSOR'). Human-readable names are auto-normalized.",
        ),
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI agent sessions across the fleet, filtered by product.

        These rows cannot be tied to one agent or host. The AIAgentSession entity
        offers no agent or host filter, its `SensorId` and `AIAgentIds` are never
        populated upstream, and nothing on a session points back to the agent that
        ran it. Two questions therefore have no answer here: how many sessions a
        single agent had, and which agents ran the most. `Product` names the
        software rather than an agent, and many agents share a product, so
        grouping these rows by `Product` counts products.

        Returns session records carrying `Id`, `Product` (with a friendly
        `ProductName`), `Name`, the seen timestamps, and a nested
        `Cim.AIAgentSession` holding `sessionId`, `modelsInvoked` and
        `workingDirectory`; see falcon://guardian/inventory/schema-guide for the
        full field reference. The result also carries `notices` if the requested
        window had to be narrowed.

        For a single host, use search_guardian_executions(aid=...) — the
        host-scoped session grain, which also reports the model and token counts
        for each process. For a ready-made count by product, use
        `sessions.by_product` from get_guardian_inventory.
        """
        product = unwrap_field_default(product)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        if product:
            product = _normalize_product_name(product)

        response = self._query(_AGENT_SESSIONS_QUERY_ROUTE, {
            "product": product,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        result = self._format_response(response, limit=limit)
        # The scope warning has to be the FIRST key, not appended. Measured live:
        # when the caller raises `limit` to count rows, the envelope exceeds the
        # client's tool-output budget and is persisted to a file, of which only a
        # ~2KB preview reaches the model. Appended, the note sits ~240KB deep and
        # is never read; first, it lands inside that preview and survives the
        # spill. The rows themselves invite two wrong counts, so the note names
        # both and gives the query that answers each. Success envelope only — an
        # error dict carries no rows to misread.
        if isinstance(result, dict) and "results" in result:
            result = {
                "note": (
                    "These rows are fleet-wide and cannot be tied to one agent or "
                    "host, because this entity has no agent or host filter. So two "
                    "counts are not derivable here: a single agent's session total "
                    "(use search_guardian_executions(aid=...), the host-scoped "
                    "session grain) and a per-agent ranking, which does not exist "
                    "anywhere in this API. `Product` names the software and many "
                    "agents share a product, so grouping these rows by "
                    "`Product`/`ProductName` counts products rather than agents; "
                    "for a ready-made product rollup use `sessions.by_product` "
                    "from get_guardian_inventory."
                ),
                **result,
            }
        return result

    async def get_guardian_session_detail(
        self,
        session_id: str = Field(
            description="The AgenticSessionId (UUID) of the session to get details for.",
        ),
        include_activity: bool = Field(
            default=True,
            description="If true (default), also fetches the graph activity (tools, skills, processes, models, MCP servers) for this session.",
        ),
    ) -> dict[str, Any]:
        """Get detailed information about a specific AI session.

        Use when you have an AgenticSessionId (UUID) and need full context. For
        discovering sessions by criteria, use get_guardian_agent_sessions
        instead. Returns the session's process executions plus the
        per-invocation tools and skills used. When `include_activity` is true,
        also returns the threat-graph activity (which adds processes, models,
        MCP servers, and child sessions as edges).
        """
        include_activity = unwrap_field_default(include_activity)
        sanitize_guardian_value(session_id)

        # The AgenticSessionId keys the executions entity directly, and (via
        # server-side vertex resolution) the session-activity graph. It is the
        # verification path — the old entities/sessions lookup keyed on the
        # AIAgentSession entity Id, not the UUID.
        exec_resp = await self._query_async(
            _EXECUTIONS_ENTITIES_ROUTE,
            {"id": session_id},
        )

        if not exec_resp.ok:
            return {"error": exec_resp.errors}

        if exec_resp.count == 0:
            return {"error": f"No session found with session_id: {session_id}"}

        # Per-invocation tools and skills are session-scoped on the LogScale usage
        # endpoints. Both legs state the window explicitly (the API defaults these
        # to 2h), so an older session still returns its activity.
        (
            tools_resp,
            skills_resp,
        ) = await asyncio.gather(
            self._query_async(_TOOL_USAGE_QUERY_ROUTE, {
                "session_id": session_id,
                "time_range": _LOGSCALE_DEFAULT_LOOKBACK,
                "limit": 100,
            }),
            self._query_async(_SKILL_USAGE_QUERY_ROUTE, {
                "session_id": session_id,
                "time_range": _LOGSCALE_DEFAULT_LOOKBACK,
                "limit": 100,
            }),
        )

        result: dict[str, Any] = {
            "executions": exec_resp.resources,
            "tools": tools_resp.resources,
            "skills": skills_resp.resources,
        }

        # The activity graph carries the same relationships plus processes,
        # models, MCP servers, and child sessions as edges; the server resolves
        # the UUID to its vertex key, so the raw session_id is accepted directly.
        if include_activity:
            result["activity"] = await self._get_graph_activity(session_id)

        return result

    def get_guardian_session_activity(
        self,
        session_id: str = Field(
            description="Vertex ID (aisess:{aid}:{uuid}) or inventory AgenticSessionId (UUID). Comma-separated vertex IDs accepted.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get activity for one or more AI sessions.

        Use this to see full graph relationships including tools, models, processes,
        sub-agents, and MCP servers. Accepts vertex IDs or inventory session IDs.
        Returns session activity with all connected graph entities.
        """
        # Parse comma-separated IDs
        ids = [v.strip() for v in session_id.split(",") if v.strip()]

        if not ids:
            return {"error": "No valid session IDs provided", "session_id": session_id}

        response = self._query(_SESSION_ACTIVITY_ROUTE, {"ids": ids})

        if not response.ok:
            return {"error": response.errors, "session_id": session_id}
        if response.count == 0:
            return {"error": f"No session(s) found for: {session_id}", "session_id": session_id}

        if len(ids) == 1:
            return response.resources[0]
        return response.resources

    def search_guardian_tools(
        self,
        sensor_id: str | None = Field(
            default=None,
            description="Filter by the tool's own host sensor ID (32-hex aid / AIAgent.SensorId). This identifies a host, so it returns the tools of every agent on that host rather than one agent's. The store is thinly populated, so an agent's SensorId often matches nothing; search_guardian_tool_usage(aid=...) covers the same host from the event side.",
        ),
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI tools from the AITool entity store — the inventory of which tools exist.

        Use this to see what tools are present. A tool cannot be attributed to a
        single agent: rows are flat (`Id`, `Name`, `SensorId`, the seen
        timestamps) and there is no per-agent filter, so `sensor_id` narrows to
        the tool's host, which covers every agent on it. Coverage is also thin —
        the store spans few hosts, so most agents match nothing here. For the
        tools an agent's host actually invoked, prefer
        search_guardian_tool_usage(aid=...), which also carries file paths and
        command lines.
        """
        sensor_id = unwrap_field_default(sensor_id)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_TOOLS_QUERY_ROUTE, {
            "sensor_id": sensor_id,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_tool_usage(
        self,
        tool_name: str | None = Field(
            default=None,
            description="Filter by tool name. Exact and case-sensitive, not a substring or a wildcard. Use the spelling the event store uses ('Bash', 'Read', 'Edit', 'Grep', or lowercase names such as 'apply_diff'), because the inventory can differ: search_guardian_tools and get_guardian_inventory's tools.by_name list 'bash' where these events carry 'Bash'. A mismatched case returns zero rows rather than an error, so an empty result does not prove the tool was never used — try the other capitalization before reporting a zero.",
        ),
        aid: str | None = Field(
            default=None,
            description="Filter by sensor ID (aid) — identifies a HOST, not a single agent.",
        ),
        session_id: str | None = Field(
            default=None,
            description="Filter by AgenticSessionId.",
        ),
        time_range: str = Field(
            default=_LOGSCALE_TOOL_DEFAULT,
            description="Time range (e.g., '2h', '24h', '7d'). Defaults to '2h', matching the API — widen it explicitly to look further back, up to a 7-day maximum (this route scans raw events; a wider window is refused and narrowed back to 7d). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '2h'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI tool usage from LogScale AgenticToolRequest events.

        Use this to find tool invocations by name, sensor (aid), or session;
        the default window is 2 hours, so widen `time_range` explicitly for
        anything beyond current activity, up to the 7-day maximum this route
        allows (it scans raw LogScale events; a wider window is refused and the
        ladder narrows it back to 7d). Returns tool usage records
        (AgenticToolName, AgenticPath, CommandLine, aid). If the requested
        window had to be narrowed, the result is `{results, notices}` instead
        of a bare list; read `notices` before reporting counts.
        """
        session_id = unwrap_field_default(session_id)
        tool_name = unwrap_field_default(tool_name)
        aid = unwrap_field_default(aid)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_TOOL_USAGE_QUERY_ROUTE, {
            "tool_name": tool_name,
            "aid": aid,
            "session_id": session_id,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_executions(
        self,
        session_id: str | None = Field(
            default=None,
            description="Filter by AgenticSessionId (UUID).",
        ),
        aid: str | None = Field(
            default=None,
            description="Filter by sensor ID (aid). Identifies a HOST, not a single agent.",
        ),
        time_range: str = Field(
            default=_LOGSCALE_TOOL_DEFAULT,
            description="Time range (e.g., '2h', '24h', '7d'). Defaults to '2h', matching the API — widen it explicitly to look further back, up to a 7-day maximum (this route scans raw events; a wider window is refused and narrowed back to 7d). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '2h'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI agent process executions, with the model and token counts for each.

        This is the only Guardian tool that reports token usage
        (`AgenticInputTokens` / `AgenticOutputTokens`), so use it for any question
        about tokens consumed, model cost, or which model a process ran. It is
        backed by LogScale `AgenticSessionStart` events, so each row is one
        process a session spawned, carrying the model, the token counts, the
        working directory, a flat `AgenticSessionId` and the host `aid`. That also
        makes it the only way to see the sessions on a given host — pass `aid` —
        because the agent-sessions entity has no host filter at all. The default
        window is 2 hours, so widen `time_range` explicitly for older activity, up
        to the 7 days this route allows — it scans raw LogScale events, and a
        wider window is refused, after which the retry ladder narrows it back to
        7d and reports the change in `notices`.
        """
        session_id = unwrap_field_default(session_id)
        aid = unwrap_field_default(aid)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_EXECUTIONS_QUERY_ROUTE, {
            "session_id": session_id,
            "aid": aid,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_prompts(
        self,
        session_id: str = Field(
            description="AgenticSessionId to search prompts within.",
        ),
        aid: str | None = Field(
            default=None,
            description="Optional sensor ID (aid) filter — identifies a HOST, not a single agent.",
        ),
        time_range: str = Field(
            default=_LOGSCALE_TOOL_DEFAULT,
            description="Time range (e.g., '2h', '24h', '7d'). Defaults to '2h', matching the API — widen it explicitly for older prompts, up to a 7-day maximum (this route scans raw events; a wider window is refused and narrowed back to 7d). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '2h'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for AI prompts within a session (LogScale AgenticUserPromptSubmit).

        Use this to retrieve prompt content for a specific session; the
        default window is 2 hours, so widen `time_range` explicitly to reach
        older prompts, up to the 7-day maximum this route allows (it scans raw
        LogScale events; a wider window is refused and the ladder narrows it back
        to 7d). Returns prompt records including `AgenticPrompt`,
        `AgenticSessionId`, `aid`, and a `timestamp` that is epoch
        milliseconds encoded as a string — see
        falcon://guardian/inventory/schema-guide for the full field
        reference. If the requested window had to be narrowed, the result is
        `{results, notices}` instead of a bare list.
        """
        aid = unwrap_field_default(aid)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_PROMPTS_QUERY_ROUTE, {
            "session_id": session_id,
            "aid": aid,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_detections(
        self,
        agent_id: str | None = Field(
            default=None,
            description="Filter by the detection's AgentId. ⚠️ This takes a 32-hex SENSOR/host ID (AIAgent.SensorId / aid), NOT the 64-hex AIAgent.Id — the API parameter name is misleading.",
        ),
        product: str | None = Field(
            default=None,
            description="Filter by AI product name (e.g., 'Kiro', 'CLAUDE_CODE'). Human-readable names are auto-normalized.",
        ),
        time_range: str = Field(
            default=_DETECTIONS_DEFAULT_LOOKBACK,
            description="Time range (e.g., '1h', '24h', '7d'). Filters the detection Timestamp. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List detections involving AI agent processes.

        Use this to find security detections (alerts) that involved an AI
        agent; every row is agent-related, scoped server-side and not
        client-controllable. `agent_id` takes the 32-hex SENSOR/host ID
        (`== AIAgent.SensorId`/`aid`), NOT the 64-hex `AIAgent.Id` — passing
        the latter returns zero rows with no error, and because it identifies
        a host, a detection cannot be pinned to one agent on a multi-agent
        host. See falcon://guardian/events/query-guide for the full field
        reference and a `product` filter trap: it takes the product name,
        not the numeric tag value the API itself returns in responses.
        """
        agent_id = unwrap_field_default(agent_id)
        product = unwrap_field_default(product)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        if error := _reject_agent_ids_token(agent_id):
            return error

        if product:
            product = _normalize_product_name(product)

        response = self._query(_DETECTIONS_QUERY_ROUTE, {
            "agent_id": agent_id,
            "product": product,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def get_guardian_detection_scores(
        self,
        agent_id: str | None = Field(
            default=None,
            description="Filter by AgentId. ⚠️ A 32-hex SENSOR/host ID (AIAgent.SensorId / aid), NOT the 64-hex AIAgent.Id.",
        ),
        product: str | None = Field(
            default=None,
            description="Filter by AI product name (e.g., 'Kiro', 'CLAUDE_CODE'). Human-readable names are auto-normalized.",
        ),
        time_range: str = Field(
            default=_DETECTIONS_DEFAULT_LOOKBACK,
            description="Time range (e.g., '1h', '24h', '7d'). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get the Agentic Threat Score for each agent.

        Returns rows of `{AgentId, AgenticProductTag, maxDetectionScore}`.
        Joining these onto agents needs BOTH `AgentId == AIAgent.SensorId`
        AND `AgenticProductTag == AIAgent.Product`, because `AgentId`
        identifies a HOST and a host usually runs several AI agents; most
        rows leave the product tag unattributed, so an exact join resolves
        few agents (the agent_detail report handles that fallback and labels
        the result host-scoped). `offset` is silently ignored here and the
        grouping caps at 500 groups; see falcon://guardian/events/query-guide
        for the join details and read `notices` before treating this as
        fleet-complete.
        """
        agent_id = unwrap_field_default(agent_id)
        product = unwrap_field_default(product)
        time_range = unwrap_field_default(time_range)

        if error := _reject_agent_ids_token(agent_id):
            return error

        if product:
            product = _normalize_product_name(product)

        response = self._query(_DETECTIONS_AGGREGATES_ROUTE, {
            "agent_id": agent_id,
            "product": product,
            "time_range": time_range,
        })
        return self._format_response(response)

    def search_guardian_installs(
        self,
        sensor_id: str | None = Field(
            default=None,
            description="Filter by sensor ID (32-hex aid / AIAgent.SensorId).",
        ),
        product: str | None = Field(
            default=None,
            description="Filter by AI product name (e.g., 'Codex', 'CLAUDE_CODE'). Human-readable names are auto-normalized.",
        ),
        hostname: str | None = Field(
            default=None,
            description="Filter by hostname of the device the agent is installed on.",
        ),
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI agent installations (AIAgentInstallationView entity).

        Use this to find install records by sensor, product, or hostname.
        Returns `Id`, `SensorId`, `Hostname`, `AgentName`, `AgentProduct`,
        `AgentVersion`, `InstallSource`, `AgentDeclarationPath`, `BinaryPath`,
        `FileSha256`, `LastExecutionTime`, and the seen timestamps — see
        falcon://guardian/inventory/schema-guide for the full field reference.
        """
        sensor_id = unwrap_field_default(sensor_id)
        product = unwrap_field_default(product)
        hostname = unwrap_field_default(hostname)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        if product:
            product = _normalize_product_name(product)

        response = self._query(_AGENT_INSTALLATIONS_QUERY_ROUTE, {
            "sensor_id": sensor_id,
            "product": product,
            "hostname": hostname,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_models(
        self,
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI model names (AIModelName entity).

        Returns the human-friendly model name in `Cim.AIModelName.modelName`
        (the `Id` is only a hashed dedup key) and the seen timestamps. There is
        no name/product/sensor scalar to filter on, so the only server-side
        filter is `time_range` on LastSeen. For the model used per session,
        prefer get_guardian_agent_sessions (its
        `Cim.AIAgentSession.modelsInvoked`) or search_guardian_executions (its
        `AgenticModel`). This tool reports no usage volume — for per-process
        model plus token counts (`AgenticInputTokens`/`AgenticOutputTokens`), use
        search_guardian_executions.
        """
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_MODEL_NAMES_QUERY_ROUTE, {
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    async def get_guardian_inventory(
        self,
        time_range: str = Field(
            default=_INVENTORY_DEFAULT_LOOKBACK,
            description="Lookback window for the rollups (e.g., '24h', '7d'). Filters LastSeen (Timestamp for detections). Default: '7d'",
        ),
    ) -> dict[str, Any]:
        """Get a summary overview of AI activity in your environment.

        Use this for a high-level fleet snapshot: agent counts by product,
        session counts by product, top tools by name, and a detection summary.
        `agents.by_product` counts AGENTS while `sessions.by_product` counts
        logical AIAgentSession rows — different metrics, so do not relabel one
        as the other. Both product buckets are keyed by the friendly product
        name (e.g. "Claude Code") when the API resolves the tag, falling back to
        the numeric tag ID for unrecognized products. Read `notices` before
        reporting any count.
        """
        time_range = unwrap_field_default(time_range)

        (
            agents_resp,
            sessions_resp,
            tools_resp,
            detections_resp,
        ) = await asyncio.gather(
            self._query_async(_AGENTS_AGGREGATES_ROUTE, {"time_range": time_range}),
            self._query_async(
                _AGENT_SESSIONS_AGGREGATES_ROUTE, {"time_range": time_range}
            ),
            self._query_async(
                _TOOLS_AGGREGATES_ROUTE, {"time_range": time_range, "limit": 100}
            ),
            self._query_async(
                _DETECTIONS_AGGREGATES_ROUTE, {"time_range": time_range}
            ),
        )

        # Agent rollup by product. The API decorates each bucket with a friendly
        # AgentProductName; prefer it and fall back to the numeric tag (keyed via
        # _tag_key so a string-encoded tag and an int-encoded one collapse to the
        # same bucket) for products it cannot resolve.
        # Counts arrive as JSON strings on some aggregates, so every one goes
        # through _as_int.
        agents_by_product: dict[str, int] = {}
        total_agents = 0
        for r in agents_resp.resources:
            product = r.get("AgentProductName") or _tag_key(r.get("AgentProduct")) or "unknown"
            count = _as_int(r.get("count", r.get("_count", 0)))
            agents_by_product[product] = count
            total_agents += count

        # Session rollup by product. The AIAgentSession aggregate groups by
        # Product, decorated with a friendly ProductName; prefer it and fall back
        # to the numeric tag. count arrives as a JSON string here.
        sessions_by_product: dict[str, int] = {}
        total_sessions = 0
        for r in sessions_resp.resources:
            product = r.get("ProductName") or _tag_key(r.get("Product")) or "unknown"
            count = _as_int(r.get("count", r.get("_count", 0)))
            sessions_by_product[product] = count
            total_sessions += count

        tools_by_name = {}
        for r in tools_resp.resources:
            name = r.get("Name", "unknown")
            tools_by_name[name] = _as_int(r.get("count", r.get("_count", 0)))

        # Detection rollup. Rows whose product tag is absent cannot be attributed
        # to an agent, so they are counted separately rather than dropped silently.
        scored_hosts: set[str] = set()
        max_score = 0
        unattributed_rows = 0
        for r in detections_resp.resources:
            host = r.get("AgentId")
            if host:
                scored_hosts.add(host)
            if _is_unattributed_tag(r.get("AgenticProductTag")):
                unattributed_rows += 1
            max_score = max(max_score, _as_int(r.get("maxDetectionScore")))

        result: dict[str, Any] = {
            "agents": {
                "total": total_agents,
                "by_product": agents_by_product,
                "window": time_range,
            },
            "sessions": {
                "by_product": sessions_by_product,
                "total": total_sessions,
                "products_reporting": len(sessions_by_product),
                "window": time_range,
                "truncated": len(sessions_resp.resources) >= _AGGREGATE_GROUP_LIMIT,
                "note": (
                    "Keyed by product name (numeric tag ID for products the API "
                    "cannot resolve). This counts logical AIAgentSession rows per "
                    "product; agents.by_product counts agents, which is a "
                    "different metric."
                ),
            },
            "tools": {
                "by_name": tools_by_name,
            },
            "detections": {
                "hosts_with_detections": len(scored_hosts),
                "max_score": max_score,
                "unattributed_rows": unattributed_rows,
                "truncated": len(detections_resp.resources) >= _AGGREGATE_GROUP_LIMIT,
                "window": time_range,
            },
        }

        notices = (
            agents_resp.notices
            + sessions_resp.notices
            + tools_resp.notices
            + detections_resp.notices
        )
        if notices:
            result["notices"] = notices
        return result

    def search_guardian_skills(
        self,
        name_filter: str | None = Field(
            default=None,
            description="Filter skills by name pattern (supports wildcards via 'like').",
        ),
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List AI skill frontmatters (AISkillFrontmatterView entity).

        Use this for the fleet-wide inventory of skills. Each row carries
        `SkillName`, `SkillDescription`, and the seen timestamps; the endpoint
        has no agent_id filter. For per-invocation skill events, use
        search_guardian_skill_usage instead.
        """
        name_filter = unwrap_field_default(name_filter)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_SKILLS_QUERY_ROUTE, {
            "name_filter": name_filter,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_skill_usage(
        self,
        name: str | None = Field(
            default=None,
            description="Filter by skill name. Exact and case-sensitive, not a substring or a wildcard — a wrong name returns zero rows rather than an error. Take the name verbatim from search_guardian_skills or get_guardian_fleet_skill_inventory. Most skills have no events in the default 2h window, so widen `time_range` before concluding a skill was never used.",
        ),
        session_id: str | None = Field(
            default=None,
            description="Filter by AgenticSessionId.",
        ),
        aid: str | None = Field(
            default=None,
            description="Filter by sensor ID (aid) — identifies a HOST, not a single agent.",
        ),
        time_range: str = Field(
            default=_LOGSCALE_TOOL_DEFAULT,
            description="Time range (e.g., '2h', '24h', '7d'). Defaults to '2h', matching the API — widen it explicitly to look further back, up to a 7-day maximum (this route scans raw events; a wider window is refused and narrowed back to 7d). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '2h'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List per-invocation AI skill events (LogScale AgenticToolRequest).

        Use this for the session-scoped grain of skill invocations
        (`AgenticSkill`, `AgenticSessionId`, `aid`), distinct from the
        AISkillFrontmatter inventory (search_guardian_skills). The default
        window is 2 hours, so widen `time_range` explicitly for older activity,
        up to the 7-day maximum this route allows (it scans raw LogScale events;
        a wider window is refused and the ladder narrows it back to 7d).
        """
        name = unwrap_field_default(name)
        session_id = unwrap_field_default(session_id)
        aid = unwrap_field_default(aid)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_SKILL_USAGE_QUERY_ROUTE, {
            "name": name,
            "session_id": session_id,
            "aid": aid,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def get_guardian_fleet_skill_inventory(
        self,
        name_filter: str | None = Field(
            default=None,
            description="Filter skills by name pattern (supports wildcards via 'like').",
        ),
        time_range: str = Field(
            default="7d",
            description="Lookback window (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get a fleet-wide skill usage rollup by name (AISkill aggregate).

        Use this to see which skills are most used, optionally filtered by name
        pattern. Returns grouped `{SkillName, count}` buckets. This is an
        aggregate with no server-side pagination; `limit` is applied
        client-side. For the per-skill records, use search_guardian_skills
        instead.
        """
        name_filter = unwrap_field_default(name_filter)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)

        response = self._query(_SKILLS_AGGREGATES_ROUTE, {
            "name_filter": name_filter,
            "time_range": time_range,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_os_users(
        self,
        aid: str | None = Field(
            default=None,
            description="Filter by the OS user's sensor ID (aid).",
        ),
        username: str | None = Field(
            default=None,
            description="Filter by OS username.",
        ),
        object_sid: str | None = Field(
            default=None,
            description="Filter by the OS user's ObjectSid (AD security identifier).",
        ),
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List OS users that have run AI agents (AIAgentOSUser entity).

        Use this to find which OS accounts ran agents, by sensor, username, or
        AD ObjectSid.
        """
        aid = unwrap_field_default(aid)
        username = unwrap_field_default(username)
        object_sid = unwrap_field_default(object_sid)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_AGENT_OS_USERS_QUERY_ROUTE, {
            "aid": aid,
            "username": username,
            "object_sid": object_sid,
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    def search_guardian_mcp_servers(
        self,
        time_range: str = Field(
            default="7d",
            description="Time range (e.g., '24h', '7d'). Filters LastSeen. Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Index of the first record to return, for paging. Pair with `limit`; read `pagination` in the response to page. The API refuses an offset above 1000 — narrow `time_range` instead of paging deeper.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List MCP server names observed across the fleet (MCPServerName entity).

        Use this to see which MCP servers agents have connected to. The
        human-friendly server name lives in `Cim.MCPServerName.serverName` (the
        `Id` is only a hashed dedup key). The endpoint carries no agent/sensor
        filter, so this is fleet-wide. To see which MCP servers a single session
        connected to, use get_guardian_session_detail (its activity graph
        exposes them under `ConnectedMcpMcpsrv`).
        """
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)
        offset = unwrap_field_default(offset)

        response = self._query(_MCP_SERVER_NAMES_QUERY_ROUTE, {
            "time_range": time_range,
            "limit": limit,
            "offset": offset,
        })
        return self._format_response(response, limit=limit)

    async def pivot_on_guardian_attribute(
        self,
        attribute: str = Field(
            description="Attribute to pivot on: Product, HostName, Skill, or Name.",
        ),
        value: str = Field(
            description="Value to search for.",
        ),
        time_range: str = Field(
            default="7d",
            description="Lookback window (e.g., '1h', '24h', '7d'). Sent to the API as requested; if refused, Guardian retries narrower and reports it in 'notices'. Default: '7d'",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Pivot from a known attribute value to the agents or activity carrying it.

        Use this to pivot from a known attribute to the agents (or activity)
        with that value:

        - `Product` — agents of a product (value normalized like
          search_guardian_agents).
        - `HostName` — agents on a host.
        - `Skill` — skill frontmatters matching a name pattern (substring).
        - `Name` — merges per-invocation skill-usage and tool-usage, deduped
          by sensor (`aid`); rows without an `aid` are all kept.

        Returns the `{results, pagination}` envelope for every branch.
        """
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)

        allowed_attrs = ["Product", "HostName", "Skill", "Name"]
        if attribute not in allowed_attrs:
            return {
                "error": f"Invalid attribute: {attribute!r}. "
                f"Allowed: {', '.join(allowed_attrs)}"
            }

        if attribute == "Product":
            # Normalize exactly as search_guardian_agents does, so "Claude Code"
            # and "CLAUDE_CODE" behave the same in both tools.
            response = await self._query_async(_AGENTS_QUERY_ROUTE, {
                "product": _normalize_product_name(value),
                "time_range": time_range,
                "limit": limit,
            })
            return self._format_response(response, limit=limit)

        elif attribute == "HostName":
            response = await self._query_async(_AGENTS_QUERY_ROUTE, {
                "hostname": value, "time_range": time_range, "limit": limit,
            })
            return self._format_response(response, limit=limit)

        elif attribute == "Skill":
            # Substring match on skill-frontmatter name.
            response = await self._query_async(_SKILLS_QUERY_ROUTE, {
                "name_filter": value, "time_range": time_range, "limit": limit,
            })
            return self._format_response(response, limit=limit)

        else:  # Name — search both skills and tools
            # Both legs are LogScale-backed and default to 2h without an
            # explicit window, so time_range is threaded through.
            skill_resp, tool_resp = await asyncio.gather(
                self._query_async(_SKILL_USAGE_QUERY_ROUTE, {
                    "name": value, "time_range": time_range, "limit": limit,
                }),
                self._query_async(_TOOL_USAGE_QUERY_ROUTE, {
                    "tool_name": value, "time_range": time_range, "limit": limit,
                }),
            )

            # Dedup by sensor (aid) across both legs, but keep rows that carry no
            # aid — they cannot collide on a sensor, and dropping them would hide
            # real tool-usage/skill-usage activity.
            seen_ids: set[str] = set()
            results: list[dict[str, Any]] = []
            for r in (skill_resp.resources + tool_resp.resources):
                iid = r.get("aid", "")
                if iid:
                    if iid in seen_ids:
                        continue
                    seen_ids.add(iid)
                results.append(r)

            # Two merged legs have no single pagination block, so report the merged
            # count. Every other branch returns the same envelope, and one tool must
            # not change shape with its own input.
            merged = GuardianResponse(
                resources=results,
                status_code=200,
                notices=skill_resp.notices + tool_resp.notices,
                pagination={"offset": 0, "limit": limit, "total": len(results)},
            )
            return self._format_response(merged, limit=limit)

    def get_guardian_process_tree(
        self,
        session_id: str = Field(
            description="AgenticSessionId (UUID) or vertex key (aisess:...).",
        ),
        depth: int = Field(
            default=2,
            ge=1,
            le=3,
            description="Process tree depth (1=direct spawns, 2=grandchildren, 3=max).",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get the spawned process tree for an AI session.

        Use this to see what processes an AI session launched. Returns process
        tree with command lines, image filenames, and timestamps.
        """
        depth = unwrap_field_default(depth)

        response = self._query(_PROCESS_TREE_ROUTE, {"id": session_id, "depth": depth})

        if not response.ok and response.count == 0:
            return {"error": response.errors, "session_id": session_id}
        if response.count == 0:
            return {"error": f"No session found for: {session_id}"}
        result = response.resources[0]
        if response.errors:
            result["_warnings"] = response.errors
        return result

    def get_guardian_network_events(
        self,
        session_id: str = Field(
            description="AgenticSessionId (UUID) or vertex key (aisess:...).",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get outbound network connections from an AI session's processes.

        Use this to see what network activity an AI session generated.
        Returns destination IPs, ports, protocols, and timestamps.
        """
        response = self._query(_NETWORK_EVENTS_ROUTE, {"id": session_id})

        if not response.ok and response.count == 0:
            return {"error": response.errors, "session_id": session_id}
        if response.count == 0:
            return {"error": f"No session found for: {session_id}"}
        result = response.resources[0]
        if response.errors:
            result["_warnings"] = response.errors
        return result

    async def get_guardian_file_events(
        self,
        session_id: str = Field(
            description="AgenticSessionId (UUID) or vertex key (aisess:...).",
        ),
        sensitive_only: bool = Field(
            default=False,
            description="Only show access to sensitive paths (.env, credentials, secrets, keys, tokens).",
        ),
        time_range: str = Field(
            default=_LOGSCALE_TOOL_DEFAULT,
            description="Lookback window for the tool-usage leg (raw events). Default: '2h'",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of results to return. [1-500]",
        ),
    ) -> dict[str, Any]:
        """Get file activity for processes spawned from an AI session.

        Use this to see files written by spawned processes and file tool
        usage; use `sensitive_only` to filter to credential and secret paths.
        Returns combined file events from the graph and inventory layers.
        The graph leg has no time dimension; `time_range` applies only to
        the tool-usage leg, which defaults to 2 hours.
        """
        sensitive_only = unwrap_field_default(sensitive_only)
        time_range = unwrap_field_default(time_range)
        limit = unwrap_field_default(limit)

        # Resolve the inventory session_id from vertex key if needed
        inventory_session_id = self._extract_session_id_from_vertex_key(session_id)

        # Graph file events + Inventory tool file access in parallel
        graph_resp, inv_resp = await asyncio.gather(
            self._query_async(_FILE_EVENTS_ROUTE, {"id": session_id}),
            self._query_async(_TOOL_USAGE_QUERY_ROUTE, {
                "session_id": inventory_session_id,
                "time_range": time_range,
                "limit": limit,
            }),
        )

        module_writes = []
        if graph_resp.ok and graph_resp.count > 0:
            session_data = graph_resp.resources[0]
            # Graph edges come back as null when the target vertex is not
            # resolvable, so each edge is checked before being read as a dict.
            for proc_edge in session_data.get("SessionProcessPid", []) or []:
                if not proc_edge:
                    continue
                proc = proc_edge.get("Process") or {}
                for mod_edge in proc.get("ModuleWrittenMod", []) or []:
                    if not mod_edge:
                        continue
                    module_info = mod_edge.get("Module", {})
                    module_writes.append({
                        "process": proc.get("ImageFileName", proc.get("__id", "")),
                        "file": module_info.get("TargetFileName")
                        or module_info.get("ImageFileName", ""),
                        "sha256": module_info.get("SHA256HashData", ""),
                        "timestamp": mod_edge.get("EventCloudTime", ""),
                    })

        # Filter inventory results to file-related tools only
        file_tools = {"Read", "Write", "Edit", "Glob", "Grep"}
        tool_file_access = []
        for r in inv_resp.resources[:limit]:
            if r.get("AgenticToolName") in file_tools:
                tool_file_access.append({
                    "tool": r.get("AgenticToolName") or "",
                    "path": r.get("AgenticPath") or "",
                    "command_line": r.get("CommandLine") or "",
                })

        if sensitive_only:
            sensitive_patterns = [
                ".env", "credential", "secret", ".key", ".pem", "token", "password"
            ]
            module_writes = [
                m for m in module_writes
                if any(p in m.get("file", "").lower() for p in sensitive_patterns)
            ]
            tool_file_access = [
                t for t in tool_file_access
                if any(
                    p in ((t.get("path") or "") + (t.get("command_line") or "")).lower()
                    for p in sensitive_patterns
                )
            ]

        return {
            "module_writes": module_writes[:limit],
            "tool_file_access": tool_file_access[:limit],
        }

    def get_guardian_classified_file_access(
        self,
        process_id: str = Field(
            description="Process vertex ID (pid:{aid}:{upid}). Get from session activity or process tree results.",
        ),
    ) -> dict[str, Any]:
        """Get classified/sensitive file access for an AI agent process.

        Use this to see which files a process accessed that Falcon Data
        Protection (FDP) classified, and whether it triggered a data
        protection policy violation. Returns data pattern categories (PII,
        credentials, etc.), classification policy names, rule actions
        (allowed/blocked), and individual file details (path, name, SHA256,
        timestamps).
        """
        response = self._query(
            _CLASSIFIED_FILE_ACCESS_ROUTE, {"id": process_id}
        )
        if not response.ok:
            return {"error": response.errors}
        if response.count == 0:
            return {"error": f"No classified file access found for process: {process_id}"}
        return response.resources[0]

    async def generate_guardian_report(
        self,
        report_type: str = Field(
            description="Report type: fleet_summary, agent_detail, skill_threat, or sensitive_access.",
        ),
        time_range: str = Field(
            default="7d",
            description="Lookback window. Affects only fleet_summary and sensitive_access; agent_detail and skill_threat use their own per-leg windows and ignore this. Default: '7d'",
        ),
        product_filter: str | None = Field(
            default=None,
            description="Optional product filter for fleet-level reports.",
        ),
        agent_id: str | None = Field(
            default=None,
            description="Required for agent_detail report. The AIAgent Id.",
        ),
    ) -> dict[str, Any]:
        """Generate a structured Guardian report.

        Use this to produce fleet_summary, agent_detail, skill_threat, or
        sensitive_access reports; agent_detail requires agent_id.
        `time_range` applies only to fleet_summary and sensitive_access; the
        other two types use their own per-leg windows. Returns a structured
        report with timestamp and data.
        """
        agent_id = unwrap_field_default(agent_id)
        time_range = unwrap_field_default(time_range)
        product_filter = unwrap_field_default(product_filter)

        valid_types = ["fleet_summary", "agent_detail", "skill_threat", "sensitive_access"]
        if report_type not in valid_types:
            return {"error": f"Invalid report_type: {report_type!r}. Valid: {valid_types}"}

        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if report_type == "fleet_summary":
            inventory = await self.get_guardian_inventory(time_range=time_range)
            skills = await self._offload(self.get_guardian_fleet_skill_inventory)
            report: dict[str, Any] = {
                "report_type": report_type,
                "generated_at": generated_at,
                "time_range": time_range,
                "data": {"inventory": inventory, "skills": skills},
            }
            notices = list(inventory.get("notices") or [])
            _, skill_notices = self._unwrap_results(skills)
            notices += skill_notices
            if notices:
                report["notices"] = notices
            return report

        elif report_type == "agent_detail":
            if not agent_id:
                return {"error": "agent_id is required for agent_detail report"}
            sanitize_guardian_value(agent_id)
            agent = await self._agent_profile(agent_id)
            # No time_range key: _agent_profile uses its own per-leg windows and
            # takes no window argument, so echoing the caller's value would claim a
            # coverage this report does not have.
            return {
                "report_type": report_type,
                "generated_at": generated_at,
                "data": {"agent": agent},
            }

        elif report_type == "skill_threat":
            skills = await self._offload(self.get_guardian_fleet_skill_inventory)
            # The skill aggregate takes a window; this report leaves it at the
            # tool's own default rather than echoing the caller's value.
            return {
                "report_type": report_type,
                "generated_at": generated_at,
                "data": {"skills": skills},
            }

        else:  # sensitive_access
            _MAX_SENSITIVE_SESSIONS = 3
            # Executions carry a flat AgenticSessionId (agent-session rows nest it
            # under Cim), and it is the id the file-events graph resolves, so it is
            # the right source for the session IDs to drill into.
            sessions = await self._offload(self.search_guardian_executions, time_range=time_range)
            sensitive_results: list[dict[str, Any]] = []
            if isinstance(sessions, dict) and "error" in sessions:
                return {"report_type": "sensitive_access", "error": sessions["error"]}
            # search_guardian_executions wraps its list in {results, notices} when
            # the window was narrowed; unwrap or the loop below silently sees nothing.
            sessions, notices = self._unwrap_results(sessions)
            if isinstance(sessions, list):
                seen: set[str] = set()
                sids: list[str] = []
                for s in sessions:
                    sid = s.get("AgenticSessionId", "")
                    if sid and sid not in seen:
                        seen.add(sid)
                        sids.append(sid)
                    if len(sids) >= _MAX_SENSITIVE_SESSIONS:
                        break
                if sids:
                    file_results = await asyncio.gather(
                        *(
                            self.get_guardian_file_events(
                                session_id=sid, sensitive_only=True, time_range=time_range
                            )
                            for sid in sids
                        )
                    )
                    for sid, file_events in zip(sids, file_results):
                        if isinstance(file_events, dict) and (
                            file_events.get("module_writes")
                            or file_events.get("tool_file_access")
                        ):
                            sensitive_results.append({
                                "session_id": sid,
                                "file_events": file_events,
                            })
            report = {
                "report_type": report_type,
                "generated_at": generated_at,
                "time_range": time_range,
                "data": {"sensitive_sessions": sensitive_results},
            }
            if notices:
                report["notices"] = notices
            return report

    # --- Helpers ---


    def _extract_session_id_from_vertex_key(self, session_id: str) -> str:
        """Extract the inventory session UUID from either a vertex key or raw UUID.

        Given 'aisess:abc123:uuid-here' returns 'uuid-here'.
        Given a raw UUID, returns it as-is.
        """
        if session_id.startswith("aisess:"):
            # Format: aisess:{aid}:{session_uuid}
            parts = session_id.split(":", 2)
            if len(parts) == 3:
                return parts[2]
        return session_id

    async def _get_graph_activity(self, vertex_id: str) -> list[dict[str, Any]] | dict[str, Any]:
        """Get graph activity for a single vertex ID via session-activity endpoint."""
        response = await self._query_async(
            _SESSION_ACTIVITY_ROUTE,
            {"ids": vertex_id},
        )
        if not response.ok:
            return {"error": response.errors, "vertex_ids": [vertex_id]}
        if response.count == 0:
            return {"error": f"No session found for: {vertex_id}", "vertex_ids": [vertex_id]}
        return response.resources[0]

    def _missing_aid_response(self) -> GuardianResponse:
        """Stand-in for an event query that cannot be scoped to a single agent.

        Returned instead of issuing an unfiltered query, which would surface
        fleet-wide activity under an agent-scoped key.
        """
        return GuardianResponse(
            resources=[],
            errors=[
                {
                    "message": "Agent record has no SensorId; "
                    "cannot scope event queries to this agent."
                }
            ],
        )

    def _pick_detection_score(
        self, response: GuardianResponse, sensor_id: str, product: Any
    ) -> Any:
        """Select this agent's detection score from the aggregate.

        Prefers the exact two-key match on AgentId (== AIAgent.SensorId) AND
        AgenticProductTag (== AIAgent.Product). Both keys are needed because a
        host usually runs more than one AI agent, so SensorId alone would
        attribute one host's worst detection to every agent on it.

        Most rows cannot be matched that way: ``aggregates/detections`` leaves the
        product tag unattributed on the majority of rows (encoded as ``0``, while
        ``queries/detections`` uses ``null`` for the same thing), so an exact-only
        join resolves ~1% of agents. Those rows still carry a real host, so they
        fall back to a sensor-only match reported as host-scoped — the score is
        real, but it belongs to the machine rather than to this agent.

        Both keys hold the same numeric product tag IDs but disagree on encoding
        (``aggregates/detections`` returns an int, the agent side a string), so
        they are compared via ``_tag_key``, which coerces both to ``str``.

        Returns one of:
          - a bare score (int) — exact match on both keys, agent-specific
          - ``{"host_max_score", "scope": "host", "note": …}`` — matched on
            sensor only; covers every AI agent on that host
          - ``None`` — no row for this host at all
        """
        if not response.ok:
            return self._with_notices({"error": response.errors}, response)

        want = _tag_key(product)
        host_fallback: Any = None
        for r in response.resources:
            if r.get("AgentId") != sensor_id:
                continue
            tag = r.get("AgenticProductTag")
            if want and not _is_unattributed_tag(tag) and _tag_key(tag) == want:
                return r.get("maxDetectionScore")
            if _is_unattributed_tag(tag):
                score = r.get("maxDetectionScore")
                if score is not None:
                    host_fallback = max(host_fallback or 0, _as_int(score))

        if host_fallback is not None:
            return {
                "host_max_score": host_fallback,
                "scope": "host",
                "note": (
                    "The detection carries no product tag, so it cannot be tied "
                    "to one agent. This is the highest score on this HOST and "
                    "may belong to a different AI agent running on it."
                ),
            }
        return None

    def _sub_result(
        self, response: GuardianResponse, limit: int
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Format one sub-query of a fan-out, preserving failures.

        Truncating ``response.resources`` directly would turn an API error into an
        empty list, making a failed query indistinguishable from "no activity".

        Args:
            response: Guardian query response
            limit: Max results to return (client-side truncation)
        """
        if not response.ok:
            return self._with_notices({"error": response.errors}, response)
        resources = response.resources[:limit]
        if response.notices:
            return {"results": resources, "notices": response.notices}
        return resources

    def _format_response(
        self, response: GuardianResponse, limit: int | None = None
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Format a Guardian response as the standard search envelope.

        Returns ``{results, pagination}`` (plus ``notices`` when the query had to be
        adjusted — window narrowed, unsupported parameter dropped, timeout retried —
        so a caller cannot report a count without seeing it covers a different window
        than was asked for). Errors stay ``{error, notices?}``.

        Args:
            response: Guardian query response
            limit: Optional max results to return (client-side truncation)
        """
        if not response.ok:
            return self._with_notices({"error": response.errors}, response)
        resources = response.resources
        if limit is not None:
            resources = resources[:limit]
        envelope = self._build_pagination_envelope(
            resources, self._aidr_pagination(response, limit)
        )
        return self._with_notices(envelope, response)

    @staticmethod
    def _aidr_pagination(
        response: GuardianResponse, limit: int | None
    ) -> dict[str, Any] | None:
        """AIDR's pagination block with its unusable ``total`` blanked out.

        AIDR reports ``meta.pagination.total`` as ``offset + len(page)``. On a FULL
        page that merely restates the cursor, so it is not a match count and must not
        be surfaced as one: the envelope contract is "the API's count, or null — never
        synthesize one", and forwarding AIDR's number synthesizes one by proxy. A SHORT
        page means the rows ran out, and there AIDR's total IS the real count.

        Verified live: /aidr/queries/agent-sessions/v1 reported total=28 at every offset
        from 20 through 100 (short pages), but total=offset+limit on every full page.
        """
        pagination = response.pagination
        if not pagination:
            return None
        result = dict(pagination)
        page_limit = pagination.get("limit", limit)
        # Fullness is about what the API returned, before our client-side truncation.
        returned = len(response.resources)
        if page_limit is not None and returned >= int(page_limit):
            result["total"] = None
        # Report the page size the caller actually got. On paginated routes this
        # equals the API's echoed limit; on the no-pagination aggregates the API
        # echoes its group cap (e.g. 500) while the real page was truncated to the
        # caller's limit, so echoing the API value would misreport the page size.
        if limit is not None:
            result["limit"] = limit
        return result

    @staticmethod
    def _with_notices(
        payload: dict[str, Any], response: GuardianResponse
    ) -> dict[str, Any]:
        """Attach a response's notices to an already-dict payload."""
        if response.notices:
            payload["notices"] = response.notices
        return payload

    @staticmethod
    def _unwrap_results(value: Any) -> tuple[Any, list[str]]:
        """Split a tool result into (payload, notices).

        Tools return either a bare list or ``{results, notices}`` depending on
        whether the query was adjusted. Callers that consume another tool's
        output go through this so the wrapped form does not read as "no data".
        """
        if isinstance(value, dict) and "results" in value:
            return value["results"], list(value.get("notices") or [])
        return value, []
