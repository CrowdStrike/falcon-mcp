// Package spotlight implements the Falcon MCP "spotlight" toolset: search and
// retrieval of Spotlight vulnerability findings. This is a single-step combined
// query — the API returns full vulnerability resources directly, with no
// separate details call.
package spotlight

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/spotlight_vulnerabilities"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://spotlight/vulnerabilities/fql-guide"
)

// SpotlightAPI is the narrow slice of the gofalcon spotlight_vulnerabilities
// client this toolset uses. Declaring it here keeps handlers unit-testable
// with a hand-written mock.
type SpotlightAPI interface {
	CombinedQueryVulnerabilities(*spotlight_vulnerabilities.CombinedQueryVulnerabilitiesParams, ...spotlight_vulnerabilities.ClientOption) (*spotlight_vulnerabilities.CombinedQueryVulnerabilitiesOK, error)
}

// Toolset is the spotlight domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "spotlight" }

func (Toolset) GetDescription() string {
	return "Access and manage CrowdStrike Falcon Spotlight vulnerability findings."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_vulnerabilities_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_vulnerabilities` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_vulnerabilities"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchVulnerabilities(s, fc.SpotlightVulnerabilities())
			},
		},
	}
}

// --- falcon_search_vulnerabilities ---

// SearchVulnerabilitiesInput mirrors the Python search_vulnerabilities signature.
// Optional fields use pointers so the inferred JSON Schema marks them optional.
// Note: the Spotlight combined API is cursor-paginated via `after`; gofalcon's
// CombinedQueryVulnerabilities exposes no numeric offset, so (unlike the Python
// tool) this input omits `offset` — use `after` for pagination.
type SearchVulnerabilitiesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://spotlight/vulnerabilities/fql-guide for syntax. Examples: status:'open', cve.severity:'HIGH'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of results to return [1-5000]. Default 10."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort vulnerabilities using FQL syntax. Supported fields: created_timestamp, closed_timestamp, updated_timestamp. Format: 'field|direction'. Examples: 'created_timestamp|desc', 'updated_timestamp|desc', 'closed_timestamp|asc'."`
	After  *string `json:"after,omitempty" jsonschema:"A pagination token used with the limit parameter to manage pagination of results. On your first request, don't provide an after token. On subsequent requests, provide the after token from the previous response to continue from that place in the results."`
	Facet  *string `json:"facet,omitempty" jsonschema:"Select various detail blocks to be returned for each vulnerability. Important: Use only one value! Supported values: host_info (host/asset context), remediation (fix information), cve (CVE details and scoring), evaluation_logic (assessment methodology). Examples: 'host_info', 'cve', 'remediation'."`
}

func registerSearchVulnerabilities(s *mcp.Server, api SpotlightAPI) {
	desc := "Search for vulnerabilities in your CrowdStrike environment. " +
		"Use this to find vulnerabilities by CVE severity, status, host, or remediation " +
		"state. Consult falcon://spotlight/vulnerabilities/fql-guide before constructing " +
		"filter expressions. Returns vulnerability details including CVE info, host context, " +
		"and remediation guidance (based on facet selection)."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_vulnerabilities",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchVulnerabilitiesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		qp := spotlight_vulnerabilities.NewCombinedQueryVulnerabilitiesParamsWithContext(ctx)
		if in.Filter != nil {
			qp.Filter = *in.Filter
		}
		qp.Limit = &limit
		qp.After = in.After
		qp.Sort = in.Sort
		if in.Facet != nil {
			qp.Facet = []string{*in.Facet}
		}

		resp, err := api.CombinedQueryVulnerabilities(qp)
		if err != nil {
			return searchErr(ctx, "combinedQueryVulnerabilities", "Failed to search vulnerabilities", in.Filter, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- helpers ---

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
