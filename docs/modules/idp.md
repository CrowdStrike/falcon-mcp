<!-- meta:title Identity Protection -->
<!-- meta:description Accessing and managing CrowdStrike Falcon Identity Protection capabilities -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Accessing and managing CrowdStrike Falcon Identity Protection capabilities

## API Scopes

- `Identity Protection Assessment:read`
- `Identity Protection Detections:read`
- `Identity Protection Entities:read`
- `Identity Protection Timeline:read`
- `Identity Protection GraphQL:write`

## Tools

### `falcon_idp_investigate_entity`

**Required scopes:** `Identity Protection Assessment:read`, `Identity Protection Detections:read`, `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection GraphQL:write`

Investigate one or more Identity Protection entities by ID, name, email, IP, or domain.

Use this to look up entity details, activity timelines, relationship graphs, and risk
assessments; at least one identifier must be supplied, and multiple identifiers are
combined with AND logic (email and IP cannot be combined — email takes precedence).
Returns a structured response with an investigation_summary, resolved entity IDs,
and results keyed by each requested investigation type.

**Example prompts:**

- "Investigate user john.doe@company.com and show their risk assessment"
- "Look up entity Administrator in domain CORP.LOCAL"
