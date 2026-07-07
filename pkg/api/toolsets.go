// Package api defines the interfaces that domain toolsets implement and the
// value types used to register their tools and resources with an MCP server.
// It mirrors the reference kubernetes-mcp-server pkg/api contract.
package api

import (
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
)

// ServerTool bundles an MCP tool definition with a registration function that
// binds the tool's typed handler (closed over a FalconClient) to a server.
// A registrar is used rather than a bare handler because mcp.AddTool is generic
// over the tool's input/output types, which cannot be expressed in a single
// non-generic field.
type ServerTool struct {
	Tool     *mcp.Tool
	Register func(s *mcp.Server, fc *falcon.FalconClient)
}

// ServerResource bundles an MCP resource definition with its read handler.
type ServerResource struct {
	Resource *mcp.Resource
	Handler  mcp.ResourceHandler
}

// Toolset is a single Falcon domain module (hosts, detections, ...). Each
// toolset lives in its own package under pkg/toolsets and self-registers via
// an init() function.
type Toolset interface {
	// GetName returns the module name used for --modules selection.
	GetName() string
	// GetDescription returns a human-readable description of the module.
	GetDescription() string
	// GetTools returns the tools this module contributes, bound to fc.
	GetTools(fc *falcon.FalconClient) []ServerTool
	// GetResources returns the FQL-guide resources this module serves,
	// or nil if it has none.
	GetResources() []ServerResource
}
