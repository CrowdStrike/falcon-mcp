<!-- meta:title Dynamic Mode -->
<!-- meta:description Reduce context usage by exposing two meta-tools instead of all module tools. -->
<!-- meta:section usage -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP server registers one tool schema per tool across all enabled modules. As the module
set grows, this balloons the context window that AI clients must hold in every conversation — even
for tools that will never be called in that session.

Dynamic mode solves this by replacing the full tool surface with two meta-tools:
`falcon_search_tools` to discover tools on demand and `falcon_execute_tool` to run them. The agent
fetches the schema for exactly the tools it needs, paying a short discovery round-trip instead of a
large up-front context cost. A third always-on tool, `falcon_list_enabled_modules`, remains
available to help orient the agent before it starts searching.

> [!NOTE]
> Dynamic mode is in public preview. The feature flag and behavior are stable, but feedback is
> welcome through [GitHub Issues](https://github.com/CrowdStrike/falcon-mcp/issues).

## Enabling Dynamic Mode

**Command-line flag:**

```bash
falcon-mcp --dynamic
```

**Environment variable:**

```bash
export FALCON_MCP_DYNAMIC=true
falcon-mcp
```

**In `.env` file:**

```bash
FALCON_MCP_DYNAMIC=true
```

Dynamic mode can be combined with any other flag, including `--modules` to restrict which modules
are loaded into the catalog and `--transport` to choose the server transport.

## How It Works

With dynamic mode enabled, the server exposes two meta-tools plus the `falcon_list_enabled_modules`
core tool, instead of the full module surface:

| Tool | Purpose |
|------|---------|
| `falcon_search_tools` | Discover tools by keyword, module name, or parameter name |
| `falcon_execute_tool` | Execute a discovered tool by name with the given parameters |
| `falcon_list_enabled_modules` | List which modules are loaded in the current server |

The typical agent workflow is:

1. Call `falcon_search_tools` with a keyword or module name to find relevant tools and their
   parameter schemas.
2. Call `falcon_execute_tool` with the tool name and parameters to run it.

Because `falcon_execute_tool` is a general dispatcher, it carries no read-only safety annotation by
default — the agent must rely on the `read_only` and `destructive` fields returned by
`falcon_search_tools` to understand a tool's mutation risk before executing it.

## Discover → Execute Example

**Step 1 — Find the right tool:**

```json
{
  "tool": "falcon_search_tools",
  "arguments": {
    "query": "search detections",
    "module": "detections"
  }
}
```

The response includes the tool name, a description, and its full parameter schema with FQL field
hints already inlined for filter parameters.

**Step 2 — Execute it:**

```json
{
  "tool": "falcon_execute_tool",
  "arguments": {
    "tool_name": "falcon_search_detections",
    "parameters": {
      "filter": "severity_name:'Critical'+status:'new'",
      "limit": 10
    }
  }
}
```

Results are returned in full. Use each tool's `limit` parameter to control result volume and
avoid large responses.

## Search Tips

`falcon_search_tools` supports keyword and module filtering:

```json
{ "query": "host containment", "limit": 5 }
```

```json
{ "module": "intel", "limit": 20 }
```

```json
{ "query": "quarantine release" }
```

If no tools match, the response lists available module names so the agent can narrow its query.

## When to Use Dynamic Mode

Dynamic mode is a good fit when:

- You enable a large number of modules and want to keep the context window lean.
- Your AI client has a limited context budget or charges per token of registered tool schemas.
- The agent only needs a small subset of tools per session but you want the full module set available.

The trade-off is the extra `falcon_search_tools` round-trip before every new tool call. For sessions
that call a stable, known set of tools repeatedly, the overhead adds up. For exploratory or broad
security-analysis workflows, dynamic mode often pays for itself quickly.
