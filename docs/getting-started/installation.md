<!-- meta:title Installation -->
<!-- meta:description Install the Falcon MCP Server using uv or pip. -->
<!-- meta:section getting-started -->
<!-- meta:link-base /falcon-mcp/ -->

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

> [!TIP]
> If `falcon-mcp` isn't found after installation, update your shell `PATH`.

## Run without installing

You can run the server directly without a permanent install using `uvx`:

```bash
uvx falcon-mcp
```

This is the recommended approach for editor integrations.

> [!NOTE]
> If you just want to interact with falcon-mcp via an agent chat interface rather than running the server yourself, see the [Deployment](/falcon-mcp/deployment/docker/) options.

## Find it on a registry

falcon-mcp is published to public MCP catalogs for discovery and one-click setup in compatible clients:

- [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.CrowdStrike%2Ffalcon-mcp&all=1)<!-- link:external -->
- [GitHub MCP Registry](https://github.com/mcp/CrowdStrike/falcon-mcp)<!-- link:external -->
- [Gemini CLI Extensions](https://geminicli.com/extensions/?name=CrowdStrikefalcon-mcp)<!-- link:external -->
