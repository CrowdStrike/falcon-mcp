// Package serverless implements the Falcon MCP "serverless" toolset: search
// for vulnerabilities in serverless functions (Lambda/Cloud Functions/Azure
// Functions) across cloud providers. It is a single-step search example —
// GetCombinedVulnerabilitiesSARIF returns vulnerability data directly in SARIF
// format, unlike the two-step query+details pattern used by hosts.
package serverless

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/serverless_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://serverless/vulnerabilities/fql-guide"
)

// ServerlessVulnerabilitiesAPI is the narrow slice of the gofalcon serverless
// vulnerabilities client this toolset uses. Declaring it here (rather than
// depending on the full ClientService) keeps the handler unit-testable with a
// hand-written mock.
type ServerlessVulnerabilitiesAPI interface {
	GetCombinedVulnerabilitiesSARIF(*serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFParams, ...serverless_vulnerabilities.ClientOption) (*serverless_vulnerabilities.GetCombinedVulnerabilitiesSARIFOK, error)
}

// Toolset is the serverless domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "serverless" }

func (Toolset) GetDescription() string {
	return "Access and manage CrowdStrike Falcon Serverless Vulnerabilities."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_serverless_vulnerabilities_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_serverless_vulnerabilities` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_serverless_vulnerabilities"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchServerlessVulnerabilities(s, fc.ServerlessVulnerabilities())
			},
		},
	}
}

// --- falcon_search_serverless_vulnerabilities ---

// SearchServerlessVulnerabilitiesInput mirrors the Python
// search_serverless_vulnerabilities signature. Filter is required (unlike the
// hosts search); limit/offset/sort are optional.
type SearchServerlessVulnerabilitiesInput struct {
	Filter string  `json:"filter" jsonschema:"FQL filter expression (required). See falcon://serverless/vulnerabilities/fql-guide for syntax. Examples: cloud_provider:'aws', severity:'HIGH'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"The upper-bound on the number of records to retrieve [1+]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"The offset from where to begin."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort serverless vulnerabilities using FQL syntax. Format: 'field'. Supported fields: application_name, application_name_version, cid, cloud_account_id, cloud_account_name, cloud_provider, cve_id, cvss_base_score, exprt_rating, first_seen_timestamp, function_resource_id, is_supported, layer, region, runtime, severity, timestamp, type. Examples: 'severity', 'cloud_provider', 'first_seen_timestamp'."`
}

func registerSearchServerlessVulnerabilities(s *mcp.Server, api ServerlessVulnerabilitiesAPI) {
	desc := "Search for vulnerabilities in serverless functions across all cloud providers. Use " +
		"this to find CVEs in Lambda/Cloud Functions/Azure Functions by severity, provider, or " +
		"runtime. Consult falcon://serverless/vulnerabilities/fql-guide before constructing filter " +
		"expressions. Returns vulnerability data in SARIF format including CVE IDs, severity " +
		"levels, and descriptions."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_serverless_vulnerabilities",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchServerlessVulnerabilitiesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		filter := in.Filter

		qp := serverless_vulnerabilities.NewGetCombinedVulnerabilitiesSARIFParamsWithContext(ctx)
		qp.Filter = &filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		resp, err := api.GetCombinedVulnerabilitiesSARIF(qp)
		if err != nil {
			normalized := falcon.NormalizeError("GetCombinedVulnerabilitiesSARIF", "Failed to search serverless vulnerabilities", err)
			if falcon.IsFQLError(normalized.StatusCode) {
				return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, &filter, fql.MustGuide(fqlGuideURI)))
			}
			return mcpx.JSONResult([]any{normalized})
		}

		// The SARIF payload nests its findings under Resources[].Runs (each
		// resource is a SARIF document). The Python module flattens this to a
		// single "runs" list (`response.get("runs") or []`); mirror that here
		// by concatenating Runs across every resource.
		runs := flattenRuns(resp.GetPayload().Resources)
		if len(runs) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(&filter))
		}
		return mcpx.JSONResult(runs)
	})
}

// flattenRuns concatenates the Runs of every SARIF resource into a single
// slice, matching the Python module's flattened "runs" return value.
func flattenRuns(resources []*models.ModelsVulnerabilitySARIF) []*models.ModelsRun {
	var runs []*models.ModelsRun
	for _, r := range resources {
		if r == nil {
			continue
		}
		runs = append(runs, r.Runs...)
	}
	return runs
}

// normalizeLimit clamps the requested limit to a minimum of 1, defaulting to
// 10 when unset (0). The API documents no upper bound for this operation.
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	return limit
}
