package toolsets

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// Dynamic builds the 3-tool discovery facade over the given toolsets, mirroring
// the Python dynamic mode. Instead of exposing every module's tools directly,
// it registers falcon_list_enabled_modules, falcon_search_tools, and
// falcon_execute_tool, keeping the client-visible surface (and context window)
// minimal while all functionality stays reachable on demand.
//
// The catalog is built from the same [Tool] structs passed in, so any filtering
// already applied to sets (notably read-only) carries through: a write tool
// dropped by [Registry.Build] is absent from both search and execute here.
func Dynamic(sets []*Toolset) *Toolset {
	cat := newCatalog(sets)
	return &Toolset{
		Name:        "dynamic",
		Description: "Dynamic discovery facade exposing tools on demand.",
		Tools: []Tool{
			NewTool("falcon_list_enabled_modules", listModulesDescription, ReadOnly(), cat.listModules),
			NewTool("falcon_search_tools", searchToolsDescription, ReadOnly(), cat.searchTools),
			NewTool("falcon_execute_tool", executeToolDescription, Annotations{}, cat.executeTool),
		},
	}
}

const listModulesDescription = "List the Falcon modules enabled on this server.\n\n" +
	"Use this to discover which capability areas are available before searching " +
	"for tools. Returns the enabled module names."

const searchToolsDescription = "Discover available Falcon tools by keyword search.\n\n" +
	"Use this to find tools by name, description, module, or parameter keywords. " +
	"Returns tool schemas with parameter details so you can call falcon_execute_tool. " +
	"Consult this before executing any tool to understand its parameters."

const executeToolDescription = "Execute a Falcon tool by name with the given parameters.\n\n" +
	"Use falcon_search_tools first to discover tool names, parameter schemas, and " +
	"mutation risk (read_only / destructive fields). Do not execute destructive " +
	"tools without confirming the user's intent. Results are returned in full."

// catalogEntry indexes one tool for search and dispatch.
type catalogEntry struct {
	tool         Tool
	module       string
	searchCorpus string
}

// catalog is the searchable index of tools built from the enabled toolsets.
type catalog struct {
	entries map[string]catalogEntry
	modules []string // sorted, enabled module names
}

func newCatalog(sets []*Toolset) *catalog {
	c := &catalog{entries: make(map[string]catalogEntry)}
	seen := map[string]bool{}
	for _, ts := range sets {
		if !seen[ts.Name] {
			seen[ts.Name] = true
			c.modules = append(c.modules, ts.Name)
		}
		for _, t := range ts.Tools {
			c.entries[t.Name] = catalogEntry{
				tool:         t,
				module:       ts.Name,
				searchCorpus: buildCorpus(t, ts.Name),
			}
		}
	}
	sort.Strings(c.modules)
	return c
}

// buildCorpus assembles the lowercased searchable text for a tool: its name,
// description, module, and parameter names.
func buildCorpus(t Tool, module string) string {
	var params []string
	if t.InputSchema != nil {
		for name := range t.InputSchema.Properties {
			params = append(params, name)
		}
	}
	return strings.ToLower(strings.Join([]string{
		t.Name, t.Description, module, strings.Join(params, " "),
	}, " "))
}

// listModulesInput has no parameters.
type listModulesInput struct{}

func (c *catalog) listModules(_ context.Context, _ listModulesInput) (any, error) {
	return map[string]any{"modules": c.modules}, nil
}

type searchToolsInput struct {
	Query  string `json:"query,omitempty"  jsonschema:"Keywords to search across tool names, descriptions, module names, and parameter names."`
	Module string `json:"module,omitempty" jsonschema:"Filter results to a specific module (e.g., 'hosts', 'detections')."`
	Limit  int    `json:"limit,omitempty"  jsonschema:"Maximum number of results to return (default: 20)."`
}

func (c *catalog) searchTools(_ context.Context, in searchToolsInput) (any, error) {
	limit := in.Limit
	if limit <= 0 {
		limit = 20
	}

	// Iterate in sorted name order for deterministic results.
	names := make([]string, 0, len(c.entries))
	for name := range c.entries {
		names = append(names, name)
	}
	sort.Strings(names)

	tokens := strings.Fields(strings.ToLower(in.Query))
	results := make([]map[string]any, 0, limit)
	for _, name := range names {
		e := c.entries[name]
		if in.Module != "" && e.module != in.Module {
			continue
		}
		if !matchesAll(e.searchCorpus, tokens) {
			continue
		}
		results = append(results, formatEntry(e))
		if len(results) >= limit {
			break
		}
	}

	if len(results) == 0 {
		return map[string]any{
			"results": []any{},
			"hint": fmt.Sprintf("No tools found matching your query. Available modules: %s. "+
				"Try a broader search or check falcon_list_enabled_modules.",
				strings.Join(c.modules, ", ")),
		}, nil
	}
	return results, nil
}

// matchesAll reports whether corpus contains every token.
func matchesAll(corpus string, tokens []string) bool {
	for _, tok := range tokens {
		if !strings.Contains(corpus, tok) {
			return false
		}
	}
	return true
}

// formatEntry renders a catalog entry as the search-result shape, summarizing
// each parameter's type, requiredness, description, and examples.
func formatEntry(e catalogEntry) map[string]any {
	params := map[string]any{}
	if s := e.tool.InputSchema; s != nil {
		required := map[string]bool{}
		for _, r := range s.Required {
			required[r] = true
		}
		for name, prop := range s.Properties {
			info := map[string]any{
				"type":        schemaType(prop.Type),
				"required":    required[name],
				"description": prop.Description,
			}
			if len(prop.Examples) > 0 {
				info["examples"] = prop.Examples
			}
			params[name] = info
		}
	}
	destructive := false
	if e.tool.Annotations.Destructive != nil {
		destructive = *e.tool.Annotations.Destructive
	}
	return map[string]any{
		"name":        e.tool.Name,
		"module":      e.module,
		"description": e.tool.Description,
		"parameters":  params,
		"read_only":   e.tool.Annotations.ReadOnly,
		"destructive": destructive,
	}
}

// schemaType returns the JSON type string, defaulting to "any" when unset.
func schemaType(t string) string {
	if t == "" {
		return "any"
	}
	return t
}

type executeToolInput struct {
	ToolName   string         `json:"tool_name"            jsonschema:"Exact tool name to execute (from falcon_search_tools results)."`
	Parameters map[string]any `json:"parameters,omitempty" jsonschema:"Tool parameters as a JSON object."`
}

func (c *catalog) executeTool(ctx context.Context, in executeToolInput) (any, error) {
	e, ok := c.entries[in.ToolName]
	if !ok {
		return map[string]any{
			"error": fmt.Sprintf("Unknown tool: %q. Use falcon_search_tools to discover valid names.", in.ToolName),
		}, nil
	}
	raw, err := json.Marshal(in.Parameters)
	if err != nil {
		return map[string]any{"error": fmt.Sprintf("invalid parameters: %v", err), "tool": in.ToolName}, nil
	}
	result, err := e.tool.Run(ctx, raw)
	if err != nil {
		return map[string]any{"error": fmt.Sprintf("Execution failed: %v", err), "tool": in.ToolName}, nil
	}
	return normalizeEmpty(result), nil
}

// normalizeEmpty returns a helpful hint dict when a tool produced an empty list,
// mirroring the Python facade so empty results are self-explaining.
func normalizeEmpty(result any) any {
	if list, ok := result.([]any); ok && len(list) == 0 {
		return map[string]any{
			"results":     []any{},
			"total_count": 0,
			"hint":        "No records returned. Use falcon_search_tools to review the tool parameters if this is unexpected.",
		}
	}
	return result
}
