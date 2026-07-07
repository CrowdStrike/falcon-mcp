package base

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// entryIn/entryOut are a minimal typed handler shape for exercising AddTool's
// ToolEntry construction without a live server.
type entryIn struct {
	Name  string `json:"name,omitempty"`
	Count int    `json:"count,omitempty" jsonschema:"how many"`
}

type entryOut struct {
	Echo  string `json:"echo"`
	Count int    `json:"count"`
}

// captureAddTool registers handler through AddTool into a capturing sink and
// returns the resulting entry.
func captureAddTool(t *testing.T, handler mcp.ToolHandlerFor[entryIn, entryOut]) ToolEntry {
	t.Helper()
	var captured ToolEntry
	sink := funcRegistrar(func(e ToolEntry) { captured = e })
	AddTool(sink, &mcp.Tool{Name: "echo", Description: "echoes"}, handler)
	return captured
}

// funcRegistrar adapts a func to the Registrar interface for tests.
type funcRegistrar func(ToolEntry)

func (f funcRegistrar) Add(e ToolEntry) { f(e) }

// TestAddToolPrefixesNameAndInfersSchemas verifies AddTool applies the falcon_
// prefix, default read-only annotations, and an inferred input schema carrying
// the handler's parameters — the data the dynamic catalog reads.
func TestAddToolPrefixesNameAndInfersSchemas(t *testing.T) {
	t.Parallel()
	e := captureAddTool(t, func(_ context.Context, _ *mcp.CallToolRequest, in entryIn) (*mcp.CallToolResult, entryOut, error) {
		return nil, entryOut{Echo: in.Name, Count: in.Count}, nil
	})

	if e.Tool.Name != "falcon_echo" {
		t.Errorf("Name = %q, want falcon_echo", e.Tool.Name)
	}
	if e.Tool.Annotations == nil || !e.Tool.Annotations.ReadOnlyHint {
		t.Errorf("default read-only annotations not applied: %+v", e.Tool.Annotations)
	}
	if e.InputSchema == nil {
		t.Fatal("InputSchema is nil, want inferred schema")
	}
	if _, ok := e.InputSchema.Properties["name"]; !ok {
		t.Errorf("InputSchema missing property name: %+v", e.InputSchema.Properties)
	}
	if _, ok := e.InputSchema.Properties["count"]; !ok {
		t.Errorf("InputSchema missing property count: %+v", e.InputSchema.Properties)
	}
}

// TestAddToolRegistersOnServer verifies the entry's register closure adds the
// tool to a real *mcp.Server via the SDK's own mcp.AddTool, and that the tool
// then invokes end-to-end over an in-memory session — the SDK owns erasure,
// validation, and result packing.
func TestAddToolRegistersOnServer(t *testing.T) {
	t.Parallel()
	e := captureAddTool(t, func(_ context.Context, _ *mcp.CallToolRequest, in entryIn) (*mcp.CallToolResult, entryOut, error) {
		return nil, entryOut{Echo: in.Name, Count: in.Count}, nil
	})

	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "test"}, nil)
	e.Register(srv)

	ctx := context.Background()
	clientT, serverT := mcp.NewInMemoryTransports()
	ss, err := srv.Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "test"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	res, err := cs.CallTool(ctx, &mcp.CallToolParams{
		Name:      "falcon_echo",
		Arguments: map[string]any{"name": "hi", "count": 2},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	if res.IsError {
		t.Fatalf("unexpected error result: %v", res.Content)
	}

	var got entryOut
	if err := remarshalStructured(t, res.StructuredContent, &got); err != nil {
		t.Fatalf("decode structured content: %v", err)
	}
	if got.Echo != "hi" || got.Count != 2 {
		t.Errorf("got %+v, want {Echo:hi Count:2}", got)
	}
}

// remarshalStructured decodes a CallToolResult.StructuredContent (a generic
// value after the in-memory JSON round-trip) into v.
func remarshalStructured(t *testing.T, sc any, v any) error {
	t.Helper()
	b, err := json.Marshal(sc)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, v)
}
