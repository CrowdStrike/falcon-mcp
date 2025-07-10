# Falcon MCP Server

A Model Context Protocol (MCP) server for CrowdStrike Falcon that provides AI assistants with access to
CrowdStrike Falcon capabilities.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- CrowdStrike Falcon API credentials

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/CrowdStrike/falcon-mcp.git
   cd falcon-mcp
   ```

1. Install dependencies:

   ```bash
   # Optionally create a virtual environment
   python -m venv .venv && source .venv/bin/activate

   pip install -e .
   ```

1. Create a `.env` file with your Falcon API credentials:

   ```bash
   FALCON_CLIENT_ID=your-client-id
   FALCON_CLIENT_SECRET=your-client-secret
   FALCON_BASE_URL=https://api.us-2.crowdstrike.com  # Or your appropriate region
   # Optional: Specify which modules to enable (comma-separated)
   FALCON_MODULES=detections,incidents,intel,hosts
   ```

### Usage

#### Command Line

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

### Docker Usage

The Falcon MCP Server can be run in Docker containers for easy deployment:

```bash
# Build the Docker image
docker build -t falcon-mcp .

# Run with stdio transport (default)
docker run --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret falcon-mcp

# Run with SSE transport
docker run --rm -p 8000:8000 -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  falcon-mcp --transport sse --host 0.0.0.0

# Run with streamable-http transport
docker run --rm -p 8000:8000 -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  falcon-mcp --transport streamable-http --host 0.0.0.0

# Run with custom port
docker run --rm -p 8080:8080 -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080

# Run with specific modules
docker run --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  falcon-mcp --modules detections,incidents
```

**Note**: When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to the container.

#### Module Configuration

The Falcon MCP Server supports multiple ways to specify which modules to enable:

##### 1. Command Line Arguments (highest priority)

Specify modules using comma-separated lists:

```bash
# Enable specific modules
falcon-mcp --modules detections,incidents,intel

# Enable only one module
falcon-mcp --modules detections
```

##### 2. Environment Variable (fallback)

Set the `FALCON_MODULES` environment variable:

```bash
# Export environment variable
export FALCON_MODULES=detections,incidents,intel
falcon-mcp

# Or set inline
FALCON_MODULES=detections,incidents,intel falcon-mcp
```

##### 3. Default Behavior (all modules)

If no modules are specified via command line or environment variable, all available modules are enabled by default.

**Module Priority Order:**

1. Command line `--modules` argument (overrides all)
2. `FALCON_MODULES` environment variable (fallback)
3. All modules (default when none specified)

#### Additional Command Line Options

For all available options:

```bash
falcon-mcp --help
```

#### As a Library

```python
from falcon_mcp.server import FalconMCPServer

# Create and run the server
server = FalconMCPServer(
    client_id="your-client-id",  # Optional, defaults to env var
    client_secret="your-client-secret",  # Optional, defaults to env var
    base_url="https://api.us-2.crowdstrike.com",  # Optional, defaults to env var
    debug=True  # Optional, enable debug logging
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

#### Running examples

```python
pip install -e .

# Run with stdio transport
python examples/basic_usage.py

# Run with SSE transport
python examples/sse_usage.py

# Run with streamable-http transport
python examples/streamable_http_usage.py
```

#### Running tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run end-to-end tests
pytest --run-e2e tests/e2e/

# Run end-to-end tests with verbose output (note: -s is required to see output)
pytest --run-e2e -v -s tests/e2e/
```

> **Note**: The `-s` flag is required to see detailed output from E2E tests.

For more details on running tests, see the [End-to-End Testing Guide](docs/e2e_testing.md).

#### Editor Integration

You can integrate the Falcon MCP server with your editor in two ways:

##### Using an .env file (recommended)

This approach keeps your credentials in a single `.env` file (which should be gitignored) and references them in the editor configuration:

1. Create a `.env` file in your project root with your credentials:

   ```bash
   FALCON_CLIENT_ID=your-client-id
   FALCON_CLIENT_SECRET=your-client-secret
   FALCON_BASE_URL=https://api.us-2.crowdstrike.com  # Or your appropriate region
   ```

2. Configure your editor to use environment variables from the `.env` file:

   ```json
   {
     "mcpServers": {
       "falcon-mcp": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "--env-file",
           "/full/path/to/.env",
           "falcon-mcp"
         ],
         "disabled": false
       }
     }
   }
   ```

This approach is more secure and maintainable as it:

- Keeps sensitive credentials out of your editor configuration
- Allows you to easily update credentials in one place
- Prevents accidental credential exposure in version control

###### Direct environment variables (alternative)

Alternatively, you can specify environment variables directly in the configuration:

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "FALCON_CLIENT_ID",
        "-e",
        "FALCON_CLIENT_SECRET",
        "-e",
        "FALCON_BASE_URL",
        "falcon-mcp"
      ],
      "env": {
        "FALCON_CLIENT_ID": "YOUR_CLIENT_ID",
        "FALCON_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "FALCON_BASE_URL": "YOUR_BASE_URL"
      },
      "disabled": false
    }
  }
}
```

## Available Modules

### Core Functionality (Built into Server)

The server provides core tools for interacting with the Falcon API:

- `falcon_check_connectivity`: Check connectivity to the Falcon API
- `falcon_get_available_modules`: Get information about available modules

### Detections Module

Provides tools for accessing and analyzing CrowdStrike Falcon detections:

- `falcon_search_detections`: Find and analyze detections to understand malicious activity in your environment
- `falcon_search_detections_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_detections tool
- `falcon_get_detection_details`: Get comprehensive detection details for specific detection IDs to understand security threats

### Incidents Module

Provides tools for accessing and analyzing CrowdStrike Falcon incidents:

- `falcon_show_crowd_score`: View calculated CrowdScores and security posture metrics for your environment
- `falcon_show_crowd_score_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_show_crowd_score tool
- `falcon_search_incidents`: Find and analyze security incidents to understand coordinated activity in your environment
- `falcon_search_incidents_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_incidents tool
- `falcon_get_incident_details`: Get comprehensive incident details to understand attack patterns and coordinated activities
- `falcon_search_behaviors`: Find and analyze behaviors to understand suspicious activity in your environment
- `falcon_search_behaviors_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_behaviors tool
- `falcon_get_behavior_details`: Get detailed behavior information to understand attack techniques and tactics

### Intel Module

Provides tools for accessing and analyzing CrowdStrike Intel:

- `falcon_search_actors`: Research threat actors and adversary groups tracked by CrowdStrike intelligence
- `falcon_search_actors_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_actors tool
- `falcon_search_indicators`: Search for threat indicators and indicators of compromise (IOCs) from CrowdStrike intelligence
- `falcon_search_indicators_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_indicators tool
- `falcon_search_reports`: Access CrowdStrike intelligence publications and threat reports
- `falcon_search_reports_fql_filter_guide`: Get comprehensive FQL documentation for the search_reports tool

### Hosts Module

Provides tools for accessing and managing CrowdStrike Falcon hosts/devices:

- `falcon_search_hosts`: Search for hosts in your CrowdStrike environment
- `falcon_search_hosts_fql_filter_guide`: Get comprehensive FQL documentation for the falcon_search_hosts tool
- `falcon_get_host_details`: Retrieve detailed information for specified host device IDs

## MCP Configuration

To use the Falcon MCP server with AI assistants, you can use the provided `examples/mcp_config.json` file:

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
      "name": "falcon-stdio-docker",
      "transport": {
        "type": "stdio",
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "--env-file",
          "/full/path/to/.env",
          "falcon-mcp"
        ]
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

## Documentation

- [Module Development Guide](docs/module_development.md): Instructions for implementing new modules
- [Resource Development Guide](docs/resource_development.md): Instructions for implementing resources
- [Architecture Decisions](docs/architecture_decisions.md): Key architectural decisions and their rationale
- [End-to-End Testing Guide](docs/e2e_testing.md): Guide for running and understanding E2E tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.
