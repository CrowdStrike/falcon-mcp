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

When running HTTP transports (`sse` or `streamable-http`), protect the endpoint with an API key:

```bash
falcon-mcp --transport streamable-http --api-key your-secret-key
```

This is a self-generated key (any secure string you create) that ensures only authorized clients with the matching key can access the MCP server. It is separate from your CrowdStrike API credentials.
