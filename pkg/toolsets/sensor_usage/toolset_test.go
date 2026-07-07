package sensor_usage

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/sensor_usage_api"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockSensorUsageAPI is a hand-written mock satisfying the narrow SensorUsageAPI
// interface. Each field lets a test supply a canned response or error for the
// operation, and captures the params the toolset actually sent.
type mockSensorUsageAPI struct {
	resp *sensor_usage_api.GetSensorUsageWeeklyOK
	err  error
	got  *sensor_usage_api.GetSensorUsageWeeklyParams
}

func (m *mockSensorUsageAPI) GetSensorUsageWeekly(p *sensor_usage_api.GetSensorUsageWeeklyParams, _ ...sensor_usage_api.ClientOption) (*sensor_usage_api.GetSensorUsageWeeklyOK, error) {
	m.got = p
	return m.resp, m.err
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

func usageOK(records ...*models.EntitiesRollingAverage) *sensor_usage_api.GetSensorUsageWeeklyOK {
	return &sensor_usage_api.GetSensorUsageWeeklyOK{
		Payload: &models.APIWeeklyAverageResponse{Resources: records},
	}
}

func float64Ptr(f float64) *float64 { return &f }
func strPtr(s string) *string       { return &s }

func TestSearchSensorUsageSuccess(t *testing.T) {
	ws := float64Ptr(42.5)
	sv := float64Ptr(10.0)
	record := &models.EntitiesRollingAverage{
		Workstations:                 ws,
		ServersWithoutContainers:     sv,
		ServersWithContainers:        float64Ptr(0),
		PublicCloudWithContainers:    float64Ptr(0),
		PublicCloudWithoutContainers: float64Ptr(0),
		Mobile:                       float64Ptr(0),
		Lumos:                        float64Ptr(0),
		Containers:                   float64Ptr(0),
		ChromeOs:                     float64Ptr(0),
	}
	mock := &mockSensorUsageAPI{resp: usageOK(record)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchSensorUsage(s, mock) },
		"falcon_search_sensor_usage", map[string]any{"filter": "period:'30'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 record, got %d", len(got))
	}
	if got[0]["workstations"] != 42.5 {
		t.Errorf("expected workstations 42.5, got %v", got[0]["workstations"])
	}

	// Verify the filter was forwarded.
	if mock.got == nil {
		t.Fatal("GetSensorUsageWeekly was not called")
	}
	if mock.got.Filter == nil || *mock.got.Filter != "period:'30'" {
		t.Errorf("filter not forwarded correctly: %v", mock.got.Filter)
	}
}

func TestSearchSensorUsageEmpty(t *testing.T) {
	mock := &mockSensorUsageAPI{resp: usageOK()} // no records
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchSensorUsage(s, mock) },
		"falcon_search_sensor_usage", map[string]any{"filter": "event_date:'2024-06-11'"})
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

func TestSearchSensorUsageFQLError(t *testing.T) {
	mock := &mockSensorUsageAPI{err: runtime.NewAPIError("GetSensorUsageWeekly", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchSensorUsage(s, mock) },
		"falcon_search_sensor_usage", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	// FQL error branch must include the guide.
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

func TestSearchSensorUsage403Scopes(t *testing.T) {
	mock := &mockSensorUsageAPI{err: sensor_usage_api.NewGetSensorUsageWeeklyForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchSensorUsage(s, mock) },
		"falcon_search_sensor_usage", map[string]any{})
	// 403 is not an FQL error → no guide, but scopes should surface.
	if !contains(text, "Sensor Usage:read") {
		t.Errorf("expected required scope 'Sensor Usage:read' in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// helper functions

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
