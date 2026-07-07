package cases

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/case_management"
	"github.com/crowdstrike/gofalcon/falcon/client/cases"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// ---- mock for CasesAPI ----

type mockCasesAPI struct {
	queryResp *cases.QueriesCasesGetV1OK
	queryErr  error
	queryGot  *cases.QueriesCasesGetV1Params

	detailsResp *cases.EntitiesCasesPostV2OK
	detailsErr  error
	detailsGot  *cases.EntitiesCasesPostV2Params

	putResp *cases.EntitiesCasesPutV2Created
	putErr  error
	putGot  *cases.EntitiesCasesPutV2Params

	patchResp *cases.EntitiesCasesPatchV2OK
	patchErr  error
	patchGot  *cases.EntitiesCasesPatchV2Params

	alertEvidResp *cases.EntitiesAlertEvidencePostV1OK
	alertEvidErr  error

	eventEvidResp *cases.EntitiesEventEvidencePostV1OK
	eventEvidErr  error

	tagPostResp *cases.EntitiesCaseTagsPostV1OK
	tagPostErr  error
	tagPostGot  *cases.EntitiesCaseTagsPostV1Params

	tagDelResp *cases.EntitiesCaseTagsDeleteV1OK
	tagDelErr  error
	tagDelGot  *cases.EntitiesCaseTagsDeleteV1Params
}

func (m *mockCasesAPI) QueriesCasesGetV1(p *cases.QueriesCasesGetV1Params, _ ...cases.ClientOption) (*cases.QueriesCasesGetV1OK, error) {
	m.queryGot = p
	return m.queryResp, m.queryErr
}

func (m *mockCasesAPI) EntitiesCasesPostV2(p *cases.EntitiesCasesPostV2Params, _ ...cases.ClientOption) (*cases.EntitiesCasesPostV2OK, error) {
	m.detailsGot = p
	return m.detailsResp, m.detailsErr
}

func (m *mockCasesAPI) EntitiesCasesPutV2(p *cases.EntitiesCasesPutV2Params, _ ...cases.ClientOption) (*cases.EntitiesCasesPutV2Created, error) {
	m.putGot = p
	return m.putResp, m.putErr
}

func (m *mockCasesAPI) EntitiesCasesPatchV2(p *cases.EntitiesCasesPatchV2Params, _ ...cases.ClientOption) (*cases.EntitiesCasesPatchV2OK, error) {
	m.patchGot = p
	return m.patchResp, m.patchErr
}

func (m *mockCasesAPI) EntitiesAlertEvidencePostV1(p *cases.EntitiesAlertEvidencePostV1Params, _ ...cases.ClientOption) (*cases.EntitiesAlertEvidencePostV1OK, error) {
	return m.alertEvidResp, m.alertEvidErr
}

func (m *mockCasesAPI) EntitiesEventEvidencePostV1(p *cases.EntitiesEventEvidencePostV1Params, _ ...cases.ClientOption) (*cases.EntitiesEventEvidencePostV1OK, error) {
	return m.eventEvidResp, m.eventEvidErr
}

func (m *mockCasesAPI) EntitiesCaseTagsPostV1(p *cases.EntitiesCaseTagsPostV1Params, _ ...cases.ClientOption) (*cases.EntitiesCaseTagsPostV1OK, error) {
	m.tagPostGot = p
	return m.tagPostResp, m.tagPostErr
}

func (m *mockCasesAPI) EntitiesCaseTagsDeleteV1(p *cases.EntitiesCaseTagsDeleteV1Params, _ ...cases.ClientOption) (*cases.EntitiesCaseTagsDeleteV1OK, error) {
	m.tagDelGot = p
	return m.tagDelResp, m.tagDelErr
}

// ---- mock for CaseManagementAPI ----

type mockCaseMgmtAPI struct {
	queryResp   *case_management.QueriesTemplatesGetV1OK
	queryErr    error
	detailsResp *case_management.EntitiesTemplatesGetV1OK
	detailsErr  error
}

func (m *mockCaseMgmtAPI) QueriesTemplatesGetV1(p *case_management.QueriesTemplatesGetV1Params, _ ...case_management.ClientOption) (*case_management.QueriesTemplatesGetV1OK, error) {
	return m.queryResp, m.queryErr
}

func (m *mockCaseMgmtAPI) EntitiesTemplatesGetV1(p *case_management.EntitiesTemplatesGetV1Params, _ ...case_management.ClientOption) (*case_management.EntitiesTemplatesGetV1OK, error) {
	return m.detailsResp, m.detailsErr
}

// ---- helpers ----

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

func makeCaseOK(ids ...string) *cases.QueriesCasesGetV1OK {
	return &cases.QueriesCasesGetV1OK{
		Payload: &models.CasesapiGetQueriesCasesV1Response{Resources: ids},
	}
}

func makeCaseDetailsOK(cs ...*models.SdkCaseVM) *cases.EntitiesCasesPostV2OK {
	return &cases.EntitiesCasesPostV2OK{
		Payload: &models.OperationsGetCasesByIDsResponseVM{Resources: cs},
	}
}

func caseVM(id, name string) *models.SdkCaseVM {
	return &models.SdkCaseVM{ID: &id, Name: &name}
}

func makeUpdateOK(cs ...*models.SdkCaseVM) *models.OperationsUpdateCaseResponseVM {
	return &models.OperationsUpdateCaseResponseVM{Resources: cs}
}

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i >= 0
		}
	}
	return false
}

// ---- search_cases tests ----

func TestSearchCasesTwoStep(t *testing.T) {
	cv := caseVM("case-1", "Incident Alpha")
	mock := &mockCasesAPI{
		queryResp:   makeCaseOK("case-1"),
		detailsResp: makeCaseDetailsOK(cv),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCases(s, mock) },
		"falcon_search_cases", map[string]any{"filter": "status:'new'"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "case-1" || got[0]["name"] != "Incident Alpha" {
		t.Fatalf("unexpected result: %s", text)
	}
	// Details step must have been called with the queried ID.
	if mock.detailsGot == nil || len(mock.detailsGot.Body.Ids) != 1 || mock.detailsGot.Body.Ids[0] != "case-1" {
		t.Errorf("details step not called with correct ID; got %+v", mock.detailsGot)
	}
}

func TestSearchCasesEmpty(t *testing.T) {
	mock := &mockCasesAPI{queryResp: makeCaseOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCases(s, mock) },
		"falcon_search_cases", map[string]any{"filter": "status:'closed'"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	if mock.detailsGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchCasesFQLError(t *testing.T) {
	mock := &mockCasesAPI{queryErr: runtime.NewAPIError("QueriesCasesGetV1", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchCases(s, mock) },
		"falcon_search_cases", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got %v", got)
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short: %q", guide)
	}
}

func TestSearchCases403Scopes(t *testing.T) {
	mock := &mockCasesAPI{queryErr: cases.NewQueriesCasesGetV1Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchCases(s, mock) },
		"falcon_search_cases", map[string]any{})
	if !contains(text, "Cases:read") {
		t.Errorf("expected Cases:read scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ---- get_cases tests ----

func TestGetCasesSuccess(t *testing.T) {
	cv := caseVM("case-99", "Threat Hunt")
	mock := &mockCasesAPI{
		detailsResp: makeCaseDetailsOK(cv),
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetCases(s, mock) },
		"falcon_get_cases", map[string]any{"ids": []any{"case-99"}})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-99") {
		t.Errorf("expected case ID in result: %s", text)
	}
}

func TestGetCasesEmptyIDs(t *testing.T) {
	mock := &mockCasesAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetCases(s, mock) },
		"falcon_get_cases", map[string]any{"ids": []any{}})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
	if mock.detailsGot != nil {
		t.Error("no API call expected for empty IDs")
	}
}

// ---- create_case tests ----

func TestCreateCaseSuccess(t *testing.T) {
	id := "new-case-1"
	name := "New Incident"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		putResp: &cases.EntitiesCasesPutV2Created{
			Payload: &models.OperationsCreateCaseResponseVM{Resources: []*models.SdkCaseVM{cv}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateCase(s, mock) },
		"falcon_create_case", map[string]any{
			"name":     "New Incident",
			"severity": float64(75),
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "new-case-1") {
		t.Errorf("expected case ID in result: %s", text)
	}
	// Verify body was populated.
	if mock.putGot == nil || mock.putGot.Body == nil {
		t.Fatal("expected PUT call with body")
	}
	if *mock.putGot.Body.Name != "New Incident" {
		t.Errorf("name mismatch: got %q", *mock.putGot.Body.Name)
	}
	if *mock.putGot.Body.Severity != 75 {
		t.Errorf("severity mismatch: got %d", *mock.putGot.Body.Severity)
	}
}

func TestCreateCase403Scopes(t *testing.T) {
	mock := &mockCasesAPI{putErr: cases.NewEntitiesCasesPutV2Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerCreateCase(s, mock) },
		"falcon_create_case", map[string]any{
			"name":     "Test",
			"severity": float64(50),
		})
	if !contains(text, "Cases:write") {
		t.Errorf("expected Cases:write scope in 403 result: %s", text)
	}
}

// ---- update_case tests ----

func TestUpdateCaseSuccess(t *testing.T) {
	id := "case-5"
	name := "Updated"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		patchResp: &cases.EntitiesCasesPatchV2OK{
			Payload: makeUpdateOK(cv),
		},
	}
	newName := "Updated"
	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateCase(s, mock) },
		"falcon_update_case", map[string]any{
			"id":   "case-5",
			"name": newName,
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-5") {
		t.Errorf("expected case ID in result: %s", text)
	}
	if mock.patchGot == nil || mock.patchGot.Body == nil {
		t.Fatal("expected PATCH call with body")
	}
	if *mock.patchGot.Body.ID != "case-5" {
		t.Errorf("case ID mismatch: got %q", *mock.patchGot.Body.ID)
	}
	if *mock.patchGot.Body.Fields.Name != "Updated" {
		t.Errorf("name mismatch: got %q", *mock.patchGot.Body.Fields.Name)
	}
}

func TestUpdateCaseNoFields(t *testing.T) {
	mock := &mockCasesAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateCase(s, mock) },
		"falcon_update_case", map[string]any{"id": "case-x"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "at least one field") {
		t.Errorf("expected 'at least one field' message, got: %s", text)
	}
	if mock.patchGot != nil {
		t.Error("PATCH should not be called when no fields provided")
	}
}

// ---- manage_case_tags tests ----

func TestManageCaseTagsAdd(t *testing.T) {
	id := "case-t"
	name := "Tagged Case"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		tagPostResp: &cases.EntitiesCaseTagsPostV1OK{
			Payload: makeUpdateOK(cv),
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerManageCaseTags(s, mock) },
		"falcon_manage_case_tags", map[string]any{
			"id":     "case-t",
			"action": "add",
			"tags":   []any{"malware", "priority"},
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-t") {
		t.Errorf("expected case ID in result: %s", text)
	}
	if mock.tagPostGot == nil || mock.tagPostGot.Body == nil {
		t.Fatal("expected POST tags call")
	}
	if len(mock.tagPostGot.Body.Tags) != 2 {
		t.Errorf("expected 2 tags, got %d", len(mock.tagPostGot.Body.Tags))
	}
	if mock.tagDelGot != nil {
		t.Error("delete should not be called for add action")
	}
}

func TestManageCaseTagsRemove(t *testing.T) {
	id := "case-t"
	name := "Tagged Case"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		tagDelResp: &cases.EntitiesCaseTagsDeleteV1OK{
			Payload: makeUpdateOK(cv),
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerManageCaseTags(s, mock) },
		"falcon_manage_case_tags", map[string]any{
			"id":     "case-t",
			"action": "remove",
			"tags":   []any{"malware"},
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-t") {
		t.Errorf("expected case ID in result: %s", text)
	}
	if mock.tagDelGot == nil {
		t.Fatal("expected DELETE tags call")
	}
	if mock.tagDelGot.ID != "case-t" {
		t.Errorf("case ID mismatch: got %q", mock.tagDelGot.ID)
	}
	if len(mock.tagDelGot.Tag) != 1 || mock.tagDelGot.Tag[0] != "malware" {
		t.Errorf("tag mismatch: got %v", mock.tagDelGot.Tag)
	}
	if mock.tagPostGot != nil {
		t.Error("post should not be called for remove action")
	}
}

func TestManageCaseTagsInvalidAction(t *testing.T) {
	mock := &mockCasesAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerManageCaseTags(s, mock) },
		"falcon_manage_case_tags", map[string]any{
			"id":     "case-x",
			"action": "invalid",
			"tags":   []any{"foo"},
		})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "invalid action") {
		t.Errorf("expected invalid action message, got: %s", text)
	}
}

// ---- add_case_alert_evidence test ----

func TestAddCaseAlertEvidenceSuccess(t *testing.T) {
	id := "case-ev"
	name := "Evidence Case"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		alertEvidResp: &cases.EntitiesAlertEvidencePostV1OK{
			Payload: makeUpdateOK(cv),
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerAddCaseAlertEvidence(s, mock) },
		"falcon_add_case_alert_evidence", map[string]any{
			"id":        "case-ev",
			"alert_ids": []any{"alert-123"},
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-ev") {
		t.Errorf("expected case ID in result: %s", text)
	}
}

// ---- add_case_event_evidence test ----

func TestAddCaseEventEvidenceSuccess(t *testing.T) {
	id := "case-ev2"
	name := "Event Evidence Case"
	cv := caseVM(id, name)
	mock := &mockCasesAPI{
		eventEvidResp: &cases.EntitiesEventEvidencePostV1OK{
			Payload: makeUpdateOK(cv),
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerAddCaseEventEvidence(s, mock) },
		"falcon_add_case_event_evidence", map[string]any{
			"id":        "case-ev2",
			"event_ids": []any{"event-abc"},
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "case-ev2") {
		t.Errorf("expected case ID in result: %s", text)
	}
}

// ---- list_case_templates tests ----

func TestListCaseTemplatesNilAPI(t *testing.T) {
	// With nil api (not yet wired), the tool should return an informative error.
	text, isErr := callTool(t, func(s *mcp.Server) { registerListCaseTemplates(s, nil) },
		"falcon_list_case_templates", map[string]any{})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "not yet wired") {
		t.Errorf("expected 'not yet wired' message, got: %s", text)
	}
}

func TestListCaseTemplatesSuccess(t *testing.T) {
	tmplName := "IR Template"
	tmpl := &models.APITemplateV1{Name: &tmplName}
	mock := &mockCaseMgmtAPI{
		queryResp: &case_management.QueriesTemplatesGetV1OK{
			Payload: &models.MsaspecQueryResponse{Resources: []string{"tmpl-1"}},
		},
		detailsResp: &case_management.EntitiesTemplatesGetV1OK{
			Payload: &models.APITemplateV1Response{Resources: []*models.APITemplateV1{tmpl}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerListCaseTemplates(s, mock) },
		"falcon_list_case_templates", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "IR Template") {
		t.Errorf("expected template name in result: %s", text)
	}
}

func TestListCaseTemplatesEmpty(t *testing.T) {
	mock := &mockCaseMgmtAPI{
		queryResp: &case_management.QueriesTemplatesGetV1OK{
			Payload: &models.MsaspecQueryResponse{Resources: []string{}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerListCaseTemplates(s, mock) },
		"falcon_list_case_templates", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
}

// ---- normalizeLimit tests ----

func TestNormalizeLimit(t *testing.T) {
	// default (0) → 10
	if got := normalizeLimit(0, 500); got != 10 {
		t.Errorf("normalizeLimit(0, 500) = %d, want 10", got)
	}
	// negative → 10
	if got := normalizeLimit(-1, 500); got != 10 {
		t.Errorf("normalizeLimit(-1, 500) = %d, want 10", got)
	}
	// over max → max
	if got := normalizeLimit(1000, 500); got != 500 {
		t.Errorf("normalizeLimit(1000, 500) = %d, want 500", got)
	}
	// in range → unchanged
	if got := normalizeLimit(50, 500); got != 50 {
		t.Errorf("normalizeLimit(50, 500) = %d, want 50", got)
	}
}

// ---- severityToLevel tests ----

func TestSeverityToLevel(t *testing.T) {
	cases := map[int64]string{
		1:   "informational",
		15:  "informational",
		20:  "low",
		39:  "low",
		40:  "medium",
		69:  "medium",
		70:  "high",
		89:  "high",
		90:  "critical",
		100: "critical",
	}
	for sev, want := range cases {
		if got := severityToLevel(sev); got != want {
			t.Errorf("severityToLevel(%d) = %q, want %q", sev, got, want)
		}
	}
}

// ---- transport error propagation ----

func TestSearchCasesTransportError(t *testing.T) {
	mock := &mockCasesAPI{queryErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchCases(s, mock) },
		"falcon_search_cases", map[string]any{})
	if !contains(text, "Failed to search cases") {
		t.Errorf("expected error message, got: %s", text)
	}
}
