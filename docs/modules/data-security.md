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

Search Data Security (DLP, formerly Data Protection) configuration entities.

Covers classifications, policies, content patterns, cloud applications,
enterprise accounts, web locations, local applications, local application
groups, sensitivity labels, and file types; a policy search also needs
platform_name. Consult the entity's FQL guide before constructing filter
expressions, e.g. falcon://data-security/policies/fql-guide (all ten are
listed in falcon://data-security/entities/model-guide). Returns full entity
details in a pagination envelope whose `pagination.total` is the API's count
of matches, or null when the API does not report one.

**Example prompts:**

- "What Data Security classifications are configured in my environment?"
- "List all enabled Windows Data Security policies"
- "Show me custom Data Security regex patterns in the PII category"

### `falcon_get_data_security_entities`

**Required scopes:** `Data Protection:read`

Retrieve full details of Data Security entities of one entity_type by ID.

Use when you already hold IDs, such as the ones one entity lists for the
entities it references; to find entities by their attributes, use
falcon_search_data_security_entities instead. See
falcon://data-security/entities/model-guide for how the entities reference
each other. Returns a list of the matching entities.

**Example prompts:**

- "Show me the full details of that classification"
- "Get the Data Security policy by ID so I can see its current config"

### `falcon_create_data_security_entity`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Data Protection:write`

Create a Data Security entity of the chosen entity_type.

Creates classifications, policies, content patterns, cloud applications,
enterprise accounts, web locations, local applications, local application
groups, and sensitivity labels; policies also need platform_name. Bodies
reference other entities by ID, so look those IDs up with search first and
never guess them. Returns a list containing the created entity.

**Example prompts:**

- "Create a new Data Security classification called 'PCI Card Numbers'"
- "Add a custom content pattern that detects internal project codes"

### `falcon_update_data_security_entity`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Data Protection:read`, `Data Protection:write`

Update an existing Data Security entity of the chosen entity_type.

Updates classifications, policies, content patterns, cloud applications,
enterprise accounts, web locations, local applications, and local
application groups; policies also need platform_name. Find the entity with
search, then send its "id" plus only the fields to change. Returns a list
containing the updated entity.

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
- **`falcon://data-security/agent/behavioral-guide`**: Behavioral guidance for working with Data Security entities: domain context and operational rules.
