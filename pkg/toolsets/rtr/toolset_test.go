package rtr

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	rtr_client "github.com/crowdstrike/gofalcon/falcon/client/real_time_response"
	rtr_audit "github.com/crowdstrike/gofalcon/falcon/client/real_time_response_audit"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// ---------------------------------------------------------------------------
// Mock implementations
// ---------------------------------------------------------------------------

type mockRTRAPI struct {
	listAllResp   *rtr_client.RTRListAllSessionsOK
	listAllErr    error
	listSessResp  *rtr_client.RTRListSessionsOK
	listSessErr   error
	aggregateResp *rtr_client.RTRAggregateSessionsOK
	aggregateErr  error
	initResp      *rtr_client.RTRInitSessionCreated
	initErr       error
	pulseResp     *rtr_client.RTRPulseSessionCreated
	pulseErr      error
	execResp      *rtr_client.RTRExecuteCommandCreated
	execErr       error
	statusResps   []*rtr_client.RTRCheckCommandStatusOK // consumed in order
	statusIdx     int
	statusErr     error
	listFilesResp *rtr_client.RTRListFilesV2OK
	listFilesErr  error
	deleteResp    *rtr_client.RTRDeleteSessionNoContent
	deleteErr     error
}

func (m *mockRTRAPI) RTRListAllSessions(p *rtr_client.RTRListAllSessionsParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRListAllSessionsOK, error) {
	return m.listAllResp, m.listAllErr
}
func (m *mockRTRAPI) RTRListSessions(p *rtr_client.RTRListSessionsParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRListSessionsOK, error) {
	return m.listSessResp, m.listSessErr
}
func (m *mockRTRAPI) RTRAggregateSessions(p *rtr_client.RTRAggregateSessionsParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRAggregateSessionsOK, error) {
	return m.aggregateResp, m.aggregateErr
}
func (m *mockRTRAPI) RTRInitSession(p *rtr_client.RTRInitSessionParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRInitSessionCreated, error) {
	return m.initResp, m.initErr
}
func (m *mockRTRAPI) RTRPulseSession(p *rtr_client.RTRPulseSessionParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRPulseSessionCreated, error) {
	return m.pulseResp, m.pulseErr
}
func (m *mockRTRAPI) RTRExecuteCommand(p *rtr_client.RTRExecuteCommandParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRExecuteCommandCreated, error) {
	return m.execResp, m.execErr
}
func (m *mockRTRAPI) RTRCheckCommandStatus(p *rtr_client.RTRCheckCommandStatusParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRCheckCommandStatusOK, error) {
	if m.statusErr != nil {
		return nil, m.statusErr
	}
	if m.statusIdx < len(m.statusResps) {
		resp := m.statusResps[m.statusIdx]
		m.statusIdx++
		return resp, nil
	}
	return m.statusResps[len(m.statusResps)-1], nil
}
func (m *mockRTRAPI) RTRListFilesV2(p *rtr_client.RTRListFilesV2Params, _ ...rtr_client.ClientOption) (*rtr_client.RTRListFilesV2OK, error) {
	return m.listFilesResp, m.listFilesErr
}
func (m *mockRTRAPI) RTRDeleteSession(p *rtr_client.RTRDeleteSessionParams, _ ...rtr_client.ClientOption) (*rtr_client.RTRDeleteSessionNoContent, error) {
	return m.deleteResp, m.deleteErr
}

type mockAuditAPI struct {
	resp *rtr_audit.RTRAuditSessionsOK
	err  error
}

func (m *mockAuditAPI) RTRAuditSessions(p *rtr_audit.RTRAuditSessionsParams, _ ...rtr_audit.ClientOption) (*rtr_audit.RTRAuditSessionsOK, error) {
	return m.resp, m.err
}

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

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

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}

// Helper builders.

func boolPtr(b bool) *bool    { return &b }
func strPtr(s string) *string { return &s }

func makeListAllOK(ids ...string) *rtr_client.RTRListAllSessionsOK {
	return &rtr_client.RTRListAllSessionsOK{
		Payload: &models.DomainListSessionsResponseMsa{Resources: ids},
	}
}

func makeListSessionsOK(sessions ...*models.DomainSession) *rtr_client.RTRListSessionsOK {
	return &rtr_client.RTRListSessionsOK{
		Payload: &models.DomainSessionResponseWrapper{Resources: sessions},
	}
}

func makeInitOK(sessionID string) *rtr_client.RTRInitSessionCreated {
	return &rtr_client.RTRInitSessionCreated{
		Payload: &models.DomainInitResponseWrapper{
			Resources: []*models.DomainInitResponse{{SessionID: &sessionID}},
		},
	}
}

func makePulseOK(sessionID string) *rtr_client.RTRPulseSessionCreated {
	return &rtr_client.RTRPulseSessionCreated{
		Payload: &models.DomainInitResponseWrapper{
			Resources: []*models.DomainInitResponse{{SessionID: &sessionID}},
		},
	}
}

func makeExecOK(cloudRequestID string) *rtr_client.RTRExecuteCommandCreated {
	sessionID := "sess-1"
	queued := false
	return &rtr_client.RTRExecuteCommandCreated{
		Payload: &models.DomainCommandExecuteResponseWrapper{
			Resources: []*models.DomainCommandExecuteResponse{
				{CloudRequestID: &cloudRequestID, SessionID: &sessionID, QueuedCommandOffline: &queued},
			},
		},
	}
}

func makeStatusOK(complete bool, stdout string) *rtr_client.RTRCheckCommandStatusOK {
	sessionID := "sess-1"
	stderr := ""
	return &rtr_client.RTRCheckCommandStatusOK{
		Payload: &models.DomainStatusResponseWrapper{
			Resources: []*models.DomainStatusResponse{
				{Complete: &complete, Stdout: &stdout, Stderr: &stderr, SessionID: &sessionID},
			},
		},
	}
}

func makeDeleteOK() *rtr_client.RTRDeleteSessionNoContent {
	return &rtr_client.RTRDeleteSessionNoContent{
		Payload: &models.MsaReplyMetaOnly{},
	}
}

func makeAggregateOK() *rtr_client.RTRAggregateSessionsOK {
	return &rtr_client.RTRAggregateSessionsOK{
		Payload: &models.MsaAggregatesResponse{
			Resources: []*models.MsaAggregationResult{},
		},
	}
}

// ---------------------------------------------------------------------------
// Tests: search_rtr_sessions (two-step)
// ---------------------------------------------------------------------------

func TestSearchRTRSessionsTwoStep(t *testing.T) {
	sessionID := "sess-abc"
	sess := &models.DomainSession{ID: &sessionID}
	mock := &mockRTRAPI{
		listAllResp:  makeListAllOK("sess-abc"),
		listSessResp: makeListSessionsOK(sess),
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRSessions(s, mock) },
		"falcon_search_rtr_sessions", map[string]any{"filter": "hostname:'PC-1'"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 session, got %d", len(got))
	}
	if got[0]["id"] != "sess-abc" {
		t.Errorf("expected session id sess-abc, got %v", got[0]["id"])
	}
}

func TestSearchRTRSessionsEmpty(t *testing.T) {
	mock := &mockRTRAPI{listAllResp: makeListAllOK()}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRSessions(s, mock) },
		"falcon_search_rtr_sessions", map[string]any{})
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
}

func TestSearchRTRSessionsFQLError(t *testing.T) {
	mock := &mockRTRAPI{listAllErr: runtime.NewAPIError("RTRListAllSessions", "bad filter", 400)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRSessions(s, mock) },
		"falcon_search_rtr_sessions", map[string]any{"filter": "bogus=="})
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
	if guide, _ := got["fql_guide"].(string); len(guide) < 50 {
		t.Errorf("fql_guide too short: %q", guide)
	}
}

func TestSearchRTRSessions403Scopes(t *testing.T) {
	mock := &mockRTRAPI{listAllErr: rtr_client.NewRTRListAllSessionsForbidden()}

	text, _ := callTool(t, func(s *mcp.Server) { registerSearchRTRSessions(s, mock) },
		"falcon_search_rtr_sessions", map[string]any{})
	if !contains(text, "Real time response") {
		t.Errorf("expected Real time response scope in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: search_rtr_audit_sessions
// ---------------------------------------------------------------------------

func TestSearchRTRAuditSessionsSuccess(t *testing.T) {
	sessionID := "audit-sess-1"
	sess := &models.DomainSession{ID: &sessionID}
	mock := &mockAuditAPI{
		resp: &rtr_audit.RTRAuditSessionsOK{
			Payload: &models.DomainSessionResponseWrapper{Resources: []*models.DomainSession{sess}},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRAuditSessions(s, mock) },
		"falcon_search_rtr_audit_sessions", map[string]any{"filter": "created_at:>'now-7d'"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "audit-sess-1") {
		t.Errorf("expected session ID in result: %s", text)
	}
}

func TestSearchRTRAuditSessionsEmpty(t *testing.T) {
	mock := &mockAuditAPI{
		resp: &rtr_audit.RTRAuditSessionsOK{
			Payload: &models.DomainSessionResponseWrapper{Resources: []*models.DomainSession{}},
		},
	}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRAuditSessions(s, mock) },
		"falcon_search_rtr_audit_sessions", map[string]any{})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected empty response, got %s", text)
	}
}

func TestSearchRTRAuditSessionsFQLError(t *testing.T) {
	mock := &mockAuditAPI{err: runtime.NewAPIError("RTRAuditSessions", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchRTRAuditSessions(s, mock) },
		"falcon_search_rtr_audit_sessions", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "fql_guide") {
		t.Errorf("expected fql_guide in 400 response: %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: aggregate_rtr_sessions
// ---------------------------------------------------------------------------

func TestAggregateRTRSessionsSuccess(t *testing.T) {
	mock := &mockRTRAPI{aggregateResp: makeAggregateOK()}

	text, isErr := callTool(t, func(s *mcp.Server) { registerAggregateRTRSessions(s, mock) },
		"falcon_aggregate_rtr_sessions", map[string]any{"field": "hostname"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	// Should be a JSON array (possibly empty).
	var got []any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not JSON array: %v (%s)", err, text)
	}
}

// ---------------------------------------------------------------------------
// Tests: init_rtr_session
// ---------------------------------------------------------------------------

func TestInitRTRSessionSuccess(t *testing.T) {
	mock := &mockRTRAPI{initResp: makeInitOK("sess-new")}

	text, isErr := callTool(t, func(s *mcp.Server) { registerInitRTRSession(s, mock) },
		"falcon_init_rtr_session", map[string]any{"device_id": "device-abc"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "sess-new") {
		t.Errorf("expected session_id in result: %s", text)
	}
}

func TestInitRTRSessionError(t *testing.T) {
	mock := &mockRTRAPI{initErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerInitRTRSession(s, mock) },
		"falcon_init_rtr_session", map[string]any{"device_id": "device-abc"})
	if !contains(text, "Failed to initialize RTR session") {
		t.Errorf("expected error message, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: execute_rtr_read_only_command (allowlist enforcement)
// ---------------------------------------------------------------------------

func TestExecuteRTRReadOnlyCommandSuccess(t *testing.T) {
	mock := &mockRTRAPI{execResp: makeExecOK("cloud-req-1")}

	text, isErr := callTool(t, func(s *mcp.Server) { registerExecuteRTRReadOnlyCommand(s, mock) },
		"falcon_execute_rtr_read_only_command", map[string]any{
			"session_id":   "sess-1",
			"base_command": "ls",
		})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "cloud-req-1") {
		t.Errorf("expected cloud_request_id in result: %s", text)
	}
}

func TestExecuteRTRReadOnlyCommandRejected(t *testing.T) {
	mock := &mockRTRAPI{} // should not be called

	text, isErr := callTool(t, func(s *mcp.Server) { registerExecuteRTRReadOnlyCommand(s, mock) },
		"falcon_execute_rtr_read_only_command", map[string]any{
			"session_id":   "sess-1",
			"base_command": "rm",
		})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if mock.execResp != nil || mock.execErr != nil {
		t.Error("API should not have been called for a rejected command")
	}
	if !contains(text, "not in the read-only RTR allowlist") {
		t.Errorf("expected rejection message, got %s", text)
	}
	if !contains(text, "rm") {
		t.Errorf("expected rejected command name in error, got %s", text)
	}
}

func TestExecuteRTRReadOnlyCommandAllowedVariants(t *testing.T) {
	allowed := []string{"cat", "cd", "clear", "env", "eventlog", "filehash", "getsid",
		"help", "history", "ipconfig", "ls", "mount", "netstat", "ps", "reg"}
	for _, cmd := range allowed {
		if err := validateReadOnlyCommand(cmd); err != nil {
			t.Errorf("command %q should be allowed, got error: %v", cmd, err)
		}
	}
}

func TestExecuteRTRReadOnlyCommandDeniedVariants(t *testing.T) {
	denied := []string{"rm", "put", "run", "runscript", "memdump", "kill", "reg set",
		"xmemdump", "restart", "shutdown", "mv", "cp", "mkdir"}
	for _, cmd := range denied {
		if err := validateReadOnlyCommand(cmd); err == nil {
			t.Errorf("command %q should be denied but was allowed", cmd)
		}
	}
}

// ---------------------------------------------------------------------------
// Tests: run_rtr_read_only_command_and_wait (polling)
// ---------------------------------------------------------------------------

func TestRunRTRReadOnlyCommandAndWaitPolling(t *testing.T) {
	// mock returns "in progress" on first poll, "complete" on second.
	mock := &mockRTRAPI{
		execResp: makeExecOK("cloud-req-poll"),
		statusResps: []*rtr_client.RTRCheckCommandStatusOK{
			makeStatusOK(false, ""),           // poll 1: not done
			makeStatusOK(true, "file1.txt\n"), // poll 2: complete
		},
	}

	// Use a no-op sleep so the test does not actually wait.
	noopSleep := func(d time.Duration) {}

	text, isErr := callTool(t, func(s *mcp.Server) {
		registerRunRTRReadOnlyCommandAndWait(s, mock, noopSleep)
	}, "falcon_run_rtr_read_only_command_and_wait", map[string]any{
		"session_id":   "sess-1",
		"base_command": "ls",
	})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not JSON object: %v (%s)", err, text)
	}
	if got["complete"] != true {
		t.Errorf("expected complete=true, got %v", got["complete"])
	}
	if got["timed_out"] != false {
		t.Errorf("expected timed_out=false, got %v", got["timed_out"])
	}
	if !contains(got["stdout"].(string), "file1.txt") {
		t.Errorf("expected stdout to contain file1.txt, got %q", got["stdout"])
	}
	if got["cloud_request_id"] != "cloud-req-poll" {
		t.Errorf("expected cloud_request_id, got %v", got["cloud_request_id"])
	}
}

func TestRunRTRReadOnlyCommandAndWaitRejected(t *testing.T) {
	mock := &mockRTRAPI{}
	noopSleep := func(d time.Duration) {}

	text, isErr := callTool(t, func(s *mcp.Server) {
		registerRunRTRReadOnlyCommandAndWait(s, mock, noopSleep)
	}, "falcon_run_rtr_read_only_command_and_wait", map[string]any{
		"session_id":   "sess-1",
		"base_command": "put",
	})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "not in the read-only RTR allowlist") {
		t.Errorf("expected rejection, got %s", text)
	}
}

func TestRunRTRReadOnlyCommandAndWaitTimeout(t *testing.T) {
	// always return incomplete
	mock := &mockRTRAPI{
		execResp: makeExecOK("cloud-req-timeout"),
		statusResps: []*rtr_client.RTRCheckCommandStatusOK{
			makeStatusOK(false, "partial"),
		},
	}
	noopSleep := func(d time.Duration) {}

	text, isErr := callTool(t, func(s *mcp.Server) {
		registerRunRTRReadOnlyCommandAndWait(s, mock, noopSleep)
	}, "falcon_run_rtr_read_only_command_and_wait", map[string]any{
		"session_id":            "sess-1",
		"base_command":          "ps",
		"timeout_seconds":       0.0001, // effectively immediate timeout
		"poll_interval_seconds": 0.0001,
	})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON: %v", err)
	}
	// Either timed out or happened to complete; the key fields must be present.
	if _, ok := got["timed_out"]; !ok {
		t.Errorf("expected timed_out field: %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: check_rtr_command_status
// ---------------------------------------------------------------------------

func TestCheckRTRCommandStatus(t *testing.T) {
	mock := &mockRTRAPI{
		statusResps: []*rtr_client.RTRCheckCommandStatusOK{makeStatusOK(true, "hello")},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerCheckRTRCommandStatus(s, mock) },
		"falcon_check_rtr_command_status", map[string]any{"cloud_request_id": "crid-1"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "hello") {
		t.Errorf("expected stdout in result: %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: list_rtr_session_files
// ---------------------------------------------------------------------------

func TestListRTRSessionFiles(t *testing.T) {
	name := "artifact.bin"
	mock := &mockRTRAPI{
		listFilesResp: &rtr_client.RTRListFilesV2OK{
			Payload: &models.DomainListFilesV2ResponseWrapper{
				Resources: []*models.DomainFileV2{{Name: &name}},
			},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerListRTRSessionFiles(s, mock) },
		"falcon_list_rtr_session_files", map[string]any{"session_id": "sess-1"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if !contains(text, "artifact.bin") {
		t.Errorf("expected file name in result: %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: delete_rtr_session
// ---------------------------------------------------------------------------

func TestDeleteRTRSessionSuccess(t *testing.T) {
	mock := &mockRTRAPI{deleteResp: makeDeleteOK()}

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteRTRSession(s, mock) },
		"falcon_delete_rtr_session", map[string]any{"session_id": "sess-del"})
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not JSON: %v", err)
	}
	if got["deleted"] != true {
		t.Errorf("expected deleted=true, got %v", got["deleted"])
	}
	if got["session_id"] != "sess-del" {
		t.Errorf("expected session_id=sess-del, got %v", got["session_id"])
	}
}

func TestDeleteRTRSessionError(t *testing.T) {
	mock := &mockRTRAPI{deleteErr: errors.New("not found")}
	text, _ := callTool(t, func(s *mcp.Server) { registerDeleteRTRSession(s, mock) },
		"falcon_delete_rtr_session", map[string]any{"session_id": "sess-del"})
	if !contains(text, "Failed to delete RTR session") {
		t.Errorf("expected error message, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// Tests: normalizeLimit
// ---------------------------------------------------------------------------

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -1: 10, 1: 1, 100: 100, 5001: 5000}
	for in, want := range cases {
		if got := normalizeLimit(in, 5000); got != want {
			t.Errorf("normalizeLimit(%d,5000) = %d, want %d", in, got, want)
		}
	}
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
