---
title: Basic Usage
description: Python code examples for using the Falcon MCP Server programmatically.
---

These examples show how to run the Falcon MCP Server programmatically using the Python API.

## stdio Transport (Default)

The simplest way to run the server. MCP clients manage the process via stdin/stdout.

```python
#!/usr/bin/env python3
"""Basic usage example for Falcon MCP Server."""

import os
from dotenv import load_dotenv
from falcon_mcp.server import FalconMCPServer


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Create and run the server with stdio transport
    server = FalconMCPServer(
        # Optionally override the base URL
        # base_url="https://api.us-2.crowdstrike.com",
        debug=os.environ.get("DEBUG", "").lower() == "true",
    )

    # Run with stdio transport (default)
    server.run()


if __name__ == "__main__":
    main()
```

To run:

```bash
python examples/basic_usage.py
```

## SSE Transport

For web-based clients that connect via HTTP.

```python
#!/usr/bin/env python3
"""SSE transport example for Falcon MCP Server."""

import os
from dotenv import load_dotenv
from falcon_mcp.server import FalconMCPServer


def main() -> None:
    load_dotenv()

    server = FalconMCPServer(
        debug=os.environ.get("DEBUG", "").lower() == "true",
    )

    # Run with SSE transport — listens at http://127.0.0.1:8000/sse
    server.run("sse")


if __name__ == "__main__":
    main()
```

To run:

```bash
python examples/sse_usage.py
```

## Streamable HTTP Transport

The recommended transport for server deployments.

```python
#!/usr/bin/env python3
"""Streamable HTTP transport example for Falcon MCP Server."""

import os
from dotenv import load_dotenv
from falcon_mcp.server import FalconMCPServer


def main() -> None:
    load_dotenv()

    # Custom host/port for external access
    server = FalconMCPServer(
        debug=os.environ.get("DEBUG", "").lower() == "true",
        host="0.0.0.0",
        port=8080,
    )

    # Run — listens at http://0.0.0.0:8080/mcp
    server.run("streamable-http")


if __name__ == "__main__":
    main()
```

To run:

```bash
python examples/streamable_http_usage.py
```

## Direct Credentials (Secret Management)

For enterprise deployments using secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.):

```python
from falcon_mcp.server import FalconMCPServer

# Retrieve credentials from your secrets manager
# client_id = vault.read_secret("crowdstrike/client_id")
# client_secret = vault.read_secret("crowdstrike/client_secret")

server = FalconMCPServer(
    client_id="your-client-id",
    client_secret="your-client-secret",
    base_url="https://api.us-2.crowdstrike.com",
    enabled_modules=["detections", "hosts"]
)

server.run()
```

When both direct parameters and environment variables are set, direct parameters take precedence.
