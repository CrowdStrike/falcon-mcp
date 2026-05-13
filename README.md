![CrowdStrike Logo (Light)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-light-mode.png#gh-light-mode-only)
![CrowdStrike Logo (Dark)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-dark-mode.png#gh-dark-mode-only)

<!-- mcp-name: io.github.CrowdStrike/falcon-mcp -->

# falcon-mcp

[![PyPI version](https://badge.fury.io/py/falcon-mcp.svg)](https://badge.fury.io/py/falcon-mcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/falcon-mcp)](https://pypi.org/project/falcon-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://crowdstrike.github.io/falcon-mcp/)

**falcon-mcp** is a Model Context Protocol (MCP) server that connects AI agents with the CrowdStrike Falcon platform, powering intelligent security analysis in your agentic workflows. It delivers programmatic access to essential security capabilities—including detections, threat intelligence, and host management—establishing the foundation for advanced security operations and automation.

> [!IMPORTANT]
> **🚧 Public Preview**: This project is currently in public preview and under active development. Features and functionality may change before the stable 1.0 release. While we encourage exploration and testing, please avoid production deployments. We welcome your feedback through [GitHub Issues](https://github.com/crowdstrike/falcon-mcp/issues) to help shape the final release.

## Documentation

Full docs are available at **[crowdstrike.github.io/falcon-mcp](https://crowdstrike.github.io/falcon-mcp/)**.

## Modules

| Module | Description |
|--------|-------------|
| Core | Basic connectivity and system information |
| [Cloud Security](https://crowdstrike.github.io/falcon-mcp/modules/cloud/) | Kubernetes containers, image vulnerabilities, CSPM asset inventory, IOM/IOA findings, and suppression rules |
| [Custom IOA](https://crowdstrike.github.io/falcon-mcp/modules/custom-ioa/) | Create and manage Custom IOA behavioral detection rules and rule groups |
| [Detections](https://crowdstrike.github.io/falcon-mcp/modules/detections/) | Find and analyze detections to understand malicious activity |
| [Discover](https://crowdstrike.github.io/falcon-mcp/modules/discover/) | Search application inventory and discover unmanaged assets |
| [Firewall Management](https://crowdstrike.github.io/falcon-mcp/modules/firewall/) | Search and manage firewall rules and rule groups |
| [Hosts](https://crowdstrike.github.io/falcon-mcp/modules/hosts/) | Manage and query host/device information |
| [Identity Protection](https://crowdstrike.github.io/falcon-mcp/modules/idp/) | Entity investigation and identity protection analysis |
| [Intel](https://crowdstrike.github.io/falcon-mcp/modules/intel/) | Research threat actors, IOCs, and intelligence reports |
| [IOC](https://crowdstrike.github.io/falcon-mcp/modules/ioc/) | Search, create, and remove custom indicators of compromise |
| [NGSIEM](https://crowdstrike.github.io/falcon-mcp/modules/ngsiem/) | Execute CQL queries against Next-Gen SIEM |
| [Real Time Response](https://crowdstrike.github.io/falcon-mcp/modules/rtr/) | Initialize RTR sessions and execute read-only triage commands |
| [Scheduled Reports](https://crowdstrike.github.io/falcon-mcp/modules/scheduled-reports/) | Manage scheduled reports and download report files |
| [Sensor Usage](https://crowdstrike.github.io/falcon-mcp/modules/sensor-usage/) | Access and analyze sensor usage data |
| [Serverless](https://crowdstrike.github.io/falcon-mcp/modules/serverless/) | Search for vulnerabilities in serverless functions |
| [Shield](https://crowdstrike.github.io/falcon-mcp/modules/shield/) | SaaS security posture, checks, alerts, and app inventory |
| [Spotlight](https://crowdstrike.github.io/falcon-mcp/modules/spotlight/) | Manage and analyze vulnerability data and security assessments |

See the [Module Overview](https://crowdstrike.github.io/falcon-mcp/modules/overview/) for required API scopes, available tools, and FQL resources.

## Quick Start

### Install

#### Using uv (recommended)

```bash
uv tool install falcon-mcp
```

#### Using pip

```bash
pip install falcon-mcp
```

### Configure

Set the required environment variables (or use a `.env` file — see the [Configuration Guide](https://crowdstrike.github.io/falcon-mcp/getting-started/configuration/)):

```bash
export FALCON_CLIENT_ID="your-client-id"
export FALCON_CLIENT_SECRET="your-client-secret"
export FALCON_BASE_URL="https://api.crowdstrike.com"
```

### Run

```bash
falcon-mcp
```

See the [Getting Started guide](https://crowdstrike.github.io/falcon-mcp/getting-started/installation/) for full installation and configuration details.

## Editor Integration

### Using `uvx` (recommended)

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

### With Module Selection

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

### Docker

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

See the [Usage guide](https://crowdstrike.github.io/falcon-mcp/usage/cli/) for all command line options, module configuration, and library usage.

## Container Usage

```bash
# Pull the latest image
docker pull quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file (stdio transport)
docker run -i --rm --env-file /path/to/.env quay.io/crowdstrike/falcon-mcp:latest

# Run with streamable-http transport
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0
```

See the [Docker Deployment guide](https://crowdstrike.github.io/falcon-mcp/deployment/docker/) for building locally, custom ports, and advanced configurations.

## Deployment Options

- [Amazon Bedrock AgentCore](https://crowdstrike.github.io/falcon-mcp/deployment/amazon-bedrock/)
- [Google Cloud (Cloud Run / Vertex AI)](./examples/adk/README.md)

## Contributing

```bash
# Clone and install
git clone https://github.com/CrowdStrike/falcon-mcp.git
cd falcon-mcp
uv sync --all-extras

# Run tests
uv run pytest
```

> [!IMPORTANT]
> This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases. Please follow the commit message format outlined in our [Contributing Guide](docs/CONTRIBUTING.md).

### Developer Documentation

- [Docs Site Guide](docs/development/docs_site.md): Architecture and development guide for the documentation site
- [Module Development Guide](docs/development/module_development.md): Instructions for implementing new modules
- [Resource Development Guide](docs/development/resource_development.md): Instructions for implementing resources
- [End-to-End Testing Guide](docs/development/e2e_testing.md): Guide for running and understanding E2E tests
- [Integration Testing Guide](docs/development/integration_testing.md): Guide for running integration tests with real API calls

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

This is a community-driven, open source project. While it is not an official CrowdStroke product, it is actively maintained by CrowdStrike and supported in collaboration with the open source developer community.

For more information, please see our [SUPPORT](SUPPORT.md) file.
