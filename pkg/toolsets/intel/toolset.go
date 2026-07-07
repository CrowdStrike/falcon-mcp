// Package intel implements the Falcon MCP "intel" toolset: searching threat
// actors, indicators, and intelligence reports, and generating MITRE ATT&CK
// reports for a given threat actor.
package intel

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"unicode"

	"github.com/crowdstrike/gofalcon/falcon/client/intel"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	actorsFQLGuideURI     = "falcon://intel/actors/fql-guide"
	indicatorsFQLGuideURI = "falcon://intel/indicators/fql-guide"
	reportsFQLGuideURI    = "falcon://intel/reports/fql-guide"
)

// IntelAPI is the narrow slice of the gofalcon intel client this toolset uses.
// Declaring it here keeps handlers unit-testable with a hand-written mock.
type IntelAPI interface {
	QueryIntelActorEntities(*intel.QueryIntelActorEntitiesParams, ...intel.ClientOption) (*intel.QueryIntelActorEntitiesOK, error)
	QueryIntelIndicatorEntities(*intel.QueryIntelIndicatorEntitiesParams, ...intel.ClientOption) (*intel.QueryIntelIndicatorEntitiesOK, error)
	QueryIntelReportEntities(*intel.QueryIntelReportEntitiesParams, ...intel.ClientOption) (*intel.QueryIntelReportEntitiesOK, error)
}

// mitreDownloadFunc downloads a MITRE ATT&CK report for an actor by ID and
// format. Injected so handlers can be unit-tested without the gofalcon transport.
type mitreDownloadFunc func(ctx context.Context, actorID, format string) ([]byte, error)

// actorSearchFunc resolves an actor name to a list of actor documents via
// QueryIntelActorEntities. Injected for testability.
type actorSearchFunc func(ctx context.Context, filter string, limit int64) ([]*models.ActorActorDocument, error)

// Toolset is the intel domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "intel" }

func (Toolset) GetDescription() string {
	return "Access CrowdStrike Falcon intelligence: threat actors, indicators, reports, and MITRE ATT&CK data."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			actorsFQLGuideURI,
			"falcon_search_actors_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_actors` tool.",
		),
		fql.Resource(
			indicatorsFQLGuideURI,
			"falcon_search_indicators_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_indicators` tool.",
		),
		fql.Resource(
			reportsFQLGuideURI,
			"falcon_search_reports_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_reports` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_actors"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchActors(s, fc.Intel())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_indicators"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchIndicators(s, fc.Intel())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_reports"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchReports(s, fc.Intel())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_mitre_report"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				searchFn := func(ctx context.Context, filter string, limit int64) ([]*models.ActorActorDocument, error) {
					p := intel.NewQueryIntelActorEntitiesParamsWithContext(ctx)
					p.Filter = &filter
					p.Limit = &limit
					resp, err := fc.Intel().QueryIntelActorEntities(p)
					if err != nil {
						return nil, err
					}
					return resp.GetPayload().Resources, nil
				}
				registerGetMitreReport(s, searchFn, fc.GetMitreReport)
			},
		},
	}
}

// --- falcon_search_actors ---

type searchActorsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://intel/actors/fql-guide for syntax. Examples: name:'COZY BEAR', target_countries:'US'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-5000]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return records. Defaults to 0."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Field and direction to sort results. Format: {field}|{asc/desc}. Valid fields: name, target_countries, target_industries, type, created_date, last_activity_date, last_modified_date. Ex: created_date|desc."`
	Q      *string `json:"q,omitempty" jsonschema:"Free text search across all indexed fields. Ex: 'BEAR'."`
}

func registerSearchActors(s *mcp.Server, api IntelAPI) {
	desc := "Research threat actors and adversary groups tracked by CrowdStrike intelligence. " +
		"Use this to search actors by name, target countries/industries, or activity dates. " +
		"Consult falcon://intel/actors/fql-guide before constructing filter expressions. " +
		"Returns full actor profiles including aliases, motivations, and targeting details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_actors",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchActorsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		p := intel.NewQueryIntelActorEntitiesParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort
		p.Q = in.Q

		resp, err := api.QueryIntelActorEntities(p)
		if err != nil {
			return intelSearchErr("QueryIntelActorEntities", "Failed to search actors", in.Filter, actorsFQLGuideURI, err)
		}
		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_search_indicators ---

type searchIndicatorsInput struct {
	Filter           *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://intel/indicators/fql-guide for syntax. Examples: type:'domain', malware_families:'Emotet'."`
	Limit            int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-5000]. Default 10."`
	Offset           *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return records. Defaults to 0."`
	Sort             *string `json:"sort,omitempty" jsonschema:"Field and direction to sort results. Format: {field}|{asc/desc}. Valid fields: id, indicator, type, published_date, last_updated, _marker. Ex: published_date|desc."`
	Q                *string `json:"q,omitempty" jsonschema:"Free text search across all indexed fields."`
	IncludeDeleted   *bool   `json:"include_deleted,omitempty" jsonschema:"If true, include both published and deleted indicators in the response. Defaults to false."`
	IncludeRelations *bool   `json:"include_relations,omitempty" jsonschema:"If true, include related indicators in the response. Defaults to true."`
}

func registerSearchIndicators(s *mcp.Server, api IntelAPI) {
	desc := "Search for threat indicators and IOCs from CrowdStrike intelligence. " +
		"Use this to find indicators by type, publish date, malware family, or threat actor " +
		"association. Consult falcon://intel/indicators/fql-guide before constructing filter " +
		"expressions. Returns full indicator details including labels, relations, and kill chain stage."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_indicators",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchIndicatorsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		p := intel.NewQueryIntelIndicatorEntitiesParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort
		p.Q = in.Q
		p.IncludeDeleted = in.IncludeDeleted
		p.IncludeRelations = in.IncludeRelations

		resp, err := api.QueryIntelIndicatorEntities(p)
		if err != nil {
			return intelSearchErr("QueryIntelIndicatorEntities", "Failed to search indicators", in.Filter, indicatorsFQLGuideURI, err)
		}
		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_search_reports ---

type searchReportsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://intel/reports/fql-guide for syntax. Examples: type.name:'Threat Intelligence Report', target_industries:'Finance'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of records to return [1-5000]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return records. Defaults to 0."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Field and direction to sort results. Format: {field}|{asc/desc}. Valid fields: name, target_countries, target_industries, type, created_date, last_modified_date. Ex: created_date|desc."`
	Q      *string `json:"q,omitempty" jsonschema:"Free text search across all indexed fields."`
}

func registerSearchReports(s *mcp.Server, api IntelAPI) {
	desc := "Search CrowdStrike intelligence publications and threat reports. " +
		"Use this to find reports by name, target industry, threat type, or publication date. " +
		"Consult falcon://intel/reports/fql-guide before constructing filter expressions. " +
		"Returns full report metadata including title, description, and target details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_reports",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchReportsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		p := intel.NewQueryIntelReportEntitiesParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort
		p.Q = in.Q

		resp, err := api.QueryIntelReportEntities(p)
		if err != nil {
			return intelSearchErr("QueryIntelReportEntities", "Failed to search reports", in.Filter, reportsFQLGuideURI, err)
		}
		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_get_mitre_report ---

type getMitreReportInput struct {
	Actor  string `json:"actor" jsonschema:"Threat actor name or numeric ID. Examples: 'WARP PANDA', '234987', 'revenant spider'. If a name is given, it is resolved to an ID via QueryIntelActorEntities first."`
	Format string `json:"format,omitempty" jsonschema:"Report format. Accepted options: 'csv' or 'json'. Defaults to 'json'."`
}

func registerGetMitreReport(s *mcp.Server, searchFn actorSearchFunc, download mitreDownloadFunc) {
	desc := "Generate a MITRE ATT&CK report for a given threat actor. " +
		"Accepts an actor name (e.g. 'WARP PANDA') or numeric ID. " +
		"Returns MITRE ATT&CK tactics, techniques, and procedures (TTPs) for the actor. " +
		"JSON format returns structured data; CSV format returns raw CSV text."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_mitre_report",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getMitreReportInput) (*mcp.CallToolResult, any, error) {
		format := in.Format
		if format == "" {
			format = "json"
		}

		actorID := strings.TrimSpace(in.Actor)

		// If the actor value is not all digits, resolve the name to a numeric ID.
		if !isAllDigits(actorID) {
			filter := fmt.Sprintf("name:'%s'", actorID)
			results, err := searchFn(ctx, filter, 1)
			if err != nil {
				e := falcon.NormalizeError("QueryIntelActorEntities", "Failed to search for actor by name", err)
				return mcpx.JSONResult([]any{e})
			}
			if len(results) == 0 {
				return mcpx.JSONResult([]any{map[string]string{
					"error":   "Actor not found",
					"message": fmt.Sprintf("No actor found with name: %s", in.Actor),
				}})
			}
			selected := results[0]
			if selected.ID == nil {
				return mcpx.JSONResult([]any{map[string]any{
					"error":      "Invalid actor data",
					"message":    fmt.Sprintf("Found actor '%s' but missing ID field", selected.Name),
					"actor_data": selected,
				}})
			}
			actorID = fmt.Sprintf("%d", *selected.ID)
		}

		data, err := download(ctx, actorID, format)
		if err != nil {
			e := falcon.NormalizeError("GetMitreReport", "Failed to get MITRE report", err)
			return mcpx.JSONResult([]any{e})
		}

		// For JSON format, parse the bytes and return structured data (matching the
		// Python json.loads path). For CSV, return the raw decoded string.
		if strings.EqualFold(format, "json") {
			stripped := strings.TrimSpace(string(data))
			if stripped == "" || stripped == "null" {
				return mcpx.JSONResult([]any{})
			}
			var parsed any
			if err := json.Unmarshal([]byte(stripped), &parsed); err != nil {
				return mcpx.JSONResult([]any{map[string]string{
					"error":   "JSON parse failure",
					"message": err.Error(),
				}})
			}
			return mcpx.JSONResult(parsed)
		}
		// CSV: return raw string
		return mcpx.JSONResult(string(data))
	})
}

// isAllDigits reports whether s consists entirely of ASCII digit characters
// (matching the Python actor_id.isdigit() check).
func isAllDigits(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if !unicode.IsDigit(r) {
			return false
		}
	}
	return true
}

// --- helpers ---

func intelSearchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 5000 {
		return 5000
	}
	return limit
}
