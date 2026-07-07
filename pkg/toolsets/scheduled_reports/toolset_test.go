package scheduled_reports

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/report_executions"
	"github.com/crowdstrike/gofalcon/falcon/client/scheduled_reports"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// --- mocks over the narrow interfaces ---

type mockScheduledReports struct {
	queryResp *scheduled_reports.QueryOK
	queryErr  error
	byIDResp  *scheduled_reports.QueryByIDOK
	byIDErr   error
	byIDGot   *scheduled_reports.QueryByIDParams
	execResp  *scheduled_reports.ExecuteOK
	execErr   error
	execGot   *scheduled_reports.ExecuteParams
}

func (m *mockScheduledReports) Query(p *scheduled_reports.QueryParams, _ ...scheduled_reports.ClientOption) (*scheduled_reports.QueryOK, error) {
	return m.queryResp, m.queryErr
}
func (m *mockScheduledReports) QueryByID(p *scheduled_reports.QueryByIDParams, _ ...scheduled_reports.ClientOption) (*scheduled_reports.QueryByIDOK, error) {
	m.byIDGot = p
	return m.byIDResp, m.byIDErr
}
func (m *mockScheduledReports) Execute(p *scheduled_reports.ExecuteParams, _ ...scheduled_reports.ClientOption) (*scheduled_reports.ExecuteOK, error) {
	m.execGot = p
	return m.execResp, m.execErr
}

type mockReportExecutions struct {
	queryResp *report_executions.ReportExecutionsQueryOK
	queryErr  error
	getResp   *report_executions.ReportExecutionsGetOK
	getErr    error
	getGot    *report_executions.ReportExecutionsGetParams
}

func (m *mockReportExecutions) ReportExecutionsQuery(p *report_executions.ReportExecutionsQueryParams, _ ...report_executions.ClientOption) (*report_executions.ReportExecutionsQueryOK, error) {
	return m.queryResp, m.queryErr
}
func (m *mockReportExecutions) ReportExecutionsGet(p *report_executions.ReportExecutionsGetParams, _ ...report_executions.ClientOption) (*report_executions.ReportExecutionsGetOK, error) {
	m.getGot = p
	return m.getResp, m.getErr
}

// callTool wires a register fn into a real MCP server and invokes the tool.
func callTool(t *testing.T, register func(*mcp.Server), name string, args map[string]any) string {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "t", Version: "0"}, nil)
	register(srv)
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
	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: name, Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	return res.Content[0].(*mcp.TextContent).Text
}

func strptr(s string) *string { return &s }

func TestSearchScheduledReportsTwoStep(t *testing.T) {
	id := "rpt-1"
	mock := &mockScheduledReports{
		queryResp: &scheduled_reports.QueryOK{Payload: &models.MsaQueryResponse{Resources: []string{"rpt-1"}}},
		byIDResp: &scheduled_reports.QueryByIDOK{Payload: &models.DomainScheduledReportsResultV1{
			Resources: []*models.DomainScheduledReportV1{{ID: &id}},
		}},
	}
	text := callTool(t, func(s *mcp.Server) { registerSearchScheduledReports(s, mock) },
		"falcon_search_scheduled_reports", map[string]any{"filter": "type:'dashboard'"})

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "rpt-1" {
		t.Fatalf("expected full report details, got %s", text)
	}
	if mock.byIDGot == nil || len(mock.byIDGot.Ids) != 1 || mock.byIDGot.Ids[0] != "rpt-1" {
		t.Errorf("QueryByID not called with queried ID: %+v", mock.byIDGot)
	}
}

func TestSearchScheduledReportsEmpty(t *testing.T) {
	mock := &mockScheduledReports{queryResp: &scheduled_reports.QueryOK{Payload: &models.MsaQueryResponse{}}}
	text := callTool(t, func(s *mcp.Server) { registerSearchScheduledReports(s, mock) },
		"falcon_search_scheduled_reports", map[string]any{})
	if !strings.Contains(text, `"total": 0`) {
		t.Errorf("expected empty response, got %s", text)
	}
	if mock.byIDGot != nil {
		t.Error("details fetched despite no IDs")
	}
}

func TestSearchScheduledReportsFQLError(t *testing.T) {
	mock := &mockScheduledReports{queryErr: runtime.NewAPIError("scheduled_reports_query", "bad", 400)}
	text := callTool(t, func(s *mcp.Server) { registerSearchScheduledReports(s, mock) },
		"falcon_search_scheduled_reports", map[string]any{"filter": "bad=="})
	if !strings.Contains(text, "fql_guide") {
		t.Errorf("expected fql_guide in 400 response: %s", text)
	}
}

func TestLaunchScheduledReport(t *testing.T) {
	execID := "exec-9"
	mock := &mockScheduledReports{
		execResp: &scheduled_reports.ExecuteOK{Payload: &models.DomainReportExecutionsResponseV1{
			Resources: []*models.DomainReportExecutionV1{{ID: &execID}},
		}},
	}
	text := callTool(t, func(s *mcp.Server) { registerLaunchScheduledReport(s, mock) },
		"falcon_launch_scheduled_report", map[string]any{"id": "rpt-1"})
	if !strings.Contains(text, "exec-9") {
		t.Errorf("expected execution id in result: %s", text)
	}
	// Body must carry the requested report ID.
	if mock.execGot == nil || len(mock.execGot.Body) != 1 || mock.execGot.Body[0].ID == nil || *mock.execGot.Body[0].ID != "rpt-1" {
		t.Errorf("Execute body missing report id: %+v", mock.execGot)
	}
}

func TestSearchReportExecutionsTwoStep(t *testing.T) {
	id := "exec-1"
	mock := &mockReportExecutions{
		queryResp: &report_executions.ReportExecutionsQueryOK{Payload: &models.MsaQueryResponse{Resources: []string{"exec-1"}}},
		getResp: &report_executions.ReportExecutionsGetOK{Payload: &models.DomainReportExecutionsResponseV1{
			Resources: []*models.DomainReportExecutionV1{{ID: &id}},
		}},
	}
	text := callTool(t, func(s *mcp.Server) { registerSearchReportExecutions(s, mock) },
		"falcon_search_report_executions", map[string]any{})
	if !strings.Contains(text, "exec-1") {
		t.Errorf("expected execution details: %s", text)
	}
	if mock.getGot == nil || len(mock.getGot.Ids) != 1 {
		t.Errorf("Get not called with queried IDs: %+v", mock.getGot)
	}
}

func TestDownloadReportExecution(t *testing.T) {
	download := func(_ context.Context, id string) ([]byte, error) {
		if id != "exec-1" {
			t.Errorf("unexpected id %q", id)
		}
		return []byte("report,csv,content\n1,2,3"), nil
	}
	text := callTool(t, func(s *mcp.Server) { registerDownloadReportExecution(s, download) },
		"falcon_download_report_execution", map[string]any{"id": "exec-1"})
	var got map[string]string
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not object: %v", err)
	}
	if !strings.Contains(got["content"], "report,csv,content") {
		t.Errorf("content not returned: %s", text)
	}
}

func TestDownloadReportExecutionError(t *testing.T) {
	download := func(_ context.Context, _ string) ([]byte, error) {
		return nil, errors.New("boom")
	}
	text := callTool(t, func(s *mcp.Server) { registerDownloadReportExecution(s, download) },
		"falcon_download_report_execution", map[string]any{"id": "exec-1"})
	if !strings.Contains(text, "Failed to download report execution") {
		t.Errorf("expected error message: %s", text)
	}
}

func TestOffsetString(t *testing.T) {
	if offsetString(nil) != nil {
		t.Error("nil offset should map to nil")
	}
	v := int64(42)
	if got := offsetString(&v); got == nil || *got != "42" {
		t.Errorf("offsetString(42) = %v, want 42", got)
	}
}

// compile guard for the download strptr helper usage in future edits.
var _ = strptr
