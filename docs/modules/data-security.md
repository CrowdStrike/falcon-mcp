<!-- meta:title Data Security -->
<!-- meta:description Provides access to Data Security configuration data — classifications, policies, content patterns, cloud/local applications, enterprise accounts, web locations, sensitivity labels, and file types — so an LLM can inspect, create, and update Data Security rule definitions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Provides access to Data Security configuration data — classifications, policies, content patterns, cloud/local applications, enterprise accounts, web locations, sensitivity labels, and file types — so an LLM can inspect, create, and update Data Security rule definitions

## API Scopes

- `Data Protection:read`
- `Data Protection:write`

## Tools

### `falcon_search_data_security_entities`

**Required scopes:** `Data Protection:read`

Search for Data Security entities of the given entity_type.

A single generic search across all Data Security entity types. The
entity_type discriminator selects which collection is queried. Consult
the matching FQL guide resource (listed in
falcon://data-security/entities/model-guide) before constructing filter
expressions. Returns full entity details wrapped in a pagination envelope.

entity_type='policy' requires platform_name ('win' or 'mac').

Read falcon://data-security/agent/behavioral-guide for behavioral rules
and falcon://data-security/entities/model-guide for entity relationships.

Formatting rules (apply to all Data Security output):

- Protection mode emoji: blue circle = Enforce, yellow = Simulate, green = Monitor.
- Use "Off" for disabled/unset settings — never a red X emoji.
- Show entity NAMES, not raw UUIDs. If you only have IDs, say
  "<n> attached" and offer to expand rather than dumping UUIDs.
- Omit sections with no data.
- Listings: aligned columns (#, Name, Mode, CPs, Rules, Created).
- Single entity: header with name + mode circle, then labeled sections
  (ID, Platform, Status, Precedence, Description, Created/Modified,
  Host Groups, Inspection, Evidence, Justification).
- Drill-downs: ASCII tree (Policy → Classification → Content Patterns → Rules
  with egress channels).

**Example prompts:**

- "What Data Security classifications are configured in my environment?"
- "List all enabled Windows Data Security policies"
- "Show me custom Data Security regex patterns in the Financial category"

### `falcon_get_data_security_entities`

**Required scopes:** `Data Protection:read`

Retrieve full details of Data Security entities by their IDs.

A single generic get-by-IDs across all Data Security entity types.
Always re-fetch by ID rather than relying on earlier search results,
which may be stale. See falcon://data-security/entities/model-guide for
entity relationships.

Formatting rules (apply to all Data Security output):

- Protection mode emoji: blue circle = Enforce, yellow = Simulate, green = Monitor.
- Use "Off" for disabled/unset settings — never a red X emoji.
- Show entity NAMES, not raw UUIDs. If you only have IDs, say
  "<n> attached" and offer to expand rather than dumping UUIDs.
- Omit sections with no data.
- Single entity: header with name + mode circle, then labeled sections
  (ID, Platform, Status, Precedence, Description, Created/Modified,
  Host Groups, Inspection, Evidence, Justification).
- Drill-downs: ASCII tree (Policy → Classification → Content Patterns → Rules
  with egress channels).

**Example prompts:**

- "Show me the full details of that classification"
- "Get the Data Security policy by ID so I can see its current config"

### `falcon_create_data_security_entity`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Data Protection:read`, `Data Protection:write`

Create a new Data Security entity of the given entity_type.

A single generic create across all writable Data Security entity types.
Bodies reference other entities (Classifications, Content Patterns, Web
Locations, File Types, Sensitivity Labels) by ID — obtain those IDs via the
search/get tools first (never guess them). entity_type='policy' requires
platform_name. See falcon://data-security/entities/model-guide.

**Example prompts:**

- "Create a new Data Security classification called 'PCI Card Numbers'"
- "Add a custom content pattern that detects internal project codes"

### `falcon_update_data_security_entity`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Data Protection:read`, `Data Protection:write`

Update an existing Data Security entity of the given entity_type.

A single generic update across all updatable Data Security entity types.
Retrieve the current entity via search/get, then submit the changed fields
with the entity "id" included in the body. entity_type='policy' requires
platform_name. See falcon://data-security/entities/model-guide.

**Example prompts:**

- "Enable that Data Security policy"
- "Change the classification's protection mode to enforce"

## Resources

- **`falcon://data-security/classifications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='classification'`.
- **`falcon://data-security/policies/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='policy'`.
- **`falcon://data-security/content-patterns/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='content_pattern'`.
- **`falcon://data-security/cloud-applications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='cloud_application'`.
- **`falcon://data-security/enterprise-accounts/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='enterprise_account'`.
- **`falcon://data-security/web-locations/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='web_location'`.
- **`falcon://data-security/local-applications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='local_application'`.
- **`falcon://data-security/local-application-groups/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='local_application_group'`.
- **`falcon://data-security/sensitivity-labels/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='sensitivity_label'`.
- **`falcon://data-security/file-types/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_data_security_entities` tool with `entity_type='file_type'`.
- **`falcon://data-security/entities/model-guide`**: Data Security entity relationship model. Shows how Policies reference Classifications, which combine Content Patterns, File Types, Web Origins, Sensitivity Labels, and Rules.
- **`falcon://data-security/agent/behavioral-guide`**: Behavioral guidance for working with Data Security entities: domain context, operational rules, mandatory privacy/redaction requirements, and data freshness rules.
