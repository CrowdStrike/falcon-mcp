<!-- meta:title MCP Config -->
<!-- meta:description MCP configuration file examples for connecting to the Falcon MCP Server. -->
<!-- meta:section examples -->
<!-- meta:link-base /falcon-mcp/ -->

The `examples/mcp_config.json` file shows all three transport configurations in a single file.

## All Transport Configurations

```json
{
  "servers": [
    {
      "name": "falcon-stdio",
      "transport": {
        "type": "stdio",
        "command": "python -m falcon_mcp.server"
      }
    },
    {
      "name": "falcon-sse",
      "transport": {
        "type": "sse",
        "url": "http://127.0.0.1:8000/sse"
      }
    },
    {
      "name": "falcon-streamable-http",
      "transport": {
        "type": "streamable-http",
        "url": "http://127.0.0.1:8000/mcp"
      }
    }
  ]
}
```

## Claude Desktop Configuration

For Claude Desktop, the config format uses `mcpServers`. Place this in `claude_desktop_config.json`:

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

## Selecting Modules

Limit which modules are loaded to reduce tool count:

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file", "/path/to/.env",
        "falcon-mcp",
        "--modules", "detections,intel,hosts"
      ]
    }
  }
}
```

## Remote HTTP Server

If running the server on a remote host or in Docker:

```json
{
  "mcpServers": {
    "falcon-mcp-remote": {
      "type": "streamable-http",
      "url": "http://your-server:8000/mcp"
    }
  }
}
```

For authenticated endpoints (with `--api-key`):

```json
{
  "mcpServers": {
    "falcon-mcp-remote": {
      "type": "streamable-http",
      "url": "http://your-server:8000/mcp",
      "headers": {
        "x-api-key": "your-api-key"
      }
    }
  }
}
```

See [Transport Methods](/falcon-mcp/usage/transports/) for more details on each transport type and client compatibility.
