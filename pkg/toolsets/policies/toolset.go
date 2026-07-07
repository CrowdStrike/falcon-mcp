// Package policies implements the Falcon MCP "policies" toolset: a unified set
// of seven tools for managing CrowdStrike host-based policies across six policy
// types (prevention, sensor_update, firewall, device_control, response,
// content_update) behind a single policy_type discriminator.
//
// Per-type API differences — operation names, request-body models, search mode,
// and platform requirements — are absorbed by a per-type policyOps dispatch
// table so the seven tool handlers stay uniform and unit-testable.
package policies

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/content_update_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/device_control_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/firewall_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/prevention_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/response_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/sensor_update_policies"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://policies/search/fql-guide"
)

// validPolicyTypes is the ordered list of discriminator values.
var validPolicyTypes = []string{
	"prevention",
	"sensor_update",
	"firewall",
	"device_control",
	"response",
	"content_update",
}

// safeSearchSortFields are the only sort fields that do not trigger HTTP 500.
// platform_name is deliberately excluded — sorting by it causes 500 on every type.
var safeSearchSortFields = map[string]bool{
	"name":               true,
	"created_timestamp":  true,
	"modified_timestamp": true,
	"enabled":            true,
	"created_by":         true,
	"modified_by":        true,
	"precedence":         true,
}

// validActions lists the accepted action_name values per policy type.
var validActions = map[string]map[string]bool{
	"prevention": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
		"add-rule-group": true, "remove-rule-group": true,
	},
	"sensor_update": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
		"add-rule-group": true, "remove-rule-group": true,
	},
	"firewall": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
	},
	"device_control": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
	},
	"response": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
		"add-rule-group": true, "remove-rule-group": true,
	},
	"content_update": {
		"enable": true, "disable": true,
		"add-host-group": true, "remove-host-group": true,
		"override-allow": true, "override-pause": true, "override-revert": true,
	},
}

// requiresPlatformCreate is true for all types that require platform_name on create.
var requiresPlatformCreate = map[string]bool{
	"prevention":     true,
	"sensor_update":  true,
	"firewall":       true,
	"device_control": true,
	"response":       true,
	"content_update": false,
}

// requiresPlatformPrecedence matches requiresPlatformCreate.
var requiresPlatformPrecedence = map[string]bool{
	"prevention":     true,
	"sensor_update":  true,
	"firewall":       true,
	"device_control": true,
	"response":       true,
	"content_update": false,
}

// --- operation name constants (used in NormalizeError) ---

const (
	opSearchPrevention     = "queryCombinedPreventionPolicies"
	opMembersPrevention    = "queryCombinedPreventionPolicyMembers"
	opCreatePrevention     = "createPreventionPolicies"
	opUpdatePrevention     = "updatePreventionPolicies"
	opDeletePrevention     = "deletePreventionPolicies"
	opActionPrevention     = "performPreventionPoliciesAction"
	opPrecedencePrevention = "setPreventionPoliciesPrecedence"

	opSearchSensorUpdate     = "queryCombinedSensorUpdatePoliciesV2"
	opMembersSensorUpdate    = "queryCombinedSensorUpdatePolicyMembers"
	opCreateSensorUpdate     = "createSensorUpdatePoliciesV2"
	opUpdateSensorUpdate     = "updateSensorUpdatePoliciesV2"
	opDeleteSensorUpdate     = "deleteSensorUpdatePolicies"
	opActionSensorUpdate     = "performSensorUpdatePoliciesAction"
	opPrecedenceSensorUpdate = "setSensorUpdatePoliciesPrecedence"

	opSearchFirewall     = "queryCombinedFirewallPolicies"
	opMembersFirewall    = "queryCombinedFirewallPolicyMembers"
	opCreateFirewall     = "createFirewallPolicies"
	opUpdateFirewall     = "updateFirewallPolicies"
	opDeleteFirewall     = "deleteFirewallPolicies"
	opActionFirewall     = "performFirewallPoliciesAction"
	opPrecedenceFirewall = "setFirewallPoliciesPrecedence"

	opQueryDeviceControl      = "queryDeviceControlPolicies"
	opGetDeviceControl        = "getDeviceControlPoliciesV2"
	opMembersDeviceControl    = "queryCombinedDeviceControlPolicyMembers"
	opCreateDeviceControl     = "postDeviceControlPoliciesV2"
	opUpdateDeviceControl     = "patchDeviceControlPoliciesV2"
	opDeleteDeviceControl     = "deleteDeviceControlPolicies"
	opActionDeviceControl     = "performDeviceControlPoliciesAction"
	opPrecedenceDeviceControl = "setDeviceControlPoliciesPrecedence"

	opSearchResponse     = "queryCombinedRTResponsePolicies"
	opMembersResponse    = "queryCombinedRTResponsePolicyMembers"
	opCreateResponse     = "createRTResponsePolicies"
	opUpdateResponse     = "updateRTResponsePolicies"
	opDeleteResponse     = "deleteRTResponsePolicies"
	opActionResponse     = "performRTResponsePoliciesAction"
	opPrecedenceResponse = "setRTResponsePoliciesPrecedence"

	opSearchContentUpdate     = "queryCombinedContentUpdatePolicies"
	opMembersContentUpdate    = "queryCombinedContentUpdatePolicyMembers"
	opCreateContentUpdate     = "createContentUpdatePolicies"
	opUpdateContentUpdate     = "updateContentUpdatePolicies"
	opDeleteContentUpdate     = "deleteContentUpdatePolicies"
	opActionContentUpdate     = "performContentUpdatePoliciesAction"
	opPrecedenceContentUpdate = "setContentUpdatePoliciesPrecedence"
)

// policySearchResult holds the flattened resources from any combined-search call.
type policySearchResult struct {
	resources []any
	err       error
	opName    string
}

// policyOps holds all the dispatch closures for one policy type. Each function
// maps directly to one or two gofalcon calls, hiding the per-type model differences.
type policyOps struct {
	// searchMode is "combined" or "two_step".
	searchMode string

	// searchOp and membersOp are the operation names for NormalizeError scope lookup.
	searchOp     string
	membersOp    string
	createOp     string
	updateOp     string
	deleteOp     string
	actionOp     string
	precedenceOp string

	// combined executes the combined-search call and returns serializable resources.
	combined func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error)

	// twoStepQuery executes the ID-only query (device_control two-step phase 1).
	twoStepQuery func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]string, error)

	// twoStepGet executes the details fetch (device_control two-step phase 2).
	twoStepGet func(ctx context.Context, ids []string) ([]any, error)

	// members executes the combined members search.
	members func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error)

	// create executes the create call. name is required for all types.
	// For content_update, platformName is ignored (platform-agnostic type).
	create func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error)

	// update executes the update call. id is required.
	update func(ctx context.Context, id, name, description string, settings any) ([]any, error)

	// delete executes the delete call. Returns a MsaQueryResponse.Resources ([]string).
	delete func(ctx context.Context, ids []string) error

	// action executes the perform-action call.
	action func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error)

	// precedence executes the set-precedence call. platformName is empty for content_update.
	precedence func(ctx context.Context, ids []string, platformName string) error
}

// --- Toolset ---

// Toolset is the policies domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "policies" }

func (Toolset) GetDescription() string {
	return "Manage CrowdStrike Falcon host-based policies across prevention, sensor update, firewall, device control, response, and content update policy types."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_policies_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_policies` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	reg := buildRegistry(fc)
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_policies"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchPolicies(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_policy_members"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchPolicyMembers(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_policy"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreatePolicy(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_policy"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdatePolicy(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_policies"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeletePolicies(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_perform_policy_action"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerPerformPolicyAction(s, reg)
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_set_policy_precedence"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSetPolicyPrecedence(s, reg)
			},
		},
	}
}

// --- Registry builder ---

// buildRegistry constructs the per-type dispatch tables from the six gofalcon sub-clients.
func buildRegistry(fc *falcon.FalconClient) map[string]policyOps {
	return map[string]policyOps{
		"prevention":     buildPreventionOps(fc.PreventionPolicies()),
		"sensor_update":  buildSensorUpdateOps(fc.SensorUpdatePolicies()),
		"firewall":       buildFirewallOps(fc.FirewallPolicies()),
		"device_control": buildDeviceControlOps(fc.DeviceControlPolicies()),
		"response":       buildResponseOps(fc.ResponsePolicies()),
		"content_update": buildContentUpdateOps(fc.ContentUpdatePolicies()),
	}
}

// --- prevention ---

func buildPreventionOps(api prevention_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "combined",
		searchOp:     opSearchPrevention,
		membersOp:    opMembersPrevention,
		createOp:     opCreatePrevention,
		updateOp:     opUpdatePrevention,
		deleteOp:     opDeletePrevention,
		actionOp:     opActionPrevention,
		precedenceOp: opPrecedencePrevention,

		combined: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := prevention_policies.NewQueryCombinedPreventionPoliciesParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedPreventionPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := prevention_policies.NewQueryCombinedPreventionPolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedPreventionPolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error) {
			res := &models.PreventionCreatePolicyReqV1{Name: &name, PlatformName: &platformName}
			if description != "" {
				res.Description = description
			}
			if cloneID != "" {
				res.CloneID = cloneID
			}
			if settings != nil {
				if s, ok := settings.([]*models.PreventionSettingReqV1); ok {
					res.Settings = s
				}
			}
			p := prevention_policies.NewCreatePreventionPoliciesParamsWithContext(ctx)
			p.Body = &models.PreventionCreatePoliciesReqV1{Resources: []*models.PreventionCreatePolicyReqV1{res}}
			resp, err := api.CreatePreventionPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.PreventionUpdatePolicyReqV1{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				desc := description
				res.Description = &desc
			}
			if settings != nil {
				if s, ok := settings.([]*models.PreventionSettingReqV1); ok {
					res.Settings = s
				}
			}
			p := prevention_policies.NewUpdatePreventionPoliciesParamsWithContext(ctx)
			p.Body = &models.PreventionUpdatePoliciesReqV1{Resources: []*models.PreventionUpdatePolicyReqV1{res}}
			resp, err := api.UpdatePreventionPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := prevention_policies.NewDeletePreventionPoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeletePreventionPolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := prevention_policies.NewPerformPreventionPoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformPreventionPoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, platformName string) error {
			p := prevention_policies.NewSetPreventionPoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetPolicyPrecedenceReqV1{Ids: ids, PlatformName: &platformName}
			_, err := api.SetPreventionPoliciesPrecedence(p)
			return err
		},
	}
}

// --- sensor_update ---

func buildSensorUpdateOps(api sensor_update_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "combined",
		searchOp:     opSearchSensorUpdate,
		membersOp:    opMembersSensorUpdate,
		createOp:     opCreateSensorUpdate,
		updateOp:     opUpdateSensorUpdate,
		deleteOp:     opDeleteSensorUpdate,
		actionOp:     opActionSensorUpdate,
		precedenceOp: opPrecedenceSensorUpdate,

		combined: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := sensor_update_policies.NewQueryCombinedSensorUpdatePoliciesV2ParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedSensorUpdatePoliciesV2(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := sensor_update_policies.NewQueryCombinedSensorUpdatePolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedSensorUpdatePolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error) {
			res := &models.SensorUpdateCreatePolicyReqV2{Name: &name, PlatformName: &platformName}
			if description != "" {
				res.Description = description
			}
			// sensor_update does not have clone_id in the V2 model
			p := sensor_update_policies.NewCreateSensorUpdatePoliciesV2ParamsWithContext(ctx)
			p.Body = &models.SensorUpdateCreatePoliciesReqV2{Resources: []*models.SensorUpdateCreatePolicyReqV2{res}}
			resp, err := api.CreateSensorUpdatePoliciesV2(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.SensorUpdateUpdatePolicyReqV2{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				res.Description = description
			}
			p := sensor_update_policies.NewUpdateSensorUpdatePoliciesV2ParamsWithContext(ctx)
			p.Body = &models.SensorUpdateUpdatePoliciesReqV2{Resources: []*models.SensorUpdateUpdatePolicyReqV2{res}}
			resp, err := api.UpdateSensorUpdatePoliciesV2(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := sensor_update_policies.NewDeleteSensorUpdatePoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeleteSensorUpdatePolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := sensor_update_policies.NewPerformSensorUpdatePoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformSensorUpdatePoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, platformName string) error {
			p := sensor_update_policies.NewSetSensorUpdatePoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetPolicyPrecedenceReqV1{Ids: ids, PlatformName: &platformName}
			_, err := api.SetSensorUpdatePoliciesPrecedence(p)
			return err
		},
	}
}

// --- firewall ---

func buildFirewallOps(api firewall_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "combined",
		searchOp:     opSearchFirewall,
		membersOp:    opMembersFirewall,
		createOp:     opCreateFirewall,
		updateOp:     opUpdateFirewall,
		deleteOp:     opDeleteFirewall,
		actionOp:     opActionFirewall,
		precedenceOp: opPrecedenceFirewall,

		combined: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := firewall_policies.NewQueryCombinedFirewallPoliciesParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedFirewallPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := firewall_policies.NewQueryCombinedFirewallPolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedFirewallPolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error) {
			res := &models.FirewallCreateFirewallPolicyReqV1{Name: &name, PlatformName: &platformName}
			if description != "" {
				res.Description = description
			}
			if cloneID != "" {
				res.CloneID = cloneID
			}
			p := firewall_policies.NewCreateFirewallPoliciesParamsWithContext(ctx)
			p.Body = &models.FirewallCreateFirewallPoliciesReqV1{Resources: []*models.FirewallCreateFirewallPolicyReqV1{res}}
			resp, err := api.CreateFirewallPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.FirewallUpdateFirewallPolicyReqV1{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				res.Description = description
			}
			p := firewall_policies.NewUpdateFirewallPoliciesParamsWithContext(ctx)
			p.Body = &models.FirewallUpdateFirewallPoliciesReqV1{Resources: []*models.FirewallUpdateFirewallPolicyReqV1{res}}
			resp, err := api.UpdateFirewallPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := firewall_policies.NewDeleteFirewallPoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeleteFirewallPolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := firewall_policies.NewPerformFirewallPoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformFirewallPoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, platformName string) error {
			p := firewall_policies.NewSetFirewallPoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetPolicyPrecedenceReqV1{Ids: ids, PlatformName: &platformName}
			_, err := api.SetFirewallPoliciesPrecedence(p)
			return err
		},
	}
}

// --- device_control (two_step search) ---

func buildDeviceControlOps(api device_control_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "two_step",
		searchOp:     opQueryDeviceControl,
		membersOp:    opMembersDeviceControl,
		createOp:     opCreateDeviceControl,
		updateOp:     opUpdateDeviceControl,
		deleteOp:     opDeleteDeviceControl,
		actionOp:     opActionDeviceControl,
		precedenceOp: opPrecedenceDeviceControl,

		twoStepQuery: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]string, error) {
			p := device_control_policies.NewQueryDeviceControlPoliciesParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryDeviceControlPolicies(p)
			if err != nil {
				return nil, err
			}
			return resp.GetPayload().Resources, nil
		},

		twoStepGet: func(ctx context.Context, ids []string) ([]any, error) {
			p := device_control_policies.NewGetDeviceControlPoliciesParamsWithContext(ctx)
			p.Ids = ids
			resp, err := api.GetDeviceControlPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := device_control_policies.NewQueryCombinedDeviceControlPolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedDeviceControlPolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error) {
			res := &models.DeviceControlCreatePolicyReqV1{Name: &name, PlatformName: &platformName}
			if description != "" {
				res.Description = description
			}
			if cloneID != "" {
				res.CloneID = cloneID
			}
			p := device_control_policies.NewCreateDeviceControlPoliciesParamsWithContext(ctx)
			p.Body = &models.DeviceControlCreatePoliciesV1{Resources: []*models.DeviceControlCreatePolicyReqV1{res}}
			resp, err := api.CreateDeviceControlPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.DeviceControlUpdatePolicyReqV1{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				res.Description = description
			}
			p := device_control_policies.NewUpdateDeviceControlPoliciesParamsWithContext(ctx)
			p.Body = &models.DeviceControlUpdatePoliciesReqV1{Resources: []*models.DeviceControlUpdatePolicyReqV1{res}}
			resp, err := api.UpdateDeviceControlPolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := device_control_policies.NewDeleteDeviceControlPoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeleteDeviceControlPolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := device_control_policies.NewPerformDeviceControlPoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformDeviceControlPoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, platformName string) error {
			p := device_control_policies.NewSetDeviceControlPoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetPolicyPrecedenceReqV1{Ids: ids, PlatformName: &platformName}
			_, err := api.SetDeviceControlPoliciesPrecedence(p)
			return err
		},
	}
}

// --- response ---

func buildResponseOps(api response_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "combined",
		searchOp:     opSearchResponse,
		membersOp:    opMembersResponse,
		createOp:     opCreateResponse,
		updateOp:     opUpdateResponse,
		deleteOp:     opDeleteResponse,
		actionOp:     opActionResponse,
		precedenceOp: opPrecedenceResponse,

		combined: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := response_policies.NewQueryCombinedRTResponsePoliciesParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedRTResponsePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := response_policies.NewQueryCombinedRTResponsePolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedRTResponsePolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error) {
			res := &models.RemoteResponseCreatePolicyReqV1{Name: &name, PlatformName: &platformName}
			if description != "" {
				res.Description = description
			}
			if cloneID != "" {
				res.CloneID = cloneID
			}
			p := response_policies.NewCreateRTResponsePoliciesParamsWithContext(ctx)
			p.Body = &models.RemoteResponseCreatePoliciesV1{Resources: []*models.RemoteResponseCreatePolicyReqV1{res}}
			resp, err := api.CreateRTResponsePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.RemoteResponseUpdatePolicyReqV1{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				desc := description
				res.Description = &desc
			}
			p := response_policies.NewUpdateRTResponsePoliciesParamsWithContext(ctx)
			p.Body = &models.RemoteResponseUpdatePoliciesReqV1{Resources: []*models.RemoteResponseUpdatePolicyReqV1{res}}
			resp, err := api.UpdateRTResponsePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := response_policies.NewDeleteRTResponsePoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeleteRTResponsePolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := response_policies.NewPerformRTResponsePoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformRTResponsePoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, platformName string) error {
			p := response_policies.NewSetRTResponsePoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetPolicyPrecedenceReqV1{Ids: ids, PlatformName: &platformName}
			_, err := api.SetRTResponsePoliciesPrecedence(p)
			return err
		},
	}
}

// --- content_update ---

func buildContentUpdateOps(api content_update_policies.ClientService) policyOps {
	return policyOps{
		searchMode:   "combined",
		searchOp:     opSearchContentUpdate,
		membersOp:    opMembersContentUpdate,
		createOp:     opCreateContentUpdate,
		updateOp:     opUpdateContentUpdate,
		deleteOp:     opDeleteContentUpdate,
		actionOp:     opActionContentUpdate,
		precedenceOp: opPrecedenceContentUpdate,

		combined: func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := content_update_policies.NewQueryCombinedContentUpdatePoliciesParamsWithContext(ctx)
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedContentUpdatePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		members: func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error) {
			p := content_update_policies.NewQueryCombinedContentUpdatePolicyMembersParamsWithContext(ctx)
			p.ID = &id
			p.Filter = filter
			p.Limit = &limit
			p.Offset = offset
			p.Sort = sort
			resp, err := api.QueryCombinedContentUpdatePolicyMembers(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		create: func(ctx context.Context, name, _ /* platformName, ignored */, description string, settings any, cloneID string) ([]any, error) {
			res := &models.ContentUpdateCreatePolicyReqV1{Name: &name}
			if description != "" {
				res.Description = description
			}
			// content_update does not support clone_id in this model
			p := content_update_policies.NewCreateContentUpdatePoliciesParamsWithContext(ctx)
			p.Body = &models.ContentUpdateCreatePoliciesReqV1{Resources: []*models.ContentUpdateCreatePolicyReqV1{res}}
			resp, err := api.CreateContentUpdatePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		update: func(ctx context.Context, id, name, description string, settings any) ([]any, error) {
			res := &models.ContentUpdateUpdatePolicyReqV1{ID: &id}
			if name != "" {
				res.Name = name
			}
			if description != "" {
				res.Description = description
			}
			p := content_update_policies.NewUpdateContentUpdatePoliciesParamsWithContext(ctx)
			p.Body = &models.ContentUpdateUpdatePoliciesReqV1{Resources: []*models.ContentUpdateUpdatePolicyReqV1{res}}
			resp, err := api.UpdateContentUpdatePolicies(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		delete: func(ctx context.Context, ids []string) error {
			p := content_update_policies.NewDeleteContentUpdatePoliciesParamsWithContext(ctx)
			p.Ids = ids
			_, err := api.DeleteContentUpdatePolicies(p)
			return err
		},

		action: func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			p := content_update_policies.NewPerformContentUpdatePoliciesActionParamsWithContext(ctx)
			p.ActionName = actionName
			p.Body = buildActionBody(ids, groupID)
			resp, err := api.PerformContentUpdatePoliciesAction(p)
			if err != nil {
				return nil, err
			}
			return toAnySlice(resp.GetPayload().Resources), nil
		},

		precedence: func(ctx context.Context, ids []string, _ /* no platform */ string) error {
			p := content_update_policies.NewSetContentUpdatePoliciesPrecedenceParamsWithContext(ctx)
			p.Body = &models.BaseSetContentUpdatePolicyPrecedenceReqV1{Ids: ids}
			_, err := api.SetContentUpdatePoliciesPrecedence(p)
			return err
		},
	}
}

// --- Tool registrations ---

// searchPoliciesInput is the input for falcon_search_policies.
type searchPoliciesInput struct {
	PolicyType string  `json:"policy_type" jsonschema:"Policy type to search. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	Filter     *string `json:"filter,omitempty" jsonschema:"FQL filter expression. For name matching use name:~'value' (contains). Do NOT sort by platform_name (returns HTTP 500). See falcon://policies/search/fql-guide for full syntax."`
	Limit      int64   `json:"limit,omitempty" jsonschema:"Maximum number of policies to return [1-500]. Default 100."`
	Offset     *int64  `json:"offset,omitempty" jsonschema:"Starting index of the result set from which to return policies."`
	Sort       *string `json:"sort,omitempty" jsonschema:"Sort expression (e.g. 'modified_timestamp.desc'). Do NOT sort by platform_name (returns HTTP 500). Safe fields: name, created_timestamp, modified_timestamp, enabled, created_by, modified_by, precedence."`
}

func registerSearchPolicies(s *mcp.Server, reg map[string]policyOps) {
	desc := "Search host-based policies of a given type and return full policy records. " +
		"Use this to find prevention, sensor update, firewall, device control, response, or " +
		"content update policies by name, platform, enabled state, or timestamp — the " +
		"policy_type parameter selects which policy API is queried. Consult " +
		"falcon://policies/search/fql-guide before constructing filter expressions; the " +
		"name match operator differs per type. Returns full policy records including id, name, " +
		"platform_name, enabled, settings, and assigned host groups. " +
		"WARNING: Do NOT sort by platform_name — it returns HTTP 500 on every policy type."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_policies",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchPoliciesInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		if sortErr := validateSort(in.Sort); sortErr != nil {
			return mcpx.JSONResult([]any{sortErr})
		}

		limit := normalizeLimit(in.Limit)

		if ops.searchMode == "two_step" {
			ids, err := ops.twoStepQuery(ctx, in.Filter, limit, in.Offset, in.Sort)
			if err != nil {
				normalized := falcon.NormalizeError(ops.searchOp, "Failed to search "+in.PolicyType+" policies", err)
				if falcon.IsFQLError(normalized.StatusCode) {
					return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, in.Filter, fql.MustGuide(fqlGuideURI)))
				}
				return mcpx.JSONResult([]any{normalized})
			}
			if len(ids) == 0 {
				return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
			}
			resources, err := ops.twoStepGet(ctx, ids)
			if err != nil {
				normalized := falcon.NormalizeError(ops.searchOp, "Failed to get "+in.PolicyType+" policy details", err)
				return mcpx.JSONResult([]any{normalized})
			}
			return mcpx.JSONResult(resources)
		}

		// combined path
		resources, err := ops.combined(ctx, in.Filter, limit, in.Offset, in.Sort)
		if err != nil {
			normalized := falcon.NormalizeError(ops.searchOp, "Failed to search "+in.PolicyType+" policies", err)
			if falcon.IsFQLError(normalized.StatusCode) {
				return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, in.Filter, fql.MustGuide(fqlGuideURI)))
			}
			return mcpx.JSONResult([]any{normalized})
		}
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// searchPolicyMembersInput is the input for falcon_search_policy_members.
type searchPolicyMembersInput struct {
	PolicyType string  `json:"policy_type" jsonschema:"Policy type. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	ID         string  `json:"id" jsonschema:"The policy ID whose host members should be retrieved. If you don't have it, use falcon_search_policies to look it up."`
	Filter     *string `json:"filter,omitempty" jsonschema:"FQL filter expression on HOST attributes. See falcon://hosts/search/fql-guide for syntax."`
	Limit      int64   `json:"limit,omitempty" jsonschema:"Maximum records to return [1-5000]. Default 100."`
	Offset     *int64  `json:"offset,omitempty" jsonschema:"The offset to start retrieving records from."`
	Sort       *string `json:"sort,omitempty" jsonschema:"Sort members using host FQL sort syntax (e.g. 'hostname.asc', 'last_seen.desc')."`
}

func registerSearchPolicyMembers(s *mcp.Server, reg map[string]policyOps) {
	desc := "Search for the host members governed by a specific policy. Use this to list " +
		"the devices a policy is applied to. Requires the policy id; filters on HOST " +
		"attributes — consult falcon://hosts/search/fql-guide for filter syntax. Returns " +
		"full host device entities including device_id, hostname, platform_name, and network context."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_policy_members",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchPolicyMembersInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		limit := normalizeMembersLimit(in.Limit)
		resources, err := ops.members(ctx, in.ID, in.Filter, limit, in.Offset, in.Sort)
		if err != nil {
			normalized := falcon.NormalizeError(ops.membersOp, "Failed to search "+in.PolicyType+" policy members", err)
			return mcpx.JSONResult([]any{normalized})
		}
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// createPolicyInput is the input for falcon_create_policy.
type createPolicyInput struct {
	PolicyType   string  `json:"policy_type" jsonschema:"Policy type to create. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	Name         *string `json:"name,omitempty" jsonschema:"Name for the new policy. Required — omitting it returns a guiding error."`
	PlatformName *string `json:"platform_name,omitempty" jsonschema:"Target platform ('Windows', 'Mac', 'Linux'). Required for all types except content_update (which is platform-agnostic); omitting it for those types returns a guiding error."`
	Description  *string `json:"description,omitempty" jsonschema:"Description for the policy."`
	CloneID      *string `json:"clone_id,omitempty" jsonschema:"ID of an existing policy to clone settings from. An alternative to supplying settings directly."`
}

func registerCreatePolicy(s *mcp.Server, reg map[string]policyOps) {
	desc := "Create a host-based policy of the given type. Provide a name and (for every " +
		"type except content_update) a platform_name. New policies are created disabled. " +
		"Clone an existing policy with clone_id to inherit its settings, then adjust with " +
		"falcon_update_policy. Returns the created policy record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_policy",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createPolicyInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		if in.Name == nil || *in.Name == "" {
			e := falcon.ErrorResponse{Error: "Creating a " + in.PolicyType + " policy requires a 'name'."}
			return mcpx.JSONResult([]any{e})
		}

		platformName := ""
		if requiresPlatformCreate[in.PolicyType] {
			if in.PlatformName == nil || *in.PlatformName == "" {
				e := falcon.ErrorResponse{Error: "Creating a " + in.PolicyType + " policy requires a 'platform_name' (e.g. 'Windows', 'Mac', 'Linux')."}
				return mcpx.JSONResult([]any{e})
			}
			platformName = *in.PlatformName
		}

		description := ""
		if in.Description != nil {
			description = *in.Description
		}
		cloneID := ""
		if in.CloneID != nil {
			cloneID = *in.CloneID
		}

		resources, err := ops.create(ctx, *in.Name, platformName, description, nil, cloneID)
		if err != nil {
			normalized := falcon.NormalizeError(ops.createOp, "Failed to create "+in.PolicyType+" policy", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(resources)
	})
}

// updatePolicyInput is the input for falcon_update_policy.
type updatePolicyInput struct {
	PolicyType  string  `json:"policy_type" jsonschema:"Policy type to update. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	ID          *string `json:"id,omitempty" jsonschema:"ID of the policy to update. Required."`
	Name        *string `json:"name,omitempty" jsonschema:"New name for the policy."`
	Description *string `json:"description,omitempty" jsonschema:"New description for the policy."`
}

func registerUpdatePolicy(s *mcp.Server, reg map[string]policyOps) {
	desc := "Update an existing host-based policy of the given type. Provide the policy id " +
		"plus any fields to change (name, description). platform_name is not updatable after " +
		"creation. Unspecified fields are left unchanged. Returns the updated policy record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_policy",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updatePolicyInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		if in.ID == nil || *in.ID == "" {
			e := falcon.ErrorResponse{Error: "A policy 'id' is required to update a policy."}
			return mcpx.JSONResult([]any{e})
		}

		name := ""
		if in.Name != nil {
			name = *in.Name
		}
		description := ""
		if in.Description != nil {
			description = *in.Description
		}

		resources, err := ops.update(ctx, *in.ID, name, description, nil)
		if err != nil {
			normalized := falcon.NormalizeError(ops.updateOp, "Failed to update "+in.PolicyType+" policy", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(resources)
	})
}

// deletePoliciesInput is the input for falcon_delete_policies.
type deletePoliciesInput struct {
	PolicyType string   `json:"policy_type" jsonschema:"Policy type to delete. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	IDs        []string `json:"ids" jsonschema:"IDs of the policies to delete. A policy usually must be disabled before deletion (enabled policies return HTTP 400). Use falcon_perform_policy_action with action_name='disable' first."`
}

func registerDeletePolicies(s *mcp.Server, reg map[string]policyOps) {
	desc := "Delete one or more host-based policies of the given type. A policy usually must " +
		"be DISABLED before it can be deleted — an enabled policy returns HTTP 400. Disable it " +
		"first with falcon_perform_policy_action(action_name='disable'). The Default policy of " +
		"each type cannot be deleted. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_policies",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deletePoliciesInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "A non-empty 'ids' list is required to delete policies."}
			return mcpx.JSONResult([]any{e})
		}

		err := ops.delete(ctx, in.IDs)
		if err != nil {
			normalized := falcon.NormalizeError(ops.deleteOp, "Failed to delete "+in.PolicyType+" policies", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult([]any{})
	})
}

// performPolicyActionInput is the input for falcon_perform_policy_action.
type performPolicyActionInput struct {
	PolicyType string   `json:"policy_type" jsonschema:"Policy type. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	ActionName string   `json:"action_name" jsonschema:"The action to perform. Common to all types: 'enable', 'disable', 'add-host-group', 'remove-host-group'. prevention/sensor_update/response also allow 'add-rule-group'/'remove-rule-group'; content_update also allows 'override-allow'/'override-pause'/'override-revert'. The valid set is validated per type."`
	IDs        []string `json:"ids" jsonschema:"IDs of the policies to act on."`
	GroupID    *string  `json:"group_id,omitempty" jsonschema:"Group ID for group actions. Required for 'add-host-group'/'remove-host-group' (a host group ID) and 'add-rule-group'/'remove-rule-group' (a rule group ID); omit for other actions."`
}

func registerPerformPolicyAction(s *mcp.Server, reg map[string]policyOps) {
	desc := "Perform an action on one or more policies of the given type. Use this to " +
		"enable/disable policies or attach/detach host groups and rule groups. action_name is " +
		"validated against the actions valid for that policy_type. The add/remove-host-group and " +
		"add/remove-rule-group actions require a group_id. Returns the updated policy records."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_perform_policy_action",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in performPolicyActionInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		allowed := validActions[in.PolicyType]
		if !allowed[in.ActionName] {
			validList := sortedKeys(allowed)
			e := falcon.ErrorResponse{Error: "Invalid action_name '" + in.ActionName + "' for " + in.PolicyType + ". Valid actions are: " + joinStrings(validList) + "."}
			return mcpx.JSONResult([]any{e})
		}

		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "A non-empty 'ids' list is required to perform a policy action."}
			return mcpx.JSONResult([]any{e})
		}

		groupID := ""
		if needsGroupID(in.ActionName) {
			if in.GroupID == nil || *in.GroupID == "" {
				e := falcon.ErrorResponse{Error: "action_name '" + in.ActionName + "' requires a 'group_id'."}
				return mcpx.JSONResult([]any{e})
			}
			groupID = *in.GroupID
		}

		resources, err := ops.action(ctx, in.ActionName, in.IDs, groupID)
		if err != nil {
			normalized := falcon.NormalizeError(ops.actionOp, "Failed to perform "+in.ActionName+" on "+in.PolicyType+" policies", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult(resources)
	})
}

// setPolicyPrecedenceInput is the input for falcon_set_policy_precedence.
type setPolicyPrecedenceInput struct {
	PolicyType   string   `json:"policy_type" jsonschema:"Policy type. One of: 'prevention', 'sensor_update', 'firewall', 'device_control', 'response', 'content_update'."`
	IDs          []string `json:"ids" jsonschema:"The COMPLETE ordered list of non-Default policy IDs for the platform, highest precedence first. Partial lists are rejected by the API."`
	PlatformName *string  `json:"platform_name,omitempty" jsonschema:"Target platform ('Windows', 'Mac', 'Linux'). Required for all types EXCEPT content_update."`
}

func registerSetPolicyPrecedence(s *mcp.Server, reg map[string]policyOps) {
	desc := "Set the precedence (evaluation order) of policies for a platform. The ids list " +
		"must be the COMPLETE ordered set of non-Default policies for the given platform — the " +
		"first id is highest precedence. Partial lists are rejected by the API. platform_name " +
		"is required for every type except content_update. Returns the API response."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_set_policy_precedence",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in setPolicyPrecedenceInput) (*mcp.CallToolResult, any, error) {
		ops, typeErr := lookupOps(reg, in.PolicyType)
		if typeErr != nil {
			return mcpx.JSONResult([]any{typeErr})
		}

		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "A non-empty 'ids' list is required to set policy precedence."}
			return mcpx.JSONResult([]any{e})
		}

		platformName := ""
		if requiresPlatformPrecedence[in.PolicyType] {
			if in.PlatformName == nil || *in.PlatformName == "" {
				e := falcon.ErrorResponse{Error: "Setting precedence for " + in.PolicyType + " policies requires a 'platform_name'."}
				return mcpx.JSONResult([]any{e})
			}
			platformName = *in.PlatformName
		}

		err := ops.precedence(ctx, in.IDs, platformName)
		if err != nil {
			normalized := falcon.NormalizeError(ops.precedenceOp, "Failed to set "+in.PolicyType+" policy precedence", err)
			return mcpx.JSONResult([]any{normalized})
		}
		return mcpx.JSONResult([]any{})
	})
}

// --- helpers ---

// lookupOps validates policy_type and returns the corresponding policyOps or an
// ErrorResponse if the type is not recognized.
func lookupOps(reg map[string]policyOps, policyType string) (policyOps, *falcon.ErrorResponse) {
	ops, ok := reg[policyType]
	if !ok {
		e := falcon.ErrorResponse{
			Error: "Invalid policy_type '" + policyType + "'. Valid values are: " + joinStrings(validPolicyTypes) + ".",
		}
		return policyOps{}, &e
	}
	return ops, nil
}

// validateSort rejects platform_name and unknown sort fields (would cause HTTP 500).
func validateSort(sort *string) *falcon.ErrorResponse {
	if sort == nil || *sort == "" {
		return nil
	}
	base := sortBase(*sort)
	if base == "platform_name" {
		e := falcon.ErrorResponse{Error: "Sorting by 'platform_name' is not supported — it returns HTTP 500. Use one of: name, created_timestamp, modified_timestamp, enabled, created_by, modified_by, precedence."}
		return &e
	}
	if !safeSearchSortFields[base] {
		e := falcon.ErrorResponse{Error: "Invalid sort field '" + base + "'. Valid sort fields: name, created_timestamp, modified_timestamp, enabled, created_by, modified_by, precedence."}
		return &e
	}
	return nil
}

// sortBase extracts the field name from a sort expression like "name.asc" or "name|desc".
func sortBase(sort string) string {
	for i, c := range sort {
		if c == '.' || c == '|' {
			return sort[:i]
		}
	}
	return sort
}

// buildActionBody creates the MsaEntityActionRequestV2 body for perform-action calls.
// If groupID is non-empty it is appended as an action_parameter named "group_id".
func buildActionBody(ids []string, groupID string) *models.MsaEntityActionRequestV2 {
	body := &models.MsaEntityActionRequestV2{Ids: ids}
	if groupID != "" {
		name := "group_id"
		body.ActionParameters = []*models.MsaspecActionParameter{
			{Name: &name, Value: &groupID},
		}
	}
	return body
}

// needsGroupID reports whether the given action_name requires a group_id parameter.
func needsGroupID(actionName string) bool {
	switch actionName {
	case "add-host-group", "remove-host-group", "add-rule-group", "remove-rule-group":
		return true
	}
	return false
}

// normalizeLimit clamps the requested search limit to [1, 500], defaulting to 100.
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 500 {
		return 500
	}
	return limit
}

// normalizeMembersLimit clamps the members limit to [1, 5000], defaulting to 100.
func normalizeMembersLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 5000 {
		return 5000
	}
	return limit
}

// toAnySlice converts a typed slice to []any for uniform JSON serialization.
func toAnySlice[T any](in []T) []any {
	out := make([]any, len(in))
	for i, v := range in {
		out[i] = v
	}
	return out
}

// joinStrings joins a []string with ", ".
func joinStrings(ss []string) string {
	result := ""
	for i, s := range ss {
		if i > 0 {
			result += ", "
		}
		result += s
	}
	return result
}

// sortedKeys returns the keys of a map[string]bool in sorted order.
func sortedKeys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	// simple insertion sort (small N)
	for i := 1; i < len(out); i++ {
		for j := i; j > 0 && out[j] < out[j-1]; j-- {
			out[j], out[j-1] = out[j-1], out[j]
		}
	}
	return out
}
