package server_test

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/pkg/server"

	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/all"
)

func dynamicClient(t *testing.T) *mcp.ClientSession {
	t.Helper()
	fc, err := falcon.NewClient(context.Background(), falcon.Credentials{
		ClientID: "id", ClientSecret: "secret", BaseURL: "https://api.us-2.crowdstrike.com",
	}, false, "")
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}
	srv, toolCount, _, err := server.Build(fc, server.Options{Dynamic: true})
	if err != nil {
		t.Fatalf("Build(dynamic): %v", err)
	}
	if toolCount != 3 {
		t.Errorf("dynamic mode tool count = %d, want 3", toolCount)
	}
	ct, st := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, st, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, ct, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })
	return cs
}

// TestDynamicModeThreeTools verifies dynamic mode exposes exactly the 3 meta-tools.
func TestDynamicModeThreeTools(t *testing.T) {
	cs := dynamicClient(t)
	res, err := cs.ListTools(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	if len(res.Tools) != 3 {
		var names []string
		for _, tl := range res.Tools {
			names = append(names, tl.Name)
		}
		t.Fatalf("dynamic mode exposed %d tools, want 3: %v", len(res.Tools), names)
	}
	got := map[string]bool{}
	for _, tl := range res.Tools {
		got[tl.Name] = true
	}
	for _, want := range []string{"falcon_list_enabled_modules", "falcon_search_tools", "falcon_execute_tool"} {
		if !got[want] {
			t.Errorf("missing dynamic tool %q", want)
		}
	}
}

// TestDynamicSearchTools verifies falcon_search_tools finds tools by keyword and
// injects the FQL hint into filter params.
func TestDynamicSearchTools(t *testing.T) {
	cs := dynamicClient(t)
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_search_tools",
		Arguments: map[string]any{"query": "hosts", "module": "hosts"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	text := res.Content[0].(*mcp.TextContent).Text
	var results []map[string]any
	if err := json.Unmarshal([]byte(text), &results); err != nil {
		t.Fatalf("search result not an array: %v (%s)", err, text)
	}
	if len(results) == 0 {
		t.Fatal("expected at least one hosts tool")
	}
	// falcon_search_hosts should appear and its filter param should carry the FQL suffix.
	var found bool
	for _, r := range results {
		if r["name"] == "falcon_search_hosts" {
			found = true
			params, _ := r["parameters"].(map[string]any)
			filter, _ := params["filter"].(map[string]any)
			desc, _ := filter["description"].(string)
			if !contains(desc, "FQL uses + for AND") {
				t.Errorf("filter description missing FQL suffix: %q", desc)
			}
		}
	}
	if !found {
		t.Error("falcon_search_hosts not in search results")
	}
}

// TestDynamicExecuteUnknownTool verifies a helpful error for an unknown tool.
func TestDynamicExecuteUnknownTool(t *testing.T) {
	cs := dynamicClient(t)
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_execute_tool",
		Arguments: map[string]any{"tool_name": "falcon_nonexistent"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	text := res.Content[0].(*mcp.TextContent).Text
	if !contains(text, "Unknown tool") {
		t.Errorf("expected unknown-tool error, got %s", text)
	}
}

// TestDynamicSearchNoResults verifies the no-results hint path.
func TestDynamicSearchNoResults(t *testing.T) {
	cs := dynamicClient(t)
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_search_tools",
		Arguments: map[string]any{"query": "zzzznotarealtoolkeyword"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	text := res.Content[0].(*mcp.TextContent).Text
	if !contains(text, "No tools found") {
		t.Errorf("expected no-results hint, got %s", text)
	}
}

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
