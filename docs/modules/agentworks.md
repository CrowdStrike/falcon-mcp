<!-- meta:title AgentWorks -->
<!-- meta:description Calling, listing, and observing CrowdStrike AgentWorks (agentic-studio) Charlotte AI agents and their execution traces -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Calling, listing, and observing CrowdStrike AgentWorks (agentic-studio) Charlotte AI agents and their execution traces

## API Scopes

- `Charlotte AI Agent Definition:read`
- `Charlotte AI Agent Definition:write`

## Tools

### `falcon_search_agentworks_agents`

**Required scopes:** `Charlotte AI Agent Definition:read`

Search for AgentWorks (Charlotte AI) agents in your CrowdStrike environment.

Use this to list agents and find their IDs and active versions before invoking
one or inspecting its versions. Filter by template, backing model, or published
version — consult falcon://agentworks/agents/fql-guide before constructing filter
expressions. Returns full agent details including active version and published
version IDs.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).

**Example prompts:**

- "List my AgentWorks agents"
- "Which agents run on the claude-4-6-sonnet model?"

### `falcon_search_agentworks_agent_versions`

**Required scopes:** `Charlotte AI Agent Definition:read`

Search for versions of AgentWorks agents.

Use this to list an agent's versions (filter by `agent_id`) and find a specific
`version_id` — for example to invoke a non-published version by passing that
version_id to falcon_invoke_agentworks_agent. Filter by agent, name, model, or
published/enabled state — consult falcon://agentworks/agent-versions/fql-guide
before constructing filter expressions. Returns full version details.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).

**Example prompts:**

- "Show me all versions of agent 467e856f"
- "Find the published versions of this agent"

### `falcon_search_agentworks_spans`

**Required scopes:** `Charlotte AI Agent Definition:read`

Search AgentWorks execution spans (traces) for observability.

This is effectively a trace-scoped tool: spans number in the hundreds of
thousands, so ALWAYS filter — the primary use is passing an invocation's
`ai_trace_id` as `trace_id:'<value>'` to retrieve that run's spans (LLM calls,
agent steps, cost, request/response content). You can further narrow by
span_type, status, name, or duration_ms; note start_time is limited to the last
90 days. Consult falcon://agentworks/spans/fql-guide before constructing filter
expressions. Returns full span details.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count).

**Example prompts:**

- "Show the spans for trace abc123"
- "Find errored LLM spans in trace abc123"

### `falcon_get_agentworks_agent_invocation`

**Required scopes:** `Charlotte AI Agent Definition:read`

Get the current state of an AgentWorks agent invocation by ID.

Use this to resume or observe a run that paused (waiting_for_tool_approval) or
that timed out from falcon_invoke_agentworks_agent — poll it until `status` is
terminal (completed/failed). Returns the invocation resource including status,
conversation, ai_trace_id, and any tool approvals.

**Example prompts:**

- "Check the status of invocation inv-123"

### `falcon_invoke_agentworks_agent`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Charlotte AI Agent Definition:read`, `Charlotte AI Agent Definition:write`

Invoke an AgentWorks (Charlotte AI) agent and return its reply.

Use this to actually run an agent on a prompt: it invokes the agent's published
version, or a specific version when you pass version_id. This is asynchronous and
spends credits — it starts the run and blocks, polling until the agent finishes
(timeout FALCON_MCP_AGENTWORKS_TIMEOUT, default 45s, kept under the MCP client
request timeout). Returns the invocation id, status, conversation, and ai_trace_id —
feed ai_trace_id to falcon_search_agentworks_spans to observe the run. If the run
pauses for tool approval (approving a tool is not supported) or exceeds the timeout,
it returns the id and status so you can resume or observe the run with
falcon_get_agentworks_agent_invocation; the run continues server-side either way.

**Example prompts:**

- "Run the IOC review agent with the prompt 'Reply OK'"
- "Invoke agent 467e856f and summarize today's critical detections"
- "Test version v-42 of this agent with the prompt 'Reply OK'"

## Resources

- **`falcon://agentworks/agents/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_agentworks_agents` tool.
- **`falcon://agentworks/agent-versions/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_agentworks_agent_versions` tool.
- **`falcon://agentworks/spans/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_agentworks_spans` tool.
