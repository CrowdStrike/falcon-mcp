// Package host_groups implements the Falcon MCP "host_groups" toolset: searching,
// creating, updating, deleting host groups, and managing their membership. The two
// search operations are single-step combined calls that return full group or member
// resources directly; the four mutation tools follow the standard write pattern.
package host_groups

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://host-groups/search/fql-guide"
)

// HostGroupAPI is the narrow slice of the gofalcon host_group client this
// toolset uses. Declaring it as an interface keeps handlers unit-testable with
// a hand-written mock.
type HostGroupAPI interface {
	QueryCombinedHostGroups(*host_group.QueryCombinedHostGroupsParams, ...host_group.ClientOption) (*host_group.QueryCombinedHostGroupsOK, error)
	QueryCombinedGroupMembers(*host_group.QueryCombinedGroupMembersParams, ...host_group.ClientOption) (*host_group.QueryCombinedGroupMembersOK, error)
	CreateHostGroups(*host_group.CreateHostGroupsParams, ...host_group.ClientOption) (*host_group.CreateHostGroupsCreated, error)
	UpdateHostGroups(*host_group.UpdateHostGroupsParams, ...host_group.ClientOption) (*host_group.UpdateHostGroupsOK, error)
	DeleteHostGroups(*host_group.DeleteHostGroupsParams, ...host_group.ClientOption) (*host_group.DeleteHostGroupsOK, error)
	PerformGroupAction(*host_group.PerformGroupActionParams, ...host_group.ClientOption) (*host_group.PerformGroupActionOK, error)
}

// Toolset is the host_groups domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "host_groups" }

func (Toolset) GetDescription() string {
	return "Search, create, update, and delete CrowdStrike Falcon host groups, and manage group membership."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_host_groups_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_host_groups` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_host_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchHostGroups(s, fc.HostGroup())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_host_group_members"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchHostGroupMembers(s, fc.HostGroup())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_host_group"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateHostGroup(s, fc.HostGroup())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_host_group"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateHostGroup(s, fc.HostGroup())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_host_groups"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteHostGroups(s, fc.HostGroup())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_perform_host_group_action"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerPerformHostGroupAction(s, fc.HostGroup())
			},
		},
	}
}

// --- falcon_search_host_groups ---

type searchHostGroupsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://host-groups/search/fql-guide for syntax. Examples: group_type:'static', name:'Production Servers'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum records to return [1-5000]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"The offset to start retrieving records from."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort host groups. Fields: name, group_type, created_by, created_timestamp, modified_by, modified_timestamp. Direction: asc or desc. Examples: 'name.asc', 'created_timestamp.desc'."`
}

func registerSearchHostGroups(s *mcp.Server, api HostGroupAPI) {
	desc := "Search for host groups in your CrowdStrike environment. Use this to find host groups " +
		"by name, type, creator, or timestamps. Consult " +
		"falcon://host-groups/search/fql-guide before constructing filter expressions. Returns full " +
		"host group details including id, name, group_type, description, and audit metadata in a " +
		"single call."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_host_groups",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchHostGroupsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		sort := defaultSort(in.Sort)

		qp := host_group.NewQueryCombinedHostGroupsParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = sort

		resp, err := api.QueryCombinedHostGroups(qp)
		if err != nil {
			return searchErr("queryCombinedHostGroups", "Failed to search host groups", in.Filter, fqlGuideURI, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_search_host_group_members ---

type searchHostGroupMembersInput struct {
	ID     string  `json:"id" jsonschema:"The host group ID whose members should be retrieved. If you don't already have it, use falcon_search_host_groups to look it up."`
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression on HOST attributes. See falcon://hosts/search/fql-guide for syntax. Examples: platform_name:'Windows', hostname:'PC*'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum records to return [1-5000]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"The offset to start retrieving records from."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort members using host FQL sort syntax. Examples: 'hostname.asc', 'last_seen.desc'."`
}

func registerSearchHostGroupMembers(s *mcp.Server, api HostGroupAPI) {
	desc := "Search for the host members of a specific host group. Use this to list the devices " +
		"that belong to a host group. Requires the group `id` and filters on HOST attributes " +
		"(platform, hostname, etc.) — consult falcon://hosts/search/fql-guide for the filter " +
		"syntax. Returns full host device entities including device_id, hostname, platform, and " +
		"network context."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_host_group_members",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchHostGroupMembersInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		qp := host_group.NewQueryCombinedGroupMembersParamsWithContext(ctx)
		qp.ID = &in.ID
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		resp, err := api.QueryCombinedGroupMembers(qp)
		if err != nil {
			normalized := falcon.NormalizeError("queryCombinedGroupMembers", "Failed to search host group members", err)
			return mcpx.JSONResult([]any{normalized})
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_create_host_group ---

type createHostGroupInput struct {
	Name           string  `json:"name" jsonschema:"Name for the new host group."`
	GroupType      string  `json:"group_type" jsonschema:"Type of host group. One of: 'static' (hosts added manually by ID via falcon_perform_host_group_action), 'staticByID' (same, populated after creation), or 'dynamic' (hosts matched automatically by an assignment_rule)."`
	Description    *string `json:"description,omitempty" jsonschema:"Description for the host group."`
	AssignmentRule *string `json:"assignment_rule,omitempty" jsonschema:"FQL assignment rule for dynamic groups (e.g. platform_name:'Windows'). Required for 'dynamic' groups; the API rejects it for 'static'/'staticByID' groups."`
}

func registerCreateHostGroup(s *mcp.Server, api HostGroupAPI) {
	desc := "Create a host group. Provide a name and group_type. 'dynamic' groups take an " +
		"assignment_rule (host FQL) that automatically includes matching hosts. 'static' and " +
		"'staticByID' groups are created empty (no assignment_rule) and populated afterwards via " +
		"falcon_perform_host_group_action. Returns the created host group record on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_host_group",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createHostGroupInput) (*mcp.CallToolResult, any, error) {
		resource := &models.HostGroupsCreateGroupReqV1{
			Name:      &in.Name,
			GroupType: &in.GroupType,
		}
		if in.Description != nil {
			resource.Description = *in.Description
		}
		if in.AssignmentRule != nil {
			resource.AssignmentRule = *in.AssignmentRule
		}

		p := host_group.NewCreateHostGroupsParamsWithContext(ctx)
		p.Body = &models.HostGroupsCreateGroupsReqV1{
			Resources: []*models.HostGroupsCreateGroupReqV1{resource},
		}

		resp, err := api.CreateHostGroups(p)
		if err != nil {
			e := falcon.NormalizeError("createHostGroups", "Failed to create host group", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_host_group ---

type updateHostGroupInput struct {
	ID             string  `json:"id" jsonschema:"The host group ID to update. If you don't already have it, use falcon_search_host_groups to look it up."`
	Name           *string `json:"name,omitempty" jsonschema:"New name for the host group."`
	Description    *string `json:"description,omitempty" jsonschema:"New description for the host group."`
	AssignmentRule *string `json:"assignment_rule,omitempty" jsonschema:"New FQL assignment rule (e.g. platform_name:'Windows'). Only set this for 'dynamic' groups. The API does not block setting it on 'static'/'staticByID' groups, but doing so leaves the group in an inconsistent state and should be avoided."`
}

func registerUpdateHostGroup(s *mcp.Server, api HostGroupAPI) {
	desc := "Update an existing host group. Provide the group `id` and any fields to change. " +
		"name and description are safe for any group type; only set assignment_rule on 'dynamic' " +
		"groups. Unspecified fields are left unchanged. Returns the updated host group record on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_host_group",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateHostGroupInput) (*mcp.CallToolResult, any, error) {
		resource := &models.HostGroupsUpdateGroupReqV1{
			ID: &in.ID,
		}
		if in.Name != nil {
			resource.Name = *in.Name
		}
		if in.Description != nil {
			resource.Description = *in.Description
		}
		if in.AssignmentRule != nil {
			resource.AssignmentRule = in.AssignmentRule
		}

		p := host_group.NewUpdateHostGroupsParamsWithContext(ctx)
		p.Body = &models.HostGroupsUpdateGroupsReqV1{
			Resources: []*models.HostGroupsUpdateGroupReqV1{resource},
		}

		resp, err := api.UpdateHostGroups(p)
		if err != nil {
			e := falcon.NormalizeError("updateHostGroups", "Failed to update host group", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_delete_host_groups ---

type deleteHostGroupsInput struct {
	IDs []string `json:"ids" jsonschema:"Host group IDs to delete. If you don't already have them, use falcon_search_host_groups to look them up."`
}

func registerDeleteHostGroups(s *mcp.Server, api HostGroupAPI) {
	desc := "Delete one or more host groups. Provide the host group `ids` to delete. This " +
		"permanently removes the groups. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_host_groups",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteHostGroupsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "Failed to delete host groups: `ids` must be provided to delete host groups."}
			return mcpx.JSONResult([]any{e})
		}

		p := host_group.NewDeleteHostGroupsParamsWithContext(ctx)
		p.Ids = in.IDs

		_, err := api.DeleteHostGroups(p)
		if err != nil {
			e := falcon.NormalizeError("deleteHostGroups", "Failed to delete host groups", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult([]any{})
	})
}

// --- falcon_perform_host_group_action ---

type performHostGroupActionInput struct {
	ActionName string   `json:"action_name" jsonschema:"The membership action to perform. Either 'add-hosts' or 'remove-hosts'."`
	IDs        []string `json:"ids" jsonschema:"Host group IDs to add hosts to or remove hosts from. If you don't already have them, use falcon_search_host_groups to look them up."`
	Filter     string   `json:"filter" jsonschema:"Host FQL expression selecting which hosts to add or remove (e.g. device_id:['id1','id2'] or platform_name:'Windows'). See falcon://hosts/search/fql-guide for syntax."`
}

func registerPerformHostGroupAction(s *mcp.Server, api HostGroupAPI) {
	desc := "Add or remove hosts from one or more host groups. Set action_name to 'add-hosts' or " +
		"'remove-hosts', provide the target group `ids`, and a host FQL filter selecting which " +
		"hosts to act on. Applies only to static groups. Returns the updated host group records on success."

	filterName := "filter"
	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_perform_host_group_action",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in performHostGroupActionInput) (*mcp.CallToolResult, any, error) {
		p := host_group.NewPerformGroupActionParamsWithContext(ctx)
		p.ActionName = in.ActionName
		p.Body = &models.MsaEntityActionRequestV2{
			Ids: in.IDs,
			ActionParameters: []*models.MsaspecActionParameter{
				{Name: &filterName, Value: &in.Filter},
			},
		}

		resp, err := api.PerformGroupAction(p)
		if err != nil {
			e := falcon.NormalizeError("performGroupAction", "Failed to perform host group action", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- helpers ---

// searchErr normalizes a search error, surfacing the FQL guide on 400 errors.
func searchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to [1, 5000], defaulting to 100.
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 5000 {
		return 5000
	}
	return limit
}

// defaultSort returns "name.asc" when no sort is specified, matching the Python default.
func defaultSort(sort *string) *string {
	if sort != nil {
		return sort
	}
	s := "name.asc"
	return &s
}
