package dynamic

import (
	"sort"
	"strings"

	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// toolNamePrefix is the prefix base.AddTool applies to every tool name. The
// catalog keys tools by their prefixed name; lookup also accepts the bare name.
const toolNamePrefix = "falcon_"

// paramSummary describes one tool parameter for search results. It mirrors
// upstream falcon-mcp's per-parameter summary: type, whether it is required,
// and its description.
type paramSummary struct {
	Name        string `json:"name"`
	Type        string `json:"type,omitempty"`
	Required    bool   `json:"required"`
	Description string `json:"description,omitempty"`
}

// paramSummaries extracts the top-level parameters from a tool's inferred input
// schema (the *jsonschema.Schema base.AddTool derives from the handler's In
// type). It reflects exactly the schema the served tool advertises and, unlike
// raw struct reflection, omits json:"-" fields. Parameters are returned in
// sorted name order for deterministic output. A nil schema (In is any) yields
// no parameters.
func paramSummaries(schema *jsonschema.Schema) []paramSummary {
	if schema == nil || len(schema.Properties) == 0 {
		return nil
	}
	required := make(map[string]bool, len(schema.Required))
	for _, name := range schema.Required {
		required[name] = true
	}

	names := make([]string, 0, len(schema.Properties))
	for name := range schema.Properties {
		names = append(names, name)
	}
	sort.Strings(names)

	out := make([]paramSummary, 0, len(names))
	for _, name := range names {
		p := schema.Properties[name]
		summary := paramSummary{Name: name, Required: required[name]}
		if p != nil {
			summary.Type = p.Type
			summary.Description = p.Description
		}
		out = append(out, summary)
	}
	return out
}

// searchCorpus builds the lowercased text falcon_search_tools matches against,
// mirroring upstream's "{name} {description} {module} {param_names}".
func searchCorpus(tool *mcp.Tool, module string, params []paramSummary) string {
	var b strings.Builder
	b.WriteString(tool.Name)
	b.WriteByte(' ')
	b.WriteString(tool.Description)
	b.WriteByte(' ')
	b.WriteString(module)
	for _, p := range params {
		b.WriteByte(' ')
		b.WriteString(p.Name)
	}
	return strings.ToLower(b.String())
}
