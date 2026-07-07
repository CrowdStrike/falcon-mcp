// Package sensor_usage implements the Falcon MCP "sensor_usage" toolset:
// weekly sensor usage retrieval. It is a single-step call — GetSensorUsageWeekly
// returns full usage records directly with no separate details fetch.
package sensor_usage

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/sensor_usage_api"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://sensor-usage/weekly/fql-guide"
)

// SensorUsageAPI is the narrow slice of the gofalcon sensor_usage_api client
// this toolset uses. Declaring it here keeps the handler unit-testable with a
// hand-written mock.
type SensorUsageAPI interface {
	GetSensorUsageWeekly(*sensor_usage_api.GetSensorUsageWeeklyParams, ...sensor_usage_api.ClientOption) (*sensor_usage_api.GetSensorUsageWeeklyOK, error)
}

// Toolset is the sensor_usage domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "sensor_usage" }

func (Toolset) GetDescription() string {
	return "Access CrowdStrike Falcon sensor usage billing and metrics data."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_sensor_usage_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_sensor_usage` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_sensor_usage"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchSensorUsage(s, fc.SensorUsage())
			},
		},
	}
}

// --- falcon_search_sensor_usage ---

// SearchSensorUsageInput mirrors the Python search_sensor_usage signature.
// Filter is the only parameter; it is optional.
type SearchSensorUsageInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://sensor-usage/weekly/fql-guide for syntax. Examples: event_date:'2024-06-11', period:'30'."`
}

func registerSearchSensorUsage(s *mcp.Server, api SensorUsageAPI) {
	desc := "Search for weekly sensor usage data in your CrowdStrike environment. " +
		"Use this to retrieve sensor billing and usage metrics by date or period. Consult " +
		"falcon://sensor-usage/weekly/fql-guide before constructing filter expressions. " +
		"Returns weekly usage records."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_sensor_usage",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchSensorUsageInput) (*mcp.CallToolResult, any, error) {
		p := sensor_usage_api.NewGetSensorUsageWeeklyParamsWithContext(ctx)
		p.Filter = in.Filter

		resp, err := api.GetSensorUsageWeekly(p)
		if err != nil {
			return searchErr(ctx, in.Filter, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise.
func searchErr(_ context.Context, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError("GetSensorUsageWeekly", "Failed to search sensor usage", err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}
