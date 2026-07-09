package toolsets

import (
	"context"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client"
)

func newTestToolset(name string) *Toolset {
	return &Toolset{
		Name: name,
		Tools: []Tool{
			NewTool(name+"_read", "read tool", ReadOnly(),
				func(_ context.Context, _ struct{}) (any, error) { return nil, nil }),
			NewTool(name+"_write", "write tool", Annotations{ReadOnly: false},
				func(_ context.Context, _ struct{}) (any, error) { return nil, nil }),
		},
	}
}

func TestRegistry_RegisterAndBuildEnabled(t *testing.T) {
	r := NewRegistry()
	r.Register("hosts", func(*client.CrowdStrikeAPISpecification) *Toolset { return newTestToolset("hosts") })
	r.Register("detections", func(*client.CrowdStrikeAPISpecification) *Toolset { return newTestToolset("detections") })

	// Enable only hosts.
	sets := r.Build(nil, []string{"hosts"}, false)
	if len(sets) != 1 || sets[0].Name != "hosts" {
		t.Fatalf("Build enabled=[hosts] = %+v, want just hosts", names(sets))
	}
}

func TestRegistry_BuildAllWhenEnabledEmpty(t *testing.T) {
	r := NewRegistry()
	r.Register("hosts", func(*client.CrowdStrikeAPISpecification) *Toolset { return newTestToolset("hosts") })
	r.Register("detections", func(*client.CrowdStrikeAPISpecification) *Toolset { return newTestToolset("detections") })

	sets := r.Build(nil, nil, false)
	if len(sets) != 2 {
		t.Fatalf("Build enabled=nil should return all, got %v", names(sets))
	}
}

func TestRegistry_ReadOnlyFiltersWriteTools(t *testing.T) {
	r := NewRegistry()
	r.Register("hosts", func(*client.CrowdStrikeAPISpecification) *Toolset { return newTestToolset("hosts") })

	sets := r.Build(nil, []string{"hosts"}, true)
	if len(sets) != 1 {
		t.Fatalf("want 1 toolset, got %d", len(sets))
	}
	for _, tool := range sets[0].Tools {
		if !tool.Annotations.ReadOnly {
			t.Fatalf("read-only build kept non-read-only tool %q", tool.Name)
		}
	}
	if len(sets[0].Tools) != 1 {
		t.Fatalf("read-only build should keep exactly the 1 read tool, got %d", len(sets[0].Tools))
	}
}

func names(sets []*Toolset) []string {
	out := make([]string, len(sets))
	for i, s := range sets {
		out[i] = s.Name
	}
	return out
}
