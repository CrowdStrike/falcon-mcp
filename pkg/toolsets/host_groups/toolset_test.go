package host_groups

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// mockHostGroupAPI is a hand-written mock satisfying the narrow HostGroupAPI
// interface. Each field lets a test supply a canned response or error for one
// operation, and captures the params the toolset actually sent.
type mockHostGroupAPI struct {
	searchGroupsResp *host_group.QueryCombinedHostGroupsOK
	searchGroupsErr  error
	searchGroupsGot  *host_group.QueryCombinedHostGroupsParams

	searchMembersResp *host_group.QueryCombinedGroupMembersOK
	searchMembersErr  error
	searchMembersGot  *host_group.QueryCombinedGroupMembersParams

	createResp *host_group.CreateHostGroupsCreated
	createErr  error
	createGot  *host_group.CreateHostGroupsParams

	updateResp *host_group.UpdateHostGroupsOK
	updateErr  error
	updateGot  *host_group.UpdateHostGroupsParams

	deleteResp *host_group.DeleteHostGroupsOK
	deleteErr  error
	deleteGot  *host_group.DeleteHostGroupsParams

	performResp *host_group.PerformGroupActionOK
	performErr  error
	performGot  *host_group.PerformGroupActionParams
}

func (m *mockHostGroupAPI) QueryCombinedHostGroups(p *host_group.QueryCombinedHostGroupsParams, _ ...host_group.ClientOption) (*host_group.QueryCombinedHostGroupsOK, error) {
	m.searchGroupsGot = p
	return m.searchGroupsResp, m.searchGroupsErr
}

func (m *mockHostGroupAPI) QueryCombinedGroupMembers(p *host_group.QueryCombinedGroupMembersParams, _ ...host_group.ClientOption) (*host_group.QueryCombinedGroupMembersOK, error) {
	m.searchMembersGot = p
	return m.searchMembersResp, m.searchMembersErr
}

func (m *mockHostGroupAPI) CreateHostGroups(p *host_group.CreateHostGroupsParams, _ ...host_group.ClientOption) (*host_group.CreateHostGroupsCreated, error) {
	m.createGot = p
	return m.createResp, m.createErr
}

func (m *mockHostGroupAPI) UpdateHostGroups(p *host_group.UpdateHostGroupsParams, _ ...host_group.ClientOption) (*host_group.UpdateHostGroupsOK, error) {
	m.updateGot = p
	return m.updateResp, m.updateErr
}

func (m *mockHostGroupAPI) DeleteHostGroups(p *host_group.DeleteHostGroupsParams, _ ...host_group.ClientOption) (*host_group.DeleteHostGroupsOK, error) {
	m.deleteGot = p
	return m.deleteResp, m.deleteErr
}

func (m *mockHostGroupAPI) PerformGroupAction(p *host_group.PerformGroupActionParams, _ ...host_group.ClientOption) (*host_group.PerformGroupActionOK, error) {
	m.performGot = p
	return m.performResp, m.performErr
}

// callTool wires a mock into a real MCP server and calls the named tool,
// returning the decoded JSON text content.
func callTool(t *testing.T, register func(*mcp.Server), name string, args map[string]any) (string, bool) {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "0"}, nil)
	register(srv)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	defer cs.Close()

	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: name, Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("expected TextContent, got %T", res.Content[0])
	}
	return tc.Text, res.IsError
}

// --- test helpers ---

func strPtr(s string) *string { return &s }

func groupsOK(groups ...*models.HostGroupsHostGroupV1) *host_group.QueryCombinedHostGroupsOK {
	return &host_group.QueryCombinedHostGroupsOK{
		Payload: &models.HostGroupsRespV1{
			Resources: groups,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func membersOK(members ...*models.DeviceDevice) *host_group.QueryCombinedGroupMembersOK {
	return &host_group.QueryCombinedGroupMembersOK{
		Payload: &models.HostGroupsMembersRespV1{
			Resources: members,
			Errors:    []*models.MsaAPIError{},
			Meta:      &models.MsaMetaInfo{},
		},
	}
}

func hostGroupRespOK(groups ...*models.HostGroupsHostGroupV1) *models.HostGroupsRespV1 {
	return &models.HostGroupsRespV1{
		Resources: groups,
		Errors:    []*models.MsaAPIError{},
		Meta:      &models.MsaMetaInfo{},
	}
}

// --- falcon_search_host_groups ---

func TestSearchHostGroupsSuccess(t *testing.T) {
	groupID := "grp-1"
	groupType := "static"
	name := "Production Servers"
	group := &models.HostGroupsHostGroupV1{
		ID:          &groupID,
		GroupType:   groupType,
		Name:        &name,
		CreatedBy:   strPtr("admin@example.com"),
		Description: strPtr("Production server group"),
	}
	mock := &mockHostGroupAPI{searchGroupsResp: groupsOK(group)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{"filter": "group_type:'static'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// The result must be the full group details (single-step combined call).
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 result, got %d: %s", len(got), text)
	}
	if got[0]["id"] != "grp-1" {
		t.Errorf("expected id=grp-1, got %v", got[0]["id"])
	}
	if got[0]["group_type"] != "static" {
		t.Errorf("expected group_type=static, got %v", got[0]["group_type"])
	}
	if got[0]["name"] != "Production Servers" {
		t.Errorf("expected name=Production Servers, got %v", got[0]["name"])
	}

	// The filter must have been passed through.
	if mock.searchGroupsGot == nil {
		t.Fatal("QueryCombinedHostGroups was not called")
	}
	if mock.searchGroupsGot.Filter == nil || *mock.searchGroupsGot.Filter != "group_type:'static'" {
		t.Errorf("unexpected filter passed: %+v", mock.searchGroupsGot.Filter)
	}
}

func TestSearchHostGroupsEmpty(t *testing.T) {
	mock := &mockHostGroupAPI{searchGroupsResp: groupsOK()} // no resources
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{"filter": "name:'nope'"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	results, ok := got["results"].([]any)
	if !ok || len(results) != 0 {
		t.Errorf("expected empty results array, got %v", got["results"])
	}
}

func TestSearchHostGroupsFQLError(t *testing.T) {
	mock := &mockHostGroupAPI{searchGroupsErr: runtime.NewAPIError("QueryCombinedHostGroups", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{"filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	// FQL error branch must include the guide.
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
	// Hint must be present.
	if _, ok := got["hint"]; !ok {
		t.Errorf("expected hint in 400 response, got keys %v", keysOf(got))
	}
}

func TestSearchHostGroups403Scopes(t *testing.T) {
	mock := &mockHostGroupAPI{searchGroupsErr: host_group.NewQueryCombinedHostGroupsForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{})
	// 403 must surface the required scope, not the FQL guide.
	if !contains(text, "Host Groups:read") {
		t.Errorf("expected required scope 'Host Groups:read' in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestSearchHostGroupsDefaultSort(t *testing.T) {
	mock := &mockHostGroupAPI{searchGroupsResp: groupsOK()}
	_, _ = callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{})
	if mock.searchGroupsGot == nil || mock.searchGroupsGot.Sort == nil || *mock.searchGroupsGot.Sort != "name.asc" {
		t.Errorf("expected default sort 'name.asc', got %+v", mock.searchGroupsGot)
	}
}

func TestSearchHostGroupsTransportError(t *testing.T) {
	mock := &mockHostGroupAPI{searchGroupsErr: errors.New("connection refused")}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchHostGroups(s, mock) },
		"falcon_search_host_groups", map[string]any{})
	if !contains(text, "Failed to search host groups") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- falcon_search_host_group_members ---

func TestSearchHostGroupMembersSuccess(t *testing.T) {
	deviceID := "device-1"
	member := &models.DeviceDevice{DeviceID: &deviceID, Hostname: "WIN-SERVER"}
	mock := &mockHostGroupAPI{searchMembersResp: membersOK(member)}

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroupMembers(s, mock) },
		"falcon_search_host_group_members", map[string]any{
			"id":     "grp-1",
			"filter": "platform_name:'Windows'",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["device_id"] != "device-1" || got[0]["hostname"] != "WIN-SERVER" {
		t.Fatalf("expected full device details, got %s", text)
	}

	// The group ID must have been passed to the API.
	if mock.searchMembersGot == nil || mock.searchMembersGot.ID == nil || *mock.searchMembersGot.ID != "grp-1" {
		t.Errorf("expected id='grp-1' passed to API, got %+v", mock.searchMembersGot)
	}
}

func TestSearchHostGroupMembersEmpty(t *testing.T) {
	mock := &mockHostGroupAPI{searchMembersResp: membersOK()} // no members
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroupMembers(s, mock) },
		"falcon_search_host_group_members", map[string]any{"id": "grp-empty"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v (%s)", err, text)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

func TestSearchHostGroupMembersFQLError(t *testing.T) {
	mock := &mockHostGroupAPI{searchMembersErr: runtime.NewAPIError("QueryCombinedGroupMembers", "bad filter", 400)}
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchHostGroupMembers(s, mock) },
		"falcon_search_host_group_members", map[string]any{"id": "grp-1", "filter": "bogus=="})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	// Members search returns a plain error array (not FQL guide), matching Python behavior.
	var got []any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) == 0 {
		t.Error("expected at least one error in result")
	}
}

func TestSearchHostGroupMembers403Scopes(t *testing.T) {
	mock := &mockHostGroupAPI{searchMembersErr: host_group.NewQueryCombinedGroupMembersForbidden()}
	text, _ := callTool(t, func(s *mcp.Server) { registerSearchHostGroupMembers(s, mock) },
		"falcon_search_host_group_members", map[string]any{"id": "grp-1"})
	if !contains(text, "Host Groups:read") {
		t.Errorf("expected required scope 'Host Groups:read' in 403 result: %s", text)
	}
}

// --- falcon_create_host_group ---

func TestCreateHostGroupSuccess(t *testing.T) {
	groupID := "grp-new"
	groupType := "static"
	name := "New Group"
	mock := &mockHostGroupAPI{
		createResp: &host_group.CreateHostGroupsCreated{
			Payload: hostGroupRespOK(&models.HostGroupsHostGroupV1{
				ID:        &groupID,
				GroupType: groupType,
				Name:      &name,
			}),
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerCreateHostGroup(s, mock) },
		"falcon_create_host_group", map[string]any{
			"name":        "New Group",
			"group_type":  "static",
			"description": "A new static group",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "grp-new" {
		t.Fatalf("expected created group in result, got %s", text)
	}

	// Confirm the body fields were carried through.
	if mock.createGot == nil || mock.createGot.Body == nil {
		t.Fatal("CreateHostGroups not called with a body")
	}
	r := mock.createGot.Body.Resources
	if len(r) != 1 {
		t.Fatalf("expected 1 resource in body, got %d", len(r))
	}
	if r[0].Name == nil || *r[0].Name != "New Group" {
		t.Errorf("expected name='New Group', got %+v", r[0].Name)
	}
	if r[0].GroupType == nil || *r[0].GroupType != "static" {
		t.Errorf("expected group_type='static', got %+v", r[0].GroupType)
	}
	if r[0].Description != "A new static group" {
		t.Errorf("expected description='A new static group', got %q", r[0].Description)
	}
}

func TestCreateHostGroupError(t *testing.T) {
	mock := &mockHostGroupAPI{createErr: errors.New("api error")}
	text, _ := callTool(t, func(s *mcp.Server) { registerCreateHostGroup(s, mock) },
		"falcon_create_host_group", map[string]any{"name": "x", "group_type": "static"})
	if !contains(text, "Failed to create host group") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- falcon_update_host_group ---

func TestUpdateHostGroupSuccess(t *testing.T) {
	groupID := "grp-1"
	groupType := "static"
	updatedName := "Renamed Group"
	mock := &mockHostGroupAPI{
		updateResp: &host_group.UpdateHostGroupsOK{
			Payload: hostGroupRespOK(&models.HostGroupsHostGroupV1{
				ID:        &groupID,
				GroupType: groupType,
				Name:      &updatedName,
			}),
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerUpdateHostGroup(s, mock) },
		"falcon_update_host_group", map[string]any{
			"id":   "grp-1",
			"name": "Renamed Group",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["name"] != "Renamed Group" {
		t.Fatalf("expected updated group in result, got %s", text)
	}

	if mock.updateGot == nil || mock.updateGot.Body == nil {
		t.Fatal("UpdateHostGroups not called with a body")
	}
	r := mock.updateGot.Body.Resources
	if len(r) != 1 || r[0].ID == nil || *r[0].ID != "grp-1" {
		t.Errorf("expected id='grp-1' in body resource, got %+v", r)
	}
	if r[0].Name != "Renamed Group" {
		t.Errorf("expected name='Renamed Group', got %q", r[0].Name)
	}
}

func TestUpdateHostGroupError(t *testing.T) {
	mock := &mockHostGroupAPI{updateErr: errors.New("api error")}
	text, _ := callTool(t, func(s *mcp.Server) { registerUpdateHostGroup(s, mock) },
		"falcon_update_host_group", map[string]any{"id": "grp-1", "name": "x"})
	if !contains(text, "Failed to update host group") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- falcon_delete_host_groups ---

func TestDeleteHostGroupsSuccess(t *testing.T) {
	mock := &mockHostGroupAPI{
		deleteResp: &host_group.DeleteHostGroupsOK{
			Payload: &models.MsaQueryResponse{
				Resources: []string{},
				Errors:    []*models.MsaAPIError{},
				Meta:      &models.MsaMetaInfo{},
			},
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeleteHostGroups(s, mock) },
		"falcon_delete_host_groups", map[string]any{"ids": []any{"grp-1", "grp-2"}})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Success returns an empty list.
	if text != "[]" {
		t.Errorf("expected empty array on success, got %s", text)
	}

	// Confirm the IDs were passed through.
	if mock.deleteGot == nil || len(mock.deleteGot.Ids) != 2 {
		t.Fatalf("expected 2 IDs passed to DeleteHostGroups, got %+v", mock.deleteGot)
	}
	if mock.deleteGot.Ids[0] != "grp-1" || mock.deleteGot.Ids[1] != "grp-2" {
		t.Errorf("unexpected IDs: %v", mock.deleteGot.Ids)
	}
}

func TestDeleteHostGroupsEmptyIDs(t *testing.T) {
	mock := &mockHostGroupAPI{}
	text, _ := callTool(t, func(s *mcp.Server) { registerDeleteHostGroups(s, mock) },
		"falcon_delete_host_groups", map[string]any{"ids": []any{}})
	if !contains(text, "ids") {
		t.Errorf("expected ids-related error message, got %s", text)
	}
	if mock.deleteGot != nil {
		t.Error("no API call should be made for empty ids")
	}
}

func TestDeleteHostGroupsError(t *testing.T) {
	mock := &mockHostGroupAPI{deleteErr: errors.New("api error")}
	text, _ := callTool(t, func(s *mcp.Server) { registerDeleteHostGroups(s, mock) },
		"falcon_delete_host_groups", map[string]any{"ids": []any{"grp-1"}})
	if !contains(text, "Failed to delete host groups") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- falcon_perform_host_group_action ---

func TestPerformHostGroupActionSuccess(t *testing.T) {
	groupID := "grp-1"
	groupType := "static"
	groupName := "Static Group"
	mock := &mockHostGroupAPI{
		performResp: &host_group.PerformGroupActionOK{
			Payload: hostGroupRespOK(&models.HostGroupsHostGroupV1{
				ID:        &groupID,
				GroupType: groupType,
				Name:      &groupName,
			}),
		},
	}

	text, isErr := callTool(t, func(s *mcp.Server) { registerPerformHostGroupAction(s, mock) },
		"falcon_perform_host_group_action", map[string]any{
			"action_name": "add-hosts",
			"ids":         []any{"grp-1"},
			"filter":      "device_id:['dev-1','dev-2']",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 || got[0]["id"] != "grp-1" {
		t.Fatalf("expected updated group in result, got %s", text)
	}

	// Confirm action, IDs and filter were passed through.
	if mock.performGot == nil {
		t.Fatal("PerformGroupAction was not called")
	}
	if mock.performGot.ActionName != "add-hosts" {
		t.Errorf("expected action_name='add-hosts', got %q", mock.performGot.ActionName)
	}
	if mock.performGot.Body == nil {
		t.Fatal("PerformGroupAction body is nil")
	}
	if len(mock.performGot.Body.Ids) != 1 || mock.performGot.Body.Ids[0] != "grp-1" {
		t.Errorf("expected ids=['grp-1'], got %v", mock.performGot.Body.Ids)
	}
	params := mock.performGot.Body.ActionParameters
	if len(params) != 1 || params[0].Name == nil || *params[0].Name != "filter" {
		t.Errorf("expected action_parameters with filter, got %+v", params)
	}
	if params[0].Value == nil || *params[0].Value != "device_id:['dev-1','dev-2']" {
		t.Errorf("unexpected filter value: %+v", params[0].Value)
	}
}

func TestPerformHostGroupActionError(t *testing.T) {
	mock := &mockHostGroupAPI{performErr: errors.New("api error")}
	text, _ := callTool(t, func(s *mcp.Server) { registerPerformHostGroupAction(s, mock) },
		"falcon_perform_host_group_action", map[string]any{
			"action_name": "add-hosts",
			"ids":         []any{"grp-1"},
			"filter":      "platform_name:'Windows'",
		})
	if !contains(text, "Failed to perform host group action") {
		t.Errorf("expected error message, got %s", text)
	}
}

// --- normalizeLimit ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{
		0:    100,
		-1:   100,
		1:    1,
		100:  100,
		5000: 5000,
		9999: 5000,
	}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// --- utilities ---

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

func contains(s, sub string) bool {
	return len(s) >= len(sub) && indexOf(s, sub) >= 0
}

func indexOf(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}
