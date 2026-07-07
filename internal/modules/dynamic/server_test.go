package dynamic

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// TestExecuteToolThroughServer drives falcon_execute_tool over a real in-memory
// MCP server. Unlike the direct-call unit tests, this exercises the meta-tool's
// OWN input-schema validation — the path that rejected an object-typed
// parameters argument when Parameters was a json.RawMessage. It is the
// regression guard for that bug.
func TestExecuteToolThroughServer(t *testing.T) {
	t.Parallel()

	cat, meta := buildCatalog(t, fakeModule{name: "hosts"})
	_ = cat

	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "test"}, nil)
	meta.RegisterTools(base.ServerRegistrar(srv))

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

	// An object-valued "parameters" must pass falcon_execute_tool's own schema
	// validation and dispatch to the underlying tool.
	res, err := cs.CallTool(ctx, &mcp.CallToolParams{
		Name: "falcon_execute_tool",
		Arguments: map[string]any{
			"tool_name":  "falcon_search_hosts",
			"parameters": map[string]any{"filter": "platform:'Windows'"},
		},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	if res.IsError {
		t.Fatalf("execute through server returned error: %v", res.Content)
	}

	var out searchOut
	raw, ok := res.StructuredContent.(json.RawMessage)
	if !ok {
		// Over the wire, StructuredContent decodes to a generic value; re-marshal.
		b, mErr := json.Marshal(res.StructuredContent)
		if mErr != nil {
			t.Fatalf("marshal structured content: %v", mErr)
		}
		raw = b
	}
	if err := json.Unmarshal(raw, &out); err != nil {
		t.Fatalf("unmarshal output: %v", err)
	}
	if out.Total != 1 || len(out.Resources) != 1 || out.Resources[0].Filter != "platform:'Windows'" {
		t.Errorf("got %+v, want the filter echoed back", out)
	}
}
