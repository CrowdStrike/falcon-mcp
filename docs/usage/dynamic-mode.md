<!-- meta:title Dynamic Mode -->
<!-- meta:description Reduce context usage by exposing three tools instead of all module tools. -->
<!-- meta:section usage -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP server registers one tool schema per tool across all enabled modules. As the module
set grows, this balloons the context window that AI clients must hold in every conversation — even
for tools that will never be called in that session.

Dynamic mode solves this by replacing the full tool surface with three tools. Two are the
discovery pair: `falcon_search_tools` to find a tool and look up its parameter schema, and
`falcon_execute_tool` to run it. The third, `falcon_list_enabled_tools`, is always on and
returns the full inventory of Falcon tools available on the server. The agent fetches the
schema for exactly the tools it needs, paying a short discovery round-trip instead of a large
up-front context cost.

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

With dynamic mode enabled, the server exposes three tools instead of the full module surface —
the `falcon_search_tools` / `falcon_execute_tool` discovery pair plus the always-on
`falcon_list_enabled_tools`:

| Tool | Purpose |
|------|---------|
| `falcon_list_enabled_tools` | List the Falcon tools available on this server, grouped by the module each belongs to (meta-tools excluded) |
| `falcon_search_tools` | Find tools by keyword or module, then return the parameters of the ones you name |
| `falcon_execute_tool` | Execute a discovered tool by name with the given parameters |

The typical agent workflow is:

1. Call `falcon_list_enabled_tools` when you need to know what the server has at all — a name
   absent from that list is not available, whether because its module is off or a tool filter
   withholds it. Its `by_module` map also publishes the module names `falcon_search_tools` accepts.
2. Call `falcon_search_tools` with a keyword or module name to see candidate tools, ordered by
   likely relevance, with their `read_only` and `destructive` flags. The order is a keyword match,
   not a judgement of intent — read the descriptions and flags and pick the tool that fits.
3. Call `falcon_search_tools` again with `tool_names` set to the tool you picked, to get its
   parameters.
4. Call `falcon_execute_tool` with the tool name and parameters to run it.

Because `falcon_execute_tool` is a general dispatcher, it carries no read-only safety annotation by
default — the agent must rely on the `read_only` and `destructive` fields returned by
`falcon_search_tools` to understand a tool's mutation risk before executing it. Those flags are
present on discovery results, so mutation risk is visible before the schema is fetched.

## Two Response Shapes

`falcon_search_tools` answers two different questions, and returns a different shape for each.

**Discovery** — `query` and/or `module`, the default. Answers "which tool do I want?" Each result
carries `name`, `module`, `description`, `read_only`, and `destructive`, and deliberately **no**
`parameters` key. The absent key is the signal that a second call is needed; the `hint` field says so
explicitly.

**Schema** — `tool_names`. Answers "how do I call it?" Each named tool comes back as a full entry
including every parameter (type, required, description, examples) with FQL or CQL syntax hints
inlined. `query`, `module`, and `limit` are ignored. Naming two or more tools compares candidates in
a single call.

Splitting the two is what makes discovery cheap: on the full 141-tool catalog the input schema is
roughly two thirds of an entry's bytes, and at the moment of searching the agent has not chosen a
tool to need it. A 50-result discovery response plus the schema for the one chosen tool costs
slightly less than 20 results with schemas did.

If `tool_names` names something this server does not have, the response says which name and why —
withheld by a tool filter, or never available at all — rather than silently returning fewer entries,
which would read as a tool that takes no parameters.

## Discover → Describe → Execute Example

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

The response is a `results` list alongside `total` and `truncated`. Each entry names the tool,
describes it, and flags whether it mutates — but carries no parameters.

**Step 2 — Get its parameters:**

```json
{
  "tool": "falcon_search_tools",
  "arguments": {
    "tool_names": ["falcon_search_detections"]
  }
}
```

Now the entry includes the full parameter schema, with FQL field hints already inlined for filter
parameters.

**Step 3 — Execute it:**

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

```json
{ "tool_names": ["falcon_search_hosts", "falcon_get_host_details"] }
```

Results are ordered by relevance. A tool whose name matches the query outranks one that only
mentions it in its description, and an exact tool name — with or without the `falcon_` prefix —
returns that tool alone, since naming a tool is a request for it rather than a keyword search. Tools
matching every word the search narrowed on are ordered ahead of tools that matched only some, and
within each of those groups the tool covering more of the query comes first. When two tools are
otherwise tied — a bare noun like `iocs` matches `falcon_search_iocs` and `falcon_remove_iocs`
equally — the read-only one ranks first, so the order never steers toward a mutator by default.
Ordering is deterministic: the same query returns the same order on every server process. A query
with no keywords (module browsing) is ordered by tool name.

Every word in `query` is matched against the tool's name, description, module, and parameter names.
Generic words — `list`, `show`, `get`, `find`, `all`, and similar filler — are not used to narrow the
candidate set, because they appear as prose in most descriptions ("returns an empty list on success")
and so would select whichever tools happened to use the word rather than the ones the query is about.
They still count toward ranking wherever they appear in a tool's own name, so `list case templates`
still ranks `falcon_list_case_templates` first.

On the remaining words the search prefers tools matching all of them. When too few tools do to
choose between, it also returns tools matching at least half of those words, or carrying any one of
them in their own name, ranked below the full matches; if that is still too thin, it widens once more
to any tool matching a single one of those words — so a phrase like `real-time response command`
returns ranked candidates instead of nothing. The `hint` field describes the split, saying how many
results matched every word and how many matched only some. A query whose every word is generic has
narrowed nothing, so all of its results are reported as loose matches. The order is a keyword match
with no view of intent, so read each candidate's description and its `read_only` / `destructive`
flags and pick the one that fits, rather than taking the first row on trust.

`module` ignores case and separators, so `hostgroups`, `host_groups`, and `Host-Groups` all select
the same module. `falcon_list_enabled_tools` returns a `by_module` map whose keys are the exact
module names this server accepts; it comes from the same catalog the search dispatches from, so it
cannot drift from what `module` will match. A key groups the tools that belong to that module and
are available here — with `--tools`, that can be a subset of the module's full surface, so `module=`
returns only what the map lists.

Every response carries `total` (the number of tools matching the query, before any limit) and
`truncated`, so a capped result set is never mistaken for the complete set. When results are
truncated, raise `limit` (up to 500) or narrow the query. The default is 50: lean discovery entries
are cheap enough that a wide window costs less than a narrow one did with schemas attached, and
because generic words no longer widen the candidate set, ordinary keyword queries land well inside
it — a query like `host` matches 40 tools and is not truncated at all. In schema mode `total` counts
the entries returned, since no query ran for it to describe.

If no tools match, none of the query's non-generic words appears anywhere in the available surface.
The response says so and points at `falcon_list_enabled_tools`. A capability absent from that full
inventory is not available on that server — report that rather than searching again.

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
  flag. A name that was never available still returns the plain unknown-tool error, so the two cases
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

The trade-off is the round-trips before a new tool call: one to find it, one to fetch its
parameters. For sessions that call a stable, known set of tools repeatedly, that overhead adds up —
though an agent that already knows the name can skip discovery and go straight to `tool_names`. For
exploratory or broad security-analysis workflows, dynamic mode often pays for itself quickly.
