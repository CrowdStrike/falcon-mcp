<!-- meta:title CLI Commands -->
<!-- meta:description Command-line options for running the Falcon MCP Server. -->
<!-- meta:section usage -->
<!-- meta:link-base /falcon-mcp/ -->

## Basic Usage

Run the server with default settings (stdio transport):

```bash
falcon-mcp
```

Run with SSE transport:

```bash
falcon-mcp --transport sse
```

Run with streamable-http transport:

```bash
falcon-mcp --transport streamable-http
```

Run with streamable-http on a custom port:

```bash
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080 --api-key your-secret-key
```

Run with stateless HTTP mode (for scalable deployments like AWS AgentCore):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

Run with API key authentication:

```bash
falcon-mcp --transport streamable-http --api-key your-secret-key
```

> [!CAUTION]
> HTTP transports have no authentication by default. Binding to a non-loopback address such as
> `--host 0.0.0.0` exposes an unauthenticated server that anyone who can reach the port can drive with
> your CrowdStrike credentials. Keep the default loopback bind (`127.0.0.1`) for local use, and set
> `--api-key` whenever you bind wider. See
> [HTTP Transport Security](/falcon-mcp/getting-started/configuration/#http-transport-security).

## Module Selection

Enable specific modules by name (comma-separated):

```bash
falcon-mcp --modules detections,intel,spotlight,idp
```

Enable only one module:

```bash
falcon-mcp --modules detections
```

If no `--modules` flag is provided, all available modules are enabled.

## All Options

```text
falcon-mcp --help
```

| Flag | Env Variable | Default | Description |
|------|-------------|---------|-------------|
| `--transport` | `FALCON_MCP_TRANSPORT` | `stdio` | Transport method: `stdio`, `sse`, `streamable-http` |
| `--host` | `FALCON_MCP_HOST` | `127.0.0.1` | Host for HTTP transports |
| `--port` | `FALCON_MCP_PORT` | `8000` | Port for HTTP transports |
| `--modules` | `FALCON_MCP_MODULES` | all | Comma-separated list of modules to enable |
| `--debug` | `FALCON_MCP_DEBUG` | `false` | Enable debug logging |
| `--api-key` | `FALCON_MCP_API_KEY` | — | API key for HTTP transport auth |
| `--stateless-http` | `FALCON_MCP_STATELESS_HTTP` | `false` | Stateless mode for scalable deployments |
| `--member-cid` | `FALCON_MEMBER_CID` | — | Flight Control child CID |
| `--proxy` | `FALCON_PROXY_URL` | — | HTTP/HTTPS proxy for outbound API connections |
| `--dynamic` | `FALCON_MCP_DYNAMIC` | `false` | [Dynamic mode](/falcon-mcp/usage/dynamic-mode/): expose three tools (list-enabled-tools, search, execute) instead of all module tools to reduce context usage |
| `--read-only` | `FALCON_MCP_READ_ONLY` | `false` | Register only read-only tools, disabling every tool that mutates tenant state |
| `--tools` | `FALCON_MCP_TOOLS` | — | Comma-separated allow-list of tool names, added to the enabled modules |
| `--exclude-tools` | `FALCON_MCP_EXCLUDE_TOOLS` | — | Comma-separated deny-list of tool names to withhold |

## Restricting the Tool Surface

`--modules` gates whole modules, so enabling one to reach its search tools also exposes its
mutating tools. The three tool-level options narrow that surface further:

```bash
# Investigation-only server
falcon-mcp --read-only

# Expose exactly two tools, nothing else
falcon-mcp --tools falcon_search_detections,falcon_search_hosts

# Keep the module, drop one tool
falcon-mcp --modules hostgroups --exclude-tools falcon_delete_host_groups

# All of detections, plus one tool from a module you did not enable
falcon-mcp --modules detections --tools falcon_search_applications
```

Tool names are the `falcon_`-prefixed names clients display. An unrecognized name aborts startup
instead of being ignored, so a typo in a deny-list cannot silently leave a tool exposed.

`--tools` is **additive**, not a narrowing filter. It grants individual tools on top of whatever
`--modules` already enabled, reaching across the module boundary:

- `--tools X` on its own registers **only** X — no modules are loaded by default.
- `--modules detections --tools X` registers every `detections` tool **plus** X, even when X belongs
  to a module that is not enabled. That module contributes only X, not its whole surface, and
  `falcon_list_enabled_modules` does not list it. `falcon_list_enabled_tools` does list X — it
  reports the tools available on the server, so it is the reliable answer to "is this capability
  available here?"

To *subtract*, use `--exclude-tools` or `--read-only`. All four options compose and resolve in a
fixed order:

1. `--exclude-tools` removes a tool unconditionally, even if `--tools` names it.
2. `--read-only` removes every mutating tool unconditionally, even if `--tools` names it.
3. `--tools` adds the tools it names, bypassing the module gate.
4. `--modules` decides which tools are candidates by default.

Since the first two rules always win, they work as a deployment-wide floor that an additive
`--tools` list cannot widen past. The restrictions also hold in dynamic mode: a withheld tool is
absent from `falcon_search_tools` results and rejected by `falcon_execute_tool`. Since dynamic mode
dispatches by name, that rejection says the tool exists but is withheld by configuration and names
the one rule responsible, so an agent does not report a disabled tool as a capability the product
lacks. In either mode `falcon_list_enabled_tools` carries a
`filters_active` field while any rule is in effect. The startup log
reports which rules are active and how many tools `--read-only` and `--exclude-tools` withheld; add
`--debug` to see those tools by name. A tool that was simply never requested is not counted as
withheld — only `--tools` grants and the two subtracting rules are decisions worth reporting.

These options filter tools, not resources. A withheld tool's FQL guide resource stays available,
since guides are static field documentation carrying no tenant data.

## Using as a Library

You can also embed the server directly in Python:

```python
from falcon_mcp.server import FalconMCPServer

server = FalconMCPServer(
    base_url="https://api.us-2.crowdstrike.com",  # Optional
    debug=True,
    enabled_modules=["detections", "spotlight"],
    api_key="your-api-key"
)

# Run with stdio transport (default)
server.run()

# Or with a specific transport
server.run("streamable-http")
```

For enterprise deployments using secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.), you can pass credentials directly:

```python
server = FalconMCPServer(
    client_id="your-client-id",
    client_secret="your-client-secret",
    base_url="https://api.us-2.crowdstrike.com",
    enabled_modules=["detections", "hosts"],
    proxy="http://proxy.corp.example.com:8080",
)
server.run()
```

When both direct parameters and environment variables are available, direct parameters take precedence.
