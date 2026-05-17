<!-- meta:title Falcon MCP -->
<!-- meta:description Connect AI assistants to the CrowdStrike Falcon platform via the Model Context Protocol. -->
<!-- frontmatter:index sidebar hidden:true -->
<!-- frontmatter:overview sidebar label:"Overview" -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP connects AI assistants to the CrowdStrike Falcon platform through the [Model Context Protocol](https://modelcontextprotocol.io)<!-- link:external -->.

This gives tools like Claude Desktop, VS Code, Gemini CLI, and custom agents direct access to your Falcon environment — enabling AI-powered threat investigation, detection triage, and security operations.

## What Can Your AI Do with Falcon?

<!-- component:card-grid -->
| Title | Description |
|-------|-------------|
| [Investigate Threats](/falcon-mcp/modules/detections/) | Search detections by severity, time range, hostname, or MITRE ATT&CK technique. |
| [Query Your Fleet](/falcon-mcp/modules/hosts/) | Find hosts by platform, sensor version, network segment, or containment status. |
| [Hunt Vulnerabilities](/falcon-mcp/modules/spotlight/) | Pull Spotlight CVE data with ExPRT ratings and remediation priorities. |
| [Research Adversaries](/falcon-mcp/modules/intel/) | Look up threat actors, indicators, and intelligence reports. |
| [Monitor Cloud Posture](/falcon-mcp/modules/cloud/) | Search CSPM assets, container images, and Kubernetes workloads. |
| [Assess Identity Risk](/falcon-mcp/modules/idp/) | Investigate entities, analyze timelines, and map relationships. |
| [Execute CQL Queries](/falcon-mcp/modules/ngsiem/) | Run searches against CrowdStrike Next-Gen SIEM. |
| [Manage IOCs](/falcon-mcp/modules/ioc/) | Search, create, and remove custom indicators of compromise. |
| [Audit Firewall Rules](/falcon-mcp/modules/firewall/) | Search and manage Falcon firewall rule groups. |
<!-- /component:card-grid -->

## Quick Start

Install and run in under 5 minutes:

```bash
uv tool install falcon-mcp
```

Or run without installing:

```bash
uvx falcon-mcp
```

Connect to Claude Desktop, VS Code, or any MCP-compatible client:

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": ["--env-file", "/path/to/.env", "falcon-mcp"]
    }
  }
}
```

You'll need a `.env` file with your CrowdStrike API credentials:

```bash
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com
```

## Deploy Anywhere

- **Local** — run as a CLI tool via stdio, SSE, or streamable HTTP
- **Docker** — pre-built image at `quay.io/crowdstrike/falcon-mcp`
- **AWS Bedrock AgentCore** — available on the AWS Marketplace
- **Google Cloud** — deploy to Cloud Run or Vertex AI Agent Engine

<!-- layout:accent-image src:"/images/adversaries/spectral-kitten.png" class:"sdk-accent" -->

## Go Deeper

- [Installation](/falcon-mcp/getting-started/installation/)
- [API Credentials](/falcon-mcp/getting-started/credentials/)
- [Configuration](/falcon-mcp/getting-started/configuration/)
- [All Modules](/falcon-mcp/modules/overview/)
- [Transport Methods](/falcon-mcp/usage/transports/)
- [Editor Integration](/falcon-mcp/usage/editor-integration/)
- [Flight Control (MSSP)](/falcon-mcp/usage/flight-control/)
- [View on GitHub](https://github.com/CrowdStrike/falcon-mcp)
