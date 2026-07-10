package mcpserver

import (
	"context"
	"log/slog"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	gofalconhosts "github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/config"
	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
	hostgroups "github.com/crowdstrike/falcon-mcp/internal/modules/host_groups"
	hostsmod "github.com/crowdstrike/falcon-mcp/internal/modules/hosts"
)

// stubHosts and stubGroups are no-op fakes sufficient to register the tools and
// drive tools/list, resources/list, and a read-only tools/call end-to-end.
type stubHosts struct{}

func (stubHosts) QueryDevicesByFilter(*gofalconhosts.QueryDevicesByFilterParams, ...gofalconhosts.ClientOption) (*gofalconhosts.QueryDevicesByFilterOK, error) {
	return &gofalconhosts.QueryDevicesByFilterOK{Payload: &models.MsaQueryResponse{Resources: []string{}}}, nil
}
func (stubHosts) PostDeviceDetailsV2(*gofalconhosts.PostDeviceDetailsV2Params, ...gofalconhosts.ClientOption) (*gofalconhosts.PostDeviceDetailsV2OK, error) {
	return &gofalconhosts.PostDeviceDetailsV2OK{Payload: &models.DeviceapiDeviceDetailsResponseSwagger{}}, nil
}

type stubGroups struct{}

func (stubGroups) QueryCombinedHostGroups(*host_group.QueryCombinedHostGroupsParams, ...host_group.ClientOption) (*host_group.QueryCombinedHostGroupsOK, error) {
	return &host_group.QueryCombinedHostGroupsOK{Payload: &models.HostGroupsRespV1{}}, nil
}
func (stubGroups) QueryCombinedGroupMembers(*host_group.QueryCombinedGroupMembersParams, ...host_group.ClientOption) (*host_group.QueryCombinedGroupMembersOK, error) {
	return &host_group.QueryCombinedGroupMembersOK{Payload: &models.HostGroupsMembersRespV1{}}, nil
}
func (stubGroups) CreateHostGroups(*host_group.CreateHostGroupsParams, ...host_group.ClientOption) (*host_group.CreateHostGroupsCreated, error) {
	return &host_group.CreateHostGroupsCreated{Payload: &models.HostGroupsRespV1{}}, nil
}
func (stubGroups) UpdateHostGroups(*host_group.UpdateHostGroupsParams, ...host_group.ClientOption) (*host_group.UpdateHostGroupsOK, error) {
	return &host_group.UpdateHostGroupsOK{Payload: &models.HostGroupsRespV1{}}, nil
}
func (stubGroups) DeleteHostGroups(*host_group.DeleteHostGroupsParams, ...host_group.ClientOption) (*host_group.DeleteHostGroupsOK, error) {
	return &host_group.DeleteHostGroupsOK{Payload: &models.MsaQueryResponse{}}, nil
}
func (stubGroups) PerformGroupAction(*host_group.PerformGroupActionParams, ...host_group.ClientOption) (*host_group.PerformGroupActionOK, error) {
	return &host_group.PerformGroupActionOK{Payload: &models.HostGroupsRespV1{}}, nil
}

// connectTestServer registers the host and host-group modules on a server and
// returns a connected in-memory client session.
func connectTestServer(t *testing.T) *mcp.ClientSession {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "falcon-mcp-test", Version: "test"}, nil)
	reg := base.ServerRegistrar(srv)
	for _, m := range []base.Module{&hostsmod.Module{API: stubHosts{}, Concurrency: 4, Logger: slog.New(slog.DiscardHandler)}, &hostgroups.Module{API: stubGroups{}, Logger: slog.New(slog.DiscardHandler)}} {
		m.RegisterTools(reg)
		m.RegisterResources(srv)
	}

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	ss, err := srv.Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })

	client := mcp.NewClient(&mcp.Implementation{Name: "test-client", Version: "test"}, nil)
	cs, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })
	return cs
}

func TestToolsAndResourcesAreRegistered(t *testing.T) {
	cs := connectTestServer(t)
	ctx := context.Background()

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	want := map[string]bool{
		"falcon_search_hosts": false, "falcon_get_host_details": false,
		"falcon_search_host_groups": false, "falcon_search_host_group_members": false,
		"falcon_create_host_group": false, "falcon_update_host_group": false,
		"falcon_delete_host_groups": false, "falcon_perform_host_group_action": false,
	}
	for _, tool := range tools.Tools {
		if _, ok := want[tool.Name]; ok {
			want[tool.Name] = true
		}
	}
	for name, found := range want {
		if !found {
			t.Errorf("tool %q not registered", name)
		}
	}

	resources, err := cs.ListResources(ctx, nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	// Resources are keyed by URI and must carry the Python-matching, falcon_-
	// prefixed name so falcon-mcp clients see identical resource identities.
	gotNameForURI := map[string]string{}
	for _, r := range resources.Resources {
		gotNameForURI[r.URI] = r.Name
	}
	wantResources := map[string]string{
		"falcon://hosts/search/fql-guide":       "falcon_search_hosts_fql_guide",
		"falcon://host-groups/search/fql-guide": "falcon_search_host_groups_fql_guide",
	}
	for uri, wantName := range wantResources {
		name, ok := gotNameForURI[uri]
		if !ok {
			t.Errorf("resource %q not registered", uri)
			continue
		}
		if name != wantName {
			t.Errorf("resource %q name = %q, want %q", uri, name, wantName)
		}
	}
}

func TestCallToolEndToEnd(t *testing.T) {
	cs := connectTestServer(t)
	res, err := cs.CallTool(context.Background(), &mcp.CallToolParams{
		Name:      "falcon_search_hosts",
		Arguments: map[string]any{"filter": "platform_name:'Windows'"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	if res.IsError {
		t.Fatalf("tool returned error result: %+v", res.Content)
	}
	// The result must carry native structured JSON (an object with a
	// "resources" array), not a stringified blob in text content.
	if res.StructuredContent == nil {
		t.Fatalf("expected structured content")
	}
	obj, ok := res.StructuredContent.(map[string]any)
	if !ok {
		t.Fatalf("structured content should be a JSON object, got %T", res.StructuredContent)
	}
	if _, ok := obj["resources"]; !ok {
		t.Fatalf("structured content missing resources field: %v", obj)
	}
}

// TestModuleSelectionEndToEnd drives a real New-built server over the in-memory
// transport and asserts the tools/list surface reflects the --modules allowlist:
// only the hosts module's tools are advertised, and detection/host-group tools
// are absent. A zero API is safe here — New only reads sub-client pointers to
// register tools (see TestServerMCPNotNil), it makes no API calls.
func TestModuleSelectionEndToEnd(t *testing.T) {
	srv, err := New(
		&config.Config{Modules: []string{"hosts"}},
		&client.CrowdStrikeAPISpecification{},
	)
	if err != nil {
		t.Fatalf("New: %v", err)
	}

	ctx := context.Background()
	clientT, serverT := mcp.NewInMemoryTransports()
	ss, err := srv.MCP().Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })

	c := mcp.NewClient(&mcp.Implementation{Name: "test-client", Version: "test"}, nil)
	cs, err := c.Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	got := map[string]bool{}
	for _, tool := range tools.Tools {
		got[tool.Name] = true
	}
	if !got["falcon_search_hosts"] {
		t.Errorf("hosts module tool falcon_search_hosts not advertised")
	}
	for _, absent := range []string{"falcon_search_detections", "falcon_search_host_groups"} {
		if got[absent] {
			t.Errorf("tool %q advertised, want absent (module not enabled)", absent)
		}
	}
}
