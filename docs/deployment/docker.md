---
title: Docker
description: Deploy the Falcon MCP Server using Docker containers.
---

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

:::note
When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to the container.

The `-i` flag is required when using the default stdio transport.
:::

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
