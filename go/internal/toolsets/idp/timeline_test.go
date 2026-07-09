package idp

import (
	"context"
	"strings"
	"testing"
)

func TestTimelineAnalysis_AllowlistsEventTypes(t *testing.T) {
	stub := &graphqlStub{responses: []string{
		`{"data":{"entities":{"nodes":[{"entityId":"e1"}]}}}`, // resolution
		`{"data":{"timeline":{"nodes":[],"pageInfo":{}}}}`,    // timeline
	}}
	c := newIDPTestClient(t, stub)
	h := &handlers{c: c}

	_, err := h.investigateEntity(context.Background(), investigateEntityInput{
		EntityNames:        "Admin*",
		InvestigationTypes: []string{"timeline_analysis"},
		// One valid enum, one injection attempt that must be dropped entirely.
		TimelineEventTypes: []string{"ACTIVITY", "THREAT{evil}"},
	})
	if err != nil {
		t.Fatalf("investigateEntity: %v", err)
	}
	// The timeline query is the second GraphQL call.
	if len(stub.queries) < 2 {
		t.Fatalf("expected resolution + timeline queries, got %d", len(stub.queries))
	}
	q := stub.queries[1]
	if !strings.Contains(q, "categories: [ACTIVITY]") {
		t.Fatalf("valid event type not passed through: %s", q)
	}
	if strings.Contains(q, "evil") || strings.Contains(q, "THREAT{") {
		t.Fatalf("non-allowlisted event type leaked into query: %s", q)
	}
}
