package detections

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockAlertsAPI is a hand-written mock satisfying the narrow AlertsAPI
// interface. Each field lets a test supply a canned response or error for one
// operation.
type mockAlertsAPI struct {
	queryResp *alerts.QueryV2OK
	queryErr  error
	queryGot  *alerts.QueryV2Params

	getResp *alerts.GetV2OK
	getErr  error
	getGot  *alerts.GetV2Params

	updateResp *alerts.UpdateV3OK
	updateErr  error
	updateGot  *alerts.UpdateV3Params
}

func (m *mockAlertsAPI) QueryV2(p *alerts.QueryV2Params, _ ...alerts.ClientOption) (*alerts.QueryV2OK, error) {
	m.queryGot = p
	return m.queryResp, m.queryErr
}

func (m *mockAlertsAPI) GetV2(p *alerts.GetV2Params, _ ...alerts.ClientOption) (*alerts.GetV2OK, error) {
	m.getGot = p
	return m.getResp, m.getErr
}

func (m *mockAlertsAPI) UpdateV3(p *alerts.UpdateV3Params, _ ...alerts.ClientOption) (*alerts.UpdateV3OK, error) {
	m.updateGot = p
	return m.updateResp, m.updateErr
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

// queryOK builds a canned QueryV2OK with the provided IDs.
func queryOK(ids ...string) *alerts.QueryV2OK {
	return &alerts.QueryV2OK{
		Payload: &models.DetectsapiAlertQueryResponse{Resources: ids},
	}
}

// getOK builds a canned GetV2OK with the provided alert stubs.
func getOK(items ...*models.DetectsAlert) *alerts.GetV2OK {
	return &alerts.GetV2OK{
		Payload: &models.DetectsapiPostEntitiesAlertsV2Response{Resources: items},
	}
}

// updateOK builds a canned UpdateV3OK.
func updateOK() *alerts.UpdateV3OK {
	return &alerts.UpdateV3OK{Payload: &models.DetectsapiResponseFields{}}
}

// strPtr is a convenience pointer helper for string literals.
func strPtr(s string) *string { return &s }

// TestSearchDetectionsTwoStep verifies the full two-step flow: query IDs
// then fetch details, and asserts that the details op received the IDs
// returned by the query op.
func TestSearchDetectionsTwoStep(t *testing.T) {
	cid := "d615:ind:abc123"
	status := "new"
	alert := &models.DetectsAlert{CompositeID: strPtr(cid), Status: &status}
	mock := &mockAlertsAPI{
		queryResp: queryOK(cid),
		getResp:   getOK(alert),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchDetections(s, mock) },
		"falcon_search_detections", map[string]any{"filter": "status:'new'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Result must be the full alert details (never just IDs).
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["composite_id"] != cid {
		t.Fatalf("expected full detection details with composite_id=%q, got %s", cid, text)
	}

	// GetV2 must have received the ID returned by QueryV2.
	if mock.getGot == nil || mock.getGot.Body == nil ||
		len(mock.getGot.Body.CompositeIds) != 1 || mock.getGot.Body.CompositeIds[0] != cid {
		t.Errorf("GetV2 not called with queried ID; got %+v", mock.getGot)
	}
}

// TestSearchDetectionsEmpty verifies that an empty query result returns the
// FormatEmptyResponse shape and that the details op is never called.
func TestSearchDetectionsEmpty(t *testing.T) {
	mock := &mockAlertsAPI{queryResp: queryOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchDetections(s, mock) },
		"falcon_search_detections", map[string]any{"filter": "status:'closed'"})
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
	if mock.getGot != nil {
		t.Error("GetV2 should not be called when no IDs matched")
	}
}

// TestSearchDetectionsFQLError verifies that a 400 (bad filter) error causes
// the fql_guide to be embedded in the response.
func TestSearchDetectionsFQLError(t *testing.T) {
	mock := &mockAlertsAPI{queryErr: runtime.NewAPIError("QueryV2", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchDetections(s, mock) },
		"falcon_search_detections", map[string]any{"filter": "bogus=="})
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

// TestSearchDetections403Scopes verifies that a 403 error surfaces the
// required scopes but does not include the FQL guide.
func TestSearchDetections403Scopes(t *testing.T) {
	mock := &mockAlertsAPI{queryErr: alerts.NewQueryV2Forbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchDetections(s, mock) },
		"falcon_search_detections", map[string]any{})
	if !contains(text, "Alerts:read") {
		t.Errorf("expected required scope Alerts:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// TestGetDetectionDetailsEmptyIDs verifies that passing no IDs returns an
// empty array without calling the API.
func TestGetDetectionDetailsEmptyIDs(t *testing.T) {
	mock := &mockAlertsAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetDetectionDetails(s, mock) },
		"falcon_get_detection_details", map[string]any{"ids": []any{}})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
	if mock.getGot != nil {
		t.Error("no API call should be made for empty IDs")
	}
}

// TestUpdateDetectionsSuccess verifies that a successful update call sends
// the right composite IDs and status action_parameter, and returns [].
func TestUpdateDetectionsSuccess(t *testing.T) {
	mock := &mockAlertsAPI{updateResp: updateOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateDetections(s, mock) },
		"falcon_update_detections", map[string]any{
			"ids":    []any{"d615:ind:abc123", "d615:ind:def456"},
			"status": "in_progress",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// UpdateV3 must have received both IDs.
	if mock.updateGot == nil || mock.updateGot.Body == nil {
		t.Fatal("UpdateV3 was not called")
	}
	body := mock.updateGot.Body
	if len(body.CompositeIds) != 2 {
		t.Errorf("expected 2 composite IDs, got %v", body.CompositeIds)
	}

	// The action_parameters must include update_status=in_progress.
	found := false
	for _, ap := range body.ActionParameters {
		if ap.Name != nil && *ap.Name == "update_status" && ap.Value != nil && *ap.Value == "in_progress" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected update_status=in_progress action parameter, got %+v", body.ActionParameters)
	}

	// On success with no close+resolution hint, result is [].
	if text != "[]" {
		t.Errorf("expected empty array on success, got %s", text)
	}
}

// TestUpdateDetectionsCloseWithoutResolutionTag verifies that closing a
// detection without adding a resolution tag produces the soft hint.
func TestUpdateDetectionsCloseWithoutResolutionTag(t *testing.T) {
	mock := &mockAlertsAPI{updateResp: updateOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateDetections(s, mock) },
		"falcon_update_detections", map[string]any{
			"ids":    []any{"d615:ind:abc123"},
			"status": "closed",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if _, ok := got["hint"]; !ok {
		t.Errorf("expected hint key when closing without resolution tag, got keys %v", keysOf(got))
	}
}

// TestUpdateDetectionsCloseWithResolutionTag verifies that closing with a
// resolution tag does NOT produce the soft hint.
func TestUpdateDetectionsCloseWithResolutionTag(t *testing.T) {
	mock := &mockAlertsAPI{updateResp: updateOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateDetections(s, mock) },
		"falcon_update_detections", map[string]any{
			"ids":      []any{"d615:ind:abc123"},
			"status":   "closed",
			"add_tags": []any{"true_positive"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array when closing with resolution tag, got %s", text)
	}
}

// TestUpdateDetectionsValidationErrors covers the client-side validation
// paths that return error maps without calling the API.
func TestUpdateDetectionsValidationErrors(t *testing.T) {
	cases := []struct {
		name       string
		args       map[string]any
		wantSubstr string
	}{
		{
			name:       "no ids",
			args:       map[string]any{"ids": []any{}, "status": "new"},
			wantSubstr: "At least one detection ID",
		},
		{
			name:       "no update params",
			args:       map[string]any{"ids": []any{"x"}},
			wantSubstr: "At least one update parameter",
		},
		{
			name:       "invalid status",
			args:       map[string]any{"ids": []any{"x"}, "status": "invalid"},
			wantSubstr: "status must be one of",
		},
		{
			name:       "multiple assignment params",
			args:       map[string]any{"ids": []any{"x"}, "assign_to_uuid": "u1", "assign_to_user_id": "u@e.com"},
			wantSubstr: "at most one",
		},
	}

	mock := &mockAlertsAPI{}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			text, _ := callTool(t, func(s *mcp.Server) { registerUpdateDetections(s, mock) },
				"falcon_update_detections", tc.args)
			if !contains(text, tc.wantSubstr) {
				t.Errorf("expected %q in response, got: %s", tc.wantSubstr, text)
			}
			if mock.updateGot != nil {
				t.Error("UpdateV3 should not be called for validation errors")
				mock.updateGot = nil // reset for next case
			}
		})
	}
}

// TestNormalizeLimit verifies the limit clamping logic.
func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 9999: 9999, 10000: 9999}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// keysOf returns sorted map keys for diagnostic messages.
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
