"""
Contains AgentWorks (agentic-studio) FQL filter resources.

Every field documented here was live-verified against real tenant data
(2026-08-05). Eight of the nine agentic-studio query endpoints silently return
HTTP 200 with zero results for an unsupported filter field rather than a 400, so
only fields confirmed against a known real value are listed. Sort-only fields are
deliberately excluded — being sortable does not make a field filterable.
"""

from falcon_mcp.common.fql import FQL_BASE_OPERATORS
from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, operators, description)
SEARCH_AGENTWORKS_AGENTS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "template_id",
        "String",
        "No",
        """
        ID of the agent template the agent was created from.

        Ex: template_id:'ioc-review-agent'
        """
    ),
    (
        "active_version.model",
        "String",
        "No",
        """
        Model backing the agent's active version. This is a nested field; the
        top-level agent record has no filterable name/model of its own.

        Ex: active_version.model:'bedrock.claude-4-6-sonnet'
        """
    ),
    (
        "published_version_ids",
        "String",
        "No",
        """
        Matches agents that publish a given agent-version ID.

        Ex: published_version_ids:'a1b2c3d4-0000-1111-2222-333344445555'
        """
    ),
]

SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "agent_id",
        "String",
        "No",
        """
        ID of the parent agent. The primary way to list a single agent's versions.

        Ex: agent_id:'467e856f-0000-1111-2222-333344445555'
        """
    ),
    (
        "name",
        "String",
        "No",
        """
        Exact version name. Wildcards are NOT supported here (name:'x*' returns 0).

        Ex: name:'IOC Review Agent'
        """
    ),
    (
        "model",
        "String",
        "No",
        """
        Model backing the version.

        Ex: model:'bedrock.claude-3-7-sonnet'
        """
    ),
    (
        "is_published",
        "Boolean",
        "No",
        """
        Whether the version is published. Quoted or unquoted both work.

        Ex: is_published:true
        """
    ),
    (
        "is_enabled",
        "Boolean",
        "No",
        """
        Whether the version is enabled.

        Ex: is_enabled:true
        """
    ),
    (
        "created_at",
        "Timestamp",
        "Yes",
        """
        When the version was created. Range operators work.

        Ex: created_at:>'2026-01-01'
        """
    ),
]

SEARCH_AGENTWORKS_SPANS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "trace_id",
        "String",
        "No",
        """
        Trace the span belongs to. This is the primary use of the spans tool:
        pass an invocation's `ai_trace_id` here to retrieve that run's spans.

        Ex: trace_id:'a1b2c3d4-0000-1111-2222-333344445555'
        """
    ),
    (
        "span_type",
        "String",
        "No",
        """
        Type of span. Values seen live include: llm, aw_agent, aiplatform_agent,
        aw_agent_response, aiplatform_agent_response, charlotteai_reply,
        charlotteai_agent.

        Ex: span_type:'llm'
        """
    ),
    (
        "status",
        "String",
        "No",
        """
        Span status. Values: unset, ok, error.

        Ex: status:'error'
        """
    ),
    (
        "name",
        "String",
        "No",
        """
        Exact span name.

        Ex: name:'llm'
        """
    ),
    (
        "duration_ms",
        "Number",
        "Yes",
        """
        Span duration in milliseconds. Numeric operators work.

        Ex: duration_ms:>100
        """
    ),
    (
        "start_time",
        "Timestamp",
        "Yes",
        """
        When the span started. Range operators work, but the API enforces a
        90-day retention window: a start_time older than 90 days returns a 400.

        Ex: start_time:>'now-7d'
        """
    ),
]

SEARCH_AGENTWORKS_AGENTS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search AgentWorks Agents Guide

""" + FQL_BASE_OPERATORS + """

=== falcon_search_agentworks_agents FQL filter options ===

""" + generate_md_table(SEARCH_AGENTWORKS_AGENTS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• The agent record has no top-level name/model — filter the model via the nested
  active_version.model field.
• Wildcards (*) are not supported on these fields.
• sort supports: created_date

=== COMMON FILTER EXAMPLES ===
• Agents on a specific model: active_version.model:'bedrock.claude-4-6-sonnet'
• Agents from a template: template_id:'ioc-review-agent'
"""

SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search AgentWorks Agent Versions Guide

""" + FQL_BASE_OPERATORS + """

=== falcon_search_agentworks_agent_versions FQL filter options ===

""" + generate_md_table(SEARCH_AGENTWORKS_AGENT_VERSIONS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Wildcards (*) are NOT supported here (e.g. name:'x*' returns 0 results) — use
  exact names.
• Booleans work quoted or unquoted: is_published:true
• Dates support range operators: created_at:>'2026-01-01'
• sort supports: created_at

=== COMMON FILTER EXAMPLES ===
• All versions of one agent: agent_id:'467e856f-...'
• Published versions only: is_published:true
• Versions on a model: model:'bedrock.claude-3-7-sonnet'
"""

SEARCH_AGENTWORKS_SPANS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search AgentWorks Spans Guide

""" + FQL_BASE_OPERATORS + """

=== falcon_search_agentworks_spans FQL filter options ===

""" + generate_md_table(SEARCH_AGENTWORKS_SPANS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Spans total in the hundreds of thousands — ALWAYS filter, usually by trace_id.
• The invocation→spans link is trace_id only: pass an invocation's `ai_trace_id`
  as trace_id:'<value>' to see that run's spans.
• start_time is limited to the last 90 days (older values return a 400).
• Use single quotes around string values: 'value'
• sort supports: start_time

=== COMMON FILTER EXAMPLES ===
• One run's spans: trace_id:'<ai_trace_id from an invocation>'
• Errored LLM spans in a trace: trace_id:'...'+span_type:'llm'+status:'error'
• Slow spans in a trace: trace_id:'...'+duration_ms:>1000
"""
