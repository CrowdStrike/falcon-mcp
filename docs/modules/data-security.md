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
platform_name. Read falcon://data-security/agent/behavioral-guide once first:
it holds the operating rules. Search narrowly: filter on what the user named
and keep limit small; for a listing, show the first page with its total and
offer the next. Consult the entity's FQL guide before composing a filter,
e.g. falcon://data-security/policies/fql-guide.

Returns a pagination envelope: `pagination.total` is the API's count of
matches (null when it reports none) and `pagination.next` the offset of the
next page (null on the last); `_warnings` lists per-entity errors the API
reported. Policy and classification results are summary records unless you
pass fields (a `hint` names the summary fields); other types return full
records. Large inline images (e.g. a policy's euj_dialog_box_logo) come back
as an "<elided …>" placeholder. With child CIDs, results span every CID (each
record's cid says which); policy precedence and the default policy are per
CID, so group policies by cid. Rule ad_users / ad_groups are AD SIDs: show
them as-is, names cannot be resolved.

**Example prompts:**

- "What Data Security classifications are configured in my environment?"
- "List all enabled Windows Data Security policies"
- "Show me custom Data Security regex patterns in the PII category"

### `falcon_get_data_security_entities`

**Required scopes:** `Data Protection:read`

Retrieve full Data Security entities of one entity_type by ID.

Use it for IDs you already hold, e.g. the IDs another entity references
(relationships: falcon://data-security/entities/model-guide). To find entities
by attribute, use falcon_search_data_security_entities. Returns a list of the
matching entities, or `{results, _warnings}` when some IDs failed. Large
inline images (e.g. a policy's euj_dialog_box_logo) come back as an
"<elided …>" placeholder. Rule ad_users / ad_groups are AD SIDs: show them
as-is, names cannot be resolved.

**Example prompts:**

- "Show me the full details of that classification"
- "Get the Data Security policy by ID so I can see its current config"

### `falcon_get_data_security_entity_schema`

Return the write-body guide of one or more Data Security entity types.

Each guide gives the field names, types, allowed values, nesting and required
fields. Covers every type except file_type, which is read-only. Reads embedded
docs only, no API call. Call it before building a create or update body,
batching every type you will write (e.g. ["classification", "policy"]); never
guess field names. Returns one body guide per entity type plus a usage hint.

**Example prompts:**

- "What fields does a Data Security classification body take?"
- "Show me the body format for creating a policy and a content pattern"

### `falcon_create_data_security_entity`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Data Protection:write`

Create a Data Security entity of the chosen entity_type.

Creates classifications, policies, content patterns, cloud applications,
enterprise accounts, web locations, local applications, local application
groups, and sensitivity labels; policies also need platform_name. Build the
body from falcon_get_data_security_entity_schema and follow
falcon://data-security/agent/behavioral-guide (ask rather than assume a
setting). Returns a list with the created entity, `{results, _warnings}` when
the API also reported errors, or an acknowledgement {status, entity_type,
message} when it accepted the write but returned no entity (do not retry). If
the API rejects the body, the error includes its body_guide.

Rules (the API accepts violations silently):

- Create bottom-up, referencing only real IDs from search/get, never guessed:
  cloud application / enterprise account → web location → classification →
  policy.
- Enforcement is only on the classification: rule response_action applies
  only when protection_mode is 'enforce' ('simulate' runs silently, 'monitor'
  only observes). Policy settings control inspection.
- "Upload TO X" is a rule destination (web_locations, scope 'specific');
  "data FROM X" is a classification origin (web_sources). Ask when unclear.
- A policy's classifications are ordered: the first match with a rule
  covering the egress wins; classifications without detection criteria go last.
- One policy per host per platform (they never stack): extend the hosts'
  existing policy. Windows and macOS each need their own.
- A classification has no effect until a policy references it.

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
application groups; policies also need platform_name. Send the entity's "id"
(from search/get) plus only the fields to change; its body guide
(falcon_get_data_security_entity_schema) says which fields are updatable.
Returns a list with the updated entity, `{results, _warnings}` when the API
also reported errors, or an acknowledgement {status, entity_type, id, message}
when it accepted the write but returned no entity. If the API rejects the
body, the error includes its body_guide.

Rules (the API accepts violations silently):

- A list you send replaces the stored list: to add or remove an item (e.g. a
  policy's classification), get the entity and send its full list with your
  change.
- The rules of falcon_create_data_security_entity apply (IDs and SIDs,
  destinations vs origins, classification order, enforcement).

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
- **`falcon://data-security/classifications/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='classification'`.
- **`falcon://data-security/policies/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='policy'`.
- **`falcon://data-security/content-patterns/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='content_pattern'`.
- **`falcon://data-security/cloud-applications/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='cloud_application'`.
- **`falcon://data-security/enterprise-accounts/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='enterprise_account'`.
- **`falcon://data-security/web-locations/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='web_location'`.
- **`falcon://data-security/local-applications/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='local_application'`.
- **`falcon://data-security/local-application-groups/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` and `falcon_update_data_security_entity` tools with `entity_type='local_application_group'`.
- **`falcon://data-security/sensitivity-labels/body-guide`**: Contains the guide for the `body` param of the `falcon_create_data_security_entity` tool with `entity_type='sensitivity_label'`.
- **`falcon://data-security/entities/model-guide`**: Data Security entity relationship model. Policies reference ordered Classifications, which combine detection criteria (Content Patterns, File Types, Sensitivity Labels, Web Origins, File Paths), a protection mode, and nested Rules (channels, Web Destinations, Local Application Groups, user scope, response action). Also covers the supporting Cloud Applications, Enterprise Accounts, Web Locations, and Local Applications.
- **`falcon://data-security/agent/behavioral-guide`**: Behavioral guidance for working with Data Security entities: domain context and operational rules.
