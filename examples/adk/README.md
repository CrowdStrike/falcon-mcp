# Running/Deploying with a prebuilt agent

This repository includes a prebuilt [Google ADK](https://google.github.io/adk-docs/) based agent integrated with the `falcon-mcp` server.

The goal is to provide customers an opinionated and validated set of instructions for running falcon-mcp and deploying it for their teams.

## Table of Contents

1. [Setting up and running locally (5 minutes)](#setting-up-and-running-locally-5-minutes)
2. [Deployment - Why Deploy?](#deployment---why-deploy)
3. [Deploying to Agent Runtime and using as Gemini Enterprise App Agent](#deploying-to-agent-runtime-and-using-as-gemini-enterprise-app-agent)
4. [Securing access, Evaluating, Optimizing performance and costs](#securing-access-evaluating-optimizing-performance-and-costs)
5. [FQL Guide Resources](#fql-guide-resources)
6. [Troubleshooting](#troubleshooting)

### Setting up and running locally (5 minutes)

You can run the following commands locally on Linux / Mac or in Google Cloud Shell.
If you plan to deploy the agent, it is recommended to run in Google Cloud Shell.

```bash

git clone https://github.com/CrowdStrike/falcon-mcp.git

cd falcon-mcp

cd examples/adk

cp falcon_agent/env.properties falcon_agent/.env

```

Now update the following Environment variables in the `falcon_agent/.env` file. Make sure the `GOOGLE_GENAI_USE_VERTEXAI` is left to `True`. You can update the `GOOGLE_MODEL` and `FALCON_AGENT_PROMPT` variables as needed or leave them as is.


```
# Must update following values

FALCON_CLIENT_ID
FALCON_CLIENT_SECRET
FALCON_BASE_URL

GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION

```

Install dependencies - 

```bash

# Create and activate python environment
# You can also use uv

python3 -m venv .venv
. .venv/bin/activate

# install depenencies
pip install -r falcon_agent/requirements.txt

```

Run the agent locally


```bash

adk web

# if running in cloud shell - use the following command.
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

You may want to deploy the agent (with the `falcon-mcp` server) for following reasons

1. You do not want to hand out credentials to everyone to run MCP server locally
2. You want to share the ready to use agent with your team
3. Use it for demos without any setup

You have two distinct paths to deployment:

1. Deploy and use in Agent Runtime playground
2. Deploy in Agent Runtime and use via Gemini Enterprise.

<br>

> [!NOTE]
> For all the following sections - If you are not running in Google Cloud Shell, make sure you have `gcloud` CLI [installed](https://cloud.google.com/sdk/docs/install) and you have authenticated with your username (preferably as owner of the project) on your local computer.



### Deploying to Agent Runtime and using as Gemini Enterprise App Agent

This section covers deployment to GCP Agent Platform Agent Runtime. To acces the agent and to consolidate all your agents under one umbrella you can also add the deployed agent to a Gemini Enterprise App.


Here are the deployment instructions


```bash
# while in exaples/adk directory
# if using uv; use uv run adk

adk deploy agent_engine --display_name falcon_adk_agent falcon_agent/

```


<details>
<summary>
Updating an already deployed agent
</summary>

If you updated the agent code for some reason (like for optimizing for cost / performance as shown [below](#optimizing-performance-and-costs)) then you can update your agent like this


```bash

# while in exaples/adk directory
# if using uv; use uv run adk
# you should have agent engine Id of the agent getting updated e.g. projects/12345678910/locations/europe-west2/reasoningEngines/12345678910

adk deploy agent_engine --display_name falcon_adk_agent --agent_engine_id <use full resourse name> falcon_agent/

```


</details>


#### Accessing the Agent

Go to 

Agent Platform - Agent Registry - Your Agent - Click - Playground - interact with the agent


#### Accessing the Agent as a Gemini Enterprise Agent Application

Here are the steps

1. Goto Gemini enterprise menu in GCP Console
1. Create an App (Global)
1. Click the application - goto Agents - Add Agent - Choose Custom agent via Agent Runtime
1. Skip Authorizations screen
1. On the Configuration screen add Agent name, Description and Agent Engine path (format - `projects/{project}/locations/{location}/reasoningEngines/{reasoningEngine}`), Click create
1. Provide Access - Select Created Agent - User permissions tab - Add User - Provide "Agent User" role to a user / All Users as needed
1. Access the Gemini enterprise app and select the agent or invoke it with `@agent_name`


### Securing access, Evaluating, Optimizing performance and costs

#### Securing access

  1. For local runs, make sure that you are not using a shared machine.
  1. For agent accessed from Gemini Enterprise - the access is granted using step 6 from [Accessing the Agent as a Gemini Enterprise Agent Application](#accessing-the-agent-as-a-gemini-enterprise-agent-application). 

#### Evaluating

It is advised to evaluate the agent for the trajectory it takes and the output it produces - you can use [ADK documentation](https://google.github.io/adk-docs/evaluate/) to evaluate this agent. You can also test with different models.

#### Optimizing performance and costs

Various native performance improvements are included in the codebase:

- **Event Compaction & Context Caching**: The values `EVENT_COMPACTION=Y` and `CONTEXT_CACHING=Y` in `.env` enable ADK [event compaction](https://adk.dev/context/compaction/) and [context caching](https://adk.dev/context/caching/). They are on by default; you can change them in `.env` file and also change finer configuration details in `agent.py` file.
- **Gemini Model Selection**: Refer to [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing) before choosing a Gemini model.

### FQL Guide Resources

The agent is configured with `use_mcp_resources=True`, which enables ADK's MCP resource support. The falcon-mcp server exposes FQL (Falcon Query Language) guide resources (e.g., `falcon://detections/search/fql-guide`) that the agent can fetch on demand via the auto-discovered `load_mcp_resource` tool. This gives the LLM access to field names, filter syntax, and query examples — resulting in more accurate Falcon queries without needing to embed all FQL documentation in the system prompt.

### Troubleshooting

#### `Context variable not found: 'user_name'`

Google ADK interprets `{variable_name}` patterns in agent instruction strings as template variables that must be resolved from session state. If your `FALCON_AGENT_PROMPT` contains curly braces, you will see this error when sending messages.

**Fix:** Remove all curly braces from your prompt. The default prompt in `env.properties` is safe to use as-is.

#### `Consistent 429 errors / consistent model errors`

**Fix:** Check your Gemini Quota, Try changing the model and switching off `EVENT_COMPACTION` and `CONTEXT_CACHING`
