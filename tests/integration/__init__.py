"""Integration tests for Falcon MCP Server modules.

These tests make real API calls to the CrowdStrike Falcon platform and require
valid credentials. They validate:
- Correct FalconPy operation names
- HTTP method usage (POST body vs GET query parameters)
- Two-step search patterns returning full details
- API response schema compatibility

Run with: uv run pytest --run-integration tests/integration/
"""
