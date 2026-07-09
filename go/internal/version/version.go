// Package version exposes the falcon-mcp build version, set via -ldflags.
package version

// Version is the falcon-mcp server version, injected at build time with
// -ldflags "-X github.com/crowdstrike/falcon-mcp/internal/version.Version=...".
var Version = "dev"
