package mcpx

import (
	"context"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// RunStdio serves the MCP server over stdio, blocking until the context is
// canceled or the transport closes. stdio requires that no diagnostic output
// goes to stdout; logging is configured to stderr elsewhere.
func RunStdio(ctx context.Context, srv *mcp.Server) error {
	return srv.Run(ctx, &mcp.StdioTransport{})
}
