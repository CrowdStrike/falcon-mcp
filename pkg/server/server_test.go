package server

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
)

// newTestClient builds the server with a dummy FalconClient and connects an
// in-process MCP client to it, returning the connected client session.
func newTestClient(t *testing.T, opts Options) *mcp.ClientSession {
	t.Helper()

	fc, err := falcon.NewClient(context.Background(), falcon.Credentials{
		ClientID:     "test-id",
		ClientSecret: "test-secret",
		BaseURL:      "https://api.us-2.crowdstrike.com", // host override avoids autodiscovery network call
	}, false, "")
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	srv, _, _, err := Build(fc, opts)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server Connect: %v", err)
	}

	client := mcp.NewClient(&mcp.Implementation{Name: "test", Version: "0"}, nil)
	cs, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client Connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })
	return cs
}

// TestServerTools verifies the three server-level tools are registered and
// listable over the MCP protocol.
func TestServerTools(t *testing.T) {
	cs := newTestClient(t, Options{})

	res, err := cs.ListTools(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}

	got := map[string]bool{}
	for _, tool := range res.Tools {
		got[tool.Name] = true
	}

	for _, want := range []string{
		"falcon_list_enabled_modules",
		"falcon_check_connectivity",
		"falcon_list_modules",
	} {
		if !got[want] {
			t.Errorf("missing server-level tool %q; got tools: %v", want, keys(got))
		}
	}
}

// TestListModulesTool verifies the falcon_list_modules tool returns a modules
// array and that the result is unstructured JSON text (structured_output=False
// parity).
func TestListModulesTool(t *testing.T) {
	cs := newTestClient(t, Options{})

	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_list_modules",
		Arguments: map[string]any{},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	if res.IsError {
		t.Fatalf("tool returned error: %+v", res.Content)
	}
	if len(res.Content) != 1 {
		t.Fatalf("expected 1 content block, got %d", len(res.Content))
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("expected TextContent, got %T", res.Content[0])
	}
	var payload map[string][]string
	if err := json.Unmarshal([]byte(tc.Text), &payload); err != nil {
		t.Fatalf("result is not JSON: %v (text=%q)", err, tc.Text)
	}
	if _, ok := payload["modules"]; !ok {
		t.Errorf("result missing 'modules' key: %v", payload)
	}
}

func keys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
