# Falcon MCP Server

A Model Context Protocol (MCP) server for CrowdStrike Falcon that provides AI assistants with access to
CrowdStrike Falcon capabilities.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- CrowdStrike Falcon API credentials

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/CrowdStrike/falcon-mcp.git
   cd falcon-mcp
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Falcon API credentials:

   ```bash
   FALCON_CLIENT_ID=your-client-id
   FALCON_CLIENT_SECRET=your-client-secret
   FALCON_BASE_URL=https://api.us-2.crowdstrike.com  # Or your appropriate region
   ```

### Usage

#### Command Line

Run the server with default settings (stdio transport):

```bash
python -m falcon-mcp
```

Run with SSE transport:

```bash
python -m falcon-mcp --transport sse
```

Run with specific modules:

```bash
python -m falcon-mcp --modules detections
```

For all available options:

```bash
python -m falcon-mcp --help
```

#### As a Library

```python
from src.server import FalconMCPServer

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
```

#### Running examples

```python
pip install -e .
cd examples
python sse_usage.py
```

#### Running tests

```python
pip install -e ".[dev]"
pytest
```

## Available Modules

### Core Functionality (Built into Server)

The server provides core tools for interacting with the Falcon API:

- `check_falcon_connectivity`: Check connectivity to the Falcon API
- `get_available_modules`: Get information about available modules

### Detections Module

Provides tools for accessing and analyzing CrowdStrike Falcon detections:

- `detects_query_detects`: Search for detections in your CrowdStrike environment
- `detects_get_detect_summaries`: Get detailed information about a specific detection

### Incidents Module

Provides tools for accessing and analyzing CrowdStrike Falcon incidents:

- `incidents_crowd_score`: Show CrowdScore in the environment
- `incidents_get_incidents`: Get incidents by ID
- `incidents_query_incidents`: Query for incidents
- `incidents_get_behaviors`: Get behaviors by ID
- `incidents_query_behaviors`: Query for behaviors

## MCP Configuration

To use the Falcon MCP server with AI assistants, you can use the provided `examples/mcp_config.json` file:

```json
{
  "servers": [
    {
      "name": "falcon-stdio",
      "transport": {
        "type": "stdio",
        "command": "python -m falcon-mcp"
      }
    },
    {
      "name": "falcon-sse",
      "transport": {
        "type": "sse",
        "url": "http://127.0.0.1:8000/sse"
      }
    }
  ]
}
```

## Documentation

- [Module Development Guide](docs/module_development.md): Instructions for implementing new modules
- [Architecture Decisions](docs/architecture_decisions.md): Key architectural decisions and their rationale

## License

This project is licensed under the MIT License - see the LICENSE file for details.
