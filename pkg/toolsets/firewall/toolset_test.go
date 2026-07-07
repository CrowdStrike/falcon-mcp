package firewall

import (
	"context"
	"encoding/json"
	"testing"

	fwclient "github.com/crowdstrike/gofalcon/falcon/client/firewall_management"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockFirewallAPI is a hand-written mock satisfying the narrow FirewallAPI interface.
type mockFirewallAPI struct {
	queryRulesResp *fwclient.QueryRulesOK
	queryRulesErr  error
	queryRulesGot  *fwclient.QueryRulesParams

	getRulesResp *fwclient.GetRulesOK
	getRulesErr  error
	getRulesGot  *fwclient.GetRulesParams

	queryGroupsResp *fwclient.QueryRuleGroupsOK
	queryGroupsErr  error
	queryGroupsGot  *fwclient.QueryRuleGroupsParams

	getGroupsResp *fwclient.GetRuleGroupsOK
	getGroupsErr  error
	getGroupsGot  *fwclient.GetRuleGroupsParams

	queryPolicyResp *fwclient.QueryPolicyRulesOK
	queryPolicyErr  error
	queryPolicyGot  *fwclient.QueryPolicyRulesParams

	createResp *fwclient.CreateRuleGroupCreated
	createErr  error
	createGot  *fwclient.CreateRuleGroupParams

	deleteResp *fwclient.DeleteRuleGroupsOK
	deleteErr  error
	deleteGot  *fwclient.DeleteRuleGroupsParams
}

func (m *mockFirewallAPI) QueryRules(p *fwclient.QueryRulesParams, _ ...fwclient.ClientOption) (*fwclient.QueryRulesOK, error) {
	m.queryRulesGot = p
	return m.queryRulesResp, m.queryRulesErr
}

func (m *mockFirewallAPI) GetRules(p *fwclient.GetRulesParams, _ ...fwclient.ClientOption) (*fwclient.GetRulesOK, error) {
	m.getRulesGot = p
	return m.getRulesResp, m.getRulesErr
}

func (m *mockFirewallAPI) QueryRuleGroups(p *fwclient.QueryRuleGroupsParams, _ ...fwclient.ClientOption) (*fwclient.QueryRuleGroupsOK, error) {
	m.queryGroupsGot = p
	return m.queryGroupsResp, m.queryGroupsErr
}

func (m *mockFirewallAPI) GetRuleGroups(p *fwclient.GetRuleGroupsParams, _ ...fwclient.ClientOption) (*fwclient.GetRuleGroupsOK, error) {
	m.getGroupsGot = p
	return m.getGroupsResp, m.getGroupsErr
}

func (m *mockFirewallAPI) QueryPolicyRules(p *fwclient.QueryPolicyRulesParams, _ ...fwclient.ClientOption) (*fwclient.QueryPolicyRulesOK, error) {
	m.queryPolicyGot = p
	return m.queryPolicyResp, m.queryPolicyErr
}

func (m *mockFirewallAPI) CreateRuleGroup(p *fwclient.CreateRuleGroupParams, _ ...fwclient.ClientOption) (*fwclient.CreateRuleGroupCreated, error) {
	m.createGot = p
	return m.createResp, m.createErr
}

func (m *mockFirewallAPI) DeleteRuleGroups(p *fwclient.DeleteRuleGroupsParams, _ ...fwclient.ClientOption) (*fwclient.DeleteRuleGroupsOK, error) {
	m.deleteGot = p
	return m.deleteResp, m.deleteErr
}

// --- helpers ---

// callTool wires a mock into a real MCP server and calls the named tool.
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

func queryRulesOK(ids ...string) *fwclient.QueryRulesOK {
	return &fwclient.QueryRulesOK{Payload: &models.FwmgrAPIQueryResponse{Resources: ids}}
}

func getRulesOK(rules ...*models.FwmgrFirewallRuleV1) *fwclient.GetRulesOK {
	return &fwclient.GetRulesOK{Payload: &models.FwmgrAPIRulesResponse{Resources: rules}}
}

func queryGroupsOK(ids ...string) *fwclient.QueryRuleGroupsOK {
	return &fwclient.QueryRuleGroupsOK{Payload: &models.FwmgrAPIQueryResponse{Resources: ids}}
}

func getGroupsOK(groups ...*models.FwmgrAPIRuleGroupV1) *fwclient.GetRuleGroupsOK {
	return &fwclient.GetRuleGroupsOK{Payload: &models.FwmgrAPIRuleGroupsResponse{Resources: groups}}
}

func queryPolicyOK(ids ...string) *fwclient.QueryPolicyRulesOK {
	return &fwclient.QueryPolicyRulesOK{Payload: &models.FwmgrAPIQueryResponse{Resources: ids}}
}

// --- falcon_search_firewall_rules tests ---

func TestSearchFirewallRulesTwoStep(t *testing.T) {
	ruleID := "rule-001"
	enabled := true
	rule := &models.FwmgrFirewallRuleV1{ID: &ruleID, Enabled: &enabled}
	mock := &mockFirewallAPI{
		queryRulesResp: queryRulesOK("rule-001"),
		getRulesResp:   getRulesOK(rule),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallRules(s, mock) },
		"falcon_search_firewall_rules", map[string]any{"filter": "enabled:true"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Result must be full rule details, never just IDs.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "rule-001" {
		t.Fatalf("expected full rule details, got %s", text)
	}

	// Step 2 must have received the IDs from step 1.
	if mock.getRulesGot == nil || len(mock.getRulesGot.Ids) != 1 || mock.getRulesGot.Ids[0] != "rule-001" {
		t.Errorf("GetRules not called with queried ID; got %+v", mock.getRulesGot)
	}
}

func TestSearchFirewallRulesEmpty(t *testing.T) {
	mock := &mockFirewallAPI{queryRulesResp: queryRulesOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallRules(s, mock) },
		"falcon_search_firewall_rules", map[string]any{"filter": "platform:'none'"})
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
	if mock.getRulesGot != nil {
		t.Error("GetRules should not be called when no IDs matched")
	}
}

func TestSearchFirewallRulesFQLError(t *testing.T) {
	mock := &mockFirewallAPI{queryRulesErr: runtime.NewAPIError("QueryRules", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallRules(s, mock) },
		"falcon_search_firewall_rules", map[string]any{"filter": "bogus=="})
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

func TestSearchFirewallRules403Scopes(t *testing.T) {
	mock := &mockFirewallAPI{queryRulesErr: fwclient.NewQueryRulesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchFirewallRules(s, mock) },
		"falcon_search_firewall_rules", map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Firewall Management:read") {
		t.Errorf("expected required scope 'Firewall Management:read' in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// --- falcon_search_firewall_rule_groups tests ---

func TestSearchFirewallRuleGroupsTwoStep(t *testing.T) {
	groupID := "grp-001"
	groupName := "Test Group"
	group := &models.FwmgrAPIRuleGroupV1{ID: &groupID, Name: &groupName}
	mock := &mockFirewallAPI{
		queryGroupsResp: queryGroupsOK("grp-001"),
		getGroupsResp:   getGroupsOK(group),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallRuleGroups(s, mock) },
		"falcon_search_firewall_rule_groups", map[string]any{"filter": "enabled:true"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "grp-001" || got[0]["name"] != "Test Group" {
		t.Fatalf("expected full group details, got %s", text)
	}

	if mock.getGroupsGot == nil || len(mock.getGroupsGot.Ids) != 1 || mock.getGroupsGot.Ids[0] != "grp-001" {
		t.Errorf("GetRuleGroups not called with queried ID; got %+v", mock.getGroupsGot)
	}
}

func TestSearchFirewallRuleGroupsEmpty(t *testing.T) {
	mock := &mockFirewallAPI{queryGroupsResp: queryGroupsOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallRuleGroups(s, mock) },
		"falcon_search_firewall_rule_groups", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	if mock.getGroupsGot != nil {
		t.Error("GetRuleGroups should not be called when no IDs matched")
	}
}

// --- falcon_search_firewall_policy_rules tests ---

func TestSearchFirewallPolicyRulesTwoStep(t *testing.T) {
	ruleID := "pr-001"
	enabled := true
	rule := &models.FwmgrFirewallRuleV1{ID: &ruleID, Enabled: &enabled}
	mock := &mockFirewallAPI{
		queryPolicyResp: queryPolicyOK("pr-001"),
		getRulesResp:    getRulesOK(rule),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchFirewallPolicyRules(s, mock) },
		"falcon_search_firewall_policy_rules", map[string]any{"policy_id": "pol-xyz"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "pr-001" {
		t.Fatalf("expected full rule details, got %s", text)
	}

	// Policy ID must have been passed to QueryPolicyRules.
	if mock.queryPolicyGot == nil || mock.queryPolicyGot.ID == nil || *mock.queryPolicyGot.ID != "pol-xyz" {
		t.Errorf("QueryPolicyRules not called with policy_id; got %+v", mock.queryPolicyGot)
	}
	if mock.getRulesGot == nil || len(mock.getRulesGot.Ids) != 1 || mock.getRulesGot.Ids[0] != "pr-001" {
		t.Errorf("GetRules not called with policy rule ID; got %+v", mock.getRulesGot)
	}
}

// --- falcon_create_firewall_rule_group tests ---

func TestCreateFirewallRuleGroupSuccess(t *testing.T) {
	mock := &mockFirewallAPI{
		createResp: &fwclient.CreateRuleGroupCreated{
			Payload: &models.FwmgrAPIQueryResponse{Resources: []string{"grp-new-001"}},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateFirewallRuleGroup(s, mock) },
		"falcon_create_firewall_rule_group", map[string]any{
			"name":     "My Group",
			"platform": "windows",
			"clone_id": "src-grp-000",
			"comment":  "test creation",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0].(string) != "grp-new-001" {
		t.Fatalf("expected created group ID, got %s", text)
	}

	// Assert that the body was populated with the convenience fields.
	if mock.createGot == nil || mock.createGot.Body == nil {
		t.Fatal("CreateRuleGroup not called with a body")
	}
	if mock.createGot.Body.Name == nil || *mock.createGot.Body.Name != "My Group" {
		t.Errorf("expected name 'My Group', got %v", mock.createGot.Body.Name)
	}
	if mock.createGot.Body.Platform == nil || *mock.createGot.Body.Platform != "windows" {
		t.Errorf("expected platform 'windows', got %v", mock.createGot.Body.Platform)
	}
	// comment should have been passed as a query param.
	if mock.createGot.Comment == nil || *mock.createGot.Comment != "test creation" {
		t.Errorf("expected comment 'test creation', got %v", mock.createGot.Comment)
	}
}

func TestCreateFirewallRuleGroupWithCloneID(t *testing.T) {
	mock := &mockFirewallAPI{
		createResp: &fwclient.CreateRuleGroupCreated{
			Payload: &models.FwmgrAPIQueryResponse{Resources: []string{"grp-cloned"}},
		},
	}

	cloneID := "src-grp-001"
	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateFirewallRuleGroup(s, mock) },
		"falcon_create_firewall_rule_group", map[string]any{
			"name":     "Cloned Group",
			"platform": "linux",
			"clone_id": cloneID,
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	if mock.createGot.CloneID == nil || *mock.createGot.CloneID != cloneID {
		t.Errorf("expected clone_id %q, got %v", cloneID, mock.createGot.CloneID)
	}
	_ = text
}

func TestCreateFirewallRuleGroupMissingFields(t *testing.T) {
	mock := &mockFirewallAPI{}
	// Missing name and platform.
	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateFirewallRuleGroup(s, mock) },
		"falcon_create_firewall_rule_group", map[string]any{})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "name") && !contains(text, "platform") {
		t.Errorf("expected validation error about name/platform, got %s", text)
	}
	if mock.createGot != nil {
		t.Error("CreateRuleGroup should not be called when validation fails")
	}
}

// --- falcon_delete_firewall_rule_groups tests ---

func TestDeleteFirewallRuleGroupsSuccess(t *testing.T) {
	mock := &mockFirewallAPI{
		deleteResp: &fwclient.DeleteRuleGroupsOK{
			Payload: &models.FwmgrAPIQueryResponse{Resources: []string{"grp-001", "grp-002"}},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteFirewallRuleGroups(s, mock) },
		"falcon_delete_firewall_rule_groups", map[string]any{
			"ids":     []any{"grp-001", "grp-002"},
			"comment": "cleanup",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON object: %v (%s)", err, text)
	}
	if got["status"] != "deleted" {
		t.Errorf("expected status 'deleted', got %v", got["status"])
	}
	if got["count"].(float64) != 2 {
		t.Errorf("expected count 2, got %v", got["count"])
	}

	// IDs must have been passed down.
	if mock.deleteGot == nil || len(mock.deleteGot.Ids) != 2 ||
		mock.deleteGot.Ids[0] != "grp-001" || mock.deleteGot.Ids[1] != "grp-002" {
		t.Errorf("DeleteRuleGroups not called with correct IDs; got %+v", mock.deleteGot)
	}
	if mock.deleteGot.Comment == nil || *mock.deleteGot.Comment != "cleanup" {
		t.Errorf("expected comment 'cleanup', got %v", mock.deleteGot.Comment)
	}
}

func TestDeleteFirewallRuleGroupsEmptyIDs(t *testing.T) {
	mock := &mockFirewallAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteFirewallRuleGroups(s, mock) },
		"falcon_delete_firewall_rule_groups", map[string]any{"ids": []any{}})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "ids") {
		t.Errorf("expected validation error about ids, got %s", text)
	}
	if mock.deleteGot != nil {
		t.Error("DeleteRuleGroups should not be called with empty IDs")
	}
}

// --- normalizeLimit tests ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -1: 10, 1: 1, 10: 10, 5000: 5000, 9999: 5000}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- utility ---

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
