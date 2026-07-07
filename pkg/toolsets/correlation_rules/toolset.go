// Package correlation_rules implements the Falcon MCP "correlation_rules"
// toolset: searching, creating, updating, and deleting NG-SIEM Correlation
// Rules. Search uses the combined endpoint (CombinedRulesGetV2) which returns
// full rule objects in a single call; create/update/delete use the entities
// endpoints.
package correlation_rules

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/correlation_rules"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://correlation-rules/search/fql-guide"
)

// CorrelationRulesAPI is the narrow slice of the gofalcon correlation_rules
// client this toolset uses. Declaring it here keeps handlers unit-testable
// with a hand-written mock.
type CorrelationRulesAPI interface {
	CombinedRulesGetV2(*correlation_rules.CombinedRulesGetV2Params, ...correlation_rules.ClientOption) (*correlation_rules.CombinedRulesGetV2OK, error)
	EntitiesRulesPostV1(*correlation_rules.EntitiesRulesPostV1Params, ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesPostV1OK, error)
	EntitiesRulesPatchV1(*correlation_rules.EntitiesRulesPatchV1Params, ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesPatchV1OK, error)
	EntitiesRulesDeleteV1(*correlation_rules.EntitiesRulesDeleteV1Params, ...correlation_rules.ClientOption) (*correlation_rules.EntitiesRulesDeleteV1OK, error)
}

// Toolset is the correlation_rules domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "correlation_rules" }

func (Toolset) GetDescription() string {
	return "Manage CrowdStrike Falcon NG-SIEM Correlation Rules."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_correlation_rules_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_correlation_rules` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_correlation_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchCorrelationRules(s, fc.CorrelationRules())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_correlation_rule"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateCorrelationRule(s, fc.CorrelationRules())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_correlation_rule"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateCorrelationRule(s, fc.CorrelationRules())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_correlation_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteCorrelationRules(s, fc.CorrelationRules())
			},
		},
	}
}

// --- falcon_search_correlation_rules ---

type searchCorrelationRulesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://correlation-rules/search/fql-guide for syntax. Examples: status:'active'+severity:>50, mitre_attack.tactic_id:'TA0001'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of rules to return [1-500]. Default 20."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort rules using FQL sort syntax. Example: 'last_updated_on.desc'."`
}

func registerSearchCorrelationRules(s *mcp.Server, api CorrelationRulesAPI) {
	desc := "Search NG-SIEM Correlation Rules and return full rule details. " +
		"Use this to find detection rules by name, status, severity, or MITRE tactic/technique. " +
		"Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions. " +
		"Returns full rule objects; use the `rule_id` field when passing results to update or " +
		"delete tools. Filter with state:'published' to get one result per rule."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_correlation_rules",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchCorrelationRulesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		p := correlation_rules.NewCombinedRulesGetV2ParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort

		resp, err := api.CombinedRulesGetV2(p)
		if err != nil {
			normalized := falcon.NormalizeError("combined_rules_get_v2", "Failed to search Correlation Rules", err)
			if falcon.IsFQLError(normalized.StatusCode) {
				return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, in.Filter, fql.MustGuide(fqlGuideURI)))
			}
			return mcpx.JSONResult([]any{normalized})
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_create_correlation_rule ---

// mitreAttackInput is the JSON representation of a single MITRE ATT&CK mapping
// supplied by the caller. It is mapped to the gofalcon model before sending.
type mitreAttackInput struct {
	TacticID    string `json:"tactic_id"`
	TechniqueID string `json:"technique_id,omitempty"`
}

type createCorrelationRuleInput struct {
	CustomerID    string             `json:"customer_id" jsonschema:"CID of the tenant to create the rule in."`
	Name          string             `json:"name" jsonschema:"Name for the new detection rule."`
	SearchFilter  string             `json:"search_filter" jsonschema:"CQL query that defines the detection logic evaluated against NG-SIEM events. Example: '#event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*'."`
	Severity      int32              `json:"severity" jsonschema:"Severity score for alerts generated by this rule. Must be one of: 10, 30, 50, 70, 90."`
	SearchOutcome string             `json:"search_outcome,omitempty" jsonschema:"Outcome type for rule matches. Default 'detection'. Examples: detection, case."`
	Lookback      string             `json:"lookback,omitempty" jsonschema:"Lookback window for event aggregation. Default '1h0m'. Examples: 1h0m, 24h0m, 7d0h0m."`
	Schedule      string             `json:"schedule,omitempty" jsonschema:"Schedule definition for rule evaluation (minimum: @every 0h5m). Default '@every 1h0m'. Examples: @every 1h0m, @every 0h5m, @every 24h0m."`
	Status        string             `json:"status,omitempty" jsonschema:"Initial rule status. Default 'active'. Examples: active, inactive."`
	TriggerMode   string             `json:"trigger_mode,omitempty" jsonschema:"How alerts are triggered per evaluation window. Default 'summary'. Examples: summary, verbose."`
	UseIngestTime bool               `json:"use_ingest_time,omitempty" jsonschema:"Use event ingest time instead of event timestamp for the lookback window."`
	Description   *string            `json:"description,omitempty" jsonschema:"Optional description explaining what the rule detects and why."`
	MitreAttack   []mitreAttackInput `json:"mitre_attack,omitempty" jsonschema:"MITRE ATT&CK mapping as a list of objects with tactic_id and technique_id. Example: [{\"tactic_id\": \"TA0002\", \"technique_id\": \"T1059\"}]."`
	Comment       *string            `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule is being created."`
}

func registerCreateCorrelationRule(s *mcp.Server, api CorrelationRulesAPI) {
	desc := "Create a new NG-SIEM Correlation Rule. " +
		"Wraps a user-provided CQL query as a scheduled detection rule. The caller must " +
		"supply the CQL query — use falcon_search_ngsiem to test queries before creating rules. " +
		"Returns the created rule record on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_correlation_rule",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createCorrelationRuleInput) (*mcp.CallToolResult, any, error) {
		outcome := in.SearchOutcome
		if outcome == "" {
			outcome = "detection"
		}
		lookback := in.Lookback
		if lookback == "" {
			lookback = "1h0m"
		}
		triggerMode := in.TriggerMode
		if triggerMode == "" {
			triggerMode = "summary"
		}
		status := in.Status
		if status == "" {
			status = "active"
		}
		schedule := in.Schedule
		if schedule == "" {
			schedule = "@every 1h0m"
		}
		// execution_mode is required by the model; use "scheduled" as the default.
		executionMode := "scheduled"
		templateID := ""

		body := &models.CorrelationrulesapiRuleCreateRequestV1{
			CustomerID: &in.CustomerID,
			Name:       &in.Name,
			Severity:   &in.Severity,
			Status:     &status,
			TemplateID: &templateID,
			Search: &models.CorrelationrulesapiRuleSearchV1{
				Filter:        &in.SearchFilter,
				Outcome:       &outcome,
				Lookback:      &lookback,
				TriggerMode:   &triggerMode,
				ExecutionMode: &executionMode,
				UseIngestTime: in.UseIngestTime,
			},
			Operation: &models.CorrelationrulesapiCreateRuleOperationV1{
				Schedule: &models.CorrelationrulesapiRuleScheduleV1{
					Definition: &schedule,
				},
			},
		}

		if in.Description != nil {
			body.Description = *in.Description
		}
		if in.Comment != nil {
			body.Comment = *in.Comment
		}
		if len(in.MitreAttack) > 0 {
			body.MitreAttack = toMitreAttackModels(in.MitreAttack)
		}

		p := correlation_rules.NewEntitiesRulesPostV1ParamsWithContext(ctx)
		p.Body = body

		resp, err := api.EntitiesRulesPostV1(p)
		if err != nil {
			e := falcon.NormalizeError("entities_rules_post_v1", "Failed to create Correlation Rule", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_correlation_rule ---

type updateCorrelationRuleInput struct {
	RuleID        string             `json:"rule_id" jsonschema:"Rule ID to update. Use the 'rule_id' field from falcon_search_correlation_rules results."`
	Name          *string            `json:"name,omitempty" jsonschema:"New name for the rule."`
	Description   *string            `json:"description,omitempty" jsonschema:"New description for the rule."`
	Status        *string            `json:"status,omitempty" jsonschema:"New status. Examples: active, inactive."`
	Severity      *int32             `json:"severity,omitempty" jsonschema:"New severity score. Must be one of: 10, 30, 50, 70, 90."`
	SearchFilter  *string            `json:"search_filter,omitempty" jsonschema:"Updated CQL query for the detection logic."`
	Lookback      *string            `json:"lookback,omitempty" jsonschema:"Updated lookback window. Example: '1h0m', '24h0m'."`
	TriggerMode   *string            `json:"trigger_mode,omitempty" jsonschema:"Updated trigger mode. Examples: summary, verbose."`
	UseIngestTime *bool              `json:"use_ingest_time,omitempty" jsonschema:"Use event ingest time instead of event timestamp for the lookback window."`
	MitreAttack   []mitreAttackInput `json:"mitre_attack,omitempty" jsonschema:"Updated MITRE ATT&CK mapping as a list of objects with tactic_id and technique_id."`
	Comment       *string            `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule is being updated."`
}

func registerUpdateCorrelationRule(s *mcp.Server, api CorrelationRulesAPI) {
	desc := "Update an existing NG-SIEM Correlation Rule. " +
		"Modifies fields on the rule and auto-publishes a new version — no separate publish " +
		"step needed. To enable/disable a rule, set status to 'active' or 'inactive'. " +
		"Only provided fields are changed; omitted fields retain current values."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_correlation_rule",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateCorrelationRuleInput) (*mcp.CallToolResult, any, error) {
		patch := &models.CorrelationrulesapiRulePatchRequestV1{
			ID: &in.RuleID,
		}

		if in.Name != nil {
			patch.Name = *in.Name
		}
		if in.Description != nil {
			patch.Description = *in.Description
		}
		if in.Status != nil {
			patch.Status = *in.Status
		}
		if in.Severity != nil {
			patch.Severity = *in.Severity
		}
		if in.Comment != nil {
			patch.Comment = *in.Comment
		}
		if len(in.MitreAttack) > 0 {
			patch.MitreAttack = toMitreAttackModels(in.MitreAttack)
		}

		searchFieldsSet := in.SearchFilter != nil || in.Lookback != nil ||
			in.TriggerMode != nil || in.UseIngestTime != nil
		if searchFieldsSet {
			search := &models.CorrelationrulesapiPatchRuleSearchV1{}
			if in.SearchFilter != nil {
				search.Filter = *in.SearchFilter
			}
			if in.Lookback != nil {
				search.Lookback = *in.Lookback
			}
			if in.TriggerMode != nil {
				search.TriggerMode = *in.TriggerMode
			}
			if in.UseIngestTime != nil {
				search.UseIngestTime = *in.UseIngestTime
			}
			patch.Search = search
		}

		p := correlation_rules.NewEntitiesRulesPatchV1ParamsWithContext(ctx)
		p.Body = []*models.CorrelationrulesapiRulePatchRequestV1{patch}

		resp, err := api.EntitiesRulesPatchV1(p)
		if err != nil {
			e := falcon.NormalizeError("entities_rules_patch_v1", "Failed to update Correlation Rule", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_correlation_rules ---

type deleteCorrelationRulesInput struct {
	IDs     []string `json:"ids" jsonschema:"Rule IDs to delete. Use the 'rule_id' field from falcon_search_correlation_rules results."`
	Comment *string  `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rules are being deleted."`
}

func registerDeleteCorrelationRules(s *mcp.Server, api CorrelationRulesAPI) {
	desc := "Permanently delete NG-SIEM Correlation Rules by rule ID. " +
		"Removes the specified rules and all their versions. This action cannot be undone — " +
		"use falcon_search_correlation_rules to confirm IDs before deleting. Returns an " +
		"empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_correlation_rules",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteCorrelationRulesInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{
				Error: "Failed to delete Correlation Rules: `ids` must be provided to delete Correlation Rules.",
			}
			return mcpx.JSONResult([]any{e})
		}

		p := correlation_rules.NewEntitiesRulesDeleteV1ParamsWithContext(ctx)
		p.Ids = in.IDs

		_, err := api.EntitiesRulesDeleteV1(p)
		if err != nil {
			e := falcon.NormalizeError("entities_rules_delete_v1", "Failed to delete Correlation Rules", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult([]any{})
	})
}

// --- helpers ---

func toMitreAttackModels(in []mitreAttackInput) []*models.CorrelationrulesapiMitreAttackMappingV1 {
	out := make([]*models.CorrelationrulesapiMitreAttackMappingV1, len(in))
	for i, m := range in {
		tacticID := m.TacticID
		out[i] = &models.CorrelationrulesapiMitreAttackMappingV1{
			TacticID:    &tacticID,
			TechniqueID: m.TechniqueID,
		}
	}
	return out
}

func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 20
	}
	if limit > 500 {
		return 500
	}
	return limit
}
