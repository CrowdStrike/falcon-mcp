// Package mcpx holds small helpers shared across toolsets for producing MCP
// tool results. The Falcon MCP server returns unstructured JSON (matching the
// Python server's structured_output=False), so handlers marshal their result
// value to a single JSON text content block.
package mcpx

import (
	"encoding/json"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// BoolPtr returns a pointer to b. Useful for optional *bool tool-annotation
// fields.
func BoolPtr(b bool) *bool { return &b }

// ReadOnly returns the default annotation set for a read-only tool that talks
// to an external API, matching the Python READ_ONLY_ANNOTATIONS.
func ReadOnly() *mcp.ToolAnnotations {
	return &mcp.ToolAnnotations{
		ReadOnlyHint:    true,
		DestructiveHint: BoolPtr(false),
		IdempotentHint:  true,
		OpenWorldHint:   BoolPtr(true),
	}
}

// Mutating returns the annotation set for a non-destructive write tool
// (create/update): not read-only, not destructive, open-world.
func Mutating() *mcp.ToolAnnotations {
	return &mcp.ToolAnnotations{
		ReadOnlyHint:    false,
		DestructiveHint: BoolPtr(false),
		OpenWorldHint:   BoolPtr(true),
	}
}

// Destructive returns the annotation set for a destructive write tool
// (delete/remove): not read-only, destructive, open-world.
func Destructive() *mcp.ToolAnnotations {
	return &mcp.ToolAnnotations{
		ReadOnlyHint:    false,
		DestructiveHint: BoolPtr(true),
		OpenWorldHint:   BoolPtr(true),
	}
}

// JSONResult marshals v to indented JSON and wraps it in a CallToolResult with
// a single text content block. The generic Out type of the handler should be
// `any` so the SDK omits the output schema (matching structured_output=False).
func JSONResult(v any) (*mcp.CallToolResult, any, error) {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		// Fall back to a compact error object rather than failing the call.
		data = []byte(`{"error": "failed to marshal tool result"}`)
	}
	return &mcp.CallToolResult{
		Content: []mcp.Content{&mcp.TextContent{Text: string(data)}},
	}, nil, nil
}
