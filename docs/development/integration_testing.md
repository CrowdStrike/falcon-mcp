# Integration Testing Guide

This document provides guidance on running and understanding the integration tests for the Falcon MCP Server.

## Overview

Integration tests make real API calls to the CrowdStrike Falcon platform to validate that modules work correctly against the live API. These tests catch issues that mocked unit tests cannot detect:

- **Incorrect FalconPy operation names** - Typos pass in mocks but fail against real API
- **HTTP method mismatches** - POST body vs GET query parameters
- **Two-step search patterns** - Ensuring full details are returned, not just IDs
- **API response schema changes** - Real API may return different structures than mocked data
- **Authentication and scope issues** - Only detectable with real credentials

## Configuration

Integration tests require valid CrowdStrike API credentials. Configure these using environment variables or a `.env` file:

```bash
# Required: CrowdStrike API credentials
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret

# Optional: CrowdStrike API region URL (defaults to US-1)
FALCON_BASE_URL=https://api.crowdstrike.com
```

For development, you can copy the example file:

```bash
cp .env.dev.example .env
```

### API Scopes

Your API client must have the appropriate scopes for the modules you're testing. See the main [README.md](../../README.md#api-scopes) for the complete scope mapping.

## Running Integration Tests

Integration tests are marked with the `@pytest.mark.integration` decorator and require the `--run-integration` flag:

```bash
# Run all integration tests
pytest --run-integration tests/integration/

# Run integration tests for a specific module
pytest --run-integration tests/integration/test_detections.py

# Run a specific test
pytest --run-integration tests/integration/test_scheduled_reports.py::TestScheduledReportsIntegration::test_search_scheduled_reports_returns_details
```

> [!IMPORTANT]
> When running integration tests with verbose output, the `-s` flag is **required** to see detailed output including print statements and warnings.

## Verbose Output

Integration tests support different verbosity levels:

### Standard Output

```bash
pytest --run-integration -s tests/integration/
```

### Verbose Output

For more detailed output including test names and status:

```bash
pytest --run-integration -v -s tests/integration/
```

### Extra Verbose Output

For maximum detail including all assertions and data:

```bash
pytest --run-integration -vv -s tests/integration/
```

## Test Structure

### BaseIntegrationTest

All integration tests inherit from `BaseIntegrationTest` which provides common assertion helpers:

```python
from tests.integration.utils.base_integration_test import BaseIntegrationTest

@pytest.mark.integration
class TestMyModuleIntegration(BaseIntegrationTest):
    """Integration tests for MyModule."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up module with real client."""
        self.module = MyModule(falcon_client)

    def test_search_returns_details(self):
        """Test that search returns full entity details."""
        result = self.call_method(self.module.search_entities, limit=5)

        self.assert_no_error(result)
        self.assert_valid_list_response(result)

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name", "status"],
            )
```

### Available Assertions

| Method | Description |
| -------- | ------------- |
| `assert_no_error(result)` | Verify result is not an API error |
| `assert_valid_list_response(result, min_length)` | Verify result is a list with minimum length |
| `assert_search_returns_details(result, expected_fields)` | Verify search returns full entity objects with expected fields |
| `assert_result_has_id(result, id_field)` | Verify each result has an ID field |
| `get_first_id(result, id_field)` | Extract first ID from results |
| `skip_with_warning(reason)` | Skip test with visible warning in CI output |

### Calling Module Methods

Use `call_method()` to properly resolve Pydantic `Field()` defaults:

```python
# Correct: Field defaults are resolved
result = self.call_method(self.module.search_entities, filter="status:'active'")

# Incorrect: Field defaults may not be resolved when calling directly
result = self.module.search_entities(filter="status:'active'")  # May fail
```

## Handling Missing Test Data

Integration tests should gracefully handle environments where test data may not exist:

```python
def test_download_execution(self):
    """Test downloading a report execution."""
    # Search for completed executions
    search_result = self.call_method(
        self.module.search_report_executions,
        filter="status:'DONE'",
        limit=5,
    )

    # Skip if no test data available
    if not search_result or len(search_result) == 0:
        self.skip_with_warning(
            "No completed executions available",
            context="test_download_execution",
        )

    # Continue with test...
```

Using `skip_with_warning()` ensures skipped tests are visible in CI output rather than silently passing.

## Best Practices

### 1. Test What Mocks Cannot

Focus integration tests on validating:

- FalconPy operation names are correct
- HTTP methods and parameter positions match the API
- Two-step search patterns return full details
- Response formats match expectations

### 2. Use Small Limits

Keep `limit` parameters small to minimize API calls and test data:

```python
result = self.call_method(self.module.search_entities, limit=3)
```

### 3. Be Idempotent

Avoid tests that modify data unless absolutely necessary. Prefer read-only operations:

```python
# Good: Read-only search
def test_search_detections(self):
    result = self.call_method(self.module.search_detections, limit=5)

# Careful: Creates data (document cleanup strategy)
def test_launch_report(self):
    # Only test if we have existing reports to launch
    ...
```

### 4. Document Skip Conditions

When tests may be skipped, document why:

```python
def test_pdf_format_returns_error(self):
    """Test PDF format detection.

    Note: This test may be skipped if no PDF format reports exist
    in the test environment.
    """
```

## Troubleshooting

### Tests Not Running

If integration tests are being skipped, verify:

1. You're using the `--run-integration` flag
2. Your credentials are set in environment or `.env` file
3. The API client can authenticate successfully

### Authentication Failures

If tests fail with authentication errors:

1. Verify `FALCON_CLIENT_ID` and `FALCON_CLIENT_SECRET` are set
2. Check `FALCON_BASE_URL` matches your region
3. Verify API client has required scopes

### Empty Results

If tests pass but with empty results:

1. Your Falcon tenant may not have the required data
2. Check filter parameters for typos
3. Verify API scopes allow reading the resource type

### Permission Errors

If tests fail with 403 errors:

1. Check your API client has the required scopes
2. Some endpoints require additional permissions (e.g., write access)
3. See [API Scopes](../../README.md#api-scopes) for requirements

## Adding New Integration Tests

When adding a new module, create corresponding integration tests:

1. Create `tests/integration/test_<module>.py`
2. Inherit from `BaseIntegrationTest`
3. Add `@pytest.mark.integration` decorator
4. Test search operations return full details
5. Test operation names and HTTP methods are correct

Example template:

```python
"""Integration tests for the MyModule."""

import pytest

from falcon_mcp.modules.my_module import MyModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestMyModuleIntegration(BaseIntegrationTest):
    """Integration tests for MyModule with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up module with real client."""
        self.module = MyModule(falcon_client)

    def test_search_returns_details(self):
        """Test that search returns full entity details."""
        result = self.call_method(self.module.search_entities, limit=5)

        self.assert_no_error(result, context="search_entities")
        self.assert_valid_list_response(result, min_length=0)

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_entities",
            )

    def test_operation_names_are_correct(self):
        """Validate FalconPy operation names."""
        # If operation names are wrong, this will fail
        result = self.call_method(self.module.search_entities, limit=1)
        self.assert_no_error(result, context="operation name validation")
```
