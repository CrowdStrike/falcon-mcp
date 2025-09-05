#!/bin/bash

# This script runs or deploys an AI agent based on the provided operation mode.
# It loads environment variables from ./falcon_agent/.env and validates required variables
# for the chosen mode.

# IMPORTANT: If you want the exported environment variables to persist in your
# calling shell (e.g., your terminal session) after this script finishes,
# you MUST 'source' this script, like:
# source ./adk_agent_operations.sh local_run

# --- Configuration ---
ENV_DIR="./falcon_agent"
ENV_FILE="${ENV_DIR}/.env"
ENV_PROPERTIES_TEMPLATE="${ENV_DIR}/env.properties"
INVALID_VALUE="NOT_SET" # The literal string considered an invalid value
ENV_BACKUP_FILE="${ENV_FILE}.bak"

# Define required variables for each operation mode
# These are comma-separated lists of variable names
vars_for_local_run="GOOGLE_GENAI_USE_VERTEXAI,GOOGLE_API_KEY,GOOGLE_MODEL,FALCON_CLIENT_ID,FALCON_CLIENT_SECRET,FALCON_BASE_URL,FALCON_AGENT_PROMPT"
vars_for_cloudrun_deploy="GOOGLE_GENAI_USE_VERTEXAI,GOOGLE_MODEL,FALCON_CLIENT_ID,FALCON_CLIENT_SECRET,FALCON_BASE_URL,FALCON_AGENT_PROMPT,PROJECT_ID,REGION"
vars_for_agent_engine_deploy="GOOGLE_GENAI_USE_VERTEXAI,GOOGLE_MODEL,FALCON_CLIENT_ID,FALCON_CLIENT_SECRET,FALCON_BASE_URL,FALCON_AGENT_PROMPT,PROJECT_ID,REGION,AGENT_ENGINE_STAGING_BUCKET"
vars_for_agentspace_register="GOOGLE_GENAI_USE_VERTEXAI,GOOGLE_MODEL,FALCON_CLIENT_ID,FALCON_CLIENT_SECRET,FALCON_BASE_URL,FALCON_AGENT_PROMPT,PROJECT_ID,REGION,PROJECT_NUMBER,AGENT_LOCATION,REASONING_ENGINE_NUMBER,AGENT_SPACE_APP_NAME" # Added AGENT_SPACE_APP_NAME

# --- Functions ---

# Function to display script usage
usage() {
  echo "Usage: $0 <operation_mode>"
  echo ""
  echo "Operation Modes:"
  echo "  local_run"
  echo "  cloudrun_deploy"
  echo "  agent_engine_deploy"
  echo "  agentspace_register"
  echo ""
  echo "Example: source $0 local_run"
  exit 1 # Exit with error code
}

# Function to validate required environment variables
# Arguments: $1 = comma-separated string of required variable names
validate_required_vars() {
  local required_vars_string="$1"
  IFS=',' read -r -a required_vars_array <<< "$required_vars_string" # Split string into array

  local all_vars_valid=true

  echo "--- Validating required environment variables for '$OPERATION_MODE' mode ---"
  for var_name in "${required_vars_array[@]}"; do
    # Check if variable is set and not empty
    if [[ -z "${!var_name}" ]]; then
      echo "ERROR: Required environment variable '$var_name' is missing or empty."
      all_vars_valid=false
    # Check if variable's value is the literal INVALID_VALUE string
    elif [[ "${!var_name}" == "$INVALID_VALUE" ]]; then
      echo "ERROR: Required environment variable '$var_name' has an invalid value: '$INVALID_VALUE'."
      all_vars_valid=false
    else
      echo "INFO: Variable '$var_name' is set and valid."
    fi
  done

  if ! $all_vars_valid; then
    echo "--- Validation FAILED. Please check your '$ENV_FILE' file. ---"
    return 1 # Indicate validation failure within the function
  fi

  echo "--- All required environment variables are VALID. ---"
  return 0 # Indicate validation success within the function
}

# Function to backup, modify, and restore .env file
# This function is intended to be called with 'trap' for cleanup.
cleanup_env_on_exit() {
    if [[ -f "$ENV_BACKUP_FILE" ]]; then
        echo "INFO: Restoring .env file from backup: '$ENV_BACKUP_FILE'."
        mv "$ENV_BACKUP_FILE" "$ENV_FILE" || echo "WARNING: Failed to restore .env file from backup. Manual intervention may be required."
    fi
}

# --- Main Script Logic ---

# Handle case: no arguments provided
if [ "$#" -eq 0 ]; then
    if [ ! -f "$ENV_FILE" ]; then
        echo "INFO: No operation mode provided and '$ENV_FILE' is not found."
        echo "INFO: Attempting to copy template '$ENV_PROPERTIES_TEMPLATE' to '$ENV_FILE'."

        # Ensure the directory exists
        mkdir -p "$ENV_DIR" || { echo "ERROR: Failed to create directory '$ENV_DIR'."; exit 1; }

        if [ -f "$ENV_PROPERTIES_TEMPLATE" ]; then
            cp "$ENV_PROPERTIES_TEMPLATE" "$ENV_FILE" || { echo "ERROR: Failed to copy '$ENV_PROPERTIES_TEMPLATE' to '$ENV_FILE'."; exit 1; }
            echo "SUCCESS: '$ENV_PROPERTIES_TEMPLATE' copied to '$ENV_FILE'."
            echo "ACTION REQUIRED: Please update the variables in '$ENV_FILE' before running this script with an operation mode."
            exit 0 # Exit after setup, user needs to edit the file
        else
            echo "ERROR: Template file '$ENV_PROPERTIES_TEMPLATE' not found. Cannot create '$ENV_FILE'."
            exit 1
        fi
    else
        # .env file exists but no arguments provided, so show usage
        echo "ERROR: No operation mode argument provided."
        usage # usage function calls exit 1
    fi
fi


OPERATION_MODE="$1"

# Validate the provided operation mode
case "$OPERATION_MODE" in
  local_run|cloudrun_deploy|agent_engine_deploy|agentspace_register)
    echo "INFO: Operation mode selected: '$OPERATION_MODE'."
    ;;
  *)
    echo "ERROR: Invalid operation mode: '$OPERATION_MODE'."
    usage # usage function calls exit 1
    ;;
esac

# Check if the .env file exists (after potential creation in no-arg case)
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: Environment file '$ENV_FILE' not found after initial checks. This should not happen."
  exit 1 # Terminate the script
fi

echo "--- Loading environment variables from '$ENV_FILE' ---"
# Load all valid variables from the .env file into the current shell environment.
eval "$(grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -E '^[[:alnum:]_]+=.*$' | sed -E 's/^([[:alnum:]_]+)=(.*)$/export \1="\2"/' )"
echo "--- Environment variables loaded. ---"

# Perform validation and execute mode-specific logic
case "$OPERATION_MODE" in
  local_run)
    validate_required_vars "$vars_for_local_run" || exit 1 # Exit if validation fails
    echo "INFO: Running ADK Agent for local development..."
    # Execute the local run command
    adk web
    local_run_status=$? # Capture exit status of the command
    if [ $local_run_status -eq 0 ]; then
        echo "SUCCESS: 'adk web' command completed successfully."
    else
        echo "ERROR: 'adk web' command failed with exit status $local_run_status."
        exit $local_run_status
    fi
    ;;

  cloudrun_deploy)
    validate_required_vars "$vars_for_cloudrun_deploy" || exit 1 # Exit if validation fails
    echo "INFO: Preparing for Cloud Run deployment..."

    # Backup .env file
    echo "INFO: Backing up '$ENV_FILE' to '$ENV_BACKUP_FILE'."
    cp "$ENV_FILE" "$ENV_BACKUP_FILE" || { echo "ERROR: Failed to backup .env file."; exit 1; }
    # Set trap to restore .env file on script exit (success or failure)
    trap cleanup_env_on_exit EXIT ERR

    # Modify .env file variables
    echo "INFO: Modifying '$ENV_FILE': Deleting GOOGLE_API_KEY and setting GOOGLE_GENAI_USE_VERTEXAI=True."
    # Use sed -i for in-place editing.
    # Delete line containing GOOGLE_API_KEY
    sed -i '/^GOOGLE_API_KEY=/d' "$ENV_FILE" || { echo "WARNING: Failed to delete GOOGLE_API_KEY from .env."; }
    # Replace GOOGLE_GENAI_USE_VERTEXAI value
    sed -i 's/^GOOGLE_GENAI_USE_VERTEXAI=.*/GOOGLE_GENAI_USE_VERTEXAI=True/' "$ENV_FILE" || { echo "WARNING: Failed to set GOOGLE_GENAI_USE_VERTEXAI=True in .env."; }

    # Re-load modified variables into current shell environment
    echo "INFO: Re-loading modified environment variables."
    eval "$(grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -E '^[[:alnum:]_]+=.*$' | sed -E 's/^([[:alnum:]_]+)=(.*)$/export \1="\2"/' )"

    echo "INFO: Deploying ADK Agent to Cloud Run..."
    # Execute the Cloud Run deployment command
    adk deploy cloud_run --project="$PROJECT_ID" --region="$REGION" --service_name="falcon-agent-service" --with_ui ./falcon_agent
    deploy_status=$? # Capture exit status of the command

    # Trap will handle restoration on exit
    if [ $deploy_status -eq 0 ]; then
        echo "SUCCESS: Cloud Run deployment completed successfully."
    else
        echo "ERROR: Cloud Run deployment failed with exit status $deploy_status."
        exit $deploy_status
    fi
    ;;

  agent_engine_deploy)
    validate_required_vars "$vars_for_agent_engine_deploy" || exit 1 # Exit if validation fails
    echo "INFO: Preparing for Agent Engine deployment..."

    # Backup .env file
    echo "INFO: Backing up '$ENV_FILE' to '$ENV_BACKUP_FILE'."
    cp "$ENV_FILE" "$ENV_BACKUP_FILE" || { echo "ERROR: Failed to backup .env file."; exit 1; }
    # Set trap to restore .env file on script exit (success or failure)
    trap cleanup_env_on_exit EXIT ERR

    # Modify .env file variables (same as cloudrun_deploy for now)
    echo "INFO: Modifying '$ENV_FILE': Deleting GOOGLE_API_KEY and setting GOOGLE_GENAI_USE_VERTEXAI=True."
    sed -i '/^GOOGLE_API_KEY=/d' "$ENV_FILE" || { echo "WARNING: Failed to delete GOOGLE_API_KEY from .env."; }
    sed -i 's/^GOOGLE_GENAI_USE_VERTEXAI=.*/GOOGLE_GENAI_USE_VERTEXAI=True/' "$ENV_FILE" || { echo "WARNING: Failed to set GOOGLE_GENAI_USE_VERTEXAI=True in .env."; }

    # Re-load modified variables into current shell environment
    echo "INFO: Re-loading modified environment variables."
    eval "$(grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -E '^[[:alnum:]_]+=.*$' | sed -E 's/^([[:alnum:]_]+)=(.*)$/export \1="\2"/' )"

    echo "INFO: Deploying ADK Agent to Agent Engine..."
    # Execute the Agent Engine deployment command
    adk deploy agent_engine --project="$PROJECT_ID" --region="$REGION" --staging_bucket="$AGENT_ENGINE_STAGING_BUCKET" --display_name=falcon_agent ./falcon_agent
    deploy_status=$? # Capture exit status of the command

    # Trap will handle restoration on exit
    if [ $deploy_status -eq 0 ]; then
        echo "SUCCESS: Agent Engine deployment completed successfully."
    else
        echo "ERROR: Agent Engine deployment failed with exit status $deploy_status."
        exit $deploy_status
    fi
    ;;

  agentspace_register)
    validate_required_vars "$vars_for_agentspace_register" || exit 1 # Exit if validation fails
    echo "INFO: Registering ADK Agent with AgentSpace..."

    TARGET_URL="https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_ID/locations/$AGENT_LOCATION/collections/default_collection/engines/$AGENT_SPACE_APP_NAME/assistants/default_assistant/agents"

    # Construct JSON data using a here-document
    JSON_DATA=$(cat <<EOF
{
    "displayName": "CrowdStrike Falcon Agent",
    "description": "Allows users interact with CrowdStrike Falcon backend",
    "adk_agent_definition":
    {
        "tool_settings": {
            "tool_description": "CrowdStrike Falcon tools"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine":"projects/$PROJECT_NUMBER/locations/$REGION/reasoningEngines/$REASONING_ENGINE_NUMBER"
        }
    }
}
EOF
)

    echo "INFO: Sending POST request to: $TARGET_URL"
    echo "DEBUG: Request Body :"
    echo "$JSON_DATA"
    echo "..."

    # Perform the POST request using curl
    # Note: X-Goog-User-Project header should use the variable value
    curl -X POST \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $(gcloud auth print-access-token)" \
         -H "X-Goog-User-Project: $PROJECT_ID" \
         -d "$JSON_DATA" \
         "$TARGET_URL"
    curl_status=$? # Capture exit status of curl

    echo "" # Add a newline after curl output for better readability
    if [ $curl_status -eq 0 ]; then
        echo "SUCCESS: cURL command completed successfully for AgentSpace registration."
    else
        echo "ERROR: cURL command failed with exit status $curl_status during AgentSpace registration."
        exit $curl_status
    fi
    ;;
esac

echo "--- Operation '$OPERATION_MODE' complete. ---"
