// Package ngsiem implements the Falcon MCP "ngsiem" toolset: executing CQL
// queries against CrowdStrike Next-Gen SIEM via the asynchronous job-based
// search API (StartSearchV1 → poll GetSearchStatusV1 until done → events).
package ngsiem

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/crowdstrike/gofalcon/falcon/client/ngsiem"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	defaultPollInterval = 5 * time.Second
	defaultTimeout      = 300 * time.Second
)

// ngsiemAPI is the narrow slice of the ngsiem client used by this toolset.
// Declaring it here keeps the handler unit-testable with a hand-written mock.
type ngsiemAPI interface {
	StartSearchV1(*ngsiem.StartSearchV1Params, ...ngsiem.ClientOption) (*ngsiem.StartSearchV1OK, error)
	GetSearchStatusV1(*ngsiem.GetSearchStatusV1Params, ...ngsiem.ClientOption) (*ngsiem.GetSearchStatusV1OK, error)
	StopSearchV1(*ngsiem.StopSearchV1Params, ...ngsiem.ClientOption) (*ngsiem.StopSearchV1OK, error)
}

// Toolset is the ngsiem domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "ngsiem" }

func (Toolset) GetDescription() string {
	return "Execute CQL search queries against CrowdStrike Next-Gen SIEM."
}

// GetResources returns nil — the ngsiem toolset has no FQL guide resource.
func (Toolset) GetResources() []api.ServerResource { return nil }

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_ngsiem"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchNgsiem(s, fc.Ngsiem(), time.Sleep)
			},
		},
	}
}

// --- falcon_search_ngsiem ---

type searchNgsiemInput struct {
	QueryString string  `json:"query_string" jsonschema:"The CQL query string to execute. This tool executes pre-written CQL queries — it does NOT help construct queries. Users must provide a complete, valid CQL query. Example: '#event_simpleName=ProcessRollup2' or 'source=firewall | count()'"`
	Start       string  `json:"start" jsonschema:"Search start time as an ISO 8601 timestamp (REQUIRED). Example: '2025-01-01T00:00:00Z'"`
	Repository  string  `json:"repository,omitempty" jsonschema:"Repository to search. Options: search-all (default), investigate_view, third-party, falcon_for_it_view, forensics_view."`
	End         *string `json:"end,omitempty" jsonschema:"Search end time as an ISO 8601 timestamp. If not provided, defaults to the current time. Example: '2025-02-06T00:00:00Z'"`
}

func registerSearchNgsiem(s *mcp.Server, api ngsiemAPI, sleepFn func(time.Duration)) {
	pollInterval := envDuration("FALCON_MCP_NGSIEM_POLL_INTERVAL", defaultPollInterval)
	timeout := envDuration("FALCON_MCP_NGSIEM_TIMEOUT", defaultTimeout)

	desc := "Execute a CQL query against CrowdStrike Next-Gen SIEM. Use this to search security " +
		"events, logs, and telemetry. Callers must supply a complete, valid CQL query — this tool " +
		"does not assist with query construction. Returns matching event records, or an error dict " +
		"if the job fails or times out."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_ngsiem",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchNgsiemInput) (*mcp.CallToolResult, any, error) {
		return runSearch(ctx, api, sleepFn, pollInterval, timeout, in)
	})
}

func runSearch(
	ctx context.Context,
	api ngsiemAPI,
	sleepFn func(time.Duration),
	pollInterval, timeout time.Duration,
	in searchNgsiemInput,
) (*mcp.CallToolResult, any, error) {
	repository := in.Repository
	if repository == "" {
		repository = "search-all"
	}

	// Build body — start/end are ISO 8601 strings; the API accepts them as strings.
	queryString := in.QueryString
	body := &models.APIQueryJobInput{
		QueryString: &queryString,
		Start:       in.Start,
	}
	if in.End != nil {
		body.End = *in.End
	}

	// Step 1: start the search job.
	sp := ngsiem.NewStartSearchV1ParamsWithContext(ctx)
	sp.Repository = repository
	sp.Body = body

	startResp, err := api.StartSearchV1(sp)
	if err != nil {
		e := falcon.NormalizeError("StartSearchV1", "Failed to start NGSIEM search", err)
		return mcpx.JSONResult([]any{e})
	}

	jobID := ""
	if startResp.GetPayload() != nil && startResp.GetPayload().ID != nil {
		jobID = *startResp.GetPayload().ID
	}
	if jobID == "" {
		e := falcon.ErrorResponse{Error: "Failed to start NGSIEM search: no job ID returned"}
		return mcpx.JSONResult([]any{e})
	}

	// Step 2: poll until done or timeout.
	deadline := time.Now().Add(timeout)
	for {
		sleepFn(pollInterval)

		if time.Now().After(deadline) {
			break
		}

		pp := ngsiem.NewGetSearchStatusV1ParamsWithContext(ctx)
		pp.Repository = repository
		pp.ID = jobID

		pollResp, err := api.GetSearchStatusV1(pp)
		if err != nil {
			e := falcon.NormalizeError("GetSearchStatusV1", "Failed to poll NGSIEM search status", err)
			return mcpx.JSONResult([]any{e})
		}

		payload := pollResp.GetPayload()
		if payload != nil && payload.Done != nil && *payload.Done {
			return mcpx.JSONResult(payload.Events)
		}
	}

	// Step 3: timeout — attempt cleanup.
	stopP := ngsiem.NewStopSearchV1ParamsWithContext(ctx)
	stopP.Repository = repository
	stopP.ID = jobID
	_, _ = api.StopSearchV1(stopP) //nolint:errcheck // best-effort cleanup

	timeoutSecs := int(timeout.Seconds())
	e := falcon.ErrorResponse{
		Error: fmt.Sprintf(
			"Failed to poll NGSIEM search status: NGSIEM search timed out after %d seconds. "+
				"Try narrowing your query or reducing the time range.",
			timeoutSecs,
		),
	}
	return mcpx.JSONResult([]any{e})
}

// envDuration reads a duration in whole seconds from an env variable,
// returning the default when the variable is absent or unparseable.
func envDuration(key string, def time.Duration) time.Duration {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.Atoi(v)
	if err != nil || n <= 0 {
		return def
	}
	return time.Duration(n) * time.Second
}
