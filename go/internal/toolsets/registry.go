package toolsets

import (
	"sort"

	"github.com/crowdstrike/gofalcon/falcon/client"
)

// Registry maps module slugs to their Toolset factories. The zero value is not
// usable; construct one with NewRegistry.
type Registry struct {
	factories map[string]Factory
}

// NewRegistry returns an empty Registry.
func NewRegistry() *Registry {
	return &Registry{factories: make(map[string]Factory)}
}

// Register associates a module slug with its factory. It panics on a duplicate
// slug, since that is a build-time wiring mistake.
func (r *Registry) Register(slug string, f Factory) {
	if _, dup := r.factories[slug]; dup {
		panic("toolsets: duplicate registration for module " + slug)
	}
	r.factories[slug] = f
}

// Slugs returns the registered module slugs in sorted order.
func (r *Registry) Slugs() []string {
	out := make([]string, 0, len(r.factories))
	for slug := range r.factories {
		out = append(out, slug)
	}
	sort.Strings(out)
	return out
}

// Build instantiates the enabled toolsets from the given client. When enabled
// is empty, every registered module is built. When readOnly is true, tools that
// are not read-only are dropped. Toolsets are returned in sorted slug order for
// deterministic tool listing.
func (r *Registry) Build(c *client.CrowdStrikeAPISpecification, enabled []string, readOnly bool) []*Toolset {
	want := make(map[string]bool, len(enabled))
	for _, slug := range enabled {
		want[slug] = true
	}

	var sets []*Toolset
	for _, slug := range r.Slugs() {
		if len(want) > 0 && !want[slug] {
			continue
		}
		ts := r.factories[slug](c)
		if ts == nil {
			continue
		}
		if readOnly {
			ts.Tools = filterReadOnly(ts.Tools)
		}
		sets = append(sets, ts)
	}
	return sets
}

// filterReadOnly returns only the read-only tools, preserving order.
func filterReadOnly(tools []Tool) []Tool {
	kept := make([]Tool, 0, len(tools))
	for _, t := range tools {
		if t.Annotations.ReadOnly {
			kept = append(kept, t)
		}
	}
	return kept
}

// The package-global default registry lets domain packages self-register in
// init via blank imports, mirroring the net/http and database/sql patterns.
var defaultRegistry = NewRegistry()

// Register adds a factory to the default registry. Domain packages call this
// from init so a blank import wires them in.
func Register(slug string, f Factory) { defaultRegistry.Register(slug, f) }

// Default returns the package-global registry that Register populates.
func Default() *Registry { return defaultRegistry }
