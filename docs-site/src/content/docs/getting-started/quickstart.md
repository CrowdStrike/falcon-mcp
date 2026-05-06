---
title: Quick Start
description: Get up and running with the Falcon MCP Server in 5 minutes.
---

This guide gets you from zero to a working Falcon MCP Server connection in 5 minutes.

## Step 1: Get API Credentials

1. Log into your CrowdStrike console
2. Navigate to **Support > API Clients and Keys**
3. Click **Add new API client** and configure:
   - Give it a name (e.g., "Falcon MCP Server")
   - Enable at minimum: `Hosts:read`, `Alerts:read`
4. Save your **Client ID**, **Client Secret**, and **Base URL**

## Step 2: Install

```bash
uv tool install falcon-mcp
```

Or run without installing:

```bash
uvx falcon-mcp --help
```

## Step 3: Configure Credentials

Create a `.env` file in your working directory:

```bash
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com
```

## Step 4: Connect to Your Editor

Add to your editor's MCP configuration (e.g., Claude Desktop's `claude_desktop_config.json`):

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

## Step 5: Verify the Connection

In your AI assistant, ask:

> "Check connectivity to the Falcon API"

The server will call `falcon_check_connectivity` and confirm the connection.

> "List all enabled modules"

You should see all 16 modules listed.

## Next Steps

- [CLI Commands](/falcon-mcp/usage/cli/) — all command-line options
- [Editor Integration](/falcon-mcp/usage/editor-integration/) — full config examples for popular clients
- [Module Overview](/falcon-mcp/modules/overview/) — explore available tools
