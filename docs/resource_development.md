# Falcon MCP Server Resource Development Guide

This guide provides instructions for implementing resources for the Falcon MCP server.

## What are Resources?

Resources in the Model Context Protocol (MCP) represent data sources that can be accessed by clients. Unlike tools, which are functions that can be called with arguments, resources are data objects that can be accessed directly. Resources are useful for providing context, configuration, or other data that doesn't require computation.

Examples of resources include:

- Configuration data
- Reference information
- Static data sets
- Cached API responses
- System information

## Resource Structure

Resources in the Falcon MCP server:

1. Are registered by modules
2. Have a unique URI prefixed with `falcon:`
3. Are provided by a function that returns the resource data
4. Can have an optional description

## Step-by-Step Implementation Guide

### 1. Update Your Module Class

Modify your module class to implement the `register_resources` method:

```python
def register_resources(self, server: FastMCP) -> None:
    """Register resources with the MCP server.

    Args:
        server: MCP server instance
    """
    # Register resources
    self._add_resource(
        server,
        self.get_your_resource,
        uri="your_resource_name",
        description="Description of your resource"
    )

    # Add more resources as needed
```

### 2. Implement Resource Functions

Create methods in your module class that return resource data:

```python
def get_your_resource(self) -> Dict[str, Any]:
    """Get your resource data.

    Returns:
        Resource data
    """
    # Prepare parameters
    params = prepare_api_parameters({
        "param1": "value1",
        "param2": "value2"
    })

    # Define the operation name
    operation = "YourFalconAPIOperation"

    # Make the API request
    response = self.client.command(operation, parameters=params)

    # Handle the response
    return handle_api_response(
        response,
        operation=operation,
        error_message="Failed to get resource data",
        default_result={}
    )
```

### 3. Resource Auto-Discovery

Resources are automatically registered by the server when the module's `register_resources` method is called. You don't need to modify any registration code in the server.

## Best Practices

### Resource Naming

1. **Use Clear, Descriptive Names**: Resource URIs should be descriptive and follow a consistent naming pattern
2. **Use Namespaces**: Group related resources using namespaces (e.g., `hosts/summary`, `hosts/counts`)
3. **Follow Conventions**: Use lowercase names with underscores for resource URIs

### Resource Data

1. **Return Structured Data**: Resources should return well-structured data (typically JSON-serializable)
2. **Handle Errors Gracefully**: Use error handling utilities to handle API errors
3. **Provide Default Values**: Always provide sensible defaults if data is unavailable
4. **Keep Resources Lightweight**: Resources should be quick to access and not require heavy computation

### Caching

1. **Consider Caching**: For resources that don't change frequently, consider implementing caching
2. **Use Timeouts**: Set appropriate cache timeouts based on how frequently the data changes
3. **Invalidate Cache**: Provide a way to invalidate the cache when needed

### Documentation

1. **Document Resources**: Include detailed docstrings for all resource methods
2. **Describe Data Structure**: Document the structure of the data returned by the resource
3. **Provide Examples**: Include examples of how to use the resource

## Example: Implementing Resources in a Hosts Module

Here's an example of implementing resources in a Hosts module:

```python
"""
Hosts module for Falcon MCP Server

This module provides tools and resources for accessing and managing CrowdStrike Falcon hosts.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_resources
from .base import BaseModule


class HostsModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon hosts."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.search_hosts,
            name="search_hosts"
        )

        # Add more tools as needed

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register resources
        self._add_resource(
            server,
            self.get_host_summary,
            uri="hosts/summary",
            description="Summary of hosts in the environment"
        )

        self._add_resource(
            server,
            self.get_host_counts_by_platform,
            uri="hosts/counts/platform",
            description="Host counts by platform"
        )

        # Add more resources as needed

    def search_hosts(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for hosts in your CrowdStrike environment.

        Args:
            query: FQL query string to filter hosts
            limit: Maximum number of results to return

        Returns:
            List of host details
        """
        # Tool implementation...
        pass

    def get_host_summary(self) -> Dict[str, Any]:
        """Get a summary of hosts in the environment.

        Returns:
            Summary of hosts including total count, online count, and offline count
        """
        # Define the operation name
        operation = "QueryDevices"

        # Make the API request for all hosts
        all_response = self.client.command(operation, parameters={})

        # Make the API request for online hosts
        online_params = prepare_api_parameters({
            "filter": "status:'normal'"
        })
        online_response = self.client.command(operation, parameters=online_params)

        # Handle the responses
        all_hosts = handle_api_response(
            all_response,
            operation=operation,
            error_message="Failed to get host summary",
            default_result=[]
        )

        online_hosts = handle_api_response(
            online_response,
            operation=operation,
            error_message="Failed to get online hosts",
            default_result=[]
        )

        # If either response is an error, return the error
        if self._is_error(all_hosts):
            return all_hosts
        if self._is_error(online_hosts):
            return online_hosts

        # Calculate counts
        total_count = len(all_hosts)
        online_count = len(online_hosts)
        offline_count = total_count - online_count

        # Return the summary
        return {
            "total_count": total_count,
            "online_count": online_count,
            "offline_count": offline_count,
            "last_updated": self.client.command("GetTime")["body"]["utc_time"]
        }

    def get_host_counts_by_platform(self) -> Dict[str, Any]:
        """Get host counts by platform.

        Returns:
            Dictionary with counts for each platform (Windows, Mac, Linux)
        """
        # Define the operation name
        operation = "QueryDevices"

        # Make the API requests for each platform
        windows_params = prepare_api_parameters({
            "filter": "platform_name:'Windows'"
        })
        windows_response = self.client.command(operation, parameters=windows_params)

        mac_params = prepare_api_parameters({
            "filter": "platform_name:'Mac'"
        })
        mac_response = self.client.command(operation, parameters=mac_params)

        linux_params = prepare_api_parameters({
            "filter": "platform_name:'Linux'"
        })
        linux_response = self.client.command(operation, parameters=linux_params)

        # Handle the responses
        windows_hosts = handle_api_response(
            windows_response,
            operation=operation,
            error_message="Failed to get Windows hosts",
            default_result=[]
        )

        mac_hosts = handle_api_response(
            mac_response,
            operation=operation,
            error_message="Failed to get Mac hosts",
            default_result=[]
        )

        linux_hosts = handle_api_response(
            linux_response,
            operation=operation,
            error_message="Failed to get Linux hosts",
            default_result=[]
        )

        # Check for errors
        if self._is_error(windows_hosts) or self._is_error(mac_hosts) or self._is_error(linux_hosts):
            return {"error": "Failed to get host counts by platform"}

        # Return the counts
        return {
            "windows": len(windows_hosts),
            "mac": len(mac_hosts),
            "linux": len(linux_hosts),
            "last_updated": self.client.command("GetTime")["body"]["utc_time"]
        }
```

## Using Resources in the MCP Client

Resources can be accessed by MCP clients using the `access_mcp_resource` function:

```python
# Access a resource
resource_data = access_mcp_resource(
    server_name="falcon-mcp-local",
    uri="falcon:hosts/summary"
)

# Use the resource data
print(f"Total hosts: {resource_data['total_count']}")
print(f"Online hosts: {resource_data['online_count']}")
print(f"Offline hosts: {resource_data['offline_count']}")
```

## Combining Tools and Resources

Tools and resources can work together to provide a comprehensive solution:

1. **Resources for Context**: Use resources to provide context for tool operations
2. **Tools for Actions**: Use tools to perform actions based on resource data
3. **Resources for Caching**: Use resources to cache data that is used by multiple tools

For example, a tool might use a resource to get context before performing an action:

```python
def perform_action(self, param1: str) -> Dict[str, Any]:
    """Perform an action using context from a resource.

    Args:
        param1: Parameter for the action

    Returns:
        Result of the action
    """
    # Get context from a resource
    context = self.get_resource_data()

    # Use the context to perform the action
    result = self._perform_action_with_context(param1, context)

    return result
```

## Testing Resources

Resources should be tested like any other functionality:

1. **Unit Tests**: Test resource functions with mock API responses
2. **Integration Tests**: Test resources with real API responses
3. **Error Handling**: Test error cases and default values

Example test for a resource:

```python
def test_get_host_summary(self):
    """Test the get_host_summary resource."""
    # Setup mock responses
    all_response = {
        "status_code": 200,
        "body": {
            "resources": ["id1", "id2", "id3"]
        }
    }
    online_response = {
        "status_code": 200,
        "body": {
            "resources": ["id1", "id2"]
        }
    }
    time_response = {
        "status_code": 200,
        "body": {
            "utc_time": "2023-01-01T00:00:00Z"
        }
    }

    # Configure mock client
    self.mock_client.command.side_effect = [all_response, online_response, time_response]

    # Call the resource function
    result = self.module.get_host_summary()

    # Verify client commands were called correctly
    self.mock_client.command.assert_any_call("QueryDevices", parameters={})
    self.mock_client.command.assert_any_call("QueryDevices", parameters={"filter": "status:'normal'"})
    self.mock_client.command.assert_any_call("GetTime")

    # Verify result
    expected_result = {
        "total_count": 3,
        "online_count": 2,
        "offline_count": 1,
        "last_updated": "2023-01-01T00:00:00Z"
    }
    self.assertEqual(result, expected_result)
```
