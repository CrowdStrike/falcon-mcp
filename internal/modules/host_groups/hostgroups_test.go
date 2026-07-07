package hostgroups

import (
	"context"
	"errors"
	"log/slog"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// testLogger discards output; modules require a non-nil logger.
var testLogger = slog.New(slog.DiscardHandler)

// fakeHostGroups is a configurable test double for the hostGroupAPI interface.
type fakeHostGroups struct {
	searchResp  *host_group.QueryCombinedHostGroupsOK
	searchErr   error
	membersResp *host_group.QueryCombinedGroupMembersOK
	membersErr  error
	createResp  *host_group.CreateHostGroupsCreated
	createErr   error
	updateResp  *host_group.UpdateHostGroupsOK
	updateErr   error
	deleteErr   error
	actionResp  *host_group.PerformGroupActionOK
	actionErr   error

	lastCreateBody *models.HostGroupsCreateGroupsReqV1
	lastUpdateBody *models.HostGroupsUpdateGroupsReqV1
	lastDeleteIDs  []string
	lastActionName string
	lastActionBody *models.MsaEntityActionRequestV2
}

func (f *fakeHostGroups) QueryCombinedHostGroups(*host_group.QueryCombinedHostGroupsParams, ...host_group.ClientOption) (*host_group.QueryCombinedHostGroupsOK, error) {
	return f.searchResp, f.searchErr
}

func (f *fakeHostGroups) QueryCombinedGroupMembers(*host_group.QueryCombinedGroupMembersParams, ...host_group.ClientOption) (*host_group.QueryCombinedGroupMembersOK, error) {
	return f.membersResp, f.membersErr
}

func (f *fakeHostGroups) CreateHostGroups(p *host_group.CreateHostGroupsParams, _ ...host_group.ClientOption) (*host_group.CreateHostGroupsCreated, error) {
	f.lastCreateBody = p.Body
	return f.createResp, f.createErr
}

func (f *fakeHostGroups) UpdateHostGroups(p *host_group.UpdateHostGroupsParams, _ ...host_group.ClientOption) (*host_group.UpdateHostGroupsOK, error) {
	f.lastUpdateBody = p.Body
	return f.updateResp, f.updateErr
}

func (f *fakeHostGroups) DeleteHostGroups(p *host_group.DeleteHostGroupsParams, _ ...host_group.ClientOption) (*host_group.DeleteHostGroupsOK, error) {
	f.lastDeleteIDs = p.Ids
	return &host_group.DeleteHostGroupsOK{}, f.deleteErr
}

func (f *fakeHostGroups) PerformGroupAction(p *host_group.PerformGroupActionParams, _ ...host_group.ClientOption) (*host_group.PerformGroupActionOK, error) {
	f.lastActionName = p.ActionName
	f.lastActionBody = p.Body
	return f.actionResp, f.actionErr
}

func str(s string) *string { return &s }
func i32(v int32) *int32   { return &v }

func TestSearchHostGroupsSuccess(t *testing.T) {
	t.Parallel()

	f := &fakeHostGroups{searchResp: &host_group.QueryCombinedHostGroupsOK{Payload: &models.HostGroupsRespV1{
		Resources: []*models.HostGroupsHostGroupV1{{ID: str("g1"), Name: str("Servers")}},
	}}}
	m := New(Params{API: f, Logger: testLogger})

	_, out, err := m.searchHostGroups(context.Background(), nil, SearchInput{Filter: "group_type:'static'"})
	if err != nil {
		t.Fatalf("searchHostGroups: %v", err)
	}
	if out.Total != 1 || len(out.Resources) != 1 || out.FilterUsed != "group_type:'static'" {
		t.Fatalf("unexpected result: %+v", out)
	}
}

func TestSearchHostGroupsEmpty(t *testing.T) {
	t.Parallel()

	f := &fakeHostGroups{searchResp: &host_group.QueryCombinedHostGroupsOK{Payload: &models.HostGroupsRespV1{
		Resources: []*models.HostGroupsHostGroupV1{},
	}}}
	m := New(Params{API: f, Logger: testLogger})

	_, out, err := m.searchHostGroups(context.Background(), nil, SearchInput{})
	if err != nil {
		t.Fatalf("searchHostGroups: %v", err)
	}
	if out.Total != 0 || out.Resources == nil {
		t.Fatalf("expected non-nil empty slice, got %+v", out)
	}
}

func TestSearchHostGroupsFQLError(t *testing.T) {
	t.Parallel()

	badReq := &host_group.QueryCombinedHostGroupsBadRequest{Payload: &models.HostGroupsRespV1{
		Errors: []*models.MsaAPIError{{Code: i32(400), Message: str("invalid filter")}},
	}}
	f := &fakeHostGroups{searchErr: badReq}
	m := New(Params{API: f, Logger: testLogger})

	_, out, err := m.searchHostGroups(context.Background(), nil, SearchInput{Filter: "bogus"})
	if err != nil {
		t.Fatalf("expected FQL error to be formatted, not returned: %v", err)
	}
	if len(out.Errors) != 1 || out.Errors[0].Message != "invalid filter" {
		t.Fatalf("expected FQL error detail, got %+v", out.Errors)
	}
	if out.FQLGuide == "" || out.Hint == "" {
		t.Fatalf("expected fql_guide and hint to be populated")
	}
}

func TestSearchHostGroupsAPIError(t *testing.T) {
	t.Parallel()

	f := &fakeHostGroups{searchErr: errors.New("boom")}
	m := New(Params{API: f, Logger: testLogger})

	_, _, err := m.searchHostGroups(context.Background(), nil, SearchInput{})
	if err == nil {
		t.Fatalf("expected non-FQL error to be returned")
	}
}

func TestSearchHostGroupMembers(t *testing.T) {
	t.Parallel()

	t.Run("requires id", func(t *testing.T) {
		t.Parallel()
		m := New(Params{API: &fakeHostGroups{}, Logger: testLogger})
		_, _, err := m.searchHostGroupMembers(context.Background(), nil, MembersInput{})
		if !errors.Is(err, errInvalidInput) {
			t.Fatalf("expected errInvalidInput, got %v", err)
		}
	})

	t.Run("success", func(t *testing.T) {
		t.Parallel()
		f := &fakeHostGroups{membersResp: &host_group.QueryCombinedGroupMembersOK{Payload: &models.HostGroupsMembersRespV1{
			Resources: []*models.DeviceDevice{{DeviceID: str("d1")}},
		}}}
		m := New(Params{API: f, Logger: testLogger})
		_, out, err := m.searchHostGroupMembers(context.Background(), nil, MembersInput{ID: "g1", Filter: "platform_name:'Windows'"})
		if err != nil {
			t.Fatalf("searchHostGroupMembers: %v", err)
		}
		if out.Total != 1 || out.FilterUsed != "platform_name:'Windows'" {
			t.Fatalf("unexpected result: %+v", out)
		}
	})
}

func TestCreateHostGroupValidation(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		in      CreateInput
		wantErr bool
	}{
		{"missing name", CreateInput{GroupType: "static"}, true},
		{"bad group_type", CreateInput{Name: "x", GroupType: "bogus"}, true},
		{"rule on static", CreateInput{Name: "x", GroupType: "static", AssignmentRule: "platform_name:'Windows'"}, true},
		{"valid static", CreateInput{Name: "x", GroupType: "static"}, false},
		{"valid dynamic with rule", CreateInput{Name: "x", GroupType: "dynamic", AssignmentRule: "platform_name:'Windows'"}, false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			f := &fakeHostGroups{createResp: &host_group.CreateHostGroupsCreated{Payload: &models.HostGroupsRespV1{}}}
			m := New(Params{API: f, Logger: testLogger})
			_, _, err := m.createHostGroup(context.Background(), nil, tc.in)
			if tc.wantErr && !errors.Is(err, errInvalidInput) {
				t.Fatalf("expected errInvalidInput, got %v", err)
			}
			if !tc.wantErr && err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}

func TestCreateHostGroupBody(t *testing.T) {
	t.Parallel()

	f := &fakeHostGroups{createResp: &host_group.CreateHostGroupsCreated{Payload: &models.HostGroupsRespV1{
		Resources: []*models.HostGroupsHostGroupV1{{ID: str("new")}},
	}}}
	m := New(Params{API: f, Logger: testLogger})

	_, out, err := m.createHostGroup(context.Background(), nil, CreateInput{Name: "Servers", GroupType: "dynamic", Description: "desc", AssignmentRule: "platform_name:'Windows'"})
	if err != nil {
		t.Fatalf("createHostGroup: %v", err)
	}
	if out.Total != 1 {
		t.Fatalf("expected created record returned, got %+v", out)
	}
	if len(f.lastCreateBody.Resources) != 1 {
		t.Fatalf("expected one resource in body")
	}
	got := f.lastCreateBody.Resources[0]
	if *got.Name != "Servers" || *got.GroupType != "dynamic" || got.Description != "desc" || got.AssignmentRule != "platform_name:'Windows'" {
		t.Fatalf("unexpected create body: %+v", got)
	}
}

func TestUpdateHostGroup(t *testing.T) {
	t.Parallel()

	t.Run("requires id", func(t *testing.T) {
		t.Parallel()
		m := New(Params{API: &fakeHostGroups{}, Logger: testLogger})
		_, _, err := m.updateHostGroup(context.Background(), nil, UpdateInput{Name: "x"})
		if !errors.Is(err, errInvalidInput) {
			t.Fatalf("expected errInvalidInput, got %v", err)
		}
	})

	t.Run("sends provided fields", func(t *testing.T) {
		t.Parallel()
		f := &fakeHostGroups{updateResp: &host_group.UpdateHostGroupsOK{Payload: &models.HostGroupsRespV1{
			Resources: []*models.HostGroupsHostGroupV1{{ID: str("g1")}},
		}}}
		m := New(Params{API: f, Logger: testLogger})
		rule := "platform_name:'Linux'"
		_, out, err := m.updateHostGroup(context.Background(), nil, UpdateInput{ID: "g1", Name: "renamed", AssignmentRule: &rule})
		if err != nil {
			t.Fatalf("updateHostGroup: %v", err)
		}
		if out.Total != 1 {
			t.Fatalf("expected updated record returned, got %+v", out)
		}
		got := f.lastUpdateBody.Resources[0]
		if *got.ID != "g1" || got.Name != "renamed" || got.AssignmentRule == nil || *got.AssignmentRule != rule {
			t.Fatalf("unexpected update body: %+v", got)
		}
	})

	t.Run("omits unset assignment_rule", func(t *testing.T) {
		t.Parallel()
		f := &fakeHostGroups{updateResp: &host_group.UpdateHostGroupsOK{Payload: &models.HostGroupsRespV1{}}}
		m := New(Params{API: f, Logger: testLogger})
		_, _, err := m.updateHostGroup(context.Background(), nil, UpdateInput{ID: "g1", Description: "d"})
		if err != nil {
			t.Fatalf("updateHostGroup: %v", err)
		}
		if got := f.lastUpdateBody.Resources[0]; got.AssignmentRule != nil {
			t.Fatalf("expected assignment_rule left unset, got %q", *got.AssignmentRule)
		}
	})
}

func TestDeleteHostGroups(t *testing.T) {
	t.Parallel()

	t.Run("empty ids", func(t *testing.T) {
		t.Parallel()
		m := New(Params{API: &fakeHostGroups{}, Logger: testLogger})
		_, _, err := m.deleteHostGroups(context.Background(), nil, DeleteInput{})
		if !errors.Is(err, errInvalidInput) {
			t.Fatalf("expected errInvalidInput, got %v", err)
		}
	})

	t.Run("success", func(t *testing.T) {
		t.Parallel()
		f := &fakeHostGroups{}
		m := New(Params{API: f, Logger: testLogger})
		_, out, err := m.deleteHostGroups(context.Background(), nil, DeleteInput{IDs: []string{"g1", "g2"}})
		if err != nil {
			t.Fatalf("deleteHostGroups: %v", err)
		}
		if !out.Ok {
			t.Fatalf("expected Ok, got %+v", out)
		}
		if len(f.lastDeleteIDs) != 2 {
			t.Fatalf("expected 2 ids passed, got %v", f.lastDeleteIDs)
		}
	})
}

func TestPerformHostGroupAction(t *testing.T) {
	t.Parallel()

	t.Run("validation", func(t *testing.T) {
		t.Parallel()
		tests := []struct {
			name string
			in   ActionInput
		}{
			{"bad action", ActionInput{ActionName: "nope", IDs: []string{"g1"}, Filter: "hostname:'x'"}},
			{"empty ids", ActionInput{ActionName: "add-hosts", Filter: "hostname:'x'"}},
			{"empty filter", ActionInput{ActionName: "add-hosts", IDs: []string{"g1"}}},
		}
		for _, tc := range tests {
			t.Run(tc.name, func(t *testing.T) {
				t.Parallel()
				m := New(Params{API: &fakeHostGroups{}, Logger: testLogger})
				_, _, err := m.performHostGroupAction(context.Background(), nil, tc.in)
				if !errors.Is(err, errInvalidInput) {
					t.Fatalf("expected errInvalidInput, got %v", err)
				}
			})
		}
	})

	t.Run("builds filter action parameter", func(t *testing.T) {
		t.Parallel()
		f := &fakeHostGroups{actionResp: &host_group.PerformGroupActionOK{Payload: &models.HostGroupsRespV1{
			Resources: []*models.HostGroupsHostGroupV1{{ID: str("g1")}},
		}}}
		m := New(Params{API: f, Logger: testLogger})
		_, out, err := m.performHostGroupAction(context.Background(), nil, ActionInput{ActionName: "add-hosts", IDs: []string{"g1"}, Filter: "hostname:'PC*'"})
		if err != nil {
			t.Fatalf("performHostGroupAction: %v", err)
		}
		if out.Total != 1 {
			t.Fatalf("expected updated record returned, got %+v", out)
		}
		if f.lastActionName != "add-hosts" {
			t.Fatalf("expected action_name add-hosts, got %q", f.lastActionName)
		}
		if len(f.lastActionBody.Ids) != 1 || f.lastActionBody.Ids[0] != "g1" {
			t.Fatalf("expected target id g1, got %v", f.lastActionBody.Ids)
		}
		params := f.lastActionBody.ActionParameters
		if len(params) != 1 || *params[0].Name != "filter" || *params[0].Value != "hostname:'PC*'" {
			t.Fatalf("expected filter action parameter, got %+v", params)
		}
	})
}

// TestRegisterResourcesServesFQLGuide verifies the host-groups module publishes
// its FQL guide as the falcon://host-groups/search/fql-guide resource, with the
// Python-matching name, and that reading it returns the embedded guide text.
func TestRegisterResourcesServesFQLGuide(t *testing.T) {
	t.Parallel()

	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "test"}, nil)
	New(Params{API: &fakeHostGroups{}, Logger: testLogger}).RegisterResources(srv)

	ctx := context.Background()
	clientT, serverT := mcp.NewInMemoryTransports()
	ss, err := srv.Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })

	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "test"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	list, err := cs.ListResources(ctx, nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	if len(list.Resources) != 1 {
		t.Fatalf("expected 1 resource, got %d", len(list.Resources))
	}
	if got := list.Resources[0]; got.Name != "falcon_search_host_groups_fql_guide" || got.URI != fqlGuideURI {
		t.Fatalf("resource = {name:%q uri:%q}, want falcon_search_host_groups_fql_guide / %s", got.Name, got.URI, fqlGuideURI)
	}

	read, err := cs.ReadResource(ctx, &mcp.ReadResourceParams{URI: fqlGuideURI})
	if err != nil {
		t.Fatalf("ReadResource: %v", err)
	}
	if len(read.Contents) != 1 || read.Contents[0].Text != fqlGuide {
		t.Fatalf("read content does not match embedded guide")
	}
}
