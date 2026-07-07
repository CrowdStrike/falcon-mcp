package mcpserver

import (
	"context"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/config"
)

// listToolNames connects an in-memory client to srv and returns the registered
// tool names.
func listToolNames(t *testing.T, srv *Server) map[string]bool {
	t.Helper()
	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	ss, err := srv.MCP().Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })

	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "test"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	names := map[string]bool{}
	for _, tool := range tools.Tools {
		names[tool.Name] = true
	}
	return names
}

// metaToolNames are the three meta-tools exposed only in dynamic mode.
var metaToolNames = []string{"falcon_search_tools", "falcon_execute_tool", "falcon_list_enabled_modules"}

// TestDynamicModeExposesOnlyMetaTools verifies that with Dynamic=true the server
// exposes exactly the three meta-tools and none of the real tools.
func TestDynamicModeExposesOnlyMetaTools(t *testing.T) {
	t.Parallel()
	srv, err := New(&config.Config{Dynamic: true}, &client.CrowdStrikeAPISpecification{})
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	names := listToolNames(t, srv)

	if len(names) != len(metaToolNames) {
		t.Errorf("tool count = %d %v, want %d meta-tools", len(names), keys(names), len(metaToolNames))
	}
	for _, want := range metaToolNames {
		if !names[want] {
			t.Errorf("meta-tool %q not registered", want)
		}
	}
	// A representative real tool must NOT be present.
	if names["falcon_search_hosts"] {
		t.Error("real tool falcon_search_hosts leaked in dynamic mode")
	}
}

// TestNormalModeExposesRealToolsNotMeta verifies the default mode exposes the
// real tools and none of the meta-tools.
func TestNormalModeExposesRealToolsNotMeta(t *testing.T) {
	t.Parallel()
	srv, err := New(&config.Config{}, &client.CrowdStrikeAPISpecification{})
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	names := listToolNames(t, srv)

	if !names["falcon_search_hosts"] {
		t.Error("real tool falcon_search_hosts missing in normal mode")
	}
	for _, meta := range metaToolNames {
		if names[meta] {
			t.Errorf("meta-tool %q leaked in normal mode", meta)
		}
	}
}

func keys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
