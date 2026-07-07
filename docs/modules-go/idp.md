# Idp

Investigate CrowdStrike Falcon Identity Protection entities: entity details, timelines, relationships, and risk assessments.

## Tools

### `falcon_idp_investigate_entity`

**Type:** read-only

Investigate one or more Identity Protection entities by ID, name, email, IP address, or domain. Use this to look up entity details, activity timelines, relationship graphs, and risk assessments. At least one identifier must be supplied; multiple identifiers are combined with AND logic (email and IP cannot be combined — email takes precedence). Returns a structured response with an investigation_summary, resolved entity IDs, and results keyed by each requested investigation type.

