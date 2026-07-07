// Package data_protection implements the Falcon MCP "data_protection" toolset:
// read-only search for Data Protection classifications, policies, and content
// patterns. Each tool follows the canonical two-step pattern — query (IDs) then
// entities-get (full records) — matching the Python DataProtectionModule.
package data_protection

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/data_protection_configuration"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	classificationsFQLGuideURI = "falcon://data-protection/classifications/fql-guide"
	policiesFQLGuideURI        = "falcon://data-protection/policies/fql-guide"
	contentPatternsFQLGuideURI = "falcon://data-protection/content-patterns/fql-guide"
)

// DataProtectionAPI is the narrow slice of the gofalcon
// data_protection_configuration client this toolset uses. Declaring it here
// keeps the handlers unit-testable with a hand-written mock.
type DataProtectionAPI interface {
	QueriesClassificationGetV2(*data_protection_configuration.QueriesClassificationGetV2Params, ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesClassificationGetV2OK, error)
	EntitiesClassificationGetV2(*data_protection_configuration.EntitiesClassificationGetV2Params, ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesClassificationGetV2OK, error)

	QueriesPolicyGetV2(*data_protection_configuration.QueriesPolicyGetV2Params, ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesPolicyGetV2OK, error)
	EntitiesPolicyGetV2(*data_protection_configuration.EntitiesPolicyGetV2Params, ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesPolicyGetV2OK, error)

	QueriesContentPatternGetV2(*data_protection_configuration.QueriesContentPatternGetV2Params, ...data_protection_configuration.ClientOption) (*data_protection_configuration.QueriesContentPatternGetV2OK, error)
	EntitiesContentPatternGet(*data_protection_configuration.EntitiesContentPatternGetParams, ...data_protection_configuration.ClientOption) (*data_protection_configuration.EntitiesContentPatternGetOK, error)
}

// Toolset is the data_protection domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "data_protection" }

func (Toolset) GetDescription() string {
	return "Read-only access to CrowdStrike Falcon Data Protection classifications, policies, and content patterns."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			classificationsFQLGuideURI,
			"falcon_search_data_protection_classifications_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_data_protection_classifications` tool.",
		),
		fql.Resource(
			policiesFQLGuideURI,
			"falcon_search_data_protection_policies_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_data_protection_policies` tool.",
		),
		fql.Resource(
			contentPatternsFQLGuideURI,
			"falcon_search_data_protection_content_patterns_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_data_protection_content_patterns` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_data_protection_classifications"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchClassifications(s, fc.DataProtectionConfiguration())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_data_protection_policies"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchPolicies(s, fc.DataProtectionConfiguration())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_data_protection_content_patterns"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchContentPatterns(s, fc.DataProtectionConfiguration())
			},
		},
	}
}

// --- falcon_search_data_protection_classifications ---

// SearchClassificationsInput mirrors the Python search_data_protection_classifications
// signature. Optional fields use pointers so the inferred JSON Schema marks them
// optional; limit/offset use int64 to match the gofalcon API param type.
type SearchClassificationsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://data-protection/classifications/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-500]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Pagination offset."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort order. Ex: name.asc, created_at.desc, modified_at.desc"`
}

func registerSearchClassifications(s *mcp.Server, api DataProtectionAPI) {
	desc := "Search for Data Protection classifications in your CrowdStrike environment. " +
		"Use this to find classification rules that define what sensitive data patterns to detect. " +
		"Consult falcon://data-protection/classifications/fql-guide before constructing filter " +
		"expressions. Returns full classification details including content pattern references and " +
		"rule configuration."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_data_protection_classifications",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchClassificationsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 500)

		// Step 1: query IDs.
		qp := data_protection_configuration.NewQueriesClassificationGetV2ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.QueriesClassificationGetV2(qp)
		if err != nil {
			return searchErr("queries_classification_get_v2", "Failed to search Data Protection classifications", in.Filter, classificationsFQLGuideURI, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full classification details.
		ep := data_protection_configuration.NewEntitiesClassificationGetV2ParamsWithContext(ctx)
		ep.Ids = ids
		entResp, err := api.EntitiesClassificationGetV2(ep)
		if err != nil {
			normalized := falcon.NormalizeError("entities_classification_get_v2", "Failed to get Data Protection classification details", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(entResp.GetPayload().Resources)
	})
}

// --- falcon_search_data_protection_policies ---

// SearchPoliciesInput mirrors the Python search_data_protection_policies signature.
// PlatformName is required (no default in Python).
type SearchPoliciesInput struct {
	PlatformName string  `json:"platform_name" jsonschema:"Required. Platform to query: 'win' or 'mac'."`
	Filter       *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://data-protection/policies/fql-guide for syntax."`
	Limit        int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-500]. Default 100."`
	Offset       *int64  `json:"offset,omitempty" jsonschema:"Pagination offset."`
	Sort         *string `json:"sort,omitempty" jsonschema:"Sort order. Ex: name.asc, precedence.asc, created_at.desc"`
}

func registerSearchPolicies(s *mcp.Server, api DataProtectionAPI) {
	desc := "Search for Data Protection policies in your CrowdStrike environment. " +
		"Use this to find data protection policies by platform, enablement status, or precedence. " +
		"Requires a platform_name ('win' or 'mac'). Consult " +
		"falcon://data-protection/policies/fql-guide before constructing filter expressions. " +
		"Returns full policy details including host groups and classification assignments."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_data_protection_policies",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchPoliciesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 500)

		// Step 1: query IDs.
		qp := data_protection_configuration.NewQueriesPolicyGetV2ParamsWithContext(ctx)
		qp.PlatformName = in.PlatformName
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.QueriesPolicyGetV2(qp)
		if err != nil {
			return searchErr("queries_policy_get_v2", "Failed to search Data Protection policies", in.Filter, policiesFQLGuideURI, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full policy details.
		ep := data_protection_configuration.NewEntitiesPolicyGetV2ParamsWithContext(ctx)
		ep.Ids = ids
		entResp, err := api.EntitiesPolicyGetV2(ep)
		if err != nil {
			normalized := falcon.NormalizeError("entities_policy_get_v2", "Failed to get Data Protection policy details", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(entResp.GetPayload().Resources)
	})
}

// --- falcon_search_data_protection_content_patterns ---

// SearchContentPatternsInput mirrors the Python
// search_data_protection_content_patterns signature.
type SearchContentPatternsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://data-protection/content-patterns/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-500]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Pagination offset."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort order. Ex: name.asc, category.asc, region.asc"`
}

func registerSearchContentPatterns(s *mcp.Server, api DataProtectionAPI) {
	desc := "Search for Data Protection content patterns in your CrowdStrike environment. " +
		"Use this to find regex-based content detection patterns by type, category, or region. " +
		"Consult falcon://data-protection/content-patterns/fql-guide before constructing filter " +
		"expressions. Returns full pattern details including regex definitions and match thresholds."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_data_protection_content_patterns",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchContentPatternsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 500)

		// Step 1: query IDs.
		qp := data_protection_configuration.NewQueriesContentPatternGetV2ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.QueriesContentPatternGetV2(qp)
		if err != nil {
			return searchErr("queries_content_pattern_get_v2", "Failed to search Data Protection content patterns", in.Filter, contentPatternsFQLGuideURI, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full content pattern details.
		ep := data_protection_configuration.NewEntitiesContentPatternGetParamsWithContext(ctx)
		ep.Ids = ids
		entResp, err := api.EntitiesContentPatternGet(ep)
		if err != nil {
			normalized := falcon.NormalizeError("entities_content_pattern_get", "Failed to get Data Protection content pattern details", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(entResp.GetPayload().Resources)
	})
}

// --- helpers ---

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise. It always returns a
// successful tool result wrapping the error object (parity with the Python
// modules, which return error dicts rather than protocol errors).
func searchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to [1,max], defaulting to def when
// unset (0).
func normalizeLimit(limit int64, def, max int64) int64 {
	if limit <= 0 {
		return def
	}
	if limit > max {
		return max
	}
	return limit
}
