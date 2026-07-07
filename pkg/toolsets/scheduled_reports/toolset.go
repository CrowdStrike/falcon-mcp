// Package scheduled_reports implements the Falcon MCP "scheduled_reports"
// toolset: searching scheduled reports and their executions, launching a report
// on demand, and downloading a completed execution's content.
package scheduled_reports

import (
	"context"
	"fmt"

	"github.com/crowdstrike/gofalcon/falcon/client/report_executions"
	"github.com/crowdstrike/gofalcon/falcon/client/scheduled_reports"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	reportsFQLGuideURI    = "falcon://scheduled-reports/search/fql-guide"
	executionsFQLGuideURI = "falcon://scheduled-reports/executions/search/fql-guide"
)

// ScheduledReportsAPI is the narrow slice of the scheduled_reports client used.
type ScheduledReportsAPI interface {
	Query(*scheduled_reports.QueryParams, ...scheduled_reports.ClientOption) (*scheduled_reports.QueryOK, error)
	QueryByID(*scheduled_reports.QueryByIDParams, ...scheduled_reports.ClientOption) (*scheduled_reports.QueryByIDOK, error)
	Execute(*scheduled_reports.ExecuteParams, ...scheduled_reports.ClientOption) (*scheduled_reports.ExecuteOK, error)
}

// ReportExecutionsAPI is the narrow slice of the report_executions client used
// for the query→details execution search (the binary download is handled
// separately via a FalconClient helper).
type ReportExecutionsAPI interface {
	ReportExecutionsQuery(*report_executions.ReportExecutionsQueryParams, ...report_executions.ClientOption) (*report_executions.ReportExecutionsQueryOK, error)
	ReportExecutionsGet(*report_executions.ReportExecutionsGetParams, ...report_executions.ClientOption) (*report_executions.ReportExecutionsGetOK, error)
}

// downloadFunc downloads a report execution's content by ID. It is injected so
// handlers can be unit-tested without the gofalcon transport.
type downloadFunc func(ctx context.Context, id string) ([]byte, error)

// Toolset is the scheduled_reports domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "scheduled_reports" }

func (Toolset) GetDescription() string {
	return "Access CrowdStrike Falcon scheduled reports and their executions."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(reportsFQLGuideURI, "falcon_search_scheduled_reports_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_scheduled_reports` tool."),
		fql.Resource(executionsFQLGuideURI, "falcon_search_report_executions_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_report_executions` tool."),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_scheduled_reports"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchScheduledReports(s, fc.ScheduledReports())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_launch_scheduled_report"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerLaunchScheduledReport(s, fc.ScheduledReports())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_report_executions"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchReportExecutions(s, fc.ReportExecutions())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_download_report_execution"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDownloadReportExecution(s, fc.DownloadReportExecution)
			},
		},
	}
}

// --- falcon_search_scheduled_reports (two-step: Query IDs → QueryByID details) ---

type searchScheduledReportsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://scheduled-reports/search/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-5000]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Property to sort by. Ex: created_on.asc, last_updated_on.desc."`
}

func registerSearchScheduledReports(s *mcp.Server, api ScheduledReportsAPI) {
	desc := "Search for scheduled reports in your CrowdStrike environment. Consult " +
		"falcon://scheduled-reports/search/fql-guide before constructing filter expressions. " +
		"Returns full scheduled-report details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_scheduled_reports",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchScheduledReportsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		qp := scheduled_reports.NewQueryParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = offsetString(in.Offset)
		qp.Sort = in.Sort

		queryResp, err := api.Query(qp)
		if err != nil {
			return searchErr("scheduled_reports_query", "Failed to search scheduled reports", in.Filter, reportsFQLGuideURI, err)
		}
		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := scheduled_reports.NewQueryByIDParamsWithContext(ctx)
		dp.Ids = ids
		details, err := api.QueryByID(dp)
		if err != nil {
			resp := falcon.NormalizeError("scheduled_reports_get", "Failed to get scheduled report details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details.GetPayload().Resources)
	})
}

// --- falcon_launch_scheduled_report (mutation) ---

type launchScheduledReportInput struct {
	ID string `json:"id" jsonschema:"The scheduled report ID to launch on demand."`
}

func registerLaunchScheduledReport(s *mcp.Server, api ScheduledReportsAPI) {
	desc := "Launch a scheduled report or search on demand. Executes the report immediately " +
		"outside its recurring schedule. Returns execution records containing an execution ID " +
		"that can be tracked with falcon_search_report_executions and downloaded with " +
		"falcon_download_report_execution when complete."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_launch_scheduled_report",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in launchScheduledReportInput) (*mcp.CallToolResult, any, error) {
		id := in.ID
		ep := scheduled_reports.NewExecuteParamsWithContext(ctx)
		ep.Body = []*models.DomainReportExecutionLaunchRequestV1{{ID: &id}}

		resp, err := api.Execute(ep)
		if err != nil {
			e := falcon.NormalizeError("scheduled_reports_launch", "Failed to launch scheduled report", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_search_report_executions (two-step) ---

type searchReportExecutionsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://scheduled-reports/executions/search/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-5000]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Property to sort by. Ex: created_on.asc, last_updated_on.desc."`
}

func registerSearchReportExecutions(s *mcp.Server, api ReportExecutionsAPI) {
	desc := "Search for report/search execution history. Consult " +
		"falcon://scheduled-reports/executions/search/fql-guide before constructing filter " +
		"expressions. Returns full execution details including status and download availability."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_report_executions",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchReportExecutionsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		qp := report_executions.NewReportExecutionsQueryParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = offsetString(in.Offset)
		qp.Sort = in.Sort

		queryResp, err := api.ReportExecutionsQuery(qp)
		if err != nil {
			return searchErr("report_executions_query", "Failed to search report executions", in.Filter, executionsFQLGuideURI, err)
		}
		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := report_executions.NewReportExecutionsGetParamsWithContext(ctx)
		dp.Ids = ids
		details, err := api.ReportExecutionsGet(dp)
		if err != nil {
			resp := falcon.NormalizeError("report_executions_get", "Failed to get report execution details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details.GetPayload().Resources)
	})
}

// --- falcon_download_report_execution (binary) ---

type downloadReportExecutionInput struct {
	ID string `json:"id" jsonschema:"The report execution ID to download. Get execution IDs from falcon_search_report_executions."`
}

func registerDownloadReportExecution(s *mcp.Server, download downloadFunc) {
	desc := "Download the content of a completed report execution by ID. Returns the report " +
		"content as text. Get execution IDs from falcon_search_report_executions; the execution " +
		"must be in a completed state to download."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_download_report_execution",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in downloadReportExecutionInput) (*mcp.CallToolResult, any, error) {
		if in.ID == "" {
			e := falcon.ErrorResponse{Error: "Failed to download report execution: id is required"}
			return mcpx.JSONResult([]any{e})
		}
		data, err := download(ctx, in.ID)
		if err != nil {
			e := falcon.NormalizeError("report_executions_download_get", "Failed to download report execution", err)
			return mcpx.JSONResult([]any{e})
		}
		// The report content is decoded as a UTF-8 string, matching the Python
		// module's bytes.decode('utf-8') behavior for this download endpoint.
		return mcpx.JSONResult(map[string]string{"content": string(data)})
	})
}

// --- helpers ---

func searchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// offsetString converts an optional numeric offset to the *string form the
// scheduled_reports/report_executions query params expect (they use a string
// offset token rather than an int).
func offsetString(offset *int64) *string {
	if offset == nil {
		return nil
	}
	s := fmt.Sprintf("%d", *offset)
	return &s
}

func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 5000 {
		return 5000
	}
	return limit
}
