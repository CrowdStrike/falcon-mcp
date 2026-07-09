package idp

import (
	"context"
	"strings"
	"testing"
)

func TestInvestigateEntity_DirectIDsSkipResolution(t *testing.T) {
	// entity_ids are used directly; only the entity_details query is sent.
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[{"entityId":"e1","primaryDisplayName":"Admin"}]}}}`,
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	out, err := h.investigateEntity(context.Background(), investigateEntityInput{EntityIDs: []string{"e1"}})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	m := asMap(t, out)
	if m["error"] != nil {
		t.Fatalf("unexpected error: %#v", m)
	}
	summary := m["investigation_summary"].(map[string]any)
	if summary["status"] != "completed" {
		t.Fatalf("status = %v, want completed", summary["status"])
	}
	// Direct IDs => exactly one GraphQL call (entity_details), no resolution query.
	if len(stub.queries) != 1 {
		t.Fatalf("want 1 GraphQL call, got %d: %v", len(stub.queries), stub.queries)
	}
	if _, ok := m["entity_details"]; !ok {
		t.Fatalf("missing entity_details result: %#v", m)
	}
}

func TestInvestigateEntity_ResolvesByNameThenDetails(t *testing.T) {
	// First response resolves the name to an entity ID; second returns details.
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[{"entityId":"resolved-1"}]}}}`,
		`{"data":{"entities":{"nodes":[{"entityId":"resolved-1","primaryDisplayName":"Administrator"}]}}}`,
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	out, err := h.investigateEntity(context.Background(), investigateEntityInput{EntityNames: "Administrator"})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	m := asMap(t, out)
	if m["error"] != nil {
		t.Fatalf("unexpected error: %#v", m)
	}
	if len(stub.queries) != 2 {
		t.Fatalf("want 2 GraphQL calls (resolve + details), got %d", len(stub.queries))
	}
	// Resolution query must carry a sanitized primaryDisplayNamePattern filter.
	if !strings.Contains(stub.queries[0], "primaryDisplayNamePattern") {
		t.Fatalf("resolution query missing name filter: %s", stub.queries[0])
	}
}

func TestInvestigateEntity_SanitizesInjection(t *testing.T) {
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[]}}}`,
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	// A name containing quotes/newlines must be stripped before interpolation.
	_, err := h.investigateEntity(context.Background(), investigateEntityInput{EntityNames: "Ad\"min\n'x"})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	if len(stub.queries) == 0 {
		t.Fatal("no query sent")
	}
	q := stub.queries[0]
	if strings.Contains(q, `"min`) && strings.ContainsAny(q, "\n") {
		t.Fatalf("query not sanitized: %s", q)
	}
	// The sanitized value 'Adminx' should appear.
	if !strings.Contains(q, "Adminx") {
		t.Fatalf("sanitized name not found in query: %s", q)
	}
}

func TestInvestigateEntity_NoEntitiesFound(t *testing.T) {
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[]}}}`,
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	out, err := h.investigateEntity(context.Background(), investigateEntityInput{EntityNames: "NoSuchUser"})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	m := asMap(t, out)
	if m["error"] == nil {
		t.Fatalf("expected 'no entities found' error, got %#v", m)
	}
}

func TestInvestigateEntity_EmailAndIPConflictPrioritizesEmail(t *testing.T) {
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[{"entityId":"u1"}]}}}`,
		`{"data":{"entities":{"nodes":[{"entityId":"u1","primaryDisplayName":"user"}]}}}`,
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	_, err := h.investigateEntity(context.Background(), investigateEntityInput{
		EmailAddresses: "user@example.com",
		IPAddresses:    []string{"1.1.1.1"},
	})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	// Email takes precedence => USER filter present, ENDPOINT filter absent.
	q := stub.queries[0]
	if !strings.Contains(q, "types: [USER]") {
		t.Fatalf("expected USER filter (email precedence): %s", q)
	}
	if strings.Contains(q, "ENDPOINT") {
		t.Fatalf("IP/ENDPOINT filter should be dropped when email present: %s", q)
	}
}

func TestNew_RegistersTool(t *testing.T) {
	ts := New(nil)
	if ts.Name != "idp" {
		t.Fatalf("toolset name = %q", ts.Name)
	}
	if len(ts.Tools) != 1 || ts.Tools[0].Name != "idp_investigate_entity" {
		t.Fatalf("expected single idp_investigate_entity tool, got %+v", ts.Tools)
	}
}
