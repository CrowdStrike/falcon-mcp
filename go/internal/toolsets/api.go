// Package toolsets defines the framework-agnostic contract between Falcon
// domain modules and the MCP layer. Domain packages build [Tool] values with
// [NewTool] and register a [Factory] in their init function; the mcpx package
// consumes the registry without either side importing the other's framework.
package toolsets

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/google/jsonschema-go/jsonschema"
)

// Tool is a single MCP tool, independent of any MCP SDK. Build one with
// [NewTool].
type Tool struct {
	Name        string // Full tool name including the "falcon_" prefix.
	Description string
	InputSchema *jsonschema.Schema
	Annotations Annotations
	handler     func(ctx context.Context, raw json.RawMessage) (any, error)
}

// Run unmarshals raw JSON arguments into the tool's typed input, validates them
// against the resolved schema, and invokes the handler.
func (t Tool) Run(ctx context.Context, raw json.RawMessage) (any, error) {
	return t.handler(ctx, raw)
}

// Constrainer is optionally implemented by a tool input type to set schema
// constraints (minimum/maximum/default/examples) that jsonschema struct tags
// cannot express. NewTool calls it on the derived schema before resolving.
type Constrainer interface {
	ApplyConstraints(schema *jsonschema.Schema)
}

// NewTool builds a Tool from a typed input struct. The json tags name the
// params and the jsonschema tags describe them. The schema is derived and
// resolved once at startup; a derivation error is fatal because a misconfigured
// tool must not ship.
func NewTool[In any](
	name, description string,
	ann Annotations,
	h func(ctx context.Context, in In) (any, error),
) Tool {
	schema, err := jsonschema.For[In](nil)
	if err != nil {
		panic(fmt.Sprintf("tool %s: deriving schema: %v", name, err))
	}
	// A *In method set includes value-receiver methods, so the pointer probe
	// matches both pointer- and value-receiver Constrainer implementations.
	var zero In
	if c, ok := any(&zero).(Constrainer); ok {
		c.ApplyConstraints(schema)
	}
	// InputSchema (below) keeps the pre-resolution schema for MCP wire
	// advertisement; resolved is the validator used at call time. Both reflect
	// the same constraints because ApplyConstraints runs before Resolve. Do not
	// collapse them: dropping resolved silently disables call-time validation.
	resolved, err := schema.Resolve(nil)
	if err != nil {
		panic(fmt.Sprintf("tool %s: resolving schema: %v", name, err))
	}
	return Tool{
		Name:        name,
		Description: description,
		InputSchema: schema,
		Annotations: ann,
		handler: func(ctx context.Context, raw json.RawMessage) (any, error) {
			var in In
			if len(raw) > 0 {
				if err := json.Unmarshal(raw, &in); err != nil {
					return nil, fmt.Errorf("invalid arguments: %w", err)
				}
			}
			// jsonschema-go validates a generic JSON value, so decode again
			// into any for validation.
			// TODO(perf): this double-decodes raw; unmarshal once when
			// streamable-http brings concurrent load.
			var generic any = map[string]any{}
			if len(raw) > 0 {
				if err := json.Unmarshal(raw, &generic); err != nil {
					return nil, fmt.Errorf("invalid arguments: %w", err)
				}
			}
			if err := resolved.Validate(generic); err != nil {
				return nil, fmt.Errorf("invalid arguments: %w", err)
			}
			return h(ctx, in)
		},
	}
}

// Annotations carries the MCP tool behavior hints. Destructive, Idempotent, and
// OpenWorld are pointers so "unset" is distinct from "false".
type Annotations struct {
	ReadOnly    bool
	Destructive *bool
	Idempotent  *bool
	OpenWorld   *bool
}

// ReadOnly returns Annotations marking a tool as read-only and non-destructive.
func ReadOnly() Annotations {
	no := false
	return Annotations{ReadOnly: true, Destructive: &no}
}

// Toolset is a named group of tools and resources produced by one Falcon
// module.
type Toolset struct {
	Name        string
	Description string
	Tools       []Tool
	Resources   []Resource
}

// Resource is an embedded guide exposed as an MCP resource. URI is the exact,
// stable resource URI (not derived from a filename).
type Resource struct {
	URI         string
	Name        string
	Description string
	MIMEType    string
	Text        string
}

// Factory builds a Toolset from an authenticated Falcon client.
type Factory func(c *client.CrowdStrikeAPISpecification) *Toolset
