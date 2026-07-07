package shield

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"

	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/gofalcon/falcon/client/saas_security"
	"github.com/crowdstrike/gofalcon/falcon/models"
)

// --- mock ---

// mockShieldAPI is a hand-written mock satisfying the ShieldAPI interface.
// Each pair of (resp, err) fields lets a test supply canned responses.
// The "Got" field captures the params received for assertion.
type mockShieldAPI struct {
	checksResp *saas_security.GetSecurityChecksV3OK
	checksErr  error
	checksGot  *saas_security.GetSecurityChecksV3Params

	affectedResp *saas_security.GetSecurityCheckAffectedV3OK
	affectedErr  error

	metricsResp *saas_security.GetMetricsV3OK
	metricsErr  error

	complianceResp *saas_security.GetSecurityCheckComplianceV3OK
	complianceErr  error

	alertsResp *saas_security.GetAlertsV3OK
	alertsErr  error
	alertsGot  *saas_security.GetAlertsV3Params

	activityResp *saas_security.GetActivityMonitorV3OK
	activityErr  error

	usersResp *saas_security.GetUserInventoryV3OK
	usersErr  error

	devicesResp *saas_security.GetDeviceInventoryV3OK
	devicesErr  error

	appsResp *saas_security.GetAppInventoryOK
	appsErr  error

	appUsersResp *saas_security.GetAppInventoryUsersOK
	appUsersErr  error

	dataSharesResp *saas_security.GetAssetInventoryV3OK
	dataSharesErr  error

	integrationsResp *saas_security.GetIntegrationsV3OK
	integrationsErr  error

	systemUsersResp *saas_security.GetSystemUsersV3OK
	systemUsersErr  error

	supportedResp *saas_security.GetSupportedSaasV3OK
	supportedErr  error

	systemLogsResp *saas_security.GetSystemLogsV3OK
	systemLogsErr  error

	dismissCheckResp *saas_security.DismissSecurityCheckV3OK
	dismissCheckErr  error
	dismissCheckGot  *saas_security.DismissSecurityCheckV3Params

	dismissEntityResp *saas_security.DismissAffectedEntityV3OK
	dismissEntityErr  error
	dismissEntityGot  *saas_security.DismissAffectedEntityV3Params
}

func (m *mockShieldAPI) GetSecurityChecksV3(p *saas_security.GetSecurityChecksV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSecurityChecksV3OK, error) {
	m.checksGot = p
	return m.checksResp, m.checksErr
}
func (m *mockShieldAPI) GetSecurityCheckAffectedV3(p *saas_security.GetSecurityCheckAffectedV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSecurityCheckAffectedV3OK, error) {
	return m.affectedResp, m.affectedErr
}
func (m *mockShieldAPI) GetMetricsV3(p *saas_security.GetMetricsV3Params, _ ...saas_security.ClientOption) (*saas_security.GetMetricsV3OK, error) {
	return m.metricsResp, m.metricsErr
}
func (m *mockShieldAPI) GetSecurityCheckComplianceV3(p *saas_security.GetSecurityCheckComplianceV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSecurityCheckComplianceV3OK, error) {
	return m.complianceResp, m.complianceErr
}
func (m *mockShieldAPI) GetAlertsV3(p *saas_security.GetAlertsV3Params, _ ...saas_security.ClientOption) (*saas_security.GetAlertsV3OK, error) {
	m.alertsGot = p
	return m.alertsResp, m.alertsErr
}
func (m *mockShieldAPI) GetActivityMonitorV3(p *saas_security.GetActivityMonitorV3Params, _ ...saas_security.ClientOption) (*saas_security.GetActivityMonitorV3OK, error) {
	return m.activityResp, m.activityErr
}
func (m *mockShieldAPI) GetUserInventoryV3(p *saas_security.GetUserInventoryV3Params, _ ...saas_security.ClientOption) (*saas_security.GetUserInventoryV3OK, error) {
	return m.usersResp, m.usersErr
}
func (m *mockShieldAPI) GetDeviceInventoryV3(p *saas_security.GetDeviceInventoryV3Params, _ ...saas_security.ClientOption) (*saas_security.GetDeviceInventoryV3OK, error) {
	return m.devicesResp, m.devicesErr
}
func (m *mockShieldAPI) GetAppInventory(p *saas_security.GetAppInventoryParams, _ ...saas_security.ClientOption) (*saas_security.GetAppInventoryOK, error) {
	return m.appsResp, m.appsErr
}
func (m *mockShieldAPI) GetAppInventoryUsers(p *saas_security.GetAppInventoryUsersParams, _ ...saas_security.ClientOption) (*saas_security.GetAppInventoryUsersOK, error) {
	return m.appUsersResp, m.appUsersErr
}
func (m *mockShieldAPI) GetAssetInventoryV3(p *saas_security.GetAssetInventoryV3Params, _ ...saas_security.ClientOption) (*saas_security.GetAssetInventoryV3OK, error) {
	return m.dataSharesResp, m.dataSharesErr
}
func (m *mockShieldAPI) GetIntegrationsV3(p *saas_security.GetIntegrationsV3Params, _ ...saas_security.ClientOption) (*saas_security.GetIntegrationsV3OK, error) {
	return m.integrationsResp, m.integrationsErr
}
func (m *mockShieldAPI) GetSystemUsersV3(p *saas_security.GetSystemUsersV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSystemUsersV3OK, error) {
	return m.systemUsersResp, m.systemUsersErr
}
func (m *mockShieldAPI) GetSupportedSaasV3(p *saas_security.GetSupportedSaasV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSupportedSaasV3OK, error) {
	return m.supportedResp, m.supportedErr
}
func (m *mockShieldAPI) GetSystemLogsV3(p *saas_security.GetSystemLogsV3Params, _ ...saas_security.ClientOption) (*saas_security.GetSystemLogsV3OK, error) {
	return m.systemLogsResp, m.systemLogsErr
}
func (m *mockShieldAPI) DismissSecurityCheckV3(p *saas_security.DismissSecurityCheckV3Params, _ ...saas_security.ClientOption) (*saas_security.DismissSecurityCheckV3OK, error) {
	m.dismissCheckGot = p
	return m.dismissCheckResp, m.dismissCheckErr
}
func (m *mockShieldAPI) DismissAffectedEntityV3(p *saas_security.DismissAffectedEntityV3Params, _ ...saas_security.ClientOption) (*saas_security.DismissAffectedEntityV3OK, error) {
	m.dismissEntityGot = p
	return m.dismissEntityResp, m.dismissEntityErr
}

// --- test helper ---

// callTool wires a mock into a real MCP server and calls the named tool,
// returning the decoded JSON text content and the isError flag.
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

// --- canned response constructors ---

func strPtr(s string) *string { return &s }

func checksOK(checks ...*models.SecurityCheckWithComplianceGetSecurityChecks) *saas_security.GetSecurityChecksV3OK {
	return &saas_security.GetSecurityChecksV3OK{
		Payload: &models.GetSecurityChecks{Resources: checks},
	}
}

func alertsOK(alerts ...*models.AlertGetAlertsResponse) *saas_security.GetAlertsV3OK {
	return &saas_security.GetAlertsV3OK{
		Payload: &models.GetAlertsResponse{Resources: alerts},
	}
}

func appsOK(apps ...*models.AppAppInventory) *saas_security.GetAppInventoryOK {
	return &saas_security.GetAppInventoryOK{
		Payload: &models.AppInventory{Resources: apps},
	}
}

func dismissCheckOK(ids ...string) *saas_security.DismissSecurityCheckV3OK {
	return &saas_security.DismissSecurityCheckV3OK{
		Payload: &models.DismissSecurityCheck{Resources: ids},
	}
}

func dismissEntityOK() *saas_security.DismissAffectedEntityV3OK {
	return &saas_security.DismissAffectedEntityV3OK{
		Payload: &models.DismissAffected{},
	}
}

// --- helper predicates ---

func hasKey(t *testing.T, text, key string) {
	t.Helper()
	var m map[string]any
	if err := json.Unmarshal([]byte(text), &m); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	if _, ok := m[key]; !ok {
		t.Errorf("expected key %q in result, keys: %v", key, keysOf(m))
	}
}

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func containsStr(s, sub string) bool { return strings.Contains(s, sub) }

// =============================================================================
// falcon_search_shield_checks
// =============================================================================

func TestSearchShieldChecksSuccess(t *testing.T) {
	id := "check-001"
	name := "MFA Enforcement"
	status := "Failed"
	check := &models.SecurityCheckWithComplianceGetSecurityChecks{
		ID:     &id,
		Name:   &name,
		Status: &status,
	}
	mock := &mockShieldAPI{checksResp: checksOK(check)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{"status": "Failed"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 result, got %d", len(got))
	}
	if got[0]["id"] != "check-001" {
		t.Errorf("expected check id check-001, got %v", got[0]["id"])
	}
}

func TestSearchShieldChecksNormalizesImpact(t *testing.T) {
	mock := &mockShieldAPI{checksResp: checksOK()}
	// Call with lowercase impact — the API should receive "High" (title-case).
	callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{"impact": "high"})
	if mock.checksGot == nil {
		t.Fatal("expected API to be called")
	}
	if mock.checksGot.Impact == nil || *mock.checksGot.Impact != "High" {
		t.Errorf("expected normalized impact High, got %v", mock.checksGot.Impact)
	}
}

func TestSearchShieldChecksEmpty(t *testing.T) {
	mock := &mockShieldAPI{checksResp: checksOK()} // empty resources
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	// Empty result → query guide surfaced.
	hasKey(t, text, "query_guide")
	hasKey(t, text, "hint")
	var m map[string]any
	_ = json.Unmarshal([]byte(text), &m)
	hint, _ := m["hint"].(string)
	if !containsStr(hint, "No results") {
		t.Errorf("expected 'No results' hint, got %q", hint)
	}
}

func TestSearchShieldChecksErrorWithGuide(t *testing.T) {
	mock := &mockShieldAPI{checksErr: runtime.NewAPIError("GetSecurityChecksV3", "bad request", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{"status": "bogus"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	hasKey(t, text, "query_guide")
	if guide, _ := func() (string, bool) {
		var m map[string]any
		_ = json.Unmarshal([]byte(text), &m)
		s, ok := m["query_guide"].(string)
		return s, ok
	}(); len(guide) < 50 {
		t.Errorf("query_guide too short: %q", guide)
	}
}

func TestSearchShieldChecks403Scopes(t *testing.T) {
	mock := &mockShieldAPI{checksErr: saas_security.NewGetSecurityChecksV3Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{})
	if !containsStr(text, "SaaS Security:read") {
		t.Errorf("expected required scope SaaS Security:read in 403 result: %s", text)
	}
}

func TestSearchShieldChecksTransportError(t *testing.T) {
	mock := &mockShieldAPI{checksErr: errors.New("dial tcp: connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldChecks(s, mock) },
		"falcon_search_shield_checks", map[string]any{})
	if !containsStr(text, "Failed to search Shield security checks") {
		t.Errorf("expected error message in result: %s", text)
	}
}

// =============================================================================
// falcon_search_shield_alerts
// =============================================================================

func TestSearchShieldAlertsSuccess(t *testing.T) {
	alertID := "alert-xyz"
	alertType := "configuration_drift"
	alert := &models.AlertGetAlertsResponse{
		ID:        &alertID,
		AlertType: &alertType,
	}
	mock := &mockShieldAPI{alertsResp: alertsOK(alert)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldAlerts(s, mock) },
		"falcon_search_shield_alerts", map[string]any{"type": "configuration_drift"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "alert-xyz" {
		t.Fatalf("expected alert with id alert-xyz, got %s", text)
	}
}

func TestSearchShieldAlertsPassesParamsThrough(t *testing.T) {
	mock := &mockShieldAPI{alertsResp: alertsOK()}
	lastID := "cursor-42"
	callTool(t, func(s *mcp.Server) { registerSearchShieldAlerts(s, mock) },
		"falcon_search_shield_alerts", map[string]any{
			"last_id": lastID,
			"limit":   float64(5),
		})
	if mock.alertsGot == nil {
		t.Fatal("expected API to be called")
	}
	if mock.alertsGot.LastID == nil || *mock.alertsGot.LastID != lastID {
		t.Errorf("expected last_id %q, got %v", lastID, mock.alertsGot.LastID)
	}
	if mock.alertsGot.Limit == nil || *mock.alertsGot.Limit != 5 {
		t.Errorf("expected limit 5, got %v", mock.alertsGot.Limit)
	}
}

func TestSearchShieldAlertsEmpty(t *testing.T) {
	mock := &mockShieldAPI{alertsResp: alertsOK()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldAlerts(s, mock) },
		"falcon_search_shield_alerts", map[string]any{})
	hasKey(t, text, "query_guide")
}

func TestSearchShieldAlertsErrorWithGuide(t *testing.T) {
	mock := &mockShieldAPI{alertsErr: runtime.NewAPIError("GetAlertsV3", "bad params", 400)}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldAlerts(s, mock) },
		"falcon_search_shield_alerts", map[string]any{})
	hasKey(t, text, "query_guide")
	hasKey(t, text, "hint")
}

// =============================================================================
// falcon_dismiss_shield_check
// =============================================================================

func TestDismissShieldCheckWholeCheck(t *testing.T) {
	mock := &mockShieldAPI{dismissCheckResp: dismissCheckOK("check-001")}
	text, isErr := callTool(t, func(s *mcp.Server) { registerDismissShieldCheck(s, mock) },
		"falcon_dismiss_shield_check", map[string]any{
			"id":     "check-001",
			"reason": "accepted risk",
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	// Must have called DismissSecurityCheckV3, not DismissAffectedEntityV3.
	if mock.dismissCheckGot == nil {
		t.Fatal("expected DismissSecurityCheckV3 to be called")
	}
	if mock.dismissEntityGot != nil {
		t.Error("DismissAffectedEntityV3 should NOT be called when entities is omitted")
	}
	// Verify the params.
	if mock.dismissCheckGot.ID != "check-001" {
		t.Errorf("expected ID check-001, got %q", mock.dismissCheckGot.ID)
	}
	if mock.dismissCheckGot.Body.Reason != "accepted risk" {
		t.Errorf("expected reason 'accepted risk', got %q", mock.dismissCheckGot.Body.Reason)
	}
}

func TestDismissShieldCheckSpecificEntities(t *testing.T) {
	mock := &mockShieldAPI{dismissEntityResp: dismissEntityOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerDismissShieldCheck(s, mock) },
		"falcon_dismiss_shield_check", map[string]any{
			"id":       "check-002",
			"reason":   "only affects test account",
			"entities": "user@example.com,admin@example.com",
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	// Must have called DismissAffectedEntityV3, not DismissSecurityCheckV3.
	if mock.dismissEntityGot == nil {
		t.Fatal("expected DismissAffectedEntityV3 to be called")
	}
	if mock.dismissCheckGot != nil {
		t.Error("DismissSecurityCheckV3 should NOT be called when entities is provided")
	}
	if mock.dismissEntityGot.ID != "check-002" {
		t.Errorf("expected ID check-002, got %q", mock.dismissEntityGot.ID)
	}
	if mock.dismissEntityGot.Body.Entities != "user@example.com,admin@example.com" {
		t.Errorf("expected entities, got %q", mock.dismissEntityGot.Body.Entities)
	}
	if mock.dismissEntityGot.Body.Reason != "only affects test account" {
		t.Errorf("expected reason, got %q", mock.dismissEntityGot.Body.Reason)
	}
}

func TestDismissShieldCheckError(t *testing.T) {
	mock := &mockShieldAPI{dismissCheckErr: saas_security.NewDismissSecurityCheckV3Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerDismissShieldCheck(s, mock) },
		"falcon_dismiss_shield_check", map[string]any{
			"id":     "check-001",
			"reason": "test",
		})
	if !containsStr(text, "SaaS Security:write") {
		t.Errorf("expected required scope SaaS Security:write in 403 result: %s", text)
	}
}

// =============================================================================
// falcon_search_shield_apps (inventory tool, table-driven)
// =============================================================================

func TestSearchShieldAppsSuccess(t *testing.T) {
	itemID := "integ-1|||app-42"
	appName := "Slack OAuth"
	app := &models.AppAppInventory{
		ItemID:  &itemID,
		AppName: &appName,
	}
	mock := &mockShieldAPI{appsResp: appsOK(app)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldApps(s, mock) },
		"falcon_search_shield_apps", map[string]any{"type": "oauth"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["item_id"] != "integ-1|||app-42" {
		t.Fatalf("expected app with item_id integ-1|||app-42, got %s", text)
	}
}

func TestSearchShieldAppsEmpty(t *testing.T) {
	mock := &mockShieldAPI{appsResp: appsOK()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldApps(s, mock) },
		"falcon_search_shield_apps", map[string]any{})
	hasKey(t, text, "query_guide")
}

func TestSearchShieldAppsError(t *testing.T) {
	mock := &mockShieldAPI{appsErr: errors.New("network error")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchShieldApps(s, mock) },
		"falcon_search_shield_apps", map[string]any{})
	hasKey(t, text, "query_guide")
	if !containsStr(text, "Failed to search Shield apps") {
		t.Errorf("expected error message, got %s", text)
	}
}

// =============================================================================
// Remaining tools — success + empty table-driven smoke tests
// =============================================================================

func TestGetShieldCheckAffectedEntitiesSuccess(t *testing.T) {
	entityName := "user@example.com"
	entity := &models.AffectedEntityGetAffected{EntityName: &entityName}
	mock := &mockShieldAPI{
		affectedResp: &saas_security.GetSecurityCheckAffectedV3OK{
			Payload: &models.GetAffected{Resources: []*models.AffectedEntityGetAffected{entity}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldCheckAffectedEntities(s, mock) },
		"falcon_get_shield_check_affected_entities", map[string]any{"id": "check-001"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "user@example.com") {
		t.Errorf("expected entity name in result, got %s", text)
	}
}

func TestGetShieldCheckAffectedEntitiesEmpty(t *testing.T) {
	mock := &mockShieldAPI{
		affectedResp: &saas_security.GetSecurityCheckAffectedV3OK{
			Payload: &models.GetAffected{},
		},
	}
	text, _ := callTool(t, func(s *mcp.Server) { registerGetShieldCheckAffectedEntities(s, mock) },
		"falcon_get_shield_check_affected_entities", map[string]any{"id": "check-001"})
	hasKey(t, text, "query_guide")
}

func TestGetShieldPostureMetricsSuccess(t *testing.T) {
	accountID := "acct-1"
	metric := &models.SecurityCheckMetricsGetMetrics{AccountID: &accountID}
	mock := &mockShieldAPI{
		metricsResp: &saas_security.GetMetricsV3OK{
			Payload: &models.GetMetrics{Resources: []*models.SecurityCheckMetricsGetMetrics{metric}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldPostureMetrics(s, mock) },
		"falcon_get_shield_posture_metrics", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) == 0 {
		t.Fatalf("expected at least one metric, got empty")
	}
}

func TestGetShieldCheckComplianceSuccess(t *testing.T) {
	exposureID := "exp-soc2"
	comp := &models.CriteriaGetSecurityCompliance{ExposureID: &exposureID, Criteria: []map[string]*string{{"framework": strPtr("SOC 2")}}}
	mock := &mockShieldAPI{
		complianceResp: &saas_security.GetSecurityCheckComplianceV3OK{
			Payload: &models.GetSecurityCompliance{
				Resources: []*models.CriteriaGetSecurityCompliance{comp},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldCheckCompliance(s, mock) },
		"falcon_get_shield_check_compliance", map[string]any{"id": "check-001"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "SOC 2") {
		t.Errorf("expected framework in result, got %s", text)
	}
}

func TestGetShieldActivityMonitorSuccess(t *testing.T) {
	resultVal := "login"
	activity := &models.Activity2GetActivityMonitor{
		Result: map[string]*string{"event_name": &resultVal},
	}
	mock := &mockShieldAPI{
		activityResp: &saas_security.GetActivityMonitorV3OK{
			Payload: &models.GetActivityMonitor{
				Resources: []*models.Activity2GetActivityMonitor{activity},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldActivityMonitor(s, mock) },
		"falcon_get_shield_activity_monitor", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "login") {
		t.Errorf("expected event name in result, got %s", text)
	}
}

func TestSearchShieldUsersSuccess(t *testing.T) {
	email := "alice@example.com"
	user := &models.UserGetUserInventory{Email: &email}
	mock := &mockShieldAPI{
		usersResp: &saas_security.GetUserInventoryV3OK{
			Payload: &models.GetUserInventory{
				Resources: []*models.UserGetUserInventory{user},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldUsers(s, mock) },
		"falcon_search_shield_users", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "alice@example.com") {
		t.Errorf("expected email in result, got %s", text)
	}
}

func TestSearchShieldDevicesSuccess(t *testing.T) {
	deviceName := "MacBook-Pro-Alice"
	device := &models.DeviceGetDeviceInventory{DeviceName: &deviceName}
	mock := &mockShieldAPI{
		devicesResp: &saas_security.GetDeviceInventoryV3OK{
			Payload: &models.GetDeviceInventory{
				Resources: []*models.DeviceGetDeviceInventory{device},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldDevices(s, mock) },
		"falcon_search_shield_devices", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "MacBook-Pro-Alice") {
		t.Errorf("expected device name in result, got %s", text)
	}
}

func TestGetShieldAppUsersSuccess(t *testing.T) {
	itemID := "integ-1|||app-1"
	userEmail := "bob@example.com"
	user := &models.AppUsersAppInventoryUsers{
		ItemID: &itemID,
		Users:  []*string{&userEmail},
	}
	mock := &mockShieldAPI{
		appUsersResp: &saas_security.GetAppInventoryUsersOK{
			Payload: &models.AppInventoryUsers{
				Resources: []*models.AppUsersAppInventoryUsers{user},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldAppUsers(s, mock) },
		"falcon_get_shield_app_users", map[string]any{"item_id": itemID})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "bob@example.com") {
		t.Errorf("expected user email in result, got %s", text)
	}
}

func TestSearchShieldDataSharesSuccess(t *testing.T) {
	resourceName := "Q3 Budget.xlsx"
	accountID := "acct-1"
	created := "2024-01-01"
	share := &models.AssetGetAssetInventory{
		ResourceName: &resourceName,
		AccountID:    &accountID,
		Created:      &created,
	}
	mock := &mockShieldAPI{
		dataSharesResp: &saas_security.GetAssetInventoryV3OK{
			Payload: &models.GetAssetInventory{
				Resources: []*models.AssetGetAssetInventory{share},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchShieldDataShares(s, mock) },
		"falcon_search_shield_data_shares", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "Q3 Budget.xlsx") {
		t.Errorf("expected resource name in result, got %s", text)
	}
}

func TestGetShieldIntegrationsSuccess(t *testing.T) {
	integID := "integ-slack-001"
	alias := "Slack Prod"
	enabled := true
	integ := &models.AccountIntegrationGetIntegrations{
		ID:      &integID,
		Alias:   &alias,
		Enabled: &enabled,
	}
	mock := &mockShieldAPI{
		integrationsResp: &saas_security.GetIntegrationsV3OK{
			Payload: &models.GetIntegrations{
				Resources: []*models.AccountIntegrationGetIntegrations{integ},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldIntegrations(s, mock) },
		"falcon_get_shield_integrations", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "integ-slack-001") {
		t.Errorf("expected integration id in result, got %s", text)
	}
}

func TestGetShieldSystemUsersSuccess(t *testing.T) {
	email := "admin@example.com"
	user := &models.SystemUserGetSystemUsers{Email: &email}
	mock := &mockShieldAPI{
		systemUsersResp: &saas_security.GetSystemUsersV3OK{
			Payload: &models.GetSystemUsers{
				Resources: []*models.SystemUserGetSystemUsers{user},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldSystemUsers(s, mock) },
		"falcon_get_shield_system_users", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "admin@example.com") {
		t.Errorf("expected admin email in result, got %s", text)
	}
}

func TestGetShieldSupportedSaasSuccess(t *testing.T) {
	saasName := "Slack"
	saasID := "saas-slack"
	saas := &models.SupportedIntegrationGetSupportedSaas{Name: &saasName, ID: &saasID}
	mock := &mockShieldAPI{
		supportedResp: &saas_security.GetSupportedSaasV3OK{
			Payload: &models.GetSupportedSaas{
				Resources: []*models.SupportedIntegrationGetSupportedSaas{saas},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldSupportedSaas(s, mock) },
		"falcon_get_shield_supported_saas", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "Slack") {
		t.Errorf("expected Slack in result, got %s", text)
	}
}

func TestGetShieldSystemLogsSuccess(t *testing.T) {
	action := "integration_created"
	accountID := "acct-1"
	log := &models.SystemLogGetSystemLogs{Action: &action, AccountID: &accountID}
	mock := &mockShieldAPI{
		systemLogsResp: &saas_security.GetSystemLogsV3OK{
			Payload: &models.GetSystemLogs{
				Resources: []*models.SystemLogGetSystemLogs{log},
			},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetShieldSystemLogs(s, mock) },
		"falcon_get_shield_system_logs", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !containsStr(text, "integration_created") {
		t.Errorf("expected event type in result, got %s", text)
	}
}

// =============================================================================
// normalizeImpact unit tests
// =============================================================================

func TestNormalizeImpact(t *testing.T) {
	cases := []struct {
		in   *string
		want *string
	}{
		{nil, nil},
		{strPtr("low"), strPtr("Low")},
		{strPtr("LOW"), strPtr("Low")},
		{strPtr("medium"), strPtr("Medium")},
		{strPtr("MEDIUM"), strPtr("Medium")},
		{strPtr("high"), strPtr("High")},
		{strPtr("HIGH"), strPtr("High")},
		{strPtr("unknown"), nil},
		{strPtr(""), nil},
	}
	for _, c := range cases {
		got := normalizeImpact(c.in)
		if c.want == nil && got != nil {
			t.Errorf("normalizeImpact(%v): expected nil, got %q", c.in, *got)
		} else if c.want != nil && (got == nil || *got != *c.want) {
			t.Errorf("normalizeImpact(%q): expected %q, got %v", *c.in, *c.want, got)
		}
	}
}

// =============================================================================
// normalizeLimit unit tests
// =============================================================================

func TestNormalizeLimitShield(t *testing.T) {
	cases := []struct {
		in, def, want int64
	}{
		{0, 10, 10},
		{-1, 10, 10},
		{1, 10, 1},
		{50, 10, 50},
		{100, 100, 100},
	}
	for _, c := range cases {
		if got := normalizeLimit(c.in, c.def); got != c.want {
			t.Errorf("normalizeLimit(%d, %d) = %d, want %d", c.in, c.def, got, c.want)
		}
	}
}

// =============================================================================
// parseDateTime unit tests
// =============================================================================

func TestParseDateTime(t *testing.T) {
	if parseDateTime(nil) != nil {
		t.Error("expected nil for nil input")
	}
	bad := strPtr("not-a-date")
	if parseDateTime(bad) != nil {
		t.Error("expected nil for unparseable input")
	}
	good := strPtr("2024-01-15T00:00:00.000Z")
	if got := parseDateTime(good); got == nil {
		t.Error("expected non-nil for valid ISO8601 date")
	}
}

// =============================================================================
// Toolset metadata
// =============================================================================

func TestToolsetMetadata(t *testing.T) {
	ts := Toolset{}
	if ts.GetName() != "shield" {
		t.Errorf("GetName() = %q, want shield", ts.GetName())
	}
	if ts.GetDescription() == "" {
		t.Error("GetDescription() is empty")
	}
	res := ts.GetResources()
	if len(res) != 1 {
		t.Fatalf("expected 1 resource, got %d", len(res))
	}
	if res[0].Resource.URI != queryGuideURI {
		t.Errorf("expected resource URI %q, got %q", queryGuideURI, res[0].Resource.URI)
	}
	if res[0].Resource.Name != "falcon_shield_query_guide" {
		t.Errorf("expected resource name falcon_shield_query_guide, got %q", res[0].Resource.Name)
	}
}
