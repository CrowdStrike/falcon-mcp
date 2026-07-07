package quarantine

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	gofalconquarantine "github.com/crowdstrike/gofalcon/falcon/client/quarantine"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockQuarantineAPI is a hand-written mock satisfying the narrow QuarantineAPI
// interface. Each field lets a test supply a canned response or error for one
// operation.
type mockQuarantineAPI struct {
	queryResp *gofalconquarantine.QueryQuarantineFilesOK
	queryErr  error
	queryGot  *gofalconquarantine.QueryQuarantineFilesParams

	getResp *gofalconquarantine.GetQuarantineFilesOK
	getErr  error
	getGot  *gofalconquarantine.GetQuarantineFilesParams

	countResp *gofalconquarantine.ActionUpdateCountOK
	countErr  error
	countGot  *gofalconquarantine.ActionUpdateCountParams

	updateByIDsResp *gofalconquarantine.UpdateQuarantinedDetectsByIdsOK
	updateByIDsErr  error
	updateByIDsGot  *gofalconquarantine.UpdateQuarantinedDetectsByIdsParams

	updateByQueryResp *gofalconquarantine.UpdateQfByQueryOK
	updateByQueryErr  error
	updateByQueryGot  *gofalconquarantine.UpdateQfByQueryParams
}

func (m *mockQuarantineAPI) QueryQuarantineFiles(p *gofalconquarantine.QueryQuarantineFilesParams, _ ...gofalconquarantine.ClientOption) (*gofalconquarantine.QueryQuarantineFilesOK, error) {
	m.queryGot = p
	return m.queryResp, m.queryErr
}

func (m *mockQuarantineAPI) GetQuarantineFiles(p *gofalconquarantine.GetQuarantineFilesParams, _ ...gofalconquarantine.ClientOption) (*gofalconquarantine.GetQuarantineFilesOK, error) {
	m.getGot = p
	return m.getResp, m.getErr
}

func (m *mockQuarantineAPI) ActionUpdateCount(p *gofalconquarantine.ActionUpdateCountParams, _ ...gofalconquarantine.ClientOption) (*gofalconquarantine.ActionUpdateCountOK, error) {
	m.countGot = p
	return m.countResp, m.countErr
}

func (m *mockQuarantineAPI) UpdateQuarantinedDetectsByIds(p *gofalconquarantine.UpdateQuarantinedDetectsByIdsParams, _ ...gofalconquarantine.ClientOption) (*gofalconquarantine.UpdateQuarantinedDetectsByIdsOK, error) {
	m.updateByIDsGot = p
	return m.updateByIDsResp, m.updateByIDsErr
}

func (m *mockQuarantineAPI) UpdateQfByQuery(p *gofalconquarantine.UpdateQfByQueryParams, _ ...gofalconquarantine.ClientOption) (*gofalconquarantine.UpdateQfByQueryOK, error) {
	m.updateByQueryGot = p
	return m.updateByQueryResp, m.updateByQueryErr
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

// --- helpers for building canned responses ---

func queryOK(ids ...string) *gofalconquarantine.QueryQuarantineFilesOK {
	return &gofalconquarantine.QueryQuarantineFilesOK{
		Payload: &models.MsaspecQueryResponse{Resources: ids},
	}
}

func getOK(files ...*models.QuarantineQuarantinedFile) *gofalconquarantine.GetQuarantineFilesOK {
	return &gofalconquarantine.GetQuarantineFilesOK{
		Payload: &models.DomainMsaQfResponse{
			Resources: files,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func countOK(results ...*models.MsaAggregationResult) *gofalconquarantine.ActionUpdateCountOK {
	return &gofalconquarantine.ActionUpdateCountOK{
		Payload: &models.MsaAggregatesResponse{
			Resources: results,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func updateByIDsOK() *gofalconquarantine.UpdateQuarantinedDetectsByIdsOK {
	return &gofalconquarantine.UpdateQuarantinedDetectsByIdsOK{
		Payload: &models.MsaReplyMetaOnly{Meta: &models.MsaMetaInfo{}},
	}
}

func updateByQueryOK() *gofalconquarantine.UpdateQfByQueryOK {
	return &gofalconquarantine.UpdateQfByQueryOK{
		Payload: &models.MsaReplyMetaOnly{Meta: &models.MsaMetaInfo{}},
	}
}

// --- search tests ---

func TestSearchQuarantinedFilesTwoStep(t *testing.T) {
	sha := "abc123sha"
	hostname := "WORKSTATION-1"
	file := &models.QuarantineQuarantinedFile{
		Sha256:   sha,
		Hostname: hostname,
	}
	mock := &mockQuarantineAPI{
		queryResp: queryOK("qfile-001"),
		getResp:   getOK(file),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchQuarantinedFiles(s, mock) },
		"falcon_search_quarantined_files", map[string]any{"filter": "hostname:'WORKSTATION-1'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Result must be the full file details (never just IDs).
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["sha256"] != sha || got[0]["hostname"] != hostname {
		t.Fatalf("expected full quarantine file details, got %s", text)
	}

	// Step 2 must have received the ID from step 1.
	if mock.getGot == nil || mock.getGot.Body == nil ||
		len(mock.getGot.Body.Ids) != 1 || mock.getGot.Body.Ids[0] != "qfile-001" {
		t.Errorf("GetQuarantineFiles not called with queried ID; got %+v", mock.getGot)
	}
}

func TestSearchQuarantinedFilesEmpty(t *testing.T) {
	mock := &mockQuarantineAPI{queryResp: queryOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchQuarantinedFiles(s, mock) },
		"falcon_search_quarantined_files", map[string]any{"filter": "hostname:'nope'"})
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
	if mock.getGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchQuarantinedFilesFQLError(t *testing.T) {
	mock := &mockQuarantineAPI{queryErr: runtime.NewAPIError("QueryQuarantineFiles", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchQuarantinedFiles(s, mock) },
		"falcon_search_quarantined_files", map[string]any{"filter": "bogus=="})
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

func TestSearchQuarantinedFiles403Scopes(t *testing.T) {
	mock := &mockQuarantineAPI{queryErr: gofalconquarantine.NewQueryQuarantineFilesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchQuarantinedFiles(s, mock) },
		"falcon_search_quarantined_files", map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Quarantined Files:read") {
		t.Errorf("expected required scope Quarantined Files:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// --- preview tests ---

func TestPreviewQuarantineActionsSuccess(t *testing.T) {
	name := "release"
	result := &models.MsaAggregationResult{
		Name:    &name,
		Buckets: []*models.MsaAggregationResultItem{},
	}
	mock := &mockQuarantineAPI{countResp: countOK(result)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerPreviewQuarantineActions(s, mock) },
		"falcon_preview_quarantine_actions", map[string]any{"filter": "state:'quarantined'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if mock.countGot == nil || mock.countGot.Filter != "state:'quarantined'" {
		t.Errorf("ActionUpdateCount not called with expected filter; got %+v", mock.countGot)
	}
	if !contains(text, "release") {
		t.Errorf("expected action name in preview result: %s", text)
	}
}

func TestPreviewQuarantineActionsEmptyFilter(t *testing.T) {
	mock := &mockQuarantineAPI{}
	text, _ := callTool(t, func(s *mcp.Server) { registerPreviewQuarantineActions(s, mock) },
		"falcon_preview_quarantine_actions", map[string]any{"filter": ""})
	if !contains(text, "non-empty FQL") {
		t.Errorf("expected validation error for empty filter: %s", text)
	}
	if mock.countGot != nil {
		t.Error("API should not be called with empty filter")
	}
}

// --- update tests ---

func TestUpdateQuarantinedFilesByIDsSuccess(t *testing.T) {
	mock := &mockQuarantineAPI{updateByIDsResp: updateByIDsOK()}

	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateQuarantinedFiles(s, mock) },
		"falcon_update_quarantined_files", map[string]any{
			"action": "release",
			"ids":    []any{"qf-001", "qf-002"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if mock.updateByIDsGot == nil || mock.updateByIDsGot.Body == nil {
		t.Fatal("UpdateQuarantinedDetectsByIds not called")
	}
	body := mock.updateByIDsGot.Body
	if body.Action != "release" {
		t.Errorf("expected action=release, got %q", body.Action)
	}
	if len(body.Ids) != 2 || body.Ids[0] != "qf-001" || body.Ids[1] != "qf-002" {
		t.Errorf("unexpected ids: %v", body.Ids)
	}
	// Success returns empty list.
	if text != "[]" {
		t.Errorf("expected empty array on success, got %s", text)
	}
}

func TestUpdateQuarantinedFilesInvalidAction(t *testing.T) {
	mock := &mockQuarantineAPI{}
	text, _ := callTool(t, func(s *mcp.Server) { registerUpdateQuarantinedFiles(s, mock) },
		"falcon_update_quarantined_files", map[string]any{
			"action": "delete",
			"ids":    []any{"qf-001"},
		})
	if !contains(text, "Unsupported quarantine") {
		t.Errorf("expected validation error for invalid action: %s", text)
	}
}

func TestUpdateQuarantinedFilesNoIDsOrFilter(t *testing.T) {
	mock := &mockQuarantineAPI{}
	text, _ := callTool(t, func(s *mcp.Server) { registerUpdateQuarantinedFiles(s, mock) },
		"falcon_update_quarantined_files", map[string]any{"action": "release"})
	if !contains(text, "ids") || !contains(text, "filter") {
		t.Errorf("expected validation error for missing ids/filter: %s", text)
	}
}

func TestUpdateQuarantinedFilesTransportError(t *testing.T) {
	mock := &mockQuarantineAPI{updateByIDsErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerUpdateQuarantinedFiles(s, mock) },
		"falcon_update_quarantined_files", map[string]any{
			"action": "unrelease",
			"ids":    []any{"qf-001"},
		})
	if !contains(text, "Failed to update quarantined files by IDs") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- delete tests ---

func TestDeleteQuarantinedFilesByQuerySuccess(t *testing.T) {
	mock := &mockQuarantineAPI{updateByQueryResp: updateByQueryOK()}

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteQuarantinedFiles(s, mock) },
		"falcon_delete_quarantined_files", map[string]any{
			"filter": "state:'quarantined'",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if mock.updateByQueryGot == nil || mock.updateByQueryGot.Body == nil {
		t.Fatal("UpdateQfByQuery not called")
	}
	body := mock.updateByQueryGot.Body
	if body.Action != "delete" {
		t.Errorf("expected action=delete, got %q", body.Action)
	}
	if body.Filter != "state:'quarantined'" {
		t.Errorf("expected filter passed through, got %q", body.Filter)
	}
	if text != "[]" {
		t.Errorf("expected empty array on success, got %s", text)
	}
}

func TestDeleteQuarantinedFilesNoIDsOrFilter(t *testing.T) {
	mock := &mockQuarantineAPI{}
	text, _ := callTool(t, func(s *mcp.Server) { registerDeleteQuarantinedFiles(s, mock) },
		"falcon_delete_quarantined_files", map[string]any{})
	if !contains(text, "ids") || !contains(text, "filter") {
		t.Errorf("expected validation error for missing ids/filter: %s", text)
	}
}

// --- limit normalization ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 500: 500, 9999: 500}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- normalize restore action ---

func TestNormalizeRestoreAction(t *testing.T) {
	cases := []struct {
		in     string
		want   string
		wantOK bool
	}{
		{"release", "release", true},
		{"unrelease", "unrelease", true},
		{"delete", "", false},
		{"RELEASE", "", false},
		{"", "", false},
	}
	for _, tc := range cases {
		got, ok := normalizeRestoreAction(tc.in)
		if ok != tc.wantOK || got != tc.want {
			t.Errorf("normalizeRestoreAction(%q) = %q, %v; want %q, %v", tc.in, got, ok, tc.want, tc.wantOK)
		}
	}
}

// --- stdlib helpers ---

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
