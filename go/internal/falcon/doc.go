// Package falcon wraps the gofalcon SDK for the falcon-mcp server. It builds an
// authenticated CrowdStrike API client with fail-fast credential verification
// (a scope-independent OAuth2 probe) and proxy support injected via the
// oauth2.HTTPClient context key. It also provides the cross-cutting utilities
// every module reuses: APIError, which normalizes gofalcon's per-operation
// error and *OK response types into one JSON envelope (enriching 403s with the
// required scopes); the Scope type modules declare for that enrichment; Opt for
// omitting zero-valued optional params; and ReorderByIDs for restoring
// query-step sort order on entities hydrated by a get-by-IDs step.
//
// This is the only package that imports gofalcon.
package falcon
