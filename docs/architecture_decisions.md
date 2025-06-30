# Architecture Decisions

This document outlines key architectural decisions made during the development of the Falcon MCP Server.

## Resource Implementation

### Context

The initial implementation of the Falcon MCP Server only supported tools, which are functions that can be called with arguments. However, the Model Context Protocol (MCP) also supports resources, which are data sources that can be accessed directly. Resources provide a way to expose data that doesn't require computation or that should be available as context for tools.

### Decision

We implemented a resource system that:

1. Allows modules to register resources with the server
2. Provides a consistent naming scheme for resources (prefixed with `falcon:`)
3. Integrates with the existing module architecture
4. Makes resources discoverable and accessible to MCP clients

### Implementation

- Added an `add_resource` method to the `FalconMCPServer` class
- Added a `_register_resources` method to the server to register resources from modules
- Added a `register_resources` method to the `BaseModule` class (optional for modules to implement)
- Added an `_add_resource` helper method to the `BaseModule` class
- Updated the server initialization to call `_register_resources()`
- Added tracking of registered resources in modules
- Created documentation for resource development in `docs/resource_development.md`

This implementation allows modules to register resources in a similar way to how they register tools, maintaining consistency in the codebase while extending its capabilities.

## Module Registry System

### Context

The initial implementation had modules directly registered in the `server.py` file by importing module classes and
adding them to an `AVAILABLE_MODULES` dictionary. This created a cyclic import issue:

1. `server.py` imported module classes from `modules/core.py`, `modules/detections.py`, etc.
2. These module files imported from `server.py` to access the `AVAILABLE_MODULES` dictionary.

### Decision

We implemented a dedicated module registry system in `src/modules/registry.py` that:

1. Provides a central location for module registration
2. Breaks the cyclic import dependency
3. Makes the codebase more maintainable and extensible

### Implementation

The registry system consists of:

- A dictionary to store available modules: `AVAILABLE_MODULES`
- A `discover_modules` function that automatically discovers and registers modules
- A `get_module_names` function to retrieve registered module names

Initially, modules were registered by calling `register_module("module_name", ModuleClass)`, but this approach was later
replaced by the auto-discovery pattern (see "Module Auto-Discovery" section below).

## Module Auto-Discovery

### Context

The initial module registry implementation required explicit registration of modules in the `modules/__init__.py` file.
This approach had several drawbacks:

1. It required function calls in the `__init__.py` file, which is not a common Python pattern
2. Adding new modules required remembering to register them explicitly
3. The server needed to import BaseModule to use `__subclasses__()` for discovery
4. The explicit import of `src.modules` in server.py created a non-standard import pattern

### Decision

We implemented an auto-discovery pattern that:

1. Uses standard library tools (importlib, pkgutil) to scan for modules
2. Automatically registers modules based on naming conventions
3. Eliminates the need for explicit registration calls
4. Follows more standard Python practices

### Implementation

- Added a `discover_modules()` function in `registry.py` that scans the modules directory
- Uses importlib to dynamically import modules and inspect their contents
- Automatically registers classes that end with "Module" and aren't BaseModule
- Simplified the server initialization to just call `registry.discover_modules()`
- Kept the modules/__init__.py file minimal with just the necessary imports
- Removed the dependency on `BaseModule.__subclasses__()`

## Error Handling Refactoring

### Context

The initial implementation had error handling utilities split between `utils.py` and `errors.py`, creating another
cyclic import issue:

1. `utils.py` defined `format_error_response` and imported from `errors.py`
2. `errors.py` imported `format_error_response` from `utils.py`

Additionally, error handling in some modules (like `detections.py`) was inconsistent, using manual status code checks
instead of the common error handling utilities.

### Decision

We consolidated error handling utilities in `errors.py` to:

1. Break the cyclic import dependency
2. Group related functionality in a single module
3. Improve code organization and maintainability
4. Ensure consistent error handling across all modules

### Implementation

- Moved `format_error_response` from `utils.py` to `errors.py`
- Renamed it to `_format_error_response` to indicate it's an internal function
- Updated all references to use the new function name and location
- Refactored the `detections.py` module to use `handle_api_response` instead of manual error handling
- Ensured consistent error response formats across all modules

## Code Quality Improvements

### Context

The codebase had some minor code quality issues that could be improved.

### Decision

We implemented a `.pylintrc` configuration file to:

1. Set a line length of 120 characters
2. Disable warnings for "too few public methods" where appropriate
3. Configure other linting rules to match the project's coding style

### Implementation

- Created a `.pylintrc` file with appropriate configuration
- Fixed issues identified by pylint
- Achieved a pylint score of 10.00/10

## Testing Strategy

### Context

Tests needed to be updated to reflect the architectural changes. Additionally, we wanted to standardize the approach to testing modules to ensure consistency and reduce code duplication.

### Decision

We updated the tests to:

1. Use the new module registry system
2. Properly mock dependencies
3. Ensure all functionality is correctly tested
4. Create a base test class for module tests to standardize testing patterns

### Implementation

- Updated test mocks to patch the correct locations after refactoring
- Fixed assertions to match the new function signatures and behavior
- Created a `TestModules` base class in `tests/modules/utils/test_modules.py` that:
  - Provides a `setup_module()` method to handle the common setup of mocking the client and server
  - Provides an `assert_tools_registered()` helper method to verify tool registration
  - Simplifies test code and ensures consistency across all module tests
- Updated all module test classes to inherit from `TestModules` instead of directly from `unittest.TestCase`
- Ensured all tests pass with the new architecture

## Authentication Headers Access

### Context

The `FalconClient` class needed a way to expose authentication headers for potential
advanced integration scenarios and custom HTTP requests.

### Decision

We added a `get_headers()` method to the `FalconClient` class that:

1. Exposes authentication headers from the underlying `APIHarnessV2` client
2. Enables integration with custom HTTP clients and requests
3. Provides flexibility for future transport implementations

### Implementation

The implementation is a simple pass-through to the underlying client's `auth_headers` property:

```python
def get_headers(self) -> Dict[str, str]:
    """Get authentication headers for API requests."""
    return self.client.auth_headers
```

This method provides access to authentication headers when needed for custom integrations
while maintaining the encapsulation of the authentication process.
