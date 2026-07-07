package detections

import (
	"context"
	"errors"
	"log/slog"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// testLogger discards output; modules require a non-nil logger.
var testLogger = slog.New(slog.DiscardHandler)

// fakeAlerts is a configurable test double for the alertsAPI interface.
type fakeAlerts struct {
	queryResp *alerts.QueryV2OK
	queryErr  error
	getResp   *alerts.GetV2OK
	getErr    error
	updateErr error

	lastUpdateBody *models.DetectsapiPatchEntitiesAlertsV3Request
	getCalls       int
}

func (f *fakeAlerts) QueryV2(*alerts.QueryV2Params, ...alerts.ClientOption) (*alerts.QueryV2OK, error) {
	return f.queryResp, f.queryErr
}

func (f *fakeAlerts) GetV2(p *alerts.GetV2Params, _ ...alerts.ClientOption) (*alerts.GetV2OK, error) {
	f.getCalls++
	return f.getResp, f.getErr
}

func (f *fakeAlerts) UpdateV3(p *alerts.UpdateV3Params, _ ...alerts.ClientOption) (*alerts.UpdateV3OK, error) {
	f.lastUpdateBody = p.Body
	return &alerts.UpdateV3OK{}, f.updateErr
}

func str(s string) *string { return &s }
func i32(v int32) *int32   { return &v }

func TestSearchDetectionsEmpty(t *testing.T) {
	t.Parallel()

	f := &fakeAlerts{queryResp: &alerts.QueryV2OK{Payload: &models.DetectsapiAlertQueryResponse{Resources: []string{}}}}
	m := New(Params{API: f, Concurrency: 4, Logger: testLogger})

	_, out, err := m.searchDetections(context.Background(), nil, SearchInput{Filter: "status:'new'"})
	if err != nil {
		t.Fatalf("searchDetections: %v", err)
	}
	if out.Total != 0 || len(out.Resources) != 0 || out.FilterUsed != "status:'new'" {
		t.Fatalf("expected empty result, got %+v", out)
	}
	if out.Resources == nil {
		t.Fatalf("resources must be a non-nil empty slice for stable JSON array output")
	}
	if f.getCalls != 0 {
		t.Fatalf("expected no detail fetch on empty result, got %d GetV2 calls", f.getCalls)
	}
}

func TestSearchDetectionsFQLError(t *testing.T) {
	t.Parallel()

	badReq := &alerts.QueryV2BadRequest{Payload: &models.DetectsapiAlertQueryResponse{
		Errors: []*models.MsaAPIError{{Code: i32(400), Message: str("invalid filter")}},
	}}
	f := &fakeAlerts{queryErr: badReq}
	m := New(Params{API: f, Concurrency: 4, Logger: testLogger})

	_, out, err := m.searchDetections(context.Background(), nil, SearchInput{Filter: "bogus"})
	if err != nil {
		t.Fatalf("expected FQL error to be formatted, not returned: %v", err)
	}
	if len(out.Errors) != 1 || out.Errors[0].Message != "invalid filter" {
		t.Fatalf("expected FQL error detail, got %+v", out.Errors)
	}
	if out.FQLGuide == "" || out.Hint == "" {
		t.Fatalf("expected fql_guide and hint to be populated")
	}
}

func TestSearchDetectionsFetchesDetails(t *testing.T) {
	t.Parallel()

	// GetV2 returns alerts scrambled relative to the query order; the tool must
	// reorder them back to the query step's sort (composite_id).
	f := &fakeAlerts{
		queryResp: &alerts.QueryV2OK{Payload: &models.DetectsapiAlertQueryResponse{Resources: []string{"id1", "id2"}}},
		getResp: &alerts.GetV2OK{Payload: &models.DetectsapiPostEntitiesAlertsV2Response{Resources: []*models.DetectsAlert{
			{CompositeID: str("id2")},
			{CompositeID: str("id1")},
		}}},
	}
	m := New(Params{API: f, Concurrency: 4, Logger: testLogger})

	_, out, err := m.searchDetections(context.Background(), nil, SearchInput{})
	if err != nil {
		t.Fatalf("searchDetections: %v", err)
	}
	if out.Total != 2 || len(out.Resources) != 2 {
		t.Fatalf("expected 2 fetched resources, got %+v", out)
	}
	if got := *out.Resources[0].CompositeID; got != "id1" {
		t.Fatalf("expected query order restored (id1 first), got %q", got)
	}
	if got := *out.Resources[1].CompositeID; got != "id2" {
		t.Fatalf("expected query order restored (id2 second), got %q", got)
	}
	if f.getCalls != 1 {
		t.Fatalf("expected 1 GetV2 call, got %d", f.getCalls)
	}
}

func TestUpdateDetectionsValidation(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		in      UpdateInput
		wantErr bool
	}{
		{"no ids", UpdateInput{Status: "closed"}, true},
		{"no fields", UpdateInput{IDs: []string{"x"}}, true},
		{"bad status", UpdateInput{IDs: []string{"x"}, Status: "frozen"}, true},
		{"two assignments", UpdateInput{IDs: []string{"x"}, AssignToUUID: "a", AssignToName: "b"}, true},
		{"unassign with assign", UpdateInput{IDs: []string{"x"}, Unassign: true, AssignToUUID: "a"}, true},
		{"valid status", UpdateInput{IDs: []string{"x"}, Status: "in_progress"}, false},
		{"valid unassign", UpdateInput{IDs: []string{"x"}, Unassign: true}, false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			f := &fakeAlerts{}
			m := New(Params{API: f, Concurrency: 4, Logger: testLogger})
			_, _, err := m.updateDetections(context.Background(), nil, tc.in)
			if tc.wantErr && err == nil {
				t.Fatalf("expected error, got nil")
			}
			if tc.wantErr && !errors.Is(err, errInvalidInput) {
				t.Fatalf("expected errInvalidInput, got %v", err)
			}
			if !tc.wantErr && err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}

func TestUpdateDetectionsBooleanAsString(t *testing.T) {
	t.Parallel()

	f := &fakeAlerts{}
	m := New(Params{API: f, Concurrency: 4, Logger: testLogger})
	show := false
	_, _, err := m.updateDetections(context.Background(), nil, UpdateInput{IDs: []string{"x"}, ShowInUI: &show})
	if err != nil {
		t.Fatalf("updateDetections: %v", err)
	}
	found := false
	for _, ap := range f.lastUpdateBody.ActionParameters {
		if *ap.Name == "show_in_ui" {
			found = true
			if *ap.Value != "false" {
				t.Fatalf("show_in_ui should be lowercase string, got %q", *ap.Value)
			}
		}
	}
	if !found {
		t.Fatalf("show_in_ui action parameter not sent")
	}
}

func TestUpdateDetectionsCloseWithoutResolutionHint(t *testing.T) {
	t.Parallel()

	f := &fakeAlerts{}
	m := New(Params{API: f, Concurrency: 4, Logger: testLogger})
	_, out, err := m.updateDetections(context.Background(), nil, UpdateInput{IDs: []string{"x"}, Status: "closed"})
	if err != nil {
		t.Fatalf("updateDetections: %v", err)
	}
	if !out.Ok || out.Hint == "" {
		t.Fatalf("expected close-without-resolution hint, got %+v", out)
	}
}

// TestRegisterResourcesServesFQLGuide verifies the detections module publishes
// its FQL guide as the falcon://detections/search/fql-guide resource, with the
// Python-matching name, and that reading it returns the embedded guide text.
func TestRegisterResourcesServesFQLGuide(t *testing.T) {
	t.Parallel()

	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "test"}, nil)
	New(Params{API: &fakeAlerts{}, Concurrency: 4, Logger: testLogger}).RegisterResources(srv)

	ctx := context.Background()
	clientT, serverT := mcp.NewInMemoryTransports()
	ss, err := srv.Connect(ctx, serverT, nil)
	if err != nil {
		t.Fatalf("server connect: %v", err)
	}
	t.Cleanup(func() { _ = ss.Wait() })

	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "test"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	list, err := cs.ListResources(ctx, nil)
	if err != nil {
		t.Fatalf("ListResources: %v", err)
	}
	if len(list.Resources) != 1 {
		t.Fatalf("expected 1 resource, got %d", len(list.Resources))
	}
	if got := list.Resources[0]; got.Name != "falcon_search_detections_fql_guide" || got.URI != fqlGuideURI {
		t.Fatalf("resource = {name:%q uri:%q}, want falcon_search_detections_fql_guide / %s", got.Name, got.URI, fqlGuideURI)
	}

	read, err := cs.ReadResource(ctx, &mcp.ReadResourceParams{URI: fqlGuideURI})
	if err != nil {
		t.Fatalf("ReadResource: %v", err)
	}
	if len(read.Contents) != 1 || read.Contents[0].Text != fqlGuide {
		t.Fatalf("read content does not match embedded guide")
	}
}
