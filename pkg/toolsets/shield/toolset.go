// Package shield implements the Falcon MCP "shield" toolset: SaaS Security
// (Falcon Shield) posture checks, alerts, inventory, and audit tools. All 16
// tools map to the gofalcon saas_security sub-client, plus one query-guide
// resource. The Python ShieldModule._search_with_docs pattern is replicated as
// searchWithGuide, which surfaces the Shield query guide on error or empty
// results instead of the FQL guide used by other toolsets.
package shield

import (
	"context"
	"strings"

	"github.com/go-openapi/strfmt"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
	"github.com/crowdstrike/gofalcon/falcon/client/saas_security"
)

const (
	queryGuideURI = "falcon://shield/search/query-guide"
)

// ShieldAPI is the narrow slice of the gofalcon saas_security client this
// toolset uses. Declaring it as an interface keeps handlers unit-testable with
// a hand-written mock.
type ShieldAPI interface {
	GetSecurityChecksV3(*saas_security.GetSecurityChecksV3Params, ...saas_security.ClientOption) (*saas_security.GetSecurityChecksV3OK, error)
	GetSecurityCheckAffectedV3(*saas_security.GetSecurityCheckAffectedV3Params, ...saas_security.ClientOption) (*saas_security.GetSecurityCheckAffectedV3OK, error)
	GetMetricsV3(*saas_security.GetMetricsV3Params, ...saas_security.ClientOption) (*saas_security.GetMetricsV3OK, error)
	GetSecurityCheckComplianceV3(*saas_security.GetSecurityCheckComplianceV3Params, ...saas_security.ClientOption) (*saas_security.GetSecurityCheckComplianceV3OK, error)
	GetAlertsV3(*saas_security.GetAlertsV3Params, ...saas_security.ClientOption) (*saas_security.GetAlertsV3OK, error)
	GetActivityMonitorV3(*saas_security.GetActivityMonitorV3Params, ...saas_security.ClientOption) (*saas_security.GetActivityMonitorV3OK, error)
	GetUserInventoryV3(*saas_security.GetUserInventoryV3Params, ...saas_security.ClientOption) (*saas_security.GetUserInventoryV3OK, error)
	GetDeviceInventoryV3(*saas_security.GetDeviceInventoryV3Params, ...saas_security.ClientOption) (*saas_security.GetDeviceInventoryV3OK, error)
	GetAppInventory(*saas_security.GetAppInventoryParams, ...saas_security.ClientOption) (*saas_security.GetAppInventoryOK, error)
	GetAppInventoryUsers(*saas_security.GetAppInventoryUsersParams, ...saas_security.ClientOption) (*saas_security.GetAppInventoryUsersOK, error)
	GetAssetInventoryV3(*saas_security.GetAssetInventoryV3Params, ...saas_security.ClientOption) (*saas_security.GetAssetInventoryV3OK, error)
	GetIntegrationsV3(*saas_security.GetIntegrationsV3Params, ...saas_security.ClientOption) (*saas_security.GetIntegrationsV3OK, error)
	GetSystemUsersV3(*saas_security.GetSystemUsersV3Params, ...saas_security.ClientOption) (*saas_security.GetSystemUsersV3OK, error)
	GetSupportedSaasV3(*saas_security.GetSupportedSaasV3Params, ...saas_security.ClientOption) (*saas_security.GetSupportedSaasV3OK, error)
	GetSystemLogsV3(*saas_security.GetSystemLogsV3Params, ...saas_security.ClientOption) (*saas_security.GetSystemLogsV3OK, error)
	DismissSecurityCheckV3(*saas_security.DismissSecurityCheckV3Params, ...saas_security.ClientOption) (*saas_security.DismissSecurityCheckV3OK, error)
	DismissAffectedEntityV3(*saas_security.DismissAffectedEntityV3Params, ...saas_security.ClientOption) (*saas_security.DismissAffectedEntityV3OK, error)
}

// Toolset is the shield domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "shield" }

func (Toolset) GetDescription() string {
	return "Falcon Shield (SaaS Security): query posture checks, alerts, user/device/app inventory, data shares, integrations, and audit logs for connected SaaS applications."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			queryGuideURI,
			"falcon_shield_query_guide",
			"Query parameter guide for Falcon Shield (SaaS Security) tools.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_checks"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldChecks(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_check_affected_entities"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldCheckAffectedEntities(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_posture_metrics"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldPostureMetrics(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_check_compliance"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldCheckCompliance(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_alerts"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldAlerts(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_activity_monitor"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldActivityMonitor(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_users"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldUsers(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_devices"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldDevices(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_apps"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldApps(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_app_users"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldAppUsers(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_shield_data_shares"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchShieldDataShares(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_integrations"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldIntegrations(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_system_users"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldSystemUsers(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_supported_saas"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldSupportedSaas(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_shield_system_logs"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetShieldSystemLogs(s, fc.SaasSecurity())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_dismiss_shield_check"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDismissShieldCheck(s, fc.SaasSecurity())
			},
		},
	}
}

// --- shared helpers ---

// impactNames normalizes impact strings to title-case, matching Python's
// _normalize_impact (IMPACT_NAMES map).
var impactNames = map[string]string{
	"low":    "Low",
	"medium": "Medium",
	"high":   "High",
}

// normalizeImpact converts an optional impact string to the title-cased form
// expected by the API, returning nil when the input is nil or unrecognised.
func normalizeImpact(impact *string) *string {
	if impact == nil {
		return nil
	}
	normalized, ok := impactNames[strings.ToLower(*impact)]
	if !ok {
		return nil
	}
	return &normalized
}

// ShieldQueryGuideResponse is the shape returned when a Shield search returns
// no results or an error. It mirrors Python's _format_empty_or_error output,
// embedding the Shield query guide so the model can self-correct.
type ShieldQueryGuideResponse struct {
	Results    any    `json:"results"`
	QueryGuide string `json:"query_guide"`
	Hint       string `json:"hint"`
}

// searchWithGuide wraps a Shield API call: on error or empty results it
// surfaces the Shield query guide, replicating Python's _search_with_docs and
// _format_empty_or_error.
func searchWithGuide(operation, errMsg string, callFn func() (any, error)) (*mcp.CallToolResult, any, error) {
	guide := fql.MustGuide(queryGuideURI)

	result, err := callFn()
	if err != nil {
		e := falcon.NormalizeError(operation, errMsg, err)
		return mcpx.JSONResult(ShieldQueryGuideResponse{
			Results:    []any{e},
			QueryGuide: guide,
			Hint:       "Query error occurred. Review your parameters using the query guide.",
		})
	}
	if result == nil {
		return mcpx.JSONResult(ShieldQueryGuideResponse{
			Results:    []any{},
			QueryGuide: guide,
			Hint:       "No results matched your query. Review available parameters in the query guide.",
		})
	}
	return mcpx.JSONResult(result)
}

// parseDateTime parses an ISO-8601 / YYYY-MM-DD date string into a
// strfmt.DateTime pointer. Returns nil when s is nil or parsing fails.
func parseDateTime(s *string) *strfmt.DateTime {
	if s == nil {
		return nil
	}
	dt, err := strfmt.ParseDateTime(*s)
	if err != nil {
		return nil
	}
	return &dt
}

// normalizeLimit returns the input limit, defaulting to def when ≤0.
func normalizeLimit(limit int64, def int64) int64 {
	if limit <= 0 {
		return def
	}
	return limit
}

// --- falcon_search_shield_checks ---

type searchShieldChecksInput struct {
	ID            *string `json:"id,omitempty"             jsonschema:"Specific security check ID."`
	Status        *string `json:"status,omitempty"         jsonschema:"Filter by status: Passed, Failed, Dismissed, Pending, Can't Run, Stale."`
	Impact        *string `json:"impact,omitempty"         jsonschema:"Filter by impact: Low, Medium, High."`
	IntegrationID *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Compliance    *bool   `json:"compliance,omitempty"     jsonschema:"If true, return only checks that are defined as part of a compliance framework (SOC 2, CIS, NIST, etc.) at the catalog level."`
	CheckType     *string `json:"check_type,omitempty"     jsonschema:"Filter by type: apps, devices, users, assets, permissions, custom, Falcon Shield Security Check."`
	CheckTags     *string `json:"check_tags,omitempty"     jsonschema:"Comma-separated tag filters."`
	Limit         int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 10)."`
	Offset        *int64  `json:"offset,omitempty"         jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerSearchShieldChecks(s *mcp.Server, api ShieldAPI) {
	desc := "Search individual Falcon Shield (SaaS Security) posture checks with filtering. " +
		"Use this to find specific failing checks by status, impact, integration, or type; consult " +
		"falcon://shield/search/query-guide for valid filter values. Returns check records containing " +
		"id, name, status, impact level, affected entity count, and remediation plan."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_checks",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldChecksInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetSecurityChecksV3", "Failed to search Shield security checks", func() (any, error) {
			p := saas_security.NewGetSecurityChecksV3ParamsWithContext(ctx)
			p.ID = in.ID
			p.Status = in.Status
			p.Impact = normalizeImpact(in.Impact)
			p.IntegrationID = in.IntegrationID
			p.Compliance = in.Compliance
			p.CheckType = in.CheckType
			p.CheckTags = in.CheckTags
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetSecurityChecksV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_check_affected_entities ---

type getShieldCheckAffectedEntitiesInput struct {
	ID     string `json:"id"             jsonschema:"Security check ID. Obtain from the id field in results returned by falcon_search_shield_checks."`
	Limit  int64  `json:"limit,omitempty"  jsonschema:"Maximum number of results to return (default: 10)."`
	Offset *int64 `json:"offset,omitempty" jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerGetShieldCheckAffectedEntities(s *mcp.Server, api ShieldAPI) {
	desc := "Retrieve the specific entities (users, apps, or devices) that are violating a given Falcon Shield posture check. " +
		"Use this after falcon_search_shield_checks to drill into which entities are failing a specific check. " +
		"Returns entity objects with entity name, type, and relevant security details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_check_affected_entities",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldCheckAffectedEntitiesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetSecurityCheckAffectedV3", "Failed to get affected entities", func() (any, error) {
			p := saas_security.NewGetSecurityCheckAffectedV3ParamsWithContext(ctx)
			p.ID = in.ID
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetSecurityCheckAffectedV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_posture_metrics ---

type getShieldPostureMetricsInput struct {
	Status        *string `json:"status,omitempty"         jsonschema:"Filter by status: Passed, Failed, Dismissed, Pending, Can't Run, Stale."`
	Impact        *string `json:"impact,omitempty"         jsonschema:"Filter by impact: Low, Medium, High."`
	IntegrationID *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Compliance    *bool   `json:"compliance,omitempty"     jsonschema:"If true, return only metrics for checks defined as part of a compliance framework (SOC 2, CIS, NIST, etc.) at the catalog level."`
	CheckType     *string `json:"check_type,omitempty"     jsonschema:"Filter by type: apps, devices, users, assets, permissions, custom, Falcon Shield Security Check."`
	Limit         int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 10)."`
	Offset        *int64  `json:"offset,omitempty"         jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerGetShieldPostureMetrics(s *mcp.Server, api ShieldAPI) {
	desc := "Get aggregated Falcon Shield (SaaS Security) posture metrics for a dashboard or summary view. " +
		"Use this for a high-level overview of your SaaS security posture; for individual check records " +
		"with remediation details, use falcon_search_shield_checks instead. Returns total check counts, " +
		"overall score percentage, and a breakdown of checks by status across connected SaaS applications."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_posture_metrics",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldPostureMetricsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetMetricsV3", "Failed to get posture metrics", func() (any, error) {
			p := saas_security.NewGetMetricsV3ParamsWithContext(ctx)
			p.Status = in.Status
			p.Impact = normalizeImpact(in.Impact)
			p.IntegrationID = in.IntegrationID
			p.Compliance = in.Compliance
			p.CheckType = in.CheckType
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetMetricsV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_check_compliance ---

type getShieldCheckComplianceInput struct {
	ID string `json:"id" jsonschema:"Security check ID. Obtain from the id field in results returned by falcon_search_shield_checks."`
}

func registerGetShieldCheckCompliance(s *mcp.Server, api ShieldAPI) {
	desc := "Retrieve the compliance framework mappings for a specific Falcon Shield posture check. " +
		"Use this after falcon_search_shield_checks to understand the regulatory impact of a failing check. " +
		"Returns compliance objects identifying the framework (e.g., SOC 2, CIS, NIST, PCI DSS), " +
		"control ID, and control description that the check satisfies."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_check_compliance",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldCheckComplianceInput) (*mcp.CallToolResult, any, error) {
		return searchWithGuide("GetSecurityCheckComplianceV3", "Failed to get compliance data", func() (any, error) {
			p := saas_security.NewGetSecurityCheckComplianceV3ParamsWithContext(ctx)
			p.ID = in.ID
			resp, err := api.GetSecurityCheckComplianceV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_search_shield_alerts ---

type searchShieldAlertsInput struct {
	ID            *string `json:"id,omitempty"             jsonschema:"Specific alert ID."`
	Type          *string `json:"type,omitempty"           jsonschema:"Filter by type: configuration_drift, check_degraded, integration_failure, threat."`
	IntegrationID *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	FromDate      *string `json:"from_date,omitempty"      jsonschema:"Start date (YYYY-MM-DD)."`
	ToDate        *string `json:"to_date,omitempty"        jsonschema:"End date (YYYY-MM-DD)."`
	Ascending     *bool   `json:"ascending,omitempty"      jsonschema:"If true, return oldest alerts first. If false or omitted, return newest first."`
	Limit         int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 10)."`
	Offset        *int64  `json:"offset,omitempty"         jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
	LastID        *string `json:"last_id,omitempty"        jsonschema:"Cursor-based pagination token from the last result (alternative to offset)."`
}

func registerSearchShieldAlerts(s *mcp.Server, api ShieldAPI) {
	desc := "Search Falcon Shield (SaaS Security) alerts for monitored SaaS applications. " +
		"Use this to find configuration drift, degraded checks, integration failures, or active threats; " +
		"use last_id from the last result for cursor-based pagination or offset for offset-based pagination. " +
		"Returns alert objects containing id, type, integration details, timestamp, and severity."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_alerts",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldAlertsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetAlertsV3", "Failed to search Shield alerts", func() (any, error) {
			p := saas_security.NewGetAlertsV3ParamsWithContext(ctx)
			p.ID = in.ID
			p.Type = in.Type
			p.IntegrationID = in.IntegrationID
			p.FromDate = parseDateTime(in.FromDate)
			p.ToDate = parseDateTime(in.ToDate)
			p.Ascending = in.Ascending
			p.Limit = &limit
			p.Offset = in.Offset
			p.LastID = in.LastID
			resp, err := api.GetAlertsV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_activity_monitor ---

type getShieldActivityMonitorInput struct {
	IntegrationID *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Actor         *string `json:"actor,omitempty"          jsonschema:"Filter by the identity that performed the activity (e.g., user email, service account name). This is not a threat actor name."`
	Category      *string `json:"category,omitempty"       jsonschema:"Comma-separated activity categories: Events, Threat, IoC."`
	Projection    *string `json:"projection,omitempty"     jsonschema:"Comma-separated list of fields to include in each event. Valid fields: timestamp_utc, severity, datetime, event_name, actor, integration_id, integration_name, type, category, created_by, ip, asn_name, country, browser, os, target, object_type, object, status. Omit for default fields."`
	FromDate      *string `json:"from_date,omitempty"      jsonschema:"Start datetime (ISO 8601)."`
	ToDate        *string `json:"to_date,omitempty"        jsonschema:"End datetime (ISO 8601)."`
	Limit         int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 100, max: 10000)."`
	Skip          *int64  `json:"skip,omitempty"           jsonschema:"Pagination offset. Use meta.pagination.offset from the previous response for subsequent pages."`
}

func registerGetShieldActivityMonitor(s *mcp.Server, api ShieldAPI) {
	desc := "Get events from the Falcon Shield (SaaS Security) activity monitor; data is retained for 180 days. " +
		"Use this to investigate user activity, threats, or IoC events across connected SaaS platforms; " +
		"when filtering by integration_id, category, or actor, the date range must be within 24 hours. " +
		"Returns activity event objects including timestamp, event name, actor identity, integration, " +
		"category, and location details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_activity_monitor",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldActivityMonitorInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100)
		return searchWithGuide("GetActivityMonitorV3", "Failed to get activity monitor events", func() (any, error) {
			p := saas_security.NewGetActivityMonitorV3ParamsWithContext(ctx)
			p.IntegrationID = in.IntegrationID
			p.Actor = in.Actor
			p.Category = in.Category
			p.Projection = in.Projection
			p.FromDate = parseDateTime(in.FromDate)
			p.ToDate = parseDateTime(in.ToDate)
			p.Limit = &limit
			p.Skip = in.Skip
			resp, err := api.GetActivityMonitorV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_search_shield_users ---

type searchShieldUsersInput struct {
	IntegrationID  *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Email          *string `json:"email,omitempty"          jsonschema:"Filter results to users matching this email address."`
	PrivilegedOnly *bool   `json:"privileged_only,omitempty" jsonschema:"If true, return only users with privileged or administrative roles."`
	Limit          int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 10)."`
	Offset         *int64  `json:"offset,omitempty"         jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerSearchShieldUsers(s *mcp.Server, api ShieldAPI) {
	desc := "List end-users discovered across Falcon Shield (SaaS Security) connected SaaS applications. " +
		"Use this to audit user access across your SaaS estate or identify over-privileged or stale accounts; " +
		"for Shield platform administrators instead of SaaS app end-users, use falcon_get_shield_system_users. " +
		"Returns user objects containing email, display name, connected application details, privilege status, " +
		"and exposure metrics."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_users",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldUsersInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetUserInventoryV3", "Failed to search Shield users", func() (any, error) {
			p := saas_security.NewGetUserInventoryV3ParamsWithContext(ctx)
			p.IntegrationID = in.IntegrationID
			p.Email = in.Email
			p.PrivilegedOnly = in.PrivilegedOnly
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetUserInventoryV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_search_shield_devices ---

type searchShieldDevicesInput struct {
	IntegrationID       *string `json:"integration_id,omitempty"        jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Email               *string `json:"email,omitempty"                 jsonschema:"Filter by user email associated with the device."`
	PrivilegedOnly      *bool   `json:"privileged_only,omitempty"       jsonschema:"If true, return only devices belonging to users with privileged roles."`
	UnassociatedDevices *bool   `json:"unassociated_devices,omitempty"  jsonschema:"If true, include devices not associated with a known user."`
	Limit               int64   `json:"limit,omitempty"                 jsonschema:"Maximum number of results to return (default: 10)."`
	Offset              *int64  `json:"offset,omitempty"                jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerSearchShieldDevices(s *mcp.Server, api ShieldAPI) {
	desc := "List devices registered to users in Falcon Shield (SaaS Security) connected SaaS applications. " +
		"Use this to identify unmanaged or unassociated devices in your SaaS estate; note that this returns " +
		"devices from SaaS provider records, not Falcon sensor inventory — use falcon_search_hosts for that. " +
		"Returns device objects containing device name, owner email, compliance posture, and management status."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_devices",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldDevicesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetDeviceInventoryV3", "Failed to search Shield devices", func() (any, error) {
			p := saas_security.NewGetDeviceInventoryV3ParamsWithContext(ctx)
			p.IntegrationID = in.IntegrationID
			p.Email = in.Email
			p.PrivilegedOnly = in.PrivilegedOnly
			p.UnassociatedDevices = in.UnassociatedDevices
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetDeviceInventoryV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_search_shield_apps ---

type searchShieldAppsInput struct {
	Type          *string `json:"type,omitempty"           jsonschema:"App type: oauth, sign_in, api_token, browser_extension, etc."`
	Status        *string `json:"status,omitempty"         jsonschema:"Status: approved, in review, rejected, unclassified."`
	AccessLevel   *string `json:"access_level,omitempty"   jsonschema:"Access level: high, medium, low, none."`
	IntegrationID *string `json:"integration_id,omitempty" jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	Scopes        *string `json:"scopes,omitempty"         jsonschema:"Comma-separated OAuth scope filter."`
	Users         *string `json:"users,omitempty"          jsonschema:"Filter by user association. Format: 'is equal <email>' for exact match, or 'contains <value>' for partial match. Example: 'is equal user@example.com'."`
	Groups        *string `json:"groups,omitempty"         jsonschema:"Group filter."`
	LastActivity  *string `json:"last_activity,omitempty"  jsonschema:"Filter by time since the app was last active. Format: 'was N' (active within N days) or 'was not N' (inactive for more than N days). Example: 'was not 90'."`
	Limit         int64   `json:"limit,omitempty"          jsonschema:"Maximum number of results to return (default: 10)."`
	Offset        *int64  `json:"offset,omitempty"         jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerSearchShieldApps(s *mcp.Server, api ShieldAPI) {
	desc := "List third-party applications (OAuth apps, API tokens, browser extensions, service principals) " +
		"with access to Falcon Shield (SaaS Security) monitored platforms. " +
		"Use this to audit app access across your SaaS estate; use the item_id from results with " +
		"falcon_get_shield_app_users to see who authorized a specific app. Returns app objects containing " +
		"item_id, name, type, status, access_level, granted scopes, and user count."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_apps",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldAppsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetAppInventory", "Failed to search Shield apps", func() (any, error) {
			p := saas_security.NewGetAppInventoryParamsWithContext(ctx)
			p.Type = in.Type
			p.Status = in.Status
			p.AccessLevel = in.AccessLevel
			p.IntegrationID = in.IntegrationID
			p.Scopes = in.Scopes
			p.Users = in.Users
			p.Groups = in.Groups
			p.LastActivity = in.LastActivity
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetAppInventory(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_app_users ---

type getShieldAppUsersInput struct {
	ItemID string `json:"item_id" jsonschema:"Composite app identifier in the format integration_id|||app_id. Obtain from the item_id field in results returned by falcon_search_shield_apps."`
}

func registerGetShieldAppUsers(s *mcp.Server, api ShieldAPI) {
	desc := "Retrieve the users who have authorized or are associated with a specific third-party app in Falcon Shield. " +
		"Use this after falcon_search_shield_apps to drill into a specific app's user population. " +
		"Returns user objects including email, display name, and granted permissions."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_app_users",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldAppUsersInput) (*mcp.CallToolResult, any, error) {
		return searchWithGuide("GetAppInventoryUsers", "Failed to get app users", func() (any, error) {
			p := saas_security.NewGetAppInventoryUsersParamsWithContext(ctx)
			p.ItemID = in.ItemID
			resp, err := api.GetAppInventoryUsers(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_search_shield_data_shares ---

type searchShieldDataSharesInput struct {
	IntegrationID        *string `json:"integration_id,omitempty"          jsonschema:"Comma-separated IDs of SaaS integrations to filter by. Use falcon_get_shield_integrations to retrieve available integration IDs."`
	ResourceType         *string `json:"resource_type,omitempty"           jsonschema:"File type filter (e.g., PDF, XLSX)."`
	AccessLevel          *string `json:"access_level,omitempty"            jsonschema:"Sharing access level filter (comma-separated). Values: public_link, external_user, org_wide, internal."`
	ResourceName         *string `json:"resource_name,omitempty"           jsonschema:"Filter to resources whose name contains this value."`
	ResourceOwner        *string `json:"resource_owner,omitempty"          jsonschema:"Filter to resources whose owner name or email contains this value."`
	ResourceOwnerEnabled *bool   `json:"resource_owner_enabled,omitempty"  jsonschema:"If true, return only resources with an active owner account. If false, only disabled owner accounts."`
	PasswordProtected    *bool   `json:"password_protected,omitempty"      jsonschema:"If true, return only password-protected resources. If false, only unprotected resources."`
	LastAccessed         *string `json:"last_accessed,omitempty"           jsonschema:"Filter by time since the resource was last accessed. Format: 'was N' (within N days) or 'was not N' (not accessed in more than N days). Example: 'was not 30'."`
	LastModified         *string `json:"last_modified,omitempty"           jsonschema:"Filter by time since the resource was last modified. Format: 'was N' (within N days) or 'was not N' (not modified in more than N days). Example: 'was not 30'."`
	UnmanagedDomain      *string `json:"unmanaged_domain,omitempty"        jsonschema:"Filter to resources shared with external (non-organization) domains. Comma-separated domain names (e.g., 'gmail.com,yahoo.com')."`
	Limit                int64   `json:"limit,omitempty"                   jsonschema:"Maximum number of results to return (default: 10)."`
	Offset               *int64  `json:"offset,omitempty"                  jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
}

func registerSearchShieldDataShares(s *mcp.Server, api ShieldAPI) {
	desc := "List files and resources shared externally across Falcon Shield (SaaS Security) monitored applications. " +
		"Use this to identify overshared or externally exposed files such as Google Drive documents shared " +
		"outside the organization. Returns resource objects containing resource name, type, owner, sharing " +
		"access level, password protection status, and last access/modification timestamps."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_shield_data_shares",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchShieldDataSharesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10)
		return searchWithGuide("GetAssetInventoryV3", "Failed to search Shield data shares", func() (any, error) {
			p := saas_security.NewGetAssetInventoryV3ParamsWithContext(ctx)
			p.IntegrationID = in.IntegrationID
			p.ResourceType = in.ResourceType
			p.AccessLevel = in.AccessLevel
			p.ResourceName = in.ResourceName
			p.ResourceOwner = in.ResourceOwner
			p.ResourceOwnerEnabled = in.ResourceOwnerEnabled
			p.PasswordProtected = in.PasswordProtected
			p.LastAccessed = in.LastAccessed
			p.LastModified = in.LastModified
			p.UnmanagedDomain = in.UnmanagedDomain
			p.Limit = &limit
			p.Offset = in.Offset
			resp, err := api.GetAssetInventoryV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_integrations ---

type getShieldIntegrationsInput struct {
	SaasID *string `json:"saas_id,omitempty" jsonschema:"Comma-separated SaaS platform IDs to filter by."`
}

func registerGetShieldIntegrations(s *mcp.Server, api ShieldAPI) {
	desc := "List all SaaS integrations connected to Falcon Shield and their current connection status. " +
		"Call this first when starting a Shield investigation to discover available integration IDs, " +
		"which are required as input to most other Shield tools. Returns integration objects containing " +
		"integration_id, SaaS platform name, connection health, and last sync time."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_integrations",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldIntegrationsInput) (*mcp.CallToolResult, any, error) {
		return searchWithGuide("GetIntegrationsV3", "Failed to get Shield integrations", func() (any, error) {
			p := saas_security.NewGetIntegrationsV3ParamsWithContext(ctx)
			p.SaasID = in.SaasID
			resp, err := api.GetIntegrationsV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_system_users ---

type getShieldSystemUsersInput struct{}

func registerGetShieldSystemUsers(s *mcp.Server, api ShieldAPI) {
	desc := "List Falcon Shield (SaaS Security) platform administrators. " +
		"Use this to audit console-level admin accounts; for end-users of connected SaaS applications, " +
		"use falcon_search_shield_users instead. Returns system-level user objects including email, role, " +
		"and MFA status."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_system_users",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, _ getShieldSystemUsersInput) (*mcp.CallToolResult, any, error) {
		return searchWithGuide("GetSystemUsersV3", "Failed to get Shield system users", func() (any, error) {
			p := saas_security.NewGetSystemUsersV3ParamsWithContext(ctx)
			resp, err := api.GetSystemUsersV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_supported_saas ---

type getShieldSupportedSaasInput struct{}

func registerGetShieldSupportedSaas(s *mcp.Server, api ShieldAPI) {
	desc := "List SaaS platforms supported by Falcon Shield for integration. " +
		"Use this to discover which SaaS applications can be connected before setting up new integrations. " +
		"Returns supported SaaS platform objects including platform name and ID."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_supported_saas",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, _ getShieldSupportedSaasInput) (*mcp.CallToolResult, any, error) {
		return searchWithGuide("GetSupportedSaasV3", "Failed to get supported SaaS platforms", func() (any, error) {
			p := saas_security.NewGetSupportedSaasV3ParamsWithContext(ctx)
			resp, err := api.GetSupportedSaasV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_get_shield_system_logs ---

type getShieldSystemLogsInput struct {
	FromDate   *string `json:"from_date,omitempty"   jsonschema:"Start date (YYYY-MM-DD)."`
	ToDate     *string `json:"to_date,omitempty"     jsonschema:"End date (YYYY-MM-DD)."`
	Limit      int64   `json:"limit,omitempty"       jsonschema:"Maximum number of results to return (default: 100)."`
	Offset     *int64  `json:"offset,omitempty"      jsonschema:"Zero-based offset for pagination. Omit or set to 0 for the first page. Increment by limit for subsequent pages."`
	TotalCount *bool   `json:"total_count,omitempty" jsonschema:"If true, include total count of matching logs in the response metadata."`
}

func registerGetShieldSystemLogs(s *mcp.Server, api ShieldAPI) {
	desc := "Retrieve Falcon Shield (SaaS Security) system audit logs; data is retained for 90 days. " +
		"Use date range filters to narrow results, covering events such as integration creates, check " +
		"dismissals, and data syncs. Returns log objects containing timestamp, event type, actor, and details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_shield_system_logs",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getShieldSystemLogsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100)
		return searchWithGuide("GetSystemLogsV3", "Failed to get Shield system logs", func() (any, error) {
			p := saas_security.NewGetSystemLogsV3ParamsWithContext(ctx)
			p.FromDate = parseDateTime(in.FromDate)
			p.ToDate = parseDateTime(in.ToDate)
			p.Limit = &limit
			p.Offset = in.Offset
			p.TotalCount = in.TotalCount
			resp, err := api.GetSystemLogsV3(p)
			if err != nil {
				return nil, err
			}
			resources := resp.GetPayload().Resources
			if len(resources) == 0 {
				return nil, nil
			}
			return resources, nil
		})
	})
}

// --- falcon_dismiss_shield_check ---

type dismissShieldCheckInput struct {
	ID       string  `json:"id"                jsonschema:"Security check ID. Obtain from the id field in results returned by falcon_search_shield_checks."`
	Reason   string  `json:"reason"            jsonschema:"Required explanation for the dismissal. This is written to the audit log and visible to other administrators."`
	Entities *string `json:"entities,omitempty" jsonschema:"Comma-separated entity names to dismiss. If omitted, dismisses the entire check for all entities. If provided, only the specified entities are dismissed and the check remains active for others."`
}

func registerDismissShieldCheck(s *mcp.Server, api ShieldAPI) {
	desc := "Dismiss a Falcon Shield (SaaS Security) posture check to suppress it from the failed checks list. " +
		"Use this only when a check is intentionally accepted as a known risk; omit entities to dismiss " +
		"the entire check for all entities, or provide specific entity names to dismiss only those. " +
		"This action is permanent and cannot be undone from the API — the dismissal reason is recorded " +
		"in audit logs."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_dismiss_shield_check",
		Description: desc,
		Annotations: &mcp.ToolAnnotations{
			ReadOnlyHint:    false,
			DestructiveHint: mcpx.BoolPtr(true),
			IdempotentHint:  true,
			OpenWorldHint:   mcpx.BoolPtr(true),
		},
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in dismissShieldCheckInput) (*mcp.CallToolResult, any, error) {
		if in.Entities != nil {
			// Dismiss specific entities only.
			p := saas_security.NewDismissAffectedEntityV3ParamsWithContext(ctx)
			p.ID = in.ID
			p.Body = saas_security.DismissAffectedEntityV3Body{
				Reason:   in.Reason,
				Entities: *in.Entities,
			}
			resp, err := api.DismissAffectedEntityV3(p)
			if err != nil {
				e := falcon.NormalizeError("DismissAffectedEntityV3", "Failed to dismiss Shield check", err)
				return mcpx.JSONResult([]any{e})
			}
			return mcpx.JSONResult(resp.GetPayload().Resources)
		}

		// Dismiss the entire check.
		p := saas_security.NewDismissSecurityCheckV3ParamsWithContext(ctx)
		p.ID = in.ID
		p.Body = saas_security.DismissSecurityCheckV3Body{Reason: in.Reason}
		resp, err := api.DismissSecurityCheckV3(p)
		if err != nil {
			e := falcon.NormalizeError("DismissSecurityCheckV3", "Failed to dismiss Shield check", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}
