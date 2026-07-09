package mcpx

import (
	"context"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

// addResource registers one embedded guide as an MCP resource, preserving its
// exact URI. The handler synthesizes the read result from the resource's
// embedded text.
func addResource(srv *mcp.Server, r toolsets.Resource) {
	res := &mcp.Resource{
		URI:         r.URI,
		Name:        r.Name,
		Description: r.Description,
		MIMEType:    r.MIMEType,
	}
	text := r.Text
	mime := r.MIMEType
	srv.AddResource(res, func(_ context.Context, _ *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		return &mcp.ReadResourceResult{
			Contents: []*mcp.ResourceContents{{
				URI:      r.URI,
				MIMEType: mime,
				Text:     text,
			}},
		}, nil
	})
}
