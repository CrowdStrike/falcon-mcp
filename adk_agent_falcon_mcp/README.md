# Running/Deploying with a prebuilt agent

This repository includes a prebuilt [Google ADK](https://google.github.io/adk-docs/) based agent integrated with the `falcon-mcp` server.

The goal is to provide customers opinionated and validated set of instructions for running the Falcon MCP server and deploying it for their teams.

## Table of Contents

1. [Setting up and running locally (5 minutes)](#setting-up-and-running-locally-5-minutes)
2. [Deployment - Why Deploy?](#deployment---why-deploy)
3. [Deploying the agent to Cloud Run](#deploying-the-agent-to-cloud-run)
4. [Deploying to Vertex AI Agent Engine and registering on Agentspace](#deploying-to-vertex-ai-agent-engine-and-registering-on-agentspace)
5. [Securing access, Evaluating, Optimizing performance and costs](#securing-access-evaluating-optimizing-performance-and-costs)


### Setting up and running locally (5 minutes)
You can run the following commands locally on Linux / Mac or in Google Cloud Shell. 
If you plan to deploy the agent, it is recommended to run in Google Cloud Shell.

```bash

git clone https://github.com/CrowdStrike/falcon-mcp.git

cd falcon-mcp

cd adk_agent_falcon_mcp

# create and activate python environment
python3 -m venv .venv
. .venv/bin/activate

# install depenencies
pip install -r falcon_agent/requirements.txt

chmod +x adk_agent_operations.sh

./adk_agent_operations.sh

```



The script will create `.env` file in `falcon_agent/` directory and prompt you to update it. At a minimum update the `General Agent Configuration` section.


<details>

<summary><b>Sample Output - Very First Run</b></summary>

```bash
./adk_agent_operations.sh
INFO: No operation mode provided and './falcon_agent/.env' is not found.
INFO: Attempting to copy template './falcon_agent/env.properties' to './falcon_agent/.env'.
SUCCESS: './falcon_agent/env.properties' copied to './falcon_agent/.env'.
ACTION REQUIRED: Please update the variables in './falcon_agent/.env' before running this script with an operation mode.

```
</details>

<br>

> 🪧 **NOTE:**  
> Make sure you get and update the GOOGLE_API_KEY using these [instructions](https://ai.google.dev/gemini-api/docs/api-key).

Now run the script with `local_run` parameter.


```bash
# local run
./adk_agent_operations.sh local_run
```



Here is the sample output


<details>

<summary><b>Sample Output - Local Run</b></summary>

```bash
./adk_agent_operations.sh local_run
INFO: Operation mode selected: 'local_run'.
--- Loading environment variables from './falcon_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'local_run' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
INFO: Variable 'GOOGLE_API_KEY' is set and valid.
INFO: Variable 'GOOGLE_MODEL' is set and valid.
INFO: Variable 'FALCON_CLIENT_ID' is set and valid.
INFO: Variable 'FALCON_CLIENT_SECRET' is set and valid.
INFO: Variable 'FALCON_BASE_URL' is set and valid.
INFO: Variable 'FALCON_AGENT_PROMPT' is set and valid.
--- All required environment variables are VALID. ---
INFO: Running ADK Agent for local development...
INFO:     Started server process [20071]
INFO:     Waiting for application startup.

+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```
</details>

<br>

You can access the agent on http://localhost:8000 🚀

> If running in the Google Cloud Shell - please use the web preview with port 8000.

You can stop the agent with `ctrl+C`


### Deployment - Why Deploy?
You may want to deploy the agent (with the `falcon-mcp` server) for following reasons

1. You do not want to hand out credentials to everyone to run MCP server locally
2. You want to share the ready to use agent with your team
3. Use it for demos w/o any setup

You have two dinstinct paths to deployment
1. Deploy on Cloud Run
2. Deploy on Vertex AI Agent Engine (and access through Agentspace after registration)


### Deploying the agent to Cloud Run

This section covers deployment to cloud run. Make sure you have all the required [APIs enabled](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service#before-you-begin) on the GCP project.

```bash
cd adk_agent_falcon_mcp/
./adk_agent_operations.sh cloudrun_deploy
```

In the sample output below, note the lines market with ⬅️

1. You will have to provide input for `Allow unauthenticated invocations?`
2. Once deployment is completed you get a URL to access your agent.


<details>

<summary><b>Sample Output - Cloud Run Deloyment</b></summary>

```bash
INFO: Operation mode selected: 'cloudrun_deploy'.
--- Loading environment variables from './falcon_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'cloudrun_deploy' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
INFO: Variable 'GOOGLE_MODEL' is set and valid.
INFO: Variable 'FALCON_CLIENT_ID' is set and valid.
INFO: Variable 'FALCON_CLIENT_SECRET' is set and valid.
INFO: Variable 'FALCON_BASE_URL' is set and valid.
INFO: Variable 'FALCON_AGENT_PROMPT' is set and valid.
INFO: Variable 'PROJECT_ID' is set and valid.
INFO: Variable 'REGION' is set and valid.
--- All required environment variables are VALID. ---
INFO: Preparing for Cloud Run deployment...
INFO: Backing up './falcon_agent/.env' to './falcon_agent/.env.bak'.
INFO: Modifying './falcon_agent/.env': Deleting GOOGLE_API_KEY and setting GOOGLE_GENAI_USE_VERTEXAI=True.
INFO: Re-loading modified environment variables.
INFO: Deploying ADK Agent to Cloud Run...
Start generating Cloud Run source files in /tmp/cloud_run_deploy_src/20250801_071151
Copying agent source code...
Copying agent source code complete.
Creating Dockerfile...
Creating Dockerfile complete: /tmp/cloud_run_deploy_src/20250801_071151/Dockerfile
Deploying to Cloud Run...
Allow unauthenticated invocations to [falcon-agent-service] (y/N)?  y ⬅️

Building using Dockerfile and deploying container to Cloud Run service [falcon-agent-service] in project [crowdstrikexxxxxxx] region [us-central1]
⠛ Building and deploying new service... Uploading sources.                                                                                                                                                                        
  ⠛ Uploading sources...                                                                                                                                                                                                          
✓ Building and deploying new service... Done.                                                                                                                                                                                     
  ✓ Uploading sources...                                                                                                                                                                                                          
  ✓ Building Container... Logs are available at [https://console.cloud.google.com/cloud-build/builds;region=us-central1/b1dbfe60-46fe-4cc1-ba6a-xxxx?project=xxxxx].                                               
  ✓ Creating Revision...                                                                                                                                                                                                          
  ✓ Routing traffic...                                                                                                                                                                                                            
  ✓ Setting IAM Policy...                                                                                                                                                                                                         
Done.                                                                                                                                                                                                                             
Service [falcon-agent-service] revision [falcon-agent-service-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://falcon-agent-service-xxxxx.us-central1.run.app ⬅️
INFO: Display format: "none"
Cleaning up the temp folder: /tmp/cloud_run_deploy_src/20250801_071151
SUCCESS: Cloud Run deployment completed successfully.
--- Operation 'cloudrun_deploy' complete. ---
INFO: Restoring .env file from backup: './falcon_agent/.env.bak'.
```  

</details>

<br>

> ⚠️ **CAUTION:**  
> By default the cloud run service (which is your agent with the mcp server) is available without any authentication. Please check the [Securing access, Validating, Optimizing performance and costs](#securing-access-validating-optimizing-performance-and-costs) section to control the access to this service.

### Deploying to Vertex AI Agent Engine and registering on Agentspace

This section covers deployment to Vetex AI Agent Engine. To acces the agent and to consolidate all your agents under one umbrella you can also register the deployed agent to Agentspace.

1. Make sure that you create a bucket for staging theAgent Engine artifacts in the same project as the deployment (env variable - `AGENT_ENGINE_STAGING_BUCKET`).

```bash
cd adk_agent_falcon_mcp/
./adk_agent_operations.sh agent_engine_deploy
```

And here is the sample output.

Make sure you copy the Agent Engine Number from the output (marked by ⬅️ for illustration)

<details>

<summary><b>Sample Output - Agent Engine Deployment</b></summary>

```bash
INFO: Operation mode selected: 'agent_engine_deploy'.
--- Loading environment variables from './falcon_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'agent_engine_deploy' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
INFO: Variable 'GOOGLE_MODEL' is set and valid.
INFO: Variable 'FALCON_CLIENT_ID' is set and valid.
INFO: Variable 'FALCON_CLIENT_SECRET' is set and valid.
INFO: Variable 'FALCON_BASE_URL' is set and valid.
INFO: Variable 'FALCON_AGENT_PROMPT' is set and valid.
INFO: Variable 'PROJECT_ID' is set and valid.
INFO: Variable 'REGION' is set and valid.
INFO: Variable 'AGENT_ENGINE_STAGING_BUCKET' is set and valid.
--- All required environment variables are VALID. ---
INFO: Preparing for Agent Engine deployment...
INFO: Backing up './falcon_agent/.env' to './falcon_agent/.env.bak'.
INFO: Modifying './falcon_agent/.env': Deleting GOOGLE_API_KEY and setting GOOGLE_GENAI_USE_VERTEXAI=True.
INFO: Re-loading modified environment variables.
INFO: Deploying ADK Agent to Agent Engine...
Copying agent source code...
Copying agent source code complete.
Initializing Vertex AI...
Resolving files and dependencies...
Reading environment variables from /tmp/agent_engine_deploy_src/20250801_103024/.env
Vertex AI initialized.
Created /tmp/agent_engine_deploy_src/20250801_103024/agent_engine_app.py
Files and dependencies resolved
Deploying to agent engine...
Reading requirements from requirements='/tmp/agent_engine_deploy_src/20250801_103024/requirements.txt'
Read the following lines: ['google-adk[eval]', 'falcon-mcp', 'google-cloud-aiplatform[agent_engines]', 'cloudpickle']
Identified the following requirements: {'google-cloud-aiplatform': '1.105.0', 'cloudpickle': '3.1.1', 'pydantic': '2.11.7'}
The following requirements are missing: {'pydantic'}
The following requirements are appended: {'pydantic==2.11.7'}
The final list of requirements: ['google-adk[eval]', 'falcon-mcp', 'google-cloud-aiplatform[agent_engines]', 'cloudpickle', 'pydantic==2.11.7']
Using bucket agent-engine-xxyyzz
Wrote to gs://agent-engine-xxyyzz/agent_engine/agent_engine.pkl
Writing to gs://agent-engine-xxyyzz/agent_engine/requirements.txt
Creating in-memory tarfile of extra_packages
Writing to gs://agent-engine-xxyyzz/agent_engine/dependencies.tar.gz
Creating AgentEngine
INFO:vertexai.agent_engines:Creating AgentEngine
Create AgentEngine backing LRO: projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456/operations/5379102769057612345
INFO:vertexai.agent_engines:Create AgentEngine backing LRO: projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456/operations/5379102769057612345
View progress and logs at https://console.cloud.google.com/logs/query?project=crowdstrike-xxxx-yyyy
INFO:vertexai.agent_engines:View progress and logs at https://console.cloud.google.com/logs/query?project=crowdstrike-xxxx-yyyy
AgentEngine created. Resource name: projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456 ⬅️
INFO:vertexai.agent_engines:AgentEngine created. Resource name: projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456
To use this AgentEngine in another session:
INFO:vertexai.agent_engines:To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456')
INFO:vertexai.agent_engines:agent_engine = vertexai.agent_engines.get('projects/123456789101/locations/us-central1/reasoningEngines/3670952665795123456')
Cleaning up the temp folder: /tmp/agent_engine_deploy_src/20250801_103024
SUCCESS: Agent Engine deployment completed successfully.
--- Operation 'agent_engine_deploy' complete. ---
INFO: Restoring .env file from backup: './falcon_agent/.env.bak'.

```


</details>

<br>

Once the agent is deployed on Agent Engine, you can register it on Agentspace to work with an Agent Engine Application.

Make sure you have the Agent Engine Number from the previous step


1. Go to the Agentspace [page](https://console.cloud.google.com/gen-app-builder/engines) in Google Cloud Console.
2. Create an App (Type - AgentSpace)
3. Note down the app details including the app name (e.g. google-security-agent-app_1750057151234)
4. Make sure that you have the Agent Space Admin role while performing the following actions
5. Enable Discovery Engine API for your project
6. Provide the following roles to the Discovery Engine Service Account  
  Vertex AI viewer  
  Vertex AI user  
7. Please note that these roles need to be provided into the project housing your Agent Engine Agent. Also you need to enable the show Google provided role grants to access the Discovery Engine Service Account.

Update the environment variables PROJECT_NUMBER, AGENT_LOCATION, REASONING_ENGINE_NUMBER and AGENT_SPACE_APP_NAME in the `# Agentspace Specific` section.

Now to register the agent and make it available to your application use the following command.

```bash
cd adk_agent_falcon_mcp/
./adk_agent_operations.sh agentspace_register
```

<details>

<summary><b>Sample Output - Agentspace Registration</b></summary>


```bash
INFO: Operation mode selected: 'agentspace_register'.
--- Loading environment variables from './falcon_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'agentspace_register' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
INFO: Variable 'GOOGLE_MODEL' is set and valid.
INFO: Variable 'FALCON_CLIENT_ID' is set and valid.
INFO: Variable 'FALCON_CLIENT_SECRET' is set and valid.
INFO: Variable 'FALCON_BASE_URL' is set and valid.
INFO: Variable 'FALCON_AGENT_PROMPT' is set and valid.
INFO: Variable 'PROJECT_ID' is set and valid.
INFO: Variable 'REGION' is set and valid.
INFO: Variable 'PROJECT_NUMBER' is set and valid.
INFO: Variable 'AGENT_LOCATION' is set and valid.
INFO: Variable 'REASONING_ENGINE_NUMBER' is set and valid.
INFO: Variable 'AGENT_SPACE_APP_NAME' is set and valid.
--- All required environment variables are VALID. ---
INFO: Registering ADK Agent with AgentSpace...
INFO: Sending POST request to: https://discoveryengine.googleapis.com/v1alpha/projects/security-xyzabc-123456/locations/global/collections/default_collection/engines/google-security-agent-app_1750057112345/assistants/default_assistant/agents
DEBUG: Request Body :
{
    "displayName": "Crowdstrike Falcon Agent",
    "description": "Allows users interact with Crowdstrike Falcon backend",
    "adk_agent_definition":
    {
        "tool_settings": {
            "tool_description": "Crowdstrike Falcon tools"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine":"projects/707099123456/locations/us-central1/reasoningEngines/5047646776881234567"
        }
    }
}
...
{
  "name": "projects/707099123456/locations/global/collections/default_collection/engines/google-security-agent-app_1750057112345/assistants/default_assistant/agents/2662627860861234567",
  "displayName": "Crowdstrike Falcon Agent",
  "description": "Allows users interact with Crowdstrike Falcon backend",
  "createTime": "2025-08-03T15:39:03.129318186Z",
  "adkAgentDefinition": {
    "toolSettings": {
      "toolDescription": "Crowdstrike Falcon tools"
    },
    "provisionedReasoningEngine": {
      "reasoningEngine": "projects/707099123456/locations/us-central1/reasoningEngines/5047646776881234567"
    }
  },
  "state": "ENABLED"
}

SUCCESS: cURL command completed successfully for AgentSpace registration.
--- Operation 'agentspace_register' complete. ---

```
</details>

<br>

> You can find more about AgentSpace registration [here](https://cloud.google.com/agentspace/agentspace-enterprise/docs/assistant#create-assistant-existing-app).

Now you can access the agent in the Agentspace application you created earlier.


In case you want to delete the agent from the Agentspace application, use the following set of commands (replace the variables as needed).

<details>

<summary><b>List and deregister the Agent</b></summary>

```bash
# List the agents for your application

curl -X GET -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: $PROJECT_ID" \
"https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_ID/locations/global/collections/default_collection/engines/$AGENT_ENGINE_APP_NAME/assistants/default_assistant/agents" 

# note down the agent number (export as REASONING_ENGINE_NUMBER) and use that in the next command.

curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: $PROJECT_ID" \
https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_ID/locations/global/collections/default_collection/engines/$AGENT_ENGINE_APP_NAME/assistants/default_assistant/agents/$REASONING_ENGINE_NUMBER


```
</details>

### Securing access, Evaluating, Optimizing performance and costs

#### Securing access
  1. For local runs make sure that you are not using a shared machine
  2. For Cloud Run deployment you can use - [Control access on an individual service or job](https://cloud.google.com/run/docs/securing/managing-access#control-service-or-job-access)
  3. For agent running in Agentspace - you can provide access (Predefined role - `Discovery Engine User`) selectively by navigating to Agentspace-Apps-Your App -Integration-Grant Permissions.

#### Evaluating
It is adviced to evaluate the agent for the trajectory it takes and the output it produces - you can use [ADK documentation](https://google.github.io/adk-docs/evaluate/) to evaluate this agent. You can also test with different models.

#### Optimizing performance and costs
Various native performance improvements are already part of the codebase. You can further optimize the performance and reduce the LLM costs by controlling the value of the envrionment variable `MAX_PREV_USER_INTERACTIONS`. You can test how many previous conversations (instead of ALL conversations by default) work for your use case (recommended 5). You can also use the appropriate [Gemini Model](https://ai.google.dev/gemini-api/docs/models#model-variations) for both cost and performance optimizations.