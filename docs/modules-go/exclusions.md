# Exclusions

Manage CrowdStrike Falcon exclusions (IOA, ML, Sensor Visibility, Certificate-Based).

## Tools

### `falcon_create_exclusion`

**Type:** mutating

Create an exclusion of the given exclusion_type (ioa, ml, sensor_visibility, certificate).

### `falcon_delete_exclusions`

**Type:** destructive

Delete exclusions of the given exclusion_type by ID.

### `falcon_get_certificate_details`

**Type:** read-only

Retrieve details for one or more certificates by ID (used when building certificate-based exclusions).

### `falcon_search_exclusions`

**Type:** read-only

Search for exclusions by type. The exclusion_type parameter selects which exclusion API is queried (ioa, ml, sensor_visibility, certificate). Consult falcon://exclusions/search/fql-guide before constructing filter expressions. Returns full exclusion details.

### `falcon_update_exclusion`

**Type:** mutating

Update an existing exclusion of the given exclusion_type.

## Resources

- `falcon://exclusions/search/fql-guide` — Contains the guide for the `filter` param of the `falcon_search_exclusions` tool.

