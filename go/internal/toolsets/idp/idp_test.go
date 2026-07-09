package idp

import (
	"context"
	"encoding/json"
	"testing"
)

// asMap marshals a handler result back through JSON into a generic map for
// assertions, mirroring what the MCP layer emits on the wire.
func asMap(t *testing.T, out any) map[string]any {
	t.Helper()
	b, _ := json.Marshal(out)
	var m map[string]any
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatalf("output is not a JSON object: %v (%s)", err, b)
	}
	return m
}

func TestInvestigateEntity_NoIdentifiersReturnsError(t *testing.T) {
	h := &handlers{c: nil}
	out, err := h.investigateEntity(context.Background(), investigateEntityInput{})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	m := asMap(t, out)
	if m["error"] == nil {
		t.Fatalf("expected an error field, got %#v", m)
	}
	summary, ok := m["investigation_summary"].(map[string]any)
	if !ok || summary["status"] != "failed" {
		t.Fatalf("expected failed investigation_summary, got %#v", m)
	}
}

func TestInvestigateEntity_BareWildcardRejected(t *testing.T) {
	h := &handlers{c: nil}
	out, err := h.investigateEntity(context.Background(), investigateEntityInput{EntityNames: "*"})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	m := asMap(t, out)
	if m["error"] == nil {
		t.Fatalf("bare wildcard should be rejected, got %#v", m)
	}
}
