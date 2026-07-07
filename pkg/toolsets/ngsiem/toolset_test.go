package ngsiem

import (
	"context"
	"encoding/json"
	"strings"
	"testing"
	"time"

	"github.com/crowdstrike/gofalcon/falcon/client/ngsiem"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// --- mock ---

type mockNgsiem struct {
	// StartSearchV1
	startResp *ngsiem.StartSearchV1OK
	startErr  error

	// GetSearchStatusV1 — each call pops from the front; last entry repeats.
	statusResps []*ngsiem.GetSearchStatusV1OK
	statusErrs  []error
	statusCalls int

	// StopSearchV1
	stopCalled bool
	stopRepo   string
	stopID     string
}

func (m *mockNgsiem) StartSearchV1(p *ngsiem.StartSearchV1Params, _ ...ngsiem.ClientOption) (*ngsiem.StartSearchV1OK, error) {
	return m.startResp, m.startErr
}

func (m *mockNgsiem) GetSearchStatusV1(p *ngsiem.GetSearchStatusV1Params, _ ...ngsiem.ClientOption) (*ngsiem.GetSearchStatusV1OK, error) {
	i := m.statusCalls
	m.statusCalls++
	if i >= len(m.statusResps) {
		i = len(m.statusResps) - 1
	}
	var err error
	if i < len(m.statusErrs) {
		err = m.statusErrs[i]
	}
	return m.statusResps[i], err
}

func (m *mockNgsiem) StopSearchV1(p *ngsiem.StopSearchV1Params, _ ...ngsiem.ClientOption) (*ngsiem.StopSearchV1OK, error) {
	m.stopCalled = true
	m.stopRepo = p.Repository
	m.stopID = p.ID
	return &ngsiem.StopSearchV1OK{}, nil
}

// --- helpers ---

func noopSleep(_ time.Duration) {}

func boolPtr(b bool) *bool    { return &b }
func strPtr(s string) *string { return &s }

func jobID(id string) *ngsiem.StartSearchV1OK {
	return &ngsiem.StartSearchV1OK{
		Payload: &models.APIQueryJobResponse{
			ID:                strPtr(id),
			HashedQueryOnView: strPtr(""),
		},
	}
}

func statusDone(events []models.APIQueryJobsResultsEvents) *ngsiem.GetSearchStatusV1OK {
	done := true
	return &ngsiem.GetSearchStatusV1OK{
		Payload: &models.APIQueryJobsResults{
			Done:                   &done,
			Cancelled:              boolPtr(false),
			Events:                 events,
			FilesUsed:              []models.APIQueryJobsResultsFilesUsed{},
			FilterMatches:          []models.APIQueryJobsResultsFilterMatches{},
			MetaData:               &models.APIQueryMetadataJSON{},
			QueryEventDistribution: &models.APIQueryEventDistribution{},
			Warnings:               []*models.APIWarningJSON{},
		},
	}
}

func statusNotDone() *ngsiem.GetSearchStatusV1OK {
	return &ngsiem.GetSearchStatusV1OK{
		Payload: &models.APIQueryJobsResults{
			Done:                   boolPtr(false),
			Cancelled:              boolPtr(false),
			Events:                 []models.APIQueryJobsResultsEvents{},
			FilesUsed:              []models.APIQueryJobsResultsFilesUsed{},
			FilterMatches:          []models.APIQueryJobsResultsFilterMatches{},
			MetaData:               &models.APIQueryMetadataJSON{},
			QueryEventDistribution: &models.APIQueryEventDistribution{},
			Warnings:               []*models.APIWarningJSON{},
		},
	}
}

// callTool wires registerSearchNgsiem into a real MCP server and invokes the tool.
func callTool(t *testing.T, mock ngsiemAPI, sleep func(time.Duration), poll, tout time.Duration, args map[string]any) string {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "t", Version: "0"}, nil)
	registerSearchNgsiem(srv, mock, sleep)

	// Override poll interval/timeout captured in closure by using runSearch directly
	// — but since registerSearchNgsiem reads env at registration time, we instead
	// exercise runSearch directly for the poll/timeout tests and use the helper
	// only for wired-server tests.
	_ = poll
	_ = tout

	ct, st := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, st, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, ct, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	defer cs.Close()
	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: "falcon_search_ngsiem", Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	return res.Content[0].(*mcp.TextContent).Text
}

// --- tests ---

// TestPollUntilDone: GetSearchStatusV1 returns not-done once, then done with events.
func TestPollUntilDone(t *testing.T) {
	event := map[string]any{"field": "value"}
	mock := &mockNgsiem{
		startResp: jobID("job-1"),
		statusResps: []*ngsiem.GetSearchStatusV1OK{
			statusNotDone(),
			statusDone([]models.APIQueryJobsResultsEvents{event}),
		},
	}

	in := searchNgsiemInput{
		QueryString: "#event_simpleName=ProcessRollup2",
		Start:       "2025-01-01T00:00:00Z",
		Repository:  "search-all",
	}
	result, _, err := runSearch(context.Background(), mock, noopSleep, 0, 10*time.Second, in)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	text := result.Content[0].(*mcp.TextContent).Text
	if !strings.Contains(text, "value") {
		t.Errorf("expected events in result, got: %s", text)
	}
	if mock.stopCalled {
		t.Error("StopSearchV1 should not have been called on success")
	}
	if mock.statusCalls != 2 {
		t.Errorf("expected 2 status poll calls, got %d", mock.statusCalls)
	}
}

// TestStartError: StartSearchV1 returns an error.
func TestStartError(t *testing.T) {
	mock := &mockNgsiem{
		startErr: runtime.NewAPIError("StartSearchV1", "unauthorized", 401),
	}
	in := searchNgsiemInput{
		QueryString: "* | count()",
		Start:       "2025-01-01T00:00:00Z",
	}
	result, _, err := runSearch(context.Background(), mock, noopSleep, 0, 10*time.Second, in)
	if err != nil {
		t.Fatalf("unexpected protocol error: %v", err)
	}
	text := result.Content[0].(*mcp.TextContent).Text
	if !strings.Contains(text, "Failed to start NGSIEM search") {
		t.Errorf("expected start error message, got: %s", text)
	}
	var got []map[string]any
	if jsonErr := json.Unmarshal([]byte(text), &got); jsonErr != nil {
		t.Fatalf("result is not a JSON array: %v (%s)", jsonErr, text)
	}
}

// TestPollError: GetSearchStatusV1 returns an error.
func TestPollError(t *testing.T) {
	mock := &mockNgsiem{
		startResp:   jobID("job-2"),
		statusResps: []*ngsiem.GetSearchStatusV1OK{nil},
		statusErrs:  []error{runtime.NewAPIError("GetSearchStatusV1", "server error", 500)},
	}
	in := searchNgsiemInput{
		QueryString: "* | count()",
		Start:       "2025-01-01T00:00:00Z",
	}
	result, _, err := runSearch(context.Background(), mock, noopSleep, 0, 10*time.Second, in)
	if err != nil {
		t.Fatalf("unexpected protocol error: %v", err)
	}
	text := result.Content[0].(*mcp.TextContent).Text
	if !strings.Contains(text, "Failed to poll NGSIEM search status") {
		t.Errorf("expected poll error message, got: %s", text)
	}
}

// TestTimeout: job never completes; StopSearchV1 is called and timeout error returned.
func TestTimeout(t *testing.T) {
	mock := &mockNgsiem{
		startResp:   jobID("job-timeout"),
		statusResps: []*ngsiem.GetSearchStatusV1OK{statusNotDone()},
	}
	in := searchNgsiemInput{
		QueryString: "* | count()",
		Start:       "2025-01-01T00:00:00Z",
		Repository:  "search-all",
	}
	// Use a 0-duration timeout so the loop exits immediately after the first sleep.
	result, _, err := runSearch(context.Background(), mock, noopSleep, 0, 0, in)
	if err != nil {
		t.Fatalf("unexpected protocol error: %v", err)
	}
	text := result.Content[0].(*mcp.TextContent).Text
	if !strings.Contains(text, "timed out") {
		t.Errorf("expected timeout message, got: %s", text)
	}
	if !mock.stopCalled {
		t.Error("StopSearchV1 must be called on timeout")
	}
	if mock.stopID != "job-timeout" {
		t.Errorf("StopSearchV1 called with wrong job id %q", mock.stopID)
	}
	if mock.stopRepo != "search-all" {
		t.Errorf("StopSearchV1 called with wrong repo %q", mock.stopRepo)
	}
}

// TestToolRegistration: verifies the tool is correctly wired through the MCP server.
func TestToolRegistration(t *testing.T) {
	event := map[string]any{"key": "v"}
	mock := &mockNgsiem{
		startResp: jobID("job-wired"),
		statusResps: []*ngsiem.GetSearchStatusV1OK{
			statusDone([]models.APIQueryJobsResultsEvents{event}),
		},
	}
	text := callTool(t, mock, noopSleep, defaultPollInterval, defaultTimeout, map[string]any{
		"query_string": "#event_simpleName=DnsRequest",
		"start":        "2025-01-01T00:00:00Z",
	})
	if !strings.Contains(text, "v") {
		t.Errorf("expected event value in result: %s", text)
	}
}

// TestGetNameAndResources: verify Toolset metadata.
func TestGetNameAndResources(t *testing.T) {
	ts := Toolset{}
	if ts.GetName() != "ngsiem" {
		t.Errorf("expected name 'ngsiem', got %q", ts.GetName())
	}
	if ts.GetResources() != nil {
		t.Errorf("expected nil resources, got %v", ts.GetResources())
	}
}
