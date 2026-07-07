package server

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
)

// dynamicCatalog holds a searchable catalog of all enabled tools plus an
// in-process MCP session used to execute them by name. Dynamic mode exposes just
// three tools (falcon_list_enabled_modules + falcon_search_tools +
// falcon_execute_tool) to keep the client's context window small while all
// functionality stays reachable on demand.
type dynamicCatalog struct {
	entries map[string]catalogEntry
	session *mcp.ClientSession // in-process client connected to the scratch server
}

type catalogEntry struct {
	name        string
	module      string
	description string
	inputSchema map[string]any
	readOnly    bool
	destructive bool
	searchText  string // lowercased corpus: name + description + module + param names
}

// buildDynamicCatalog registers every enabled toolset's tools into a scratch
// mcp.Server, connects an in-process client, and lists the tools to capture
// their schemas. The scratch session is retained for execution.
func buildDynamicCatalog(ctx context.Context, fc *falcon.FalconClient, enabled []api.Toolset) (*dynamicCatalog, error) {
	scratch := mcp.NewServer(&mcp.Implementation{Name: "falcon-dynamic-scratch", Version: "0"}, nil)

	// Track which module each tool belongs to.
	toolModule := map[string]string{}
	for _, ts := range enabled {
		for _, st := range ts.GetTools(fc) {
			toolModule[st.Tool.Name] = ts.GetName()
			st.Register(scratch, fc)
		}
	}

	clientT, serverT := mcp.NewInMemoryTransports()
	if _, err := scratch.Connect(ctx, serverT, nil); err != nil {
		return nil, fmt.Errorf("dynamic: scratch server connect: %w", err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "falcon-dynamic-client", Version: "0"}, nil)
	session, err := client.Connect(ctx, clientT, nil)
	if err != nil {
		return nil, fmt.Errorf("dynamic: in-process client connect: %w", err)
	}

	listed, err := session.ListTools(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("dynamic: list tools: %w", err)
	}

	cat := &dynamicCatalog{entries: map[string]catalogEntry{}, session: session}
	for _, tool := range listed.Tools {
		schema := schemaToMap(tool.InputSchema)
		e := catalogEntry{
			name:        tool.Name,
			module:      toolModule[tool.Name],
			description: tool.Description,
			inputSchema: schema,
		}
		if tool.Annotations != nil {
			e.readOnly = tool.Annotations.ReadOnlyHint
			e.destructive = tool.Annotations.DestructiveHint != nil && *tool.Annotations.DestructiveHint
		}
		e.searchText = strings.ToLower(strings.Join([]string{
			tool.Name, tool.Description, e.module, strings.Join(paramNames(schema), " "),
		}, " "))
		cat.entries[tool.Name] = e
	}
	return cat, nil
}

// search returns catalog entries matching query (all whitespace-separated tokens
// must appear in the search corpus) and optional module filter, capped at limit.
func (c *dynamicCatalog) search(query, module string, limit int) []map[string]any {
	var matched []catalogEntry
	for _, e := range c.entries {
		if module != "" && e.module != module {
			continue
		}
		if query != "" {
			ok := true
			for _, tok := range strings.Fields(strings.ToLower(query)) {
				if !strings.Contains(e.searchText, tok) {
					ok = false
					break
				}
			}
			if !ok {
				continue
			}
		}
		matched = append(matched, e)
	}
	sort.Slice(matched, func(i, j int) bool { return matched[i].name < matched[j].name })
	if limit > 0 && len(matched) > limit {
		matched = matched[:limit]
	}
	out := make([]map[string]any, 0, len(matched))
	for _, e := range matched {
		out = append(out, c.formatEntry(e))
	}
	return out
}

// formatEntry builds the search-result view for a tool, summarizing parameters
// and injecting the per-tool FQL hint + the FQL suffix into the filter param.
func (c *dynamicCatalog) formatEntry(e catalogEntry) map[string]any {
	params := summarizeParams(e.inputSchema)

	if filterParam, ok := params["filter"].(map[string]any); ok {
		desc, _ := filterParam["description"].(string)
		if hint := fql.FilterHints[e.name]; hint != "" {
			desc = appendHint(desc, hint)
		}
		desc = appendHint(desc, fql.FQLFilterHintSuffix)
		filterParam["description"] = desc
	}

	return map[string]any{
		"name":        e.name,
		"module":      e.module,
		"description": e.description,
		"parameters":  params,
		"read_only":   e.readOnly,
		"destructive": e.destructive,
	}
}

func appendHint(desc, hint string) string {
	if desc == "" {
		return hint
	}
	if strings.HasSuffix(desc, ".") {
		return desc + " " + hint
	}
	return desc + ". " + hint
}

// registerDynamicTools registers falcon_search_tools and falcon_execute_tool
// against srv, backed by the given catalog. falcon_list_enabled_modules is
// registered separately by Build (giving 3 client-visible tools total).
func registerDynamicTools(srv *mcp.Server, cat *dynamicCatalog) {
	type searchInput struct {
		Query  string `json:"query,omitempty" jsonschema:"Keywords to search across tool names, descriptions, module names, and parameter names."`
		Module string `json:"module,omitempty" jsonschema:"Filter results to a specific module (e.g. hosts, detections)."`
		Limit  int    `json:"limit,omitempty" jsonschema:"Maximum number of results to return [1-100]. Default 20."`
	}
	mcp.AddTool(srv, &mcp.Tool{
		Name: "falcon_search_tools",
		Description: "Discover available Falcon tools by keyword search. Use this to find tools by " +
			"name, description, module, or parameter keywords. Returns tool schemas with parameter " +
			"details so you can call falcon_execute_tool. Consult this before executing any tool.",
		Annotations: mcpx.ReadOnly(),
	}, func(_ context.Context, _ *mcp.CallToolRequest, in searchInput) (*mcp.CallToolResult, any, error) {
		limit := in.Limit
		if limit <= 0 {
			limit = 20
		}
		if limit > 100 {
			limit = 100
		}
		results := cat.search(in.Query, in.Module, limit)
		if len(results) == 0 {
			mods := map[string]bool{}
			for _, e := range cat.entries {
				mods[e.module] = true
			}
			available := make([]string, 0, len(mods))
			for m := range mods {
				available = append(available, m)
			}
			sort.Strings(available)
			return mcpx.JSONResult(map[string]any{
				"results": []any{},
				"hint": "No tools found matching your query. Available modules: " +
					strings.Join(available, ", ") + ". Try a broader search or check falcon_list_enabled_modules.",
			})
		}
		return mcpx.JSONResult(results)
	})

	type executeInput struct {
		ToolName   string         `json:"tool_name" jsonschema:"Exact tool name to execute (from falcon_search_tools results)."`
		Parameters map[string]any `json:"parameters,omitempty" jsonschema:"Tool parameters as a JSON object."`
	}
	mcp.AddTool(srv, &mcp.Tool{
		Name: "falcon_execute_tool",
		Description: "Execute a Falcon tool by name with the given parameters. Use falcon_search_tools " +
			"first to discover tool names, parameter schemas, and mutation risk (read_only / " +
			"destructive). Do not execute destructive tools without confirming the user's intent.",
		// No read-only annotation: execute can invoke mutating tools.
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in executeInput) (*mcp.CallToolResult, any, error) {
		entry, ok := cat.entries[in.ToolName]
		if !ok {
			return mcpx.JSONResult(map[string]any{
				"error": fmt.Sprintf("Unknown tool: %q. Use falcon_search_tools to discover valid names.", in.ToolName),
			})
		}
		args := in.Parameters
		if args == nil {
			args = map[string]any{}
		}
		res, err := cat.session.CallTool(ctx, &mcp.CallToolParams{Name: entry.name, Arguments: args})
		if err != nil {
			return mcpx.JSONResult(map[string]any{
				"error": fmt.Sprintf("Execution failed: %v", err),
				"tool":  in.ToolName,
			})
		}
		// The underlying tool already returns unstructured JSON text; pass its
		// content through unchanged.
		return res, nil, nil
	})
}

// --- helpers ---

// schemaToMap normalizes an InputSchema (which may be a *jsonschema.Schema or a
// map) into a generic map by round-tripping through JSON.
func schemaToMap(schema any) map[string]any {
	if schema == nil {
		return map[string]any{}
	}
	data, err := json.Marshal(schema)
	if err != nil {
		return map[string]any{}
	}
	var m map[string]any
	if err := json.Unmarshal(data, &m); err != nil {
		return map[string]any{}
	}
	return m
}

func paramNames(schema map[string]any) []string {
	props, _ := schema["properties"].(map[string]any)
	names := make([]string, 0, len(props))
	for k := range props {
		names = append(names, k)
	}
	return names
}

// summarizeParams builds a compact per-parameter summary (type, required,
// description) from a JSON-schema map, mirroring the Python catalog output.
func summarizeParams(schema map[string]any) map[string]any {
	props, _ := schema["properties"].(map[string]any)
	requiredList, _ := schema["required"].([]any)
	required := map[string]bool{}
	for _, r := range requiredList {
		if s, ok := r.(string); ok {
			required[s] = true
		}
	}
	out := map[string]any{}
	for name, raw := range props {
		ps, _ := raw.(map[string]any)
		typ, _ := ps["type"].(string)
		if typ == "" {
			typ = "any"
		}
		desc, _ := ps["description"].(string)
		info := map[string]any{
			"type":        typ,
			"required":    required[name],
			"description": desc,
		}
		out[name] = info
	}
	return out
}
