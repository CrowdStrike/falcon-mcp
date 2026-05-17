---
title: Installation
description: Install the Falcon MCP Server using uv or pip.
---

## Prerequisites

- Python 3.11 or higher
- [`uv`](https://docs.astral.sh/uv/) or pip
- CrowdStrike Falcon API credentials ([see API Credentials](/falcon-mcp/getting-started/credentials))

## Install using uv

```bash
uv tool install falcon-mcp
```

## Install using pip

```bash
pip install falcon-mcp
```

:::tip
If `falcon-mcp` isn't found after installation, update your shell `PATH`.
:::

## Run without installing

You can run the server directly without a permanent install using `uvx`:

```bash
uvx falcon-mcp
```

This is the recommended approach for editor integrations.

:::note
If you just want to interact with falcon-mcp via an agent chat interface rather than running the server yourself, see the [Deployment](/falcon-mcp/deployment/docker/) options.
:::
