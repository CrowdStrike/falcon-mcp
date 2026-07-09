package toolsets

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/google/jsonschema-go/jsonschema"
)

type sampleInput struct {
	Filter string `json:"filter,omitempty" jsonschema:"an FQL filter"`
	Limit  int64  `json:"limit,omitempty"  jsonschema:"max records"`
}

// ApplyConstraints exercises the Constrainer opt-in: bound Limit to [1,5000]
// with a default of 10.
func (sampleInput) ApplyConstraints(s *jsonschema.Schema) {
	lim := s.Properties["limit"]
	min, max := 1.0, 5000.0
	lim.Minimum = &min
	lim.Maximum = &max
	lim.Default = json.RawMessage(`10`)
}

func TestNewTool_DerivesSchemaAndDescription(t *testing.T) {
	tool := NewTool("falcon_sample", "does a thing", ReadOnly(),
		func(_ context.Context, in sampleInput) (any, error) { return in.Filter, nil })

	if tool.Name != "falcon_sample" {
		t.Fatalf("Name = %q", tool.Name)
	}
	if tool.InputSchema == nil {
		t.Fatal("InputSchema is nil")
	}
	props := tool.InputSchema.Properties
	if props["filter"] == nil || props["filter"].Description != "an FQL filter" {
		t.Fatalf("filter description not derived from tag: %+v", props["filter"])
	}
}

func TestNewTool_AppliesConstraints(t *testing.T) {
	tool := NewTool("falcon_sample", "does a thing", ReadOnly(),
		func(_ context.Context, in sampleInput) (any, error) { return nil, nil })

	lim := tool.InputSchema.Properties["limit"]
	if lim.Minimum == nil || *lim.Minimum != 1 {
		t.Fatalf("Minimum = %v, want 1", lim.Minimum)
	}
	if lim.Maximum == nil || *lim.Maximum != 5000 {
		t.Fatalf("Maximum = %v, want 5000", lim.Maximum)
	}
	if string(lim.Default) != "10" {
		t.Fatalf("Default = %s, want 10", lim.Default)
	}
}

func TestTool_RunTypedInput(t *testing.T) {
	tool := NewTool("falcon_sample", "does a thing", ReadOnly(),
		func(_ context.Context, in sampleInput) (any, error) { return in.Filter + "!", nil })

	out, err := tool.Run(context.Background(), json.RawMessage(`{"filter":"platform_name:'Windows'"}`))
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if out != "platform_name:'Windows'!" {
		t.Fatalf("out = %v", out)
	}
}

func TestTool_RunEmptyArgs(t *testing.T) {
	tool := NewTool("falcon_sample", "does a thing", ReadOnly(),
		func(_ context.Context, in sampleInput) (any, error) { return "ok", nil })
	// no arguments at all is valid: all fields omitempty/optional.
	if _, err := tool.Run(context.Background(), nil); err != nil {
		t.Fatalf("Run(nil): %v", err)
	}
}

func TestTool_RunRejectsMalformedJSON(t *testing.T) {
	tool := NewTool("falcon_sample", "does a thing", ReadOnly(),
		func(_ context.Context, in sampleInput) (any, error) { return nil, nil })
	if _, err := tool.Run(context.Background(), json.RawMessage(`{"limit": "not-a-number"}`)); err == nil {
		t.Fatal("expected error on type-mismatched argument, got nil")
	}
}

func TestReadOnly(t *testing.T) {
	ann := ReadOnly()
	if !ann.ReadOnly {
		t.Fatal("ReadOnly() should set ReadOnly=true")
	}
}
