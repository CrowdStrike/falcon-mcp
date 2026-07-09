// Package mcpx is the only package that imports the MCP go-sdk. It adapts the
// framework-agnostic toolsets contract onto an mcp.Server, keeping SDK churn
// contained to one place.
package mcpx

import (
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

// NewServer builds an MCP server with the Falcon implementation metadata.
func NewServer(version string) *mcp.Server {
	return mcp.NewServer(
		&mcp.Implementation{Name: "Falcon MCP Server", Version: version},
		&mcp.ServerOptions{
			Instructions: "This server provides access to CrowdStrike Falcon capabilities.",
		},
	)
}

// Register adds every tool and resource from the given toolsets to the server.
func Register(srv *mcp.Server, sets []*toolsets.Toolset) {
	for _, ts := range sets {
		for _, tool := range ts.Tools {
			addTool(srv, tool)
		}
		for _, res := range ts.Resources {
			addResource(srv, res)
		}
	}
}
