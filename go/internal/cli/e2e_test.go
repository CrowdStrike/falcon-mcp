package cli

import (
	"context"
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
