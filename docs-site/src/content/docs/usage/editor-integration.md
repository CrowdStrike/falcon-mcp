---
title: Editor Integration
description: Configure the Falcon MCP Server in popular MCP-compatible editors and assistants.
---

The Falcon MCP Server works with any MCP-compatible editor or AI assistant. Below are configuration examples for popular clients.

## Claude Desktop

Edit `claude_desktop_config.json`:

### Using uvx (recommended)

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "falcon-mcp"
      ]
    }
  }
}
```

### With module selection

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "falcon-mcp",
        "--modules",
        "detections,hosts,intel"
      ]
    }
  }
}
```

### Using individual environment variables

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": ["falcon-mcp"],
      "env": {
        "FALCON_CLIENT_ID": "your-client-id",
        "FALCON_CLIENT_SECRET": "your-client-secret",
        "FALCON_BASE_URL": "https://api.crowdstrike.com"
      }
    }
  }
}
```

### Docker version

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

:::note
The `-i` flag is required when using the default stdio transport with Docker.
:::

## Cline (VS Code)

Cline supports stdio and SSE transports. Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "falcon-mcp"
      ]
    }
  }
}
```

## Gemini CLI

```bash
# Install uv first
gemini extensions install https://github.com/CrowdStrike/falcon-mcp
```

```bash
# Copy .env file
cp /path/to/.env ~/.gemini/extensions/falcon-mcp/.env
```

## SSE / HTTP Clients

For clients that connect via URL (SSE or streamable-http), start the server first:

```bash
# SSE
falcon-mcp --transport sse --host 0.0.0.0 --port 8000
```

```bash
# Streamable HTTP
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

Then configure your client with:

- SSE URL: `http://your-host:8000/sse`
- Streamable HTTP URL: `http://your-host:8000/mcp`
