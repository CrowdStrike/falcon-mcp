<!-- meta:title Zero Trust Assessment -->
<!-- meta:description Retrieving Zero Trust Assessment posture scores and sensor and OS hardening signals for hosts -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Retrieving Zero Trust Assessment posture scores and sensor and OS hardening signals for hosts

> [!NOTE]
> This module is not available on CrowdStrike's hosted Falcon MCP; it is only available when self-hosting this server. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

## API Scopes

- `Zero Trust Assessment:read`

## Tools

### `falcon_search_zta_assessments`

**Required scopes:** `Zero Trust Assessment:read`

Search Zero Trust Assessment scores and return full assessment details.

Use this to rank hosts by security posture: pass `max_score` to list the weakest
hosts, `min_score` to list the strongest. Score is the only attribute this tool can
select on, so start from `falcon_get_zta_assessments` when you already have an agent
ID (AID) and from `falcon_search_hosts` when you have a hostname.
Returns each host's Zero Trust score with its full sensor and OS hardening signals,
in the standard pagination envelope; feed `pagination.next` back as `after`.

Results name hosts only by AID, so pair this with `falcon_search_hosts` to report
hostnames. Each record carries a long signal list, so raise `limit` deliberately.

**Example prompts:**

- "Which hosts have the weakest Zero Trust posture?"
- "Show me hosts scoring below 40 on Zero Trust Assessment"

### `falcon_get_zta_assessments`

**Required scopes:** `Zero Trust Assessment:read`

Get Zero Trust Assessment details for specific hosts by agent ID (AID).

Use this when you already hold an AID: a detection reports one as its `device_id`, and
`falcon_search_hosts` resolves a hostname to one. No Zero Trust tool accepts a
hostname, so resolve the name with `falcon_search_hosts` first.
Returns `results` holding one record per assessed host — the Zero Trust score plus the
full sensor and OS hardening signals — and `not_found` listing the AIDs with no
assessment.

`not_found` is always present, even when empty, because the API reports an unknown or
never-assessed AID by omitting its record from an otherwise successful response.

**Example prompts:**

- "What is the security posture of host WEB-01?"
- "Show the Zero Trust hardening signals for this agent ID"

### `falcon_get_zta_audit`

**Required scopes:** `Zero Trust Assessment:read`

Get the tenant-wide Zero Trust Assessment summary.

Use this to answer how the whole tenant scores, rather than which hosts score badly —
it is a single CID-level rollup and carries no per-host data, so reach for
`falcon_search_zta_assessments` when you need individual hosts.
Returns one record with the assessed host count and average Zero Trust score for the
tenant, broken down by platform.

**Example prompts:**

- "What is our overall Zero Trust score?"
- "Break down our Zero Trust posture by platform"
