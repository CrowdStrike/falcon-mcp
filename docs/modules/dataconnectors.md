<!-- meta:title Data Connectors -->
<!-- meta:description Data Connectors module for CrowdStrike Falcon Next-Gen SIEM. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:11 -->

Data Connectors module for CrowdStrike Falcon Next-Gen SIEM — discover available connector
types, search and manage active data connections, create and delete connections, retrieve and
regenerate ingest tokens, and manage pull-based connector configurations.

## API Scopes

- `ngsiem-data-connections:read`
- `ngsiem-data-connections:write`

## Tools

### `falcon_search_data_connectors`

**Required scopes:** `ngsiem-data-connections:read`

List available data connector types from the Falcon catalog.

Returns the catalog of connector types (e.g. Okta, AWS CloudTrail, Microsoft Entra ID).
Each connector includes: id, name, description, vendor_name, vendor_product_name, type
(PUSH/PULL), parsers, and subscription.

Use this to discover what connectors are available before creating a connection, or to
find which connector provides data from a specific vendor.

**Example prompts:**

- "What data connectors are available?"
- "Show me all AWS connectors"
- "Find the connector for Okta identity data"

### `falcon_search_data_connections`

**Required scopes:** `ngsiem-data-connections:read`

Search active data connections and return full details including status.

Use this to find deployed data connections, check their health, and identify
connections with errors or that are idle/disconnected.
Each connection includes: id, name, vendor_name, vendor_product_name, parser_name,
status, source_type, last_ingested_volume_one_day, and ingest_url (for push).

Connection status values (title-case required): `Active`, `Idle`, `Disconnected`, `Paused`, `Pending`, `Error`.

**Example prompts:**

- "Show me all active data connections"
- "Which data connections have errors?"
- "List all push-based connections"

### `falcon_get_data_connection`

**Required scopes:** `ngsiem-data-connections:read`

Get full details for a data connection: configuration, status, and optionally ingest token.

Returns connection details, provisioning status, and (if `include_token=True`) the
ingest API token and URL for push-based connections. Use this to drill into a
specific connection for troubleshooting or to get the push ingest credentials.
A 202 on the token means the connection is still provisioning — retry shortly.

**Example prompts:**

- "Get details for this data connection"
- "Show me the ingest token for this push connection"

### `falcon_create_data_connection`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ngsiem-data-connections:write`

Create a new data connection.

Creates a connection for a specified connector type. For push-based connectors,
after creation use `falcon_get_data_connection` with `include_token=True` to get
the ingest URL and API key. For pull-based connectors, provide a `config_id` with
data source credentials. Returns the created connection record on success.

**Example prompts:**

- "Create a new push connection for Okta"
- "Set up a data connection for AWS CloudTrail"

### `falcon_manage_data_connection`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ngsiem-data-connections:write`

Update a data connection: rename, change parser, toggle enrichment, or pause/resume.

Only provided fields are changed; omitted fields keep their current values.
To pause a push connection, set `status='paused'`. To resume, set `status='active'`.
The connector type and API URL (push-based) cannot be changed.

**Example prompts:**

- "Pause this data connection"
- "Resume the Okta connection"
- "Rename this connection to 'Prod Okta'"

### `falcon_delete_data_connection`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ngsiem-data-connections:write`

Permanently delete a data connection.

Removes the connection and stops all data ingestion. This cannot be undone.
Use `falcon_search_data_connections` to confirm the connection ID before deleting.

**Example prompts:**

- "Delete this data connection"

### `falcon_regenerate_data_connection_token`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ngsiem-data-connections:write`

Regenerate the ingest API token for a push-based data connection.

The old token is immediately invalidated. You must update any data shippers
or third-party systems with the new token. All access tokens issued before
regeneration are immediately revoked.

**Example prompts:**

- "Regenerate the ingest token for this push connection"

### `falcon_list_connector_configs`

**Required scopes:** `ngsiem-data-connections:read`

List data source configurations for a pull-based connector type.

Returns existing configurations that define how Falcon accesses a third-party
data source (credentials, endpoints, etc.). Configs can be reused across
multiple connections.

**Example prompts:**

- "List the configurations for the Okta connector"
- "Show me the pull configs for this connector type"

### `falcon_create_connector_config`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ngsiem-data-connections:write`

Create a new data source configuration for a pull-based connector.

Configurations define how Falcon accesses a third-party data source (credentials,
endpoints, etc.) and can be reused across multiple connections.

**Example prompts:**

- "Create a new pull configuration for this connector"

### `falcon_update_connector_config`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ngsiem-data-connections:write`

Update an existing data source configuration.

Modifies credentials, endpoints, or other provider-specific settings
for a pull-based connector configuration.

**Example prompts:**

- "Update the credentials for this connector config"

### `falcon_delete_connector_configs`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ngsiem-data-connections:write`

Delete one or more data source configurations.

Removes the specified configurations. This cannot be undone.
Use `falcon_list_connector_configs` to confirm IDs before deleting.

**Example prompts:**

- "Delete this connector configuration"

## Resources

- **`falcon://data-connectors/connectors/search/fql-guide`**: FQL guide for the `filter` param of `falcon_search_data_connectors`.
- **`falcon://data-connectors/connections/search/fql-guide`**: FQL guide for the `filter` param of `falcon_search_data_connections`.
- **`falcon://data-connectors/data-sources/mapping-guide`**: Cross-references correlation rule template vendors with data connectors to answer "what rules can I enable?" and "what data do I need?".
- **`falcon://data-connectors/troubleshooting/troubleshooting-guide`**: Troubleshooting guide for connection issues, status meanings, and push connector HTTP errors.
