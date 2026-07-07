package server_test

import (
	"context"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/parity"
	"github.com/crowdstrike/falcon-mcp-go/pkg/server"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"

	// Blank-import all toolsets so the registry is populated for these tests.
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/all"
)

// implementedModules lists the modules whose toolsets are registered so far.
// As each phase lands more toolsets, add them here; the parity test then
// enforces their expected tool counts. The final phase enables the full set.
var implementedModules = []string{
	"cases",
	"correlation_rules",
	"custom_ioa",
	"data_protection",
	"detections",
	"discover",
	"exclusions",
	"firewall",
	"host_groups",
	"hosts",
	"idp",
	"intel",
	"ioc",
	"ngsiem",
	"policies",
	"quarantine",
	"recon",
	"rtr",
	"scheduled_reports",
	"sensor_usage",
	"serverless",
	"spotlight",
}

func testClient(t *testing.T, enabled []string) *mcp.ClientSession {
	t.Helper()
	fc, err := falcon.NewClient(context.Background(), falcon.Credentials{
		ClientID:     "id",
		ClientSecret: "secret",
		BaseURL:      "https://api.us-2.crowdstrike.com",
	}, false, "")
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}
	srv, _, _, err := server.Build(fc, server.Options{Enabled: enabled})
	if err != nil {
		t.Fatalf("Build: %v", err)
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

// TestRegisteredModulesArePresent ensures every implemented module is in the
// registry (guards against a missing blank-import in pkg/toolsets/all).
func TestRegisteredModulesArePresent(t *testing.T) {
	registered := map[string]bool{}
	for _, n := range toolsets.Names() {
		registered[n] = true
	}
	for _, m := range implementedModules {
		if !registered[m] {
			t.Errorf("module %q not registered (missing blank-import in pkg/toolsets/all?)", m)
		}
	}
}

// TestPerModuleToolCounts verifies each implemented module registers exactly
// the number of tools the Python implementation had (parity guard).
func TestPerModuleToolCounts(t *testing.T) {
	for _, m := range implementedModules {
		m := m
		t.Run(m, func(t *testing.T) {
			cs := testClient(t, []string{m})
			res, err := cs.ListTools(context.Background(), nil)
			if err != nil {
				t.Fatalf("ListTools: %v", err)
			}
			// Subtract the 3 server-level tools that are always registered.
			moduleTools := len(res.Tools) - parity.ServerLevelTools
			want := parity.ExpectedTools[m]
			if moduleTools != want {
				var names []string
				for _, tl := range res.Tools {
					names = append(names, tl.Name)
				}
				t.Errorf("module %q registered %d tools, want %d; tools=%v", m, moduleTools, want, names)
			}
		})
	}
}

// TestAllToolsPrefixed asserts every tool name carries the falcon_ prefix.
func TestAllToolsPrefixed(t *testing.T) {
	cs := testClient(t, implementedModules)
	res, err := cs.ListTools(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	for _, tl := range res.Tools {
		if len(tl.Name) < 7 || tl.Name[:7] != "falcon_" {
			t.Errorf("tool %q missing falcon_ prefix", tl.Name)
		}
	}
}
