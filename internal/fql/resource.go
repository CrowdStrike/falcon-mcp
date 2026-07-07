package fql

import (
	"context"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
)

// Resource builds an api.ServerResource that serves the embedded FQL guide at
// uri as plain text. name and description populate the MCP resource metadata.
// It panics if the guide for uri is not embedded (a compile-time-known error).
func Resource(uri, name, description string) api.ServerResource {
	text := MustGuide(uri)
	return api.ServerResource{
		Resource: &mcp.Resource{
			URI:         uri,
			Name:        name,
			Description: description,
			MIMEType:    "text/plain",
		},
		Handler: func(_ context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
			return &mcp.ReadResourceResult{
				Contents: []*mcp.ResourceContents{
					{URI: uri, MIMEType: "text/plain", Text: text},
				},
			}, nil
		},
	}
}
