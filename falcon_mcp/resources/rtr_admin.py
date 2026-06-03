"""
Contains RTR Admin resources.
"""

from falcon_mcp.common.utils import generate_md_table

SCRIPT_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Script ID."),
    ("name", "String", "Script name."),
    ("description", "String", "Script description."),
    ("platform", "String", "Custom script platform such as windows, mac, or linux."),
    ("permission_type", "String", "Script permission level such as private, group, or public."),
    ("created_timestamp", "Timestamp", "When the script was created."),
    ("modified_timestamp", "Timestamp", "When the script was last modified."),
]

FALCON_SCRIPT_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Falcon script ID."),
    ("name", "String", "Falcon script name."),
    ("description", "String", "Falcon script description."),
    ("platform", "String", "Falcon script platform such as Windows, Mac, or Linux."),
]

PUT_FILE_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Put-file ID."),
    ("name", "String", "Put-file name."),
    ("description", "String", "Put-file description."),
    ("created_timestamp", "Timestamp", "When the put-file was created."),
    ("modified_timestamp", "Timestamp", "When the put-file was last modified."),
]

SEARCH_RTR_ADMIN_SCRIPTS_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search RTR Custom Scripts Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== COMMON EXAMPLES ===

# Windows custom scripts
platform:'windows'

# Private custom scripts
permission_type:'private'

# Scripts with triage in the name
name:~'triage'

# Scripts created after a date
created_timestamp:>'2026-01-01T00:00:00Z'

NOTE: Custom script ID filters can be API-shape dependent. Use
name/platform/time filters and compare returned IDs manually when exact lookup
matters.

NOTE: Search results can include full script content. Treat responses as
sensitive operational material and avoid copying script bodies into notes unless
content review is explicitly required.

=== falcon_search_rtr_admin_scripts FQL filter available fields ===

"""
    + generate_md_table(SCRIPT_FQL_FILTERS)
)

SEARCH_RTR_FALCON_SCRIPTS_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search RTR Falcon Scripts Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== COMMON EXAMPLES ===

# Windows Falcon scripts
platform:'Windows'

# Falcon scripts with collect in the name
name:~'collect'

# Look up known script IDs
id:['<id1>','<id2>']

NOTE: Falcon script platform casing differs from custom scripts. Use
platform:'Windows' for CrowdStrike-provided Falcon scripts, but
platform:'windows' for custom scripts.

NOTE: Search results can include full script content. Treat responses as
sensitive operational material and avoid copying script bodies into notes unless
content review is explicitly required.

=== falcon_search_rtr_falcon_scripts FQL filter available fields ===

"""
    + generate_md_table(FALCON_SCRIPT_FQL_FILTERS)
)

SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search RTR Put-Files Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== COMMON EXAMPLES ===

# Put-file by exact name
name:'approved-collector.ps1'

# Put-files created after a date
created_timestamp:>'2026-01-01T00:00:00Z'

NOTE: Put-file ID filters can be API-shape dependent. Use name/time filters and
compare returned IDs manually before using falcon_get_rtr_put_file_contents
with a selected put-file ID.

NOTE: Exact put-file name filters are more reliable than contains or wildcard
name filters in some Falcon API responses. If exact name is not known, use a
time-bounded inventory search and compare returned names client-side.

=== falcon_search_rtr_put_files FQL filter available fields ===

"""
    + generate_md_table(PUT_FILE_FQL_FILTERS)
)

RTR_ADMIN_TOOL_USE_GUIDE = """RTR Admin Tool Use Guide

This guide explains how to use the RTR Admin module tools. RTR Admin can affect
live endpoints. Use standard RTR for read-only host triage and use this module
only when an admin command, script execution, or put-file workflow is actually
needed.

=== Recommended workflow ===

1. Review available reusable material.
   - Use `falcon_search_rtr_admin_scripts` for custom cloud scripts.
   - Use `falcon_search_rtr_falcon_scripts` for CrowdStrike-provided scripts.
   - Use `falcon_search_rtr_put_files` for put-file inventory.
   - Treat script inventory responses as sensitive because they can include
     full custom or Falcon script content.
   - Use `falcon_get_rtr_put_file_contents` only after selecting a specific
     put-file ID. Treat returned content as potentially sensitive operational
     material.
   - Do not rely on put-file inventory `file_type` to predict content exposure.
     Inventory can report `file_type: binary` while the content retrieval
     endpoint returns text script content.
   - Falcon script ID filters are supported. Custom script and put-file ID
     filters may be API-dependent; prefer broader filters and compare returned
     IDs manually before acting on a selected record.
   - For put-files, prefer exact `name:'...'` filters when the name is known.
     Contains or wildcard name filters may return no rows; use time-bounded
     inventory and compare names client-side when exact name is not known.
   - Platform casing differs: custom scripts use values such as
     `platform:'windows'`, while Falcon scripts use values such as
     `platform:'Windows'`.

2. Classify the intended command locally.
   - Use `falcon_classify_rtr_admin_command` before execution planning.
   - This does not call Falcon.
   - Classification is enforced before execution. High-impact commands require
     an explicit operator approval phrase before any Falcon call is made.

3. Preview the exact payload.
   - Use `falcon_preview_rtr_admin_command` before live execution.
   - Provide `reason`, `ticket`, and `expected_effect` whenever possible.
   - Confirm `base_command` matches the first token of `command_string`;
     mismatches are rejected locally before any Falcon call.
   - Review `payload_preview`, `classification`, `missing_context`,
     `approval_gate`, and any command-specific guidance.
   - For `reg query`, keep the query shape minimal. Falcon can reject extra
     unquoted arguments with HTTP 400.
   - If `approval_gate.approval_required` is true, ask the operator to approve
     the exact target, command, expected effect, and approval hash before
     re-submitting with `operator_approval`.
   - High-impact approval is only ready when `device_id`, `reason`, `ticket`,
     and `expected_effect` are present. The approval phrase binds the target,
     payload, and audit context.

4. Execute only after target and effect review.
   - Use `falcon_execute_rtr_admin_command` for one host/session.
   - Use `falcon_run_rtr_admin_command_and_wait` when you want a focused
     single-host command to submit once and return combined stdout/stderr after
     polling. It uses the same classification and approval gate as the execution
     tool.
   - This execution tool is marked destructive because submitted commands can
     change or disrupt endpoints depending on the command string.
   - High-impact commands such as `runscript`, `rm`, `put`, `kill`, restart or
     shutdown actions, registry writes, and memory dumps return an
     approval-required response unless `operator_approval` matches the exact
     phrase for that payload.
   - For directory cleanup, use `rm <directory> -force` and verify stderr/stdout
     before assuming deletion succeeded.

5. Poll output.
   - Use `falcon_check_rtr_admin_command_status` with the returned
     `cloud_request_id`.
   - The wait helper handles this polling for simple workflows; manual polling
     remains useful for long-running commands or when the caller needs each
     status chunk.
   - Start with `sequence_id=0`; if the status response includes a
     `sequence_id`, use that returned sequence_id on the next poll.

=== Raw runscript workflow ===

- Use `base_command="runscript"`.
- Use `falcon://rtr-admin/commands/runscript-guide` for quoting and
  controller notes.
- Treat `runscript -Raw` as submit-and-poll execution, not an interactive
  terminal.
- Prefer `runscript -CloudFile="ScriptName" -CommandLine="<arguments>"` for
  reusable or multiline scripts.

=== Boundaries and disclaimers ===

- This module retrieves put-file contents by explicit ID but does not upload,
  update, or delete script / put-file records.
- Do not use automated live tests for endpoint-changing commands. Tests should
  stay mocked, smoke-only, or read-only unless the operator chooses a specific
  PC for that run.
- Keep single-host `persist` false unless the operator explicitly wants offline
  execution when a host returns to service.
- Batch admin execution is intentionally out of scope for this module slice.
- If audit/session searches return 403 during an RTR Admin investigation,
  verify the API client has `real-time-response-audit:read`.
- Do not place RTR controller actions such as status polling, `get`, `put`, or
  session cleanup inside raw script bodies. Use the separate MCP tools for those
  steps.
"""

RTR_ADMIN_RUNSCRIPT_RAW_GUIDE = """RTR Admin runscript raw command guide

Use this guide when building command strings for
`falcon_execute_rtr_admin_command` or `falcon_run_rtr_admin_command_and_wait`
with `base_command="runscript"`.

CORE SHAPE:
- base_command: runscript
- command_string: runscript -Raw=```<target-side script>```

EXAMPLES:
- Windows process list: runscript -Raw=```Get-Process```
- Windows command wrapper: runscript -Raw=```cmd /c whoami && hostname```
- Linux/macOS shell: runscript -Raw=```/bin/sh -c 'id; hostname'```

CLOUD SCRIPT SHAPE:
- command_string: runscript -CloudFile="ScriptName"
- with arguments: runscript -CloudFile="ScriptName" -CommandLine="<arguments>"

IMPORTANT CONTROLLER NOTES:
- `runscript -Raw` is not an interactive terminal. Each tool call submits one
  RTR Admin command and returns a `cloud_request_id`.
- Use `falcon_check_rtr_admin_command_status` to poll command output chunks, or
  use `falcon_run_rtr_admin_command_and_wait` for focused commands where direct
  stdout/stderr output is preferred.
- Do not put RTR controller commands such as `get`, `put`, `cd`, or status
  polling inside the raw script. Those are RTR commands, not target-side shell
  commands.
- If the target-side script needs to coordinate multiple steps, write explicit
  stdout markers or output files, then use separate RTR commands to retrieve or
  inspect results.
- Raw scripts are quoting-sensitive. Prefer short one-liners or approved cloud
  scripts for long multiline logic.
- Avoid unescaped triple backticks inside the script body because they delimit
  the raw payload.
- Prefer `-CloudFile` plus `-CommandLine` for reusable or complex scripts.
- Keep single-host `persist` false unless the operator explicitly wants offline
  execution when the host returns to service.
"""

RTR_ADMIN_APPROVAL_PACKET_TEMPLATE = """RTR Admin Approval Packet Template

Use this template before running high-impact RTR Admin commands. The operator
must review the exact target, command, expected endpoint effect, and approval
hash before the execution tool is called with `operator_approval`.

=== Target ===
- Hostname:
- Device ID:
- Session ID:
- Ticket / case:

=== Command ===
- Base command:
- Command string:
- Persist when offline: false
- Classification:
- Risk:

=== Rationale ===
- Reason:
- Expected endpoint effect:
- Evidence or inventory reviewed:

=== Approval Gate ===
- Approval required:
- Approval hash:
- Exact approval phrase:

=== Execution and Follow-up ===
- Execution tool: falcon_execute_rtr_admin_command
- Wait helper: falcon_run_rtr_admin_command_and_wait
- Status tool: falcon_check_rtr_admin_command_status
- Cloud request ID:
- Completion / stdout / stderr summary:
"""
