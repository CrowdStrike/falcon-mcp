# Running/Deploying with a prebuilt agent

This repository includes a prebuilt [Google ADK](https://google.github.io/adk-docs/) based agent integrated with the `falcon-mcp` server.

The goal is to provide customers an opinionated and validated set of instructions for running falcon-mcp and deploying it for their teams.

> [!NOTE]
> The `falcon-mcp` package is published to PyPI and installed as a dependency. Cloning this repository provides the agent code and deployment configuration.

## Table of Contents

1. [Setting up and running locally (5 minutes)](#setting-up-and-running-locally-5-minutes)
2. [Deployment - Why Deploy?](#deployment---why-deploy)
3. [Deploying to Agent Runtime and using as Gemini Enterprise App Agent](#deploying-to-agent-runtime-and-using-as-gemini-enterprise-app-agent)
4. [Securing access, Evaluating, Optimizing performance and costs](#securing-access-evaluating-optimizing-performance-and-costs)
5. [FQL Guide Resources](#fql-guide-resources)
6. [Troubleshooting](#troubleshooting)

### Setting up and running locally (5 minutes)

You can run the following commands locally on Linux / macOS or in Google Cloud Shell.
If you plan to deploy the agent, it is recommended to run in Google Cloud Shell.

#### Prerequisites

If running locally (outside Google Cloud Shell), ensure you have the `gcloud` CLI installed and authenticate with Application Default Credentials (ADC), set your project, and enable the `aiplatform` API:

```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable aiplatform.googleapis.com
```

#### Clone and Configure

```bash
git clone https://github.com/CrowdStrike/falcon-mcp.git

cd falcon-mcp

cd examples/adk

cp falcon_agent/env.properties falcon_agent/.env
```

Now update the following environment variables in the `falcon_agent/.env` file. Make sure the `GOOGLE_GENAI_USE_VERTEXAI` is left to `True`. You can update the `GOOGLE_MODEL` and `FALCON_AGENT_PROMPT` variables as needed or leave them as is.

```
# Must update following values

FALCON_CLIENT_ID
FALCON_CLIENT_SECRET
FALCON_BASE_URL

GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
```

#### Install dependencies

```bash
# Create and activate python environment
# You can also use uv

python3 -m venv .venv
. .venv/bin/activate

# Install dependencies
pip install -r falcon_agent/requirements.txt
```

#### Run the agent locally

```bash
adk web

# If running in Cloud Shell - use the following command:
# adk web --allow_origins "*"
```

> [!WARNING]
> **Do not use curly braces** (`{variable}`) in the `FALCON_AGENT_PROMPT` value. Google ADK interprets `{name}` patterns as context variables that must exist in session state, which causes `Context variable not found` errors at runtime. Use square brackets or plain text instead.

<details>

<summary><b>Sample Output - Very First Run</b></summary>

```bash
2026-07-22 17:38:47,091 - INFO - service_factory.py:266 - Using in-memory memory service
2026-07-22 17:38:47,092 - INFO - local_storage.py:89 - Using per-agent session storage

INFO:     Started server process [717057]
INFO:     Waiting for application startup.

+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</details>

<br>

You can access the agent on <http://localhost:8000> 🚀

> If running in the Google Cloud Shell - please use the web preview with port 8000.

You can stop the agent with `ctrl+C`

### Deployment - Why Deploy?

You may want to deploy the agent (with the falcon-mcp server) for the following reasons:

1. Centralize execution on Agent Runtime without distributing credentials to individual local machines (for production workloads, managing secrets via Google Cloud Secret Manager is recommended)
2. You want to share the ready-to-use agent with your team
3. Use it for demos without any client-side setup

You have two distinct paths after deployment:

1. Deploy and use in Agent Platform / Agent Registry playground
2. Deploy in Agent Runtime and use via Gemini Enterprise

### Deploying to Agent Runtime and using as Gemini Enterprise App Agent

This section covers deployment to GCP Agent Platform Agent Runtime. To access the agent and to consolidate all your agents under one umbrella you can also add the deployed agent to a Gemini Enterprise App.

> [!NOTE]
> When using `GOOGLE_CLOUD_LOCATION=global` in `.env` (which directs model inference to the global endpoint for models like `gemini-3.5-flash`), pass the `--region` flag (e.g. `--region us-central1`) during deployment to specify the supported regional location where the Agent Engine container is hosted.

Here are the deployment instructions:

```bash
# While in examples/adk directory
# If using uv; use uv run adk
# Please change the region accordingly

adk deploy agent_engine --region us-central1 --display_name falcon_adk_agent falcon_agent/

```

<details>
<summary>
Updating an already deployed agent
</summary>

If you updated the agent code for some reason (like for optimizing for cost / performance as shown [below](#optimizing-performance-and-costs)) then you can update your agent like this:

```bash
# While in examples/adk directory
# If using uv; use uv run adk
# Provide the numeric Agent Engine ID of the agent being updated (e.g. 12345678910)

adk deploy agent_engine --region us-central1 --display_name falcon_adk_agent --agent_engine_id <AGENT_ENGINE_ID> falcon_agent/
```

> In ADK 2.5.0 with Vertex AI (Non API Key mode) configuration, `--agent_engine_id` takes the bare numeric ID when project and location are set.

</details>

#### Accessing the Agent

Go to:

Agent Platform -> Agent Registry -> Your Agent -> Click -> Playground -> interact with the agent

#### Accessing the Agent as a Gemini Enterprise Agent Application

Here are the steps:

1. Go to Gemini Enterprise menu in GCP Console
2. Create an App (Global)
3. Click the application -> go to Agents -> Add Agent -> Choose Custom agent via Agent Runtime
4. Skip Authorizations screen
5. On the Configuration screen add Agent name, Description and Agent Engine path (format - `projects/{project}/locations/{location}/reasoningEngines/{reasoningEngine}`), Click create
6. Provide Access -> Select Created Agent -> User permissions tab -> Add User -> Provide "Agent User" role to a user / All Users as needed
7. Access the Gemini Enterprise app and select the agent or invoke it with `@agent_name`
8. If you need to delete the Agent from Gemini Enterprise App - you can select `delete` from the Actions menu for the particular agent.


### Securing access, Evaluating, Optimizing performance and costs

#### Securing access

1. For local runs, make sure that you are not using a shared machine.
2. For agent accessed from Gemini Enterprise - the access is granted using step 6 from [Accessing the Agent as a Gemini Enterprise Agent Application](#accessing-the-agent-as-a-gemini-enterprise-agent-application).

#### Evaluating

It is advised to evaluate the agent for the trajectory it takes and the output it produces - you can use [ADK documentation](https://google.github.io/adk-docs/evaluate/) to evaluate this agent. You can also test with different models.

> [!NOTE]
> Running evaluations with `adk eval` requires the ADK evaluation dependencies: `pip install "google-adk[eval]==2.5.0"`.

#### Optimizing performance and costs

Various native performance improvements are included in the codebase:

- **Event Compaction & Context Caching**: The values `EVENT_COMPACTION=Y` and `CONTEXT_CACHING=Y` in `.env` enable ADK [event compaction](https://adk.dev/context/compaction/) and [context caching](https://adk.dev/context/caching/). They are on by default; you can change them in `.env` file and also change finer configuration details in `agent.py` file.
  - *Note on Warnings*: In ADK 2.5.0, these features are marked `@experimental` and emit a `UserWarning` during startup; this is expected behavior.
  - *Context Caching Trigger*: Context caching automatically kicks in for conversations exceeding 4096 tokens (`min_tokens=4096`) and will not apply to turn 1 of short interactions.
- **Gemini Model Selection**: By default, `gemini-3.5-flash` is configured in `env.properties`. Newer models like `gemini-3.5-flash` or preview models are hosted on the global endpoint, requiring `GOOGLE_CLOUD_LOCATION=global` in your `.env`. When deploying to Agent Engine, explicitly pass `--region <REGION>` (such as `us-central1`) on the command line so the agent container is deployed in a regional runtime while querying the global model endpoint. Refer to [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing) for model capabilities and cost considerations.

### FQL Guide Resources

The agent is configured with `use_mcp_resources=True`, which enables ADK's MCP resource support. The falcon-mcp server exposes FQL (Falcon Query Language) guide resources (e.g., `falcon://detections/search/fql-guide`) that the agent can fetch on demand via the auto-discovered `load_mcp_resource` tool. This gives the LLM access to field names, filter syntax, and query examples — resulting in more accurate Falcon queries without needing to embed all FQL documentation in the system prompt.

### Troubleshooting

#### `Context variable not found: 'user_name'`

Google ADK interprets `{variable_name}` patterns in agent instruction strings as template variables that must be resolved from session state. If your `FALCON_AGENT_PROMPT` contains curly braces, you will see this error when sending messages.

**Fix:** Remove all curly braces from your prompt. The default prompt in `env.properties` is safe to use as-is.

#### `Consistent 429 errors / consistent model errors`

**Fix:** Check your Gemini Quota, Try changing the model and switching off `EVENT_COMPACTION` and `CONTEXT_CACHING`
