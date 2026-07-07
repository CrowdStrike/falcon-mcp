// Package rtr implements the Falcon MCP "rtr" toolset: Real Time Response
// session lifecycle — search, audit, aggregate, init, pulse, execute read-only
// commands, poll until completion, check status, list files, and delete sessions.
package rtr

import (
	"context"
	"fmt"
	"strings"
	"time"

	rtr_client "github.com/crowdstrike/gofalcon/falcon/client/real_time_response"
	rtr_audit "github.com/crowdstrike/gofalcon/falcon/client/real_time_response_audit"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	sessionsFQLGuideURI   = "falcon://rtr/sessions/search/fql-guide"
	auditFQLGuideURI      = "falcon://rtr/audit/sessions/search/fql-guide"
	sessionsAggregateURI  = "falcon://rtr/sessions/aggregate-guide"
	investigationGuideURI = "falcon://rtr/workflows/investigation-guide"
)

// readOnlyCommands is the exact set of RTR commands allowed by the Python module.
// Any base_command not in this set is rejected before reaching the API.
var readOnlyCommands = map[string]bool{
	"cat":      true,
	"cd":       true,
	"clear":    true,
	"env":      true,
	"eventlog": true,
	"filehash": true,
	"getsid":   true,
	"help":     true,
	"history":  true,
	"ipconfig": true,
	"ls":       true,
	"mount":    true,
	"netstat":  true,
	"ps":       true,
	"reg":      true,
}

// readOnlyCommandList is a sorted display string used in error messages.
var readOnlyCommandList = "cat, cd, clear, env, eventlog, filehash, getsid, help, history, ipconfig, ls, mount, netstat, ps, reg"

// RTRAPI is the narrow slice of the real_time_response client used.
type RTRAPI interface {
	RTRListAllSessions(*rtr_client.RTRListAllSessionsParams, ...rtr_client.ClientOption) (*rtr_client.RTRListAllSessionsOK, error)
	RTRListSessions(*rtr_client.RTRListSessionsParams, ...rtr_client.ClientOption) (*rtr_client.RTRListSessionsOK, error)
	RTRAggregateSessions(*rtr_client.RTRAggregateSessionsParams, ...rtr_client.ClientOption) (*rtr_client.RTRAggregateSessionsOK, error)
	RTRInitSession(*rtr_client.RTRInitSessionParams, ...rtr_client.ClientOption) (*rtr_client.RTRInitSessionCreated, error)
	RTRPulseSession(*rtr_client.RTRPulseSessionParams, ...rtr_client.ClientOption) (*rtr_client.RTRPulseSessionCreated, error)
	RTRExecuteCommand(*rtr_client.RTRExecuteCommandParams, ...rtr_client.ClientOption) (*rtr_client.RTRExecuteCommandCreated, error)
	RTRCheckCommandStatus(*rtr_client.RTRCheckCommandStatusParams, ...rtr_client.ClientOption) (*rtr_client.RTRCheckCommandStatusOK, error)
	RTRListFilesV2(*rtr_client.RTRListFilesV2Params, ...rtr_client.ClientOption) (*rtr_client.RTRListFilesV2OK, error)
	RTRDeleteSession(*rtr_client.RTRDeleteSessionParams, ...rtr_client.ClientOption) (*rtr_client.RTRDeleteSessionNoContent, error)
}

// RTRAuditAPI is the narrow slice of the real_time_response_audit client used.
type RTRAuditAPI interface {
	RTRAuditSessions(*rtr_audit.RTRAuditSessionsParams, ...rtr_audit.ClientOption) (*rtr_audit.RTRAuditSessionsOK, error)
}

// sleepFunc is an injectable sleep for run_and_wait polling. In production it is
// time.Sleep; in tests it can be a no-op so the poll loop finishes instantly.
type sleepFunc func(time.Duration)

// Toolset is the rtr domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "rtr" }

func (Toolset) GetDescription() string {
	return "Real Time Response session lifecycle for CrowdStrike Falcon: search, init, execute read-only commands, and manage RTR sessions."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(sessionsFQLGuideURI,
			"falcon_search_rtr_sessions_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_rtr_sessions` tool."),
		fql.Resource(auditFQLGuideURI,
			"falcon_search_rtr_audit_sessions_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_rtr_audit_sessions` tool."),
		fql.Resource(sessionsAggregateURI,
			"falcon_aggregate_rtr_sessions_guide",
			"Explains how to summarize RTR session activity with the `falcon_aggregate_rtr_sessions` tool."),
		fql.Resource(investigationGuideURI,
			"falcon_rtr_read_only_investigation_guide",
			"Provides a safe read-only RTR workflow for endpoint investigation tools."),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	rtrAPI := fc.RealTimeResponse()
	auditAPI := fc.RealTimeResponseAudit()
	sleep := time.Sleep

	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_rtr_sessions"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchRTRSessions(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_rtr_audit_sessions"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchRTRAuditSessions(s, auditAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_aggregate_rtr_sessions"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerAggregateRTRSessions(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_rtr_session_details"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetRTRSessionDetails(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_init_rtr_session"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerInitRTRSession(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_pulse_rtr_session"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerPulseRTRSession(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_execute_rtr_read_only_command"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerExecuteRTRReadOnlyCommand(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_run_rtr_read_only_command_and_wait"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerRunRTRReadOnlyCommandAndWait(s, rtrAPI, sleep)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_check_rtr_command_status"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCheckRTRCommandStatus(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_list_rtr_session_files"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerListRTRSessionFiles(s, rtrAPI)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_rtr_session"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteRTRSession(s, rtrAPI)
			},
		},
	}
}

// --- falcon_search_rtr_sessions (two-step: RTRListAllSessions IDs → RTRListSessions details) ---

type searchRTRSessionsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://rtr/sessions/search/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of RTR session IDs to return [1-5000]. Default 10."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort RTR sessions by a property. Ex: created_at.asc, updated_at.desc, hostname.asc."`
}

func registerSearchRTRSessions(s *mcp.Server, api RTRAPI) {
	desc := "Search RTR sessions and return full session details. Use this to find sessions " +
		"by hostname, agent ID, user, or creation time. Consult " +
		"falcon://rtr/sessions/search/fql-guide before constructing filter expressions. " +
		"Returns session metadata including host info, commands executed, and status."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_rtr_sessions",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchRTRSessionsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 5000)

		qp := rtr_client.NewRTRListAllSessionsParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.RTRListAllSessions(qp)
		if err != nil {
			return rtrSearchErr("RTR_ListAllSessions", "Failed to search RTR sessions", in.Filter, sessionsFQLGuideURI, err)
		}
		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := rtr_client.NewRTRListSessionsParamsWithContext(ctx)
		dp.Body = &models.MsaIdsRequest{Ids: ids}
		details, err := api.RTRListSessions(dp)
		if err != nil {
			resp := falcon.NormalizeError("RTR_ListSessions", "Failed to get RTR session details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details.GetPayload().Resources)
	})
}

// --- falcon_search_rtr_audit_sessions ---

type searchRTRAuditSessionsInput struct {
	Filter          *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://rtr/audit/sessions/search/fql-guide for syntax. Ex: created_at:>'now-7d'."`
	Limit           int64   `json:"limit,omitempty" jsonschema:"Maximum number of RTR audit session records to return [1-1000]. Default 10."`
	Offset          *string `json:"offset,omitempty" jsonschema:"Starting index of the audit result set."`
	Sort            *string `json:"sort,omitempty" jsonschema:"Sort RTR audit sessions using pipe syntax. Ex: created_at|desc, updated_at|asc."`
	WithCommandInfo *bool   `json:"with_command_info,omitempty" jsonschema:"Include command IDs and command log fields in the audit response."`
}

func registerSearchRTRAuditSessions(s *mcp.Server, api RTRAuditAPI) {
	desc := "Search RTR audit sessions for accountability and timeline evidence. Use this " +
		"when you need to understand who used RTR, when they used it, which host was targeted, " +
		"or which command activity Falcon recorded. Consult " +
		"falcon://rtr/audit/sessions/search/fql-guide before constructing filter expressions. " +
		"This is read-only audit visibility; it does not open sessions or run commands."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_rtr_audit_sessions",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchRTRAuditSessionsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 1000)
		limitStr := fmt.Sprintf("%d", limit)

		ap := rtr_audit.NewRTRAuditSessionsParamsWithContext(ctx)
		ap.Filter = in.Filter
		ap.Limit = &limitStr
		ap.Offset = in.Offset
		ap.Sort = in.Sort
		ap.WithCommandInfo = in.WithCommandInfo

		resp, err := api.RTRAuditSessions(ap)
		if err != nil {
			return rtrSearchErr("RTRAuditSessions", "Failed to search RTR audit sessions", in.Filter, auditFQLGuideURI, err)
		}
		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_aggregate_rtr_sessions ---

type dateRange struct {
	From string `json:"from"`
	To   string `json:"to"`
}

type aggregateRTRSessionsInput struct {
	Field         string      `json:"field" jsonschema:"RTR session field to aggregate, such as hostname, user_id, origin, base_command, or created_at."`
	AggregateType string      `json:"aggregate_type,omitempty" jsonschema:"Aggregation type: terms (top values) or date_range (time buckets). Default: terms."`
	Name          string      `json:"name,omitempty" jsonschema:"Friendly name for the aggregation returned by Falcon. Default: rtr_session_aggregation."`
	Filter        *string     `json:"filter,omitempty" jsonschema:"FQL filter expression to scope the aggregation."`
	Size          *int32      `json:"size,omitempty" jsonschema:"Maximum buckets to return for terms aggregations [1-1000]. Default 10."`
	Interval      *string     `json:"interval,omitempty" jsonschema:"Optional interval for date range aggregations, such as day or hour."`
	DateRanges    []dateRange `json:"date_ranges,omitempty" jsonschema:"Date ranges for date_range aggregations. Ex: [{from: now-7d, to: now}]."`
}

func registerAggregateRTRSessions(s *mcp.Server, api RTRAPI) {
	desc := "Summarize RTR session activity with Falcon aggregation buckets. Use this before " +
		"detailed searches when the user asks which hosts, users, origins, commands, or time " +
		"windows account for RTR activity. Consult falcon://rtr/sessions/aggregate-guide for " +
		"examples. This is read-only summary visibility; it does not open sessions or run commands."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_aggregate_rtr_sessions",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in aggregateRTRSessionsInput) (*mcp.CallToolResult, any, error) {
		aggType := in.AggregateType
		if aggType == "" {
			aggType = "terms"
		}
		name := in.Name
		if name == "" {
			name = "rtr_session_aggregation"
		}

		empty := ""
		emptyBool := false
		emptyBucketKey := ""
		from := int32(0)

		size := int32(10)
		if in.Size != nil {
			size = *in.Size
		}

		req := &models.MsaAggregateQueryRequest{
			Type:          &aggType,
			Name:          &name,
			Field:         &in.Field,
			Filter:        &empty,
			Interval:      &empty,
			Exclude:       &empty,
			Include:       &empty,
			Missing:       &empty,
			Q:             &empty,
			Sort:          &empty,
			TimeZone:      &empty,
			From:          &from,
			Size:          &size,
			Percents:      []float64{},
			Ranges:        []*models.MsaRangeSpec{},
			SubAggregates: []*models.MsaAggregateQueryRequest{},
			FiltersSpec: &models.MsaAPIFiltersSpec{
				Filters:        map[string]string{},
				OtherBucket:    &emptyBool,
				OtherBucketKey: &emptyBucketKey,
			},
			DateRanges: []*models.MsaDateRangeSpec{},
		}

		if in.Filter != nil {
			req.Filter = in.Filter
		}
		if in.Interval != nil {
			req.Interval = in.Interval
		}
		for _, dr := range in.DateRanges {
			from := dr.From
			to := dr.To
			req.DateRanges = append(req.DateRanges, &models.MsaDateRangeSpec{From: &from, To: &to})
		}

		ap := rtr_client.NewRTRAggregateSessionsParamsWithContext(ctx)
		ap.Body = []*models.MsaAggregateQueryRequest{req}

		resp, err := api.RTRAggregateSessions(ap)
		if err != nil {
			e := falcon.NormalizeError("RTR_AggregateSessions", "Failed to aggregate RTR sessions", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_get_rtr_session_details ---

type getRTRSessionDetailsInput struct {
	IDs []string `json:"ids" jsonschema:"RTR session IDs to retrieve details for."`
}

func registerGetRTRSessionDetails(s *mcp.Server, api RTRAPI) {
	desc := "Retrieve detailed metadata for one or more RTR sessions by ID. Use when you " +
		"already have session IDs from search results. For discovering sessions by criteria, " +
		"use falcon_search_rtr_sessions instead. Returns full session records."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_rtr_session_details",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getRTRSessionDetailsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{})
		}
		dp := rtr_client.NewRTRListSessionsParamsWithContext(ctx)
		dp.Body = &models.MsaIdsRequest{Ids: in.IDs}
		resp, err := api.RTRListSessions(dp)
		if err != nil {
			e := falcon.NormalizeError("RTR_ListSessions", "Failed to get RTR session details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_init_rtr_session (mutation) ---

type initRTRSessionInput struct {
	DeviceID        string  `json:"device_id" jsonschema:"The host agent ID (AID) to open or reuse an RTR session for."`
	Origin          string  `json:"origin,omitempty" jsonschema:"Origin label for the RTR request. Default: falcon-mcp."`
	QueueOffline    bool    `json:"queue_offline,omitempty" jsonschema:"Queue the request if the host is currently offline."`
	Timeout         *int64  `json:"timeout,omitempty" jsonschema:"How long to wait for the request in seconds [1-600]."`
	TimeoutDuration *string `json:"timeout_duration,omitempty" jsonschema:"Alternate duration syntax such as 30s, 2m, or 1h."`
}

func registerInitRTRSession(s *mcp.Server, api RTRAPI) {
	desc := "Initialize or reuse an RTR session for a single host. Opens a live connection " +
		"to the specified device for executing RTR commands. Use queue_offline=true if the " +
		"host may be offline. Returns session records containing the session_id needed for " +
		"subsequent commands."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_init_rtr_session",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in initRTRSessionInput) (*mcp.CallToolResult, any, error) {
		origin := in.Origin
		if origin == "" {
			origin = "falcon-mcp"
		}
		ip := rtr_client.NewRTRInitSessionParamsWithContext(ctx)
		ip.Body = &models.DomainInitRequest{
			DeviceID:     &in.DeviceID,
			Origin:       &origin,
			QueueOffline: &in.QueueOffline,
		}
		ip.Timeout = in.Timeout
		ip.TimeoutDuration = in.TimeoutDuration

		resp, err := api.RTRInitSession(ip)
		if err != nil {
			e := falcon.NormalizeError("RTR_InitSession", "Failed to initialize RTR session", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_pulse_rtr_session (mutation) ---

type pulseRTRSessionInput struct {
	DeviceID     string `json:"device_id" jsonschema:"The host agent ID (AID) whose RTR session timeout should be refreshed."`
	Origin       string `json:"origin,omitempty" jsonschema:"Origin label for the RTR request. Default: falcon-mcp."`
	QueueOffline bool   `json:"queue_offline,omitempty" jsonschema:"Queue the pulse if the host is currently offline."`
}

func registerPulseRTRSession(s *mcp.Server, api RTRAPI) {
	desc := "Refresh an RTR session timeout for a single host. Keeps an existing session " +
		"alive by resetting its inactivity timer. Use this to prevent session expiration " +
		"during long investigations."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_pulse_rtr_session",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in pulseRTRSessionInput) (*mcp.CallToolResult, any, error) {
		origin := in.Origin
		if origin == "" {
			origin = "falcon-mcp"
		}
		pp := rtr_client.NewRTRPulseSessionParamsWithContext(ctx)
		pp.Body = &models.DomainInitRequest{
			DeviceID:     &in.DeviceID,
			Origin:       &origin,
			QueueOffline: &in.QueueOffline,
		}

		resp, err := api.RTRPulseSession(pp)
		if err != nil {
			e := falcon.NormalizeError("RTR_PulseSession", "Failed to pulse RTR session", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_execute_rtr_read_only_command (mutation) ---

type executeRTRReadOnlyCommandInput struct {
	SessionID     string `json:"session_id" jsonschema:"RTR session ID returned from falcon_init_rtr_session or falcon_search_rtr_sessions."`
	BaseCommand   string `json:"base_command" jsonschema:"Read-only RTR base command to execute, such as ls, ps, cat, filehash, or reg. Allowed: cat, cd, clear, env, eventlog, filehash, getsid, help, history, ipconfig, ls, mount, netstat, ps, reg."`
	CommandString string `json:"command_string,omitempty" jsonschema:"Optional full command line to execute. Example: cat C:\\Windows\\win.ini."`
	Persist       bool   `json:"persist,omitempty" jsonschema:"Persist the read-only command in the RTR session history."`
}

func registerExecuteRTRReadOnlyCommand(s *mcp.Server, api RTRAPI) {
	desc := "Execute a read-only RTR command on a single host. Limited to read-only commands " +
		"(cat, cd, clear, env, eventlog, filehash, getsid, help, history, ipconfig, ls, mount, " +
		"netstat, ps, reg) for hunt and triage workflows. Returns command records containing a " +
		"cloud_request_id for polling output via falcon_check_rtr_command_status."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_execute_rtr_read_only_command",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in executeRTRReadOnlyCommandInput) (*mcp.CallToolResult, any, error) {
		if err := validateReadOnlyCommand(in.BaseCommand); err != nil {
			return mcpx.JSONResult(map[string]any{"error": err.Error()})
		}
		return executeCommand(ctx, api, in.SessionID, in.BaseCommand, in.CommandString, in.Persist)
	})
}

// --- falcon_run_rtr_read_only_command_and_wait (mutation) ---

type runRTRReadOnlyCommandAndWaitInput struct {
	SessionID           string  `json:"session_id" jsonschema:"RTR session ID returned from falcon_init_rtr_session or falcon_search_rtr_sessions."`
	BaseCommand         string  `json:"base_command" jsonschema:"Read-only RTR base command to execute, such as ls, ps, cat, filehash, or reg."`
	CommandString       string  `json:"command_string,omitempty" jsonschema:"Optional full command line to execute. Example: cat C:\\Windows\\win.ini."`
	Persist             bool    `json:"persist,omitempty" jsonschema:"Persist the read-only command in the RTR session history."`
	TimeoutSeconds      float64 `json:"timeout_seconds,omitempty" jsonschema:"Maximum time to wait for command completion in seconds [1-600]. Default 60."`
	PollIntervalSeconds float64 `json:"poll_interval_seconds,omitempty" jsonschema:"Seconds to wait between command status checks [0.5-30]. Default 2."`
}

func registerRunRTRReadOnlyCommandAndWait(s *mcp.Server, api RTRAPI, sleep sleepFunc) {
	desc := "Execute a read-only RTR command and poll until completion. Use this for simple, " +
		"focused RTR evidence collection when you want the command output directly without " +
		"manually managing a cloud_request_id. Limited to the same read-only command set as " +
		"falcon_execute_rtr_read_only_command. Polls command status until completion or timeout, " +
		"accumulating output chunks into one result."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_run_rtr_read_only_command_and_wait",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in runRTRReadOnlyCommandAndWaitInput) (*mcp.CallToolResult, any, error) {
		if err := validateReadOnlyCommand(in.BaseCommand); err != nil {
			return mcpx.JSONResult(map[string]any{"error": err.Error(), "phase": "validate"})
		}

		timeoutSecs := in.TimeoutSeconds
		if timeoutSecs <= 0 {
			timeoutSecs = 60
		}
		if timeoutSecs > 600 {
			timeoutSecs = 600
		}
		pollSecs := in.PollIntervalSeconds
		if pollSecs <= 0 {
			pollSecs = 2.0
		}
		if pollSecs > 30 {
			pollSecs = 30
		}

		// Step 1: execute the command.
		execResult, execErr := api.RTRExecuteCommand(buildExecuteParams(ctx, in.SessionID, in.BaseCommand, in.CommandString, in.Persist))
		if execErr != nil {
			e := falcon.NormalizeError("RTR_ExecuteCommand", "Failed to execute RTR read-only command", execErr)
			e2 := map[string]any{"error": e.Error, "status_code": e.StatusCode, "phase": "execute"}
			return mcpx.JSONResult(e2)
		}

		execResources := execResult.GetPayload().Resources
		if len(execResources) == 0 {
			return mcpx.JSONResult(map[string]any{
				"error":   "RTR command execution did not return a command request.",
				"phase":   "execute",
				"results": execResources,
			})
		}

		commandRequest := execResources[0]
		if commandRequest.CloudRequestID == nil {
			return mcpx.JSONResult(map[string]any{
				"error":     "RTR command execution did not return a cloud_request_id.",
				"phase":     "execute",
				"execution": commandRequest,
			})
		}
		cloudRequestID := *commandRequest.CloudRequestID

		// Step 2: poll until complete or timeout.
		deadline := time.Now().Add(time.Duration(timeoutSecs * float64(time.Second)))
		var statusChunks []*models.DomainStatusResponse
		sequenceID := int64(0)

		for {
			sp := rtr_client.NewRTRCheckCommandStatusParamsWithContext(ctx)
			sp.CloudRequestID = cloudRequestID
			sp.SequenceID = sequenceID

			statusResp, statusErr := api.RTRCheckCommandStatus(sp)
			if statusErr != nil {
				e := falcon.NormalizeError("RTR_CheckCommandStatus", "Failed to check RTR command status", statusErr)
				return mcpx.JSONResult(map[string]any{
					"error":            e.Error,
					"status_code":      e.StatusCode,
					"phase":            "status",
					"cloud_request_id": cloudRequestID,
				})
			}

			statusChunks = append(statusChunks, statusResp.GetPayload().Resources...)

			// Check if any chunk is complete.
			complete := false
			for _, chunk := range statusChunks {
				if chunk.Complete != nil && *chunk.Complete {
					complete = true
					break
				}
			}
			if complete {
				return mcpx.JSONResult(formatWaitResult(cloudRequestID, commandRequest, statusChunks, true, false))
			}

			if time.Now().After(deadline) {
				return mcpx.JSONResult(formatWaitResult(cloudRequestID, commandRequest, statusChunks, false, true))
			}

			// Advance sequence ID from last chunk.
			if len(statusChunks) > 0 {
				last := statusChunks[len(statusChunks)-1]
				if last.SequenceID > sequenceID {
					sequenceID = last.SequenceID
				}
			}

			sleep(time.Duration(pollSecs * float64(time.Second)))
		}
	})
}

// --- falcon_check_rtr_command_status ---

type checkRTRCommandStatusInput struct {
	CloudRequestID string `json:"cloud_request_id" jsonschema:"Cloud request ID returned from falcon_execute_rtr_read_only_command."`
	SequenceID     int64  `json:"sequence_id,omitempty" jsonschema:"Sequence chunk to retrieve for command output. Starts at 0."`
}

func registerCheckRTRCommandStatus(s *mcp.Server, api RTRAPI) {
	desc := "Get the status and output for an RTR command execution. Poll this after " +
		"falcon_execute_rtr_read_only_command to retrieve command output. Use sequence_id " +
		"to paginate through large output chunks."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_check_rtr_command_status",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in checkRTRCommandStatusInput) (*mcp.CallToolResult, any, error) {
		sp := rtr_client.NewRTRCheckCommandStatusParamsWithContext(ctx)
		sp.CloudRequestID = in.CloudRequestID
		sp.SequenceID = in.SequenceID

		resp, err := api.RTRCheckCommandStatus(sp)
		if err != nil {
			e := falcon.NormalizeError("RTR_CheckCommandStatus", "Failed to check RTR command status", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_list_rtr_session_files ---

type listRTRSessionFilesInput struct {
	SessionID string `json:"session_id" jsonschema:"RTR session ID to retrieve extracted session files for."`
}

func registerListRTRSessionFiles(s *mcp.Server, api RTRAPI) {
	desc := "List files extracted during an RTR session. Returns file metadata for artifacts " +
		"captured during the session, such as files pulled with the get command."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_list_rtr_session_files",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in listRTRSessionFilesInput) (*mcp.CallToolResult, any, error) {
		lp := rtr_client.NewRTRListFilesV2ParamsWithContext(ctx)
		lp.SessionID = in.SessionID

		resp, err := api.RTRListFilesV2(lp)
		if err != nil {
			e := falcon.NormalizeError("RTR_ListFilesV2", "Failed to list RTR session files", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_rtr_session (destructive) ---

type deleteRTRSessionInput struct {
	SessionID string `json:"session_id" jsonschema:"RTR session ID to close."`
}

func registerDeleteRTRSession(s *mcp.Server, api RTRAPI) {
	desc := "Close an RTR session and release the host connection. Use this when " +
		"investigation is complete to free up session resources."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_rtr_session",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteRTRSessionInput) (*mcp.CallToolResult, any, error) {
		dp := rtr_client.NewRTRDeleteSessionParamsWithContext(ctx)
		dp.SessionID = in.SessionID

		_, err := api.RTRDeleteSession(dp)
		if err != nil {
			e := falcon.NormalizeError("RTR_DeleteSession", "Failed to delete RTR session", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(map[string]any{"deleted": true, "session_id": in.SessionID})
	})
}

// --- helpers ---

// validateReadOnlyCommand returns an error if cmd is not in the read-only allowlist.
func validateReadOnlyCommand(cmd string) error {
	if readOnlyCommands[strings.ToLower(cmd)] {
		return nil
	}
	return fmt.Errorf(
		"command %q is not in the read-only RTR allowlist. Allowed commands: %s",
		cmd, readOnlyCommandList,
	)
}

// buildExecuteParams constructs RTRExecuteCommandParams from individual fields.
func buildExecuteParams(ctx context.Context, sessionID, baseCommand, commandString string, persist bool) *rtr_client.RTRExecuteCommandParams {
	ep := rtr_client.NewRTRExecuteCommandParamsWithContext(ctx)
	id := int32(0)
	deviceID := ""
	ep.Body = &models.DomainCommandExecuteRequest{
		SessionID:     &sessionID,
		BaseCommand:   &baseCommand,
		CommandString: &commandString,
		Persist:       &persist,
		DeviceID:      &deviceID,
		ID:            &id,
	}
	return ep
}

// executeCommand is the shared implementation for the execute-only handler.
func executeCommand(ctx context.Context, api RTRAPI, sessionID, baseCommand, commandString string, persist bool) (*mcp.CallToolResult, any, error) {
	resp, err := api.RTRExecuteCommand(buildExecuteParams(ctx, sessionID, baseCommand, commandString, persist))
	if err != nil {
		e := falcon.NormalizeError("RTR_ExecuteCommand", "Failed to execute RTR read-only command", err)
		return mcpx.JSONResult([]any{e})
	}
	return mcpx.JSONResult(resp.GetPayload().Resources)
}

// formatWaitResult assembles the run_and_wait composite result.
func formatWaitResult(
	cloudRequestID string,
	commandRequest *models.DomainCommandExecuteResponse,
	statusChunks []*models.DomainStatusResponse,
	complete bool,
	timedOut bool,
) map[string]any {
	var stdout strings.Builder
	var stderr strings.Builder
	for _, chunk := range statusChunks {
		if chunk.Stdout != nil && *chunk.Stdout != "" {
			stdout.WriteString(*chunk.Stdout)
		}
		if chunk.Stderr != nil && *chunk.Stderr != "" {
			stderr.WriteString(*chunk.Stderr)
		}
	}

	result := map[string]any{
		"cloud_request_id": cloudRequestID,
		"complete":         complete,
		"timed_out":        timedOut,
		"execution":        commandRequest,
		"status":           statusChunks,
		"stdout":           stdout.String(),
		"stderr":           stderr.String(),
	}
	if timedOut {
		result["warning"] = "Timed out waiting for RTR command completion."
	}
	return result
}

// rtrSearchErr normalizes a search error, surfacing the FQL guide on 400.
func rtrSearchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps limit to [1, max], defaulting to 10 when unset (0).
func normalizeLimit(limit int64, max int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > max {
		return max
	}
	return limit
}
