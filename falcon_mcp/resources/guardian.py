"""
Guardian resources for Falcon MCP Server.

Contains documentation resources for Guardian API usage, entity schema reference,
and example queries for AI agent analysis.

Covers both the ThreatGraph security-telemetry layer and the AI entity
store / LogScale event layer.
"""

QUERY_GUIDE_DOCUMENTATION = """\
# Guardian API Reference

Guardian uses structured Falcon MSA API endpoints to query AI agent telemetry data, where clients interact with typed REST parameters.

## Two Query Layers

- **AI Entity Store**: agent identity and catalogs (AIAgent, AIAgentSession,
  AITool, AISkillFrontmatter, MCPServerName, AIAgentInstallation, AIModelName,
  AIAgentOSUser). Filtered by `sensor_id`/`product`/`hostname` and windowed by
  `time_range` on `LastSeen`.
- **LogScale Events**: per-invocation activity (`AgenticSessionStart`,
  `AgenticToolRequest`, `AgenticUserPromptSubmit`) surfaced by
  `queries/executions`, `queries/tool-usage`, `queries/skill-usage`, and
  `queries/prompts`. Filtered by `aid`/`session_id` and windowed by
  `time_range`, which defaults to **2 hours** when omitted.

## ⚠️ Three identifiers — do not conflate

| Identifier | Shape | What it is | Endpoints that take it |
|---|---|---|---|
| `Id` | opaque record token (e.g. `ASCWQseSk3b76g...`) | one AIAgent record | entities/agents (`ids`); pass to get_guardian_agent |
| `AgentIds[]` | content hash (width varies) | the agent's content hash(es) | **no endpoint takes it.** It is carried in the record only — no filter parameter accepts it, and nothing joins against it any more (see below) |
| `aid` / `SensorId` | **32-hex** | a HOST/sensor | tools, agent-os-users, installs (`sensor_id`); executions/tool-usage/skill-usage/prompts (`aid`); detections (`agent_id`; misleadingly named). Not a filter on agent-sessions — that route has no host filter. |

**Many hosts run more than one AI agent** — up to 13 observed — so anything
keyed only by `aid`/`sensor_id` covers every agent on that machine, not one
agent.

⚠️ **No entity can be scoped to a single agent.** The API used to return
reverse-relationship arrays (`UsedByAIAgents[]` on tools/skills/models/
mcp-server-names, `RanByAIAgents[]` on sessions, `UsedAIAgentSessions[]` on OS
users, `UsedByAIAgentOSUsers[]` on agents), which allowed a client-side join on
`AgentIds[]`. **All of them were removed and none are returned now** — verified
live across every affected route. So per-agent attribution is not possible for
tools, skills, models or MCP servers; `sensor_id`/`aid` (HOST scope) is the
finest grain that exists. Do not build a client-side join on these entities.

## ⚠️ Two product encodings

- **Entity sources** (agents, sessions, installs, models, detections) return the
  product as a **numeric tag ID**, e.g. `213584428666200`. The encoding is not
  consistent across sources: `queries/agents` returns it as a JSON **string**
  (`"213584428666221"`) while `aggregates/detections` returns a JSON **int**
  (`0` for unattributed). Coerce both sides with `str()` before comparing, or the
  join silently misses. (Python's `json` decodes an integer literal to `int`, not
  `float`, so no exponent form is involved.) Each product tag field is also
  decorated server-side with a friendly `<field>Name` sibling
  (`AgentProductName` / `ProductName` / `AgenticProductTagName`) resolved to a
  readable name (e.g. "Claude Code"); unrecognized tags are left undecorated (no
  sibling).
- **LogScale event sources** return product **names**.

On *input* you always pass a human name (`CLAUDE_CODE`, `Claude Code`,
`claude-code` all normalize); unknown names are a 400. On *output* the encodings
differ, so joining a LogScale row to an entity row requires mapping. Mixing them
yields a silent empty join.

## Time windows: sent as requested, the API decides

There is no pre-emptive per-route ceiling in Guardian's code. Whatever
`time_range` the caller asks for is sent to the API as asked. The `/aidr`
lookback limits differ between deployments, so the API, not this client, is
the authority on what it will serve.

Every `queries/*` and `aggregates/*` route accepts `time_range`. The
entity-store queries and aggregates filter `LastSeen` (or `Timestamp` for
detections). The LogScale-backed event sources (`queries/executions`,
`queries/tool-usage`, `queries/skill-usage`, `queries/prompts`) default to
**2 hours** when `time_range` is omitted — widen it explicitly to reach older
activity.

The maximum lookback splits cleanly by layer, and is enforced server-side:

- **Entity and aggregate routes** (agents, agent-sessions, tools, skills,
  models, mcp-server-names, installs, os-users, detections, all aggregates)
  serve up to **90 days**.
- **LogScale event routes** (`queries/executions`, `queries/tool-usage`,
  `queries/skill-usage`, `queries/prompts`) cap at **7 days** — they scan raw
  event data, which cannot be scanned over longer windows. `7d` is inclusive
  (`168h` is accepted, `8d` is refused with a 400 naming the 7-day maximum).

These are the observed limits, but the client applies no pre-emptive ceiling:
whatever `time_range` the caller asks for is still sent as asked, and the API
remains the authority. When it refuses, the ladder below narrows reactively.

If the API refuses the requested window (a 504 timeout, or a 400 that names
`time_range`), Guardian retries with progressively narrower windows (`7d`,
`24h`, `6h`, `1h`) until one succeeds, and reports the narrowing in
`notices`. There is a 30-second wall-clock budget on this retry ladder. If it
runs out before a window succeeds, `notices` says so and asks the caller to
retry with a smaller `time_range` directly. Read `notices` before reporting
any count: a narrowed window means the numbers cover less time than asked
for.

Only the **entity fetch-by-id** and **threat-graph** routes reject
`time_range` outright, at any width, with a 400: every `entities/*` route
(`entities/agents`, `entities/executions`, `entities/session-activity`,
`entities/process-tree`, `entities/network-events`, `entities/file-events`,
`entities/classified-file-access`). These have no time dimension.

## API Endpoint Pattern

```
/aidr/{queries|entities|aggregates}/{resource}/v1
```

- **queries** — List/search with filters (GET, returns paginated results)
- **entities** — Get full details by IDs (GET with `?ids=id1&ids=id2` or `?id=vertex-key`)
- **aggregates** — Counts and summaries (GET, returns grouped counts)

## Available Endpoints

### AI Entity & Event Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/aidr/queries/agents/v1` | Search agent instances |
| GET | `/aidr/entities/agents/v1` | Get agents by IDs |
| GET | `/aidr/aggregates/agents/v1` | Agent counts by product |
| GET | `/aidr/queries/agent-sessions/v1` | Search agent sessions (entity store) |
| GET | `/aidr/aggregates/agent-sessions/v1` | Session counts by product; `count` is a JSON string |
| GET | `/aidr/queries/executions/v1` | Per-process invocations (LogScale) |
| GET | `/aidr/entities/executions/v1` | Execution detail by session id |
| GET | `/aidr/queries/tools/v1` | AITool inventory |
| GET | `/aidr/aggregates/tools/v1` | Tool counts by name |
| GET | `/aidr/queries/tool-usage/v1` | Per-invocation tool events (LogScale) |
| GET | `/aidr/queries/skills/v1` | AISkillFrontmatter inventory |
| GET | `/aidr/aggregates/skills/v1` | Skill counts by name |
| GET | `/aidr/queries/skill-usage/v1` | Per-invocation skill events (LogScale) |
| GET | `/aidr/queries/agent-os-users/v1` | OS users that ran AI agents |
| GET | `/aidr/queries/mcp-server-names/v1` | MCP server names (fleet-wide) |
| GET | `/aidr/queries/prompts/v1` | Search prompts (LogScale) |
| GET | `/aidr/queries/detections/v1` | Detections involving AI agent processes |
| GET | `/aidr/aggregates/detections/v1` | Max detection severity per agent + product |
| GET | `/aidr/queries/agent-installations/v1` | AI agent installations |
| GET | `/aidr/queries/model-names/v1` | AI model names (fleet-wide) |

### Agentic Graph (Security Telemetry)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/aidr/entities/session-activity/v1` | Full graph activity for sessions |
| GET | `/aidr/entities/process-tree/v1` | Spawned process tree |
| GET | `/aidr/entities/network-events/v1` | Network connections |
| GET | `/aidr/entities/file-events/v1` | File write activity |
| GET | `/aidr/entities/classified-file-access/v1` | FDP classified file access |

## Query Parameters (GET endpoints)

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `time_range` | string | Lookback window: `1h`, `24h`, `7d`, `30d`. Max lookback is 90d on entity/aggregate routes and 7d on LogScale event routes (see "Time windows" above). Sent to the API as requested; no pre-emptive ceiling is applied client-side. If the API refuses the window, Guardian retries narrower windows and reports this in `notices`. Rejected only by `entities/*` routes; see "Time windows" above. |
| `limit` | int | Max results (1–500, default 50) |
| `offset` | int | Pagination offset. **Capped at 1000** — a higher value is a 400 (`offset must not exceed 1000; use time_range filters for deep pagination`). To reach older records, narrow `time_range` rather than paging deeper. |

Also note `time_range` accepts only `h` (hours) and `d` (days). Minutes are
rejected with a 400 (`invalid time_range unit: "m"`), so use `1h`, not `60m`.

### Agents (`/aidr/queries/agents/v1`)

AIAgent entity + FalconHost. `time_range` filters `LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `product` | Filter by product (e.g., `CLAUDE_CODE`, `CURSOR`) |
| `hostname` | Filter by device hostname |

Returns records carrying the opaque `Id`, the 32-hex `SensorId`, the
`AgentIds[]` content hash(es), `AgentProduct`, `AgentName`, `Hostname`, and the seen timestamps.

### Agent Sessions (`/aidr/queries/agent-sessions/v1`)

Backed by the AIAgentSession entity store; `time_range` filters `LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `product` | Filter by product |

Returns `Id`, `Product` (+ friendly `ProductName`), `Name`, the seen
timestamps, and the nested `Cim.AIAgentSession` (`sessionId`, `modelsInvoked[]`,
`startTime`, `workingDirectory`, `updatedTime`).

⚠️ **Results are fleet-wide and cannot be attributed to an agent or a host.**
There is no `sensor_id` and no agent filter — the entity's inherited
`SensorId`/`AIAgentIds` are never populated upstream and are not returned. A
count from this route is a count for the whole product, so do not report it as
one agent's session count, and do not rank agents by grouping these rows on
`Product` — that ranks products. There is no per-agent session count anywhere in
this API. The tool response carries a `note` saying the same. For a single host,
and for the flat process grain with per-execution model and token counts, use
`queries/executions/v1` instead.

### Executions (`/aidr/queries/executions/v1`)

Backed by LogScale `AgenticSessionStart` events — one row per process
invocation. Defaults to 2h when `time_range` is omitted; max 7d (see "Time windows").

| Parameter | Description |
|-----------|-------------|
| `session_id` | Filter by AgenticSessionId |
| `aid` | Filter by sensor ID (aid). Identifies a HOST |

Returns `aid`, `AgenticSessionId`, `AgenticModel`, `AgenticWorkingDirectory`,
`AgenticInputTokens`, `AgenticOutputTokens`, `ContextProcessId`, `ProcessTags`,
`timestamp`. Each row carries a **flat `AgenticSessionId`**, so this is the
right source for session IDs to drill into with the graph endpoints.

### Tools (`/aidr/queries/tools/v1`)

AITool entity store — the inventory of which tools exist. `time_range` filters
`LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `sensor_id` | Filter by the tool's host sensor ID (32-hex aid) |

Rows are flat: `Id`, `Name`, `SensorId`, `FirstSeen`/`LastSeen`. There is **no
per-agent filter and no way to attribute a tool to one agent** — `sensor_id`
scopes to the tool's HOST, covering every agent on it.

⚠️ **This store is thinly populated.** It covers far fewer hosts than the agent
store does, so an agent's sensor often matches nothing at all. For the tools an
agent's host actually invoked, use `queries/tool-usage/v1?aid=<aid>` — the event
side is far better populated and carries the command lines.

### Tool Usage (`/aidr/queries/tool-usage/v1`)

Backed by LogScale `AgenticToolRequest` events — per-invocation grain with file
paths and command lines. Defaults to 2h when `time_range` is omitted; max 7d.

| Parameter | Description |
|-----------|-------------|
| `tool_name` | **Exact, case-sensitive** match on `AgenticToolName` |
| `aid` | Filter by sensor ID (aid) |
| `session_id` | Filter by session ID |

⚠️ **`tool_name` is exact and case-sensitive, and the two stores disagree on
spelling.** A mismatch returns zero rows with HTTP 200, not an error, so it is
indistinguishable from "this tool was never used". `tool_name='bash'` matches
nothing where `tool_name='Bash'` matches.

The AITool inventory (`aggregates/tools`, `queries/tools`, and
`get_guardian_inventory`'s `tools.by_name`) lists lowercase names — `bash`,
`edit`, `grep`, `code_search`, `execute` — while these events carry `Bash`,
`Edit`, `Grep`. Some names really are lowercase in both (`apply_diff`,
`list_files`, `read_file`, `mcp__*`), and both `glob` and `Glob` exist as
distinct names, so the case cannot be guessed or normalized. Do not hand a name
straight from the inventory to `tool_name` and read an empty result as absence —
try the other capitalization first.

### Skills (`/aidr/queries/skills/v1`)

AISkillFrontmatterView entity store. `time_range` filters `LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `name_filter` | **Substring** filter on skill name (wildcard via 'like') |

Returns `Id`, `SkillName`, `SkillDescription`, `SkillDirectoryHash`, and the
seen timestamps.

### Skill Usage (`/aidr/queries/skill-usage/v1`)

Backed by LogScale `AgenticToolRequest` (AgenticTool == '13'). Defaults to 2h; max 7d.

| Parameter | Description |
|-----------|-------------|
| `name` | Filter by skill name (**exact** match on `AgenticSkill`) |
| `aid` | Filter by sensor ID (aid) |
| `session_id` | Filter by session ID |

### OS Users (`/aidr/queries/agent-os-users/v1`)

AIAgentOSUser entity store. `time_range` filters `LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `aid` | Filter by the OS user's sensor ID (aid) |
| `username` | Filter by OS username |
| `object_sid` | Filter by ObjectSid (AD security identifier) |

Returns `Aid`, `Username`, `ObjectSid`, and the seen timestamps.

### MCP Server Names (`/aidr/queries/mcp-server-names/v1`)

MCPServerName entity store. **Fleet-wide — no agent/sensor filter.**
`time_range` filters `LastSeen`.

Returns the human-friendly name in `Cim.MCPServerName.serverName` (the `Id` is
only a hashed dedup key) and the used/seen timestamps.

### Prompts (`/aidr/queries/prompts/v1`)

Backed by LogScale `AgenticUserPromptSubmit` events. Defaults to 2h; max 7d.

| Parameter | Description |
|-----------|-------------|
| `session_id` | Filter by session ID |
| `aid` | Filter by sensor ID (aid) |

### Detections (`/aidr/queries/detections/v1`)

Alert source. `time_range` filters the detection `Timestamp`. Always scoped
server-side to `HasAgenticProcess == true`; that is not client-controllable.

| Parameter | Description |
|-----------|-------------|
| `agent_id` | ⚠️ Takes a **32-hex SENSOR/host ID** (`== AIAgent.SensorId`), NOT the opaque `AIAgent.Id` and NOT the `AgentIds[]` content hash. The parameter name is misleading. |
| `product` | Filter by product name → resolved to a tag ID |

⚠️ **`product` takes the name the API expects on input, not a value the API
returns on output.** `product=CLAUDE_CODE` works; feeding back the numeric
`AgenticProductTag` value from a response returns a 400. Use the
human-readable product name only.

Response: `AssignedToName, AgentId, CompositeId, CreatedTimestamp, DataDomains,
Name, Product, RiskScore, Severity, SeverityName, Sha256, SourceHosts,
SourceProducts, Status, Tactic, Technique, UserNames, HasAgenticProcess,
AgenticProductTag, AgenticProductTagName, Timestamp`.

- `Severity` (0–100) and `RiskScore` (0–100) are **different** metrics.
- `DataDomains` and `SourceProducts` are **arrays**.
- `AssignedToName`, `SourceHosts`, `UserNames` are frequently `null`.
- The product field is **`AgenticProductTag`** (friendly name in the
  `AgenticProductTagName` sibling when resolved). It is **unattributed on many
  rows**, encoded as `null` here and as `0` on `aggregates/detections`. Those
  detections cannot be tied to a product or a specific agent.

### Detection Scores (`/aidr/aggregates/detections/v1`)

The **"Agentic Threat Score"**. Same parameters as `queries/detections/v1`.
Fixed `GroupBy(AgentId, AgenticProductTag)` with `max(Severity)` as
`maxDetectionScore`.

⚠️ **Joining these rows onto agents requires BOTH keys:**

```
detections.AgentId == agent.SensorId && detections.AgenticProductTag == agent.AgentProduct
```

`AgentId` alone identifies a HOST, and many hosts run more than one AI agent, so
a single-key join attaches one host's worst detection to *every* agent on that
host. Both sides of the product key are numeric tag IDs — normalize each to a
plain integer string before comparing (a JSON float renders in exponent form
otherwise).

⚠️ **The two detection endpoints encode "no product" differently.**
`aggregates/detections` uses `0`; `queries/detections` uses a real `null`.
Neither is a member of the product taxonomy (every real tag is ~2.1e14), so treat
**both `0` and `null` as unattributed**. Most aggregate rows are unattributed
this way, so an exact two-key join resolves only a small fraction of agents.

Capped at 500 groups, no pagination.

### Installs (`/aidr/queries/agent-installations/v1`)

AIAgentInstallationView entity. `time_range` filters `LastSeen`.

| Parameter | Description |
|-----------|-------------|
| `sensor_id` | Filter by sensor ID (32-hex aid) |
| `product` | Filter by product name |
| `hostname` | Filter by hostname |

Returns `Id`, `SensorId`, `Hostname`, `AgentName`, `AgentProduct`,
`AgentVersion`, `InstallSource`, `AgentDeclarationPath`, `BinaryPath`,
`FileSha256`, `LastExecutionTime`, and the seen timestamps.

### Models (`/aidr/queries/model-names/v1`)

AIModelName entity. **Fleet-wide — the only server-side filter is `time_range`
on `LastSeen`.** There is no name/product/sensor scalar to filter on.

Returns the human-friendly name in `Cim.AIModelName.modelName` (the `Id` is only
a hashed dedup key) and the used/seen timestamps. For the model used per
session, prefer `queries/agent-sessions/v1`
(`Cim.AIAgentSession.modelsInvoked`) or `queries/executions/v1`
(`AgenticModel`).

### Agent Aggregates (`/aidr/aggregates/agents/v1`)

Accepts `time_range`, `limit`, `offset`. Groups agent counts by product
(`AgentProduct`, a numeric tag ID; each bucket also carries a friendly
`AgentProductName`).

### Session Aggregates (`/aidr/aggregates/agent-sessions/v1`)

Groups session counts **by product** (`Product`, a numeric tag ID; each bucket
also carries a friendly `ProductName`), and `count` comes back as a **JSON
string** (`"7"`); coerce before arithmetic. Accepts `time_range` (filters
`LastSeen`) and `product`.

### Tool Aggregates (`/aidr/aggregates/tools/v1`)

AITool entity aggregate. Accepts `time_range`, `limit`, `sensor_id`. Groups by
`Name`.

### Skill Aggregates (`/aidr/aggregates/skills/v1`)

AISkillFrontmatter aggregate. Accepts `time_range`, `name_filter`. Groups by
`SkillName`.

| Parameter | Description |
|-----------|-------------|
| `name_filter` | Substring filter on skill name |

## Aggregate truncation

All aggregates cap at **500 groups with no pagination** (`offset` is accepted but
always applied as 0 internally). A response with exactly 500 rows is very likely
truncated. Narrow with `sensor_id`, `product`, or a shorter `time_range`.

## Error contract

| Status | Meaning | What to do |
|---|---|---|
| **400** | A parameter is not in the endpoint's allowlist, or an unknown product name | Read the message. It names the offending parameter. Do not retry unchanged. |
| **403** | Missing `AIDR:read`, or the `cloud.falcon-guardian.mcp-api.enable-query` flag is off for this CID | An access problem, not a query problem |
| **500** | Server-side query error | Report it; not caller-fixable |
| **504** | **Your query was too broad.** The engine aborted it. **This does NOT mean the API is broken.** | Narrow the window or add a filter (`aid`, `product`, `session_id`). Guardian retries automatically with progressively smaller windows and reports which one succeeded in `notices`. |

## Entities Parameters (GET endpoints)

Entities endpoints use query parameters for IDs:

```
GET /aidr/entities/agents/v1?ids=id1&ids=id2
GET /aidr/entities/executions/v1?id=session-uuid
```

`entities/agents` takes `ids` (agent record tokens, repeatable, max 100).
`entities/executions` takes a single `id` (an AgenticSessionId UUID) and an
optional `context_process_id`.

## Agentic Graph Parameters

```
GET /aidr/entities/session-activity/v1?ids=aisess:{aid}:{session_uuid}
GET /aidr/entities/process-tree/v1?id=aisess:{aid}:{session_uuid}&depth=2
GET /aidr/entities/network-events/v1?id=aisess:{aid}:{session_uuid}
GET /aidr/entities/file-events/v1?id=aisess:{aid}:{session_uuid}
GET /aidr/entities/classified-file-access/v1?id=pid:{aid}:{upid}
```

- `ids` / `id` — Session IDs (vertex keys or UUIDs; server resolves automatically)
- `depth` — Process tree depth (1–3, default 2; only for process-tree endpoint)

## Agentic Graph Vertex ID Format

Each vertex has a scoped ID: `{type_prefix}:{aid}:{unique_id}`

| Vertex Type | ID Pattern | Example |
|-------------|-----------|---------|
| AISession | `aisess:{aid}:{id}` | `aisess:aaaa0000bbbb1111:eb5ca156-1128-44ab-b933-3154a36e8a54` |
| AIAgent | `aiagent:{aid}:{hash}` | `aiagent:aaaa0000bbbb1111:a1b2c3...` |
| AITool | `aitool:{aid}:{hash}` | `aitool:aaaa0000bbbb1111:d4e5f6...` |
| AIModel | `aimod:{aid}:{hash}` | `aimod:aaaa0000bbbb1111:7a8b9c...` |

## Cross-Layer Linkage

The Agentic Graph endpoints resolve an `AgenticSessionId` UUID to its vertex key
automatically — pass a UUID and the server resolves it. A vertex key
(`aisess:{aid}:{uuid}`) is also accepted directly.

## Response Format

All endpoints return the standard Falcon API envelope:

```json
{
  "meta": {
    "pagination": {"offset": 0, "limit": 50, "total": 123},
    "query_time": 0.045,
    "trace_id": "uuid"
  },
  "resources": [...],
  "errors": []
}
```

⚠️ **`meta.pagination.total` is NOT a match count on a full page.** It is
synthesized as `offset + len(page)`, so on a full page it merely restates the
cursor. Guardian blanks it out (reports `null`) on full pages and forwards the
real count only on a short page, where the rows genuinely ran out. To know
whether more data exists, page until a short page comes back.

## Tips

- Product values are UPPER_SNAKE_CASE on input: `CLAUDE_CODE`, `CURSOR`,
  `CLAUDE_COWORK` (human names like `Claude Code` are normalized). Entity
  sources return them as **numeric tag IDs** on output. On detections, the
  filter takes the name, not the tag.
- `time_range` is sent to the API as requested; there is no pre-emptive
  client-side ceiling. LogScale event queries default to 2h when the parameter
  is omitted. Only the `entities/*` routes reject `time_range` outright.
- Agentic Graph endpoints accept both vertex keys and session UUIDs.
- Use aggregates for fleet-wide counts; use queries for individual records.
- `sensitive_only` filtering for file events is done client-side after receiving results.
- An empty `resources: []` with HTTP 200 is a valid response — it means no data
  matches the given filters. Widen `time_range` or relax filters to find data.

## Composed Tools

Some MCP tools fan out to several `/aidr` routes and merge the results. Read
this before trusting a merged result's scope or counts.

### get_guardian_agent

A single lookup: fetches one AIAgent record by its `Id` (the opaque record
token) via `entities/agents/v1` and returns it. It does **not** fan out. For a
one-shot overview of every facet, use
`generate_guardian_report(report_type='agent_detail')`.

Which follow-up key to use depends on the route:

- `search_guardian_tool_usage`, `search_guardian_executions`,
  `search_guardian_skill_usage`, `search_guardian_prompts`,
  `search_guardian_detections` and `search_guardian_tools` all take the record's
  `SensorId` (as `aid`, `agent_id` or `sensor_id`). Every one of them is
  therefore **HOST-scoped**, not agent-scoped.
- The record's `AgentIds[]` is not usable as a follow-up key. No parameter
  accepts it, and the arrays it used to join against are gone.
- `get_guardian_agent_sessions` takes **neither** — it has no agent or host
  filter, so it cannot be scoped to this agent. Use
  `search_guardian_executions(aid=...)` for the host's session grain.

### generate_guardian_report — agent_detail

Fans out from one agent (verified via `entities/agents/v1`). **Every leg is
HOST-scoped by `SensorId`/`aid`**, so every count covers all the AI agents on
that host, not just the requested one: `tools`, `executions`, `tool_usage`,
`skill_usage`, `detections`. Nothing finer exists — the entities carry no agent
filter and no longer return any reverse-relationship array.

- `tools` is the thinnest leg. The AITool store covers few hosts, so it is empty
  for most agents. `tool_usage` answers the same question from the event side and
  is far better populated.
- `max_detection_score` is matched on both `SensorId` and the product tag, so it
  IS agent-specific — but it can be `None` even when `detections` is non-empty,
  because many detections carry no `AgenticProductTag`.

There is no `sessions` leg — the agent-sessions route has no host filter, and
`executions` (keyed by `aid`, carrying `AgenticSessionId`) already covers the
host's sessions.

### get_guardian_inventory

Four aggregate rollups over a single `time_range`. `agents.by_product` counts
AGENTS; `sessions.by_product` counts logical AIAgentSession rows — a different
metric, so do not relabel one as the other. Both product buckets are keyed by
the numeric product tag ID. Read `notices` before reporting any count.

### pivot_on_guardian_attribute

Allowed attributes: `Product`, `HostName`, `Skill`, `Name`. `Product` and
`HostName` search agents; `Skill` searches skill frontmatters (substring on
name); `Name` merges per-invocation skill-usage and tool-usage, deduped by
sensor (`aid`). Returns the `{results, pagination}` envelope for every branch.
"""

ENTITY_SCHEMA_DOCUMENTATION = """\
# AI Entity Field Reference (Agentic Graph Layer)

## Reading the graph

Two shapes catch every caller out.

⚠️ **Vertices key on `__id`, never `Id`.** There is no `Id` field anywhere in the
graph. The tables below name `__id` for that reason.

⚠️ **An edge wraps its target under a differently-named key.** The edge key comes
from the table of outgoing edges (`UsedToolAitool`), but the vertex inside sits
under a short key (`AiTool`), alongside an `EventCloudTime` for the edge itself.
So the path is `UsedToolAitool[].AiTool`, not `UsedToolAitool[].AiToolVertex`. The
short keys are `AiTool`, `AiSkill`, `AiModel`, `McpServer` and `Process`.

⚠️ **Several vertices carry an enum ordinal where you expect a name**, and the
graph holds nothing that resolves it. Each one is called out below. Read names
from the flat `tools` / `skills` / `executions` keys of the same
`get_guardian_session_detail` response instead — those come from the event store
and do carry names.

## AiAgentVertex

⚠️ **Not populated.** The `SessionRunByAiagent` edge is present, but the `AiAgent`
object inside it comes back empty. This vertex has no usable fields, so no
per-agent join is possible through the graph — the same wall the removed
reverse-relationship arrays leave you at. For the agent record, call
`search_guardian_agents` or `get_guardian_agent`.

## AiSessionVertex

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `aisess:{aid}:{session_uuid}`) |
| `DisplayName` | Same string as `__id` |
| `AgenticProduct` | ⚠️ **An integer enum ordinal, not a name.** The graph layer is no better than the LogScale event here, and nothing in the graph maps the ordinal to a product. Use `Product` / `ProductName` from `get_guardian_agent_sessions` instead — you already hold that row, because its `sessionId` is what you passed to fetch this graph. |
| `AgenticSessionId` | Session UUID |

### Outgoing Edges

| Edge | Target | Description |
|------|--------|-------------|
| `UsedToolAitool` | AiToolVertex | Tools used during the session |
| `InvokesModelAimod` | AiModelVertex | Models invoked |
| `ConnectedMcpMcpsrv` | McpServerVertex | MCP servers connected |
| `LoadedSkillAiskill` | AiSkillVertex | Skills loaded |
| `SessionProcessPid` | ProcessVertex | Processes spawned by session |
| `SessionRunByAiagent` | AiAgentVertex | ⚠️ Present but empty — see AiAgentVertex |
| `ChildSessionAisess` | AiSessionVertex | Sub-agent child sessions (often null) |

## AiToolVertex

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `aitool:{aid}:{session_uuid}\\|{ordinal}`) |
| `DisplayName` | Same string as `__id`, so it also ends in the ordinal |
| `AgenticTool` | ⚠️ **An integer enum ordinal, not a name.** This vertex carries no tool name at all. Passing the ordinal to `tool_name` returns zero rows. For names, read the flat `tools` key of the same `get_guardian_session_detail` response, which carries `AgenticToolName` ("Bash", "Read", "apply_diff") next to the same `AgenticToolUseId`. |

## AiModelVertex

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `aimod:{aid}:{model_name}`) |
| `DisplayName` | Same string as `__id` |
| `AgenticModel` | Model name/identifier (e.g., "claude-sonnet-4-6"). A real name, not an ordinal. |

## AiSkillVertex

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `aiskill:{aid}:{session_uuid}\\|{slug}`) |
| `DisplayName` | Same string as `__id` |
| `AgenticSkill` | Skill name (e.g., "git:pr-create"). A real name, not an ordinal. |

## McpServerVertex

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `mcpsrv:{aid}:{session_uuid}\\|{server_name}`) |
| `DisplayName` | Same string as `__id` |

⚠️ **No name field.** The server name is only the suffix after the final `|` in
`__id` / `DisplayName` — split on it to read the name. For a fleet-wide list, use
`search_guardian_mcp_servers`.

## ProcessVertex (bridged from AI sessions)

| Field | Description |
|-------|-------------|
| `__id` | Vertex ID (format: `pid:{aid}:{upid}`) |
| `DisplayName` | Same string as `__id` |
| `CommandLine` | Full command line of the process |
| `ImageFileName` | Executable path/name |
| `SHA256HashData` | SHA256 hash of the executable |
| `ProcessStartTime` | Process start timestamp |
| `ProcessEndTime` | Process end timestamp |
| `UserName` | User who ran the process |
| `UserUid` | ⚠️ **A list, not a scalar** — it is the outgoing edge below, and it comes back unresolved. Do not read a user ID from it. |
| `Tags` | Process tags |
| `NetworkConnectCount` | Number of network connections |
| `GenericFileWrittenCount` | Number of files written |
| `DnsRequestCount` | Number of DNS requests |
| `ParentProcessId` | Parent process ID |

⚠️ **Expect nulls.** Through `get_guardian_session_detail` this vertex arrives
flat, with none of the outgoing edges below resolved, and the timestamp, count and
user fields are commonly empty. Treat every field here as optional. For the
processes an AI session launched, `get_guardian_process_tree` walks the spawn tree
and returns command lines and image filenames directly.

Note: `MD5HashData` is NOT available on ProcessVertex — use ModuleVertex for MD5 hashes.

### Outgoing Edges from ProcessVertex

| Edge | Target | Description |
|------|--------|-------------|
| `ChildProcessPid` | ProcessVertex | Child processes (recursive) |
| `Ipv4Ip4` | Ipv4Vertex | IPv4 network connections |
| `AccessedWebWeb` | WebAccessVertex | HTTP/HTTPS web access |
| `PrimaryModuleMod` | ModuleVertex | Executable being run |
| `ModuleWrittenMod` | ModuleVertex | Files/binaries written by process |
| `UserUid` | UserIdVertex | OS user who ran the process |
| `UserSessionUses` | UserSessionVertex | User session that owns the process |

### Edge Properties: ProcessIpv4Ipv4 (network connection)

| Field | Description |
|-------|-------------|
| `RemoteAddressIP4` | Remote IP address |
| `RemotePort` | Remote port number |
| `LocalAddressIP4` | Local IP address |
| `LocalPort` | Local port number |
| `Protocol` | Protocol (TCP/UDP) |
| `ConnectionDirection` | Inbound/outbound |
| `ConnectionFlags` | Connection flags |
| `EventCloudTime` | When connection was observed |

### Edge Properties: ProcessModuleWrittenModule (file write)

| Field | Description |
|-------|-------------|
| `EventCloudTime` | When file was written |
| `IsOnNetwork` | Whether file is on a network path |
| `IsOnRemovableDisk` | Whether file is on removable media |

## Ipv4Vertex


| Field | Description |
|-------|-------------|
| `Id` | Vertex ID |
| `RemoteAddressIP4` | IP address |
| `LocalAddressIP4` | Local IP address |
| `RemoteIp` | Remote IP (alternate field) |

## ModuleVertex


| Field | Description |
|-------|-------------|
| `Id` | Vertex ID |
| `ImageFileName` | File name/path |
| `SHA256HashData` | SHA256 hash |
| `MD5HashData` | MD5 hash |
| `TargetFileName` | Target file path (for written files) |

## WebAccessVertex

| Field | Description |
|-------|-------------|
| `Id` | Vertex ID |
| `HostUrl` | URL accessed |

## UserIdVertex

Reached via `UserUid` edge from ProcessVertex.

| Field | Description |
|-------|-------------|
| `Id` | Vertex ID |
| `UserName` | OS username |
| `UserSid` | Security Identifier (SID) |
| `LogonDomain` | Active Directory / domain name |
| `UserIsAdmin` | Whether the user has admin privileges |
| `LogonType` | Logon type (interactive, service, etc.) |

## UserSessionVertex

Reached via `UserSessionUses` edge from ProcessVertex.

| Field | Description |
|-------|-------------|
| `Id` | Vertex ID |
| `UserName` | OS username |
| `UserSid` | Security Identifier (SID) |
| `LogonDomain` | Active Directory / domain name |
| `UserIsAdmin` | Whether the user has admin privileges |
| `LogonType` | Logon type |
| `RemoteAddressIP4` | Remote IP if session is from a remote login |

## Edge Properties (common to all edges)

| Field | Description |
|-------|-------------|
| `EventCloudTime` | When the edge was created (cloud timestamp) |
| `Id` | Edge ID |
| `__typename` | Edge type name |
"""

AGENTIC_INVENTORY_SCHEMA_DOCUMENTATION = """\
# AI Entity & LogScale Event Field Reference

The backend splits AI telemetry across two layers:

1. **AI Entity Store** — identity and catalog entities (AIAgent, AIAgentSession,
   AITool, AISkillFrontmatter, MCPServerName, AIAgentInstallation, AIModelName,
   AIAgentOSUser). Queried by `sensor_id`/`product`/`hostname` within a
   `time_range` window on `LastSeen`.
2. **LogScale Events** — per-invocation activity (`AgenticSessionStart`,
   `AgenticToolRequest`, `AgenticUserPromptSubmit`) via `queries/executions`,
   `queries/tool-usage`, `queries/skill-usage`, `queries/prompts`. Queried by
   `aid`/`session_id` within a `time_range` window (defaults to 2h).

## Product Tag IDs

The entity-store `Product`/`AgentProduct` field is a numeric tag ID (not a
string name). Human names are accepted on query parameters and normalized
server-side.

⚠️ **Two encodings exist and must not be mixed:** entity sources (agents,
sessions, installs, models, detections) return the **tag ID**; LogScale event
sources return the product **name**. A tag ID decoded from JSON is a float whose
default string form is exponent notation — normalize to a plain integer string
before comparing, or a join silently misses.

| Product | Tag ID |
|---------|--------|
| `CLAUDE` | 213584428666145 |
| `CLAUDE_CODE` | 213584428666146 |
| `CLAUDE_COWORK` | 213584428666147 |
| `OPENCLAW` | 213584428666148 |
| `GITHUB_COPILOT` | 213584428666189 |
| `KIRO` | 213584428666190 |
| `ZERO_AGENT` | 213584428666191 |
| `MPC_BUILDER` | 213584428666192 |
| `QUICKWORK_AGENT` | 213584428666193 |
| `AGENT_ORCHA` | 213584428666194 |
| `AGENT_SMITH` | 213584428666195 |
| `ANTIGRAVITY` | 213584428666196 |
| `CODEX` | 213584428666200 |
| `CURSOR` | 213584428666201 |
| `GENERIC` | 213584428666221 |
| `MICROSOFT_COPILOT` | 213584428666293 |
| `CHATGPT_DESKTOP` | 213584428666294 |
| `WINDSURF` | 213584428666295 |
| `JETBRAINS` | 213584428666296 |
| `EXPERIMENTAL` | 213584428666297 |
| `CLINE` | 213584428666298 |
| `CONTINUE_DEV` | 213584428666299 |

## AIAgent (entity store)

Returned by `queries/agents/v1`, `entities/agents/v1`, `aggregates/agents/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Unique agent record token (opaque, e.g. `ASCWQseSk3b76g...`). Pass to `entities/agents/v1?ids=` / get_guardian_agent. |
| `AgentIds` | Array | The agent's content hash(es) (width varies). Carried in the record; not a filter parameter. |
| `SensorId` | String | CrowdStrike sensor ID (aid): a **32-hex HOST** id. Use for `aid`/`sensor_id` filters on the event and host-scoped queries. Not unique per agent. |
| `AgentName` | String | Agent name |
| `AgentProduct` | String | Product tag ID (see mapping above) |
| `AgentProductName` | String | Friendly product name (sibling of `AgentProduct`; omitted for unresolved tags) |
| `Hostname` | String | Device hostname (joined from FalconHost) |
| `SpiffeId` | String | SPIFFE workload identity |
| `LastExecutionTime` | DateTime | Last observed execution |
| `LastInventoryTime` | DateTime | Last inventory refresh |
| `FirstSeen` / `LastSeen` | DateTime | Seen window. **`LastSeen` is what `time_range` filters.** |

`CustomerId` is **never returned** by any Guardian endpoint.

## Agent Sessions — AIAgentSession (entity store)

Returned by `queries/agent-sessions/v1`, `entities/agent-sessions/v1`,
`aggregates/agent-sessions/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Session record id (use for `entities/agent-sessions/v1?ids=`) |
| `Product` | String | Product tag ID |
| `ProductName` | String | Friendly product name (sibling of `Product`; omitted for unresolved tags) |
| `Name` | String | Session name |
| `FirstSeen` / `LastSeen` | DateTime | Seen window (`LastSeen` is filtered) |
| `Cim.AIAgentSession.sessionId` | String | The AgenticSessionId (UUID) |
| `Cim.AIAgentSession.modelsInvoked` | Array | Models used in the session |
| `Cim.AIAgentSession.workingDirectory` | String | Working directory |
| `Cim.AIAgentSession.startTime` / `updatedTime` | DateTime | Session timing |

`SensorId` and `AIAgentIds` are **not returned** — they are never populated on
this entity upstream.

## Executions — LogScale `AgenticSessionStart`

Returned by `queries/executions/v1`, `entities/executions/v1`. One row per
process invocation.

| Field | Type | Description |
|-------|------|-------------|
| `AgenticSessionId` | String | Session UUID (**flat** — drill into the graph with this) |
| `AgenticModel` | String | LLM model used |
| `AgenticWorkingDirectory` | String | Working directory path |
| `AgenticInputTokens` | Number | Input token count |
| `AgenticOutputTokens` | Number | Output token count |
| `ContextProcessId` | String | Context process ID |
| `ProcessTags` | Multi-value | Product tag ID(s) for the process |
| `aid` | String | Sensor ID (no hyphens) |
| `timestamp` | Number | Event time (epoch milliseconds) |

## Tool Usage — LogScale `AgenticToolRequest`

Returned by `queries/tool-usage/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `AgenticSessionId` | String | Session this tool was used in |
| `AgenticTool` | String | Tool type (numeric enum) |
| `AgenticToolName` | String | Tool name (e.g., "Bash", "Read", "Write", "Edit") |
| `AgenticToolUseId` | String | Unique tool use identifier |
| `AgenticPath` | String | File path (Read/Write/Edit/Glob tools) |
| `AgenticDescription` | String | Agent's stated purpose for this tool use |
| `AgenticPattern` | String | Pattern for Glob/Grep tools |
| `AgenticQuery` | String | Search query for Grep/WebSearch tools |
| `AgenticSkill` | String | Skill name for the Skill tool |
| `CommandLine` | String | Command line/arguments (Bash tool) |
| `Url` | String | URL for WebFetch/WebSearch tools |
| `aid` | String | Sensor ID |

## Tool Catalog — AITool (entity store)

Returned by `queries/tools/v1`, `aggregates/tools/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Tool record id |
| `Name` | String | Tool name |
| `SensorId` | String | The tool's host sensor ID |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

## Skills — AISkillFrontmatter (entity store)

Returned by `queries/skills/v1`, `aggregates/skills/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Skill frontmatter record id |
| `SkillName` | String | Skill name |
| `SkillDescription` | String | Skill description |
| `SkillDirectoryHash` | String | Content hash of the skill directory |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

Per-invocation skill events come from LogScale (`queries/skill-usage/v1`):
`AgenticSessionId`, `AgenticSkill`, `AgenticToolUseId`, `aid`.

## MCP Server Names — MCPServerName (entity store)

Returned by `queries/mcp-server-names/v1`. **Fleet-wide, no agent filter.**

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | MCP server name record id (a hashed dedup key) |
| `Cim.MCPServerName.serverName` | String | Human-friendly server name |
| `LastUsedTime` / `LastInventoryTime` | DateTime | Usage/inventory timing |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

## OS Users — AIAgentOSUser (entity store)

Returned by `queries/agent-os-users/v1`, `entities/agent-os-users/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Aid` | String | Host sensor ID |
| `Username` | String | OS username |
| `ObjectSid` | String | AD security identifier |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

## Model Names — AIModelName (entity store)

Returned by `queries/model-names/v1`. **Fleet-wide, only `time_range` filters.**

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Model name record id (a hashed dedup key) |
| `Cim.AIModelName.modelName` | String | Human-friendly model name |
| `LastUsedTime` / `LastInventoryTime` | DateTime | Usage/inventory timing |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

## Prompts — LogScale `AgenticUserPromptSubmit`

Returned by `queries/prompts/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `AgenticPrompt` | String | The user prompt text |
| `AgenticSessionId` | String | Session the prompt belongs to |
| `aid` | String | Sensor ID (a HOST) |
| `timestamp` | String | Epoch **milliseconds as a STRING**, not a number. Coerce with `int()` before comparing or sorting |
| `ProcessTags` | Multi-value | Product tag ID(s) for the emitting process |

To name a session by its opening prompt: group by `AgenticSessionId` and take the
row with `min(int(timestamp))`.

## Installs — AIAgentInstallationView (entity store)

Returned by `queries/agent-installations/v1`.

| Field | Type | Description |
|-------|------|-------------|
| `Id` | String | Install record id |
| `SensorId` | String | Host sensor ID |
| `Hostname` | String | Device hostname |
| `AgentName` / `AgentProduct` | String | Agent name / product tag ID |
| `AgentProductName` | String | Friendly product name (sibling of `AgentProduct`; omitted for unresolved tags) |
| `AgentVersion` | String | Installed version |
| `InstallSource` | String | Where the install came from |
| `AgentDeclarationPath` / `BinaryPath` | String | On-disk paths |
| `FileSha256` | String | Binary SHA256 |
| `LastExecutionTime` / `LastInventoryTime` | DateTime | Timing |
| `FirstSeen` / `LastSeen` | DateTime | Seen window |

## Time Filtering

All `queries/*` and `aggregates/*` accept `time_range`. Entity-store sources
filter `LastSeen`; LogScale event queries (executions, tool-usage, skill-usage,
prompts) default to **2 hours** when omitted:

```
GET /aidr/queries/tool-usage/v1?time_range=7d
```

There is no pre-emptive ceiling in Guardian's code; the requested window is
sent to the API as asked, and the API decides what it will serve (see the
"Time windows" section of the query guide for the retry ladder used when it
refuses). Only the `entities/*` routes reject `time_range` outright.

## Cross-Layer Linkage

The Agentic Graph endpoints resolve an `AgenticSessionId` UUID to its vertex key
automatically. A vertex key `aisess:{aid}:{AgenticSessionId}` is also accepted.
"""


EXAMPLE_QUERIES_DOCUMENTATION = """\
# Example Guardian API Calls

## AI Entity & Event Examples

### 1. List all AI agents (last 7 days)

```
GET /aidr/queries/agents/v1?time_range=7d&limit=50
```

Returns all agent instances active in the last 7 days. `7d` is just an
example value here, not a maximum; see "Time windows" in the query guide.

### 2. List agents filtered by product

```
GET /aidr/queries/agents/v1?product=CLAUDE_CODE&time_range=7d&limit=10
```

### 3. List agents filtered by hostname

```
GET /aidr/queries/agents/v1?hostname=dev-laptop-01&time_range=7d
```

### 4. Get agent details by ID

```
GET /aidr/entities/agents/v1?ids=<agent_id>
```

`<agent_id>` is the opaque `Id` record token from a search result, not the
32-hex SensorId and not the AgentIds[] content-hash value.

### 5. List agent sessions (optionally by product)

```
GET /aidr/queries/agent-sessions/v1?product=CLAUDE_CODE&time_range=7d&limit=20
```

There is **no host/sensor filter** on this route. To find the sessions on a
specific host, use the per-process executions instead (keyed by `aid`, carrying
`AgenticSessionId`): `GET /aidr/queries/executions/v1?aid=<aid>&time_range=7d`.
Each session row carries the nested `Cim.AIAgentSession` (sessionId,
modelsInvoked, workingDirectory).

### 6. List per-process executions for a session

```
GET /aidr/queries/executions/v1?session_id=<session_id>&time_range=7d
```

Returns the flat `AgenticSessionId`, `AgenticModel`, and token counts per
process invocation. Also filterable by `aid`.

### 7. Get execution detail by session id

```
GET /aidr/entities/executions/v1?id=<session_id>
```

### 8. List tool usage for a session (per-invocation)

```
GET /aidr/queries/tool-usage/v1?session_id=<session_id>&time_range=7d&limit=100
```

### 9. List Bash tool usage across fleet

```
GET /aidr/queries/tool-usage/v1?tool_name=Bash&time_range=7d&limit=50
```

### 10. List the tool inventory for a host (AITool entity)

```
GET /aidr/queries/tools/v1?sensor_id=<aid>&time_range=7d&limit=100
```

### 11. List skill frontmatters (fleet inventory)

```
GET /aidr/queries/skills/v1?name_filter=review&time_range=7d
```

### 12. List per-invocation skill usage

```
GET /aidr/queries/skill-usage/v1?name=code-review&session_id=<session_id>&time_range=7d
```

`name` is an exact match on `AgenticSkill`.

### 13. List OS users that ran agents

```
GET /aidr/queries/agent-os-users/v1?aid=<aid>&time_range=7d
```

Also filterable by `username` and `object_sid`.

### 14. List MCP server names (fleet-wide)

```
GET /aidr/queries/mcp-server-names/v1?time_range=7d&limit=100
```

No agent/sensor filter.

### 15. Search prompts within a session

```
GET /aidr/queries/prompts/v1?session_id=<session_id>&time_range=7d
```

### 16. Fleet aggregates

```
GET /aidr/aggregates/agents/v1?time_range=7d
GET /aidr/aggregates/agent-sessions/v1?time_range=7d
GET /aidr/aggregates/tools/v1?time_range=7d&limit=100
GET /aidr/aggregates/skills/v1?time_range=7d
GET /aidr/aggregates/detections/v1?time_range=7d
```

The agents and agent-sessions aggregates group **by product tag ID**;
agent-sessions returns `count` as a JSON string.

## Agentic Graph Examples

### 17. Get full session activity (tools, models, processes, skills)

```
GET /aidr/entities/session-activity/v1?ids=aisess:aabbccdd:session-uuid
```

Also accepts plain session UUIDs (server resolves vertex key):

```
GET /aidr/entities/session-activity/v1?ids=session-uuid-here
```

### 18. Get process tree (depth 2)

```
GET /aidr/entities/process-tree/v1?id=aisess:aabbccdd:session-uuid&depth=2
```

### 19. Get network connections from session

```
GET /aidr/entities/network-events/v1?id=aisess:aabbccdd:session-uuid
```

### 20. Get file write activity from session

```
GET /aidr/entities/file-events/v1?id=aisess:aabbccdd:session-uuid
```

## Common Patterns

### Fleet Inventory (combine aggregate calls)

Call these in parallel for a fleet overview. `time_range` is sent as
requested on each call; if a route refuses a wide window, Guardian retries
narrower and reports it in `notices`:
```
GET /aidr/aggregates/agents/v1?time_range=7d
GET /aidr/aggregates/agent-sessions/v1?time_range=7d
GET /aidr/aggregates/tools/v1?time_range=7d&limit=100
GET /aidr/aggregates/detections/v1?time_range=7d
```
The agents and agent-sessions aggregates both group **by product tag ID**;
agent-sessions `count` is a JSON string.

### Agent Investigation (drill down)

1. Find the agent: `GET /aidr/queries/agents/v1?hostname=suspect-host&time_range=7d`
2. Get its sessions on the host (executions are keyed by `aid` and carry
   `AgenticSessionId`): `GET /aidr/queries/executions/v1?aid=<aid>&time_range=7d`
3. Get session activity: `GET /aidr/entities/session-activity/v1?ids=<session_id>`
4. Get process tree: `GET /aidr/entities/process-tree/v1?id=<session_id>&depth=3`
5. Get network events: `GET /aidr/entities/network-events/v1?id=<session_id>`
6. Get detections for the host: `GET /aidr/queries/detections/v1?agent_id=<aid>&time_range=7d`

### Pivot from known attribute

Find all agents on a specific host:
```
GET /aidr/queries/agents/v1?hostname=prod-server-01&time_range=7d
```

Find skill frontmatters matching a pattern:
```
GET /aidr/queries/skills/v1?name_filter=review&time_range=7d
```

### Detections involving AI agents

What fired in the last 7 days:
```
GET /aidr/queries/detections/v1?time_range=7d&limit=50
```

For one host (⚠️ `agent_id` here takes the 32-hex **SensorId**, not `AIAgent.Id`):
```
GET /aidr/queries/detections/v1?agent_id=<aid>&time_range=7d
```

Agentic Threat Score per agent:
```
GET /aidr/aggregates/detections/v1?time_range=7d
```
Join each row onto agents with **BOTH** keys —
`AgentId == AIAgent.SensorId` AND `AgenticProductTag == AIAgent.AgentProduct`. A
SensorId-only join mis-attributes one host's worst detection to every agent on
that host. Rows with a null `AgenticProductTag` cannot be attributed at all.

### Installs and models

```
GET /aidr/queries/agent-installations/v1?sensor_id=<aid>&product=CODEX&time_range=7d&limit=50
GET /aidr/queries/model-names/v1?time_range=7d
```
`model-names` is fleet-wide with only a `time_range` filter. For the model used
per session, prefer `queries/agent-sessions/v1`
(`Cim.AIAgentSession.modelsInvoked`) or `queries/executions/v1`
(`AgenticModel`).
"""
