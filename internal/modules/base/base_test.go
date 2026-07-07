package base

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sync/atomic"
	"testing"
	"time"

	"github.com/go-openapi/strfmt"
	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// TestTextResourceRegistersAndServes verifies TextResource applies the
// "falcon_" name prefix, leaves the URI unprefixed, defaults the MIME type to
// text/markdown, and serves the text verbatim over resources/list and
// resources/read via the in-memory client transport.
func TestTextResourceRegistersAndServes(t *testing.T) {
	t.Parallel()

	const (
		uri  = "falcon://detections/search/fql-guide"
		text = "# FQL guide\nfilter syntax"
	)
	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "test"}, nil)
	// Empty mime must default to text/markdown.
	TextResource(srv, uri, "search_detections_fql_guide", "guide desc", "", text)

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
	got := list.Resources[0]
	if got.Name != "falcon_search_detections_fql_guide" {
		t.Errorf("name = %q, want falcon_ prefix applied", got.Name)
	}
	if got.URI != uri {
		t.Errorf("URI = %q, want %q (no prefix)", got.URI, uri)
	}
	if got.MIMEType != defaultResourceMIME {
		t.Errorf("MIMEType = %q, want %q", got.MIMEType, defaultResourceMIME)
	}

	read, err := cs.ReadResource(ctx, &mcp.ReadResourceParams{URI: uri})
	if err != nil {
		t.Fatalf("ReadResource: %v", err)
	}
	if len(read.Contents) != 1 || read.Contents[0].Text != text {
		t.Fatalf("read content = %+v, want text %q", read.Contents, text)
	}
	if read.Contents[0].URI != uri {
		t.Errorf("content URI = %q, want %q", read.Contents[0].URI, uri)
	}
}

func TestFetchDetailsSingleChunkSequential(t *testing.T) {
	t.Parallel()

	var calls atomic.Int32
	got, err := FetchDetails(context.Background(), FetchDetailsParams[string]{
		IDs:         []string{"a", "b", "c"},
		ChunkSize:   10,
		Concurrency: 4,
		Fetch: func(_ context.Context, ids []string) ([]string, error) {
			calls.Add(1)
			return ids, nil
		},
	})
	if err != nil {
		t.Fatalf("FetchDetails: %v", err)
	}
	if calls.Load() != 1 {
		t.Fatalf("expected 1 fetch call, got %d", calls.Load())
	}
	if len(got) != 3 {
		t.Fatalf("expected 3 results, got %d", len(got))
	}
}

func TestFetchDetailsStableReassembly(t *testing.T) {
	t.Parallel()

	// 5 chunks of 2; later chunks return faster to scramble completion order.
	ids := []string{"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
	got, err := FetchDetails(context.Background(), FetchDetailsParams[string]{
		IDs:         ids,
		ChunkSize:   2,
		Concurrency: 5,
		Fetch: func(_ context.Context, chunk []string) ([]string, error) {
			// Delay proportional to first ID descending: earlier chunks finish last.
			d := 10 - int(chunk[0][0]-'0')
			time.Sleep(time.Duration(d) * time.Millisecond)
			return chunk, nil
		},
	})
	if err != nil {
		t.Fatalf("FetchDetails: %v", err)
	}
	for i, v := range got {
		if v != fmt.Sprint(i) {
			t.Fatalf("result out of order at %d: got %q, want %q", i, v, fmt.Sprint(i))
		}
	}
}

func TestFetchDetailsFirstErrorCancels(t *testing.T) {
	t.Parallel()

	sentinel := errors.New("boom")
	var cancelled atomic.Bool
	_, err := FetchDetails(context.Background(), FetchDetailsParams[string]{
		IDs:         []string{"0", "1", "2", "3"},
		ChunkSize:   1,
		Concurrency: 4,
		Fetch: func(ctx context.Context, chunk []string) ([]string, error) {
			if chunk[0] == "0" {
				return nil, sentinel
			}
			// Siblings should observe cancellation from the errgroup.
			select {
			case <-ctx.Done():
				cancelled.Store(true)
				return nil, ctx.Err()
			case <-time.After(time.Second):
				return chunk, nil
			}
		},
	})
	if !errors.Is(err, sentinel) {
		t.Fatalf("expected sentinel error, got %v", err)
	}
}

func TestFetchDetailsCtxCancelAborts(t *testing.T) {
	t.Parallel()

	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	_, err := FetchDetails(ctx, FetchDetailsParams[string]{
		IDs:         []string{"0", "1", "2", "3"},
		ChunkSize:   1,
		Concurrency: 2,
		Fetch: func(ctx context.Context, chunk []string) ([]string, error) {
			<-ctx.Done()
			return nil, ctx.Err()
		},
	})
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("expected context.Canceled, got %v", err)
	}
}

func TestFetchDetailsEmpty(t *testing.T) {
	t.Parallel()

	got, err := FetchDetails(context.Background(), FetchDetailsParams[string]{
		IDs:   nil,
		Fetch: func(_ context.Context, ids []string) ([]string, error) { return ids, nil },
	})
	if err != nil {
		t.Fatalf("FetchDetails: %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("expected empty result, got %d", len(got))
	}
}

func TestReorderByIDs(t *testing.T) {
	t.Parallel()

	// entity is a minimal keyed record for exercising the reorder helper.
	type entity struct {
		id string
	}
	key := func(e entity) string { return e.id }

	tests := []struct {
		name     string
		ids      []string
		entities []entity
		want     []string // expected ids in order
	}{
		{
			name:     "already in order is a no-op",
			ids:      []string{"a", "b", "c"},
			entities: []entity{{id: "a"}, {id: "b"}, {id: "c"}},
			want:     []string{"a", "b", "c"},
		},
		{
			name:     "reversed is restored",
			ids:      []string{"a", "b", "c"},
			entities: []entity{{id: "c"}, {id: "b"}, {id: "a"}},
			want:     []string{"a", "b", "c"},
		},
		{
			name:     "entity not in ids is appended, never dropped",
			ids:      []string{"a", "b"},
			entities: []entity{{id: "b"}, {id: "x"}, {id: "a"}},
			want:     []string{"a", "b", "x"},
		},
		{
			name:     "id with no matching entity is skipped",
			ids:      []string{"a", "missing", "b"},
			entities: []entity{{id: "b"}, {id: "a"}},
			want:     []string{"a", "b"},
		},
		{
			name:     "duplicate ids place the entity once",
			ids:      []string{"a", "a", "b"},
			entities: []entity{{id: "a"}, {id: "b"}},
			want:     []string{"a", "b"},
		},
		{
			name:     "keyless entity is appended",
			ids:      []string{"a", "b"},
			entities: []entity{{id: "b"}, {id: ""}, {id: "a"}},
			want:     []string{"a", "b", ""},
		},
		{
			name:     "empty entities returns empty",
			ids:      []string{"a", "b"},
			entities: nil,
			want:     nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			got := reorderByIDs(tt.ids, tt.entities, key)
			if len(got) != len(tt.want) {
				t.Fatalf("length mismatch: got %d, want %d (%+v)", len(got), len(tt.want), got)
			}
			for i, e := range got {
				if e.id != tt.want[i] {
					t.Fatalf("order mismatch at %d: got %q, want %q (%+v)", i, e.id, tt.want[i], got)
				}
			}
		})
	}
}

func TestReorderByIDsNilKeyIsNoop(t *testing.T) {
	t.Parallel()

	entities := []string{"c", "b", "a"}
	got := reorderByIDs([]string{"a", "b", "c"}, entities, nil)
	for i, v := range got {
		if v != entities[i] {
			t.Fatalf("nil key must not reorder: got %v", got)
		}
	}
}

func TestFetchDetailsReordersScrambledChunks(t *testing.T) {
	t.Parallel()

	// 3 chunks of 2; each chunk's fetcher returns its IDs reversed to simulate a
	// get-by-IDs endpoint discarding the query-step sort. With KeyFn set, the
	// assembled output must still match the requested ID order.
	ids := []string{"0", "1", "2", "3", "4", "5"}
	got, err := FetchDetails(context.Background(), FetchDetailsParams[string]{
		IDs:         ids,
		ChunkSize:   2,
		Concurrency: 3,
		Fetch: func(_ context.Context, chunk []string) ([]string, error) {
			rev := make([]string, len(chunk))
			for i, id := range chunk {
				rev[len(chunk)-1-i] = id
			}
			return rev, nil
		},
		KeyFn: func(s string) string { return s },
	})
	if err != nil {
		t.Fatalf("FetchDetails: %v", err)
	}
	for i, v := range got {
		if v != fmt.Sprint(i) {
			t.Fatalf("result out of order at %d: got %q, want %q", i, v, fmt.Sprint(i))
		}
	}
}

func TestFound(t *testing.T) {
	t.Parallel()

	// A nil slice must normalize to a non-nil empty slice for stable JSON arrays.
	got := Found[string](nil, "status:'new'")
	if got.Total != 0 || got.FilterUsed != "status:'new'" || got.Resources == nil {
		t.Fatalf("unexpected empty result: %+v", got)
	}

	full := Found([]string{"a", "b"}, "")
	if full.Total != 2 || len(full.Resources) != 2 {
		t.Fatalf("unexpected populated result: %+v", full)
	}
}

func TestFQLError(t *testing.T) {
	t.Parallel()

	got := FQLError[string]([]FQLErrorDetail{{Code: 400, Message: "bad"}}, "bogus", "guide-text")
	if len(got.Errors) != 1 || got.FQLGuide != "guide-text" || got.Hint == "" {
		t.Fatalf("unexpected FQL error result: %+v", got)
	}
	if got.Resources == nil {
		t.Fatalf("resources must be non-nil empty slice")
	}
}

// policyDates mirrors a gofalcon model fragment: strfmt date wrappers nested
// inside a struct, both by value and behind a pointer. It reproduces the shape
// that broke device_policies.*.assigned_date without depending on the full
// gofalcon models package.
type policyDates struct {
	AssignedID string          `json:"assigned_id"`
	Assigned   strfmt.DateTime `json:"assigned_date,omitempty"`
	Applied    *strfmt.Date    `json:"applied_date,omitempty"`
}

type policyEnvelope struct {
	Resources []policyDates `json:"resources"`
	Total     int           `json:"total"`
}

// findProp walks nested object schemas by property name, following the Items
// schema for arrays. It fails the test if any hop is missing.
func findProp(t *testing.T, s *jsonschema.Schema, path ...string) *jsonschema.Schema {
	t.Helper()
	cur := s
	for _, p := range path {
		if p == "[]" {
			if cur.Items == nil {
				t.Fatalf("expected array items schema at %v", path)
			}
			cur = cur.Items
			continue
		}
		next := cur.Properties[p]
		if next == nil {
			t.Fatalf("missing property %q while walking %v", p, path)
		}
		cur = next
	}
	return cur
}

// schemaType returns the single type of a schema, tolerating the ["null","T"]
// form the reflector emits for pointer (nullable) fields.
func schemaType(s *jsonschema.Schema) string {
	if s.Type != "" {
		return s.Type
	}
	for _, t := range s.Types {
		if t != "null" {
			return t
		}
	}
	return ""
}

// TestInferOutputSchemaRecordIsOpaqueObject guards the mechanism that keeps
// strfmt date fields from being mis-typed. inferOutputSchema deliberately does
// not descend into resource records: the record element is advertised as an
// open object (opaqueRecordSchema), so nested strfmt.DateTime/strfmt.Date
// fields pass through as their marshaled string form rather than being
// reflected into object schemas that would reject a string date. The end-to-end
// consequence — a populated date validating against the schema — is covered by
// TestInferOutputSchemaValidatesRealPayload.
func TestInferOutputSchemaRecordIsOpaqueObject(t *testing.T) {
	t.Parallel()

	schema := inferOutputSchema[policyEnvelope]()
	if schema == nil {
		t.Fatal("inferOutputSchema returned nil for a concrete type")
	}

	item := findProp(t, schema, "resources", "[]")
	if got := schemaType(item); got != "object" {
		t.Fatalf("resource item schema type = %q, want %q", got, "object")
	}
	// The record interior must not be reflected — no per-field properties that
	// could mis-type the embedded strfmt date fields as objects.
	if len(item.Properties) != 0 {
		t.Fatalf("resource item must be an opaque object, got properties %v", item.Properties)
	}
}

// TestInferOutputSchemaValidatesRealPayload is the regression guard for the
// bug where a populated date field was rejected by the tool's own output
// schema. It resolves the schema and validates a marshaled value carrying
// non-zero dates — the exact case that previously failed.
func TestInferOutputSchemaValidatesRealPayload(t *testing.T) {
	t.Parallel()

	schema := inferOutputSchema[policyEnvelope]()
	resolved, err := schema.Resolve(&jsonschema.ResolveOptions{ValidateDefaults: true})
	if err != nil {
		t.Fatalf("resolve schema: %v", err)
	}

	appliedDate := strfmt.Date(time.Date(2026, 5, 19, 0, 0, 0, 0, time.UTC))
	payload := policyEnvelope{
		Resources: []policyDates{{
			AssignedID: "sensor_update",
			Assigned:   strfmt.DateTime(time.Date(2026, 5, 19, 19, 6, 41, 0, time.UTC)),
			Applied:    &appliedDate,
		}},
		Total: 1,
	}

	// Round-trip through JSON exactly as the SDK does before validating.
	raw, err := json.Marshal(payload)
	if err != nil {
		t.Fatalf("marshal payload: %v", err)
	}
	var instance any
	if err := json.Unmarshal(raw, &instance); err != nil {
		t.Fatalf("unmarshal payload: %v", err)
	}

	if err := resolved.Validate(instance); err != nil {
		t.Fatalf("real payload with populated dates must validate, got: %v", err)
	}
}

func TestInferOutputSchemaAnyIsNil(t *testing.T) {
	t.Parallel()

	if got := inferOutputSchema[any](); got != nil {
		t.Fatalf("inferOutputSchema[any] = %v, want nil so the SDK omits the output schema", got)
	}
}
