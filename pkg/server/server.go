// Package server builds a configured MCP server: it wires the enabled Falcon
// toolsets' tools and resources onto an mcp.Server, plus the three server-level
// tools (falcon_list_enabled_modules, falcon_check_connectivity,
// falcon_list_modules) that exist independent of any single module.
package server

import (
	"context"
	"log/slog"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
	"github.com/crowdstrike/falcon-mcp-go/pkg/version"
)

// ReadOnlyAnnotations is the default annotation set for read-only tools that
// talk to an external API, matching the Python READ_ONLY_ANNOTATIONS.
func ReadOnlyAnnotations() *mcp.ToolAnnotations {
	return &mcp.ToolAnnotations{
		ReadOnlyHint:    true,
		DestructiveHint: mcpx.BoolPtr(false),
		IdempotentHint:  true,
		OpenWorldHint:   mcpx.BoolPtr(true),
	}
}

// Options configures how the MCP server is assembled.
type Options struct {
	// Enabled is the list of module names to enable; empty means all.
	Enabled []string
	// Dynamic enables dynamic mode (3 meta-tools instead of all module tools).
	Dynamic bool
}

// Build constructs an mcp.Server with the enabled toolsets registered against
// fc. It returns the server plus the number of tools and resources registered.
func Build(fc *falcon.FalconClient, opts Options) (*mcp.Server, int, int, error) {
	if err := toolsets.Validate(opts.Enabled); err != nil {
		return nil, 0, 0, err
	}

	impl := &mcp.Implementation{
		Name:    "Falcon MCP Server",
		Version: version.String(),
	}
	srv := mcp.NewServer(impl, &mcp.ServerOptions{
		Instructions: "This server provides access to CrowdStrike Falcon capabilities.",
	})

	enabled := toolsets.Toolsets(opts.Enabled)
	enabledNames := make([]string, 0, len(enabled))
	for _, ts := range enabled {
		enabledNames = append(enabledNames, ts.GetName())
	}

	toolCount := 0
	resourceCount := 0

	// falcon_list_enabled_modules is always registered (both modes).
	registerListEnabledModules(srv, enabledNames)
	toolCount++

	if opts.Dynamic {
		// Dynamic mode registration is implemented in Phase 6; for now the
		// non-dynamic path is the supported one. The two meta-tools will be
		// added here.
		slog.Warn("dynamic mode not yet implemented; falling back to full tool registration")
	}

	// Server-level tools available in normal mode.
	registerCheckConnectivity(srv, fc)
	toolCount++
	registerListModules(srv)
	toolCount++

	// Register each enabled toolset's tools and resources.
	for _, ts := range enabled {
		for _, st := range ts.GetTools(fc) {
			st.Register(srv, fc)
			toolCount++
		}
		for _, r := range ts.GetResources() {
			srv.AddResource(r.Resource, r.Handler)
			resourceCount++
		}
	}

	return srv, toolCount, resourceCount, nil
}

// --- Server-level tools ---

type emptyInput struct{}

func registerListEnabledModules(srv *mcp.Server, enabled []string) {
	mcp.AddTool(srv, &mcp.Tool{
		Name: "falcon_list_enabled_modules",
		Description: "Lists enabled modules in the falcon-mcp server. These modules are " +
			"determined by the --modules flag when starting the server. If no modules " +
			"are specified, all available modules are enabled.",
		Annotations: ReadOnlyAnnotations(),
	}, func(_ context.Context, _ *mcp.CallToolRequest, _ emptyInput) (*mcp.CallToolResult, any, error) {
		return mcpx.JSONResult(map[string][]string{"modules": enabled})
	})
}

func registerListModules(srv *mcp.Server) {
	mcp.AddTool(srv, &mcp.Tool{
		Name:        "falcon_list_modules",
		Description: "Lists all available modules in the falcon-mcp server.",
		Annotations: ReadOnlyAnnotations(),
	}, func(_ context.Context, _ *mcp.CallToolRequest, _ emptyInput) (*mcp.CallToolResult, any, error) {
		return mcpx.JSONResult(map[string][]string{"modules": toolsets.Names()})
	})
}

func registerCheckConnectivity(srv *mcp.Server, fc *falcon.FalconClient) {
	mcp.AddTool(srv, &mcp.Tool{
		Name:        "falcon_check_connectivity",
		Description: "Check connectivity to the Falcon API.",
		Annotations: ReadOnlyAnnotations(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, _ emptyInput) (*mcp.CallToolResult, any, error) {
		connected := fc.Connectivity(ctx) == nil
		return mcpx.JSONResult(map[string]bool{"connected": connected})
	})
}
