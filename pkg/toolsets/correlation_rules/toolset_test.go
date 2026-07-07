package correlation_rules

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/correlation_rules"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockCorrelationRulesAPI is a hand-written mock satisfying the narrow
// CorrelationRulesAPI interface. Each field lets a test supply canned
// responses or errors for a single operation.
type mockCorrelationRulesAPI struct {
	searchResp *correlation_rules.CombinedRulesGetV2OK
	searchErr  error
	searchGot  *correlation_rules.CombinedRulesGetV2Params

	createResp *correlation_rules.EntitiesRulesPostV1OK
	createErr  error
	createGot  *correlation_rules.EntitiesRulesPostV1Params

	updateResp *correlation_rules.EntitiesRulesPatchV1OK
	updateErr  error
	updateGot  *correlation_rules.EntitiesRulesPatchV1Params

	deleteResp *correlation_rules.EntitiesRulesDeleteV1OK
	deleteErr  error
	deleteGot  *correlation_rules.EntitiesRulesDeleteV1Params
}

func (m *mockCorrelationRulesAPI) CombinedRulesGetV2(p *correlation_rules.CombinedRulesGetV2Params, _ ...correlation_rules.ClientOption) (*correlation_rules.CombinedRulesGetV2OK, error) {
	m.searchGot = p
	return m.searchResp, m.searchErr
}

func (m *mockCorrelationRulesAPI) EntitiesRulesPostV1(p *correlation_rules.EntitiesRulesPostV1Params, _ ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesPostV1OK, error) {
	m.createGot = p
	return m.createResp, m.createErr
}

func (m *mockCorrelationRulesAPI) EntitiesRulesPatchV1(p *correlation_rules.EntitiesRulesPatchV1Params, _ ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesPatchV1OK, error) {
	m.updateGot = p
	return m.updateResp, m.updateErr
}

func (m *mockCorrelationRulesAPI) EntitiesRulesDeleteV1(p *correlation_rules.EntitiesRulesDeleteV1Params, _ ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesDeleteV1OK, error) {
	m.deleteGot = p
	return m.deleteResp, m.deleteErr
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

// helpers for building mock responses

func strPtr(s string) *string { return &s }

func searchOK(rules ...*models.CorrelationrulesapiRuleV1) *correlation_rules.CombinedRulesGetV2OK {
	return &correlation_rules.CombinedRulesGetV2OK{
		Payload: &models.CorrelationrulesapiGetEntitiesRulesResponseV1{
			Resources: rules,
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func rulesRespOK(rules ...*models.CorrelationrulesapiRuleV1) *models.CorrelationrulesapiGetEntitiesRulesResponseV1 {
	return &models.CorrelationrulesapiGetEntitiesRulesResponseV1{
		Resources: rules,
		Meta:      &models.MsaMetaInfo{},
	}
}

// --- Tests ---

func TestSearchCorrelationRulesSuccess(t *testing.T) {
	name := "Suspicious PowerShell"
	rule := &models.CorrelationrulesapiRuleV1{
		RuleID: "rule-abc",
		Name:   &name,
	}
	mock := &mockCorrelationRulesAPI{searchResp: searchOK(rule)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCorrelationRules(s, mock) },
		"falcon_search_correlation_rules", map[string]any{"filter": "status:'active'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 rule, got %d", len(got))
	}
	if got[0]["rule_id"] != "rule-abc" {
		t.Errorf("expected rule_id=rule-abc, got %v", got[0]["rule_id"])
	}
	if got[0]["name"] != "Suspicious PowerShell" {
		t.Errorf("expected name=Suspicious PowerShell, got %v", got[0]["name"])
	}
}

func TestSearchCorrelationRulesEmpty(t *testing.T) {
	mock := &mockCorrelationRulesAPI{searchResp: searchOK()} // no rules
	filter := "status:'active'"
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCorrelationRules(s, mock) },
		"falcon_search_correlation_rules", map[string]any{"filter": filter})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	if got["results"] == nil {
		t.Error("expected results key in empty response")
	}
}

func TestSearchCorrelationRulesFQLError(t *testing.T) {
	mock := &mockCorrelationRulesAPI{
		searchErr: runtime.NewAPIError("CombinedRulesGetV2", "bad filter", 400),
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCorrelationRules(s, mock) },
		"falcon_search_correlation_rules", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchCorrelationRules403Scopes(t *testing.T) {
	mock := &mockCorrelationRulesAPI{
		searchErr: correlation_rules.NewCombinedRulesGetV2Forbidden(),
	}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchCorrelationRules(s, mock) },
		"falcon_search_correlation_rules", map[string]any{})
	if !contains(text, "Correlation Rules:read") {
		t.Errorf("expected required scope Correlation Rules:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestCreateCorrelationRuleSuccess(t *testing.T) {
	name := "New Rule"
	rule := &models.CorrelationrulesapiRuleV1{
		RuleID: "rule-new",
		Name:   &name,
	}
	mock := &mockCorrelationRulesAPI{
		createResp: &correlation_rules.EntitiesRulesPostV1OK{
			Payload: rulesRespOK(rule),
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateCorrelationRule(s, mock) },
		"falcon_create_correlation_rule", map[string]any{
			"customer_id":   "cid-123",
			"name":          "New Rule",
			"search_filter": "#event_simpleName=ProcessRollup2",
			"severity":      float64(70),
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["rule_id"] != "rule-new" {
		t.Errorf("unexpected create result: %s", text)
	}

	// Verify the body carried key fields.
	if mock.createGot == nil || mock.createGot.Body == nil {
		t.Fatal("EntitiesRulesPostV1 not called with a body")
	}
	body := mock.createGot.Body
	if *body.CustomerID != "cid-123" {
		t.Errorf("expected customer_id cid-123, got %q", *body.CustomerID)
	}
	if *body.Name != "New Rule" {
		t.Errorf("expected name 'New Rule', got %q", *body.Name)
	}
	if *body.Severity != 70 {
		t.Errorf("expected severity 70, got %d", *body.Severity)
	}
	if *body.Search.Filter != "#event_simpleName=ProcessRollup2" {
		t.Errorf("unexpected search filter: %q", *body.Search.Filter)
	}
}

func TestDeleteCorrelationRulesSuccess(t *testing.T) {
	mock := &mockCorrelationRulesAPI{
		deleteResp: &correlation_rules.EntitiesRulesDeleteV1OK{
			Payload: &models.MsaspecQueryResponse{
				Resources: []string{},
				Meta:      &models.MsaMetaInfo{},
			},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteCorrelationRules(s, mock) },
		"falcon_delete_correlation_rules", map[string]any{
			"ids": []any{"rule-1", "rule-2"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// On success, delete returns an empty list.
	var got []any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 0 {
		t.Errorf("expected empty list on success, got %v", got)
	}

	// Verify the IDs were passed.
	if mock.deleteGot == nil {
		t.Fatal("EntitiesRulesDeleteV1 not called")
	}
	if len(mock.deleteGot.Ids) != 2 || mock.deleteGot.Ids[0] != "rule-1" || mock.deleteGot.Ids[1] != "rule-2" {
		t.Errorf("unexpected ids passed to delete: %v", mock.deleteGot.Ids)
	}
}

func TestDeleteCorrelationRulesEmptyIDs(t *testing.T) {
	mock := &mockCorrelationRulesAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteCorrelationRules(s, mock) },
		"falcon_delete_correlation_rules", map[string]any{"ids": []any{}})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "ids") {
		t.Errorf("expected error mentioning ids, got: %s", text)
	}
	if mock.deleteGot != nil {
		t.Error("delete API should not be called for empty IDs")
	}
}

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 20, -1: 20, 1: 1, 20: 20, 500: 500, 999: 500}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- test helpers ---

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
