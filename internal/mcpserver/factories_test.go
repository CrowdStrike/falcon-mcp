package mcpserver

import (
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client"

	"github.com/crowdstrike/falcon-mcp/internal/modules/registry"
)

// TestModuleFactoriesDiscovered verifies that the generated aggregator wires
// every tool module in deterministic (directory-name) order. It guards against
// a stale factories_gen.go: a newly added module missing here means the
// generator was not re-run.
func TestModuleFactoriesDiscovered(t *testing.T) {
	modules := registry.Build(registry.Deps{
		API: &client.CrowdStrikeAPISpecification{},
	}, moduleFactories())

	var got []string
	for _, m := range modules {
		got = append(got, m.Name())
	}

	want := []string{"detections", "host_groups", "hosts"}
	if len(got) != len(want) {
		t.Fatalf("moduleFactories() built %v, want %v", got, want)
	}
	for i, name := range want {
		if got[i] != name {
			t.Errorf("module %d = %q, want %q", i, got[i], name)
		}
	}
}
