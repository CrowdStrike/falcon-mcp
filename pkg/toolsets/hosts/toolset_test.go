package hosts

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockHostsAPI is a hand-written mock satisfying the narrow HostsAPI interface.
// Each field lets a test supply a canned response or error for one operation.
type mockHostsAPI struct {
	queryResp *hosts.QueryDevicesByFilterOK
	queryErr  error
	queryGot  *hosts.QueryDevicesByFilterParams

	detailsResp *hosts.PostDeviceDetailsV2OK
	detailsErr  error
	detailsGot  *hosts.PostDeviceDetailsV2Params
}

func (m *mockHostsAPI) QueryDevicesByFilter(p *hosts.QueryDevicesByFilterParams, _ ...hosts.ClientOption) (*hosts.QueryDevicesByFilterOK, error) {
	m.queryGot = p
	return m.queryResp, m.queryErr
}

func (m *mockHostsAPI) PostDeviceDetailsV2(p *hosts.PostDeviceDetailsV2Params, _ ...hosts.ClientOption) (*hosts.PostDeviceDetailsV2OK, error) {
	m.detailsGot = p
	return m.detailsResp, m.detailsErr
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

func queryOK(ids ...string) *hosts.QueryDevicesByFilterOK {
	return &hosts.QueryDevicesByFilterOK{Payload: &models.MsaQueryResponse{Resources: ids}}
}

func detailsOK(devs ...*models.DeviceapiDeviceSwagger) *hosts.PostDeviceDetailsV2OK {
	return &hosts.PostDeviceDetailsV2OK{Payload: &models.DeviceapiDeviceDetailsResponseSwagger{Resources: devs}}
}

func TestSearchHostsTwoStep(t *testing.T) {
	devID := "abc123"
	dev := &models.DeviceapiDeviceSwagger{DeviceID: &devID, Hostname: "PC-1"}
	mock := &mockHostsAPI{
		queryResp:   queryOK("abc123"),
		detailsResp: detailsOK(dev),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHosts(s, mock) },
		"falcon_search_hosts", map[string]any{"filter": "hostname:'PC-1'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// The result must be the full device details (never just IDs).
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["device_id"] != "abc123" || got[0]["hostname"] != "PC-1" {
		t.Fatalf("expected full host details, got %s", text)
	}

	// Step 2 must have received the ID from step 1.
	if mock.detailsGot == nil || mock.detailsGot.Body == nil ||
		len(mock.detailsGot.Body.Ids) != 1 || mock.detailsGot.Body.Ids[0] != "abc123" {
		t.Errorf("PostDeviceDetailsV2 not called with queried ID; got %+v", mock.detailsGot)
	}
}

func TestSearchHostsEmpty(t *testing.T) {
	mock := &mockHostsAPI{queryResp: queryOK()} // no IDs
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHosts(s, mock) },
		"falcon_search_hosts", map[string]any{"filter": "hostname:'nope'"})
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
	if mock.detailsGot != nil {
		t.Error("details should not be fetched when no IDs matched")
	}
}

func TestSearchHostsFQLError(t *testing.T) {
	mock := &mockHostsAPI{queryErr: runtime.NewAPIError("QueryDevicesByFilter", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHosts(s, mock) },
		"falcon_search_hosts", map[string]any{"filter": "bogus=="})
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

func TestSearchHosts403Scopes(t *testing.T) {
	mock := &mockHostsAPI{queryErr: hosts.NewQueryDevicesByFilterForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchHosts(s, mock) },
		"falcon_search_hosts", map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Hosts:read") {
		t.Errorf("expected required scope Hosts:read in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestGetHostDetailsEmptyIDs(t *testing.T) {
	mock := &mockHostsAPI{}
	text, isErr := callTool(t, func(s *mcp.Server) { registerGetHostDetails(s, mock) },
		"falcon_get_host_details", map[string]any{"ids": []any{}})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
	if mock.detailsGot != nil {
		t.Error("no API call should be made for empty IDs")
	}
}

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 5000: 5000, 9999: 5000}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// Ensure a plain (non-status) error still produces a usable result.
func TestSearchHostsTransportError(t *testing.T) {
	mock := &mockHostsAPI{queryErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchHosts(s, mock) },
		"falcon_search_hosts", map[string]any{})
	if !contains(text, "Failed to search hosts") {
		t.Errorf("expected error message, got %s", text)
	}
}

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func contains(s, sub string) bool {
	return len(s) >= len(sub) && (indexOf(s, sub) >= 0)
}

func indexOf(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}
