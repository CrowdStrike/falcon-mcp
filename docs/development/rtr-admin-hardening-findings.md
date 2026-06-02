# RTR Admin Hardening Findings

This sidecar captures planning lessons and follow-up findings from the RTR Admin
module hardening pass. It is intentionally separate from generated module docs
and from private agent metadata.

## Module Planning Lessons from PR #410

Use this note before planning new Falcon MCP modules or expanding sensitive
module surfaces.

### Start with the Codebase Shape

Before drafting tools from FalconPy operations, inspect nearby modules and mirror
the local grammar:

- `register_tools()` method names should match registered tool names.
- Search tools should generally return full records, not raw IDs.
- FQL guidance should live in resource guides when it is more than a short field
  description.
- Docs, generated module metadata, API scope mappings, registry support, unit
  tests, and integration tests are part of the module slice.

For RTR-style work, inspect `falcon_mcp/modules/rtr.py` and similar
search/detail modules before adding new tools.

### Treat Tool Count as API Design

Do not add a separate MCP tool just because Falcon exposes a separate operation.
Add a tool only when it gives the operator or model a distinct workflow.

For query -> get APIs:

- Prefer one `search_*` tool that queries IDs and returns full details.
- If known IDs can be expressed through FQL, document `id:` filters instead of
  adding redundant `get_*_details` tools.
- Keep separate `get_*` tools only when they are established in comparable
  modules or provide a meaningfully different input/output contract.

PR #410 cleanup removed three redundant `get_*_details` tools because the same
lookup could be handled by `id:` filters through search.

### Plan from the Operator Workflow

For sensitive or high-impact modules, plan the workflow before coding endpoints:

1. Inventory or search the relevant assets.
2. Classify the intended action locally when possible.
3. Preview exact target, payload, risk, and approval requirements.
4. Execute only the smallest safe first slice.
5. Poll or retrieve status separately.

Keep upload, update, delete, batch, and content-retrieval surfaces out of the
first slice unless the requested workflow requires them.

### Classify Risk Before Encoding Policy

For command execution modules, enumerate the command set before implementation:

- read-only commands
- evidence collection commands
- sensitive collection commands
- high-impact or destructive commands
- commands blocked until later review
- unknown commands

Approval hashes should key on stable execution material. Avoid including
display-only or drift-prone fields, such as hostnames, if they can break an
otherwise valid approval phrase.

### Review Checklist

Before opening or updating a module PR, verify:

- Tool names, method names, docs, and tests use the same naming pattern.
- Search tools return full details and use existing query -> get helpers.
- Redundant get-by-ID tools were not added when FQL `id:` filters work.
- The API scope map covers every Falcon operation used.
- Resources describe FQL fields and examples without bloating tool parameter
  descriptions.
- Mutating or execution tools have explicit MCP annotations.
- Execution tools verify `base_command` matches the first token of
  `command_string`.
- Workflow helpers such as `run_*_and_wait` must reuse the same execution policy
  gate as the lower-level execution tool, then poll the documented status
  operation. Do not let convenience helpers bypass approval or target review.
- Treat content retrieval tools as sensitive even when they are read-only API
  calls. Put-file contents may expose scripts, binaries, or operational payloads.
- Cross-check command policy names against the FalconPy docs/source when editing
  classifiers. For example, keep documented `unmount` behavior from falling into
  the unknown bucket just because older notes used `umount`.
- Spend CodeRabbit after edits and local validation settle. If full review hits
  file-count or rate limits, run the smallest meaningful `--dir` scopes and
  record any incomplete scope explicitly.
- Tests cover registered tool count, API call shape, ID lookup behavior, local
  validation, safety policy, and any approval phrase logic.
- The PR summary states what was intentionally left out of the first slice.

## Follow-Up Backlog from RTR Admin Hardening

Captured 2026-06-02 during the RTR Admin module hardening pass. These were found
while reviewing the branch, but were intentionally not fixed in the RTR Admin PR
because they are pre-existing, out of scope, tooling-only, or already identified
as false positives.

### Existing Detections Resource Issues

CodeRabbit flagged these during a scoped `falcon_mcp` review, but the files were
not changed by the RTR Admin branch. Handle them in a separate detections/docs
cleanup PR.

- `falcon_mcp/resources/detections.py`: FQL examples mix `+` and `,` without
  explicit grouping. Confirm Falcon FQL precedence and update examples such as
  the name-based high/critical filters and product combinations so the intended
  AND/OR behavior is unambiguous.
- `falcon_mcp/resources/detections.py`: Critical severity guidance says
  `severity:>=80`, but the "Unassigned critical alerts from last 24 hours"
  numeric example uses `severity:>=90`. Decide whether the example means all
  critical detections or only the highest critical band, then align the wording
  and threshold.

### Existing Test and Repo Health Warnings

These warnings are not caused by RTR Admin directly, but they showed up in the
full validation pass and should be reviewed when we do repo-health cleanup.

- `tests/common/test_api_scopes.py::test_no_unused_scope_mappings` warns that
  `entities_classification_get_v2`, `entities_content_pattern_get`, and
  `entities_policy_get_v2` may be unused. Audit the scope-extraction test versus
  `falcon_mcp/modules/data_protection.py` before removing anything; the
  operations appear to be used by the Data Protection module.
- `falcon_mcp/modules/idp.py` still uses `datetime.utcnow()` in timestamp
  payloads. Replace with timezone-aware UTC values and update any tests or
  expected output that assume naive timestamps.
- `tests/test_tools_list_output_schema.py::test_tools_list_payload_within_budget`
  warns that the full `tools/list` payload exceeds the 120,000 byte soft budget.
  Review schema verbosity, default module selection, and client guidance before
  hiding or relaxing the warning.

### CodeRabbit and Review Tooling Notes

- Full uncommitted CodeRabbit review failed because the branch diff was over
  CodeRabbit's 150-file limit. Use focused `--dir` reviews, compare against a
  closer base, or commit/split work before asking for a broad review.
- Final scoped CodeRabbit reviews were run for `falcon_mcp`, `scripts`, `tests`,
  and `docs-site/src/content/docs/modules`; each completed with 0 findings after
  the hardening fixes.
- CodeRabbit reported EOF-newline issues for `rtr.md` and `rtr-admin.md`, but a
  byte-level check showed both files already ended with newline byte `10`. Treat
  those specific findings as false positives unless they reappear after a fresh
  regeneration.
