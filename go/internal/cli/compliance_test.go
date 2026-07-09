package cli

import (
	"context"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/mcpx"
	"github.com/crowdstrike/falcon-mcp/internal/toolsets"

	// Blank imports register every module so compliance runs over the real,
	// full registered tool set rather than a synthetic toolset.
	_ "github.com/crowdstrike/falcon-mcp/internal/toolsets/idp"
)

// connectRegistry builds a server from the full default registry (nil client:
// no tool is invoked, only listed) and returns a connected in-memory client.
func connectRegistry(t *testing.T) *mcp.ClientSession {
	t.Helper()
	sets := toolsets.Default().Build(nil, nil, false)
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
	return cs
}

// TestCompliance_RegisteredToolSet asserts the MCP protocol contract across the
// real registered tool set: every tool has a non-empty name and description, a
// non-nil InputSchema, no OutputSchema (structured output stays OFF per D6), and
// annotations present. Tool names are NOT required to share a common prefix —
// they must match the Python originals exactly, which are heterogeneous (e.g.
// falcon_search_hosts vs idp_investigate_entity). This generalizes the synthetic
// server_test compliance check so Phase 4 modules are validated automatically.
func TestCompliance_RegisteredToolSet(t *testing.T) {
	cs := connectRegistry(t)
	res, err := cs.ListTools(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	if len(res.Tools) == 0 {
		t.Fatal("no tools registered; expected at least the hosts and idp modules")
	}

	for _, tl := range res.Tools {
		t.Run(tl.Name, func(t *testing.T) {
			if strings.TrimSpace(tl.Name) == "" {
				t.Error("tool has an empty name")
			}
			if strings.TrimSpace(tl.Description) == "" {
				t.Errorf("tool %q has an empty description", tl.Name)
			}
			if tl.InputSchema == nil {
				t.Errorf("tool %q has a nil InputSchema", tl.Name)
			}
			if tl.OutputSchema != nil {
				t.Errorf("tool %q has an OutputSchema; structured output must stay OFF (D6)", tl.Name)
			}
			if tl.Annotations == nil {
				t.Errorf("tool %q has no annotations", tl.Name)
			}
		})
	}
}

// TestCompliance_ResourcesHaveExactURIs asserts every registered resource
// exposes a non-empty, stable URI and is readable, generalizing the hosts-only
// resource check.
func TestCompliance_ResourcesHaveExactURIs(t *testing.T) {
	cs := connectRegistry(t)
	res, err := cs.ListResources(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	for _, r := range res.Resources {
		if r.URI == "" {
			t.Errorf("resource %q has an empty URI", r.Name)
			continue
		}
		read, err := cs.ReadResource(context.Background(), &mcp.ReadResourceParams{URI: r.URI})
		if err != nil {
			t.Errorf("ReadResource(%q): %v", r.URI, err)
			continue
		}
		if len(read.Contents) == 0 || read.Contents[0].Text == "" {
			t.Errorf("resource %q returned no text content", r.URI)
		}
	}
}
