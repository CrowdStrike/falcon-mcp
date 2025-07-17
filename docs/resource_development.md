# Falcon MCP Server Resource Development Guide

This guide provides instructions for implementing and registering resources for the Falcon MCP server.

## What are Resources?

Resources in the Falcon MCP server represent data sources that can be accessed by the model. Unlike tools, which perform actions, resources provide context or information that the model can reference. Resources are particularly useful for:

1. Providing documentation or guides that the model can reference
2. Exposing structured data that tools can use
3. Making reference information available without requiring a tool call

## Resource Structure

Each resource should:

1. Be created using an appropriate resource class (e.g., `TextResource`)
2. Have a unique URI that identifies it
3. Include a descriptive name and description
4. Be registered with the MCP server through a module's `register_resources` method

## Step-by-Step Implementation Guide

### 1. Create Resource Content

First, define the content for your resource. This could be:

- Documentation text in a separate file
- Structured data in a Python dictionary
- Reference information in a dedicated module

For text-based resources, it's recommended to store the content in a separate file in the `falcon_mcp/resources` directory:

```python
# falcon_mcp/resources/your_resource.py
YOUR_RESOURCE_CONTENT = """
Detailed documentation or reference information goes here.
This can be multi-line text with formatting.

## Section Headers

- Bullet points
- And other formatting

Code examples:
...

"""

```

### 2. Register Resources in Your Module

In your module class, implement the `register_resources` method:

```python
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl

from ..resources.your_resource import YOUR_RESOURCE_CONTENT
from .base import BaseModule


class YourModule(BaseModule):
    """Your module description."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        # Tool registration code...

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        your_resource = TextResource(
            uri=AnyUrl("falcon://your-module/resource-name"),
            name="your_resource_name",
            description="Description of what this resource provides.",
            text=YOUR_RESOURCE_CONTENT
        )

        self._add_resource(
            server,
            your_resource
        )
```

### 3. Resource URI Conventions

Resource URIs should follow a consistent pattern:

- Start with `falcon://` as the scheme
- Include the module name as the first path segment
- Use descriptive path segments for the resource
- Use hyphens to separate words in path segments

Examples:

- `falcon://intel/query_actor_entities/fql-guide`
- `falcon://detections/search/fql-guide`
- `falcon://incidents/status-codes`

### 4. Resource Types

The MCP server supports several resource types:

#### TextResource

Used for providing text-based documentation or reference information:

```python
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl

text_resource = TextResource(
    uri=AnyUrl("falcon://module/resource-name"),
    name="resource_name",
    description="Resource description",
    text="Resource content"
)
```

#### Other Resource Types

Additional resource types may be available depending on the MCP server implementation. Consult the MCP server documentation for details on other resource types.

## Best Practices

### Resource Content

1. **Comprehensive Documentation**: Provide detailed information that covers all aspects of the topic
2. **Structured Format**: Use clear section headers, bullet points, and code examples
3. **Examples**: Include practical examples that demonstrate usage
4. **Consistent Style**: Follow a consistent documentation style across all resources

### Resource Registration

1. **Descriptive Names**: Use clear, descriptive names for resources
2. **Detailed Descriptions**: Provide informative descriptions that explain what the resource contains
3. **Logical Organization**: Group related resources together with consistent URI patterns
4. **Reference from Tools**: Reference resources in tool documentation where appropriate

### Resource Usage

1. **Tool Integration**: Design resources to complement tools by providing context or documentation
2. **Self-Contained**: Resources should be self-contained and not require additional context
3. **Versioning**: Consider versioning strategies for resources that may change over time

## Example: Intel Module Resources

The Intel module provides a good example of resource implementation:

```python
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl

from ..resources.intel import QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION
from .base import BaseModule


class IntelModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon intelligence data."""

    def register_resources(self, server) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """

        query_actor_entities_resource = TextResource(
            uri=AnyUrl("falcon://intel/query_actor_entities/fql-guide"),
            name="falcon_query_actor_entities_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_actors` tool.",
            text=QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION
        )

        self._add_resource(
            server,
            query_actor_entities_resource
        )
```

In this example:

1. The resource content (`QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION`) is defined in a separate file (`falcon_mcp/resources/intel.py`)
2. The resource is created as a `TextResource` with a clear URI, name, and description
3. The resource is registered with the server using the `_add_resource` method
4. The resource complements the `search_actors` tool by providing documentation for its `filter` parameter

## Integrating Resources with Tools

Resources can be particularly valuable when integrated with tools. Here's how the Intel module references its resource in a tool method:

```python
def query_actor_entities(
    self,
    filter: Optional[str] = Field(
        default=None,
        description="FQL query expression that should be used to limit the results. IMPORTANT: use the 'falcon://query_actor_entities_fql_documentation' resource when building this parameter."
    ),
    # Other parameters...
) -> List[Dict[str, Any]]:
    """Get info about actors that match provided FQL filters.

    IMPORTANT: You must call the FQL Guide for Intel Query Actor Entities (falcon://intel/query_actor_entities/fql-guide) resource first

    Returns:
        Information about actors that match the provided filters.
    """
    # Method implementation...
```

Note how:

1. The resource URI is referenced in the parameter description
2. The docstring explicitly mentions the resource that should be consulted
3. This creates a clear link between the tool and its supporting documentation

## Contributing Resource Changes

When contributing new resources or changes to existing resources, please follow these guidelines:

### Conventional Commits for Resources

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases and clear commit history. When contributing resource-related changes, use these commit message patterns:

**Adding New Resources:**

```bash
git commit -m "feat(resources): add FQL guide for [module-name] module"
git commit -m "feat(resources): add documentation for [specific-topic]"
# Examples:
git commit -m "feat(resources): add FQL guide for cloud module"
git commit -m "feat(resources): add hosts search documentation"
```

**Modifying Existing Resources:**

```bash
git commit -m "refactor(resources): reword FQL guide in cloud resource"
git commit -m "fix(resources): correct formatting in intel FQL documentation"
git commit -m "docs(resources): update resource development guide"
# Examples:
git commit -m "refactor(resources): improve clarity in detections FQL guide"
git commit -m "fix(resources): correct syntax examples in incidents resource"
```

**Resource Tests and Infrastructure:**

```bash
git commit -m "test(resources): add validation tests for resource content"
git commit -m "chore(resources): update resource registration patterns"
```

See the main [CONTRIBUTING.md](CONTRIBUTING.md) guide for complete conventional commits guidelines.

## Conclusion

Resources are a powerful way to provide context and documentation to the model. By following the guidelines in this document, you can create effective resources that complement your tools and enhance the overall functionality of the Falcon MCP server.

When developing resources:

1. Focus on providing clear, comprehensive information
2. Follow consistent naming and URI conventions
3. Integrate resources with related tools
4. Test resource registration to ensure proper functionality

Resources, when used effectively alongside tools, create a more powerful and user-friendly experience by providing the necessary context and documentation for complex operations.
