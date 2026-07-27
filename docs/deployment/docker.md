<!-- meta:title Docker -->
<!-- meta:description Deploy the Falcon MCP Server using Docker containers. -->
<!-- meta:section deployment -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP Server is available as a pre-built container image at `quay.io/crowdstrike/falcon-mcp`.

## Using the Pre-built Image (Recommended)

Pull the latest image:

```bash
docker pull quay.io/crowdstrike/falcon-mcp:latest
```

Run with stdio transport (requires -i flag):

```bash
docker run -i --rm --env-file /path/to/.env quay.io/crowdstrike/falcon-mcp:latest
```

Run with SSE transport:

```bash
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport sse --host 0.0.0.0
```

Run with streamable-http transport:

```bash
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0
```

Run with custom port:

```bash
docker run --rm -p 8080:8080 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0 --port 8080
```

Run with specific modules (stdio transport):

```bash
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --modules detections,spotlight,idp
```

Use a pinned version:

```bash
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:1.2.3
```

## Using Individual Environment Variables

Instead of a `.env` file, pass variables directly:

```bash
docker run -i --rm \
  -e FALCON_CLIENT_ID=your_client_id \
  -e FALCON_CLIENT_SECRET=your_secret \
  -e FALCON_BASE_URL=https://api.crowdstrike.com \
  quay.io/crowdstrike/falcon-mcp:latest
```

> [!NOTE]
> When using HTTP transports in Docker, always set `--host 0.0.0.0` so the server accepts connections
> from outside the container. This binds to all interfaces *inside* the container; what the endpoint is
> actually reachable from is controlled by how you publish the port (`-p`), the container network, and
> any load balancer in front of it.
>
> The `-i` flag is required when using the default stdio transport.

The HTTP transports have no authentication by default. Whenever the published port is reachable beyond
the local host, set `--api-key` (or the `FALCON_MCP_API_KEY` environment variable) so callers must send
a matching `x-api-key` header, otherwise anyone who can reach the port can drive the server with your
CrowdStrike credentials:

```bash
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --api-key your-secret-key
```

See [HTTP Transport Security](/falcon-mcp/getting-started/configuration/#http-transport-security).

## Building Locally (Development)

For development or customization, build the image from source.

Build the image:

```bash
docker build -t falcon-mcp .
```

Run the locally built image:

```bash
docker run --rm \
  -e FALCON_CLIENT_ID=your_client_id \
  -e FALCON_CLIENT_SECRET=your_secret \
  falcon-mcp
```

## MCP Client Configuration

To use the Docker image with Claude Desktop or similar clients, add to your MCP config:

```json
{
  "mcpServers": {
    "falcon-mcp-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/full/path/to/.env",
        "quay.io/crowdstrike/falcon-mcp:latest"
      ]
    }
  }
}
```
