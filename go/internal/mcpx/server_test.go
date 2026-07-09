package mcpx

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

func testToolset() *toolsets.Toolset {
	return &toolsets.Toolset{
		Name:        "hosts",
		Description: "test hosts",
		Tools: []toolsets.Tool{
			toolsets.NewTool("falcon_search_hosts", "search hosts", toolsets.ReadOnly(),
				func(_ context.Context, in struct {
					Filter string `json:"filter,omitempty" jsonschema:"an FQL filter"`
				}) (any, error) {
					return []map[string]any{{"device_id": "abc", "filter": in.Filter}}, nil
				}),
			toolsets.NewTool("falcon_boom", "always errors", toolsets.ReadOnly(),
				func(_ context.Context, _ struct{}) (any, error) {
					return nil, errDomain
				}),
		},
		Resources: []toolsets.Resource{{
			URI:      "falcon://hosts/search/fql-guide",
			Name:     "falcon_search_hosts_fql_guide",
			MIMEType: "text/markdown",
			Text:     "# FQL guide\nsample content",
		}},
	}
}

var errDomain = &domainErr{"kaboom"}

type domainErr struct{ msg string }

func (e *domainErr) Error() string { return e.msg }

// connectInMemory wires a client to a server built from the given toolsets over
// the SDK's in-memory transport, returning a connected client session.
func connectInMemory(t *testing.T, sets []*toolsets.Toolset) *mcp.ClientSession {
	t.Helper()
	srv := NewServer("test-version")
	Register(srv, sets)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "test-client", Version: "0"}, nil)
	cs, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })
	return cs
}

func TestServer_ListsToolsWithAnnotationsAndSchema(t *testing.T) {
	cs := connectInMemory(t, []*toolsets.Toolset{testToolset()})
	res, err := cs.ListTools(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}

	byName := map[string]*mcp.Tool{}
	for _, tool := range res.Tools {
		byName[tool.Name] = tool
	}
	search := byName["falcon_search_hosts"]
	if search == nil {
		t.Fatal("falcon_search_hosts not listed")
	}
	if search.Annotations == nil || !search.Annotations.ReadOnlyHint {
		t.Fatalf("falcon_search_hosts should carry ReadOnlyHint, got %+v", search.Annotations)
	}
	if search.InputSchema == nil {
		t.Fatal("falcon_search_hosts has no InputSchema")
	}
	if search.OutputSchema != nil {
		t.Fatal("OutputSchema must stay nil (structured_output OFF)")
	}
}

func TestServer_CallToolReturnsJSONTextContent(t *testing.T) {
	cs := connectInMemory(t, []*toolsets.Toolset{testToolset()})
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_search_hosts",
		Arguments: map[string]any{"filter": "platform_name:'Windows'"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	if res.IsError {
		t.Fatalf("unexpected IsError: %+v", res.Content)
	}
	if len(res.Content) != 1 {
		t.Fatalf("want 1 content block, got %d", len(res.Content))
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("content is %T, want *mcp.TextContent", res.Content[0])
	}
	var payload []map[string]any
	if err := json.Unmarshal([]byte(tc.Text), &payload); err != nil {
		t.Fatalf("tool output is not JSON: %v (%q)", err, tc.Text)
	}
	if payload[0]["device_id"] != "abc" {
		t.Fatalf("unexpected payload: %v", payload)
	}
}

func TestServer_DomainErrorIsToolError(t *testing.T) {
	cs := connectInMemory(t, []*toolsets.Toolset{testToolset()})
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{Name: "falcon_boom"})
	if err != nil {
		t.Fatalf("CallTool returned a protocol error, want tool-level IsError: %v", err)
	}
	if !res.IsError {
		t.Fatal("domain error should set IsError=true")
	}
}

func TestServer_ListsResourcesWithExactURI(t *testing.T) {
	cs := connectInMemory(t, []*toolsets.Toolset{testToolset()})
	res, err := cs.ListResources(context.Background(), nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	var found *mcp.Resource
	for _, r := range res.Resources {
		if r.URI == "falcon://hosts/search/fql-guide" {
			found = r
		}
	}
	if found == nil {
		t.Fatal("FQL guide resource not listed with its exact URI")
	}

	read, err := cs.ReadResource(context.Background(), &mcp.ReadResourceParams{URI: "falcon://hosts/search/fql-guide"})
	if err != nil {
		t.Fatalf("ReadResource: %v", err)
	}
	if len(read.Contents) != 1 || read.Contents[0].Text == "" {
		t.Fatalf("resource read returned no text: %+v", read.Contents)
	}
	if read.Contents[0].MIMEType != "text/markdown" {
		t.Fatalf("MIMEType = %q, want text/markdown", read.Contents[0].MIMEType)
	}
}
