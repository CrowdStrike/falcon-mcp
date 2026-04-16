---
title: Resource Development
description: How to implement and register MCP resources in the Falcon MCP Server.
---

Resources provide documentation and context to AI assistants without requiring a tool call. They are particularly useful for FQL (Falcon Query Language) guides that help AI assistants construct accurate queries.

## What Are Resources?

Unlike tools (which perform actions), resources provide reference information — documentation, FQL syntax guides, or structured data that a model can read at any time via a URI.

## Step 1: Create Resource Content

Store content in `falcon_mcp/resources/your_resource.py`:

```python
YOUR_RESOURCE_CONTENT = """
## FQL Filter Guide

Use these fields when filtering:

| Field | Type | Description |
|-------|------|-------------|
| `status` | String | Entity status. Ex: `new`, `in_progress`, `closed` |
| `severity` | Integer | Severity 1-4. Ex: `severity:>=3` |

## Examples

# Recent high-severity items
status:'new'+severity:>=3

# Items in the last 24 hours
created_timestamp:>'2024-01-01T00:00:00Z'

"""

```

## Step 2: Register the Resource

In your module class, implement `register_resources()`:

```python
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl

from falcon_mcp.resources.your_resource import YOUR_RESOURCE_CONTENT
from falcon_mcp.modules.base import BaseModule


class YourModule(BaseModule):
    def register_resources(self, server: FastMCP) -> None:
        resource = TextResource(
            uri=AnyUrl("falcon://your-module/entities/fql-guide"),
            name="falcon_your_module_fql_guide",
            description="FQL documentation for your_module entity searches.",
            text=YOUR_RESOURCE_CONTENT,
        )
        self._add_resource(server, resource)
```

## URI Conventions

Resource URIs follow the pattern:

```text
falcon://<module-name>/<resource-name>/<type>
```

Examples:

- `falcon://detections/search/fql-guide`
- `falcon://intel/actors/fql-guide`
- `falcon://hosts/search/fql-guide`

Use hyphens to separate words in path segments.

## Linking Resources to Tools

Reference the resource URI in your tool's docstring and parameter descriptions so AI assistants know to fetch it:

```python
def search_entities(
    self,
    filter: str | None = Field(
        default=None,
        description="FQL filter. IMPORTANT: use the falcon://your-module/entities/fql-guide resource when building this parameter.",
    ),
) -> list[dict[str, Any]]:
    """Search for entities.

    IMPORTANT: Call the FQL guide resource first:
    falcon://your-module/entities/fql-guide
    """
```

## FQL Table Format

Use `generate_md_table` for consistent FQL filter documentation:

```python
from falcon_mcp.common.utils import generate_md_table

FQL_FILTERS = [
    ("field_name", "String", "Description with examples. Ex: example_value"),
    ("other_field", "Integer", "Numeric field. Ex: 42"),
]

DOCUMENTATION = """## FQL Filter Guide\n\n""" + generate_md_table(FQL_FILTERS)
```

## Commit Messages

```bash frame="none"
git commit -m "feat(resources): add FQL guide for [module-name] module"
git commit -m "refactor(resources): improve clarity in detections FQL guide"
```
