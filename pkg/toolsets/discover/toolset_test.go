package discover

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/discover"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockDiscoverAPI is a hand-written mock satisfying the narrow DiscoverAPI
// interface. Each field lets a test supply a canned response or error for one
// operation, and captures the params the toolset actually sent.
type mockDiscoverAPI struct {
	appsResp *discover.CombinedApplicationsOK
	appsErr  error
	appsGot  *discover.CombinedApplicationsParams

	hostsResp *discover.CombinedHostsOK
	hostsErr  error
	hostsGot  *discover.CombinedHostsParams
}

func (m *mockDiscoverAPI) CombinedApplications(p *discover.CombinedApplicationsParams, _ ...discover.ClientOption) (*discover.CombinedApplicationsOK, error) {
	m.appsGot = p
	return m.appsResp, m.appsErr
}

func (m *mockDiscoverAPI) CombinedHosts(p *discover.CombinedHostsParams, _ ...discover.ClientOption) (*discover.CombinedHostsOK, error) {
	m.hostsGot = p
	return m.hostsResp, m.hostsErr
}

// callTool wires a mock into a real MCP server and calls the named tool,
// returning the decoded JSON text content.
func callTool(t *testing.T, register func(*mcp.Server), name string, args map[string]any) (string, bool) {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "0"}, nil)
	register(srv)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	defer cs.Close()

	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: name, Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("expected TextContent, got %T", res.Content[0])
	}
	return tc.Text, res.IsError
}

func appsOK(apps ...*models.DomainDiscoverAPIApplication) *discover.CombinedApplicationsOK {
	return &discover.CombinedApplicationsOK{
		Payload: &models.DomainDiscoverAPICombinedApplicationsResponse{Resources: apps},
	}
}

func hostsOK(hosts ...*models.DomainDiscoverAPIHost) *discover.CombinedHostsOK {
	return &discover.CombinedHostsOK{
		Payload: &models.DomainDiscoverAPICombinedHostsResponse{Resources: hosts},
	}
}

func strPtr(s string) *string { return &s }

// --- falcon_search_applications ---

func TestSearchApplicationsSuccess(t *testing.T) {
	appID := "app-1"
	app := &models.DomainDiscoverAPIApplication{ID: &appID, Name: "Chrome", Vendor: "Google"}
	mock := &mockDiscoverAPI{appsResp: appsOK(app)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchApplications(s, mock) },
		"falcon_search_applications", map[string]any{"filter": "name:'Chrome'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// The result must be the full resource list, not IDs (single-step search).
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "app-1" || got[0]["name"] != "Chrome" || got[0]["vendor"] != "Google" {
		t.Fatalf("expected full application details, got %s", text)
	}

	if mock.appsGot == nil || mock.appsGot.Filter != "name:'Chrome'" {
		t.Errorf("CombinedApplications not called with expected filter; got %+v", mock.appsGot)
	}
}

func TestSearchApplicationsEmpty(t *testing.T) {
	mock := &mockDiscoverAPI{appsResp: appsOK()} // no resources
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchApplications(s, mock) },
		"falcon_search_applications", map[string]any{"filter": "name:'nope'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

func TestSearchApplicationsFQLError(t *testing.T) {
	mock := &mockDiscoverAPI{appsErr: runtime.NewAPIError("CombinedApplications", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchApplications(s, mock) },
		"falcon_search_applications", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	// FQL error branch must include the guide.
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchApplicationsTransportError(t *testing.T) {
	mock := &mockDiscoverAPI{appsErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchApplications(s, mock) },
		"falcon_search_applications", map[string]any{"filter": "name:'x'"})
	if !contains(text, "Failed to search applications") {
		t.Errorf("expected error message, got %s", text)
	}
}

func TestSearchApplicationsFacet(t *testing.T) {
	mock := &mockDiscoverAPI{appsResp: appsOK()}
	_, _ = callTool(t, func(s *mcp.Server) { registerSearchApplications(s, mock) },
		"falcon_search_applications", map[string]any{"filter": "name:'x'", "facet": "host_info"})
	if mock.appsGot == nil || len(mock.appsGot.Facet) != 1 || mock.appsGot.Facet[0] != "host_info" {
		t.Errorf("expected facet [host_info] passed through, got %+v", mock.appsGot)
	}
}

// --- falcon_search_unmanaged_assets ---

func TestSearchUnmanagedAssetsSuccess(t *testing.T) {
	hostID := "host-1"
	host := &models.DomainDiscoverAPIHost{ID: &hostID, Hostname: "PC-1", EntityType: "unmanaged"}
	mock := &mockDiscoverAPI{hostsResp: hostsOK(host)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{"filter": "platform_name:'Windows'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "host-1" || got[0]["hostname"] != "PC-1" {
		t.Fatalf("expected full asset details, got %s", text)
	}
}

// TestSearchUnmanagedAssetsFilterComposition asserts that entity_type:'unmanaged'
// is always ANDed onto the user-supplied filter, matching the Python module's
// base_filter + "+" + filter composition.
func TestSearchUnmanagedAssetsFilterComposition(t *testing.T) {
	mock := &mockDiscoverAPI{hostsResp: hostsOK()}
	_, _ = callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{"filter": "platform_name:'Windows'"})

	want := "entity_type:'unmanaged'+platform_name:'Windows'"
	if mock.hostsGot == nil || mock.hostsGot.Filter != want {
		t.Errorf("expected composed filter %q, got %+v", want, mock.hostsGot)
	}
}

// TestSearchUnmanagedAssetsNoUserFilter asserts the base filter alone is sent
// when the caller supplies no filter at all.
func TestSearchUnmanagedAssetsNoUserFilter(t *testing.T) {
	mock := &mockDiscoverAPI{hostsResp: hostsOK()}
	_, _ = callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{})

	want := "entity_type:'unmanaged'"
	if mock.hostsGot == nil || mock.hostsGot.Filter != want {
		t.Errorf("expected base filter %q, got %+v", want, mock.hostsGot)
	}
}

func TestSearchUnmanagedAssetsEmpty(t *testing.T) {
	mock := &mockDiscoverAPI{hostsResp: hostsOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{"filter": "hostname:'nope'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	// filter_used must reflect the composed (entity_type-injected) filter.
	if got["filter_used"] != "entity_type:'unmanaged'+hostname:'nope'" {
		t.Errorf("unexpected filter_used: %v", got["filter_used"])
	}
}

func TestSearchUnmanagedAssetsFQLError(t *testing.T) {
	mock := &mockDiscoverAPI{hostsErr: runtime.NewAPIError("CombinedHosts", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchUnmanagedAssets403Scopes(t *testing.T) {
	mock := &mockDiscoverAPI{hostsErr: discover.NewCombinedHostsForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchUnmanagedAssets(s, mock) },
		"falcon_search_unmanaged_assets", map[string]any{})
	if !contains(text, "Assets:read") {
		t.Errorf("expected required scope Assets:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestNormalizeLimit(t *testing.T) {
	cases := []struct {
		limit, def, max, want int64
	}{
		{0, 100, 1000, 100},
		{-5, 100, 1000, 100},
		{1, 100, 1000, 1},
		{500, 100, 1000, 500},
		{1000, 100, 1000, 1000},
		{9999, 100, 1000, 1000},
		{0, 100, 5000, 100},
		{6000, 100, 5000, 5000},
	}
	for _, c := range cases {
		if got := normalizeLimit(c.limit, c.def, c.max); got != c.want {
			t.Errorf("normalizeLimit(%d,%d,%d) = %d, want %d", c.limit, c.def, c.max, got, c.want)
		}
	}
}

func TestComposeUnmanagedFilter(t *testing.T) {
	if got := composeUnmanagedFilter(nil); got != "entity_type:'unmanaged'" {
		t.Errorf("nil filter: got %q", got)
	}
	empty := ""
	if got := composeUnmanagedFilter(&empty); got != "entity_type:'unmanaged'" {
		t.Errorf("empty filter: got %q", got)
	}
	if got := composeUnmanagedFilter(strPtr("hostname:'PC-1'")); got != "entity_type:'unmanaged'+hostname:'PC-1'" {
		t.Errorf("non-empty filter: got %q", got)
	}
}

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func contains(s, sub string) bool {
	return len(s) >= len(sub) && (indexOf(s, sub) >= 0)
}

func indexOf(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}
