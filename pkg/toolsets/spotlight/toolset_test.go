package spotlight

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/spotlight_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockSpotlightAPI is a hand-written mock satisfying the narrow SpotlightAPI
// interface. Each field lets a test supply a canned response or error for the
// operation, and captures the params the toolset actually sent.
type mockSpotlightAPI struct {
	resp *spotlight_vulnerabilities.CombinedQueryVulnerabilitiesOK
	err  error
	got  *spotlight_vulnerabilities.CombinedQueryVulnerabilitiesParams
}

func (m *mockSpotlightAPI) CombinedQueryVulnerabilities(p *spotlight_vulnerabilities.CombinedQueryVulnerabilitiesParams, _ ...spotlight_vulnerabilities.ClientOption) (*spotlight_vulnerabilities.CombinedQueryVulnerabilitiesOK, error) {
	m.got = p
	return m.resp, m.err
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

func vulnsOK(vulns ...*models.DomainBaseAPIVulnerabilityV2) *spotlight_vulnerabilities.CombinedQueryVulnerabilitiesOK {
	return &spotlight_vulnerabilities.CombinedQueryVulnerabilitiesOK{
		Payload: &models.DomainSPAPICombinedVulnerabilitiesResponse{Resources: vulns},
	}
}

func strPtr(s string) *string { return &s }
func int64Ptr(i int64) *int64 { return &i }

func TestSearchVulnerabilitiesSuccess(t *testing.T) {
	vulnID := "vuln-abc-123"
	aid := "sensor-abc"
	cid := "customer-xyz"
	status := "open"
	vuln := &models.DomainBaseAPIVulnerabilityV2{
		ID:     &vulnID,
		Aid:    &aid,
		Cid:    &cid,
		Status: &status,
	}
	mock := &mockSpotlightAPI{resp: vulnsOK(vuln)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchVulnerabilities(s, mock) },
		"falcon_search_vulnerabilities", map[string]any{
			"filter": "status:'open'",
			"limit":  float64(5),
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Result must be a JSON array with the full vulnerability resource.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 vulnerability, got %d", len(got))
	}
	if got[0]["id"] != "vuln-abc-123" {
		t.Errorf("expected id 'vuln-abc-123', got %v", got[0]["id"])
	}
	if got[0]["status"] != "open" {
		t.Errorf("expected status 'open', got %v", got[0]["status"])
	}

	// Params should reflect the input.
	if mock.got == nil {
		t.Fatal("CombinedQueryVulnerabilities was not called")
	}
	if mock.got.Filter != "status:'open'" {
		t.Errorf("filter not passed correctly: %q", mock.got.Filter)
	}
	if mock.got.Limit == nil || *mock.got.Limit != 5 {
		t.Errorf("limit not passed correctly: %v", mock.got.Limit)
	}
}

func TestSearchVulnerabilitiesEmpty(t *testing.T) {
	mock := &mockSpotlightAPI{resp: vulnsOK()} // no vulns
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchVulnerabilities(s, mock) },
		"falcon_search_vulnerabilities", map[string]any{"filter": "status:'closed'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

func TestSearchVulnerabilitiesFQLError(t *testing.T) {
	mock := &mockSpotlightAPI{err: runtime.NewAPIError("combinedQueryVulnerabilities", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchVulnerabilities(s, mock) },
		"falcon_search_vulnerabilities", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	// FQL error branch must include the guide.
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchVulnerabilities403Scopes(t *testing.T) {
	mock := &mockSpotlightAPI{err: spotlight_vulnerabilities.NewCombinedQueryVulnerabilitiesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchVulnerabilities(s, mock) },
		"falcon_search_vulnerabilities", map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Vulnerabilities:read") {
		t.Errorf("expected required scope Vulnerabilities:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 5000: 5000, 9999: 5000}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

func TestSearchVulnerabilitiesFacetPagination(t *testing.T) {
	vulnID := "vuln-page2"
	aid := "sensor-1"
	cid := "cid-1"
	vuln := &models.DomainBaseAPIVulnerabilityV2{ID: &vulnID, Aid: &aid, Cid: &cid}
	mock := &mockSpotlightAPI{resp: vulnsOK(vuln)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchVulnerabilities(s, mock) },
		"falcon_search_vulnerabilities", map[string]any{
			"facet": "cve",
			"after": "token-xyz",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 result, got %d", len(got))
	}

	// Verify facet and after were forwarded.
	if mock.got == nil {
		t.Fatal("CombinedQueryVulnerabilities was not called")
	}
	if len(mock.got.Facet) != 1 || mock.got.Facet[0] != "cve" {
		t.Errorf("facet not forwarded correctly: %v", mock.got.Facet)
	}
	if mock.got.After == nil || *mock.got.After != "token-xyz" {
		t.Errorf("after token not forwarded correctly: %v", mock.got.After)
	}
}

// helper functions

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func contains(s, sub string) bool {
	return len(s) >= len(sub) && indexOf(s, sub) >= 0
}

func indexOf(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}
