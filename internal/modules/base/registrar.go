package base

import (
	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// Registrar is the sink base.AddTool writes each registered tool to. It is
// declared next to AddTool, its only writer. In normal mode the sink forwards
// each tool to the live *mcp.Server via ServerRegistrar. In dynamic mode the
// sink registers the tool on a separate internal *mcp.Server and records it in
// a catalog, so the three meta-tools can dispatch to it by name through an
// in-process client session without the tool ever appearing on the served
// server.
//
// The interface is type-erased (no In/Out type parameters) because Go interface
// methods cannot be generic: AddTool resolves the generics up front and hands
// the sink a ToolEntry carrying an SDK-registration closure. Both modes drive
// tool invocation through the SDK's own mcp.AddTool erasure — the server does
// the schema validation and result packing, so there is no hand-maintained copy
// of the SDK's internals to drift on an SDK upgrade.
type Registrar interface {
	// Add records one registered tool.
	Add(ToolEntry)
}

// ToolEntry is one registered tool, captured with everything both modes need.
// register is populated by AddTool while In/Out are still in scope, so the SDK
// owns type erasure verbatim; InputSchema is the schema inferred from In, kept
// for the dynamic catalog's parameter display and search corpus (the served
// tool's own schema is inferred independently by the SDK at registration).
type ToolEntry struct {
	// Tool is the SDK tool descriptor. Its Name already carries the "falcon_"
	// prefix and its annotations/output schema are applied.
	Tool *mcp.Tool
	// Module is the owning module's name, stamped by the dynamic catalog. It is
	// empty on entries handed to a ServerRegistrar (normal mode does not need it).
	Module string
	// InputSchema is the JSON Schema inferred from the handler's In type. The
	// dynamic catalog reads it for parameter summaries and the search corpus;
	// normal mode ignores it. Nil when In is any (no properties to describe).
	InputSchema *jsonschema.Schema

	// register performs registration on the target server via the SDK's own
	// mcp.AddTool, closing over the original In/Out types.
	register func(s *mcp.Server)
}

// Register registers this entry's tool on s via the SDK's mcp.AddTool. Normal
// mode registers on the served server; dynamic mode registers on its internal
// server. Either way the SDK owns type erasure, schema validation, and result
// packing.
func (e ToolEntry) Register(s *mcp.Server) { e.register(s) }

// ServerRegistrar returns a Registrar that registers each tool directly on s
// via the SDK's mcp.AddTool.
func ServerRegistrar(s *mcp.Server) Registrar { return serverRegistrar{s: s} }

type serverRegistrar struct{ s *mcp.Server }

func (r serverRegistrar) Add(e ToolEntry) { e.register(r.s) }
