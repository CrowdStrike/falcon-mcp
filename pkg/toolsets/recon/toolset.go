// Package recon implements the Falcon MCP "recon" toolset: search and detail
// retrieval for Falcon Intelligence Recon notifications, monitoring rules, and
// exposed-data records. Each tool follows the canonical two-step pattern:
// query (IDs) then details (full records).
package recon

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/recon"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	notificationsFQLGuideURI      = "falcon://recon/notifications/search/fql-guide"
	rulesFQLGuideURI              = "falcon://recon/rules/search/fql-guide"
	exposedDataRecordsFQLGuideURI = "falcon://recon/exposed-data-records/search/fql-guide"
)

// ReconAPI is the narrow slice of the gofalcon recon client this toolset uses.
// Declaring it here keeps the handlers unit-testable with a hand-written mock.
type ReconAPI interface {
	QueryNotificationsV1(*recon.QueryNotificationsV1Params, ...recon.ClientOption) (*recon.QueryNotificationsV1OK, error)
	GetNotificationsDetailedV1(*recon.GetNotificationsDetailedV1Params, ...recon.ClientOption) (*recon.GetNotificationsDetailedV1OK, error)
	QueryRulesV1(*recon.QueryRulesV1Params, ...recon.ClientOption) (*recon.QueryRulesV1OK, error)
	GetRulesV1(*recon.GetRulesV1Params, ...recon.ClientOption) (*recon.GetRulesV1OK, error)
	QueryNotificationsExposedDataRecordsV1(*recon.QueryNotificationsExposedDataRecordsV1Params, ...recon.ClientOption) (*recon.QueryNotificationsExposedDataRecordsV1OK, error)
	GetNotificationsExposedDataRecordsV1(*recon.GetNotificationsExposedDataRecordsV1Params, ...recon.ClientOption) (*recon.GetNotificationsExposedDataRecordsV1OK, error)
}

// Toolset is the recon domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "recon" }

func (Toolset) GetDescription() string {
	return "Access Falcon Intelligence Recon notifications, monitoring rules, and exposed-data records."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			notificationsFQLGuideURI,
			"falcon_search_recon_notifications_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_recon_notifications` tool.",
		),
		fql.Resource(
			rulesFQLGuideURI,
			"falcon_search_recon_rules_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_recon_rules` tool.",
		),
		fql.Resource(
			exposedDataRecordsFQLGuideURI,
			"falcon_search_recon_exposed_data_records_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_recon_exposed_data_records` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_recon_notifications"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchReconNotifications(s, fc.Recon())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_recon_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchReconRules(s, fc.Recon())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_recon_exposed_data_records"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchReconExposedDataRecords(s, fc.Recon())
			},
		},
	}
}

// --- shared input type for all three search tools ---

// SearchReconInput holds the common parameters shared across all three recon
// search tools. Optional fields use pointers so the inferred JSON Schema marks
// them optional.
type SearchReconInput struct {
	Filter *string `json:"filter,omitempty"`
	Q      *string `json:"q,omitempty"      jsonschema:"Free text search across all indexed fields."`
	Limit  int64   `json:"limit,omitempty"`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination. offset + limit must not exceed 10,000."`
	Sort   *string `json:"sort,omitempty"`
}

// --- falcon_search_recon_notifications ---

func registerSearchReconNotifications(s *mcp.Server, api ReconAPI) {
	desc := "Search Falcon Intelligence Recon notifications (also called recon alerts) and return " +
		"their full details. Use this for dark web matches, leaked credentials, typosquatting " +
		"matches, and breach summaries triggered by your monitoring rules. Consult " +
		"falcon://recon/notifications/search/fql-guide before constructing filter expressions. " +
		"This serves the external cyber risk monitoring capability of CrowdStrike Counter " +
		"Adversary Operations (CAO). For endpoint, XDR, or NG-SIEM alerts, use " +
		"falcon_search_detections instead. Returns full notification records with a nested " +
		"`notification` object containing status, rule metadata, breach_summary, and item details."

	type input struct {
		Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://recon/notifications/search/fql-guide for syntax. Examples: status:'new'+rule_priority:'high', item_site:'telegram.org', created_date:>'now-7d'."`
		Q      *string `json:"q,omitempty"      jsonschema:"Free text search across all notification metadata."`
		Limit  int64   `json:"limit,omitempty"  jsonschema:"Maximum number of notifications to return [1-500]. Default 10. offset + limit must not exceed 10,000."`
		Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination. offset + limit must not exceed 10,000."`
		Sort   *string `json:"sort,omitempty"   jsonschema:"Sort notifications. Possible order by fields: created_date, updated_date. Append |asc or |desc for direction (default desc). Examples: 'created_date|desc', 'updated_date|asc'."`
	}

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_recon_notifications",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in input) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		qp := recon.NewQueryNotificationsV1ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q

		queryResp, err := api.QueryNotificationsV1(qp)
		if err != nil {
			return notificationsSearchErr(ctx, "QueryNotificationsV1", "Failed to search recon notifications", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := recon.NewGetNotificationsDetailedV1ParamsWithContext(ctx)
		dp.Ids = ids
		detailsResp, err := api.GetNotificationsDetailedV1(dp)
		if err != nil {
			return notificationsSearchErr(ctx, "GetNotificationsDetailedV1", "Failed to get recon notification details", in.Filter, err)
		}
		return mcpx.JSONResult(detailsResp.GetPayload().Resources)
	})
}

func notificationsSearchErr(_ context.Context, operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(notificationsFQLGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// --- falcon_search_recon_rules ---

func registerSearchReconRules(s *mcp.Server, api ReconAPI) {
	desc := "Search Falcon Intelligence Recon monitoring rules and return their full details. " +
		"Use this to list the rules that generate your recon notifications — find rules by " +
		"topic (domain, email, typosquatting, brand), priority, status, or whether breach " +
		"monitoring is enabled. Consult falcon://recon/rules/search/fql-guide before " +
		"constructing filter expressions. These monitoring rules power the external cyber risk " +
		"monitoring capability of CrowdStrike Counter Adversary Operations (CAO). Returns full " +
		"rule definitions including topic, priority, filter expressions, and notification settings."

	type input struct {
		Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://recon/rules/search/fql-guide for syntax. Examples: status:'active'+priority:'high', topic:'SA_TYPOSQUATTING', breach_monitoring_enabled:true."`
		Q      *string `json:"q,omitempty"      jsonschema:"Free text search across all rule metadata."`
		Limit  int64   `json:"limit,omitempty"  jsonschema:"Maximum number of rules to return [1-500]. Default 10. offset + limit must not exceed 10,000."`
		Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination. offset + limit must not exceed 10,000."`
		Sort   *string `json:"sort,omitempty"   jsonschema:"Sort rules. Possible order by fields: created_timestamp, last_updated_timestamp, priority, topic. Append |asc or |desc for direction (default desc). Examples: 'created_timestamp|desc', 'priority|asc'."`
	}

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_recon_rules",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in input) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		qp := recon.NewQueryRulesV1ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q

		queryResp, err := api.QueryRulesV1(qp)
		if err != nil {
			return rulesSearchErr(ctx, "QueryRulesV1", "Failed to search recon rules", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := recon.NewGetRulesV1ParamsWithContext(ctx)
		dp.Ids = ids
		detailsResp, err := api.GetRulesV1(dp)
		if err != nil {
			return rulesSearchErr(ctx, "GetRulesV1", "Failed to get recon rule details", in.Filter, err)
		}
		return mcpx.JSONResult(detailsResp.GetPayload().Resources)
	})
}

func rulesSearchErr(_ context.Context, operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(rulesFQLGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// --- falcon_search_recon_exposed_data_records ---

func registerSearchReconExposedDataRecords(s *mcp.Server, api ReconAPI) {
	desc := "Search Falcon Intelligence Recon exposed-data records and return their full details. " +
		"Use this to find leaked credential and PII rows associated with recon notifications — " +
		"emails, login IDs, password hashes, domains, and breach metadata. Consult " +
		"falcon://recon/exposed-data-records/search/fql-guide before constructing filter " +
		"expressions. These records are part of the external cyber risk monitoring capability of " +
		"CrowdStrike Counter Adversary Operations (CAO). Returns full records including credential " +
		"fields, location data, and associated notification context."

	type input struct {
		Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://recon/exposed-data-records/search/fql-guide for syntax. Examples: domain:'example.com'+credential_status:'confirmed_active', notification_id:'abc123def456', created_date:>'now-7d'."`
		Q      *string `json:"q,omitempty"      jsonschema:"Free text search across all exposed-data record fields."`
		Limit  int64   `json:"limit,omitempty"  jsonschema:"Maximum number of records to return [1-500]. Default 10. offset + limit must not exceed 10,000."`
		Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination. offset + limit must not exceed 10,000."`
		Sort   *string `json:"sort,omitempty"   jsonschema:"Sort records. Possible order by fields: created_date, updated_date. Append |asc or |desc for direction (default desc). Examples: 'created_date|desc', 'exposure_date|desc'."`
	}

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_recon_exposed_data_records",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in input) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		qp := recon.NewQueryNotificationsExposedDataRecordsV1ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q

		queryResp, err := api.QueryNotificationsExposedDataRecordsV1(qp)
		if err != nil {
			return exposedDataSearchErr(ctx, "QueryNotificationsExposedDataRecordsV1", "Failed to search recon exposed-data records", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		dp := recon.NewGetNotificationsExposedDataRecordsV1ParamsWithContext(ctx)
		dp.Ids = ids
		detailsResp, err := api.GetNotificationsExposedDataRecordsV1(dp)
		if err != nil {
			return exposedDataSearchErr(ctx, "GetNotificationsExposedDataRecordsV1", "Failed to get recon exposed-data record details", in.Filter, err)
		}
		return mcpx.JSONResult(detailsResp.GetPayload().Resources)
	})
}

func exposedDataSearchErr(_ context.Context, operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(exposedDataRecordsFQLGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// --- helpers ---

// normalizeLimit clamps the requested limit to the documented [1, 500] range,
// defaulting to 10 when unset (0).
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 500 {
		return 500
	}
	return limit
}

// Compile-time interface satisfaction checks.
var _ ReconAPI = (*recon.Client)(nil)

// resourceType aliases to avoid dot-importing models while keeping test helpers readable.
type notificationDetailResource = models.DomainDetailedNotificationV1
type ruleResource = models.SadomainRule
type exposedDataResource = models.APINotificationExposedDataRecordV1
