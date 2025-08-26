import logging
import os
import sys
from typing import List, Optional, TextIO, Union

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_schemes import AuthScheme
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import ToolPredicate
from google.adk.tools.mcp_tool import MCPTool
from google.adk.tools.mcp_tool.mcp_session_manager import (
  MCPSessionManager,
  SseConnectionParams,
  StdioConnectionParams,
  StreamableHTTPConnectionParams,
  retry_on_closed_resource,
)
from google.adk.tools.mcp_tool.mcp_toolset import (
  MCPToolset,
  StdioConnectionParams,
  StdioServerParameters,
)
from mcp import StdioServerParameters
from mcp.types import ListToolsResult
from typing_extensions import override

tools_cache={}

class MCPToolSetWithSchemaAccess(MCPToolset):

  def __init__(
      self,
      *,
      tool_set_name: str,
      connection_params: Union[
          StdioServerParameters,
          StdioConnectionParams,
          SseConnectionParams,
          StreamableHTTPConnectionParams,
      ],
      tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
      errlog: TextIO = sys.stderr,
      auth_scheme: Optional[AuthScheme] = None,
      auth_credential: Optional[AuthCredential] = None,
  ):
    self.tool_set_name = tool_set_name
    super().__init__(tool_filter=tool_filter)

    if not connection_params:
      raise ValueError("Missing connection params in MCPToolset.")

    self._connection_params = connection_params
    self._errlog = errlog

    # Create the session manager that will handle the MCP connection
    self._mcp_session_manager = MCPSessionManager(
        connection_params=self._connection_params,
        errlog=self._errlog,
    )
    self._auth_scheme = auth_scheme
    self._auth_credential = auth_credential

  @retry_on_closed_resource
  @override
  async def get_tools(
      self,
      readonly_context: Optional[ReadonlyContext] = None,
  ) -> List[BaseTool]:
    """Return all tools in the toolset based on the provided context.

    Args:
        readonly_context: Context used to filter tools available to the agent.
            If None, all tools in the toolset are returned.

    Returns:
        List[BaseTool]: A list of tools available under the specified context.
    """
    # Get session from session manager
    session = await self._mcp_session_manager.create_session()

    if self.tool_set_name in tools_cache.keys():
      logging.info(f"Tools found in cache for toolset {self.tool_set_name}, returning them")
      return tools_cache[self.tool_set_name]
    else:
      logging.info(f"No tools found in cache for toolset {self.tool_set_name}, loading")

    # Fetch available tools from the MCP server
    tools_response: ListToolsResult = await session.list_tools()

    # Apply filtering based on context and tool_filter
    tools = []
    for tool in tools_response.tools:
      mcp_tool = MCPTool(
          mcp_tool=tool,
          mcp_session_manager=self._mcp_session_manager,
          auth_scheme=self._auth_scheme,
          auth_credential=self._auth_credential,
      )

      if self._is_tool_selected(mcp_tool, readonly_context):
        tools.append(mcp_tool)

    model_version = os.environ.get("GOOGLE_MODEL").split("-")[1]
    if float(model_version) < 2.5 or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI").upper() == "TRUE":
      logging.error(f"Model - {os.environ.get('GOOGLE_MODEL')} needs Gemini compatible tools, updating schema ...")
      tools = make_tools_compatible(tools)
    else:
      logging.info(f"Model - {os.environ.get('GOOGLE_MODEL')} does not need updating schema")

    # add tools to the cache
    tools_cache[self.tool_set_name] = tools
    return tools


class MCPToolSetWithSchemaAccess(MCPToolset):
  """
    Added to make the MCP tools schema compatible with Vertext AI API and also older Gemini models.
    Also introduced a small performance improvement with tools caching.
  """

  def __init__(
      self,
      *,
      tool_set_name: str, # <-- new parameter
      connection_params: Union[
          StdioServerParameters,
          StdioConnectionParams,
          SseConnectionParams,
          StreamableHTTPConnectionParams,
      ],
      tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
      errlog: TextIO = sys.stderr,
  ):
    super().__init__(
        connection_params=connection_params,
        tool_filter=tool_filter,
        errlog=errlog
    )
    self.tool_set_name = tool_set_name
    logging.info(f"MCPToolSetWithSchemaAccess initialized with tool_set_name: '{self.tool_set_name}'")
    self._session = None

  @retry_on_closed_resource
  async def get_tools(
      self,
      readonly_context: Optional[ReadonlyContext] = None,
  ) -> List[BaseTool]:
    """Return all tools in the toolset based on the provided context.

    Args:
        readonly_context: Context used to filter tools available to the agent.
            If None, all tools in the toolset are returned.

    Returns:
        List[BaseTool]: A list of tools available under the specified context.
    """
    # Get session from session manager
    session = await self._mcp_session_manager.create_session()

    if self.tool_set_name in tools_cache.keys():
      logging.info(f"Tools found in cache for toolset {self.tool_set_name}, returning them")
      return tools_cache[self.tool_set_name]
    else:
      logging.info(f"No tools found in cache for toolset {self.tool_set_name}, loading")

    # Fetch available tools from the MCP server
    tools_response: ListToolsResult = await session.list_tools()

    # Apply filtering based on context and tool_filter
    tools = []
    for tool in tools_response.tools:
      mcp_tool = MCPTool(
          mcp_tool=tool,
          mcp_session_manager=self._mcp_session_manager,
          auth_scheme=self._auth_scheme,
          auth_credential=self._auth_credential,
      )

      if self._is_tool_selected(mcp_tool, readonly_context):
        tools.append(mcp_tool)

    model_version = os.environ.get("GOOGLE_MODEL").split("-")[1]
    if float(model_version) < 2.5 or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI").upper() == "TRUE":
      logging.error(f"Model - {os.environ.get('GOOGLE_MODEL')} needs Gemini compatible tools, updating schema ...")
      tools = make_tools_compatible(tools)
    else:
      logging.info(f"Model - {os.environ.get('GOOGLE_MODEL')} does not need updating schema")

    tools_cache[self.tool_set_name] = tools

    return tools

def make_tools_compatible(tools):
  """
  This function makes the schema compatible with Gemini/Vertex AI API
  It is only needed when API used is Gemini and model is other than 2.5 models
  It is however needed for ALL models when API used is VertexAI
  """
  for tool in tools:
    for key in tool._mcp_tool.inputSchema.keys():
      if key == "properties":
          for prop_name in tool._mcp_tool.inputSchema["properties"].keys():
            if "anyOf" in tool._mcp_tool.inputSchema["properties"][prop_name].keys():
              if (tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][0]["type"] == "array"):
                tool._mcp_tool.inputSchema["properties"][prop_name]["type"] = tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][0]["items"]["type"]
              else:
                 tool._mcp_tool.inputSchema["properties"][prop_name]["type"] = tool._mcp_tool.inputSchema["properties"][prop_name]["anyOf"][0]["type"]
              tool._mcp_tool.inputSchema["properties"][prop_name].pop("anyOf")

  return tools


# Controlling context size to improve Model response time and for cost optimization
# https://github.com/google/adk-python/issues/752#issuecomment-2948152979
def bmc_trim_llm_request(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:

    max_prev_user_interactions = int(os.environ.get("MAX_PREV_USER_INTERACTIONS","-1"))

    logging.info(f"Number of contents going to LLM - {len(llm_request.contents)}, MAX_PREV_USER_INTERACTIONS = {max_prev_user_interactions}")

    temp_processed_list = []

    if max_prev_user_interactions == -1:
        return None
    else:
        user_message_count = 0
        for i in range(len(llm_request.contents) - 1, -1, -1):
            item = llm_request.contents[i]

            if item.role == "user" and item.parts[0] and item.parts[0].text and item.parts[0].text != "For context:":
                logging.info(f"Encountered a user message => {item.parts[0].text}")
                user_message_count += 1

            if user_message_count > max_prev_user_interactions:
                logging.info(f"Breaking at user_message_count => {user_message_count}")
                temp_processed_list.append(item)
                break

            temp_processed_list.append(item)

        final_list = temp_processed_list[::-1]

        if user_message_count < max_prev_user_interactions:
            logging.info("User message count did not reach the allowed limit. List remains unchanged.")
        else:
            logging.info(f"User message count reached {max_prev_user_interactions}. List truncated.")
            llm_request.contents = final_list

    return None


root_agent = LlmAgent(
    model=os.environ.get("GOOGLE_MODEL"),
    name='falcon_agent',
    instruction=os.environ.get("FALCON_AGENT_PROMPT"),
    tools=[
        MCPToolSetWithSchemaAccess(
          tool_set_name="falcon-tools",
            connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                      command='falcon-mcp',
                      env={
                      "FALCON_CLIENT_ID":os.environ.get("FALCON_CLIENT_ID"),
                      "FALCON_CLIENT_SECRET":os.environ.get("FALCON_CLIENT_SECRET"),
                      "FALCON_BASE_URL":os.environ.get("FALCON_BASE_URL"),
                      }
                    )
                    )
            ),
    ],
)
