---
title: Transport Methods
description: The three transport methods supported by the Falcon MCP Server.
---

The Falcon MCP Server supports three transport methods. Choose based on your deployment scenario.

## stdio (Default)

The simplest transport. The MCP client manages the server process directly via stdin/stdout.

```bash
falcon-mcp
# or explicitly: falcon-mcp --transport stdio
```

**Best for:** Claude Desktop, Cline/VS Code, and any MCP client that supports subprocess management.

**Client compatibility:** All clients.

## SSE (Server-Sent Events)

HTTP-based transport with server-sent events for streaming. Start the server independently, then connect via URL.

```bash
falcon-mcp --transport sse
# Server listens at http://127.0.0.1:8000/sse
```

Custom host/port:

```bash
falcon-mcp --transport sse --host 0.0.0.0 --port 8080
```

**Best for:** Web-based clients and environments where subprocess management isn't available.

**Client compatibility:** Claude Desktop, Cline/VS Code, MCP Inspector.

## Streamable HTTP

Modern HTTP transport with streaming support. The recommended transport for server deployments and containerized environments.

```bash
falcon-mcp --transport streamable-http
# Server listens at http://127.0.0.1:8000/mcp
```

Custom host/port:

```bash
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

Stateless mode (required for AWS AgentCore and other scalable deployments):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

**Best for:** Docker containers, cloud deployments, AWS Bedrock AgentCore, scalable deployments.

**Client compatibility:** Claude Desktop, MCP Inspector.

:::note
When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to the container.
:::

## Client Compatibility

| Client | stdio | SSE | streamable-http |
|--------|:-----:|:---:|:---------------:|
| Claude Desktop | ✓ | ✓ | ✓ |
| Cline / VS Code | ✓ | ✓ | — |
| MCP Inspector | ✓ | ✓ | ✓ |
| Docker (stdio) | ✓ (requires `-i`) | — | — |
