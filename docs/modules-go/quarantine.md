# Quarantine

Investigate and manage CrowdStrike Falcon quarantined files.

## Tools

### `falcon_delete_quarantined_files`

**Type:** destructive

Delete quarantine records selected by IDs or filter. This tool is destructive and should be used only when quarantine records should be removed rather than released. Provide `ids` for specific records, or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide before constructing filter expressions. Returns an empty list on success.

### `falcon_preview_quarantine_actions`

**Type:** read-only

Estimate how many quarantine records each action would affect for a given filter. Use this read-only tool before calling a mutating quarantine action to understand the blast radius of a release, unrelease, or delete request. Consult falcon://quarantine/files/search/fql-guide before constructing filter expressions. Returns a list of action counts keyed by action name.

### `falcon_search_quarantined_files`

**Type:** read-only

Search quarantined files and return full quarantine metadata. Use this to discover quarantine records by host, hash, user, or state. Consult falcon://quarantine/files/search/fql-guide before constructing filter expressions. Returns full quarantine details including hostname, sha256, paths, state, and associated alert and detection IDs.

### `falcon_update_quarantined_files`

**Type:** mutating

Apply a reversible quarantine action to records selected by IDs or filter. Use this to release or unrelease quarantined files. Provide `ids` for specific records, or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide before constructing filter expressions. Returns an empty list on success.

## Resources

- `falcon://quarantine/files/search/fql-guide` — Contains the guide for the `filter` param of quarantine search and filter-based action tools.

