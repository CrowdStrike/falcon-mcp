# End-to-End Testing Guide

This document provides guidance on running and understanding the end-to-end tests for the Falcon MCP Server.

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

By default, tests run with minimal output:

```bash
pytest --run-e2e -s tests/e2e/
```

### Verbose Output

To see more detailed output, use both `-v` and `-s` flags:

```bash
pytest --run-e2e -v -s tests/e2e/
```

### Extra Verbose Output

For even more detailed output, including all events:

```bash
pytest --run-e2e -vv -s tests/e2e/
```

> [!NOTE]
> The `-s` flag disables pytest's output capture, allowing all print statements to be displayed.
> Without this flag, you won't see any of the detailed output from the tests.

## Test Retry Logic

The E2E tests use a retry mechanism to handle the non-deterministic nature of LLM responses. Each test is run multiple times against different models, and the test passes if a certain percentage of runs succeed.

The retry configuration can be found at the top of `tests/e2e/test_mcp_server.py`:

```python
# Models to test against
MODELS_TO_TEST = ["gpt-4o", "gpt-4.1-mini", "gpt-4o-mini"]
# Number of times to run each test
RUNS_PER_TEST = 5
# Success threshold for passing a test
SUCCESS_THRESHOLD = 0.7
```

This means each test will run 5 times for each model and the test will pass if at least 70% of the runs succeed (i.e., 4 out of 5 runs).

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

If a test is failing, try running it with full debug output (`-v -s` flags) to see what's happening. Look for:

1. Connection issues with the MCP server
2. Unexpected LLM responses
3. Assertion failures in the test logic

The verbose output will show you the exact prompts, responses, and tool calls, which can help diagnose the issue.
