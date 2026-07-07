package custom_ioa

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	goioa "github.com/crowdstrike/gofalcon/falcon/client/custom_ioa"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockCustomIOAAPI is a hand-written mock satisfying the narrow CustomIOAAPI
// interface. Each field lets a test supply a canned response or error, and
// captures the params the toolset actually sent.
type mockCustomIOAAPI struct {
	queryRuleGroupsFullResp *goioa.QueryRuleGroupsFullOK
	queryRuleGroupsFullErr  error
	queryRuleGroupsFullGot  *goioa.QueryRuleGroupsFullParams

	queryPlatformsResp *goioa.QueryPlatformsMixin0OK
	queryPlatformsErr  error

	getPlatformsResp *goioa.GetPlatformsMixin0OK
	getPlatformsErr  error
	getPlatformsGot  *goioa.GetPlatformsMixin0Params

	queryRuleTypesResp *goioa.QueryRuleTypesOK
	queryRuleTypesErr  error

	getRuleTypesResp *goioa.GetRuleTypesOK
	getRuleTypesErr  error
	getRuleTypesGot  *goioa.GetRuleTypesParams

	createRuleGroupResp *goioa.CreateRuleGroupMixin0Created
	createRuleGroupErr  error
	createRuleGroupGot  *goioa.CreateRuleGroupMixin0Params

	updateRuleGroupResp *goioa.UpdateRuleGroupMixin0OK
	updateRuleGroupErr  error
	updateRuleGroupGot  *goioa.UpdateRuleGroupMixin0Params

	deleteRuleGroupsResp *goioa.DeleteRuleGroupsMixin0OK
	deleteRuleGroupsErr  error
	deleteRuleGroupsGot  *goioa.DeleteRuleGroupsMixin0Params

	createRuleResp *goioa.CreateRuleCreated
	createRuleErr  error
	createRuleGot  *goioa.CreateRuleParams

	updateRulesV2Resp *goioa.UpdateRulesV2OK
	updateRulesV2Err  error
	updateRulesV2Got  *goioa.UpdateRulesV2Params

	deleteRulesResp *goioa.DeleteRulesOK
	deleteRulesErr  error
	deleteRulesGot  *goioa.DeleteRulesParams
}

func (m *mockCustomIOAAPI) QueryRuleGroupsFull(p *goioa.QueryRuleGroupsFullParams, _ ...goioa.ClientOption) (*goioa.QueryRuleGroupsFullOK, error) {
	m.queryRuleGroupsFullGot = p
	return m.queryRuleGroupsFullResp, m.queryRuleGroupsFullErr
}

func (m *mockCustomIOAAPI) QueryPlatformsMixin0(p *goioa.QueryPlatformsMixin0Params, _ ...goioa.ClientOption) (*goioa.QueryPlatformsMixin0OK, error) {
	return m.queryPlatformsResp, m.queryPlatformsErr
}

func (m *mockCustomIOAAPI) GetPlatformsMixin0(p *goioa.GetPlatformsMixin0Params, _ ...goioa.ClientOption) (*goioa.GetPlatformsMixin0OK, error) {
	m.getPlatformsGot = p
	return m.getPlatformsResp, m.getPlatformsErr
}

func (m *mockCustomIOAAPI) QueryRuleTypes(p *goioa.QueryRuleTypesParams, _ ...goioa.ClientOption) (*goioa.QueryRuleTypesOK, error) {
	return m.queryRuleTypesResp, m.queryRuleTypesErr
}

func (m *mockCustomIOAAPI) GetRuleTypes(p *goioa.GetRuleTypesParams, _ ...goioa.ClientOption) (*goioa.GetRuleTypesOK, error) {
	m.getRuleTypesGot = p
	return m.getRuleTypesResp, m.getRuleTypesErr
}

func (m *mockCustomIOAAPI) CreateRuleGroupMixin0(p *goioa.CreateRuleGroupMixin0Params, _ ...goioa.ClientOption) (*goioa.CreateRuleGroupMixin0Created, error) {
	m.createRuleGroupGot = p
	return m.createRuleGroupResp, m.createRuleGroupErr
}

func (m *mockCustomIOAAPI) UpdateRuleGroupMixin0(p *goioa.UpdateRuleGroupMixin0Params, _ ...goioa.ClientOption) (*goioa.UpdateRuleGroupMixin0OK, error) {
	m.updateRuleGroupGot = p
	return m.updateRuleGroupResp, m.updateRuleGroupErr
}

func (m *mockCustomIOAAPI) DeleteRuleGroupsMixin0(p *goioa.DeleteRuleGroupsMixin0Params, _ ...goioa.ClientOption) (*goioa.DeleteRuleGroupsMixin0OK, error) {
	m.deleteRuleGroupsGot = p
	return m.deleteRuleGroupsResp, m.deleteRuleGroupsErr
}

func (m *mockCustomIOAAPI) CreateRule(p *goioa.CreateRuleParams, _ ...goioa.ClientOption) (*goioa.CreateRuleCreated, error) {
	m.createRuleGot = p
	return m.createRuleResp, m.createRuleErr
}

func (m *mockCustomIOAAPI) UpdateRulesV2(p *goioa.UpdateRulesV2Params, _ ...goioa.ClientOption) (*goioa.UpdateRulesV2OK, error) {
	m.updateRulesV2Got = p
	return m.updateRulesV2Resp, m.updateRulesV2Err
}

func (m *mockCustomIOAAPI) DeleteRules(p *goioa.DeleteRulesParams, _ ...goioa.ClientOption) (*goioa.DeleteRulesOK, error) {
	m.deleteRulesGot = p
	return m.deleteRulesResp, m.deleteRulesErr
}

// callTool wires a mock into a real MCP server and invokes the named tool,
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

// --- test helpers ---

func strPtr(s string) *string { return &s }

func ruleGroupsFullOK(groups ...*models.APIRuleGroupV1) *goioa.QueryRuleGroupsFullOK {
	return &goioa.QueryRuleGroupsFullOK{
		Payload: &models.APIRuleGroupsResponse{
			Resources: groups,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func msaQueryRespOK(ids ...string) *models.MsaQueryResponse {
	return &models.MsaQueryResponse{
		Resources: ids,
		Errors:    []*models.MsaAPIError{},
		Meta:      &models.MsaMetaInfo{},
	}
}

func platformsQueryOK(ids ...string) *goioa.QueryPlatformsMixin0OK {
	return &goioa.QueryPlatformsMixin0OK{
		Payload: msaQueryRespOK(ids...),
	}
}

func platformsGetOK(platforms ...*models.DomainPlatform) *goioa.GetPlatformsMixin0OK {
	return &goioa.GetPlatformsMixin0OK{
		Payload: &models.APIPlatformsResponse{
			Resources: platforms,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func ruleTypesQueryOK(ids ...string) *goioa.QueryRuleTypesOK {
	return &goioa.QueryRuleTypesOK{
		Payload: msaQueryRespOK(ids...),
	}
}

func ruleTypesGetOK(types ...*models.APIRuleTypeV1) *goioa.GetRuleTypesOK {
	return &goioa.GetRuleTypesOK{
		Payload: &models.APIRuleTypesResponse{
			Resources: types,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func ruleGroupCreatedOK(groups ...*models.APIRuleGroupV1) *goioa.CreateRuleGroupMixin0Created {
	return &goioa.CreateRuleGroupMixin0Created{
		Payload: &models.APIRuleGroupsResponse{
			Resources: groups,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func ruleGroupUpdatedOK(groups ...*models.APIRuleGroupV1) *goioa.UpdateRuleGroupMixin0OK {
	return &goioa.UpdateRuleGroupMixin0OK{
		Payload: &models.APIRuleGroupsResponse{
			Resources: groups,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func ruleCreatedOK(rules ...*models.APIRuleV1) *goioa.CreateRuleCreated {
	return &goioa.CreateRuleCreated{
		Payload: &models.APIRulesResponse{
			Resources: rules,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func rulesV2UpdatedOK(rules ...*models.APIRuleV1) *goioa.UpdateRulesV2OK {
	return &goioa.UpdateRulesV2OK{
		Payload: &models.APIRulesResponse{
			Resources: rules,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func deleteRulesOK() *goioa.DeleteRulesOK {
	return &goioa.DeleteRulesOK{
		Payload: &models.MsaReplyMetaOnly{
			Meta: &models.MsaMetaInfo{},
		},
	}
}

// parseJSON decodes the tool result text into a map or slice.
func parseJSON(t *testing.T, text string) any {
	t.Helper()
	var out any
	if err := json.Unmarshal([]byte(text), &out); err != nil {
		t.Fatalf("JSON unmarshal: %v\ntext: %s", err, text)
	}
	return out
}

func parseMap(t *testing.T, text string) map[string]any {
	t.Helper()
	var out map[string]any
	if err := json.Unmarshal([]byte(text), &out); err != nil {
		t.Fatalf("JSON unmarshal as map: %v\ntext: %s", err, text)
	}
	return out
}

func parseSlice(t *testing.T, text string) []any {
	t.Helper()
	var out []any
	if err := json.Unmarshal([]byte(text), &out); err != nil {
		t.Fatalf("JSON unmarshal as slice: %v\ntext: %s", err, text)
	}
	return out
}

// contains is a helper for substring checks on tool output.
func contains(s, substr string) bool {
	return strings.Contains(s, substr)
}

// ============================================================
// falcon_search_ioa_rule_groups
// ============================================================

func TestSearchIOARuleGroupsSuccess(t *testing.T) {
	groupID := "rg-1"
	platform := "windows"
	name := "Suspicious PowerShell"
	enabled := true
	group := &models.APIRuleGroupV1{
		ID:       &groupID,
		Platform: &platform,
		Name:     &name,
		Enabled:  &enabled,
	}
	mock := &mockCustomIOAAPI{queryRuleGroupsFullResp: ruleGroupsFullOK(group)}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOARuleGroups(s, mock) },
		"falcon_search_ioa_rule_groups",
		map[string]any{"filter": "platform:'windows'", "limit": float64(5)},
	)

	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}

	// Params assertions.
	got := mock.queryRuleGroupsFullGot
	if got == nil {
		t.Fatal("no params captured")
	}
	if got.Filter == nil || *got.Filter != "platform:'windows'" {
		t.Errorf("unexpected filter: %v", got.Filter)
	}
	if got.Limit == nil || *got.Limit != 5 {
		t.Errorf("unexpected limit: %v", got.Limit)
	}
}

func TestSearchIOARuleGroupsEmpty(t *testing.T) {
	mock := &mockCustomIOAAPI{queryRuleGroupsFullResp: ruleGroupsFullOK()}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOARuleGroups(s, mock) },
		"falcon_search_ioa_rule_groups",
		map[string]any{},
	)

	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := parseMap(t, text)
	if _, ok := got["results"]; !ok {
		t.Errorf("expected 'results' key for empty response, got: %v", got)
	}
	if total, _ := got["total"].(float64); total != 0 {
		t.Errorf("expected total=0, got %v", total)
	}
}

func TestSearchIOARuleGroupsFQLError(t *testing.T) {
	mock := &mockCustomIOAAPI{
		queryRuleGroupsFullErr: runtime.NewAPIError("QueryRuleGroupsFull", "bad filter", 400),
	}
	filter := "invalid%%fql"

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOARuleGroups(s, mock) },
		"falcon_search_ioa_rule_groups",
		map[string]any{"filter": filter},
	)

	if isErr {
		t.Fatalf("unexpected protocol-level error: %s", text)
	}
	got := parseMap(t, text)
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, keys: %v", keysOf(got))
	}
	guide, _ := got["fql_guide"].(string)
	if len(guide) < 50 {
		t.Errorf("fql_guide too short: %q", guide)
	}
	if !contains(text, filter) {
		t.Errorf("expected filter_used in response, got: %s", text)
	}
}

func TestSearchIOARuleGroups403Scopes(t *testing.T) {
	mock := &mockCustomIOAAPI{
		queryRuleGroupsFullErr: goioa.NewQueryRuleGroupsFullForbidden(),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOARuleGroups(s, mock) },
		"falcon_search_ioa_rule_groups",
		map[string]any{},
	)

	if isErr {
		t.Fatalf("unexpected protocol-level error: %s", text)
	}
	if !contains(text, "Custom IOA Rules") {
		t.Errorf("expected Custom IOA Rules scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ============================================================
// falcon_get_ioa_platforms
// ============================================================

func TestGetIOAPlatformsSuccess(t *testing.T) {
	name := "windows"
	platform := &models.DomainPlatform{Name: &name}

	mock := &mockCustomIOAAPI{
		queryPlatformsResp: platformsQueryOK("windows"),
		getPlatformsResp:   platformsGetOK(platform),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerGetIOAPlatforms(s, mock) },
		"falcon_get_ioa_platforms",
		map[string]any{},
	)

	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 platform, got %d", len(results))
	}
	// Verify IDs were passed through to the get call.
	if mock.getPlatformsGot == nil {
		t.Fatal("GetPlatformsMixin0 not called")
	}
	if len(mock.getPlatformsGot.Ids) != 1 || mock.getPlatformsGot.Ids[0] != "windows" {
		t.Errorf("unexpected IDs passed to GetPlatformsMixin0: %v", mock.getPlatformsGot.Ids)
	}
}

func TestGetIOAPlatformsEmpty(t *testing.T) {
	mock := &mockCustomIOAAPI{
		queryPlatformsResp: platformsQueryOK(), // no IDs
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerGetIOAPlatforms(s, mock) },
		"falcon_get_ioa_platforms",
		map[string]any{},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 0 {
		t.Errorf("expected empty slice, got %d items", len(results))
	}
}

// ============================================================
// falcon_get_ioa_rule_types
// ============================================================

func TestGetIOARuleTypesSuccess(t *testing.T) {
	typeID := "rt-1"
	name := "Process Creation"
	ruleType := &models.APIRuleTypeV1{ID: &typeID, Name: &name}

	mock := &mockCustomIOAAPI{
		queryRuleTypesResp: ruleTypesQueryOK("rt-1"),
		getRuleTypesResp:   ruleTypesGetOK(ruleType),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerGetIOARuleTypes(s, mock) },
		"falcon_get_ioa_rule_types",
		map[string]any{},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 rule type, got %d", len(results))
	}
	if mock.getRuleTypesGot == nil {
		t.Fatal("GetRuleTypes not called")
	}
}

// ============================================================
// falcon_create_ioa_rule_group
// ============================================================

func TestCreateIOARuleGroupSuccess(t *testing.T) {
	groupID := "rg-new"
	platform := "windows"
	name := "Test Group"
	group := &models.APIRuleGroupV1{ID: &groupID, Platform: &platform, Name: &name}

	mock := &mockCustomIOAAPI{
		createRuleGroupResp: ruleGroupCreatedOK(group),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateIOARuleGroup(s, mock) },
		"falcon_create_ioa_rule_group",
		map[string]any{
			"name":        "Test Group",
			"platform":    "windows",
			"description": "A test group",
			"comment":     "creating for tests",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}

	// Body assertions.
	got := mock.createRuleGroupGot
	if got == nil || got.Body == nil {
		t.Fatal("no params/body captured")
	}
	if *got.Body.Name != "Test Group" {
		t.Errorf("unexpected name: %s", *got.Body.Name)
	}
	if *got.Body.Platform != "windows" {
		t.Errorf("unexpected platform: %s", *got.Body.Platform)
	}
	if *got.Body.Description != "A test group" {
		t.Errorf("unexpected description: %s", *got.Body.Description)
	}
	if *got.Body.Comment != "creating for tests" {
		t.Errorf("unexpected comment: %s", *got.Body.Comment)
	}
}

func TestCreateIOARuleGroupNoOptionals(t *testing.T) {
	groupID := "rg-2"
	platform := "linux"
	name := "Minimal Group"
	group := &models.APIRuleGroupV1{ID: &groupID, Platform: &platform, Name: &name}

	mock := &mockCustomIOAAPI{
		createRuleGroupResp: ruleGroupCreatedOK(group),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateIOARuleGroup(s, mock) },
		"falcon_create_ioa_rule_group",
		map[string]any{
			"name":     "Minimal Group",
			"platform": "linux",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	got := mock.createRuleGroupGot
	if got == nil || got.Body == nil {
		t.Fatal("no params/body captured")
	}
	// Optional fields should be empty strings (not nil) to satisfy model.
	if got.Body.Comment == nil {
		t.Errorf("comment should be non-nil (empty string), got nil")
	}
	if got.Body.Description == nil {
		t.Errorf("description should be non-nil (empty string), got nil")
	}
}

// ============================================================
// falcon_update_ioa_rule_group
// ============================================================

func TestUpdateIOARuleGroupSuccess(t *testing.T) {
	groupID := "rg-1"
	platform := "windows"
	name := "Updated Group"
	group := &models.APIRuleGroupV1{ID: &groupID, Platform: &platform, Name: &name}

	mock := &mockCustomIOAAPI{
		updateRuleGroupResp: ruleGroupUpdatedOK(group),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerUpdateIOARuleGroup(s, mock) },
		"falcon_update_ioa_rule_group",
		map[string]any{
			"id":                "rg-1",
			"rulegroup_version": float64(3),
			"name":              "Updated Group",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}

	got := mock.updateRuleGroupGot
	if got == nil || got.Body == nil {
		t.Fatal("no params/body captured")
	}
	if *got.Body.ID != "rg-1" {
		t.Errorf("unexpected ID: %s", *got.Body.ID)
	}
	if *got.Body.RulegroupVersion != 3 {
		t.Errorf("unexpected version: %d", *got.Body.RulegroupVersion)
	}
	if *got.Body.Name != "Updated Group" {
		t.Errorf("unexpected name: %s", *got.Body.Name)
	}
}

// ============================================================
// falcon_delete_ioa_rule_groups
// ============================================================

func TestDeleteIOARuleGroupsSuccess(t *testing.T) {
	mock := &mockCustomIOAAPI{
		deleteRuleGroupsResp: &goioa.DeleteRuleGroupsMixin0OK{
			Payload: &models.MsaReplyMetaOnly{Meta: &models.MsaMetaInfo{}},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteIOARuleGroups(s, mock) },
		"falcon_delete_ioa_rule_groups",
		map[string]any{
			"ids":     []any{"rg-1", "rg-2"},
			"comment": "cleanup",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 0 {
		t.Errorf("expected empty slice on success, got %d items", len(results))
	}

	got := mock.deleteRuleGroupsGot
	if got == nil {
		t.Fatal("no params captured")
	}
	if len(got.Ids) != 2 {
		t.Errorf("expected 2 IDs, got %d", len(got.Ids))
	}
	if got.Comment == nil || *got.Comment != "cleanup" {
		t.Errorf("unexpected comment: %v", got.Comment)
	}
}

func TestDeleteIOARuleGroupsEmptyIDs(t *testing.T) {
	mock := &mockCustomIOAAPI{}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteIOARuleGroups(s, mock) },
		"falcon_delete_ioa_rule_groups",
		map[string]any{"ids": []any{}},
	)

	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "ids") {
		t.Errorf("expected ids validation error, got: %s", text)
	}
	// API should not have been called.
	if mock.deleteRuleGroupsGot != nil {
		t.Error("API should not have been called with empty IDs")
	}
}

// ============================================================
// falcon_create_ioa_rule
// ============================================================

func TestCreateIOARuleSuccess(t *testing.T) {
	ruleID := "rule-1"
	name := "Block cmd spawned from Office"
	rule := &models.APIRuleV1{InstanceID: &ruleID, Name: &name}

	mock := &mockCustomIOAAPI{
		createRuleResp: ruleCreatedOK(rule),
	}

	fvs := []any{
		map[string]any{
			"name":  "GrandparentImageFilename",
			"value": ".*\\\\winword\\.exe",
			"type":  "excludable",
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateIOARule(s, mock) },
		"falcon_create_ioa_rule",
		map[string]any{
			"rulegroup_id":     "rg-1",
			"name":             "Block cmd spawned from Office",
			"ruletype_id":      "rt-1",
			"disposition_id":   float64(10),
			"pattern_severity": "high",
			"field_values":     fvs,
			"description":      "Blocks cmd.exe",
			"comment":          "test rule",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}

	got := mock.createRuleGot
	if got == nil || got.Body == nil {
		t.Fatal("no params/body captured")
	}
	if *got.Body.RulegroupID != "rg-1" {
		t.Errorf("unexpected rulegroup_id: %s", *got.Body.RulegroupID)
	}
	if *got.Body.Name != "Block cmd spawned from Office" {
		t.Errorf("unexpected name: %s", *got.Body.Name)
	}
	if *got.Body.DispositionID != 10 {
		t.Errorf("unexpected disposition_id: %d", *got.Body.DispositionID)
	}
	if len(got.Body.FieldValues) != 1 {
		t.Errorf("expected 1 field value, got %d", len(got.Body.FieldValues))
	}
}

// ============================================================
// falcon_update_ioa_rule
// ============================================================

func TestUpdateIOARuleSuccess(t *testing.T) {
	ruleID := "rule-1"
	name := "Updated Rule"
	rule := &models.APIRuleV1{InstanceID: &ruleID, Name: &name}

	mock := &mockCustomIOAAPI{
		updateRulesV2Resp: rulesV2UpdatedOK(rule),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerUpdateIOARule(s, mock) },
		"falcon_update_ioa_rule",
		map[string]any{
			"rulegroup_id":      "rg-1",
			"rulegroup_version": float64(2),
			"instance_id":       "rule-1",
			"name":              "Updated Rule",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}

	got := mock.updateRulesV2Got
	if got == nil || got.Body == nil {
		t.Fatal("no params/body captured")
	}
	if *got.Body.RulegroupID != "rg-1" {
		t.Errorf("unexpected rulegroup_id: %s", *got.Body.RulegroupID)
	}
	if len(got.Body.RuleUpdates) != 1 {
		t.Fatalf("expected 1 rule_update, got %d", len(got.Body.RuleUpdates))
	}
	if *got.Body.RuleUpdates[0].InstanceID != "rule-1" {
		t.Errorf("unexpected instance_id: %s", *got.Body.RuleUpdates[0].InstanceID)
	}
	if *got.Body.RuleUpdates[0].Name != "Updated Rule" {
		t.Errorf("unexpected name: %s", *got.Body.RuleUpdates[0].Name)
	}
}

// ============================================================
// falcon_delete_ioa_rules
// ============================================================

func TestDeleteIOARulesSuccess(t *testing.T) {
	mock := &mockCustomIOAAPI{
		deleteRulesResp: deleteRulesOK(),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteIOARules(s, mock) },
		"falcon_delete_ioa_rules",
		map[string]any{
			"rule_group_id": "rg-1",
			"ids":           []any{"rule-1", "rule-2"},
			"comment":       "removing stale rules",
		},
	)

	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	results := parseSlice(t, text)
	if len(results) != 0 {
		t.Errorf("expected empty slice on success, got %d items", len(results))
	}

	got := mock.deleteRulesGot
	if got == nil {
		t.Fatal("no params captured")
	}
	if got.RuleGroupID != "rg-1" {
		t.Errorf("unexpected rule_group_id: %s", got.RuleGroupID)
	}
	if len(got.Ids) != 2 {
		t.Errorf("expected 2 IDs, got %d", len(got.Ids))
	}
	if got.Comment == nil || *got.Comment != "removing stale rules" {
		t.Errorf("unexpected comment: %v", got.Comment)
	}
}

func TestDeleteIOARulesEmptyIDs(t *testing.T) {
	mock := &mockCustomIOAAPI{}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteIOARules(s, mock) },
		"falcon_delete_ioa_rules",
		map[string]any{
			"rule_group_id": "rg-1",
			"ids":           []any{},
		},
	)

	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "ids") {
		t.Errorf("expected ids validation error, got: %s", text)
	}
	if mock.deleteRulesGot != nil {
		t.Error("API should not have been called with empty IDs")
	}
}

// ============================================================
// helpers
// ============================================================

func keysOf(m map[string]any) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}
