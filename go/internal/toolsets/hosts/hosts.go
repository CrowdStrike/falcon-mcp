// Package hosts provides tools for searching and inspecting Falcon-managed
// hosts. It is the reference two-step search module: query device IDs honoring
// the requested sort, then hydrate full details by ID and restore that order.
package hosts

import (
	"context"
	_ "embed"
	"encoding/json"

	"github.com/crowdstrike/gofalcon/falcon/client"
	fhosts "github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/google/jsonschema-go/jsonschema"

	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

//go:embed search_fql.md
var searchHostsFQLGuide string

// scopeHostsRead is the API scope both hosts operations require.
var scopeHostsRead = fal.Scope{Name: "Hosts", Read: true}

// defaultSearchLimit matches the Python tool's default of 10 records.
const defaultSearchLimit = 10

func init() { toolsets.Register("hosts", New) }

type searchHostsInput struct {
	Filter string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://hosts/search/fql-guide for syntax."`
	Limit  int64  `json:"limit,omitempty"  jsonschema:"The maximum records to return. [1-5000]"`
	Offset int64  `json:"offset,omitempty" jsonschema:"The offset to start retrieving records from."`
	Sort   string `json:"sort,omitempty"   jsonschema:"Sort by e.g. hostname.asc, last_seen.desc (also accepts hostname|desc)."`
}

// searchHostsInput satisfies toolsets.Constrainer (value receiver) so a drift
// in the interface surfaces as a build error rather than a silent no-op. A
// module using a pointer receiver would assert &fooInput{} instead.
var _ toolsets.Constrainer = searchHostsInput{}

// ApplyConstraints sets the limit bounds and default the Python tool declares
// (default=10, ge=1, le=5000), which jsonschema struct tags cannot express.
func (searchHostsInput) ApplyConstraints(schema *jsonschema.Schema) {
	lim := schema.Properties["limit"]
	if lim == nil {
		return
	}
	minLimit, maxLimit := 1.0, 5000.0
	lim.Minimum = &minLimit
	lim.Maximum = &maxLimit
	lim.Default = json.RawMessage("10")
	lim.Examples = []any{10, 100}
}

type getHostDetailsInput struct {
	IDs []string `json:"ids" jsonschema:"Host device IDs to retrieve details for. Maximum: 5000 IDs per request."`
}

// New builds the hosts toolset from an authenticated Falcon client.
func New(c *client.CrowdStrikeAPISpecification) *toolsets.Toolset {
	h := &handlers{c: c}
	return &toolsets.Toolset{
		Name:        "hosts",
		Description: "Search and inspect Falcon-managed hosts.",
		Tools: []toolsets.Tool{
			toolsets.NewTool("falcon_search_hosts", searchHostsDescription, toolsets.ReadOnly(), h.searchHosts),
			toolsets.NewTool("falcon_get_host_details", getHostDetailsDescription, toolsets.ReadOnly(), h.getHostDetails),
		},
		Resources: []toolsets.Resource{{
			URI:         "falcon://hosts/search/fql-guide",
			Name:        "falcon_search_hosts_fql_guide",
			Description: "Contains the guide for the `filter` param of the `falcon_search_hosts` tool.",
			MIMEType:    "text/markdown",
			Text:        searchHostsFQLGuide,
		}},
	}
}

const searchHostsDescription = "Search for hosts in your CrowdStrike environment.\n\n" +
	"Use this to find devices by hostname, platform, IP, sensor version, or other " +
	"attributes. Consult falcon://hosts/search/fql-guide before constructing filter " +
	"expressions. Returns full host details including device info, OS, and network context."

const getHostDetailsDescription = "Retrieve detailed information for one or more host device IDs.\n\n" +
	"Use when you already have specific device IDs from search results, the Falcon " +
	"console, or the Streaming API. For discovering hosts by criteria, use " +
	"falcon_search_hosts instead. Returns comprehensive host details."

type handlers struct {
	c *client.CrowdStrikeAPISpecification
}

// searchHosts queries device IDs by filter, then hydrates full details and
// restores the query-step sort order on the result.
func (h *handlers) searchHosts(ctx context.Context, in searchHostsInput) (any, error) {
	limit := in.Limit
	if limit == 0 {
		limit = defaultSearchLimit
	}

	q, err := h.c.Hosts.QueryDevicesByFilter(&fhosts.QueryDevicesByFilterParams{
		Context: ctx,
		Filter:  fal.Opt(in.Filter),
		Limit:   &limit,
		Offset:  fal.Opt(in.Offset),
		Sort:    fal.Opt(in.Sort),
	})
	if e := fal.APIError(err, q, scopeHostsRead); e != nil {
		return []any{e}, nil // parity: hosts wraps the search error in a list
	}

	ids := q.Payload.Resources
	if len(ids) == 0 {
		return []any{}, nil // parity: bare empty list
	}

	details, e := h.fetchDetails(ctx, ids)
	if e != nil {
		return []any{e}, nil
	}
	// Restore the query-step sort order in case the details endpoint returns
	// entities in a different order.
	return fal.ReorderByIDs(ids, details, deviceID), nil
}

// getHostDetails hydrates details for explicit device IDs. An empty ids list
// short-circuits with a bare empty list and makes no API call.
func (h *handlers) getHostDetails(ctx context.Context, in getHostDetailsInput) (any, error) {
	if len(in.IDs) == 0 {
		return []any{}, nil
	}
	details, e := h.fetchDetails(ctx, in.IDs)
	if e != nil {
		return e, nil // parity: get_host_details returns the bare error dict
	}
	return details, nil
}

// fetchDetails calls the details endpoint for the given IDs, returning the
// device entities or a normalized error.
func (h *handlers) fetchDetails(ctx context.Context, ids []string) ([]*models.DeviceapiDeviceSwagger, *fal.Error) {
	d, err := h.c.Hosts.PostDeviceDetailsV2(&fhosts.PostDeviceDetailsV2Params{
		Context: ctx,
		Body:    &models.MsaIdsRequest{Ids: ids},
	})
	if e := fal.APIError(err, d, scopeHostsRead); e != nil {
		return nil, e
	}
	return d.Payload.Resources, nil
}

// deviceID extracts the device_id from a host entity for order restoration.
func deviceID(d *models.DeviceapiDeviceSwagger) string {
	if d == nil || d.DeviceID == nil {
		return ""
	}
	return *d.DeviceID
}
