<!-- meta:title Exclusions -->
<!-- meta:description This module provides a unified set of tools for managing CrowdStrike exclusions across four types — IOA, Machine Learning, Sensor Visibility, and Certificate-Based — behind a single `exclusion_type` discriminator -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides a unified set of tools for managing CrowdStrike exclusions across four types — IOA, Machine Learning, Sensor Visibility, and Certificate-Based — behind a single `exclusion_type` discriminator

## API Scopes

- `IOA Exclusions:read`
- `Machine Learning Exclusions:read`
- `Sensor Visibility Exclusions:read`
- `IOA Exclusions:write`
- `Machine Learning Exclusions:write`
- `Sensor Visibility Exclusions:write`

## Tools

### `falcon_create_exclusion`

> [!NOTE]
> This tool modifies data.

Create an exclusion of the given type.

The `exclusion_type` selects which fields are required: 'ioa' needs name,
pattern_id, ifn_regex, and cl_regex; 'ml' and 'sensor_visibility' need
value (sensor_visibility also needs host_groups); 'certificate' needs
name, certificate, and status. Invalid or missing fields return a guiding
error before any API call. Returns the created exclusion record(s).

**Example prompts:**

- "Create an ML exclusion for /tmp/foo.sh applied to all hosts"
- "Add a sensor visibility exclusion for C:\Temp\* on the Workstations group"

### `falcon_delete_exclusions`

> [!CAUTION]
> This tool performs destructive operations.

Delete one or more exclusions of the given type.

Provide the `exclusion_type` and a non-empty list of exclusion `ids`.
Returns the API response for the deletion.

**Example prompts:**

- "Delete the certificate exclusion with ID abc123"

### `falcon_get_certificate_details`

**Required scopes:** `Machine Learning Exclusions:read`

Retrieve the code-signing certificate metadata for a file by SHA256.

Use this as the pre-flight lookup before building a certificate-based
exclusion: it returns the file's signing certificate details (issuer,
subject, serial, thumbprint, validity window) which you then pass as the
`certificate` argument to falcon_create_exclusion. Returns certificate
metadata for the given hash.

**Example prompts:**

- "Look up the signing certificate for SHA256 3dd9a..."

### `falcon_search_certificates`

Search certificate-based exclusions and return full records.

Use this to discover existing certificate-based exclusions by name,
value, or timestamp. This is a convenience equivalent to
falcon_search_exclusions with exclusion_type='certificate'. Returns full
exclusion records including the certificate metadata, status, and scope.

**Example prompts:**

- "Show me the certificate-based exclusions in my environment"

### `falcon_search_exclusions`

Search exclusions of a given type and return full exclusion records.

Use this to find IOA, machine learning, sensor visibility, or
certificate-based exclusions by name, value, scope, or timestamp. The
`exclusion_type` parameter selects which exclusion API is queried.
Consult falcon://exclusions/search/fql-guide before constructing filter
expressions — the available fields differ per type. Returns full
exclusion records including id, scope, and timestamps.

**Example prompts:**

- "Show me my most recent IOA and machine learning exclusions"
- "List sensor visibility exclusions created in the last 7 days"

### `falcon_update_exclusion`

> [!NOTE]
> This tool modifies data.

Update an existing exclusion of the given type.

Provide the `id` of the exclusion plus the same fields used when creating
that type. All four types update via HTTP PATCH. Invalid or missing
fields return a guiding error before any API call. Returns the updated
exclusion record(s).

**Example prompts:**

- "Update IOA exclusion abc123 to also match a new command line regex"

## Resources

- **`falcon://exclusions/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_exclusions` tool.
