package toolsets

import (
	"context"
	"encoding/json"
	"testing"
)

// dynTool is a small helper to build a read/write tool for catalog tests.
func dynTool(name, desc string, ann Annotations, ran *bool) Tool {
	return NewTool(name, desc, ann, func(_ context.Context, in struct {
		Filter string `json:"filter,omitempty" jsonschema:"an FQL filter"`
	}) (any, error) {
		if ran != nil {
			*ran = true
		}
		return []map[string]any{{"ok": true, "filter": in.Filter}}, nil
	})
}

func writeAnn() Annotations {
	yes := true
	return Annotations{ReadOnly: false, Destructive: &yes}
}

func sampleSets(ran *bool) []*Toolset {
	return []*Toolset{
		{
			Name: "hosts",
			Tools: []Tool{
				dynTool("falcon_search_hosts", "Search for hosts by attributes", ReadOnly(), nil),
				dynTool("falcon_get_host_details", "Get host details", ReadOnly(), nil),
			},
		},
		{
			Name: "detections",
			Tools: []Tool{
				dynTool("falcon_update_detection", "Update a detection status", writeAnn(), ran),
			},
		},
	}
}

func callMeta(t *testing.T, ts *Toolset, name string, args map[string]any) any {
	t.Helper()
	var tool *Tool
	for i := range ts.Tools {
		if ts.Tools[i].Name == name {
			tool = &ts.Tools[i]
		}
	}
	if tool == nil {
		t.Fatalf("meta-tool %q not found in dynamic toolset", name)
	}
	if args == nil {
		args = map[string]any{}
	}
	raw, _ := json.Marshal(args)
	out, err := tool.Run(context.Background(), raw)
	if err != nil {
		t.Fatalf("%s run: %v", name, err)
	}
	return out
}

func TestDynamic_ExposesExactlyThreeTools(t *testing.T) {
	ts := Dynamic(sampleSets(nil))
	if len(ts.Tools) != 3 {
		t.Fatalf("want 3 meta-tools, got %d", len(ts.Tools))
	}
	names := map[string]bool{}
	for _, tl := range ts.Tools {
		names[tl.Name] = true
	}
	for _, want := range []string{"falcon_list_enabled_modules", "falcon_search_tools", "falcon_execute_tool"} {
		if !names[want] {
			t.Fatalf("missing meta-tool %q; have %v", want, names)
		}
	}
}

func TestDynamic_ListEnabledModules(t *testing.T) {
	ts := Dynamic(sampleSets(nil))
	out := callMeta(t, ts, "falcon_list_enabled_modules", nil)
	got, _ := json.Marshal(out)
	var payload struct {
		Modules []string `json:"modules"`
	}
	_ = json.Unmarshal(got, &payload)
	if len(payload.Modules) != 2 || payload.Modules[0] != "detections" || payload.Modules[1] != "hosts" {
		t.Fatalf("modules = %v, want sorted [detections hosts]", payload.Modules)
	}
}

func TestDynamic_SearchByKeyword(t *testing.T) {
	ts := Dynamic(sampleSets(nil))
	out := callMeta(t, ts, "falcon_search_tools", map[string]any{"query": "hosts"})
	results, ok := out.([]map[string]any)
	if !ok {
		t.Fatalf("search result type %T, want []map[string]any", out)
	}
	if len(results) != 2 {
		t.Fatalf("want 2 hosts tools, got %d: %v", len(results), results)
	}
	for _, r := range results {
		if r["module"] != "hosts" {
			t.Fatalf("unexpected module in result: %v", r["module"])
		}
	}
}

func TestDynamic_SearchNoMatchReturnsHint(t *testing.T) {
	ts := Dynamic(sampleSets(nil))
	out := callMeta(t, ts, "falcon_search_tools", map[string]any{"query": "zzznotarealthing"})
	m, ok := out.(map[string]any)
	if !ok {
		t.Fatalf("no-match result type %T, want map with hint", out)
	}
	if _, has := m["hint"]; !has {
		t.Fatalf("no-match result missing hint: %v", m)
	}
}

func TestDynamic_ExecuteToolDispatches(t *testing.T) {
	ran := false
	ts := Dynamic(sampleSets(&ran))
	out := callMeta(t, ts, "falcon_execute_tool", map[string]any{
		"tool_name":  "falcon_search_hosts",
		"parameters": map[string]any{"filter": "platform_name:'Windows'"},
	})
	b, _ := json.Marshal(out)
	if !json.Valid(b) || len(b) == 0 {
		t.Fatalf("execute produced no output: %q", b)
	}
	var rows []map[string]any
	if err := json.Unmarshal(b, &rows); err != nil {
		t.Fatalf("execute output not a list: %v (%s)", err, b)
	}
	if rows[0]["filter"] != "platform_name:'Windows'" {
		t.Fatalf("parameters not forwarded to handler: %v", rows[0])
	}
}

func TestDynamic_ExecuteUnknownTool(t *testing.T) {
	ts := Dynamic(sampleSets(nil))
	out := callMeta(t, ts, "falcon_execute_tool", map[string]any{"tool_name": "falcon_nope"})
	m, ok := out.(map[string]any)
	if !ok || m["error"] == nil {
		t.Fatalf("unknown tool should return an error map, got %T %v", out, out)
	}
}

// TestDynamic_ReadOnlyExcludesWriteTools proves the net-new interaction (no
// Python oracle): when the sets fed to Dynamic were built read-only, write
// tools are absent from both search and execute.
func TestDynamic_ReadOnlyExcludesWriteTools(t *testing.T) {
	ran := false
	full := sampleSets(&ran)
	// Simulate what Registry.Build(readOnly=true) produces: drop write tools.
	for _, ts := range full {
		ts.Tools = filterReadOnly(ts.Tools)
	}
	ts := Dynamic(full)

	// Search must not surface the write tool.
	out := callMeta(t, ts, "falcon_search_tools", map[string]any{"query": "update detection"})
	if results, ok := out.([]map[string]any); ok {
		for _, r := range results {
			if r["name"] == "falcon_update_detection" {
				t.Fatal("read-only dynamic catalog leaked a write tool via search")
			}
		}
	}

	// Execute must refuse the write tool and never invoke it.
	exec := callMeta(t, ts, "falcon_execute_tool", map[string]any{
		"tool_name":  "falcon_update_detection",
		"parameters": map[string]any{},
	})
	m, ok := exec.(map[string]any)
	if !ok || m["error"] == nil {
		t.Fatalf("read-only execute of write tool should error, got %T %v", exec, exec)
	}
	if ran {
		t.Fatal("write tool handler ran despite read-only filtering")
	}
}
