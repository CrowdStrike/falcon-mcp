# End-to-End Testing Guide

This document provides guidance on running and understanding the end-to-end tests for the Falcon MCP Server.

## Configuration

The E2E tests can be configured using environment variables or a `.env` file. For development and testing, copy the development example file:

```bash
cp .env.dev.example .env
```

Then configure the E2E testing variables:

### LLM Configuration

```bash
# API key for OpenAI or compatible API
OPENAI_API_KEY=your-api-key

# Optional: Custom base URL for LLM API (for VPN-only or custom endpoints)
OPENAI_BASE_URL=https://your-custom-llm-endpoint.com/v1

# Optional: Comma-separated list of models to test against
MODELS_TO_TEST=example-model-1,example-model-2
```

If not specified, the tests will use the default models defined in `tests/e2e/utils/base_e2e_test.py`.

## Running E2E Tests

End-to-end tests are marked with the `@pytest.mark.e2e` decorator and require the `--run-e2e` flag to run:

```bash
# Run all E2E tests
pytest --run-e2e tests/e2e/

# Run a specific E2E test
pytest --run-e2e tests/e2e/test_mcp_server.py::TestFalconMCPServerE2E::test_get_top_3_high_severity_detections
```

> [!IMPORTANT]
> When running E2E tests with verbose output, the `-s` flag is **required** to see any meaningful output.
> This is because pytest normally captures stdout/stderr, and our tests output information via print statements.
> Without the `-s` flag, you won't see any of the detailed output, even with `-v` or `-vv` flags.

## Verbose Output

The E2E tests support different levels of verbosity, but **all require the `-s` flag** to display detailed output:

### Standard Output (No Verbosity)

By default, tests run with minimal output and the agent runs silently:

```bash
pytest --run-e2e -s tests/e2e/
```

### Verbose Output

To see more detailed output, including basic agent debug information, use both `-v` and `-s` flags:

```bash
pytest --run-e2e -v -s tests/e2e/
```

With this level of verbosity, you'll see:

- Test execution progress
- Basic agent operations
- Tool calls and responses
- Test success/failure information

### Extra Verbose Output

For even more detailed output, including all agent events and detailed debugging information:

```bash
pytest --run-e2e -vv -s tests/e2e/
```

This level shows everything from the verbose level plus:

- Detailed agent thought processes
- Step-by-step execution flow
- Complete prompt and response content
- Detailed tool execution information

> [!NOTE]
> The `-s` flag disables pytest's output capture, allowing all print statements to be displayed.
> Without this flag, you won't see any of the detailed output from the tests.
>
> The verbosity level (`-v`, `-vv`) controls both test output verbosity AND agent debug output.
> Higher verbosity levels are extremely useful when diagnosing test failures or unexpected agent behavior.

## Test Retry Logic

The E2E tests use a retry mechanism to handle the non-deterministic nature of LLM responses. Each test is run multiple times against different models, and the test passes if a certain percentage of runs succeed.

The retry configuration can be found at the top of `tests/e2e/utils/base_e2e_test.py`:

```python
# Default models to test against
DEFAULT_MODLES_TO_TEST = ["gpt-4.1-mini", "gpt-4o-mini"]
# Default number of times to run each test
DEFAULT_RUNS_PER_TEST = 2
# Default success threshold for passing a test
DEFAULT_SUCCESS_THRESHOLD = 0.7
```

This means each test will run 2 times for each model and the test will pass if at least 70% of the runs succeed.

Each of these can be overridden by using the appropriate environment variable:

- MODELS_TO_TEST
- RUNS_PER_TEST
- SUCCESS_THRESHOLD

For example:

```bash
# Test with Claude models
MODELS_TO_TEST=example-model-1,example-model-2 pytest --run-e2e -s tests/e2e/
```

## Troubleshooting

### Not Seeing Any Output?

If you're running tests with `-v` but not seeing any detailed output, make sure you've included the `-s` flag:

```bash
# CORRECT: Will show detailed output
pytest --run-e2e -v -s tests/e2e/

# INCORRECT: Will not show detailed output
pytest --run-e2e -v tests/e2e/
```

### Diagnosing Test Failures

If a test is failing, try running it with full debug output (`-v -s` or `-vv -s` flags) to see what's happening. Look for:

1. Connection issues with the MCP server
2. Unexpected LLM responses
3. Assertion failures in the test logic
4. Agent debugging information (enabled with verbosity)

The verbose output will show you the exact prompts, responses, and tool calls, which can help diagnose the issue. With higher verbosity levels, you'll also see detailed agent debugging information that can help identify why the agent isn't behaving as expected.

### Using Custom LLM Endpoints

If you need to use a custom LLM endpoint (e.g., for VPN-only accessible models), set the `OPENAI_BASE_URL` environment variable:

```bash
# Use a custom LLM endpoint
OPENAI_BASE_URL=https://your-custom-llm-endpoint.com/v1 pytest --run-e2e -s tests/e2e/
```

This is particularly useful when testing with models that are only accessible through specific endpoints or when using a proxy server.
