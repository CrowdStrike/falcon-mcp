<!-- meta:title Transport Methods -->
<!-- meta:description The three transport methods supported by the Falcon MCP Server. -->
<!-- meta:section usage -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP Server supports three transport methods. Choose based on your deployment scenario.

> [!CAUTION]
> The HTTP transports (`sse` and `streamable-http`) have no authentication by default. Binding to a
> non-loopback address such as `--host 0.0.0.0` exposes an unauthenticated server — anyone who can
> reach the port can invoke every tool using your CrowdStrike credentials. Bind to loopback
> (`127.0.0.1`, the default) for local use, and set `--api-key` whenever you bind wider. See
> [HTTP Transport Security](/falcon-mcp/getting-started/configuration/#http-transport-security).

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
falcon-mcp --transport sse --host 0.0.0.0 --port 8080 --api-key your-secret-key
```

Binding to `0.0.0.0` reaches the network, so pair it with `--api-key` to require callers to send a
matching `x-api-key` header.

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
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080 --api-key your-secret-key
```

Binding to `0.0.0.0` reaches the network, so pair it with `--api-key` to require callers to send a
matching `x-api-key` header.

Stateless mode (required for AWS AgentCore and other scalable deployments):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

**Best for:** Docker containers, cloud deployments, AWS Bedrock AgentCore, scalable deployments.

**Client compatibility:** Claude Desktop, MCP Inspector.

> [!NOTE]
> When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to
> the container. The container port is still only reachable by whatever you expose it to (a published
> `-p` port, another container, a load balancer), so control that exposure and add `--api-key` when the
> endpoint is reachable beyond the local host.
>
> Managed runtimes such as AWS Bedrock AgentCore and Google Cloud Run sit behind their own network
> security layer (IAM, private networking), so the open-bind concern above does not apply to them —
> `--api-key` remains available there as optional defense in depth.

## Client Compatibility

| Client | stdio | SSE | streamable-http |
|--------|:-----:|:---:|:---------------:|
| Claude Desktop | ✓ | ✓ | ✓ |
| Cline / VS Code | ✓ | ✓ | — |
| MCP Inspector | ✓ | ✓ | ✓ |
| Docker (stdio) | ✓ (requires `-i`) | — | — |
