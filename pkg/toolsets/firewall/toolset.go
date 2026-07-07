// Package firewall implements the Falcon MCP "firewall" toolset: searching
// firewall rules, rule groups, and policy rules, plus creating and deleting
// rule groups via the Firewall Management service collection.
package firewall

import (
	"context"

	fwclient "github.com/crowdstrike/gofalcon/falcon/client/firewall_management"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://firewall/rules/fql-guide"
)

// FirewallAPI is the narrow slice of the gofalcon firewall_management client
// this toolset uses. Declaring it here keeps handlers unit-testable with a
// hand-written mock.
type FirewallAPI interface {
	QueryRules(*fwclient.QueryRulesParams, ...fwclient.ClientOption) (*fwclient.QueryRulesOK, error)
	GetRules(*fwclient.GetRulesParams, ...fwclient.ClientOption) (*fwclient.GetRulesOK, error)
	QueryRuleGroups(*fwclient.QueryRuleGroupsParams, ...fwclient.ClientOption) (*fwclient.QueryRuleGroupsOK, error)
	GetRuleGroups(*fwclient.GetRuleGroupsParams, ...fwclient.ClientOption) (*fwclient.GetRuleGroupsOK, error)
	QueryPolicyRules(*fwclient.QueryPolicyRulesParams, ...fwclient.ClientOption) (*fwclient.QueryPolicyRulesOK, error)
	CreateRuleGroup(*fwclient.CreateRuleGroupParams, ...fwclient.ClientOption) (*fwclient.CreateRuleGroupCreated, error)
	DeleteRuleGroups(*fwclient.DeleteRuleGroupsParams, ...fwclient.ClientOption) (*fwclient.DeleteRuleGroupsOK, error)
}

// Toolset is the firewall domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "firewall" }

func (Toolset) GetDescription() string {
	return "Search and manage CrowdStrike Falcon Firewall Management rules, rule groups, and policies."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_firewall_rules_fql_guide",
			"Contains the guide for the `filter` param of firewall search tools.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_firewall_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchFirewallRules(s, fc.FirewallManagement())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_firewall_rule_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchFirewallRuleGroups(s, fc.FirewallManagement())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_firewall_policy_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchFirewallPolicyRules(s, fc.FirewallManagement())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_firewall_rule_group"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateFirewallRuleGroup(s, fc.FirewallManagement())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_firewall_rule_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteFirewallRuleGroups(s, fc.FirewallManagement())
			},
		},
	}
}

// --- falcon_search_firewall_rules ---

type searchFirewallRulesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://firewall/rules/fql-guide for syntax. Examples: enabled:true, platform:'windows'+name:'Block*'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of rule IDs to return [1-5000]. Default 10."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort firewall rules using FQL syntax. Examples: name.asc, modified_on.desc, platform|asc."`
	Q      *string `json:"q,omitempty" jsonschema:"Free-text query string across rule fields."`
	After  *string `json:"after,omitempty" jsonschema:"Pagination token from a previous query response."`
}

func registerSearchFirewallRules(s *mcp.Server, api FirewallAPI) {
	desc := "Search firewall rules and return full rule details. Use this to find firewall rules " +
		"by name, platform, or enabled state. Consult falcon://firewall/rules/fql-guide before " +
		"constructing filter expressions. Returns complete rule objects including conditions and actions."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_firewall_rules",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchFirewallRulesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching rule IDs.
		qp := fwclient.NewQueryRulesParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q
		qp.After = in.After

		queryResp, err := api.QueryRules(qp)
		if err != nil {
			return firewallSearchErr(ctx, "query_rules", "Failed to search firewall rules", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full rule details for the matched IDs.
		rules, err := fetchRules(ctx, api, ids)
		if err != nil {
			e := falcon.NormalizeError("get_rules", "Failed to get firewall rule details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(rules)
	})
}

// --- falcon_search_firewall_rule_groups ---

type searchFirewallRuleGroupsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://firewall/rules/fql-guide for syntax. Examples: enabled:true, platform:'windows'+name:'Default*'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of rule group IDs to return [1-5000]. Default 10."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression in FQL syntax (e.g., modified_on.desc)."`
	Q      *string `json:"q,omitempty" jsonschema:"Free-text query string across rule group fields."`
	After  *string `json:"after,omitempty" jsonschema:"Pagination token from a previous query response."`
}

func registerSearchFirewallRuleGroups(s *mcp.Server, api FirewallAPI) {
	desc := "Search firewall rule groups and return full rule group details. Use this to find rule " +
		"groups by name, platform, or enabled state. Consult falcon://firewall/rules/fql-guide before " +
		"constructing filter expressions. Returns rule group objects including their contained rules."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_firewall_rule_groups",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchFirewallRuleGroupsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching rule group IDs.
		qp := fwclient.NewQueryRuleGroupsParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q
		qp.After = in.After

		queryResp, err := api.QueryRuleGroups(qp)
		if err != nil {
			return firewallSearchErr(ctx, "query_rule_groups", "Failed to search firewall rule groups", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full rule group details for the matched IDs.
		groups, err := fetchRuleGroups(ctx, api, ids)
		if err != nil {
			e := falcon.NormalizeError("get_rule_groups", "Failed to get firewall rule group details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(groups)
	})
}

// --- falcon_search_firewall_policy_rules ---

type searchFirewallPolicyRulesInput struct {
	PolicyID string  `json:"policy_id" jsonschema:"Policy container ID to query rules within."`
	Filter   *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://firewall/rules/fql-guide for syntax."`
	Limit    int64   `json:"limit,omitempty" jsonschema:"Maximum number of policy rule IDs to return [1-5000]. Default 10."`
	Offset   *string `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort     *string `json:"sort,omitempty" jsonschema:"Sort expression in FQL syntax (e.g., modified_on.desc)."`
	Q        *string `json:"q,omitempty" jsonschema:"Free-text query string across policy rule fields."`
}

func registerSearchFirewallPolicyRules(s *mcp.Server, api FirewallAPI) {
	desc := "Search firewall rules within a specific policy container. Use this when you need rules " +
		"scoped to a particular policy. Consult falcon://firewall/rules/fql-guide before constructing " +
		"filter expressions. Returns full rule details for the specified policy."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_firewall_policy_rules",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchFirewallPolicyRulesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching policy rule IDs.
		qp := fwclient.NewQueryPolicyRulesParamsWithContext(ctx)
		qp.ID = &in.PolicyID
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q

		queryResp, err := api.QueryPolicyRules(qp)
		if err != nil {
			return firewallSearchErr(ctx, "query_policy_rules", "Failed to search firewall policy rules", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full rule details for the matched IDs.
		rules, err := fetchRules(ctx, api, ids)
		if err != nil {
			e := falcon.NormalizeError("get_rules", "Failed to get firewall policy rule details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(rules)
	})
}

// --- falcon_create_firewall_rule_group ---

type createFirewallRuleGroupInput struct {
	Name        *string          `json:"name,omitempty" jsonschema:"Rule group name. Required when body is not provided."`
	Platform    *string          `json:"platform,omitempty" jsonschema:"Target platform (e.g. windows, mac, linux). Required when body is not provided."`
	Rules       []map[string]any `json:"rules,omitempty" jsonschema:"Rule definitions. Required when body is not provided and clone_id is not set."`
	Description *string          `json:"description,omitempty" jsonschema:"Rule group description."`
	Enabled     *bool            `json:"enabled,omitempty" jsonschema:"Whether this rule group is enabled. Default true."`
	CloneID     *string          `json:"clone_id,omitempty" jsonschema:"Rule group ID to clone from."`
	Library     *string          `json:"library,omitempty" jsonschema:"Set to true when cloning from the CrowdStrike rule group library."`
	Comment     *string          `json:"comment,omitempty" jsonschema:"Audit log comment for this action."`
	Body        map[string]any   `json:"body,omitempty" jsonschema:"Full request body override. If provided, convenience fields are ignored."`
}

func registerCreateFirewallRuleGroup(s *mcp.Server, api FirewallAPI) {
	desc := "Create a firewall rule group. Provide a name, platform, and either rules or a clone_id. " +
		"Returns a list containing the created rule group object."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_firewall_rule_group",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createFirewallRuleGroupInput) (*mcp.CallToolResult, any, error) {
		var body *models.FwmgrAPIRuleGroupCreateRequestV1

		if in.Body != nil {
			// Raw body override: marshal/unmarshal through JSON to coerce into model.
			body = buildRuleGroupBodyFromMap(in.Body)
		} else {
			if in.Name == nil || in.Platform == nil {
				e := falcon.NormalizeError("create_rule_group",
					"`name` and `platform` are required when `body` is not provided", nil)
				return mcpx.JSONResult([]any{e})
			}
			if len(in.Rules) == 0 && in.CloneID == nil {
				e := falcon.NormalizeError("create_rule_group",
					"Provide `rules` or `clone_id` when creating a firewall rule group", nil)
				return mcpx.JSONResult([]any{e})
			}

			enabled := true
			if in.Enabled != nil {
				enabled = *in.Enabled
			}
			description := ""
			if in.Description != nil {
				description = *in.Description
			}
			body = &models.FwmgrAPIRuleGroupCreateRequestV1{
				Name:        in.Name,
				Platform:    in.Platform,
				Enabled:     &enabled,
				Description: &description,
				Rules:       []*models.FwmgrAPIRuleCreateRequestV1{},
			}
		}

		cp := fwclient.NewCreateRuleGroupParamsWithContext(ctx)
		cp.Body = body
		cp.CloneID = in.CloneID
		cp.Comment = in.Comment
		cp.Library = in.Library

		resp, err := api.CreateRuleGroup(cp)
		if err != nil {
			e := falcon.NormalizeError("create_rule_group", "Failed to create firewall rule group", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_firewall_rule_groups ---

type deleteFirewallRuleGroupsInput struct {
	IDs     []string `json:"ids" jsonschema:"Rule group IDs to delete."`
	Comment *string  `json:"comment,omitempty" jsonschema:"Audit log comment for this action."`
}

func registerDeleteFirewallRuleGroups(s *mcp.Server, api FirewallAPI) {
	desc := "Delete firewall rule groups by ID. Permanently removes the specified rule groups and " +
		"all rules within them. Returns a success summary with deleted rule group IDs."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_firewall_rule_groups",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteFirewallRuleGroupsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.NormalizeError("delete_rule_groups",
				"`ids` is required when deleting firewall rule groups", nil)
			return mcpx.JSONResult([]any{e})
		}

		dp := fwclient.NewDeleteRuleGroupsParamsWithContext(ctx)
		dp.Ids = in.IDs
		dp.Comment = in.Comment

		resp, err := api.DeleteRuleGroups(dp)
		if err != nil {
			e := falcon.NormalizeError("delete_rule_groups", "Failed to delete firewall rule groups", err)
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

func fetchRules(ctx context.Context, api FirewallAPI, ids []string) ([]*models.FwmgrFirewallRuleV1, error) {
	gp := fwclient.NewGetRulesParamsWithContext(ctx)
	gp.Ids = ids
	resp, err := api.GetRules(gp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

func fetchRuleGroups(ctx context.Context, api FirewallAPI, ids []string) ([]*models.FwmgrAPIRuleGroupV1, error) {
	gp := fwclient.NewGetRuleGroupsParamsWithContext(ctx)
	gp.Ids = ids
	resp, err := api.GetRuleGroups(gp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

// firewallSearchErr normalizes a search error, surfacing the FQL guide on 400
// (filter syntax) errors and a plain normalized error otherwise.
func firewallSearchErr(_ context.Context, operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// buildRuleGroupBodyFromMap converts a raw map body override into the API model
// by mapping the common string and bool fields.
func buildRuleGroupBodyFromMap(m map[string]any) *models.FwmgrAPIRuleGroupCreateRequestV1 {
	body := &models.FwmgrAPIRuleGroupCreateRequestV1{
		Rules: []*models.FwmgrAPIRuleCreateRequestV1{},
	}
	if v, ok := m["name"].(string); ok {
		body.Name = &v
	}
	if v, ok := m["platform"].(string); ok {
		body.Platform = &v
	}
	if v, ok := m["description"].(string); ok {
		body.Description = &v
	}
	if v, ok := m["enabled"].(bool); ok {
		body.Enabled = &v
	}
	return body
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
