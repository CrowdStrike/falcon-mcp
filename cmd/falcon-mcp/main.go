// Command falcon-mcp is the CrowdStrike Falcon MCP server. It resolves
// configuration from flags, environment, and config files, authenticates to the
// Falcon platform, and serves the Phase 1 tool modules over the configured
// transport (stdio, http, or sse).
package main

import (
	"os"

	"github.com/crowdstrike/falcon-mcp/internal/cli"
)

func main() {
	if err := cli.Execute(); err != nil {
		os.Exit(1)
	}
}
