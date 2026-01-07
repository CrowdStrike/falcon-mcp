![CrowdStrike Logo (Light)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-light-mode.png#gh-light-mode-only)
![CrowdStrike Logo (Dark)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-dark-mode.png#gh-dark-mode-only)

# falcon-mcp

[![PyPI version](https://badge.fury.io/py/falcon-mcp.svg)](https://badge.fury.io/py/falcon-mcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/falcon-mcp)](https://pypi.org/project/falcon-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**falcon-mcp** is a Model Context Protocol (MCP) server that connects AI agents with the CrowdStrike Falcon platform, powering intelligent security analysis in your agentic workflows. It delivers programmatic access to essential security capabilities—including detections, incidents, and behaviors—establishing the foundation for advanced security operations and automation.

> [!IMPORTANT]
> **🚧 Public Preview**: This project is currently in public preview and under active development. Features and functionality may change before the stable 1.0 release. While we encourage exploration and testing, please avoid production deployments. We welcome your feedback through [GitHub Issues](https://github.com/crowdstrike/falcon-mcp/issues) to help shape the final release.

## Table of Contents

- [API Credentials \& Required Scopes](#api-credentials--required-scopes)
  - [Setting Up CrowdStrike API Credentials](#setting-up-crowdstrike-api-credentials)
  - [Required API Scopes by Module](#required-api-scopes-by-module)
- [Available Modules, Tools \& Resources](#available-modules-tools--resources)
  - [Cloud Security Module](#cloud-security-module)
  - [Core Functionality (Built into Server)](#core-functionality-built-into-server)
  - [Detections Module](#detections-module)
  - [Discover Module](#discover-module)
  - [Hosts Module](#hosts-module)
  - [Identity Protection Module](#identity-protection-module)
  - [Incidents Module](#incidents-module)
  - [Intel Module](#intel-module)
  - [Sensor Usage Module](#sensor-usage-module)
  - [Serverless Module](#serverless-module)
  - [Spotlight Module](#spotlight-module)
- [Installation \& Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Module Configuration](#module-configuration)
  - [Additional Command Line Options](#additional-command-line-options)
  - [As a Library](#as-a-library)
  - [Running Examples](#running-examples)
- [Container Usage](#container-usage)
  - [Using Pre-built Image (Recommended)](#using-pre-built-image-recommended)
  - [Building Locally (Development)](#building-locally-development)
- [Editor/Assistant Integration](#editorassistant-integration)
  - [Using `uvx` (recommended)](#using-uvx-recommended)
  - [With Module Selection](#with-module-selection)
  - [Using Individual Environment Variables](#using-individual-environment-variables)
  - [Docker Version](#docker-version)
- [Additional Deployment Options](#additional-deployment-options)
  - [Amazon Bedrock AgentCore](#amazon-bedrock-agentcore)
  - [Google Cloud (Cloud Run and Vertex AI)](#google-cloud-cloud-run-and-vertex-ai)
- [Contributing](#contributing)
  - [Getting Started for Contributors](#getting-started-for-contributors)
  - [Running Tests](#running-tests)
  - [Developer Documentation](#developer-documentation)
- [License](#license)
- [Support](#support)

## API Credentials & Required Scopes

### Setting Up CrowdStrike API Credentials

Before using the Falcon MCP Server, you need to create API credentials in your CrowdStrike console:

1. **Log into your CrowdStrike console**
2. **Navigate to Support > API Clients and Keys**
3. **Click "Add new API client"**
4. **Configure your API client**:
   - **Client Name**: Choose a descriptive name (e.g., "Falcon MCP Server")
   - **Description**: Optional description for your records
   - **API Scopes**: Select the scopes based on which modules you plan to use (see below)

> **Important**: Ensure your API client has the necessary scopes for the modules you plan to use. You can always update scopes later in the CrowdStrike console.

### Required API Scopes by Module

The Falcon MCP Server supports different modules, each requiring specific API scopes:

| Module | Required API Scopes | Purpose |
|-|-|-|
| **Cloud Security** | `Falcon Container Image:read` | Find and analyze kubernetes containers inventory and container imges vulnerabilities |
| **Core** | _No additional scopes_ | Basic connectivity and system information |
| **Detections** | `Alerts:read` | Find and analyze detections to understand malicious activity |
| **Discover** | `Assets:read` | Search and analyze application inventory across your environment |
| **Hosts** | `Hosts:read` | Manage and query host/device information |
| **Identity Protection** | `Identity Protection Entities:read`<br>`Identity Protection Timeline:read`<br>`Identity Protection Detections:read`<br>`Identity Protection Assessment:read`<br>`Identity Protection GraphQL:write` | Comprehensive entity investigation and identity protection analysis |
| **Incidents** | `Incidents:read` | Analyze security incidents and coordinated activities |
| **Intel** | `Actors (Falcon Intelligence):read`<br>`Indicators (Falcon Intelligence):read`<br>`Reports (Falcon Intelligence):read` | Research threat actors, IOCs, and intelligence reports |
| **Sensor Usage** | `Sensor Usage:read` | Access and analyze sensor usage data |
| **Serverless** | `Falcon Container Image:read` | Search for vulnerabilities in serverless functions across cloud service providers |
| **Spotlight** | `Vulnerabilities:read` | Manage and analyze vulnerability data and security assessments |

## Available Modules, Tools & Resources

> [!IMPORTANT]
> ⚠️ **Important Note on FQL Guide Resources**: Several modules include FQL (Falcon Query Language) guide resources that provide comprehensive query documentation and examples. While these resources are designed to assist AI assistants and users with query construction, **FQL has nuanced syntax requirements and field-specific behaviors** that may not be immediately apparent. AI-generated FQL filters should be **tested and validated** before use in production environments. We recommend starting with simple queries and gradually building complexity while verifying results in a test environment first.

**About Tools & Resources**: This server provides both tools (actions you can perform) and resources (documentation and context). Tools execute operations like searching for detections or analyzing threats, while resources provide comprehensive documentation like FQL query guides that AI assistants can reference for context without requiring tool calls.

### Cloud Security Module

**API Scopes Required**:

- `Falcon Container Image:read`

Provides tools for accessing and analyzing CrowdStrike Cloud Security resources:

- `falcon_search_kubernetes_containers`: Search for containers from CrowdStrike Kubernetes & Containers inventory
- `falcon_count_kubernetes_containers`: Count for containers by filter criteria from CrowdStrike Kubernetes & Containers inventory
- `falcon_search_images_vulnerabilities`: Search for images vulnerabilities from CrowdStrike Image Assessments

**Resources**:

- `falcon://cloud/kubernetes-containers/fql-guide`: Comprehensive FQL documentation and examples for kubernetes containers searches
- `falcon://cloud/images-vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for images vulnerabilities searches

**Use Cases**: Manage kubernetes containers inventory, container images vulnerabilities analysis

### Core Functionality (Built into Server)

**API Scopes**: _None required beyond basic API access_

The server provides core tools for interacting with the Falcon API:

- `falcon_check_connectivity`: Check connectivity to the Falcon API
- `falcon_list_enabled_modules`: Lists enabled modules in the falcon-mcp server
    > These modules are determined by the `--modules` [flag](#module-configuration) when starting the server. If no modules are specified, all available modules are enabled.
- `falcon_list_modules`: Lists all available modules in the falcon-mcp server

### Detections Module

**API Scopes Required**: `Alerts:read`

Provides tools for accessing and analyzing CrowdStrike Falcon detections:

- `falcon_search_detections`: Find and analyze detections to understand malicious activity in your environment
- `falcon_get_detection_details`: Get comprehensive detection details for specific detection IDs to understand security threats

**Resources**:

- `falcon://detections/search/fql-guide`: Comprehensive FQL documentation and examples for detection searches

**Use Cases**: Threat hunting, security analysis, incident response, malware investigation

### Discover Module

**API Scopes Required**: `Assets:read`

Provides tools for accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets:

- `falcon_search_applications`: Search for applications in your CrowdStrike environment
- `falcon_search_unmanaged_assets`: Search for unmanaged assets (systems without Falcon sensor installed) that have been discovered by managed systems

**Resources**:

- `falcon://discover/applications/fql-guide`: Comprehensive FQL documentation and examples for application searches
- `falcon://discover/hosts/fql-guide`: Comprehensive FQL documentation and examples for unmanaged assets searches

**Use Cases**: Application inventory management, software asset management, license compliance, vulnerability assessment, unmanaged asset discovery, security gap analysis

### Hosts Module

**API Scopes Required**: `Hosts:read`

Provides tools for accessing and managing CrowdStrike Falcon hosts/devices:

- `falcon_search_hosts`: Search for hosts in your CrowdStrike environment
- `falcon_get_host_details`: Retrieve detailed information for specified host device IDs

**Resources**:

- `falcon://hosts/search/fql-guide`: Comprehensive FQL documentation and examples for host searches

**Use Cases**: Asset management, device inventory, host monitoring, compliance reporting

### Identity Protection Module

**API Scopes Required**: `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection Detections:read`, `Identity Protection Assessment:read`, `Identity Protection GraphQL:write`

Provides tools for accessing and managing CrowdStrike Falcon Identity Protection capabilities:

- `idp_investigate_entity`: Entity investigation tool for analyzing users, endpoints, and other entities with support for timeline analysis, relationship mapping, and risk assessment

**Use Cases**: Entity investigation, identity protection analysis, user behavior analysis, endpoint security assessment, relationship mapping, risk assessment

### Incidents Module

**API Scopes Required**: `Incidents:read`

Provides tools for accessing and analyzing CrowdStrike Falcon incidents:

- `falcon_show_crowd_score`: View calculated CrowdScores and security posture metrics for your environment
- `falcon_search_incidents`: Find and analyze security incidents to understand coordinated activity in your environment
- `falcon_get_incident_details`: Get comprehensive incident details to understand attack patterns and coordinated activities
- `falcon_search_behaviors`: Find and analyze behaviors to understand suspicious activity in your environment
- `falcon_get_behavior_details`: Get detailed behavior information to understand attack techniques and tactics

**Resources**:

- `falcon://incidents/crowd-score/fql-guide`: Comprehensive FQL documentation for CrowdScore queries
- `falcon://incidents/search/fql-guide`: Comprehensive FQL documentation and examples for incident searches
- `falcon://incidents/behaviors/fql-guide`: Comprehensive FQL documentation and examples for behavior searches

**Use Cases**: Incident management, threat assessment, attack pattern analysis, security posture monitoring

### Intel Module

**API Scopes Required**:

- `Actors (Falcon Intelligence):read`
- `Indicators (Falcon Intelligence):read`
- `Reports (Falcon Intelligence):read`

Provides tools for accessing and analyzing CrowdStrike Intelligence:

- `falcon_search_actors`: Research threat actors and adversary groups tracked by CrowdStrike intelligence
- `falcon_search_indicators`: Search for threat indicators and indicators of compromise (IOCs) from CrowdStrike intelligence
- `falcon_search_reports`: Access CrowdStrike intelligence publications and threat reports
- `falcon_get_mitre_report`: Generate MITRE ATT&CK reports for threat actors, providing detailed tactics, techniques, and procedures (TTPs) in JSON or CSV format

**Resources**:

- `falcon://intel/actors/fql-guide`: Comprehensive FQL documentation and examples for threat actor searches
- `falcon://intel/indicators/fql-guide`: Comprehensive FQL documentation and examples for indicator searches
- `falcon://intel/reports/fql-guide`: Comprehensive FQL documentation and examples for intelligence report searches

**Use Cases**: Threat intelligence research, adversary tracking, IOC analysis, threat landscape assessment, MITRE ATT&CK framework analysis

### Sensor Usage Module

**API Scopes Required**: `Sensor Usage:read`

Provides tools for accessing and analyzing CrowdStrike Falcon sensor usage data:

- `falcon_search_sensor_usage`: Search for weekly sensor usage data in your CrowdStrike environment

**Resources**:

- `falcon://sensor-usage/weekly/fql-guide`: Comprehensive FQL documentation and examples for sensor usage searches

**Use Cases**: Sensor deployment monitoring, license utilization analysis, sensor health tracking

### Serverless Module

**API Scopes Required**: `Falcon Container Image:read`

Provides tools for accessing and managing CrowdStrike Falcon Serverless Vulnerabilities:

- `falcon_search_serverless_vulnerabilities`: Search for vulnerabilities in your serverless functions across all cloud service providers

**Resources**:

- `falcon://serverless/vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for serverless vulnerabilities searches

**Use Cases**: Serverless security assessment, vulnerability management, cloud security monitoring

### Spotlight Module

**API Scopes Required**: `Vulnerabilities:read`

Provides tools for accessing and managing CrowdStrike Spotlight vulnerabilities:

- `falcon_search_vulnerabilities`: Search for vulnerabilities in your CrowdStrike environment

**Resources**:

- `falcon://spotlight/vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for vulnerability searches

**Use Cases**: Vulnerability management, security assessments, compliance reporting, risk analysis, patch prioritization

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- [`uv`](https://docs.astral.sh/uv/) or pip
- CrowdStrike Falcon API credentials (see above)

### Environment Configuration

You can configure your CrowdStrike API credentials in several ways:

#### Use a `.env` File

If you prefer using a `.env` file, you have several options:

##### Option 1: Copy from cloned repository (if you've cloned it)

```bash
cp .env.example .env
```

##### Option 2: Download the example file from GitHub

```bash
curl -o .env https://raw.githubusercontent.com/CrowdStrike/falcon-mcp/main/.env.example
```

##### Option 3: Create manually with the following content

```bash
# Required Configuration
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com

# Optional Configuration (uncomment and modify as needed)
#FALCON_MCP_MODULES=detections,incidents,intel
#FALCON_MCP_TRANSPORT=stdio
#FALCON_MCP_DEBUG=false
#FALCON_MCP_HOST=127.0.0.1
#FALCON_MCP_PORT=8000
#FALCON_MCP_STATELESS_HTTP=false
```

#### Environment Variables

Alternatively, you can use environment variables directly.

Set the following environment variables in your shell:

```bash
# Required Configuration
export FALCON_CLIENT_ID="your-client-id"
export FALCON_CLIENT_SECRET="your-client-secret"
export FALCON_BASE_URL="https://api.crowdstrike.com"

# Optional Configuration
export FALCON_MCP_MODULES="detections,incidents,intel"  # Comma-separated list (default: all modules)
export FALCON_MCP_TRANSPORT="stdio"                     # Transport method: stdio, sse, streamable-http
export FALCON_MCP_DEBUG="false"                         # Enable debug logging: true, false
export FALCON_MCP_HOST="127.0.0.1"                      # Host for HTTP transports
export FALCON_MCP_PORT="8000"                           # Port for HTTP transports
export FALCON_MCP_STATELESS_HTTP="false"                # Stateless mode for scalable deployments
```

**CrowdStrike API Region URLs:**

- **US-1 (Default)**: `https://api.crowdstrike.com`
- **US-2**: `https://api.us-2.crowdstrike.com`
- **EU-1**: `https://api.eu-1.crowdstrike.com`
- **US-GOV**: `https://api.laggar.gcw.crowdstrike.com`

### Installation

> [!NOTE]
> If you just want to interact with falcon-mcp via an agent chat interface rather than running the server itself, take a look at [Additional Deployment Options](#additional-deployment-options). Otherwise continue to the installations steps below.

#### Install using uv

```bash
uv tool install falcon-mcp
```

#### Install using pip

```bash
pip install falcon-mcp
```

> [!TIP]
> If `falcon-mcp` isn't found, update your shell PATH.

For installation via code editors/assistants, see the [Editor/Assitant](#editorassistant-integration) section below

## Usage

### Command Line

Run the server with default settings (stdio transport):

```bash
falcon-mcp
```

Run with SSE transport:

```bash
falcon-mcp --transport sse
```

Run with streamable-http transport:

```bash
falcon-mcp --transport streamable-http
```

Run with streamable-http transport on custom port:

```bash
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

Run with stateless HTTP mode (for scalable deployments like AWS AgentCore):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

### Module Configuration

The Falcon MCP Server supports multiple ways to specify which modules to enable:

#### 1. Command Line Arguments (highest priority)

Specify modules using comma-separated lists:

```bash
# Enable specific modules
falcon-mcp --modules detections,incidents,intel,spotlight,idp

# Enable only one module
falcon-mcp --modules detections
```

#### 2. Environment Variable (fallback)

Set the `FALCON_MCP_MODULES` environment variable:

```bash
# Export environment variable
export FALCON_MCP_MODULES=detections,incidents,intel,spotlight,idp
falcon-mcp

# Or set inline
FALCON_MCP_MODULES=detections,incidents,intel,spotlight,idp falcon-mcp
```

#### 3. Default Behavior (all modules)

If no modules are specified via command line or environment variable, all available modules are enabled by default.

**Module Priority Order:**

1. Command line `--modules` argument (overrides all)
2. `FALCON_MCP_MODULES` environment variable (fallback)
3. All modules (default when none specified)

### Additional Command Line Options

For all available options:

```bash
falcon-mcp --help
```

### As a Library

```python
from falcon_mcp.server import FalconMCPServer

# Create and run the server
server = FalconMCPServer(
    base_url="https://api.us-2.crowdstrike.com",  # Optional, defaults to env var
    debug=True,  # Optional, enable debug logging
    enabled_modules=["detections", "incidents", "spotlight", "idp"]  # Optional, defaults to all modules
)

# Run with stdio transport (default)
server.run()

# Or run with SSE transport
server.run("sse")

# Or run with streamable-http transport
server.run("streamable-http")

# Or run with streamable-http transport on custom host/port
server.run("streamable-http", host="0.0.0.0", port=8080)
```

### Running Examples

```bash
# Run with stdio transport
python examples/basic_usage.py

# Run with SSE transport
python examples/sse_usage.py

# Run with streamable-http transport
python examples/streamable_http_usage.py
```

## Container Usage

The Falcon MCP Server is available as a pre-built container image for easy deployment:

### Using Pre-built Image (Recommended)

```bash
# Pull the latest pre-built image
docker pull quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file (recommended)
docker run -i --rm --env-file /path/to/.env quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file and SSE transport
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport sse --host 0.0.0.0

# Run with .env file and streamable-http transport
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0

# Run with .env file and custom port
docker run --rm -p 8080:8080 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0 --port 8080

# Run with .env file and specific modules (stdio transport - requires -i flag)
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --modules detections,incidents,spotlight,idp

# Use a specific version instead of latest (stdio transport - requires -i flag)
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:1.2.3

# Alternative: Individual environment variables (stdio transport - requires -i flag)
docker run -i --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  quay.io/crowdstrike/falcon-mcp:latest
```

### Building Locally (Development)

For development or customization purposes, you can build the image locally:

```bash
# Build the Docker image
docker build -t falcon-mcp .

# Run the locally built image
docker run --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret falcon-mcp
```

> [!NOTE]
> When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to the container.

## Editor/Assistant Integration

You can integrate the Falcon MCP server with your editor or AI assistant. Here are configuration examples for popular MCP clients:

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
        "detections,incidents,intel"
      ]
    }
  }
}
```

### Using Individual Environment Variables

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

### Docker Version

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

> [!NOTE]
> The `-i` flag is required when using the default stdio transport.

## Additional Deployment Options

### Amazon Bedrock AgentCore

To deploy the MCP Server as a tool in Amazon Bedrock AgentCore, please refer to the [following document](./docs/deployment/amazon_bedrock_agentcore.md).

### Google Cloud (Cloud Run and Vertex AI)

To deploy the MCP server as an agent within Cloud Run or Vertex AI Agent Engine (including for registration within Agentspace), refer to the [Google ADK example](./examples/adk/README.md).

## Contributing

### Getting Started for Contributors

1. Clone the repository:

   ```bash
   git clone https://github.com/CrowdStrike/falcon-mcp.git
   cd falcon-mcp
   ```

2. Install in development mode:

   ```bash
   # Create .venv and install dependencies
   uv sync --all-extras

   # Activate the venv
   source .venv/bin/activate
   ```

> [!IMPORTANT]
> This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases and semantic versioning. Please follow the commit message format outlined in our [Contributing Guide](docs/CONTRIBUTING.md) when submitting changes.

### Running Tests

```bash
# Run all tests
pytest

# Run end-to-end tests
pytest --run-e2e tests/e2e/

# Run end-to-end tests with verbose output (note: -s is required to see output)
pytest --run-e2e -v -s tests/e2e/
```

> **Note**: The `-s` flag is required to see detailed output from E2E tests.

### Developer Documentation

- [Module Development Guide](docs/module_development.md): Instructions for implementing new modules
- [Resource Development Guide](docs/resource_development.md): Instructions for implementing resources
- [End-to-End Testing Guide](docs/e2e_testing.md): Guide for running and understanding E2E tests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

This is a community-driven, open source project. While it is not an official CrowdStroke product, it is actively maintained by CrowdStrike and supported in collaboration with the open source developer community.

For more information, please see our [SUPPORT](SUPPORT.md) file.
