package recon

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/recon"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockReconAPI is a hand-written mock satisfying the narrow ReconAPI interface.
type mockReconAPI struct {
	// notifications
	notifQueryResp *recon.QueryNotificationsV1OK
	notifQueryErr  error
	notifQueryGot  *recon.QueryNotificationsV1Params

	notifDetailsResp *recon.GetNotificationsDetailedV1OK
	notifDetailsErr  error
	notifDetailsGot  *recon.GetNotificationsDetailedV1Params

	// rules
	rulesQueryResp *recon.QueryRulesV1OK
	rulesQueryErr  error
	rulesQueryGot  *recon.QueryRulesV1Params

	rulesDetailsResp *recon.GetRulesV1OK
	rulesDetailsErr  error
	rulesDetailsGot  *recon.GetRulesV1Params

	// exposed data records
	exposedQueryResp *recon.QueryNotificationsExposedDataRecordsV1OK
	exposedQueryErr  error
	exposedQueryGot  *recon.QueryNotificationsExposedDataRecordsV1Params

	exposedDetailsResp *recon.GetNotificationsExposedDataRecordsV1OK
	exposedDetailsErr  error
	exposedDetailsGot  *recon.GetNotificationsExposedDataRecordsV1Params
}

func (m *mockReconAPI) QueryNotificationsV1(p *recon.QueryNotificationsV1Params, _ ...recon.ClientOption) (*recon.QueryNotificationsV1OK, error) {
	m.notifQueryGot = p
	return m.notifQueryResp, m.notifQueryErr
}

func (m *mockReconAPI) GetNotificationsDetailedV1(p *recon.GetNotificationsDetailedV1Params, _ ...recon.ClientOption) (*recon.GetNotificationsDetailedV1OK, error) {
	m.notifDetailsGot = p
	return m.notifDetailsResp, m.notifDetailsErr
}

func (m *mockReconAPI) QueryRulesV1(p *recon.QueryRulesV1Params, _ ...recon.ClientOption) (*recon.QueryRulesV1OK, error) {
	m.rulesQueryGot = p
	return m.rulesQueryResp, m.rulesQueryErr
}

func (m *mockReconAPI) GetRulesV1(p *recon.GetRulesV1Params, _ ...recon.ClientOption) (*recon.GetRulesV1OK, error) {
	m.rulesDetailsGot = p
	return m.rulesDetailsResp, m.rulesDetailsErr
}

func (m *mockReconAPI) QueryNotificationsExposedDataRecordsV1(p *recon.QueryNotificationsExposedDataRecordsV1Params, _ ...recon.ClientOption) (*recon.QueryNotificationsExposedDataRecordsV1OK, error) {
	m.exposedQueryGot = p
	return m.exposedQueryResp, m.exposedQueryErr
}

func (m *mockReconAPI) GetNotificationsExposedDataRecordsV1(p *recon.GetNotificationsExposedDataRecordsV1Params, _ ...recon.ClientOption) (*recon.GetNotificationsExposedDataRecordsV1OK, error) {
	m.exposedDetailsGot = p
	return m.exposedDetailsResp, m.exposedDetailsErr
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

// --- helpers for building mock responses ---

func notifQueryOK(ids ...string) *recon.QueryNotificationsV1OK {
	return &recon.QueryNotificationsV1OK{
		Payload: &models.DomainQueryResponse{Resources: ids},
	}
}

func notifDetailsOK(notifs ...*models.DomainDetailedNotificationV1) *recon.GetNotificationsDetailedV1OK {
	return &recon.GetNotificationsDetailedV1OK{
		Payload: &models.DomainNotificationDetailsResponseV1{
			Resources: notifs,
			Errors:    []*models.DomainReconAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func rulesQueryOK(ids ...string) *recon.QueryRulesV1OK {
	return &recon.QueryRulesV1OK{
		Payload: &models.DomainRuleQueryResponseV1{Resources: ids},
	}
}

func rulesDetailsOK(rules ...*models.SadomainRule) *recon.GetRulesV1OK {
	return &recon.GetRulesV1OK{
		Payload: &models.DomainRulesEntitiesResponseV1{
			Resources: rules,
			Errors:    []*models.DomainReconAPIError{},
			Meta:      &models.DomainRuleMetaInfo{},
		},
	}
}

func exposedQueryOK(ids ...string) *recon.QueryNotificationsExposedDataRecordsV1OK {
	return &recon.QueryNotificationsExposedDataRecordsV1OK{
		Payload: &models.DomainQueryResponse{Resources: ids},
	}
}

func exposedDetailsOK(records ...*models.APINotificationExposedDataRecordV1) *recon.GetNotificationsExposedDataRecordsV1OK {
	return &recon.GetNotificationsExposedDataRecordsV1OK{
		Payload: &models.APINotificationExposedDataRecordEntitiesResponseV1{
			Resources: records,
			Errors:    []*models.DomainReconAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

// --- falcon_search_recon_notifications tests ---

func TestSearchReconNotificationsTwoStep(t *testing.T) {
	notifID := "notif-abc-123"
	notifIDField := notifID
	notifPayload := &models.DomainDetailedNotificationV1{ID: &notifIDField}

	mock := &mockReconAPI{
		notifQueryResp:   notifQueryOK("notif-abc-123"),
		notifDetailsResp: notifDetailsOK(notifPayload),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconNotifications(s, mock) },
		"falcon_search_recon_notifications",
		map[string]any{"filter": "status:'new'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "notif-abc-123" {
		t.Fatalf("expected full notification details with id=notif-abc-123, got %s", text)
	}

	// Step 2 must have received the IDs from step 1.
	if mock.notifDetailsGot == nil || len(mock.notifDetailsGot.Ids) != 1 || mock.notifDetailsGot.Ids[0] != "notif-abc-123" {
		t.Errorf("GetNotificationsDetailedV1 not called with queried ID; got %+v", mock.notifDetailsGot)
	}
}

func TestSearchReconNotificationsEmpty(t *testing.T) {
	mock := &mockReconAPI{notifQueryResp: notifQueryOK()} // no IDs
	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconNotifications(s, mock) },
		"falcon_search_recon_notifications",
		map[string]any{"filter": "status:'nope'"})
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
	if mock.notifDetailsGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchReconNotificationsFQLError(t *testing.T) {
	mock := &mockReconAPI{
		notifQueryErr: runtime.NewAPIError("QueryNotificationsV1", "bad filter", 400),
	}
	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconNotifications(s, mock) },
		"falcon_search_recon_notifications",
		map[string]any{"filter": "bogus=="})
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

func TestSearchReconNotifications403Scopes(t *testing.T) {
	mock := &mockReconAPI{
		notifQueryErr: recon.NewQueryNotificationsV1Forbidden(),
	}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconNotifications(s, mock) },
		"falcon_search_recon_notifications",
		map[string]any{})

	if !contains(text, "Monitoring rules (Falcon Intelligence Recon):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestSearchReconNotificationsTransportError(t *testing.T) {
	mock := &mockReconAPI{notifQueryErr: errors.New("connection refused")}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconNotifications(s, mock) },
		"falcon_search_recon_notifications",
		map[string]any{})
	if !contains(text, "Failed to search recon notifications") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- falcon_search_recon_rules tests ---

func TestSearchReconRulesTwoStep(t *testing.T) {
	ruleID := "rule-xyz-456"
	cid := "testcid"
	boolTrue := true
	boolFalse := false
	rule := &models.SadomainRule{
		Cid:                     &cid,
		BreachMonitorOnly:       &boolFalse,
		BreachMonitoringEnabled: &boolTrue,
	}

	mock := &mockReconAPI{
		rulesQueryResp:   rulesQueryOK(ruleID),
		rulesDetailsResp: rulesDetailsOK(rule),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconRules(s, mock) },
		"falcon_search_recon_rules",
		map[string]any{"filter": "status:'active'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 rule result, got %d: %s", len(got), text)
	}

	// Step 2 must have received the ID from step 1.
	if mock.rulesDetailsGot == nil || len(mock.rulesDetailsGot.Ids) != 1 || mock.rulesDetailsGot.Ids[0] != ruleID {
		t.Errorf("GetRulesV1 not called with queried ID; got %+v", mock.rulesDetailsGot)
	}
}

func TestSearchReconRulesEmpty(t *testing.T) {
	mock := &mockReconAPI{rulesQueryResp: rulesQueryOK()} // no IDs
	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconRules(s, mock) },
		"falcon_search_recon_rules",
		map[string]any{})
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
	if mock.rulesDetailsGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchReconRulesFQLError(t *testing.T) {
	mock := &mockReconAPI{
		rulesQueryErr: runtime.NewAPIError("QueryRulesV1", "bad filter", 400),
	}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconRules(s, mock) },
		"falcon_search_recon_rules",
		map[string]any{"filter": "bogus=="})

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
}

func TestSearchReconRules403Scopes(t *testing.T) {
	mock := &mockReconAPI{
		rulesQueryErr: recon.NewQueryRulesV1Forbidden(),
	}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconRules(s, mock) },
		"falcon_search_recon_rules",
		map[string]any{})

	if !contains(text, "Monitoring rules (Falcon Intelligence Recon):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
}

// --- falcon_search_recon_exposed_data_records tests ---

func TestSearchReconExposedDataRecordsTwoStep(t *testing.T) {
	recordID := "edr-record-789"
	author := "test-author"
	cid := "testcid"
	record := &models.APINotificationExposedDataRecordV1{
		Author: &author,
		Cid:    &cid,
	}

	mock := &mockReconAPI{
		exposedQueryResp:   exposedQueryOK(recordID),
		exposedDetailsResp: exposedDetailsOK(record),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconExposedDataRecords(s, mock) },
		"falcon_search_recon_exposed_data_records",
		map[string]any{"filter": "domain:'example.com'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 record result, got %d: %s", len(got), text)
	}

	// Step 2 must have received the ID from step 1.
	if mock.exposedDetailsGot == nil || len(mock.exposedDetailsGot.Ids) != 1 || mock.exposedDetailsGot.Ids[0] != recordID {
		t.Errorf("GetNotificationsExposedDataRecordsV1 not called with queried ID; got %+v", mock.exposedDetailsGot)
	}
}

func TestSearchReconExposedDataRecordsEmpty(t *testing.T) {
	mock := &mockReconAPI{exposedQueryResp: exposedQueryOK()} // no IDs
	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchReconExposedDataRecords(s, mock) },
		"falcon_search_recon_exposed_data_records",
		map[string]any{})
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
	if mock.exposedDetailsGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchReconExposedDataRecordsFQLError(t *testing.T) {
	mock := &mockReconAPI{
		exposedQueryErr: runtime.NewAPIError("QueryNotificationsExposedDataRecordsV1", "bad filter", 400),
	}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconExposedDataRecords(s, mock) },
		"falcon_search_recon_exposed_data_records",
		map[string]any{"filter": "bogus=="})

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
}

func TestSearchReconExposedDataRecords403Scopes(t *testing.T) {
	mock := &mockReconAPI{
		exposedQueryErr: recon.NewQueryNotificationsExposedDataRecordsV1Forbidden(),
	}
	text, _ := callTool(t,
		func(s *mcp.Server) { registerSearchReconExposedDataRecords(s, mock) },
		"falcon_search_recon_exposed_data_records",
		map[string]any{})

	if !contains(text, "Monitoring rules (Falcon Intelligence Recon):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
}

// --- normalizeLimit tests ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -1: 10, 1: 1, 10: 10, 500: 500, 501: 500, 9999: 500}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- test utilities ---

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
