package mcpserver

// Dynamic mode: instead of registering every module's tools on the served MCP
// server (each carrying a full schema that costs the client context-window
// tokens), it registers three fixed meta-tools — falcon_search_tools,
// falcon_execute_tool, and falcon_list_enabled_modules — backed by an in-process
// Catalog of the real tools. Clients discover tools on demand via search and
// invoke them by name via execute, paying each tool's schema cost only when they
// use it.
//
// The real tools are registered on a separate internal *mcp.Server that is
// never served to the client. falcon_execute_tool dispatches to them over an
// in-process client session wired to that internal server with
// mcp.NewInMemoryTransports, so the SDK owns all argument validation and result
// packing — there is no hand-maintained copy of the SDK's tool erasure to drift
// on an SDK upgrade.
//
// This is a faithful port of the upstream Python crowdstrike/falcon-mcp dynamic
// mode. It does NOT use the MCP notifications/tools/list_changed mechanism: the
// three meta-tools are the served server's entire tool surface for the process
// lifetime.

import (
	"context"
	"fmt"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// Catalog holds the real tools captured in dynamic mode. Tools are registered
// on an internal *mcp.Server at startup; after Connect wires an in-process
// client session to that server, the catalog is read-only and its meta-tool
// handlers only read it, so it needs no mutex.
type Catalog struct {
	internal *mcp.Server
	entries  []catalogEntry
	byName   map[string]catalogEntry // "falcon_"-prefixed name -> entry
	modules  []string                // contributing module names, in registration order

	// session is the in-process client connected to internal, established by
	// Connect and used by falcon_execute_tool to dispatch by name. It is nil
	// until Connect succeeds.
	session *mcp.ClientSession
	ss      *mcp.ServerSession
}

// catalogEntry is one real tool captured for dynamic dispatch: its SDK
// descriptor (already "falcon_"-prefixed), owning module, the lowercased search
// corpus, and the parameter summary derived from its inferred input schema.
type catalogEntry struct {
	tool   *mcp.Tool
	module string
	corpus string
	params []paramSummary
}

// NewCatalog returns an empty Catalog with a fresh internal server for the real
// tools.
func NewCatalog() *Catalog {
	return &Catalog{
		internal: mcp.NewServer(&mcp.Implementation{Name: "falcon-mcp-internal", Version: "internal"}, nil),
		byName:   map[string]catalogEntry{},
	}
}

// ForModule returns a base.Registrar that registers each tool the named module
// registers onto the internal server (via the SDK's mcp.AddTool) and records a
// catalog entry (stamping the module name). The recorded entry carries the
// tool's inferred input schema, which the search corpus and parameter summaries
// read.
func (c *Catalog) ForModule(name string) base.Registrar {
	c.modules = append(c.modules, name)
	return &catalogRegistrar{cat: c, module: name}
}

// Connect wires an in-process client session to the internal server so
// falcon_execute_tool can dispatch tools by name. It must be called once, after
// all modules have registered and before the meta-tools are invoked. The
// session lives until Close; ctx governs only the connection handshake.
func (c *Catalog) Connect(ctx context.Context) error {
	clientT, serverT := mcp.NewInMemoryTransports()
	ss, err := c.internal.Connect(ctx, serverT, nil)
	if err != nil {
		return fmt.Errorf("dynamic: connect internal server: %w", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "falcon-mcp-dynamic", Version: "internal"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		_ = ss.Close()
		return fmt.Errorf("dynamic: connect internal client: %w", err)
	}
	c.ss = ss
	c.session = cs
	return nil
}

// Close tears down the in-process session established by Connect. It is safe to
// call on a catalog that was never connected.
func (c *Catalog) Close() error {
	if c.session != nil {
		_ = c.session.Close()
	}
	if c.ss != nil {
		_ = c.ss.Wait()
	}
	return nil
}

// Modules returns the contributing module names in registration order.
func (c *Catalog) Modules() []string {
	out := make([]string, len(c.modules))
	copy(out, c.modules)
	return out
}

// lookup returns the entry for name, accepting either the exact "falcon_"-
// prefixed name or the bare name.
func (c *Catalog) lookup(name string) (catalogEntry, bool) {
	if e, ok := c.byName[name]; ok {
		return e, true
	}
	e, ok := c.byName[toolNamePrefix+name]
	return e, ok
}

// catalogRegistrar is the per-module sink returned by ForModule. It implements
// base.Registrar.
type catalogRegistrar struct {
	cat    *Catalog
	module string
}

func (r *catalogRegistrar) Add(e base.ToolEntry) {
	e.Module = r.module
	// Register the real tool on the internal server; the SDK owns its erasure.
	e.Register(r.cat.internal)

	ce := catalogEntry{
		tool:   e.Tool,
		module: r.module,
		params: paramSummaries(e.InputSchema),
	}
	ce.corpus = searchCorpus(e.Tool, r.module, ce.params)

	r.cat.entries = append(r.cat.entries, ce)
	r.cat.byName[e.Tool.Name] = ce
}
