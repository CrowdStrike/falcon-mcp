// Package detections implements the falcon_search_detections,
// falcon_get_detection_details, and falcon_update_detections tools over the
// gofalcon alerts client. It covers EPP, IDP, XDR, OverWatch, and NG-SIEM
// alerts.
package detections

import (
	"context"
	"errors"
	"log/slog"

	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
	"github.com/crowdstrike/falcon-mcp/internal/modules/registry"
)

// Factory builds the detections module from shared deps. The generated
// aggregator (internal/mcpserver) collects it, so the module needs no init
// side effect.
var Factory registry.Factory = func(d registry.Deps) base.Module {
	return &Module{API: d.API.Alerts, Concurrency: d.Concurrency, Logger: d.Logger}
}

// errInvalidInput classifies client-side validation failures in update_detections.
var errInvalidInput = errors.New("detections: invalid input")

// alertBatchSize is the maximum number of composite IDs fetched per GetV2 call.
const alertBatchSize = 1000

// alertsAPI is the minimal slice of the gofalcon alerts client this module
// consumes, declared next to its consumer so handlers can be tested against a
// tiny fake rather than all of gofalcon.
type alertsAPI interface {
	QueryV2(params *alerts.QueryV2Params, opts ...alerts.ClientOption) (*alerts.QueryV2OK, error)
	GetV2(params *alerts.GetV2Params, opts ...alerts.ClientOption) (*alerts.GetV2OK, error)
	UpdateV3(params *alerts.UpdateV3Params, opts ...alerts.ClientOption) (*alerts.UpdateV3OK, error)
}

// CrowdStrike API scopes required by this module's alerts operations. Surfaced
// on a 403 via base.APIError, referenced directly at each call site.
var (
	scopeAlertsRead  = base.Scope{Name: "Alerts", Read: true}
	scopeAlertsWrite = base.Scope{Name: "Alerts", Write: true}
)

// Module registers the detections tools. It holds only the shared, concurrency-
// safe Falcon client and configuration; handlers are stateless and reentrant.
// Logger must be non-nil.
type Module struct {
	API         alertsAPI
	Concurrency int // bounds detail-fetch fan-out
	Logger      *slog.Logger
}

// Name reports the module name.
func (m *Module) Name() string { return "detections" }

// Description reports a one-line summary of the module.
func (m *Module) Description() string {
	return "Search, retrieve, and triage Falcon detections/alerts (EPP, IDP, XDR, OverWatch, NG-SIEM)"
}

// RegisterTools registers the three detection tools into r.
func (m *Module) RegisterTools(r base.Registrar) {
	base.AddTool(r, &mcp.Tool{
		Name:        "search_detections",
		Description: "Search for detections/alerts in CrowdStrike Falcon using FQL. Returns full alert records. Covers EPP, IDP, XDR, OverWatch, and NG-SIEM alerts.",
	}, m.searchDetections)

	base.AddTool(r, &mcp.Tool{
		Name:        "get_detection_details",
		Description: "Retrieve full details for the given detection/alert composite IDs.",
	}, m.getDetectionDetails)

	base.AddTool(r, &mcp.Tool{
		Name:        "update_detections",
		Description: "Update one or more detections/alerts: status, assignment, comments, tags, or UI visibility.",
		Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, IdempotentHint: false},
	}, m.updateDetections)
}

// RegisterResources publishes the detections FQL guide as an MCP resource,
// mirroring falcon-mcp's falcon://detections/search/fql-guide resource.
func (m *Module) RegisterResources(s *mcp.Server) {
	base.TextResource(s,
		fqlGuideURI,
		"search_detections_fql_guide",
		"Contains the guide for the `filter` param of the `falcon_search_detections` tool.",
		"text/markdown",
		fqlGuide,
	)
}

// SearchInput is the input for falcon_search_detections.
type SearchInput struct {
	Filter        string `json:"filter,omitempty" jsonschema:"FQL filter (e.g. severity.desc, status:'new')"`
	Limit         int    `json:"limit,omitempty" jsonschema:"maximum results to return (1-9999, default 10)"`
	Offset        int    `json:"offset,omitempty" jsonschema:"pagination offset"`
	Q             string `json:"q,omitempty" jsonschema:"free-text metadata search"`
	Sort          string `json:"sort,omitempty" jsonschema:"FQL sort (e.g. timestamp.desc)"`
	IncludeHidden *bool  `json:"include_hidden,omitempty" jsonschema:"include hidden alerts (default true)"`
}

func (m *Module) searchDetections(ctx context.Context, _ *mcp.CallToolRequest, in SearchInput) (*mcp.CallToolResult, base.SearchResult[*models.DetectsAlert], error) {
	var zero base.SearchResult[*models.DetectsAlert]
	limit := int64(in.Limit)
	if limit == 0 {
		limit = 10
	}
	m.Logger.Debug("search_detections", "filter", in.Filter, "limit", limit, "offset", in.Offset, "q", in.Q, "sort", in.Sort)
	params := alerts.NewQueryV2ParamsWithContext(ctx)
	params.Limit = &limit
	if in.Filter != "" {
		params.Filter = &in.Filter
	}
	if in.Offset != 0 {
		offset := int64(in.Offset)
		params.Offset = &offset
	}
	if in.Q != "" {
		params.Q = &in.Q
	}
	if in.Sort != "" {
		params.Sort = &in.Sort
	}

	queryResp, err := m.API.QueryV2(params)
	if err != nil {
		if details, ok := fqlBadRequest(err); ok {
			return nil, base.FQLError[*models.DetectsAlert](details, in.Filter, fqlGuide), nil
		}
	}
	if e := base.APIError(err, queryResp, scopeAlertsRead); e != nil {
		return nil, zero, e
	}

	ids := queryResp.Payload.Resources
	m.Logger.Debug("search_detections query complete", "matched_ids", len(ids))
	if len(ids) == 0 {
		return nil, base.Found([]*models.DetectsAlert{}, in.Filter), nil
	}

	alertsResult, err := m.fetchDetails(ctx, ids, in.IncludeHidden)
	if err != nil {
		return nil, zero, err
	}
	return nil, base.Found(alertsResult, in.Filter), nil
}

// DetailsInput is the input for falcon_get_detection_details.
type DetailsInput struct {
	IDs           []string `json:"ids" jsonschema:"composite IDs of the detections to retrieve"`
	IncludeHidden *bool    `json:"include_hidden,omitempty" jsonschema:"include hidden alerts (default true)"`
}

func (m *Module) getDetectionDetails(ctx context.Context, _ *mcp.CallToolRequest, in DetailsInput) (*mcp.CallToolResult, base.EntitiesResult[*models.DetectsAlert], error) {
	m.Logger.Debug("get_detection_details", "ids", len(in.IDs))
	if len(in.IDs) == 0 {
		return nil, base.Entities([]*models.DetectsAlert{}), nil
	}
	alertsResult, err := m.fetchDetails(ctx, in.IDs, in.IncludeHidden)
	if err != nil {
		return nil, base.EntitiesResult[*models.DetectsAlert]{}, err
	}
	return nil, base.Entities(alertsResult), nil
}

// fetchDetails fetches full alert records for the given composite IDs, chunking and
// fetching concurrently when the set exceeds a single GetV2 call's capacity.
func (m *Module) fetchDetails(ctx context.Context, ids []string, includeHidden *bool) ([]*models.DetectsAlert, error) {
	return base.FetchDetails(ctx, base.FetchDetailsParams[*models.DetectsAlert]{
		IDs:         ids,
		ChunkSize:   alertBatchSize,
		Concurrency: m.Concurrency,
		Fetch: func(ctx context.Context, chunk []string) ([]*models.DetectsAlert, error) {
			params := alerts.NewGetV2ParamsWithContext(ctx)
			params.Body = &models.DetectsapiPostEntitiesAlertsV2Request{CompositeIds: chunk}
			if includeHidden != nil {
				params.IncludeHidden = includeHidden
			}
			resp, err := m.API.GetV2(params)
			if e := base.APIError(err, resp, scopeAlertsRead); e != nil {
				return nil, e
			}
			return resp.Payload.Resources, nil
		},
		// GetV2 returns alerts in arbitrary order; reorder to the query step's
		// sort. Field verified against the live API: composite_id.
		KeyFn: func(a *models.DetectsAlert) string {
			if a == nil || a.CompositeID == nil {
				return ""
			}
			return *a.CompositeID
		},
	})
}

// fqlBadRequest reports whether err is a 400-class alerts query error and, if
// so, extracts the API error details for an FQL-error response. gofalcon
// surfaces 400s as a typed *alerts.QueryV2BadRequest whose payload carries the
// errors; classify with errors.As rather than string matching.
func fqlBadRequest(err error) ([]base.FQLErrorDetail, bool) {
	var badReq *alerts.QueryV2BadRequest
	if !errors.As(err, &badReq) || badReq.Payload == nil {
		return nil, false
	}
	return apiErrorDetails(badReq.Payload.Errors), true
}

// apiErrorDetails flattens gofalcon MsaAPIError values into base.FQLErrorDetail.
func apiErrorDetails(errs []*models.MsaAPIError) []base.FQLErrorDetail {
	details := make([]base.FQLErrorDetail, 0, len(errs))
	for _, e := range errs {
		if e == nil {
			continue
		}
		var code int32
		if e.Code != nil {
			code = *e.Code
		}
		var msg string
		if e.Message != nil {
			msg = *e.Message
		}
		details = append(details, base.FQLErrorDetail{Code: code, Message: msg})
	}
	return details
}
