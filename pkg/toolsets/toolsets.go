// Package toolsets maintains the explicit registry of available Falcon domain
// toolsets. Toolset packages self-register via Register in their init()
// functions; cmd/falcon-mcp blank-imports every toolset package to populate the
// registry. No reflection or filesystem discovery is used (unlike the Python
// implementation), mirroring the reference kubernetes-mcp-server registry.
package toolsets

import (
	"fmt"
	"sort"
	"sync"

	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
)

var (
	mu       sync.RWMutex
	registry = map[string]api.Toolset{}
)

// Register adds a toolset to the global registry. It panics on duplicate
// names, which can only happen from a programming error at init time.
func Register(ts api.Toolset) {
	mu.Lock()
	defer mu.Unlock()
	name := ts.GetName()
	if _, exists := registry[name]; exists {
		panic(fmt.Sprintf("toolsets: duplicate registration for %q", name))
	}
	registry[name] = ts
}

// Names returns the sorted names of all registered toolsets.
func Names() []string {
	mu.RLock()
	defer mu.RUnlock()
	names := make([]string, 0, len(registry))
	for name := range registry {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// Get returns the toolset registered under name, and whether it exists.
func Get(name string) (api.Toolset, bool) {
	mu.RLock()
	defer mu.RUnlock()
	ts, ok := registry[name]
	return ts, ok
}

// Toolsets returns the registered toolsets whose names appear in the enabled
// list, in sorted-name order. A nil or empty enabled list selects all
// registered toolsets. Validate should be called first to reject unknown names.
func Toolsets(enabled []string) []api.Toolset {
	mu.RLock()
	defer mu.RUnlock()

	var names []string
	if len(enabled) == 0 {
		for name := range registry {
			names = append(names, name)
		}
	} else {
		names = append(names, enabled...)
	}
	sort.Strings(names)

	out := make([]api.Toolset, 0, len(names))
	for _, name := range names {
		if ts, ok := registry[name]; ok {
			out = append(out, ts)
		}
	}
	return out
}

// Validate reports the names in enabled that are not registered. An empty or
// nil enabled list (meaning "all modules") is always valid.
func Validate(enabled []string) error {
	if len(enabled) == 0 {
		return nil
	}
	mu.RLock()
	defer mu.RUnlock()

	var invalid []string
	for _, name := range enabled {
		if _, ok := registry[name]; !ok {
			invalid = append(invalid, name)
		}
	}
	if len(invalid) > 0 {
		available := make([]string, 0, len(registry))
		for name := range registry {
			available = append(available, name)
		}
		sort.Strings(available)
		return fmt.Errorf("invalid modules: %v. Available modules: %v", invalid, available)
	}
	return nil
}
