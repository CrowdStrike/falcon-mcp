package intel

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/intel"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockIntelAPI is a hand-written mock satisfying the narrow IntelAPI interface.
type mockIntelAPI struct {
	actorResp     *intel.QueryIntelActorEntitiesOK
	actorErr      error
	indicatorResp *intel.QueryIntelIndicatorEntitiesOK
	indicatorErr  error
	reportResp    *intel.QueryIntelReportEntitiesOK
	reportErr     error
}

func (m *mockIntelAPI) QueryIntelActorEntities(p *intel.QueryIntelActorEntitiesParams, _ ...intel.ClientOption) (*intel.QueryIntelActorEntitiesOK, error) {
	return m.actorResp, m.actorErr
}

func (m *mockIntelAPI) QueryIntelIndicatorEntities(p *intel.QueryIntelIndicatorEntitiesParams, _ ...intel.ClientOption) (*intel.QueryIntelIndicatorEntitiesOK, error) {
	return m.indicatorResp, m.indicatorErr
}

func (m *mockIntelAPI) QueryIntelReportEntities(p *intel.QueryIntelReportEntitiesParams, _ ...intel.ClientOption) (*intel.QueryIntelReportEntitiesOK, error) {
	return m.reportResp, m.reportErr
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

// --- helpers to build canned responses ---

func actorOK(actors ...*models.ActorActorDocument) *intel.QueryIntelActorEntitiesOK {
	return &intel.QueryIntelActorEntitiesOK{
		Payload: &models.ActorActorPaginatedResponse{
			Resources: actors,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.ActorMsaMetaInfoWithPaging{},
		},
	}
}

func indicatorOK(inds ...*models.DomainPublicIndicatorV3) *intel.QueryIntelIndicatorEntitiesOK {
	marker := ""
	return &intel.QueryIntelIndicatorEntitiesOK{
		Payload: &models.DomainPublicIndicatorsV3Response{
			Resources: inds,
			Errors:    []*models.MsaAPIError{},
			Meta: &models.MsaMetaInfo{
				QueryTime: ptrFloat64(0),
				TraceID:   ptrStr(""),
			},
		},
		NextPage: marker,
	}
}

func reportOK(docs ...*models.DomainNewsDocument) *intel.QueryIntelReportEntitiesOK {
	return &intel.QueryIntelReportEntitiesOK{
		Payload: &models.DomainNewsResponse{
			Resources: docs,
			Errors:    []*models.MsaAPIError{},
			Meta: &models.MsaMetaInfo{
				QueryTime: ptrFloat64(0),
				TraceID:   ptrStr(""),
			},
		},
	}
}

func ptrStr(s string) *string       { return &s }
func ptrFloat64(f float64) *float64 { return &f }

// --- search_actors tests ---

func TestSearchActorsSuccess(t *testing.T) {
	active := true
	actor := &models.ActorActorDocument{
		Name:         "COZY BEAR",
		Active:       &active,
		Capabilities: []*models.DomainEntity{},
		Motivations:  []*models.DomainEntity{},
	}
	mock := &mockIntelAPI{actorResp: actorOK(actor)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchActors(s, mock) },
		"falcon_search_actors", map[string]any{"filter": "name:'COZY BEAR'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["name"] != "COZY BEAR" {
		t.Errorf("unexpected actor result: %s", text)
	}
}

func TestSearchActorsEmpty(t *testing.T) {
	mock := &mockIntelAPI{actorResp: actorOK()} // no results
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchActors(s, mock) },
		"falcon_search_actors", map[string]any{"filter": "name:'nobody'"})
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

func TestSearchActorsFQLError(t *testing.T) {
	mock := &mockIntelAPI{actorErr: runtime.NewAPIError("QueryIntelActorEntities", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchActors(s, mock) },
		"falcon_search_actors", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchActors403Scopes(t *testing.T) {
	mock := &mockIntelAPI{actorErr: intel.NewQueryIntelActorEntitiesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchActors(s, mock) },
		"falcon_search_actors", map[string]any{})
	if !contains(text, "Actors (Falcon Intelligence):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// --- search_indicators tests ---

func TestSearchIndicatorsSuccess(t *testing.T) {
	marker := "abc"
	deleted := false
	actors := []string{"COZY BEAR"}
	domainTypes := []string{}
	ipTypes := []string{}
	killChains := []string{}
	indicator := &models.DomainPublicIndicatorV3{
		Marker:          &marker,
		Deleted:         &deleted,
		Actors:          actors,
		DomainTypes:     domainTypes,
		IPAddressTypes:  ipTypes,
		KillChains:      killChains,
		Labels:          []*models.DomainCSIXLabel{},
		MalwareFamilies: []string{},
		Reports:         []string{},
		Targets:         []string{},
		ThreatTypes:     []string{},
		Vulnerabilities: []string{},
	}
	mock := &mockIntelAPI{indicatorResp: indicatorOK(indicator)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIndicators(s, mock) },
		"falcon_search_indicators", map[string]any{"filter": "actors:'COZY BEAR'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Errorf("expected 1 indicator, got %d", len(got))
	}
}

func TestSearchIndicatorsEmpty(t *testing.T) {
	mock := &mockIntelAPI{indicatorResp: indicatorOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIndicators(s, mock) },
		"falcon_search_indicators", map[string]any{})
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
}

func TestSearchIndicatorsFQLError(t *testing.T) {
	mock := &mockIntelAPI{indicatorErr: runtime.NewAPIError("QueryIntelIndicatorEntities", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchIndicators(s, mock) },
		"falcon_search_indicators", map[string]any{"filter": "bogus=="})
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
}

func TestSearchIndicators403Scopes(t *testing.T) {
	mock := &mockIntelAPI{indicatorErr: intel.NewQueryIntelIndicatorEntitiesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchIndicators(s, mock) },
		"falcon_search_indicators", map[string]any{})
	if !contains(text, "Indicators (Falcon Intelligence):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
}

// --- search_reports tests ---

func TestSearchReportsSuccess(t *testing.T) {
	reportName := "APT Report Q1"
	createdDate := int64(1700000000)
	doc := &models.DomainNewsDocument{
		Name:        &reportName,
		CreatedDate: &createdDate,
		Actors:      []*models.DomainSimpleActor{},
	}
	mock := &mockIntelAPI{reportResp: reportOK(doc)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchReports(s, mock) },
		"falcon_search_reports", map[string]any{"q": "APT"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["name"] != "APT Report Q1" {
		t.Errorf("unexpected report result: %s", text)
	}
}

func TestSearchReportsEmpty(t *testing.T) {
	mock := &mockIntelAPI{reportResp: reportOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchReports(s, mock) },
		"falcon_search_reports", map[string]any{})
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
}

func TestSearchReportsFQLError(t *testing.T) {
	mock := &mockIntelAPI{reportErr: runtime.NewAPIError("QueryIntelReportEntities", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchReports(s, mock) },
		"falcon_search_reports", map[string]any{"filter": "bogus=="})
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
}

func TestSearchReports403Scopes(t *testing.T) {
	mock := &mockIntelAPI{reportErr: intel.NewQueryIntelReportEntitiesForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchReports(s, mock) },
		"falcon_search_reports", map[string]any{})
	if !contains(text, "Reports (Falcon Intelligence):read") {
		t.Errorf("expected required scope in 403 result: %s", text)
	}
}

// --- get_mitre_report tests ---

// noOpSearchFn is used when the test passes a numeric actor ID (resolution
// should be skipped entirely).
func noOpSearchFn(_ context.Context, _ string, _ int64) ([]*models.ActorActorDocument, error) {
	return nil, errors.New("search should not be called for numeric IDs")
}

// TestGetMitreReportNumericID: numeric actor ID → skips name resolution,
// downloads, JSON bytes are parsed and returned as structured data.
func TestGetMitreReportNumericID(t *testing.T) {
	reportBytes := []byte(`[{"technique": "T1059"}]`)
	var capturedActorID, capturedFormat string
	downloadFn := func(_ context.Context, actorID, format string) ([]byte, error) {
		capturedActorID = actorID
		capturedFormat = format
		return reportBytes, nil
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, noOpSearchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "12345", "format": "json"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if capturedActorID != "12345" {
		t.Errorf("expected actorID '12345', got %q", capturedActorID)
	}
	if capturedFormat != "json" {
		t.Errorf("expected format 'json', got %q", capturedFormat)
	}
	// JSON bytes must be parsed — result should be an array, not a {"report":...} wrapper.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["technique"] != "T1059" {
		t.Errorf("unexpected parsed result: %s", text)
	}
}

// TestGetMitreReportNameResolution: actor name → resolved via search, then downloaded.
func TestGetMitreReportNameResolution(t *testing.T) {
	actorID := int64(99887)
	actor := &models.ActorActorDocument{
		Name: "WARP PANDA",
		ID:   &actorID,
	}
	var capturedFilter string
	searchFn := func(_ context.Context, filter string, limit int64) ([]*models.ActorActorDocument, error) {
		capturedFilter = filter
		return []*models.ActorActorDocument{actor}, nil
	}

	reportBytes := []byte(`{"ttps": []}`)
	var capturedActorID string
	downloadFn := func(_ context.Context, actorID, format string) ([]byte, error) {
		capturedActorID = actorID
		return reportBytes, nil
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, searchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "WARP PANDA"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if capturedFilter != "name:'WARP PANDA'" {
		t.Errorf("expected search filter name:'WARP PANDA', got %q", capturedFilter)
	}
	if capturedActorID != "99887" {
		t.Errorf("expected resolved actorID '99887', got %q", capturedActorID)
	}
	// Result must be parsed JSON, not a raw string wrapper.
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not JSON object: %v (%s)", err, text)
	}
}

// TestGetMitreReportNameNotFound: name search returns no results → "Actor not found" error.
func TestGetMitreReportNameNotFound(t *testing.T) {
	searchFn := func(_ context.Context, filter string, limit int64) ([]*models.ActorActorDocument, error) {
		return []*models.ActorActorDocument{}, nil
	}
	downloadFn := func(_ context.Context, _, _ string) ([]byte, error) {
		return nil, errors.New("should not be called")
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, searchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "NOBODY PANDA"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "Actor not found") {
		t.Errorf("expected 'Actor not found' in result: %s", text)
	}
	if !contains(text, "NOBODY PANDA") {
		t.Errorf("expected actor name in error message: %s", text)
	}
}

// TestGetMitreReportCSVFormat: csv format → raw string returned (not parsed JSON).
func TestGetMitreReportCSVFormat(t *testing.T) {
	csvData := "technique,tactic\nT1059,Execution\n"
	downloadFn := func(_ context.Context, actorID, format string) ([]byte, error) {
		if format != "csv" {
			return nil, errors.New("expected csv format")
		}
		return []byte(csvData), nil
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, noOpSearchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "99", "format": "csv"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	// For CSV, result must be the raw string (JSON-encoded), not a structured object.
	var got string
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("expected a JSON string for csv result: %v (%s)", err, text)
	}
	if got != csvData {
		t.Errorf("csv content mismatch: got %q, want %q", got, csvData)
	}
}

// TestGetMitreReportDefaultFormat: omitting format defaults to "json".
func TestGetMitreReportDefaultFormat(t *testing.T) {
	var capturedFormat string
	downloadFn := func(_ context.Context, _ string, format string) ([]byte, error) {
		capturedFormat = format
		return []byte("{}"), nil
	}

	callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, noOpSearchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "99"})
	if capturedFormat != "json" {
		t.Errorf("expected default format 'json', got %q", capturedFormat)
	}
}

// TestGetMitreReportDownloadError: download failure surfaces the error message.
func TestGetMitreReportDownloadError(t *testing.T) {
	downloadFn := func(_ context.Context, _ string, _ string) ([]byte, error) {
		return nil, runtime.NewAPIError("GetMitreReport", "not found", 404)
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, noOpSearchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "99999"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "Failed to get MITRE report") {
		t.Errorf("expected error message in result: %s", text)
	}
}

// TestGetMitreReportSearchError: actor name search error is surfaced.
func TestGetMitreReportSearchError(t *testing.T) {
	searchFn := func(_ context.Context, _ string, _ int64) ([]*models.ActorActorDocument, error) {
		return nil, runtime.NewAPIError("QueryIntelActorEntities", "forbidden", 403)
	}
	downloadFn := func(_ context.Context, _, _ string) ([]byte, error) {
		return nil, errors.New("should not be called")
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerGetMitreReport(s, searchFn, downloadFn) },
		"falcon_get_mitre_report", map[string]any{"actor": "SOME PANDA"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "Failed to search for actor by name") {
		t.Errorf("expected search error message in result: %s", text)
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

// --- utility helpers ---

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
