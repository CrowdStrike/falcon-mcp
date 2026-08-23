"""
Contains Fusion SOAR Workflows FQL filter resources.

Every field documented here was live-verified against real tenant data on two
separate tenants (2026-08-21) by filtering on a known entity's own value and
confirming a non-empty result. Both workflow search endpoints reject an unknown
property with a 400 that names it, but a *known* field with an unsupported
operator still returns an empty HTTP 200 — so operator support was verified per
field as well. Fields that the API accepted as valid properties but that never
matched a known value are omitted rather than presented as working.
"""

from falcon_mcp.common.fql import FQL_BASE_OPERATORS
from falcon_mcp.common.utils import generate_md_table

# List of tuples containing filter options data: (name, type, operators, description)
SEARCH_WORKFLOW_DEFINITIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "name.raw",
        "String",
        "Yes",
        """
        Workflow name, unanalyzed. This is the ONLY field that does exact and
        substring name matching. Note name.raw is not returned in the response
        entity, which carries `name` instead.

        Ex (exact): name.raw:'Adversary Exposure Mitigation'
        Ex (substring): name.raw:*'*Exposure*'
        """
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Workflow name, analyzed into tokens. Matches WHOLE tokens with ~ only:
        name:~'Multi-' matches but name:~'Multi-Ag' does not, and exact
        (name:'Full Name') returns zero rows. Prefer name.raw.

        Ex: name:~'Exposure'
        """
    ),
    (
        "id",
        "String",
        "No",
        """
        Workflow definition ID (32 hex characters). Not unique in a result set:
        the endpoint returns multiple versions of the same definition.

        Ex: id:'2617e3fcf0804945ba6389328f3444f4'
        """
    ),
    (
        "enabled",
        "Boolean",
        "No",
        """
        Whether the definition is enabled. A disabled definition is refused by
        falcon_execute_workflow with a 412.

        Ex: enabled:true
        """
    ),
    (
        "trigger.type",
        "String",
        "No",
        """
        How the workflow starts. Verified values: 'On demand', 'Signal',
        'Scheduled'. The list is partial — these three covered 2973 of 3340
        definitions on the test tenant. Only 'On demand' and 'Scheduled' can be
        run by falcon_execute_workflow; 'Signal' is refused with a 412.

        Ex: trigger.type:'On demand'
        """
    ),
    (
        "version",
        "Number",
        "Yes",
        """
        Definition version. Numeric operators work.

        Ex: version:>1
        """
    ),
    (
        "last_modified_timestamp",
        "Timestamp",
        "Yes",
        """
        When the definition was last changed. Range and relative dates work.

        Ex: last_modified_timestamp:>'now-30d'
        """
    ),
    (
        "description",
        "String",
        "Yes",
        """
        Definition description, analyzed. Use ~ for token matching.

        Ex: description:~'containment'
        """
    ),
    (
        "mock_activities",
        "Boolean",
        "No",
        """
        Whether the definition has mocked activities. Sparse — set on only 419
        of 3340 definitions on the test tenant, so false does not mean "all the
        rest".

        Ex: mock_activities:true
        """
    ),
]

SEARCH_WORKFLOW_EXECUTIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "ui_status",
        "String",
        "No",
        """
        Execution status as displayed, and the field to filter status on. Values:
        'Completed', 'Failed', 'In progress', 'Action required'. This matches the
        `status` value in the response entity. 'Action required' means the run is
        waiting on a human and will not finish on its own.

        Ex: ui_status:'Completed'
        """
    ),
    (
        "status",
        "String",
        "No",
        """
        Execution status in the API's INTERNAL vocabulary, which differs from
        what the response shows: 'Succeeded', 'Failed', 'In progress',
        'Canceled'. An execution the response reports as 'Completed' matches
        status:'Succeeded', not status:'Completed'. Use ui_status unless you
        specifically need 'Canceled', which ui_status has no equivalent for.

        Ex: status:'Canceled'
        """
    ),
    (
        "id",
        "String",
        "No",
        """
        Execution ID. The response entity calls this `execution_id`, which is
        rejected as a filter field with a 400.

        Ex: id:'0e6a7a46545b926f3dff9fd2dab82fb3'
        """
    ),
    (
        "definition_id",
        "String",
        "No",
        """
        ID of the workflow definition that ran. The way to list one workflow's
        run history.

        Ex: definition_id:'2617e3fcf0804945ba6389328f3444f4'
        """
    ),
    (
        "definition_name",
        "String",
        "Yes",
        """
        Name of the workflow that ran, analyzed. Matches whole tokens with ~
        only — exact, wildcard and :* all return zero rows here.

        Ex: definition_name:~'Exposure'
        """
    ),
    (
        "started_timestamp",
        "Timestamp",
        "Yes",
        """
        When the run started. The response entity calls this `start_timestamp`,
        which is rejected as a filter field with a 400.

        Ex: started_timestamp:>'now-7d'
        """
    ),
    (
        "completed_timestamp",
        "Timestamp",
        "Yes",
        """
        When the run finished. The response entity calls this `end_timestamp`,
        which is rejected as a filter field with a 400.

        Ex: completed_timestamp:>'now-1d'
        """
    ),
    (
        "definition_version",
        "Number",
        "Yes",
        """
        Version of the definition that ran. Numeric operators work.

        Ex: definition_version:>1
        """
    ),
    (
        "test_mode",
        "Boolean",
        "No",
        """
        Whether the run was a test execution.

        Ex: test_mode:true
        """
    ),
    (
        "contains_mocks",
        "Boolean",
        "No",
        """
        Whether the run used mocked activity output.

        Ex: contains_mocks:true
        """
    ),
]

SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Workflow Definitions Guide

""" + FQL_BASE_OPERATORS + """

=== falcon_search_workflow_definitions FQL filter options ===

""" + generate_md_table(SEARCH_WORKFLOW_DEFINITIONS_FQL_FILTERS) + """

=== IMPORTANT NOTES ===
• Use name.raw, NOT name, to match a workflow by name. `name` is analyzed and
  matches whole tokens with ~ only, so name:'Full Workflow Name' returns ZERO
  rows even when that workflow exists. name.raw:'Full Workflow Name' returns it.
• An unknown filter field returns a 400 that names it, so a typo is loud. A
  known field with an unsupported operator returns an empty 200 instead, which
  is quiet — check the operator column above.
• Records are LARGE: a definition embeds its full action configuration,
  including whole Charlotte AI prompts and NG-SIEM queries. Narrow the filter
  rather than raising the limit.
• The same definition ID appears more than once, one row per version, so a
  result set can hold more rows than the limit you asked for. Read `version`
  and `enabled` to tell versions apart.
• Not every returned field is filterable: has_validation_errors and
  trigger.name are in the response but rejected as filter fields.
• sort uses DOT notation and a bare property defaults to descending. Verified to
  reorder: name, last_modified_timestamp, version, enabled, id. The pipe form
  (name|desc) is rejected with a 400. Nested fields such as trigger.type and
  name.raw are not sortable, because the accepted pattern allows no dot inside the
  property name.

=== COMMON FILTER EXAMPLES ===
• Workflows you can run on demand: enabled:true+trigger.type:'On demand'
• One workflow by exact name: name.raw:'Adversary Exposure Mitigation'
• Workflows whose name contains a word: name.raw:*'*Exposure*'
• Disabled workflows: enabled:false
• Recently changed: last_modified_timestamp:>'now-30d'
"""

SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Workflow Executions Guide

""" + FQL_BASE_OPERATORS + """

=== falcon_search_workflow_executions FQL filter options ===

""" + generate_md_table(SEARCH_WORKFLOW_EXECUTIONS_FQL_FILTERS) + """

=== RESPONSE FIELD vs FILTER FIELD ===
Several fields are named one way in the response and another way in a filter.
Filtering on the response name returns a 400.

""" + generate_md_table([
    ("Response field", "Filter field"),
    ("execution_id", "id"),
    ("start_timestamp", "started_timestamp"),
    ("end_timestamp", "completed_timestamp"),
    ("status", "ui_status (displayed values), or status (internal values)"),
]) + """

=== IMPORTANT NOTES ===
• Filter status via ui_status. The `status` field exists but uses a different
  vocabulary: an execution the response reports as 'Completed' is
  status:'Succeeded'. 'Failed' and 'In progress' are spelled the same in both,
  which is why the mismatch is easy to miss.
• An unknown filter field returns a 400 that names it. A known field with an
  unsupported operator returns an empty 200 instead.
• Records are LARGE: an execution embeds the entire triggering event, such as a
  full detection or case object. Narrow the filter rather than raising the limit.
• pagination.total saturates at 10000. A reported total of exactly 10000 means
  "at least 10000", not an exact count. Narrow the filter to get a real count.
• To look executions up directly by ID, without building a filter, use
  falcon_get_workflow_execution_results — it takes up to 500 IDs and offers
  skip_fields to trim oversized records.
• sort uses DOT notation and a bare property defaults to descending. Verified to
  reorder: started_timestamp, completed_timestamp, definition_id,
  definition_name, definition_version, ui_status, status, id. The pipe form
  (started_timestamp|desc) is rejected with a 400.
• PREFER DESCENDING on a long history. This endpoint hydrates matches by ID
  internally, and an execution that is still indexed but no longer retrievable
  makes the whole call fail with a 404 naming those IDs. Ascending order reaches
  the oldest records first, so it is the order most likely to hit them. Narrow by
  started_timestamp instead of paging back through everything.

=== COMMON FILTER EXAMPLES ===
• Runs that completed: ui_status:'Completed'
• Recent completed runs: ui_status:'Completed'+started_timestamp:>'now-7d'
• Runs waiting on a human: ui_status:'Action required'
• One workflow's run history: definition_id:'2617e3fcf0804945ba6389328f3444f4'
• Finished in the last day: completed_timestamp:>'now-1d'
"""
