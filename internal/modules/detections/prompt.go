package detections

import (
	"fmt"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// buildFilterPromptName is the unprefixed name of the detections FQL-builder
// prompt; base.Prompt exposes it as falcon_build_detection_filter.
const buildFilterPromptName = "build_detection_filter"

// promptArgs declares the FQL fields the build_detection_filter prompt accepts.
// Each is optional: the client supplies whichever it wants folded into the
// suggested filter, and the rendered guidance covers the rest.
var promptArgs = []*mcp.PromptArgument{
	{Name: "status", Description: "detection status (e.g. new, in_progress, closed)"},
	{Name: "severity", Description: "severity name or numeric threshold (e.g. high, critical)"},
	{Name: "product", Description: "detection product (e.g. epp, idp, mobile, ngsiem)"},
}

// RegisterPrompts registers the detections module's FQL-builder prompt. It
// guides an LLM client through composing a valid falcon_search_detections
// filter, echoing any arguments the client already chose and pointing at the
// FQL guide resource for the full syntax.
func (m *Module) RegisterPrompts(s *mcp.Server) {
	base.Prompt(s, base.PromptParams{
		Name:        buildFilterPromptName,
		Title:       "Build a detection FQL filter",
		Description: "Guide the composition of an FQL filter for falcon_search_detections.",
		Arguments:   promptArgs,
	}, renderBuildFilterPrompt)
}

// renderBuildFilterPrompt builds the prompt messages from the supplied
// arguments. It always returns a single user message; provided arguments are
// woven into the guidance so the model starts from the caller's intent.
func renderBuildFilterPrompt(args map[string]string) []*mcp.PromptMessage {
	var b strings.Builder
	b.WriteString("Help construct a CrowdStrike FQL filter for the falcon_search_detections tool.\n\n")

	if chosen := chosenArgs(args); chosen != "" {
		b.WriteString("The user has indicated these constraints: ")
		b.WriteString(chosen)
		b.WriteString(".\n\n")
	}

	b.WriteString("Compose a single FQL filter string combining the relevant constraints, ")
	b.WriteString("then call falcon_search_detections with it. Consult the ")
	b.WriteString(fqlGuideURI)
	b.WriteString(" resource for the full field list and operators before finalizing the filter.")

	return []*mcp.PromptMessage{
		{
			Role:    "user",
			Content: &mcp.TextContent{Text: b.String()},
		},
	}
}

// chosenArgs renders the non-empty prompt arguments as a comma-separated
// "field=value" list, in the fixed promptArgs order for deterministic output.
// It returns "" when the client supplied none.
func chosenArgs(args map[string]string) string {
	parts := make([]string, 0, len(promptArgs))
	for _, a := range promptArgs {
		if v := strings.TrimSpace(args[a.Name]); v != "" {
			parts = append(parts, fmt.Sprintf("%s=%s", a.Name, v))
		}
	}
	return strings.Join(parts, ", ")
}
