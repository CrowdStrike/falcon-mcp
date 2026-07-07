package policies

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"

	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// callTool wires a fake registry into a real MCP server and calls the named
// tool, returning the decoded JSON text content and the isError flag.
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

// --- fake policyOps builders ---

// fakePreventionOps returns a policyOps for policy_type="prevention" backed by
// the supplied combined/create/delete/action/precedence stubs.
func fakePreventionOps(
	combinedFn func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]any, error),
	membersFn func(ctx context.Context, id string, filter *string, limit int64, offset *int64, sort *string) ([]any, error),
	createFn func(ctx context.Context, name, platformName, description string, settings any, cloneID string) ([]any, error),
	deleteFn func(ctx context.Context, ids []string) error,
	actionFn func(ctx context.Context, actionName string, ids []string, groupID string) ([]any, error),
	precedenceFn func(ctx context.Context, ids []string, platformName string) error,
) policyOps {
	ops := policyOps{
		searchMode:   "combined",
		searchOp:     opSearchPrevention,
		membersOp:    opMembersPrevention,
		createOp:     opCreatePrevention,
		updateOp:     opUpdatePrevention,
		deleteOp:     opDeletePrevention,
		actionOp:     opActionPrevention,
		precedenceOp: opPrecedencePrevention,
	}
	if combinedFn != nil {
		ops.combined = combinedFn
	}
	if membersFn != nil {
		ops.members = membersFn
	}
	if createFn != nil {
		ops.create = createFn
	}
	if deleteFn != nil {
		ops.delete = deleteFn
	}
	if actionFn != nil {
		ops.action = actionFn
	}
	if precedenceFn != nil {
		ops.precedence = precedenceFn
	}
	return ops
}

// fakeDeviceControlOps returns a two-step policyOps for device_control.
func fakeDeviceControlOps(
	queryFn func(ctx context.Context, filter *string, limit int64, offset *int64, sort *string) ([]string, error),
	getFn func(ctx context.Context, ids []string) ([]any, error),
) policyOps {
	return policyOps{
		searchMode:   "two_step",
		searchOp:     opQueryDeviceControl,
		membersOp:    opMembersDeviceControl,
		createOp:     opCreateDeviceControl,
		updateOp:     opUpdateDeviceControl,
		deleteOp:     opDeleteDeviceControl,
		actionOp:     opActionDeviceControl,
		precedenceOp: opPrecedenceDeviceControl,
		twoStepQuery: queryFn,
		twoStepGet:   getFn,
	}
}

// singleReg builds a registry with a single policy_type entry.
func singleReg(pType string, ops policyOps) map[string]policyOps {
	return map[string]policyOps{pType: ops}
}

// --- helpers ---

func strPtr(s string) *string { return &s }

func contains(s, sub string) bool { return strings.Contains(s, sub) }

func mustUnmarshalArray(t *testing.T, text string) []map[string]any {
	t.Helper()
	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON array: %v (%s)", err, text)
	}
	return got
}

func mustUnmarshalObject(t *testing.T, text string) map[string]any {
	t.Helper()
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("result not a JSON object: %v (%s)", err, text)
	}
	return got
}

// --- falcon_search_policies (combined, prevention) ---

func TestSearchPoliciesPreventionSuccess(t *testing.T) {
	polID := "pol-1"
	polName := "My Prevention Policy"
	ops := fakePreventionOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]any, error) {
			return []any{map[string]any{"id": polID, "name": polName, "enabled": true}}, nil
		},
		nil, nil, nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{
			"policy_type": "prevention",
			"filter":      "enabled:true",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalArray(t, text)
	if len(got) != 1 {
		t.Fatalf("expected 1 result, got %d: %s", len(got), text)
	}
	if got[0]["id"] != "pol-1" {
		t.Errorf("expected id=pol-1, got %v", got[0]["id"])
	}
	if got[0]["name"] != "My Prevention Policy" {
		t.Errorf("expected name='My Prevention Policy', got %v", got[0]["name"])
	}
}

func TestSearchPoliciesPreventionEmpty(t *testing.T) {
	ops := fakePreventionOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]any, error) {
			return []any{}, nil
		},
		nil, nil, nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{"policy_type": "prevention"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalObject(t, text)
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	if results, ok := got["results"].([]any); !ok || len(results) != 0 {
		t.Errorf("expected empty results array, got %v", got["results"])
	}
}

func TestSearchPoliciesPreventionFQL400(t *testing.T) {
	ops := fakePreventionOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]any, error) {
			return nil, runtime.NewAPIError("queryCombinedPreventionPolicies", "bad filter", 400)
		},
		nil, nil, nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	filter := "bogus=="
	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{
			"policy_type": "prevention",
			"filter":      filter,
		})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	got := mustUnmarshalObject(t, text)
	// FQL 400 must include the guide
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide key in 400 response, got keys: %v", keysOf(got))
	}
	guide, _ := got["fql_guide"].(string)
	if len(guide) < 50 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
	if _, ok := got["hint"]; !ok {
		t.Errorf("expected hint key in 400 response, got keys: %v", keysOf(got))
	}
}

func TestSearchPoliciesPrevention403Scopes(t *testing.T) {
	ops := fakePreventionOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]any, error) {
			// Simulate a 403 with the typed error that carries Code()==403
			return nil, runtime.NewAPIError("queryCombinedPreventionPolicies", "forbidden", 403)
		},
		nil, nil, nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{"policy_type": "prevention"})
	// 403 must surface the required scope, not the FQL guide
	if !contains(text, "Prevention Policies:read") {
		t.Errorf("expected 'Prevention Policies:read' in 403 result: %s", text)
	}
	if contains(text, "fql_guide") {
		t.Errorf("403 result should not include fql_guide: %s", text)
	}
}

func TestSearchPoliciesInvalidType(t *testing.T) {
	reg := map[string]policyOps{} // empty registry

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{"policy_type": "bad_type"})
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "Invalid policy_type") {
		t.Errorf("expected Invalid policy_type error, got: %s", text)
	}
	if !contains(text, "bad_type") {
		t.Errorf("expected rejected type name in error, got: %s", text)
	}
}

func TestSearchPoliciesSortPlatformNameRejected(t *testing.T) {
	ops := fakePreventionOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]any, error) {
			return []any{}, nil
		},
		nil, nil, nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{
			"policy_type": "prevention",
			"sort":        "platform_name.asc",
		})
	if !contains(text, "platform_name") {
		t.Errorf("expected platform_name rejection, got: %s", text)
	}
	if !contains(text, "HTTP 500") {
		t.Errorf("expected HTTP 500 mention in sort rejection, got: %s", text)
	}
}

// --- falcon_search_policies (two_step, device_control) ---

func TestSearchPoliciesDeviceControlTwoStep(t *testing.T) {
	queryCalledWith := ""
	getCalledWith := []string(nil)

	dcOps := fakeDeviceControlOps(
		func(_ context.Context, filter *string, _ int64, _ *int64, _ *string) ([]string, error) {
			if filter != nil {
				queryCalledWith = *filter
			}
			return []string{"dc-id-1", "dc-id-2"}, nil
		},
		func(_ context.Context, ids []string) ([]any, error) {
			getCalledWith = ids
			return []any{
				map[string]any{"id": "dc-id-1", "name": "DC Policy 1"},
				map[string]any{"id": "dc-id-2", "name": "DC Policy 2"},
			}, nil
		},
	)
	reg := singleReg("device_control", dcOps)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{
			"policy_type": "device_control",
			"filter":      "enabled:true",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}

	// Both steps must have been called.
	if queryCalledWith != "enabled:true" {
		t.Errorf("expected query filter 'enabled:true', got %q", queryCalledWith)
	}
	if len(getCalledWith) != 2 || getCalledWith[0] != "dc-id-1" || getCalledWith[1] != "dc-id-2" {
		t.Errorf("expected get called with [dc-id-1, dc-id-2], got %v", getCalledWith)
	}

	// Result must be full details, not just IDs.
	got := mustUnmarshalArray(t, text)
	if len(got) != 2 {
		t.Fatalf("expected 2 detail records, got %d: %s", len(got), text)
	}
	if got[0]["name"] != "DC Policy 1" {
		t.Errorf("expected full detail in result, got %v", got[0])
	}
}

func TestSearchPoliciesDeviceControlTwoStepEmpty(t *testing.T) {
	dcOps := fakeDeviceControlOps(
		func(_ context.Context, _ *string, _ int64, _ *int64, _ *string) ([]string, error) {
			return []string{}, nil // no IDs — get step must NOT be called
		},
		func(_ context.Context, ids []string) ([]any, error) {
			// should never be called
			return []any{map[string]any{"id": "should-not-appear"}}, nil
		},
	)
	reg := singleReg("device_control", dcOps)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSearchPolicies(s, reg) },
		"falcon_search_policies", map[string]any{"policy_type": "device_control"})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalObject(t, text)
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	// should-not-appear must not be in the result
	if contains(text, "should-not-appear") {
		t.Errorf("get step was called even though query returned empty: %s", text)
	}
}

// --- falcon_create_policy ---

func TestCreatePolicyPreventionSuccess(t *testing.T) {
	var gotName, gotPlatform string
	ops := fakePreventionOps(
		nil, nil,
		func(_ context.Context, name, platformName, description string, _ any, _ string) ([]any, error) {
			gotName = name
			gotPlatform = platformName
			return []any{map[string]any{"id": "new-pol", "name": name, "platform_name": platformName}}, nil
		},
		nil, nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerCreatePolicy(s, reg) },
		"falcon_create_policy", map[string]any{
			"policy_type":   "prevention",
			"name":          "New Pol",
			"platform_name": "Windows",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalArray(t, text)
	if len(got) != 1 || got[0]["id"] != "new-pol" {
		t.Fatalf("expected created policy in result, got %s", text)
	}
	if gotName != "New Pol" {
		t.Errorf("expected name='New Pol', got %q", gotName)
	}
	if gotPlatform != "Windows" {
		t.Errorf("expected platformName='Windows', got %q", gotPlatform)
	}
}

func TestCreatePolicyMissingName(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerCreatePolicy(s, reg) },
		"falcon_create_policy", map[string]any{
			"policy_type":   "prevention",
			"platform_name": "Windows",
		})
	if !contains(text, "name") {
		t.Errorf("expected name-related error, got: %s", text)
	}
}

func TestCreatePolicyMissingPlatform(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerCreatePolicy(s, reg) },
		"falcon_create_policy", map[string]any{
			"policy_type": "prevention",
			"name":        "Foo",
		})
	if !contains(text, "platform_name") {
		t.Errorf("expected platform_name error, got: %s", text)
	}
}

// content_update does not need platform_name
func TestCreatePolicyContentUpdateNoPlatform(t *testing.T) {
	var gotName string
	cuOps := policyOps{
		searchMode: "combined",
		createOp:   opCreateContentUpdate,
		create: func(_ context.Context, name, _ /*platform*/, description string, _ any, _ string) ([]any, error) {
			gotName = name
			return []any{map[string]any{"id": "cu-pol", "name": name}}, nil
		},
	}
	reg := singleReg("content_update", cuOps)

	text, isErr := callTool(t, func(s *mcp.Server) { registerCreatePolicy(s, reg) },
		"falcon_create_policy", map[string]any{
			"policy_type": "content_update",
			"name":        "CU Policy",
			// no platform_name — should succeed
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalArray(t, text)
	if len(got) != 1 || got[0]["id"] != "cu-pol" {
		t.Fatalf("expected created content_update policy, got %s", text)
	}
	if gotName != "CU Policy" {
		t.Errorf("expected name='CU Policy', got %q", gotName)
	}
}

// --- falcon_delete_policies ---

func TestDeletePoliciesSuccess(t *testing.T) {
	var deletedIDs []string
	ops := fakePreventionOps(
		nil, nil, nil,
		func(_ context.Context, ids []string) error {
			deletedIDs = ids
			return nil
		},
		nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerDeletePolicies(s, reg) },
		"falcon_delete_policies", map[string]any{
			"policy_type": "prevention",
			"ids":         []any{"pol-1", "pol-2"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	// Success returns an empty array
	if text != "[]" {
		t.Errorf("expected '[]' on success, got %s", text)
	}
	if len(deletedIDs) != 2 || deletedIDs[0] != "pol-1" || deletedIDs[1] != "pol-2" {
		t.Errorf("expected ids=[pol-1, pol-2] passed to delete, got %v", deletedIDs)
	}
}

func TestDeletePoliciesEmptyIDs(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerDeletePolicies(s, reg) },
		"falcon_delete_policies", map[string]any{
			"policy_type": "prevention",
			"ids":         []any{},
		})
	if !contains(text, "ids") {
		t.Errorf("expected ids-related error, got: %s", text)
	}
}

func TestDeletePoliciesError(t *testing.T) {
	ops := fakePreventionOps(
		nil, nil, nil,
		func(_ context.Context, _ []string) error {
			return errors.New("api error")
		},
		nil, nil,
	)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerDeletePolicies(s, reg) },
		"falcon_delete_policies", map[string]any{
			"policy_type": "prevention",
			"ids":         []any{"pol-1"},
		})
	if !contains(text, "Failed to delete") {
		t.Errorf("expected delete error message, got: %s", text)
	}
}

// --- falcon_perform_policy_action ---

func TestPerformPolicyActionSuccess(t *testing.T) {
	var gotAction string
	var gotIDs []string
	var gotGroupID string

	ops := fakePreventionOps(
		nil, nil, nil, nil,
		func(_ context.Context, actionName string, ids []string, groupID string) ([]any, error) {
			gotAction = actionName
			gotIDs = ids
			gotGroupID = groupID
			return []any{map[string]any{"id": "pol-1", "enabled": false}}, nil
		},
		nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerPerformPolicyAction(s, reg) },
		"falcon_perform_policy_action", map[string]any{
			"policy_type": "prevention",
			"action_name": "disable",
			"ids":         []any{"pol-1"},
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	got := mustUnmarshalArray(t, text)
	if len(got) != 1 || got[0]["id"] != "pol-1" {
		t.Fatalf("expected updated policy in result, got %s", text)
	}
	if gotAction != "disable" {
		t.Errorf("expected action='disable', got %q", gotAction)
	}
	if len(gotIDs) != 1 || gotIDs[0] != "pol-1" {
		t.Errorf("expected ids=[pol-1], got %v", gotIDs)
	}
	if gotGroupID != "" {
		t.Errorf("expected empty groupID for disable, got %q", gotGroupID)
	}
}

func TestPerformPolicyActionWithGroupID(t *testing.T) {
	var gotGroupID string
	ops := fakePreventionOps(
		nil, nil, nil, nil,
		func(_ context.Context, _ string, _ []string, groupID string) ([]any, error) {
			gotGroupID = groupID
			return []any{map[string]any{"id": "pol-1"}}, nil
		},
		nil,
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerPerformPolicyAction(s, reg) },
		"falcon_perform_policy_action", map[string]any{
			"policy_type": "prevention",
			"action_name": "add-host-group",
			"ids":         []any{"pol-1"},
			"group_id":    "grp-abc",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if gotGroupID != "grp-abc" {
		t.Errorf("expected groupID='grp-abc', got %q", gotGroupID)
	}
}

func TestPerformPolicyActionMissingGroupID(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerPerformPolicyAction(s, reg) },
		"falcon_perform_policy_action", map[string]any{
			"policy_type": "prevention",
			"action_name": "add-host-group",
			"ids":         []any{"pol-1"},
			// no group_id — should return a guiding error
		})
	if !contains(text, "group_id") {
		t.Errorf("expected group_id error, got: %s", text)
	}
}

func TestPerformPolicyActionInvalidAction(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerPerformPolicyAction(s, reg) },
		"falcon_perform_policy_action", map[string]any{
			"policy_type": "prevention",
			"action_name": "nuke-everything",
			"ids":         []any{"pol-1"},
		})
	if !contains(text, "Invalid action_name") {
		t.Errorf("expected invalid action_name error, got: %s", text)
	}
	if !contains(text, "nuke-everything") {
		t.Errorf("expected rejected action name in error, got: %s", text)
	}
}

func TestPerformPolicyActionFirewallNoRuleGroup(t *testing.T) {
	// firewall does not support add-rule-group — verify it's rejected
	fwOps := policyOps{
		searchMode: "combined",
		actionOp:   opActionFirewall,
		action: func(_ context.Context, _ string, _ []string, _ string) ([]any, error) {
			return []any{}, nil
		},
	}
	reg := singleReg("firewall", fwOps)

	text, _ := callTool(t, func(s *mcp.Server) { registerPerformPolicyAction(s, reg) },
		"falcon_perform_policy_action", map[string]any{
			"policy_type": "firewall",
			"action_name": "add-rule-group",
			"ids":         []any{"pol-fw"},
			"group_id":    "rg-1",
		})
	if !contains(text, "Invalid action_name") {
		t.Errorf("expected Invalid action_name for firewall+add-rule-group, got: %s", text)
	}
}

// --- falcon_set_policy_precedence ---

func TestSetPolicyPrecedenceSuccess(t *testing.T) {
	var gotIDs []string
	var gotPlatform string
	ops := fakePreventionOps(
		nil, nil, nil, nil, nil,
		func(_ context.Context, ids []string, platformName string) error {
			gotIDs = ids
			gotPlatform = platformName
			return nil
		},
	)
	reg := singleReg("prevention", ops)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSetPolicyPrecedence(s, reg) },
		"falcon_set_policy_precedence", map[string]any{
			"policy_type":   "prevention",
			"ids":           []any{"pol-1", "pol-2"},
			"platform_name": "Windows",
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected '[]' on success, got %s", text)
	}
	if len(gotIDs) != 2 || gotIDs[0] != "pol-1" || gotIDs[1] != "pol-2" {
		t.Errorf("expected ids=[pol-1, pol-2], got %v", gotIDs)
	}
	if gotPlatform != "Windows" {
		t.Errorf("expected platform='Windows', got %q", gotPlatform)
	}
}

func TestSetPolicyPrecedenceContentUpdateNoPlatform(t *testing.T) {
	var gotPlatform string
	cuOps := policyOps{
		searchMode:   "combined",
		precedenceOp: opPrecedenceContentUpdate,
		precedence: func(_ context.Context, ids []string, platformName string) error {
			gotPlatform = platformName
			return nil
		},
	}
	reg := singleReg("content_update", cuOps)

	text, isErr := callTool(t, func(s *mcp.Server) { registerSetPolicyPrecedence(s, reg) },
		"falcon_set_policy_precedence", map[string]any{
			"policy_type": "content_update",
			"ids":         []any{"cu-pol-1"},
			// no platform_name — content_update does not need it
		})
	if isErr {
		t.Fatalf("unexpected error result: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected '[]' on success, got %s", text)
	}
	// platform should have been passed as empty string
	if gotPlatform != "" {
		t.Errorf("expected empty platform for content_update, got %q", gotPlatform)
	}
}

func TestSetPolicyPrecedenceMissingPlatform(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerSetPolicyPrecedence(s, reg) },
		"falcon_set_policy_precedence", map[string]any{
			"policy_type": "prevention",
			"ids":         []any{"pol-1"},
			// no platform_name — should error
		})
	if !contains(text, "platform_name") {
		t.Errorf("expected platform_name error, got: %s", text)
	}
}

func TestSetPolicyPrecedenceEmptyIDs(t *testing.T) {
	ops := fakePreventionOps(nil, nil, nil, nil, nil, nil)
	reg := singleReg("prevention", ops)

	text, _ := callTool(t, func(s *mcp.Server) { registerSetPolicyPrecedence(s, reg) },
		"falcon_set_policy_precedence", map[string]any{
			"policy_type":   "prevention",
			"ids":           []any{},
			"platform_name": "Windows",
		})
	if !contains(text, "ids") {
		t.Errorf("expected ids-related error, got: %s", text)
	}
}

// --- internal helpers ---

func TestNormalizeLimit(t *testing.T) {
	cases := map[int64]int64{
		0:   100,
		-1:  100,
		1:   1,
		100: 100,
		500: 500,
		999: 500,
	}
	for in, want := range cases {
		if got := normalizeLimit(in); got != want {
			t.Errorf("normalizeLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

func TestNormalizeMembersLimit(t *testing.T) {
	cases := map[int64]int64{
		0:    100,
		-1:   100,
		100:  100,
		5000: 5000,
		9999: 5000,
	}
	for in, want := range cases {
		if got := normalizeMembersLimit(in); got != want {
			t.Errorf("normalizeMembersLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

func TestValidateSortPlatformNameRejected(t *testing.T) {
	if err := validateSort(strPtr("platform_name.asc")); err == nil {
		t.Error("expected error for platform_name sort, got nil")
	}
	if err := validateSort(strPtr("platform_name.desc")); err == nil {
		t.Error("expected error for platform_name.desc sort, got nil")
	}
}

func TestValidateSortSafeFields(t *testing.T) {
	safe := []string{"name.asc", "created_timestamp.desc", "modified_timestamp.asc", "enabled.desc"}
	for _, s := range safe {
		if err := validateSort(&s); err != nil {
			t.Errorf("validateSort(%q) returned unexpected error: %v", s, err)
		}
	}
}

func TestValidateSortNilOrEmpty(t *testing.T) {
	if err := validateSort(nil); err != nil {
		t.Errorf("validateSort(nil) returned unexpected error: %v", err)
	}
	empty := ""
	if err := validateSort(&empty); err != nil {
		t.Errorf("validateSort('') returned unexpected error: %v", err)
	}
}

func TestSortedKeys(t *testing.T) {
	m := map[string]bool{"banana": true, "apple": true, "cherry": true}
	got := sortedKeys(m)
	want := []string{"apple", "banana", "cherry"}
	if len(got) != len(want) {
		t.Fatalf("sortedKeys len mismatch: %v", got)
	}
	for i, v := range want {
		if got[i] != v {
			t.Errorf("sortedKeys[%d] = %q, want %q", i, got[i], v)
		}
	}
}

func TestNeedsGroupID(t *testing.T) {
	need := []string{"add-host-group", "remove-host-group", "add-rule-group", "remove-rule-group"}
	noNeed := []string{"enable", "disable", "override-allow", "override-pause", "override-revert"}
	for _, a := range need {
		if !needsGroupID(a) {
			t.Errorf("needsGroupID(%q) = false, want true", a)
		}
	}
	for _, a := range noNeed {
		if needsGroupID(a) {
			t.Errorf("needsGroupID(%q) = true, want false", a)
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
