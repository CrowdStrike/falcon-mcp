// Package base provides the shared contract and helpers every falcon-mcp tool
// module reuses: the Module interface consumed by the registry, a tool
// registration wrapper that applies the "falcon_" name prefix and default
// read-only annotations, sentinel errors for typed classification, structured
// output envelopes, and a bounded concurrent two-step detail-fetch helper.
//
// Modules call typed gofalcon methods directly and classify typed errors with
// errors.As against the sentinels declared here, rather than routing calls
// through a dynamic dispatch layer or sniffing untyped responses for an error.
//
// # Modules consuming multiple APIs
//
// A module declares a minimal local interface over each gofalcon sub-client it
// consumes, next to its consumer, so handlers can be tested against a small fake.
// A module that needs more than one API declares one such interface per API and
// holds one struct field per API, named for the API rather than a generic "API":
//
//	type Module struct {
//		Incidents incidentsAPI
//		Behaviors behaviorsAPI
//		Logger    *slog.Logger
//	}
//
// Its Factory pulls each field off the shared client independently; two roles
// served by the same sub-client are assigned from the same registry.Deps.API
// field, while roles from different sub-clients are assigned from their own.
// Prefer this to merging methods into one combined interface, which would force
// an adapter whenever the methods span sub-clients. Single-API modules keep the
// unambiguous field name "API".
package base

import (
	"context"
	"errors"
	"fmt"
	"reflect"

	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"
	"golang.org/x/sync/errgroup"
)

// Module is the contract every tool module implements. It is intentionally
// small and declared next to its sole consumer, the server registry. Concrete
// module types are returned from their constructors; only the registry consumes
// this interface.
type Module interface {
	// Name reports the module's short name (e.g. "detections").
	Name() string
	// Description reports a one-line, human-readable summary of what the module
	// covers. It feeds the dynamic-mode falcon_list_enabled_modules output and
	// generated help text, so it should read as a sentence without a trailing
	// period (e.g. "Search, retrieve, and triage Falcon detections/alerts").
	Description() string
	// RegisterTools registers the module's tools into r. Each tool should be
	// registered via AddTool so the "falcon_" prefix is applied centrally. The
	// Registrar sink decides whether tools land on a live *mcp.Server (normal
	// mode) or in a catalog (dynamic mode).
	RegisterTools(r Registrar)
	// RegisterResources registers the module's MCP resources on s (e.g. FQL
	// guides). Each resource should be registered via TextResource so the
	// "falcon_" name prefix is applied centrally.
	RegisterResources(s *mcp.Server)
}

// ErrFQLSyntax classifies a Falcon 400-class error caused by an invalid FQL
// filter. Modules wrap the underlying typed gofalcon error with %w so callers
// can branch with errors.Is.
var ErrFQLSyntax = errors.New("base: invalid FQL syntax")

// ErrEmptyResult classifies a successful query that matched zero entities.
var ErrEmptyResult = errors.New("base: no matching results")

// namePrefix is prepended to every registered tool name, so a tool registered
// as "search_detections" is exposed as "falcon_search_detections".
const namePrefix = "falcon_"

// ptr returns a pointer to v. Used for the *bool annotation fields whose spec
// default is true, where a nil pointer would mean "true".
func ptr[T any](v T) *T { return &v }

// readOnlyAnnotations returns the default annotations applied to query tools:
// readOnlyHint=true, idempotentHint=true, openWorldHint=true, destructiveHint=false.
func readOnlyAnnotations() *mcp.ToolAnnotations {
	return &mcp.ToolAnnotations{
		ReadOnlyHint:    true,
		IdempotentHint:  true,
		OpenWorldHint:   ptr(true),
		DestructiveHint: ptr(false),
	}
}

// AddTool registers a typed tool into r under the name "falcon_"+name. When
// tool.Annotations is nil the default read-only annotations are applied;
// mutating tools pass explicit annotations to override them. The output schema
// is inferred from Out via inferOutputSchema so gofalcon's strfmt date types
// resolve correctly.
//
// AddTool resolves the In/Out generics up front and hands the Registrar a
// ToolEntry carrying an SDK-registration closure (mcp.AddTool, the SDK's own
// erasure) plus the input schema inferred from In. The sink registers the tool
// on its target server via that closure; the dynamic catalog additionally reads
// InputSchema for parameter display and search. There is no hand-copied erasure
// path — both modes route invocation through the SDK.
func AddTool[In, Out any](r Registrar, tool *mcp.Tool, handler mcp.ToolHandlerFor[In, Out]) {
	tool.Name = namePrefix + tool.Name
	if tool.Annotations == nil {
		tool.Annotations = readOnlyAnnotations()
	}
	if tool.OutputSchema == nil {
		if schema := inferOutputSchema[Out](); schema != nil {
			tool.OutputSchema = schema
		}
	}
	r.Add(ToolEntry{
		Tool:        tool,
		InputSchema: catalogInputSchema[In](tool),
		register:    func(s *mcp.Server) { mcp.AddTool(s, tool, handler) },
	})
}

// catalogInputSchema returns the schema the dynamic catalog exposes for a tool.
// A caller-provided tool.InputSchema is authoritative — the served tool uses it
// verbatim, so the catalog must match rather than re-infer a divergent one from
// In. Only when the caller omits it does the catalog fall back to inference.
func catalogInputSchema[In any](tool *mcp.Tool) *jsonschema.Schema {
	if s, ok := tool.InputSchema.(*jsonschema.Schema); ok && s != nil {
		return s
	}
	return inferInputSchema[In]()
}

// inferInputSchema returns the JSON Schema for In, or nil when In is any (no
// properties to describe) or reflection fails. It is the schema the dynamic
// catalog exposes as a tool's parameters and folds into its search corpus,
// mirroring what the SDK infers for the served tool via the same public
// jsonschema-go call.
func inferInputSchema[In any]() *jsonschema.Schema {
	schema, err := jsonschema.For[In](nil)
	if err != nil {
		return nil
	}
	return schema
}

// defaultResourceMIME is applied to text resources registered without an
// explicit MIME type. All current FQL guides are Markdown.
const defaultResourceMIME = "text/markdown"

// TextResource registers a static UTF-8 text resource on s. Its Name is
// prefixed with "falcon_" (matching the tool-name convention applied by
// AddTool), so a resource registered as "search_detections_fql_guide" is
// exposed as "falcon_search_detections_fql_guide". uri is used verbatim (no
// prefix). When mime is empty it defaults to text/markdown. The registered
// handler serves text verbatim, echoing the requested URI in the response.
func TextResource(s *mcp.Server, uri, name, description, mime, text string) {
	if mime == "" {
		mime = defaultResourceMIME
	}
	s.AddResource(&mcp.Resource{
		Name:        namePrefix + name,
		Description: description,
		URI:         uri,
		MIMEType:    mime,
	}, func(_ context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		return &mcp.ReadResourceResult{
			Contents: []*mcp.ResourceContents{
				{URI: req.Params.URI, MIMEType: mime, Text: text},
			},
		}, nil
	})
}

// opaqueRecordSchema describes a resource record as an unconstrained (open)
// JSON object. It is used to stop schema reflection from descending into
// gofalcon's payload models — see inferOutputSchema.
var opaqueRecordSchema = &jsonschema.Schema{Types: []string{"null", "object"}}

// inferOutputSchema builds the output JSON Schema for Out. It describes our own
// result envelope precisely (resources, total, filter_used, errors, …) but
// treats each resource record as an opaque open object rather than reflecting
// gofalcon's model type.
//
// gofalcon's payload models (e.g. models.DetectsAlert) are deliberately
// polymorphic: they carry an AdditionalProperties catch-all map that MarshalJSON
// flattens back to the top level, so a single Go type represents EPP, IDP, XDR,
// and CWPP alerts with materially different field sets. Reflecting that type
// yields a closed schema (additionalProperties:false) that rejects every real
// response carrying fields not modeled on the struct, and mis-types its embedded
// strfmt.DateTime fields as objects. Rather than patch gofalcon's reflection, we
// don't describe the record interior at all — the record is advertised as an
// open object and its contents pass through unvalidated.
//
// The record type is located via Out's Resources slice field and overridden
// through TypeSchemas. The element type is dereferenced first because the
// reflector consults TypeSchemas by the pointed-to type, not the pointer.
// Envelopes without a Resources field (e.g. ActionResult) are reflected as-is.
//
// Out == any yields a nil schema so the SDK falls back to its default (no
// output schema), matching its own handling of untyped output.
func inferOutputSchema[Out any]() *jsonschema.Schema {
	ot := reflect.TypeFor[Out]()
	if ot == reflect.TypeFor[any]() {
		return nil
	}

	typeSchemas := map[reflect.Type]*jsonschema.Schema{}
	if ot.Kind() == reflect.Struct {
		if f, ok := ot.FieldByName("Resources"); ok && f.Type.Kind() == reflect.Slice {
			elem := f.Type.Elem()
			for elem.Kind() == reflect.Pointer {
				elem = elem.Elem()
			}
			typeSchemas[elem] = opaqueRecordSchema
		}
	}

	schema, err := jsonschema.For[Out](&jsonschema.ForOptions{TypeSchemas: typeSchemas})
	if err != nil {
		// A reflection failure here is a programming error (an unrepresentable
		// Out type); fall back to the SDK's own inference, which will surface it.
		return nil
	}
	return schema
}

// EntitiesResult is the structured output envelope for tools that return a set
// of entities without an FQL filter context (detail lookups and host-group
// query/CRUD tools). It is a JSON object so the SDK can derive an output schema.
type EntitiesResult[T any] struct {
	Resources []T `json:"resources"`
	Total     int `json:"total"`
}

// Entities builds an EntitiesResult, normalizing a nil slice to empty.
func Entities[T any](resources []T) EntitiesResult[T] {
	if resources == nil {
		resources = []T{}
	}
	return EntitiesResult[T]{Resources: resources, Total: len(resources)}
}

// ActionResult is the structured output envelope for mutating tools that do
// not return entity records. Ok is always true on success; Hint carries an
// optional advisory message (e.g. closing a detection without a resolution tag).
type ActionResult struct {
	Ok   bool   `json:"ok"`
	Hint string `json:"hint,omitempty"`
}

// SearchResult is the structured output envelope returned by the FQL search
// tools. It is generic over the resource type so each tool advertises an
// accurate output schema, and it is a JSON object (required for a derived
// output schema). A single shape covers three outcomes:
//   - success: Resources populated, Total set, Errors nil.
//   - empty:   Resources is an empty (non-nil) slice, Total 0.
//   - FQL error: Errors/FQLGuide/Hint populated (see FQLError); the tool still
//     returns a normal result, matching the server's data-not-protocol-error
//     contract for invalid filters.
//
// The value is returned as the handler's typed Out, so the SDK marshals it once
// into StructuredContent as native JSON — no stringify-then-reparse round trip.
type SearchResult[T any] struct {
	Resources  []T              `json:"resources"`
	Total      int              `json:"total"`
	FilterUsed string           `json:"filter_used,omitempty"`
	Errors     []FQLErrorDetail `json:"errors,omitempty"`
	FQLGuide   string           `json:"fql_guide,omitempty"`
	Hint       string           `json:"hint,omitempty"`
}

// Found builds a success (or empty) SearchResult from fetched detail resources. A nil
// slice is normalized to an empty slice so the output is always a JSON array.
func Found[T any](resources []T, filter string) SearchResult[T] {
	if resources == nil {
		resources = []T{}
	}
	return SearchResult[T]{Resources: resources, Total: len(resources), FilterUsed: filter}
}

// FQLError builds a SearchResult describing an invalid FQL filter, carrying the
// API error details and the module's FQL guide text. Resources is empty.
func FQLError[T any](details []FQLErrorDetail, filter, fqlGuide string) SearchResult[T] {
	return SearchResult[T]{
		Resources:  []T{},
		Errors:     details,
		FilterUsed: filter,
		FQLGuide:   fqlGuide,
		Hint:       "The provided FQL filter appears to be invalid. Review the fql_guide for correct syntax.",
	}
}

// FQLErrorDetail is one API error surfaced inside a SearchResult.
type FQLErrorDetail struct {
	Code    int32  `json:"code"`
	Message string `json:"message"`
}

// DetailFetcher fetches the detail records for a single chunk of IDs. It must be
// safe for concurrent use and must honor ctx cancellation.
type DetailFetcher[T any] func(ctx context.Context, ids []string) ([]T, error)

// FetchDetailsParams configures a bounded concurrent two-step detail fetch.
type FetchDetailsParams[T any] struct {
	// IDs is the full set of entity IDs to fetch details for.
	IDs []string
	// ChunkSize is the maximum number of IDs a single detail call accepts.
	ChunkSize int
	// Concurrency bounds in-flight detail calls (rate-limit aware, not CPU-bound).
	Concurrency int
	// Fetch retrieves the details for one chunk.
	Fetch DetailFetcher[T]
	// KeyFn, when non-nil, returns an entity's ID. FetchDetails uses it to
	// reorder each chunk's results back into the requested ID order, restoring
	// the sort applied by the query step: some get-by-IDs endpoints return
	// entities in arbitrary order, silently discarding that sort. When nil,
	// results keep the order the fetcher returned.
	KeyFn func(T) string
}

// FetchDetails fetches details for p.IDs, chunking when the set exceeds p.ChunkSize
// and fetching chunks concurrently under a single errgroup tied to ctx. Results
// are reassembled into a pre-sized slice indexed by chunk position, giving
// stable order without a mutex. A single chunk takes the plain
// sequential path with no goroutines spawned.
func FetchDetails[T any](ctx context.Context, p FetchDetailsParams[T]) ([]T, error) {
	if len(p.IDs) == 0 {
		return []T{}, nil
	}
	chunkSize := p.ChunkSize
	if chunkSize < 1 {
		chunkSize = len(p.IDs)
	}

	chunks := chunkIDs(p.IDs, chunkSize)
	if len(chunks) == 1 {
		res, err := p.Fetch(ctx, chunks[0])
		if err != nil {
			return nil, err
		}
		return reorderByIDs(chunks[0], res, p.KeyFn), nil
	}

	perChunk := make([][]T, len(chunks))
	g, gctx := errgroup.WithContext(ctx)
	if p.Concurrency > 0 {
		g.SetLimit(p.Concurrency)
	}
	for i, chunk := range chunks {
		g.Go(func() error {
			res, err := p.Fetch(gctx, chunk)
			if err != nil {
				return fmt.Errorf("fetch details chunk %d: %w", i, err)
			}
			perChunk[i] = reorderByIDs(chunk, res, p.KeyFn)
			return nil
		})
	}
	if err := g.Wait(); err != nil {
		return nil, err
	}

	var out []T
	for _, res := range perChunk {
		out = append(out, res...)
	}
	return out, nil
}

// chunkIDs splits ids into consecutive slices of at most size elements. The
// returned slices share ids' backing array; callers must not mutate them.
func chunkIDs(ids []string, size int) [][]string {
	var chunks [][]string
	for start := 0; start < len(ids); start += size {
		end := min(start+size, len(ids))
		chunks = append(chunks, ids[start:end])
	}
	return chunks
}

// reorderByIDs reorders entities to match the order of ids, keyed by key(entity).
// It restores the sort applied by a query step when a get-by-IDs endpoint returns
// entities in arbitrary order, and is a no-op when the endpoint already preserves
// order.
//
// Entities whose key is not in ids are appended in their original order and never
// dropped; ids with no matching entity are skipped. A keyless entity (key == "")
// is treated as not-in-ids and appended. When key is nil the entities are returned
// unchanged.
func reorderByIDs[T any](ids []string, entities []T, key func(T) string) []T {
	if key == nil || len(entities) == 0 {
		return entities
	}

	byID := make(map[string]T, len(entities))
	for _, e := range entities {
		if k := key(e); k != "" {
			if _, dup := byID[k]; !dup {
				byID[k] = e
			}
		}
	}

	out := make([]T, 0, len(entities))
	placed := make(map[string]struct{}, len(entities))
	for _, id := range ids {
		if e, ok := byID[id]; ok {
			if _, done := placed[id]; !done {
				out = append(out, e)
				placed[id] = struct{}{}
			}
		}
	}
	// Preserve entities not referenced by ids rather than dropping them.
	for _, e := range entities {
		k := key(e)
		if k == "" {
			out = append(out, e)
			continue
		}
		if _, done := placed[k]; !done {
			out = append(out, e)
		}
	}
	return out
}
