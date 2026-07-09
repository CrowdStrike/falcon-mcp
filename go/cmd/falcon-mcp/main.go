// Command falcon-mcp is the CrowdStrike Falcon MCP server.
package main

import (
	"fmt"
	"os"

	"github.com/crowdstrike/falcon-mcp/internal/cli"

	// Blank imports register each module's toolset factory in the default
	// registry at startup.
	_ "github.com/crowdstrike/falcon-mcp/internal/toolsets/hosts"
	_ "github.com/crowdstrike/falcon-mcp/internal/toolsets/idp"
)

func main() {
	if err := cli.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "falcon-mcp:", err)
		os.Exit(1)
	}
}
