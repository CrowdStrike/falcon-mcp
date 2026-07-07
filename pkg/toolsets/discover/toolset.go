// Package discover implements the Falcon MCP "discover" toolset: search for
// applications and unmanaged assets found by Falcon Discover. Unlike the
// hosts toolset, both operations here are single-step combined searches —
// the API returns full resources directly, with no separate details call.
package discover

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/discover"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	applicationsFQLGuideURI = "falcon://discover/applications/fql-guide"
	hostsFQLGuideURI        = "falcon://discover/hosts/fql-guide"

	// unmanagedFilter is unconditionally ANDed onto every falcon_search_unmanaged_assets
	// query, matching the Python module's base_filter behavior.
	unmanagedFilter = "entity_type:'unmanaged'"
)

// DiscoverAPI is the narrow slice of the gofalcon discover client this
// toolset uses. Declaring it here (rather than depending on the full
// ClientService) keeps the handlers unit-testable with a hand-written mock.
type DiscoverAPI interface {
	CombinedApplications(*discover.CombinedApplicationsParams, ...discover.ClientOption) (*discover.CombinedApplicationsOK, error)
	CombinedHosts(*discover.CombinedHostsParams, ...discover.ClientOption) (*discover.CombinedHostsOK, error)
}

// Toolset is the discover domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "discover" }

func (Toolset) GetDescription() string {
	return "Access and manage CrowdStrike Falcon Discover applications and unmanaged assets."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			applicationsFQLGuideURI,
			"falcon_search_applications_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_applications` tool.",
		),
		fql.Resource(
			hostsFQLGuideURI,
			"falcon_search_unmanaged_assets_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_applications"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchApplications(s, fc.Discover())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_unmanaged_assets"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchUnmanagedAssets(s, fc.Discover())
			},
		},
	}
}

// --- falcon_search_applications ---

// SearchApplicationsInput mirrors the Python search_applications signature.
// Filter is required (no default in Python); the rest are optional and use
// pointers so the inferred JSON Schema marks them optional.
type SearchApplicationsInput struct {
	Filter string  `json:"filter" jsonschema:"FQL filter expression (required). See falcon://discover/applications/fql-guide for syntax. Examples: name:'Chrome', vendor:'Microsoft Corporation'."`
	Facet  *string `json:"facet,omitempty" jsonschema:"Type of data to be returned for each application entity. The facet filter allows you to limit the response to just the information you want. Possible values: browser_extension, host_info, install_usage. Note: Requests that do not include the host_info or browser_extension facets still return host.ID, browser_extension.ID, and browser_extension.enabled in the response."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of items to return: 1-1000. Default is 100."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Property used to sort the results. All properties can be used to sort unless otherwise noted in their property descriptions. Examples: name.asc, vendor.desc, last_updated_timestamp.desc."`
}

func registerSearchApplications(s *mcp.Server, api DiscoverAPI) {
	desc := "Search for applications discovered in your CrowdStrike environment. Use this to find " +
		"applications by name, vendor, or installation details. Consult " +
		"falcon://discover/applications/fql-guide before constructing filter expressions. Returns " +
		"application entities with optional host info and usage data (based on facet)."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_applications",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchApplicationsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 1000)
		filter := in.Filter

		qp := discover.NewCombinedApplicationsParamsWithContext(ctx)
		qp.Filter = filter
		qp.Limit = &limit
		qp.Sort = in.Sort
		if in.Facet != nil {
			qp.Facet = []string{*in.Facet}
		}

		resp, err := api.CombinedApplications(qp)
		if err != nil {
			return searchErr(ctx, "combined_applications", "Failed to search applications", &filter, applicationsFQLGuideURI, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(&filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_search_unmanaged_assets ---

// SearchUnmanagedAssetsInput mirrors the Python search_unmanaged_assets
// signature. Filter is optional — the tool always ANDs entity_type:'unmanaged'
// onto whatever the caller supplies (or uses it alone).
// Note: the API uses cursor-based pagination via an after token, not a numeric
// offset, so we expose After for continuation requests.
type SearchUnmanagedAssetsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://discover/hosts/fql-guide for syntax. Note: entity_type:'unmanaged' is automatically applied. Examples: platform_name:'Windows', criticality:'Critical'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of items to return: 1-5000. Default is 100."`
	After  *string `json:"after,omitempty" jsonschema:"A pagination token from a previous response to continue from that place in the results."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort unmanaged assets using these options: hostname, last_seen_timestamp, first_seen_timestamp, platform_name, os_version, external_ip, country, criticality. Sort either asc (ascending) or desc (descending). Both formats are supported: 'hostname.desc' or 'hostname|desc'. Examples: hostname.asc, last_seen_timestamp.desc, criticality.desc."`
}

func registerSearchUnmanagedAssets(s *mcp.Server, api DiscoverAPI) {
	desc := "Search for unmanaged assets (hosts without Falcon sensor) in your environment. Finds " +
		"systems discovered by Falcon-managed hosts that lack a sensor themselves. Consult " +
		"falcon://discover/hosts/fql-guide before constructing filter expressions. The tool " +
		"automatically adds entity_type:'unmanaged' to all queries. Returns full asset details " +
		"including platform, network, and criticality information."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_unmanaged_assets",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchUnmanagedAssetsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 5000)
		combined := composeUnmanagedFilter(in.Filter)

		qp := discover.NewCombinedHostsParamsWithContext(ctx)
		qp.Filter = combined
		qp.Limit = &limit
		qp.After = in.After
		qp.Sort = in.Sort

		resp, err := api.CombinedHosts(qp)
		if err != nil {
			return searchErr(ctx, "combined_hosts", "Failed to search unmanaged assets", &combined, hostsFQLGuideURI, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(&combined))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- helpers ---

// composeUnmanagedFilter ANDs the always-on entity_type:'unmanaged' filter
// with the caller-supplied filter (if any), mirroring the Python module's
// base_filter + "+" + filter composition.
func composeUnmanagedFilter(filter *string) string {
	if filter == nil || *filter == "" {
		return unmanagedFilter
	}
	return unmanagedFilter + "+" + *filter
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise. It always returns a
// successful tool result wrapping the error object (parity with the Python
// modules, which return error dicts rather than protocol errors).
func searchErr(_ context.Context, operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to [1,max], defaulting to
// def when unset (0).
func normalizeLimit(limit int64, def, max int64) int64 {
	if limit <= 0 {
		return def
	}
	if limit > max {
		return max
	}
	return limit
}
