package serverless

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/serverless_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockServerlessAPI is a hand-written mock satisfying the narrow
// ServerlessVulnerabilitiesAPI interface.
type mockServerlessAPI struct {
	resp    *serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFOK
	err     error
	gotParams *serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFParams
}

func (m *mockServerlessAPI) GetCombinedVulnerabilitiesSARIF(
	p *serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFParams,
	_ ...serverless_vulnerabilities.ClientOption,
) (*serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFOK, error) {
	m.gotParams = p
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

func sarifOK(runs ...*models.ModelsRun) *serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFOK {
	schema := "$schema"
	version := "2.1.0"
	return &serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFOK{
		Payload: &models.VulnerabilitiesVulnerabilityEntitySARIFResponse{
			Resources: []*models.ModelsVulnerabilitySARIF{
				{
					DollarSchema: &schema,
					Version:      &version,
					Runs:         runs,
				},
			},
		},
	}
}

func makeRun(toolName string) *models.ModelsRun {
	name := toolName
	return &models.ModelsRun{
		Tool: &models.ModelsRunTool{
			Driver: &models.ModelsRunToolDriver{Name: &name},
		},
	}
}

// TestSearchServerlessVulnerabilitiesSuccess verifies that a successful
// response returns the SARIF runs flattened from the resources list.
func TestSearchServerlessVulnerabilitiesSuccess(t *testing.T) {
	run := makeRun("CrowdStrike Falcon")
	mock := &mockServerlessAPI{resp: sarifOK(run)}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchServerlessVulnerabilities(s, mock) },
		"falcon_search_serverless_vulnerabilities",
		map[string]any{"filter": "cloud_provider:'aws'"},
	)
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Result must be a JSON array of runs.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 run, got %d: %s", len(got), text)
	}
	// Verify the filter was forwarded to the API.
	if mock.gotParams == nil || mock.gotParams.Filter == nil || *mock.gotParams.Filter != "cloud_provider:'aws'" {
		t.Errorf("unexpected filter passed to API: %+v", mock.gotParams)
	}
}

// TestSearchServerlessVulnerabilitiesEmpty verifies that when the payload
// contains no runs an EmptyResponse is returned (not an error).
func TestSearchServerlessVulnerabilitiesEmpty(t *testing.T) {
	// sarifOK with no runs → Resources[0].Runs is empty.
	mock := &mockServerlessAPI{resp: sarifOK()}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchServerlessVulnerabilities(s, mock) },
		"falcon_search_serverless_vulnerabilities",
		map[string]any{"filter": "severity:'CRITICAL'"},
	)
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v (%s)", err, text)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

// TestSearchServerlessVulnerabilitiesFQLError verifies that a 400 response
// includes the FQL guide for self-correction.
func TestSearchServerlessVulnerabilitiesFQLError(t *testing.T) {
	mock := &mockServerlessAPI{
		err: runtime.NewAPIError("GetCombinedVulnerabilitiesSARIF", "bad filter", 400),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchServerlessVulnerabilities(s, mock) },
		"falcon_search_serverless_vulnerabilities",
		map[string]any{"filter": "bogus=="},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v (%s)", err, text)
	}
	// FQL error branch must include the guide.
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

// TestSearchServerlessVulnerabilities403Scopes verifies that a 403 response
// surfaces the required API scopes and does not include an FQL guide.
func TestSearchServerlessVulnerabilities403Scopes(t *testing.T) {
	mock := &mockServerlessAPI{
		err: serverless_vulnerabilities.NewGetCombinedVulnerabilitiesSARIFForbidden(),
	}

	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchServerlessVulnerabilities(s, mock) },
		"falcon_search_serverless_vulnerabilities",
		map[string]any{"filter": "severity:'HIGH'"},
	)
	// 403 is not an FQL error → scopes should surface, no guide.
	if !contains(text, "Falcon Container Image:read") {
		t.Errorf("expected required scope Falcon Container Image:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// TestNormalizeLimit verifies limit clamping: 0 defaults to 10, negatives to
// 10, positive values pass through.
func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 5000: 5000}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- helpers ---

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
