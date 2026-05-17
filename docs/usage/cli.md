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
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

Run with stateless HTTP mode (for scalable deployments like AWS AgentCore):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

Run with API key authentication:

```bash
falcon-mcp --transport streamable-http --api-key your-secret-key
```

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
