![CrowdStrike Logo (Light)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-light-mode.png#gh-light-mode-only)
![CrowdStrike Logo (Dark)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-dark-mode.png#gh-dark-mode-only)

<!-- mcp-name: io.github.CrowdStrike/falcon-mcp -->

# falcon-mcp

[![PyPI version](https://badge.fury.io/py/falcon-mcp.svg)](https://badge.fury.io/py/falcon-mcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/falcon-mcp)](https://pypi.org/project/falcon-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-falcon--mcp-blue)](https://registry.modelcontextprotocol.io/?q=io.github.CrowdStrike%2Ffalcon-mcp&all=1)
[![GitHub MCP](https://img.shields.io/badge/GitHub_MCP-falcon--mcp-blue?logo=github)](https://github.com/mcp/CrowdStrike/falcon-mcp)
[![Gemini CLI Extension](https://img.shields.io/badge/Gemini_CLI-falcon--mcp-blue?logo=google)](https://geminicli.com/extensions/?name=CrowdStrikefalcon-mcp)

**falcon-mcp** is a Model Context Protocol (MCP) server that connects AI agents with the CrowdStrike Falcon platform, powering intelligent security analysis in your agentic workflows. It delivers programmatic access to essential security capabilities—including detections, threat intelligence, and host management—establishing the foundation for advanced security operations and automation.

> [!IMPORTANT]
> **🚧 Public Preview**: This project is currently in public preview and under active development. Features and functionality may change before the stable 1.0 release. While we encourage exploration and testing, please avoid production deployments. We welcome your feedback through [GitHub Issues](https://github.com/crowdstrike/falcon-mcp/issues) to help shape the final release.

## Documentation

Full docs are available at **[developer.crowdstrike.com/falcon-mcp](https://developer.crowdstrike.com/falcon-mcp/)**.

## Modules

| Module | Description |
| ------ | ----------- |
| Core | Basic connectivity and system information |
| [AgentWorks](https://developer.crowdstrike.com/falcon-mcp/modules/agentworks/) | Call, list, and observe Charlotte AI agents and their execution traces |
| [Case Management](https://developer.crowdstrike.com/falcon-mcp/modules/cases/) | Case lifecycle management, evidence attachment, tagging, and templates |
| [Cloud Security](https://developer.crowdstrike.com/falcon-mcp/modules/cloud/) | Kubernetes containers, image vulnerabilities, CSPM asset inventory, IOM findings, suppression rules, cloud risks, cloud insights, and cloud groups |
| [Correlation Rules](https://developer.crowdstrike.com/falcon-mcp/modules/correlationrules/) | Search, create, update, and manage NG-SIEM correlation rules |
| [Custom IOA](https://developer.crowdstrike.com/falcon-mcp/modules/custom-ioa/) | Create and manage Custom IOA behavioral detection rules and rule groups |
| [Data Protection](https://developer.crowdstrike.com/falcon-mcp/modules/data-protection/) | Search Data Protection classifications, policies, and content patterns |
| [Detections](https://developer.crowdstrike.com/falcon-mcp/modules/detections/) | Find, aggregate, and analyze detections to understand malicious activity |
| [Discover](https://developer.crowdstrike.com/falcon-mcp/modules/discover/) | Search application inventory and managed/unmanaged assets, including drive encryption and system-insights posture |
| [Exclusions](https://developer.crowdstrike.com/falcon-mcp/modules/exclusions/) | Search, create, update, and delete IOA, machine learning, sensor visibility, and certificate-based exclusions |
| [Firewall Management](https://developer.crowdstrike.com/falcon-mcp/modules/firewall/) | Search and manage firewall rules and rule groups |
| [Fusion SOAR](https://developer.crowdstrike.com/falcon-mcp/modules/fusion/) | Search Fusion SOAR workflow definitions and executions, read execution results, and run on-demand workflows |
| [Host Groups](https://developer.crowdstrike.com/falcon-mcp/modules/host-groups/) | Search, create, update, and delete host groups; manage group membership |
| [Hosts](https://developer.crowdstrike.com/falcon-mcp/modules/hosts/) | Manage and query host/device information |
| [Identity Protection](https://developer.crowdstrike.com/falcon-mcp/modules/idp/) | Entity investigation and identity protection analysis |
| [Intel](https://developer.crowdstrike.com/falcon-mcp/modules/intel/) | Research threat actors, IOCs, and intelligence reports |
| [IOC](https://developer.crowdstrike.com/falcon-mcp/modules/ioc/) | Search, create, and remove custom indicators of compromise |
| [NGSIEM](https://developer.crowdstrike.com/falcon-mcp/modules/ngsiem/) | Execute CQL queries against Next-Gen SIEM |
| [Policies](https://developer.crowdstrike.com/falcon-mcp/modules/policies/) | Search, create, update, and delete prevention, sensor update, firewall, device control, response, and content update policies; manage host-group assignment, enable/disable, and precedence |
| [Quarantine](https://developer.crowdstrike.com/falcon-mcp/modules/quarantine/) | Search quarantine records, preview action counts, and release, unrelease, or delete quarantined files |
| [Real Time Response](https://developer.crowdstrike.com/falcon-mcp/modules/rtr/) | Audit, summarize, and run read-only RTR triage workflows |
| [Recon](https://developer.crowdstrike.com/falcon-mcp/modules/recon/) | Search and aggregate Falcon Intelligence Recon notifications (recon alerts), monitoring rules, and exposed-data records for dark web, leaked credentials, and typosquatting, and preview prospective rule noise |
| [Scheduled Reports](https://developer.crowdstrike.com/falcon-mcp/modules/scheduled-reports/) | Manage scheduled reports and download report files |
| [Sensor Usage](https://developer.crowdstrike.com/falcon-mcp/modules/sensor-usage/) | Access and analyze sensor usage data |
| [Serverless](https://developer.crowdstrike.com/falcon-mcp/modules/serverless/) | Search for vulnerabilities in serverless functions |
| [Shield](https://developer.crowdstrike.com/falcon-mcp/modules/shield/) | SaaS security posture, checks, alerts, and app inventory |
| [Spotlight](https://developer.crowdstrike.com/falcon-mcp/modules/spotlight/) | Manage and analyze vulnerability data and security assessments |
| [Zero Trust Assessment](https://developer.crowdstrike.com/falcon-mcp/modules/zero-trust-assessment/) | Retrieve Zero Trust Assessment posture scores and sensor and OS hardening signals for hosts |

See the [Module Overview](https://developer.crowdstrike.com/falcon-mcp/modules/overview/) for required API scopes, available tools, and FQL resources.

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

Set the required environment variables (or use a `.env` file — see the [Configuration Guide](https://developer.crowdstrike.com/falcon-mcp/getting-started/configuration/)):

```bash
export FALCON_CLIENT_ID="your-client-id"
export FALCON_CLIENT_SECRET="your-client-secret"
export FALCON_BASE_URL="https://api.crowdstrike.com"
```

### Run

```bash
falcon-mcp
```

See the [Getting Started guide](https://developer.crowdstrike.com/falcon-mcp/getting-started/installation/) for full installation and configuration details.

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

See the [Usage guide](https://developer.crowdstrike.com/falcon-mcp/usage/cli/) for all command line options, module configuration, and library usage.

## Container Usage

```bash
# Pull the latest image
docker pull quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file (stdio transport)
docker run -i --rm --env-file /path/to/.env quay.io/crowdstrike/falcon-mcp:latest

# Run with streamable-http transport (add --api-key when the port is reachable beyond localhost)
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --api-key your-secret-key
```

> [!CAUTION]
> HTTP transports have no authentication by default. Binding to a non-loopback address (`--host 0.0.0.0`)
> exposes an unauthenticated server that anyone who can reach the port can drive with your CrowdStrike
> credentials. Keep the default loopback bind for local use and set `--api-key` whenever you bind wider.
> Managed runtimes such as AWS Bedrock AgentCore and Google Cloud Run sit behind their own network
> security layer, so this does not apply to them. See the
> [Configuration guide](https://developer.crowdstrike.com/falcon-mcp/getting-started/configuration/#http-transport-security).

See the [Docker Deployment guide](https://developer.crowdstrike.com/falcon-mcp/deployment/docker/) for building locally, custom ports, and advanced configurations.

## Dynamic Mode

Running many modules at once inflates the context window every AI client must hold. Dynamic mode
replaces the full tool surface with three tools — `falcon_list_enabled_tools` to see every tool the
server has available, `falcon_search_tools` to find candidate tools by keyword and then fetch the parameter
schema for the one you pick, and `falcon_execute_tool` to run it — so agents only load the schemas
they actually need.

```bash
falcon-mcp --dynamic
# or: FALCON_MCP_DYNAMIC=true
```

See the [Dynamic Mode guide](https://developer.crowdstrike.com/falcon-mcp/usage/dynamic-mode/) for
the full discover → execute workflow and trade-offs.

## Restricting What a Server Can Do

`--modules` is all-or-nothing per module: enabling one to get its search tools also exposes every
mutating tool it carries. Three tool-level options narrow that surface.

```bash
# Investigation-only server: no tool that mutates tenant state is registered
falcon-mcp --read-only

# Expose exactly two tools, nothing else
falcon-mcp --tools falcon_search_detections,falcon_search_hosts

# Keep the module, drop one tool
falcon-mcp --modules hostgroups --exclude-tools falcon_delete_host_groups

# All of detections, plus one tool from a module you did not enable
falcon-mcp --modules detections --tools falcon_search_applications
```

| Flag | Environment Variable | Effect |
| --- | --- | --- |
| `--read-only` | `FALCON_MCP_READ_ONLY` | Registers only read-only tools |
| `--tools` | `FALCON_MCP_TOOLS` | Allow-list of tool names, added to the enabled modules |
| `--exclude-tools` | `FALCON_MCP_EXCLUDE_TOOLS` | Deny-list of tool names |

Tool names are the `falcon_`-prefixed names your client displays. An unrecognized name aborts
startup rather than being ignored, so a typo in a deny-list cannot silently leave a tool exposed.

### Composing the options

`--tools` is **additive**, not a narrowing filter. It grants individual tools on top of whatever
`--modules` already enabled, reaching across the module boundary:

- `--tools X` on its own registers **only** X — no modules are loaded by default.
- `--modules detections --tools X` registers every `detections` tool **plus** X, even when X
  belongs to a module that is not enabled. That module contributes only X, not its whole surface,
  and `falcon_list_enabled_modules` does not list it. `falcon_list_enabled_tools` does list X — it
  reports the tools available on the server, so it is the reliable answer to "is this capability
  available here?"

To *subtract*, use `--exclude-tools` or `--read-only`. All four knobs compose, and they resolve in
a fixed order:

1. `--exclude-tools` removes a tool unconditionally, even if `--tools` names it.
2. `--read-only` removes every mutating tool unconditionally, even if `--tools` names it.
3. `--tools` adds the tools it names, bypassing the module gate.
4. `--modules` decides which tools are candidates by default.

Because the first two rules always win, `--read-only` and `--exclude-tools` are safe to set as a
deployment-wide floor: an additive `--tools` list cannot widen past them. Combining them is how you
express "search everything, change nothing, and don't even offer that one tool":

```bash
falcon-mcp --read-only --exclude-tools falcon_execute_rtr_read_only_command
```

Filtering applies to dynamic mode too — a withheld tool is absent from `falcon_search_tools`
results and rejected by `falcon_execute_tool`. Because dynamic mode dispatches by name rather than
registering tools individually, that rejection spells out that the tool exists but the server's
configuration withholds it, and names the one rule responsible, so an agent reports a disabled tool
as disabled instead of telling the user the capability does not exist.
`falcon_list_enabled_tools` carries a `filters_active` field in either mode whenever a rule is in
effect. The startup log reports which rules are active and how many tools `--read-only` and
`--exclude-tools` withheld, so you can confirm what you deployed. Run with `--debug` to see the
withheld tools by name.

These options filter tools, not resources. A withheld tool's FQL guide resource stays available —
guides are static field documentation carrying no tenant data.

## Deployment Options

- [Amazon Bedrock AgentCore](https://developer.crowdstrike.com/falcon-mcp/deployment/amazon-bedrock/)
- [Google Cloud (Agent Platform / Gemini Enterprise)](./examples/adk/README.md)

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
> This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases. Please follow the commit message format outlined in our [Contributing Guide](.github/CONTRIBUTING.md).

### Developer Documentation

- [Documentation Guide](docs/development/docs-site.md): Architecture and maintenance guide for the documentation
- [Module Development Guide](docs/development/module-development.md): Instructions for implementing new modules
- [Resource Development Guide](docs/development/resource-development.md): Instructions for implementing resources
- [Integration Testing Guide](docs/development/integration-testing.md): Guide for running integration tests with real API calls

## Registries

falcon-mcp is published to public MCP catalogs for discovery and one-click setup in compatible clients:

- [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.CrowdStrike%2Ffalcon-mcp&all=1)
- [GitHub MCP Registry](https://github.com/mcp/CrowdStrike/falcon-mcp)
- [Gemini CLI Extensions](https://geminicli.com/extensions/?name=CrowdStrikefalcon-mcp)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

This is a community-driven, open source project. While it is not an official CrowdStrike product, it is actively maintained by CrowdStrike and supported in collaboration with the open source developer community.

For more information, please see our [SUPPORT](SUPPORT.md) file.
