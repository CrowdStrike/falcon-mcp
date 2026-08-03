<!-- meta:title Configuration -->
<!-- meta:description Configure environment variables and settings for the Falcon MCP Server. -->
<!-- meta:section getting-started -->
<!-- meta:link-base /falcon-mcp/ -->

## Environment Variables

Configure your CrowdStrike API credentials and server settings using environment variables.

### Required

| Variable | Description |
|----------|-------------|
| `FALCON_CLIENT_ID` | CrowdStrike API client ID |
| `FALCON_CLIENT_SECRET` | CrowdStrike API client secret |
| `FALCON_BASE_URL` | API base URL for your region (e.g., `https://api.crowdstrike.com`) |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `FALCON_MEMBER_CID` | — | Flight Control child CID (MSSP) |
| `FALCON_MCP_MODULES` | all | Comma-separated list of modules to enable |
| `FALCON_MCP_TRANSPORT` | `stdio` | Transport method: `stdio`, `sse`, `streamable-http` |
| `FALCON_MCP_DEBUG` | `false` | Enable debug logging |
| `FALCON_MCP_HOST` | `127.0.0.1` | Host for HTTP transports |
| `FALCON_MCP_PORT` | `8000` | Port for HTTP transports |
| `FALCON_MCP_STATELESS_HTTP` | `false` | Stateless mode for scalable deployments (required for AWS AgentCore) |
| `FALCON_MCP_API_KEY` | — | API key for HTTP transport authentication |
| `FALCON_MCP_DYNAMIC` | `false` | [Dynamic mode](/falcon-mcp/usage/dynamic-mode/): expose three tools instead of all module tools |
| `FALCON_MCP_READ_ONLY` | `false` | Register only read-only tools ([tool restrictions](/falcon-mcp/usage/cli/#restricting-the-tool-surface)) |
| `FALCON_MCP_TOOLS` | — | Comma-separated allow-list of tool names, added to the enabled modules |
| `FALCON_MCP_EXCLUDE_TOOLS` | — | Comma-separated deny-list of tool names |
| `FALCON_PROXY_URL` | — | HTTP/HTTPS proxy URL for outbound API connections |

## Using a .env File

The recommended approach for development is a `.env` file.

### Option 1: Copy from the repository

```bash
cp .env.example .env
```

### Option 2: Download from GitHub

```bash
curl -o .env https://raw.githubusercontent.com/CrowdStrike/falcon-mcp/main/.env.example
```

### Option 3: Create manually

```bash frame="code"
# Required Configuration
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com

# Optional Configuration
#FALCON_MEMBER_CID=your-child-cid
#FALCON_MCP_MODULES=detections,hosts,intel
#FALCON_MCP_TRANSPORT=stdio
#FALCON_MCP_DEBUG=false
#FALCON_MCP_HOST=127.0.0.1
#FALCON_MCP_PORT=8000
#FALCON_MCP_STATELESS_HTTP=false
#FALCON_MCP_API_KEY=your-api-key
#FALCON_MCP_DYNAMIC=false
#FALCON_MCP_READ_ONLY=false
#FALCON_MCP_TOOLS=falcon_search_detections,falcon_search_hosts
#FALCON_MCP_EXCLUDE_TOOLS=falcon_delete_host_groups
#FALCON_PROXY_URL=http://proxy.corp.example.com:8080
```

## Module Selection

By default, all available modules are enabled. To restrict which modules load:

```bash
# Command line (highest priority)
falcon-mcp --modules detections,hosts,intel
```

```bash
# Environment variable (fallback)
export FALCON_MCP_MODULES=detections,hosts,intel
falcon-mcp
```

**Priority order:** CLI flag > `FALCON_MCP_MODULES` env var > all modules (default)

## HTTP Transport Security

The HTTP transports (`sse` and `streamable-http`) have no authentication by default. The server binds
to loopback (`127.0.0.1`) unless you tell it otherwise, so out of the box it is only reachable from the
local host.

Binding to a non-loopback address such as `--host 0.0.0.0` (or `FALCON_MCP_HOST=0.0.0.0`) exposes the
server on the network. With no API key set, anyone who can reach the port can invoke every tool using
your CrowdStrike credentials. The server logs a warning at startup when it binds beyond loopback
without an API key (it does not refuse to start). Set `--api-key` whenever you bind beyond loopback:

```bash
falcon-mcp --transport streamable-http --host 0.0.0.0 --api-key your-secret-key
```

The key is a self-generated value (any secure string you create) that callers must send in the
`x-api-key` header; requests without a matching key are rejected with `401 Unauthorized`. It is
separate from your CrowdStrike API credentials. You can also supply it via the `FALCON_MCP_API_KEY`
environment variable.

Clients pass the key in an `x-api-key` header. In an MCP client config:

```json
{
  "mcpServers": {
    "falcon-mcp-remote": {
      "type": "streamable-http",
      "url": "http://your-server:8000/mcp",
      "headers": {
        "x-api-key": "your-secret-key"
      }
    }
  }
}
```

Or when calling the endpoint directly:

```bash
curl http://your-server:8000/mcp \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"example","version":"1.0"}}}'
```

**Recommendations:**

- Keep the default loopback bind (`127.0.0.1`) for local single-machine use.
- Set `--api-key` any time you bind to a non-loopback address or publish the port to a network.
- Managed runtimes such as AWS Bedrock AgentCore and Google Cloud Run sit behind their own network
  security layer (IAM, private networking), so the open-bind concern does not apply there. `--api-key`
  remains available on those platforms as optional defense in depth.
