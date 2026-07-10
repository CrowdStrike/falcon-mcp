package hostgroups

import (
	"context"
	"fmt"

	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// validGroupTypes are the accepted group_type values for create_host_group.
var validGroupTypes = map[string]bool{
	"static": true, "staticByID": true, "dynamic": true,
}

// validActions are the accepted action_name values for
// perform_host_group_action.
var validActions = map[string]bool{
	"add-hosts": true, "remove-hosts": true,
}

// CreateInput is the input for falcon_create_host_group.
type CreateInput struct {
	Name           string `json:"name" jsonschema:"the name of the group (required)"`
	GroupType      string `json:"group_type" jsonschema:"static, staticByID, or dynamic (required)"`
	Description    string `json:"description,omitempty" jsonschema:"an optional description of the group"`
	AssignmentRule string `json:"assignment_rule,omitempty" jsonschema:"host FQL assignment rule; required for dynamic groups, rejected for static/staticByID"`
}

func (m *Module) createHostGroup(ctx context.Context, _ *mcp.CallToolRequest, in CreateInput) (*mcp.CallToolResult, base.EntitiesResult[*models.HostGroupsHostGroupV1], error) {
	var zero base.EntitiesResult[*models.HostGroupsHostGroupV1]
	if err := in.validate(); err != nil {
		return nil, zero, err
	}
	m.Logger.Debug("create_host_group", "name", in.Name, "group_type", in.GroupType, "has_rule", in.AssignmentRule != "")

	params := host_group.NewCreateHostGroupsParamsWithContext(ctx)
	params.Body = &models.HostGroupsCreateGroupsReqV1{
		Resources: []*models.HostGroupsCreateGroupReqV1{{
			Name:           &in.Name,
			GroupType:      &in.GroupType,
			Description:    in.Description,
			AssignmentRule: in.AssignmentRule,
		}},
	}

	resp, err := m.API.CreateHostGroups(params)
	if e := base.APIError(err, resp, scopeHostGroupWrite); e != nil {
		return nil, zero, e
	}
	return nil, base.Entities(resp.Payload.Resources), nil
}

// validate enforces the client-side constraints on a create request: the API
// rejects an assignment rule on non-dynamic groups, so fail fast here.
func (in CreateInput) validate() error {
	if in.Name == "" {
		return wrapInvalid("create host group", "name must not be empty")
	}
	if !validGroupTypes[in.GroupType] {
		return wrapInvalid("create host group", fmt.Sprintf("invalid group_type %q (want static, staticByID, or dynamic)", in.GroupType))
	}
	if in.AssignmentRule != "" && in.GroupType != "dynamic" {
		return wrapInvalid("create host group", "assignment_rule is only valid for dynamic groups")
	}
	return nil
}

// UpdateInput is the input for falcon_update_host_group. Only the fields that
// are set are sent; unspecified fields are left unchanged. AssignmentRule is a
// pointer so an explicit empty string can be distinguished from "unset".
type UpdateInput struct {
	ID             string  `json:"id" jsonschema:"the ID of the group to update (required)"`
	Name           string  `json:"name,omitempty" jsonschema:"new name for the group"`
	Description    string  `json:"description,omitempty" jsonschema:"new description for the group"`
	AssignmentRule *string `json:"assignment_rule,omitempty" jsonschema:"new host FQL assignment rule; only set on dynamic groups"`
}

func (m *Module) updateHostGroup(ctx context.Context, _ *mcp.CallToolRequest, in UpdateInput) (*mcp.CallToolResult, base.EntitiesResult[*models.HostGroupsHostGroupV1], error) {
	var zero base.EntitiesResult[*models.HostGroupsHostGroupV1]
	if in.ID == "" {
		return nil, zero, wrapInvalid("update host group", "id must not be empty")
	}
	m.Logger.Debug("update_host_group", "id", in.ID, "set_name", in.Name != "", "set_description", in.Description != "", "set_rule", in.AssignmentRule != nil)

	resource := &models.HostGroupsUpdateGroupReqV1{
		ID:          &in.ID,
		Name:        in.Name,
		Description: in.Description,
	}
	if in.AssignmentRule != nil {
		resource.AssignmentRule = in.AssignmentRule
	}

	params := host_group.NewUpdateHostGroupsParamsWithContext(ctx)
	params.Body = &models.HostGroupsUpdateGroupsReqV1{
		Resources: []*models.HostGroupsUpdateGroupReqV1{resource},
	}

	resp, err := m.API.UpdateHostGroups(params)
	if e := base.APIError(err, resp, scopeHostGroupWrite); e != nil {
		return nil, zero, e
	}
	return nil, base.Entities(resp.Payload.Resources), nil
}

// DeleteInput is the input for falcon_delete_host_groups.
type DeleteInput struct {
	IDs []string `json:"ids" jsonschema:"IDs of the host groups to delete (required, non-empty)"`
}

func (m *Module) deleteHostGroups(ctx context.Context, _ *mcp.CallToolRequest, in DeleteInput) (*mcp.CallToolResult, base.ActionResult, error) {
	if len(in.IDs) == 0 {
		return nil, base.ActionResult{}, wrapInvalid("delete host groups", "ids must not be empty")
	}
	m.Logger.Debug("delete_host_groups", "ids", len(in.IDs))

	params := host_group.NewDeleteHostGroupsParamsWithContext(ctx)
	params.Ids = in.IDs

	resp, err := m.API.DeleteHostGroups(params)
	if e := base.APIError(err, resp, scopeHostGroupWrite); e != nil {
		return nil, base.ActionResult{}, e
	}
	return nil, base.ActionResult{Ok: true}, nil
}

// ActionInput is the input for falcon_perform_host_group_action.
type ActionInput struct {
	ActionName string   `json:"action_name" jsonschema:"add-hosts or remove-hosts (required)"`
	IDs        []string `json:"ids" jsonschema:"IDs of the target static host groups (required)"`
	Filter     string   `json:"filter" jsonschema:"host/device FQL selecting which hosts to add or remove (required)"`
}

func (m *Module) performHostGroupAction(ctx context.Context, _ *mcp.CallToolRequest, in ActionInput) (*mcp.CallToolResult, base.EntitiesResult[*models.HostGroupsHostGroupV1], error) {
	var zero base.EntitiesResult[*models.HostGroupsHostGroupV1]
	if err := in.validate(); err != nil {
		return nil, zero, err
	}
	m.Logger.Debug("perform_host_group_action", "action_name", in.ActionName, "ids", len(in.IDs), "filter", in.Filter)

	params := host_group.NewPerformGroupActionParamsWithContext(ctx)
	params.ActionName = in.ActionName
	params.Body = &models.MsaEntityActionRequestV2{
		Ids: in.IDs,
		ActionParameters: []*models.MsaspecActionParameter{
			{Name: ptr("filter"), Value: &in.Filter},
		},
	}

	resp, err := m.API.PerformGroupAction(params)
	if e := base.APIError(err, resp, scopeHostGroupWrite); e != nil {
		return nil, zero, e
	}
	return nil, base.Entities(resp.Payload.Resources), nil
}

// validate enforces the client-side constraints on a membership action.
func (in ActionInput) validate() error {
	if !validActions[in.ActionName] {
		return wrapInvalid("perform host group action", fmt.Sprintf("invalid action_name %q (want add-hosts or remove-hosts)", in.ActionName))
	}
	if len(in.IDs) == 0 {
		return wrapInvalid("perform host group action", "ids must not be empty")
	}
	if in.Filter == "" {
		return wrapInvalid("perform host group action", "filter must not be empty")
	}
	return nil
}

// wrapInvalid builds an errInvalidInput-wrapped error for op with detail.
func wrapInvalid(op, detail string) error {
	return fmt.Errorf("%s: %w: %s", op, errInvalidInput, detail)
}

// ptr returns a pointer to v.
func ptr[T any](v T) *T { return &v }
