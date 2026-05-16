---
title: Module Development
description: Step-by-step guide for implementing new Falcon MCP modules.
---

This guide covers implementing new modules for the Falcon MCP Server.

## Module Structure

Each module:

1. Inherits from `BaseModule`
2. Implements `register_tools()`
3. Defines tool methods that interact with the Falcon API
4. Uses common utilities for error handling and API interactions

## Step 1: Create the Module File

Create `falcon_mcp/modules/your_module.py`:

```python
"""Your module for Falcon MCP Server."""
from typing import Any

from mcp.server import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class YourModule(BaseModule):
    """Module for [description]."""

    def register_tools(self, server: FastMCP) -> None:
        # Read-only tool — default annotations apply automatically
        self._add_tool(
            server=server,
            method=self.your_search_method,
            name="your_search_name",
        )

        # Mutating tool — must override annotations
        self._add_tool(
            server=server,
            method=self.your_create_method,
            name="your_create_name",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def your_search_method(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://your-module/entities/fql-guide` for syntax.",
        ),
        limit: int = Field(default=100, ge=1, le=500),
    ) -> list[dict[str, Any]]:
        """Search for entities in your CrowdStrike environment.

        Use this to find entities by name, status, or other attributes. Consult
        falcon://your-module/entities/fql-guide before constructing filter expressions.
        Returns full entity details.
        """
        ids = self._base_search("QueryOperation", filter=filter, limit=limit)
        if self._is_error(ids):
            return [ids]
        if ids:
            details = self._base_get_by_ids("GetOperation", ids)
            if self._is_error(details):
                return [details]
            return details
        return []
```

## Step 2: Auto-Discovery

Modules are **automatically discovered** — no manual imports or registration needed. The registry scans `falcon_mcp/modules/`, finds classes ending in `Module`, and registers them.

## Step 3: Tool Annotations

All tools default to `READ_ONLY_ANNOTATIONS`. Override for mutating tools:

| Tool Type | readOnlyHint | destructiveHint | idempotentHint |
|-----------|:---:|:---:|:---:|
| Search/Get/List | `True` | `False` | `True` |
| Create/Write | `False` | `False` | `False` |
| Delete/Remove | `False` | `True` | `True` |
| Launch/Trigger | `False` | `False` | `False` |

## Step 4: Search Tool Pattern

**Search tools MUST return full entity details, not just IDs.** Always follow the two-step pattern:

```python
# Step 1: Query for IDs
ids = self._base_search("QueryDevicesByFilter", filter=filter, limit=limit)
if self._is_error(ids):
    return [ids]

# Step 2: Fetch full details
if ids:
    return self._base_get_by_ids("PostDeviceDetailsV2", ids)
return []
```

## Step 5: Add Tests

Create `tests/modules/test_your_module.py` inheriting from `TestModules`:

```python
from falcon_mcp.modules.your_module import YourModule
from tests.modules.utils.test_modules import TestModules


class TestYourModule(TestModules):
    def setUp(self):
        self.setup_module(YourModule)

    def test_register_tools(self):
        self.assert_tools_registered(["falcon_your_search_name"])

    def test_search_returns_details(self):
        mock_response = {"status_code": 200, "body": {"resources": ["id1"]}}
        self.mock_client.command.return_value = mock_response
        result = self.module.your_search_method()
        # verify result contains full details, not IDs
```

## Type Hints

Use modern Python 3.10+ syntax:

```python
# ✅ Correct
def search(filter: str | None = None) -> list[dict[str, Any]]:

# ❌ Avoid
from typing import Optional, List, Dict
def search(filter: Optional[str] = None) -> List[Dict[str, Any]]:
```

## Common Utilities

| Module | Utility |
|--------|---------|
| `falcon_mcp.common.errors` | `handle_api_response`, `is_success_response` |
| `falcon_mcp.common.utils` | `prepare_api_parameters`, `extract_resources` |
| `falcon_mcp.common.logging` | `get_logger` |
| `falcon_mcp.common.api_scopes` | `get_required_scopes` |
