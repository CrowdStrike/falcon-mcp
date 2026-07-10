// Package hostgroups implements the six host-group tools over the gofalcon
// host_group client: searching groups and their member devices, creating,
// updating, and deleting groups, and adding or removing hosts from static
// groups. It registers the host-groups FQL guide resource.
//
// Two FQL dialects apply here and must not be mixed: searching groups uses
// host-group fields (name, group_type, created_by, timestamps), while member
// search and the membership action filter on host/device attributes.
package hostgroups

import (
	"context"
	"errors"
	"log/slog"

	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
	"github.com/crowdstrike/falcon-mcp/internal/modules/registry"
)

// Factory builds the host-groups module from shared deps. The generated
// aggregator (internal/mcpserver) collects it, so the module needs no init
// side effect. This module does no bulk detail fetch, so it ignores
// Deps.Concurrency.
var Factory registry.Factory = func(d registry.Deps) base.Module {
	return &Module{API: d.API.HostGroup, Logger: d.Logger}
}

// errInvalidInput classifies client-side validation failures in the mutating
// and member-search tools.
var errInvalidInput = errors.New("hostgroups: invalid input")

// defaultLimit is the search page size applied when the caller omits limit.
const defaultLimit = 100

// defaultSort is the group search ordering applied when the caller omits sort.
const defaultSort = "name.asc"

// CrowdStrike API scopes required by this module's operations. Surfaced on a
// 403 via base.APIError, referenced directly at each call site.
var (
	scopeHostGroupRead  = base.Scope{Name: "host-group", Read: true}
	scopeHostGroupWrite = base.Scope{Name: "host-group", Write: true}
)

// hostGroupAPI is the minimal slice of the gofalcon host_group client this
// module consumes, declared next to its consumer so handlers can be tested
// against a tiny fake rather than all of gofalcon.
type hostGroupAPI interface {
	QueryCombinedHostGroups(params *host_group.QueryCombinedHostGroupsParams, opts ...host_group.ClientOption) (*host_group.QueryCombinedHostGroupsOK, error)
	QueryCombinedGroupMembers(params *host_group.QueryCombinedGroupMembersParams, opts ...host_group.ClientOption) (*host_group.QueryCombinedGroupMembersOK, error)
	CreateHostGroups(params *host_group.CreateHostGroupsParams, opts ...host_group.ClientOption) (*host_group.CreateHostGroupsCreated, error)
	UpdateHostGroups(params *host_group.UpdateHostGroupsParams, opts ...host_group.ClientOption) (*host_group.UpdateHostGroupsOK, error)
	DeleteHostGroups(params *host_group.DeleteHostGroupsParams, opts ...host_group.ClientOption) (*host_group.DeleteHostGroupsOK, error)
	PerformGroupAction(params *host_group.PerformGroupActionParams, opts ...host_group.ClientOption) (*host_group.PerformGroupActionOK, error)
}

// Module registers the host-groups tools. It holds only the shared, concurrency-
// safe Falcon client and configuration; handlers are stateless and reentrant.
// Logger must be non-nil.
type Module struct {
	API    hostGroupAPI
	Logger *slog.Logger
}

// Name reports the module name.
func (m *Module) Name() string { return "host_groups" }

// Description reports a one-line summary of the module.
func (m *Module) Description() string {
	return "Search, create, update, and delete Falcon host groups and manage their membership"
}

// RegisterTools registers the six host-group tools into r.
func (m *Module) RegisterTools(r base.Registrar) {
	base.AddTool(r, &mcp.Tool{
		Name:        "search_host_groups",
		Description: "Search host groups in CrowdStrike Falcon using host-group FQL (fields: name, group_type, created_by, created_timestamp, modified_by, modified_timestamp). Returns full group records.",
	}, m.searchHostGroups)

	base.AddTool(r, &mcp.Tool{
		Name:        "search_host_group_members",
		Description: "List the member devices of a host group. The filter and sort operate on HOST/DEVICE attributes (e.g. platform_name, hostname), not group attributes — see the hosts FQL guide. Returns full host device records.",
	}, m.searchHostGroupMembers)

	base.AddTool(r, &mcp.Tool{
		Name:        "create_host_group",
		Description: "Create a host group of type static, staticByID, or dynamic. A dynamic group requires an assignment_rule (host FQL); the API rejects an assignment_rule on static and staticByID groups.",
		Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, IdempotentHint: false},
	}, m.createHostGroup)

	base.AddTool(r, &mcp.Tool{
		Name:        "update_host_group",
		Description: "Update a host group's name, description, or assignment_rule. Unspecified fields are left unchanged. Only set assignment_rule on dynamic groups.",
		Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, IdempotentHint: false},
	}, m.updateHostGroup)

	base.AddTool(r, &mcp.Tool{
		Name:        "delete_host_groups",
		Description: "Permanently delete one or more host groups by ID. Idempotent.",
		Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, IdempotentHint: true, DestructiveHint: ptr(true)},
	}, m.deleteHostGroups)

	base.AddTool(r, &mcp.Tool{
		Name:        "perform_host_group_action",
		Description: "Add or remove hosts from static host groups. The filter selects which hosts to act on using HOST/DEVICE FQL (see the hosts FQL guide). Applies to static groups only.",
		Annotations: &mcp.ToolAnnotations{ReadOnlyHint: false, IdempotentHint: false},
	}, m.performHostGroupAction)
}

// RegisterResources publishes the host-groups FQL guide as an MCP resource,
// mirroring falcon-mcp's falcon://host-groups/search/fql-guide resource.
func (m *Module) RegisterResources(s *mcp.Server) {
	base.TextResource(s,
		fqlGuideURI,
		"search_host_groups_fql_guide",
		"Contains the guide for the `filter` param of the `falcon_search_host_groups` tool.",
		"text/markdown",
		fqlGuide,
	)
}

// SearchInput is the input for falcon_search_host_groups.
type SearchInput struct {
	Filter string `json:"filter,omitempty" jsonschema:"host-group FQL filter (e.g. name:'Servers*', group_type:'static')"`
	Limit  int    `json:"limit,omitempty" jsonschema:"maximum results to return (1-5000, default 100)"`
	Offset int    `json:"offset,omitempty" jsonschema:"pagination offset"`
	Sort   string `json:"sort,omitempty" jsonschema:"host-group FQL sort (e.g. name.asc, modified_timestamp.desc); default name.asc"`
}

func (m *Module) searchHostGroups(ctx context.Context, _ *mcp.CallToolRequest, in SearchInput) (*mcp.CallToolResult, base.SearchResult[*models.HostGroupsHostGroupV1], error) {
	var zero base.SearchResult[*models.HostGroupsHostGroupV1]
	limit := int64(in.Limit)
	if limit == 0 {
		limit = defaultLimit
	}
	sort := in.Sort
	if sort == "" {
		sort = defaultSort
	}
	m.Logger.Debug("search_host_groups", "filter", in.Filter, "limit", limit, "offset", in.Offset, "sort", sort)

	params := host_group.NewQueryCombinedHostGroupsParamsWithContext(ctx)
	params.Limit = &limit
	params.Sort = &sort
	if in.Filter != "" {
		params.Filter = &in.Filter
	}
	if in.Offset != 0 {
		offset := int64(in.Offset)
		params.Offset = &offset
	}

	resp, err := m.API.QueryCombinedHostGroups(params)
	if err != nil {
		if details, ok := groupsFQLBadRequest(err); ok {
			return nil, base.FQLError[*models.HostGroupsHostGroupV1](details, in.Filter, fqlGuide), nil
		}
	}
	if e := base.APIError(err, resp, scopeHostGroupRead); e != nil {
		return nil, zero, e
	}

	groups := resp.Payload.Resources
	m.Logger.Debug("search_host_groups query complete", "matched", len(groups))
	return nil, base.Found(groups, in.Filter), nil
}

// MembersInput is the input for falcon_search_host_group_members.
type MembersInput struct {
	ID     string `json:"id" jsonschema:"the host group ID whose members to list (required)"`
	Filter string `json:"filter,omitempty" jsonschema:"host/device FQL filter on member attributes (e.g. platform_name:'Windows')"`
	Limit  int    `json:"limit,omitempty" jsonschema:"maximum results to return (1-5000, default 100)"`
	Offset int    `json:"offset,omitempty" jsonschema:"pagination offset"`
	Sort   string `json:"sort,omitempty" jsonschema:"host/device FQL sort (e.g. hostname.asc)"`
}

func (m *Module) searchHostGroupMembers(ctx context.Context, _ *mcp.CallToolRequest, in MembersInput) (*mcp.CallToolResult, base.SearchResult[*models.DeviceDevice], error) {
	var zero base.SearchResult[*models.DeviceDevice]
	if in.ID == "" {
		return nil, zero, wrapInvalid("search host group members", "id must not be empty")
	}
	limit := int64(in.Limit)
	if limit == 0 {
		limit = defaultLimit
	}
	m.Logger.Debug("search_host_group_members", "id", in.ID, "filter", in.Filter, "limit", limit, "offset", in.Offset, "sort", in.Sort)

	params := host_group.NewQueryCombinedGroupMembersParamsWithContext(ctx)
	params.ID = &in.ID
	params.Limit = &limit
	if in.Filter != "" {
		params.Filter = &in.Filter
	}
	if in.Offset != 0 {
		offset := int64(in.Offset)
		params.Offset = &offset
	}
	if in.Sort != "" {
		params.Sort = &in.Sort
	}

	resp, err := m.API.QueryCombinedGroupMembers(params)
	if err != nil {
		if details, ok := membersFQLBadRequest(err); ok {
			return nil, base.FQLError[*models.DeviceDevice](details, in.Filter, fqlGuide), nil
		}
	}
	if e := base.APIError(err, resp, scopeHostGroupRead); e != nil {
		return nil, zero, e
	}

	members := resp.Payload.Resources
	m.Logger.Debug("search_host_group_members query complete", "matched", len(members))
	return nil, base.Found(members, in.Filter), nil
}

// groupsFQLBadRequest reports whether err is a 400-class host-group query error
// and, if so, extracts the API error details for an FQL-error response. gofalcon
// surfaces 400s as a typed *host_group.QueryCombinedHostGroupsBadRequest;
// classify with errors.As rather than string matching.
func groupsFQLBadRequest(err error) ([]base.FQLErrorDetail, bool) {
	var badReq *host_group.QueryCombinedHostGroupsBadRequest
	if !errors.As(err, &badReq) || badReq.Payload == nil {
		return nil, false
	}
	return apiErrorDetails(badReq.Payload.Errors), true
}

// membersFQLBadRequest is the member-search counterpart of groupsFQLBadRequest.
func membersFQLBadRequest(err error) ([]base.FQLErrorDetail, bool) {
	var badReq *host_group.QueryCombinedGroupMembersBadRequest
	if !errors.As(err, &badReq) || badReq.Payload == nil {
		return nil, false
	}
	return apiErrorDetails(badReq.Payload.Errors), true
}

// apiErrorDetails flattens gofalcon MsaAPIError values into base.FQLErrorDetail.
func apiErrorDetails(errs []*models.MsaAPIError) []base.FQLErrorDetail {
	details := make([]base.FQLErrorDetail, 0, len(errs))
	for _, e := range errs {
		if e == nil {
			continue
		}
		var code int32
		if e.Code != nil {
			code = *e.Code
		}
		var msg string
		if e.Message != nil {
			msg = *e.Message
		}
		details = append(details, base.FQLErrorDetail{Code: code, Message: msg})
	}
	return details
}
