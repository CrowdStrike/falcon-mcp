// Package exclusions implements the Falcon MCP "exclusions" toolset: search,
// create, update, and delete exclusions across four exclusion types — IOA, ML,
// Sensor Visibility, and Certificate-Based — behind a single exclusion_type
// discriminator, plus a certificate-details lookup.
//
// Divergence note: the Python module uses the ML v2 query/get ops
// (exclusions_search_v2 / exclusions_get_v2), but gofalcon v0.21.0's generated
// OK structs for those ops discard the response body (no Payload field). This
// toolset therefore uses the ML v1 query/get ops (QueryMLExclusionsV1 /
// GetMLExclusionsV1), which return the same data via typed payloads. Create,
// update, and delete still use the v2 ML ops (their meta payloads are intact).
package exclusions

import (
	"context"
	"fmt"

	cbe "github.com/crowdstrike/gofalcon/falcon/client/certificate_based_exclusions"
	ioae "github.com/crowdstrike/gofalcon/falcon/client/ioa_exclusions"
	mle "github.com/crowdstrike/gofalcon/falcon/client/ml_exclusions"
	sve "github.com/crowdstrike/gofalcon/falcon/client/sensor_visibility_exclusions"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const fqlGuideURI = "falcon://exclusions/search/fql-guide"

var validTypes = []string{"ioa", "ml", "sensor_visibility", "certificate"}

// limitCap is the per-type maximum for the limit param.
var limitCap = map[string]int64{
	"ioa": 500, "ml": 500, "sensor_visibility": 500, "certificate": 100,
}

// --- narrow interfaces, one per gofalcon sub-client ---

type ioaAPI interface {
	SsIoaExclusionsSearchV2(*ioae.SsIoaExclusionsSearchV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsSearchV2OK, error)
	SsIoaExclusionsGetV2(*ioae.SsIoaExclusionsGetV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsGetV2OK, error)
	SsIoaExclusionsCreateV2(*ioae.SsIoaExclusionsCreateV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsCreateV2OK, error)
	SsIoaExclusionsUpdateV2(*ioae.SsIoaExclusionsUpdateV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsUpdateV2OK, error)
	SsIoaExclusionsDeleteV2(*ioae.SsIoaExclusionsDeleteV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsDeleteV2OK, error)
}

type mlAPI interface {
	QueryMLExclusionsV1(*mle.QueryMLExclusionsV1Params, ...mle.ClientOption) (*mle.QueryMLExclusionsV1OK, error)
	GetMLExclusionsV1(*mle.GetMLExclusionsV1Params, ...mle.ClientOption) (*mle.GetMLExclusionsV1OK, error)
	ExclusionsCreateV2(*mle.ExclusionsCreateV2Params, ...mle.ClientOption) (*mle.ExclusionsCreateV2OK, error)
	ExclusionsUpdateV2(*mle.ExclusionsUpdateV2Params, ...mle.ClientOption) (*mle.ExclusionsUpdateV2OK, error)
	ExclusionsDeleteV2(*mle.ExclusionsDeleteV2Params, ...mle.ClientOption) (*mle.ExclusionsDeleteV2OK, error)
}

type svAPI interface {
	QuerySensorVisibilityExclusionsV1(*sve.QuerySensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.QuerySensorVisibilityExclusionsV1OK, error)
	GetSensorVisibilityExclusionsV1(*sve.GetSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.GetSensorVisibilityExclusionsV1OK, error)
	CreateSVExclusionsV1(*sve.CreateSVExclusionsV1Params, ...sve.ClientOption) (*sve.CreateSVExclusionsV1Created, error)
	UpdateSensorVisibilityExclusionsV1(*sve.UpdateSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.UpdateSensorVisibilityExclusionsV1OK, error)
	DeleteSensorVisibilityExclusionsV1(*sve.DeleteSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.DeleteSensorVisibilityExclusionsV1OK, error)
}

type certAPI interface {
	CbExclusionsQueryV1(*cbe.CbExclusionsQueryV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsQueryV1OK, error)
	CbExclusionsGetV1(*cbe.CbExclusionsGetV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsGetV1OK, error)
	CbExclusionsCreateV1(*cbe.CbExclusionsCreateV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsCreateV1Created, error)
	CbExclusionsUpdateV1(*cbe.CbExclusionsUpdateV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsUpdateV1OK, error)
	CbExclusionsDeleteV1(*cbe.CbExclusionsDeleteV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsDeleteV1OK, error)
	CertificatesGetV1(*cbe.CertificatesGetV1Params, ...cbe.ClientOption) (*cbe.CertificatesGetV1OK, error)
}

// apis bundles the four sub-client interfaces for handler injection.
type apis struct {
	ioa  ioaAPI
	ml   mlAPI
	sv   svAPI
	cert certAPI
}

// Toolset is the exclusions domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "exclusions" }

func (Toolset) GetDescription() string {
	return "Manage CrowdStrike Falcon exclusions (IOA, ML, Sensor Visibility, Certificate-Based)."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(fqlGuideURI, "falcon_search_exclusions_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_exclusions` tool."),
	}
}

func (Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	build := func() apis {
		return apis{ioa: fc.IoaExclusions(), ml: fc.MlExclusions(), sv: fc.SensorVisibilityExclusions(), cert: fc.CertificateBasedExclusions()}
	}
	return []api.ServerTool{
		{Tool: &mcp.Tool{Name: "falcon_search_exclusions"}, Register: func(s *mcp.Server, _ *falcon.FalconClient) { registerSearch(s, build()) }},
		{Tool: &mcp.Tool{Name: "falcon_create_exclusion"}, Register: func(s *mcp.Server, _ *falcon.FalconClient) { registerCreate(s, build()) }},
		{Tool: &mcp.Tool{Name: "falcon_update_exclusion"}, Register: func(s *mcp.Server, _ *falcon.FalconClient) { registerUpdate(s, build()) }},
		{Tool: &mcp.Tool{Name: "falcon_delete_exclusions"}, Register: func(s *mcp.Server, _ *falcon.FalconClient) { registerDelete(s, build()) }},
		{Tool: &mcp.Tool{Name: "falcon_get_certificate_details"}, Register: func(s *mcp.Server, _ *falcon.FalconClient) { registerGetCert(s, build()) }},
	}
}

// --- falcon_search_exclusions (two-step per type) ---

type searchInput struct {
	ExclusionType string  `json:"exclusion_type" jsonschema:"Exclusion type to search: ioa, ml, sensor_visibility, or certificate."`
	Filter        *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://exclusions/search/fql-guide for syntax."`
	Limit         int64   `json:"limit,omitempty" jsonschema:"Maximum records to return. Default 100 (ioa/ml/sensor_visibility cap 500, certificate cap 100)."`
	Offset        *int64  `json:"offset,omitempty" jsonschema:"Offset to start retrieving records from."`
	Sort          *string `json:"sort,omitempty" jsonschema:"Sort expression, e.g. created_by.asc (ignored for certificate type)."`
}

func registerSearch(s *mcp.Server, a apis) {
	mcp.AddTool(s, &mcp.Tool{
		Name: "falcon_search_exclusions",
		Description: "Search for exclusions by type. The exclusion_type parameter selects which " +
			"exclusion API is queried (ioa, ml, sensor_visibility, certificate). Consult " +
			"falcon://exclusions/search/fql-guide before constructing filter expressions. Returns " +
			"full exclusion details.",
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchInput) (*mcp.CallToolResult, any, error) {
		if err := validateType(in.ExclusionType); err != nil {
			return mcpx.JSONResult([]any{*err})
		}
		limit := clampLimit(in.ExclusionType, in.Limit)
		sort := in.Sort
		if in.ExclusionType == "certificate" {
			sort = nil // certificate query does not support sort
		}

		switch in.ExclusionType {
		case "ioa":
			qp := ioae.NewSsIoaExclusionsSearchV2ParamsWithContext(ctx)
			qp.Filter, qp.Limit, qp.Offset, qp.Sort = in.Filter, &limit, in.Offset, sort
			qr, err := a.ioa.SsIoaExclusionsSearchV2(qp)
			if err != nil {
				return searchErr("ss_ioa_exclusions_search_v2", in.Filter, err)
			}
			ids := qr.GetPayload().Resources
			if len(ids) == 0 {
				return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
			}
			gp := ioae.NewSsIoaExclusionsGetV2ParamsWithContext(ctx)
			gp.Ids = ids
			dr, err := a.ioa.SsIoaExclusionsGetV2(gp)
			if err != nil {
				return detErr("ss_ioa_exclusions_get_v2", err)
			}
			return mcpx.JSONResult(dr.GetPayload().Resources)
		case "ml":
			qp := mle.NewQueryMLExclusionsV1ParamsWithContext(ctx)
			qp.Filter, qp.Limit, qp.Offset, qp.Sort = in.Filter, &limit, in.Offset, sort
			qr, err := a.ml.QueryMLExclusionsV1(qp)
			if err != nil {
				return searchErr("exclusions_search_v2", in.Filter, err)
			}
			ids := qr.GetPayload().Resources
			if len(ids) == 0 {
				return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
			}
			gp := mle.NewGetMLExclusionsV1ParamsWithContext(ctx)
			gp.Ids = ids
			dr, err := a.ml.GetMLExclusionsV1(gp)
			if err != nil {
				return detErr("exclusions_get_v2", err)
			}
			return mcpx.JSONResult(dr.GetPayload().Resources)
		case "sensor_visibility":
			qp := sve.NewQuerySensorVisibilityExclusionsV1ParamsWithContext(ctx)
			qp.Filter, qp.Limit, qp.Offset, qp.Sort = in.Filter, &limit, in.Offset, sort
			qr, err := a.sv.QuerySensorVisibilityExclusionsV1(qp)
			if err != nil {
				return searchErr("querySensorVisibilityExclusionsV1", in.Filter, err)
			}
			ids := qr.GetPayload().Resources
			if len(ids) == 0 {
				return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
			}
			gp := sve.NewGetSensorVisibilityExclusionsV1ParamsWithContext(ctx)
			gp.Ids = ids
			dr, err := a.sv.GetSensorVisibilityExclusionsV1(gp)
			if err != nil {
				return detErr("getSensorVisibilityExclusionsV1", err)
			}
			return mcpx.JSONResult(dr.GetPayload().Resources)
		default: // certificate
			qp := cbe.NewCbExclusionsQueryV1ParamsWithContext(ctx)
			qp.Filter, qp.Limit, qp.Offset = in.Filter, &limit, in.Offset
			qr, err := a.cert.CbExclusionsQueryV1(qp)
			if err != nil {
				return searchErr("cb_exclusions_query_v1", in.Filter, err)
			}
			ids := qr.GetPayload().Resources
			if len(ids) == 0 {
				return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
			}
			gp := cbe.NewCbExclusionsGetV1ParamsWithContext(ctx)
			gp.Ids = ids
			dr, err := a.cert.CbExclusionsGetV1(gp)
			if err != nil {
				return detErr("cb_exclusions_get_v1", err)
			}
			return mcpx.JSONResult(dr.GetPayload().Resources)
		}
	})
}

// --- falcon_create_exclusion ---

type createInput struct {
	ExclusionType   string   `json:"exclusion_type" jsonschema:"Exclusion type: ioa, ml, sensor_visibility, or certificate."`
	Name            *string  `json:"name,omitempty" jsonschema:"Exclusion name (IOA)."`
	Value           *string  `json:"value,omitempty" jsonschema:"Exclusion value/pattern (ML, Sensor Visibility)."`
	PatternID       *string  `json:"pattern_id,omitempty" jsonschema:"IOA pattern ID."`
	PatternName     *string  `json:"pattern_name,omitempty" jsonschema:"IOA pattern name."`
	IfnRegex        *string  `json:"ifn_regex,omitempty" jsonschema:"IOA image filename regex."`
	ClRegex         *string  `json:"cl_regex,omitempty" jsonschema:"IOA command line regex."`
	Description     *string  `json:"description,omitempty" jsonschema:"Exclusion description."`
	HostGroups      []string `json:"host_groups,omitempty" jsonschema:"Host group IDs to scope the exclusion to."`
	AppliedGlobally *bool    `json:"applied_globally,omitempty" jsonschema:"Apply the exclusion to all hosts."`
	Comment         *string  `json:"comment,omitempty" jsonschema:"Audit comment."`
	Groups          []string `json:"groups,omitempty" jsonschema:"Group IDs (ML / Sensor Visibility scoping)."`
}

func registerCreate(s *mcp.Server, a apis) {
	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_exclusion",
		Description: "Create an exclusion of the given exclusion_type (ioa, ml, sensor_visibility, certificate).",
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createInput) (*mcp.CallToolResult, any, error) {
		if err := validateType(in.ExclusionType); err != nil {
			return mcpx.JSONResult([]any{*err})
		}
		switch in.ExclusionType {
		case "ioa":
			body := &models.DomainSsIoaExclusionsCreateReqV2{
				Exclusions: []*models.DomainSsIoaExclusionCreateReqV2{{
					Name:        in.Name,
					PatternID:   in.PatternID,
					PatternName: strOrEmpty(in.PatternName),
					IfnRegex:    in.IfnRegex,
					ClRegex:     in.ClRegex,
					Description: strOrEmpty(in.Description),
					Comment:     strOrEmpty(in.Comment),
					HostGroups:  in.HostGroups,
				}},
			}
			p := ioae.NewSsIoaExclusionsCreateV2ParamsWithContext(ctx)
			p.Body = body
			r, err := a.ioa.SsIoaExclusionsCreateV2(p)
			return mutResult("ss_ioa_exclusions_create_v2", "Failed to create exclusion", err, func() any { return r.GetPayload() })
		case "ml":
			body := &models.DomainExclusionsCreateReqV2{
				Exclusions: []*models.DomainExclusionCreateReqV2{{
					Value:   strOrEmpty(in.Value),
					Groups:  in.Groups,
					Comment: strOrEmpty(in.Comment),
				}},
			}
			p := mle.NewExclusionsCreateV2ParamsWithContext(ctx)
			p.Body = body
			_, err := a.ml.ExclusionsCreateV2(p)
			return mutAck("exclusions_create_v2", "Failed to create exclusion", err)
		case "sensor_visibility":
			body := &models.SvExclusionsCreateReqV1{
				Value:   strOrEmpty(in.Value),
				Groups:  in.Groups,
				Comment: strOrEmpty(in.Comment),
			}
			p := sve.NewCreateSVExclusionsV1ParamsWithContext(ctx)
			p.Body = body
			r, err := a.sv.CreateSVExclusionsV1(p)
			return mutResult("createSVExclusionsV1", "Failed to create exclusion", err, func() any { return r.GetPayload() })
		default: // certificate
			body := &models.APICertBasedExclusionsCreateReqV1{
				Exclusions: []*models.APICertBasedExclusionCreateReqV1{{
					Name:            in.Name,
					Description:     strOrEmpty(in.Description),
					HostGroups:      in.HostGroups,
					AppliedGlobally: boolOrFalse(in.AppliedGlobally),
				}},
			}
			p := cbe.NewCbExclusionsCreateV1ParamsWithContext(ctx)
			p.Body = body
			r, err := a.cert.CbExclusionsCreateV1(p)
			return mutResult("cb_exclusions_create_v1", "Failed to create exclusion", err, func() any { return r.GetPayload() })
		}
	})
}

// --- falcon_update_exclusion ---

type updateInput struct {
	ExclusionType string   `json:"exclusion_type" jsonschema:"Exclusion type: ioa, ml, sensor_visibility, or certificate."`
	ID            string   `json:"id" jsonschema:"ID of the exclusion to update."`
	Name          *string  `json:"name,omitempty" jsonschema:"Updated name."`
	Value         *string  `json:"value,omitempty" jsonschema:"Updated value/pattern."`
	Description   *string  `json:"description,omitempty" jsonschema:"Updated description."`
	HostGroups    []string `json:"host_groups,omitempty" jsonschema:"Updated host group IDs."`
	Groups        []string `json:"groups,omitempty" jsonschema:"Updated group IDs (ML/Sensor Visibility)."`
	Comment       *string  `json:"comment,omitempty" jsonschema:"Audit comment."`
}

func registerUpdate(s *mcp.Server, a apis) {
	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_exclusion",
		Description: "Update an existing exclusion of the given exclusion_type.",
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateInput) (*mcp.CallToolResult, any, error) {
		if err := validateType(in.ExclusionType); err != nil {
			return mcpx.JSONResult([]any{*err})
		}
		if in.ID == "" {
			return mcpx.JSONResult([]any{falcon.ErrorResponse{Error: "Failed to update exclusion: id is required"}})
		}
		switch in.ExclusionType {
		case "ioa":
			body := &models.DomainSsIoaExclusionsUpdateReqV2{
				Exclusions: []*models.DomainSsIoaExclusionUpdateReqV2{{
					ID:          &in.ID,
					Name:        strOrEmpty(in.Name),
					Description: strOrEmpty(in.Description),
					Comment:     strOrEmpty(in.Comment),
					HostGroups:  in.HostGroups,
				}},
			}
			p := ioae.NewSsIoaExclusionsUpdateV2ParamsWithContext(ctx)
			p.Body = body
			r, err := a.ioa.SsIoaExclusionsUpdateV2(p)
			return mutResult("ss_ioa_exclusions_update_v2", "Failed to update exclusion", err, func() any { return r.GetPayload() })
		case "ml":
			body := &models.DomainExclusionUpdateReqV2{
				ID:      &in.ID,
				Value:   strOrEmpty(in.Value),
				Groups:  in.Groups,
				Comment: strOrEmpty(in.Comment),
			}
			p := mle.NewExclusionsUpdateV2ParamsWithContext(ctx)
			p.Body = body
			_, err := a.ml.ExclusionsUpdateV2(p)
			return mutAck("exclusions_update_v2", "Failed to update exclusion", err)
		case "sensor_visibility":
			body := &models.SvExclusionsUpdateReqV1{
				ID:      &in.ID,
				Value:   strOrEmpty(in.Value),
				Groups:  in.Groups,
				Comment: strOrEmpty(in.Comment),
			}
			p := sve.NewUpdateSensorVisibilityExclusionsV1ParamsWithContext(ctx)
			p.Body = body
			r, err := a.sv.UpdateSensorVisibilityExclusionsV1(p)
			return mutResult("updateSensorVisibilityExclusionsV1", "Failed to update exclusion", err, func() any { return r.GetPayload() })
		default: // certificate
			body := &models.APICertBasedExclusionsUpdateReqV1{
				Exclusions: []*models.APICertBasedExclusionUpdateReqV1{{
					ID:          &in.ID,
					Name:        strOrEmpty(in.Name),
					Description: strOrEmpty(in.Description),
					HostGroups:  in.HostGroups,
				}},
			}
			p := cbe.NewCbExclusionsUpdateV1ParamsWithContext(ctx)
			p.Body = body
			r, err := a.cert.CbExclusionsUpdateV1(p)
			return mutResult("cb_exclusions_update_v1", "Failed to update exclusion", err, func() any { return r.GetPayload() })
		}
	})
}

// --- falcon_delete_exclusions ---

type deleteInput struct {
	ExclusionType string   `json:"exclusion_type" jsonschema:"Exclusion type: ioa, ml, sensor_visibility, or certificate."`
	IDs           []string `json:"ids" jsonschema:"IDs of the exclusions to delete."`
	Comment       *string  `json:"comment,omitempty" jsonschema:"Audit comment."`
}

func registerDelete(s *mcp.Server, a apis) {
	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_exclusions",
		Description: "Delete exclusions of the given exclusion_type by ID.",
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteInput) (*mcp.CallToolResult, any, error) {
		if err := validateType(in.ExclusionType); err != nil {
			return mcpx.JSONResult([]any{*err})
		}
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{falcon.ErrorResponse{Error: "Failed to delete exclusions: ids is required"}})
		}
		switch in.ExclusionType {
		case "ioa":
			p := ioae.NewSsIoaExclusionsDeleteV2ParamsWithContext(ctx)
			p.Ids, p.Comment = in.IDs, in.Comment
			r, err := a.ioa.SsIoaExclusionsDeleteV2(p)
			return mutResult("ss_ioa_exclusions_delete_v2", "Failed to delete exclusions", err, func() any { return r.GetPayload() })
		case "ml":
			p := mle.NewExclusionsDeleteV2ParamsWithContext(ctx)
			p.Ids, p.Comment = in.IDs, in.Comment
			_, err := a.ml.ExclusionsDeleteV2(p)
			return mutAck("exclusions_delete_v2", "Failed to delete exclusions", err)
		case "sensor_visibility":
			p := sve.NewDeleteSensorVisibilityExclusionsV1ParamsWithContext(ctx)
			p.Ids, p.Comment = in.IDs, in.Comment
			r, err := a.sv.DeleteSensorVisibilityExclusionsV1(p)
			return mutResult("deleteSensorVisibilityExclusionsV1", "Failed to delete exclusions", err, func() any { return r.GetPayload() })
		default: // certificate
			p := cbe.NewCbExclusionsDeleteV1ParamsWithContext(ctx)
			p.Ids, p.Comment = in.IDs, in.Comment
			r, err := a.cert.CbExclusionsDeleteV1(p)
			return mutResult("cb_exclusions_delete_v1", "Failed to delete exclusions", err, func() any { return r.GetPayload() })
		}
	})
}

// --- falcon_get_certificate_details ---

type getCertInput struct {
	IDs []string `json:"ids" jsonschema:"Certificate IDs (SHA256 hashes) to retrieve details for."`
}

func registerGetCert(s *mcp.Server, a apis) {
	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_certificate_details",
		Description: "Retrieve details for one or more certificates by ID (used when building certificate-based exclusions).",
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getCertInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{})
		}
		p := cbe.NewCertificatesGetV1ParamsWithContext(ctx)
		p.Ids = in.IDs[0] // CertificatesGetV1 takes a single id string
		r, err := a.cert.CertificatesGetV1(p)
		if err != nil {
			e := falcon.NormalizeError("certificates_get_v1", "Failed to get certificate details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(r.GetPayload().Resources)
	})
}

// --- helpers ---

func validateType(t string) *falcon.ErrorResponse {
	for _, v := range validTypes {
		if t == v {
			return nil
		}
	}
	return &falcon.ErrorResponse{Error: fmt.Sprintf(
		"Invalid exclusion_type %q. Valid types: ioa, ml, sensor_visibility, certificate", t)}
}

func clampLimit(t string, limit int64) int64 {
	cap := limitCap[t]
	if cap == 0 {
		cap = 500
	}
	if limit <= 0 {
		if cap < 100 {
			return cap
		}
		return 100
	}
	if limit > cap {
		return cap
	}
	return limit
}

func searchErr(operation string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, "Failed to search exclusions", err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

func detErr(operation string, err error) (*mcp.CallToolResult, any, error) {
	e := falcon.NormalizeError(operation, "Failed to get exclusion details", err)
	return mcpx.JSONResult([]any{e})
}

func mutResult(operation, msg string, err error, payload func() any) (*mcp.CallToolResult, any, error) {
	if err != nil {
		e := falcon.NormalizeError(operation, msg, err)
		return mcpx.JSONResult([]any{e})
	}
	return mcpx.JSONResult(payload())
}

// mutAck is used for ML v2 mutation ops whose gofalcon OK structs discard the
// response body (no Payload). On success it returns a simple acknowledgment.
func mutAck(operation, msg string, err error) (*mcp.CallToolResult, any, error) {
	if err != nil {
		e := falcon.NormalizeError(operation, msg, err)
		return mcpx.JSONResult([]any{e})
	}
	return mcpx.JSONResult(map[string]any{"status": "ok", "operation": operation})
}

func strOrEmpty(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

func boolOrFalse(b *bool) bool {
	return b != nil && *b
}
