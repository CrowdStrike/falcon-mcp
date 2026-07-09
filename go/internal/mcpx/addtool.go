package mcpx

import (
	"context"
	"encoding/json"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

// addTool registers one toolsets.Tool on the server via the low-level AddTool.
// The typed input handling already lives in toolsets.NewTool, so this adapter
// only bridges the wire types. Crucially it sets InputSchema but NOT
// OutputSchema: emitting an output schema would make some MCP clients inline it
// into model context where large schemas get truncated, so structured output
// stays off and results are returned as JSON text content.
func addTool(srv *mcp.Server, t toolsets.Tool) {
	srv.AddTool(&mcp.Tool{
		Name:        t.Name,
		Description: t.Description,
		InputSchema: t.InputSchema,
		Annotations: toSDKAnnotations(t.Annotations),
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		out, err := t.Run(ctx, req.Params.Arguments)
		if err != nil {
			// A domain error becomes a tool-level error result, not a
			// protocol error, matching the Python server's behavior.
			return errorResult(err), nil
		}
		return jsonTextResult(out)
	})
}

// toSDKAnnotations maps the framework-agnostic annotations onto the SDK type.
func toSDKAnnotations(a toolsets.Annotations) *mcp.ToolAnnotations {
	ann := &mcp.ToolAnnotations{ReadOnlyHint: a.ReadOnly}
	if a.Destructive != nil {
		ann.DestructiveHint = a.Destructive
	}
	// IdempotentHint is a bare bool in go-sdk v1.6.1 (unlike its *bool
	// neighbours), so we dereference here; the nil-guard preserves "unset".
	if a.Idempotent != nil {
		ann.IdempotentHint = *a.Idempotent
	}
	if a.OpenWorld != nil {
		ann.OpenWorldHint = a.OpenWorld
	}
	return ann
}

// jsonTextResult marshals a handler's output into a single JSON text-content
// block.
func jsonTextResult(out any) (*mcp.CallToolResult, error) {
	b, err := json.Marshal(out)
	if err != nil {
		return nil, err
	}
	return &mcp.CallToolResult{
		Content: []mcp.Content{&mcp.TextContent{Text: string(b)}},
	}, nil
}

// errorResult wraps a domain error as a tool-level error result.
func errorResult(err error) *mcp.CallToolResult {
	return &mcp.CallToolResult{
		IsError: true,
		Content: []mcp.Content{&mcp.TextContent{Text: err.Error()}},
	}
}
