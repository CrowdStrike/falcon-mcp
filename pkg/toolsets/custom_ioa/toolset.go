// Package custom_ioa implements the Falcon MCP "custom_ioa" toolset: searching,
// creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral
// rule groups and rules using the Falcon Custom IOA Service Collection endpoints.
package custom_ioa

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/custom_ioa"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://custom-ioa/rule-groups/fql-guide"
)

// CustomIOAAPI is the narrow slice of the gofalcon custom_ioa client this
// toolset uses. Declaring it as an interface keeps handlers unit-testable with
// a hand-written mock.
type CustomIOAAPI interface {
	QueryRuleGroupsFull(*custom_ioa.QueryRuleGroupsFullParams, ...custom_ioa.ClientOption) (*custom_ioa.QueryRuleGroupsFullOK, error)
	QueryPlatformsMixin0(*custom_ioa.QueryPlatformsMixin0Params, ...custom_ioa.ClientOption) (*custom_ioa.QueryPlatformsMixin0OK, error)
	GetPlatformsMixin0(*custom_ioa.GetPlatformsMixin0Params, ...custom_ioa.ClientOption) (*custom_ioa.GetPlatformsMixin0OK, error)
	QueryRuleTypes(*custom_ioa.QueryRuleTypesParams, ...custom_ioa.ClientOption) (*custom_ioa.QueryRuleTypesOK, error)
	GetRuleTypes(*custom_ioa.GetRuleTypesParams, ...custom_ioa.ClientOption) (*custom_ioa.GetRuleTypesOK, error)
	CreateRuleGroupMixin0(*custom_ioa.CreateRuleGroupMixin0Params, ...custom_ioa.ClientOption) (*custom_ioa.CreateRuleGroupMixin0Created, error)
	UpdateRuleGroupMixin0(*custom_ioa.UpdateRuleGroupMixin0Params, ...custom_ioa.ClientOption) (*custom_ioa.UpdateRuleGroupMixin0OK, error)
	DeleteRuleGroupsMixin0(*custom_ioa.DeleteRuleGroupsMixin0Params, ...custom_ioa.ClientOption) (*custom_ioa.DeleteRuleGroupsMixin0OK, error)
	CreateRule(*custom_ioa.CreateRuleParams, ...custom_ioa.ClientOption) (*custom_ioa.CreateRuleCreated, error)
	UpdateRulesV2(*custom_ioa.UpdateRulesV2Params, ...custom_ioa.ClientOption) (*custom_ioa.UpdateRulesV2OK, error)
	DeleteRules(*custom_ioa.DeleteRulesParams, ...custom_ioa.ClientOption) (*custom_ioa.DeleteRulesOK, error)
}

// Toolset is the custom_ioa domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "custom_ioa" }

func (Toolset) GetDescription() string {
	return "Search, create, update, and delete Custom IOA behavioral rule groups and rules in CrowdStrike Falcon."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_ioa_rule_groups_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_ioa_rule_groups` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_ioa_rule_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchIOARuleGroups(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_ioa_platforms"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetIOAPlatforms(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_ioa_rule_types"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetIOARuleTypes(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_ioa_rule_group"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateIOARuleGroup(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_ioa_rule_group"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateIOARuleGroup(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_ioa_rule_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteIOARuleGroups(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_ioa_rule"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateIOARule(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_ioa_rule"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateIOARule(s, fc.CustomIOA())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_ioa_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteIOARules(s, fc.CustomIOA())
			},
		},
	}
}

// --- falcon_search_ioa_rule_groups ---

type searchIOARuleGroupsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://custom-ioa/rule-groups/fql-guide for syntax. Examples: platform:'windows'+enabled:true, rules.pattern_severity:'high'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of rule groups to return [1-500]. Default 10."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting offset for pagination. Use the offset value from a previous response."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort rule groups using FQL sort syntax. Fields: created_by, created_on, enabled, modified_by, modified_on, name, description. Example: 'modified_on.desc'."`
	Q      *string `json:"q,omitempty" jsonschema:"Free-text match query that searches across all filter string fields."`
}

func registerSearchIOARuleGroups(s *mcp.Server, api CustomIOAAPI) {
	desc := "Search Custom IOA rule groups and return full details including their rules. " +
		"Use this to find rule groups by platform, name, or enabled state. Consult " +
		"falcon://custom-ioa/rule-groups/fql-guide before constructing filter expressions. " +
		"Returns rule group objects with their contained behavioral detection rules."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_ioa_rule_groups",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchIOARuleGroupsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 10, 500)

		qp := custom_ioa.NewQueryRuleGroupsFullParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort
		qp.Q = in.Q

		resp, err := api.QueryRuleGroupsFull(qp)
		if err != nil {
			return ioaSearchErr("query_rule_groups_full", "Failed to search IOA rule groups", in.Filter, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_get_ioa_platforms ---

func registerGetIOAPlatforms(s *mcp.Server, api CustomIOAAPI) {
	desc := "Get all available platforms for Custom IOA rule groups. " +
		"Use this to discover valid platform values (windows, mac, linux) before " +
		"creating a rule group. Returns platform details."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_ioa_platforms",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, _ struct{}) (*mcp.CallToolResult, any, error) {
		// Step 1: query platform IDs.
		qp := custom_ioa.NewQueryPlatformsMixin0ParamsWithContext(ctx)
		queryResp, err := api.QueryPlatformsMixin0(qp)
		if err != nil {
			e := falcon.NormalizeError("query_platformsMixin0", "Failed to query IOA platforms", err)
			return mcpx.JSONResult([]any{e})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult([]any{})
		}

		// Step 2: fetch full platform details.
		gp := custom_ioa.NewGetPlatformsMixin0ParamsWithContext(ctx)
		gp.Ids = ids
		getResp, err := api.GetPlatformsMixin0(gp)
		if err != nil {
			e := falcon.NormalizeError("get_platformsMixin0", "Failed to get IOA platform details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(getResp.GetPayload().Resources)
	})
}

// --- falcon_get_ioa_rule_types ---

type getIOARuleTypesInput struct {
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of rule types to return [1-500]. Default 100."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting offset for pagination."`
}

func registerGetIOARuleTypes(s *mcp.Server, api CustomIOAAPI) {
	desc := "Get all available Custom IOA rule types. " +
		"Use this to discover valid rule type IDs, required fields, and disposition IDs " +
		"before creating a behavioral detection rule. Returns rule type details including " +
		"platform, fields, and supported actions."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_ioa_rule_types",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getIOARuleTypesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 100, 500)

		// Step 1: query rule type IDs.
		qp := custom_ioa.NewQueryRuleTypesParamsWithContext(ctx)
		qp.Limit = &limit
		qp.Offset = in.Offset
		queryResp, err := api.QueryRuleTypes(qp)
		if err != nil {
			e := falcon.NormalizeError("query_rule_types", "Failed to query IOA rule types", err)
			return mcpx.JSONResult([]any{e})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult([]any{})
		}

		// Step 2: fetch full rule type details.
		gp := custom_ioa.NewGetRuleTypesParamsWithContext(ctx)
		gp.Ids = ids
		getResp, err := api.GetRuleTypes(gp)
		if err != nil {
			e := falcon.NormalizeError("get_rule_types", "Failed to get IOA rule type details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(getResp.GetPayload().Resources)
	})
}

// --- falcon_create_ioa_rule_group ---

type createIOARuleGroupInput struct {
	Name        string  `json:"name" jsonschema:"Name for the new rule group. Examples: 'Suspicious PowerShell Activity', 'Lateral Movement Detection'."`
	Platform    string  `json:"platform" jsonschema:"Platform this rule group applies to. Allowed values: windows, mac, linux."`
	Description *string `json:"description,omitempty" jsonschema:"Optional description for the rule group."`
	Comment     *string `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule group is being created."`
}

func registerCreateIOARuleGroup(s *mcp.Server, api CustomIOAAPI) {
	desc := "Create a new Custom IOA rule group. " +
		"Rule groups are containers for behavioral detection rules scoped to a platform. " +
		"Use falcon_get_ioa_platforms to see valid platform values. After creating a " +
		"group, use falcon_create_ioa_rule to add detection rules to it. " +
		"Returns the created rule group on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_ioa_rule_group",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createIOARuleGroupInput) (*mcp.CallToolResult, any, error) {
		// All fields are required by the API model even when nil — pass empty string
		// pointers for optional fields not provided by the caller.
		comment := ptrOrEmpty(in.Comment)
		description := ptrOrEmpty(in.Description)

		p := custom_ioa.NewCreateRuleGroupMixin0ParamsWithContext(ctx)
		p.Body = &models.APIRuleGroupCreateRequestV1{
			Name:        &in.Name,
			Platform:    &in.Platform,
			Comment:     comment,
			Description: description,
		}

		resp, err := api.CreateRuleGroupMixin0(p)
		if err != nil {
			e := falcon.NormalizeError("create_rule_groupMixin0", "Failed to create IOA rule group", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_ioa_rule_group ---

type updateIOARuleGroupInput struct {
	ID               string  `json:"id" jsonschema:"ID of the rule group to update."`
	RulegroupVersion int64   `json:"rulegroup_version" jsonschema:"Current version of the rule group. Required for optimistic locking. Retrieve this from falcon_search_ioa_rule_groups."`
	Name             *string `json:"name,omitempty" jsonschema:"New name for the rule group."`
	Description      *string `json:"description,omitempty" jsonschema:"New description for the rule group."`
	Enabled          *bool   `json:"enabled,omitempty" jsonschema:"Whether the rule group should be enabled or disabled."`
	Comment          *string `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule group is being updated."`
}

func registerUpdateIOARuleGroup(s *mcp.Server, api CustomIOAAPI) {
	desc := "Update an existing Custom IOA rule group. " +
		"Modify name, description, or enabled state. Requires rulegroup_version for " +
		"optimistic locking — get it from falcon_search_ioa_rule_groups. " +
		"Returns the updated rule group on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_ioa_rule_group",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateIOARuleGroupInput) (*mcp.CallToolResult, any, error) {
		comment := ptrOrEmpty(in.Comment)
		description := ptrOrEmpty(in.Description)
		name := ptrOrEmpty(in.Name)

		// enabled is required by the model even when not changing it.
		enabled := in.Enabled
		if enabled == nil {
			// Default to true (leave the group enabled) when the caller omits it.
			t := true
			enabled = &t
		}

		p := custom_ioa.NewUpdateRuleGroupMixin0ParamsWithContext(ctx)
		p.Body = &models.APIRuleGroupModifyRequestV1{
			ID:               &in.ID,
			RulegroupVersion: &in.RulegroupVersion,
			Comment:          comment,
			Description:      description,
			Enabled:          enabled,
			Name:             name,
		}

		resp, err := api.UpdateRuleGroupMixin0(p)
		if err != nil {
			e := falcon.NormalizeError("update_rule_groupMixin0", "Failed to update IOA rule group", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_ioa_rule_groups ---

type deleteIOARuleGroupsInput struct {
	IDs     []string `json:"ids" jsonschema:"IDs of the rule groups to delete."`
	Comment *string  `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule groups are being deleted."`
}

func registerDeleteIOARuleGroups(s *mcp.Server, api CustomIOAAPI) {
	desc := "Delete Custom IOA rule groups by ID. " +
		"Permanently removes the rule groups and all rules within them. Use " +
		"falcon_search_ioa_rule_groups to find rule group IDs. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_ioa_rule_groups",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteIOARuleGroupsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "Failed to delete IOA rule groups: `ids` must be provided to delete IOA rule groups."}
			return mcpx.JSONResult([]any{e})
		}

		p := custom_ioa.NewDeleteRuleGroupsMixin0ParamsWithContext(ctx)
		p.Ids = in.IDs
		p.Comment = in.Comment

		_, err := api.DeleteRuleGroupsMixin0(p)
		if err != nil {
			e := falcon.NormalizeError("delete_rule_groupsMixin0", "Failed to delete IOA rule groups", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult([]any{})
	})
}

// --- falcon_create_ioa_rule ---

// fieldValueInput is the JSON-compatible representation of a rule field value
// supplied by the tool caller. We convert it to *models.DomainFieldValue.
type fieldValueInput struct {
	Name       string            `json:"name"`
	Value      string            `json:"value"`
	Type       string            `json:"type,omitempty"`
	Label      string            `json:"label,omitempty"`
	FinalValue string            `json:"final_value,omitempty"`
	Values     []domainValueItem `json:"values,omitempty"`
}

type domainValueItem struct {
	Label string `json:"label"`
	Value string `json:"value"`
}

type createIOARuleInput struct {
	RulegroupID     string            `json:"rulegroup_id" jsonschema:"ID of the rule group to add the rule to."`
	Name            string            `json:"name" jsonschema:"Name for the new rule. Examples: 'Block cmd.exe spawned from Office', 'Detect encoded PowerShell'."`
	RuletypeID      string            `json:"ruletype_id" jsonschema:"Rule type ID that defines the detection category. Use falcon_get_ioa_rule_types to find valid IDs."`
	DispositionID   int32             `json:"disposition_id" jsonschema:"Disposition ID that determines the action taken when the rule fires. Use falcon_get_ioa_rule_types to find valid disposition IDs for the rule type."`
	PatternSeverity string            `json:"pattern_severity" jsonschema:"Severity level for this rule. Allowed values: critical, high, medium, low, informational."`
	FieldValues     []fieldValueInput `json:"field_values" jsonschema:"List of field value objects that define the rule's matching criteria. Each object must include 'name', 'value', and 'type'. Use falcon_get_ioa_rule_types to discover required fields for the chosen rule type."`
	Description     *string           `json:"description,omitempty" jsonschema:"Optional description for the rule."`
	Comment         *string           `json:"comment,omitempty" jsonschema:"Audit comment explaining why this rule is being created."`
}

func registerCreateIOARule(s *mcp.Server, api CustomIOAAPI) {
	desc := "Create a new Custom IOA behavioral detection rule within a rule group. " +
		"Use falcon_get_ioa_rule_types first to discover rule type IDs, required fields, " +
		"and valid disposition IDs. The field_values parameter defines the behavioral " +
		"criteria the rule matches against (process names, file paths, command line regex). " +
		"Returns the created rule on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_ioa_rule",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createIOARuleInput) (*mcp.CallToolResult, any, error) {
		comment := ptrOrEmpty(in.Comment)
		description := ptrOrEmpty(in.Description)

		fvs := toFieldValues(in.FieldValues)

		p := custom_ioa.NewCreateRuleParamsWithContext(ctx)
		p.Body = &models.APIRuleCreateV1{
			RulegroupID:     &in.RulegroupID,
			Name:            &in.Name,
			RuletypeID:      &in.RuletypeID,
			DispositionID:   &in.DispositionID,
			PatternSeverity: &in.PatternSeverity,
			FieldValues:     fvs,
			Comment:         comment,
			Description:     description,
		}

		resp, err := api.CreateRule(p)
		if err != nil {
			e := falcon.NormalizeError("create_rule", "Failed to create IOA rule", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_ioa_rule ---

type updateIOARuleInput struct {
	RulegroupID      string            `json:"rulegroup_id" jsonschema:"ID of the rule group containing the rule."`
	RulegroupVersion int64             `json:"rulegroup_version" jsonschema:"Current version of the rule group. Required for optimistic locking. Retrieve from falcon_search_ioa_rule_groups."`
	InstanceID       string            `json:"instance_id" jsonschema:"Instance ID of the rule to update. Retrieve from falcon_search_ioa_rule_groups."`
	Name             *string           `json:"name,omitempty" jsonschema:"New name for the rule."`
	Description      *string           `json:"description,omitempty" jsonschema:"New description for the rule."`
	Enabled          *bool             `json:"enabled,omitempty" jsonschema:"Whether the rule should be enabled or disabled."`
	PatternSeverity  *string           `json:"pattern_severity,omitempty" jsonschema:"New severity level. Allowed values: critical, high, medium, low, informational."`
	DispositionID    *int32            `json:"disposition_id,omitempty" jsonschema:"New disposition ID for the action taken when the rule fires."`
	FieldValues      []fieldValueInput `json:"field_values,omitempty" jsonschema:"Updated field value objects that define the rule's matching criteria."`
	Comment          *string           `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rule is being updated."`
}

func registerUpdateIOARule(s *mcp.Server, api CustomIOAAPI) {
	desc := "Update an existing Custom IOA behavioral detection rule. " +
		"Requires rulegroup_version for optimistic locking. Get the current version " +
		"and instance_id from falcon_search_ioa_rule_groups. " +
		"Returns the updated rule on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_ioa_rule",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateIOARuleInput) (*mcp.CallToolResult, any, error) {
		comment := ptrOrEmpty(in.Comment)

		// Build the per-rule update object.
		ruleUpdate := &models.APIRuleUpdateV2{
			InstanceID:       &in.InstanceID,
			RulegroupVersion: &in.RulegroupVersion,
		}
		// All fields in APIRuleUpdateV2 are required pointers; supply non-nil
		// values so the API model validation passes for any fields the caller
		// provided.
		if in.Name != nil {
			ruleUpdate.Name = in.Name
		} else {
			empty := ""
			ruleUpdate.Name = &empty
		}
		if in.Description != nil {
			ruleUpdate.Description = in.Description
		} else {
			empty := ""
			ruleUpdate.Description = &empty
		}
		if in.Enabled != nil {
			ruleUpdate.Enabled = in.Enabled
		} else {
			t := true
			ruleUpdate.Enabled = &t
		}
		if in.PatternSeverity != nil {
			ruleUpdate.PatternSeverity = in.PatternSeverity
		} else {
			empty := ""
			ruleUpdate.PatternSeverity = &empty
		}
		if in.DispositionID != nil {
			ruleUpdate.DispositionID = in.DispositionID
		} else {
			var zero int32
			ruleUpdate.DispositionID = &zero
		}
		if len(in.FieldValues) > 0 {
			ruleUpdate.FieldValues = toFieldValues(in.FieldValues)
		} else {
			ruleUpdate.FieldValues = []*models.DomainFieldValue{}
		}

		p := custom_ioa.NewUpdateRulesV2ParamsWithContext(ctx)
		p.Body = &models.APIRuleUpdatesRequestV2{
			RulegroupID:      &in.RulegroupID,
			RulegroupVersion: &in.RulegroupVersion,
			RuleUpdates:      []*models.APIRuleUpdateV2{ruleUpdate},
			Comment:          comment,
		}

		resp, err := api.UpdateRulesV2(p)
		if err != nil {
			e := falcon.NormalizeError("update_rules_v2", "Failed to update IOA rule", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_ioa_rules ---

type deleteIOARulesInput struct {
	RuleGroupID string   `json:"rule_group_id" jsonschema:"ID of the rule group containing the rules to delete."`
	IDs         []string `json:"ids" jsonschema:"IDs of the rules to delete. Retrieve from falcon_search_ioa_rule_groups."`
	Comment     *string  `json:"comment,omitempty" jsonschema:"Audit comment explaining why the rules are being deleted."`
}

func registerDeleteIOARules(s *mcp.Server, api CustomIOAAPI) {
	desc := "Delete Custom IOA behavioral detection rules from a rule group. " +
		"Use falcon_search_ioa_rule_groups to find the rule group ID and individual " +
		"rule instance IDs to delete. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_ioa_rules",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteIOARulesInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "Failed to delete IOA rules: `ids` must be provided to delete IOA rules."}
			return mcpx.JSONResult([]any{e})
		}

		p := custom_ioa.NewDeleteRulesParamsWithContext(ctx)
		p.RuleGroupID = in.RuleGroupID
		p.Ids = in.IDs
		p.Comment = in.Comment

		_, err := api.DeleteRules(p)
		if err != nil {
			e := falcon.NormalizeError("delete_rules", "Failed to delete IOA rules", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult([]any{})
	})
}

// --- helpers ---

// ioaSearchErr normalizes a search error, surfacing the FQL guide on 400 errors.
func ioaSearchErr(operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to [1, max], applying defaultVal when 0.
func normalizeLimit(limit int64, defaultVal, max int64) int64 {
	if limit <= 0 {
		return defaultVal
	}
	if limit > max {
		return max
	}
	return limit
}

// ptrOrEmpty returns the pointed-to string or a pointer to an empty string
// when p is nil. The gofalcon model validators require non-nil pointers for
// all string fields even when the API accepts empty values.
func ptrOrEmpty(p *string) *string {
	if p != nil {
		return p
	}
	empty := ""
	return &empty
}

// toFieldValues converts the tool-caller's field value list to the model type.
func toFieldValues(in []fieldValueInput) []*models.DomainFieldValue {
	out := make([]*models.DomainFieldValue, 0, len(in))
	for _, fv := range in {
		name := fv.Name
		val := fv.Value
		typ := fv.Type
		fvModel := &models.DomainFieldValue{
			Name:       &name,
			Value:      &val,
			Type:       &typ,
			Label:      fv.Label,
			FinalValue: fv.FinalValue,
		}
		if len(fv.Values) > 0 {
			for _, item := range fv.Values {
				label := item.Label
				value := item.Value
				fvModel.Values = append(fvModel.Values, &models.DomainValueItem{
					Label: &label,
					Value: &value,
				})
			}
		} else {
			fvModel.Values = []*models.DomainValueItem{}
		}
		out = append(out, fvModel)
	}
	return out
}
