// Package mcpserver assembles the falcon-mcp MCP server: it builds the server,
// registers the enabled tool modules, and exposes Run over a transport.
package mcpserver

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"slices"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/config"
	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
	"github.com/crowdstrike/falcon-mcp/internal/modules/registry"
	"github.com/crowdstrike/falcon-mcp/internal/version"
)

// ErrUnknownModule classifies a --modules allowlist entry that names no
// registered module. Callers can branch with errors.Is.
var ErrUnknownModule = errors.New("mcpserver: unknown module")

// serverInstructions is returned to clients in the initialize response's
// instructions field as a usage hint for the LLM. It is intentionally empty for
// now: the field is wired end-to-end so populating it later is a one-line change,
// and an empty value is omitted from the wire (json:",omitempty"), leaving the
// initialize response unchanged until real guidance is written here.
const serverInstructions = ""

// Server wraps the assembled MCP server and its registered modules. In dynamic
// mode it also owns the tool catalog's in-process session, torn down by Close.
type Server struct {
	mcp     *mcp.Server
	modules []base.Module
	catalog *Catalog // non-nil only in dynamic mode
}

// New builds a Server from cfg and the shared Falcon client. It constructs the
// full set of Phase 1 modules (detections, hosts, host groups), filters them
// against cfg.Modules (empty enables all), and registers the selected modules.
// It returns ErrUnknownModule (wrapped) when the allowlist names a module that
// does not exist. In dynamic mode it wires the catalog's in-process session;
// call Close to release it.
func New(cfg *config.Config, api *client.CrowdStrikeAPISpecification) (*Server, error) {
	s := mcp.NewServer(&mcp.Implementation{Name: "falcon-mcp", Version: version.Version}, &mcp.ServerOptions{
		Instructions: serverInstructions,
		// KeepAlive pings idle sessions to detect dead peers and hold long-lived
		// http/sse connections open. Zero disables it (the SDK default), so stdio
		// and unconfigured deployments are unaffected.
		KeepAlive: cfg.KeepAlive,
	})

	// The process logger's level was already set by the CLI (preRunE) before we
	// are called; injecting it here keeps handlers free of the slog global.
	logger := slog.Default()
	allModules := registry.Build(registry.Deps{
		API:         api,
		Concurrency: cfg.DetailFetchConcurrency,
		Logger:      logger,
	}, moduleFactories())

	enabled, err := selectModules(allModules, cfg.Modules)
	if err != nil {
		return nil, err
	}

	cat, err := registerModules(s, enabled, cfg.Dynamic)
	if err != nil {
		return nil, err
	}
	slog.Info("modules enabled", "modules", moduleNames(enabled), "dynamic", cfg.Dynamic)

	return &Server{mcp: s, modules: enabled, catalog: cat}, nil
}

// registerModules registers the enabled modules on s. In normal mode each
// module registers its tools directly on the server and the returned catalog is
// nil. In dynamic mode the real tools are registered on the catalog's internal
// server and only the three meta-tools are registered on s; the returned
// catalog owns the in-process session (already connected) and must be closed by
// the caller. Module resources (FQL guides) and prompts are exposed on s in both
// modes.
func registerModules(s *mcp.Server, enabled []base.Module, dynamicMode bool) (*Catalog, error) {
	if !dynamicMode {
		reg := base.ServerRegistrar(s)
		for _, m := range enabled {
			m.RegisterTools(reg)
			m.RegisterResources(s)
			m.RegisterPrompts(s)
		}
		return nil, nil
	}

	cat := NewCatalog()
	for _, m := range enabled {
		m.RegisterTools(cat.ForModule(m.Name()))
		m.RegisterResources(s)
		m.RegisterPrompts(s)
	}
	// Connect the in-process session before serving so falcon_execute_tool can
	// dispatch. context.Background is right here: the session lives for the
	// server's lifetime, not a single request, and is closed via Server.Close.
	if err := cat.Connect(context.Background()); err != nil {
		return nil, err
	}
	NewMetaModule(cat, enabled).RegisterTools(base.ServerRegistrar(s))
	return cat, nil
}

// moduleNames returns the Name() of each module, in order. It is the single
// source for the enabled-modules log line and the "known" list in selection
// errors, so the module set is never enumerated by hand.
func moduleNames(modules []base.Module) []string {
	names := make([]string, len(modules))
	for i, m := range modules {
		names[i] = m.Name()
	}
	return names
}

// selectModules returns the subset of all whose Name() appears in want,
// preserving all's order. An empty want selects everything. Names in want that
// match no module yield a wrapped ErrUnknownModule; duplicates in want collapse.
func selectModules(all []base.Module, want []string) ([]base.Module, error) {
	if len(want) == 0 {
		return all, nil
	}

	known := moduleNames(all)
	var unknown []string
	for _, name := range want {
		if !slices.Contains(known, name) {
			unknown = append(unknown, name)
		}
	}
	if len(unknown) > 0 {
		return nil, fmt.Errorf("%w: %v (known: %v)", ErrUnknownModule, unknown, known)
	}

	var enabled []base.Module
	for _, m := range all {
		if slices.Contains(want, m.Name()) {
			enabled = append(enabled, m)
		}
	}
	return enabled, nil
}

// MCP returns the underlying MCP server, for wiring HTTP/SSE handlers that
// need a *mcp.Server per request.
func (s *Server) MCP() *mcp.Server { return s.mcp }

// Close releases resources held by the server. In dynamic mode it tears down
// the catalog's in-process session; in normal mode it is a no-op. It is safe to
// call more than once.
func (s *Server) Close() error {
	if s.catalog != nil {
		return s.catalog.Close()
	}
	return nil
}

// Run serves the MCP protocol over t until ctx is cancelled or the session
// ends, then releases server resources.
func (s *Server) Run(ctx context.Context, t mcp.Transport) error {
	defer func() { _ = s.Close() }()
	if err := s.mcp.Run(ctx, t); err != nil {
		return fmt.Errorf("mcpserver: run: %w", err)
	}
	return nil
}
