// Package hosts implements the falcon_search_hosts and falcon_get_host_details
// tools over the gofalcon hosts client, and registers the hosts FQL guide
// resource.
package hosts

import (
	"context"
	"log/slog"

	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
	"github.com/crowdstrike/falcon-mcp/internal/modules/registry"
)

const filterParamDescription = "FQL filter expression. See `falcon://hosts/search/fql-guide` for syntax."

// Factory builds the hosts module from shared deps. The generated aggregator
// (internal/mcpserver) collects it, so the module needs no init side effect.
var Factory registry.Factory = func(d registry.Deps) base.Module {
	return &Module{API: d.API.Hosts, Concurrency: d.Concurrency, Logger: d.Logger}
}

// deviceBatchSize is the maximum number of device IDs fetched per details call.
const deviceBatchSize = 5000

// fqlGuideURI is the MCP resource URI serving the hosts FQL filter guide.
const fqlGuideURI = "falcon://hosts/search/fql-guide"

// hostsAPI is the minimal slice of the gofalcon hosts client this module
// consumes, declared next to its consumer for testability.
type hostsAPI interface {
	QueryDevicesByFilter(params *hosts.QueryDevicesByFilterParams, opts ...hosts.ClientOption) (*hosts.QueryDevicesByFilterOK, error)
	PostDeviceDetailsV2(params *hosts.PostDeviceDetailsV2Params, opts ...hosts.ClientOption) (*hosts.PostDeviceDetailsV2OK, error)
}

// scopeHostsRead is the CrowdStrike API scope required by this module's hosts
// operations. Surfaced on a 403 via base.APIError.
var scopeHostsRead = base.Scope{Name: "Hosts", Read: true}

// Module registers the hosts tools. It holds only the shared Falcon client and
// configuration; handlers are stateless and reentrant. Logger must be non-nil.
type Module struct {
	API         hostsAPI
	Concurrency int // bounds concurrent detail fetches
	Logger      *slog.Logger
}

// Name reports the module name.
func (m *Module) Name() string { return "hosts" }

// Description reports a one-line summary of the module.
func (m *Module) Description() string {
	return "Search Falcon hosts/devices and retrieve their full details"
}

// searchHostsDescription is the falcon_search_hosts tool description, kept 1:1
// with the Python falcon-mcp hosts module.
const searchHostsDescription = `Search for hosts in your CrowdStrike environment.

Use this to find devices by hostname, platform, IP, sensor version, or other
attributes. Consult falcon://hosts/search/fql-guide before constructing filter
expressions. Returns full host details including device info, OS, and network
context.`

// getHostDetailsDescription is the falcon_get_host_details tool description,
// kept 1:1 with the Python falcon-mcp hosts module.
const getHostDetailsDescription = `Retrieve detailed information for one or more host device IDs.

Use when you already have specific device IDs from search results, the Falcon
console, or the Streaming API. For discovering hosts by criteria, use
falcon_search_hosts instead. Returns comprehensive host details.`

// RegisterTools registers the hosts tools into r.
func (m *Module) RegisterTools(r base.Registrar) {
	base.AddTool(r, &mcp.Tool{
		Name:        "search_hosts",
		Description: searchHostsDescription,
	}, m.searchHosts)

	base.AddTool(r, &mcp.Tool{
		Name:        "get_host_details",
		Description: getHostDetailsDescription,
	}, m.getHostDetails)
}

// RegisterResources publishes the hosts FQL guide as an MCP resource,
// mirroring falcon-mcp's falcon://hosts/search/fql-guide resource.
func (m *Module) RegisterResources(s *mcp.Server) {
	base.TextResource(s,
		fqlGuideURI,
		"search_hosts_fql_guide",
		"Contains the guide for the `filter` param of the `falcon_search_hosts` tool.",
		"text/markdown",
		fqlGuide,
	)
}

// SearchInput is the input for falcon_search_hosts.
type SearchInput struct {
	Filter string `json:"filter,omitempty" jsonschema:"FQL filter (e.g. platform_name:'Windows', hostname:'PC*')"`
	Limit  int    `json:"limit,omitempty" jsonschema:"maximum results to return (1-5000, default 10)"`
	Offset int    `json:"offset,omitempty" jsonschema:"pagination offset"`
	Sort   string `json:"sort,omitempty" jsonschema:"FQL sort (e.g. hostname.asc, last_seen.desc)"`
}

func (m *Module) searchHosts(ctx context.Context, _ *mcp.CallToolRequest, in SearchInput) (*mcp.CallToolResult, base.SearchResult[*models.DeviceapiDeviceSwagger], error) {
	var zero base.SearchResult[*models.DeviceapiDeviceSwagger]
	limit := int64(in.Limit)
	if limit == 0 {
		limit = 10
	}
	m.Logger.Debug("search_hosts", "filter", in.Filter, "limit", limit, "offset", in.Offset, "sort", in.Sort)
	params := hosts.NewQueryDevicesByFilterParamsWithContext(ctx)
	params.Limit = &limit
	if in.Filter != "" {
		params.Filter = &in.Filter
	}
	if in.Offset != 0 {
		offset := int64(in.Offset)
		params.Offset = &offset
	}
	if in.Sort != "" {
		params.Sort = &in.Sort
	}

	queryResp, err := m.API.QueryDevicesByFilter(params)
	if e := base.APIError(err, queryResp, scopeHostsRead); e != nil {
		return nil, zero, e
	}

	ids := queryResp.Payload.Resources
	m.Logger.Debug("search_hosts query complete", "matched_ids", len(ids))
	if len(ids) == 0 {
		return nil, base.Found([]*models.DeviceapiDeviceSwagger{}, in.Filter), nil
	}
	devices, err := m.fetchDetails(ctx, ids)
	if err != nil {
		return nil, zero, err
	}
	return nil, base.Found(devices, in.Filter), nil
}

// DetailsInput is the input for falcon_get_host_details.
type DetailsInput struct {
	IDs []string `json:"ids" jsonschema:"device IDs to retrieve (max 5000)"`
}

func (m *Module) getHostDetails(ctx context.Context, _ *mcp.CallToolRequest, in DetailsInput) (*mcp.CallToolResult, base.EntitiesResult[*models.DeviceapiDeviceSwagger], error) {
	m.Logger.Debug("get_host_details", "ids", len(in.IDs))
	if len(in.IDs) == 0 {
		return nil, base.Entities([]*models.DeviceapiDeviceSwagger{}), nil
	}
	devices, err := m.fetchDetails(ctx, in.IDs)
	if err != nil {
		return nil, base.EntitiesResult[*models.DeviceapiDeviceSwagger]{}, err
	}
	return nil, base.Entities(devices), nil
}

// fetchDetails fetches full device records for the given IDs, chunking and fetching
// concurrently when the set exceeds a single details call's capacity.
func (m *Module) fetchDetails(ctx context.Context, ids []string) ([]*models.DeviceapiDeviceSwagger, error) {
	return base.FetchDetails(ctx, base.FetchDetailsParams[*models.DeviceapiDeviceSwagger]{
		IDs:         ids,
		ChunkSize:   deviceBatchSize,
		Concurrency: m.Concurrency,
		Fetch: func(ctx context.Context, chunk []string) ([]*models.DeviceapiDeviceSwagger, error) {
			params := hosts.NewPostDeviceDetailsV2ParamsWithContext(ctx)
			params.Body = &models.MsaIdsRequest{Ids: chunk}
			resp, err := m.API.PostDeviceDetailsV2(params)
			if e := base.APIError(err, resp, scopeHostsRead); e != nil {
				return nil, e
			}
			return resp.Payload.Resources, nil
		},
		// PostDeviceDetailsV2 may reorder devices; reorder to the query step's
		// sort. Field verified against the live API: device_id.
		KeyFn: func(d *models.DeviceapiDeviceSwagger) string {
			if d == nil || d.DeviceID == nil {
				return ""
			}
			return *d.DeviceID
		},
	})
}
