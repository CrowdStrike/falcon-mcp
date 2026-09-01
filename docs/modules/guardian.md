<!-- meta:title Guardian -->
<!-- meta:description Provides tools for querying AI agent inventory and activity data -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Provides tools for querying AI agent inventory and activity data

## API Scopes

- `AIDR:read`

## Tools

### `falcon_search_guardian_agents`

**Required scopes:** `AIDR:read`

List AI agents from the AIAgent entity store.

Use this to find agents by product or hostname. Returns full agent
records, including the opaque record token `Id` (pass to
get_guardian_agent), the 32-hex `SensorId` (`== aid`, identifies the
HOST), and the `AgentIds[]` content hash(es) (width varies). See
falcon://guardian/inventory/schema-guide for the full field reference
and the `Id` vs `SensorId` vs `AgentIds` distinction.

**Example prompts:**

- "List AI agents running Claude Code in the last 7 days"
- "Find AI agents on hostname WORKSTATION-42"

### `falcon_get_guardian_agent`

**Required scopes:** `AIDR:read`

Get a specific AI agent's record from the AIAgent entity store.

Use when you have an AIAgent `Id` (the opaque record token from a
search result, not the 32-hex `SensorId`/`aid` and not the
`AgentIds[]` content-hash value) and want the full agent record. The record carries
`SensorId`, which the host-scoped follow-up tools
(get_guardian_agent_sessions, search_guardian_tools,
search_guardian_tool_usage, search_guardian_detections) take as
`aid`/`sensor_id`. For a one-shot overview of every facet, use
generate_guardian_report with report_type='agent_detail'. For
discovering agents by criteria, use search_guardian_agents instead.

**Example prompts:**

- "Show the record for that AI agent instance"

### `falcon_search_guardian_mcp_servers`

**Required scopes:** `AIDR:read`

List MCP server names observed across the fleet (MCPServerName entity).

Use this to see which MCP servers agents have connected to. The
human-friendly server name lives in `Cim.MCPServerName.serverName` (the
`Id` is only a hashed dedup key). The endpoint carries no agent/sensor
filter, so this is fleet-wide. To see which MCP servers a single session
connected to, use get_guardian_session_detail (its activity graph
exposes them under `ConnectedMcpMcpsrv`).

**Example prompts:**

- "Which MCP servers have AI agents connected to across the fleet?"

### `falcon_get_guardian_agent_sessions`

**Required scopes:** `AIDR:read`

List AI agent sessions across the fleet, filtered by product.

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

**Example prompts:**

- "Show me AI agent sessions for the CLAUDE_CODE product from the past 24 hours"
- "How many Cursor sessions ran across the fleet this week?"

### `falcon_get_guardian_session_detail`

**Required scopes:** `AIDR:read`

Get detailed information about a specific AI session.

Use when you have an AgenticSessionId (UUID) and need full context. For
discovering sessions by criteria, use get_guardian_agent_sessions
instead. Returns the session's process executions plus the
per-invocation tools and skills used. When `include_activity` is true,
also returns the threat-graph activity (which adds processes, models,
MCP servers, and child sessions as edges).

**Example prompts:**

- "Show full details for that AI session"

### `falcon_get_guardian_session_activity`

**Required scopes:** `AIDR:read`

Get activity for one or more AI sessions.

Use this to see full graph relationships including tools, models, processes,
sub-agents, and MCP servers. Accepts vertex IDs or inventory session IDs.
Returns session activity with all connected graph entities.

**Example prompts:**

- "Show the full activity graph for that session — tools, models, and processes"

### `falcon_search_guardian_tools`

**Required scopes:** `AIDR:read`

List AI tools from the AITool entity store — the inventory of which tools exist.

Use this to see what tools are present. A tool cannot be attributed to a
single agent: rows are flat (`Id`, `Name`, `SensorId`, the seen
timestamps) and there is no per-agent filter, so `sensor_id` narrows to
the tool's host, which covers every agent on it. Coverage is also thin —
the store spans few hosts, so most agents match nothing here. For the
tools an agent's host actually invoked, prefer
search_guardian_tool_usage(aid=...), which also carries file paths and
command lines.

**Example prompts:**

- "List the AI tool inventory across the fleet"
- "Which tools exist on that host?"

### `falcon_search_guardian_tool_usage`

**Required scopes:** `AIDR:read`

List AI tool usage from LogScale AgenticToolRequest events.

Use this to find tool invocations by name, sensor (aid), or session;
the default window is 2 hours, so widen `time_range` explicitly for
anything beyond current activity, up to the 7-day maximum this route
allows (it scans raw LogScale events; a wider window is refused and the
ladder narrows it back to 7d). Returns tool usage records
(AgenticToolName, AgenticPath, CommandLine, aid). If the requested
window had to be narrowed, the result is `{results, notices}` instead
of a bare list; read `notices` before reporting counts.

**Example prompts:**

- "Find every Bash tool invocation in the last 7 days"
- "Show tool usage for that session"

### `falcon_search_guardian_executions`

**Required scopes:** `AIDR:read`

List AI agent process executions, with the model and token counts for each.

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

**Example prompts:**

- "Show the per-process executions for that session"
- "How many input and output tokens did that session use?"
- "Which models and token counts did that agent's processes use?"

### `falcon_search_guardian_prompts`

**Required scopes:** `AIDR:read`

Search for AI prompts within a session (LogScale AgenticUserPromptSubmit).

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

**Example prompts:**

- "Show me the prompts from that session"

### `falcon_get_guardian_inventory`

**Required scopes:** `AIDR:read`

Get a summary overview of AI activity in your environment.

Use this for a high-level fleet snapshot: agent counts by product,
session counts by product, top tools by name, and a detection summary.
`agents.by_product` counts AGENTS while `sessions.by_product` counts
logical AIAgentSession rows — different metrics, so do not relabel one
as the other. Both product buckets are keyed by the friendly product
name (e.g. "Claude Code") when the API resolves the tag, falling back to
the numeric tag ID for unrecognized products. Read `notices` before
reporting any count.

**Example prompts:**

- "Give me a summary of AI activity across the fleet"

### `falcon_search_guardian_skills`

**Required scopes:** `AIDR:read`

List AI skill frontmatters (AISkillFrontmatterView entity).

Use this for the fleet-wide inventory of skills. Each row carries
`SkillName`, `SkillDescription`, and the seen timestamps; the endpoint
has no agent_id filter. For per-invocation skill events, use
search_guardian_skill_usage instead.

**Example prompts:**

- "List the AI skill frontmatters matching 'review'"

### `falcon_search_guardian_skill_usage`

**Required scopes:** `AIDR:read`

List per-invocation AI skill events (LogScale AgenticToolRequest).

Use this for the session-scoped grain of skill invocations
(`AgenticSkill`, `AgenticSessionId`, `aid`), distinct from the
AISkillFrontmatter inventory (search_guardian_skills). The default
window is 2 hours, so widen `time_range` explicitly for older activity,
up to the 7-day maximum this route allows (it scans raw LogScale events;
a wider window is refused and the ladder narrows it back to 7d).

**Example prompts:**

- "Show every invocation of the code-review skill in the last 7 days"

### `falcon_get_guardian_fleet_skill_inventory`

**Required scopes:** `AIDR:read`

Get a fleet-wide skill usage rollup by name (AISkill aggregate).

Use this to see which skills are most used, optionally filtered by name
pattern. Returns grouped `{SkillName, count}` buckets. This is an
aggregate with no server-side pagination; `limit` is applied
client-side. For the per-skill records, use search_guardian_skills
instead.

**Example prompts:**

- "Which skills are most used across all AI agents?"

### `falcon_search_guardian_os_users`

**Required scopes:** `AIDR:read`

List OS users that have run AI agents (AIAgentOSUser entity).

Use this to find which OS accounts ran agents, by sensor, username, or
AD ObjectSid.

**Example prompts:**

- "Which OS users have run AI agents on that host?"

### `falcon_pivot_on_guardian_attribute`

**Required scopes:** `AIDR:read`

Pivot from a known attribute value to the agents or activity carrying it.

Use this to pivot from a known attribute to the agents (or activity)
with that value:

- `Product` — agents of a product (value normalized like
  search_guardian_agents).
- `HostName` — agents on a host.
- `Skill` — skill frontmatters matching a name pattern (substring).
- `Name` — merges per-invocation skill-usage and tool-usage, deduped
  by sensor (`aid`); rows without an `aid` are all kept.

Returns the `{results, pagination}` envelope for every branch.

**Example prompts:**

- "Find all agents running the CLAUDE_CODE product"
- "Show every agent that used the git-commit skill"

### `falcon_get_guardian_process_tree`

**Required scopes:** `AIDR:read`

Get the spawned process tree for an AI session.

Use this to see what processes an AI session launched. Returns process
tree with command lines, image filenames, and timestamps.

**Example prompts:**

- "Show the process tree spawned by that AI session"

### `falcon_get_guardian_network_events`

**Required scopes:** `AIDR:read`

Get outbound network connections from an AI session's processes.

Use this to see what network activity an AI session generated.
Returns destination IPs, ports, protocols, and timestamps.

**Example prompts:**

- "What outbound connections did that AI session make?"

### `falcon_get_guardian_file_events`

**Required scopes:** `AIDR:read`

Get file activity for processes spawned from an AI session.

Use this to see files written by spawned processes and file tool
usage; use `sensitive_only` to filter to credential and secret paths.
Returns combined file events from the graph and inventory layers.
The graph leg has no time dimension; `time_range` applies only to
the tool-usage leg, which defaults to 2 hours.

**Example prompts:**

- "Show files written by that session's processes"
- "Did that session touch any credential or secret files?"

### `falcon_get_guardian_classified_file_access`

**Required scopes:** `AIDR:read`

Get classified/sensitive file access for an AI agent process.

Use this to see which files a process accessed that Falcon Data
Protection (FDP) classified, and whether it triggered a data
protection policy violation. Returns data pattern categories (PII,
credentials, etc.), classification policy names, rule actions
(allowed/blocked), and individual file details (path, name, SHA256,
timestamps).

**Example prompts:**

- "What sensitive files did that process access?"
- "Did that process trigger any data protection policy violations?"

### `falcon_generate_guardian_report`

**Required scopes:** `AIDR:read`

Generate a structured Guardian report.

Use this to produce fleet_summary, agent_detail, skill_threat, or
sensitive_access reports; agent_detail requires agent_id.
`time_range` applies only to fleet_summary and sensitive_access; the
other two types use their own per-leg windows. Returns a structured
report with timestamp and data.

**Example prompts:**

- "Generate a fleet summary report for the last 7 days"
- "Produce an agent detail report for that instance"

### `falcon_search_guardian_detections`

**Required scopes:** `AIDR:read`

List detections involving AI agent processes.

Use this to find security detections (alerts) that involved an AI
agent; every row is agent-related, scoped server-side and not
client-controllable. `agent_id` takes the 32-hex SENSOR/host ID
(`== AIAgent.SensorId`/`aid`), NOT the 64-hex `AIAgent.Id` — passing
the latter returns zero rows with no error, and because it identifies
a host, a detection cannot be pinned to one agent on a multi-agent
host. See falcon://guardian/events/query-guide for the full field
reference and a `product` filter trap: it takes the product name,
not the numeric tag value the API itself returns in responses.

**Example prompts:**

- "What AI-agent detections fired in the last 30 days?"
- "Show detections involving Kiro agents"

### `falcon_get_guardian_detection_scores`

**Required scopes:** `AIDR:read`

Get the Agentic Threat Score for each agent.

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

**Example prompts:**

- "What's the agentic threat score for each agent?"

### `falcon_search_guardian_installs`

**Required scopes:** `AIDR:read`

List AI agent installations (AIAgentInstallationView entity).

Use this to find install records by sensor, product, or hostname.
Returns `Id`, `SensorId`, `Hostname`, `AgentName`, `AgentProduct`,
`AgentVersion`, `InstallSource`, `AgentDeclarationPath`, `BinaryPath`,
`FileSha256`, `LastExecutionTime`, and the seen timestamps — see
falcon://guardian/inventory/schema-guide for the full field reference.

**Example prompts:**

- "What AI agent installations are on that host?"

### `falcon_search_guardian_models`

**Required scopes:** `AIDR:read`

List AI model names (AIModelName entity).

Returns the human-friendly model name in `Cim.AIModelName.modelName`
(the `Id` is only a hashed dedup key) and the seen timestamps. There is
no name/product/sensor scalar to filter on, so the only server-side
filter is `time_range` on LastSeen. For the model used per session,
prefer get_guardian_agent_sessions (its
`Cim.AIAgentSession.modelsInvoked`) or search_guardian_executions (its
`AgenticModel`). This tool reports no usage volume — for per-process
model plus token counts (`AgenticInputTokens`/`AgenticOutputTokens`), use
search_guardian_executions.

**Example prompts:**

- "List the AI models observed across the fleet"

## Resources

- **`falcon://guardian/events/query-guide`**: Guardian API reference for the AI entity and LogScale event query endpoints. Use this when choosing endpoints and parameters for the Guardian tools.
- **`falcon://guardian/entities/schema-guide`**: AI vertex and edge field reference. Shows available fields for AIAgent, AISession, AITool, AIModel, AISkill, MCPServer, AIPrompt entities.
- **`falcon://guardian/inventory/schema-guide`**: AI entity and LogScale event field reference. Shows available fields for the AIAgent/AIAgentSession/AITool/AISkillFrontmatter/MCPServerName/AIAgentInstallation/AIModelName/AIAgentOSUser entity store and the LogScale AgenticSessionStart/AgenticToolRequest/AgenticUserPromptSubmit events.
- **`falcon://guardian/events/examples-guide`**: Example Guardian queries for common AI activity questions. Reference these when choosing Guardian tools and parameters.
