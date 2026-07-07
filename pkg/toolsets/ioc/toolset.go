// Package ioc implements the Falcon MCP "ioc" toolset: searching, creating, and
// deleting custom IOCs using the Falcon IOC Service Collection endpoints.
package ioc

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/ioc"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/strfmt"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://ioc/search/fql-guide"
)

// IOCAPI is the narrow slice of the gofalcon ioc client this toolset uses.
// Declaring it here keeps the handlers unit-testable with a hand-written mock.
type IOCAPI interface {
	IndicatorSearchV1(*ioc.IndicatorSearchV1Params, ...ioc.ClientOption) (*ioc.IndicatorSearchV1OK, error)
	IndicatorGetV1(*ioc.IndicatorGetV1Params, ...ioc.ClientOption) (*ioc.IndicatorGetV1OK, error)
	IndicatorCreateV1(*ioc.IndicatorCreateV1Params, ...ioc.ClientOption) (*ioc.IndicatorCreateV1Created, error)
	IndicatorDeleteV1(*ioc.IndicatorDeleteV1Params, ...ioc.ClientOption) (*ioc.IndicatorDeleteV1OK, error)
}

// Toolset is the ioc domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "ioc" }

func (Toolset) GetDescription() string {
	return "Search, create, and remove custom IOCs in CrowdStrike Falcon."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_iocs_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_iocs` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_iocs"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchIOCs(s, fc.IOC())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_add_ioc"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerAddIOC(s, fc.IOC())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_remove_iocs"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerRemoveIOCs(s, fc.IOC())
			},
		},
	}
}

// --- falcon_search_iocs ---

type searchIOCsInput struct {
	Filter     *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://ioc/search/fql-guide for syntax. Examples: type:'domain'+expired:false, source:'mcp'."`
	Limit      int64   `json:"limit,omitempty" jsonschema:"Maximum number of IOC IDs to return from search [1-500]. Default 10."`
	Offset     *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort       *string `json:"sort,omitempty" jsonschema:"Sort IOCs using FQL sort syntax. Common fields: action, applied_globally, created_on, expiration, modified_on, severity_number, source, type, value. Examples: modified_on.desc, severity_number|desc."`
	After      *string `json:"after,omitempty" jsonschema:"Pagination token for large result sets. Use the 'after' value returned by the previous search call."`
	FromParent *bool   `json:"from_parent,omitempty" jsonschema:"Return indicators from the MSSP parent when applicable."`
}

func registerSearchIOCs(s *mcp.Server, api IOCAPI) {
	desc := "Search custom IOCs and return full IOC details. Use this to find IOCs by type, " +
		"value, action, severity, or expiration status. Consult falcon://ioc/search/fql-guide " +
		"before constructing filter expressions. Returns full indicator records including " +
		"metadata, platforms, and host groups."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_iocs",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchIOCsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching indicator IDs.
		sp := ioc.NewIndicatorSearchV1ParamsWithContext(ctx)
		sp.Filter = in.Filter
		sp.Limit = &limit
		sp.Offset = in.Offset
		sp.Sort = in.Sort
		sp.After = in.After
		sp.FromParent = in.FromParent

		searchResp, err := api.IndicatorSearchV1(sp)
		if err != nil {
			return iocSearchErr("indicator_search_v1", "Failed to search IOCs", in.Filter, err)
		}

		ids := searchResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full details for the matched IDs.
		details, err := fetchIndicators(ctx, api, ids)
		if err != nil {
			resp := falcon.NormalizeError("indicator_get_v1", "Failed to get IOC details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_add_ioc ---

type addIOCInput struct {
	Type            *string          `json:"type,omitempty" jsonschema:"IOC type for single IOC creation. Common values: domain, ipv4, ipv6, md5, sha256. Required when indicators is not provided."`
	Value           *string          `json:"value,omitempty" jsonschema:"IOC value for single IOC creation. Required when indicators is not provided."`
	Action          string           `json:"action,omitempty" jsonschema:"Action for single IOC creation. Example values: detect, prevent, no_action. Default: detect."`
	Source          string           `json:"source,omitempty" jsonschema:"Source label for the IOC. Default: mcp."`
	Severity        *string          `json:"severity,omitempty" jsonschema:"Severity label for single IOC creation."`
	Description     *string          `json:"description,omitempty" jsonschema:"Description text for single IOC creation."`
	Expiration      *string          `json:"expiration,omitempty" jsonschema:"Expiration timestamp in UTC (ISO 8601). Example: 2026-12-31T23:59:59Z"`
	AppliedGlobally *bool            `json:"applied_globally,omitempty" jsonschema:"Whether the IOC is applied globally."`
	MobileAction    *string          `json:"mobile_action,omitempty" jsonschema:"Action to apply on mobile platforms."`
	Platforms       []string         `json:"platforms,omitempty" jsonschema:"Platform list for single IOC creation."`
	HostGroups      []string         `json:"host_groups,omitempty" jsonschema:"Host groups for scoped IOC application."`
	Tags            []string         `json:"tags,omitempty" jsonschema:"Falcon grouping tags to attach to the IOC."`
	Filename        *string          `json:"filename,omitempty" jsonschema:"Convenience shortcut for metadata filename."`
	Comment         *string          `json:"comment,omitempty" jsonschema:"Audit comment for IOC creation."`
	Indicators      []map[string]any `json:"indicators,omitempty" jsonschema:"Optional bulk IOC payload. If provided, single IOC fields are ignored."`
	IgnoreWarnings  bool             `json:"ignore_warnings,omitempty" jsonschema:"Set to true to ignore warnings and create all submitted IOCs."`
	Retrodetects    *bool            `json:"retrodetects,omitempty" jsonschema:"Whether to submit IOCs to retrodetect processing."`
}

func registerAddIOC(s *mcp.Server, api IOCAPI) {
	desc := "Create one or more custom IOCs. Provide type/value/action for a single IOC, or " +
		"pass a bulk indicators array. Returns the created indicator records on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_add_ioc",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in addIOCInput) (*mcp.CallToolResult, any, error) {
		body, validationErr := buildCreateBody(in)
		if validationErr != nil {
			return mcpx.JSONResult([]any{*validationErr})
		}

		cp := ioc.NewIndicatorCreateV1ParamsWithContext(ctx)
		cp.Body = body
		if in.IgnoreWarnings {
			v := true
			cp.IgnoreWarnings = &v
		}
		cp.Retrodetects = in.Retrodetects

		resp, err := api.IndicatorCreateV1(cp)
		if err != nil {
			e := falcon.NormalizeError("indicator_create_v1", "Failed to add IOC", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_remove_iocs ---

type removeIOCsInput struct {
	IDs        []string `json:"ids,omitempty" jsonschema:"IOC IDs to remove. Use this when deleting specific IOCs."`
	Filter     *string  `json:"filter,omitempty" jsonschema:"FQL expression for bulk IOC removal. If both filter and ids are provided, filter takes precedence."`
	Comment    *string  `json:"comment,omitempty" jsonschema:"Audit comment describing why these IOCs are being removed."`
	FromParent *bool    `json:"from_parent,omitempty" jsonschema:"Limit action to IOCs originating from the MSSP parent."`
}

func registerRemoveIOCs(s *mcp.Server, api IOCAPI) {
	desc := "Remove custom IOCs by IDs or FQL filter. Provide either specific IDs or an FQL " +
		"filter for bulk removal. If both are given, filter takes precedence. Returns a success " +
		"summary with deleted IOC IDs."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_remove_iocs",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in removeIOCsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 && in.Filter == nil {
			e := falcon.ErrorResponse{Error: "Either ids or filter must be provided to remove IOCs."}
			return mcpx.JSONResult([]any{e})
		}

		dp := ioc.NewIndicatorDeleteV1ParamsWithContext(ctx)
		dp.Ids = in.IDs
		dp.Filter = in.Filter
		dp.Comment = in.Comment
		dp.FromParent = in.FromParent

		resp, err := api.IndicatorDeleteV1(dp)
		if err != nil {
			e := falcon.NormalizeError("indicator_delete_v1", "Failed to remove IOCs", err)
			return mcpx.JSONResult([]any{e})
		}

		deleted := resp.GetPayload().Resources
		return mcpx.JSONResult(map[string]any{
			"status":      "deleted",
			"deleted_ids": deleted,
			"count":       len(deleted),
		})
	})
}

// --- helpers ---

func fetchIndicators(ctx context.Context, api IOCAPI, ids []string) ([]*models.APIIndicatorV1, error) {
	gp := ioc.NewIndicatorGetV1ParamsWithContext(ctx)
	gp.Ids = ids
	resp, err := api.IndicatorGetV1(gp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

func iocSearchErr(operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// buildCreateBody constructs the API request body from addIOCInput, mirroring
// the Python _build_add_ioc_payload logic. Returns a validation error when
// neither bulk indicators nor a type+value pair is provided.
func buildCreateBody(in addIOCInput) (*models.APIIndicatorCreateReqsV1, *falcon.ErrorResponse) {
	body := &models.APIIndicatorCreateReqsV1{}
	if in.Comment != nil {
		body.Comment = *in.Comment
	}

	if len(in.Indicators) > 0 {
		// Bulk path: caller supplied raw indicator maps. Convert to model structs.
		for _, m := range in.Indicators {
			body.Indicators = append(body.Indicators, mapToIndicator(m))
		}
		return body, nil
	}

	// Single indicator path.
	if in.Type == nil || in.Value == nil {
		e := falcon.NormalizeError("indicator_create_v1",
			"`type` and `value` are required when `indicators` is not provided", nil)
		return nil, &e
	}

	action := in.Action
	if action == "" {
		action = "detect"
	}
	source := in.Source
	if source == "" {
		source = "mcp"
	}

	indicator := &models.APIIndicatorCreateReqV1{
		Type:   *in.Type,
		Value:  *in.Value,
		Action: action,
		Source: source,
	}

	if in.Severity != nil {
		indicator.Severity = *in.Severity
	}
	if in.Description != nil {
		indicator.Description = *in.Description
	}
	if in.Expiration != nil {
		if dt, err := strfmt.ParseDateTime(*in.Expiration); err == nil {
			indicator.Expiration = &dt
		}
	}
	if in.AppliedGlobally != nil {
		indicator.AppliedGlobally = in.AppliedGlobally
	}
	if in.MobileAction != nil {
		indicator.MobileAction = *in.MobileAction
	}
	if len(in.Platforms) > 0 {
		indicator.Platforms = in.Platforms
	}
	if len(in.HostGroups) > 0 {
		indicator.HostGroups = in.HostGroups
	}
	if len(in.Tags) > 0 {
		indicator.Tags = in.Tags
	}
	if in.Filename != nil {
		indicator.Metadata = &models.APIMetadataReqV1{Filename: *in.Filename}
	}

	body.Indicators = []*models.APIIndicatorCreateReqV1{indicator}
	return body, nil
}

// mapToIndicator converts a raw map (from the bulk indicators input) to an
// APIIndicatorCreateReqV1. Only the string fields used in practice are mapped;
// unrecognized keys are silently ignored.
func mapToIndicator(m map[string]any) *models.APIIndicatorCreateReqV1 {
	ind := &models.APIIndicatorCreateReqV1{}
	if v, ok := m["type"].(string); ok {
		ind.Type = v
	}
	if v, ok := m["value"].(string); ok {
		ind.Value = v
	}
	if v, ok := m["action"].(string); ok {
		ind.Action = v
	}
	if v, ok := m["source"].(string); ok {
		ind.Source = v
	}
	if v, ok := m["severity"].(string); ok {
		ind.Severity = v
	}
	if v, ok := m["description"].(string); ok {
		ind.Description = v
	}
	if v, ok := m["mobile_action"].(string); ok {
		ind.MobileAction = v
	}
	if v, ok := m["expiration"].(string); ok {
		if dt, err := strfmt.ParseDateTime(v); err == nil {
			ind.Expiration = &dt
		}
	}
	if v, ok := m["applied_globally"].(bool); ok {
		ind.AppliedGlobally = &v
	}
	if vs, ok := toStringSlice(m["platforms"]); ok {
		ind.Platforms = vs
	}
	if vs, ok := toStringSlice(m["host_groups"]); ok {
		ind.HostGroups = vs
	}
	if vs, ok := toStringSlice(m["tags"]); ok {
		ind.Tags = vs
	}
	if meta, ok := m["metadata"].(map[string]any); ok {
		if fn, ok := meta["filename"].(string); ok {
			ind.Metadata = &models.APIMetadataReqV1{Filename: fn}
		}
	}
	return ind
}

func toStringSlice(v any) ([]string, bool) {
	raw, ok := v.([]any)
	if !ok {
		return nil, false
	}
	out := make([]string, 0, len(raw))
	for _, item := range raw {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out, true
}

func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 500 {
		return 500
	}
	return limit
}
