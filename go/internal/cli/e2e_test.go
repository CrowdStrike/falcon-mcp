package cli

import (
	"context"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/mcpx"
	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

// TestEndToEnd_ServerListsHostsToolsAndResources drives the server built from
// the real module registry (hosts registered via blank import) over the SDK's
// in-memory transport, without needing live Falcon credentials. It is the
// stdio-equivalent protocol check for the PoC.
func TestEndToEnd_ServerListsHostsToolsAndResources(t *testing.T) {
	// nil client: New() only stores it; no tool is invoked here.
	sets := toolsets.Default().Build(nil, []string{"hosts"}, false)
	srv := mcpx.NewServer("test")
	mcpx.Register(srv, sets)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil)
	cs, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	got := map[string]*mcp.Tool{}
	for _, tl := range tools.Tools {
		got[tl.Name] = tl
	}
	for _, want := range []string{"falcon_search_hosts", "falcon_get_host_details"} {
		if got[want] == nil {
			t.Fatalf("tool %q not listed; have %v", want, keys(got))
		}
		if got[want].Annotations == nil || !got[want].Annotations.ReadOnlyHint {
			t.Fatalf("tool %q missing ReadOnlyHint", want)
		}
	}

	res, err := cs.ListResources(ctx, nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	var haveGuide bool
	for _, r := range res.Resources {
		if r.URI == "falcon://hosts/search/fql-guide" {
			haveGuide = true
		}
	}
	if !haveGuide {
		t.Fatal("hosts FQL guide resource not listed")
	}
}

func keys(m map[string]*mcp.Tool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

// TestEndToEnd_DynamicModeExposesThreeMetaTools drives the server built with
// dynamic mode enabled over the real registry, asserting exactly the 3
// meta-tools are listed and that falcon_search_tools finds the hosts tools.
func TestEndToEnd_DynamicModeExposesThreeMetaTools(t *testing.T) {
	sets := toolsets.Default().Build(nil, []string{"hosts"}, false)
	sets = []*toolsets.Toolset{toolsets.Dynamic(sets)}
	srv := mcpx.NewServer("test")
	mcpx.Register(srv, sets)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil)
	cs, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	if len(tools.Tools) != 3 {
		var names []string
		for _, tl := range tools.Tools {
			names = append(names, tl.Name)
		}
		t.Fatalf("dynamic mode should list 3 tools, got %d: %v", len(tools.Tools), names)
	}

	// falcon_search_tools must find the hosts tools by keyword.
	res, err := cs.CallTool(ctx, &mcp.CallToolParams{
		Name:      "falcon_search_tools",
		Arguments: map[string]any{"query": "hosts"},
	})
	if err != nil {
		t.Fatalf("CallTool search: %v", err)
	}
	tc := res.Content[0].(*mcp.TextContent)
	if !strings.Contains(tc.Text, "falcon_search_hosts") {
		t.Fatalf("search did not surface falcon_search_hosts: %s", tc.Text)
	}
}
