package ioc

import (
	"context"
	"encoding/json"
	"testing"

	gofalioc "github.com/crowdstrike/gofalcon/falcon/client/ioc"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockIOCAPI is a hand-written mock satisfying the narrow IOCAPI interface.
type mockIOCAPI struct {
	searchResp *gofalioc.IndicatorSearchV1OK
	searchErr  error
	searchGot  *gofalioc.IndicatorSearchV1Params

	getResp *gofalioc.IndicatorGetV1OK
	getErr  error
	getGot  *gofalioc.IndicatorGetV1Params

	createResp *gofalioc.IndicatorCreateV1Created
	createErr  error
	createGot  *gofalioc.IndicatorCreateV1Params

	deleteResp *gofalioc.IndicatorDeleteV1OK
	deleteErr  error
	deleteGot  *gofalioc.IndicatorDeleteV1Params
}

func (m *mockIOCAPI) IndicatorSearchV1(p *gofalioc.IndicatorSearchV1Params, _ ...gofalioc.ClientOption) (*gofalioc.IndicatorSearchV1OK, error) {
	m.searchGot = p
	return m.searchResp, m.searchErr
}

func (m *mockIOCAPI) IndicatorGetV1(p *gofalioc.IndicatorGetV1Params, _ ...gofalioc.ClientOption) (*gofalioc.IndicatorGetV1OK, error) {
	m.getGot = p
	return m.getResp, m.getErr
}

func (m *mockIOCAPI) IndicatorCreateV1(p *gofalioc.IndicatorCreateV1Params, _ ...gofalioc.ClientOption) (*gofalioc.IndicatorCreateV1Created, error) {
	m.createGot = p
	return m.createResp, m.createErr
}

func (m *mockIOCAPI) IndicatorDeleteV1(p *gofalioc.IndicatorDeleteV1Params, _ ...gofalioc.ClientOption) (*gofalioc.IndicatorDeleteV1OK, error) {
	m.deleteGot = p
	return m.deleteResp, m.deleteErr
}

// callTool wires a mock into a real MCP server and invokes the named tool.
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

// --- search test helpers ---

func searchOK(ids ...string) *gofalioc.IndicatorSearchV1OK {
	return &gofalioc.IndicatorSearchV1OK{
		Payload: &models.APIIndicatorQueryRespV1{
			Resources: ids,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.APIIndicatorsQueryMeta{},
		},
	}
}

func getOK(inds ...*models.APIIndicatorV1) *gofalioc.IndicatorGetV1OK {
	return &gofalioc.IndicatorGetV1OK{
		Payload: &models.APIIndicatorRespV1{
			Resources: inds,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.APIIndicatorsQueryMeta{},
		},
	}
}

func deleteOK(ids ...string) *gofalioc.IndicatorDeleteV1OK {
	return &gofalioc.IndicatorDeleteV1OK{
		Payload: &models.APIIndicatorQueryRespV1{
			Resources: ids,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.APIIndicatorsQueryMeta{},
		},
	}
}

// --- falcon_search_iocs tests ---

func TestSearchIOCsTwoStep(t *testing.T) {
	iocID := "ioc-abc-123"
	iocType := "domain"
	iocValue := "evil.example.com"
	ind := &models.APIIndicatorV1{ID: iocID, Type: iocType, Value: iocValue}

	mock := &mockIOCAPI{
		searchResp: searchOK(iocID),
		getResp:    getOK(ind),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIOCs(s, mock) },
		"falcon_search_iocs", map[string]any{"filter": "type:'domain'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Must return full details, not just IDs.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != iocID || got[0]["type"] != iocType || got[0]["value"] != iocValue {
		t.Fatalf("expected full indicator details, got %s", text)
	}

	// Step 2 must have been called with the ID returned from step 1.
	if mock.getGot == nil || len(mock.getGot.Ids) != 1 || mock.getGot.Ids[0] != iocID {
		t.Errorf("IndicatorGetV1 not called with queried ID; got %+v", mock.getGot)
	}
}

func TestSearchIOCsEmpty(t *testing.T) {
	mock := &mockIOCAPI{searchResp: searchOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIOCs(s, mock) },
		"falcon_search_iocs", map[string]any{"filter": "type:'sha256'"})
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
		t.Error("IndicatorGetV1 should not be called when no IDs matched")
	}
}

func TestSearchIOCsFQLError(t *testing.T) {
	mock := &mockIOCAPI{searchErr: runtime.NewAPIError("IndicatorSearchV1", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIOCs(s, mock) },
		"falcon_search_iocs", map[string]any{"filter": "bogus=="})
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

func TestSearchIOCs403Scopes(t *testing.T) {
	mock := &mockIOCAPI{searchErr: gofalioc.NewIndicatorSearchV1Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchIOCs(s, mock) },
		"falcon_search_iocs", map[string]any{})
	// 403 is not an FQL error → no guide, but required scopes should surface.
	if !contains(text, "IOC Management") {
		t.Errorf("expected IOC Management scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// --- falcon_add_ioc tests ---

func TestAddIOCSuccess(t *testing.T) {
	iocID := "created-ioc-1"
	iocType := "ipv4"
	iocValue := "1.2.3.4"
	created := &models.APIIndicatorV1{ID: iocID, Type: iocType, Value: iocValue}

	mock := &mockIOCAPI{
		createResp: &gofalioc.IndicatorCreateV1Created{
			Payload: &models.APIIndicatorRespV1{
				Resources: []*models.APIIndicatorV1{created},
				Errors:    []*models.MsaAPIError{},
				Meta:      &models.APIIndicatorsQueryMeta{},
			},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerAddIOC(s, mock) },
		"falcon_add_ioc", map[string]any{
			"type":        iocType,
			"value":       iocValue,
			"action":      "detect",
			"severity":    "medium",
			"description": "test indicator",
			"platforms":   []any{"windows", "linux"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != iocID {
		t.Fatalf("expected created indicator, got %s", text)
	}

	// Assert the create body carried the indicator fields.
	if mock.createGot == nil || mock.createGot.Body == nil {
		t.Fatal("IndicatorCreateV1 not called with a body")
	}
	inds := mock.createGot.Body.Indicators
	if len(inds) != 1 {
		t.Fatalf("expected 1 indicator in body, got %d", len(inds))
	}
	ind := inds[0]
	if ind.Type != iocType {
		t.Errorf("indicator type = %q, want %q", ind.Type, iocType)
	}
	if ind.Value != iocValue {
		t.Errorf("indicator value = %q, want %q", ind.Value, iocValue)
	}
	if ind.Severity != "medium" {
		t.Errorf("indicator severity = %q, want %q", ind.Severity, "medium")
	}
	if len(ind.Platforms) != 2 {
		t.Errorf("expected 2 platforms, got %v", ind.Platforms)
	}
}

func TestAddIOCDefaultsApplied(t *testing.T) {
	mock := &mockIOCAPI{
		createResp: &gofalioc.IndicatorCreateV1Created{
			Payload: &models.APIIndicatorRespV1{
				Resources: []*models.APIIndicatorV1{},
				Errors:    []*models.MsaAPIError{},
				Meta:      &models.APIIndicatorsQueryMeta{},
			},
		},
	}

	callTool(t, func(s *mcp.Server) { registerAddIOC(s, mock) },
		"falcon_add_ioc", map[string]any{
			"type":  "md5",
			"value": "d41d8cd98f00b204e9800998ecf8427e",
		})

	if mock.createGot == nil || mock.createGot.Body == nil || len(mock.createGot.Body.Indicators) == 0 {
		t.Fatal("create body missing")
	}
	ind := mock.createGot.Body.Indicators[0]
	if ind.Action != "detect" {
		t.Errorf("default action = %q, want detect", ind.Action)
	}
	if ind.Source != "mcp" {
		t.Errorf("default source = %q, want mcp", ind.Source)
	}
}

func TestAddIOCMissingTypeValue(t *testing.T) {
	mock := &mockIOCAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerAddIOC(s, mock) },
		"falcon_add_ioc", map[string]any{})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	// Should return a validation error without calling the API.
	if mock.createGot != nil {
		t.Error("IndicatorCreateV1 should not be called when type/value are missing")
	}
	if !contains(text, "required") && !contains(text, "type") {
		t.Errorf("expected validation error, got: %s", text)
	}
}

func TestAddIOCBulkIndicators(t *testing.T) {
	mock := &mockIOCAPI{
		createResp: &gofalioc.IndicatorCreateV1Created{
			Payload: &models.APIIndicatorRespV1{
				Resources: []*models.APIIndicatorV1{},
				Errors:    []*models.MsaAPIError{},
				Meta:      &models.APIIndicatorsQueryMeta{},
			},
		},
	}

	callTool(t, func(s *mcp.Server) { registerAddIOC(s, mock) },
		"falcon_add_ioc", map[string]any{
			"indicators": []any{
				map[string]any{"type": "domain", "value": "bad.example.com", "action": "prevent"},
				map[string]any{"type": "ipv4", "value": "10.0.0.1", "action": "detect"},
			},
		})

	if mock.createGot == nil || mock.createGot.Body == nil {
		t.Fatal("create body missing")
	}
	if len(mock.createGot.Body.Indicators) != 2 {
		t.Errorf("expected 2 indicators in bulk body, got %d", len(mock.createGot.Body.Indicators))
	}
}

// --- falcon_remove_iocs tests ---

func TestRemoveIOCsSuccess(t *testing.T) {
	mock := &mockIOCAPI{deleteResp: deleteOK("ioc-1", "ioc-2")}

	text, isErr := callTool(t, func(s *mcp.Server) { registerRemoveIOCs(s, mock) },
		"falcon_remove_iocs", map[string]any{"ids": []any{"ioc-1", "ioc-2"}})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if got["status"] != "deleted" {
		t.Errorf("expected status=deleted, got %v", got["status"])
	}
	if got["count"].(float64) != 2 {
		t.Errorf("expected count=2, got %v", got["count"])
	}

	// Assert ids were passed through.
	if mock.deleteGot == nil || len(mock.deleteGot.Ids) != 2 {
		t.Errorf("IndicatorDeleteV1 not called with expected IDs; got %+v", mock.deleteGot)
	}
}

func TestRemoveIOCsByFilter(t *testing.T) {
	filter := "source:'mcp'"
	mock := &mockIOCAPI{deleteResp: deleteOK("ioc-5")}

	text, isErr := callTool(t, func(s *mcp.Server) { registerRemoveIOCs(s, mock) },
		"falcon_remove_iocs", map[string]any{"filter": filter})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON object: %v", err)
	}
	if got["count"].(float64) != 1 {
		t.Errorf("expected count=1, got %v", got["count"])
	}

	if mock.deleteGot == nil || mock.deleteGot.Filter == nil || *mock.deleteGot.Filter != filter {
		t.Errorf("IndicatorDeleteV1 not called with expected filter; got %+v", mock.deleteGot)
	}
}

func TestRemoveIOCsNoIdsOrFilter(t *testing.T) {
	mock := &mockIOCAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerRemoveIOCs(s, mock) },
		"falcon_remove_iocs", map[string]any{})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if mock.deleteGot != nil {
		t.Error("IndicatorDeleteV1 should not be called when no ids or filter provided")
	}
	if !contains(text, "ids") || !contains(text, "filter") {
		t.Errorf("expected validation error mentioning ids/filter, got: %s", text)
	}
}

func TestRemoveIOCs403Scopes(t *testing.T) {
	mock := &mockIOCAPI{deleteErr: gofalioc.NewIndicatorDeleteV1Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerRemoveIOCs(s, mock) },
		"falcon_remove_iocs", map[string]any{"ids": []any{"ioc-1"}})
	if !contains(text, "IOC Management") {
		t.Errorf("expected IOC Management scope in 403 result: %s", text)
	}
}

// --- normalizeLimit tests ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -1: 10, 1: 1, 10: 10, 500: 500, 999: 500}
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
