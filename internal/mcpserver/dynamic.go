package mcpserver

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
	"strings"

	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// defaultSearchLimit and the clamp bounds mirror upstream falcon-mcp.
const (
	defaultSearchLimit = 20
	minSearchLimit     = 1
	maxSearchLimit     = 100
)

// ErrUnknownTool classifies a falcon_execute_tool call naming a tool that is
// not in the catalog. It is surfaced as a tool-error result (not a protocol
// error), matching the server's data-not-protocol-error contract.
var ErrUnknownTool = errors.New("dynamic: unknown tool")

// MetaModule is the base.Module that exposes the three dynamic-mode meta-tools
// over a pre-built Catalog. It registers no resources of its own.
type MetaModule struct {
	catalog *Catalog
	modules []base.Module
}

// NewMetaModule returns a MetaModule over cat. modules is the set of enabled
// modules that contributed tools; falcon_list_enabled_modules reports each
// module's name and description from it.
func NewMetaModule(cat *Catalog, modules []base.Module) *MetaModule {
	return &MetaModule{catalog: cat, modules: modules}
}

// Name reports the module name.
func (m *MetaModule) Name() string { return "dynamic" }

// Description reports a one-line summary of the module.
func (m *MetaModule) Description() string {
	return "Meta-tools to discover and execute Falcon tools on demand (dynamic mode)"
}

// RegisterResources is a no-op: the meta-module owns no resources. Real modules
// still register their FQL guides separately in dynamic mode.
func (m *MetaModule) RegisterResources(_ *mcp.Server) {}

// RegisterPrompts is a no-op: the meta-module owns no prompts.
func (m *MetaModule) RegisterPrompts(_ *mcp.Server) {}

// searchToolsSchema is the input schema for falcon_search_tools. It is inferred
// from SearchToolsInput's struct tags, then a mutate func adds the limit
// bounds/default the tag syntax cannot express, reusing the clamp constants.
var searchToolsSchema = base.SchemaFor[SearchToolsInput](func(s *jsonschema.Schema) {
	s.Properties["limit"].Minimum = jsonschema.Ptr(float64(minSearchLimit))
	s.Properties["limit"].Maximum = jsonschema.Ptr(float64(maxSearchLimit))
	s.Properties["limit"].Default = json.RawMessage(strconv.Itoa(defaultSearchLimit))
})

// RegisterTools registers the three meta-tools into r (the live server, in
// dynamic mode). They flow through base.AddTool so they get the "falcon_"
// prefix and default annotations too.
func (m *MetaModule) RegisterTools(r base.Registrar) {
	base.AddTool(r, &mcp.Tool{
		Name:        "search_tools",
		Description: "Discover available Falcon tools by keyword search. Returns matching tool names, descriptions, and parameters; call falcon_execute_tool to run one.",
		InputSchema: searchToolsSchema,
	}, m.searchTools)

	base.AddTool(r, &mcp.Tool{
		Name:        "execute_tool",
		Description: "Execute a Falcon tool by name with the given parameters. Use falcon_search_tools to discover tool names and parameters first.",
	}, m.executeTool)

	base.AddTool(r, &mcp.Tool{
		Name:        "list_enabled_modules",
		Description: "List the Falcon modules enabled on this server.",
	}, m.listEnabledModules)
}

// SearchToolsInput is the input for falcon_search_tools.
type SearchToolsInput struct {
	Query  string `json:"query,omitempty" jsonschema:"keywords to match across tool names, descriptions, module names, and parameter names"`
	Module string `json:"module,omitempty" jsonschema:"filter results to a specific module (e.g. 'hosts', 'detections')"`
	Limit  int    `json:"limit,omitempty" jsonschema:"maximum results to return"`
}

// ToolSummary is one falcon_search_tools result.
type ToolSummary struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Module      string         `json:"module"`
	Parameters  []paramSummary `json:"parameters"`
	ReadOnly    bool           `json:"read_only"`
	Destructive bool           `json:"destructive"`
}

// SearchToolsResult is the falcon_search_tools output envelope.
type SearchToolsResult struct {
	Tools []ToolSummary `json:"tools"`
	Total int           `json:"total"`
}

// searchTools implements falcon_search_tools. It filters the catalog by exact
// module (when given), then keeps entries whose search corpus contains every
// lowercased query token (AND substring match), and returns the first Limit
// results — matching upstream falcon-mcp's algorithm.
func (m *MetaModule) searchTools(_ context.Context, _ *mcp.CallToolRequest, in SearchToolsInput) (*mcp.CallToolResult, SearchToolsResult, error) {
	limit := in.Limit
	switch {
	case limit == 0:
		limit = defaultSearchLimit
	case limit < minSearchLimit:
		limit = minSearchLimit
	case limit > maxSearchLimit:
		limit = maxSearchLimit
	}

	tokens := strings.Fields(strings.ToLower(in.Query))

	tools := make([]ToolSummary, 0, limit)
	for _, ce := range m.catalog.entries {
		if in.Module != "" && ce.module != in.Module {
			continue
		}
		if !matchesAll(ce.corpus, tokens) {
			continue
		}
		tools = append(tools, summarize(ce))
		if len(tools) == limit {
			break
		}
	}
	return nil, SearchToolsResult{Tools: tools, Total: len(tools)}, nil
}

// matchesAll reports whether corpus contains every token (AND substring).
// An empty token set matches everything.
func matchesAll(corpus string, tokens []string) bool {
	for _, t := range tokens {
		if !strings.Contains(corpus, t) {
			return false
		}
	}
	return true
}

// summarize builds a ToolSummary from a catalog entry, deriving the read-only
// and destructive flags from the tool's annotations.
func summarize(ce catalogEntry) ToolSummary {
	ann := ce.tool.Annotations
	readOnly := ann == nil || ann.ReadOnlyHint
	destructive := ann != nil && ann.DestructiveHint != nil && *ann.DestructiveHint
	return ToolSummary{
		Name:        ce.tool.Name,
		Description: ce.tool.Description,
		Module:      ce.module,
		Parameters:  ce.params,
		ReadOnly:    readOnly,
		Destructive: destructive,
	}
}

// ExecuteToolInput is the input for falcon_execute_tool. Parameters is a JSON
// object so its inferred schema is "object" (a json.RawMessage would infer as
// a byte array and reject object arguments at the meta-tool's own validation).
type ExecuteToolInput struct {
	ToolName   string         `json:"tool_name" jsonschema:"exact tool name to execute (from falcon_search_tools results)"`
	Parameters map[string]any `json:"parameters,omitempty" jsonschema:"tool parameters as a JSON object"`
}

// executeTool implements falcon_execute_tool. It looks up the named tool in the
// catalog and dispatches to it over the catalog's in-process client session, so
// the internal server (and the SDK) performs argument validation and result
// packing. An unknown tool yields a tool-error result carrying a discovery
// hint; parameter validation failures surface as the tool's own error result,
// enriched with the expected parameters.
func (m *MetaModule) executeTool(ctx context.Context, _ *mcp.CallToolRequest, in ExecuteToolInput) (*mcp.CallToolResult, any, error) {
	ce, ok := m.catalog.lookup(in.ToolName)
	if !ok {
		var res mcp.CallToolResult
		res.SetError(fmt.Errorf("%w: %q; call falcon_search_tools to discover available tools", ErrUnknownTool, in.ToolName))
		return &res, nil, nil
	}

	// Parameters is an object (map) already; the SDK marshals it over the
	// in-process transport. A nil map is sent as an empty object.
	args := any(in.Parameters)
	if in.Parameters == nil {
		args = map[string]any{}
	}

	res, err := m.catalog.session.CallTool(ctx, &mcp.CallToolParams{
		Name:      ce.tool.Name,
		Arguments: args,
	})
	if err != nil {
		return nil, nil, err
	}
	if res != nil && res.IsError {
		enrichValidationError(res, ce)
	}
	// Return the underlying tool's result verbatim: nil Out leaves res's own
	// StructuredContent/Content (set by the internal server) untouched.
	return res, nil, nil
}

// enrichValidationError appends the tool's expected parameters to an error
// result's text, matching upstream's parameter-validation guidance.
func enrichValidationError(res *mcp.CallToolResult, ce catalogEntry) {
	if len(ce.params) == 0 {
		return
	}
	names := make([]string, len(ce.params))
	for i, p := range ce.params {
		names[i] = p.Name
	}
	hint := fmt.Sprintf(" (expected parameters: %s)", strings.Join(names, ", "))
	if len(res.Content) > 0 {
		if tc, ok := res.Content[0].(*mcp.TextContent); ok {
			tc.Text += hint
		}
	}
}

// ModuleInfo describes one enabled module in a falcon_list_enabled_modules
// result.
type ModuleInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// EnabledModulesResult is the falcon_list_enabled_modules output envelope.
type EnabledModulesResult struct {
	Modules []ModuleInfo `json:"modules"`
	Total   int          `json:"total"`
}

// listEnabledModules implements falcon_list_enabled_modules. It reports the
// enabled modules that contributed tools to the catalog (honoring --modules),
// each with its name and description, excluding the synthetic meta-module
// itself.
func (m *MetaModule) listEnabledModules(_ context.Context, _ *mcp.CallToolRequest, _ struct{}) (*mcp.CallToolResult, EnabledModulesResult, error) {
	mods := make([]ModuleInfo, len(m.modules))
	for i, mod := range m.modules {
		mods[i] = ModuleInfo{Name: mod.Name(), Description: mod.Description()}
	}
	return nil, EnabledModulesResult{Modules: mods, Total: len(mods)}, nil
}
