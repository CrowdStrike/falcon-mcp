import logging
import os
from typing import Any

from google.adk.agents import LlmAgent  # type: ignore[import-untyped]
from google.adk.agents.callback_context import CallbackContext  # type: ignore[import-untyped]
from google.adk.agents.readonly_context import ReadonlyContext  # type: ignore[import-untyped]
from google.adk.models import LlmRequest, LlmResponse  # type: ignore[import-untyped]
from google.adk.tools.base_tool import BaseTool  # type: ignore[import-untyped]
from google.adk.tools.mcp_tool.mcp_session_manager import (  # type: ignore[import-untyped]
    StdioConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset  # type: ignore[import-untyped]
from mcp import StdioServerParameters

tools_cache: dict[str, list[BaseTool]] = {}


class CachedMCPToolset(MCPToolset):
    """Adds tool caching on top of MCPToolset to avoid repeated MCP server round-trips."""

    def __init__(self, *, tool_set_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.tool_set_name = tool_set_name
        logging.info(f"CachedMCPToolset initialized: '{self.tool_set_name}'")

    async def get_tools(
        self,
        readonly_context: ReadonlyContext | None = None,
    ) -> list[BaseTool]:
        if self.tool_set_name in tools_cache:
            logging.info(f"Returning cached tools for '{self.tool_set_name}'")
            return tools_cache[self.tool_set_name]

        logging.info(f"Fetching tools for '{self.tool_set_name}' from MCP server")
        tools = await super().get_tools(readonly_context)
        tools_cache[self.tool_set_name] = tools
        logging.info(f"Cached {len(tools)} tools for '{self.tool_set_name}'")
        return tools


# Controlling context size to improve Model response time and for cost optimization
# https://github.com/google/adk-python/issues/752#issuecomment-2948152979
def bmc_trim_llm_request(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    max_prev_user_interactions = int(os.environ.get("MAX_PREV_USER_INTERACTIONS", "-1"))

    logging.info(
        f"Number of contents going to LLM - {len(llm_request.contents)}, MAX_PREV_USER_INTERACTIONS = {max_prev_user_interactions}"
    )

    temp_processed_list = []

    if max_prev_user_interactions == -1:
        return None
    else:
        user_message_count = 0
        for i in range(len(llm_request.contents) - 1, -1, -1):
            item = llm_request.contents[i]

            if (
                item.role == "user"
                and item.parts[0]
                and item.parts[0].text
                and item.parts[0].text != "For context:"
            ):
                logging.info(f"Encountered a user message => {item.parts[0].text}")
                user_message_count += 1

            if user_message_count > max_prev_user_interactions:
                logging.info(f"Breaking at user_message_count => {user_message_count}")
                temp_processed_list.append(item)
                break

            temp_processed_list.append(item)

        final_list = temp_processed_list[::-1]

        if user_message_count < max_prev_user_interactions:
            logging.info(
                "User message count did not reach the allowed limit. List remains unchanged."
            )
        else:
            logging.info(
                f"User message count reached {max_prev_user_interactions}. List truncated."
            )
            llm_request.contents = final_list

    return None


# Get required environment variables
_google_model = os.environ.get("GOOGLE_MODEL", "")
_falcon_agent_prompt = os.environ.get("FALCON_AGENT_PROMPT", "")
_falcon_client_id = os.environ.get("FALCON_CLIENT_ID", "")
_falcon_client_secret = os.environ.get("FALCON_CLIENT_SECRET", "")
_falcon_base_url = os.environ.get("FALCON_BASE_URL", "")

root_agent = LlmAgent(
    model=_google_model,
    name="falcon_agent",
    instruction=_falcon_agent_prompt,
    before_model_callback=bmc_trim_llm_request,
    tools=[
        CachedMCPToolset(
            tool_set_name="falcon-tools",
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="falcon-mcp",
                    env={
                        "FALCON_CLIENT_ID": _falcon_client_id,
                        "FALCON_CLIENT_SECRET": _falcon_client_secret,
                        "FALCON_BASE_URL": _falcon_base_url,
                    },
                )
            ),
            use_mcp_resources=True,
        ),
    ],
)
