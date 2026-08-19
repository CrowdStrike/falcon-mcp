import os
import sys

from google.adk.agents import LlmAgent  # type: ignore[import-untyped]
from google.adk.agents.context_cache_config import (  # type: ignore[import-untyped]
    ContextCacheConfig,
)
from google.adk.apps.app import App, EventsCompactionConfig  # type: ignore[import-untyped]
from google.adk.tools.mcp_tool.mcp_session_manager import (  # type: ignore[import-untyped]
    StdioConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset  # type: ignore[import-untyped]
from mcp import StdioServerParameters

# Validate required environment variables
_required_vars = [
    "FALCON_CLIENT_ID",
    "FALCON_CLIENT_SECRET",
    "FALCON_BASE_URL",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
]
_missing = [v for v in _required_vars if not os.environ.get(v) or os.environ.get(v) == "NOT_SET"]
if _missing:
    _error_msg = (
        f"\n❌ [falcon_agent] Missing or unset required environment variables: {', '.join(_missing)}\n"
        "👉 Please configure them in your .env file.\n"
    )
    print(_error_msg, file=sys.stderr)
    raise RuntimeError(_error_msg)

# Get required environment variables
_google_model = os.environ.get("GOOGLE_MODEL", "gemini-2.5-flash")
_falcon_agent_prompt = os.environ.get("FALCON_AGENT_PROMPT", "")
_falcon_client_id = os.environ.get("FALCON_CLIENT_ID", "")
_falcon_client_secret = os.environ.get("FALCON_CLIENT_SECRET", "")
_falcon_base_url = os.environ.get("FALCON_BASE_URL", "")
_event_compaction = os.environ.get("EVENT_COMPACTION", "")
_context_caching = os.environ.get("CONTEXT_CACHING", "")

root_agent = LlmAgent(
    model=_google_model,
    name="falcon_agent",
    instruction=_falcon_agent_prompt,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="falcon-mcp",
                    env={
                        "FALCON_CLIENT_ID": _falcon_client_id,
                        "FALCON_CLIENT_SECRET": _falcon_client_secret,
                        "FALCON_BASE_URL": _falcon_base_url,
                    },
                ),
                timeout=30.0,
            ),
            use_mcp_resources=True,
        ),
    ],
)

# Documentation - https://adk.dev/context/compaction/
events_compaction_config = (
    EventsCompactionConfig(
        compaction_interval=5,  # Trigger compaction every 5 new invocations.
        overlap_size=1,  # Include last invocation from the previous window.
    )
    if _event_compaction == "Y"
    else None
)

# Documentation - https://adk.dev/context/caching/
context_cache_config = (
    ContextCacheConfig(
        min_tokens=4096,  # Minimum tokens to trigger caching
        ttl_seconds=600,  # Store for up to 10 minutes
        cache_intervals=5,  # Refresh after 5 uses
    )
    if _context_caching == "Y"
    else None
)

# Context caching and event compression configuration requires an ADK App.
app = App(
    name="falcon_agent",
    root_agent=root_agent,
    # Context Caching
    context_cache_config=context_cache_config,
    # Context Compaction
    events_compaction_config=events_compaction_config,
)