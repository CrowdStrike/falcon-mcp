package data_protection

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/data_protection_configuration"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockDataProtectionAPI is a hand-written mock satisfying the narrow
// DataProtectionAPI interface. Each field lets a test supply a canned response
// or error for one operation.
type mockDataProtectionAPI struct {
	// classifications
	classQueryResp *data_protection_configuration.QueriesClassificationGetV2OK
	classQueryErr  error
	classQueryGot  *data_protection_configuration.QueriesClassificationGetV2Params

	classEntResp *data_protection_configuration.EntitiesClassificationGetV2OK
	classEntErr  error
	classEntGot  *data_protection_configuration.EntitiesClassificationGetV2Params

	// policies
	polQueryResp *data_protection_configuration.QueriesPolicyGetV2OK
	polQueryErr  error
	polQueryGot  *data_protection_configuration.QueriesPolicyGetV2Params

	polEntResp *data_protection_configuration.EntitiesPolicyGetV2OK
	polEntErr  error
	polEntGot  *data_protection_configuration.EntitiesPolicyGetV2Params

	// content patterns
	cpQueryResp *data_protection_configuration.QueriesContentPatternGetV2OK
	cpQueryErr  error
	cpQueryGot  *data_protection_configuration.QueriesContentPatternGetV2Params

	cpEntResp *data_protection_configuration.EntitiesContentPatternGetOK
	cpEntErr  error
	cpEntGot  *data_protection_configuration.EntitiesContentPatternGetParams
}

func (m *mockDataProtectionAPI) QueriesClassificationGetV2(p *data_protection_configuration.QueriesClassificationGetV2Params, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesClassificationGetV2OK, error) {
	m.classQueryGot = p
	return m.classQueryResp, m.classQueryErr
}

func (m *mockDataProtectionAPI) EntitiesClassificationGetV2(p *data_protection_configuration.EntitiesClassificationGetV2Params, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesClassificationGetV2OK, error) {
	m.classEntGot = p
	return m.classEntResp, m.classEntErr
}

func (m *mockDataProtectionAPI) QueriesPolicyGetV2(p *data_protection_configuration.QueriesPolicyGetV2Params, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesPolicyGetV2OK, error) {
	m.polQueryGot = p
	return m.polQueryResp, m.polQueryErr
}

func (m *mockDataProtectionAPI) EntitiesPolicyGetV2(p *data_protection_configuration.EntitiesPolicyGetV2Params, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesPolicyGetV2OK, error) {
	m.polEntGot = p
	return m.polEntResp, m.polEntErr
}

func (m *mockDataProtectionAPI) QueriesContentPatternGetV2(p *data_protection_configuration.QueriesContentPatternGetV2Params, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesContentPatternGetV2OK, error) {
	m.cpQueryGot = p
	return m.cpQueryResp, m.cpQueryErr
}

func (m *mockDataProtectionAPI) EntitiesContentPatternGet(p *data_protection_configuration.EntitiesContentPatternGetParams, _ ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesContentPatternGetOK, error) {
	m.cpEntGot = p
	return m.cpEntResp, m.cpEntErr
}

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

// ---- helper constructors ----

func classQueryOK(ids ...string) *data_protection_configuration.QueriesClassificationGetV2OK {
	return &data_protection_configuration.QueriesClassificationGetV2OK{
		Payload: &models.ResponsesPolicySearchV1{Resources: ids},
	}
}

func classEntOK(names ...string) *data_protection_configuration.EntitiesClassificationGetV2OK {
	items := make([]*models.PolicymanagerExternalClassification, 0, len(names))
	for _, n := range names {
		name := n
		items = append(items, &models.PolicymanagerExternalClassification{Name: &name})
	}
	return &data_protection_configuration.EntitiesClassificationGetV2OK{
		Payload: &models.PolicymanagerClassificationsResponse{Resources: items},
	}
}

func polQueryOK(ids ...string) *data_protection_configuration.QueriesPolicyGetV2OK {
	return &data_protection_configuration.QueriesPolicyGetV2OK{
		Payload: &models.ResponsesPolicySearchV1{Resources: ids},
	}
}

func polEntOK(names ...string) *data_protection_configuration.EntitiesPolicyGetV2OK {
	items := make([]*models.PolicymanagerExternalPolicy, 0, len(names))
	for _, n := range names {
		name := n
		items = append(items, &models.PolicymanagerExternalPolicy{Name: &name})
	}
	return &data_protection_configuration.EntitiesPolicyGetV2OK{
		Payload: &models.PolicymanagerPoliciesResponse{Resources: items},
	}
}

func cpQueryOK(ids ...string) *data_protection_configuration.QueriesContentPatternGetV2OK {
	return &data_protection_configuration.QueriesContentPatternGetV2OK{
		Payload: &models.MsaspecQueryResponse{Resources: ids},
	}
}

func cpEntOK(names ...string) *data_protection_configuration.EntitiesContentPatternGetOK {
	items := make([]*models.APIContentPatternV1, 0, len(names))
	for _, n := range names {
		items = append(items, &models.APIContentPatternV1{Name: n})
	}
	return &data_protection_configuration.EntitiesContentPatternGetOK{
		Payload: &models.APIContentPatternMSAResponseV1{Resources: items},
	}
}

// ===== Classifications =====

func TestSearchClassificationsTwoStep(t *testing.T) {
	mock := &mockDataProtectionAPI{
		classQueryResp: classQueryOK("cid-1"),
		classEntResp:   classEntOK("PII - SSN"),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchClassifications(s, mock) },
		"falcon_search_data_protection_classifications",
		map[string]any{"filter": "name:'PII - SSN'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Must return full details, not just IDs.
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 classification, got %d: %s", len(got), text)
	}
	if got[0]["name"] != "PII - SSN" {
		t.Errorf("expected name 'PII - SSN', got %v", got[0]["name"])
	}

	// Step 2 must have received the ID from step 1.
	if mock.classEntGot == nil || len(mock.classEntGot.Ids) != 1 || mock.classEntGot.Ids[0] != "cid-1" {
		t.Errorf("EntitiesClassificationGetV2 not called with queried ID; got %+v", mock.classEntGot)
	}
}

func TestSearchClassificationsEmpty(t *testing.T) {
	mock := &mockDataProtectionAPI{classQueryResp: classQueryOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchClassifications(s, mock) },
		"falcon_search_data_protection_classifications",
		map[string]any{"filter": "name:'nope'"})
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
	if mock.classEntGot != nil {
		t.Error("entities should not be fetched when no IDs matched")
	}
}

func TestSearchClassificationsFQLError(t *testing.T) {
	mock := &mockDataProtectionAPI{
		classQueryErr: runtime.NewAPIError("QueriesClassificationGetV2", "bad filter", 400),
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchClassifications(s, mock) },
		"falcon_search_data_protection_classifications",
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

func TestSearchClassifications403Scopes(t *testing.T) {
	mock := &mockDataProtectionAPI{
		classQueryErr: data_protection_configuration.NewQueriesClassificationGetV2Forbidden(),
	}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchClassifications(s, mock) },
		"falcon_search_data_protection_classifications",
		map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Data Protection:read") {
		t.Errorf("expected required scope Data Protection:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ===== Policies =====

func TestSearchPoliciesTwoStep(t *testing.T) {
	mock := &mockDataProtectionAPI{
		polQueryResp: polQueryOK("pid-1"),
		polEntResp:   polEntOK("Default Windows Policy"),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, mock) },
		"falcon_search_data_protection_policies",
		map[string]any{"platform_name": "win"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 policy, got %d: %s", len(got), text)
	}

	// Verify step 1 received the platform_name.
	if mock.polQueryGot == nil || mock.polQueryGot.PlatformName != "win" {
		t.Errorf("QueriesPolicyGetV2 not called with platform_name 'win'; got %+v", mock.polQueryGot)
	}
	// Verify step 2 received the ID from step 1.
	if mock.polEntGot == nil || len(mock.polEntGot.Ids) != 1 || mock.polEntGot.Ids[0] != "pid-1" {
		t.Errorf("EntitiesPolicyGetV2 not called with queried ID; got %+v", mock.polEntGot)
	}
}

func TestSearchPoliciesEmpty(t *testing.T) {
	mock := &mockDataProtectionAPI{polQueryResp: polQueryOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, mock) },
		"falcon_search_data_protection_policies",
		map[string]any{"platform_name": "mac"})
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
}

func TestSearchPoliciesFQLError(t *testing.T) {
	mock := &mockDataProtectionAPI{
		polQueryErr: runtime.NewAPIError("QueriesPolicyGetV2", "bad filter", 400),
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, mock) },
		"falcon_search_data_protection_policies",
		map[string]any{"platform_name": "win", "filter": "bad=="})
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
}

func TestSearchPolicies403Scopes(t *testing.T) {
	mock := &mockDataProtectionAPI{
		polQueryErr: data_protection_configuration.NewQueriesPolicyGetV2Forbidden(),
	}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, mock) },
		"falcon_search_data_protection_policies",
		map[string]any{"platform_name": "win"})
	if !contains(text, "Data Protection:read") {
		t.Errorf("expected required scope Data Protection:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ===== Content Patterns =====

func TestSearchContentPatternsTwoStep(t *testing.T) {
	mock := &mockDataProtectionAPI{
		cpQueryResp: cpQueryOK("cp-1"),
		cpEntResp:   cpEntOK("SSN Pattern"),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchContentPatterns(s, mock) },
		"falcon_search_data_protection_content_patterns",
		map[string]any{"filter": "category:'PII'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 pattern, got %d: %s", len(got), text)
	}
	if got[0]["name"] != "SSN Pattern" {
		t.Errorf("expected name 'SSN Pattern', got %v", got[0]["name"])
	}
	if mock.cpEntGot == nil || len(mock.cpEntGot.Ids) != 1 || mock.cpEntGot.Ids[0] != "cp-1" {
		t.Errorf("EntitiesContentPatternGet not called with queried ID; got %+v", mock.cpEntGot)
	}
}

func TestSearchContentPatternsEmpty(t *testing.T) {
	mock := &mockDataProtectionAPI{cpQueryResp: cpQueryOK()}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchContentPatterns(s, mock) },
		"falcon_search_data_protection_content_patterns",
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
}

func TestSearchContentPatternsFQLError(t *testing.T) {
	mock := &mockDataProtectionAPI{
		cpQueryErr: runtime.NewAPIError("QueriesContentPatternGetV2", "bad filter", 400),
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchContentPatterns(s, mock) },
		"falcon_search_data_protection_content_patterns",
		map[string]any{"filter": "bad=="})
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
}

func TestSearchContentPatterns403Scopes(t *testing.T) {
	mock := &mockDataProtectionAPI{
		cpQueryErr: data_protection_configuration.NewQueriesContentPatternGetV2Forbidden(),
	}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchContentPatterns(s, mock) },
		"falcon_search_data_protection_content_patterns",
		map[string]any{})
	if !contains(text, "Data Protection:read") {
		t.Errorf("expected required scope Data Protection:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ===== normalizeLimit =====

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 100, -1: 100, 1: 1, 100: 100, 500: 500, 999: 500}
	for in, want := range cases {
		if got := normalizeLimit(in, 100, 500); got != want {
			t.Errorf("normalizeLimit(%d, 100, 500) = %d, want %d", in, got, want)
		}
	}
}

// ===== test helpers =====

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
			return i >= 0
		}
	}
	return false
}
