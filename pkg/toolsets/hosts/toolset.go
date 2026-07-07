// Package hosts implements the Falcon MCP "hosts" toolset: search and detail
// retrieval for hosts/devices. It is the canonical two-step search example —
// QueryDevicesByFilter (IDs) then PostDeviceDetailsV2 (full details) — that the
// other Tier-1 toolsets follow.
package hosts

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://hosts/search/fql-guide"
)

// HostsAPI is the narrow slice of the gofalcon hosts client this toolset uses.
// Declaring it here (rather than depending on the full ClientService) keeps the
// handlers unit-testable with a hand-written mock.
type HostsAPI interface {
	QueryDevicesByFilter(*hosts.QueryDevicesByFilterParams, ...hosts.ClientOption) (*hosts.QueryDevicesByFilterOK, error)
	PostDeviceDetailsV2(*hosts.PostDeviceDetailsV2Params, ...hosts.ClientOption) (*hosts.PostDeviceDetailsV2OK, error)
}

// Toolset is the hosts domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "hosts" }

func (Toolset) GetDescription() string {
	return "Access and manage CrowdStrike Falcon hosts/devices."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_hosts_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_hosts` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_hosts"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchHosts(s, fc.Hosts())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_host_details"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetHostDetails(s, fc.Hosts())
			},
		},
	}
}

// --- falcon_search_hosts ---

// SearchHostsInput mirrors the Python search_hosts signature. Optional fields
// use pointers so the inferred JSON Schema marks them optional; numeric bounds
// are documented in the description and enforced post-parse (the jsonschema tag
// carries no ge/le).
type SearchHostsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://hosts/search/fql-guide for syntax. Examples: platform_name:'Windows', hostname:'PC*'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum records to return [1-5000]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"The offset to start retrieving records from."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression, e.g. hostname.asc, last_seen.desc. Fields: hostname, last_seen, first_seen, modified_timestamp, platform_name, agent_version, os_version, external_ip."`
}

func registerSearchHosts(s *mcp.Server, api HostsAPI) {
	desc := "Search for hosts in your CrowdStrike environment. Use this to find devices by " +
		"hostname, platform, IP, sensor version, or other attributes. Consult " +
		"falcon://hosts/search/fql-guide before constructing filter expressions. Returns full " +
		"host details including device info, OS, and network context."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_hosts",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchHostsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching device IDs.
		qp := hosts.NewQueryDevicesByFilterParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.QueryDevicesByFilter(qp)
		if err != nil {
			return searchErr(ctx, "QueryDevicesByFilter", "Failed to search hosts", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full details for the matched IDs.
		details, err := fetchDetails(ctx, api, ids)
		if err != nil {
			return searchErr(ctx, "PostDeviceDetailsV2", "Failed to get host details", in.Filter, err)
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_get_host_details ---

// GetHostDetailsInput takes explicit device IDs.
type GetHostDetailsInput struct {
	IDs []string `json:"ids" jsonschema:"Host device IDs to retrieve details for (from search_hosts, the Falcon console, or the Streaming API). Maximum 5000 IDs per request."`
}

func registerGetHostDetails(s *mcp.Server, api HostsAPI) {
	desc := "Retrieve detailed information for one or more host device IDs. Use when you already " +
		"have specific device IDs from search results, the Falcon console, or the Streaming API. " +
		"For discovering hosts by criteria, use falcon_search_hosts instead."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_host_details",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in GetHostDetailsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{})
		}
		details, err := fetchDetails(ctx, api, in.IDs)
		if err != nil {
			resp := falcon.NormalizeError("PostDeviceDetailsV2", "Failed to get host details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- helpers ---

// fetchDetails calls PostDeviceDetailsV2 for the given IDs and returns the
// device resource list.
func fetchDetails(ctx context.Context, api HostsAPI, ids []string) ([]*models.DeviceapiDeviceSwagger, error) {
	dp := hosts.NewPostDeviceDetailsV2ParamsWithContext(ctx)
	dp.Body = &models.MsaIdsRequest{Ids: ids}
	resp, err := api.PostDeviceDetailsV2(dp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise. It always returns a
// successful tool result wrapping the error object (parity with the Python
// modules, which return error dicts rather than protocol errors).
func searchErr(_ context.Context, operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to the documented [1,5000] range,
// defaulting to 10 when unset (0).
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 5000 {
		return 5000
	}
	return limit
}
