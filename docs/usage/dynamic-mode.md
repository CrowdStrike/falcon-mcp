<!-- meta:title Dynamic Mode -->
<!-- meta:description Reduce context usage by exposing three meta-tools instead of all module tools. -->
<!-- meta:section usage -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP server registers one tool schema per tool across all enabled modules. As the module
set grows, this balloons the context window that AI clients must hold in every conversation — even
for tools that will never be called in that session.

Dynamic mode solves this by replacing the full tool surface with two meta-tools:
`falcon_search_tools` to look up a tool's parameter schema and `falcon_execute_tool` to run it. The
agent fetches the schema for exactly the tools it needs, paying a short discovery round-trip instead
of a large up-front context cost. A third always-on tool, `falcon_list_enabled_tools`, returns the
complete inventory of served tool names.

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

With dynamic mode enabled, the server exposes two meta-tools plus the `falcon_list_enabled_tools`
core tool, instead of the full module surface:

| Tool | Purpose |
|------|---------|
| `falcon_list_enabled_tools` | List every capability tool this server serves, grouped by module (meta-tools excluded) |
| `falcon_search_tools` | Look up the parameters of tools matching a keyword or module |
| `falcon_execute_tool` | Execute a discovered tool by name with the given parameters |

The typical agent workflow is:

1. Call `falcon_list_enabled_tools` when you need to know what the server serves at all — a name
   absent from that list is not available, whether because its module is off or a tool filter
   withholds it. Its `by_module` map also publishes the module names `falcon_search_tools` accepts.
2. Call `falcon_search_tools` with a keyword or module name to get the parameters of the tools you
   intend to use, along with their `read_only` and `destructive` flags.
3. Call `falcon_execute_tool` with the tool name and parameters to run it.

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
hints already inlined for filter parameters, wrapped in a `results` list alongside `total` and
`truncated`.

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

Results are ordered by relevance. A tool whose name matches the query outranks one that only
mentions it in its description, and an exact tool name — with or without the `falcon_` prefix —
ranks first. Ordering is deterministic: the same query returns the same order on every server
process. A query with no keywords (module browsing) is ordered by tool name.

Every token in `query` is matched against the tool's name, description, module, and parameter
names. Tools matching every token are preferred; when no tool matches all of them, the search falls
back to tools matching at least one, so a phrase like `real-time response command` returns ranked
candidates instead of nothing. The `hint` field says when that fallback was used — treat those
results as looser and check the top few. Ranking is what makes the wider set usable, so prefer the
first results rather than scanning the whole list.

`module` ignores case and separators, so `hostgroups`, `host_groups`, and `Host-Groups` all select
the same module. `falcon_list_enabled_tools` returns a `by_module` map whose keys are the exact
module names this server accepts; it is derived from the same catalog the search serves, so it
cannot drift from what `module` will match.

Every response carries `total` (the number of tools matching the query, before any limit) and
`truncated`, so a capped result set is never mistaken for the complete set. When results are
truncated, raise `limit` (up to 500) or narrow the query.

If no tools match, no word in the query appears anywhere in the served surface. The response says so
and points at `falcon_list_enabled_tools`. A capability absent from that full inventory is not served
by that server — report that rather than searching again.

## Tool Filtering in Dynamic Mode

`--read-only`, `--tools`, and `--exclude-tools` apply here as they do in normal mode: a withheld
tool is absent from `falcon_search_tools` and cannot be run through `falcon_execute_tool`. Omitting
it from the catalog is the enforcement, so the executor is not a bypass.

Because a withheld tool is missing rather than flagged, its absence would otherwise be
indistinguishable from a tool that never existed — leading an agent to tell the user the capability
does not exist when the operator simply disabled it. This matters here in particular: dynamic mode
dispatches by name, so an agent can name a withheld tool, whereas in normal mode the tool is not in
`tools/list` at all. Two things prevent the misreport:

- `falcon_execute_tool` on a withheld name reports that the tool exists but the server's
  configuration withholds it, naming the single rule responsible — `read-only` or `deny-list`, not
  every rule the server has enabled — so an operator debugging their config is pointed at the right
  flag. A name that was never served still returns the plain unknown-tool error, so the two cases
  stay distinguishable. The message warns against reproducing the withheld effect through another
  tool, not against using other tools at all.
- `falcon_list_enabled_tools` carries a `filters_active` field describing the rules in effect. The
  field is absent when no filter is configured.

A tool from a module that was never enabled is not a filtered tool — it reports as unknown, since
no rule withheld it.

## When to Use Dynamic Mode

Dynamic mode is a good fit when:

- You enable a large number of modules and want to keep the context window lean.
- Your AI client has a limited context budget or charges per token of registered tool schemas.
- The agent only needs a small subset of tools per session but you want the full module set available.

The trade-off is the extra `falcon_search_tools` round-trip before every new tool call. For sessions
that call a stable, known set of tools repeatedly, the overhead adds up. For exploratory or broad
security-analysis workflows, dynamic mode often pays for itself quickly.
