---
title: E2E Testing
description: Running end-to-end tests with a real LLM agent against the Falcon MCP Server.
---

End-to-end tests run a real LLM agent connected to the Falcon MCP Server to validate full tool-call workflows from natural language prompts.

## Configuration

:::note
Requires valid CrowdStrike API credentials and OpenAI API key:
:::

Copy the development example file:

```bash
cp .env.dev.example .env
```

Then configure the E2E testing variables:

```bash frame="none"
# Required
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret

# Optional (defaults to US-1)
FALCON_BASE_URL=https://api.crowdstrike.com

# API key for OpenAI or compatible API
OPENAI_API_KEY=your-api-key

# Optional: Custom base URL (for VPN-only or custom endpoints)
OPENAI_BASE_URL=https://your-custom-llm-endpoint.com/v1

# Optional: Comma-separated list of models to test against
MODELS_TO_TEST=example-model-1,example-model-2
```

## Running E2E Tests

E2E tests require the `--run-e2e` flag:

```bash title="Run all E2E tests"
uv run pytest --run-e2e tests/e2e/
```

```bash title="Run a specific test"
uv run pytest --run-e2e tests/e2e/test_mcp_server.py::TestFalconMCPServerE2E::test_get_top_3_high_severity_detections
```

:::caution
The `-s` flag is **required** to see any meaningful output from E2E tests. Without it, pytest captures all stdout/stderr.
:::

## Verbosity Levels

```bash title="Standard output"
uv run pytest --run-e2e -s tests/e2e/
```

```bash title="Verbose — tool calls and responses"
uv run pytest --run-e2e -v -s tests/e2e/
```

```bash title="Extra verbose — agent thought process, all events"
uv run pytest --run-e2e -vv -s tests/e2e/
```

## Retry Logic

Each test runs multiple times against different models and passes if a threshold percentage succeeds. Defaults in `tests/e2e/utils/base_e2e_test.py`:

```python
DEFAULT_MODELS_TO_TEST = ["gpt-4.1-mini", "gpt-4o-mini"]
DEFAULT_RUNS_PER_TEST = 2
DEFAULT_SUCCESS_THRESHOLD = 0.7  # 70% of runs must pass
```

Override with environment variables:

| Variable | Description |
|----------|-------------|
| `MODELS_TO_TEST` | Comma-separated model list |
| `RUNS_PER_TEST` | Number of runs per test |
| `SUCCESS_THRESHOLD` | Minimum pass rate (0.0–1.0) |

## Troubleshooting

**Not seeing any output?**

```bash
# CORRECT: shows detailed output
uv run pytest --run-e2e -v -s tests/e2e/

# INCORRECT: no output visible
uv run pytest --run-e2e -v tests/e2e/
```

**Using a custom LLM endpoint:**

```bash
OPENAI_BASE_URL=https://your-endpoint.com/v1 uv run pytest --run-e2e -s tests/e2e/
```

**Diagnosing failures:** Use `-vv -s` to see complete prompt/response content and step-by-step agent execution.
