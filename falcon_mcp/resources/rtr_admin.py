"""
Contains RTR Admin resources.
"""

from falcon_mcp.common.utils import generate_md_table

SCRIPT_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Script ID."),
    ("name", "String", "Script name."),
    ("description", "String", "Script description."),
    ("platform", "String", "Script platform such as windows, mac, or linux."),
    ("permission_type", "String", "Script permission level such as private, group, or public."),
    ("created_at", "Timestamp", "When the script was created."),
    ("updated_at", "Timestamp", "When the script was last updated."),
]

FALCON_SCRIPT_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Falcon script ID."),
    ("name", "String", "Falcon script name."),
    ("description", "String", "Falcon script description."),
    ("platform", "String", "Script platform such as windows, mac, or linux."),
]

PUT_FILE_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    ("id", "String", "Put-file ID."),
    ("name", "String", "Put-file name."),
    ("description", "String", "Put-file description."),
    ("created_at", "Timestamp", "When the put-file was created."),
    ("updated_at", "Timestamp", "When the put-file was last updated."),
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

# Look up known script IDs
id:['<id1>','<id2>']

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
platform:'windows'

# Falcon scripts with collect in the name
name:~'collect'

# Look up known script IDs
id:['<id1>','<id2>']

=== falcon_search_rtr_falcon_scripts FQL filter available fields ===

"""
    + generate_md_table(FALCON_SCRIPT_FQL_FILTERS)
)

SEARCH_RTR_PUT_FILES_FQL_DOCUMENTATION = (
    """Falcon Query Language (FQL) - Search RTR Put-Files Guide

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== COMMON EXAMPLES ===

# Put-files with collector in the name
name:~'collector'

# Put-files created after a date
created_at:>'2026-01-01T00:00:00Z'

# Look up known put-file IDs
id:['<id1>','<id2>']

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
   - When you already have IDs, filter the matching search tool with the `id`
     field, such as `id:['<id1>','<id2>']`.

2. Classify the intended command locally.
   - Use `falcon_classify_rtr_admin_command` before execution planning.
   - This does not call Falcon.
   - Classification is enforced before execution. High-impact commands require
     an explicit operator approval phrase before any Falcon call is made.

3. Preview the exact payload.
   - Use `falcon_preview_rtr_admin_command` before live execution.
   - Provide `reason`, `ticket`, and `expected_effect` whenever possible.
   - Review `payload_preview`, `classification`, `missing_context`,
     `approval_gate`, and any command-specific guidance.
   - If `approval_gate.approval_required` is true, ask the operator to approve
     the exact target, command, expected effect, and approval hash before
     re-submitting with `operator_approval`.

4. Execute only after target and effect review.
   - Use `falcon_execute_rtr_admin_command` for one host/session.
   - This execution tool is marked destructive because submitted commands can
     change or disrupt endpoints depending on the command string.
   - High-impact commands such as `runscript`, `rm`, `put`, `kill`, restart or
     shutdown actions, registry writes, and memory dumps return an
     approval-required response unless `operator_approval` matches the exact
     phrase for that payload.

5. Poll output.
   - Use `falcon_check_rtr_admin_command_status` with the returned
     `cloud_request_id`.
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

- This module does not upload, update, delete, or retrieve contents for scripts
  or put-files in the first implementation slice.
- Do not use automated live tests for endpoint-changing commands. Tests should
  stay mocked, smoke-only, or read-only unless the operator chooses a specific
  PC for that run.
- Keep single-host `persist` false unless the operator explicitly wants offline
  execution when a host returns to service.
- Batch admin execution is intentionally out of scope for this first module
  slice.
- Do not place RTR controller actions such as status polling, `get`, `put`, or
  session cleanup inside raw script bodies. Use the separate MCP tools for those
  steps.
"""

RTR_ADMIN_RUNSCRIPT_RAW_GUIDE = """RTR Admin runscript raw command guide

Use this guide when building command strings for
`falcon_execute_rtr_admin_command` with `base_command="runscript"`.

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
- Use `falcon_check_rtr_admin_command_status` to poll command output chunks.
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
