package mcpserver

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// --- test fixtures -----------------------------------------------------------

// searchIn/searchOut model a read-only search tool. Resources is a slice of
// objects (not strings) so its inferred output schema matches base's opaque-
// record override, which the internal server validates tool output against.
type searchIn struct {
	Filter string `json:"filter,omitempty" jsonschema:"FQL filter"`
	Limit  int    `json:"limit,omitempty" jsonschema:"max results"`
}
type resource struct {
	Filter string `json:"filter"`
}
type searchOut struct {
	Resources []resource `json:"resources"`
	Total     int        `json:"total"`
}

// updateIn/updateOut model a mutating tool.
type updateIn struct {
	ID string `json:"id" jsonschema:"entity id"`
}
type updateOut struct {
	Ok bool `json:"ok"`
}

// fakeToolModule registers one search tool and (optionally) one mutating/destructive
// tool, so tests can build a catalog without a live API.
type fakeToolModule struct {
	name        string
	withMutator bool
	withDelete  bool
}

func (m fakeToolModule) Name() string                    { return m.name }
func (m fakeToolModule) Description() string             { return "fake " + m.name + " module" }
func (m fakeToolModule) RegisterResources(_ *mcp.Server) {}
func (m fakeToolModule) RegisterPrompts(_ *mcp.Server)   {}

func (m fakeToolModule) RegisterTools(r base.Registrar) {
	base.AddTool(r, &mcp.Tool{
		Name:        "search_" + m.name,
		Description: "Search " + m.name + " using FQL.",
	}, func(_ context.Context, _ *mcp.CallToolRequest, in searchIn) (*mcp.CallToolResult, searchOut, error) {
		return nil, searchOut{Resources: []resource{{Filter: in.Filter}}, Total: 1}, nil
	})
	if m.withMutator {
		base.AddTool(r, &mcp.Tool{
			Name:        "update_" + m.name,
			Description: "Update " + m.name + ".",
			Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false},
		}, func(_ context.Context, _ *mcp.CallToolRequest, _ updateIn) (*mcp.CallToolResult, updateOut, error) {
			return nil, updateOut{Ok: true}, nil
		})
	}
	if m.withDelete {
		destructive := true
		base.AddTool(r, &mcp.Tool{
			Name:        "delete_" + m.name,
			Description: "Delete " + m.name + ".",
			Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, DestructiveHint: &destructive},
		}, func(_ context.Context, _ *mcp.CallToolRequest, _ updateIn) (*mcp.CallToolResult, updateOut, error) {
			return nil, updateOut{Ok: true}, nil
		})
	}
}

// buildCatalog builds a catalog from the given modules and connects its
// in-process session (so falcon_execute_tool can dispatch), returning the
// catalog and a MetaModule over it. The session is closed on test cleanup.
func buildCatalog(t *testing.T, modules ...fakeToolModule) *MetaModule {
	t.Helper()
	cat := NewCatalog()
	mods := make([]base.Module, 0, len(modules))
	for _, m := range modules {
		m.RegisterTools(cat.ForModule(m.Name()))
		mods = append(mods, m)
	}
	if err := cat.Connect(context.Background()); err != nil {
		t.Fatalf("catalog connect: %v", err)
	}
	t.Cleanup(func() { _ = cat.Close() })
	return NewMetaModule(cat, mods)
}

func callSearch(t *testing.T, m *MetaModule, in SearchToolsInput) SearchToolsResult {
	t.Helper()
	_, out, err := m.searchTools(context.Background(), nil, in)
	if err != nil {
		t.Fatalf("searchTools: %v", err)
	}
	return out
}

func toolNames(res SearchToolsResult) []string {
	names := make([]string, len(res.Tools))
	for i, s := range res.Tools {
		names[i] = s.Name
	}
	return names
}

// --- search ------------------------------------------------------------------

func TestSearchTools(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t,
		fakeToolModule{name: "hosts"},
		fakeToolModule{name: "detections", withMutator: true},
	)

	tests := []struct {
		name  string
		in    SearchToolsInput
		want  []string // expected tool names (order-independent membership)
		exact bool     // if true, require exactly this set
	}{
		{name: "empty query returns all", in: SearchToolsInput{}, want: []string{"falcon_search_hosts", "falcon_search_detections", "falcon_update_detections"}, exact: true},
		{name: "single token", in: SearchToolsInput{Query: "hosts"}, want: []string{"falcon_search_hosts"}, exact: true},
		{name: "multi token AND", in: SearchToolsInput{Query: "update detections"}, want: []string{"falcon_update_detections"}, exact: true},
		{name: "multi token AND no match", in: SearchToolsInput{Query: "update hosts"}, want: nil, exact: true},
		{name: "token matches param name", in: SearchToolsInput{Query: "filter"}, want: []string{"falcon_search_hosts", "falcon_search_detections"}, exact: true},
		{name: "module filter", in: SearchToolsInput{Module: "detections"}, want: []string{"falcon_search_detections", "falcon_update_detections"}, exact: true},
		{name: "module plus query", in: SearchToolsInput{Module: "detections", Query: "search"}, want: []string{"falcon_search_detections"}, exact: true},
		{name: "case insensitive", in: SearchToolsInput{Query: "HOSTS"}, want: []string{"falcon_search_hosts"}, exact: true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got := toolNames(callSearch(t, m, tt.in))
			if tt.exact {
				assertSameSet(t, got, tt.want)
			}
		})
	}
}

func TestSearchToolsLimit(t *testing.T) {
	t.Parallel()
	// Build 5 modules => 5 search tools.
	mods := []fakeToolModule{{name: "a"}, {name: "b"}, {name: "c"}, {name: "d"}, {name: "e"}}
	m := buildCatalog(t, mods...)

	tests := []struct {
		name     string
		limit    int
		wantSize int
	}{
		{name: "zero uses default 20", limit: 0, wantSize: 5}, // only 5 exist
		{name: "explicit truncates", limit: 2, wantSize: 2},
		{name: "negative clamps to 1", limit: -3, wantSize: 1},
		{name: "over max still bounded by count", limit: 500, wantSize: 5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got := callSearch(t, m, SearchToolsInput{Limit: tt.limit})
			if len(got.Tools) != tt.wantSize {
				t.Errorf("got %d tools, want %d", len(got.Tools), tt.wantSize)
			}
			if got.Total != len(got.Tools) {
				t.Errorf("Total = %d, want %d", got.Total, len(got.Tools))
			}
		})
	}
}

func TestSearchToolsNoMatchIsEmptyNotNil(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})
	got := callSearch(t, m, SearchToolsInput{Query: "nonexistent"})
	if got.Tools == nil {
		t.Fatal("Tools is nil, want empty slice")
	}
	if len(got.Tools) != 0 {
		t.Errorf("Tools len = %d, want 0", len(got.Tools))
	}
}

// --- annotation → flags ------------------------------------------------------

func TestSearchToolsAnnotationFlags(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "groups", withMutator: true, withDelete: true})
	got := callSearch(t, m, SearchToolsInput{})

	byName := map[string]ToolSummary{}
	for _, s := range got.Tools {
		byName[s.Name] = s
	}

	cases := []struct {
		name            string
		wantReadOnly    bool
		wantDestructive bool
	}{
		{"falcon_search_groups", true, false},
		{"falcon_update_groups", false, false},
		{"falcon_delete_groups", false, true},
	}
	for _, c := range cases {
		s, ok := byName[c.name]
		if !ok {
			t.Fatalf("tool %q missing from results", c.name)
		}
		if s.ReadOnly != c.wantReadOnly {
			t.Errorf("%s ReadOnly = %v, want %v", c.name, s.ReadOnly, c.wantReadOnly)
		}
		if s.Destructive != c.wantDestructive {
			t.Errorf("%s Destructive = %v, want %v", c.name, s.Destructive, c.wantDestructive)
		}
	}
}

// --- parameter summaries -----------------------------------------------------

func TestSearchToolsParameterSummaries(t *testing.T) {
	t.Parallel()
	// hosts has a search tool (all-optional params) and a mutating tool whose
	// "id" field is required (no omitempty).
	m := buildCatalog(t, fakeToolModule{name: "hosts", withMutator: true})
	got := callSearch(t, m, SearchToolsInput{})

	byName := map[string]ToolSummary{}
	for _, s := range got.Tools {
		byName[s.Name] = s
	}

	// search_hosts: filter and limit are optional.
	search := byName["falcon_search_hosts"]
	for _, p := range search.Parameters {
		if p.Required {
			t.Errorf("search param %q Required = true, want false", p.Name)
		}
	}

	// update_hosts: id is required.
	update := byName["falcon_update_hosts"]
	var sawID bool
	for _, p := range update.Parameters {
		if p.Name == "id" {
			sawID = true
			if !p.Required {
				t.Error("update param id Required = false, want true")
			}
		}
	}
	if !sawID {
		t.Fatalf("update_hosts params missing id: %+v", update.Parameters)
	}
}

// --- execute -----------------------------------------------------------------

func callExecute(t *testing.T, m *MetaModule, in ExecuteToolInput) *mcp.CallToolResult {
	t.Helper()
	res, _, err := m.executeTool(context.Background(), nil, in)
	if err != nil {
		t.Fatalf("executeTool protocol error: %v", err)
	}
	if res == nil {
		t.Fatal("executeTool returned nil result")
	}
	return res
}

func TestExecuteToolKnown(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})

	res := callExecute(t, m, ExecuteToolInput{
		ToolName:   "falcon_search_hosts",
		Parameters: map[string]any{"filter": "platform:'Windows'"},
	})
	if res.IsError {
		t.Fatalf("unexpected error result: %v", res.Content)
	}
	var out searchOut
	if err := decodeStructured(t, res.StructuredContent, &out); err != nil {
		t.Fatalf("decode structured content: %v", err)
	}
	if out.Total != 1 || len(out.Resources) != 1 || out.Resources[0].Filter != "platform:'Windows'" {
		t.Errorf("got %+v, want the filter echoed back", out)
	}
}

func TestExecuteToolAcceptsBareName(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})
	res := callExecute(t, m, ExecuteToolInput{ToolName: "search_hosts", Parameters: map[string]any{}})
	if res.IsError {
		t.Fatalf("bare name should resolve; got error: %v", res.Content)
	}
}

func TestExecuteToolUnknown(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})
	res := callExecute(t, m, ExecuteToolInput{ToolName: "falcon_nonexistent"})
	if !res.IsError {
		t.Fatal("expected IsError result for unknown tool")
	}
	text := contentText(t, res)
	if !strings.Contains(text, "falcon_search_tools") {
		t.Errorf("error text %q missing discovery hint", text)
	}
}

func TestExecuteToolEmptyParametersDefaultsToObject(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})
	// No parameters at all: should default to {} and succeed (all fields optional).
	res := callExecute(t, m, ExecuteToolInput{ToolName: "falcon_search_hosts"})
	if res.IsError {
		t.Fatalf("empty params should succeed; got error: %v", res.Content)
	}
}

func TestExecuteToolBadParamsEnriched(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"})
	// filter should be a string; passing a number fails schema validation.
	res := callExecute(t, m, ExecuteToolInput{
		ToolName:   "falcon_search_hosts",
		Parameters: map[string]any{"filter": 123},
	})
	if !res.IsError {
		t.Fatal("expected IsError result for bad params")
	}
	text := contentText(t, res)
	if !strings.Contains(text, "expected parameters") {
		t.Errorf("error text %q missing expected-parameters hint", text)
	}
	if !strings.Contains(text, "filter") {
		t.Errorf("error text %q missing param name", text)
	}
}

// --- list_enabled_modules ----------------------------------------------------

func TestListEnabledModules(t *testing.T) {
	t.Parallel()
	m := buildCatalog(t, fakeToolModule{name: "hosts"}, fakeToolModule{name: "detections"})
	_, out, err := m.listEnabledModules(context.Background(), nil, struct{}{})
	if err != nil {
		t.Fatalf("listEnabledModules: %v", err)
	}
	names := make([]string, len(out.Modules))
	for i, info := range out.Modules {
		names[i] = info.Name
		if info.Name == "dynamic" {
			t.Error("meta-module should not appear in enabled modules")
		}
		if info.Description == "" {
			t.Errorf("module %q has empty description", info.Name)
		}
	}
	assertSameSet(t, names, []string{"hosts", "detections"})
	if out.Total != 2 {
		t.Errorf("Total = %d, want 2", out.Total)
	}
}

// --- helpers -----------------------------------------------------------------

// decodeStructured decodes a CallToolResult.StructuredContent into v. Because
// execute_tool dispatches over the catalog's in-process (JSON) transport, the
// returned StructuredContent is a generic value, not a json.RawMessage; a
// re-marshal round-trips it into the concrete type.
func decodeStructured(t *testing.T, sc any, v any) error {
	t.Helper()
	b, err := json.Marshal(sc)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, v)
}

func contentText(t *testing.T, res *mcp.CallToolResult) string {
	t.Helper()
	if len(res.Content) == 0 {
		t.Fatal("no content")
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("Content[0] type = %T, want *mcp.TextContent", res.Content[0])
	}
	return tc.Text
}

func assertSameSet(t *testing.T, got, want []string) {
	t.Helper()
	if len(got) != len(want) {
		t.Fatalf("set size = %d %v, want %d %v", len(got), got, len(want), want)
	}
	seen := map[string]bool{}
	for _, g := range got {
		seen[g] = true
	}
	for _, w := range want {
		if !seen[w] {
			t.Errorf("missing %q in %v", w, got)
		}
	}
}

// --- through a real server ---------------------------------------------------

// TestExecuteToolThroughServer drives falcon_execute_tool over a real in-memory
// MCP server. Unlike the direct-call unit tests, this exercises the meta-tool's
// OWN input-schema validation — the path that rejected an object-typed
// parameters argument when Parameters was a json.RawMessage. It is the
// regression guard for that bug.
func TestExecuteToolThroughServer(t *testing.T) {
	t.Parallel()

	meta := buildCatalog(t, fakeToolModule{name: "hosts"})

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
