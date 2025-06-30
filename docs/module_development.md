# Falcon MCP Server Module Development Guide

This guide provides instructions for implementing new modules for the Falcon MCP server.

## Module Structure

Each module should:

1. Inherit from the `BaseModule` class
2. Implement the `register_tools` method
3. Optionally implement the `register_resources` method
4. Define tool methods that interact with the Falcon API
5. Optionally define resource methods that provide data
6. Use common utilities for configuration, logging, error handling, and API interactions

## Step-by-Step Implementation Guide

### 1. Create a New Module File

Create a new file in the `src/modules` directory:

```python
"""
[Module Name] module for Falcon MCP Server

This module provides tools for [brief description].
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_first_resource
from .base import BaseModule


class YourModule(BaseModule):
    """Module for [description]."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.your_tool_method,
            name="your_tool_name"
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
            self.your_resource_method,
            uri="your_resource_name",
            description="Description of your resource"
        )

        # Add more resources as needed

    def your_tool_method(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
        """Description of what your tool does.

        Args:
            param1: Description of param1
            param2: Description of param2

        Returns:
            Tool result description
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "param1": param1,
            "param2": param2
        })

        # Define the operation name (used for error handling)
        operation = "YourFalconAPIOperation"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )

    def your_resource_method(self) -> Dict[str, Any]:
        """Description of what your resource provides.

        Returns:
            Resource data description
        """
        # Define the operation name (used for error handling)
        operation = "YourFalconAPIOperation"

        # Make the API request
        response = self.client.command(operation, parameters={})

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to get resource data",
            default_result={}
        )
```

### 2. Update API Scope Requirements

Add your API operations to the `API_SCOPE_REQUIREMENTS` dictionary in `src/common/errors.py`:

```python
API_SCOPE_REQUIREMENTS = {
    # Existing operations...
    "YourFalconAPIOperation": ["required:scope"],
    # Add more operations as needed
}
```

### 3. Module Auto-Discovery

Modules are automatically registered by the server once they're discovered. You don't need to call any registration functions, but you do need to:

1. Create your module class in the `src/modules` directory (e.g., `your_module.py`)
2. Make sure it inherits from `BaseModule`
3. Import it in `src/modules/__init__.py` to make it available for discovery:

```python
# In src/modules/__init__.py
from .your_module import YourModule
```

The server will automatically discover and register your module during initialization. The module name will be derived
from the class name (e.g., `YourModule` becomes `your`).

During server initialization, the registry system will:

1. Scan the modules directory
2. Import the modules listed in `__init__.py`
3. Find classes that end with "Module" (excluding BaseModule)
4. Register them in the `AVAILABLE_MODULES` dictionary
5. Make them available to the server

This approach simplifies module registration while maintaining a clean architecture that avoids cyclic imports.

### 4. Add Tests

Create a test file in the `tests/modules` directory that inherits from the `TestModules` base class:

```python
"""
Tests for the YourModule module.
"""
from src.modules.your_module import YourModule
from tests.modules.utils.test_modules import TestModules


class TestYourModule(TestModules):
    """Test cases for the YourModule module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(YourModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_your_tool_name",
            # Add other tools here
        ]
        self.assert_tools_registered(expected_tools)

    def test_your_tool_method(self):
        """Test your tool method."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [{"id": "test", "name": "Test Resource"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call your tool method
        result = self.module.your_tool_method("test_param", 123)

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "YourFalconAPIOperation",
            parameters={"param1": "test_param", "param2": 123}
        )

        # Verify result
        expected_result = [{"id": "test", "name": "Test Resource"}]
        self.assertEqual(result, expected_result)

    def test_your_tool_method_error(self):
        """Test your tool method with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Access denied"}]
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call your tool method
        result = self.module.your_tool_method("test_param")

        # Verify result contains error
        self.assertIn("error", result)
        self.assertIn("details", result)
```

The `TestModules` base class provides:

1. A `setup_module()` method that handles the common setup of mocking the client and server
2. An `assert_tools_registered()` helper method to verify tool registration
3. An `assert_resources_registered()` helper method to verify resource registration

This approach simplifies test code and ensures consistency across all module tests.

## Best Practices

### Error Handling

1. **Use Common Error Utilities**: Always use `handle_api_response` for API responses instead of manual status code checks
2. **Provide Operation Names**: Include the operation name for better error messages and permission handling
3. **Custom Error Messages**: Use descriptive error messages for each operation
4. **Consistent Error Format**: Ensure error responses follow the standard format with `error` and optional `details` fields

Example of proper error handling:

```python
# Make the API request
response = self.client.command(operation, parameters=params)

# Use handle_api_response to process the response
result = handle_api_response(
    response,
    operation=operation,
    error_message="Failed to perform operation",
    default_result=[]
)

# Check if the result is an error response
if isinstance(result, dict) and "error" in result:
    # Handle error case
    return result  # or wrap it in a list if returning to a tool expecting a list
```

### Parameter Handling

1. **Use prepare_api_parameters**: Filter out None values and format parameters
2. **Type Annotations**: Always include type annotations for parameters and return values
3. **Default Values**: Provide sensible defaults for optional parameters

### Response Processing

1. **Use extract_resources**: Extract resources from API responses
2. **Handle Empty Results**: Provide appropriate defaults for empty results
3. **Return Structured Data**: Return well-structured data that follows consistent patterns

### Documentation

1. **Docstrings**: Include detailed docstrings for all classes and methods. Tool descriptions are derived from method docstrings, so make sure they are comprehensive and well-written.
2. **Parameter Descriptions**: Document all parameters and return values
3. **Examples**: Include examples in docstrings where helpful

### Testing

1. **Test All Tools**: Write tests for all tools in your module
2. **Test Error Cases**: Include tests for error scenarios
3. **Mock API Responses**: Use mock responses for testing

## Common Utilities Reference

### Configuration (`src/common/config.py`)

- `FalconConfig`: Configuration class for the Falcon MCP server
- `load_config`: Load configuration from environment variables and arguments

### Logging (`src/common/logging.py`)

- `configure_logging`: Configure logging for the Falcon MCP server
- `get_logger`: Get a logger with the specified name

### Error Handling (`src/common/errors.py`)

- `is_success_response`: Check if an API response indicates success
- `get_required_scopes`: Get the required API scopes for a specific operation
- `_format_error_response`: Format an error as a standardized response
- `handle_api_response`: Handle an API response, returning either the result or an error

### Utilities (`src/common/utils.py`)

- `filter_none_values`: Remove None values from a dictionary
- `prepare_api_parameters`: Prepare parameters for Falcon API requests
- `extract_resources`: Extract resources from an API response
- `extract_first_resource`: Extract the first resource from an API response

## Example: Implementing a Hosts Module

Here's an example of implementing a Hosts module that provides tools and resources for accessing and managing hosts in the Falcon platform:

```python
"""
Hosts module for Falcon MCP Server

This module provides tools and resources for accessing and managing CrowdStrike Falcon hosts.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_resources, extract_first_resource
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

        self._add_tool(
            server,
            self.get_host_details,
            name="get_host_details"
        )

        self._add_tool(
            server,
            self.get_host_count,
            name="get_host_count"
        )

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

    def search_hosts(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for hosts in your CrowdStrike environment.

        Args:
            query: FQL query string to filter hosts
            limit: Maximum number of results to return

        Returns:
            List of host details
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": query,
            "limit": limit
        })

        # Define the operation name
        operation = "QueryDevices"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        host_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search hosts",
            default_result=[]
        )

        # If we have host IDs, get the details for each one
        if host_ids:
            details_operation = "GetDeviceDetails"
            details_response = self.client.command(
                details_operation,
                body={"ids": host_ids}
            )

            return handle_api_response(
                details_response,
                operation=details_operation,
                error_message="Failed to get host details",
                default_result=[]
            )

        return []

    def get_host_details(self, host_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific host.

        Args:
            host_id: The ID of the host to retrieve

        Returns:
            Host details
        """
        # Define the operation name
        operation = "GetDeviceDetails"

        # Make the API request
        response = self.client.command(
            operation,
            body={"ids": [host_id]}
        )

        # Extract the first resource
        return extract_first_resource(
            response,
            operation=operation,
            not_found_error="Host not found"
        )

    def get_host_count(self, query: Optional[str] = None) -> Dict[str, int]:
        """Get the count of hosts matching a query.

        Args:
            query: FQL query string to filter hosts

        Returns:
            Dictionary with host count
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": query
        })

        # Define the operation name
        operation = "QueryDevices"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get host IDs
        host_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to get host count",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it with a count of 0
        if isinstance(host_ids, dict) and "error" in host_ids:
            return {"count": 0, **host_ids}

        return {"count": len(host_ids)}

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

Don't forget to update the `API_SCOPE_REQUIREMENTS` dictionary in `src/common/errors.py`:

```python
API_SCOPE_REQUIREMENTS = {
    # Existing operations...
    "QueryDevices": ["hosts:read"],
    "GetDeviceDetails": ["hosts:read"],
    # Add more operations as needed
}
```

And import the module in the `src/modules/__init__.py` file:

```python
# In src/modules/__init__.py
from .hosts import HostsModule
```

## Resources vs. Tools

When deciding whether to implement functionality as a tool or a resource, consider the following:

### Use Tools When:

1. The functionality requires user input (parameters)
2. The operation performs an action or computation
3. The result may change based on input parameters
4. The operation might modify data or state

### Use Resources When:

1. The data is static or changes infrequently
2. The data provides context for other operations
3. The data doesn't require user input
4. Multiple tools might need the same data
5. The data is useful as reference information

For more detailed information about implementing resources, see the [Resource Development Guide](resource_development.md).
