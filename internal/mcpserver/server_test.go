package mcpserver

import (
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/config"
	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

func TestServerMCPNotNil(t *testing.T) {
	// api can be a zero *client.CrowdStrikeAPISpecification for this wiring test;
	// New only reads sub-client fields to register tools, does not call the API.
	// (WHY: exercises accessor wiring, not live API calls.)
	srv, err := New(&config.Config{}, &client.CrowdStrikeAPISpecification{})
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	if srv.MCP() == nil {
		t.Fatal("MCP() returned nil")
	}
}

// fakeModule is a name-only base.Module for exercising selectModules without
// constructing real modules or a live API.
type fakeModule struct{ name string }

func (m fakeModule) Name() string                  { return m.name }
func (m fakeModule) Description() string           { return "fake " + m.name + " module" }
func (m fakeModule) RegisterTools(base.Registrar)  {}
func (m fakeModule) RegisterResources(*mcp.Server) {}

func TestSelectModules(t *testing.T) {
	t.Parallel()
	all := []base.Module{
		fakeModule{"detections"},
		fakeModule{"hosts"},
		fakeModule{"host_groups"},
	}
	names := func(ms []base.Module) []string {
		out := make([]string, len(ms))
		for i, m := range ms {
			out[i] = m.Name()
		}
		return out
	}

	tests := []struct {
		name    string
		want    []string
		wantOut []string // nil means "same slice as all"
		wantErr bool
	}{
		{name: "empty selects all", want: nil, wantOut: []string{"detections", "hosts", "host_groups"}},
		{name: "subset", want: []string{"hosts"}, wantOut: []string{"hosts"}},
		{name: "full set", want: []string{"detections", "hosts", "host_groups"}, wantOut: []string{"detections", "hosts", "host_groups"}},
		{name: "order follows all not want", want: []string{"host_groups", "detections"}, wantOut: []string{"detections", "host_groups"}},
		{name: "duplicates collapse", want: []string{"hosts", "hosts"}, wantOut: []string{"hosts"}},
		{name: "unknown name errors", want: []string{"bogus"}, wantErr: true},
		{name: "mix of known and unknown errors", want: []string{"hosts", "bogus"}, wantErr: true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got, err := selectModules(all, tt.want)
			if tt.wantErr {
				if !errors.Is(err, ErrUnknownModule) {
					t.Fatalf("err = %v, want ErrUnknownModule", err)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected err: %v", err)
			}
			gotNames := names(got)
			if len(gotNames) != len(tt.wantOut) {
				t.Fatalf("got %v, want %v", gotNames, tt.wantOut)
			}
			for i, n := range tt.wantOut {
				if gotNames[i] != n {
					t.Fatalf("got %v, want %v", gotNames, tt.wantOut)
				}
			}
		})
	}
}

func TestNewSelectsModules(t *testing.T) {
	t.Parallel()
	srv, err := New(
		&config.Config{Modules: []string{"hosts"}},
		&client.CrowdStrikeAPISpecification{},
	)
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	if len(srv.modules) != 1 || srv.modules[0].Name() != "hosts" {
		t.Fatalf("modules = %v, want [hosts]", srv.modules)
	}
}

func TestNewUnknownModule(t *testing.T) {
	t.Parallel()
	_, err := New(
		&config.Config{Modules: []string{"bogus"}},
		&client.CrowdStrikeAPISpecification{},
	)
	if !errors.Is(err, ErrUnknownModule) {
		t.Fatalf("err = %v, want ErrUnknownModule", err)
	}
}

// TestNewRegistersAllModules guards against the aggregator import being dropped:
// New must build the full default module set (sorted by name) from the registry.
func TestNewRegistersAllModules(t *testing.T) {
	t.Parallel()
	srv, err := New(&config.Config{}, &client.CrowdStrikeAPISpecification{})
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	want := []string{"detections", "host_groups", "hosts"}
	if len(srv.modules) != len(want) {
		t.Fatalf("modules = %v, want %v", moduleNames(srv.modules), want)
	}
	for i, n := range want {
		if srv.modules[i].Name() != n {
			t.Fatalf("modules = %v, want %v", moduleNames(srv.modules), want)
		}
	}
}
